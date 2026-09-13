#!/usr/bin/env python3
"""BEA 图片分析助手：引导式分析上传的产品/设计图片，生成标准化报告。

用法：
  python3 analyze_image.py                    # 交互模式，逐步引导分析
  python3 analyze_image.py --category phone   # 指定品类，跳过品类选择
  python3 analyze_image.py --quick            # 快速模式，只问核心问题
  python3 analyze_image.py --template         # 输出空白分析模板

纯标准库，无外部依赖，离线可用。
AI视觉自动识别需要额外配置API Key，本脚本提供手动引导模式。
"""
import argparse
import json
import sys
import os
from datetime import datetime

# ============================================================
# 品类配置
# ============================================================
CATEGORIES = {
    "phone": {
        "name": "手机/消费电子",
        "dimensions": ["形状线条", "色彩", "明度对比", "质感", "构图比例", "光影", "细节线条"],
        "weights": {"形状线条": 0.20, "色彩": 0.12, "明度对比": 0.08, "质感": 0.20,
                    "构图比例": 0.12, "光影": 0.08, "细节线条": 0.20},
        "questions": {
            "形状线条": "整机轮廓是圆润还是锐利？边缘倒角大还是小？（0=极圆润，10=极锐利）",
            "色彩": "主色调是暖还是冷？饱和度高还是低？（0=极暖极低饱和，10=极冷极高饱和）",
            "明度对比": "整体是亮还是暗？明暗过渡柔和还是硬边？（0=极亮极柔和，10=极暗极硬对比）",
            "质感": "表面是磨砂亲肤还是镜面冷金属？（0=极温润亲肤，10=极冰冷高反）",
            "构图比例": "是居中对称还是偏移？留白多还是少？（0=极对称多留白，10=极失衡满版）",
            "光影": "是柔光还是硬光？投影柔和还是锐利？（0=极柔光柔投影，10=极硬光长投影）",
            "细节线条": "按键/镜头/字体等细节是圆润还是锐利？（0=极圆润，10=极锐利）",
        }
    },
    "car": {
        "name": "汽车/交通工具",
        "dimensions": ["形体曲面", "特征线条", "灯组图形", "比例姿态", "材质光影"],
        "weights": {"形体曲面": 0.30, "特征线条": 0.25, "灯组图形": 0.15,
                    "比例姿态": 0.15, "材质光影": 0.15},
        "questions": {
            "形体曲面": "车身大面是饱满圆润还是棱角分明？（0=极饱满圆润，10=极棱角分明）",
            "特征线条": "腰线/特征线是柔和还是锐利？（0=极柔和，10=极锐利）",
            "灯组图形": "灯组造型是圆润还是锐利切角？（0=极圆润，10=极锐利）",
            "比例姿态": "是稳重水平还是前冲楔形？（0=极稳重水平，10=极前冲楔形）",
            "材质光影": "是温润漆面还是冷硬金属？（0=极温润，10=极冷硬）",
        }
    },
    "brand": {
        "name": "平面/品牌/海报",
        "dimensions": ["图形形状", "色彩", "字体", "版式构图", "质感"],
        "weights": {"图形形状": 0.25, "色彩": 0.25, "字体": 0.20, "版式构图": 0.20, "质感": 0.10},
        "questions": {
            "图形形状": "图形/Logo是圆润还是锐利？（0=极圆润，10=极锐利）",
            "色彩": "配色是柔和低饱和还是强烈高饱和撞色？（0=极柔和，10=极强烈）",
            "字体": "字体是圆润无衬线还是锐利衬线/哥特？（0=极圆润，10=极锐利）",
            "版式构图": "是居中对称留白还是偏移满版？（0=极对称留白，10=极偏移满版）",
            "质感": "是柔和哑光还是高反/纹理？（0=极柔和，10=极强烈）",
        }
    },
    "ui": {
        "name": "App界面/网页",
        "dimensions": ["布局留白", "色彩对比", "组件形状", "动效", "字体图标"],
        "weights": {"布局留白": 0.25, "色彩对比": 0.20, "组件形状": 0.20,
                    "动效": 0.20, "字体图标": 0.15},
        "questions": {
            "布局留白": "是宽松留白还是紧凑满版？（0=极宽松，10=极紧凑）",
            "色彩对比": "是柔和低对比还是强烈高对比？（0=极柔和，10=极强烈）",
            "组件形状": "卡片/按钮是大圆角还是直角？（0=极大圆角，10=极直角）",
            "动效": "是舒缓缓动还是快速骤变？（0=极舒缓，10=极骤变）",
            "字体图标": "是圆润还是锐利？（0=极圆润，10=极锐利）",
        }
    },
    "generic": {
        "name": "通用/其他",
        "dimensions": ["形状线条", "色彩", "明度对比", "质感", "构图比例", "光影"],
        "weights": {"形状线条": 0.20, "色彩": 0.20, "明度对比": 0.15,
                    "质感": 0.15, "构图比例": 0.15, "光影": 0.15},
        "questions": {
            "形状线条": "整体轮廓是圆润还是锐利？（0=极圆润，10=极锐利）",
            "色彩": "配色是柔和还是强烈？（0=极柔和，10=极强烈）",
            "明度对比": "明暗过渡是柔和还是硬边？（0=极柔和，10=极硬）",
            "质感": "表面是温润还是冰冷？（0=极温润，10=极冰冷）",
            "构图比例": "是对称稳定还是失衡动态？（0=极对称，10=极失衡）",
            "光影": "是柔光还是硬光？（0=极柔光，10=极硬光）",
        }
    },
}

