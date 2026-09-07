#!/usr/bin/env python3
"""SkillSynth thesis cover — content, print metrics, layout geometry, Warm Craft tokens (data module).

Everything the layered-SVG generator needs that is data rather than geometry/emission,
isolated so the data lives separately from layout code (data-module exception to the
300-line rule, mirroring seed_v4.py). All lengths are print points (1/72 in). Imported
by build_covers.py only.

Callers: build_covers.py (star-import). Callees: none (module-level constants).
"""
MM = 72 / 25.4
BLEED, SAFE, GRID = 9.0, 27.0, 36.0
SPINE_MM = 15.0
TRIM_MARK_LEN, TRIM_MARK_OFF = 24.0, 6.0   # crop-mark arm length / offset from the sheet corner

W = 210 * MM          # panel trim width  (595.2756)
H = 297 * MM          # panel trim height (841.8898)
SB = SPINE_MM * MM    # spine width      (42.5197)
CX = W / 2            # horizontal centre of a panel

# canonical palette — 12 identity roles (authoritative hexes, Warm Craft)
PAPER, PAPER2, CARD = "#FBF6EC", "#F3EDE1", "#FFFDF7"
INK, INKSOFT, CLAY = "#2A2521", "#4A4238", "#8A7B6C"
OCHRE, OCHREDEEP = "#B5862E", "#8A6520"
SAGE, SAGEDEEP = "#7C8A6B", "#5F6C50"
LINE, LINESTRONG = "#E4DAC8", "#CFC3AE"
WHITE = "#FFFFFF"

# type stacks (declared family strings are authoritative — El Messiri is the Arabic display face now installed)
F_DISPLAY = "Bricolage Grotesque, Public Sans, Noto Sans, sans-serif"
F_LATIN = "Public Sans, Bricolage Grotesque, Noto Sans, sans-serif"
F_AR = "El Messiri, Noto Sans Arabic, sans-serif"
F_AR_DISP = "El Messiri, Noto Sans Arabic, sans-serif"

# front layout geometry — distributed axis: letterhead → title → description,
# then a unified identity panel (authors + supervisors inside one card), then the year tab.
EMBLEM_SIZE = 92.0                               # seal size (pt)
EMBLEM_TOP, EMBLEM_CX = 37.0, 520.0              # seal top-left corner + horizontal centre (top-right block)
R_EDGE = 566.0                                   # letterhead right flush edge (>2pt inside the 27pt safe rim)
LETTERHEAD_YS = (176.0, 200.0, 224.0)            # university / faculty / degree baselines (right-aligned to R_EDGE)
TITLE_Y, MARK_Y = 268.0, 279.0                   # EN title baseline + marker underline (centre column)
DESC_YS = (330.0, 358.0)                         # AR description baselines
DIV_Y = 404.0                                    # hairline divider under the description

# unified identity panel — one outer paper-2 card holds all eight name lines (nothing spills)
PANEL_W, PANEL_H, PANEL_RX = 344.0, 204.0, 10.0  # outer card (centred on CX, rounded)
PANEL_X0, PANEL_Y0 = CX - PANEL_W / 2, 462.0     # card top-left (125.64, 462)
PANEL_X1, PANEL_Y1 = PANEL_X0 + PANEL_W, PANEL_Y0 + PANEL_H   # 469.64, 666
PANEL_INSET = 6.0                                # inner CARD field inset from the outer card
NAME_SIZE = 13.0                                 # author/supervisor name size — sized so the widest name clears the card edges (see AUTH_COLS/SUP_COLS)
TICK_Y, TICK_W, TICK_H = 472.0, 56.0, 3.0        # ochre top tick (centred on CX)
RULE_Y, RULE_W = 578.0, 84.0                     # hairline section rule between authors and supervisors
AUTH_LBL_Y = 494.0                               # «إعداد الطلبة» label baseline
AUTH_ROWS = (522.0, 552.0)                       # 2×2 author grid rows
AUTH_COLS = (CX - 90.0, CX + 90.0)               # 2×2 author grid cols — the widest name (≈142pt @13) keeps ≥7pt from the inner CARD edge
SUP_LBL_Y = 600.0                                # «إشراف» label baseline
SUP_Y = 630.0                                    # supervisor names baseline
SUP_COLS = (CX - 95.0, CX + 95.0)                # side-by-side supervisor columns — widest (≈120pt @13) keeps ≥10pt from the inner CARD edge
YEAR_TAB_Y, YEAR_TAB_W, YEAR_TAB_H = 756.0, 110.0, 48.0   # academic-year tab (centred on CX)
YEAR_TAB_TEXT_Y = YEAR_TAB_Y + 28.0

