#!/usr/bin/env python3
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

"""
BEA MCP Server 一键安装脚本

自动检测并配置支持 MCP 的 AI 客户端：
  - Claude Desktop（macOS / Windows）
  - WorkBuddy
  - Cursor
  - Cline（VS Code 插件）
  - Continue（VS Code 插件）

用法：
  python3 install.py              # 交互式安装
  python3 install.py --all       # 自动配置所有检测到的平台
  python3 install.py --claude    # 只配置 Claude Desktop
  python3 install.py --cursor    # 只配置 Cursor
  python3 install.py --status    # 查看当前配置状态
  python3 install.py --uninstall # 卸载所有配置

安装后重启对应的 AI 客户端即可使用 BEA 工具。
"""

import argparse
import json
import os
import platform
import sys
from pathlib import Path

_HERE = Path(__file__).parent.resolve()
_SERVER_PATH = _HERE / "server.py"
_PYTHON_PATH = sys.executable

CONFIG_TEMPLATE = {
    "mcpServers": {
        "bea": {
            "command": _PYTHON_PATH,
            "args": [str(_SERVER_PATH)],
        }
    }
}


def print_banner():
    print("=" * 60)
    print("  BEA MCP Server 一键安装工具 v2.8.0")
    print("  双极情绪美学 · 作者：马星 · CC BY-NC-SA 4.0")
    print("=" * 60)
    print()


def get_config_path(platform_name: str) -> Path | None:
    """获取各平台的 MCP 配置文件路径"""
    system = platform.system()
    home = Path.home()

    paths = {
        "claude": {
            "Darwin": home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
            "Windows": home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
            "Linux": home / ".config" / "Claude" / "claude_desktop_config.json",
        },
        "workbuddy": {
            "Darwin": home / ".workbuddy" / "mcp.json",
            "Windows": home / ".workbuddy" / "mcp.json",
            "Linux": home / ".workbuddy" / "mcp.json",
        },
        "cursor": {
            "Darwin": home / "Library" / "Application Support" / "Cursor" / "User" / "mcp.json",
            "Windows": home / "AppData" / "Roaming" / "Cursor" / "User" / "mcp.json",
            "Linux": home / ".config" / "Cursor" / "User" / "mcp.json",
        },
        "cline": {
            "Darwin": home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "mcp_settings.json",
            "Windows": home / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "mcp_settings.json",
            "Linux": home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "mcp_settings.json",
        },
        "continue": {
            "Darwin": home / ".continue" / "config.json",
            "Windows": home / ".continue" / "config.json",
            "Linux": home / ".continue" / "config.json",
        },
    }

    platform_paths = paths.get(platform_name, {})
    return platform_paths.get(system)


def detect_platforms() -> list[str]:
    """检测已安装的支持 MCP 的平台"""
    detected = []
    system = platform.system()
    home = Path.home()

    checks = {
        "claude": [
            home / "Library" / "Application Support" / "Claude",
            home / "AppData" / "Roaming" / "Claude",
            home / ".config" / "Claude",
        ],
        "workbuddy": [
            home / ".workbuddy",
        ],
        "cursor": [
            home / "Library" / "Application Support" / "Cursor",
            home / "AppData" / "Roaming" / "Cursor",
            home / ".config" / "Cursor",
        ],
        "cline": [
            home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev",
            home / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev",
        ],
        "continue": [
            home / ".continue",
        ],
    }

    for name, paths in checks.items():
        for p in paths:
            if p.exists():
                detected.append(name)
                break

    return detected


def install_platform(platform_name: str) -> bool:
    """安装配置到指定平台"""
    config_path = get_config_path(platform_name)
    if config_path is None:
        print(f"  ❌ 不支持的操作系统：{platform.system()}")
        return False

    print(f"  📍 配置文件：{config_path}")

    # 确保目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # 读取现有配置
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"  ⚠️  配置文件解析失败，将备份并重建：{e}")
            backup_path = config_path.with_suffix(".bak")
            config_path.rename(backup_path)
            print(f"  💾 已备份到：{backup_path}")
            config = {}

    # 合并配置
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    config["mcpServers"]["bea"] = {
        "command": _PYTHON_PATH,
        "args": [str(_SERVER_PATH)],
    }

    # 写入配置
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"  ✅ 配置成功！")
        return True
    except Exception as e:
        print(f"  ❌ 写入配置失败：{e}")
        return False


def uninstall_platform(platform_name: str) -> bool:
    """从指定平台卸载配置"""
    config_path = get_config_path(platform_name)
    if config_path is None or not config_path.exists():
        print(f"  ⚠️  配置文件不存在，跳过")
        return True

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        if "mcpServers" in config and "bea" in config["mcpServers"]:
            del config["mcpServers"]["bea"]
            if not config["mcpServers"]:
                del config["mcpServers"]

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"  ✅ 已卸载")
        else:
            print(f"  ⚠️  未找到 BEA 配置")
        return True
    except Exception as e:
        print(f"  ❌ 卸载失败：{e}")
        return False


def check_status():
    """检查各平台的配置状态"""
    print("📊 当前配置状态：")
    print()

    platforms = ["claude", "workbuddy", "cursor", "cline", "continue"]
    platform_names = {
        "claude": "Claude Desktop",
        "workbuddy": "WorkBuddy",
        "cursor": "Cursor",
        "cline": "Cline (VS Code)",
        "continue": "Continue (VS Code)",
    }

    for p in platforms:
        config_path = get_config_path(p)
        if config_path is None:
            status = "❌ 不支持的系统"
        elif not config_path.exists():
            status = "⚪ 未安装"
        else:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                if "mcpServers" in config and "bea" in config["mcpServers"]:
                    status = "✅ 已配置"
                else:
                    status = "⚪ 未配置 BEA"
            except Exception:
                status = "❌ 配置文件损坏"

        print(f"  {platform_names[p]:<20} {status}")

    print()
    print(f"🐍 Python 路径：{_PYTHON_PATH}")
    print(f"📁 服务器路径：{_SERVER_PATH}")
    print()


