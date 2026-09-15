#!/usr/bin/env python3
"""BEA 技能打包工具——导出各平台适配格式。

用法：
  python3 package.py --all              # 打包所有平台
  python3 package.py --platform coze    # 只打包 Coze
  python3 package.py --skillhub         # 生成 SkillHub 上传包（附平台规范校验）
  python3 package.py --check            # 只做预检，不生成 zip
  python3 package.py --output dist/     # 指定输出目录

输出：
  dist/bea-v{版本}-core.zip          # 核心包（SKILL.md + scripts + references）
  dist/bea-v{版本}-full.zip          # 完整包（含 docs、platforms、templates）
  dist/bea-v{版本}-skillhub.zip      # SkillHub 上传包（根目录直接含 SKILL.md，内容同 full）
  dist/bea-{平台}-v{版本}.zip        # 各平台适配包（coze/chatgpt/claude/tongyi/dify）
  dist/system-prompt.txt             # 通用 System Prompt（纯文本）

版本号统一从 manifest.json 读取，避免各处版本不一致。
"""
import argparse
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent  # scripts/ 的上一级是项目根目录


def load_version() -> str:
    """版本号单一来源：manifest.json（读不到时退回 SKILL.md frontmatter）"""
    manifest = ROOT / "manifest.json"
    if manifest.exists():
        try:
            return str(json.loads(manifest.read_text(encoding="utf-8"))["version"])
        except (ValueError, KeyError):
            pass
    skill = ROOT / "SKILL.md"
    if skill.exists():
        for line in skill.read_text(encoding="utf-8").splitlines():
            if line.startswith("version:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")
    print("⚠ 无法从 manifest.json / SKILL.md 读取版本号，回退到 0.0.0")
    return "0.0.0"


VERSION = load_version()

# 核心包文件（所有平台共用）
CORE_FILES = [
    "SKILL.md",
    "manifest.json",
    "LICENSE.md",
    "QUICKSTART.md",
    "scripts/bea_quant.py",
    "scripts/bea_guide.py",
    "references/01-core-theory.md",
    "references/02-workflow.md",
    "references/03-dimension-guide.md",
    "references/04-checklist.md",
    "references/05-case-studies.md",
    "references/06-image-anchors.md",
    "templates/review-record.md",
    "templates/output-templates.md",
]

# 完整包额外文件
# 注意：SkillHub 禁止上传二进制文件（png/jpg 等会被平台跳过并警告），
# 因此 assets/ 下的 logo 图标不进包——图标在网页端"编辑头像"处单独上传。
FULL_EXTRA = [
    "README.md",
    "FAQ.md",
    "CHANGELOG.md",
    "docs/index.html",
    "docs/case-library.html",
    "docs/image-analyzer.html",
    "platforms/",
]

# SkillHub 禁止的二进制扩展名（预检时命中即报错，防止再次混入包里）
BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tiff",
    ".svgz", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".mp3", ".wav", ".mp4", ".mov",
    ".ttf", ".otf", ".woff", ".woff2", ".eot", ".pyc", ".so", ".dylib",
    ".exe", ".bin", ".db", ".sqlite",
}

# 各平台适配文件
PLATFORM_FILES = {
    "coze": ["platforms/coze/README.md", "platforms/universal-system-prompt.md"],
    "chatgpt": ["platforms/chatgpt/README.md", "platforms/universal-system-prompt.md"],
    "claude": ["platforms/claude/README.md", "platforms/universal-system-prompt.md"],
    "tongyi": ["platforms/tongyi/README.md", "platforms/universal-system-prompt.md"],
    "dify": ["platforms/dify/README.md", "platforms/universal-system-prompt.md"],
}


def zip_files(file_list, output_path, base_dir=None, prefix=None):
    """将文件列表打包成 zip

    prefix: 若指定，包内所有文件都放到该目录下（SkillHub 本地上传要求解压后是技能目录）
    """
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
                        zf.write(file_path, Path(prefix) / arcname if prefix else arcname)
            elif f_path.exists():
                arcname = f_path.relative_to(ROOT) if base_dir is None else f_path.relative_to(base_dir)
                zf.write(f_path, Path(prefix) / arcname if prefix else arcname)
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


def preflight(file_list):
    """打包前预检：列出所有缺失文件与二进制文件，避免产出缺文件/含二进制的包"""
    missing = [f for f in file_list if not (ROOT / f).exists()]
    binaries = []
    for f in file_list:
        f_path = ROOT / f
        if not f_path.exists():
            continue
        if f_path.is_dir():
            for root, dirs, files in os.walk(f_path):
                for name in files:
                    if Path(name).suffix.lower() in BINARY_EXTS:
                        binaries.append(str(Path(root) / name).replace(str(ROOT) + "/", ""))
        elif f_path.suffix.lower() in BINARY_EXTS:
            binaries.append(f)
    return missing, binaries


