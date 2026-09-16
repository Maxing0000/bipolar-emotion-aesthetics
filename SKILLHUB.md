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
   - **版本号**：2.14.0（与 `manifest.json` 的 `version` 字段保持一致）
   - **描述**：见下方"描述模板"
7. 点击"发布"

### 方式2：本地上传（网页端）

1. 生成上传包：`python3 scripts/package.py --skillhub`（会先跑一次平台规范校验）
2. 上传 `dist/bea-v2.14.0-skillhub.zip`——压缩包**根目录直接包含 `SKILL.md`**，符合官方"确认根目录包含 SKILL.md"的要求
3. 登录 SkillHub → "发布 Skill" → 本地上传 ZIP 包（或直接选技能文件夹）
4. 在网页表单里填写 Slug、显示名称、图标与描述后发布

> Slug 填 `bipolar-emotion-aesthetics`（与既有发布保持一致，才能更新而不是新建；Slug 提交后不可修改）。
> `bea-v2.14.0-full.zip` 内容与 skillhub 包相同，二者择一即可。

**关于二进制文件**：SkillHub **禁止上传二进制文件**（png/jpg/pdf 等），包内若含此类文件，平台会提示"部分文件被跳过"。因此打包清单**不含 `assets/` 下的 logo 图标**——图标在网页端"编辑头像"处单独上传。`package.py` 预检会拦截二进制文件，命中直接报错退出。

### 方式3：CLI 发布（适合频繁迭代）

```bash
# 1. 安装 CLI（首次）
curl -fsSL https://skillhub.cn/install/install.sh | bash -s -- --cli-only

# 2. 登录（Token 从「个人中心 → API keys」创建，只显示一次）
skillhub login --key <你的Token> --host https://api.skillhub.cn

# 3. 本地预检（不真正发布，几秒出结果）
skillhub publish /Users/m/Documents/BEA --host https://api.skillhub.cn --dry-run

# 4. 正式发布
skillhub publish /Users/m/Documents/BEA --host https://api.skillhub.cn --changelog "v2.14.0 文档与打包规范优化"
```

### 方式4：Agent 自然对话发布（WorkBuddy 可直接用）

SkillHub 官方支持在接入的 Agent 客户端里用自然语言发布，支持的 Agent 包括 **WorkBuddy**、Claude Code、Codex 等。

在 WorkBuddy 对话里直接说：

```
根据 https://skillhub.cn/ai/release.md 把 /Users/m/Documents/BEA 发布到 SkillHub
```

Agent 会在后台调用同一套 CLI，完成预检、提交发布，并反馈结果。

## 平台规范要求（官方 release.md 摘要）

### SKILL.md frontmatter

| 字段 | 要求 | 本项目取值 |
|---|---|---|
| `slug` | **必填**，kebab-case，长度 2–128，全网唯一 | `bipolar-emotion-aesthetics` |
| `displayName` | **必填**，对外展示名称 | `双极情绪美学 BEA` |
| `version` | **必填**，合法 SemVer | `2.14.0` |
| `summary` / `description` / `tags` / `license` / `homepage` | 建议填写（不阻断发布） | 均已填 |

> 缺 `slug` / `displayName` / `version` 任一，发布会被阻断。`python3 scripts/package.py --check` 已内置该校验。

### 上传包限制

| 项目 | 官方要求 | 本项目现状 |
|---|---|---|
| 必备文件 | 包内必须包含 `SKILL.md` | ✅ 根目录直接包含 |
| 单次上传体积 | ≤ 10.00 MB | ✅ 0.46 MB |
| 文件数量 | 建议 ≤ 200 个 | ✅ 30 个 |
| slug 命名 | 仅小写字母、数字、连字符 | ✅ 合规 |

### 审核与评测

平台采用 TRACE 五维评测：Trust（可信任度，**红线维度**，触碰安全红线直接淘汰）、Reliability、Adaptability、Convention、Effectiveness。

本项目对应情况：
- **Trust**：纯 Python 标准库、无网络请求、无外部依赖、包内无任何密钥或内网地址（`manifest.json` 已声明 `offline_capable: true` / `network_required: false`）
- **Convention**：SKILL.md 结构清晰、含使用示例与限制说明，符合"渐进式披露"

审核通常 1–3 个工作日。

### 图标

