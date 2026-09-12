#!/usr/bin/env python3
"""CI：英文文件中英混杂检查。

英文面向文件（README_EN.md、GLOSSARY.md 的英文列除外项、arxiv/ 草稿）不得出现
中日韩统一表意文字。GLOSSARY.md 本身是双语对照表，跳过。
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_FILES = ["README_EN.md"]
EN_DIRS = ["arxiv"]
CJK = re.compile(r"[一-鿿]")


def targets():
    for rel in EN_FILES:
        p = os.path.join(REPO, rel)
        if os.path.exists(p):
            yield p
    for d in EN_DIRS:
        root = os.path.join(REPO, d)
        if not os.path.isdir(root):
            continue
        for r, _, files in os.walk(root):
            for f in files:
                if f.endswith((".md", ".html", ".tex")):
                    yield os.path.join(r, f)


def main():
    bad = []
    for path in targets():
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            if CJK.search(line):
                bad.append(f"{os.path.relpath(path, REPO)}:{i}: {line.strip()[:60]}")
    if bad:
        print("英文文件中发现中文残留：")
        for b in bad[:20]:
            print("  " + b)
        sys.exit(1)
    print("英文文件无中文残留 ✓")


if __name__ == "__main__":
    main()
