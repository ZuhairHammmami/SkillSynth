# SkillSynth Thesis Cover — Layer Map

Panels are authored in print pt (1/72in); A4 trim 210×297 mm, 9pt bleed, 27pt safe margin.
Each <g> carries `id` + `inkscape:label`. Read in paint order (top of list = top of stack).

| nº | layer id | contents |
|---|----------|----------|

**FRONT — thesis-front.svg (paint order, top-most first)**
| 11 | f-year | academic-year tab (110×48 at y 756, Arabic-Indic, on the sage mound) |
| 10 | f-dividers | centred hairline divider under the description |
| 09 | f-supervisors | «إشراف» label + 2 supervisor names inside the unified identity panel (below the section rule) |
| 08 | f-authors | «إعداد الطلبة» label + 2×2 author grid inside the unified identity panel (above the section rule) |
| 07 | f-description | Arabic description of the project (2 lines, under the title) |
| 06 | f-title | EN title in Bricolage Grotesque 700 (Skill ink + Synth ochre) + marker underline |
| 05 | f-univ | official letterhead block right-aligned to the top-right: جامعة حلب / كلية الهندسة المعلوماتية / مشروع السنة الرابعة |
| 04 | f-emblem | official University of Aleppo emblem — <image> linked to university-logo.png (replaceable, 92pt, transparent-ground seal), top-right block |
| 03 | f-grid | 36pt hairline construction grid (toggle for editing) |
| 02 | f-colors | identity field: symmetric sage mound (true bleed) + ochre dash-route + sage-deep/ochre stage dots + unified identity panel behind the names + ochre halo / clay echo rings behind the seal |
| 01 | f-ground | paper ground |
| 00 | f-bleed | container wrapping ground/identity-field; drawn UNCLIPPED in the jacket so the mound reaches the bleed |

**BACK — thesis-back.svg (paint order)**
| 08 | b-mark | single-ink project mark, centred (the project side of the cover pair) |
| 07 | b-colors | identity motif: quiet crest language — dashed sage-deep route line + stage-dot triplet + small year/rule below |
| 06 | b-rule2 | centred rule under the abstract |
| 05 | b-abstract | «الملخص» heading + 5-line centred abstract (replace text in the layer) |
| 04 | b-rule | top rule under the echo line |
| 03 | b-echo | university echo line: جامعة حلب — كلية الهندسة المعلوماتية |
| 02 | b-grid | 36pt hairline construction grid (toggle) |
| 01 | b-ground | paper-2 ground |

**SPINE — thesis-spine.svg**
| 03 | s-title | vertical EN title (Bricolage, ascending bottom-to-top: rotate(-90), start 710) |
| 04 | s-year | vertical academic year (Arabic-Indic, ascending: start 598) |
| 05 | s-mark | single-ink sprout mark (top 90) |
| 06 | s-tick | 18pt dashed crest-echo tick (y 250, family continuity) |
| 02 | s-borders | two edge hairlines |
| 01 | s-ground | paper-2 ground |

**PARAMETERS**
- **TITLE:** SkillSynth — edit cover_spec.py then re-run, or edit the text layer directly
- **DEGREE:** مشروع السنة الرابعة (replaces the bachelor-degree lines per revision)
- **DESCRIPTION:** منظومة ذكية للتعلم التكيفي وبناء المهارات / تُرسم مسارًا مهنيًا شخصيًا خطوة بخطوة
- **COMPOSITION:** Top-right emblem + letterhead block (right-aligned to R_EDGE=566); over-CX centre column: title 268 / marker 279 / description 330,358 / divider 404; unified identity panel (125.64..469.64 × 462..666) holding all 8 name lines inside one rounded card, with an ochre top tick at 472 and a section rule at 578; then the year tab.
- **PALETTE:** All 12 identity roles used across the set: paper, paper-2, card, ink, ink-soft, clay, ochre, ochre-deep, sage, sage-deep, line, line-strong.
- **LOGO:** university-logo.png is the black University-of-Aleppo seal (source «لوغو جامعة حلب .png», untouched) processed by a pure-Python PNG pipeline: RGBA alpha = 255 − min(R,G,B), so near-white (253→α 2) becomes transparent and the seal sits directly on the cream paper.
- **SPINE:** 15.0 mm nominal. Adjust SPINE_MM in cover_spec.py; formula: spine(mm) ≈ pages × 0.11 (80gsm) + boards
- **YEAR:** ٢٠٢٥–٢٠٢٦
- **FONTS:** Declared family strings are authoritative (El Messiri, Bricolage Grotesque, Public Sans, Noto Sans Arabic).
- **RTL BOOK:** Jacket order front|spine|back ⇒ the spine bonds to the RIGHT edge of the front cover (Arabic book): front faces you, spine down the right edge, open by lifting the LEFT fore-edge. Spine title is ASCENDING bottom-to-top, the Arabic shelf convention.
- **RGB→CMYK:** All exports are RGB. Convert to CMYK at the print shop only.
