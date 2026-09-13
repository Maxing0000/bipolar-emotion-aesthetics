#!/usr/bin/env python3
"""BEA 量化计算引擎 v2.0：W(T)计算 + 范式定位 + 四维评分 + 病症诊断 + 处方生成。

用法：
  python3 bea_quant.py --category phone --t "形状=4,质感=3,色彩=2,构图=2,光影=2,细节=5"
  python3 bea_quant.py --category car --t "形体=3,特征线=5,灯组=6,比例=3,材质=4" --target 0.40
  python3 bea_quant.py --interactive    # 交互模式，逐步输入
  python3 bea_quant.py --list           # 查看品类与维度

纯标准库，无外部依赖，离线可用。
"""
import argparse
import json
import sys

# ============================================================
# 品类权重
# ============================================================
CATEGORY_WEIGHTS = {
    "phone": {"形状": 0.25, "质感": 0.25, "色彩": 0.15, "构图": 0.15, "光影": 0.10, "细节": 0.10},
    "car": {"形体": 0.30, "特征线": 0.25, "灯组": 0.15, "比例": 0.15, "材质": 0.15},
    "brand": {"图形": 0.25, "色彩": 0.25, "字体": 0.20, "版式": 0.20, "质感": 0.10},
    "ui": {"布局": 0.25, "色彩对比": 0.20, "组件形": 0.20, "动效": 0.20, "字体图标": 0.15},
    "generic": {"形状": 0.20, "色彩": 0.20, "质感": 0.20, "构图": 0.20, "光影": 0.20},
}

# ============================================================
# 八范式区间
# ============================================================
PARADIGMS = [
    (0.15, "治愈松弛", "放松舒展、无攻击性，像被温柔接住"),
    (0.25, "亲和精致", "第一眼亲和、细看精密，商业世界最通用的高级感公式"),
    (0.37, "诗意朦胧", "含蓄暧昧、余韵悠长，像雾里看花"),
    (0.48, "均衡典雅", "刚柔各半、持久耐看，像有教养的贵族"),
    (0.58, "崇高震撼", "先敬畏后沉醉的深层震撼（康德意义的崇高）"),
    (0.64, "冷峻克制", "冷硬简、靠比例维持温度，像手术刀"),
    (0.70, "神秘魅惑", "幽暗诱人、不可捉摸，像深夜里的一束光"),
    (0.85, "先锋反叛", "刺激反叛、临界于不适，受众享受被挑战"),
    (float("inf"), "越阈非美", "超过审美窗口，变为焦虑/伤害"),
]

# ============================================================
# 病症库
# ============================================================
DISEASES = [
    {"name": "甜腻症", "type": "单一极性", "condition": "wt < 0.12",
     "desc": "亲极过载，全圆角全柔色无锐度，发腻幼稚廉价",
     "prescription": "高价值细节注入10%-20%危极（利落线/冷灰/清晰边界），柔中藏骨"},
    {"name": "攻击症", "type": "单一极性", "condition": "wt > 0.60 and max_t > 7",
     "desc": "危极过载，处处锐角强对比硬冷，令人紧张想回避",
     "prescription": "扩亲极基底、降危极到范式区间，用大曲面/柔光/对称接住张力"},
    {"name": "空洞症", "type": "单一极性", "condition": "max_t < 4 and wt < 0.30",
     "desc": "张力缺失，元素都对但无记忆点，一眼到头",
     "prescription": "造一对清晰双极对立（方圆/明暗/繁简）并用秩序收束"},
    {"name": "均分症", "type": "结构层级", "condition": "0.35 < wt < 0.50 and max_t < 6 and min_t > 2",
     "desc": "主辅缺失，亲危各半无主次，情绪暧昧",
     "prescription": "确立至少6:4主辅比，先让第一印象明确"},
    {"name": "重点通胀症", "type": "结构层级", "condition": "high_t_count >= 4",
     "desc": "哪里都想强调，结果哪里都不突出，视觉噪音大",
     "prescription": "做减法，强调点压回1-2个，建视觉等级"},
]


