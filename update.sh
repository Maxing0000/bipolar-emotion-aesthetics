#!/usr/bin/env bash
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

# BEA v2.2 更新脚本（macOS / Linux）
# 从 GitHub 拉取最新版本并覆盖安装
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "BEA v2.2 更新程序"
echo ""

# 如果本地有 install.sh，直接调用（支持覆盖）
if [ -f "$SCRIPT_DIR/install.sh" ]; then
    exec bash "$SCRIPT_DIR/install.sh"
fi

# 否则从 GitHub 获取最新安装脚本
echo "从 GitHub 获取最新安装脚本..."
curl -fsSL https://raw.githubusercontent.com/Maxing0000/bipolar-emotion-aesthetics/main/install.sh | bash
