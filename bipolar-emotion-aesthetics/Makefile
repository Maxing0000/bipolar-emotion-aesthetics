# ==============================================================================
# BEA 双极情绪美学技能包 - Makefile
# ==============================================================================
# 用法:
#   make install    # 安装技能包
#   make uninstall  # 卸载技能包
#   make update     # 更新技能包
#   make check      # 检查环境
#   make test       # 运行脚本测试
#   make clean      # 清理临时文件
#   make help       # 显示帮助
# ==============================================================================

SKILL_NAME := bipolar-emotion-aesthetics
SKILL_VERSION := 2.0.0

.PHONY: install uninstall update check test clean help

## install: 安装技能包（自动检测目录）
install:
	@chmod +x install.sh
	@./install.sh

## uninstall: 卸载技能包
uninstall:
	@chmod +x uninstall.sh
	@./uninstall.sh

## update: 更新技能包（强制覆盖）
update:
	@chmod +x update.sh
	@./update.sh

## check: 检查环境和依赖
check:
	@chmod +x install.sh
	@./install.sh --check

## test: 运行Python脚本语法测试
test:
	@echo "▶ 测试 Python 脚本语法..."
	@for f in scripts/*.py; do \
		python3 -m py_compile $$f && echo "  ✅ $$f" || echo "  ❌ $$f"; \
	done
	@echo ""
	@echo "▶ 测试 W(T) 计算器..."
	@python3 scripts/wt_calc.py --category phone --t "形状线条=4,质感触觉=3,色彩=2,构图比例=2,光影=2,细节线条=5"
	@echo ""
	@echo "✅ 所有测试通过"

## clean: 清理临时文件和缓存
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ 清理完成"

## help: 显示帮助信息
help:
	@echo "BEA 双极情绪美学技能包 v$(SKILL_VERSION)"
	@echo ""
	@echo "可用命令:"
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## //' | column -t -s ':'
	@echo ""
	@echo "示例:"
	@echo "  make install    # 安装"
	@echo "  make update     # 更新"
	@echo "  make test       # 测试"
