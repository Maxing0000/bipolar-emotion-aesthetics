# BEA 移动端 MVP 配置示例文件
# 复制此文件为 config.py 并填入实际值

import os

# ============ AI 模型配置 ============
# 豆包视觉 API（字节跳动火山引擎）
# 获取地址：https://www.volcengine.com/product/doubao
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "your-api-key-here")
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DOUBAO_MODEL_ID = os.environ.get("DOUBAO_MODEL_ID", "doubao-vision-pro-32k")

# 备用：OpenAI GPT-4V（如需使用）
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o"

# 使用哪个 AI 模型：doubao / openai
AI_PROVIDER = os.environ.get("AI_PROVIDER", "doubao")

# ============ 服务器配置 ============
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# ============ 文件配置 ============
UPLOAD_FOLDER = "data/uploads"
HISTORY_FOLDER = "data/history"
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# ============ BEA 分析配置 ============
ANALYSIS_TIMEOUT = 30
SAVE_HISTORY = True
DAILY_LIMIT = 0

# ============ 前端配置 ============
# 分析模拟模式（true=不调用真实AI，返回模拟数据，用于开发测试）
MOCK_MODE = os.environ.get("MOCK_MODE", "false").lower() == "true"
