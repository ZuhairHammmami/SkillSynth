#!/usr/bin/env python3
"""Emit a dimensioned technical drawing of the SkillSynth thesis 1-up jacket media as an Inkscape-labeled SVG.

Self-contained (no imports from cover_spec/build_covers); all media geometry is recomputed here.
The jacket is laid out **front | spine | back** — the Arabic (RTL) book convention: the spine bonds
to the RIGHT edge of the front cover (front faces you, spine down the right edge, open by lifting the
left fore-edge). Run: python3 print_spec.py  ->  writes thesis-print-spec.svg in the script directory."""
from __future__ import annotations

# ---- authoritative media geometry (recomputed, never hardcoded decimal results) ----
MM = 72 / 25.4                 # points per millimetre
W = 210 * MM                   # A4 trim width per panel  (595.28 pt)
H = 297 * MM                   # A4 trim height per panel (841.89 pt)
BLEED = 9.0                    # bleed on all four edges (pt)
SAFE = 27.0                    # safe margin inside each trim (pt)
SPINE_MM = 15.0                # nominal spine width (mm)
SB = SPINE_MM * MM             # spine width in pt (42.52)
WC = BLEED + W + SB + W + BLEED   # 1-up jacket media width  (1251.07 pt)
HC = H + 2 * BLEED                # 1-up jacket media height (859.89 pt)
fold_front_spine = BLEED + W          # first spine score/fold x (604.28) — spine bonds to FRONT's right edge (Arabic)
fold_spine_back = fold_front_spine + SB   # second spine score/fold x (646.80)
trim_right = WC - BLEED           # trim right edge of the back panel (1242.07)
TRIM_MARK_LEN, TRIM_MARK_OFF = 24.0, 6.0   # crop-mark arm length / offset from media edge

# ---- Warm Craft palette + Linear/Notion minimal line-drawing tokens ----
PAPER, PAPER2 = "#FBF6EC", "#F3EDE1"
INK, INKSOFT = "#2A2521", "#4A4238"
OCHRE, OCHREDEEP = "#B5862E", "#8A6520"
LINE_STRONG = "#CFC3AE"
F_LATIN = "Public Sans, Bricolage Grotesque, Noto Sans, sans-serif"

# ---- viewport: media sits inside left/top margins so dimension arrows fit in the margin ----
ML, MT = 165.0, 150.0          # translate the whole drawing into the viewport
VW, VH = 1570.0, 1180.0        # viewBox width/height (pt == user units)
OUT = "thesis-print-spec.svg"


def pt2mm(v: float) -> float:
    """Convert a pt length to mm (MM). Caller: label/build; callee: none."""
    return v / MM


def r(v: float, nd: int = 2) -> str:
    """Format a float rounded to nd decimals for SVG output. Caller: all emitters; callee: none."""
    return f"{v:.{nd}f}"


def vx(mx: float) -> str:
    """View x for a media-relative mx (adds ML). Caller: all emitters; callee: none."""
    return r(ML + mx)


def vy(my: float) -> str:
    """View y for a media-relative my (adds MT). Caller: all emitters; callee: none."""
    return r(MT + my)


def rect(x, y, w, h, fill, stroke, sw=1.0, dash="", rx=None):
    """Return a <rect> element with optional dash/rx. Caller: outline/sections/guides; callee: none."""
    dx = f' stroke-dasharray="{dash}"' if dash else ""
    rr = f' rx="{r(rx)}"' if rx is not None else ""
    return (f'<rect x="{r(ML + x)}" y="{r(MT + y)}" width="{r(w)}" height="{r(h)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{r(sw)}"{dx}{rr}/>\n')


def label(txt, cx_view, y_view, size=8.5, weight=700, fill=INK, ls="0", anchor="middle"):
    """Return a centred <text> label (kept as text). Caller: section/score/note emitters; callee: none."""
    lsa = f' letter-spacing="{ls}"' if ls != "0" else ""
    return (f'<text x="{r(cx_view)}" y="{r(y_view)}" text-anchor="{anchor}" '
            f'font-family="{F_LATIN}" font-size="{r(size)}" font-weight="{weight}" '
            f'fill="{fill}"{lsa}>{txt}</text>\n')


