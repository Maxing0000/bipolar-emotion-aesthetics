# AI 生图社区传播包 · 「审美控制语法」

> 用途：把 BEA 提示词语法包装成生图社区能直接拿走用的东西。
> 核心洞察：生图社区第一大痛点是「为什么我的图总差点意思」——他们找的不是美学理论，是「图不好看怎么办」。BEA 恰好是答案。
> 使用方式：以下帖子模板可直接发布，按平台调性微调。发布后把链接回填到本文底部「已发布记录」。

---

## 帖子一：小红书 / 即刻（痛点切入型）

**标题**：AI 画图总「差点意思」？问题可能出在张力配比上

**正文**：

同一个 prompt，别人的图高级耐看，你的图甜腻平庸——差的不是模型，是**元素极性配比**。

分享一套我在用的「审美控制语法」（开源，免费）：

🎯 核心公式：美感 = 可控张力下的情绪奖赏

每张图里的元素都分两极：
- 亲极（安全）：圆润、低饱和、柔光、留白 → 让人放松
- 危极（张力）：锐利、高饱和、强对比、压迫感 → 把人抓住

**全柔则腻，全锐则戾。** 好图都是「柔中藏骨」。

📐 直接能抄的配比锚点：
- 治愈系 90:10（绘本、睡前场景）
- 精致感 80:20（产品图、生活方式）
- 高级感 60:40（海报、封面）← 大部分「高级感」图在这
- 震撼感 45:55（主视觉、大片）

✍️ 用法：在 prompt 里显式写出两极元素，例如——

❌ 「宋代美学风格的静物，高级感」（玄学祈祷）
✅ 「汝窑天青瓶（圆润·柔光·大面积留白）+ 瘦金体梅枝（锐利折线）+ 朱红印章（小面积强对比），三色板严格限定天青/墨黑/朱红，黄金构图」

第二版把「高级感」拆成了：亲极基底 60% + 危极提神 40% + 色板纪律——模型想跑偏都难。

🔗 完整语法表（范式 × 维度 × 强度档 → prompt 模板）在 GitHub 开源，搜「双极情绪美学 BEA」，还有在线计算器可以拖滑块看你的图落在哪个范式。

#AI绘画 #即梦 #midjourney #prompt分享 #审美提升

---

## 帖子二：ComfyUI / Stable Diffusion 社区（技术型）

**标题**：A controllable vocabulary for "aesthetic quality" in prompts (open source)

**正文**：

Tired of prompt lottery? "masterpiece, best quality, 8k" does nothing because it carries no structural information.

BEA (Bipolar Emotion Aesthetics) gives you a **controllable grammar**: every visual element sits on a bipolar axis (safe-approach ↔ threat-arousal), and aesthetic pleasure = tension within order. Instead of praying with quality tags, you specify:

1. **Archetype anchor** (tension budget): Healing 90:10 / Refined 80:20 / Balanced 60:40 / Sublime 45:55 / Cold 38:62 / Avant-garde 30:70
2. **Element-level polarity assignment**: which elements carry the threat share (e.g. "sharp calligraphic branch lines" as the single T-element in a soft Song-style still life)
3. **Order constraints**: palette discipline (≤3 colors), golden-ratio composition, motif repetition

Example diff:

```
- Song dynasty aesthetic still life, masterpiece, best quality
+ Song-style still life: celadon vase (soft curves, diffused light, large negative space) as P-base;
  sharp "slender-gold" calligraphic plum branch as the single T-accent; one small vermillion seal;
  strict 3-color palette (celadon/ink/vermillion); rule-of-thirds composition; 60:40 P:T ratio
```

Full mapping tables (archetype × dimension × intensity → prompt phrases) + an interactive W(T) calculator: github.com/Maxing0000/bipolar-emotion-aesthetics (CC BY 4.0)

---

## 帖子三：知乎（案例论证型）

**标题**：为什么你的 AI 图「说不出哪里错，但记不住」？——一个可计算的审美框架

**正文骨架**：
1. 开篇：两张图对比（同主题，一张平庸一张高级），差异到底在哪
2. 提出：美感不是玄学，是「可控张力下的情绪奖赏」；神经机制=奖赏回路与警觉回路同时激活
3. 工具：双极谱系表 + W(T) 公式 + 六大范式区间（≤0.15 治愈 / 0.15–0.30 精致 / 0.30–0.48 典雅 / 0.48–0.60 崇高 / 0.60–0.66 冷峻 / 0.66–0.85 先锋）
4. 案例：用框架解释 iPhone 17 Pro 为什么「设计圈叫最大胆、热搜骂最丑」（W(T) 0.285→0.475，单代冲出手机品类窗口）
5. 落地：生图提示词语法 + 在线计算器 + Agent 技能，全部开源
6. 结尾：仓库链接 + 欢迎提交盲评实验数据（见 docs/experiment-protocol.md）

---

## 发布清单（建议顺序）

| 顺序 | 平台 | 模板 | 备注 |
|---|---|---|---|
| 1 | 小红书 | 帖子一 | 配两张对照图（腻 vs 柔中藏骨） |
| 2 | 即刻 | 帖子一精简版 | 一句话钩子 + 链接 |
| 3 | Reddit r/StableDiffusion / ComfyUI 社区 | 帖子二 | 英文，强调 open source + calculator |
| 4 | 知乎 | 帖子三 | 长文，配 iPhone 案例 |

## 已发布记录

（发布后回填：日期 / 平台 / 链接 / 阅读量 / 评论要点——评论里的质疑是 FAQ 与盲评实验的最好素材）
