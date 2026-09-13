#!/usr/bin/env python3
"""
BEA 移动端 MVP - Flask 后端 API
提供图片上传、AI 分析、历史记录、分享卡片等接口
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from PIL import Image
import io

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from ai_analyzer import AIAnalyzer

# ============ Flask 应用初始化 ============
app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

# 确保目录存在
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.HISTORY_FOLDER, exist_ok=True)

# AI 分析器
analyzer = AIAnalyzer()


# ============ 工具函数 ============
def allowed_file(filename: str) -> bool:
    """检查文件扩展名"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS


def compress_image(image_path: str, max_size: int = 1024, quality: int = 85) -> str:
    """压缩图片"""
    try:
        img = Image.open(image_path)
        # 调整大小
        if img.width > max_size or img.height > max_size:
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 转换为 RGB（处理 PNG 透明通道）
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 保存为 JPEG
        output_path = image_path.rsplit(".", 1)[0] + "_compressed.jpg"
        img.save(output_path, "JPEG", quality=quality, optimize=True)
        return output_path
    except Exception as e:
        print(f"图片压缩失败: {e}")
        return image_path


def save_history(result: dict, image_filename: str) -> str:
    """保存分析历史"""
    if not config.SAVE_HISTORY:
        return ""

    history_id = str(uuid.uuid4())[:8]
    history_data = {
        "id": history_id,
        "timestamp": datetime.now().isoformat(),
        "image": image_filename,
        "result": result,
    }

    history_path = os.path.join(config.HISTORY_FOLDER, f"{history_id}.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    return history_id


# ============ API 路由 ============

@app.route("/")
def index():
    """首页"""
    return send_from_directory("../frontend", "index.html")


@app.route("/api/health")
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "mock_mode": config.MOCK_MODE,
        "ai_provider": config.AI_PROVIDER,
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """图片分析接口"""
    try:
        # 检查是否有文件
        if "image" not in request.files:
            return jsonify({"error": "未找到图片文件"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "未选择文件"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": f"不支持的文件格式，支持: {', '.join(config.ALLOWED_EXTENSIONS)}"}), 400

        # 保存文件
        file_id = str(uuid.uuid4())[:8]
        filename = f"{file_id}_{secure_filename(file.filename)}"
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        # 压缩图片
        compressed_path = compress_image(filepath)

        # AI 分析
        result = analyzer.analyze_image(compressed_path)

        # 添加图片信息
        result["image_id"] = file_id
        result["image_url"] = f"/uploads/{os.path.basename(compressed_path)}"

        # 保存历史
        history_id = save_history(result, filename)
        result["history_id"] = history_id

        return jsonify(result)

    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"分析失败: {str(e)}"}), 500


@app.route("/api/history")
def get_history():
    """获取分析历史列表"""
    try:
        history_files = sorted(
            [f for f in os.listdir(config.HISTORY_FOLDER) if f.endswith(".json")],
            reverse=True,
        )[:20]  # 最近20条

        history_list = []
        for hf in history_files:
            with open(os.path.join(config.HISTORY_FOLDER, hf), "r", encoding="utf-8") as f:
                data = json.load(f)
                history_list.append({
                    "id": data.get("id"),
                    "timestamp": data.get("timestamp"),
                    "paradigm": data.get("result", {}).get("paradigm", {}).get("name"),
                    "wt": data.get("result", {}).get("wt"),
                    "total_score": data.get("result", {}).get("total_score"),
                    "image_url": data.get("result", {}).get("image_url"),
                })

        return jsonify({"history": history_list, "count": len(history_list)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/<history_id>")
def get_history_detail(history_id):
    """获取单条历史详情"""
    try:
        history_path = os.path.join(config.HISTORY_FOLDER, f"{history_id}.json")
        if not os.path.exists(history_path):
            return jsonify({"error": "历史记录不存在"}), 404

        with open(history_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/share/<history_id>")
def get_share_card(history_id):
    """生成分享卡片（返回分享页面 URL）"""
    # 分享页面由前端渲染，这里只返回数据
    return get_history_detail(history_id)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """访问上传的图片"""
    return send_from_directory(config.UPLOAD_FOLDER, filename)


# ============ 错误处理 ============

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": f"文件过大，最大支持 {config.MAX_CONTENT_LENGTH // 1024 // 1024}MB"}), 413


@app.errorhandler(404)
def not_found(e):
    return send_from_directory("../frontend", "index.html")


# ============ 启动 ============

if __name__ == "__main__":
    print("=" * 50)
    print("BEA 移动端 MVP 启动中...")
    print(f"模式: {'模拟（MOCK）' if config.MOCK_MODE else '真实AI分析'}")
    print(f"AI 提供商: {config.AI_PROVIDER}")
    print(f"地址: http://{config.HOST}:{config.PORT}")
    print("=" * 50)

    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
