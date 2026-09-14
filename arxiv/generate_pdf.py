#!/usr/bin/env python3
"""Generate BEA paper as PDF using fpdf2 with Chinese font support."""

from fpdf import FPDF

FONT_REG = '/Library/Fonts/Arial Unicode.ttf'
FONT_BOLD = '/Library/Fonts/Arial Unicode.ttf'
FONT_SERIF = '/Library/Fonts/Arial Unicode.ttf'

class BEAPaper(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.add_font('Hei', '', FONT_REG)
        self.add_font('Hei', 'B', FONT_BOLD)
        self.add_font('Uni', '', FONT_SERIF)
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(25, 25, 25)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Hei', '', 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, '双极情绪美学（BEA）：一种可量化的协同设计评估框架', align='C')
            self.ln(4)
            self.set_draw_color(200, 200, 200)
            self.line(25, self.get_y(), 185, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Hei', '', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'- {self.page_no()} -', align='C')

    def title_text(self, text):
        self.set_font('Hei', 'B', 18)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 10, text, align='C')
        self.ln(3)

    def author_text(self, text):
        self.set_font('Hei', '', 12)
        self.cell(0, 7, text, align='C')
        self.ln(7)

    def date_text(self, text):
        self.set_font('Hei', '', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, text, align='C')
        self.ln(10)
        self.set_text_color(0, 0, 0)

    def h1(self, text):
        if self.get_y() > 230:
            self.add_page()
        self.ln(3)
        self.set_font('Hei', 'B', 13)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, text)
        self.ln(8)
        self.set_draw_color(0, 0, 0)
        self.line(25, self.get_y(), 185, self.get_y())
        self.ln(3)

    def h2(self, text):
        if self.get_y() > 240:
            self.add_page()
        self.ln(2)
        self.set_font('Hei', 'B', 11)
        self.cell(0, 7, text)
        self.ln(7)

    def body(self, text, indent=True):
        self.set_font('Hei', '', 10)
        self.set_text_color(30, 30, 30)
        if indent:
            x = self.get_x()
            self.set_x(x + 7)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def quote(self, text):
        self.ln(2)
        self.set_x(35)
        self.set_font('Hei', 'B', 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(140, 6, text, align='C')
        self.ln(2)
        self.set_text_color(30, 30, 30)

    def formula(self, text):
        self.ln(2)
        self.set_font('Uni', '', 11)
        self.cell(0, 7, text, align='C')
        self.ln(9)

    def bullet(self, label, text):
        self.set_font('Hei', 'B', 10)
        x = self.get_x()
        self.set_x(x + 5)
        self.cell(28, 5.5, label)
        self.set_font('Hei', '', 10)
        self.multi_cell(0, 5.5, text)
        self.ln(0.5)

    def table(self, headers, rows, caption=None, col_widths=None):
        if caption:
            self.ln(1)
            self.set_font('Hei', 'B', 9)
            self.cell(0, 5, caption, align='C')
            self.ln(5)
        if not col_widths:
            col_widths = [160 / len(headers)] * len(headers)
        # header
        self.set_font('Hei', 'B', 8.5)
        self.set_fill_color(230, 230, 230)
        self.set_draw_color(150, 150, 150)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, align='C', fill=True)
        self.ln()
        # rows
        self.set_font('Hei', '', 8.5)
        self.set_fill_color(255, 255, 255)
        for row in rows:
            # Check if row fits
            if self.get_y() > 250:
                self.add_page()
                # reprint header
                self.set_font('Hei', 'B', 8.5)
                self.set_fill_color(230, 230, 230)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, h, border=1, align='C', fill=True)
                self.ln()
                self.set_font('Hei', '', 8.5)
                self.set_fill_color(255, 255, 255)
            max_lines = 1
            for i, val in enumerate(row):
                lines = self.multi_cell(col_widths[i], 5, str(val), split_only=True)
                max_lines = max(max_lines, len(lines))
            row_h = max_lines * 5
            x_start = self.get_x()
            y_start = self.get_y()
            for i, val in enumerate(row):
                x = self.get_x()
                y = self.get_y()
                self.multi_cell(col_widths[i], 5, str(val), border=1, align='L')
                self.set_xy(x + col_widths[i], y)
            self.set_xy(x_start, y_start + row_h)
        self.ln(3)

    def ref(self, text):
        self.set_font('Uni', '', 8.5)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        self.set_x(x + 5)
        self.multi_cell(150, 4.5, text)
        self.ln(0.5)


pdf = BEAPaper()
pdf.add_page()

# ═══ TITLE ═══
pdf.title_text('双极情绪美学（BEA）：\n一种可量化的协同设计评估框架')
pdf.author_text('马星')
pdf.date_text('2026年9月')

