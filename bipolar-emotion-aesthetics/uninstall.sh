#!/usr/bin/env bash
# ==============================================================================
# BEA 技能包 - 卸载脚本
# ==============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SKILL_NAME="bipolar-emotion-aesthetics"

echo -e "${CYAN}▶ BEA 技能包卸载程序${NC}"
echo ""

# 检测技能目录
detect_dirs() {
    local dirs=()
    [[ -d "$HOME/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills" ]] && dirs+=("$HOME/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills")
    [[ -d "$HOME/.doubao/agent_mode/workspace/.user_skills" ]] && dirs+=("$HOME/.doubao/agent_mode/workspace/.user_skills")
    [[ -d "$HOME/.claude/skills" ]] && dirs+=("$HOME/.claude/skills")
    [[ -d "$HOME/.skills" ]] && dirs+=("$HOME/.skills")
    echo "${dirs[@]}"
}

dirs=($(detect_dirs))
found=()

for dir in "${dirs[@]}"; do
    if [[ -d "$dir/$SKILL_NAME" ]]; then
        found+=("$dir/$SKILL_NAME")
    fi
done

if [[ ${#found[@]} -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  未找到已安装的 BEA 技能包${NC}"
    exit 0
fi

echo "找到以下安装:"
for i in "${!found[@]}"; do
    echo -e "  ${GREEN}$((i+1)))${NC} ${found[$i]}"
done
echo ""

read -rp "确认卸载以上所有？(y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

for dir in "${found[@]}"; do
    rm -rf "$dir"
    echo -e "${GREEN}✅ 已卸载: $dir${NC}"
done

# 清理备份
for dir in "${dirs[@]}"; do
    for backup in "$dir/${SKILL_NAME}.backup."*; do
        if [[ -d "$backup" ]]; then
            rm -rf "$backup"
            echo -e "${YELLOW}🗑️  已清理备份: $backup${NC}"
        fi
    done
done

echo ""
echo -e "${GREEN}✅ 卸载完成${NC}"
