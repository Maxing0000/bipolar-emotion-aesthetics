# BEA MCP Server

把**双极情绪美学（BEA）**的计算工具暴露给所有 MCP 客户端（Claude Desktop、Cursor、WorkBuddy 等）。
一次安装，你的 AI 助手直接获得「计算 W(T)、A/B 方案对比、评分卡诊断」能力。

## 四个工具

| 工具 | 作用 |
|---|---|
| `bea_list_categories` | 列出内置品类（phone/car/brand/ui）与维度权重表 |
| `bea_wt_calc` | 计算危极指数 W(T)：范式落点 + 极性画像 + 目标区间对照 |
| `bea_wt_compare` | A/B 双方案对比：双画像 + 差异维度 + 目标接近度裁决 |
| `bea_scoresheet` | 评分卡：四维打分（各 25 分）+ 短板定位 + 六步法修复指引 |

## 安装

```bash
# 方式一：PyPI 一键安装（推荐）
pip install bea-mcp

# 方式二：从 GitHub 直接安装
pip install "git+https://github.com/Maxing0000/bipolar-emotion-aesthetics#subdirectory=mcp-server"

# 方式三：本地源码
git clone https://github.com/Maxing0000/bipolar-emotion-aesthetics
cd bipolar-emotion-aesthetics/mcp-server
pip install .
```

要求 Python ≥ 3.10，唯一依赖是官方 `mcp` SDK。

## 客户端配置

**Claude Desktop**（`claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "bea-aesthetics": {
      "command": "python3",
      "args": ["-m", "bea_mcp.server"]
    }
  }
}
```

**Cursor / WorkBuddy**（MCP 配置同理，command 用安装环境的 python 绝对路径更稳）：

```json
{
  "mcpServers": {
    "bea-aesthetics": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "bea_mcp.server"]
    }
  }
}
```

## 使用示例（对 AI 说）

- 「用 BEA 算一下这款手机设计：形状线条 2、质感触觉 4、色彩 6、构图比例 3、光影 3、细节线条 4，目标 0.28」
- 「A/B 对比两个 LOGO 方案，帮我裁决哪个更接近亲和精致」
- 「评分卡：张力 20、秩序 22、阈值 23、语境 21，看看有没有短板」

## 说明

- 数据表与仓库 `../bipolar-emotion-aesthetics/scripts/` 的 wt_calc.py / scoresheet.py 保持一致（CI 同步校验）
- 0–10 刻度与 W(T) 为协作参照刻度，非心理物理常数
- 理论全文见仓库 `../docs/theory-book.html`；交互计算器见 [在线版](https://maxing0000.github.io/bipolar-emotion-aesthetics/)
- 许可：CC BY 4.0，使用请署名「星空本空 / BEA」
