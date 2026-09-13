# BEA 移动端 MVP

双极情绪美学（Bipolar Emotion Aesthetics）移动端应用 - 拍一张照片，30秒看懂为什么美。

## 功能特性

- 📸 **拍照分析**：拍摄或上传图片，AI 自动分析美学构成
- 🧠 **智能识别**：多模态大模型自动识别 6 维度视觉元素极性
- 📊 **完整报告**：W(T) 计算、范式定位、四象限、四维评分、病症诊断、优化处方
- 📈 **可视化图表**：四象限定位图、四维评分雷达图
- 📱 **移动端优先**：响应式设计，完美适配手机
- 💾 **历史记录**：本地保存分析历史，随时回看
- 🔗 **分享功能**：一键生成精美分享卡片

## 技术栈

- **前端**：纯 HTML + CSS + JavaScript + ECharts
- **后端**：Python Flask
- **AI 模型**：豆包视觉（Doubao Vision）/ GPT-4V
- **图片处理**：Pillow

## 快速开始

### 1. 安装依赖

```bash
cd mobile/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 API Key

复制配置文件并填入你的 API Key：

```bash
cp config.example.py config.py
```

编辑 `config.py`，填入豆包视觉 API Key：

```python
DOUBAO_API_KEY = "your-api-key-here"
DOUBAO_MODEL_ID = "doubao-vision-pro-32k"
```

> 获取 API Key：https://www.volcengine.com/product/doubao

### 3. 启动服务

```bash
# 方式一：使用启动脚本
cd mobile
chmod +x run.sh
./run.sh

# 方式二：手动启动
cd mobile/backend
source venv/bin/activate
python app.py
```

### 4. 访问应用

打开浏览器访问：http://localhost:5000

手机访问：确保手机和电脑在同一局域网，访问 `http://<电脑IP>:5000`

## 开发模式（模拟数据）

如果没有 API Key，可以使用模拟模式开发测试：

```bash
# 设置环境变量
export MOCK_MODE=true
python app.py
```

模拟模式下，分析接口会返回模拟数据，用于前端开发和 UI 调试。

## API 接口

### 图片分析

```
POST /api/analyze
Content-Type: multipart/form-data

参数：
- image: 图片文件（必填）

返回：
{
  "wt": 0.5,
  "paradigm": {"name": "崇高震撼", "emotion": "..."},
  "quadrant": {"tension": 0.5, "order": 0.5, "name": "黄金区"},
  "scores": {"tension": 22, "order": 20, "threshold": 23, "context": 20},
  "total_score": 85,
  "diagnoses": [...],
  "prescriptions": [...],
  "elements": {"positive": [...], "negative": [...]},
  "mood": "...",
  "image_url": "/uploads/xxx.jpg",
  "history_id": "abc123"
}
```

### 健康检查

```
GET /api/health
```

### 历史记录

```
GET /api/history          # 历史列表
GET /api/history/<id>     # 历史详情
```

## 项目结构

```
mobile/
├── frontend/              # 前端
│   ├── index.html        # 首页（拍照/上传）
│   ├── report.html       # 分析报告页
│   ├── css/
│   │   └── style.css     # 样式
│   └── js/
│       └── app.js        # 主逻辑
├── backend/               # 后端
│   ├── app.py            # Flask 应用
│   ├── bea_engine.py     # BEA 计算引擎
│   ├── ai_analyzer.py    # AI 图像分析
│   ├── config.py         # 配置文件
│   └── requirements.txt  # 依赖
├── data/                  # 数据目录
│   ├── uploads/          # 上传的图片
│   └── history/          # 分析历史
├── run.sh                 # 启动脚本
└── README.md              # 说明文档
```

## BEA 理论核心

- **美感 = 可控张力下的情绪奖赏**
- **亲极 P+**：圆润、柔色、光滑、舒缓、对称、留白、稳定
- **危极 T−**：尖锐、强对比、坚硬、突变、失衡、拥挤、冷峻
- **W(T) 危极权重**：0-1，衡量整体危极占比
- **8 大范式**：治愈松弛、亲和精致、诗意朦胧、均衡典雅、崇高震撼、冷峻克制、神秘魅惑、先锋反叛

## 部署

### 生产环境部署

推荐使用 Gunicorn + Nginx：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker 部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 许可证

CC BY 4.0 - 双极情绪美学理论由星空本空创立

## 联系方式

- 理论官网：https://maxing0000.github.io/bipolar-emotion-aesthetics/
- GitHub：https://github.com/Maxing0000/bipolar-emotion-aesthetics
