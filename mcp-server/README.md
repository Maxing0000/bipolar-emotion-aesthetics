# BEA MCP Server

把 BEA 量化引擎暴露为 MCP（Model Context Protocol）工具，任意支持 MCP 的 AI 客户端（WorkBuddy、Claude Desktop、Cursor 等）即可精确调用引擎，无需装任何第三方依赖——**纯 Python 标准库，离线可用**。

## 提供的工具

| 工具 | 作用 |
|------|------|
| `bea_analyze` | 单对象分析：输入品类 + 各维度 t 值（0-10），返回 W(T)、六范式定位、病症诊断、调分建议与 markdown 报告 |
| `bea_compare` | A/B 对比：返回两方分析、逐维度差值与引擎对比报告 |
| `bea_dimensions` | 查询品类维度/权重定义、t 值标尺与六范式锚点（打分前必查） |
| `bea_suggest` | 调整建议：给定目标（范式名或 W(T)），返回逐步调分方案与调整后验证 |
| `bea_generate` | 美感生成：给定目标自动生成最优维度配置（三种策略） |
| `bea_sensitivity` | 灵敏度分析：找出"改动哪个维度效果最明显" |
| `bea_batch` | 批量分析：多对象一次分析并按 W(T) 排名 |
| `bea_rubric` | 视觉评分标尺：AI 看图打 t 值的锚点依据（看图打分前必查） |
| `bea_analyze_image` | 图片直接分析：程序提取六项视觉特征 → t 值 → W(T)（需 Pillow，`pipx install "bea-mcp[image]"`） |

支持品类：`phone` / `car` / `brand` / `ui` / `building`

## 客户端配置

**方式一：npx 免安装（推荐，需 Node.js）**

```json
{
  "mcpServers": {
    "bea": {
      "command": "npx",
      "args": ["-y", "bea-mcp"]
    }
  }
}
```

**方式二：pipx 安装（推荐，需 Python 3.9+）**

```bash
pipx install bea-mcp              # 基础版（8 个工具）
pipx install "bea-mcp[image]"     # 加图片直接分析（9 个工具）
```

```json
{
  "mcpServers": {
    "bea": {
      "command": "bea-mcp"
    }
  }
}
```

**方式三：直接指向仓库**（开发者）

将下方片段加入客户端的 MCP 配置（路径改为你的实际路径）：

```json
{
  "mcpServers": {
    "bea": {
      "command": "python3",
      "args": ["/绝对路径/BEA/mcp-server/server.py"]
    }
  }
}
```

- **WorkBuddy**：连接器管理 → 自定义连接器 → 编辑 `~/.workbuddy/mcp.json` 后在页面点击「信任」启用
- **Claude Desktop**：`claude_desktop_config.json` 同上格式

## 调用示例

```
bea_rubric { category: "building" }        → 看图打分前先取标尺
bea_analyze_image { category: "building", path: "/path/to/photo.jpg" }
bea_dimensions {}                          → 获取 5 个品类的维度与权重
bea_analyze { category: "phone",
              t_values: "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6" }
bea_compare { category: "building",
              a: "中银=8,7,6,5,6",         ← 紧凑格式（按维度顺序）
              b: "汇丰=立面线条=4,比例尺度=6,..." }  ← 完整格式（带维度名）
```

`t` 标尺：0 = 纯亲极（圆润/柔色/对称/舒缓），10 = 纯危极（尖锐/强对比/失衡/冷峻）。

## 自测

```bash
python3 mcp-server/test_server.py
```

起真实子进程走完整 MCP 会话（握手 → 工具列表 → 九工具调用 → 错误路径），共 41 项检查，并与引擎直算结果比对。

## 设计说明

- 协议：JSON-RPC 2.0 over stdio（MCP `2024-11-05`），逐行读入、逐行写出
- 引擎复用：通过 `importlib` 动态加载 `scripts/bea_quant.py`（以及 `bea_rubric.py`、`bea_image.py`），版本号直接读引擎 `__version__`，不重复维护
- 图像分析（`bea_analyze_image`）依赖可选的 Pillow；未安装时该工具优雅报错，其余 8 个工具不受影响
- 工具级错误按 MCP 规范放入 `result.isError`，不中断会话

---
BEA v2.12.0 · 署名：马星 · CC BY-NC-SA 4.0
