#!/usr/bin/env bash
# ==============================================================================
# BEA 双极情绪美学技能包 - 一键安装脚本 (macOS / Linux)
# ==============================================================================
# 用法:
#   ./install.sh              # 自动检测并安装到默认技能目录
#   ./install.sh --path DIR  # 安装到指定目录
#   ./install.sh --force      # 强制覆盖已有安装
#   ./install.sh --check      # 仅检查环境，不安装
#   ./install.sh --help       # 显示帮助
# ==============================================================================

set -euo pipefail

# ============================== 颜色定义 ======================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ============================== 配置变量 ======================================
SKILL_NAME="bipolar-emotion-aesthetics"
SKILL_VERSION="2.0.0"
SKILL_DISPLAY_NAME="BEA 双极情绪美学"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_PATH=""
FORCE=false
CHECK_ONLY=false
BACKUP_DIR=""

# ============================== 工具函数 ======================================
print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           BEA 双极情绪美学技能包 v${SKILL_VERSION} 安装程序              ║"
    echo "║           Bipolar Emotion Aesthetics Skill Pack               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${CYAN}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# ============================== 参数解析 ======================================
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --path)
                INSTALL_PATH="$2"
                shift 2
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --check)
                CHECK_ONLY=true
                shift
                ;;
            --help|-h)
                print_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                print_help
                exit 1
                ;;
        esac
    done
}

print_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --path DIR    安装到指定目录（默认自动检测）"
    echo "  --force       强制覆盖已有安装"
    echo "  --check       仅检查环境，不安装"
    echo "  --help, -h    显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 自动检测并安装"
    echo "  $0 --path ~/skills    # 安装到指定目录"
    echo "  $0 --force             # 强制覆盖安装"
}

# ============================== 环境检测 ======================================
detect_os() {
    local os
    case "$(uname -s)" in
        Darwin) os="macOS" ;;
        Linux)  os="Linux" ;;
        *)      os="Unknown" ;;
    esac
    echo "$os"
}

check_python() {
    if command -v python3 &>/dev/null; then
        local version
        version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python 已安装: $version"
        return 0
    else
        print_warning "Python3 未安装，脚本功能将受限（仅文档可用）"
        return 1
    fi
}

detect_skill_dirs() {
    local dirs=()

    # 豆包 (Doubao) - macOS
    if [[ -d "$HOME/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills" ]]; then
        dirs+=("$HOME/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills")
    fi

    # 豆包 (Doubao) - Linux
    if [[ -d "$HOME/.doubao/agent_mode/workspace/.user_skills" ]]; then
        dirs+=("$HOME/.doubao/agent_mode/workspace/.user_skills")
    fi

    # Claude Desktop
    if [[ -d "$HOME/.claude/skills" ]]; then
        dirs+=("$HOME/.claude/skills")
    fi

    # 通用用户技能目录
    if [[ -d "$HOME/.skills" ]]; then
        dirs+=("$HOME/.skills")
    fi

    # 当前目录下的 skills
    if [[ -d "$SCRIPT_DIR/../skills" ]]; then
        dirs+=("$(cd "$SCRIPT_DIR/../skills" && pwd)")
    fi

    echo "${dirs[@]}"
}

