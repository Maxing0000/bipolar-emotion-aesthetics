#!/usr/bin/env python3
"""BEA 量化模型 v2.0 计算器：支持非线性激活、维度交互、注意力权重、连续量表、子维度评分、统一美感总分。

用法：
  # 简化模式（兼容 v1.0）
  python3 bea_quant_v2.py --category phone --t "形状线条=2,质感触觉=3,色彩=2,构图比例=2,光影=2,细节线条=6"

  # 完整模式（v2.0）
  python3 bea_quant_v2.py --category phone --t "形状线条=2.5,质感触觉=3.0,色彩=2.0,构图比例=2.0,光影=2.5,细节线条=6.5" --mode full --activation sigmoid --attention "形状线条=1.2,细节线条=1.4"

  # 带子维度评分
  python3 bea_quant_v2.py --category phone --t "..." --subscores "对立清晰度=4,成对呼应度=3,范式匹配度=5,主辅层级=4,比例精当度=4,全局统一性=5,本能红线=5,认知负荷=4,文化适配=5,受众匹配=4,场景功能=4,时代位置=3"

  # 输出 JSON
  python3 bea_quant_v2.py --category phone --t "..." --json

  # 输出诊断报告
  python3 bea_quant_v2.py --category phone --t "..." --report

  # 列出品类与维度
  python3 bea_quant_v2.py --list

品类权重源自 method.md 第 3 节，可按项目用 --weights 覆盖。
分值为协作刻度，不是心理物理常数。
"""
import argparse
import json
import math
import sys
from typing import Dict, Optional, Tuple

# ============================================================
# 品类权重（v1.0 经验值，可通过数据校准更新）
# ============================================================
CATEGORY_WEIGHTS = {
    "phone": {
        "形状线条": 0.25, "质感触觉": 0.25, "色彩": 0.15,
        "构图比例": 0.15, "光影": 0.10, "细节线条": 0.10
    },
    "car": {
        "形体曲面动势": 0.30, "特征线条": 0.25, "灯组图形": 0.15,
        "比例姿态": 0.15, "材质光影": 0.15
    },
    "brand": {
        "图形形状": 0.25, "色彩": 0.25, "字体": 0.20,
        "版式构图": 0.20, "质感": 0.10
    },
    "ui": {
        "布局留白": 0.25, "色彩对比": 0.20, "组件形": 0.20,
        "动效": 0.20, "字体图标": 0.15
    },
    "architecture": {
        "空间尺度": 0.25, "形体造型": 0.20, "材料质感": 0.20,
        "光影": 0.15, "色彩": 0.10, "动线布局": 0.10
    },
    "fashion": {
        "廓形": 0.25, "面料质感": 0.25, "色彩": 0.20,
        "细节配件": 0.15, "比例剪裁": 0.15
    },
}

# ============================================================
# 范式区间
# ============================================================
PARADIGM_RANGES = [
    (0.15, "治愈松弛"),
    (0.30, "亲和精致"),
    (0.48, "均衡典雅"),
    (0.60, "崇高震撼（需单元素高强度支撑）"),
    (0.66, "冷峻克制"),
    (0.85, "先锋反叛"),
    (float("inf"), "逼近越阈——非美区"),
]

# ============================================================
# 高相关维度对（交互项）
# ============================================================
INTERACTION_PAIRS = {
    "phone": [
        ("形状线条", "质感触觉", 1.2),
        ("色彩", "光影", 1.1),
    ],
    "car": [
        ("形体曲面动势", "特征线条", 1.3),
        ("灯组图形", "材质光影", 1.1),
    ],
    "brand": [
        ("图形形状", "字体", 1.2),
        ("色彩", "版式构图", 1.1),
    ],
    "ui": [
        ("布局留白", "组件形", 1.2),
        ("色彩对比", "动效", 1.1),
    ],
    "architecture": [
        ("空间尺度", "形体造型", 1.2),
        ("材料质感", "光影", 1.1),
    ],
    "fashion": [
        ("廓形", "面料质感", 1.3),
        ("色彩", "细节配件", 1.1),
    ],
}

# ============================================================
# BEA 美感总分加权（按品类）
# ============================================================
BEA_SCORE_WEIGHTS = {
    "phone": {"tension": 0.25, "order": 0.30, "threshold": 0.25, "context": 0.20},
    "car": {"tension": 0.30, "order": 0.25, "threshold": 0.20, "context": 0.25},
    "brand": {"tension": 0.30, "order": 0.30, "threshold": 0.15, "context": 0.25},
    "ui": {"tension": 0.20, "order": 0.30, "threshold": 0.30, "context": 0.20},
    "architecture": {"tension": 0.25, "order": 0.30, "threshold": 0.25, "context": 0.20},
    "fashion": {"tension": 0.30, "order": 0.25, "threshold": 0.20, "context": 0.25},
}

