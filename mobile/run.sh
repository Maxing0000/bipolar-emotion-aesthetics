#!/bin/bash
# BEA 移动端 MVP 启动脚本

cd "$(dirname "$0")/backend"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

# 安装依赖（首次运行）
if [ ! -d "venv" ]; then
    echo "首次运行，创建虚拟环境并安装依赖..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查配置
if [ ! -f "config.py" ]; then
    echo "错误: 未找到 config.py，请复制 config.example.py 为 config.py 并配置 API Key"
    exit 1
fi

# 启动
echo ""
echo "=========================================="
echo "  BEA 移动端 MVP 启动中..."
echo "=========================================="
echo ""
echo "访问地址: http://localhost:5000"
echo "停止服务: Ctrl+C"
echo ""

python app.py