# ═══ ABSTRACT ═══
pdf.h1('摘要')
pdf.body('设计评审中"我觉得不好看"式的主观判断无法被讨论、比较和追踪，导致设计决策效率低下且难以复用。本文提出双极情绪美学（Bipolar Emotion Aesthetics, BEA）框架，将审美判断从主观投票转化为可计算的工程过程。BEA 的核心命题为"美感即可控张力下的情绪奖赏"：亲极元素（圆润、柔色、对称）激活奖赏回路以安抚观者，危极元素（尖锐、强对比、坚硬）激活警觉回路以制造唤醒，二者在可认知秩序中组合且危极被约束于安全阈值内时，产生复合审美愉悦。框架定义了五个基本概念、六范式风格谱系、危极综合权重指数 W(T)、四维评分卡以及七类审美病症与对应处方，并实现了仅依赖 Python 标准库的离线量化引擎。通过消费电子、汽车、品牌视觉和建筑四个领域的九个案例验证，BEA 能够定位设计风格、诊断审美问题并给出元素级改进建议。本文同时讨论了框架的适用边界、局限性与未来方向。')
pdf.set_font('Hei', 'B', 10)
pdf.cell(15, 5.5, '关键词：')
pdf.set_font('Hei', '', 10)
pdf.multi_cell(0, 5.5, '设计评估；审美量化；情绪美学；协同设计；设计方法论；形式美')
pdf.ln(2)

# ═══ 1 引言 ═══
pdf.h1('1  引言')
pdf.body('在产品设计、品牌视觉和界面设计等领域，审美判断长期依赖个体经验与主观感受。设计评审会上，"我觉得不好看""这个感觉不对"之类的表述无法被反驳、无法被复现，也无法积累为组织知识。当团队成员对同一设计产生分歧时，争论往往停留在个人品味层面，而非可验证的形式特征层面。这一问题的根源在于：审美判断缺乏一套共享的描述语言和可操作的分析工具。')
pdf.body('现有美学理论从哲学[1,2]、心理学[3,4]和神经科学[5,6]等角度对审美体验做出了丰富解释，但多数理论停留在描述层面，难以直接指导设计实践。设计评估领域的量化尝试（如 Birkhoff 的审美度量公式[7]）因过于简化而未能获得广泛应用。工业界常用的语义差异法[9]和李克特量表虽可操作，但维度定义松散、评分标准不统一，结果难以跨项目比较。')
pdf.body('本文提出双极情绪美学（Bipolar Emotion Aesthetics, BEA）框架，旨在填补"审美理论"与"设计实践"之间的鸿沟。BEA 的核心思路是：将审美判断拆解为可标注的形式维度、可计算的综合指数和可诊断的问题类型，使团队能够围绕具体元素进行讨论，而非围绕个人品味进行投票。')
pdf.body('本文的主要贡献包括：（1）提出"美感=可控张力下的情绪奖赏"的核心命题及双极极性理论；（2）定义危极综合权重指数 W(T) 及六范式风格谱系，实现风格定位的可计算化；（3）构建四维评分卡与七类审美病症诊断体系，提供元素级改进处方；（4）实现开源量化引擎并通过多领域案例验证框架的可操作性。')

# ═══ 2 相关工作 ═══
pdf.h1('2  相关工作')
pdf.h2('2.1  美学理论基础')
pdf.body('BEA 的理论建构整合了多条思想脉络。伯克（Burke）对优美与崇高的区分[1]对应于亲极主导与危极主导两种审美体验；康德（Kant）的审美判断理论[2]强调审美愉悦的无功利性与普遍可传达性，为 BEA 的"协作刻度"理念提供了哲学基础。伯莱因（Berlyne）的唤醒理论[3]提出愉悦与唤醒呈倒 U 型关系，直接支撑了 BEA 的审美窗口概念——张力不足则乏味，张力过强则不适。')
pdf.body('格式塔心理学[4]为"秩序"概念提供了认知机制：大脑倾向于将分散元素组织为可理解的整体，混乱的对立只造成认知负担而非审美愉悦。神经美学研究[5,6]发现人类对对称、曲线和适度复杂度存在先天偏好，为极性方向的跨文化恒定性提供了生物学依据。进化论美学[11]则解释了亲/危极性的生存适应起源：安全信号趋近、威胁信号回避。')
pdf.body('信息论美学[12]将秩序等同于冗余、将新奇等同于信息增量，BEA 的双极配比可视为信息最优比的操作化表达。中国传统美学中的"刚柔相济""虚实相生"则提供了双极对立统一的东方表述[13]。布洛（Bullough）的"心理距离说"[14]为阈值概念提供了理论支撑：审美的前提是与对象保持适当心理距离，过近则功利、过远则冷漠。')