# ============================================================
# 子维度定义
# ============================================================
SUBDIMENSIONS = {
    "tension": ["对立清晰度", "成对呼应度", "范式匹配度"],
    "order": ["主辅层级", "比例精当度", "全局统一性"],
    "threshold": ["本能红线", "认知负荷", "文化适配"],
    "context": ["受众匹配", "场景功能", "时代位置"],
}

SUBDIMENSION_DESCRIPTIONS = {
    "对立清晰度": "对立元素是否清晰可辨",
    "成对呼应度": "对立元素是否成对出现、互相呼应",
    "范式匹配度": "整体配比是否匹配目标范式",
    "主辅层级": "主导与从属极性是否分明",
    "比例精当度": "尺寸比例是否精当",
    "全局统一性": "全局是否有统一秩序主线",
    "本能红线": "是否触及本能安全阈",
    "认知负荷": "复杂度是否在受众认知带宽内",
    "文化适配": "是否适配目标文化",
    "受众匹配": "是否匹配目标受众阈值",
    "场景功能": "是否适配使用场景与功能",
    "时代位置": "是否处于合适的时代风格位置",
}


# ============================================================
# 核心函数
# ============================================================
def paradigm_of(wt: float) -> str:
    """根据 W(T) 判定范式。"""
    for upper, name in PARADIGM_RANGES:
        if wt < upper:
            return name
    return PARADIGM_RANGES[-1][1]


def activation_linear(t: float) -> float:
    """线性激活（v1.0 兼容）。"""
    return t / 10.0


def activation_sigmoid(t: float, k: float = 0.8, t0: float = 5.0) -> float:
    """Sigmoid 激活（模拟感知阈值效应）。"""
    return 1.0 / (1.0 + math.exp(-k * (t - t0)))


def activation_power(t: float, gamma: float = 1.0) -> float:
    """幂函数激活（模拟感知压缩/放大）。"""
    return (t / 10.0) ** gamma


def get_activation_fn(name: str, **kwargs):
    """获取激活函数。"""
    if name == "linear":
        return activation_linear
    elif name == "sigmoid":
        k = kwargs.get("k", 0.8)
        t0 = kwargs.get("t0", 5.0)
        return lambda t: activation_sigmoid(t, k, t0)
    elif name == "power":
        gamma = kwargs.get("gamma", 1.0)
        return lambda t: activation_power(t, gamma)
    else:
        raise ValueError(f"未知激活函数: {name}")


def calculate_wt_v1(
    tvals: Dict[str, float],
    weights: Dict[str, float]
) -> float:
    """v1.0 线性 W(T) 计算。"""
    total = 0.0
    for dim, w in weights.items():
        t = tvals.get(dim, 0.0)
        total += w * t / 10.0
    return total


def calculate_wt_v2(
    tvals: Dict[str, float],
    weights: Dict[str, float],
    category: str,
    activation: str = "linear",
    attention: Optional[Dict[str, float]] = None,
    alpha: float = 0.7,
    beta: float = 0.3,
    use_interaction: bool = True,
    **activation_kwargs
) -> Tuple[float, Dict]:
    """v2.0 完整 W(T) 计算。

    返回：(W(T), 详细计算过程)
    """
    act_fn = get_activation_fn(activation, **activation_kwargs)
    attention = attention or {}

    # 主效应
    main_effect = 0.0
    main_details = []
    for dim, w in weights.items():
        t = tvals.get(dim, 0.0)
        a = attention.get(dim, 1.0)
        contrib = w * a * act_fn(t)
        main_effect += contrib
        main_details.append({
            "dimension": dim,
            "weight": w,
            "t": t,
            "attention": a,
            "activation": act_fn(t),
            "contribution": contrib
        })

    # 交互效应
    interaction_effect = 0.0
    interaction_details = []
    if use_interaction and category in INTERACTION_PAIRS:
        for dim1, dim2, coeff in INTERACTION_PAIRS[category]:
            if dim1 in tvals and dim2 in tvals:
                t1 = tvals[dim1]
                t2 = tvals[dim2]
                contrib = coeff * (t1 / 10.0) * (t2 / 10.0)
                interaction_effect += contrib
                interaction_details.append({
                    "pair": f"{dim1}×{dim2}",
                    "coefficient": coeff,
                    "t1": t1,
                    "t2": t2,
                    "contribution": contrib
                })

    # 归一化交互效应（使其与主效应同量级）
    if interaction_details:
        max_interaction = sum(c for _, _, c in INTERACTION_PAIRS[category])
        interaction_effect = interaction_effect / max_interaction if max_interaction > 0 else 0

    wt = alpha * main_effect + beta * interaction_effect

    details = {
        "main_effect": main_effect,
        "interaction_effect": interaction_effect,
        "alpha": alpha,
        "beta": beta,
        "main_details": main_details,
        "interaction_details": interaction_details,
        "activation": activation,
        "wt_v1": calculate_wt_v1(tvals, weights)
    }

    return wt, details