def check_skillhub_spec():
    """SkillHub 平台规范校验（依据官方 release.md）

    阻断项：SKILL.md 必须含 slug / displayName / version
            slug 须为 kebab-case 且长度 2-128，version 须为合法 SemVer
    返回错误列表（空列表 = 通过）
    """
    skill = ROOT / "SKILL.md"
    if not skill.exists():
        return ["SKILL.md 不存在（SkillHub 要求上传包内必须包含 SKILL.md）"]

    text = skill.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return ["SKILL.md 缺少 YAML frontmatter"]
    fm = m.group(1)

    def field(key):
        hit = re.search(rf"^{key}:\s*(.+)$", fm, re.M)
        return hit.group(1).strip().strip('"').strip("'") if hit else None

    slug, version, display = field("slug"), field("version"), field("displayName")
    errors = []
    for key, val in (("slug", slug), ("displayName", display), ("version", version)):
        if not val:
            errors.append(f"frontmatter 缺少必填字段 {key}（SkillHub 会阻断发布）")
    if slug:
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
            errors.append(f"slug '{slug}' 不是合法 kebab-case（仅允许小写字母、数字、连字符）")
        if not 2 <= len(slug) <= 128:
            errors.append(f"slug 长度 {len(slug)} 超出 2-128")
    if version:
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            errors.append(f"version '{version}' 不是合法 SemVer（应形如 1.0.0）")
        elif version != VERSION:
            errors.append(f"SKILL.md version({version}) 与 manifest.json({VERSION}) 不一致")
    return errors


def main():
    parser = argparse.ArgumentParser(description="BEA 技能打包工具")
    parser.add_argument("--all", action="store_true", help="打包所有平台")
    parser.add_argument("--platform", type=str, choices=["coze", "chatgpt", "claude", "tongyi", "dify"],
                        help="只打包指定平台")
    parser.add_argument("--output", type=str, default="dist", help="输出目录")
    parser.add_argument("--check", action="store_true", help="只做预检，不生成 zip")
    parser.add_argument("--skillhub", action="store_true",
                        help="生成 SkillHub 上传包（根目录直接含 SKILL.md）并执行平台规范校验")
    args = parser.parse_args()

    output_dir = ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 56)
    print(f"  BEA v{VERSION} 技能打包")
    print("=" * 56)
    print()

    # 预检：确保清单里的文件真实存在，且不含 SkillHub 禁止的二进制文件
    all_needed = CORE_FILES + FULL_EXTRA
    for files in PLATFORM_FILES.values():
        all_needed += files
    missing, binaries = preflight(all_needed)
    print("【预检】")
    if missing:
        print(f"  ✗ 清单中有 {len(missing)} 个文件/目录不存在：")
        for f in missing:
            print(f"      - {f}")
        print("  请先补齐或在列表中将它们移除，再重新打包。")
        sys.exit(1)
    if binaries:
        print(f"  ✗ 清单中有 {len(binaries)} 个二进制文件（SkillHub 禁止上传，会被平台跳过并警告）：")
        for f in binaries:
            print(f"      - {f}")
        print("  请将它们从打包清单移除；图标类素材改在 SkillHub 网页端单独上传。")
        sys.exit(1)
    print(f"  ✓ {len(set(all_needed))} 个文件/目录全部存在，无二进制文件")
    print()

    # SkillHub 平台规范校验（上传前必查，--check 模式也会执行）
    if args.skillhub or args.all or args.check:
        print("【SkillHub 规范校验】")
        spec_errors = check_skillhub_spec()
        if spec_errors:
            print("  ✗ 不符合 SkillHub 上传要求：")
            for e in spec_errors:
                print(f"      - {e}")
            print("  请修正 SKILL.md 或 manifest.json 后重试。")
            sys.exit(1)
        print("  ✓ SKILL.md frontmatter 合规（slug / displayName / version 齐备）")
        print()

    if args.check:
        print("预检通过（--check 模式，未生成 zip）")
        return

    # 核心包
    print("【核心包】")
    zip_files(CORE_FILES, output_dir / f"bea-v{VERSION}-core.zip")

    # 完整包
    print("\n【完整包】")
    zip_files(CORE_FILES + FULL_EXTRA, output_dir / f"bea-v{VERSION}-full.zip")

    # 通用 System Prompt
    print("\n【通用 System Prompt】")
    extract_system_prompt(output_dir / "system-prompt.txt")

    # SkillHub 上传包（官方要求 ZIP 根目录直接包含 SKILL.md，故为平铺结构）
    if args.skillhub or args.all:
        print("\n【SkillHub 上传包】")
        zip_files(CORE_FILES + FULL_EXTRA, output_dir / f"bea-v{VERSION}-skillhub.zip")

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
    print("  - skillhub.zip：SkillHub 上传用（根目录直接含 SKILL.md，内容同 full）")
    print("  - system-prompt.txt：通用 System Prompt，复制粘贴到任意 AI 平台")
    print("  - bea-{platform}.zip：指定平台的适配包")
    print()


if __name__ == "__main__":
    main()