pdf.h2('2.2  设计评估方法')
pdf.body('在设计评估领域，Birkhoff[7]提出 M=O/C 的审美度量公式（秩序除以复杂度），开创了量化美学的先河，但因维度单一且忽略情绪因素而受到批评[8]。Eysenck[8]修正为 M=O×C，仍未脱离简化框架。Stamps[10]对环境美学中的神秘性、复杂度、可读性和连贯性进行了实证研究，验证了环境偏好的可预测性。')
pdf.body('在 HCI 领域，Tractinsky 等[15]发现"美的就是可用的"（What is beautiful is usable），Hassenzahl[16]区分了产品的享乐属性与实用属性，Norman[17]提出情感设计三层次理论（本能层、行为层、反思层）。这些研究证明了审美在产品体验中的重要性，但未提供可操作的设计评估工具。Leder 等[18]提出的审美欣赏模型涵盖了从知觉分析到审美判断的完整认知过程，为 BEA 的多维度评估提供了参考框架。')
pdf.body('Hekkert[19]提出设计美学的愉悦原则（最大效果、最优差异、安全威胁、对立统一），与 BEA 的双极张力理念高度契合。然而，上述工作多为理论模型或实证发现，缺乏面向设计团队的可操作工具。BEA 的定位正是将这些理论洞察转化为日常设计评审中可直接使用的方法论与工具。')

# ═══ 3 理论框架 ═══
pdf.h1('3  理论框架')
pdf.h2('3.1  核心命题')
pdf.quote('美感 = 可控张力下的情绪奖赏。')
pdf.body('这一命题包含三个要件。第一，张力：双极对立造成的情绪唤醒是美感的引力来源。纯亲极只有舒适没有吸引力，纯危极只有排斥没有愉悦。第二，可控：张力必须被秩序统摄、被阈值约束。混乱的对立造成认知负担，越界的唤醒变为真实不适。第三，情绪奖赏：当警觉系统的唤醒被奖赏系统"收编"，主体获得"被吸引（张力）+被安抚（安全）"并存的复合愉悦，这种体验比单纯舒适更强烈、更持久。')
pdf.body('操作总纲可概括为：以亲极安其心，以危极提其神，以秩序统其乱，以阈值守其界。')

pdf.h2('3.2  五个基本概念')
pdf.body('BEA 定义了五个相互关联的基本概念，构成框架的概念基础（表1）。')
pdf.table(
    ['概念', '含义', '操作意义'],
    [
        ['元素 Element', '可分辨的最小形式单位（一条线/一块色/一段质）', '分析的起点'],
        ['极性 Polarity', '元素先天的情绪方向（亲 P+/危 T−），连续可分级', '每个元素必标方向'],
        ['张力 Tension', '双极对立造成的情绪唤醒，美感的引力来源', '张力不足加对立，过强补秩序'],
        ['秩序 Order', '统摄元素关系的可认知结构（对称/比例/节奏/层级/呼应）', '消化张力的唯一手段'],
        ['阈值 Threshold', '危极由快感转为不适的临界，分本能/认知/文化三级', '越阈一票否决'],
    ],
    caption='表1  BEA 五个基本概念',
    col_widths=[28, 72, 60]
)

pdf.h2('3.3  双极极性与张力')
pdf.body('一切形式元素都在两极之间占据一个位置：')
pdf.bullet('亲极 P+：', '圆润、柔色、光滑、舒缓、对称、留白、稳定——激活奖赏回路，让人想接近。')
pdf.bullet('危极 T−：', '尖锐、强对比、坚硬、突变、失衡、拥挤、冷峻——激活警觉回路，制造唤醒与张力。')
pdf.body('极性的方向跨文化相对恒定（圆润≈安全，尖锐≈威胁，源于进化预置），但强度受文化经验调制。例如红色在生理层均为高唤醒，但中国文化中关联喜庆（趋亲），西方文化中偏警告（趋危）。所谓"翻转"几乎总是符号意义变亲而生理唤醒仍在，高明设计会顺势用秩序与语境安抚残留唤醒。')
pdf.body('单一极性不产生高级美感：纯亲极导致甜腻、平庸、廉价感；纯危极导致攻击、排斥、焦虑。双极在可认知秩序中组合，且危极被约束在安全阈值内，才产生复合愉悦。')

