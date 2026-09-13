#!/usr/bin/env python3
"""CI：范式区间一致性检查（防 P0 回归）。

检查项：
1. wt_calc.py 与 MCP server.py 的 PARADIGM_RANGES 完全一致
2. 文档中不再出现旧的中心点表述（"0.1 治愈"、"0.2 亲和"等）
3. paradigms.md 不再出现旧表述"四大范式"或"四选一"
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERRORS = []


def extract_ranges(path):
    """从 Python 文件中提取 PARADIGM_RANGES 列表。"""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"PARADIGM_RANGES\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not m:
        return None
    # 提取所有 (数字, "名称") 元组
    pairs = re.findall(r'\(([\d.]+|float\("inf"\)),\s*"([^"]+)"', m.group(1))
    return pairs


def check_code_consistency():
    """检查 wt_calc.py 与 MCP server.py 的 PARADIGM_RANGES 一致。"""
    wt_path = os.path.join(REPO, "bipolar-emotion-aesthetics", "scripts", "wt_calc.py")
    mcp_path = os.path.join(REPO, "mcp-server", "bea_mcp", "server.py")
    wt_ranges = extract_ranges(wt_path)
    mcp_ranges = extract_ranges(mcp_path)
    if wt_ranges is None:
        ERRORS.append(f"无法从 {wt_path} 提取 PARADIGM_RANGES")
        return
    if mcp_ranges is None:
        ERRORS.append(f"无法从 {mcp_path} 提取 PARADIGM_RANGES")
        return
    if wt_ranges != mcp_ranges:
        ERRORS.append(f"PARADIGM_RANGES 不一致：\n  wt_calc.py: {wt_ranges}\n  server.py: {mcp_ranges}")
    else:
        print(f"✓ wt_calc.py 与 MCP server.py 的 PARADIGM_RANGES 一致（{len(wt_ranges)} 个区间）")


def check_old_center_point_notation():
    """检查文档中不再出现旧的中心点表述。"""
    old_patterns = [
        (r"0\.1\s*治愈", "0.1 治愈（旧中心点表述）"),
        (r"0\.2\s*亲和", "0.2 亲和（旧中心点表述）"),
        (r"0\.4\s*均衡", "0.4 均衡（旧中心点表述）"),
        (r"0\.55\s*崇高", "0.55 崇高（旧中心点表述）"),
        (r"0\.62\s*冷峻", "0.62 冷峻（旧中心点表述）"),
        (r"0\.7\s*先锋", "0.7 先锋（旧中心点表述）"),
    ]
    doc_files = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in files:
            if f.endswith((".md", ".html", ".py")):
                doc_files.append(os.path.join(root, f))

    found = False
    for filepath in doc_files:
        rel = os.path.relpath(filepath, REPO)
        # 跳过更新日志/历史记录
        if "更新日志" in rel or "CHANGELOG" in rel:
            continue
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        for pattern, desc in old_patterns:
            if re.search(pattern, content):
                # 允许在 method.md 中出现"传统锚点表述（0.1/0.2/...）为近似参考值"的说明
                if "传统锚点表述" in content and "近似参考值" in content:
                    continue
                ERRORS.append(f"{rel}: 发现旧表述「{desc}」，应改为区间表述")
                found = True
    if not found:
        print("✓ 文档中无旧的中心点表述")


def check_paradigms_old_notation():
    """检查 paradigms.md 不再出现旧表述。"""
    path = os.path.join(REPO, "bipolar-emotion-aesthetics", "references", "paradigms.md")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if "四大范式" in content and "四大核心范式与两种过渡范式" not in content:
        ERRORS.append("paradigms.md: 发现旧表述「四大范式」，应改为「四大核心范式与两种过渡范式」")
    elif "四选一" in content and "六选一" not in content:
        ERRORS.append("paradigms.md: 发现旧表述「四选一」，应改为「六选一」")
    else:
        print("✓ paradigms.md 无旧表述")


def main():
    print("=== 范式区间一致性检查 ===")
    check_code_consistency()
    check_old_center_point_notation()
    check_paradigms_old_notation()

    print()
    if ERRORS:
        print(f"❌ 发现 {len(ERRORS)} 个问题：")
        for e in ERRORS:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("✅ 全部检查通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
