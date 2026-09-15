> Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

# 双极情绪美学 · Bipolar Emotion Aesthetics（BEA）

![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)
![Version](https://img.shields.io/badge/version-2.5.0-blue)
![Type](https://img.shields.io/badge/type-Agent%20Skill-success)
![Tests](https://img.shields.io/badge/tests-108%20passing-brightgreen)
![Website](https://img.shields.io/badge/website-GitHub%20Pages-orange)

> 把审美判断从"我觉得"变成可讨论、可比较、可追踪的协作工具。

## 在线体验

**[BEA 官方网站 →](https://maxing0000.github.io/bipolar-emotion-aesthetics/)**

无需安装，直接在浏览器中体验 BEA 双极情绪美学：

- **W(T) 互动计算器**：拖动滑块，实时计算危极权重与范式落点（支持手机/汽车/品牌/UI/建筑）
- **六范式谱系**：交互式浏览治愈松弛→先锋反叛的完整风格谱
- **核心理论**：亲极/危极双极模型、四维评分卡、六步创作法
- **病症诊断**：7种常见审美病症及元素级改进处方
- **案例库**：[30个真实案例完整分析](https://maxing0000.github.io/bipolar-emotion-aesthetics/case-library.html)（支持搜索/筛选/排序/对比）

## 多平台支持

BEA 技能可在多个 AI 平台使用，**零依赖纯文本模式**适用于所有平台：

| 平台 | 适配方式 | 文档 |
|---|---|---|
| **豆包 Doubao** | 原生 SKILL.md | 本文件 |
| **Coze 扣子** | Bot System Prompt / 插件 | `platforms/coze/` |
| **ChatGPT / GPTs** | Custom Instructions / GPTs | `platforms/chatgpt/` |
| **Claude** | Project Instructions | `platforms/claude/` |
| **通义千问** | 智能体 System Prompt | `platforms/tongyi/` |
| **Dify** | 应用系统提示词 / 工具 | `platforms/dify/` |

**30秒快速使用**：
1. 复制 `platforms/universal-system-prompt.md` 中的 System Prompt
2. 粘贴到你使用的 AI 平台的 System Prompt / 人设 / 指令中
3. 开始对话："帮我分析这个设计怎么样"

**两种使用模式**：
- **纯文本模式（推荐）**：零依赖，AI 按工作流程手动计算 W(T)，适用于所有平台
- **脚本增强模式**：调用 `scripts/bea_quant.py` 精确计算，需平台支持代码执行

**一键打包**：
```bash
python3 scripts/package.py --all  # 生成所有平台的适配包
# 输出到 dist/ 目录：core.zip / full.zip / system-prompt.txt / bea-{platform}.zip
```

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

## 快速开始

```bash
# 1. 生成分打模板（含维度顺序和锚点参考）
python3 scripts/bea_quant.py template --category phone

# 2. 完整分析报告
python3 scripts/bea_quant.py report --category car --t "曲面=4,特征线=6,灯组=5,比例=3,材质=4"

# 3. 调整建议：想达到某范式，该改哪个维度
python3 scripts/bea_quant.py suggest --category car --t "曲面=4,特征线=6,灯组=5,比例=3,材质=4" --target 崇高震撼

# 4. 美感生成：给定目标，自动生成最优维度配置
python3 scripts/bea_quant.py generate --category phone --target 0.30 --strategy balanced

# 5. 灵敏度分析：改哪个维度效果最明显
python3 scripts/bea_quant.py sensitivity --category car --t "曲面=4,特征线=6,灯组=5,比例=3,材质=4" --target 0.55
```

## 功能详解

### 1. 分析报告（report）

输入各维度危极强度（0-10），输出完整分析报告，包含：

- **维度极性审计**：每个维度的权重、t值、极性（亲极/中性/危极）
- **W(T) 危极综合权重**：整体张力水平，0-1
- **范式定位**：治愈松弛/亲和精致/均衡典雅/崇高震撼/冷峻克制/先锋反叛
- **维度贡献排序**：哪些维度对 W(T) 贡献最大
- **主辅比分析**：主导极性、亲危占比、是否达到 6:4 主辅比
- **耐看性评估**：0-100分，含 W(T)水平、维度稳定性、病症影响、主辅比四因素
- **病症诊断**：7种审美病症，含证据和处方
- **四维评分卡**：双极张力/结构秩序/阈值安全/语境适配，含加分扣分原因

**示例：**
```bash
python3 scripts/bea_quant.py report --category car --t "曲面=4,特征线=6,灯组=5,比例=3,材质=4"
```

输出：
```
W(T) = 0.450 → 均衡典雅
主辅比：53:47 ⚠ 主辅不足
耐看指数：88/100 极耐看
病症：无
四维评分：张力19 秩序20 阈值23 语境19 = 81/100
```

### 2. 调整建议（suggest）

给定目标范式或目标 W(T)，输出具体的维度调整方案。

**三种策略：**
- `focused`（集中，默认）：优先调整高权重维度，改动维度少但每个维度调整量大
- `distributed`（分散）：均衡调整多个维度，每个维度调整量小

**输出包含：**
- 调整方案表（维度、原值、目标值、变化、W(T)变化）
- 调整后验证（实际W(T)、偏差、调整维度数、总调整级数、是否达到目标）
- 调整后的新范式和新病症
- 可直接复制的验证命令

**示例：**
```bash
python3 scripts/bea_quant.py suggest --category car --t "曲面=4,特征线=6,灯组=5,比例=3,材质=4" --target 0.55
```

输出：
```
目标：W(T)=0.550 → 崇高震撼
【调整方案】
  曲面  4→7  +3  +0.090
  比例  3→4  +1  +0.015
【调整后验证】
  实际W(T)=0.555，偏差=+0.005 ✓ 已达到目标
  新范式：崇高震撼
```

### 3. 美感生成（generate）⭐ v2.5.0 新增

给定目标 W(T)/范式，**自动生成最优维度配置**。这是 BEA 从"分析"走向"生成"的核心功能。

**三种生成策略：**
- `balanced`（均衡，默认）：各维度差异适中，高权重维度略高
- `focused`（集中）：1-2个高权重维度承担主要危极，其他维度保持亲和
- `distributed`（分散）：各维度均匀提升，制造适度差异

**算法特点：**
- 自动微调使 W(T) 接近目标（偏差≤0.01）
- 避免极端值（t=0 或 t=10）
- 确保维度有适度差异（避免均分症）
- 输出可直接复制的命令

**示例：**
```bash
python3 scripts/bea_quant.py generate --category phone --target 亲和精致 --strategy balanced
```

输出：
```
目标：W(T)=0.200 → 亲和精致
【生成的维度配置】
  形状  t=3  质感  t=4  色彩  t=3
  构图  t=3  光影  t=2  细节  t=2
实际 W(T) = 0.305 → 均衡典雅（偏差+0.005）
```

### 4. 灵敏度分析（sensitivity）

计算每个维度 t±1（或 ±2/±3）对 W(T) 和四维评分的影响，找出"改动哪个维度效果最明显"。

**输出包含：**
- 最值得改动的维度排序（按综合灵敏度）
- 朝目标方向最有效的调整
- 详细灵敏度表（t+1/t-1 的 W(T)变化和评分变化）
- W(T)灵敏度和评分灵敏度分项

**示例：**
```bash
python3 scripts/bea_quant.py sensitivity --category car --t "曲面=4,特征线=6,灯组=5,比例=3,材质=4" --target 0.55 --step 1
```

### 5. 对比分析（compare）

对比两个设计方案的 W(T)、范式、维度差异、病症差异。

**支持两种输入格式：**
- 紧凑格式：`名称=4,6,5,3,4`（按维度顺序）
- 完整格式：`名称=曲面=4,特征线=6,...`（带维度名）

**示例：**
```bash
python3 scripts/bea_quant.py compare --category car --a "方案A=4,6,5,3,4" --b "方案B=7,6,5,4,4"
```

### 6. 多组分析（multigroup）

跨模态一致性检查 + 层级嵌套分析。输入多组维度数据（如外形/内饰/声音，或宏观/中观/微观），检查各组极性方向是否一致。

**输入格式：** `组名=维度=值,维度=值,...;组名=维度=值,...`

**输出包含：**
- 各组概览（W(T)、范式、主导极性、主辅比）
- 跨模态一致性评分（0-100，连续评分）
- 层级嵌套分析（同向叠加/微差补偿/反向冲突）

**示例：**
```bash
python3 scripts/bea_quant.py multigroup --category car \
  --groups "外形=曲面=4,特征线=6,灯组=5,比例=3,材质=4;内饰=曲面=3,特征线=3,灯组=4,比例=2,材质=3"
```

### 7. 风格周期律（style-cycle）

基于案例库 W(T) 分布，判断当前设计在风格周期中的位置（滞后/主流/领先/激进）。

**示例：**
```bash
python3 scripts/bea_quant.py style-cycle --category car --wt 0.45
```

### 8. 其他命令

- `analyze`：分析并输出 JSON（供程序调用）
- `score`：四维评分辅助（含加分/扣分原因）
- `batch`：批量产品对比
- `template`：打分模板（含维度顺序和锚点参考）
- `test`：自测试（108项）
- `list-profiles` / `save-profile` / `delete-profile`：自定义权重配置管理

## 命令速查

| 命令 | 用途 | 核心输出 |
|---|---|---|
| `report` | 完整分析报告 | W(T)、范式、主辅比、耐看性、病症、四维评分 |
| `suggest` | 调整建议 | 维度变更方案 + 调整后验证 |
| `generate` | ⭐ 美感生成 | 给定目标自动生成最优维度配置 |
| `sensitivity` | 灵敏度分析 | 各维度改动效果排序 |
| `compare` | 两方案对比 | W(T)、维度、病症差异 |
| `multigroup` | 多组/跨模态分析 | 一致性评分 + 层级嵌套 |
| `style-cycle` | 风格周期律 | 滞后/主流/领先/激进定位 |
| `analyze` | JSON 输出 | 供程序调用 |
| `template` | 打分模板 | 维度顺序 + 锚点参考 |
| `test` | 自测试 | 108项测试 |

**支持品类：** `phone`（手机）/ `car`（汽车）/ `brand`（品牌）/ `ui`（界面）/ `building`（建筑）

## 维度与权重

### 手机（phone）
| 维度 | 权重 | 说明 |
|---|---|---|
| 形状线条 | 0.25 | 整机轮廓、圆角、倒角 |
| 质感触觉 | 0.25 | 背板材质、中框触感、握持感 |
| 色彩 | 0.15 | 机身颜色、饱和度、明度 |
| 构图比例 | 0.15 | 屏幕比例、镜头布局、重量分布 |
| 光影 | 0.10 | 反光效果、亮面/哑光 |
| 细节线条 | 0.10 | 按键、接口、缝线、字体 |

### 汽车（car）
| 维度 | 权重 | 说明 |
|---|---|---|
| 形体曲面动势 | 0.30 | 车身曲面、楔形姿态、肌肉感 |
| 特征线条 | 0.25 | 腰线、特征棱线、肩线 |
| 灯组图形 | 0.15 | 大灯、尾灯、日行灯造型 |
| 比例姿态 | 0.15 | 车身高宽比、轴距、视觉重心 |
| 材质光影 | 0.15 | 车漆、金属质感、反光 |

### 品牌（brand）
| 维度 | 权重 |
|---|---|
| 图形形状 | 0.25 |
| 色彩 | 0.25 |
| 字体 | 0.20 |
| 版式构图 | 0.20 |
| 质感 | 0.10 |

### 界面（ui）
| 维度 | 权重 |
|---|---|
| 布局留白 | 0.25 |
| 色彩对比 | 0.20 |
| 组件形 | 0.20 |
| 动效 | 0.20 |
| 字体图标 | 0.15 |

### 建筑（building）
| 维度 | 权重 |
|---|---|
| 形体轮廓 | 0.30 |
| 立面线条 | 0.25 |
| 比例尺度 | 0.20 |
| 材质肌理 | 0.15 |
| 光影空间 | 0.10 |

## 六范式与 W(T) 区间

| 范式 | W(T) 区间 | 核心体验 | 典型应用 |
|---|---|---|---|
| 治愈松弛 | <0.15 | 放松、舒展、无攻击性 | 母婴、疗愈空间、医疗 |
| 亲和精致 | 0.15-0.30 | 第一眼亲和，细看精密 | 消费电子、主流品牌 |
| 均衡典雅 | 0.30-0.48 | 刚柔各半、克制端庄 | 经典主义、奢侈品 |
| 崇高震撼 | 0.48-0.60 | 先屏息敬畏、后沉浸沉醉 | 大型建筑、豪华旗舰 |
| 冷峻克制 | 0.60-0.66 | 冷硬简、精准比例 | 极简主义、专业工具 |
| 先锋反叛 | 0.66-0.85 | 刺激、反叛、临界于不适 | 潮牌、亚文化、概念设计 |
| 逼近越阈 | ≥0.85 | 非美区（真实不适） | — |

## 7种审美病症

| 病症 | 优先级 | 识别特征 | 处方 |
|---|---|---|---|
| 本能越界 | 一级（一票否决） | 任何维度 t>=10，触及生理红线 | 删除或钝化，无风格借口 |
| 攻击症 | 二级（严重） | W(T)>=0.55 且有 t>=6，令人紧张 | 扩大亲极基底，降危极到范式区间 |
| 刺激疲劳 | 二级（严重） | W(T)>=0.65 且所有 t>=7，全程高能 | 安排亲极呼吸段，控制强调点 |
| 重点通胀症 | 三级（中等） | >=3个维度 t>=6，视觉噪音大 | 做减法，强调点压回1-2个 |
| 均分症 | 三级（中等） | 所有 t 在3-5，W(T) 0.35-0.45，极差<2 | 确立>=6:4主辅比 |
| 甜腻症 | 四级（轻微） | W(T)<0.25 且所有 t<=4，无锐度 | 高价值细节注入10%-20%危极 |
| 张力不足症 | 四级（轻微） | W(T)<0.35 且极差<2，无记忆点 | 1-2个维度提升到6+，制造对比 |

## 典型使用场景

### 场景1：设计评审
```bash
# 评审一个手机设计，输出完整报告
python3 scripts/bea_quant.py report --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
```

### 场景2：方案对比
```bash
# 对比两个汽车设计方案
python3 scripts/bea_quant.py compare --category car --a "方案A=4,6,5,3,4" --b "方案B=7,6,5,4,4"
```

### 场景3：目标导向设计
```bash
# 想要崇高震撼风格的手机，自动生成最优配置
python3 scripts/bea_quant.py generate --category phone --target 崇高震撼 --strategy focused
```

### 场景4：优化现有设计
```bash
# 现有设计想调整到亲和精致，看该改哪个维度
python3 scripts/bea_quant.py suggest --category car --t "曲面=7,特征线=8,灯组=6,比例=5,材质=6" --target 亲和精致
```

### 场景5：跨模态一致性检查
```bash
# 检查汽车外形和内饰的极性是否一致
python3 scripts/bea_quant.py multigroup --category car \
  --groups "外形=曲面=5,特征线=7,灯组=6,比例=4,材质=5;内饰=曲面=3,特征线=3,灯组=4,比例=2,材质=3"
```

## 目录结构

```
bipolar-emotion-aesthetics/
├── SKILL.md                    # 技能入口文档（豆包原生格式）
├── manifest.json               # 标准化元数据（多平台识别）
├── README.md                   # 项目说明（本文件）
├── QUICKSTART.md               # 1分钟快速上手指南
├── FAQ.md                      # 常见问题解答
├── CHANGELOG.md                # 版本变更记录
├── LICENSE                     # CC BY-NC-SA 4.0
├── install.sh                  # macOS/Linux 一键安装
├── install.ps1                 # Windows 一键安装
├── uninstall.sh                # 卸载
├── update.sh                   # 更新
├── scripts/
│   ├── bea_quant.py            # 量化引擎（仅 Python 标准库，离线可用）
│   ├── bea_guide.py            # 交互式引导脚本（不需要记命令）
│   └── package.py              # 多平台打包工具
├── references/
│   ├── 01-core-theory.md       # 核心理论、六范式、W(T)公式、病症处方
│   ├── 02-workflow.md          # 评审流程、竞品分析、定调方法
│   ├── 03-dimension-guide.md   # 维度定义 + 真实产品锚点
│   ├── 04-checklist.md         # 设计自查清单
│   └── 05-case-studies.md      # 真实案例库（九大领域15个案例）
├── platforms/                   # 多平台适配
│   ├── README.md                # 多平台适配总索引
│   ├── universal-system-prompt.md  # 通用 System Prompt（复制粘贴即用）
│   ├── coze/                    # Coze 扣子适配
│   ├── chatgpt/                 # ChatGPT / GPTs 适配
│   ├── claude/                  # Claude 适配
│   ├── tongyi/                  # 通义千问适配
│   └── dify/                    # Dify 适配
├── docs/
│   └── index.html              # 官方网站（GitHub Pages）
└── templates/
    ├── review-record.md        # 评审记录标准模板
    └── output-templates.md     # 标准化输出模板（4种格式）
```

## 重要边界

1. W(T) 是协作刻度，不是物理常数——误差带至少 ±0.1
2. 不替代用户测试——W(T) 高不等于用户喜欢
3. 不评判艺术创作——先锋艺术刻意越阈，BEA 会误判
4. 只对形式美负责——不裁决内容美、道德美、工程可行性

## 许可证

CC BY-NC-SA 4.0（署名-非商业性使用-相同方式共享）

**作者：马星**
