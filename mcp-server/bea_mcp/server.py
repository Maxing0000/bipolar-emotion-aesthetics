#!/usr/bin/env python3
"""BEA MCP Server：把双极情绪美学的计算工具暴露给所有 MCP 客户端。

提供五个工具：
  bea_wt_calc       W(T) 危极指数计算：范式落点 + 极性画像 + 目标对照
  bea_wt_compare    A/B 双方案对比：双画像 + 差异维度 + 目标接近度裁决
  bea_prescribe     诊断处方：从现状到目标 W(T) 的维度调整方案与具体手法
  bea_scoresheet    评分卡：四维打分 + 短板定位 + 六步法修复映射
  bea_list_categories  列出内置品类与维度权重表

数据表与仓库 bipolar-emotion-aesthetics/scripts/ 中的 wt_calc.py、scoresheet.py 保持一致
（tests/test_mcp_sync.py 做同步校验）。分值为协作刻度，不是心理物理常数。

运行：python -m bea_mcp.server   （stdio 传输）
"""
import json

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------- 数据表（与 scripts/wt_calc.py 同步）

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

DIMENSIONS = ["张力", "秩序", "阈值", "语境"]
FULL_NAMES = {"张力": "双极张力", "秩序": "结构秩序", "阈值": "阈值安全", "语境": "语境适配"}
FIX_MAP = {
    "张力": "回第四步「配比与强调」：调整主辅极比例（主导极 60%–90%），检查强调点数量（一视域 ≤2 个）；张力过低补危极细节锚点，过高降高权重维度 t 值。",
    "秩序": "回第三步「秩序组织」：叠加五种秩序手段（对称/比例/节奏/层级/呼应），确立至少一条贯穿全局的统一要素（共同色板/栅格/母题）。",
    "阈值": "回第五步「校阈」：本能红线一票否决；认知阈靠补秩序/降复杂度右移；文化阈做符号审计（audit-templates.md 模板 8）。",
    "语境": "回第二步「范式选择」：重做受众三问（阈值/距离时长/第一情绪），检查符号层文化联想与使用场景是否错配。",
}

# 维度手法表：up=加锐（提 t）/down=减锐（降 t）的具体形式手法（与 wt_calc.py 同步）
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

# ---------------------------------------------------------------- 计算逻辑

def paradigm_of(wt: float) -> str:
    for upper, name in PARADIGM_RANGES:
        if wt < upper:
            return name
    return PARADIGM_RANGES[-1][1]


def compute_wt(weights: dict, tvals: dict):
    contribs = {dim: w * tvals[dim] / 10 for dim, w in weights.items()}
    return sum(contribs.values()), contribs


def _profile_block(weights, tvals, label=None):
    total, contribs = compute_wt(weights, tvals)
    lines = []
    if label:
        lines.append(f"—— {label} ——")
    lines.append(f"{'维度':<12}{'权重':>6}{'t':>5}{'贡献':>8}  画像")
    for dim, w in weights.items():
        t = tvals[dim]
        bar = "█" * int(round(t))
        lines.append(f"{dim:<12}{w:>6.2f}{t:>5.1f}{contribs[dim]:>8.3f}  T{bar:<10}")
    lines.append("-" * 56)
    lines.append(f"W(T) = {total:.3f}    范式落点：{paradigm_of(total)}")
    return total, lines


def _target_line(total, target):
    diff = total - target
    if abs(diff) <= 0.05:
        return f"对照目标 {target:.2f}：落入区间（±0.05）"
    advise = "减锐增柔（降低高权重维度的 t）" if diff > 0 else "加锐减柔（提高高权重维度的 t）"
    return f"对照目标 {target:.2f}：偏差 {diff:+.3f}，建议{advise}"


def _resolve_weights(category, weights):
    if weights:
        w = _to_float_map(weights)
        if abs(sum(w.values()) - 1) > 0.001:
            raise ValueError(f"权重合计 {sum(w.values()):.3f} ≠ 1")
        return w
    if category not in CATEGORY_WEIGHTS:
        raise ValueError(f"未知品类 {category!r}，可用：{'/'.join(sorted(CATEGORY_WEIGHTS))}（或传 weights 自定义）")
    return CATEGORY_WEIGHTS[category]


