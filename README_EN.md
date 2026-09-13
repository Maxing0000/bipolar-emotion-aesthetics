# Bipolar Emotion Aesthetics (BEA)

**A computable, cross-media framework of formal aesthetics — analysis, diagnosis, and design.**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/badge/version-v1.7.3-blue.svg)]()
[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.33684490-blue)](https://doi.org/10.6084/m9.figshare.33684490)
[![Author](https://img.shields.io/badge/author-%E6%98%9F%E7%A9%BA%E6%9C%AC%E7%A9%BA-orange.svg)]()

> Chinese README: [README.md](README.md) | Read online: [docs/index.html](docs/index.html) | Glossary: [GLOSSARY.md](GLOSSARY.md)

---

## What is BEA?

**Bipolar Emotion Aesthetics (BEA)** is an engineering-style methodology for formal aesthetics. Its core thesis:

> **Aesthetic pleasure = emotional reward under controlled tension.**

Every sensory element carries one of two innate emotional polarities:

- **Pole of Attraction (P+)** — soft, low-arousal, approach-and-safety signals: round curves, muted colors, smooth texture, calm rhythm.
- **Pole of Threat (T−)** — sharp, high-arousal, vigilance-and-stimulation signals: acute angles, strong contrast, hard texture, sudden change.

Neither pole alone produces sophisticated beauty: pure P+ feels cloying and bland; pure T− feels aggressive and repulsive. Beauty arises when **both poles are composed within cognizable order, and the threat-pole arousal is kept within the subject's safety threshold** — the vigilance is then "recruited" into reward, yielding the compound pleasure of *being captivated yet soothed*.

## What can it do?

| Mode | Input | Output |
|---|---|---|
| **Analyze / Evaluate** | A design object (description or image) | Polarity breakdown, archetype placement, W(T) threat index, BEA scorecard, root-cause explanation |
| **Create / Design** | Target mood + object type + context | Element-level design plan, P+/T− ratio, concrete variables for form/color/material/rhythm |
| **Diagnose / Tune** | "Why does this look cheap / cloying / chaotic / aggressive?" | Symptom localization (threshold breach / disorder / mis-pairing) + actionable prescription + revision checklist |

## Applicable domains

Product & industrial design (phones, cars, appliances), architecture & interiors, brand & graphic design (logos, posters, packaging), UI/UX, fashion, sound & music, film & animation, installation & sculpture — **any object presented through sensory form**.

## Core structure (11 chapters)

1. **Ontology** — definition, axioms, boundaries
2. **Mechanism** — neural circuits, evolution, inverted-U arousal, cognition, safety frame
3. **Elements** — bipolar spectrum across vision / hearing / touch / motion, 0–10 intensity scale
4. **Structure** — four laws (primary-secondary, unity of opposites, order, nested hierarchy), aesthetic map
5. **Threshold** — three-tier threshold, aesthetic window, modulation variables
6. **Archetypes** — six anchors on a continuous spectrum (4 core + 2 transitional)
7. **Context** — culture / era / audience / function modulation, polarity reversal
8. **Method** — six-step creation method, W(T) calculation, BEA scorecard
9. **Application** — nine domain playbooks
10. **Diagnosis** — symptom–prescription table
11. **Evaluation** — standards and boundaries

## Quick start (30 seconds)

1. Pick an archetype (e.g. *Refined Approachable* = P+ 80 : T− 20 for consumer electronics).
2. Audit each element dimension: mark P+/T− direction and 0–10 intensity.
3. Compute `W(T) = Σ wᵢ · (tᵢ / 10)`; keep it inside the archetype's target band.
4. Establish at least one order backbone (grid / module / feature line / palette).
5. Run the three threshold checks (instinctive / cognitive / cultural).
6. Score with the BEA scorecard; any dimension < 15 must be revised.

## Repository layout

```
bipolar-emotion-aesthetics/
├── README.md / README_EN.md   # Chinese / English overview
├── GLOSSARY.md                 # CN–EN glossary (unified translations)
├── FAQ.md                      # Frequently asked questions (CN)
├── LICENSE                     # CC BY 4.0
├── release.sh                  # One-command release script (GitHub/Gitee/ModelScope)
├── docs/
│   ├── cover.png               # Cover image
│   ├── index.html              # Interactive W(T) calculator (GitHub Pages home)
│   ├── theory-book.html        # Full online theory book (11 parts)
│   ├── boundary.md             # Scope & compliance statement
│   └── promotion.md            # Promotion kit (CN/EN copy + topic bank)
├── templates/
│   └── bea-scorecard-templates.md  # Copy-ready scorecard & audit templates
├── references/
│   └── academic-references.md  # 12 public academic sources + originality statement
└── bipolar-emotion-aesthetics/ # ← The Agent Skill itself (copy this folder)
    ├── SKILL.md                # Entry: triggers + core model + 4 workflows (A/B/C/D)
    ├── references/             # theory / paradigms / method / playbooks / audit-templates / bea-prompts
    ├── scripts/wt_calc.py      # W(T) calculator (stdlib only, offline)
    ├── anchors/                # 0–10 intensity anchor charts
    └── cases/                  # 7 verified cases (AITO M9 / Huawei / iPhone 17 Pro / phone·logo·poster demos)
```

## Originality & scope

BEA integrates publicly established knowledge from neuroaesthetics, Burke's sublime, Gestalt psychology, and approach–avoidance motivation theory. The **original framework** — element bipolar classification, three-tier threshold, W(T) threat index, six archetypes, standardized diagnosis and scoring workflow — is authored by **Xingkong Benkong** and released under **CC BY 4.0**.

BEA evaluates **formal aesthetics only** (line, texture, color, composition, rhythm). It does not judge content, narrative, morality, or ideas. W(T) and the BEA score are **relative reference scales**, not objective physical measurements.

## License

**CC BY 4.0** — You are free to share, adapt, and use commercially, provided you give appropriate credit to **Xingkong Benkong / Bipolar Emotion Aesthetics (BEA)**, indicate changes, and link to the license.

## Author & links

- **Author:** Xingkong Benkong
- **Version:** v1.7.3
- **DOI:** [10.6084/m9.figshare.33684490](https://doi.org/10.6084/m9.figshare.33684490) (Figshare archive)
- GitHub (international): https://github.com/Maxing0000/bipolar-emotion-aesthetics
- Gitee (China): https://gitee.com/maxing0000/bipolar-emotion-aesthetics
- ModelScope: https://www.modelscope.cn/datasets/xkbk0000/bipolar-emotion-aesthetics

---

*Bipolar Emotion Aesthetics — explain beauty, compose beauty, distinguish beauty, create beauty, verify beauty.*
