#!/usr/bin/env python3
"""BEA 技能打包工具——导出各平台适配格式。

用法：
  python3 package.py --all              # 打包所有平台
  python3 package.py --platform coze    # 只打包 Coze
  python3 package.py --platform chatgpt # 只打包 ChatGPT
  python3 package.py --output dist/     # 指定输出目录

输出：
  dist/bea-v2.5.0-core.zip          # 核心包（SKILL.md + scripts + references）
  dist/bea-v2.5.0-full.zip          # 完整包（含 docs、platforms、templates）
  dist/bea-coze-v2.5.0.zip          # Coze 适配包
  dist/bea-chatgpt-v2.5.0.zip       # ChatGPT 适配包
  dist/bea-claude-v2.5.0.zip        # Claude 适配包
  dist/bea-tongyi-v2.5.0.zip        # 通义千问适配包
  dist/bea-dify-v2.5.0.zip          # Dify 适配包
  dist/system-prompt.txt             # 通用 System Prompt（纯文本）
"""
import argparse
import os
import shutil
import zipfile
from pathlib import Path

VERSION = "2.6.0"
ROOT = Path(__file__).parent.parent  # scripts/ 的上一级是项目根目录

# 核心包文件（所有平台共用）
CORE_FILES = [
    "SKILL.md",
    "manifest.json",
    "LICENSE",
    "QUICKSTART.md",
    "scripts/bea_quant.py",
    "scripts/bea_guide.py",
    "references/01-core-theory.md",
    "references/02-workflow.md",
    "references/03-dimension-guide.md",
    "references/04-checklist.md",
    "references/05-case-studies.md",
    "templates/review-record.md",
    "templates/output-templates.md",
]

# 完整包额外文件
FULL_EXTRA = [
    "README.md",
    "FAQ.md",
    "CHANGELOG.md",
    "install.sh",
    "install.ps1",
    "uninstall.sh",
    "update.sh",
    "docs/index.html",
    "platforms/",
]

# 各平台适配文件
PLATFORM_FILES = {
    "coze": ["platforms/coze/README.md", "platforms/universal-system-prompt.md"],
    "chatgpt": ["platforms/chatgpt/README.md", "platforms/universal-system-prompt.md"],
    "claude": ["platforms/claude/README.md", "platforms/universal-system-prompt.md"],
    "tongyi": ["platforms/tongyi/README.md", "platforms/universal-system-prompt.md"],
    "dify": ["platforms/dify/README.md", "platforms/universal-system-prompt.md"],
}


def zip_files(file_list, output_path, base_dir=None):
    """将文件列表打包成 zip"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in file_list:
            f_path = ROOT / f
            if f_path.is_dir():
                # 目录：递归添加
                for root, dirs, files in os.walk(f_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(ROOT)
                        zf.write(file_path, arcname)
            elif f_path.exists():
                arcname = f_path.relative_to(ROOT) if base_dir is None else f_path.relative_to(base_dir)
                zf.write(f_path, arcname)
            else:
                print(f"  ⚠ 跳过不存在的文件: {f}")

    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"  ✓ {output_path.name} ({size_mb:.2f} MB)")


def extract_system_prompt(output_path):
    """从 universal-system-prompt.md 提取纯文本 System Prompt"""
    src = ROOT / "platforms/universal-system-prompt.md"
    content = src.read_text(encoding="utf-8")

    # 提取 ``` 之间的内容
    start = content.find("```")
    if start != -1:
        start = content.find("\n", start) + 1
        end = content.find("```", start)
        if end != -1:
            prompt = content[start:end].strip()
            Path(output_path).write_text(prompt, encoding="utf-8")
            print(f"  ✓ system-prompt.txt ({len(prompt)} 字符)")
            return

    # 如果没找到代码块，直接复制
    shutil.copy(src, output_path)
    print(f"  ✓ system-prompt.txt (直接复制)")


def main():
    parser = argparse.ArgumentParser(description="BEA 技能打包工具")
    parser.add_argument("--all", action="store_true", help="打包所有平台")
    parser.add_argument("--platform", type=str, choices=["coze", "chatgpt", "claude", "tongyi", "dify"],
                        help="只打包指定平台")
    parser.add_argument("--output", type=str, default="dist", help="输出目录")
    args = parser.parse_args()

    output_dir = ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 56)
    print(f"  BEA v{VERSION} 技能打包")
    print("=" * 56)
    print()

    # 核心包
    print("【核心包】")
    zip_files(CORE_FILES, output_dir / f"bea-v{VERSION}-core.zip")

    # 完整包
    print("\n【完整包】")
    zip_files(CORE_FILES + FULL_EXTRA, output_dir / f"bea-v{VERSION}-full.zip")

    # 通用 System Prompt
    print("\n【通用 System Prompt】")
    extract_system_prompt(output_dir / "system-prompt.txt")

    # 各平台适配包
    platforms_to_package = []
    if args.all:
        platforms_to_package = list(PLATFORM_FILES.keys())
    elif args.platform:
        platforms_to_package = [args.platform]

    if platforms_to_package:
        print(f"\n【平台适配包】")
        for platform in platforms_to_package:
            files = CORE_FILES + PLATFORM_FILES[platform]
            zip_files(files, output_dir / f"bea-{platform}-v{VERSION}.zip")

    print()
    print("=" * 56)
    print(f"  打包完成！输出目录: {output_dir}")
    print("=" * 56)
    print()
    print("使用说明：")
    print("  - core.zip：核心功能，适合熟悉 BEA 的用户")
    print("  - full.zip：完整包，含文档、官网、多平台适配")
    print("  - system-prompt.txt：通用 System Prompt，复制粘贴到任意 AI 平台")
    print("  - bea-{platform}.zip：指定平台的适配包")
    print()


if __name__ == "__main__":
    main()
