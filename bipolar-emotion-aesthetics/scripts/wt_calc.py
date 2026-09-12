#!/usr/bin/env python3
"""BEA W(T) 计算器：输入各维度危极强度，输出 W(T)、范式落点与极性画像。

用法：
  python3 wt_calc.py --category car --t "形体曲面动势=2,特征线条=2,灯组图形=3,比例姿态=2,材质光影=3"
  python3 wt_calc.py --category phone --t "形状线条=2,质感触觉=3,色彩=2,构图比例=2,光影=2,细节线条=6"
  python3 wt_calc.py --category car --t "..." --target 0.40   # 对照目标区间
  python3 wt_calc.py --category phone --t "方案A各维度" --compare "方案B各维度"  # A/B 对比
  python3 wt_calc.py --list                                    # 查看品类与维度

品类权重源自 method.md 第 3 节，可按项目用 --weights '{"维度":0.2,...}' 覆盖（合计须为 1）。
分值为协作刻度，不是心理物理常数。
"""
import argparse
import json
import sys

CATEGORY_WEIGHTS = {
    "phone": {"形状线条": 0.25, "质感触觉": 0.25, "色彩": 0.15, "构图比例": 0.15, "光影": 0.10, "细节线条": 0.10},
    "car": {"形体曲面动势": 0.30, "特征线条": 0.25, "灯组图形": 0.15, "比例姿态": 0.15, "材质光影": 0.15},
    "brand": {"图形形状": 0.25, "色彩": 0.25, "字体": 0.20, "版式构图": 0.20, "质感": 0.10},
    "ui": {"布局留白": 0.25, "色彩对比": 0.20, "组件形": 0.20, "动效": 0.20, "字体图标": 0.15},
}

PARADIGM_RANGES = [
    (0.15, "治愈松弛"),
    (0.30, "亲和精致"),
    (0.48, "均衡典雅"),
    (0.60, "崇高震撼（需单元素高强度支撑）"),
    (0.66, "冷峻克制"),
    (0.85, "先锋反叛"),
    (float("inf"), "逼近越阈——非美区"),
]

# 维度手法表：up=加锐（提 t）/down=减锐（降 t）的具体形式手法。
# 自定义权重表中未收录的维度，处方只给档位建议、不给手法。
DIM_MOVES = {
    # phone
    "形状线条": {"up": "引入锐利轮廓转折、切割感边缘或非常规机身长宽比", "down": "增大圆角、回归对称直板轮廓"},
    "质感触觉": {"up": "换冷硬材质（钛/陶瓷/磨砂金属）或强纹理表面", "down": "温润涂层、细腻喷砂、亲肤材质"},
    "色彩": {"up": "提高饱和度或明暗对比，尝试撞色/非常规配色", "down": "低饱和中性色、单色渐变"},
    "构图比例": {"up": "打破对称：偏心布局、放大单一模组占比", "down": "居中对称、经典分段比例"},
    "光影": {"up": "强化高光反差、锐利阴影、舞台式打光", "down": "柔光、低反差均匀照明"},
    "细节线条": {"up": "加装饰性刻线、锋芒倒角、外露结构细节", "down": "去装饰、隐藏接缝与开孔"},
    # car
    "形体曲面动势": {"up": "肌肉感曲面、俯冲姿态、外扩轮拱", "down": "平顺曲面、水平稳态轮廓"},
    "特征线条": {"up": "锋利折线、闪电式腰线、非常规分割线", "down": "圆润贯穿线、减少折线数量"},
    "灯组图形": {"up": "狭长锐角灯形、非常规灯语图形", "down": "圆润灯形、家族化经典布局"},
    "比例姿态": {"up": "低趴宽体、长车头等非常规比例", "down": "标准比例、抬高视觉重心"},
    "材质光影": {"up": "高反差漆色、碳纤维/哑光性能材质", "down": "高亮单色漆、镀铬饰条"},
    # brand
    "图形形状": {"up": "锐角、断裂、非常规几何或有机形", "down": "圆形/方正规整几何"},
    "字体": {"up": "非常规字重对比、锐笔定制字形", "down": "经典无衬线、统一字重"},
    "版式构图": {"up": "破格出血、对角动势、高密度排布", "down": "栅格对齐、大留白居中"},
    "质感": {"up": "肌理噪点、金属/全息等强材质感", "down": "扁平纯色、细腻渐变"},
    # ui
    "布局留白": {"up": "紧凑高密度、破格层叠布局", "down": "增大留白、呼吸感栅格"},
    "色彩对比": {"up": "高对比强调色、深色模式强反差", "down": "同色系低对比"},
    "组件形": {"up": "小圆角锐角、非常规组件形态", "down": "大圆角、标准控件形态"},
    "动效": {"up": "快速弹性、非常规转场动效", "down": "缓动淡入淡出"},
    "字体图标": {"up": "粗字重、锐利图标笔触", "down": "常规字重、圆润图标笔触"},
}