def section_rects():
    """Emit the three thin BACK/SPINE/FRONT section rectangles with centred top labels. Caller: main; callee: rect/label."""
    out = ""
    for (x0, x1, fill, name) in ((BLEED, fold_front_spine, PAPER, "FRONT"),
                                 (fold_front_spine, fold_spine_back, PAPER2, "SPINE"),
                                 (fold_spine_back, trim_right, PAPER2, "BACK")):
        out += rect(x0, BLEED, x1 - x0, H, fill, LINE_STRONG, 0.6)
        out += label(name, (ML + x0 + x1) / 2, MT + 46, size=9.5, ls="0.2em")
    return out


def crop_marks():
    """Emit the 8 crop marks at the trim corners (top y=0 and bottom y=HC) plus trim-edge horizontals. Caller: main; callee: none."""
    out = ""
    for x in (BLEED, fold_front_spine, fold_spine_back, trim_right):
        for ytop in (True, False):
            y = 0.0 if ytop else HC
            out += f'<path d="M{r(ML + x)},{r(MT + y)} V{r(MT - TRIM_MARK_OFF if ytop else MT + HC + TRIM_MARK_OFF)}" ' \
                   f'stroke="{INKSOFT}" stroke-width="0.75" fill="none"/>\n'
    for x in (BLEED, trim_right):
        out += f'<path d="M{r(ML + x)},{r(MT)} H{r(ML + x - TRIM_MARK_OFF - TRIM_MARK_LEN)}" stroke="{INKSOFT}" stroke-width="0.75" fill="none"/>\n'
        out += f'<path d="M{r(ML + x)},{r(MT + HC)} H{r(ML + x - TRIM_MARK_OFF - TRIM_MARK_LEN)}" stroke="{INKSOFT}" stroke-width="0.75" fill="none"/>\n'
    return out


def score_lines():
    """Emit the two spine fold (score) dashed lines spanning HC with top labels. Caller: main; callee: label."""
    out = ""
    for x in (fold_front_spine, fold_spine_back):
        out += f'<line x1="{r(ML + x)}" y1="{r(MT)}" x2="{r(ML + x)}" y2="{r(MT + HC)}" ' \
               f'stroke="{OCHREDEEP}" stroke-width="1" stroke-dasharray="7 4" stroke-opacity="0.8"/>\n'
        out += label(f"score {x:.2f}", ML + x - 6, MT + 18, size=7, weight=600, fill=OCHREDEEP, anchor="end")
    return out


def safe_guides():
    """Emit three dashed safe rects (inset SAFE in each panel trim) with one shared label. Caller: main; callee: rect/label."""
    out = ""
    for (x0, x1) in ((BLEED, fold_front_spine), (fold_front_spine, fold_spine_back), (fold_spine_back, trim_right)):
        if x1 - x0 > 2 * SAFE:
            out += rect(x0 + SAFE, BLEED + SAFE, (x1 - x0) - 2 * SAFE, H - 2 * SAFE, "none", LINE_STRONG, 0.6, "4 3")
    out += label("safe 27pt", ML + trim_right - SAFE, MT + BLEED + SAFE - 6, size=7, weight=600, fill=INKSOFT, anchor="end")
    return out


def bleed_guide():
    """Emit the dashed outer bleed rectangle (inset BLEED = the trim boundary) with a label. Caller: main; callee: rect/label."""
    out = rect(BLEED, BLEED, WC - 2 * BLEED, HC - 2 * BLEED, "none", OCHRE, 0.6, "4 3")
    out += label("bleed 9pt / 3.17mm", ML + BLEED, MT + HC, size=7, weight=600, fill=OCHRE, anchor="start")
    return out


def dim_arrow(x1, y1, x2, y2, txt, dy_label=0.0, anchor="middle"):
    """Emit a thin dimension line with arrowheads and a centred label. Caller: dim_width/dim_spine/dim_height; callee: none."""
    dx, dy = x2 - x1, y2 - y1
    off = 4.0 if dx == 0 else 0.0
    lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 + dy_label - off
    return (f'<line x1="{r(x1)}" y1="{r(y1)}" x2="{r(x2)}" y2="{r(y2)}" '
            f'stroke="{INKSOFT}" stroke-width="0.8" marker-start="url(#ah) " marker-end="url(#ah)"/>\n'
            f'<text x="{r(lx)}" y="{r(ly)}" text-anchor="{anchor}" font-family="{F_LATIN}" '
            f'font-size="7.5" font-weight="600" fill="{INKSOFT}">{txt}</text>\n')