pdf.h2('3.4  秩序与阈值')
pdf.body('秩序是消化张力的唯一手段。当亲极与危极元素成对出现、被统一结构（对称、比例、节奏、层级、呼应）统摄时，对立不再造成混乱，而是转化为可欣赏的张力。秩序的核心是可预测性——大脑能预测元素关系时，唤醒被安全框架收编为快感。')
pdf.body('阈值是危极由快感转为不适的临界，分为三级：')
pdf.body('（1）本能安全阈（绝对红线，不可移动）：锋利到割伤联想、频闪眩晕、强对比刺眼疼痛。越过即从审美对象变为伤害源，一票否决。', indent=False)
pdf.body('（2）认知处理阈（相对，可右移）：混乱度/复杂度/失预测频率超过认知带宽即转焦虑。补秩序、建层级可右推；审美经验丰富者此阈更靠右。', indent=False)
pdf.body('（3）文化接受阈（相对，可移动）：元素在特定群体中被视为禁忌、廉价、不祥。理解语境、提供线索可移动。', indent=False)
pdf.body('审美窗口即三道门之间的区间。核心技艺是：在目标受众窗口内把张力推到尽可能靠右而不越界——越靠右越有力量、越难忘。')

# ═══ 4 方法论 ═══
pdf.h1('4  方法论')
pdf.h2('4.1  W(T) 危极综合权重')
pdf.body('BEA 的核心量化指标是危极综合权重指数 W(T)，衡量设计整体的"危极程度"：')
pdf.formula('W(T) = sum(wi * ti / 10),    sum(wi) = 1')
pdf.body('其中 wi 为第 i 个维度对该品类感受的权重，ti 属于 [0,10] 为该维度主导元素的危极强度。W(T) 落在 [0,1] 区间，对照六范式区间定位风格。')
pdf.body('t 值的校准标准如表2所示。打分遵循以下纪律：独立打分后汇总；分歧 ≥2 的维度必须讨论且说证据（"这个倒角半径是多少"）而非感觉；t 值反映"1米外的整体感受"而非像素级元素。')
pdf.table(
    ['t 值', '极性', '形状', '质感', '色彩'],
    [
        ['0–1', '强亲极', '全圆角、无直线', '硅胶、毛绒', '纯白、淡粉'],
        ['2–3', '偏亲', '圆润为主、少量直线', '磨砂、哑光', '低饱和暖色'],
        ['4–5', '中性', '方圆结合', '光滑塑料、普通金属', '中等饱和'],
        ['6–7', '偏危', '硬朗线条、少量圆角', '拉丝金属、高光', '高饱和冷色'],
        ['8–9', '强危极', '锐角、切面', '镜面金属、玻璃', '纯黑、荧光色'],
        ['10', '极危', '尖锐、破碎', '冰冷、粗糙', '强对比撞色'],
    ],
    caption='表2  t 值打分校准标准（以形状/质感/色彩维度为例）',
    col_widths=[16, 20, 42, 42, 40]
)
pdf.body('需要强调的是，W(T) 是协作刻度而非心理物理常数，误差带至少 ±0.1，不应纠结小数点。')

pdf.h2('4.2  六范式锚点')
pdf.body('以 W(T) 为横轴，所有风格排成连续谱，六个稳定锚点将风格谱系切分为可讨论的区间（表3）。区间边界是人为切分的协作刻度，不是自然规律——W(T)=0.47 与 0.49 没有本质区别。')
pdf.table(
    ['范式', 'W(T) 区间', '核心体验', '典型适用'],
    [
        ['治愈松弛', '<0.15', '放松舒展、无攻击性', '母婴、疗愈空间、医疗界面'],
        ['亲和精致', '0.15–0.30', '第一眼亲和、细看精密', '消费电子、高端日用品、主流品牌'],
        ['均衡典雅', '0.30–0.48', '刚柔各半、克制端庄', '经典主义、新中式、奢侈品经典线'],
        ['崇高震撼', '0.48–0.60', '先屏息敬畏、后沉浸沉醉', '大型公共建筑、豪华旗舰、史诗视觉'],
        ['冷峻克制', '0.60–0.66', '冷硬简为主、极少暖色维持人性', '极简主义、专业工具、德系工业设计'],
        ['先锋反叛', '0.66–0.85', '刺激反叛、临界于不适的痛快', '潮牌、亚文化、先锋艺术、概念设计'],
        ['逼近越阈', '≥0.85', '真实不适、非美区', '禁止——本能红线'],
    ],
    caption='表3  六范式风格谱系',
    col_widths=[24, 24, 56, 56]
)
pdf.body('均衡典雅不是"最好"，只是"最稳妥"。范式选择应匹配产品定位、目标受众阈值和使用场景，而非默认往中间挤。')