def paradigm_of(wt):
    for upper, name, desc in PARADIGMS:
        if wt < upper:
            return name, desc
    return PARADIGMS[-1][1], PARADIGMS[-1][2]


def quadrant_of(wt, order_score):
    """张力×秩序四象限"""
    tension = wt  # 0-1
    if tension >= 0.4 and order_score >= 18:
        return "美感黄金区", "高张力×高秩序，对立被秩序统摄，高级耐看经典"
    elif tension >= 0.4 and order_score < 18:
        return "失控焦虑区", "高张力×低秩序，刺激但杂乱，需补秩序"
    elif tension < 0.4 and order_score >= 18:
        return "呆板平庸区", "低张力×高秩序，整齐但无张力，需加张力"
    else:
        return "混沌平淡区", "低张力×低秩序，潦草廉价，先立秩序再加张力"


def diagnose(wt, t_values, order_score=20):
    """病症诊断"""
    max_t = max(t_values.values()) if t_values else 0
    min_t = min(t_values.values()) if t_values else 0
    high_t_count = sum(1 for v in t_values.values() if v >= 6)

    found = []
    for d in DISEASES:
        cond = d["condition"]
        try:
            if eval(cond, {"wt": wt, "max_t": max_t, "min_t": min_t,
                            "high_t_count": high_t_count, "order_score": order_score}):
                found.append(d)
        except:
            pass
    return found


def score_card(wt, t_values, category):
    """四维评分卡（简化版，基于极性分布估算）"""
    max_t = max(t_values.values()) if t_values else 0
    min_t = min(t_values.values()) if t_values else 0
    high_t_count = sum(1 for v in t_values.values() if v >= 6)
    low_t_count = sum(1 for v in t_values.values() if v <= 2)

    # 双极张力：有清晰对立且不过载
    if 0.15 <= wt <= 0.55 and 2 <= high_t_count <= 3:
        tension = 22
    elif wt < 0.12 or high_t_count == 0:
        tension = 10
    elif wt > 0.65 or high_t_count >= 5:
        tension = 12
    else:
        tension = 18

    # 结构秩序：简化估算（实际需人工判断）
    order = 20

    # 阈值安全：无越阈元素
    if max_t >= 9:
        threshold = 12
    elif max_t >= 8:
        threshold = 18
    else:
        threshold = 22

    # 语境适配：简化（实际需结合场景）
    context = 20

    total = tension + order + threshold + context
    return {
        "双极张力": tension,
        "结构秩序": order,
        "阈值安全": threshold,
        "语境适配": context,
        "总分": total,
        "判定": "成熟作品" if total >= 80 else ("有明显短板" if min(tension, order, threshold, context) < 15 else "待优化")
    }


def parse_t(spec):
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


def interactive():
    """交互模式"""
    print("=" * 60)
    print("  BEA 量化计算引擎 v2.0 - 交互模式")
    print("=" * 60)
    print("\n可用品类：")
    for cat, dims in CATEGORY_WEIGHTS.items():
        print(f"  {cat}: {', '.join(dims.keys())}")

    category = input("\n请输入品类（phone/car/brand/ui/generic）: ").strip()
    if category not in CATEGORY_WEIGHTS:
        print(f"未知品类 {category}，使用 generic")
        category = "generic"

    weights = CATEGORY_WEIGHTS[category]
    t_values = {}
    print(f"\n请输入各维度危极强度（0-10）：")
    for dim in weights:
        while True:
            try:
                val = input(f"  {dim}（权重{weights[dim]:.2f}）: ").strip()
                t = float(val)
                if 0 <= t <= 10:
                    t_values[dim] = t
                    break
                else:
                    print("  请输入0-10之间的数字")
            except ValueError:
                print("  请输入数字")

    target = input("\n目标 W(T)（可选，直接回车跳过）: ").strip()
    target = float(target) if target else None

    print_result(category, t_values, weights, target)