def interactive_install():
    """交互式安装"""
    detected = detect_platforms()

    if not detected:
        print("⚠️  未检测到支持 MCP 的 AI 客户端。")
        print()
        print("支持的平台：")
        print("  - Claude Desktop")
        print("  - WorkBuddy")
        print("  - Cursor")
        print("  - Cline (VS Code 插件)")
        print("  - Continue (VS Code 插件)")
        print()
        print("请先安装上述任一客户端，然后重新运行此脚本。")
        return

    print(f"✅ 检测到 {len(detected)} 个支持 MCP 的平台：")
    for i, p in enumerate(detected, 1):
        names = {
            "claude": "Claude Desktop",
            "workbuddy": "WorkBuddy",
            "cursor": "Cursor",
            "cline": "Cline",
            "continue": "Continue",
        }
        print(f"  {i}. {names.get(p, p)}")

    print()
    print("选择安装方式：")
    print("  1. 全部安装（推荐）")
    print("  2. 选择指定平台")
    print("  3. 取消")

    choice = input("请输入选项 (1/2/3): ").strip()

    if choice == "1":
        targets = detected
    elif choice == "2":
        print()
        print("输入要安装的平台编号（多个用逗号分隔，如 1,3）：")
        selected = input("请输入: ").strip()
        try:
            indices = [int(x.strip()) - 1 for x in selected.split(",")]
            targets = [detected[i] for i in indices if 0 <= i < len(detected)]
        except (ValueError, IndexError):
            print("❌ 输入无效，取消安装")
            return
    else:
        print("已取消")
        return

    if not targets:
        print("❌ 未选择任何平台")
        return

    print()
    print("🚀 开始安装...")
    print()

    success = 0
    for p in targets:
        names = {
            "claude": "Claude Desktop",
            "workbuddy": "WorkBuddy",
            "cursor": "Cursor",
            "cline": "Cline",
            "continue": "Continue",
        }
        print(f"📦 正在配置 {names.get(p, p)}...")
        if install_platform(p):
            success += 1
        print()

    print("=" * 60)
    print(f"✅ 安装完成！成功配置 {success}/{len(targets)} 个平台")
    print()
    print("⚠️  重要：请重启对应的 AI 客户端以加载 BEA MCP 服务器")
    print()
    print("📖 使用方法：")
    print("  在 AI 对话中说：'用 BEA 分析这个设计'")
    print("  或直接调用工具：bea_analyze, bea_compare, bea_dimensions 等")
    print()
    print("🔧 查看状态：python3 install.py --status")
    print("🗑️  卸载：python3 install.py --uninstall")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="BEA MCP Server 一键安装工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 install.py              # 交互式安装
  python3 install.py --all       # 自动配置所有检测到的平台
  python3 install.py --claude    # 只配置 Claude Desktop
  python3 install.py --cursor    # 只配置 Cursor
  python3 install.py --status    # 查看当前配置状态
  python3 install.py --uninstall # 卸载所有配置
        """,
    )

    parser.add_argument("--all", action="store_true", help="自动配置所有检测到的平台")
    parser.add_argument("--claude", action="store_true", help="只配置 Claude Desktop")
    parser.add_argument("--workbuddy", action="store_true", help="只配置 WorkBuddy")
    parser.add_argument("--cursor", action="store_true", help="只配置 Cursor")
    parser.add_argument("--cline", action="store_true", help="只配置 Cline")
    parser.add_argument("--continue", dest="continue_", action="store_true", help="只配置 Continue")
    parser.add_argument("--status", action="store_true", help="查看当前配置状态")
    parser.add_argument("--uninstall", action="store_true", help="卸载所有配置")

    args = parser.parse_args()

    print_banner()

    if args.status:
        check_status()
        return

    if args.uninstall:
        print("🗑️  开始卸载...")
        print()
        platforms = ["claude", "workbuddy", "cursor", "cline", "continue"]
        for p in platforms:
            names = {
                "claude": "Claude Desktop",
                "workbuddy": "WorkBuddy",
                "cursor": "Cursor",
                "cline": "Cline",
                "continue": "Continue",
            }
            print(f"🗑️  正在卸载 {names.get(p, p)}...")
            uninstall_platform(p)
            print()
        print("✅ 卸载完成！请重启 AI 客户端。")
        return

    targets = []
    if args.all:
        targets = detect_platforms()
        if not targets:
            print("❌ 未检测到支持 MCP 的 AI 客户端。")
            return
    elif args.claude:
        targets = ["claude"]
    elif args.workbuddy:
        targets = ["workbuddy"]
    elif args.cursor:
        targets = ["cursor"]
    elif args.cline:
        targets = ["cline"]
    elif args.continue_:
        targets = ["continue"]

    if targets:
        print(f"🚀 开始安装 {len(targets)} 个平台...")
        print()
        success = 0
        for p in targets:
            names = {
                "claude": "Claude Desktop",
                "workbuddy": "WorkBuddy",
                "cursor": "Cursor",
                "cline": "Cline",
                "continue": "Continue",
            }
            print(f"📦 正在配置 {names.get(p, p)}...")
            if install_platform(p):
                success += 1
            print()
        print(f"✅ 安装完成！成功配置 {success}/{len(targets)} 个平台")
        print("⚠️  请重启对应的 AI 客户端以加载 BEA MCP 服务器")
    else:
        interactive_install()


if __name__ == "__main__":
    main()