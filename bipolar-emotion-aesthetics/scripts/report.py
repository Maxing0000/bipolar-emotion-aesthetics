#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BEA 一键诊断报告：打分 + W(T) + 范式落点 + 处方 + 评分卡，合成一份 Markdown。

用法：
  python3 report.py --category phone --t "形状线条=5,质感触觉=4,色彩=6,构图比例=6,光影=3,细节线条=4"
  python3 report.py --category car --t "..." --target 0.40 --name "仰望 U9"
  python3 report.py --category phone --t "..." --target 0.28 --scores "张力=20,秩序=22,阈值=23,语境=21" --out report.md

图像诊断全流程的最后一步：rubric 打分 → wt_calc 算分 → prescribe 处方 → report 成文。
CLI 与 MCP（bea_report）输出一致（tests/test_mcp_sync.py 校验）。
分值为协作刻度，不是心理物理常数。
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import scoresheet  # noqa: E402
import wt_calc  # noqa: E402


def _bar(v, vmax=10, width=10):
    n = int(round(v / vmax * width))
    return "█" * n + "░" * (width - n)


def generate_report(category, weights, tvals, target=0.0, scores=None,
                    name="", date_str=None):
    """生成完整 Markdown 诊断报告（MCP 端 bea_report 输出与本函数保持一致）。

    category  品类名（展示用）；weights 权重表；tvals 各维度 t 值（float）；
    target    目标 W(T)，>0 时输出目标对照与诊断处方；
    scores    可选，四维评分卡 {"张力": 20, ...}（各 25 分）；
    name      可选，诊断对象名（如「iPhone 17 Pro」）；
    date_str  可选，固定日期（测试用），默认今天。
    """
    total, contribs = wt_calc.compute_wt(weights, tvals)
    date_str = date_str or datetime.date.today().isoformat()
    L = []
    L.append(f"# BEA 形式诊断报告{f'：{name}' if name else ''}")
    L.append("")
    L.append(f"- 品类：{category}")
    L.append(f"- 日期：{date_str}")
    L.append("- 方法：双极情绪美学（BEA）W(T) 危极指数（分值为协作刻度，非心理物理常数）")
    L.append("")
    L.append("## 1 逐维打分与 W(T)")
    L.append("")
    L.append("| 维度 | 权重 | t 值 | 贡献 | 画像 |")
    L.append("|---|---:|---:|---:|---|")
    for dim, w in weights.items():
        t = tvals[dim]
        L.append(f"| {dim} | {w:.2f} | {t:g} | {contribs[dim]:.3f} | {_bar(t)} |")
    L.append("")
    L.append(f"**W(T) = {total:.3f}** ｜ 范式落点：**{wt_calc.paradigm_of(total)}**")
    if target:
        diff = total - target
        if abs(diff) <= 0.05:
            L.append(f"\n对照目标 {target:.2f}：落入区间（±0.05）✓")
        else:
            advise = "减锐增柔（降低高权重维度的 t）" if diff > 0 else "加锐减柔（提高高权重维度的 t）"
            L.append(f"\n对照目标 {target:.2f}：偏差 {diff:+.3f}，建议{advise}")
    if target and abs(total - target) > 0.05:
        L.append("")
        L.append(f"## 2 诊断处方（现状 {total:.3f} → 目标 {target:.2f}）")
        L.append("")
        p_lines, _ = wt_calc.prescribe(weights, tvals, target)
        L.append("```")
        L.extend(p_lines)
        L.append("```")
    if scores:
        L.append("")
        L.append("## 3 成稿评分卡")
        L.append("")
        L.append("| 维度 | 得分 | 画像 |")
        L.append("|---|---:|---|")
        sc_total = 0.0
        shorts = []
        for d in scoresheet.DIMENSIONS:
            v = float(scores[d])
            sc_total += v
            flag = " ⚠️短板" if v < 15 else ""
            L.append(f"| {scoresheet.FULL_NAMES[d]} | {v:g}/25{flag} | {_bar(v, 25, 25)} |")
            if v < 15:
                shorts.append(d)
        verdict = "成熟作品（≥80）" if sc_total >= 80 else "未成熟（<80）"
        L.append("")
        L.append(f"**总分 {sc_total:g}/100 — {verdict}**")
        if shorts:
            L.append("")
            L.append("短板修复指引：")
            for d in shorts:
                L.append(f"- **{scoresheet.FULL_NAMES[d]}**：{scoresheet.FIX_MAP[d]}")
    L.append("")
    L.append("---")
    L.append("*由 BEA 工具链生成（report.py / bea_report）。改进后请复评 t 值，并回六步法第五步「校阈」复验本能/认知/文化三阈。*")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="BEA 一键诊断报告（Markdown）")
    ap.add_argument("--category", required=True, help="品类：phone/car/brand/ui")
    ap.add_argument("--t", required=True, help='各维度危极强度，如 "形状线条=5,质感触觉=4,..."')
    ap.add_argument("--target", type=float, default=0.0, help="目标 W(T)，给出时输出诊断处方")
    ap.add_argument("--scores", help='四维评分卡，如 "张力=20,秩序=22,阈值=23,语境=21"')
    ap.add_argument("--weights", help="自定义权重 JSON（合计须为 1）")
    ap.add_argument("--name", default="", help="诊断对象名（报告标题用）")
    ap.add_argument("--out", help="输出到文件（默认打印到 stdout）")
    args = ap.parse_args()

    if args.weights:
        weights = {k: float(v) for k, v in
                   __import__("json").loads(args.weights).items()}
        if abs(sum(weights.values()) - 1) > 0.001:
            sys.exit(f"权重合计 {sum(weights.values()):.3f} ≠ 1")
    else:
        weights = wt_calc.CATEGORY_WEIGHTS.get(args.category)
        if weights is None:
            sys.exit(f"未知品类 {args.category!r}（可用：{'/'.join(sorted(wt_calc.CATEGORY_WEIGHTS))}）")

    try:
        tvals = wt_calc.parse_t(args.t)
        missing = [d for d in weights if d not in tvals]
        if missing:
            sys.exit(f"缺少维度：{'、'.join(missing)}（该品类要求：{'、'.join(weights)}）")
        scores = scoresheet.parse_scores(args.scores) if args.scores else None
    except ValueError as e:
        sys.exit(f"输入错误：{e}")

    md = generate_report(args.category, weights, tvals,
                         target=args.target, scores=scores, name=args.name)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md + "\n")
        print(f"✓ 报告已写入 {args.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