pdf.h2('4.3  四维评分卡')
pdf.body('BEA 采用四维评分卡对设计成熟度进行综合评估，满分 100 分，≥80 为成熟作品，任一维 <15 为明显短板必须回修（表4）。')
pdf.table(
    ['维度', '满分', '满分标准', '低分病症'],
    [
        ['双极张力', '25', '对立清晰成对、提神不攻击、匹配范式', '甜腻/攻击'],
        ['结构秩序', '25', '主辅分明、比例精当、层级一致、全局统一', '失序/割裂'],
        ['阈值安全', '25', '无本能红线、认知可消化、文化无禁忌', '越界/焦虑'],
        ['语境适配', '25', '匹配受众阈值、场景、功能风险、时代位置', '错位/过时'],
    ],
    caption='表4  四维评分卡',
    col_widths=[24, 14, 74, 48]
)
pdf.body('评分逻辑基于维度数据计算参考分：双极张力由 W(T) 区间、维度极差、明确对比和病症扣分构成；结构秩序由焦点数量（1–2 个最佳）、主辅清晰度和病症扣分构成；阈值安全由 W(T) 越界检查和极端值检查构成；语境适配为参考分，需人工结合受众、场景、竞品、时代和价格定位判断。')

pdf.h2('4.4  审美病症与处方')
pdf.body('BEA 定义了七类常见审美病症，每类有明确的识别特征和可执行的改进处方（表5）。其中失序症和层级冲突症无法仅通过维度值自动诊断，需人工检查。')
pdf.table(
    ['病症', '识别特征', '处方'],
    [
        ['甜腻症', 'W(T)<0.25，全维度 t≤4，无锐度', '高价值细节注入 10%–20% 危极，柔中藏骨'],
        ['攻击症', 'W(T)≥0.55，有维度 t≥6，令人紧张', '扩亲极基底，降危极到范式区间'],
        ['均分症', '所有维度集中 3–5，极差<2，无主次', '确立 ≥6:4 主辅比，第一印象明确'],
        ['失序症', '单元素精彩但堆一起打架（需人工判断）', '确立贯穿全局的统一主线（色板/模数/栅格）'],
        ['重点通胀症', '≥3 个维度 t≥6，视觉噪音大', '做减法，强调点压回 1–2 个'],
        ['张力不足症', 'W(T)<0.35，维度极差<2，温和无聊', '1–2 个维度提危极至 6+，制造对比'],
        ['层级冲突症', '宏观柔和却微观攻击（需人工判断）', '逐层逐通道审计，同向叠加或微差补偿'],
    ],
    caption='表5  审美病症—处方表',
    col_widths=[24, 64, 72]
)

pdf.h2('4.5  灵敏度分析')
pdf.body('为避免设计调整中的盲目试错，BEA 提供灵敏度分析功能：用有限差分法计算每个维度 t±1 后 W(T) 和四维评分的变化量，找出"改动哪个维度效果最明显"。')
pdf.body('W(T) 变化量满足 Delta*W(T) = wi/10（与当前 t 值无关，只要不在边界），因此高权重维度的调整效率最高。评分变化量通过实际重新计算四维评分获得，能发现"提升某维度会引入病症"的情况（如某维度 t+1 导致评分下降 7 分）。灵敏度分析与调整建议引擎配合使用：先看灵敏度找方向，再用 suggest 出完整方案。')

# ═══ 5 系统实现 ═══
pdf.h1('5  系统实现')
pdf.h2('5.1  量化引擎')
pdf.body('BEA 量化引擎以 Python 标准库实现（bea_quant.py），离线可用，提供八个子命令：analyze（分析并输出 JSON）、report（人类可读报告）、score（四维评分辅助）、suggest（调整建议）、sensitivity（灵敏度分析）、compare（两个产品对比）、batch（批量产品对比）、template（打分模板）。')
pdf.body('调整建议引擎采用贪心策略：降低危极时优先降当前 t 值最高的维度，提升危极时优先升当前 t 值最低的维度，同时考虑权重（t 值相近时优先调权重高的维度），避免调到极端值 0 或 10。引擎包含 50 项自测试，覆盖计算正确性、边界条件、格式解析和病症诊断。')

