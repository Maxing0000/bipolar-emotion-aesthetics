# 双极情绪美学 BEA

> **美感 = 可控张力下的情绪奖赏。**
>
> 把"我觉得不好看"变成可讨论、可比较、可改进的设计协作工具。

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Version](https://img.shields.io/badge/version-2.8.0-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)]()
[![Self-test](https://img.shields.io/badge/tests-108%20passed-brightgreen.svg)]()

---

## 这是什么

BEA（Bipolar Emotion Aesthetics）是一套形式美分析框架。它把审美判断拆成：

- **亲极 P+**（圆润 / 柔色 / 对称 / 舒缓）—— 安其心，让人想接近
- **危极 T−**（尖锐 / 强对比 / 坚硬 / 突变）—— 提其神，制造唤醒与张力

单一极性不产生高级美感：纯亲极甜腻平庸，纯危极攻击排斥。双极在秩序中组合、危极被约束在安全阈值内，才得到"既被吸引、又被安抚"的复合愉悦。

```
W(T) = Σ wᵢ × (tᵢ / 10)     →     0 ~ 1     →     定位到六种范式
```

---

## 六范式

| W(T) 区间 | 范式 | 核心体验 | 典型场景 |
|---|---|---|---|
| < 0.15 | 治愈松弛 | 放松舒展、无攻击性 | 母婴、疗愈、医疗 |
| 0.15 – 0.30 | 亲和精致 | 第一眼亲和，细看精密 | 消费电子、主流品牌 |
| 0.30 – 0.48 | 均衡典雅 | 刚柔各半、克制端庄 | 奢侈品、经典主义 |
| 0.48 – 0.60 | 崇高震撼 | 屏息敬畏后沉浸 | 旗舰产品、大型建筑 |
| 0.60 – 0.66 | 冷峻克制 | 冷硬简、精准比例 | 极简主义、专业工具 |
| 0.66 – 0.85 | 先锋反叛 | 刺激、临界于不适 | 潮牌、亚文化 |

---

## 快速开始

### 在 AI 助手中使用

直接对 AI 说大白话即可，例如：

- "帮我看看这个手机设计怎么样"
- "这个 logo 为什么看起来有点廉价？"
- "怎么改能让它更有高级感？"
- "帮我设计一个崇高震撼风格的汽车外形"
- "快速看看这个设计"（只给结论 + 关键数据）

上传图片也可以——AI 会自动识别形状、色彩、质感、构图、光影，逐维度打分。

### 命令行量化引擎

```bash
# 分析一个设计（输出 W(T)、范式、病症、四维评分）
python3 scripts/bea_quant.py report \
  --category car \
  --t "曲面=4,特征线=6,灯组=5,比例=3,材质=4"

# 给定目标范式，生成调整建议
python3 scripts/bea_quant.py suggest \
  --category car \
  --t "曲面=4,特征线=6,灯组=5,比例=3,材质=4" \
  --target 崇高震撼

# 美感生成：给定目标 W(T)，自动生成最优维度配置
python3 scripts/bea_quant.py generate --category phone --target 0.30

# 两个方案对比
python3 scripts/bea_quant.py compare \
  --category phone \
  --a "方案A=3,6,4,3,5,6" \
  --b "方案B=4,4,4,3,3,5"
```

支持品类：`phone`（手机）/ `car`（汽车）/ `brand`（品牌）/ `ui`（界面）/ `building`（建筑）。仅依赖 Python 标准库，离线可用。

---

## 七种审美病症

| 优先级 | 病症 | 识别特征 | 处方 |
|---|---|---|---|
| 一票否决 | 本能越界 | 任何维度 t ≥ 10 | 立即删除或钝化 |
| 严重 | 攻击症 | W(T) ≥ 0.55 且有 t ≥ 6 | 扩亲极基底，降危极 |
| 严重 | 刺激疲劳 | W(T) ≥ 0.65 且所有 t ≥ 7 | 安排亲极呼吸段 |
| 中等 | 重点通胀 | ≥ 3 个维度 t ≥ 6 | 做减法，强调点压回 1–2 个 |
| 中等 | 均分症 | 所有 t 在 3–5，无主次 | 确立 ≥ 6:4 主辅比 |
| 轻微 | 甜腻症 | W(T) < 0.25 且所有 t ≤ 4 | 高价值细节注入 10–20% 危极 |
| 轻微 | 张力不足 | W(T) < 0.35 且极差 < 2 | 1–2 个维度提至 6+ |

---

## 项目结构

```
bipolar-emotion-aesthetics/
├── SKILL.md                          # AI 技能入口
├── manifest.json                     # 版本元数据
├── LICENSE.md
├── scripts/
│   ├── bea_quant.py                  # 核心量化引擎（CLI）
│   └── bea_guide.py                  # 引导脚本
├── references/
│   ├── 01-core-theory.md             # 核心理论与 t 值校准
│   ├── 02-workflow.md                # 评审流程与常见误区
│   ├── 03-dimension-guide.md         # 五品类维度定义与产品锚点
│   ├── 04-checklist.md                # 设计自查清单
│   ├── 05-case-studies.md           # 真实案例库
│   ├── 06-image-anchors.md          # 图片分析锚点
│   └── 07-universal-system-prompt.md  # 跨平台 System Prompt
└── templates/
    ├── output-templates.md           # 标准化输出格式（含 JSON）
    └── review-record.md              # 评审记录模板
```

---

## 跨平台部署

BEA 已封装为标准 AI Skill，可直接在支持 Skill 的平台使用（豆包、Claude、Cursor、Windsurf 等）。

对于不支持 Skill 的平台（ChatGPT / 通义 / Dify / Coze 等），复制 `references/07-universal-system-prompt.md` 中的 System Prompt，粘贴到平台的"人设 / 系统指令"中即可。

---

## 边界

- W(T) 是协作刻度，不是物理常数，误差带 ±0.1。
- 只分析形式美，不裁决内容美、道德美、工程可行性、安全性。
- 先锋艺术刻意越阈，BEA 会误判——本框架适用于商业设计。
- 均衡典雅不是"最好"，根据产品定位选范式。

---

## 许可

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) —— 署名-非商业性使用-相同方式共享。

---

<p align="center">用 BEA，把"好看"说清楚。</p>
