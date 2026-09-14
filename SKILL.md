> Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

---
name: bipolar-emotion-aesthetics
description: "双极情绪美学（BEA）v2.4——把审美判断从'我觉得'变成可讨论、可比较、可追踪、可优化的协作工具。当用户需要分析、评价、诊断、优化任何以感官形式呈现的对象（产品/手机/汽车/建筑/平面/品牌/UI/服装）的美感、高级感、亲和力、攻击性、治愈感、冷峻感、崇高感，或讨论圆润与尖锐、柔和与硬朗、繁与简、明与暗、甜腻、廉价感、张力、比例、配色情绪时使用。支持：①图片分析——上传产品/设计图后识别元素极性、计算W(T)、定位范式、生成四维评分卡、给出病症诊断与元素级改进处方；②量化计算——通过bea_quant.py执行W(T)计算、范式定位、病症诊断、竞品对比、批量分析、灵敏度分析（支持t±1/2/3步长）、主辅比计算、耐看性评估；③设计优化——灵敏度分析找出最值得改的维度，调整建议给出完整方案，跨模态一致性检查和层级嵌套分析确保全通道协同；④设计评审——提供团队打分模板、评审流程、自查清单、真实案例参考、风格周期律判断；⑤自定义权重——支持保存和加载自定义权重配置，适配特殊品类。不用于：裁决内容美/道德美/思想美，非形式层的可用性、工程与安全评估，艺术创作评判。"
version: "2.4.0"
updated: "2026-09-15"
author: "马星"
license: "CC BY-NC-SA 4.0"
---

# 双极情绪美学（BEA）v2.2

## 核心价值

**BEA 解决的根本问题不是"什么是美"，而是"美感无法被讨论"。**

设计评审中，"我觉得不好看"是私人判断，无法争论。BEA 把它拆成维度、标极性、算权重、定范式、开处方——让审美从**投票**变成**工程**。你可以不同意某个人打的分，但争论的是"这个圆角到底是亲极 2 还是 3"，而不是"你懂不懂审美"——前者有解，后者无解。

**核心命题**：美感 = 可控张力下的情绪奖赏。亲极（圆润/柔色/对称）安其心，危极（尖锐/强对比/坚硬）提其神，秩序统其乱，阈值守其界。

> 完整理论（六范式、W(T)公式、四维评分、病症处方）见 `references/01-core-theory.md`

## 快速上手（5分钟）

1. **看维度定义**：读 `references/03-dimension-guide.md`，知道每个维度看什么、有哪些真实产品锚点
2. **打一轮分**：对着分析对象按维度打 t 值（0-10），不确定先打中间值
3. **算 W(T)**：`python3 scripts/bea_quant.py report --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"`
4. **看诊断**：报告给出范式和病症，对照 `references/04-checklist.md` 自查
5. **看案例**：不确定打得对不对？读 `references/05-case-studies.md` 校准

团队评审用 `templates/review-record.md` 记录。评审流程见 `references/02-workflow.md`。

## 量化引擎

`scripts/bea_quant.py`，仅用 Python 标准库，离线可用。

```bash
# 分析（JSON输出，适合程序处理）
python3 scripts/bea_quant.py analyze --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"

# 完整报告（人类可读，含范式光谱和病症诊断）
python3 scripts/bea_quant.py report --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"

# 详细评分辅助（含每个维度的加分/扣分原因）
python3 scripts/bea_quant.py score --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"

# 调整建议：给定目标范式，输出该改哪个维度、改多少
python3 scripts/bea_quant.py suggest --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6" --target 崇高震撼

# 灵敏度分析：找出改动哪个维度效果最明显（v2.3新增）
python3 scripts/bea_quant.py sensitivity --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
# 带目标：计算朝目标方向最有效的调整
python3 scripts/bea_quant.py sensitivity --category phone --t "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6" --target 0.2

# 两个产品对比（支持紧凑格式和完整格式混合使用）
python3 scripts/bea_quant.py compare --category phone --a "iPhone=3,6,4,3,5,6" --b "Samsung=形状=4,质感=4,色彩=4,构图=3,光影=3,细节=5"

# 批量分析多个产品（分号分隔）
python3 scripts/bea_quant.py batch --category phone --items "A=3,6,4,3,5,6;B=形状=4,质感=4,色彩=4,构图=3,光影=3,细节=5"

# 生成分打模板（含维度顺序，用于紧凑格式）
python3 scripts/bea_quant.py template --category phone

# 自测试
python3 scripts/bea_quant.py test
```

**输入格式说明**：
- `analyze`/`report`/`score` 用完整格式：`形状=3,质感=6,...`
- `compare`/`batch` 的每个产品支持两种格式（自动识别）：
  - 紧凑格式：`名称=3,6,4,3,5,6`（按 `template` 输出的维度顺序）
  - 完整格式：`名称=形状=3,质感=6,...`（带维度名，推荐，不易出错）

支持品类：`phone`（手机）/ `car`（汽车）/ `brand`（品牌平面）/ `ui`（界面）

## 图片分析工作流

用户上传产品/设计图片时：
1. 视觉识别：形状、色彩、质感、构图、光影
2. 极性标注：每维度标方向（P亲/T危）和强度（0-10）
3. W(T)计算：调用 `bea_quant.py report`
4. 范式定位：对照六范式
5. 四维评分
6. 病症诊断
7. 改进处方：具体维度、目标强度、预期效果

## 重要边界

1. **W(T) 是协作刻度，不是物理常数**——误差带至少 ±0.1，不要纠结小数点
2. **不替代用户测试**——W(T) 高不等于用户喜欢
3. **不评判艺术创作**——先锋艺术刻意越阈，BEA 会误判
4. **只对形式美负责**——不裁决内容美、道德美、工程可行性
5. **均衡典雅不是"最好"**——根据产品定位选范式，不要默认往中间挤
6. **层级冲突症需人工判断**——宏观/微观一致性无法自动诊断

## 文档索引

| 文件 | 内容 | 何时读 |
|---|---|---|
| `references/01-core-theory.md` | 核心理论、六范式、W(T)公式、四维评分、病症处方、t值校准 | 需要深入理论时 |
| `references/02-workflow.md` | 45分钟评审流程、竞品分析模板、定调流程、6个常见误区 | 实际执行评审时 |
| `references/03-dimension-guide.md` | **四个品类每个维度的定义+真实产品锚点** | 打分前必读 |
| `references/04-checklist.md` | **设计自查清单**（含5分钟快速版） | 设计定稿前、评审前 |
| `references/05-case-studies.md` | **真实案例库**（iPhone Duo、S26 Ultra、Model 3、苹果品牌） | 校准打分、参考写法 |
| `templates/review-record.md` | **评审记录标准模板** | 每次评审后填写存档 |

---

**BEA v2.2** — 审美协作基础设施
工具：bea_quant.py（分析/报告/评分/对比/批量/模板）
