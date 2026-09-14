> Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

# 双极情绪美学 · Bipolar Emotion Aesthetics（BEA）

![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)
![Version](https://img.shields.io/badge/version-2.2.0-blue)
![Type](https://img.shields.io/badge/type-Agent%20Skill-success)
![Website](https://img.shields.io/badge/website-GitHub%20Pages-orange)

> 把审美判断从"我觉得"变成可讨论、可比较、可追踪的协作工具。

## 在线体验

**[BEA 官方网站 →](https://maxing0000.github.io/bipolar-emotion-aesthetics/)**

无需安装，直接在浏览器中体验 BEA 双极情绪美学：

- **W(T) 互动计算器**：拖动滑块，实时计算危极权重与范式落点（支持手机/汽车/品牌/UI）
- **六范式谱系**：交互式浏览治愈松弛→先锋反叛的完整风格谱
- **核心理论**：亲极/危极双极模型、四维评分卡、六步创作法
- **病症诊断**：6种常见审美病症及元素级改进处方
- **九大应用领域**：从消费电子到公共空间的完整覆盖

## 核心价值

BEA 不回答"什么是美"，而是解决"美感无法被讨论"的问题。

设计评审中，"我觉得不好看"是私人判断，无法争论。BEA 把它拆成维度、标极性、算权重、定范式、开处方——让审美从**投票**变成**工程**。

**核心命题**：美感 = 可控张力下的情绪奖赏。亲极（圆润/柔色/对称）安其心，危极（尖锐/强对比/坚硬）提其神，秩序统其乱，阈值守其界。

## 安装

### 一键安装（推荐）

**macOS / Linux：**
```bash
curl -fsSL https://raw.githubusercontent.com/Maxing0000/bipolar-emotion-aesthetics/main/install.sh | bash
```

**Windows（PowerShell）：**
```powershell
irm https://raw.githubusercontent.com/Maxing0000/bipolar-emotion-aesthetics/main/install.ps1 | iex
```

安装脚本会自动检测 Skill 目录、复制文件、运行自测试验证。

### 手动安装

```bash
# 克隆到你的 Skill 目录
git clone https://github.com/Maxing0000/bipolar-emotion-aesthetics.git \
  ~/path/to/your/skills/bipolar-emotion-aesthetics

# 验证
cd ~/path/to/your/skills/bipolar-emotion-aesthetics
python3 scripts/bea_quant.py test
```

### 环境要求

- Python 3.7+（仅用标准库，无需 pip install）
- Git（一键安装需要，手动安装可选）

### 卸载 / 更新

```bash
# 卸载
./uninstall.sh

# 更新到最新版
./update.sh
```

## 快速开始

```bash
# 生成分打模板（含维度顺序和锚点参考）
python3 scripts/bea_quant.py template --category phone

# 完整分析报告
python3 scripts/bea_quant.py report --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"

# 调整建议：想达到某范式，该改哪个维度
python3 scripts/bea_quant.py suggest --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6" --target 崇高震撼
```

## 命令速查

| 命令 | 用途 |
|---|---|
| `analyze` | 分析并输出 JSON |
| `report` | 人类可读报告（维度审计、W(T)、贡献排序、范式距离、病症诊断） |
| `score` | 四维评分辅助（含加分/扣分原因） |
| `suggest` | 调整建议（给定目标范式，输出维度变更方案） |
| `compare` | 两个产品对比 |
| `batch` | 批量产品对比 |
| `template` | 打分模板（含维度顺序） |
| `test` | 自测试（27项） |

支持品类：`phone` / `car` / `brand` / `ui`

## 目录结构

```
bipolar-emotion-aesthetics/
├── SKILL.md                    # 技能入口文档
├── README.md                   # 项目说明（本文件）
├── FAQ.md                      # 常见问题解答（20个高频问题）
├── CHANGELOG.md                # 版本变更记录
├── install.sh                  # macOS/Linux 一键安装
├── install.ps1                 # Windows 一键安装
├── uninstall.sh                # 卸载
├── update.sh                   # 更新
├── scripts/
│   └── bea_quant.py            # 量化引擎（仅 Python 标准库，离线可用）
├── references/
│   ├── 01-core-theory.md       # 核心理论、六范式、W(T)公式、病症处方
│   ├── 02-workflow.md          # 评审流程、竞品分析、定调方法
│   ├── 03-dimension-guide.md   # 维度定义 + 真实产品锚点（打分前必读）
│   ├── 04-checklist.md         # 设计自查清单（含5分钟快速版）
│   └── 05-case-studies.md      # 真实案例（iPhone Duo、S26 Ultra 等）
└── templates/
    └── review-record.md        # 评审记录标准模板
```

## 重要边界

1. W(T) 是协作刻度，不是物理常数——误差带至少 ±0.1
2. 不替代用户测试——W(T) 高不等于用户喜欢
3. 不评判艺术创作——先锋艺术刻意越阈，BEA 会误判
4. 只对形式美负责——不裁决内容美、道德美、工程可行性

## 许可证

CC BY-NC-SA 4.0（署名-非商业性使用-相同方式共享）