CLI / Agent 发布**不会自动上传头像**，未提供 `iconUrl` 时会用默认占位图。需要在网页端"我的 Skill"里单独上传图标（本仓库 `assets/bea-logo-skillhub.png`）。

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
• 图片分析（上传图片按9步标准流程分析，同图打分差异 ≤1 档）
• 轻量级快速诊断（只出 W(T)+范式+主辅比，适合快速筛选）

覆盖九大领域：产品/手机、汽车/交通工具、建筑/室内、品牌/平面、UI/交互、服装/时尚、音乐/声音、影视/动画、公共空间。

纯 Python 标准库，离线可用，零依赖，多 AI 平台通用（豆包/WorkBuddy/Coze/ChatGPT/Claude/通义千问/Dify）。
```

### 简短版（短描述）

```
双极情绪美学（BEA）——把审美判断从'我觉得'变成可讨论、可比较、可追踪、可生成的协作工具。支持美感分析、诊断、优化和生成，覆盖九大设计领域。
```

### 一句话版（列表页用）

```
用 W(T) 权重 + 六范式 + 四维评分，把"这个设计好不好看"变成可计算的元素级改进方案。
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
- ⚠️ `.zip` - 压缩包（`dist/` 为本地构建产物，上传时会被跳过）

> 注意：`install.sh` / `install.ps1` / `uninstall.sh` / `update.sh` 等本地安装脚本已从仓库移除，安装统一走技能市场或手动 `git clone`，文档中不再出现相关命令。

## 核心文件清单

发布时确保以下核心文件存在（`python3 scripts/package.py --check` 可一键校验）：

```
bipolar-emotion-aesthetics/
├── SKILL.md                    # 技能入口（必需）
├── manifest.json               # 元数据配置（版本号单一来源）
├── README.md                   # 项目说明
├── QUICKSTART.md               # 快速上手
├── FAQ.md                      # 常见问题
├── CHANGELOG.md                # 版本变更日志
├── LICENSE.md                  # 许可证
├── assets/                     # Logo 等品牌素材
│   ├── bea-logo-skillhub.png
│   └── bea-logo-skillhub.jpg
├── references/                 # 理论文档
│   ├── 01-core-theory.md
│   ├── 02-workflow.md
│   ├── 03-dimension-guide.md
│   ├── 04-checklist.md
│   ├── 05-case-studies.md
│   └── 06-image-anchors.md
├── scripts/                    # Python 脚本
│   ├── bea_quant.py            # 量化引擎（核心）
│   ├── bea_guide.py            # 交互式引导
│   └── package.py              # 打包工具（含打包前预检）
├── platforms/                  # 多平台适配
│   ├── README.md
│   ├── universal-system-prompt.md
│   ├── workbuddy/
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
│   ├── case-library.html       # 案例库 Web 应用
│   ├── image-analyzer.html     # 图片分析助手
│   └── paper.md                # 学术论文（Markdown 版）
└── arxiv/                      # 论文生成脚本（可能被跳过）
    ├── generate_docx.py
    └── generate_pdf.py
```

## 上传前自检

```bash
python3 scripts/package.py --check      # 打包清单预检：确认清单内文件全部存在
python3 scripts/bea_quant.py test       # 全量自测，确认量化引擎无回归
python3 scripts/package.py --all        # 生成 dist/ 下的各平台上传包
python3 scripts/package.py --skillhub   # 追加生成 SkillHub 本地上传包
```

## 发布后检查清单

- [ ] SkillHub "我的 Skills" 页面显示 BEA 技能
- [ ] 审核状态为"已通过"或"审核中"
- [ ] 技能描述正确显示，版本号与 `manifest.json` 一致
- [ ] 图标已上传（CLI / Agent 发布不会自动带头像，需在网页端补传）
- [ ] 核心文件（SKILL.md、scripts/、references/）已导入
- [ ] 上传前已跑 `python3 scripts/package.py --check`（清单预检）与 `python3 scripts/bea_quant.py test`（全量自测）
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
| SkillHub | ✅ 已发布（v2.6.1，待同步 v2.14.0） | 从 GitHub 导入 |
| WorkBuddy | ✅ 已发布 | 原生技能 + 多模态图片分析 |
| Coze 扣子 | ✅ 已发布 | Bot System Prompt |
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