# ============================================================
# 范式区间
# ============================================================
PARADIGMS = [
    (0.15, "治愈松弛"), (0.25, "亲和精致"), (0.37, "诗意朦胧"),
    (0.48, "均衡典雅"), (0.58, "崇高震撼"), (0.64, "冷峻克制"),
    (0.70, "神秘魅惑"), (0.85, "先锋反叛"), (float("inf"), "越阈非美"),
]


def paradigm_of(wt):
    for upper, name in PARADIGMS:
        if wt < upper:
            return name
    return "越阈非美"


def print_template():
    """输出空白分析模板"""
    print("=" * 70)
    print("  BEA 图片分析报告模板")
    print("=" * 70)
    print("""
【基本信息】
产品名称：
产品类型：
分析日期：

【大白话总结】
这个设计给人的第一感觉是：

【六维度极性拆解】
| 维度 | 元素描述 | 方向(P/T) | 强度(0-10) | 权重 | 作用 |
|---|---|---|---|---|---|
| 形状线条 | | | | | |
| 色彩 | | | | | |
| 明度对比 | | | | | |
| 质感 | | | | | |
| 构图比例 | | | | | |
| 光影 | | | | | |

【W(T)计算】
W(T) = Σ wᵢ · (tᵢ/10) =
范式定位：
张力×秩序象限：

【四维评分卡】
双极张力：/25
结构秩序：/25
阈值安全：/25
语境适配：/25
总分：/100

【优点】
1.
2.
3.

【改进点与处方】
1. 问题：
   维度： 当前T= → 目标T=
   具体做法：
2. ...

【改完预期】
W(T)： →
范式： →
总分： →

【适合人群】
适合：
不适合：
""")


def interactive_analysis(category=None, quick=False):
    """交互模式分析"""
    print("=" * 70)
    print("  BEA 图片分析助手 v1.0")
    print("=" * 70)
    print("\n请上传/打开你要分析的图片，然后按引导回答问题。\n")

    # 选择品类
    if category is None:
        print("可分析品类：")
        for key, cat in CATEGORIES.items():
            print(f"  {key}: {cat['name']}")
        category = input("\n请输入品类编号: ").strip()
        if category not in CATEGORIES:
            print(f"未知品类，使用 generic")
            category = "generic"

    cat = CATEGORIES[category]
    print(f"\n已选择：{cat['name']}")
    print(f"分析维度：{', '.join(cat['dimensions'])}")
    print("\n请根据图片内容，为每个维度打分（0-10）：")
    print("  0 = 极亲极（圆润/柔和/温暖/对称）")
    print("  10 = 极危极（锐利/强烈/冰冷/失衡）")
    print()

    # 收集各维度评分
    t_values = {}
    for dim in cat["dimensions"]:
        question = cat["questions"].get(dim, f"{dim}的极性强度？（0-10）")
        while True:
            try:
                val = input(f"  {dim}: {question}\n  请输入0-10: ").strip()
                t = float(val)
                if 0 <= t <= 10:
                    t_values[dim] = t
                    break
                else:
                    print("  请输入0-10之间的数字")
            except ValueError:
                print("  请输入数字")

    # 快速模式跳过详细问题
    if not quick:
        print("\n--- 补充信息（可选，直接回车跳过）---")
        product_name = input("  产品名称: ").strip() or "未命名产品"
        first_feeling = input("  第一感觉（大白话）: ").strip() or "待补充"
    else:
        product_name = "未命名产品"
        first_feeling = "待补充"

    # 计算 W(T)
    weights = cat["weights"]
    wt = sum(weights[d] * t_values.get(d, 0) / 10 for d in weights)
    paradigm = paradigm_of(wt)

    # 生成报告
    report = generate_report(product_name, category, cat, t_values, weights, wt, paradigm, first_feeling)

    # 打印报告
    print("\n" + "=" * 70)
    print(report)
    print("=" * 70)

    # 保存报告
    save = input("\n是否保存报告到文件？(y/n): ").strip().lower()
    if save == "y":
        filename = f"bea-analysis-{category}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ 报告已保存到: {os.path.abspath(filename)}")

    return report