def calculate_bea_score(
    sub_scores: Dict[str, float],
    category: str,
    method: str = "geometric"
) -> Tuple[float, Dict]:
    """计算 BEA 美感总分。

    method: "geometric"（几何平均，推荐）或 "weighted"（加权平均）
    """
    dimension_scores = {}
    for dim, subdim_list in SUBDIMENSIONS.items():
        scores = [sub_scores.get(sd, 0.0) for sd in subdim_list]
        dimension_scores[dim] = sum(scores) / (len(subdim_list) * 5.0)  # 归一化到 0-1

    if method == "geometric":
        product = 1.0
        for s in dimension_scores.values():
            product *= max(s, 0.001)  # 避免 0
        bea_score = product ** (1.0 / len(dimension_scores))
    elif method == "weighted":
        weights = BEA_SCORE_WEIGHTS.get(category, BEA_SCORE_WEIGHTS["phone"])
        bea_score = sum(weights[dim] * dimension_scores[dim] for dim in dimension_scores)
    else:
        raise ValueError(f"未知评分方法: {method}")

    details = {
        "dimension_scores": dimension_scores,
        "method": method,
        "sub_scores": sub_scores
    }

    return bea_score, details


def parse_key_value(spec: str) -> Dict[str, float]:
    """解析 "key=value,key=value" 格式。"""
    out = {}
    for pair in spec.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(f"格式错误：{pair!r}，应为 维度=值")
        k, v = pair.rsplit("=", 1)
        out[k.strip()] = float(v)
    return out


