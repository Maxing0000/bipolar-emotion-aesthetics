#!/usr/bin/env bash
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

# BEA v2.3.0 一键安装脚本（macOS / Linux）
#
# 用法：
#   从 GitHub 安装：  curl -fsSL https://raw.githubusercontent.com/Maxing0000/bipolar-emotion-aesthetics/main/install.sh | bash
#   从本地安装：     ./install.sh
#   指定安装目录：   SKILL_DIR=/path/to/skills ./install.sh

set -euo pipefail

SKILL_NAME="bipolar-emotion-aesthetics"
REPO_URL="https://github.com/Maxing0000/bipolar-emotion-aesthetics.git"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ── 检测 Skill 目录 ──────────────────────────────────
detect_skill_dir() {
    # 用户手动指定
    if [ -n "${SKILL_DIR:-}" ] && [ -d "$SKILL_DIR" ]; then
        echo "$SKILL_DIR"
        return 0
    fi

    # 常见位置（按优先级）
    local candidates=(
        "$HOME/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills"
        "$HOME/.doubao/agent_mode/workspace/.user_skills"
        "$HOME/.config/doubao/agent_mode/workspace/.user_skills"
        "$HOME/.doubao/workspace/.user_skills"
    )

    for dir in "${candidates[@]}"; do
        if [ -d "$dir" ]; then
            echo "$dir"
            return 0
        fi
    done
    return 1
}

# ── 检查 Python ──────────────────────────────────────
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON=python3
    elif command -v python >/dev/null 2>&1; then
        PYTHON=python
    else
        error "未找到 Python3，请先安装：https://www.python.org/downloads/"
        exit 1
    fi
    info "Python: $($PYTHON --version 2>&1)"
}

# ── 获取 skill 文件 ──────────────────────────────────
fetch_skill() {
    local dest="$1"

    # 如果当前目录有 SKILL.md，认为是本地安装
    if [ -f "SKILL.md" ] && [ -f "scripts/bea_quant.py" ]; then
        info "检测到本地 skill 文件，直接复制"
        mkdir -p "$dest"
        cp -R SKILL.md LICENSE scripts references templates "$dest/"
        return 0
    fi

    # 从 GitHub clone
    if ! command -v git >/dev/null 2>&1; then
        error "未找到 git，请先安装 git 或手动下载 zip 包"
        exit 1
    fi

    local tmp
    tmp=$(mktemp -d)
    info "从 GitHub 克隆..."
    git clone --depth 1 "$REPO_URL" "$tmp/repo" >/dev/null 2>&1

    mkdir -p "$dest"
    cp -R "$tmp/repo/SKILL.md" "$tmp/repo/LICENSE" "$tmp/repo/scripts" "$tmp/repo/references" "$tmp/repo/templates" "$dest/"
    rm -rf "$tmp"
}

# ── 主流程 ───────────────────────────────────────────
main() {
    echo "========================================"
    echo "  BEA v2.3.0 安装程序"
    echo "========================================"
    echo ""

    check_python

    local skill_dir
    if ! skill_dir=$(detect_skill_dir); then
        error "未检测到 Skill 目录。"
        echo ""
        echo "请手动指定目录："
        echo "  SKILL_DIR=/path/to/your/skills $0"
        echo ""
        echo "常见 Skill 目录位置："
        echo "  macOS:  ~/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills"
        echo "  Linux:  ~/.doubao/agent_mode/workspace/.user_skills"
        exit 1
    fi

    info "Skill 目录: $skill_dir"

    local dest="$skill_dir/$SKILL_NAME"

    # 已安装检测
    if [ -d "$dest" ]; then
        warn "已检测到旧版本: $dest"
        read -r -p "是否覆盖？(y/N) " answer
        case "$answer" in
            [yY]|[yY][eE][sS])
                rm -rf "$dest"
                ;;
            *)
                info "取消安装"
                exit 0
                ;;
        esac
    fi

    info "安装到: $dest"
    fetch_skill "$dest"

    # 验证
    echo ""
    info "运行自测试..."
    if (cd "$dest" && $PYTHON scripts/bea_quant.py test >/dev/null 2>&1); then
        info "自测试通过"
    else
        warn "自测试失败，请检查 Python 环境"
        (cd "$dest" && $PYTHON scripts/bea_quant.py test) || true
    fi

    echo ""
    echo "========================================"
    echo -e "  ${GREEN}✅ 安装成功！${NC}"
    echo "========================================"
    echo ""
    echo "  位置: $dest"
    echo ""
    echo "  快速开始："
    echo "    cd $dest"
    echo "    python3 scripts/bea_quant.py template --category phone"
    echo "    python3 scripts/bea_quant.py report --category phone --t \"形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6\""
    echo ""
}

main "$@"