def print_result(category, t_values, weights, target=None):
    """打印完整分析结果"""
    # 计算 W(T)
    total = 0.0
    print("\n" + "=" * 60)
    print(f"  BEA 分析报告 - {category}")
    print("=" * 60)
    print(f"\n{'维度':<10}{'权重':>8}{'强度':>8}{'贡献':>10}  极性画像")
    print("-" * 60)
    for dim, w in weights.items():
        t = t_values.get(dim, 0)
        contrib = w * t / 10
        total += contrib
        bar = "█" * int(round(t))
        print(f"{dim:<10}{w:>8.2f}{t:>8.1f}{contrib:>10.3f}  T{bar}")

    print("-" * 60)
    print(f"{'W(T)':<10}{'':>8}{'':>8}{total:>10.3f}")

    # 范式定位
    p_name, p_desc = paradigm_of(total)
    print(f"\n【范式定位】{p_name}")
    print(f"  {p_desc}")

    # 四象限
    q_name, q_desc = quadrant_of(total, 20)
    print(f"\n【张力×秩序象限】{q_name}")
    print(f"  {q_desc}")

    # 评分卡
    scores = score_card(total, t_values, category)
    print(f"\n【四维评分卡】")
    for k, v in scores.items():
        if k != "判定":
            print(f"  {k}: {v}/25" if k != "总分" else f"  {k}: {v}/100")
    print(f"  判定: {scores['判定']}")

    # 病症诊断
    diseases = diagnose(total, t_values)
    if diseases:
        print(f"\n【病症诊断】发现 {len(diseases)} 个问题：")
        for i, d in enumerate(diseases, 1):
            print(f"\n  {i}. {d['name']}（{d['type']}）")
            print(f"     特征：{d['desc']}")
            print(f"     处方：{d['prescription']}")
    else:
        print(f"\n【病症诊断】未发现明显病症")

    # 目标对照
    if target is not None:
        diff = total - target
        print(f"\n【目标对照】目标 W(T)={target:.2f}")
        if abs(diff) <= 0.05:
            print(f"  ✅ 落入目标区间（±0.05）")
        else:
            advise = "减锐增柔（降低高权重维度的t）" if diff > 0 else "加锐减柔（提高高权重维度的t）"
            print(f"  ⚠️  偏差 {diff:+.3f}，建议{advise}")

    print("\n" + "=" * 60)


def main():
    ap = argparse.ArgumentParser(description="BEA 量化计算引擎 v2.0")
    ap.add_argument("--category", choices=sorted(CATEGORY_WEIGHTS), help="品类")
    ap.add_argument("--t", help='各维度危极强度，如 "形状=4,色彩=2"')
    ap.add_argument("--target", type=float, help="目标 W(T)")
    ap.add_argument("--interactive", action="store_true", help="交互模式")
    ap.add_argument("--list", action="store_true", help="列出品类与维度")
    ap.add_argument("--json", action="store_true", help="输出JSON格式")
    args = ap.parse_args()

    if args.list:
        print("可用品类与维度（权重）：")
        for cat, dims in CATEGORY_WEIGHTS.items():
            print(f"  {cat}: " + ", ".join(f"{k}={v}" for k, v in dims.items()))
        return

    if args.interactive:
        interactive()
        return

    if not args.t:
        ap.print_help()
        return

    if not args.category:
        args.category = "generic"

    weights = CATEGORY_WEIGHTS[args.category]
    t_values = parse_t(args.t)

    # 检查缺失维度
    missing = [d for d in weights if d not in t_values]
    if missing:
        print(f"⚠️  缺少维度：{'、'.join(missing)}，将按0计算")
        for d in missing:
            t_values[d] = 0

    if args.json:
        total = sum(weights[d] * t_values.get(d, 0) / 10 for d in weights)
        p_name, p_desc = paradigm_of(total)
        scores = score_card(total, t_values, args.category)
        diseases = [{"name": d["name"], "type": d["type"], "desc": d["desc"],
                     "prescription": d["prescription"]} for d in diagnose(total, t_values)]
        result = {
            "category": args.category,
            "wt": round(total, 3),
            "paradigm": p_name,
            "paradigm_desc": p_desc,
            "scores": scores,
            "diseases": diseases,
            "t_values": t_values,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_result(args.category, t_values, weights, args.target)


if __name__ == "__main__":
    main()
