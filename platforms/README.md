# BEA 多平台适配指南

BEA（双极情绪美学）技能可在多个 AI 平台使用，本目录提供各平台的适配方案。

## 支持平台

| 平台 | 状态 | 适配方式 | 文档 |
|---|---|---|---|
| **豆包 Doubao** | ✅ 原生支持 | SKILL.md + YAML frontmatter | 根目录 SKILL.md |
| **WorkBuddy** | ✅ 原生支持 + 飞书集成 | 原生技能 + 飞书生态 | [workbuddy/](workbuddy/) |
| **Coze 扣子** | ✅ 支持 | Bot System Prompt / 插件 | [coze/](coze/) |
| **ChatGPT / GPTs** | ✅ 支持 | Custom Instructions / GPTs | [chatgpt/](chatgpt/) |
| **Claude** | ✅ 支持 | Project Instructions | [claude/](claude/) |
| **通义千问** | ✅ 支持 | 智能体 System Prompt | [tongyi/](tongyi/) |
| **Dify** | ✅ 支持 | 应用系统提示词 / 工具 | [dify/](dify/) |

## 通用 System Prompt

所有平台共用一份 System Prompt，包含完整的 BEA 理论、工作流程和输出格式：

👉 **[universal-system-prompt.md](universal-system-prompt.md)**

将该文件内容粘贴到任意 AI 平台的 System Prompt / 人设 / 指令中即可使用。

## 两种使用模式

### 模式1：纯文本模式（推荐，零依赖）
- 不需要代码执行环境
- AI 按照 System Prompt 中的工作流程手动计算 W(T)
- 适用于所有 AI 平台
- W(T) 计算公式简单，AI 可直接计算

### 模式2：脚本增强模式（精确计算）
- 需要平台支持代码执行（如 ChatGPT Code Interpreter、Claude Artifacts、Dify 代码节点）
- 调用 `scripts/bea_quant.py` 进行精确计算
- 支持 10+ 种命令：report/suggest/generate/sensitivity/compare/multigroup/style-cycle
- 全量自测试全部通过

## 快速开始（30秒）

1. 复制 [universal-system-prompt.md](universal-system-prompt.md) 内容
2. 粘贴到你使用的 AI 平台的 System Prompt 中
3. 开始对话："帮我分析这个设计怎么样"

## 核心能力

- ✅ 美感分析（W(T)计算、范式定位、四维评分）
- ✅ 病症诊断（7种审美病症 + 元素级处方）
- ✅ 设计优化（给定目标，输出具体调整方案）
- ✅ 美感生成（给定目标范式，自动生成最优配置）
- ✅ 方案对比（多方案横向对比）
- ✅ 图片分析（上传设计图，自动识别元素并分析）

## 九大应用领域

消费电子/手机 · 汽车/交通工具 · 建筑/室内 · 品牌/平面 · UI/交互 · 服装/时尚 · 音乐/声音 · 影视/动画 · 公共/医疗空间

## 技术规格

- **版本**：v2.12.0
- **许可证**：CC BY-NC-SA 4.0
- **作者**：马星
- **离线可用**：是（纯文本模式零依赖）
- **Python 版本**：≥3.7（脚本模式）
- **外部依赖**：无（仅用 Python 标准库）