pdf.h2('5.2  品类维度与权重')
pdf.body('不同品类的"哪个维度最影响感受"不同，因此维度定义和权重因品类而异（表6）。权重可按项目调整，但调整时需说明理由。')
pdf.table(
    ['品类', '维度（权重）'],
    [
        ['手机', '形状(0.25) / 质感(0.25) / 色彩(0.15) / 构图(0.15) / 光影(0.10) / 细节(0.10)'],
        ['汽车', '曲面(0.30) / 特征线(0.25) / 灯组(0.15) / 比例(0.15) / 材质(0.15)'],
        ['品牌', '图形(0.25) / 色彩(0.25) / 字体(0.20) / 版式(0.20) / 质感(0.10)'],
        ['UI', '布局(0.25) / 色彩对比(0.20) / 组件形(0.20) / 动效(0.20) / 字体图标(0.15)'],
        ['建筑', '形体轮廓(0.30) / 立面线条(0.25) / 比例尺度(0.20) / 材质肌理(0.15) / 光影空间(0.10)'],
    ],
    caption='表6  各品类维度与权重',
    col_widths=[18, 142]
)
pdf.body('每个维度均配有具体的打分锚点（真实产品参考），例如手机形状维度：t=3 对应 iPhone 6–11 的圆润边框，t=5 对应 iPhone 12–15 的直角边框+圆角玻璃，t=6–7 对应 iPhone 4/5 的硬朗直线。锚点校准是团队统一刻度的关键。')

# ═══ 6 案例研究 ═══
pdf.h1('6  案例研究')
pdf.body('本节展示 BEA 在四个领域的应用案例。所有案例的 t 值由分析者基于公开产品信息独立打分后取共识值，W(T) 由量化引擎计算。')

pdf.h2('6.1  消费电子')
pdf.body('iPhone Duo（2026 折叠屏旗舰）：形状 t=3（圆润边角）、质感 t=6（镜面钛金属）、色彩 t=4、构图 t=3（对称居中）、光影 t=5、细节 t=6（精密铰链）。W(T)=0.44，定位均衡典雅偏上沿，接近崇高震撼。无自动诊断病症，但存在轻度重点通胀倾向——镜面钛、精密铰链、折叠大屏三个高端信号同时出现，缺少唯一视觉记忆锚点。改进方向包括增加中间调性配色、推出哑光钛版本（W(T) 降至 0.39）。')
pdf.body('Samsung Galaxy S26 Ultra（2026 直板旗舰）：形状 t=4、质感 t=4（喷砂铝+磨砂玻璃）、色彩 t=4、构图 t=3、光影 t=3、细节 t=5。W(T)=0.385，定位均衡典雅居中，诊断为均分症（所有维度集中 3–5，无主次）。这一代主动"去危极化"（钛换铝、直角改圆润、全机哑光），策略稳妥但旗舰视觉冲击力被稀释。处方为边框做高光倒角（质感 4→6，W(T) 升至 0.44），进入旗舰黄金区。')

pdf.h2('6.2  汽车设计')
pdf.body('Tesla Model 3：曲面 t=3、特征线 t=3、灯组 t=6（细长锐利大灯）、比例 t=5、材质 t=4。W(T)=0.39，均衡典雅偏亲和。灯组是唯一的危极元素，也是最具辨识度的设计符号——验证了"1 个精准的提神点胜过 3 个模糊的高端信号"。')
pdf.body('小米 SU7（2024 运动轿跑）：曲面 t=4、特征线 t=5、灯组 t=6、比例 t=5、材质 t=4。W(T)=0.47，均衡典雅最上沿，微调即进入崇高震撼。四维评分 90/100，设计成熟。灵敏度分析显示灯组 t-1 会扣 8 分，说明锐利灯组是核心记忆点，不能弱化。')
pdf.body('Tesla Cybertruck（2023 电动皮卡）：曲面 t=9、特征线 t=9、灯组 t=7、比例 t=7、材质 t=8。W(T)=0.825，先锋反叛最右端，接近越阈值（0.85）。诊断为攻击症+重点通胀症（5 个维度全部 t≥6），四维评分仅 60/100。这是 BEA 的完美边界案例：所有维度都是危极，完全没有亲极元素，验证了"纯危极不产生美感"的核心原则。但在特定语境下（科技展示、品牌差异化），其极端差异化策略具有商业合理性——说明 BEA 评分需结合语境适配综合判断。')

pdf.h2('6.3  品牌视觉')
pdf.body('苹果品牌视觉系统：图形 t=3（圆角几何 Logo）、色彩 t=3（白+灰为主）、字体 t=4（San Francisco 无衬线）、版式 t=2（大留白居中）、质感 t=4。W(T)=0.31，恰好踩在亲和精致与均衡典雅的分界线上。这不是巧合——苹果要的就是"第一眼亲和（让人想接近），细看精密（让人愿意付费）"。大留白版式（t=2）是最强亲极元素，产品图的精致光影（t=4）是提神点，主辅比约 7:3，非常清晰。')

