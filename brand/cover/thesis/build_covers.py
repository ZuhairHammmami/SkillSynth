#!/usr/bin/env python3
"""Generate the SkillSynth thesis cover set (University of Aleppo) as layered, Inkscape-editable SVGs.

Content lives in cover_spec.py; fonts stay text; the jacket is laid out front|spine|back so the spine
binds to the RIGHT edge of the front cover — the Arabic (RTL) book convention. Run: python3 build_covers.py."""
from __future__ import annotations
from cover_spec import *


def r(v: float) -> str:
    """Round a float to 2dp pt (print-exact)."""
    return f"{v:.2f}"


def g(id_: str, label: str, extra=""):
    """Open a named, Inkscape-labelled layer group (purpose: layered editability)."""
    return f'<g id="{id_}" inkscape:label="{label}"{extra}>\n'


def t(x, y, size, weight, fill, fam=F_AR, anchor="middle", ls="0", extra=""):
    """Return an anchored <text> element (never converted to paths)."""
    ls_a = f' letter-spacing="{ls}"' if ls != "0" else ""
    return f'<text x="{r(x)}" y="{r(y)}" text-anchor="{anchor}" font-family="{fam}" font-size="{r(size)}" font-weight="{weight}" fill="{fill}"{ls_a}{extra}>'


def divider(cx, y, w=120, color=LINESTRONG, sw=1.0):
    """Centred hairline rule (decorative only)."""
    return f'<line x1="{r(cx - w / 2)}" y1="{r(y)}" x2="{r(cx + w / 2)}" y2="{r(y)}" stroke="{color}" stroke-width="{sw}"/>\n'


def grid_lines(cw, ch, color, op, gid):
    """36pt hairline construction grid for a panel (labelled inner group)."""
    out = []
    x = GRID
    while x < cw:
        out.append(f'<path d="M{r(x)},0 V{ch}"/>')
        x += GRID
    y = GRID
    while y < ch:
        out.append(f'<path d="M0,{r(y)} H{cw}"/>')
        y += GRID
    return (f'<g id="{gid}" inkscape:label="grid lines" stroke="{color}" stroke-width="0.75" '
            f'stroke-opacity="{op}">\n' + "\n".join(out) + "\n</g>\n")


def mark(s, x, y, scheme=("main",), gid="mark-group"):
    """Warm Craft sprout mark, scaled s, top-left at (x, y). Returns a labelled <g>."""
    ring, stem, seed = "#B5862E", "#5F6C50", "#B5862E"
    if scheme[0] == "ink":
        ring = stem = seed = INK
    return (f'<g id="{gid}" inkscape:label="sprout mark (32-grid)" transform="translate({r(x)} {r(y)}) scale({r(s)})">\n'
            f'<path d="M16 28C9 28 5 23 5 16c0-5 4-9 11-9s11 4 11 9c0 7-4 12-11 12z" stroke="{ring}" stroke-width="1.8" fill="none"/>\n'
            f'<path d="M16 27V13M16 18c-3-1-5-3-5-6M16 18c3-1 5-3 5-6" stroke="{stem}" stroke-width="1.8" stroke-linecap="round" fill="none"/>\n'
            f'<circle cx="16" cy="9" r="2.2" fill="{seed}"/>\n</g>\n')


def em(cx, y, size):
    """Front emblem <image> element (PNG stays replaceable; rasterisers keep it)."""
    return (f'<image x="{r(cx - size / 2)}" y="{r(y)}" width="{r(size)}" height="{r(size)}" '
            f'preserveAspectRatio="xMidYMid meet" xlink:href="{LOGO_FILE}"/>\n')


def header(view_w, view_h, note, defs, body):
    """Assemble one standalone SVG document. Callee of panel()/jacket()."""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<!--\n{note}\n-->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
            f'viewBox="0 0 {r(view_w)} {r(view_h)}" width="{r(view_w)}" height="{r(view_h)}">\n'
            f"<defs>\n{defs}</defs>\n\n{body}</svg>\n")


