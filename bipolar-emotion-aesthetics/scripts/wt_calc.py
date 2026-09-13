#!/usr/bin/env python3
"""BEA W(T) 计算器：输入各维度危极强度，输出 W(T)、范式落点与极性画像。

用法：
  python3 wt_calc.py --category car --t "形体曲面动势=2,特征线条=2,灯组图形=3,比例姿态=2,材质光影=3"
  python3 wt_calc.py --category phone --t "形状线条=2,质感触觉=3,色彩=2,构图比例=2,光影=2,细节线条=6"
  python3 wt_calc.py --category car --t "..." --target 0.40   # 对照目标区间
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


def main():
    ap = argparse.ArgumentParser(description="BEA W(T) 计算器")
    ap.add_argument("--category", choices=sorted(CATEGORY_WEIGHTS), help="品类")
    ap.add_argument("--t", help='各维度危极强度，如 "形状=2,色彩=3"')
    ap.add_argument("--weights", help='自定义权重 JSON，如 {"形状":0.5,"色彩":0.5}')
    ap.add_argument("--target", type=float, help="目标 W(T)（对照判定用）")
    ap.add_argument("--list", action="store_true", help="列出品类与维度")
    args = ap.parse_args()

    if args.list or not args.t:
        print("可用品类与维度（权重）：")
        for cat, dims in CATEGORY_WEIGHTS.items():
            print(f"  {cat}: " + ", ".join(f"{k}={v}" for k, v in dims.items()))
        print('\n示例: python3 wt_calc.py --category car --t "形体曲面动势=2,特征线条=2,灯组图形=3,比例姿态=2,材质光影=3"')
        return

    if args.weights:
        weights = {k: float(v) for k, v in json.loads(args.weights).items()}
        if abs(sum(weights.values()) - 1) > 0.001:
            sys.exit(f"权重合计 {sum(weights.values()):.3f} ≠ 1")
    else:
        if not args.category:
            sys.exit("未提供 --weights 时必须指定 --category")
        weights = CATEGORY_WEIGHTS[args.category]

    tvals = parse_t(args.t)
    missing = [d for d in weights if d not in tvals]
    if missing:
        sys.exit(f"缺少维度：{'、'.join(missing)}（该品类/权重表要求全部维度）")

    total = 0.0
    print(f"{'维度':<12}{'权重':>6}{'t':>5}{'贡献':>8}  画像")
    for dim, w in weights.items():
        t = tvals[dim]
        contrib = w * t / 10
        total += contrib
        bar = "█" * int(round(t))
        print(f"{dim:<12}{w:>6.2f}{t:>5.1f}{contrib:>8.3f}  T{bar:<10}")

    print("-" * 56)
    print(f"W(T) = {total:.3f}    范式落点：{paradigm_of(total)}")
    if args.target is not None:
        diff = total - args.target
        if abs(diff) <= 0.05:
            print(f"对照目标 {args.target:.2f}：落入区间（±0.05）")
        else:
            advise = "减锐增柔（降低高权重维度的 t）" if diff > 0 else "加锐减柔（提高高权重维度的 t）"
            print(f"对照目标 {args.target:.2f}：偏差 {diff:+.3f}，建议{advise}")


if __name__ == "__main__":
    main()