# ============================================================
# 输出格式化
# ============================================================
def format_report(
    category: str,
    tvals: Dict[str, float],
    wt_v1: float,
    wt_v2: float,
    wt_details: Dict,
    paradigm: str,
    bea_score: Optional[float] = None,
    bea_details: Optional[Dict] = None,
    sub_scores: Optional[Dict[str, float]] = None
) -> str:
    """格式化诊断报告。"""
    lines = []
    lines.append("=" * 60)
    lines.append("BEA v2.0 诊断报告")
    lines.append("=" * 60)
    lines.append(f"品类：{category}")
    lines.append(f"范式：{paradigm}")
    lines.append("")

    # W(T) 计算
    lines.append("-" * 60)
    lines.append("【W(T) 计算】")
    lines.append(f"  v1.0 线性：{wt_v1:.4f}")
    lines.append(f"  v2.0 完整：{wt_v2:.4f}")
    lines.append(f"  主效应：{wt_details['main_effect']:.4f} (α={wt_details['alpha']})")
    lines.append(f"  交互效应：{wt_details['interaction_effect']:.4f} (β={wt_details['beta']})")
    lines.append(f"  激活函数：{wt_details['activation']}")
    lines.append("")

    # 各维度详情
    lines.append("  各维度贡献：")
    lines.append(f"  {'维度':<12}{'权重':>6}{'t':>6}{'注意力':>6}{'激活':>8}{'贡献':>8}")
    for d in wt_details["main_details"]:
        lines.append(f"  {d['dimension']:<12}{d['weight']:>6.2f}{d['t']:>6.1f}{d['attention']:>6.1f}{d['activation']:>8.3f}{d['contribution']:>8.4f}")
    lines.append("")

    # 交互项
    if wt_details["interaction_details"]:
        lines.append("  交互项贡献：")
        for d in wt_details["interaction_details"]:
            lines.append(f"    {d['pair']:<20} 系数={d['coefficient']:.1f} 贡献={d['contribution']:.4f}")
        lines.append("")

    # 子维度评分
    if sub_scores and bea_details:
        lines.append("-" * 60)
        lines.append("【子维度评分】")
        dim_names = {"tension": "双极张力", "order": "结构秩序", "threshold": "阈值安全", "context": "语境适配"}
        for dim, subdim_list in SUBDIMENSIONS.items():
            dim_score = bea_details["dimension_scores"][dim]
            lines.append(f"  {dim_names[dim]}（{dim_score:.2f}）：")
            for sd in subdim_list:
                score = sub_scores.get(sd, 0.0)
                desc = SUBDIMENSION_DESCRIPTIONS.get(sd, "")
                lines.append(f"    {sd:<10} {score:.1f}/5  — {desc}")
        lines.append("")

        # BEA 美感总分
        lines.append("-" * 60)
        lines.append("【BEA 美感总分】")
        lines.append(f"  总分：{bea_score:.4f}（{bea_score*100:.1f}/100）")
        lines.append(f"  计算方法：{bea_details['method']}")
        lines.append(f"  美感定位：(W(T)={wt_v2:.3f}, BEA_Score={bea_score:.3f})")

        # 判定
        if bea_score >= 0.8:
            judgment = "成熟佳作"
        elif bea_score >= 0.6:
            judgment = "良好作品"
        elif bea_score >= 0.4:
            judgment = "一般作品"
        else:
            judgment = "待改进作品"
        lines.append(f"  判定：{judgment}")

        # 短板识别
        weak_dims = [(dim, score) for dim, score in bea_details["dimension_scores"].items() if score < 0.6]
        if weak_dims:
            lines.append(f"  短板维度：{', '.join(dim_names[d] for d, _ in weak_dims)}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


# ============================================================
# 主函数
# ============================================================
def main():
    ap = argparse.ArgumentParser(description="BEA 量化模型 v2.0 计算器")
    ap.add_argument("--category", choices=sorted(CATEGORY_WEIGHTS), help="品类")
    ap.add_argument("--t", help='各维度危极强度，如 "形状线条=2.5,色彩=3.0"')
    ap.add_argument("--weights", help='自定义权重 JSON，如 {"形状":0.5,"色彩":0.5}')
    ap.add_argument("--mode", choices=["simple", "full"], default="simple",
                    help="计算模式：simple（v1.0 兼容）或 full（v2.0 完整）")
    ap.add_argument("--activation", choices=["linear", "sigmoid", "power"], default="linear",
                    help="非线性激活函数（仅 full 模式）")
    ap.add_argument("--attention", help='注意力系数，如 "形状线条=1.2,细节线条=1.4"（仅 full 模式）')
    ap.add_argument("--alpha", type=float, default=0.7, help="主效应系数（仅 full 模式，默认 0.7）")
    ap.add_argument("--beta", type=float, default=0.3, help="交互效应系数（仅 full 模式，默认 0.3）")
    ap.add_argument("--no-interaction", action="store_true", help="禁用交互项（仅 full 模式）")
    ap.add_argument("--subscores", help='子维度评分，如 "对立清晰度=4,成对呼应度=3,..."')
    ap.add_argument("--score-method", choices=["geometric", "weighted"], default="geometric",
                    help="BEA 美感总分计算方法")
    ap.add_argument("--target", type=float, help="目标 W(T)（对照判定用）")
    ap.add_argument("--json", action="store_true", help="输出 JSON 格式")
    ap.add_argument("--report", action="store_true", help="输出诊断报告")
    ap.add_argument("--list", action="store_true", help="列出品类与维度")
    args = ap.parse_args()

    # 列出品类
    if args.list or not args.t:
        print("可用品类与维度（权重）：")
        for cat, dims in CATEGORY_WEIGHTS.items():
            print(f"  {cat}: " + ", ".join(f"{k}={v}" for k, v in dims.items()))
        print()
        print("交互维度对：")
        for cat, pairs in INTERACTION_PAIRS.items():
            print(f"  {cat}: " + ", ".join(f"{d1}×{d2}(c={c})" for d1, d2, c in pairs))
        print()
        print("子维度：")
        for dim, subdim_list in SUBDIMENSIONS.items():
            print(f"  {dim}: " + ", ".join(subdim_list))
        print()
        print('示例: python3 bea_quant_v2.py --category phone --t "形状线条=2.5,质感触觉=3.0,色彩=2.0,构图比例=2.0,光影=2.5,细节线条=6.5" --mode full --report')
        return

    # 解析权重
    if args.weights:
        weights = {k: float(v) for k, v in json.loads(args.weights).items()}
        if abs(sum(weights.values()) - 1) > 0.001:
            sys.exit(f"权重合计 {sum(weights.values()):.3f} ≠ 1")
    else:
        if not args.category:
            sys.exit("未提供 --weights 时必须指定 --category")
        weights = CATEGORY_WEIGHTS[args.category]

    # 解析维度强度
    try:
        tvals = parse_key_value(args.t)
    except ValueError as e:
        sys.exit(str(e))

    # 检查缺失维度
    missing = [d for d in weights if d not in tvals]
    if missing:
        sys.exit(f"缺少维度：{'、'.join(missing)}（该品类/权重表要求全部维度）")

    # 检查强度范围
    for dim, t in tvals.items():
        if not 0 <= t <= 10:
            sys.exit(f"{dim} 的强度 {t} 超出 0-10")

    # 解析注意力系数
    attention = None
    if args.attention:
        try:
            attention = parse_key_value(args.attention)
        except ValueError as e:
            sys.exit(str(e))

    # 解析子维度评分
    sub_scores = None
    if args.subscores:
        try:
            sub_scores = parse_key_value(args.subscores)
        except ValueError as e:
            sys.exit(str(e))
        # 检查评分范围
        for sd, s in sub_scores.items():
            if not 0 <= s <= 5:
                sys.exit(f"{sd} 的评分 {s} 超出 0-5")

    # 计算 W(T)
    wt_v1 = calculate_wt_v1(tvals, weights)

    if args.mode == "simple":
        wt_v2 = wt_v1
        wt_details = {
            "main_effect": wt_v1,
            "interaction_effect": 0.0,
            "alpha": 1.0,
            "beta": 0.0,
            "main_details": [
                {"dimension": d, "weight": weights[d], "t": tvals[d],
                 "attention": 1.0, "activation": tvals[d]/10.0,
                 "contribution": weights[d] * tvals[d] / 10.0}
                for d in weights
            ],
            "interaction_details": [],
            "activation": "linear",
            "wt_v1": wt_v1
        }
    else:
        wt_v2, wt_details = calculate_wt_v2(
            tvals, weights, args.category,
            activation=args.activation,
            attention=attention,
            alpha=args.alpha,
            beta=args.beta,
            use_interaction=not args.no_interaction
        )

    paradigm = paradigm_of(wt_v2)

    # 计算 BEA 美感总分
    bea_score = None
    bea_details = None
    if sub_scores:
        bea_score, bea_details = calculate_bea_score(
            sub_scores, args.category, method=args.score_method
        )

    # 输出
    if args.json:
        output = {
            "category": args.category,
            "mode": args.mode,
            "wt_v1": round(wt_v1, 4),
            "wt_v2": round(wt_v2, 4),
            "paradigm": paradigm,
            "activation": args.activation if args.mode == "full" else "linear",
            "tvals": tvals,
            "weights": weights,
            "wt_details": wt_details,
        }
        if attention:
            output["attention"] = attention
        if sub_scores:
            output["sub_scores"] = sub_scores
            output["bea_score"] = round(bea_score, 4)
            output["bea_details"] = bea_details
        if args.target is not None:
            output["target"] = args.target
            output["diff"] = round(wt_v2 - args.target, 4)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.report:
        print(format_report(
            args.category, tvals, wt_v1, wt_v2, wt_details,
            paradigm, bea_score, bea_details, sub_scores
        ))
    else:
        # 简洁输出
        print(f"{'维度':<12}{'权重':>6}{'t':>6}{'贡献':>8}  画像")
        for dim, w in weights.items():
            t = tvals[dim]
            contrib = w * t / 10
            bar = "█" * int(round(t))
            print(f"{dim:<12}{w:>6.2f}{t:>6.1f}{contrib:>8.3f}  T{bar:<10}")
        print("-" * 56)
        print(f"W(T) v1.0 = {wt_v1:.4f}")
        if args.mode == "full":
            print(f"W(T) v2.0 = {wt_v2:.4f}（{args.activation} 激活，α={args.alpha}, β={args.beta}）")
        print(f"范式落点：{paradigm}")
        if bea_score is not None:
            print(f"BEA 美感总分 = {bea_score:.4f}（{bea_score*100:.1f}/100）")
        if args.target is not None:
            diff = wt_v2 - args.target
            if abs(diff) <= 0.05:
                print(f"对照目标 {args.target:.2f}：落入区间（±0.05）")
            else:
                advise = "减锐增柔（降低高权重维度的 t）" if diff > 0 else "加锐减柔（提高高权重维度的 t）"
                print(f"对照目标 {args.target:.2f}：偏差 {diff:+.4f}，建议{advise}")


if __name__ == "__main__":
    main()
