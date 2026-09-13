# 双极情绪美学 · Bipolar Emotion Aesthetics（BEA）

![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)
![Version](https://img.shields.io/badge/version-1.13.0-blue)
[![PyPI](https://img.shields.io/pypi/v/bea-mcp)](https://pypi.org/project/bea-mcp/)
[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.33684490-blue)](https://doi.org/10.6084/m9.figshare.33684490)
![Type](https://img.shields.io/badge/type-Agent%20Skill-success)
![Stack](https://img.shields.io/badge/stack-Markdown%20%2B%20Python-orange)

> 一套**可解释、可计算、可执行**的形式美学方法 / A computable framework for formal aesthetics.
> **核心命题：美感 = 可控张力下的情绪奖赏（Aesthetic pleasure = emotional reward under controlled tension）。**
>
> 🧮 [W(T) 交互计算器](https://maxing0000.github.io/bipolar-emotion-aesthetics/)　｜　🖼️ [图片分析（上传生成报告）](https://maxing0000.github.io/bipolar-emotion-aesthetics/image-analysis.html)　｜　⚡ [快速诊断（3步出结果）](https://maxing0000.github.io/bipolar-emotion-aesthetics/quick-diagnosis.html)　｜　🎯 [审美测试（测你的偏好）](https://maxing0000.github.io/bipolar-emotion-aesthetics/aesthetic-test.html)　｜　🔧 [完整诊断工作台](https://maxing0000.github.io/bipolar-emotion-aesthetics/workbench.html)　｜　📚 [案例库（14个经典分析）](https://maxing0000.github.io/bipolar-emotion-aesthetics/cases.html)　｜　📖 [完整在线理论著作](https://maxing0000.github.io/bipolar-emotion-aesthetics/theory-book.html)　｜　🌐 [English](https://maxing0000.github.io/bipolar-emotion-aesthetics/index_en.html)　｜　📚 [中英术语表](GLOSSARY.md)　｜　❓ [常见质疑 FAQ](FAQ.md)

![BEA 双极封面](docs/cover.png)

圆润让人想靠近，尖锐让人警觉——BEA 认为，任何感官对象的「美感」都来自两类情绪元素在**秩序**之内的恰当组合：让人安全趋近的**亲极（P+）**与让人警觉唤醒的**危极（T−）**。当危极被控制在阈值之内、与亲极形成张力却不越界时，人就获得美感；一旦越界则转为恐惧、攻击、杂乱或不适。

本仓库是 BEA 的**可运行技能（Agent Skill）**：把这套方法论封装为 `SKILL.md + references`，让任意支持技能机制的 AI Agent 获得专业的形式审美分析、设计创作与问题诊断能力。

---

## 它能做什么

| 任务类型 | 输入 | 输出 |
| --- | --- | --- |
| **A 分析 / 评价** | 一个设计对象（描述或图片） | 双极拆解、范式定位、W(T) 危极指数、BEA 评分卡、好/坏的机制解释 |
| **B 创作 / 设计** | 目标气质 + 对象类型 + 语境 | 元素级设计方案、亲:危配比、形态/配色/材质/节奏的具体变量 |
| **C 诊断 / 调优** |「廉价感 / 甜腻 / 杂乱 / 攻击性 / 不耐看」等问题 | 病灶定位（越阈/失衡/失序/错配）+ 对应处方与修改清单 |
| **D 讲解 / 科普** |「给我讲讲 BEA / 这套理论」 | 固定叙事链（命题→机制→四象限→范式谱→六步法）+ 图示化讲解 |

## 30 秒看懂它怎么工作

> 问：这款手机大圆角、柔色磨砂，看着舒服却「不精致、有点甜腻」，怎么改？

BEA 不会回答「更大气一点」，而是给出元素级、可复算的结论：

1. **定性**：落入「低张力·高秩序」的呆板平庸区，主病症＝甜腻症（亲极过载），整体危极权重 W(T)≈0.175，对「精致旗舰」目标偏低；
2. **宏观不动**：整机曲面、亲肤磨砂、柔色主基调保持亲极，守住长期耐看与握持舒适；
3. **细节提神（约 20% 危极集中到凑近看、反复摸处）**：中框加一圈高亮精密倒角、镜头模组内部做锐利同心切面、侧键收出利落小棱线、字体笔画收紧一档；
4. **立序**：所有圆角统一到一套模数（机身 R / 模组 0.5R / 按键 0.15R），一条特征线从中框贯穿到镜头；
5. **复算**：调整后 W(T)≈0.29，处「亲和精致」上沿、距 0.85 越阈线很远；评分由 76 升到 **88（成熟）**，远观仍亲和、近看见精密——即「柔中藏骨」。

完整填好的示范见技能内 `bipolar-emotion-aesthetics/references/audit-templates.md` 附录；不想装任何东西的话，直接用[网页版 W(T) 交互计算器](https://maxing0000.github.io/bipolar-emotion-aesthetics/)拖滑块体验。

---

## 🚀 普通人快速入门（5分钟上手）

**不需要学理论，3个工具就能用起来：**

### 1️⃣ 先测测你的审美偏好（2分钟）
👉 [BEA 审美测试](https://maxing0000.github.io/bipolar-emotion-aesthetics/aesthetic-test.html)
- 10道选择题，凭第一感觉选
- 测出你的审美类型（温柔治愈者/精致平衡者/张力追求者/先锋探索者）
- 推荐最适合你的设计范式

### 2️⃣ 快速诊断一个设计（3分钟）
👉 [BEA 快速诊断](https://maxing0000.github.io/bipolar-emotion-aesthetics/quick-diagnosis.html)
- 第1步：选品类（手机/汽车/服装/建筑...）
- 第2步：选你想要的感觉（治愈/精致/均衡/崇高/冷峻/先锋）
- 第3步：拖3个滑块，描述这个设计给你的感觉
- 自动生成：BEA评分、范式定位、匹配度、改进建议

### 3️⃣ 看案例学审美（随时看）
👉 [BEA 案例库](https://maxing0000.github.io/bipolar-emotion-aesthetics/cases.html)（14个经典产品深度分析）
- iPhone 17 Pro、尊界 S800、小米 SU7、特斯拉 Model S、戴森 V15
- 无印良品、奔驰 S 级、Cybertruck、索尼 XM5、Vision Pro
- 乐高、宜家、原神
- 按范式/品类/评分筛选，看经典设计为什么好看/不好看

### 💡 日常使用场景
- **买东西**：用快速诊断分析产品，判断值不值得买
- **装修**：用审美测试找到自己喜欢的风格，用案例库找参考
- **穿搭**：用范式定位找到适合自己的风格，避免踩雷
- **做PPT/海报**：用 BEA 框架检查设计，避免"甜腻"或"杂乱"
- **看电影/听音乐**：用 BEA 理解为什么有些作品"高级"，有些"俗"

### 🎓 想深入学习？
- [完整在线理论著作](https://maxing0000.github.io/bipolar-emotion-aesthetics/theory-book.html) — 系统学习 BEA 理论
- [10分钟读懂 BEA](https://maxing0000.github.io/bipolar-emotion-aesthetics/guide.html) — 着陆页，快速了解核心概念
- [完整诊断工作台](https://maxing0000.github.io/bipolar-emotion-aesthetics/workbench.html) — 专业版，8品类+自然语言+A-B对比+历史记录

---

## 理论速览

- **双极谱系**：亲极 P+（圆润、柔色、光滑、舒缓、对称、闭合、低对比……带来安全与趋近）；危极 T−（尖锐、强对比、坚硬、突变、倾斜、破碎、高饱和……带来警觉与唤醒）。
- **六个范式锚点（四大核心 + 两种过渡，亲:危）**：治愈松弛 90:10、亲和精致 80:20、均衡典雅 60:40（过渡）、崇高震撼 45:55（均高强度）、冷峻克制 38:62（过渡）、先锋反叛 30:70。
- **危极指数 W(T)=Σ wᵢ·(tᵢ/10)**：量化对象整体危极强度，对照范式目标区间判断是否越阈（>0.85 逼近越阈）；权重按品类给定（手持电子 / 汽车 / 平面 / 界面）。
- **三级阈值**：本能安全阈（红线，一票否决）/ 认知处理阈（可由秩序右推）/ 文化接受阈（随语境移动）。美感发生在「审美窗口」内。
- **BEA 评分卡**：双极张力、结构秩序、阈值安全、语境适配，四维各 25 分；≥80 为成熟，任一维 <15 须回修。
- **语境调制与极性翻转**：文化、时代、受众、品类会移动阈值；符号层极性可翻转，生理唤醒层难以翻转。

## 目录结构

```
bipolar-emotion-aesthetics/                 # ← 开源仓库根目录
├── README.md / README_EN.md / LICENSE / FAQ.md   # 中文说明 / 英文说明 / 许可 / 常见质疑回应
├── GLOSSARY.md                             # 中英术语表（全文统一译名，25+ 核心术语）
├── CONTRIBUTING.md                         # 🤝 贡献指南（如何参与/案例贡献模板/提交规范）
├── API.md                                  # 🔌 BEA API 规范（24个接口/计算/分析/诊断/设计/数据）
├── release.sh                              # 三平台一键发版脚本（GitHub/Gitee/ModelScope）
├── datasets/                               # 📊 结构化数据集（API/数据分析/机器学习基础）
│   ├── cases.json                          # 17个案例完整结构化数据（范式/W(T)/评分/特征）
│   └── paradigms.json                      # 8个范式锚点结构化定义（区间/配比/核心/典型领域）
├── .github/                                # GitHub 社区配置
│   ├── ISSUE_TEMPLATE/                     # Issue 模板（Bug/功能建议/案例请求/文档问题）
│   └── PULL_REQUEST_TEMPLATE.md            # PR 模板（类型/变更/测试/检查清单）
├── docs/
│   ├── cover.png                           # 封面
│   ├── guide.html                          # ★ 10 分钟读懂 BEA（着陆页，传播入口）
│   ├── index.html                          # 网页版 W(T) 交互计算器（分享链接/案例复现/导出报告/三步引导）
│   ├── theory-book.html                    # ★ 完整在线理论著作（由 build_book.py 从 references 生成）
│   ├── boundary.md                         # 模型边界与合规声明
│   ├── promotion.md                        # 传播物料包（三档中英文案 + 18 自媒体选题 + 发布渠道）
│   ├── ai-art-community-kit.md             # AI 生图社区传播包（审美控制语法的帖子模板）
│   └── experiment-protocol.md              # 盲评实验协议（BEA 预测 vs 用户投票，实证众包）
├── mcp-server/                           # MCP Server：bea_wt_calc / bea_wt_compare / bea_prescribe / bea_scoresheet 五工具（pip 可装）
├── tools/
│   └── diagnostic-workbench/
│       ├── index.html                      # ★ BEA 交互式诊断工作台（8品类/自然语言解析/历史记录/A-B对比雷达图/导出图片/AI智能分析提示词）
│       ├── quick-diagnosis.html            # ⚡ BEA 快速诊断（3步出结果，普通人零门槛）
│       └── aesthetic-test.html             # 🎯 BEA 审美测试（10道题测审美偏好+范式推荐）
├── cases/                                  # ★ 案例库（14个经典产品BEA深度分析，含索引页+筛选+搜索）
│   ├── index.html                          # 案例库索引页（按范式/品类/评分筛选+关键词搜索+范式分布统计）
│   ├── 01-iphone17-pro.html               # 崇高震撼下沿，W(T)=0.48，86分，微差补偿教科书
│   ├── 02-尊界S800-BEA分析.md               # 均衡典雅，W(T)=0.53，88分，大面柔+灯组锐
│   ├── 03-小米SU7-BEA分析.md              # 冷峻克制，W(T)=0.65，84分，静态暗示运动
│   ├── 04-特斯拉ModelS-BEA分析.md         # 崇高震撼，W(T)=0.55，85分，极简崇高代表
│   ├── 05-戴森V15-BEA分析.md              # 冷峻克制，W(T)=0.62，83分，科技冷峻代表
│   ├── 06-无印良品-BEA分析.md              # 亲和精致，W(T)=0.25，87分，柔中藏骨典范
│   ├── 07-奔驰S级-BEA分析.md              # 均衡典雅，W(T)=0.50，89分，外威内温巅峰
│   ├── 08-Cybertruck-BEA分析.md           # 先锋反叛，W(T)=0.75，78分，越阈边缘实验
│   ├── 09-索尼WH1000XM5-BEA分析.md        # 冷峻克制，W(T)=0.60，84分，专业工具美学
│   ├── 10-苹果VisionPro-BEA分析.md         # 崇高震撼，W(T)=0.52，87分，未来设备标杆
│   ├── 11-乐高LEGO-BEA分析.md              # 亲和精致，W(T)=0.22，88分，快乐精密教科书
│   ├── 12-宜家IKEA-BEA分析.md              # 均衡典雅，W(T)=0.38，87分，大众设计标杆
│   └── 13-原神Genshin-BEA分析.md           # 跨范式叙事，W(T)=0.45，89分，游戏美学巅峰
├── arxiv/
│   └── bea-position-paper.md               # 英文学术论文草稿（position paper）
├── ci/                                     # 内容体检：算式复算 / 链接有效性 / 中英混杂
├── tests/                                  # 工具链单元测试
├── templates/
│   └── bea-scorecard-templates.md          # 5 套可复制模板（基调卡/审计表/W(T)计算/评分卡/18项审计清单）
├── references/
│   └── academic-references.md              # BEA 整合的 12 项公共学术来源与原创增量声明
└── bipolar-emotion-aesthetics/             # ← 技能本体：把此文件夹放进 Agent 的 skills 目录
    ├── SKILL.md                            # 主入口：触发描述 + 核心模型 + 四类工作流（A/B/C/D）
    ├── references/
    │   ├── theory.md                       # 本体/机制/双极谱系（含关系/间隔维度）/结构法则/三级阈值
    │   ├── paradigms.md                    # 范式连续谱、六锚点、语境调制、极性翻转
    │   ├── method.md                       # 六步法、W(T) 计算、疲劳函数、BEA 评分卡
    │   ├── playbooks.md                    # 九大领域配方（含手机/汽车）+ 病症诊断处方
    │   ├── audit-templates.md              # 8 套可复制模板（含文化符号审计表）+ A/C 双示范
    │   └── bea-prompts.md                  # 提示词语法：范式×维度×强度档 → 生图提示词
    ├── scripts/
    │   ├── wt_calc.py                      # W(T) 计算器：范式落点/极性画像/A/B 对比（仅标准库，离线）
    │   ├── scoresheet.py                   # BEA 评分卡：四维打分/短板定位/修复映射
    │   └── build_book.py                   # 由 references 生成在线理论著作（单一事实源）
    ├── anchors/                            # 0–10 强度锚定图卡（形状/明度/色彩）与对卡流程
    └── cases/                              # 案例库（7 个）：M9 / 华为 / 宋式生图 / iPhone 17 Pro / 手机·LOGO·海报三个标准化示范
```

## 安装

**一行命令（macOS / Linux）**：

```bash
git clone --depth 1 https://github.com/Maxing0000/bipolar-emotion-aesthetics && cp -r bipolar-emotion-aesthetics/bipolar-emotion-aesthetics <你的技能目录>/
```

**各平台 30 秒接入**：

| 平台 | 步骤 |
|---|---|
| WorkBuddy / CodeBuddy | 技能目录为 `~/.workbuddy/skills/`，复制后新会话自动触发 |
| 扣子（Coze） | 技能已公开上架，直接搜索「双极情绪美学」添加 |
| 豆包 | 复制 `bipolar-emotion-aesthetics/SKILL.md` 全文到自定义技能/指令 |
| 其他 Agent | 任何支持 skills 目录的 Agent：把内层文件夹放进去即可 |

**不想装任何东西**：直接用[网页版 W(T) 交互计算器](https://maxing0000.github.io/bipolar-emotion-aesthetics/)拖滑块体验，或先看 [10 分钟读懂 BEA](https://maxing0000.github.io/bipolar-emotion-aesthetics/guide.html)。

**近零依赖**：核心为纯 Markdown 方法论，离线可用；`bipolar-emotion-aesthetics/scripts/` 下的 wt_calc.py 与 scoresheet.py 为可选计算辅助——仅用 Python 标准库、不联网、不调用外部 API、不读取或上传任何数据，无它们时全部流程仍可手工执行。

## 快速开始（触发示例）

- 「用双极情绪美学分析这款手机为什么显得高级 / 廉价。」
- 「按『亲和精致 80:20』给我一套智能手表外形设计方向，要元素级参数。」
- 「这张海报看着又甜又腻、不耐看，诊断一下并给出修改清单。」
- 「帮我定一个新能源 SUV 的形态气质：既要科技锋利感又要家用亲和，怎么配比？」
- 「这个 App 界面红色警示和圆角卡片混在一起很违和，做一次跨模态一致性审计。」
- 「给我讲讲双极情绪美学这套理论。」

## 适用领域

产品 / 工业设计（手机、消费电子、汽车与交通工具）、建筑与室内、品牌与平面视觉、Logo / 字体 / 海报、UI 与交互、服装时尚、声音与音乐、影视镜头、装置与雕塑等一切以感官形式呈现的对象。

## 能力边界（它不做什么）

- 只评判**形式美**（形 / 色 / 质 / 空间 / 光影 / 声 / 动态及其组合），不裁决内容美、道德美、思想美；
- 0–10 强度与 W(T) 是统一团队沟通的**协作刻度**，不是心理物理常数，不宣称存在唯一正确的美，也不滑向「美纯主观」；
- 不替代工程可行性、产品安全、医学、无障碍（Accessibility）等专业评估；涉及真实安全红线时以专业规范为准。

## 安全与合规说明

- 核心内容为静态 Markdown 方法论文档；唯一的可执行文件 `bipolar-emotion-aesthetics/scripts/wt_calc.py` 为纯标准库离线计算器，**无二进制程序、无网络请求、无数据采集、无第三方依赖**；
- 素材不涉及任何个人信息、真实用户数据或受版权限制的第三方内容；
- 采用宽松的 CC BY 4.0 协议，允许自由使用与商用，仅需署名。

## 在线版本 / Online Reading

本仓库提供两个互补的在线页面，部署到 GitHub Pages 后即可访问（Settings → Pages → Source 选 `main` 分支 `/docs` 目录）：

| 页面 | 地址 | 用途 |
| --- | --- | --- |
| 🧮 W(T) 交互计算器 | `https://maxing0000.github.io/bipolar-emotion-aesthetics/index.html`（首页） | 拖滑块实时计算危极权重、范式落点、极性画像、四象限定位；附 iPhone 17 Pro / 尊界 S800 等快捷示例 |
| 📖 完整在线理论著作 | `https://maxing0000.github.io/bipolar-emotion-aesthetics/theory-book.html` | 十一编完整体系（本体→机制→元素→结构→阈值→范式→语境→方法→应用→诊断→评价）+ 体系图 SVG / 六范式卡 / 诊断表 / 术语表 / FAQ，暖橙冷蓝双极配色，响应式适配移动端 |

两页互相链接：计算器页脚有「完整在线理论著作」入口，著作内有计算器引用。

## MCP Server（AI 客户端直连）

`mcp-server/` 把 BEA 计算工具封装为标准 MCP 服务——Claude Desktop、Cursor、WorkBuddy 等任何 MCP 客户端装上后，AI 可直接调用九个工具：`bea_list_categories`（品类权重表）、`bea_wt_calc`（W(T) 与范式落点）、`bea_wt_compare`（A/B 方案裁决）、`bea_prescribe`（诊断处方：维度调整方案与具体手法）、`bea_scoresheet`（评分卡与短板修复）、`bea_scoring_rubric`（视觉评分标尺）、`bea_diagnose_image`（图像诊断：传入产品图片，AI 看图打分并自动完成 W(T)+处方全流程）、`bea_diagnose_compare`（双图对比诊断：两张图分别打分后裁决）、`bea_report`（一键诊断报告：打分+W(T)+处方+评分卡合成完整 Markdown）。

```bash
pip install bea-mcp   # PyPI 一键安装：https://pypi.org/project/bea-mcp/
```

客户端配置（Claude Desktop / Cursor / WorkBuddy 同格式）：

```json
{
  "mcpServers": {
    "bea-aesthetics": { "command": "python3", "args": ["-m", "bea_mcp.server"] }
  }
}
```

详见 `mcp-server/README.md`。数据表与 CLI 脚本 CI 强制同步（`tests/test_mcp_sync.py`）。

## 多平台获取

| 平台 | 用途 | 地址 |
| --- | --- | --- |
| GitHub（国际主仓） | 源码 / Issue / Release | https://github.com/Maxing0000/bipolar-emotion-aesthetics |
| Gitee 码云（国内镜像） | 国内快速克隆 | https://gitee.com/maxing0000/bipolar-emotion-aesthetics |
| ModelScope 魔搭（国内数据集） | 国内下载 / 数据集形态 | https://www.modelscope.cn/datasets/xkbk0000/bipolar-emotion-aesthetics |
| 扣子 Coze（在线技能） | 一键添加使用 | 技能商店搜索「双极情绪美学」（公开上架审核中） |

三处开源仓库内容一致，任选其一获取；后续以 GitHub 为主仓更新、Gitee 与 ModelScope 同步。

## 如何引用

文本署名 / 引用请注明：

> 星空本空.《双极情绪美学 Bipolar Emotion Aesthetics(BEA)：可计算的形式美学技能》v1.13.0, 2026. CC BY 4.0. DOI: [10.6084/m9.figshare.33684490](https://doi.org/10.6084/m9.figshare.33684490).

BibTeX：

```bibtex
@misc{bea2026,
  title  = {双极情绪美学 Bipolar Emotion Aesthetics (BEA)：可计算的形式美学技能},
  author = {星空本空},
  year   = {2026},
  version= {1.9.0},
  doi    = {10.6084/m9.figshare.33684490},
  url    = {https://github.com/Maxing0000/bipolar-emotion-aesthetics},
  license= {CC BY 4.0}
}
```

## 更新日志

### v1.13.0（2026-09-13）— 范式体系重大突破

- **范式动态演化理论**：范式从"静态锚点"进化为"时间轴上的动态曲线"，提出六段式范式叙事结构（引入→发展→高潮→转折→收束→余韵），静态作品也存在"虚拟时间轴"（观看顺序与注意力流动）
- **范式叠加嵌套理论**：高级作品是多层范式叠加的"和弦"，三层模型（宏观0.5+中观0.3+微观0.2），四种和弦类型（同向叠加/微差补偿/对立碰撞/渐变过渡）
- **新增2个过渡范式**（8个锚点）：🌫️ 诗意朦胧范式（W(T)=0.35，模糊/暗示/留白，危极是"不确定"而非"尖锐"）、🌑 神秘魅惑范式（W(T)=0.66，未知/诱惑/禁忌，亲极是"诱惑"而非"安全"）
- **范式转换机制**：四种转换手法（渐变/突变/叠加/延迟），黄金分割点（61.8%）转换效果最强
- **新增 paradigm-dynamics.md**：完整范式突破理论文档（技能 references）
- **理论著作更新**：第二编新增第7节"范式突破"，含全部理论细节
- **首页范式突破展示模块**：8范式可视化连续谱+四大理论突破卡片
- **案例库新范式筛选**：诗意朦胧、神秘魅惑按钮
- **知识测验扩容**：15→18题，新增3道范式突破专项题

### v1.12.0（2026-09-13）— 内容丰富与体验优化

- **新增3个跨领域案例**（案例库达17个）：安藤忠雄·光之教堂（建筑/崇高震撼94分）、Apple iOS界面设计（UI/亲和精致94分）、Supreme潮牌设计（时尚/先锋反叛91分），覆盖9大领域
- **图片分析工具增强**：新增5个预设示例按钮（iPhone/尊界S800/光之教堂/iOS/Supreme），一键体验完整分析流程
- **新增BEA知识测验页面**：15道选择题覆盖BEA核心概念，即时反馈+详细解释+成绩评价+分享功能
- **链接中文化为英文**：16个案例HTML文件改为英文名，所有链接无中文，SEO与跨平台兼容性提升
- **全方位SEO优化**：sitemap.xml更新至28个URL，10个页面添加JSON-LD结构化数据，自定义404页面
- **可访问性优化**：12个页面导航栏添加aria-label，移动端菜单添加aria-expanded，主要内容区域添加role="main"

### v1.11.0（2026-09-13）— 首页大改版与SEO

- **首页大改版**：新增核心数据展示（14案例/10工具/6范式/3平台）、3步快速上手引导、精选案例展示、社交媒体分享（微信/微博/Twitter/复制链接）、为什么选择BEA四大优势
- **SEO优化**：新增sitemap.xml（24个URL）、robots.txt，案例库新增"随机探索"按钮
- **案例库HTML化**：14个案例从.md转换为独立.html页面，套用BEA统一样式，站内相对路径访问，国内可直接打开
- **全方位链接修复**：README版本号、导航栏、案例路径等全面修复

### v1.10.0（2026-09-13）

- **BEA 交互式诊断工作台上线**（`https://maxing0000.github.io/bipolar-emotion-aesthetics/workbench.html`）：零门槛网页工具——8大品类（手持消费电子/汽车/平面品牌/数字界面/建筑室内/时尚服装/音乐声音/影视动画）、6维度极性滑块、四维评分卡、范式定位+W(T)实时计算、张力×秩序四象限、问题诊断+改进处方、Markdown报告导出
- **诊断工作台五大进阶功能**：①自然语言智能解析（"圆润一点，颜色暖一点"→自动调维度，支持增量调整+6快捷标签+解析结果可视化）②历史记录（localStorage保存/回看/导出/删除，最多50条）③A-B对比分析（双方案参数对比+雷达图+四维评分对比+自动生成对比结论）④导出图片（一键生成高清PNG报告）⑤AI智能分析（上传图片生成完整BEA分析提示词，复制给任意AI助手获得标准化报告）
- **案例库建设完成**（`cases/`，8个经典产品BEA深度分析）：iPhone 17 Pro（崇高震撼86分）、尊界S800（均衡典雅88分）、小米SU7（冷峻克制84分）、特斯拉Model S（崇高震撼85分）、戴森V15（冷峻克制83分）、无印良品（亲和精致87分）、奔驰S级（均衡典雅89分）、Cybertruck（先锋反叛78分）；含案例库索引页（按范式/品类/评分三维筛选+关键词搜索+范式分布统计）
- **README 导航升级**：顶部新增诊断工作台和案例库入口，目录结构补充 tools/ 和 cases/ 完整说明

### v1.9.1（2026-09-13）

- **范式区间全仓库统一**：修复从 v1.6 延续的 P0 问题——代码（wt_calc/MCP）用区间上界（0.15/0.30/0.48/0.60/0.66/0.85），文档（method.md/论文/SKILL/HTML）用中心点（0.1/0.2/0.4/0.55/0.62/0.7），导致同一 W(T) 值代码与文档判定范式不同。统一为区间定义，同步修改 method.md、ArXiv 论文、MCP bea_list_categories 输出、bea_prescribe docstring、计算器 index.html、在线著作 theory-book.html、社区工具包共 7 处
- **修复 paradigms.md 旧表述**：第 10 行「四大范式...四选一」改为「四大核心范式与两种过渡范式（共六个锚点）...六选一」
- **SKILL.md 版本升级**：v1.9.0 → v1.9.1，updated 日期更新为 2026-09-13

### v1.9.0（2026-09-13）

- 能力层收官：bea_diagnose_compare 双图对比诊断 + bea_report 一键 Markdown 诊断报告（bea-mcp 1.3.0，九工具）


### v1.8.1（2026-09-13）
- **盲评实验包落地**：`docs/experiment.html`（开箱即用的盲评收集页：随机顺序、匿名背景、双指标 1-7 分、localStorage 累计、JSON 导出）+ `scripts/analyze_experiment.py`（自动均值/分组峰值/判定规则/Issue 模板生成）——实测验证从「协议文档」变「30 分钟可跑的工具链」；新增 3 项分析测试（累计 19 项），全流程无头浏览器回归零报错

### v1.8.0（2026-09-13）
- **图像诊断上线**（bea-mcp 1.2.0）：新增 `bea_scoring_rubric`（21 维度视觉评分标尺：观察点 + t=2/5/8 锚点描述）与 `bea_diagnose_image`（传入产品图片，AI 对照标尺看图打分，自动完成 W(T) + 处方全流程）——BEA 从「手动估分」进入「拍张照就出诊断报告」
- CLI 同步：新增 `scripts/rubric.py`（标尺单一事实源）；RUBRICS 纳入 test_mcp_sync 防漂移（5 项）；新增 3 项标尺单元测试（累计 16 项）；stdio 协议级冒烟验证 text+image 双内容序列化正常

### v1.7.3（2026-09-13）
- **永久 DOI 落地**：Figshare 归档完成，DOI [10.6084/m9.figshare.33684490](https://doi.org/10.6084/m9.figshare.33684490)——README 新增 DOI 徽章，BibTeX 引用补 doi 字段，学术引用身份完整

### v1.7.2（2026-09-13）
- **全代码 debug 轮**（bea-mcp 1.1.1）：修复中文逗号静默吞维度的解析 bug（wt_calc / scoresheet 均受影响）；非数字输入从英文 traceback 改为中文友好报错；新增 2 项回归测试（累计 13 项）；三个网页无头浏览器运行时回归零报错；build_book 幂等性验证通过

### v1.7.1（2026-09-13）
- **修复计算器 P0 故障**：补回丢失的引导弹窗/toast DOM 元素——JS 引用空元素中断初始化，导致滑块与预设自 v1.4.0 起完全不渲染（已用无头浏览器回归验证：22 预设、6 滑块、处方面板全正常）

### v1.7.0（2026-09-13）
- **网页计算器升级「主流产品诊断」**：22 个一键载入预设——主流手机（iPhone 16/17 Pro、华为 Mate、小米 15、Nothing Phone）、主流汽车（尊界 S800、小米 SU7、Model 3、理想 L9、保时捷 911、仰望 U9）、品牌/UI（苹果视觉、小米新 LOGO、iOS、特斯拉车机）+ 教学案例分组
- **计算器内置诊断处方**：填目标 W(T) 自动输出维度调整方案与具体手法（与 `bea_prescribe` 同算法同手法表），导出审计报告含处方全文

### v1.6.0（2026-09-13）
- **新增诊断处方工具 bea_prescribe**（bea-mcp 1.1.0）：输入现状与目标 W(T)，按权重杠杆自动给出「先动哪个维度、调几档、用什么具体手法」——内置 20 个维度 × 加锐/减锐双向手法表；BEA 从「计算器」升级为「顾问」
- CLI 同步：`wt_calc.py --prescribe` 同款处方；`DIM_MOVES` 手法表纳入 test_mcp_sync 防漂移；新增 4 项处方单元测试（累计 11 项全过）

### v1.5.2（2026-09-13）
- **PyPI 正式上线**：`pip install bea-mcp` 全球可装（https://pypi.org/project/bea-mcp/），安装命令从 git 直装切换为 PyPI，新增 PyPI 版本徽章

### v1.5.1（2026-09-13）
- 仓库卫生修复：移除误入版本控制的 `__pycache__/*.pyc`，`.gitignore` 补全 Python 构建产物规则

### v1.5.0（2026-09-13）
- 新增 **MCP Server**（`mcp-server/`）：bea_list_categories / bea_wt_calc / bea_wt_compare / bea_scoresheet 四工具，pip 一键安装，Claude Desktop / Cursor / WorkBuddy 等 MCP 客户端直连
- 新增 `tests/test_mcp_sync.py`：MCP 与 CLI 脚本数据表一致性 CI 校验


### v1.4.0（2026-09-13）

- **wt_calc.py A/B 对比**：`--compare` 双方案对照——输出双画像、差异维度与目标接近度裁决，覆盖「两个方案选哪个」的决策场景；
- **新增 scoresheet.py**：BEA 评分卡脚本化——四维打分、短板自动定位、修复指引自动映射回六步法环节；
- **CI 内容体检**（GitHub Actions）：案例算式自动复算（防数字漂移）、本地链接有效性（防幻影文件）、英文文件中英混杂检测、工具链单元测试——AI 生成内容入库前过机器门；
- **网页计算器四增强**：分享链接（配置编码进 URL，每次分析自带传播）、案例复现扩充至 10 个、Markdown 审计报告一键导出、三步上手引导；
- **新增 https://maxing0000.github.io/bipolar-emotion-aesthetics/guide.html**：「10 分钟读懂 BEA」着陆页——核心命题/双极谱系/四象限/六范式/真实案例/三入口；
- **安装说明升级**：一行命令 + 各平台 30 秒接入表；
- **新增 docs/ai-art-community-kit.md**：AI 生图社区传播包（「审美控制语法」帖子模板）；
- **新增 docs/experiment-protocol.md**：盲评实验协议——任何人可跑「BEA 预测 vs 用户投票」对照并提交数据；
- **新增 arxiv/bea-position-paper.md**：英文学术论文草稿；
- **单一事实源**：theory-book.html 改由 build_book.py 从 references/*.md 生成，理论正文只改一处。

### v1.3.0（2026-09-13）

- **质量修复（审查豆包合并批次后）**：
  - 案例算式纪律修复：手机案例删除「有效张力」黑箱，改为诚实的「初版 0.375 超阈 → 回调至 0.29」迭代示范；LOGO 案例修正品牌权重（图形 0.25/字体 0.20）与维度内混合计分（0.31，亲和精致上沿）；海报案例补混合取值说明；
  - README_EN 目录结构重写：删除幻影文件 `docs/theory-full.md`、修正 index.html 标注、全英文化；
  - 理论著作与计算器补齐双向互链；字体外链更换为 Google Fonts；
- **结构收敛**：根目录 `cases/` 三个示范案例并入技能内案例库（共 7 个，单一日录）；双 FAQ 合并为根目录 FAQ.md（13 问）；`templates/BEA评分卡模板.md`、`references/学术参考文献.md` 更名为英文文件名；
- **术语表补「有效张力」词条**：定性概念，计算一律以 W(T) 为准。

### v1.2.0（2026-09-12）

- **新增 FAQ.md**：十问十答，直面「美怎么能量化」「与设计心理学何异」「W(T) 权重凭什么」「事后解释何来预测力」等最强质疑；
- **新增网页版 W(T) 交互计算器**（https://maxing0000.github.io/bipolar-emotion-aesthetics/index.html，GitHub Pages 在线）：品类选择、维度滑块、实时 W(T) 与范式落点、极性画像、四象限定位、目标区间对照，附 iPhone 17 Pro / 尊界 S800 等快捷示例；
- **新增 release.sh 三平台一键发版脚本**：版本号替换、更新日志生成、GitHub 提交/标签/Release、Gitee 直推、ModelScope SDK 同步，一条命令完成。
- **新增完整在线理论著作**（`https://maxing0000.github.io/bipolar-emotion-aesthetics/theory-book.html`，十一编 50KB+）：本体→机制→元素→结构→阈值→范式→语境→方法→应用→诊断→评价，含体系总图 SVG、六范式配比卡、美感地图四象限、BEA 评分卡、病症处方表、术语表、FAQ，暖橙冷蓝双极配色，scrollspy 导航，响应式；
- **新增 README_EN.md** 英文精简介绍（面向海外设计师）；
- **新增 GLOSSARY.md** 中英术语表（25+ 核心术语统一译名）；
- **新增 docs/boundary.md** 模型边界与合规声明（适用范围/量化性质/原创性声明/数据隐私/安全承诺）；
- **新增 docs/faq.md** 中英双语常见问题（8 问）；
- **新增 docs/promotion.md** 传播物料包（三档中英文案 + 18 个自媒体选题 + 可复用素材清单 + 发布渠道建议）；
- **新增 templates/BEA评分卡模板.md** 5 套可复制模板（基调卡/极性审计表/W(T)计算表/评分卡/18 项审计清单）；
- **新增 cases/** 三个标准化示范案例（手机甜腻症 / 心理咨询LOGO微差补偿 / 电子音乐节海报崇高范式，均含完整 W(T) 计算与 BEA 评分）；
- **新增 references/学术参考文献.md** BEA 整合的 12 项公共学术来源（伯克/康德/泽基/LeDoux/格式塔/进化论/信息论/中国阴阳等）与原创增量声明；
- **SKILL.md 补强**：安全合规前置段落、双模式说明（诊断模式/创作模式）、仓库附加资源导航、版本标注。

### v1.1.1（2026-09-12）

- **新增案例：iPhone 17 Pro 外观分析（A 类 + 轻诊断）**——横向相机台地争议的 BEA 完整解释：两代对比 W(T) 0.285 → 0.475，单代 +0.19 冲出手机品类窗口，机制化解「史上最丑」与「最大胆设计」并存的舆论两极；
- **方法补强：「右缘策略」**——校阈节新增注记：辨识度/记忆点优先的产品（换代款、社交属性品）可有计算地把张力推到目标受众窗口的**右缘而非窗外**，短期争议与长期辨识度同时最大化（源自 iPhone 案例反哺，是案例库第一次实证回溯修订 reference）。

### v1.1.0（2026-09-12）

- **新增 D 类「讲解 / 科普」工作流**：固定叙事链 + 图示序列，理论传播场景开箱即用；
- **新增第六维度「关系/间隔」**：疏朗呼吸（亲）↔ 近距压迫（危），谱系、审计表同步扩展——对阴阳美学「虚实相生」的元素级承接；
- **新增 `scripts/wt_calc.py`**：W(T) 与极性画像计算器（四大品类权重内置，支持自定义权重与目标区间对照）；首跑即纠正一处手工加权误差，实证计算脚本化价值；
- **新增 `references/bea-prompts.md`**：BEA 提示词语法——范式 × 维度 × 强度档到生图提示词的映射模板与词汇库，理论直通 AI 生成工作流；
- **新增 `anchors/` 锚定图卡**：形状 / 明度 / 色彩三维度 0–10 档位参考图与对卡流程，解决评分刻度跨会话漂移；
- **新增 `cases/` 案例库**：尊界 S800 外观诊断（C 类）、华为旗舰档次提升（B 类）、宋式美学图像生成（B 类 + 生图）三个已验证完整案例；
- **模板扩充**：新增模板 8 文化符号审计表（生理层/符号层分栏），A 类完整示范补齐；
- **方法补强**：耐看性升级为「疲劳函数」（首次愉悦 × 衰减率）检查项；远观测试可执行化；感知边界声明（音频/触觉结论标注协作推断）；
- **入口完善**：触发描述补负面边界（不裁决内容美/道德美，不做可用性/工程评估）；范式表数据源标注以 paradigms.md 为准。

### v1.0.0（2026-09-12）

- 首次发布：核心命题、五概念、三公理、美感生成机制、双极谱系、四结构法则、三级阈值、六范式连续谱、六步创作法、四维评分卡、九大领域配方、7 套模板。

## 许可证

本作品采用 [**知识共享署名 4.0 国际许可协议（CC BY 4.0）**](LICENSE) 授权。

你可以自由地共享、复制、传播，以及 remix / 二次创作，包括商业用途，唯一需要做的是**署名**：注明出自「双极情绪美学 BEA（bipolar-emotion-aesthetics），作者：星空本空」，并在衍生时说明改动。

© 2026 星空本空（bipolar-emotion-aesthetics）