def paradigm_of(wt: float) -> str:
    for upper, name in PARADIGM_RANGES:
        if wt < upper:
            return name
    return PARADIGM_RANGES[-1][1]


def parse_t(spec: str):
    out = {}
    for pair in spec.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(f"格式错误：{pair!r}，应为 维度=强度")
        k, v = pair.rsplit("=", 1)
        t = float(v)
        if not 0 <= t <= 10:
            raise ValueError(f"{k} 的强度 {t} 超出 0-10")
        out[k.strip()] = t
    return out


def compute_wt(weights: dict, tvals: dict):
    """返回 (W(T), {维度: 贡献})。"""
    contribs = {dim: w * tvals[dim] / 10 for dim, w in weights.items()}
    return sum(contribs.values()), contribs


def resolve_weights(args):
    if args.weights:
        weights = {k: float(v) for k, v in json.loads(args.weights).items()}
        if abs(sum(weights.values()) - 1) > 0.001:
            sys.exit(f"权重合计 {sum(weights.values()):.3f} ≠ 1")
        return weights
    if not args.category:
        sys.exit("未提供 --weights 时必须指定 --category")
    return CATEGORY_WEIGHTS[args.category]


def print_profile(weights, tvals, label=None):
    total, contribs = compute_wt(weights, tvals)
    if label:
        print(f"—— {label} ——")
    print(f"{'维度':<12}{'权重':>6}{'t':>5}{'贡献':>8}  画像")
    for dim, w in weights.items():
        t = tvals[dim]
        bar = "█" * int(round(t))
        print(f"{dim:<12}{w:>6.2f}{t:>5.1f}{contribs[dim]:>8.3f}  T{bar:<10}")
    print("-" * 56)
    print(f"W(T) = {total:.3f}    范式落点：{paradigm_of(total)}")
    return total


def check_target(total, target):
    diff = total - target
    if abs(diff) <= 0.05:
        print(f"对照目标 {target:.2f}：落入区间（±0.05）")
    else:
        advise = "减锐增柔（降低高权重维度的 t）" if diff > 0 else "加锐减柔（提高高权重维度的 t）"
        print(f"对照目标 {target:.2f}：偏差 {diff:+.3f}，建议{advise}")


def prescribe(weights, tvals, target, max_step=3):
    """诊断处方：从现状到目标 W(T) 的维度调整方案。

    按权重杠杆从高到低排序，每维最多移动 max_step 档（t 每变 1，W 变 w/10）。
    返回 (输出行列表, 调整后 t 值 dict)。
    """
    total, _ = compute_wt(weights, tvals)
    lines = [
        f"现状 W(T) = {total:.3f}（{paradigm_of(total)}）",
        f"目标 W(T) = {target:.2f}（{paradigm_of(target)}）",
    ]
    gap = target - total
    if abs(gap) <= 0.05:
        lines.append(f"偏差 {gap:+.3f}，已落入目标区间（±0.05）——保持现状，只做细节质感精修。")
        return lines, dict(tvals)
    direction = "加锐" if gap > 0 else "减锐"
    lines += [f"偏差 {gap:+.3f}，方向：{direction}", "", "处方（高权重维度先动，杠杆最大）："]
    remaining = abs(gap)
    new_t = dict(tvals)
    steps = []
    for dim, w in sorted(weights.items(), key=lambda x: -x[1]):
        if remaining <= 0.005:
            break
        headroom = (10 - tvals[dim]) if gap > 0 else tvals[dim]
        dt = int(min(max_step, headroom, remaining * 10 / w + 0.999))
        if dt < 1:
            continue
        new_t[dim] = tvals[dim] + dt if gap > 0 else tvals[dim] - dt
        covered = w * dt / 10 * (1 if gap > 0 else -1)
        remaining -= abs(covered)
        move = DIM_MOVES.get(dim, {}).get("up" if gap > 0 else "down", "")
        steps.append((dim, tvals[dim], new_t[dim], dt, covered, move))
    for dim, old, new, dt, covered, move in steps:
        lines.append(f"  · {dim}：{old:.0f} → {new:.0f}（{direction} {dt} 档，贡献 {covered:+.3f}）")
        if move:
            lines.append(f"    手法：{move}")
    after, _ = compute_wt(weights, new_t)
    lines += ["", f"处方后 W(T) = {after:.3f}（{paradigm_of(after)}）"]
    if abs(after - target) > 0.05:
        lines.append(f"⚠ 单轮微调（每维 ≤{max_step} 档）未到位（差 {target - after:+.3f}）：可分两轮执行，或允许单维更大幅度调整。")
    else:
        lines.append("✓ 落入目标区间（±0.05）。")
    lines.append("提醒：t 值调整须落回具体形式决策；改后回六步法第五步「校阈」复验本能/认知/文化三阈。")
    return lines, new_t


