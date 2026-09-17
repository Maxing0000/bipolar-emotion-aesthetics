# BEA 各平台统一文案包 v2.8.0

> 本文档包含所有 AI 平台的统一文案，直接复制粘贴即可。
> 最后更新：2026-09-17
> 版本：v2.8.0

---

## 一、统一品牌标准（所有平台必须一致）

### 1. 名称
- **英文全称**：Bipolar Emotion Aesthetics
- **英文缩写**：BEA
- **中文名称**：双极情绪美学
- **统一显示名称**：`双极情绪美学 BEA`

### 2. 一句话核心价值
```
把审美判断从"我觉得"变成可讨论、可比较、可改进的协作工具。
```

### 3. 核心能力标签（统一）
`图片分析` `病症诊断` `设计优化` `美感生成` `方案对比` `快速诊断`

### 4. 覆盖领域（统一）
`产品/手机` `汽车/交通工具` `建筑/室内` `品牌/平面` `UI/交互` `服装/时尚` `音乐/声音` `影视/动画` `公共空间`

---

## 二、统一描述文案（三档，按平台字数限制选用）

### 📝 标准版（100-150字，适合大多数平台）

```
双极情绪美学（BEA）——把审美判断从"我觉得"变成可讨论、可比较、可改进的协作工具。用 W(T) 危极权重 + 六范式定位 + 四维评分卡，把"这个设计好不好看"变成可计算的元素级改进方案。支持图片分析、病症诊断、设计优化与美感生成，覆盖产品/汽车/建筑/品牌/UI/时尚九大领域。
```

### 📝 简短版（50字以内，适合列表页/短描述）

```
双极情绪美学 BEA——把审美判断从"我觉得"变成可讨论、可比较、可改进的协作工具。
```

### 📝 一句话版（30字以内，适合标签/搜索摘要）

```
用 W(T) 权重 + 六范式 + 四维评分，把"设计好不好看"变成可计算的改进方案。
```

---

## 三、统一示例提问（6个，所有平台通用）

> 直接复制到各平台的"示例"或"用户可能会问"字段。

```
1. 帮我看看这个手机设计怎么样
2. 这个 logo 为什么看起来有点廉价？
3. 怎么改能让它更有高级感？
4. 帮我设计一个崇高震撼风格的汽车外形
5. 这两个方案哪个更好？区别在哪？
6. 快速看看这个设计大概怎么样
```

---

## 四、各平台具体文案

### 1️⃣ 豆包 Doubao（SKILL.md frontmatter）

**文件位置**：`SKILL.md` 开头的 YAML frontmatter

```yaml
---
slug: bipolar-emotion-aesthetics
name: bipolar-emotion-aesthetics
displayName: 双极情绪美学 BEA
description: "双极情绪美学（BEA）v2.8.0——把审美判断从'我觉得'变成可讨论、可比较、可改进的协作工具。当用户说'这个设计好不好看/高级不高级/凶不凶/甜不甜/乱不乱/有没有廉价感/怎么改更高级/帮我设计一个XX风格'，或上传产品/手机/汽车/建筑/UI/品牌/海报图片要求评价分析改进，或讨论圆润vs尖锐/柔和vs硬朗/繁vs简/明vs暗/张力/比例/配色情绪/形态气质/风格定位/设计评审时使用。支持：①自然语言分析——大白话提问即可；②图片分析——上传图片自动识别元素极性、计算W(T)、定位范式、给出诊断和改进处方；③轻量级快速诊断——说'快速看看/大概怎么样'只输出结论+关键数据；④美感生成——给定目标风格自动生成维度配置。不用于：裁决内容美/道德美/思想美，非形式层的可用性、工程与安全评估。"
version: "2.8.0"
summary: 用 W(T) 权重 + 六范式 + 四维评分，把"这个设计好不好看"变成可计算的元素级改进方案。支持图片分析、病症诊断、设计优化与美感生成。
tags: [美学, 设计, 审美, 形式美, 双极情绪, BEA, 美感分析, 设计评审, 设计优化, 美感生成]
license: "CC BY-NC-SA 4.0"
homepage: https://maxing0000.github.io/bipolar-emotion-aesthetics/
updated: "2026-09-17"
author: "马星"
---
```

---

### 2️⃣ 扣子 Coze（Bot 配置）

**Bot 名称**：
```
双极情绪美学 BEA
```

**Bot 描述**（简短版，50字以内）：
```
双极情绪美学 BEA——把审美判断从"我觉得"变成可讨论、可比较、可改进的协作工具。
```

**Bot 开场白**：
```
你好！我是 BEA（双极情绪美学）专家，可以帮你分析、诊断、优化任何设计的美感。

你可以：
📷 上传产品/设计/建筑/UI图片，我来分析
💬 用大白话描述你的设计，我来诊断
🎯 告诉我想要的风格，我来生成方案

试试问我："帮我看看这个手机设计怎么样？"
```

**用户可能会问（6个示例）**：
```
帮我看看这个手机设计怎么样
这个 logo 为什么看起来有点廉价？
怎么改能让它更有高级感？
帮我设计一个崇高震撼风格的汽车外形
这两个方案哪个更好？区别在哪？
快速看看这个设计大概怎么样
```

**人设与回复逻辑（System Prompt）**：
> 见 `platforms/universal-system-prompt.md`，直接复制全文。

---

### 3️⃣ SkillHub

**显示名称**：
```
双极情绪美学 BEA
```

**Slug**：
```
bipolar-emotion-aesthetics
```

**版本号**：
```
2.8.0
```