def _to_float_map(d, label=""):
    """dict 值统一转 float，非数字给出友好报错。"""
    out = {}
    for k, v in d.items():
        try:
            out[k] = float(v)
        except (TypeError, ValueError):
            raise ValueError(f"{label}{k} 的值 {v!r} 不是数字")
    return out


def _check_tvals(weights, tvals, label=""):
    missing = [d for d in weights if d not in tvals]
    if missing:
        raise ValueError(f"{label}缺少维度：{'、'.join(missing)}（该品类要求全部维度：{'、'.join(weights)}）")
    for k, v in tvals.items():
        if not 0 <= float(v) <= 10:
            raise ValueError(f"{label}维度 {k} 的强度 {v} 超出 0-10")


def prescribe(weights, tvals, target, max_step=3):
    """诊断处方：从现状到目标 W(T) 的维度调整方案（与 wt_calc.py 同步）。

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


# ---------------------------------------------------------------- MCP 服务

mcp = FastMCP(
    "bea-aesthetics",
    instructions=(
        "双极情绪美学（BEA）计算工具集。BEA 认为美感=可控张力下的情绪奖赏：每个形式元素都在"
        "亲极（柔和安全）与危极（锐利警觉）之间定位，W(T) 是各维度危极强度的品类加权和。"
        "先用 bea_list_categories 查品类维度，再用 bea_wt_calc 计算落点；两方案取舍用 bea_wt_compare；"
        "有明确目标范式/W(T) 时用 bea_prescribe 直接出维度调整处方与具体手法；"
        "成稿验收用 bea_scoresheet（四维各 25 分，≥80 成熟，<15 为短板）。"
        "0-10 刻度与 W(T) 为协作参照，非心理物理常数。"
    ),
)


@mcp.tool()
def bea_list_categories() -> str:
    """列出 BEA 内置品类及其维度权重表（phone/car/brand/ui），供计算前查询维度名称与权重。"""
    lines = ["可用品类与维度（权重）："]
    for cat, dims in CATEGORY_WEIGHTS.items():
        lines.append(f"  {cat}: " + ", ".join(f"{k}={v}" for k, v in dims.items()))
    lines.append("\n范式锚点：0.1 治愈｜0.2 亲和精致｜0.4 均衡典雅｜0.55 崇高｜0.62 冷峻｜0.7 先锋｜>0.85 越阈")
    return "\n".join(lines)


@mcp.tool()
def bea_wt_calc(category: str, t: dict, target: float = 0.0, weights: dict = None) -> str:
    """计算 BEA 危极指数 W(T)：输入品类与各维度危极强度（0-10），输出 W(T)、范式落点、极性画像与目标对照。

    Args:
        category: 品类，phone/car/brand/ui 之一（自定义权重时随意填）
        t: 各维度危极强度，如 {"形状线条": 2, "质感触觉": 4, "色彩": 2, "构图比例": 3, "光影": 3, "细节线条": 3}
        target: 可选，目标 W(T)（如 0.28），用于对照判定；0 表示不对照
        weights: 可选，自定义权重表（合计须为 1），提供时忽略 category
    """
    try:
        w = _resolve_weights(category, weights)
        tv = _to_float_map(t)
        _check_tvals(w, tv)
    except ValueError as e:
        return f"输入错误：{e}"
    total, lines = _profile_block(w, tv)
    if target:
        lines.append(_target_line(total, target))
    return "\n".join(lines)


@mcp.tool()
def bea_wt_compare(category: str, t_a: dict, t_b: dict, target: float = 0.0, weights: dict = None) -> str:
    """A/B 双方案对比：分别计算 W(T) 与画像，输出差异维度排序与目标接近度裁决。

    Args:
        category: 品类，phone/car/brand/ui 之一
        t_a: 方案 A 各维度危极强度（0-10）
        t_b: 方案 B 各维度危极强度（0-10）
        target: 可选，目标 W(T)；提供时裁决哪个方案更接近目标
        weights: 可选，自定义权重表（合计须为 1）
    """
    try:
        w = _resolve_weights(category, weights)
        ta = _to_float_map(t_a, "A ")
        tb = _to_float_map(t_b, "B ")
        _check_tvals(w, ta, "A ")
        _check_tvals(w, tb, "B ")
    except ValueError as e:
        return f"输入错误：{e}"
    total_a, lines = _profile_block(w, ta, "方案 A")
    total_b, lines_b = _profile_block(w, tb, "方案 B")
    lines += [""] + lines_b + ["", "=" * 56]
    lines.append(f"A/B 对比：A={total_a:.3f}（{paradigm_of(total_a)}） vs B={total_b:.3f}（{paradigm_of(total_b)}）")
    diffs = sorted(((d, tb[d] - ta[d]) for d in w), key=lambda x: -abs(x[1]))
    main = [f"{d} {x:+.0f}" for d, x in diffs if abs(x) >= 1]
    if main:
        lines.append("拉开差距的维度：" + "、".join(main))
    sharper, softer = ("B", "A") if total_b > total_a else ("A", "B")
    lines.append(f"解读：{sharper} 更锐（张力更高），{softer} 更柔。")
    if target:
        da, db = abs(total_a - target), abs(total_b - target)
        closer = "A" if da < db else ("B" if db < da else "两者持平")
        lines.append(f"对照目标 {target:.2f}：{closer} 更接近（A 差 {da:.3f}，B 差 {db:.3f}）。")
    return "\n".join(lines)


@mcp.tool()
def bea_prescribe(category: str, t: dict, target: float, weights: dict = None) -> str:
    """诊断处方：输入现状各维度危极强度与目标 W(T)，输出维度级调整方案——先动哪个维度、调几档、用什么具体设计手法。

    Args:
        category: 品类，phone/car/brand/ui 之一（自定义权重时随意填）
        t: 现状各维度危极强度（0-10），如 {"形状线条": 5, "质感触觉": 4, "色彩": 6, "构图比例": 6, "光影": 3, "细节线条": 4}
        target: 目标 W(T)（必填，如 0.28）；范式锚点：0.1 治愈｜0.2 亲和精致｜0.4 均衡典雅｜0.55 崇高｜0.62 冷峻｜0.7 先锋
        weights: 可选，自定义权重表（合计须为 1），提供时忽略 category
    """
    try:
        w = _resolve_weights(category, weights)
        tv = _to_float_map(t)
        _check_tvals(w, tv)
        if not 0 < float(target) < 1:
            raise ValueError(f"target {target} 应在 (0, 1) 区间")
    except ValueError as e:
        return f"输入错误：{e}"
    lines, _ = prescribe(w, tv, float(target))
    return "\n".join(lines)


@mcp.tool()
def bea_scoresheet(scores: dict) -> str:
    """BEA 评分卡：四维打分（各 25 分），输出总分、短板定位与六步法修复指引。≥80 成熟，任一维 <15 为短板。

    Args:
        scores: 四维得分，如 {"张力": 20, "秩序": 22, "阈值": 23, "语境": 21}
    """
    try:
        sc = _to_float_map(scores)
        missing = [d for d in DIMENSIONS if d not in sc]
        if missing:
            raise ValueError(f"缺少维度：{'、'.join(missing)}（应为：{'/'.join(DIMENSIONS)}）")
        for d in DIMENSIONS:
            if not 0 <= sc[d] <= 25:
                raise ValueError(f"{FULL_NAMES[d]} 得分 {sc[d]} 超出 0-25")
    except (ValueError, AttributeError) as e:
        return f"输入错误：{e}"

    total = sum(sc[d] for d in DIMENSIONS)
    shorts = [d for d in DIMENSIONS if sc[d] < 15]
    lines = ["BEA 评分卡", "-" * 44]
    for d in DIMENSIONS:
        v = sc[d]
        bar = "█" * int(round(v))
        flag = "  ⚠ 短板" if v < 15 else ""
        lines.append(f"{FULL_NAMES[d]:<6}{v:>6.1f}/25  {bar:<25}{flag}")
    lines.append("-" * 44)
    verdict = "成熟作品（≥80）" if total >= 80 else "未成熟（<80）"
    lines.append(f"总分 {total:.1f}/100    {verdict}")
    if shorts:
        lines.append("\n短板修复指引（回六步法对应环节）：")
        for d in shorts:
            lines.append(f"  · {FULL_NAMES[d]}：{FIX_MAP[d]}")
    else:
        lines.append("无短板维度（均 ≥15）。")
    return "\n".join(lines)


def main():
    mcp.run()  # stdio 传输


if __name__ == "__main__":
    main()