def main():
    ap = argparse.ArgumentParser(description="BEA W(T) 计算器")
    ap.add_argument("--category", choices=sorted(CATEGORY_WEIGHTS), help="品类")
    ap.add_argument("--t", help='各维度危极强度，如 "形状=2,色彩=3"（A 方案）')
    ap.add_argument("--compare", help="B 方案各维度强度，与 --t 做 A/B 对比")
    ap.add_argument("--weights", help='自定义权重 JSON，如 {"形状":0.5,"色彩":0.5}')
    ap.add_argument("--target", type=float, help="目标 W(T)（对照判定用）")
    ap.add_argument("--prescribe", action="store_true", help="诊断处方：给出从现状到 --target 的维度调整方案与手法")
    ap.add_argument("--list", action="store_true", help="列出品类与维度")
    args = ap.parse_args()

    if args.list or not args.t:
        print("可用品类与维度（权重）：")
        for cat, dims in CATEGORY_WEIGHTS.items():
            print(f"  {cat}: " + ", ".join(f"{k}={v}" for k, v in dims.items()))
        print('\n示例: python3 wt_calc.py --category car --t "形体曲面动势=2,特征线条=2,灯组图形=3,比例姿态=2,材质光影=3"')
        return

    weights = resolve_weights(args)

    tvals_a = parse_t(args.t)
    missing = [d for d in weights if d not in tvals_a]
    if missing:
        sys.exit(f"缺少维度：{'、'.join(missing)}（该品类/权重表要求全部维度）")

    total_a = print_profile(weights, tvals_a, "方案 A" if args.compare else None)

    if args.compare:
        tvals_b = parse_t(args.compare)
        missing = [d for d in weights if d not in tvals_b]
        if missing:
            sys.exit(f"B 方案缺少维度：{'、'.join(missing)}")
        print()
        total_b = print_profile(weights, tvals_b, "方案 B")
        print()
        print("=" * 56)
        print(f"A/B 对比：A={total_a:.3f}（{paradigm_of(total_a)}） vs B={total_b:.3f}（{paradigm_of(total_b)}）")
        diffs = sorted(((dim, tvals_b[dim] - tvals_a[dim]) for dim in weights), key=lambda x: -abs(x[1]))
        main_dims = [f"{dim} {d:+.0f}" for dim, d in diffs if abs(d) >= 1]
        if main_dims:
            print("拉开差距的维度：" + "、".join(main_dims))
        sharper, softer = ("B", "A") if total_b > total_a else ("A", "B")
        print(f"解读：{sharper} 更锐（张力更高），{softer} 更柔。")
        if args.target is not None:
            da, db = abs(total_a - args.target), abs(total_b - args.target)
            closer = "A" if da < db else ("B" if db < da else "两者持平")
            print(f"对照目标 {args.target:.2f}：{closer} 更接近（A 差 {da:.3f}，B 差 {db:.3f}）。")
    elif args.target is not None:
        check_target(total_a, args.target)
        if args.prescribe:
            print()
            lines, _ = prescribe(weights, tvals_a, args.target)
            print("\n".join(lines))


if __name__ == "__main__":
    main()