select_install_dir() {
    if [[ -n "$INSTALL_PATH" ]]; then
        # 用户指定了路径
        if [[ ! -d "$INSTALL_PATH" ]]; then
            print_warning "目录不存在，尝试创建: $INSTALL_PATH"
            mkdir -p "$INSTALL_PATH" || {
                print_error "无法创建目录: $INSTALL_PATH"
                exit 1
            }
        fi
        echo "$INSTALL_PATH"
        return
    fi

    # 自动检测
    local dirs
    dirs=($(detect_skill_dirs))

    if [[ ${#dirs[@]} -eq 0 ]]; then
        # 没有检测到，使用默认路径
        local default_dir="$HOME/.skills"
        print_warning "未检测到已安装的AI技能目录"
        print_info "将使用默认目录: $default_dir"
        mkdir -p "$default_dir"
        echo "$default_dir"
        return
    fi

    if [[ ${#dirs[@]} -eq 1 ]]; then
        # 只有一个，直接使用
        print_info "检测到技能目录: ${dirs[0]}"
        echo "${dirs[0]}"
        return
    fi

    # 多个，让用户选择
    echo ""
    echo -e "${BOLD}检测到多个技能目录，请选择安装位置:${NC}"
    for i in "${!dirs[@]}"; do
        echo -e "  ${GREEN}$((i+1)))${NC} ${dirs[$i]}"
    done
    echo -e "  ${YELLOW}0)${NC} 自定义路径"
    echo ""

    local choice
    read -rp "请输入序号 [1-${#dirs[@]}]: " choice

    if [[ "$choice" == "0" ]]; then
        read -rp "请输入自定义路径: " custom_path
        mkdir -p "$custom_path"
        echo "$custom_path"
    elif [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le ${#dirs[@]} ]]; then
        echo "${dirs[$((choice-1))]}"
    else
        print_error "无效选择"
        exit 1
    fi
}

# ============================== 备份与安装 ====================================
backup_existing() {
    local target_dir="$1"
    local skill_dir="$target_dir/$SKILL_NAME"

    if [[ -d "$skill_dir" ]]; then
        if [[ "$FORCE" == false ]]; then
            print_warning "检测到已有安装: $skill_dir"
            read -rp "是否覆盖？(y/N): " confirm
            if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
                print_info "安装已取消"
                exit 0
            fi
        fi

        # 备份
        BACKUP_DIR="$target_dir/${SKILL_NAME}.backup.$(date +%Y%m%d%H%M%S)"
        print_step "备份已有版本到: $BACKUP_DIR"
        cp -R "$skill_dir" "$BACKUP_DIR"
        print_success "备份完成"
    fi
}

install_files() {
    local target_dir="$1"
    local skill_dir="$target_dir/$SKILL_NAME"

    print_step "正在安装到: $skill_dir"

    # 创建目录
    mkdir -p "$skill_dir"

    # 复制核心文件
    cp "$SCRIPT_DIR/SKILL.md" "$skill_dir/" 2>/dev/null || true
    cp "$SCRIPT_DIR/README.md" "$skill_dir/" 2>/dev/null || true

    # 复制子目录
    for subdir in references scripts templates examples; do
        if [[ -d "$SCRIPT_DIR/$subdir" ]]; then
            rm -rf "$skill_dir/$subdir"
            cp -R "$SCRIPT_DIR/$subdir" "$skill_dir/"
        fi
    done

    # 设置脚本可执行权限
    if [[ -d "$skill_dir/scripts" ]]; then
        chmod +x "$skill_dir/scripts/"*.py 2>/dev/null || true
    fi

    print_success "文件复制完成"
}

# ============================== 验证安装 ======================================
verify_installation() {
    local skill_dir="$1"
    local errors=0

    print_step "验证安装..."

    # 检查核心文件
    local required_files=("SKILL.md" "references/theory.md" "references/paradigms.md" "references/method.md" "references/playbooks.md" "scripts/wt_calc.py" "scripts/bea_quant.py")

    for file in "${required_files[@]}"; do
        if [[ -f "$skill_dir/$file" ]]; then
            print_success "  ✓ $file"
        else
            print_error "  ✗ $file 缺失"
            errors=$((errors + 1))
        fi
    done

    # 验证 Python 脚本语法
    if command -v python3 &>/dev/null; then
        for py in "$skill_dir/scripts/"*.py; do
            if [[ -f "$py" ]]; then
                if python3 -m py_compile "$py" 2>/dev/null; then
                    print_success "  ✓ $(basename "$py") 语法正确"
                else
                    print_error "  ✗ $(basename "$py") 语法错误"
                    errors=$((errors + 1))
                fi
            fi
        done
    fi

    # 验证 SKILL.md 格式
    if [[ -f "$skill_dir/SKILL.md" ]]; then
        if head -5 "$skill_dir/SKILL.md" | grep -q "^name:"; then
            print_success "  ✓ SKILL.md 格式正确"
        else
            print_warning "  ⚠ SKILL.md 可能缺少 name 字段"
        fi
    fi

    if [[ $errors -eq 0 ]]; then
        print_success "安装验证通过！"
        return 0
    else
        print_error "安装验证失败，发现 $errors 个问题"
        return 1
    fi
}

# ============================== 安装后提示 ====================================
print_post_install() {
    local skill_dir="$1"

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  ${BOLD}🎉 安装成功！${NC}                                                 ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}📦 安装信息${NC}"
    echo "  技能名称: $SKILL_DISPLAY_NAME"
    echo "  版本: v$SKILL_VERSION"
    echo "  安装路径: $skill_dir"
    if [[ -n "$BACKUP_DIR" ]]; then
        echo "  旧版本备份: $BACKUP_DIR"
    fi
    echo ""

    echo -e "${BOLD}🚀 快速开始${NC}"
    echo "  1. 重启你的 AI 客户端（豆包/Claude等），技能将自动加载"
    echo "  2. 向 AI 提问，例如:"
    echo -e "     - ${CYAN}\"帮我分析一下 iPhone 17 Pro 的设计\"${NC}"
    echo -e "     - ${CYAN}\"这个海报哪里不好看？怎么改？\"${NC}"
    echo -e "     - ${CYAN}\"帮我设计一个艺术展览的海报\"${NC}"
    echo -e "     - ${CYAN}\"上传一张图片，分析它的美感\"${NC}"
    echo ""

    echo -e "${BOLD}🛠️  命令行工具${NC}"
    echo "  # 计算 W(T)"
    echo "  python3 $skill_dir/scripts/wt_calc.py --category phone --t \"形状=4,质感=3,色彩=2\""
    echo ""
    echo "  # 完整量化分析"
    echo "  python3 $skill_dir/scripts/bea_quant.py --category car --t \"形体=3,特征线=5,灯组=6\""
    echo ""
    echo "  # 交互模式图片分析"
    echo "  python3 $skill_dir/scripts/analyze_image.py --interactive"
    echo ""

    echo -e "${BOLD}📚 更多信息${NC}"
    echo "  理论文档: $skill_dir/references/"
    echo "  输出模板: $skill_dir/templates/"
    echo "  完整示例: $skill_dir/examples/"
    echo "  开源地址: https://github.com/Maxing0000/bipolar-emotion-aesthetics"
    echo ""

    echo -e "${YELLOW}💡 提示: 如果技能没有自动加载，请检查 AI 客户端的技能目录配置，${NC}"
    echo -e "${YELLOW}   或手动将 $skill_dir 目录添加到技能搜索路径中。${NC}"
    echo ""
}

# ============================== 主流程 ========================================
main() {
    print_banner
    parse_args "$@"

    # 环境检测
    print_step "环境检测"
    local os
    os=$(detect_os)
    print_info "操作系统: $os"
    check_python || true

    if [[ "$CHECK_ONLY" == true ]]; then
        print_info "仅检查模式，不执行安装"
        echo ""
        print_step "检测到的技能目录:"
        local dirs
        dirs=($(detect_skill_dirs))
        if [[ ${#dirs[@]} -eq 0 ]]; then
            print_warning "未检测到已安装的AI技能目录"
        else
            for d in "${dirs[@]}"; do
                print_success "  - $d"
            done
        fi
        exit 0
    fi

    # 选择安装目录
    echo ""
    local target_dir
    target_dir=$(select_install_dir)

    if [[ -z "$target_dir" ]]; then
        print_error "无法确定安装目录"
        exit 1
    fi

    # 备份已有版本
    echo ""
    backup_existing "$target_dir"

    # 安装文件
    echo ""
    install_files "$target_dir"

    # 验证安装
    echo ""
    local skill_dir="$target_dir/$SKILL_NAME"
    if verify_installation "$skill_dir"; then
        print_post_install "$skill_dir"
        exit 0
    else
        print_error "安装验证失败"
        if [[ -n "$BACKUP_DIR" ]]; then
            print_warning "你可以从备份恢复: $BACKUP_DIR"
        fi
        exit 1
    fi
}

main "$@"