def _f_colors():
    """Dynamic identity shapes for the front: symmetric mound, route, stage dots, unified identity panel, seal rings. Caller: front_bleed."""
    out = g("f-colors", "02 identity field (rings, panel, mound, route, dots)")
    out += f'<path d="{MOUND_D} L{r(W + BLEED)},{r(H + BLEED)} L{r(-BLEED)},{r(H + BLEED)} Z" fill="{SAGE}"/>\n'
    out += f'<path d="{ROUTE_D}" stroke="{OCHRE}" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="5 4" fill="none"/>\n'
    for x, y, rad, col in STAGE_DOTS:
        out += f'<circle cx="{r(x)}" cy="{r(y)}" r="{rad}" fill="{col}"/>\n'
    # unified identity panel — outer paper-2 card + inner CARD field + top tick + section rule
    out += f'<rect x="{r(PANEL_X0)}" y="{r(PANEL_Y0)}" width="{r(PANEL_W)}" height="{r(PANEL_H)}" rx="{r(PANEL_RX)}" fill="{PAPER2}" stroke="{LINESTRONG}" stroke-width="0.75"/>\n'
    out += f'<rect x="{r(PANEL_X0 + PANEL_INSET)}" y="{r(PANEL_Y0 + PANEL_INSET)}" width="{r(PANEL_W - 2 * PANEL_INSET)}" height="{r(PANEL_H - 2 * PANEL_INSET)}" rx="{r(PANEL_RX * 0.6)}" fill="{CARD}" stroke="{LINESTRONG}" stroke-width="0.5"/>\n'
    out += f'<rect x="{r(CX - TICK_W / 2)}" y="{r(TICK_Y)}" width="{r(TICK_W)}" height="{r(TICK_H)}" fill="{OCHRE}"/>\n'
    out += divider(CX, RULE_Y, RULE_W, LINESTRONG, 0.75)
    # seal rings centred on the top-right emblem, not the panel
    out += f'<circle cx="{r(EMBLEM_CX)}" cy="{r(EMBLEM_CY)}" r="{r(ECHO_R)}" stroke="{CLAY}" stroke-width="1.2" fill="none"/>\n'
    out += f'<circle cx="{r(EMBLEM_CX)}" cy="{r(EMBLEM_CY)}" r="{r(HALO_R)}" stroke="{OCHRE}" stroke-width="2.2" fill="none"/>\n'
    out += "</g>\n"
    return out


def front_bleed():
    """Front bleed decor: paper ground + identity field (drawn unclipped in the jacket). Caller: art_front."""
    out = g("f-bleed", "00 bleed decor (ground + identity field)")
    out += g("f-ground", "01 ground") + f'<rect x="0" y="0" width="{r(W)}" height="{r(H)}" fill="{PAPER}"/>\n</g>\n'
    out += _f_colors()
    out += "</g>\n"
    return out


def front_header():
    """Front letterhead: emblem + official university text block, right-aligned to the top-right corner. Caller: art_front."""
    out = g("f-emblem", "04 official university emblem (Aleppo Univ — replaceable PNG, top-right block)") + em(EMBLEM_CX, EMBLEM_TOP, EMBLEM_SIZE) + "</g>\n"
    out += g("f-univ", "05 official university block (document letterhead, right-aligned)")
    out += t(R_EDGE, LETTERHEAD_YS[0], 19.18, 700, INK, anchor="end") + UNIV + "</text>\n"
    out += t(R_EDGE, LETTERHEAD_YS[1], 15.77, 600, INKSOFT, anchor="end") + FAC + "</text>\n"
    out += t(R_EDGE, LETTERHEAD_YS[2], 13.85, 600, OCHREDEEP, anchor="end") + DEG + "</text>\n</g>\n"
    return out


def front_centre():
    """Front midfield: EN project title + marker, then the Arabic description. Caller: art_front."""
    out = g("f-title", "06 academic project title (EN Bricolage)")
    out += t(CX, TITLE_Y, 34.43, 700, INK, F_DISPLAY, ls="-0.01em") + f'<tspan fill="{INK}">Skill</tspan><tspan fill="{OCHRE}">Synth</tspan></text>\n'
    out += f'<path d="M210,{r(MARK_Y)} C 224,{r(MARK_Y + 4)} 238,{r(MARK_Y)} 252,{r(MARK_Y + 4)} S 278,{r(MARK_Y)} 292,{r(MARK_Y + 4)} S 318,{r(MARK_Y)} 332,{r(MARK_Y + 4)} S 358,{r(MARK_Y)} 372,{r(MARK_Y + 4)} S 382,{r(MARK_Y + 1)} 385,{r(MARK_Y + 3)}" stroke="{OCHREDEEP}" stroke-width="6" stroke-linecap="round" fill="none"/>\n'
    out += "</g>\n"
    out += g("f-description", "07 project description (AR, under the title)")
    out += t(CX, DESC_YS[0], 13.85, 400, INKSOFT) + DESC[0] + "</text>\n" + t(CX, DESC_YS[1], 13.85, 400, INKSOFT) + DESC[1] + "</text>\n"
    out += "</g>\n"
    return out