**描述（标准版）**：
```
双极情绪美学（BEA）——把审美判断从"我觉得"变成可讨论、可比较、可改进的协作工具。用 W(T) 危极权重 + 六范式定位 + 四维评分卡，把"这个设计好不好看"变成可计算的元素级改进方案。支持图片分析、病症诊断、设计优化与美感生成，覆盖产品/汽车/建筑/品牌/UI/时尚九大领域。
```

**摘要（一句话版）**：
```
用 W(T) 权重 + 六范式 + 四维评分，把"这个设计好不好看"变成可计算的元素级改进方案。
```

**标签**：
```
美学, 设计, 审美, 形式美, 双极情绪, BEA, 美感分析, 设计评审, 设计优化, 美感生成
```

---

### 4️⃣ 虾评 Skill

**技能名称**：
```
双极情绪美学 BEA
```

**技能描述（标准版）**：
```
双极情绪美学（BEA）——把审美判断从"我觉得"变成可讨论、可比较、可改进的协作工具。用 W(T) 危极权重 + 六范式定位 + 四维评分卡，把"这个设计好不好看"变成可计算的元素级改进方案。支持图片分析、病症诊断、设计优化与美感生成，覆盖产品/汽车/建筑/品牌/UI/时尚九大领域。
```

---

### 5️⃣ ChatGPT / GPTs

**GPT 名称**：
```
双极情绪美学 BEA | Bipolar Emotion Aesthetics
```

**GPT 描述（简短版）**：
```
Bipolar Emotion Aesthetics (BEA) — Turn aesthetic judgment from "I think" into a discussable, comparable, improvable collaborative tool. Supports image analysis, diagnosis, design optimization and beauty generation.
```

**GPT 指令（System Prompt）**：
> 见 `platforms/universal-system-prompt.md`，直接复制全文（可保留中文，GPT 支持中文）。

**对话开场白**：
```
Hello! I'm a BEA (Bipolar Emotion Aesthetics) expert. I can help you analyze, diagnose, and optimize the aesthetics of any design.

You can:
📷 Upload product/design/architecture/UI images for analysis
💬 Describe your design in plain language for diagnosis
🎯 Tell me your desired style for generation

Try asking: "How does this phone design look? How can it be more premium?"
```

---

### 6️⃣ Claude（Project Instructions）

**项目名称**：
```
双极情绪美学 BEA
```

**Project Instructions**：
> 见 `platforms/universal-system-prompt.md`，直接复制全文。

---

### 7️⃣ 通义千问（智能体）

**智能体名称**：
```
双极情绪美学 BEA
```

**智能体描述（标准版）**：
```
双极情绪美学（BEA）——把审美判断从"我觉得"变成可讨论、可比较、可改进的协作工具。用 W(T) 危极权重 + 六范式定位 + 四维评分卡，把"这个设计好不好看"变成可计算的元素级改进方案。支持图片分析、病症诊断、设计优化与美感生成，覆盖产品/汽车/建筑/品牌/UI/时尚九大领域。
```

**系统提示词**：
> 见 `platforms/universal-system-prompt.md`，直接复制全文。

---

### 8️⃣ Dify（应用）

**应用名称**：
```
双极情绪美学 BEA
```

**应用描述（标准版）**：
```
双极情绪美学（BEA）——把审美判断从"我觉得"变成可讨论、可比较、可改进的协作工具。用 W(T) 危极权重 + 六范式定位 + 四维评分卡，把"这个设计好不好看"变成可计算的元素级改进方案。支持图片分析、病症诊断、设计优化与美感生成，覆盖产品/汽车/建筑/品牌/UI/时尚九大领域。
```

**系统提示词**：
> 见 `platforms/universal-system-prompt.md`，直接复制全文。

---

## 五、统一 Logo 与品牌素材

### Logo 文件位置
- **主 Logo**：`assets/bea-logo.png`（宇宙深空钻石，最终推荐版）
- **SkillHub 专用**：`assets/bea-logo-skillhub.png`（正方形，适合 SkillHub 上传）
- **各平台通用**：`assets/bea-logo-512x512.png`（512×512，大多数平台要求）

### 品牌色
- **主色**：深空蓝 `#1a1a2e`
- **强调色**：金色 `#d4a574`
- **辅助色**：暖白 `#f5e6d3`

---

## 六、各平台更新检查清单

> 更新完一个平台，打一个勾 ✅

- [ ] **豆包 Doubao**：SKILL.md frontmatter 更新为 v2.8.0
- [ ] **扣子 Coze**：Bot 名称、描述、开场白、示例、系统提示词全部更新
- [ ] **SkillHub**：显示名称、描述、摘要、标签、版本号更新
- [ ] **虾评 Skill**：技能名称、描述更新
- [ ] **ChatGPT / GPTs**：GPT 名称、描述、指令、开场白更新
- [ ] **Claude**：Project Instructions 更新
- [ ] **通义千问**：智能体名称、描述、系统提示词更新
- [ ] **Dify**：应用名称、描述、系统提示词更新
- [ ] **所有平台 Logo**：统一使用宇宙深空钻石 Logo
- [ ] **所有平台示例**：统一使用 6 个标准示例提问

---

## 七、版本信息

- **当前版本**：v2.8.0
- **发布日期**：2026-09-17
- **作者**：马星（星空本空）
- **官网**：https://maxing0000.github.io/bipolar-emotion-aesthetics/
- **GitHub**：https://github.com/Maxing0000/bipolar-emotion-aesthetics
- **许可证**：CC BY-NC-SA 4.0

---

*本文档为 BEA 各平台统一文案标准，所有平台的文案必须与此文档保持一致。如有修改，请先更新此文档，再同步到各平台。*
