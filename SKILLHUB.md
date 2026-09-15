# SkillHub 发布指南

本文档说明如何将 BEA 技能发布到 SkillHub 平台，以及如何确保同步上传成功。

## 快速发布

### 方式1：从 GitHub 导入（推荐）

1. 登录 [SkillHub](https://skillhub.cn/)
2. 完成实名认证
3. 绑定 GitHub 账号
4. 点击"发布 Skill" → "从 GitHub 导入"
5. 选择 `bipolar-emotion-aesthetics` 仓库
6. 填写信息：
   - **显示名称**：双极情绪美学 BEA
   - **版本号**：2.5.0
   - **描述**：见下方"描述模板"
7. 点击"发布"

### 方式2：本地上传

1. 打包技能目录为 zip 文件
2. 登录 SkillHub → "发布 Skill" → "本地上传"
3. 上传 zip 文件
4. 填写信息并发布

## 描述模板

### 标准版（详细描述）

```
双极情绪美学（Bipolar Emotion Aesthetics，BEA）——把审美判断从'我觉得'变成可讨论、可比较、可追踪、可生成的协作工具。

核心能力：
• W(T)危极权重计算算法
• 六范式风格定位系统
• 四维评分卡（张力/秩序/阈值/语境）
• 7种审美病症诊断与元素级改进处方
• 美感生成（给定目标范式自动生成最优配置）
• 灵敏度分析（找出最值得改的维度）
• 方案对比（多方案横向比较）
• 图片分析（上传图片自动识别元素极性）

覆盖九大领域：产品/手机、汽车/交通工具、建筑/室内、品牌/平面、UI/交互、服装/时尚、音乐/声音、影视/动画、公共空间。

纯 Python 标准库，离线可用，零依赖，多 AI 平台通用（豆包/Coze/ChatGPT/Claude/通义千问/Dify）。
```

### 简短版（短描述）

```
双极情绪美学（BEA）——把审美判断从'我觉得'变成可讨论、可比较、可追踪、可生成的协作工具。支持美感分析、诊断、优化和生成，覆盖九大设计领域。
```

## 文件格式兼容性

SkillHub 支持的文件格式：
- ✅ `.md` - Markdown 文档
- ✅ `.py` - Python 脚本
- ✅ `.txt` - 文本文件
- ✅ `.json` - JSON 配置文件
- ✅ `.html` - HTML 文件
- ✅ `.css` - CSS 文件
- ✅ `.js` - JavaScript 文件
- ✅ `.png`/`.jpg` - 图片文件
- ✅ `.sh` - Shell 脚本

SkillHub 不支持的文件格式（会被跳过）：
- ⚠️ `.gitignore` - Git 配置文件
- ⚠️ `LICENSE`（无扩展名）- 已重命名为 `LICENSE.md`
- ⚠️ `.docx` - Word 文档（已删除，Markdown 版本见 `docs/paper.md`）
- ⚠️ `.pdf` - PDF 文件（已删除）
- ⚠️ `.tex` - LaTeX 源文件（保留在 `arxiv/` 目录，可能被跳过）
- ⚠️ `.zip` - 压缩包（构建产物，已删除）

## 核心文件清单

发布时确保以下核心文件存在：

```
bipolar-emotion-aesthetics/
├── SKILL.md                    # 技能入口（必需）
├── manifest.json               # 元数据配置
├── README.md                   # 项目说明
├── QUICKSTART.md               # 快速上手
├── FAQ.md                      # 常见问题
├── CHANGELOG.md                # 版本变更日志
├── LICENSE.md                  # 许可证
├── assets/
│   └── bea-logo-mobius.png    # Logo 图标
├── references/                 # 理论文档
│   ├── 01-core-theory.md
│   ├── 02-workflow.md
│   ├── 03-dimension-guide.md
│   ├── 04-checklist.md
│   └── 05-case-studies.md
├── scripts/                    # Python 脚本
│   ├── bea_quant.py            # 量化引擎（核心）
│   ├── bea_guide.py            # 交互式引导
│   └── package.py              # 打包工具
├── platforms/                  # 多平台适配
│   ├── README.md
│   ├── universal-system-prompt.md
│   ├── coze/
│   ├── chatgpt/
│   ├── claude/
│   ├── tongyi/
│   └── dify/
├── templates/                  # 输出模板
│   ├── output-templates.md
│   └── review-record.md
├── docs/                       # 文档和网站
│   ├── index.html              # 官方网站
│   └── paper.md                # 学术论文（Markdown版）
└── arxiv/                      # 论文源码（可能被跳过）
    ├── bea_paper.tex
    ├── generate_docx.py
    └── generate_pdf.py
```

## 发布后检查清单

- [ ] SkillHub "我的 Skills" 页面显示 BEA 技能
- [ ] 审核状态为"已通过"或"审核中"
- [ ] 技能描述正确显示
- [ ] 核心文件（SKILL.md、scripts/、references/）已导入
- [ ] 可以在 WorkBuddy 中搜索到并安装
- [ ] 安装后可以正常调用（测试 `python3 scripts/bea_quant.py test`）

## 常见问题

### Q: 发布时提示"部分文件被跳过"怎么办？

A: 这是正常现象。SkillHub 会跳过不支持的文件格式（如 .gitignore、LICENSE、.docx、.pdf 等）。核心文件（SKILL.md、Python 脚本、Markdown 文档）都会成功导入，不影响技能使用。

### Q: 发布后在 WorkBuddy 中搜不到怎么办？

A: 
1. 等待审核通过（通常 1-3 个工作日）
2. 检查技能是否设置为公开
3. 尝试用不同关键词搜索（"双极情绪美学"、"BEA"、"美学分析"）
4. 检查 SkillHub "我的 Skills" 页面确认发布状态

### Q: 如何更新技能版本？

A:
1. 在 GitHub 上更新代码并提交
2. 在 SkillHub 中进入技能管理页面
3. 点击"更新"或"同步"按钮
4. 填写新版本号和更新说明
5. 提交更新

### Q: 技能审核需要多长时间？

A: SkillHub 采用三线并行安全审核流水线：
1. 内容合规过滤
2. 科恩实验室深度漏洞扫描
3. 云鼎实验室 AI 模型安全评估

通常需要 1-3 个工作日。审核结果会通过站内通知发送。

## 多平台同步

BEA 技能已适配多个 AI 平台，详见 `platforms/` 目录：

| 平台 | 状态 | 适配方式 |
|---|---|---|
| 豆包 Doubao | ✅ 已发布 | 原生 SKILL.md |
| Coze 扣子 | ✅ 已发布 | Bot System Prompt |
| SkillHub | 🔄 审核中 | 从 GitHub 导入 |
| ChatGPT / GPTs | ⏳ 待发布 | Custom Instructions |
| Claude | ⏳ 待发布 | Project Instructions |
| 通义千问 | ⏳ 待发布 | 智能体 System Prompt |
| Dify | ⏳ 待发布 | 应用系统提示词 |

## 联系方式

- **作者**：马星（星空本空）
- **GitHub**：https://github.com/Maxing0000/bipolar-emotion-aesthetics
- **官网**：https://maxing0000.github.io/bipolar-emotion-aesthetics/
- **许可证**：CC BY-NC-SA 4.0

---

*最后更新：2026-09-15*