# seal rings about the emblem centre — identity echo behind the seal (top-right block)
EMBLEM_CY = EMBLEM_TOP + EMBLEM_SIZE / 2         # 83
HALO_R, ECHO_R = 58.0, 74.0                      # ochre halo ring / clay echo ring radii (centred on EMBLEM_CX)

# symmetric sage mound + ochre route + stage dots (bleed-space, mirrored about CX)
MOUND_D = f"M-9,744 C 92,732 196,710 {CX:.2f},710 C {CX*2-196:.2f},710 {CX*2-92:.2f},732 {W+9:.2f},744"
ROUTE_D = f"M-9,745 C 92,733 196,711 {CX:.2f},711 C {CX*2-196:.2f},711 {CX*2-92:.2f},733 {W+9:.2f},745"
STAGE_DOTS = ((CX - 170.0, 721.0, 4.0, OCHRE), (CX, 710.0, 5.5, SAGEDEEP), (CX + 170.0, 721.0, 4.0, OCHRE))

# back identity motif — quiet crest language around the single-ink mark
B_MARK_Y = 500.0                                 # top of the back single-ink mark
B_ROUTE_Y, B_ROUTE_W = 640.0, 220.0              # dashed sage-deep route line (centred on CX)
B_STAGE_DOTS = ((CX - 48.0, 652.0, 4.0, OCHRE), (CX, 640.0, 5.5, SAGEDEEP),
                (CX + 48.0, 652.0, 4.0, OCHRE))
B_YEAR_RULE_Y, B_YEAR_Y = 690.0, 720.0           # small year rule + year text under the motif

# spine — ascending bottom-to-top (Arabic shelf convention, rotate(-90))
S_TITLE_Y = 710.0                                # title start y (text rises upward from here)
S_YEAR_Y = 598.0                                 # year start y (text rises upward from here)
S_MARK_Y = 90.0                                  # top of the spine single-ink mark
S_TICK_Y = 250.0                                 # 18pt dashed crest-echo tick (centred on SB/2)

# thesis content — edit here (or the text layer) then re-run the generator
TITLE = "SkillSynth"
YEAR_AR_FULL = "٢٠٢٥–٢٠٢٦"
UNIV, FAC = "جامعة حلب", "كلية الهندسة المعلوماتية"
DEG = "مشروع السنة الرابعة"
DESC = ["منظومة ذكية للتعلم التكيفي وبناء المهارات", "تُرسم مسارًا مهنيًا شخصيًا خطوة بخطوة"]
AUTHORS_LBL, AUTHORS = "إعداد الطلبة", ["علي عثمان عبد الملك", "زهير حمامي", "مصطفى منلا محمد", "أحمد أحمد"]
SUP_LBL, SUPS = "إشراف", ["د. بدر الدين قصاب", "د. سهيل خواتمي"]
ABS_LBL = "الملخص"
ABSTRACT = [
    "يتناول هذا المشروع تصميم منصّة تعليمية تكيّفيّة",
    "تقيس كفاءات المتدرّب، وتحلّل فجوات مهاراته،",
    "وترسم له مسارًا شخصيًا منظّمًا نحو الهدف الوظيفي،",
    "مع تقييمات فورية ومساعد ذكاء اصطناعي محليّ",
    "يحافظ على خصوصية المستخدم وسلامة بياناته.",
]
LOGO_FILE = "university-logo.png"

