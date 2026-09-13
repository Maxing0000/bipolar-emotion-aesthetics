#!/usr/bin/env python3
"""
BEA 计算引擎 v2.0
负责：极性计算、W(T)、范式定位、四象限、四维评分、病症诊断、优化处方
"""

import json
import math
from typing import Dict, List, Tuple, Any


# ============ 范式定义 ============
PARADIGMS = [
    {"name": "治愈松弛", "wt_range": (0, 0.15), "emotion": "放松、舒展、无攻击性"},
    {"name": "亲和精致", "wt_range": (0.15, 0.30), "emotion": "亲和友好、精密有锐度"},
    {"name": "诗意朦胧", "wt_range": (0.30, 0.38), "emotion": "含蓄、梦幻、留白"},
    {"name": "均衡典雅", "wt_range": (0.38, 0.48), "emotion": "刚柔各半、克制端庄"},
    {"name": "崇高震撼", "wt_range": (0.48, 0.60), "emotion": "敬畏、震撼、深层沉醉"},
    {"name": "冷峻克制", "wt_range": (0.60, 0.66), "emotion": "冷硬、简约、专业"},
    {"name": "神秘魅惑", "wt_range": (0.66, 0.72), "emotion": "深邃、诱惑、未知"},
    {"name": "先锋反叛", "wt_range": (0.72, 0.85), "emotion": "刺激、反叛、临界"},
]

# ============ 维度定义与权重 ============
# 通用视觉分析权重
DEFAULT_WEIGHTS = {
    "shape": 0.20,      # 形状线条
    "color": 0.20,      # 色彩色相
    "brightness": 0.15, # 明度对比
    "texture": 0.15,    # 质感肌理
    "composition": 0.15,# 构图空间
    "light": 0.15,      # 光影
}

# ============ 病症定义 ============
DIAGNOSES = {
    "sweetness": {
        "name": "甜腻症（亲极过载）",
        "desc": "全圆角、全柔色、无锐度，发腻幼稚廉价",
        "prescription": "在高价值细节注入10%-20%危极（利落线/冷灰/清晰边界），柔中藏骨"
    },
    "aggression": {
        "name": "攻击症（危极过载）",
        "desc": "处处锐角、强对比、硬冷，令人紧张想回避",
        "prescription": "扩亲极基底、降危极到范式区间，用大曲面/柔光/对称接住张力"
    },
    "balance_loss": {
        "name": "均分症（主辅缺失）",
        "desc": "亲危各半、无主次、情绪暧昧",
        "prescription": "确立至少6:4主辅比，先让第一印象明确"
    },
    "disorder": {
        "name": "失序症（有立无统）",
        "desc": "单个元素都精彩，堆一起互相打架",
        "prescription": "确立一条贯穿全局的统一主线（色板/模数/栅格/特征线）"
    },
    "hierarchy_conflict": {
        "name": "层级冲突症",
        "desc": "宏观柔和却微观攻击，视觉圆润却触感硌手",
        "prescription": "逐层逐通道审计，选同向叠加或微差补偿，消除方向冲突"
    },
    "emphasis_inflation": {
        "name": "重点通胀症",
        "desc": "哪里都想强调，结果哪里都不突出",
        "prescription": "做减法，从属极与强调点压回10%-30%，建视觉等级"
    },
    "threshold_violation": {
        "name": "本能越界",
        "desc": "触及割伤、眩晕、疼痛、刺耳等生理红线",
        "prescription": "一票否决，删除或钝化，无风格借口"
    },
    "cognitive_overload": {
        "name": "认知超载",
        "desc": "复杂度超受众带宽又缺秩序引导",
        "prescription": "降复杂度、补层级秩序，或改面向更高阈值受众"
    },
}


