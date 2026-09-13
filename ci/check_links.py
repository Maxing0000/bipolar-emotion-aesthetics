#!/usr/bin/env python3
"""CI：本地链接与文件引用检查。

扫描仓库内所有 .md / .html 中的相对路径引用（Markdown 链接、代码块内的路径、
href/src），凡指向本仓库文件的都必须存在。幻影文件（引用了不存在的文件）一律 FAIL。
外部 http(s) 链接不在本检查范围。
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "node_modules"}
# Markdown 链接与图片、HTML href/src、行内代码中的仓库相对路径
PATTERNS = [
    re.compile(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)"),
    re.compile(r'(?:href|src)="(?!https?://|#|//|data:)([^"]+)"'),
]
CODE_PATH = re.compile(r"`((?:docs|references|templates|cases|scripts|bipolar-emotion-aesthetics|ci|tests|arxiv)/[^`\s]+)`")


def iter_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith((".md", ".html")):
                yield os.path.join(root, f)


def clean(ref: str) -> str:
    return ref.split("#")[0].split("?")[0].strip()


def main():
    bad = []
    for path in iter_files():
        text = open(path, encoding="utf-8").read()
        # 更新日志中的旧文件名属于历史叙述，不参与引用检查
        text = re.split(r"^## 更新日志|^## Changelog", text, flags=re.M)[0]
        refs = []
        for pat in PATTERNS:
            refs += pat.findall(text)
        refs += CODE_PATH.findall(text)
        for ref in refs:
            ref = clean(ref)
            if not ref or ref.startswith(("mailto:", "tel:")):
                continue
            if "${" in ref or "{{" in ref:
                continue  # JS 模板占位符，非真实路径
            target = ref if os.path.isabs(ref) else os.path.normpath(os.path.join(os.path.dirname(path), ref))
            # 仓库根相对路径（如 docs/x.md 写在 README 里）也接受
            alt = os.path.normpath(os.path.join(REPO, ref))
            if not (os.path.exists(target) or os.path.exists(alt)):
                bad.append(f"{os.path.relpath(path, REPO)} -> {ref}")
    if bad:
        print("发现失效引用：")
        for b in sorted(bad):
            print("  " + b)
        sys.exit(1)
    print("全部本地引用有效 ✓")


if __name__ == "__main__":
    main()