# layer map — the *exported* LAYERS.md renders straight from this list
LAYER_ROWS = [
    ("FRONT — thesis-front.svg (paint order, top-most first)",),
    ("11", "f-year", "academic-year tab (110×48 at y 756, Arabic-Indic, on the sage mound)"),
    ("10", "f-dividers", "centred hairline divider under the description"),
    ("09", "f-supervisors", "«إشراف» label + 2 supervisor names inside the unified identity panel (below the section rule)"),
    ("08", "f-authors", "«إعداد الطلبة» label + 2×2 author grid inside the unified identity panel (above the section rule)"),
    ("07", "f-description", "Arabic description of the project (2 lines, under the title)"),
    ("06", "f-title", "EN title in Bricolage Grotesque 700 (Skill ink + Synth ochre) + marker underline"),
    ("05", "f-univ", "official letterhead block right-aligned to the top-right: جامعة حلب / كلية الهندسة المعلوماتية / مشروع السنة الرابعة"),
    ("04", "f-emblem", "official University of Aleppo emblem — <image> linked to university-logo.png (replaceable, 92pt, transparent-ground seal), top-right block"),
    ("03", "f-grid", "36pt hairline construction grid (toggle for editing)"),
    ("02", "f-colors", "identity field: symmetric sage mound (true bleed) + ochre dash-route + sage-deep/ochre stage dots + unified identity panel behind the names + ochre halo / clay echo rings behind the seal"),
    ("01", "f-ground", "paper ground"),
    ("00", "f-bleed", "container wrapping ground/identity-field; drawn UNCLIPPED in the jacket so the mound reaches the bleed"),
    ("BACK — thesis-back.svg (paint order)",),
    ("08", "b-mark", "single-ink project mark, centred (the project side of the cover pair)"),
    ("07", "b-colors", "identity motif: quiet crest language — dashed sage-deep route line + stage-dot triplet + small year/rule below"),
    ("06", "b-rule2", "centred rule under the abstract"),
    ("05", "b-abstract", "«الملخص» heading + 5-line centred abstract (replace text in the layer)"),
    ("04", "b-rule", "top rule under the echo line"),
    ("03", "b-echo", "university echo line: جامعة حلب — كلية الهندسة المعلوماتية"),
    ("02", "b-grid", "36pt hairline construction grid (toggle)"),
    ("01", "b-ground", "paper-2 ground"),
    ("SPINE — thesis-spine.svg",),
    ("03", "s-title", "vertical EN title (Bricolage, ascending bottom-to-top: rotate(-90), start 710)"),
    ("04", "s-year", "vertical academic year (Arabic-Indic, ascending: start 598)"),
    ("05", "s-mark", "single-ink sprout mark (top 90)"),
    ("06", "s-tick", "18pt dashed crest-echo tick (y 250, family continuity)"),
    ("02", "s-borders", "two edge hairlines"),
    ("01", "s-ground", "paper-2 ground"),
    ("PARAMETERS",),
    ("TITLE", TITLE + " — edit cover_spec.py then re-run, or edit the text layer directly"),
    ("DEGREE", DEG + " (replaces the bachelor-degree lines per revision)"),
    ("DESCRIPTION", " / ".join(DESC)),
    ("COMPOSITION", "Top-right emblem + letterhead block (right-aligned to R_EDGE=566); over-CX centre column: title 268 / marker 279 / description 330,358 / divider 404; unified identity panel (125.64..469.64 × 462..666) holding all 8 name lines inside one rounded card, with an ochre top tick at 472 and a section rule at 578; then the year tab."),
    ("PALETTE", "All 12 identity roles used across the set: paper, paper-2, card, ink, ink-soft, clay, ochre, ochre-deep, sage, sage-deep, line, line-strong."),
    ("LOGO", "university-logo.png is the black University-of-Aleppo seal (source «لوغو جامعة حلب .png», untouched) processed by a pure-Python PNG pipeline: RGBA alpha = 255 − min(R,G,B), so near-white (253→α 2) becomes transparent and the seal sits directly on the cream paper."),
    ("SPINE", f"{SPINE_MM} mm nominal. Adjust SPINE_MM in cover_spec.py; formula: spine(mm) ≈ pages × 0.11 (80gsm) + boards"),
    ("YEAR", YEAR_AR_FULL),
    ("FONTS", "Declared family strings are authoritative (El Messiri, Bricolage Grotesque, Public Sans, Noto Sans Arabic)."),
    ("RTL BOOK", "Jacket order front|spine|back ⇒ the spine bonds to the RIGHT edge of the front cover (Arabic book): front faces you, spine down the right edge, open by lifting the LEFT fore-edge. Spine title is ASCENDING bottom-to-top, the Arabic shelf convention."),
    ("RGB→CMYK", "All exports are RGB. Convert to CMYK at the print shop only."),
]