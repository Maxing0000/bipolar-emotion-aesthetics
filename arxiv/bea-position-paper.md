# BEA: A Computable Framework for Formal Aesthetics

**Status:** Position paper draft (for arXiv:cs.HC submission)
**Author:** Xingkong Benkong (independent researcher)
**License:** CC BY 4.0
**Repository:** https://github.com/Maxing0000/bipolar-emotion-aesthetics

---

## Abstract

Aesthetic judgment of designed objects remains largely informal: practitioners rely on intuition, and disagreements reduce to taste. We present **Bipolar Emotion Aesthetics (BEA)**, a framework that treats formal beauty as *emotional reward under controllable tension*. Every sensory element is assigned a position on a bipolar axis between safety-approach (P) and threat-arousal (T); aesthetic pleasure arises when both neural pathways are co-activated within an order structure that metabolizes the tension. BEA operationalizes this account as (i) an element-level polarity taxonomy across six dimensions, (ii) a weighted threat index W(T) with category-specific weights, (iii) six archetype anchors on a continuous tension spectrum, and (iv) a standardized six-step workflow with audit templates, a scoring rubric, and open-source tooling. The framework converts aesthetic debate into variable adjustment, and has been applied to real-world cases including the iPhone 17 Pro design controversy and flagship automotive styling. We position BEA as an *engineering coordinate system* rather than a psychophysical constant, and outline a falsifiable validation protocol.

## 1. Introduction

Design criticism lacks a shared coordinate system. Two practitioners can look at the same poster — one calls it "premium," the other "cheap" — and the disagreement terminates in taste because there is no agreed vocabulary for *which element, in which dimension, by how much*. Existing aesthetics research explains why beauty pleases (neuroaesthetics), when fear becomes sublime (Burke; Kant), and how arousal modulates preference (Berlyne's arousal theory), but offers little that a practitioner can apply at 2 a.m. before a deadline.

BEA attempts to bridge explanatory theory and studio practice. Its central claim:

> **Aesthetic pleasure = emotional reward under controllable tension.**

Every sensory element carries emotional polarity; no element is neutral. Beauty emerges when threat-arousal signals are simultaneously present and *metabolized* by safety signals and order structures — "softness with a spine; danger without collapse."

## 2. Theoretical foundations

BEA integrates publicly established knowledge and adds an original operational layer:

| Source | Contribution to BEA |
|---|---|
| Neuroaesthetics (Zeki; Ramachandran) | Pleasure as reward-system activation |
| Approach–avoidance motivation | The two co-active pathways (dopaminergic reward vs. amygdala vigilance) |
| Burke / Kant on the sublime | Safety framing: fear becomes thrill when framed as non-lethal |
| Berlyne's arousal theory | The aesthetic window between boredom and anxiety lines |
| Gestalt psychology | Order as the metabolizing structure |
| Yin–yang aesthetics | Complementary bipolarity (gang-rou xiang-ji, hardness-softness mutual aid) as a mature cultural precedent |

**Original increments:** element-level bipolar taxonomy; three-tier threshold system (instinct / cognitive / cultural); W(T) threat index; six-archetype continuous spectrum; standardized diagnosis–prescription workflow with scoring rubric.

## 3. The framework

### 3.1 Bipolar taxonomy
Six dimension families — form/line, color, light/shadow, material/texture, composition/space, relation/interval — each spanning P-pole (rounded, low-saturation, soft light, fine texture, breathing space, loose intervals) to T-pole (sharp, high-saturation, hard light, coarse texture, compressed space, tight intervals).

### 3.2 The threat index W(T)
`W(T) = Σ wᵢ · (tᵢ/10)` where tᵢ is element threat intensity (0–10, calibrated against anchor cards) and wᵢ are category weights (e.g., phones: form .25, material .25, color .15, proportion .15, light .10, detail .10). Anchor ranges: ≤0.15 Healing / 0.15–0.30 Refined / 0.30–0.48 Balanced / 0.48–0.60 Sublime (requires high-intensity single elements) / 0.60–0.66 Austere / 0.66–0.85 Avant-garde; >0.85 approaches threshold breach. Midpoints approx 0.08/0.23/0.39/0.54/0.63/0.76.

### 3.3 The golden quadrant
Plotting tension against structural order yields four quadrants; the high-tension × high-order quadrant is the target zone. Improvement reduces to two moves: add order, or add tension.

### 3.4 Thresholds and the aesthetic window
Instinct thresholds (injury associations) are absolute red lines; cognitive thresholds (complexity vs. bandwidth) shift right with added order; cultural thresholds (symbol taboos) shift with contextual cues. The practitioner's core skill: push tension as far right as possible *within* the target audience's window.

### 3.5 Workflow
Six steps — audience profiling, archetype selection, order design, ratio & emphasis, threshold checking, verification — with audit templates, a 4×25 scoring rubric, and CLI/web tooling.

## 4. Case analysis: the iPhone 17 Pro controversy

The iPhone 17 Pro (2025) drew simultaneous praise as Apple's "boldest design" and criticism as its "ugliest iPhone." BEA resolves the paradox quantitatively: W(T) rose from 0.285 (16 Pro, within the phone category's refined-archetype comfort window) to 0.475 (17 Pro) — a single-generation jump of +0.19 that exits the category window into balanced-archetype territory. The same tension value sits in the professional audience's golden zone and near the mass audience's anxiety line. The controversy is not a disagreement about facts but a **window mismatch** between audiences — predictable, and partially engineerable (the paper discusses a "right-edge strategy": pushing to the window's right edge rather than beyond it).

## 5. Scope and limitations

- BEA adjudicates **formal beauty only** (form/color/material/space/light/sound/motion), not content or moral beauty.
- Scales are collaborative coordinates, not psychophysical constants; their purpose is to make disagreement locatable.
- Category weights are currently set by expert convention; the validation protocol (below) is designed to revise them against preference data.

## 6. Validation protocol (in progress)

We specify a falsifiable blind-rating experiment: three versions of a design at W(T) below/within/above the category window, rated by ≥10 naive participants. Predictions: (1) within-window versions are preferred by ≥0.8 points; (2) professional participants' preference peaks shift right. Community-submitted results are collected as an open evidence base; disconfirming results mandate weight-table revision. The full protocol is in the repository (`docs/experiment-protocol.md`).

## 7. Tooling and availability

Everything is open source (CC BY 4.0): CLI calculators (pure standard-library Python), an interactive web calculator with shareable URLs, agent skills for major AI assistants, prompt grammars for generative image models, anchor cards, and a seven-case library with recomputation-verified arithmetic (CI-enforced).

## 8. Conclusion

BEA does not claim beauty is a number. It claims that *talking about* beauty benefits from numbers — that "too sharp" becomes "form dimension t=8, reduce to 6," and that a theory earns trust by making predictions it can lose.

## Code and Data Availability

Source code, CLI/MCP toolchain, and the interactive calculator are archived with a permanent DOI: [10.6084/m9.figshare.33684490](https://doi.org/10.6084/m9.figshare.33684490) (Figshare). Development repository: github.com/Maxing0000/bipolar-emotion-aesthetics. The MCP server is pip-installable (`pip install bea-mcp`, PyPI: bea-mcp).

## References

See `references/academic-references.md` (12 public academic sources, including Burke 1757; Kant 1790; Berlyne 1971; Zeki 1999; LeDoux 1996; Gestalt sources; and Chinese yin–yang aesthetics).
