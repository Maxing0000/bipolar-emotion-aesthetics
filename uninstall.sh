#!/usr/bin/env bash
# BEA v2.2 卸载脚本（macOS / Linux）
set -euo pipefail

SKILL_NAME="bipolar-emotion-aesthetics"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

detect_skill_dir() {
    if [ -n "${SKILL_DIR:-}" ] && [ -d "$SKILL_DIR" ]; then
        echo "$SKILL_DIR"
        return 0
    fi
    local candidates=(
        "$HOME/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills"
        "$HOME/.doubao/agent_mode/workspace/.user_skills"
        "$HOME/.config/doubao/agent_mode/workspace/.user_skills"
    )
    for dir in "${candidates[@]}"; do
        if [ -d "$dir" ]; then
            echo "$dir"
            return 0
        fi
    done
    return 1
}

main() {
    echo "BEA v2.2 卸载程序"
    echo ""

    local skill_dir
    if ! skill_dir=$(detect_skill_dir); then
        echo -e "${RED}未检测到 Skill 目录${NC}"
        echo "请手动指定：SKILL_DIR=/path/to/skills $0"
        exit 1
    fi

    local dest="$skill_dir/$SKILL_NAME"

    if [ ! -d "$dest" ]; then
        echo -e "${YELLOW}未找到已安装的 BEA skill: $dest${NC}"
        exit 0
    fi

    echo "即将删除: $dest"
    read -r -p "确认卸载？(y/N) " answer
    case "$answer" in
        [yY]|[yY][eE][sS])
            rm -rf "$dest"
            echo -e "${GREEN}✅ 已卸载${NC}"
            ;;
        *)
            echo "取消"
            ;;
    esac
}

main "$@"
