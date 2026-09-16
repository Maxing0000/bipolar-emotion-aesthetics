#!/usr/bin/env python3
"""案例库网页生成器：data/cases.json（单一数据源）→ docs/case-library.html

用法：
    python3 scripts/gen_case_library.py            # 从 JSON 重新生成网页数据段
    python3 scripts/gen_case_library.py --check    # 只校验网页数据与 JSON 是否一致

原则：案例数据只维护 data/cases.json 一份；网页内的 const cases 数组与本命令
输出属生成物，不要手改网页里的数据段（改动会在下次生成时被覆盖）。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "cases.json")
HTML_PATH = os.path.join(ROOT, "docs", "case-library.html")

START_MARK = "const cases = "
END_MARK = "\n        ];"


def load_cases():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def read_html():
    with open(HTML_PATH, encoding="utf-8") as f:
        return f.read()


def replace_block(html, cases):
    """替换 const cases = [...]; 数据段（含尾部分号）"""
    start = html.index(START_MARK)
    open_idx = html.index("[", start)
    end = html.index(END_MARK, open_idx)
    # indent=12 使元素缩进与原网页风格一致（元素 12 空格、字段 16 空格）；
    # 去掉 JSON 自带的顶层闭合括号，由 END_MARK 提供带缩进的 "];"
    body = json.dumps(cases, ensure_ascii=False, indent=12)
    inner = body[1:-1].rstrip("\n")
    block = START_MARK + "[\n" + inner + END_MARK + ";"
    return html[:start] + block + html[end + len(END_MARK) + 1:]


def replace_stat(html, total):
    """更新页头『案例总数』统计（写死的数字）"""
    old_stat = '<div class="stat-number" id="totalCases">'
    idx = html.index(old_stat)
    end = html.index("</div>", idx)
    return html[:idx] + old_stat + str(total) + html[end:]


def main():
    cases = load_cases()
    html = read_html()

    # 从现有网页提取数据段，判断是否需要更新
    try:
        start = html.index(START_MARK)
        open_idx = html.index("[", start)
        end = html.index(END_MARK, open_idx)
        current = json.loads(html[open_idx:end] + "]")
    except (ValueError, json.JSONDecodeError):
        current = None

    total = len(cases)
    new_html = replace_stat(replace_block(html, cases), total)

    if args_check():
        if current is not None and [c["id"] for c in current] == [c["id"] for c in cases] \
                and json.dumps(current, ensure_ascii=False, sort_keys=True) == \
                json.dumps(cases, ensure_ascii=False, sort_keys=True):
            print(f"✓ 网页数据与 data/cases.json 一致（{total} 个案例）")
            return
        print("✗ 网页数据与 data/cases.json 不一致，请运行：python3 scripts/gen_case_library.py")
        sys.exit(1)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
    ids = [c["id"] for c in cases]
    print(f"✓ 已生成：{total} 个案例（ids {ids[0]}–{ids[-1]}）→ docs/case-library.html")
    print(f"  页头统计「案例总数」已同步为 {total}")


def args_check():
    return "--check" in sys.argv


if __name__ == "__main__":
    main()