pdf.h2('6.4  建筑')
pdf.body('中国尊（北京中信大厦，2018）：形体轮廓 t=5（礼器"尊"造型）、立面线条 t=6（竖向收分线条）、比例尺度 t=7（528 米超高层）、材质肌理 t=4（玻璃幕墙）、光影空间 t=5。W(T)=0.55，崇高震撼范式正中。四维评分 88/100，结构秩序满分。灵敏度分析显示形体轮廓和光影空间 t+1 都会扣 7 分，说明当前设计已在崇高范式的最佳平衡点——再激进就越界，再保守就失去地标性。')
pdf.body('建筑品类天然适合崇高震撼范式——大尺度和超高层本身制造敬畏感。与汽车品类不同，建筑的危极主要来自比例尺度而非锐利造型。中国尊的"尊"造型是中国传统文化符号的现代转译，是语境适配的优秀案例。')

pdf.h2('6.5  案例对比')
pdf.body('表7汇总了九个案例的核心指标。可以观察到：主流消费产品集中在均衡典雅范式（0.30–0.48），这是当前设计的"安全区"；Cybertruck 是唯一的极端边界案例；建筑品类天然偏向崇高震撼。')
pdf.table(
    ['产品', '品类', 'W(T)', '范式', '核心病症', '评分'],
    [
        ['iPhone Duo', '手机', '0.44', '均衡典雅', '轻度重点通胀', '—'],
        ['S26 Ultra', '手机', '0.385', '均衡典雅', '均分症', '—'],
        ['Model 3', '汽车', '0.39', '均衡典雅', '无', '—'],
        ['尊界 S800', '汽车', '0.455', '均衡典雅', '无', '91'],
        ['理想 L9', '汽车', '0.36', '均衡典雅', '缺少焦点', '83'],
        ['小米 SU7', '汽车', '0.47', '均衡典雅(近上沿)', '无', '90'],
        ['Cybertruck', '汽车', '0.825', '先锋反叛(近越阈)', '攻击+重点通胀', '60'],
        ['中国尊', '建筑', '0.55', '崇高震撼', '轻度攻击', '88'],
        ['苹果品牌', '品牌', '0.31', '亲和/典雅边界', '无', '—'],
    ],
    caption='表7  案例对比汇总',
    col_widths=[24, 14, 16, 36, 40, 14]
)

# ═══ 7 讨论 ═══
pdf.h1('7  讨论')
pdf.h2('7.1  局限性')
pdf.body('BEA 框架存在以下明确局限：')
pdf.body('第一，t 值打分仍含主观成分。尽管提供了锚点校准和打分纪律，不同分析者对同一维度的判断仍可能存在 ±1–2 的差异。BEA 通过独立打分+分歧讨论的流程来缓解，但无法完全消除。W(T) 的误差带至少 ±0.1，不应过度解读小数差异。', indent=False)
pdf.body('第二，维度权重为经验值。各品类的权重基于设计实践经验设定，未经大规模用户研究验证。权重可按项目调整，但调整理由需记录在案。未来可通过用户实验数据学习最优权重。', indent=False)
pdf.body('第三，仅覆盖形式美。BEA 不裁决内容美、道德美、思想美，不评估工程可行性和可用性，不替代用户测试。W(T) 高不等于用户喜欢——BEA 是设计团队内部的协作工具，不是用户偏好预测模型。', indent=False)
pdf.body('第四，不适用于先锋艺术评判。先锋艺术刻意越阈以制造冲击，BEA 的阈值安全维度会将其误判为问题。BEA 的适用边界是"需要讨论、比较、优化感官形式给人的情绪感受"的设计场景。', indent=False)
pdf.body('第五，部分病症需人工判断。失序症和层级冲突症无法仅通过维度值自动诊断，需要分析者检查宏观/微观一致性和跨通道极性一致性。', indent=False)

pdf.h2('7.2  边界条件')
pdf.body('BEA 的有效性依赖以下边界条件：（1）分析对象具有可辨识的形式元素（纯概念或纯功能对象不适用）；（2）目标受众的审美阈值可估计（完全陌生的文化群体需先做阈值调研）；（3）团队成员接受独立打分和证据讨论的纪律（若流于形式则退化为投票）；（4）设计目标已明确（范式选择需匹配定位，BEA 不替团队做战略决策）。')

pdf.h2('7.3  未来工作')
pdf.body('未来研究方向包括：（1）通过大规模用户实验验证 W(T) 与审美偏好的相关性，学习品类最优权重；（2）开发基于计算机视觉的自动 t 值标注，减少人工打分成本；（3）扩展更多品类（家具、服装、食品包装、空间设计等）；（4）将 BEA 与生成式设计工具集成，实现范式约束下的自动设计探索；（5）开展纵向研究，追踪设计风格钟摆随时代语境的迁移规律。')

