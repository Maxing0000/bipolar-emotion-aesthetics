#!/usr/bin/env python3
"""BEA 交互式引导脚本——不需要记命令，回答几个问题就能生成分析。

用法：
  python3 bea_guide.py
  python3 bea_guide.py --lang en  # 英文界面

功能：
  1. 选择品类
  2. 选择操作（分析/调整/生成/对比）
  3. 引导输入维度值
  4. 自动调用 bea_quant.py 执行
  5. 输出结果
"""
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BEA_QUANT = os.path.join(SCRIPT_DIR, "bea_quant.py")

CATEGORIES = {
    "1": ("phone", "手机 / 消费电子"),
    "2": ("car", "汽车 / 交通工具"),
    "3": ("brand", "品牌 / 平面设计"),
    "4": ("ui", "UI / 交互界面"),
    "5": ("building", "建筑 / 室内空间"),
}

OPERATIONS = {
    "1": ("report", "完整分析报告"),
    "2": ("suggest", "调整建议（给定目标，输出改法）"),
    "3": ("generate", "美感生成（给定目标，自动生成最优配置）"),
    "4": ("compare", "两个方案对比"),
    "5": ("sensitivity", "灵敏度分析（改哪个维度效果最明显）"),
}

PARADIGMS = {
    "1": ("治愈松弛", 0.10),
    "2": ("亲和精致", 0.22),
    "3": ("均衡典雅", 0.40),
    "4": ("崇高震撼", 0.55),
    "5": ("冷峻克制", 0.63),
    "6": ("先锋反叛", 0.75),
}


def print_header():
    print("=" * 56)
    print("  BEA 双极情绪美学 · 交互式引导")
    print("  不需要记命令，回答几个问题就能生成分析")
    print("=" * 56)
    print()


def choose_category():
    print("【第一步】选择品类：")
    for k, (_, name) in CATEGORIES.items():
        print(f"  {k}. {name}")
    print()
    while True:
        choice = input("请输入编号 (1-5): ").strip()
        if choice in CATEGORIES:
            cat, name = CATEGORIES[choice]
            print(f"  ✓ 已选择: {name}")
            print()
            return cat
        print("  ✗ 无效输入，请输入 1-5")


def choose_operation():
    print("【第二步】选择操作：")
    for k, (_, name) in OPERATIONS.items():
        print(f"  {k}. {name}")
    print()
    while True:
        choice = input("请输入编号 (1-5): ").strip()
        if choice in OPERATIONS:
            op, name = OPERATIONS[choice]
            print(f"  ✓ 已选择: {name}")
            print()
            return op
        print("  ✗ 无效输入，请输入 1-5")


def get_dimensions(category):
    """获取维度列表（与 bea_quant.py 的 CATEGORY_WEIGHTS 保持一致）"""
    defaults = {
        "phone": ["形状", "质感", "色彩", "构图", "光影", "细节"],
        "car": ["曲面", "特征线", "灯组", "比例", "材质"],
        "brand": ["图形", "色彩", "字体", "版式", "质感"],
        "ui": ["布局", "色彩对比", "组件形", "动效", "字体图标"],
        "building": ["形体轮廓", "立面线条", "比例尺度", "材质肌理", "光影空间"],
    }
    return defaults.get(category, ["维度1", "维度2", "维度3"])


def input_dimensions(category, dims):
    """引导用户输入每个维度的 t 值"""
    print("【第三步】输入各维度的危极强度（0-10）：")
    print("  0-3 = 亲极（柔和/圆润/安全）")
    print("  4-5 = 中性（平衡）")
    print("  6-7 = 危极（锐利/硬朗/唤醒）")
    print("  8-9 = 强危极（尖锐/强烈/冲击）")
    print("  10 = 越阈（真实不适，一票否决）")
    print()
    print("  提示：直接回车使用默认值（3），输入 '?' 查看该维度说明")
    print()

    values = {}
    for i, dim in enumerate(dims, 1):
        while True:
            raw = input(f"  {i}/{len(dims)} {dim} (0-10，默认3): ").strip()
            if raw == "":
                values[dim] = 3
                break
            if raw == "?":
                print(f"     {dim}：该维度的危极强度，数值越大越锐利/硬朗/有冲击力")
                continue
            try:
                val = int(raw)
                if 0 <= val <= 10:
                    values[dim] = val
                    break
                print("     ✗ 请输入 0-10 之间的整数")
            except ValueError:
                print("     ✗ 请输入数字")
    print()
    return values


def choose_target():
    """选择目标范式"""
    print("【目标】选择目标范式：")
    for k, (name, wt) in PARADIGMS.items():
        print(f"  {k}. {name} (W(T)≈{wt})")
    print()
    while True:
        choice = input("请输入编号 (1-6): ").strip()
        if choice in PARADIGMS:
            name, wt = PARADIGMS[choice]
            print(f"  ✓ 已选择: {name} (W(T)≈{wt})")
            print()
            return name, wt
        print("  ✗ 无效输入，请输入 1-6")


def run_bea(category, operation, values=None, target=None, target_wt=None):
    """执行 bea_quant.py"""
    cmd = [sys.executable, BEA_QUANT, operation, "--category", category]

    if operation in ("report", "suggest", "sensitivity") and values:
        t_str = ",".join(f"{k}={v}" for k, v in values.items())
        cmd.extend(["--t", t_str])

    if operation == "suggest" and target:
        cmd.extend(["--target", target])

    if operation == "sensitivity" and target_wt:
        cmd.extend(["--target", str(target_wt)])

    if operation == "generate" and target:
        cmd.extend(["--target", target])

    print("-" * 56)
    print(f"  执行: {' '.join(cmd)}")
    print("-" * 56)
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("【错误输出】")
        print(result.stderr)

    return result.returncode == 0


def main():
    print_header()

    # 检查 bea_quant.py 是否存在
    if not os.path.exists(BEA_QUANT):
        print(f"✗ 错误：找不到 {BEA_QUANT}")
        print("  请确保 bea_guide.py 和 bea_quant.py 在同一目录")
        sys.exit(1)

    category = choose_category()
    operation = choose_operation()

    if operation == "generate":
        target, target_wt = choose_target()
        print("【生成中...】")
        run_bea(category, operation, target=target)

    elif operation == "compare":
        print("【对比分析】")
        dims = get_dimensions(category)
        print(f"  维度: {', '.join(dims)}")
        print()
        print("  方案A（紧凑格式，按维度顺序）:")
        a_vals = input(f"    输入 {len(dims)} 个数字，用逗号分隔: ").strip()
        print()
        print("  方案B（紧凑格式，按维度顺序）:")
        b_vals = input(f"    输入 {len(dims)} 个数字，用逗号分隔: ").strip()
        print()

        cmd = [sys.executable, BEA_QUANT, "compare", "--category", category,
               "--a", f"方案A={a_vals}", "--b", f"方案B={b_vals}"]
        print("-" * 56)
        print(f"  执行: {' '.join(cmd)}")
        print("-" * 56)
        print()
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("【错误输出】")
            print(result.stderr)

    else:
        dims = get_dimensions(category)
        values = input_dimensions(category, dims)

        if operation == "suggest":
            target, _ = choose_target()
            run_bea(category, operation, values, target=target)
        elif operation == "sensitivity":
            target, target_wt = choose_target()
            run_bea(category, operation, values, target_wt=target_wt)
        else:
            run_bea(category, operation, values)

    print()
    print("=" * 56)
    print("  分析完成！")
    print("  更多用法见 QUICKSTART.md 或 README.md")
    print("=" * 56)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消")
        sys.exit(0)
