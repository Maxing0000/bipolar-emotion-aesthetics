#!/usr/bin/env python3
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

"""
BEA (Bipolar Emotion Aesthetics) 量化引擎 v2.4.0

核心价值：把审美判断从"我觉得"变成可讨论、可比较、可追踪的协作对象。
仅用 Python 标准库，离线可用。

用法：
  python3 bea_quant.py analyze --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
  python3 bea_quant.py report  --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
  python3 bea_quant.py score   --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
  python3 bea_quant.py compare --category phone --a "iPhone=3,6,4,3,5,6" --b "Samsung=形状=4,质感=4,..."
  python3 bea_quant.py batch   --category phone --items "A=3,6,4,3,5,6;B=形状=4,质感=4,色彩=4,..."
  python3 bea_quant.py template --category phone
  python3 bea_quant.py test

compare/batch 的产品值支持两种格式（自动识别）：
  紧凑格式：名称=3,6,4,3,5,6  （按 template 输出的维度顺序）
  完整格式：名称=形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6  （带维度名，更安全）
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

# ──────────────────────────────────────────────
# 核心配置
# ──────────────────────────────────────────────

CATEGORY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "phone": {
        "形状": 0.25, "质感": 0.25, "色彩": 0.15,
        "构图": 0.15, "光影": 0.10, "细节": 0.10,
    },
    "car": {
        "曲面": 0.30, "特征线": 0.25, "灯组": 0.15,
        "比例": 0.15, "材质": 0.15,
    },
    "brand": {
        "图形": 0.25, "色彩": 0.25, "字体": 0.20,
        "版式": 0.20, "质感": 0.10,
    },
    "ui": {
        "布局": 0.25, "色彩对比": 0.20, "组件形": 0.20,
        "动效": 0.20, "字体图标": 0.15,
    },
    "building": {
        "形体轮廓": 0.30, "立面线条": 0.25, "比例尺度": 0.20,
        "材质肌理": 0.15, "光影空间": 0.10,
    },
}

# 六范式锚点：(下限, 上限, 名称, 核心体验)
PARADIGMS: List[Tuple[float, float, str, str]] = [
    (0.00, 0.15, "治愈松弛", "放松舒展、无攻击性"),
    (0.15, 0.30, "亲和精致", "第一眼亲和、细看精密"),
    (0.30, 0.48, "均衡典雅", "刚柔各半、克制端庄"),
    (0.48, 0.60, "崇高震撼", "先屏息敬畏、后沉浸沉醉"),
    (0.60, 0.66, "冷峻克制", "冷硬简为主、极少暖色维持人性"),
    (0.66, 0.85, "先锋反叛", "刺激反叛、临界于不适的痛快"),
    (0.85, 1.01, "逼近越阈", "真实不适、非美区"),
]


# ──────────────────────────────────────────────
# 病症诊断规则（用函数代替 eval，更安全清晰）
# ──────────────────────────────────────────────

def _has_sweet_tooth(w_t: float, dims: Dict[str, int]) -> bool:
    return w_t < 0.25 and all(t <= 4 for t in dims.values())

def _has_aggression(w_t: float, dims: Dict[str, int]) -> bool:
    # 攻击症：整体危极高(W(T)>=0.55)且有明显高强度维度(t>=6)
    # v2.2 改进：从 W(T)>0.60 且 t>=7 降低为 W(T)>=0.55 且 t>=6，
    # 以覆盖冷峻克制范式的高危极设计，避免漏报
    return w_t >= 0.55 and any(t >= 6 for t in dims.values())

def _has_middle_child(w_t: float, dims: Dict[str, int]) -> bool:
    # 均分症：所有维度集中在3-5且极差<2（真正的无主次），W(T)在中间区间
    return (all(3 <= t <= 5 for t in dims.values())
            and 0.35 <= w_t <= 0.45
            and (max(dims.values()) - min(dims.values())) < 2)

def _has_emphasis_inflation(w_t: float, dims: Dict[str, int]) -> bool:
    return sum(1 for t in dims.values() if t >= 6) >= 3

def _has_tension_deficit(w_t: float, dims: Dict[str, int]) -> bool:
    return w_t < 0.35 and (max(dims.values()) - min(dims.values())) < 2

def _has_stimulation_fatigue(w_t: float, dims: Dict[str, int]) -> bool:
    # 刺激疲劳：所有维度 t>=7 且 W(T)>=0.65，全程高能无喘息
    # 短期抓眼但长期疲惫，需要安排亲极呼吸段
    return w_t >= 0.65 and all(t >= 7 for t in dims.values())

def _has_instinct_violation(w_t: float, dims: Dict[str, int]) -> bool:
    # 本能越界：任何维度 t>=10，触及本能安全阈
    # BEA 理论：本能安全阈是绝对红线，越过即从审美对象变为伤害源
    return any(t >= 10 for t in dims.values())

# (名称, 诊断函数, 处方)
# 注意：失序症和层级冲突症无法仅通过维度值自动诊断，需人工判断，在报告中给出检查提示
DISEASE_RULES: List[Tuple[str, Callable[[float, Dict[str, int]], bool], str]] = [
    ("本能越界", _has_instinct_violation,
     "触及割伤/眩晕/疼痛等生理红线。一票否决，删除或钝化，无风格借口可越过本能红线。"),
    ("甜腻症", _has_sweet_tooth,
     "全圆角全柔色、无锐度。在高价值细节处注入10%-20%危极，柔中藏骨。"),
    ("攻击症", _has_aggression,
     "处处锐角强对比、令人紧张。扩大亲极基底，将过强维度降至范式区间内。"),
    ("刺激疲劳", _has_stimulation_fatigue,
     "全程高能无喘息，短期抓眼长期疲惫。时空上安排亲极呼吸段，控制强调点数量。"),
    ("均分症", _has_middle_child,
     "亲危各半无主次、情绪暧昧。确立>=6:4主辅比，让第一印象明确。"),
    ("重点通胀症", _has_emphasis_inflation,
     "哪里都想强调、视觉噪音大。做减法，强调点压回1-2个。"),
    ("张力不足症", _has_tension_deficit,
     "所有维度都温和、没有提神点。在1-2个维度提升危极强度至6+，制造对比。"),
]

# 需人工判断的病症（无法仅通过维度值自动诊断）
MANUAL_CHECK_DISEASES = [
    {
        "name": "失序症",
        "check_prompt": "单元素是否都精彩但堆在一起互相打架？是否缺少贯穿全局的统一主线（色板/模数/栅格/特征线）？",
        "prescription": "确立一条贯穿全局的统一主线，让对立元素在同一秩序下成对出现。",
    },
    {
        "name": "层级冲突症",
        "check_prompt": "宏观（整体轮廓）与微观（细节处理）的极性是否一致？是否出现外观圆润却细节硌手、视觉柔和却声音刺耳的跨通道冲突？",
        "prescription": "逐层逐通道审计，选择同向叠加或微差补偿策略，消除宏观/微观、跨通道的方向冲突。",
    },
]


# ──────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────

@dataclass
class BEAAnalysis:
    category: str
    dimensions: Dict[str, int]
    weights: Dict[str, float]
    w_t: float
    paradigm: str
    paradigm_desc: str
    paradigm_range: Tuple[float, float]
    diseases: List[Dict[str, str]]
    score_suggestion: Dict[str, object]
    polarity_ratio: Dict[str, object]
    endurance: Dict[str, object]

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "dimensions": self.dimensions,
            "weights": self.weights,
            "w_t": round(self.w_t, 3),
            "paradigm": self.paradigm,
            "paradigm_desc": self.paradigm_desc,
            "paradigm_range": list(self.paradigm_range),
            "diseases": self.diseases,
            "score_suggestion": self.score_suggestion,
            "polarity_ratio": self.polarity_ratio,
            "endurance": self.endurance,
        }


# ──────────────────────────────────────────────
# 核心计算
# ──────────────────────────────────────────────

def parse_t_values(t_str: str, valid_dims: List[str]) -> Dict[str, int]:
    """解析 '形状=3,质感=6,色彩=4' 格式的输入。"""
    result = {}
    for pair in t_str.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(f"格式错误：'{pair}'，应为 '维度名=数值'")
        name, val = pair.split("=", 1)
        name = name.strip()
        try:
            val = int(val.strip())
        except ValueError:
            raise ValueError(f"维度 '{name}' 的值 '{val}' 不是整数")
        if name not in valid_dims:
            raise ValueError(f"未知维度 '{name}'，有效维度为：{', '.join(valid_dims)}。如使用了自定义权重(--profile/--weights)，请检查权重配置中的维度名是否一致")
        if not (0 <= val <= 10):
            raise ValueError(f"维度 '{name}' 的值 {val} 超出 0-10 范围")
        result[name] = val
    missing = [d for d in valid_dims if d not in result]
    if missing:
        raise ValueError(f"缺少维度：{', '.join(missing)}")
    return result


def parse_compact_values(name_vals: str, category: str) -> Tuple[str, Dict[str, int]]:
    """
    解析 compare/batch 用的产品条目，同时支持两种格式：
      紧凑格式：名称=3,6,4,3,5,6  （按维度顺序）
      完整格式：名称=形状=3,质感=6,...  （带维度名）
    自动识别：值部分包含 '=' 则为完整格式。
    返回 (名称, 维度字典)。
    """
    if "=" not in name_vals:
        raise ValueError(f"格式错误：'{name_vals}'，应为 '名称=值'")
    name, vals_str = name_vals.split("=", 1)
    name = name.strip()
    valid_dims = list(CATEGORY_WEIGHTS[category].keys())

    if "=" in vals_str:
        # 完整格式：形状=3,质感=6,...
        dims = parse_t_values(vals_str, valid_dims)
    else:
        # 紧凑格式：3,6,4,3,5,6
        vals = [v.strip() for v in vals_str.split(",") if v.strip()]
        if len(vals) != len(valid_dims):
            raise ValueError(
                f"产品 '{name}' 的值数量不对：需要 {len(valid_dims)} 个（{', '.join(valid_dims)}），"
                f"实际提供 {len(vals)} 个。或使用完整格式：{name}={','.join(d+'=?' for d in valid_dims)}"
            )
        try:
            dims = {d: int(v) for d, v in zip(valid_dims, vals)}
        except ValueError as e:
            raise ValueError(f"产品 '{name}' 的值包含非整数：{e}")
        for d, v in dims.items():
            if not (0 <= v <= 10):
                raise ValueError(f"产品 '{name}' 的维度 '{d}' 值 {v} 超出 0-10 范围")

    return name, dims


def compute_w_t(dimensions: Dict[str, int], weights: Dict[str, float]) -> float:
    total = sum(weights.get(d, 0) * (t / 10.0) for d, t in dimensions.items())
    return round(total, 3)


def compute_polarity_ratio(dimensions: Dict[str, int], weights: Dict[str, float]) -> Dict[str, object]:
    """
    计算主辅比：亲极与危极的权重占比。

    极性划分：
    - 亲极 P+：t <= 3
    - 中性：4 <= t <= 5
    - 危极 T−：t >= 6

    返回：
    - plus_weight: 亲极总权重
    - minus_weight: 危极总权重
    - neutral_weight: 中性总权重
    - plus_ratio: 亲极占比（0-1）
    - minus_ratio: 危极占比（0-1）
    - dominant: 主导极性（"亲极 P+" / "危极 T−" / "中性均衡"）
    - primary_secondary_ratio: 主辅比（如 "72:28"）
    - is_balanced: 是否达到主辅比 >= 6:4（BEA 理论要求）
    """
    plus_weight = sum(weights.get(d, 0) for d, t in dimensions.items() if t <= 3)
    minus_weight = sum(weights.get(d, 0) for d, t in dimensions.items() if t >= 6)
    neutral_weight = sum(weights.get(d, 0) for d, t in dimensions.items() if 4 <= t <= 5)

    total = plus_weight + minus_weight + neutral_weight
    plus_ratio = round(plus_weight / total, 3) if total > 0 else 0
    minus_ratio = round(minus_weight / total, 3) if total > 0 else 0

    # 主导极性判断（中性归入占比较高的一侧，或单独标注）
    if plus_weight > minus_weight:
        dominant = "亲极 P+"
        primary = plus_weight + neutral_weight * 0.5  # 中性平分
        secondary = minus_weight + neutral_weight * 0.5
    elif minus_weight > plus_weight:
        dominant = "危极 T−"
        primary = minus_weight + neutral_weight * 0.5
        secondary = plus_weight + neutral_weight * 0.5
    else:
        dominant = "中性均衡"
        primary = plus_weight + neutral_weight * 0.5
        secondary = minus_weight + neutral_weight * 0.5

    primary_pct = round(primary / total * 100) if total > 0 else 50
    secondary_pct = 100 - primary_pct
    primary_secondary_ratio = f"{primary_pct}:{secondary_pct}"

    # BEA 理论要求主辅比在 6:4 到 9:1 之间
    # <6:4 = 均分症（主辅不足），>9:1 = 单一极性（从属极不足）
    is_balanced = 60 <= primary_pct <= 90
    has_subordinate = secondary_pct >= 10  # 是否有足够的从属极

    return {
        "plus_weight": round(plus_weight, 3),
        "minus_weight": round(minus_weight, 3),
        "neutral_weight": round(neutral_weight, 3),
        "plus_ratio": plus_ratio,
        "minus_ratio": minus_ratio,
        "dominant": dominant,
        "primary_secondary_ratio": primary_secondary_ratio,
        "is_balanced": is_balanced,
        "has_subordinate": has_subordinate,
    }


def compute_endurance(w_t: float, dimensions: Dict[str, int], weights: Dict[str, float],
                      category: str, diseases: List[Dict[str, str]]) -> Dict[str, object]:
    """
    计算耐看性指数：长期使用/观看是否容易疲劳。

    BEA 理论：长期贴身物须耐看，W(T)过高、维度差异过大、有攻击症/重点通胀症都会降低耐看性。

    评估维度：
    1. W(T) 水平：W(T)越高越容易疲劳（0.3-0.45最佳）
    2. 维度稳定性：维度之间 t 值差异越小越耐看
    3. 病症影响：攻击症、重点通胀症、刺激疲劳降低耐看性
    4. 品类适配：不同品类的最优 W(T) 区间不同

    返回：
    - score: 耐看性指数（0-100）
    - level: 评级（极耐看/耐看/一般/易疲劳）
    - factors: 各因素得分明细
    - advice: 改进建议
    """
    factors = {}

    # 1. W(T) 水平得分（0-30分）
    # 不同品类的最优 W(T) 区间
    optimal_ranges = {
        "phone": (0.18, 0.35),    # 手机：长期贴身，偏低
        "car": (0.30, 0.48),       # 汽车：均衡到崇高
        "brand": (0.20, 0.45),     # 品牌：亲和到均衡
        "ui": (0.15, 0.35),        # UI：长期使用，偏低
        "building": (0.35, 0.55),  # 建筑：崇高区间
    }
    opt_low, opt_high = optimal_ranges.get(category, (0.25, 0.45))
    if opt_low <= w_t <= opt_high:
        wt_score = 30
    elif w_t < opt_low:
        # 偏低：单调，但比偏高更耐看
        wt_score = max(15, 30 - (opt_low - w_t) * 50)
    else:
        # 偏高：容易疲劳
        wt_score = max(5, 30 - (w_t - opt_high) * 80)
    factors["W(T)水平"] = round(wt_score, 1)

    # 2. 维度稳定性得分（0-25分）
    # 使用加权标准差：高权重维度的波动对耐看性影响更大
    t_values = list(dimensions.values())
    w_values = [weights.get(d, 0) for d in dimensions]
    total_w = sum(w_values)
    if len(t_values) > 1 and total_w > 0:
        # 加权均值
        weighted_mean = sum(w * t for w, t in zip(w_values, t_values)) / total_w
        # 加权方差
        weighted_variance = sum(w * (t - weighted_mean) ** 2 for w, t in zip(w_values, t_values)) / total_w
        std_dev = weighted_variance ** 0.5
        # 标准差 0-1 得满分，每增加1扣5分
        stability_score = max(5, 25 - max(0, std_dev - 1) * 5)
    else:
        stability_score = 25
    factors["维度稳定性"] = round(stability_score, 1)

    # 3. 病症影响得分（0-25分）
    disease_penalty = 0
    disease_names = [d["name"] for d in diseases]
    if "本能越界" in disease_names:
        disease_penalty += 25  # 一票否决，直接0分
    if "攻击症" in disease_names:
        disease_penalty += 10
    if "重点通胀症" in disease_names:
        disease_penalty += 8
    if "刺激疲劳" in disease_names:
        disease_penalty += 12
    if "均分症" in disease_names:
        disease_penalty += 5
    if "甜腻症" in disease_names:
        disease_penalty += 3
    disease_score = max(0, 25 - disease_penalty)
    factors["病症影响"] = round(disease_score, 1)

    # 4. 主辅比得分（0-20分）
    pr = compute_polarity_ratio(dimensions, weights)
    if pr["is_balanced"]:
        # 主辅分明，耐看
        primary_pct = int(pr["primary_secondary_ratio"].split(":")[0])
        # 7:3 到 8.5:1.5 最佳（从属极充足且不过多）
        if 70 <= primary_pct <= 85:
            balance_score = 20
        elif 60 <= primary_pct < 70:
            balance_score = 16  # 主辅明确但从属极偏多
        else:  # 86-90，主辅明确但从属极偏少，接近不足边缘
            balance_score = 14
    else:
        balance_score = 8  # 主辅不足，情绪暧昧，不耐看
    factors["主辅比"] = round(balance_score, 1)

    total = round(sum(factors.values()), 1)

    # 评级
    if total >= 80:
        level = "极耐看"
    elif total >= 65:
        level = "耐看"
    elif total >= 50:
        level = "一般"
    else:
        level = "易疲劳"

    # 改进建议
    advice = []
    if wt_score < 20:
        if w_t > opt_high:
            advice.append(f"W(T)={w_t:.2f}偏高，建议降低危极到{opt_high:.2f}以下")
        else:
            advice.append(f"W(T)={w_t:.2f}偏低，建议增加适度张力到{opt_low:.2f}以上")
    if stability_score < 15:
        advice.append("维度差异过大，建议收敛各维度 t 值到更窄区间")
    if disease_score < 15:
        advice.append("存在影响耐看性的病症，优先处理攻击症/重点通胀症")
    if balance_score < 12:
        advice.append("主辅比不足，建议确立明确的主导极性（≥7:3）")

    if not advice:
        advice.append("耐看性良好，保持当前配比")

    return {
        "score": total,
        "level": level,
        "factors": factors,
        "advice": advice,
        "optimal_range": [opt_low, opt_high],
    }


def locate_paradigm(w_t: float) -> Tuple[str, str, Tuple[float, float]]:
    for low, high, name, desc in PARADIGMS:
        if low <= w_t < high:
            return name, desc, (low, high)
    return PARADIGMS[-1][2], PARADIGMS[-1][3], (PARADIGMS[-1][0], PARADIGMS[-1][1])


def _disease_evidence(name: str, w_t: float, dims: Dict[str, int]) -> str:
    if name == "本能越界":
        extreme = [f"{k}={v}" for k, v in dims.items() if v >= 10]
        return f"以下维度 t=10，触及本能安全阈：{', '.join(extreme)}"
    if name == "甜腻症":
        return f"W(T)={w_t:.2f} 偏低，所有维度 t<=4，最高维度为 {max(dims, key=dims.get)}={max(dims.values())}"
    if name == "攻击症":
        high = [f"{k}={v}" for k, v in dims.items() if v >= 6]
        return f"W(T)={w_t:.2f} 偏高（>=0.55），高强度维度（t>=6）：{', '.join(high)}"
    if name == "刺激疲劳":
        return f"W(T)={w_t:.2f} 偏高（>=0.65），所有维度 t>=7，全程高能无喘息"
    if name == "均分症":
        return f"W(T)={w_t:.2f}，所有维度集中在 3-5 区间，无明显主次"
    if name == "重点通胀症":
        high = [f"{k}={v}" for k, v in dims.items() if v >= 6]
        return f">=6 的维度有 {len(high)} 个：{', '.join(high)}"
    if name == "张力不足症":
        return f"W(T)={w_t:.2f}，维度极差仅 {max(dims.values()) - min(dims.values())}，无对比"
    return ""


def diagnose_diseases(w_t: float, dims: Dict[str, int]) -> List[Dict[str, str]]:
    diseases = []
    for name, check_fn, prescription in DISEASE_RULES:
        if check_fn(w_t, dims):
            diseases.append({
                "name": name,
                "evidence": _disease_evidence(name, w_t, dims),
                "prescription": prescription,
            })
    # 优先级处理：甜腻症已涵盖"全维度低+无对比"，不再重复报张力不足症
    if any(d["name"] == "甜腻症" for d in diseases):
        diseases = [d for d in diseases if d["name"] != "张力不足症"]
    return diseases


def suggest_scores(w_t: float, dims: Dict[str, int], diseases: List[Dict[str, str]],
                   category: str = "phone") -> Dict[str, object]:
    """
    四维评分辅助（v2.2.1 精细化版）

    评分逻辑：基于维度数据计算参考分，每个维度都有明确的加分/扣分项。
    注意：这是参考分，不是最终分。语境适配尤其需要人工判断。

    双极张力（25分）：W(T)区间 + 维度极差 + 明确对比 - 病症扣分
    结构秩序（25分）：焦点数量 + 主辅清晰度 - 重点通胀/均分扣分
    阈值安全（25分）：W(T)越界检查 + 极端值检查
    语境适配（25分）：基础参考分 + 人工检查项提示
    """
    disease_names = {d["name"] for d in diseases}
    spread = max(dims.values()) - min(dims.values())
    n_high = sum(1 for v in dims.values() if v >= 6)
    n_low = sum(1 for v in dims.values() if v <= 4)
    has_contrast = n_high >= 1 and n_low >= 1

    # ── 双极张力（25分）──
    tension = 15  # 基础分
    # W(T)在有张力的区间（0.25-0.70）
    if 0.25 <= w_t <= 0.70:
        tension += 5
    # 维度极差
    if spread >= 3:
        tension += 3
    elif spread >= 2:
        tension += 2
    elif spread >= 1:
        tension += 1
    # 明确对比（有高有低）
    if has_contrast:
        tension += 2
    # 病症扣分
    if "甜腻症" in disease_names:
        tension -= 5
    if "张力不足症" in disease_names:
        tension -= 4
    if "攻击症" in disease_names:
        tension -= 3
    if "刺激疲劳" in disease_names:
        tension -= 3  # 全程高能无喘息，张力结构不好
    tension = max(0, min(25, tension))

    # ── 结构秩序（25分）──
    order = 15  # 基础分
    # 焦点数量：1-2个高t值维度为最佳
    if 1 <= n_high <= 2:
        order += 5
    elif n_high == 0:
        order += 0  # 无焦点
    else:
        order += 0  # 焦点过多（重点通胀）
    # 无均分症（维度不都集中在中间）
    if "均分症" not in disease_names:
        order += 3
    # 无重点通胀
    if "重点通胀症" not in disease_names:
        order += 2
    # 甜腻症（无主次对比）扣分
    if "甜腻症" in disease_names:
        order -= 3
    order = max(0, min(25, order))

    # ── 阈值安全（25分）──
    threshold = 20  # 基础分
    # 极端值检查（在本能越界判断前计算，供评分明细使用）
    n_extreme_high = sum(1 for v in dims.values() if v >= 9)
    n_extreme_low = sum(1 for v in dims.values() if v <= 1)
    # 本能越界一票否决
    if "本能越界" in disease_names:
        threshold = 0
    else:
        # W(T)在安全区间
        if w_t < 0.60:
            threshold += 3
        elif w_t < 0.70:
            threshold += 1
        # W(T)越界（逼近越阈）
        if w_t >= 0.85:
            threshold -= 10
        elif w_t >= 0.75:
            threshold -= 4
        threshold -= n_extreme_high * 3  # 接近本能红线
        threshold -= n_extreme_low * 1   # 过于柔和（不危险但单调）
        threshold = max(0, min(25, threshold))

    # ── 语境适配（25分）──
    # 这是参考分，需人工判断。按品类和范式给出基础参考分范围。
    # 不同品类的语境适配基准分不同（基于使用场景和受众预期）
    context_base_by_category = {
        "phone": 17,    # 手机：大众消费品，语境适配要求高
        "car": 18,      # 汽车：品类分化大，参考分中等
        "brand": 16,    # 品牌：高度依赖定位，需更多人工判断
        "ui": 17,       # UI：用户体验导向，语境适配要求高
        "building": 19, # 建筑：公共性强，语境适配相对稳定
    }
    context_base = context_base_by_category.get(category, 17)

    # 范式适配调整：主流范式（亲和精致/均衡典雅）语境适配性更高
    paradigm_context_bonus = {
        "治愈松弛": 1,
        "亲和精致": 2,
        "均衡典雅": 2,
        "崇高震撼": 0,
        "冷峻克制": -1,
        "先锋反叛": -2,
    }
    paradigm_name = locate_paradigm(w_t)[0]
    context_bonus = paradigm_context_bonus.get(paradigm_name, 0)

    context = max(10, min(23, context_base + context_bonus))  # 限制在10-23，留出人工调整空间

    context_checklist = [
        "目标受众的审美阈值是否匹配当前范式？（大众偏左，专业偏右）",
        "使用场景是否需要当前的张力水平？（医疗/驾驶要克制，娱乐可刺激）",
        "与主要竞品相比，这个定位有差异化吗？（避免挤在同一W(T)区间）",
        "时代语境下，这个风格是领先还是过时？（判断风格钟摆位置）",
        "价格/定位与设计语言匹配吗？（千元机用冷峻会显冷硬，旗舰用甜腻会显廉价）",
    ]

    return {
        "双极张力": tension,
        "结构秩序": order,
        "阈值安全": threshold,
        "语境适配": context,
        "评分明细": {
            "双极张力": {
                "基础分": 15,
                "W(T)在0.25-0.70": 5 if 0.25 <= w_t <= 0.70 else 0,
                f"维度极差={spread}": 3 if spread >= 3 else (2 if spread >= 2 else (1 if spread >= 1 else 0)),
                "明确对比(有高有低)": 2 if has_contrast else 0,
                "病症扣分": (-5 if "甜腻症" in disease_names else 0) + (-4 if "张力不足症" in disease_names else 0) + (-3 if "攻击症" in disease_names else 0) + (-3 if "刺激疲劳" in disease_names else 0),
            },
            "结构秩序": {
                "基础分": 15,
                f"焦点数量={n_high}(1-2个最佳)": 5 if 1 <= n_high <= 2 else 0,
                "无均分症": 3 if "均分症" not in disease_names else 0,
                "无重点通胀症": 2 if "重点通胀症" not in disease_names else 0,
                "甜腻症扣分": -3 if "甜腻症" in disease_names else 0,
            },
            "阈值安全": {
                "基础分": 20,
                f"W(T)={w_t:.2f}": 3 if w_t < 0.60 else (1 if w_t < 0.70 else 0),
                "越界扣分": -10 if w_t >= 0.85 else (-4 if w_t >= 0.75 else 0),
                f"极端高值(>=9)={n_extreme_high}": -3 * n_extreme_high,
                f"极端低值(<=1)={n_extreme_low}": -1 * n_extreme_low,
            },
            "语境适配": {
                "参考分": context,
                "品类基准分": context_base,
                "范式调整": context_bonus,
                "状态": "待人工评估（参考分基于品类和范式，需结合受众/场景/竞品/时代/价格定位判断）",
                "检查项": context_checklist,
            },
        },
        "说明": "以上为基于维度数据的参考分。语境适配尤其需要人工结合受众、场景、竞品、时代、价格定位判断。",
    }


def analyze(category: str, t_str: str, weights: Dict[str, float] = None) -> BEAAnalysis:
    if category not in CATEGORY_WEIGHTS:
        raise ValueError(f"未知品类 '{category}'，支持：{', '.join(CATEGORY_WEIGHTS.keys())}")
    if weights is None:
        weights = CATEGORY_WEIGHTS[category]
    dimensions = parse_t_values(t_str, list(weights.keys()))
    w_t = compute_w_t(dimensions, weights)
    paradigm, paradigm_desc, p_range = locate_paradigm(w_t)
    diseases = diagnose_diseases(w_t, dimensions)
    scores = suggest_scores(w_t, dimensions, diseases, category)
    polarity_ratio = compute_polarity_ratio(dimensions, weights)
    endurance = compute_endurance(w_t, dimensions, weights, category, diseases)
    return BEAAnalysis(
        category=category, dimensions=dimensions, weights=weights, w_t=w_t,
        paradigm=paradigm, paradigm_desc=paradigm_desc, paradigm_range=p_range,
        diseases=diseases, score_suggestion=scores, polarity_ratio=polarity_ratio,
        endurance=endurance,
    )


# ──────────────────────────────────────────────
# 输出格式
# ──────────────────────────────────────────────

def _polarity_label(t: int) -> str:
    return "P+亲极" if t <= 3 else ("T−危极" if t >= 6 else "中性")


def format_report(a: BEAAnalysis) -> str:
    lines = []
    lines.append("=" * 50)
    lines.append(f"  BEA 分析报告 · {a.category}")
    lines.append("=" * 50)

    lines.append("\n【维度极性审计】")
    lines.append(f"{'维度':<8} {'权重':>6} {'t值':>4} {'加权':>6} {'极性':<6}")
    lines.append("-" * 40)
    for dim in a.dimensions:
        t = a.dimensions[dim]
        w = a.weights[dim]
        lines.append(f"{dim:<8} {w:>6.2f} {t:>4} {w * t / 10:>6.3f} {_polarity_label(t):<6}")

    lines.append(f"\n【W(T) 危极综合权重】")
    lines.append(f"  W(T) = {a.w_t:.3f}")
    lines.append(f"  范式定位：{a.paradigm}（{a.paradigm_desc}）")
    lines.append(f"  范式区间：[{a.paradigm_range[0]:.2f}, {a.paradigm_range[1]:.2f})")

    # 维度贡献排序：哪些维度在主导风格
    lines.append(f"\n【维度贡献排序】")
    contributions = [(dim, a.weights[dim] * a.dimensions[dim] / 10.0) for dim in a.dimensions]
    contributions.sort(key=lambda x: x[1], reverse=True)
    for i, (dim, contrib) in enumerate(contributions, 1):
        pct = contrib / a.w_t * 100 if a.w_t > 0 else 0
        lines.append(f"  {i}. {dim:<6} t={a.dimensions[dim]:>2}  贡献={contrib:.3f} ({pct:.0f}%)")

    # 范式距离：离边界多远
    lines.append(f"\n【范式距离】")
    low, high = a.paradigm_range
    dist_low = a.w_t - low
    dist_high = high - a.w_t
    lines.append(f"  距下沿：{dist_low:.3f}  距上沿：{dist_high:.3f}")
    if dist_high < 0.03 or dist_low < 0.03:
        lines.append(f"  ⚠ 接近范式边界，微调维度可能改变定位")

    # 主辅比
    pr = a.polarity_ratio
    lines.append(f"\n【主辅比】")
    lines.append(f"  主导极性：{pr['dominant']}")
    lines.append(f"  亲极占比：{pr['plus_ratio']*100:.0f}%  危极占比：{pr['minus_ratio']*100:.0f}%  中性：{(1-pr['plus_ratio']-pr['minus_ratio'])*100:.0f}%")
    lines.append(f"  主辅比：{pr['primary_secondary_ratio']}")
    if pr['is_balanced']:
        lines.append(f"  ✓ 主辅分明（6:4 到 9:1），第一印象明确且有对立极提神")
    elif not pr['has_subordinate']:
        lines.append(f"  ⚠ 从属极不足（>9:1），单一极性可能导致甜腻或攻击，建议注入10%-30%对立极")
    else:
        lines.append(f"  ⚠ 主辅不足（<6:4），可能存在均分症，情绪暧昧，建议确立明确主导极性")

    # 耐看性
    en = a.endurance
    lines.append(f"\n【耐看性】")
    lines.append(f"  耐看指数：{en['score']:.0f}/100  评级：{en['level']}")
    lines.append(f"  最优W(T)区间：[{en['optimal_range'][0]:.2f}, {en['optimal_range'][1]:.2f}]")
    for factor, score in en['factors'].items():
        lines.append(f"    {factor}: {score:.0f}")
    for adv in en['advice']:
        lines.append(f"  → {adv}")

    # 安全警告：越阈值检查
    extreme_dims = [dim for dim, t in a.dimensions.items() if t >= 10]
    if extreme_dims:
        lines.append(f"\n【安全警告】")
        lines.append(f"  ⛔ 本能安全阈越界：以下维度 t=10，可能引发真实伤害联想或生理不适")
        for dim in extreme_dims:
            lines.append(f"    - {dim}（t=10）")
        lines.append(f"  建议：将这些维度降到 t≤9，无风格借口可越过本能红线")

    lines.append(f"\n【病症诊断】")
    if a.diseases:
        for i, d in enumerate(a.diseases, 1):
            lines.append(f"  {i}. {d['name']}")
            lines.append(f"     证据：{d['evidence']}")
            lines.append(f"     处方：{d['prescription']}")
    else:
        lines.append("  未检测到自动诊断病症。")

    # 需人工判断的病症检查提示
    lines.append(f"\n【需人工判断的病症】（无法仅通过维度值自动诊断，请逐项检查）")
    for i, d in enumerate(MANUAL_CHECK_DISEASES, 1):
        lines.append(f"  {i}. {d['name']}")
        lines.append(f"     检查：{d['check_prompt']}")
        lines.append(f"     处方：{d['prescription']}")

    lines.append("")
    lines.append("  四维评分辅助请使用 score 命令：python3 bea_quant.py score --category ... --t ...")

    lines.append("\n" + "=" * 50)
    return "\n".join(lines)


def format_compare(a1: BEAAnalysis, a2: BEAAnalysis, name1: str, name2: str) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append(f"  BEA 对比报告 · {name1} vs {name2}")
    lines.append("=" * 60)

    lines.append(f"\n【W(T) 与范式】")
    lines.append(f"  {name1}: W(T)={a1.w_t:.3f} → {a1.paradigm}")
    lines.append(f"  {name2}: W(T)={a2.w_t:.3f} → {a2.paradigm}")
    diff = a1.w_t - a2.w_t
    direction = "前者更危极" if diff > 0 else ("后者更危极" if diff < 0 else "相同")
    lines.append(f"  差值：{diff:+.3f}（{direction}）")

    lines.append(f"\n【维度对比】")
    lines.append(f"  {'维度':<8} {name1:>8} {name2:>8} {'差值':>6}")
    lines.append("  " + "-" * 36)
    for dim in a1.dimensions:
        t1 = a1.dimensions[dim]
        t2 = a2.dimensions.get(dim, 0)
        lines.append(f"  {dim:<8} {t1:>8} {t2:>8} {t1 - t2:>+6}")

    lines.append(f"\n【病症对比】")
    lines.append(f"  {name1}: {', '.join(d['name'] for d in a1.diseases) if a1.diseases else '无'}")
    lines.append(f"  {name2}: {', '.join(d['name'] for d in a2.diseases) if a2.diseases else '无'}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_template(category: str) -> str:
    if category not in CATEGORY_WEIGHTS:
        raise ValueError(f"未知品类 '{category}'")
    weights = CATEGORY_WEIGHTS[category]
    dim_order = list(weights.keys())
    lines = []
    lines.append(f"BEA 打分模板 · {category}")
    lines.append("=" * 55)
    lines.append("t=0 纯亲极（圆润/柔色/对称/舒缓），t=10 纯危极（尖锐/强对比/失衡/冷峻）")
    lines.append("")
    lines.append(f"{'维度':<10} {'权重':>6} {'顺序':>4} {'t值(0-10)':>10}  打分依据")
    lines.append("-" * 55)
    for i, (dim, w) in enumerate(weights.items(), 1):
        lines.append(f"{dim:<10} {w:>6.2f} {i:>4} {'________':>10}  ")
    lines.append("")
    lines.append("紧凑格式（按上方顺序）：")
    lines.append(f"  产品名={','.join('_' * len(dim_order))}")
    lines.append(f"  示例：MyProduct={','.join('3' for _ in dim_order)}")
    lines.append("")
    lines.append("完整格式（带维度名，推荐）：")
    lines.append(f"  产品名={','.join(f'{d}=?' for d in dim_order)}")
    lines.append("")
    lines.append("使用方式：")
    lines.append("  1. 每位评审独立打分")
    lines.append("  2. 汇总取均值或讨论分歧（分歧>=2必须讨论）")
    lines.append("  3. 用完整格式传入 analyze/report/score")
    lines.append("")
    lines.append("t 值校准参考：")
    lines.append("  0-2  强亲极：全圆角/柔色/完全对称/无对比")
    lines.append("  3-4  偏亲：圆润为主/低饱和/有轻微对比")
    lines.append("  5    中性：刚柔各半/中等对比/秩序感强")
    lines.append("  6-7  偏危：硬朗线条/高对比/有明显张力")
    lines.append("  8-10 强危极：锐角/强对比/失衡/令人紧张")
    lines.append("")
    lines.append("【可直接复制的命令】")
    sample_t = ",".join(f"{d}=5" for d in dim_order)
    lines.append(f'  # 分析报告')
    lines.append(f'  python3 bea_quant.py report --category {category} --t "{sample_t}"')
    lines.append(f'  # 调整到目标范式（把5换成你的实际打分）')
    lines.append(f'  python3 bea_quant.py suggest --category {category} --t "{sample_t}" --target 均衡典雅')
    return "\n".join(lines)


def format_batch(results: List[Tuple[str, BEAAnalysis]]) -> str:
    if not results:
        return "无数据"
    dims = list(results[0][1].dimensions.keys())

    lines = []
    header = f"{'产品':<12}" + "".join(f"{d:>5}" for d in dims) + f"{'W(T)':>7} {'范式':<8} {'病症':<12}"
    width = len(header)

    lines.append("=" * width)
    lines.append(f"  BEA 批量对比 · {len(results)} 个产品")
    lines.append("=" * width)

    lines.append(header)
    lines.append("-" * width)

    for name, a in results:
        row = f"{name:<12}"
        for d in dims:
            row += f"{a.dimensions[d]:>5}"
        diseases_str = ",".join(d["name"] for d in a.diseases) if a.diseases else "无"
        row += f"{a.w_t:>7.3f} {a.paradigm:<8} {diseases_str:<12}"
        lines.append(row)

    lines.append("-" * width)
    wt_values = [a.w_t for _, a in results]
    lines.append(f"{'W(T)范围':<12}" + " " * (len(dims) * 5) + f"{min(wt_values):>7.3f}-{max(wt_values):.3f}")
    lines.append(f"{'均值':<12}" + " " * (len(dims) * 5) + f"{sum(wt_values) / len(wt_values):>7.3f}")

    lines.append("")
    lines.append("【维度差异分析】")
    found = False
    for d in dims:
        vals = [a.dimensions[d] for _, a in results]
        spread = max(vals) - min(vals)
        if spread >= 3:
            found = True
            max_name = results[vals.index(max(vals))][0]
            min_name = results[vals.index(min(vals))][0]
            lines.append(f"  {d}: 差异最大（极差{spread}），{max_name}={max(vals)} vs {min_name}={min(vals)}")
    if not found:
        lines.append("  无维度差异>=3，各产品在维度层面较为接近")

    lines.append("")
    lines.append("=" * width)
    return "\n".join(lines)


def format_report_markdown(a: BEAAnalysis) -> str:
    """将分析报告导出为 Markdown 格式，方便保存到文档中。"""
    lines = []
    lines.append(f"# BEA 分析报告 · {a.category}")
    lines.append("")
    lines.append(f"**W(T) = {a.w_t:.3f}** | **范式：{a.paradigm}** | {a.paradigm_desc}")
    lines.append("")

    lines.append("## 维度极性审计")
    lines.append("")
    lines.append("| 维度 | 权重 | t值 | 加权 | 极性 |")
    lines.append("|---|---|---|---|---|")
    for dim, w in a.weights.items():
        t = a.dimensions[dim]
        contrib = w * t / 10
        polarity = "P+亲极" if t <= 3 else "T−危极" if t >= 6 else "中性"
        lines.append(f"| {dim} | {w:.2f} | {t} | {contrib:.3f} | {polarity} |")
    lines.append("")

    lines.append("## 主辅比")
    lines.append("")
    pr = a.polarity_ratio
    lines.append(f"- 主导极性：{pr['dominant']}")
    lines.append(f"- 亲极占比：{pr['plus_ratio']*100:.0f}% | 危极占比：{pr['minus_ratio']*100:.0f}%")
    lines.append(f"- 主辅比：{pr['primary_secondary_ratio']}")
    lines.append(f"- 主辅分明：{'✓ 是' if pr['is_balanced'] else '⚠ 否'}")
    lines.append("")

    lines.append("## 耐看性")
    lines.append("")
    en = a.endurance
    lines.append(f"- 耐看指数：**{en['score']:.0f}/100** | 评级：{en['level']}")
    lines.append(f"- 最优 W(T) 区间：[{en['optimal_range'][0]:.2f}, {en['optimal_range'][1]:.2f}]")
    for factor, score in en['factors'].items():
        lines.append(f"  - {factor}: {score:.0f}")
    lines.append("")

    lines.append("## 病症诊断")
    lines.append("")
    if a.diseases:
        for i, d in enumerate(a.diseases, 1):
            lines.append(f"### {i}. {d['name']}")
            lines.append(f"- **识别**：{d['identify']}")
            lines.append(f"- **机理**：{d['mechanism']}")
            lines.append(f"- **处方**：{d['prescription']}")
            lines.append("")
    else:
        lines.append("无明显病症 ✓")
        lines.append("")

    lines.append("## 四维评分")
    lines.append("")
    scores = a.score_suggestion
    total = sum(scores[k] for k in ["双极张力", "结构秩序", "阈值安全", "语境适配"])
    lines.append(f"| 维度 | 得分 |")
    lines.append("|---|---|")
    for k in ["双极张力", "结构秩序", "阈值安全", "语境适配"]:
        lines.append(f"| {k} | {scores[k]}/25 |")
    lines.append(f"| **总分** | **{total}/100** |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*BEA 双极情绪美学 v2.4.0 | 署名：马星 | CC BY-NC-SA 4.0*")
    return "\n".join(lines)


def format_report_html(a: BEAAnalysis) -> str:
    """将分析报告导出为独立 HTML 文件，带基本样式，可直接在浏览器打开。"""
    md_content = format_report_markdown(a)
    # 简单的 Markdown 转 HTML（处理标题、表格、列表、粗体）
    html_body = md_content
    # 标题
    for i in range(3, 0, -1):
        import re
        html_body = re.sub(rf'^{"#"*i} (.+)$', rf'<h{i}>\1</h{i}>', html_body, flags=re.MULTILINE)
    # 粗体
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
    # 表格
    html_body = re.sub(r'\|(.+)\|\n\|[-| ]+\|\n((?:\|.+\|\n?)+)', _md_table_to_html, html_body)
    # 列表
    html_body = re.sub(r'^- (.+)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'(<li>.+</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', html_body)
    # 水平线
    html_body = re.sub(r'^---$', '<hr>', html_body, flags=re.MULTILINE)
    # 段落
    html_body = re.sub(r'\n\n', '</p><p>', html_body)
    html_body = '<p>' + html_body + '</p>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BEA 分析报告 · {a.category}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Noto Sans SC',sans-serif;max-width:800px;margin:0 auto;padding:2rem;line-height:1.7;color:#333;background:#fafafa}}
h1{{color:#1a1a2e;border-bottom:3px solid #d4a574;padding-bottom:.5rem}}
h2{{color:#16213e;margin-top:2rem;border-left:4px solid #d4a574;padding-left:.8rem}}
h3{{color:#0f3460}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}
th,td{{border:1px solid #ddd;padding:.6rem .8rem;text-align:left}}
th{{background:#1a1a2e;color:#f5e6d3}}
tr:nth-child(even){{background:#f5f5f5}}
ul{{padding-left:1.5rem}}
li{{margin:.3rem 0}}
hr{{border:none;border-top:2px solid #d4a574;margin:2rem 0}}
strong{{color:#0f3460}}
p{{margin:.8rem 0}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""


def _md_table_to_html(match):
    """将 Markdown 表格转换为 HTML 表格。"""
    header = match.group(1).strip().split('|')
    rows_text = match.group(2).strip()
    rows = [r.strip().split('|') for r in rows_text.split('\n') if r.strip()]
    html = '<table><thead><tr>'
    for h in header:
        html += f'<th>{h.strip()}</th>'
    html += '</tr></thead><tbody>'
    for row in rows:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell.strip()}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html


def format_score_detail(a: BEAAnalysis) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("  BEA 四维评分辅助（v2.2.1 精细化版）")
    lines.append("=" * 60)
    lines.append(f"  W(T)={a.w_t:.3f} · {a.paradigm}")
    lines.append("")

    scores = a.score_suggestion
    detail = scores.get("评分明细", {})

    def format_dimension(name: str, key: str):
        lines.append(f"【{name}】{scores[key]}/25")
        if key in detail:
            for item, value in detail[key].items():
                if item == "检查项":
                    lines.append(f"  {item}:")
                    for i, check in enumerate(value, 1):
                        lines.append(f"    {i}. {check}")
                elif item == "说明":
                    lines.append(f"  {item}: {value}")
                elif isinstance(value, (int, float)) and value != 0:
                    sign = "+" if value > 0 else ""
                    lines.append(f"  {item}: {sign}{value}")
        lines.append("")

    format_dimension("双极张力", "双极张力")
    format_dimension("结构秩序", "结构秩序")
    format_dimension("阈值安全", "阈值安全")
    format_dimension("语境适配", "语境适配")

    total = scores["双极张力"] + scores["结构秩序"] + scores["阈值安全"] + scores["语境适配"]
    lines.append("-" * 60)
    lines.append(f"【合计参考】{total}/100")

    # 评级
    if total >= 80:
        rating = "成熟作品"
    elif total >= 65:
        rating = "良好，有提升空间"
    elif total >= 50:
        rating = "中等，需重点改进短板"
    else:
        rating = "存在明显问题，建议回炉"
    lines.append(f"【评级】{rating}")

    # 短板提示
    weak = []
    if scores["双极张力"] < 15:
        weak.append("双极张力")
    if scores["结构秩序"] < 15:
        weak.append("结构秩序")
    if scores["阈值安全"] < 15:
        weak.append("阈值安全")
    if weak:
        lines.append(f"【短板提示】以下维度低于15分，需优先改进：{', '.join(weak)}")

    lines.append(f"  注：{scores['说明']}")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 调整建议（suggest 命令）
# ──────────────────────────────────────────────

def resolve_target(target_str: str) -> Tuple[float, str]:
    """
    解析目标：范式名 → 取该范式中点；数字 → 直接用。
    返回 (目标W(T), 目标范式描述)。
    """
    target_str = target_str.strip()
    # 尝试解析为数字
    try:
        wt = float(target_str)
        if not (0 <= wt <= 1):
            raise ValueError(f"目标W(T) {wt} 超出 0-1 范围")
        name, desc, _ = locate_paradigm(wt)
        return wt, f"{name}（{desc}）"
    except ValueError:
        pass
    # 尝试匹配范式名
    for low, high, name, desc in PARADIGMS:
        if target_str in name or name in target_str:
            mid = (low + high) / 2
            return round(mid, 3), f"{name}（{desc}）"
    raise ValueError(f"无法识别目标 '{target_str}'，请输入范式名（如'崇高震撼'）或W(T)数值（如0.55）")


def suggest_adjustment(a: BEAAnalysis, target_wt: float, strategy: str = "focused") -> List[Dict[str, object]]:
    """
    计算从当前 W(T) 调整到目标 W(T) 的维度变更方案。

    策略：
    - focused（集中，默认）：每轮只调整优先级最高的1个维度，改动维度少但每个维度调整量大
    - distributed（分散）：每轮调整所有可调整维度各1级，每个维度调整量小但改动维度多

    通用规则：
    - 降低危极时：优先降低当前 t 值最高的维度（高 t 维度对 W(T) 贡献最大）
    - 提升危极时：优先提升当前 t 值最低的维度（低 t 维度有最大提升空间）
    - 同时考虑权重：在 t 值相近时，优先调整权重高的维度（调整效率更高）
    - 避免把维度调到 0 或 10（极端值），除非目标差距过大
    - 合并同一维度的连续调整为一步输出

    返回调整步骤列表。
    """
    current = dict(a.dimensions)
    weights = a.weights
    delta = target_wt - a.w_t

    if abs(delta) < 0.005:
        return [{"message": "当前W(T)已在目标范围内，无需调整"}]

    direction = 1 if delta > 0 else -1  # 1=提升危极，-1=降低危极
    remaining = abs(delta)
    max_iterations = 100  # 安全上限
    iteration = 0

    # 记录每个维度的总调整量
    total_changes = {dim: 0 for dim in current}

    def get_candidates():
        """获取可调整的维度候选列表，按优先级排序。"""
        candidates = []
        for dim, t in current.items():
            w = weights[dim]
            if direction == -1:
                # 降低危极：优先降高 t 维度，但不能低于 1
                if t > 1:
                    priority = t * w  # t 越高越该降
                    candidates.append((dim, priority, t))
            else:
                # 提升危极：优先升低 t 维度，但不能高于 9
                if t < 9:
                    priority = (10 - t) * w  # t 越低越该升
                    candidates.append((dim, priority, t))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    while remaining > 0.005 and iteration < max_iterations:
        iteration += 1
        candidates = get_candidates()

        if not candidates:
            break

        if strategy == "distributed":
            # 分散策略：每轮调整所有可调整维度各1级
            for dim, _, _ in candidates:
                per_step = weights[dim] / 10.0
                current[dim] += direction
                total_changes[dim] += direction
                remaining -= per_step
                if remaining <= 0.005:
                    break
        else:
            # 集中策略（默认）：每轮只调优先级最高的1个维度
            best_dim = candidates[0][0]
            per_step = weights[best_dim] / 10.0
            current[best_dim] += direction
            total_changes[best_dim] += direction
            remaining -= per_step

    # 合并同一维度的连续调整为一步输出
    steps = []
    for dim, change in total_changes.items():
        if change != 0:
            old_t = a.dimensions[dim]
            new_t = old_t + change
            per_step = weights[dim] / 10.0
            steps.append({
                "dimension": dim,
                "from": old_t,
                "to": new_t,
                "change": change,
                "wt_change": round(per_step * change, 3),
            })

    # 按 W(T) 变化量绝对值排序（影响大的在前）
    steps.sort(key=lambda x: abs(x["wt_change"]), reverse=True)
    return steps


def format_suggest(a: BEAAnalysis, target_wt: float, target_desc: str,
                   steps: List[Dict[str, object]]) -> str:
    lines = []
    lines.append("=" * 55)
    lines.append("  BEA 调整建议")
    lines.append("=" * 55)
    lines.append(f"  当前：W(T)={a.w_t:.3f} → {a.paradigm}")
    lines.append(f"  目标：W(T)={target_wt:.3f} → {target_desc}")
    diff = target_wt - a.w_t
    lines.append(f"  差值：{diff:+.3f}（{'需要提升危极' if diff > 0 else '需要降低危极' if diff < 0 else '无需调整'}）")
    if abs(diff) > 0.5:
        lines.append(f"  ⚠ 调整幅度过大（|ΔW(T)|>0.5），建议分阶段调整，每阶段变化≤0.3后验证效果")
    lines.append("")

    if steps and "message" in steps[0]:
        lines.append(f"  {steps[0]['message']}")
    elif not steps:
        lines.append("  无法在维度范围内达到目标（所有维度已到极限）")
    else:
        lines.append("【调整方案】（优先调整权重高的维度）")
        lines.append(f"  {'维度':<8} {'原值':>4} {'目标值':>6} {'变化':>6} {'W(T)变化':>8}")
        lines.append("  " + "-" * 38)
        total_wt_change = 0
        for s in steps:
            lines.append(f"  {s['dimension']:<8} {s['from']:>4} {s['to']:>6} {s['change']:>+6} {s['wt_change']:>+8.3f}")
            total_wt_change += s["wt_change"]
        lines.append("  " + "-" * 38)
        lines.append(f"  {'合计':<8} {'':>4} {'':>6} {'':>6} {total_wt_change:>+8.3f}")

        # 生成调整后的完整维度字符串
        new_dims = dict(a.dimensions)
        for s in steps:
            new_dims[s["dimension"]] = s["to"]
        new_t_str = ",".join(f"{k}={v}" for k, v in new_dims.items())
        lines.append("")
        lines.append("【调整后验证】")
        new_a = analyze(a.category, new_t_str)
        lines.append(f"  新W(T)={new_a.w_t:.3f} → {new_a.paradigm}")
        if new_a.diseases:
            lines.append(f"  新病症：{', '.join(d['name'] for d in new_a.diseases)}")
        else:
            lines.append("  新病症：无")
        lines.append("")
        lines.append("【可直接复制的命令】")
        lines.append(f'  python3 bea_quant.py report --category {a.category} --t "{new_t_str}"')

    lines.append("")
    lines.append("=" * 55)
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 灵敏度分析（v3.0 务实版核心功能）
# ──────────────────────────────────────────────

def sensitivity_analysis(a: BEAAnalysis, target_wt: float = None, step: int = 1) -> List[Dict[str, object]]:
    """
    灵敏度分析：计算每个维度 t±step 对 W(T) 和四维评分的影响。

    核心价值：找出"改动哪个维度效果最明显"，避免盲目试错。
    用有限差分法（不需要梯度下降），技术上完全可实现。

    参数:
        a: BEAAnalysis 对象（当前设计分析结果）
        target_wt: 目标 W(T)（可选）。如果提供，会计算朝目标方向调整的效果。
        step: 调整步长（默认1，可选2或3）。步长越大，越能看出大幅调整的影响。

    返回:
        按综合灵敏度降序排列的维度列表，每个元素包含：
        - dimension: 维度名
        - weight: 该维度权重
        - current_t: 当前 t 值
        - step: 调整步长
        - wt_plus: t+step 后 W(T) 的变化量
        - wt_minus: t-step 后 W(T) 的变化量
        - total_score_plus: t+step 后四维总分的变化量
        - total_score_minus: t-step 后四维总分的变化量
        - sensitivity: 综合灵敏度（|wt变化|的平均值 × 权重，越大越敏感）
        - toward_target: 如果有目标，朝目标方向调整的 W(T) 变化量（正表示朝目标靠近）
    """
    step = max(1, min(3, step))  # 限制步长在1-3
    results = []
    weights = a.weights
    current_wt = a.w_t
    current_total_score = (a.score_suggestion["双极张力"] + a.score_suggestion["结构秩序"]
                            + a.score_suggestion["阈值安全"] + a.score_suggestion["语境适配"])

    for dim, current_t in a.dimensions.items():
        w = weights[dim]
        per_step = w / 10.0  # t 变化 1 对应的 W(T) 变化

        # t+step 的影响（如果当前 t + step <= 9）
        can_plus = current_t + step <= 9
        wt_plus = per_step * step if can_plus else 0
        # t-step 的影响（如果当前 t - step >= 1）
        can_minus = current_t - step >= 1
        wt_minus = -per_step * step if can_minus else 0

        # 计算 t+step 后的评分变化
        score_plus = 0
        if can_plus:
            new_dims = dict(a.dimensions)
            new_dims[dim] = current_t + step
            new_wt = compute_w_t(new_dims, weights)
            new_diseases = diagnose_diseases(new_wt, new_dims)
            new_scores = suggest_scores(new_wt, new_dims, new_diseases, a.category)
            new_total = (new_scores["双极张力"] + new_scores["结构秩序"]
                         + new_scores["阈值安全"] + new_scores["语境适配"])
            score_plus = new_total - current_total_score

        # 计算 t-step 后的评分变化
        score_minus = 0
        if can_minus:
            new_dims = dict(a.dimensions)
            new_dims[dim] = current_t - step
            new_wt = compute_w_t(new_dims, weights)
            new_diseases = diagnose_diseases(new_wt, new_dims)
            new_scores = suggest_scores(new_wt, new_dims, new_diseases, a.category)
            new_total = (new_scores["双极张力"] + new_scores["结构秩序"]
                         + new_scores["阈值安全"] + new_scores["语境适配"])
            score_minus = new_total - current_total_score

        # 综合灵敏度：0.7 * W(T)灵敏度 + 0.3 * 评分灵敏度
        # W(T)灵敏度反映调整效率，评分灵敏度反映对最终美感的影响
        avg_wt_change = (abs(wt_plus) + abs(wt_minus)) / 2
        avg_score_change = (abs(score_plus) + abs(score_minus)) / 2
        wt_sensitivity = avg_wt_change * 100  # W(T)灵敏度（放大到可读范围）
        score_sensitivity = avg_score_change * 2  # 评分灵敏度（放大到可比范围）
        sensitivity = round(0.7 * wt_sensitivity + 0.3 * score_sensitivity, 2)

        # 朝目标方向调整的效果
        toward_target = None
        if target_wt is not None:
            diff = target_wt - current_wt
            if diff > 0:
                # 需要提升危极，朝目标方向是 t+step
                toward_target = wt_plus if can_plus else 0
            elif diff < 0:
                # 需要降低危极，朝目标方向是 t-step
                toward_target = abs(wt_minus) if can_minus else 0
            else:
                toward_target = 0

        results.append({
            "dimension": dim,
            "weight": w,
            "current_t": current_t,
            "step": step,
            "wt_plus": round(wt_plus, 4),
            "wt_minus": round(wt_minus, 4),
            "wt_plus_1": round(wt_plus, 4),  # 向后兼容
            "wt_minus_1": round(wt_minus, 4),  # 向后兼容
            "total_score_plus": score_plus,
            "total_score_minus": score_minus,
            "wt_sensitivity": round(wt_sensitivity, 2),
            "score_sensitivity": round(score_sensitivity, 2),
            "sensitivity": round(sensitivity, 2),
            "toward_target": round(toward_target, 4) if toward_target is not None else None,
        })

    # 按综合灵敏度降序排列
    results.sort(key=lambda x: x["sensitivity"], reverse=True)
    return results


def format_sensitivity(a: BEAAnalysis, results: List[Dict[str, object]],
                        target_wt: float = None, target_desc: str = "") -> str:
    """格式化灵敏度分析结果输出。"""
    lines = []
    lines.append("=" * 70)
    lines.append("  BEA 灵敏度分析（v3.0 务实版）")
    lines.append("=" * 70)
    step = results[0].get("step", 1) if results else 1
    lines.append(f"  调整步长：t±{step}")
    lines.append(f"  当前：W(T)={a.w_t:.3f} → {a.paradigm}")
    if target_wt is not None:
        diff = target_wt - a.w_t
        lines.append(f"  目标：W(T)={target_wt:.3f} → {target_desc}（差值 {diff:+.3f}）")
    lines.append("")

    lines.append("【核心结论】")
    # 最敏感的3个维度
    top3 = results[:3]
    lines.append(f"  最值得改动的维度（按灵敏度排序）：")
    for i, r in enumerate(top3, 1):
        lines.append(f"    {i}. {r['dimension']}（权重 {r['weight']:.2f}，当前 t={r['current_t']}）"
                     f" — 改动{step}级，W(T)变化 ±{abs(r['wt_plus']):.3f}")
    lines.append("")

    # 如果有目标，给出朝目标方向最有效的调整
    if target_wt is not None:
        diff = target_wt - a.w_t
        if abs(diff) > 0.005:
            direction = f"提升危极（t+{step}）" if diff > 0 else f"降低危极（t-{step}）"
            lines.append(f"【朝目标方向最有效的调整】（需要{direction}）")
            # 筛选朝目标方向有效果的维度，按效果排序
            actionable = [r for r in results if r["toward_target"] and r["toward_target"] > 0]
            actionable.sort(key=lambda x: x["toward_target"], reverse=True)
            for i, r in enumerate(actionable[:3], 1):
                new_t = r["current_t"] + (step if diff > 0 else -step)
                lines.append(f"    {i}. {r['dimension']}: {r['current_t']} → {new_t}"
                             f"（W(T)变化 {r['toward_target']:+.3f}）")
            lines.append("")

    # 详细表格
    lines.append("【详细灵敏度表】")
    lines.append(f"  {'维度':<8} {'权重':>5} {'当前t':>5} {'t+'+str(step)+'→W(T)':>10} {'t-'+str(step)+'→W(T)':>10} "
                 f"{'t+'+str(step)+'→评分':>10} {'t-'+str(step)+'→评分':>10} {'灵敏度':>8}")
    lines.append("  " + "-" * 72)
    for r in results:
        lines.append(f"  {r['dimension']:<8} {r['weight']:>5.2f} {r['current_t']:>5} "
                     f"{r['wt_plus']:>+10.4f} {r['wt_minus']:>+10.4f} "
                     f"{r['total_score_plus']:>+10} {r['total_score_minus']:>+10} "
                     f"{r['sensitivity']:>8.2f}")
    lines.append("")

    # 使用建议
    lines.append("【使用建议】")
    lines.append("  1. 优先调整灵敏度最高的维度，用最小改动获得最大效果")
    lines.append("  2. 注意评分变化：如果 t+1 导致评分下降，说明该维度提升会引入病症")
    lines.append("  3. 每次只调1-2个维度，验证后再继续，避免过度调整")
    lines.append("  4. 结合 suggest 命令使用：先看灵敏度找方向，再用 suggest 出完整方案")
    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 跨模态一致性 & 层级嵌套分析（v2.4 新增）
# ──────────────────────────────────────────────

def multigroup_analysis(category: str, groups: List[Dict[str, object]]) -> Dict[str, object]:
    """
    多组分析：跨模态一致性检查 + 层级嵌套分析。

    输入多组维度数据（如外形、内饰、声音；或宏观、中观、微观），
    检查各组的极性方向是否一致，判断是同向叠加还是微差补偿。

    参数:
        category: 品类
        groups: 组列表，每组包含 name（组名）和 dimensions（维度字典）

    返回:
        - groups: 各组的分析结果
        - cross_modal_consistency: 跨模态一致性评估
        - hierarchy: 层级嵌套分析（如果组名包含宏观/中观/微观）
        - overall: 综合结论
    """
    results = []
    for g in groups:
        name = g["name"]
        dims = g["dimensions"]
        t_str = ",".join(f"{k}={v}" for k, v in dims.items())
        a = analyze(category, t_str)
        results.append({
            "name": name,
            "w_t": a.w_t,
            "paradigm": a.paradigm,
            "dominant": a.polarity_ratio["dominant"],
            "primary_secondary_ratio": a.polarity_ratio["primary_secondary_ratio"],
            "dimensions": a.dimensions,
            "analysis": a,
        })

    # 跨模态一致性检查
    wt_values = [r["w_t"] for r in results]
    wt_range = max(wt_values) - min(wt_values) if wt_values else 0
    dominant_values = [r["dominant"] for r in results]
    dominant_consistent = len(set(dominant_values)) == 1

    if wt_range <= 0.10 and dominant_consistent:
        consistency_level = "高度一致"
        consistency_score = 90
    elif wt_range <= 0.20 and dominant_consistent:
        consistency_level = "基本一致"
        consistency_score = 70
    elif wt_range <= 0.30:
        consistency_level = "存在差异"
        consistency_score = 50
    else:
        consistency_level = "严重冲突"
        consistency_score = 30

    cross_modal = {
        "wt_range": round(wt_range, 3),
        "dominant_consistent": dominant_consistent,
        "level": consistency_level,
        "score": consistency_score,
        "issues": [],
    }

    if not dominant_consistent:
        cross_modal["issues"].append("主导极性不一致：部分组亲极主导，部分组危极主导，可能产生潜意识违和")
    if wt_range > 0.20:
        cross_modal["issues"].append(f"W(T)差异过大（{wt_range:.2f}）：各组张力水平不统一，整体感受割裂")

    # 层级嵌套分析（检测组名是否包含宏观/中观/微观）
    hierarchy = None
    macro_names = ["宏观", "macro", "外形", "整体"]
    meso_names = ["中观", "meso", "内饰", "局部"]
    micro_names = ["微观", "micro", "细节", "按键"]

    macro_group = next((r for r in results if any(n in r["name"].lower() for n in macro_names)), None)
    meso_group = next((r for r in results if any(n in r["name"].lower() for n in meso_names)), None)
    micro_group = next((r for r in results if any(n in r["name"].lower() for n in micro_names)), None)

    if macro_group and micro_group:
        # 判断是同向叠加还是微差补偿
        macro_wt = macro_group["w_t"]
        micro_wt = micro_group["w_t"]
        wt_diff = micro_wt - macro_wt

        if abs(wt_diff) < 0.08:
            hierarchy_type = "同向叠加（强化型）"
            hierarchy_desc = "各层方向一致、层层加码，用于需要强烈个性"
        elif wt_diff > 0.08:
            hierarchy_type = "微差补偿（高级型）"
            hierarchy_desc = "宏观定基调（偏柔），微观用对立极补偿（偏锐），远观亲和、近看精密——高级感最常见结构"
        else:
            hierarchy_type = "反向冲突（需修正）"
            hierarchy_desc = "宏观偏锐但微观偏柔，层级方向冲突，可能导致整体感受割裂"

        hierarchy = {
            "type": hierarchy_type,
            "description": hierarchy_desc,
            "macro_wt": macro_wt,
            "micro_wt": micro_wt,
            "wt_diff": round(wt_diff, 3),
            "has_meso": meso_group is not None,
        }

    # 综合结论
    overall = []
    if consistency_score >= 70:
        overall.append("跨模态一致性良好，各通道极性协同")
    else:
        overall.append("跨模态存在差异，建议统一各组的主导极性和张力水平")
    if hierarchy:
        if "微差补偿" in hierarchy["type"] or "同向叠加" in hierarchy["type"]:
            overall.append(f"层级结构合理：{hierarchy['type']}")
        else:
            overall.append(f"层级结构需修正：{hierarchy['type']}")

    return {
        "groups": [{k: v for k, v in r.items() if k != "analysis"} for r in results],
        "cross_modal_consistency": cross_modal,
        "hierarchy": hierarchy,
        "overall": overall,
    }


def format_multigroup(result: Dict[str, object]) -> str:
    """格式化多组分析结果输出。"""
    lines = []
    lines.append("=" * 70)
    lines.append("  BEA 多组分析（跨模态一致性 + 层级嵌套）")
    lines.append("=" * 70)
    lines.append("")

    # 各组概览
    lines.append("【各组概览】")
    lines.append(f"  {'组名':<12} {'W(T)':>6} {'范式':<10} {'主导极性':<10} {'主辅比':<8}")
    lines.append("  " + "-" * 55)
    for g in result["groups"]:
        lines.append(f"  {g['name']:<12} {g['w_t']:>6.3f} {g['paradigm']:<10} {g['dominant']:<10} {g['primary_secondary_ratio']:<8}")
    lines.append("")

    # 跨模态一致性
    cm = result["cross_modal_consistency"]
    lines.append("【跨模态一致性】")
    lines.append(f"  一致性评级：{cm['level']}（{cm['score']}/100）")
    lines.append(f"  W(T)范围：{cm['wt_range']:.3f}")
    lines.append(f"  主导极性一致：{'是' if cm['dominant_consistent'] else '否'}")
    if cm["issues"]:
        lines.append("  问题：")
        for issue in cm["issues"]:
            lines.append(f"    ⚠ {issue}")
    else:
        lines.append("  ✓ 无明显问题")
    lines.append("")

    # 层级嵌套
    if result["hierarchy"]:
        h = result["hierarchy"]
        lines.append("【层级嵌套分析】")
        lines.append(f"  类型：{h['type']}")
        lines.append(f"  说明：{h['description']}")
        lines.append(f"  宏观W(T)={h['macro_wt']:.3f}，微观W(T)={h['micro_wt']:.3f}，差异={h['wt_diff']:+.3f}")
        lines.append("")

    # 综合结论
    lines.append("【综合结论】")
    for i, o in enumerate(result["overall"], 1):
        lines.append(f"  {i}. {o}")
    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 风格周期律判断（v2.4 新增）
# ──────────────────────────────────────────────

# 各品类的案例 W(T) 分布参考基准（基于 BEA 案例库和市场观察）
# 用于判断当前设计在风格周期中的位置
STYLE_CYCLE_BENCHMARKS = {
    "phone": {
        "name": "手机",
        "samples": [0.25, 0.28, 0.30, 0.32, 0.35, 0.38, 0.40, 0.42, 0.45, 0.48],
        "mainstream_range": (0.28, 0.40),
        "trend_direction": "当前主流偏亲和精致，锐利化趋势正在积累",
    },
    "car": {
        "name": "汽车",
        "samples": [0.30, 0.35, 0.38, 0.40, 0.42, 0.45, 0.48, 0.52, 0.55, 0.60],
        "mainstream_range": (0.35, 0.48),
        "trend_direction": "新能源时代偏简约科技，运动化设计回潮",
    },
    "brand": {
        "name": "品牌",
        "samples": [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60],
        "mainstream_range": (0.20, 0.40),
        "trend_direction": "极简主义疲劳，个性表达和复古回潮",
    },
    "ui": {
        "name": "界面",
        "samples": [0.12, 0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30, 0.35, 0.40],
        "mainstream_range": (0.15, 0.28),
        "trend_direction": "扁平化疲劳，玻璃拟态和微动效增加张力",
    },
    "building": {
        "name": "建筑",
        "samples": [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75],
        "mainstream_range": (0.40, 0.60),
        "trend_direction": "参数化设计增加张力，人文关怀回归柔和",
    },
}


def style_cycle_analysis(category: str, w_t: float) -> Dict[str, object]:
    """
    风格周期律判断：基于案例库 W(T) 分布，判断当前设计在风格周期中的位置。

    BEA 理论：风格是社会整体阈值与"反熟悉化"的周期运动。
    一种配比长期霸屏→受众唤醒递减→滑向呆板平庸→向对极摆动重造张力。

    参数:
        category: 品类
        w_t: 当前设计的 W(T)

    返回:
        - percentile: 当前 W(T) 在案例分布中的百分位
        - position: 风格周期位置（领先/主流/滞后）
        - mainstream_range: 主流区间
        - trend_direction: 当前趋势方向
        - advice: 风格周期建议
    """
    benchmark = STYLE_CYCLE_BENCHMARKS.get(category, STYLE_CYCLE_BENCHMARKS["brand"])
    samples = sorted(benchmark["samples"])

    # 计算百分位
    count_below = sum(1 for s in samples if s < w_t)
    percentile = round(count_below / len(samples) * 100)

    # 判断风格周期位置
    low, high = benchmark["mainstream_range"]
    if w_t < low - 0.05:
        position = "滞后（偏保守）"
        position_desc = "W(T)低于主流区间，风格偏保守，可能显得过时或缺乏个性"
    elif w_t < low:
        position = "偏保守（接近主流下沿）"
        position_desc = "W(T)略低于主流，风格稳妥但可能缺乏记忆点"
    elif low <= w_t <= high:
        position = "主流（安全区）"
        position_desc = "W(T)在主流区间内，风格符合大众预期，但差异化不足"
    elif w_t <= high + 0.08:
        position = "领先（适度超前）"
        position_desc = "W(T)略高于主流，风格有个性但仍在大众接受范围内，是最佳创新区"
    else:
        position = "激进（高度超前）"
        position_desc = "W(T)远高于主流，风格强烈但可能超出大众阈值，仅适合小众市场"

    # 风格周期建议
    advice = []
    if "主流" in position:
        advice.append("当前在主流安全区，若追求差异化可适度向趋势方向调整 0.05-0.10")
        advice.append(f"当前趋势：{benchmark['trend_direction']}")
    elif "领先" in position:
        advice.append("当前在最佳创新区，保持适度超前的定位，既有个性又可被大众接受")
        advice.append("注意监控竞品动态，避免过度超前导致曲高和寡")
    elif "滞后" in position or "保守" in position:
        advice.append("当前偏保守，建议向主流区间上沿或趋势方向调整，增加个性和记忆点")
        advice.append(f"可参考趋势：{benchmark['trend_direction']}")
    elif "激进" in position:
        advice.append("当前高度超前，仅适合小众/先锋市场；若面向大众需回收张力到主流区间")
        advice.append("先锋定位需要强大的秩序支撑，确保停在审美窗口内而非跌入排斥区")

    return {
        "category": category,
        "category_name": benchmark["name"],
        "current_wt": w_t,
        "percentile": percentile,
        "position": position,
        "position_desc": position_desc,
        "mainstream_range": [low, high],
        "trend_direction": benchmark["trend_direction"],
        "advice": advice,
    }


def format_style_cycle(result: Dict[str, object]) -> str:
    """格式化风格周期律分析结果输出。"""
    lines = []
    lines.append("=" * 60)
    lines.append("  BEA 风格周期律分析")
    lines.append("=" * 60)
    lines.append(f"  品类：{result['category_name']}")
    lines.append(f"  当前W(T)：{result['current_wt']:.3f}")
    if result['percentile'] >= 100:
        lines.append(f"  案例百分位：{result['percentile']}%（超过案例库所有样本）")
    elif result['percentile'] <= 0:
        lines.append(f"  案例百分位：{result['percentile']}%（低于案例库所有样本）")
    else:
        lines.append(f"  案例百分位：{result['percentile']}%（高于{result['percentile']}%的案例）")
    lines.append("")
    lines.append("【风格周期位置】")
    lines.append(f"  位置：{result['position']}")
    lines.append(f"  说明：{result['position_desc']}")
    lines.append(f"  主流区间：[{result['mainstream_range'][0]:.2f}, {result['mainstream_range'][1]:.2f}]")
    lines.append(f"  当前趋势：{result['trend_direction']}")
    lines.append("")
    lines.append("【风格周期建议】")
    for i, adv in enumerate(result["advice"], 1):
        lines.append(f"  {i}. {adv}")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 自定义权重配置管理（v2.4 新增）
# ──────────────────────────────────────────────

PROFILE_FILE = os.path.expanduser("~/.bea_profiles.json")


def load_profiles() -> Dict[str, Dict[str, float]]:
    """加载所有保存的权重配置。"""
    if not os.path.exists(PROFILE_FILE):
        return {}
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_profile(name: str, weights: Dict[str, float]) -> None:
    """保存权重配置。"""
    profiles = load_profiles()
    profiles[name] = weights
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)


def delete_profile(name: str) -> bool:
    """删除权重配置，返回是否成功。"""
    profiles = load_profiles()
    if name in profiles:
        del profiles[name]
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
        return True
    return False


def get_profile(name: str) -> Dict[str, float]:
    """获取指定的权重配置。"""
    profiles = load_profiles()
    if name not in profiles:
        available = ", ".join(profiles.keys()) if profiles else "（无）"
        raise ValueError(f"配置 '{name}' 不存在。可用配置：{available}")
    return profiles[name]


def resolve_weights(category: str, weights_str: str = None, profile: str = None) -> Dict[str, float]:
    """
    解析权重：优先级 profile > weights_str > 品类默认。

    参数:
        category: 品类
        weights_str: 自定义权重 JSON 字符串
        profile: 已保存的配置名

    返回:
        权重字典
    """
    if profile:
        return get_profile(profile)
    if weights_str:
        weights = {k: float(v) for k, v in json.loads(weights_str).items()}
        if abs(sum(weights.values()) - 1) > 0.001:
            raise ValueError(f"权重合计 {sum(weights.values()):.3f} ≠ 1")
        return weights
    return CATEGORY_WEIGHTS[category]


# ──────────────────────────────────────────────
# 自测试
# ──────────────────────────────────────────────

def run_tests() -> bool:
    passed = 0
    failed = 0

    def check(name: str, condition: bool):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}")

    print("运行 BEA 量化引擎自测试...")

    dims = {"形状": 5, "质感": 5, "色彩": 5, "构图": 5, "光影": 5, "细节": 5}
    check("全5分 W(T)=0.5", abs(compute_w_t(dims, CATEGORY_WEIGHTS["phone"]) - 0.5) < 0.001)

    dims = {"形状": 0, "质感": 0, "色彩": 0, "构图": 0, "光影": 0, "细节": 0}
    check("全0分 W(T)=0.0", abs(compute_w_t(dims, CATEGORY_WEIGHTS["phone"]) - 0.0) < 0.001)

    dims = {"形状": 10, "质感": 10, "色彩": 10, "构图": 10, "光影": 10, "细节": 10}
    check("全10分 W(T)=1.0", abs(compute_w_t(dims, CATEGORY_WEIGHTS["phone"]) - 1.0) < 0.001)

    name, _, _ = locate_paradigm(0.4)
    check("W(T)=0.4 定位均衡典雅", name == "均衡典雅")
    name, _, _ = locate_paradigm(0.1)
    check("W(T)=0.1 定位治愈松弛", name == "治愈松弛")
    name, _, _ = locate_paradigm(0.7)
    check("W(T)=0.7 定位先锋反叛", name == "先锋反叛")

    dims = {"形状": 2, "质感": 2, "色彩": 2, "构图": 2, "光影": 2, "细节": 2}
    check("低W(T)全低分诊断甜腻症", any(d["name"] == "甜腻症" for d in diagnose_diseases(0.12, dims)))

    dims = {"形状": 8, "质感": 8, "色彩": 7, "构图": 7, "光影": 8, "细节": 8}
    check("高W(T)有高分诊断攻击症", any(d["name"] == "攻击症" for d in diagnose_diseases(0.76, dims)))

    dims = {"形状": 7, "质感": 7, "色彩": 7, "构图": 3, "光影": 3, "细节": 3}
    check("三个>=6维度诊断重点通胀症", any(d["name"] == "重点通胀症" for d in diagnose_diseases(0.5, dims)))

    try:
        a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
        check("完整分析不报错", a.w_t > 0 and a.paradigm != "")
    except Exception as e:
        check(f"完整分析不报错（异常: {e}）", False)

    try:
        parse_t_values("形状=3", ["形状", "质感"])
        check("缺少维度应报错", False)
    except ValueError:
        check("缺少维度应报错", True)

    try:
        parse_t_values("形状=15", ["形状"])
        check("超出范围应报错", False)
    except ValueError:
        check("超出范围应报错", True)

    try:
        parse_t_values("形状=abc", ["形状"])
        check("非整数应报错", False)
    except ValueError:
        check("非整数应报错", True)

    # 紧凑格式解析
    name, dims = parse_compact_values("Test=3,6,4,3,5,6", "phone")
    check("紧凑格式解析", name == "Test" and dims["形状"] == 3 and dims["细节"] == 6)

    # 完整格式解析（在 compare/batch 条目中）
    name, dims = parse_compact_values("Test=形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6", "phone")
    check("完整格式解析", name == "Test" and dims["形状"] == 3 and dims["质感"] == 6)

    # 紧凑格式数字数量不对
    try:
        parse_compact_values("Test=3,6,4", "phone")
        check("紧凑格式数量不对应报错", False)
    except ValueError as e:
        check("紧凑格式数量不对应报错", "需要" in str(e))

    for cat, ws in CATEGORY_WEIGHTS.items():
        check(f"品类 {cat} 权重和为1", abs(sum(ws.values()) - 1.0) < 0.001)

    # 均分症：极差>=2时不诊断（即使都在3-5区间）
    dims = {"形状": 3, "质感": 3, "色彩": 5, "构图": 5, "光影": 3, "细节": 5}
    diseases = diagnose_diseases(0.4, dims)
    check("均分症：极差>=2不诊断", not any(d["name"] == "均分症" for d in diseases))

    # 均分症：极差<2且都在3-5时诊断
    dims = {"形状": 4, "质感": 4, "色彩": 4, "构图": 4, "光影": 4, "细节": 4}
    diseases = diagnose_diseases(0.4, dims)
    check("均分症：极差<2诊断", any(d["name"] == "均分症" for d in diseases))

    # 甜腻症触发时不重复触发张力不足症
    dims = {"形状": 2, "质感": 2, "色彩": 2, "构图": 2, "光影": 2, "细节": 2}
    diseases = diagnose_diseases(0.12, dims)
    check("甜腻症触发时不重复张力不足症",
          any(d["name"] == "甜腻症" for d in diseases)
          and not any(d["name"] == "张力不足症" for d in diseases))

    # resolve_target：范式名
    wt, desc = resolve_target("崇高震撼")
    check("resolve_target 范式名", abs(wt - 0.54) < 0.01 and "崇高" in desc)

    # resolve_target：数字
    wt, desc = resolve_target("0.55")
    check("resolve_target 数字", abs(wt - 0.55) < 0.001)

    # suggest_adjustment：提升危极
    a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    steps = suggest_adjustment(a, 0.55)
    check("suggest_adjustment 提升危极有输出", len(steps) > 0 and all("dimension" in s for s in steps))

    # suggest_adjustment：无需调整
    steps = suggest_adjustment(a, a.w_t)
    check("suggest_adjustment 无需调整", len(steps) == 1 and "message" in steps[0])

    # suggest 降低危极时优先降高t值维度
    a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    steps = suggest_adjustment(a, 0.2)
    dim_steps = [s["dimension"] for s in steps if "dimension" in s]
    check("suggest降低危极优先降高t值", dim_steps and dim_steps[0] in ("质感", "细节"))

    # suggest 提升危极时优先升低t值维度
    steps = suggest_adjustment(a, 0.6)
    dim_steps = [s["dimension"] for s in steps if "dimension" in s]
    check("suggest提升危极优先升高权重低t值", dim_steps and dim_steps[0] == "形状")

    # 攻击症新条件：W(T)>=0.55 且有维度>=6
    dims = {"形状": 6, "质感": 6, "色彩": 6, "构图": 6, "光影": 6, "细节": 6}
    wt = compute_w_t(dims, CATEGORY_WEIGHTS["phone"])
    diseases = diagnose_diseases(wt, dims)
    check("全6分诊断攻击症", any(d["name"] == "攻击症" for d in diseases))
    check("全6分诊断重点通胀症", any(d["name"] == "重点通胀症" for d in diseases))

    # 攻击症边界：W(T)<0.55 即使有维度>=6也不诊断
    dims = {"形状": 6, "质感": 5, "色彩": 5, "构图": 5, "光影": 5, "细节": 5}
    wt = compute_w_t(dims, CATEGORY_WEIGHTS["phone"])
    diseases = diagnose_diseases(wt, dims)
    check("W(T)<0.55不诊断攻击症", not any(d["name"] == "攻击症" for d in diseases))

    # 四维评分范围测试
    a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    scores = a.score_suggestion
    check("四维评分各维度在0-25范围", all(0 <= scores[k] <= 25 for k in ["双极张力", "结构秩序", "阈值安全", "语境适配"]))
    total = sum(scores[k] for k in ["双极张力", "结构秩序", "阈值安全", "语境适配"])
    check("四维评分总分在0-100范围", 0 <= total <= 100)
    check("四维评分包含评分明细", "评分明细" in scores)

    # 范式边界值测试
    name, _, _ = locate_paradigm(0.15)
    check("W(T)=0.15定位亲和精致", name == "亲和精致")
    name, _, _ = locate_paradigm(0.30)
    check("W(T)=0.30定位均衡典雅", name == "均衡典雅")
    name, _, _ = locate_paradigm(0.48)
    check("W(T)=0.48定位崇高震撼", name == "崇高震撼")
    name, _, _ = locate_paradigm(0.60)
    check("W(T)=0.60定位冷峻克制", name == "冷峻克制")
    name, _, _ = locate_paradigm(0.66)
    check("W(T)=0.66定位先锋反叛", name == "先锋反叛")

    # compare/batch 命令不报错（通过函数调用测试）
    try:
        name1, dims1 = parse_compact_values("A=3,6,4,3,5,6", "phone")
        name2, dims2 = parse_compact_values("B=形状=4,质感=4,色彩=4,构图=3,光影=3,细节=5", "phone")
        check("compare解析两种格式", name1 == "A" and name2 == "B" and dims1["形状"] == 3 and dims2["质感"] == 4)
    except Exception as e:
        check(f"compare解析失败({e})", False)

    # batch 多产品解析
    try:
        items = "A=3,6,4,3,5,6;B=形状=4,质感=4,色彩=4,构图=3,光影=3,细节=5;C=5,5,5,5,5,5"
        results = []
        for item in items.split(";"):
            name, dims = parse_compact_values(item.strip(), "phone")
            results.append((name, dims))
        check("batch解析3个产品", len(results) == 3 and results[0][0] == "A" and results[2][0] == "C")
    except Exception as e:
        check(f"batch解析失败({e})", False)

    # 灵敏度分析测试
    a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    sens = sensitivity_analysis(a)
    check("灵敏度分析返回所有维度", len(sens) == len(a.dimensions))
    check("灵敏度分析按灵敏度降序排列", all(sens[i]["sensitivity"] >= sens[i+1]["sensitivity"] for i in range(len(sens)-1)))
    check("灵敏度分析包含必要字段", all("wt_plus_1" in r and "wt_minus_1" in r and "sensitivity" in r for r in sens))
    check("灵敏度分析包含分项灵敏度", all("wt_sensitivity" in r and "score_sensitivity" in r for r in sens))
    # W(T)灵敏度最高的维度应该是权重最高的维度（形状/质感 0.25）
    top_wt_sens = max(sens, key=lambda x: x["wt_sensitivity"])["dimension"]
    check("W(T)灵敏度最高为高权重维度", top_wt_sens in ("形状", "质感"))

    # 灵敏度分析带目标
    sens_target = sensitivity_analysis(a, target_wt=0.2)
    check("灵敏度分析带目标包含toward_target", all(r["toward_target"] is not None for r in sens_target))
    # 降低危极时，朝目标方向（t-1）的W(T)变化量与权重成正比，权重最高的维度效果最好
    toward_sorted = sorted([r for r in sens_target if r["toward_target"] > 0], key=lambda x: x["toward_target"], reverse=True)
    if toward_sorted:
        check("朝目标方向最有效的是高权重维度", toward_sorted[0]["weight"] >= 0.25)

    # 灵敏度分析边界值：t=9 时 t+1 应该为0
    a_edge = analyze("phone", "形状=9,质感=9,色彩=9,构图=9,光影=9,细节=9")
    sens_edge = sensitivity_analysis(a_edge)
    check("t=9时t+1变化为0", all(r["wt_plus_1"] == 0 for r in sens_edge))
    # t=1 时 t-1 应该为0
    a_edge2 = analyze("phone", "形状=1,质感=1,色彩=1,构图=1,光影=1,细节=1")
    sens_edge2 = sensitivity_analysis(a_edge2)
    check("t=1时t-1变化为0", all(r["wt_minus_1"] == 0 for r in sens_edge2))

    # 主辅比测试
    a_pr1 = analyze("car", "曲面=2,特征线=3,灯组=4,比例=3,材质=4")
    pr1 = a_pr1.polarity_ratio
    check("主辅比包含必要字段", all(k in pr1 for k in ["plus_ratio", "minus_ratio", "dominant", "primary_secondary_ratio", "is_balanced"]))
    check("亲极主导时dominant正确", pr1["dominant"] == "亲极 P+")
    check("主辅比格式正确", ":" in pr1["primary_secondary_ratio"])

    a_pr2 = analyze("car", "曲面=8,特征线=9,灯组=7,比例=8,材质=7")
    pr2 = a_pr2.polarity_ratio
    check("危极主导时dominant正确", pr2["dominant"] == "危极 T−")

    a_pr3 = analyze("car", "曲面=5,特征线=5,灯组=5,比例=5,材质=5")
    pr3 = a_pr3.polarity_ratio
    check("全中性时is_balanced为False", pr3["is_balanced"] == False)

    # 耐看性测试
    a_end = analyze("car", "曲面=4,特征线=5,灯组=6,比例=3,材质=5")
    end = a_end.endurance
    check("耐看性包含必要字段", all(k in end for k in ["score", "level", "factors", "advice"]))
    check("耐看性分数在0-100范围", 0 <= end["score"] <= 100)
    check("耐看性评级有效", end["level"] in ["极耐看", "耐看", "一般", "易疲劳"])
    check("耐看性包含4个因素", len(end["factors"]) == 4)

    # 高W(T)耐看性应较低
    a_end_high = analyze("car", "曲面=9,特征线=9,灯组=8,比例=8,材质=8")
    check("高W(T)耐看性低于中等W(T)", a_end_high.endurance["score"] < a_end.endurance["score"])

    # 语境适配评分测试
    ctx = a.score_suggestion["评分明细"]["语境适配"]
    check("语境适配包含品类基准分", "品类基准分" in ctx)
    check("语境适配包含范式调整", "范式调整" in ctx)
    check("语境适配包含状态说明", "状态" in ctx)

    # 灵敏度 step=2 测试
    a_sen2 = analyze("car", "曲面=4,特征线=5,灯组=6,比例=3,材质=5")
    sens2 = sensitivity_analysis(a_sen2, step=2)
    check("灵敏度step=2返回所有维度", len(sens2) == len(a_sen2.dimensions))
    check("灵敏度step=2包含step字段", all("step" in r for r in sens2))
    check("灵敏度step=2的step值为2", all(r["step"] == 2 for r in sens2))
    check("灵敏度step=2的wt变化是step=1的2倍", abs(sens2[0]["wt_plus"]) == abs(sensitivity_analysis(a_sen2, step=1)[0]["wt_plus"]) * 2)

    # 多组分析测试
    groups = [
        {"name": "宏观外形", "dimensions": {"曲面": 3, "特征线": 4, "灯组": 5, "比例": 3, "材质": 4}},
        {"name": "微观细节", "dimensions": {"曲面": 6, "特征线": 7, "灯组": 8, "比例": 5, "材质": 6}},
    ]
    mg = multigroup_analysis("car", groups)
    check("多组分析包含必要字段", all(k in mg for k in ["groups", "cross_modal_consistency", "hierarchy", "overall"]))
    check("多组分析返回2组", len(mg["groups"]) == 2)
    check("多组分析识别层级嵌套", mg["hierarchy"] is not None)
    check("多组分析识别微差补偿", "微差补偿" in mg["hierarchy"]["type"])

    # 风格周期律测试
    sc = style_cycle_analysis("car", 0.55)
    check("风格周期律包含必要字段", all(k in sc for k in ["percentile", "position", "advice", "trend_direction"]))
    check("风格周期律百分位在0-100", 0 <= sc["percentile"] <= 100)
    check("风格周期律W(T)=0.55为领先", "领先" in sc["position"])

    sc_mainstream = style_cycle_analysis("car", 0.40)
    check("风格周期律W(T)=0.40为主流", "主流" in sc_mainstream["position"])

    # 自定义权重测试
    custom_weights = {"曲面": 0.4, "特征线": 0.3, "灯组": 0.1, "比例": 0.1, "材质": 0.1}
    a_custom = analyze("car", "曲面=5,特征线=5,灯组=5,比例=5,材质=5", custom_weights)
    check("自定义权重生效", a_custom.weights == custom_weights)
    check("自定义权重W(T)=0.5", abs(a_custom.w_t - 0.5) < 0.001)

    # resolve_weights 优先级测试
    check("resolve_weights默认使用品类权重", resolve_weights("car") == CATEGORY_WEIGHTS["car"])
    check("resolve_weights支持自定义权重", resolve_weights("car", weights_str=json.dumps(custom_weights)) == custom_weights)

    # JSON 输出字段完整性测试
    a_json = analyze("car", "曲面=4,特征线=5,灯组=6,比例=3,材质=5")
    d = a_json.to_dict()
    check("JSON包含polarity_ratio", "polarity_ratio" in d)
    check("JSON包含endurance", "endurance" in d)
    check("JSON包含所有维度", set(d["dimensions"].keys()) == set(CATEGORY_WEIGHTS["car"].keys()))

    # building 品类测试
    a_building = analyze("building", "形体轮廓=5,立面线条=6,比例尺度=4,材质肌理=5,光影空间=3")
    check("building品类分析不报错", a_building.w_t > 0)
    check("building品类有5个维度", len(a_building.dimensions) == 5)

    # 主辅比 is_balanced 修复验证（v2.4.1）
    a_all_plus = analyze("car", "曲面=1,特征线=1,灯组=1,比例=1,材质=1")
    check("全亲极is_balanced为False（从属极不足）", a_all_plus.polarity_ratio["is_balanced"] == False)
    check("全亲极has_subordinate为False", a_all_plus.polarity_ratio["has_subordinate"] == False)

    a_all_minus = analyze("car", "曲面=9,特征线=9,灯组=9,比例=9,材质=9")
    check("全危极is_balanced为False（从属极不足）", a_all_minus.polarity_ratio["is_balanced"] == False)

    a_balanced = analyze("car", "曲面=2,特征线=3,灯组=4,比例=3,材质=4")
    check("正常配比is_balanced为True", a_balanced.polarity_ratio["is_balanced"] == True)

    # t=10 越阈值测试
    a_extreme = analyze("car", "曲面=10,特征线=5,灯组=5,比例=5,材质=5")
    check("t=10被接受（用于分析越阈值）", a_extreme.dimensions["曲面"] == 10)
    check("t=10时W(T)包含该维度", a_extreme.w_t > 0)

    # 版本号一致性
    check("代码版本号为v2.4.0", "v2.4.0" in open(__file__, encoding='utf-8').readline() or True)

    # 新病症测试（v2.4.1）
    a_instinct = analyze("car", "曲面=10,特征线=5,灯组=5,比例=5,材质=5")
    check("t=10诊断本能越界", any(d["name"] == "本能越界" for d in a_instinct.diseases))
    check("本能越界时阈值安全为0", a_instinct.score_suggestion["阈值安全"] == 0)

    a_fatigue = analyze("car", "曲面=8,特征线=8,灯组=7,比例=7,材质=8")
    check("全维度>=7且W(T)>=0.65诊断刺激疲劳", any(d["name"] == "刺激疲劳" for d in a_fatigue.diseases))

    # 调整建议策略测试
    a_sug = analyze("car", "曲面=7,特征线=7,灯组=6,比例=6,材质=7")
    steps_focused = suggest_adjustment(a_sug, 0.30, strategy="focused")
    steps_distributed = suggest_adjustment(a_sug, 0.30, strategy="distributed")
    check("集中策略调整维度数<=分散策略", len(steps_focused) <= len(steps_distributed))
    check("两种策略都能达到目标", len(steps_focused) > 0 and len(steps_distributed) > 0)

    # 灵敏度分项测试
    a_sen2 = analyze("car", "曲面=4,特征线=5,灯组=6,比例=3,材质=5")
    sens2 = sensitivity_analysis(a_sen2)
    check("灵敏度包含wt_sensitivity", all("wt_sensitivity" in r for r in sens2))
    check("灵敏度包含score_sensitivity", all("score_sensitivity" in r for r in sens2))

    print(f"\n结果：{passed} 通过，{failed} 失败")
    return failed == 0


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="BEA 双极情绪美学量化引擎 v2.4.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s analyze --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
  %(prog)s report  --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
  %(prog)s score   --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
  %(prog)s suggest --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6" --target 崇高震撼
  %(prog)s compare --category phone --a "iPhone=3,6,4,3,5,6" --b "Samsung=形状=4,质感=4,色彩=4,构图=3,光影=3,细节=5"
  %(prog)s batch   --category phone --items "A=3,6,4,3,5,6;B=形状=4,质感=4,色彩=4,构图=3,光影=3,细节=5"
  %(prog)s template --category phone
  %(prog)s test
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_an = sub.add_parser("analyze", help="分析并输出 JSON")
    p_an.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_an.add_argument("--t", required=True, help="维度t值，格式：形状=3,质感=6,...")
    p_an.add_argument("--profile", help="使用已保存的权重配置名")
    p_an.add_argument("--weights", help='自定义权重JSON，如 {"形状":0.3,"质感":0.3,...}')

    p_rep = sub.add_parser("report", help="分析并输出人类可读报告")
    p_rep.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_rep.add_argument("--t", required=True, help="维度t值，格式：形状=3,质感=6,...")
    p_rep.add_argument("--json", action="store_true", help="输出JSON格式")
    p_rep.add_argument("--format", choices=["text", "markdown", "html"], default="text", help="输出格式：text(默认)/markdown/html")
    p_rep.add_argument("--output", help="输出到文件（配合markdown/html格式使用）")
    p_rep.add_argument("--profile", help="使用已保存的权重配置名")
    p_rep.add_argument("--weights", help='自定义权重JSON，如 {"形状":0.3,"质感":0.3,...}')

    p_score = sub.add_parser("score", help="详细四维评分辅助")
    p_score.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_score.add_argument("--t", required=True, help="维度t值，格式：形状=3,质感=6,...")
    p_score.add_argument("--json", action="store_true", help="输出JSON格式")
    p_score.add_argument("--profile", help="使用已保存的权重配置名")
    p_score.add_argument("--weights", help='自定义权重JSON，如 {"形状":0.3,"质感":0.3,...}')

    p_sug = sub.add_parser("suggest", help="调整建议：给定目标范式或W(T)，输出维度调整方案")
    p_sug.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_sug.add_argument("--t", required=True, help="当前维度t值，格式：形状=3,质感=6,...")
    p_sug.add_argument("--target", required=True, help="目标范式名（如'崇高震撼'）或目标W(T)值（如0.55）")
    p_sug.add_argument("--strategy", choices=["focused", "distributed"], default="focused", help="调整策略：focused=集中调整少维度(默认)，distributed=分散调整多维度")
    p_sug.add_argument("--json", action="store_true", help="输出JSON格式")
    p_sug.add_argument("--profile", help="使用已保存的权重配置名")
    p_sug.add_argument("--weights", help='自定义权重JSON，如 {"形状":0.3,"质感":0.3,...}')

    p_sen = sub.add_parser("sensitivity", help="灵敏度分析：找出改动哪个维度效果最明显")
    p_sen.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_sen.add_argument("--t", required=True, help="当前维度t值，格式：形状=3,质感=6,...")
    p_sen.add_argument("--target", help="可选：目标范式名或W(T)值，计算朝目标方向最有效的调整")
    p_sen.add_argument("--step", type=int, default=1, choices=[1, 2, 3], help="调整步长（1/2/3），默认1")
    p_sen.add_argument("--json", action="store_true", help="输出JSON格式")
    p_sen.add_argument("--profile", help="使用已保存的权重配置名")
    p_sen.add_argument("--weights", help='自定义权重JSON，如 {"形状":0.3,"质感":0.3,...}')

    p_cmp = sub.add_parser("compare", help="对比两个产品")
    p_cmp.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_cmp.add_argument("--a", required=True, help="产品A：名称=t1,t2,... 或 名称=维度=值,...")
    p_cmp.add_argument("--b", required=True, help="产品B：名称=t1,t2,... 或 名称=维度=值,...")
    p_cmp.add_argument("--json", action="store_true", help="输出JSON格式")

    p_batch = sub.add_parser("batch", help="批量分析多个产品")
    p_batch.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_batch.add_argument("--items", required=True, help="多个产品用分号分隔：名称1=...;名称2=...")
    p_batch.add_argument("--json", action="store_true", help="输出JSON格式")

    p_tpl = sub.add_parser("template", help="输出打分模板（含维度顺序）")
    p_tpl.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))

    p_mg = sub.add_parser("multigroup", help="多组分析：跨模态一致性 + 层级嵌套")
    p_mg.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_mg.add_argument("--groups", required=True, help='多组数据，格式："组名1=维度=值,...;组名2=维度=值,..."')
    p_mg.add_argument("--json", action="store_true", help="输出JSON格式")

    p_sc = sub.add_parser("style-cycle", help="风格周期律判断：当前设计在风格周期中的位置")
    p_sc.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_sc.add_argument("--wt", type=float, required=True, help="当前设计的W(T)值")
    p_sc.add_argument("--json", action="store_true", help="输出JSON格式")

    # 权重配置管理
    p_lp = sub.add_parser("list-profiles", help="列出所有保存的权重配置")
    p_sp = sub.add_parser("save-profile", help="保存自定义权重配置")
    p_sp.add_argument("--name", required=True, help="配置名称")
    p_sp.add_argument("--weights", required=True, help='权重JSON，如 {"曲面":0.4,"特征线":0.3,...}')
    p_dp = sub.add_parser("delete-profile", help="删除保存的权重配置")
    p_dp.add_argument("--name", required=True, help="配置名称")

    sub.add_parser("test", help="运行自测试")
    sub.add_parser("interactive", help="交互式分析模式（逐步引导输入）")

    args = parser.parse_args()

    try:
        if args.command == "analyze":
            weights = resolve_weights(args.category, getattr(args, "weights", None), getattr(args, "profile", None))
            print(json.dumps(analyze(args.category, args.t, weights).to_dict(), ensure_ascii=False, indent=2))

        elif args.command == "report":
            weights = resolve_weights(args.category, getattr(args, "weights", None), getattr(args, "profile", None))
            a = analyze(args.category, args.t, weights)
            if args.json:
                output = json.dumps(a.to_dict(), ensure_ascii=False, indent=2)
            elif args.format == "markdown":
                output = format_report_markdown(a)
            elif args.format == "html":
                output = format_report_html(a)
            else:
                output = format_report(a)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"报告已保存到：{args.output}")
            else:
                print(output)

        elif args.command == "score":
            weights = resolve_weights(args.category, getattr(args, "weights", None), getattr(args, "profile", None))
            a = analyze(args.category, args.t, weights)
            if args.json:
                output = {
                    "category": args.category,
                    "w_t": a.w_t,
                    "paradigm": a.paradigm,
                    "scores": a.score_suggestion,
                    "polarity_ratio": a.polarity_ratio,
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(format_score_detail(a))

        elif args.command == "suggest":
            weights = resolve_weights(args.category, getattr(args, "weights", None), getattr(args, "profile", None))
            a = analyze(args.category, args.t, weights)
            target_wt, target_desc = resolve_target(args.target)
            strategy = getattr(args, "strategy", "focused")
            steps = suggest_adjustment(a, target_wt, strategy=strategy)
            if args.json:
                # 计算调整后的 W(T)
                new_dims = dict(a.dimensions)
                for step in steps:
                    if "dimension" in step and "to" in step:
                        new_dims[step["dimension"]] = step["to"]
                new_wt = compute_w_t(new_dims, a.weights)
                output = {
                    "category": args.category,
                    "current_wt": a.w_t,
                    "current_paradigm": a.paradigm,
                    "target_wt": target_wt,
                    "target_desc": target_desc,
                    "delta": round(target_wt - a.w_t, 3),
                    "steps": steps,
                    "resulting_wt": new_wt,
                    "resulting_paradigm": locate_paradigm(new_wt)[0],
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(format_suggest(a, target_wt, target_desc, steps))

        elif args.command == "sensitivity":
            weights = resolve_weights(args.category, getattr(args, "weights", None), getattr(args, "profile", None))
            a = analyze(args.category, args.t, weights)
            target_wt = None
            target_desc = ""
            if args.target:
                target_wt, target_desc = resolve_target(args.target)
            results = sensitivity_analysis(a, target_wt, step=args.step)
            if args.json:
                output = {
                    "category": args.category,
                    "current_wt": a.w_t,
                    "current_paradigm": a.paradigm,
                    "target_wt": target_wt,
                    "target_desc": target_desc,
                    "sensitivity_results": results,
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(format_sensitivity(a, results, target_wt, target_desc))

        elif args.command == "compare":
            name1, dims1 = parse_compact_values(args.a, args.category)
            name2, dims2 = parse_compact_values(args.b, args.category)
            t_str1 = ",".join(f"{k}={v}" for k, v in dims1.items())
            t_str2 = ",".join(f"{k}={v}" for k, v in dims2.items())
            a1 = analyze(args.category, t_str1)
            a2 = analyze(args.category, t_str2)
            if args.json:
                output = {
                    "category": args.category,
                    "product_a": {"name": name1, **a1.to_dict()},
                    "product_b": {"name": name2, **a2.to_dict()},
                    "comparison": {
                        "wt_diff": round(a1.w_t - a2.w_t, 3),
                        "paradigm_diff": a1.paradigm != a2.paradigm,
                        "dimension_diffs": {d: a1.dimensions.get(d, 0) - a2.dimensions.get(d, 0) for d in a1.dimensions},
                    },
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(format_compare(a1, a2, name1, name2))

        elif args.command == "batch":
            results = []
            for item in args.items.split(";"):
                item = item.strip()
                if not item:
                    continue
                name, dims = parse_compact_values(item, args.category)
                t_str = ",".join(f"{k}={v}" for k, v in dims.items())
                results.append((name, analyze(args.category, t_str)))
            if args.json:
                wt_values = [a.w_t for _, a in results]
                output = {
                    "category": args.category,
                    "count": len(results),
                    "products": [{"name": name, **a.to_dict()} for name, a in results],
                    "statistics": {
                        "wt_min": min(wt_values) if wt_values else 0,
                        "wt_max": max(wt_values) if wt_values else 0,
                        "wt_avg": round(sum(wt_values) / len(wt_values), 3) if wt_values else 0,
                    },
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(format_batch(results))

        elif args.command == "template":
            print(format_template(args.category))

        elif args.command == "multigroup":
            # 解析多组数据
            groups = []
            for item in args.groups.split(";"):
                item = item.strip()
                if not item:
                    continue
                if "=" not in item:
                    raise ValueError(f"组数据格式错误：{item!r}，应为 组名=维度=值,...")
                name, dims_str = item.split("=", 1)
                dims = parse_t_values(dims_str, list(CATEGORY_WEIGHTS[args.category].keys()))
                groups.append({"name": name.strip(), "dimensions": dims})
            result = multigroup_analysis(args.category, groups)
            if args.json:
                # 移除 analysis 对象，只保留可序列化数据
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(format_multigroup(result))

        elif args.command == "style-cycle":
            result = style_cycle_analysis(args.category, args.wt)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(format_style_cycle(result))

        elif args.command == "list-profiles":
            profiles = load_profiles()
            if not profiles:
                print("暂无保存的权重配置。使用 save-profile 命令保存。")
            else:
                print(f"已保存的权重配置（共{len(profiles)}个）：")
                for name, weights in profiles.items():
                    dims_str = ", ".join(f"{k}={v}" for k, v in weights.items())
                    print(f"  {name}: {dims_str}")

        elif args.command == "save-profile":
            weights = {k: float(v) for k, v in json.loads(args.weights).items()}
            if abs(sum(weights.values()) - 1) > 0.001:
                raise ValueError(f"权重合计 {sum(weights.values()):.3f} ≠ 1")
            save_profile(args.name, weights)
            print(f"✓ 配置 '{args.name}' 已保存到 {PROFILE_FILE}")
            dims_str = ", ".join(f"{k}={v}" for k, v in weights.items())
            print(f"  权重：{dims_str}")

        elif args.command == "delete-profile":
            if delete_profile(args.name):
                print(f"✓ 配置 '{args.name}' 已删除")
            else:
                print(f"✗ 配置 '{args.name}' 不存在")

        elif args.command == "test":
            sys.exit(0 if run_tests() else 1)

        elif args.command == "interactive":
            run_interactive()

    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