# ═══ 8 结论 ═══
pdf.h1('8  结论')
pdf.body('本文提出了双极情绪美学（BEA）框架，将审美判断从主观投票转化为可计算、可讨论、可追踪的协同过程。框架以"美感=可控张力下的情绪奖赏"为核心命题，通过双极极性理论、W(T) 危极综合权重、六范式谱系、四维评分卡和病症诊断体系，为设计团队提供了一套完整的审美评估与改进工具。九个跨领域案例验证了框架的可操作性：BEA 能够定位设计风格、诊断审美问题、给出元素级改进处方，并帮助团队将争论从"你懂不懂审美"转向"这个圆角到底是亲极 2 还是 3"——前者无解，后者有解。')
pdf.body('BEA 不宣称存在唯一正确的美，也不替代用户测试和工程评估。它的定位是审美协作的基础设施——让美感成为可以被讨论、比较和积累的组织知识，而非只能被投票的个人品味。')

# ═══ 参考文献 ═══
pdf.h1('参考文献')
refs = [
    '[1] Burke E. A Philosophical Enquiry into the Origin of Our Ideas of the Sublime and Beautiful[M]. London: R. and J. Dodsley, 1757.',
    '[2] Kant I. Critique of Judgment[M]. Trans. W.S. Pluhar. Indianapolis: Hackett, 1790/1987.',
    '[3] Berlyne D E. Aesthetics and Psychobiology[M]. New York: Appleton-Century-Crofts, 1971.',
    '[4] Arnheim R. Art and Visual Perception: A Psychology of the Creative Eye[M]. Berkeley: University of California Press, 1954.',
    '[5] Zeki S. Inner Vision: An Exploration of Art and the Brain[M]. Oxford: Oxford University Press, 1999.',
    '[6] Ramachandran V S, Hirstein W. The science of art: A neurological theory of aesthetic experience[J]. Journal of Consciousness Studies, 1999, 6(6-7): 15-51.',
    '[7] Birkhoff G D. Aesthetic Measure[M]. Cambridge: Harvard University Press, 1933.',
    '[8] Eysenck H J. The empirical determination of an aesthetic formula[J]. Psychological Review, 1941, 48(1): 82-92.',
    '[9] Osgood C E, Suci G J, Tannenbaum P H. The Measurement of Meaning[M]. Urbana: University of Illinois Press, 1957.',
    '[10] Stamps A E. Mystery, complexity, legibility and coherence[J]. Environment and Behavior, 2000, 32(6): 784-805.',
    '[11] Etcoff N. Survival of the Prettiest: The Science of Beauty[M]. New York: Anchor, 2000.',
    '[12] Moles A. Information Theory and Esthetic Perception[M]. Urbana: University of Illinois Press, 1966.',
    '[13] 李泽厚. 美的历程[M]. 北京: 生活·读书·新知三联书店, 2009.',
    '[14] Bullough E. "Physical distance" as a factor in art and an aesthetic principle[J]. British Journal of Psychology, 1912, 5(2): 87-118.',
    '[15] Tractinsky N, Katz A S, Ikar D. What is beautiful is usable[J]. Interacting with Computers, 2000, 13(2): 127-145.',
    '[16] Hassenzahl M. The interplay of beauty, goodness, and usability in interactive products[J]. Human-Computer Interaction, 2004, 19(4): 319-349.',
    '[17] Norman D A. Emotional Design: Why We Love (or Hate) Everyday Things[M]. New York: Basic Books, 2004.',
    '[18] Leder H, Belke B, Oeberst A, et al. A model of aesthetic appreciation and aesthetic judgments[J]. British Journal of Psychology, 2004, 95(4): 489-508.',
    '[19] Hekkert P. Design aesthetics: Principles of pleasure in design[J]. Psychological Science, 2006, 48(3): 157-175.',
    '[20] Palmer S E, Schloss K B, Sammartino J. Visual aesthetics and human preference[J]. Annual Review of Psychology, 2013, 64: 77-107.',
    '[21] Bloch P H. Seeking the ideal form: Product design and consumer response[J]. Journal of Marketing, 1995, 59(3): 16-29.',
    '[22] Veryzer R W. Aesthetic response and the influence of design principles on product preference[C]//Advances in Consumer Research, 1993, 20: 224-228.',
    '[23] Martindale C. The pleasures of thought: A theory of cognitive hedonics[C]//Advances in Consumer Research, 1984, 11: 51-58.',
    '[24] Locher P J. The nature of the artistic experience[M]//Keyes C L, Haidt J (Eds.). Flourishing: Positive Psychology and the Life Well-Lived. Washington, DC: APA, 2003: 121-138.',
]
for ref in refs:
    pdf.ref(ref)

# ═══ Save ═══
output = '/Users/m/Documents/BEA/arxiv/BEA_双极情绪美学_论文.pdf'
pdf.output(output)
print(f'Saved: {output}')
print(f'Pages: {pdf.page_no()}')