def dim_width():
    """Top margin dimension across the full media width (pt + mm). Caller: main; callee: dim_arrow."""
    y = MT - 40
    return dim_arrow(ML, y, ML + WC, y, "1251.07 pt / 441.68 mm", dy_label=-6)


def dim_spine():
    """Top margin dimension across the spine width (pt + mm). Caller: main; callee: dim_arrow."""
    y = MT - 68
    return dim_arrow(ML + fold_front_spine, y, ML + fold_spine_back, y, "42.52 pt / 15.00 mm", dy_label=-6)


def dim_height():
    """Right-margin dimension of the vertical panel trim height (pt + mm). Caller: main; callee: dim_arrow."""
    x = ML + WC + 45
    return dim_arrow(x, MT, x, MT + H, "841.89 pt / 297 mm", dy_label=-6)


def notes():
    """Emit the RGB->CMYK corner note and the thin palette legend. Caller: main; callee: label."""
    out = label("All exports RGB. Convert to CMYK at the print shop only.", ML + 6, MT + HC + 46, size=8, weight=600, fill=INKSOFT, anchor="start")
    out += label("legend -", ML + 6, MT + HC + 92, size=7.5, weight=600, fill=INKSOFT, anchor="start")
    legend_row = (("ink", INK), ("paper", PAPER), ("ochre", OCHRE), ("line", LINE_STRONG))
    for i, (name, col) in enumerate(legend_row):
        lx = ML + 70 + i * 90
        out += f'<rect x="{r(lx)}" y="{r(MT + HC + 84)}" width="10" height="10" fill="{col}" stroke="{OCHREDEEP}" stroke-width="0.5"/>\n'
        out += label(name, lx + 5, MT + HC + 93, size=7, weight=500, fill=INKSOFT, anchor="middle")
    return out


def build():
    """Assemble the full SVG body (all guides). Caller: main; callee: all emitters."""
    out = ""
    out += rect(0, 0, WC, HC, PAPER, INK, 1.2)                       # media outline
    out += label(f"MEDIA {WC:.2f} x {HC:.2f} pt  /  {pt2mm(WC):.1f} x {pt2mm(HC):.1f} mm",
                  ML + WC / 2, MT - 20, size=9, weight=700, fill=INK)
    out += section_rects()                                           # three panels
    out += score_lines()                                             # two fold dashed lines + labels
    out += safe_guides()                                             # 3 safe rects
    out += bleed_guide()                                             # bleed trim rectangle
    out += crop_marks()                                              # 8 trim crop marks
    out += dim_width() + dim_spine() + dim_height()                  # dimension arrows
    out += notes()                                                   # RGB->CMYK note + legend
    return out


def main():
    """Write thesis-print-spec.svg and print its byte size. Callers: CLI; callee: build."""
    import pathlib
    note = ("  SkillSynth thesis — 1-up jacket print-spec technical drawing.\n"
            "  Media 1251.07 x 859.89 pt = front 595.28 + spine 42.52 (15 mm) + back 595.28, 9 pt bleed all edges.\n"
            "  Arabic (RTL): spine bonds to the RIGHT edge of the FRONT cover; open by lifting the LEFT fore-edge.\n"
            "  Fold/score lines at x = 604.28 / 646.80; safe 27 pt; crop-mark arms 24 pt at 6 pt offset.\n"
            "  RGB source — convert to CMYK at the print shop only.")
    defs = ('<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="4" refY="4" '
            'orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#4A4238"/></marker></defs>\n')
    body = f'<g id="print-spec-drawing" inkscape:label="print-spec-drawing">\n{build()}</g>\n'
    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n<!--\n{note}\n-->\n'
           f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           f'viewBox="0 0 {r(VW,0)} {r(VH,0)}" width="{r(VW,0)}" height="{r(VH,0)}">\n'
           f'{defs}\n{body}\n</svg>\n')
    here = pathlib.Path(__file__).resolve().parent
    blob = svg.encode("utf-8")
    (here / OUT).write_bytes(blob)
    print(f"wrote {OUT} ({len(blob)} B)")


if __name__ == "__main__":
    main()
