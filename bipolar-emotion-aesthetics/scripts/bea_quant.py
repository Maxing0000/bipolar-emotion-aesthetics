#!/usr/bin/env python3
"""
BEA (Bipolar Emotion Aesthetics) 量化引擎 v2.2

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
    return w_t > 0.60 and any(t >= 7 for t in dims.values())

def _has_middle_child(w_t: float, dims: Dict[str, int]) -> bool:
    # 均分症：所有维度集中在3-5且极差<2（真正的无主次），W(T)在中间区间
    return (all(3 <= t <= 5 for t in dims.values())
            and 0.35 <= w_t <= 0.45
            and (max(dims.values()) - min(dims.values())) < 2)

def _has_emphasis_inflation(w_t: float, dims: Dict[str, int]) -> bool:
    return sum(1 for t in dims.values() if t >= 6) >= 3

def _has_tension_deficit(w_t: float, dims: Dict[str, int]) -> bool:
    return w_t < 0.35 and (max(dims.values()) - min(dims.values())) < 2

# (名称, 诊断函数, 处方)
DISEASE_RULES: List[Tuple[str, Callable[[float, Dict[str, int]], bool], str]] = [
    ("甜腻症", _has_sweet_tooth,
     "全圆角全柔色、无锐度。在高价值细节处注入10%-20%危极，柔中藏骨。"),
    ("攻击症", _has_aggression,
     "处处锐角强对比、令人紧张。扩大亲极基底，将过强维度降至范式区间内。"),
    ("均分症", _has_middle_child,
     "亲危各半无主次、情绪暧昧。确立>=6:4主辅比，让第一印象明确。"),
    ("重点通胀症", _has_emphasis_inflation,
     "哪里都想强调、视觉噪音大。做减法，强调点压回1-2个。"),
    ("张力不足症", _has_tension_deficit,
     "所有维度都温和、没有提神点。在1-2个维度提升危极强度至6+，制造对比。"),
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
            raise ValueError(f"未知维度 '{name}'，该品类有效维度为：{', '.join(valid_dims)}")
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


def locate_paradigm(w_t: float) -> Tuple[str, str, Tuple[float, float]]:
    for low, high, name, desc in PARADIGMS:
        if low <= w_t < high:
            return name, desc, (low, high)
    return PARADIGMS[-1][2], PARADIGMS[-1][3], (PARADIGMS[-1][0], PARADIGMS[-1][1])


def _disease_evidence(name: str, w_t: float, dims: Dict[str, int]) -> str:
    if name == "甜腻症":
        return f"W(T)={w_t:.2f} 偏低，所有维度 t<=4，最高维度为 {max(dims, key=dims.get)}={max(dims.values())}"
    if name == "攻击症":
        high = [f"{k}={v}" for k, v in dims.items() if v >= 7]
        return f"W(T)={w_t:.2f} 偏高，过强维度：{', '.join(high)}"
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


def suggest_scores(w_t: float, dims: Dict[str, int], diseases: List[Dict[str, str]]) -> Dict[str, object]:
    tension = 20
    order = 20
    threshold = 22
    context = 20

    spread = max(dims.values()) - min(dims.values())
    disease_names = {d["name"] for d in diseases}

    # 张力：W(T)在0.35-0.60（典雅到崇高）且有维度对比时加分
    if 0.35 <= w_t <= 0.60 and spread >= 2:
        tension = 22
    if "张力不足症" in disease_names:
        tension = 16
    if "攻击症" in disease_names:
        tension = 17
    if "甜腻症" in disease_names:
        tension = 15

    # 秩序：无均分症和重点通胀症时加分；甜腻症也意味着无主次对比，扣分
    if "均分症" not in disease_names and "重点通胀症" not in disease_names and "甜腻症" not in disease_names:
        order = 22
    if "重点通胀症" in disease_names:
        order = 18
    if "甜腻症" in disease_names:
        order = 17

    # 阈值：W(T)<0.60 默认安全
    if w_t < 0.60:
        threshold = 24

    return {
        "双极张力": tension,
        "结构秩序": order,
        "阈值安全": threshold,
        "语境适配": context,
        "说明": "以上为基于维度数据的参考分，语境适配需人工结合受众与场景判断",
    }


def analyze(category: str, t_str: str) -> BEAAnalysis:
    if category not in CATEGORY_WEIGHTS:
        raise ValueError(f"未知品类 '{category}'，支持：{', '.join(CATEGORY_WEIGHTS.keys())}")
    weights = CATEGORY_WEIGHTS[category]
    dimensions = parse_t_values(t_str, list(weights.keys()))
    w_t = compute_w_t(dimensions, weights)
    paradigm, paradigm_desc, p_range = locate_paradigm(w_t)
    diseases = diagnose_diseases(w_t, dimensions)
    scores = suggest_scores(w_t, dimensions, diseases)
    return BEAAnalysis(
        category=category, dimensions=dimensions, weights=weights, w_t=w_t,
        paradigm=paradigm, paradigm_desc=paradigm_desc, paradigm_range=p_range,
        diseases=diseases, score_suggestion=scores,
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

    lines.append(f"\n【病症诊断】")
    if a.diseases:
        for i, d in enumerate(a.diseases, 1):
            lines.append(f"  {i}. {d['name']}")
            lines.append(f"     证据：{d['evidence']}")
            lines.append(f"     处方：{d['prescription']}")
    else:
        lines.append("  未检测到明显病症。")
    lines.append("  （注：层级冲突症需人工判断宏观/微观一致性，无法自动诊断）")
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


def format_score_detail(a: BEAAnalysis) -> str:
    lines = []
    lines.append("=" * 50)
    lines.append("  BEA 四维评分辅助")
    lines.append("=" * 50)
    lines.append(f"  W(T)={a.w_t:.3f} · {a.paradigm}")
    lines.append("")

    scores = a.score_suggestion
    spread = max(a.dimensions.values()) - min(a.dimensions.values())
    high_dims = [f"{k}={v}" for k, v in a.dimensions.items() if v >= 6]
    low_dims = [f"{k}={v}" for k, v in a.dimensions.items() if v <= 3]
    disease_names = {d["name"] for d in a.diseases}

    lines.append(f"【双极张力】参考分：{scores['双极张力']}/25")
    lines.append(f"  维度极差：{spread}（>=2为有对比，<2为张力不足）")
    lines.append(f"  危极维度（>=6）：{', '.join(high_dims) if high_dims else '无'}")
    lines.append(f"  亲极维度（<=3）：{', '.join(low_dims) if low_dims else '无'}")
    if "张力不足症" in disease_names:
        lines.append("  警告：张力不足症，建议在1-2个维度提危极至6+")
    if "攻击症" in disease_names:
        lines.append("  警告：攻击症，建议降危极维度")
    lines.append("")

    n_high = sum(1 for v in a.dimensions.values() if v >= 6)
    lines.append(f"【结构秩序】参考分：{scores['结构秩序']}/25")
    lines.append(f"  高强调维度数：{n_high}（<=2为有主次，>=3为重点通胀）")
    if "均分症" in disease_names:
        lines.append("  警告：均分症，所有维度集中在3-5，无主次")
    if "重点通胀症" in disease_names:
        lines.append("  警告：重点通胀症，强调点过多")
    lines.append("")

    lines.append(f"【阈值安全】参考分：{scores['阈值安全']}/25")
    if a.w_t >= 0.85:
        lines.append("  警告：W(T)>=0.85，逼近越阈，需检查本能红线")
    elif a.w_t >= 0.66:
        lines.append("  W(T)在先锋反叛区间，需确认受众阈值可接受")
    else:
        lines.append("  W(T)在安全区间，无本能红线风险")
    lines.append("")

    lines.append(f"【语境适配】参考分：{scores['语境适配']}/25（需人工判断）")
    lines.append("  - 目标受众的审美阈值是否匹配当前范式？")
    lines.append("  - 使用场景是否需要当前的张力水平？")
    lines.append("  - 与竞品相比，这个定位有差异化吗？")
    lines.append("  - 时代语境下，这个风格是领先还是过时？")

    total = sum(v for k, v in scores.items() if k != "说明")
    lines.append("")
    lines.append(f"【合计参考】{total}/100")
    lines.append(f"  注：{scores['说明']}")
    lines.append("")
    lines.append("=" * 50)
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


def suggest_adjustment(a: BEAAnalysis, target_wt: float) -> List[Dict[str, object]]:
    """
    计算从当前 W(T) 调整到目标 W(T) 的维度变更方案。
    策略：优先调整权重高的维度，每次±1，直到达到目标或无法继续。
    返回调整步骤列表。
    """
    current = dict(a.dimensions)
    weights = a.weights
    delta = target_wt - a.w_t

    if abs(delta) < 0.005:
        return [{"message": "当前W(T)已在目标范围内，无需调整"}]

    direction = 1 if delta > 0 else -1  # 1=提升危极，-1=降低危极
    steps = []
    remaining = abs(delta)

    # 按权重排序维度
    sorted_dims = sorted(weights.keys(), key=lambda d: weights[d], reverse=True)

    for dim in sorted_dims:
        if remaining <= 0.005:
            break
        t = current[dim]
        w = weights[dim]
        # 计算这个维度最多能调多少
        if direction == 1:
            max_change = 10 - t
        else:
            max_change = t
        if max_change <= 0:
            continue
        # 每次调整1的W(T)变化量
        per_step = w / 10.0
        needed_steps = min(max_change, int(remaining / per_step) + 1)
        # 精确计算需要几步
        actual_steps = 0
        for i in range(needed_steps):
            if remaining <= 0.005:
                break
            current[dim] += direction
            remaining -= per_step
            actual_steps += 1
        if actual_steps > 0:
            steps.append({
                "dimension": dim,
                "from": t,
                "to": current[dim],
                "change": direction * actual_steps,
                "wt_change": round(direction * per_step * actual_steps, 3),
            })

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

    print(f"\n结果：{passed} 通过，{failed} 失败")
    return failed == 0


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="BEA 双极情绪美学量化引擎 v2.2",
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

    p_rep = sub.add_parser("report", help="分析并输出人类可读报告")
    p_rep.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_rep.add_argument("--t", required=True, help="维度t值，格式：形状=3,质感=6,...")

    p_score = sub.add_parser("score", help="详细四维评分辅助")
    p_score.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_score.add_argument("--t", required=True, help="维度t值，格式：形状=3,质感=6,...")

    p_sug = sub.add_parser("suggest", help="调整建议：给定目标范式或W(T)，输出维度调整方案")
    p_sug.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_sug.add_argument("--t", required=True, help="当前维度t值，格式：形状=3,质感=6,...")
    p_sug.add_argument("--target", required=True, help="目标范式名（如'崇高震撼'）或目标W(T)值（如0.55）")

    p_cmp = sub.add_parser("compare", help="对比两个产品")
    p_cmp.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_cmp.add_argument("--a", required=True, help="产品A：名称=t1,t2,... 或 名称=维度=值,...")
    p_cmp.add_argument("--b", required=True, help="产品B：名称=t1,t2,... 或 名称=维度=值,...")

    p_batch = sub.add_parser("batch", help="批量分析多个产品")
    p_batch.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))
    p_batch.add_argument("--items", required=True, help="多个产品用分号分隔：名称1=...;名称2=...")

    p_tpl = sub.add_parser("template", help="输出打分模板（含维度顺序）")
    p_tpl.add_argument("--category", required=True, choices=list(CATEGORY_WEIGHTS.keys()))

    sub.add_parser("test", help="运行自测试")

    args = parser.parse_args()

    try:
        if args.command == "analyze":
            print(json.dumps(analyze(args.category, args.t).to_dict(), ensure_ascii=False, indent=2))

        elif args.command == "report":
            print(format_report(analyze(args.category, args.t)))

        elif args.command == "score":
            print(format_score_detail(analyze(args.category, args.t)))

        elif args.command == "suggest":
            a = analyze(args.category, args.t)
            target_wt, target_desc = resolve_target(args.target)
            steps = suggest_adjustment(a, target_wt)
            print(format_suggest(a, target_wt, target_desc, steps))

        elif args.command == "compare":
            name1, dims1 = parse_compact_values(args.a, args.category)
            name2, dims2 = parse_compact_values(args.b, args.category)
            t_str1 = ",".join(f"{k}={v}" for k, v in dims1.items())
            t_str2 = ",".join(f"{k}={v}" for k, v in dims2.items())
            print(format_compare(analyze(args.category, t_str1), analyze(args.category, t_str2), name1, name2))

        elif args.command == "batch":
            results = []
            for item in args.items.split(";"):
                item = item.strip()
                if not item:
                    continue
                name, dims = parse_compact_values(item, args.category)
                t_str = ",".join(f"{k}={v}" for k, v in dims.items())
                results.append((name, analyze(args.category, t_str)))
            print(format_batch(results))

        elif args.command == "template":
            print(format_template(args.category))

        elif args.command == "test":
            sys.exit(0 if run_tests() else 1)

    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