class BEAEngine:
    """BEA 计算引擎"""

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def analyze(self, polarities: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        完整 BEA 分析

        Args:
            polarities: 各维度极性数据，格式：
                {
                    "shape": {"direction": "P"|"T"|"mixed", "intensity": 0-10, "description": "..."},
                    ...
                }

        Returns:
            完整分析结果
        """
        # 1. 计算 W(T)
        wt = self._calculate_wt(polarities)

        # 2. 范式定位
        paradigm = self._get_paradigm(wt)

        # 3. 四象限定位
        quadrant = self._get_quadrant(polarities, wt)

        # 4. 四维评分
        scores = self._calculate_scores(polarities, wt, paradigm)

        # 5. 病症诊断
        diagnoses = self._diagnose(polarities, wt, scores)

        # 6. 优化处方
        prescriptions = self._generate_prescriptions(polarities, wt, diagnoses)

        # 7. 亲极/危极元素提取
        elements = self._extract_elements(polarities)

        # 8. 情绪基调
        mood = self._generate_mood(wt, paradigm, elements)

        return {
            "wt": round(wt, 3),
            "wt_percent": round(wt * 100, 1),
            "paradigm": paradigm,
            "quadrant": quadrant,
            "scores": scores,
            "total_score": sum(scores.values()),
            "diagnoses": diagnoses,
            "prescriptions": prescriptions,
            "elements": elements,
            "mood": mood,
            "polarities": polarities,
        }

    def _calculate_wt(self, polarities: Dict[str, Dict[str, Any]]) -> float:
        """计算整体危极权重 W(T)"""
        total = 0.0
        for dim, weight in self.weights.items():
            if dim in polarities:
                p = polarities[dim]
                direction = p.get("direction", "mixed")
                intensity = p.get("intensity", 5)

                if direction == "T":
                    t = intensity
                elif direction == "P":
                    t = max(0, 5 - intensity * 0.5)  # 亲极维度危极低
                else:  # mixed
                    t = intensity * 0.6

                total += weight * (t / 10)

        return min(max(total, 0), 1)

    def _get_paradigm(self, wt: float) -> Dict[str, Any]:
        """根据 W(T) 定位范式"""
        for p in PARADIGMS:
            if p["wt_range"][0] <= wt < p["wt_range"][1]:
                return {
                    "name": p["name"],
                    "emotion": p["emotion"],
                    "wt_range": p["wt_range"],
                }
        # 越界
        if wt >= 0.85:
            return {"name": "越界非美", "emotion": "焦虑/排斥", "wt_range": (0.85, 1.0)}
        return PARADIGMS[0]

    def _get_quadrant(self, polarities: Dict[str, Dict[str, Any]], wt: float) -> Dict[str, Any]:
        """四象限定位（张力×秩序）"""
        # 张力 = W(T) 相关
        tension = wt

        # 秩序 = 各维度一致性、对称性、规律性
        order_score = 0.0
        for dim, p in polarities.items():
            desc = p.get("description", "").lower()
            if any(k in desc for k in ["对称", "均衡", "规律", "秩序", "统一", "一致", "规整", "居中"]):
                order_score += 0.15
            if any(k in desc for k in ["混乱", "失衡", "随机", "破碎", "冲突", "拥挤"]):
                order_score -= 0.1
        order = min(max(0.5 + order_score, 0), 1)

        # 象限判断
        if tension >= 0.4 and order >= 0.5:
            quadrant = "黄金区（高张力×高秩序）"
            advice = "美感黄金区，高级耐看"
        elif tension >= 0.4 and order < 0.5:
            quadrant = "焦虑区（高张力×低秩序）"
            advice = "刺激但杂乱，建议补秩序"
        elif tension < 0.4 and order >= 0.5:
            quadrant = "平庸区（低张力×高秩序）"
            advice = "整齐但无张力，建议加张力"
        else:
            quadrant = "混沌区（低张力×低秩序）"
            advice = "潦草廉价，先立秩序再加张力"

        return {
            "tension": round(tension, 2),
            "order": round(order, 2),
            "name": quadrant,
            "advice": advice,
        }

    def _calculate_scores(self, polarities: Dict[str, Dict[str, Any]], wt: float, paradigm: Dict) -> Dict[str, int]:
        """四维评分（各25分，满分100）"""
        # 1. 双极张力（对立清晰且成对呼应）
        has_p = any(p.get("direction") == "P" for p in polarities.values())
        has_t = any(p.get("direction") == "T" for p in polarities.values())
        tension_score = 15
        if has_p and has_t:
            tension_score += 5
        if 0.2 <= wt <= 0.7:
            tension_score += 3
        if paradigm["name"] not in ["越界非美"]:
            tension_score += 2

        # 2. 结构秩序（主辅分明、比例精当、层级一致）
        order_score = 12
        for dim, p in polarities.items():
            desc = p.get("description", "")
            if any(k in desc for k in ["对称", "均衡", "比例", "节奏", "层级", "呼应", "统一"]):
                order_score += 2
        order_score = min(order_score, 25)

        # 3. 阈值安全（无本能红线、认知可消化）
        threshold_score = 20
        if wt > 0.8:
            threshold_score -= 10
        for dim, p in polarities.items():
            if p.get("intensity", 0) >= 9 and p.get("direction") == "T":
                threshold_score -= 3
        threshold_score = max(min(threshold_score, 25), 0)

        # 4. 语境适配（匹配范式、元素协同）
        context_score = 15
        dims_count = len([d for d in polarities if polarities[d].get("intensity", 0) > 0])
        if dims_count >= 4:
            context_score += 5
        if 0.15 <= wt <= 0.75:
            context_score += 5
        context_score = min(context_score, 25)

        return {
            "tension": min(tension_score, 25),
            "order": min(order_score, 25),
            "threshold": min(threshold_score, 25),
            "context": min(context_score, 25),
        }

    def _diagnose(self, polarities: Dict[str, Dict[str, Any]], wt: float, scores: Dict[str, int]) -> List[Dict]:
        """病症诊断"""
        diagnoses = []

        # 甜腻症：亲极过载
        if wt < 0.15:
            diagnoses.append(DIAGNOSES["sweetness"])

        # 攻击症：危极过载
        if wt > 0.7:
            diagnoses.append(DIAGNOSES["aggression"])

        # 均分症：主辅缺失
        p_count = sum(1 for p in polarities.values() if p.get("direction") == "P")
        t_count = sum(1 for p in polarities.values() if p.get("direction") == "T")
        if p_count > 0 and t_count > 0 and abs(p_count - t_count) <= 1:
            diagnoses.append(DIAGNOSES["balance_loss"])

        # 重点通胀症
        high_t_count = sum(1 for p in polarities.values() if p.get("intensity", 0) >= 7 and p.get("direction") == "T")
        if high_t_count >= 4:
            diagnoses.append(DIAGNOSES["emphasis_inflation"])

        # 本能越界
        if any(p.get("intensity", 0) >= 9 and p.get("direction") == "T" for p in polarities.values()):
            diagnoses.append(DIAGNOSES["threshold_violation"])

        # 认知超载
        if scores["order"] < 15:
            diagnoses.append(DIAGNOSES["cognitive_overload"])

        return diagnoses[:3]  # 最多返回3个主要病症

    def _generate_prescriptions(self, polarities: Dict[str, Dict[str, Any]], wt: float, diagnoses: List[Dict]) -> List[str]:
        """生成优化处方"""
        prescriptions = []

        # 基于 W(T) 的总体建议
        if wt < 0.2:
            prescriptions.append(f"当前 W(T)={wt:.2f} 偏低，建议在高价值细节注入10%-20%危极元素（锐利线条、冷色点缀、清晰边界），提升张力")
        elif wt > 0.65:
            prescriptions.append(f"当前 W(T)={wt:.2f} 偏高，建议扩大亲极基底（柔和曲面、暖色调、对称秩序），将危极压回范式区间")
        else:
            prescriptions.append(f"当前 W(T)={wt:.2f} 处于合理区间，保持现有配比，重点优化秩序与细节协同")

        # 基于病症的处方
        for d in diagnoses:
            prescriptions.append(f"【{d['name']}】{d['prescription']}")

        # 基于维度的具体建议
        for dim, p in polarities.items():
            if p.get("intensity", 0) >= 8 and p.get("direction") == "T":
                dim_name = {"shape": "形状", "color": "色彩", "brightness": "明度", "texture": "质感", "composition": "构图", "light": "光影"}.get(dim, dim)
                prescriptions.append(f"{dim_name}维度危极强度过高（{p['intensity']}/10），建议降低到5-6，或用周围亲极元素衬托")

        return prescriptions[:5]  # 最多5条处方

    def _extract_elements(self, polarities: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """提取亲极/危极元素"""
        p_elements = []
        t_elements = []

        dim_names = {
            "shape": "形状线条", "color": "色彩色相", "brightness": "明度对比",
            "texture": "质感肌理", "composition": "构图空间", "light": "光影"
        }

        for dim, p in polarities.items():
            name = dim_names.get(dim, dim)
            desc = p.get("description", "")
            if p.get("direction") == "P":
                p_elements.append(f"{name}：{desc}" if desc else name)
            elif p.get("direction") == "T":
                t_elements.append(f"{name}：{desc}" if desc else name)
            else:
                if desc:
                    p_elements.append(f"{name}：{desc}（偏亲）")

        return {"positive": p_elements[:6], "negative": t_elements[:6]}

    def _generate_mood(self, wt: float, paradigm: Dict, elements: Dict[str, List[str]]) -> str:
        """生成情绪基调一句话"""
        p_count = len(elements["positive"])
        t_count = len(elements["negative"])

        if p_count > t_count:
            mood = f"以亲和安抚为主调，{t_count}处危极细节提神，整体感受是「{paradigm['emotion']}」"
        elif t_count > p_count:
            mood = f"以唤醒张力为主导，{p_count}处亲极元素托底，整体感受是「{paradigm['emotion']}」"
        else:
            mood = f"亲危双极均衡对峙，秩序统摄全局，整体感受是「{paradigm['emotion']}」"

        return mood


# ============ 模拟数据生成（用于开发测试） ============
def generate_mock_result() -> Dict[str, Any]:
    """生成模拟分析结果"""
    polarities = {
        "shape": {"direction": "mixed", "intensity": 5, "description": "曲中带直，主体圆润细节锐利"},
        "color": {"direction": "P", "intensity": 4, "description": "低饱和暖调，邻近色搭配"},
        "brightness": {"direction": "mixed", "intensity": 6, "description": "柔和明暗过渡，局部强对比"},
        "texture": {"direction": "P", "intensity": 5, "description": "光滑细腻，哑光亲肤质感"},
        "composition": {"direction": "P", "intensity": 4, "description": "居中稳定，留白均匀，层次递进"},
        "light": {"direction": "mixed", "intensity": 5, "description": "漫射柔光为主，局部硬光提神"},
    }

    engine = BEAEngine()
    return engine.analyze(polarities)


if __name__ == "__main__":
    # 测试
    result = generate_mock_result()
    print(json.dumps(result, ensure_ascii=False, indent=2))