def front_names():
    """Front identity block: authors + supervisors, all 8 name lines inside the unified identity panel. Caller: art_front."""
    out = g("f-authors", "08 authors (إعداد الطلبة, 2×2 grid, top half of the panel)")
    out += t(CX, AUTH_LBL_Y, 13.85, 600, OCHREDEEP) + AUTHORS_LBL + "</text>\n"
    for i, n in enumerate(AUTHORS):
        out += t(AUTH_COLS[i % 2], AUTH_ROWS[i // 2], NAME_SIZE, 500, INK) + n + "</text>\n"
    out += "</g>\n"
    out += g("f-supervisors", "09 supervisors (إشراف, bottom half of the panel, below the section rule)")
    out += t(CX, SUP_LBL_Y, 13.85, 600, OCHREDEEP) + SUP_LBL + "</text>\n"
    for i, n in enumerate(SUPS):
        out += t(SUP_COLS[i], SUP_Y, NAME_SIZE, 500, INK) + n + "</text>\n"
    out += "</g>\n"
    return out


def front_bottom():
    """Front bottom: divider under the description + large academic-year tab on the sage mound. Caller: art_front."""
    out = g("f-dividers", "10 hairline divider (under the description)") + divider(CX, DIV_Y, 200) + "</g>\n"
    out += g("f-year", "11 academic year (large tab on the sage mound)")
    out += f'<rect x="{r(CX - YEAR_TAB_W / 2)}" y="{r(YEAR_TAB_Y)}" width="{r(YEAR_TAB_W)}" height="{r(YEAR_TAB_H)}" rx="6" fill="{PAPER}" stroke="{LINESTRONG}" stroke-width="1"/>\n'
    out += t(CX, YEAR_TAB_TEXT_Y, 19.18, 600, INK) + YEAR_AR_FULL + "</text>\n</g>\n"
    return out


def art_front():
    """Compose front bleed decor + core (split keeps the field's trim-bleed in the jacket). Caller: panel/jacket."""
    bleed = front_bleed()
    core = g("f-grid", "03 grid (hairline, toggle)") + grid_lines(W, H, LINE, "0.4", "f-grid-lines") + "</g>\n"
    core += front_header() + front_centre() + front_names() + front_bottom()
    return bleed, core


def art_back():
    """Back panel: official echo, abstract, identity motif, single-ink project mark. Caller: panel/jacket."""
    out = g("b-ground", "01 ground (paper-2)") + f'<rect x="0" y="0" width="{r(W)}" height="{r(H)}" fill="{PAPER2}"/>\n</g>\n'
    out += g("b-grid", "02 grid (hairline, toggle)") + grid_lines(W, H, LINESTRONG, "0.28", "b-grid-lines") + "</g>\n"
    out += g("b-echo", "03 university echo line") + t(CX, 66, 13.85, 600, INKSOFT) + f"{UNIV} — {FAC}" + "</text>\n</g>\n"
    out += g("b-rule", "04 top rule") + divider(CX, 92, 160) + "</g>\n"
    out += g("b-abstract", "05 abstract (الملخص)")
    out += t(CX, 168, 15.77, 700, OCHREDEEP) + ABS_LBL + "</text>\n"
    for i, line in enumerate(ABSTRACT):
        out += t(CX, 206 + i * 32, 13.85, 400, INKSOFT) + line + "</text>\n"
    out += "</g>\n"
    out += g("b-rule2", "06 rule under abstract") + divider(CX, 384, 120) + "</g>\n"
    out += g("b-colors", "07 identity motif (route line · dots · year)")
    out += f'<line x1="{r(CX - B_ROUTE_W / 2)}" y1="{r(B_ROUTE_Y)}" x2="{r(CX + B_ROUTE_W / 2)}" y2="{r(B_ROUTE_Y)}" stroke="{SAGEDEEP}" stroke-width="2" stroke-dasharray="6 5" stroke-linecap="round" fill="none"/>\n'
    for x, y, rad, col in B_STAGE_DOTS:
        out += f'<circle cx="{r(x)}" cy="{r(y)}" r="{rad}" fill="{col}"/>\n'
    out += divider(CX, B_YEAR_RULE_Y, 120)
    out += t(CX, B_YEAR_Y, 10.67, 500, OCHREDEEP) + YEAR_AR_FULL + "</text>\n</g>\n"
    out += g("b-mark", "08 single-ink project mark (project side)") + mark(2.6, CX - 16 * 2.6, B_MARK_Y, scheme=("ink",), gid="b-mark-group") + "</g>\n"
    return out


def art_spine():
    """Spine panel: ascending title/year, mark, crest-echo tick. Caller: panel/jacket."""
    out = g("s-ground", "01 ground (paper-2)") + f'<rect x="0" y="0" width="{r(SB)}" height="{r(H)}" fill="{PAPER2}"/>\n</g>\n'
    out += g("s-borders", "02 edge hairlines")
    out += (f'<line x1="2" y1="27" x2="2" y2="{r(H - 27)}" stroke="{LINESTRONG}" stroke-width="0.75" stroke-opacity="0.6"/>\n'
            f'<line x1="{r(SB - 2)}" y1="27" x2="{r(SB - 2)}" y2="{r(H - 27)}" stroke="{LINESTRONG}" stroke-width="0.75" stroke-opacity="0.6"/>\n</g>\n')
    out += g("s-tick", "06 crest-echo tick (family continuity, dashed)") + f'<line x1="{r(SB / 2 - 9)}" y1="{r(S_TICK_Y)}" x2="{r(SB / 2 + 9)}" y2="{r(S_TICK_Y)}" stroke="{OCHRE}" stroke-width="1.2" stroke-dasharray="4 3" stroke-linecap="round"/>\n</g>\n'
    out += g("s-mark", "05 mark (single ink)") + mark(1.25, SB / 2 - 16 * 1.25, S_MARK_Y, scheme=("ink",), gid="s-mark-group") + "</g>\n"
    out += g("s-title", "03 title (EN, Bricolage, ascending bottom-to-top)")
    out += f'<text transform="translate({r(SB / 2)} {r(S_TITLE_Y)}) rotate(-90)" text-anchor="start" font-family="{F_DISPLAY}" font-size="13.85" font-weight="700" letter-spacing="-0.01em" fill="{INK}">{TITLE}</text>\n</g>\n'
    out += g("s-year", "04 academic year (ascending bottom-to-top)")
    out += f'<text transform="translate({r(SB / 2)} {r(S_YEAR_Y)}) rotate(-90)" text-anchor="start" font-family="{F_AR}" font-size="10.67" font-weight="500" fill="{OCHREDEEP}">{YEAR_AR_FULL}</text>\n</g>\n'
    return out


def panel(kind):
    """Build one standalone panel document (front splits bleed/core in defs). Caller: main."""
    pw, ph = (SB, H) if kind == "spine" else (W, H)
    note = (f"  SkillSynth thesis — {kind} cover panel. A4 trim {r(W)} x {r(H)} pt, 9pt bleed, 27pt safe.\n"
            f"  Fully layered, Inkscape-editable, fonts kept as text. RGB source — convert to CMYK at print shop.")
    trim = f'<clipPath id="trim"><rect x="0" y="0" width="{r(pw)}" height="{r(ph)}"/></clipPath>\n'
    if kind == "front":
        bleed, core = art_front()
        defs = trim + f'<g id="front-art" inkscape:label="front cover art">{bleed}{core}</g>\n'
        body = f'<use href="#front-art" clip-path="url(#trim)"/>\n'
    else:
        aid = {"back": "back-art", "spine": "spine-art"}[kind]
        lbl = {"back": "back cover art", "spine": "spine art"}[kind]
        art = art_back() if kind == "back" else art_spine()
        defs = trim + f'<g id="{aid}" inkscape:label="{lbl}">{art}</g>\n'
        body = f'<use href="#{aid}" clip-path="url(#trim)"/>\n'
    return header(pw, ph, note, defs, body).encode("utf-8")


def jacket():
    """Jacket spread (front|spine|back = Arabic book, spine-right) with a labeled print-guides layer (crop marks, score lines, section labels). Caller: main."""
    WC, HC = BLEED + W + SB + W + BLEED, H + 2 * BLEED
    fold_front_spine = BLEED + W          # first score/fold: front cover → spine (spine bonds to FRONT's right edge)
    fold_spine_back = fold_front_spine + SB
    trim_right = WC - BLEED
    bleed, core = art_front()
    defs = (f'<clipPath id="trim-back"><rect x="0" y="0" width="{r(W)}" height="{r(H)}"/></clipPath>\n'
            f'<clipPath id="trim-front"><rect x="0" y="0" width="{r(W)}" height="{r(H)}"/></clipPath>\n'
            f'<g id="front-bleed-art" inkscape:label="front bleed decor (unclipped)">{bleed}</g>\n'
            f'<g id="front-core-art" inkscape:label="front core (trim-clipped)">{core}</g>\n'
            f'<g id="spine-art" inkscape:label="spine art">{art_spine()}</g>\n'
            f'<g id="back-art" inkscape:label="back cover art">{art_back()}</g>\n')
    body = f'<rect x="0" y="0" width="{r(WC)}" height="{r(HC)}" fill="{PAPER}"/>\n'
    body += f'<rect x="0" y="0" width="{r(fold_front_spine)}" height="{r(HC)}" fill="{PAPER}"/>\n'
    body += f'<rect x="{r(fold_front_spine)}" y="0" width="{r(WC - fold_front_spine)}" height="{r(HC)}" fill="{PAPER2}"/>\n'
    # labeled print-guides layer: crop marks at the 8 boundary points + two spine score lines + section labels
    body += g("print-guides", "print guides (crop marks · score lines · section labels)")
    for x, y in ((0, 0), (fold_front_spine, 0), (fold_spine_back, 0), (WC, 0),
                 (0, HC), (fold_front_spine, HC), (fold_spine_back, HC), (WC, HC)):
        body += _crop_mark(x, y)
    for x in (fold_front_spine, fold_spine_back):
        body += (f'<line x1="{r(x)}" y1="{r(TRIM_MARK_OFF)}" x2="{r(x)}" y2="{r(HC - TRIM_MARK_OFF)}" '
                 f'stroke="{OCHREDEEP}" stroke-width="1" stroke-dasharray="7 4" stroke-opacity="0.8"/>\n')
        body += (f'<text x="{r(x + 6)}" y="{r(TRIM_MARK_OFF * 2 + TRIM_MARK_LEN)}" text-anchor="start" '
                 f'font-family="Public Sans, sans-serif" font-size="7" fill="{OCHREDEEP}" '
                 f'font-weight="600">score {r(x)}</text>\n')
    for label, x0, x1 in (("FRONT", 0, fold_front_spine), ("SPINE", fold_front_spine, fold_spine_back),
                          ("BACK", fold_spine_back, WC)):
        body += (f'<text x="{r((x0 + x1) / 2)}" y="{r(TRIM_MARK_OFF + TRIM_MARK_LEN + 10)}" text-anchor="middle" '
                 f'font-family="Public Sans, sans-serif" font-size="9" fill="{INKSOFT}" '
                 f'font-weight="700" letter-spacing="0.2em">{label}</text>\n')
    body += "</g>\n"
    body += f'<use href="#front-bleed-art" transform="translate({r(BLEED)} {r(BLEED)})"/>\n'
    body += f'<use href="#front-core-art" clip-path="url(#trim-front)" transform="translate({r(BLEED)} {r(BLEED)})"/>\n'
    body += f'<use href="#spine-art" transform="translate({r(fold_front_spine)} {r(BLEED)})"/>\n'
    body += f'<use href="#back-art" clip-path="url(#trim-back)" transform="translate({r(fold_spine_back)} {r(BLEED)})"/>\n'
    note = (f"  SkillSynth thesis — full jacket spread. Media {r(WC)} x {r(HC)} pt = "
            f"front {r(W)} + spine {r(SB)} ({SPINE_MM}mm) + back {r(W)}, 9pt bleed all edges.\n"
            f"  Arabic (RTL) book: the spine bonds to the RIGHT edge of the FRONT cover; open by lifting the LEFT fore-edge.\n"
            f"  Print geometry: trim {r(W)}x{r(H)} per panel · safe {SAFE}pt · spine fold/scores at x = "
            f"{r(fold_front_spine)} / {r(fold_spine_back)} · media bleed edges x = {r(BLEED)} / {r(trim_right)}.\n"
            f"  RGB source — convert to CMYK at the binder; do not print the RGB PDF directly.")
    return header(WC, HC, note, defs, body).encode("utf-8")


def _crop_mark(x, y):
    """L-shaped crop-mark arms at a media boundary point (x, y), arms inset by TRIM_MARK_OFF. Caller: jacket."""
    off, ln = TRIM_MARK_OFF, TRIM_MARK_LEN
    dx = ln if x == 0 else (-ln if x == BLEED + W + SB + W + BLEED else 0)
    dy = ln if y == 0 else (-ln if y == H + 2 * BLEED else 0)
    out = f'<path d="M{r(x)}, {r(y + dy - off)} V{r(y + dy)} M{r(x + dx - off)}, {r(y)} H{r(x + dx)}" '
    out += f'stroke="{INKSOFT}" stroke-width="0.75" fill="none"/>\n'
    return out


def layers_md():
    """Format LAYER_ROWS into the layer-map document. Caller: main."""
    lines = ["# SkillSynth Thesis Cover — Layer Map", "",
             "Panels are authored in print pt (1/72in); A4 trim 210×297 mm, 9pt bleed, 27pt safe margin.",
             "Each <g> carries `id` + `inkscape:label`. Read in paint order (top of list = top of stack).",
             "", "| nº | layer id | contents |", "|---|----------|----------|"]
    for row in LAYER_ROWS:
        if len(row) == 1:
            lines += ["", f"**{row[0]}**"]
        elif len(row) == 2:
            key, desc = row
            lines.append(f"- **{key}:** {desc}")
        else:
            n, lid, desc = row
            lines.append(f"| {n} | {lid} | {desc} |")
    return ("\n".join(lines) + "\n").encode("utf-8")


def inside_sheet():
    """Blank inside (verso) face of the same jacket media — inside-front | inside-spine | inside-back on plain paper (user chose a blank inside). Caller: main."""
    WC, HC = BLEED + W + SB + W + BLEED, H + 2 * BLEED
    seams = (BLEED, BLEED + W, BLEED + W + SB)
    body = g("i-ground", "inside ground (plain paper)")
    body += f'<rect x="{r(seams[0])}" y="{r(BLEED)}" width="{r(W)}" height="{r(H)}" fill="{PAPER}"/>\n'
    body += f'<rect x="{r(seams[1])}" y="{r(BLEED)}" width="{r(SB)}" height="{r(H)}" fill="{PAPER2}"/>\n'
    body += f'<rect x="{r(seams[2])}" y="{r(BLEED)}" width="{r(W)}" height="{r(H)}" fill="{PAPER2}"/>\n'
    body += "</g>\n"
    note = (f"  SkillSynth thesis — inside (verso) face of the cover sheet, same media {r(WC)} x {r(HC)} pt.\n"
            f"  Blank inside-front | inside-spine | inside-back on plain paper, ready for double-sided printing.\n"
            f"  Mirrors the outside jacket so the two sides align; convertible to CMYK at the print shop only.")
    return header(WC, HC, note, "", body).encode("utf-8")


def main():
    """Emit all panels, the jacket composite, the blank inside sheet, and LAYERS.md; print a contrast sanity table. Callers: CLI."""
    import pathlib
    here = pathlib.Path(__file__).resolve().parent
    for name, blob in (("thesis-front.svg", panel("front")), ("thesis-back.svg", panel("back")),
                       ("thesis-spine.svg", panel("spine")), ("thesis-jacket.svg", jacket()),
                       ("thesis-inside.svg", inside_sheet()), ("LAYERS.md", layers_md())):
        (here / name).write_bytes(blob)
        print(f"wrote {name} ({len(blob)} B)")
    ratios = [("ink/paper", 14.08), ("ink-soft/paper", 9.16), ("ochre-deep/paper", 4.92),
              ("ink/paper-2", 13.0), ("ink-soft/paper-2", 8.47), ("ochre-deep/paper-2", 4.55)]
    for pair, expected in ratios:
        print(f"contrast {pair}: {expected}:1 (reference)")


if __name__ == "__main__":
    main()