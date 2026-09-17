# BEA MCP Server

把 BEA 量化引擎暴露为 MCP（Model Context Protocol）工具，任意支持 MCP 的 AI 客户端（WorkBuddy、Claude Desktop、Cursor、Cline、Continue 等）即可精确调用引擎，无需装任何第三方依赖——**纯 Python 标准库，离线可用**。

## 提供的工具（12 个）

| 工具 | 作用 |
|------|------|
| `bea_analyze` | 单对象分析：输入品类 + 各维度 t 值（0-10），返回 W(T)、六范式定位、四维评分、病症诊断与 markdown 报告 |
| `bea_compare` | A/B 对比：返回两方分析、逐维度差值与引擎对比报告 |
| `bea_dimensions` | 查询品类维度/权重定义、t 值标尺与七范式锚点（打分前必查） |
| `bea_diagnose` | 审美病症诊断：7 种病症按优先级排序，包含识别特征和处方 |
| `bea_suggest` | 调整建议：给定目标范式/W(T)，输出具体维度变更方案（含验证） |
| `bea_generate` | 美感生成：给定目标范式/W(T)，自动生成最优维度配置（三种策略） |
| `bea_sensitivity` | 灵敏度分析：找出改动哪个维度对 W(T) 影响最大 |
| `bea_paradigms` | 查询七范式定义、W(T) 区间、核心体验和典型应用场景 |
| `bea_diseases` | 查询 7 种审美病症诊断表（识别特征+发病机理+处方） |
| `bea_health` | 健康检查：服务器状态、版本号、引擎路径、支持的品类和工具列表 |
| `bea_multigroup` | 多组/跨模态分析：同时分析外形+内饰+声音等，检查跨模态一致性 |
| `bea_style_cycle` | 风格周期律分析：判断当前设计在风格周期中的位置和趋势 |

支持品类：`phone` / `car` / `brand` / `ui` / `building`

> 图片分析能力由 BEA 技能（SKILL.md）承载——技能侧可直接读图并按 `references/06-image-anchors.md` 打分，再把 t 值交给本 MCP 的 `bea_analyze` / `bea_compare` 算 W(T)。

## 一键安装（推荐）

### 交互式安装

```bash
python3 mcp-server/install.py
```

脚本会自动检测已安装的支持 MCP 的 AI 客户端，并引导你完成配置。

### 自动配置所有平台

```bash
python3 mcp-server/install.py --all
```

### 只配置指定平台

```bash
python3 mcp-server/install.py --claude     # 只配置 Claude Desktop
python3 mcp-server/install.py --cursor     # 只配置 Cursor
python3 mcp-server/install.py --workbuddy  # 只配置 WorkBuddy
```

### 查看配置状态

```bash
python3 mcp-server/install.py --status
```

### 卸载

```bash
python3 mcp-server/install.py --uninstall
```

安装后**重启对应的 AI 客户端**即可使用 BEA 工具。

## 手动配置

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

### 各平台配置文件位置

| 平台 | 配置文件路径 |
|------|-------------|
| **Claude Desktop** (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Desktop** (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| **WorkBuddy** | `~/.workbuddy/mcp.json` |
| **Cursor** (macOS) | `~/Library/Application Support/Cursor/User/mcp.json` |
| **Cursor** (Windows) | `%APPDATA%\Cursor\User\mcp.json` |
| **Cline** (VS Code) | `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/mcp_settings.json` |
| **Continue** (VS Code) | `~/.continue/config.json` |

## 调用示例

```
# 1. 查询维度（打分前必查）
bea_dimensions {}
bea_dimensions { "category": "car" }

# 2. 单对象分析
bea_analyze {
  "category": "car",
  "t_values": "曲面=4,特征线=6,灯组=5,比例=3,材质=4"
}

# 3. A/B 对比
bea_compare {
  "category": "car",
  "a": "方案A=4,6,5,3,4",
  "b": "方案B=曲面=7,特征线=6,灯组=5,比例=4,材质=4"
}

# 4. 病症诊断
bea_diagnose {
  "category": "phone",
  "t_values": "形状=1,质感=1,色彩=1,构图=1,光影=1,细节=1"
}

# 5. 调整建议
bea_suggest {
  "category": "car",
  "t_values": "曲面=4,特征线=6,灯组=5,比例=3,材质=4",
  "target": "0.30",
  "strategy": "focused"
}

# 6. 美感生成
bea_generate {
  "category": "phone",
  "target": "亲和精致",
  "strategy": "balanced"
}

# 7. 灵敏度分析
bea_sensitivity {
  "category": "car",
  "t_values": "曲面=4,特征线=6,灯组=5,比例=3,材质=4",
  "target": "0.30",
  "step": 1
}

# 8. 多组/跨模态分析
bea_multigroup {
  "category": "car",
  "groups": [
    {"name": "外形", "t_values": "曲面=4,特征线=6,灯组=5,比例=3,材质=4"},
    {"name": "内饰", "t_values": "曲面=3,特征线=3,灯组=3,比例=4,材质=3"}
  ]
}

# 9. 风格周期律
bea_style_cycle { "category": "car", "w_t": 0.45 }

# 10. 健康检查
bea_health {}
```

`t` 标尺：0 = 纯亲极（圆润/柔色/对称/舒缓），10 = 纯危极（尖锐/强对比/失衡/冷峻）。

## 自测

```bash
python3 mcp-server/test_server.py
```

起真实子进程走完整 MCP 会话（握手 → 工具列表 → 12 个工具调用 → 错误路径），共 155 项检查，并与引擎直算结果比对。

## 设计说明

- **协议**：JSON-RPC 2.0 over stdio（MCP `2024-11-05`），逐行读入、逐行写出
- **引擎复用**：通过 `importlib` 动态加载 `scripts/bea_quant.py`，版本号直接读引擎 `__version__`，不重复维护
- **工具级错误**：按 MCP 规范放入 `result.isError`，不中断会话
- **零依赖**：纯 Python 标准库实现，无需安装任何第三方包
- **离线可用**：所有计算在本地完成，无需网络连接

## 文件结构

```
mcp-server/
├── server.py          # MCP 服务器主文件（12 个工具）
├── install.py         # 一键安装脚本（自动配置各平台）
├── test_server.py     # 完整测试套件（155 项测试）
└── README.md          # 本文件
```

---
BEA v2.8.0 · 署名：马星 · CC BY-NC-SA 4.0