def generate_report(product_name, category_key, category, t_values, weights, wt, paradigm, first_feeling):
    """生成分析报告"""
    lines = []
    lines.append(f"# BEA 图片分析报告：{product_name}")
    lines.append("")
    lines.append(f"**分析日期**：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**产品类型**：{category['name']}")
    lines.append(f"**分析方法**：BEA 双极情绪美学 v2.0")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 大白话总结")
    lines.append("")
    lines.append(f"{first_feeling}")
    lines.append("")
    lines.append(f"在BEA理论中，这属于**{paradigm}**范式，W(T)={wt:.3f}。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 六维度极性拆解")
    lines.append("")
    lines.append("| 维度 | 方向 | 强度(0-10) | 权重 | 极性画像 |")
    lines.append("|---|---|---|---|---|")
    for dim in category["dimensions"]:
        t = t_values.get(dim, 0)
        direction = "T(危极)" if t >= 5 else "P(亲极)"
        bar = "█" * int(round(t)) + "░" * (10 - int(round(t)))
        lines.append(f"| {dim} | {direction} | {t:.1f} | {weights[dim]:.2f} | {bar} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## W(T) 计算与范式定位")
    lines.append("")
    lines.append("```")
    lines.append(f"W(T) = Σ wᵢ · (tᵢ/10)")
    for dim in category["dimensions"]:
        t = t_values.get(dim, 0)
        contrib = weights[dim] * t / 10
        lines.append(f"  {dim}: {weights[dim]:.2f} × {t:.1f}/10 = {contrib:.3f}")
    lines.append(f"  合计: {wt:.3f}")
    lines.append("```")
    lines.append("")
    lines.append(f"**范式定位**：{paradigm}")
    lines.append(f"**W(T)**：{wt:.3f}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 改进建议")
    lines.append("")

    # 简单改进建议
    high_t_dims = [(d, t) for d, t in t_values.items() if t >= 7]
    low_t_dims = [(d, t) for d, t in t_values.items() if t <= 2]

    if high_t_dims:
        lines.append("### 危极偏强的维度（建议适当柔化）")
        for d, t in high_t_dims:
            lines.append(f"- **{d}**（T={t:.1f}）：建议降低到 T=5-6，增加亲极元素平衡")
        lines.append("")

    if low_t_dims:
        lines.append("### 亲极强但可能缺乏张力的维度（建议适当增加细节锐度）")
        for d, t in low_t_dims:
            lines.append(f"- **{d}**（T={t:.1f}）：建议在高价值细节处注入 T=4-5 的危极，柔中藏骨")
        lines.append("")

    if not high_t_dims and not low_t_dims:
        lines.append("各维度极性分布较为均衡，整体配比合理。建议关注：")
        lines.append("- 主辅比是否达到 6:4 以上")
        lines.append("- 对立元素是否成对出现")
        lines.append("- 秩序主线是否贯穿全局")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 适合人群")
    lines.append("")
    if wt < 0.25:
        lines.append("- **适合**：喜欢柔和、温暖、治愈感的用户；母婴、疗愈、家居场景")
        lines.append("- **不适合**：追求科技感、力量感、个性表达的用户")
    elif wt < 0.48:
        lines.append("- **适合**：大多数主流用户，追求精致、耐看、有品质感")
        lines.append("- **不适合**：极端追求个性或极致柔和的用户")
    elif wt < 0.64:
        lines.append("- **适合**：喜欢科技感、力量感、专业感的用户；高端、旗舰定位")
        lines.append("- **不适合**：追求柔和、治愈、亲和力的用户")
    else:
        lines.append("- **适合**：追求个性、反叛、先锋感的用户；潮牌、亚文化、概念设计")
        lines.append("- **不适合**：大众主流用户，可能觉得过于刺激或有攻击性")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本报告基于 BEA 双极情绪美学理论生成，审美具有主观性，仅供参考。*")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="BEA 图片分析助手")
    ap.add_argument("--category", choices=sorted(CATEGORIES.keys()), help="指定品类")
    ap.add_argument("--quick", action="store_true", help="快速模式")
    ap.add_argument("--template", action="store_true", help="输出空白分析模板")
    args = ap.parse_args()

    if args.template:
        print_template()
        return

    interactive_analysis(args.category, args.quick)


if __name__ == "__main__":
    main()
