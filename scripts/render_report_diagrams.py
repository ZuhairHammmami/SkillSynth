"""Render the three deterministic report diagrams (fully-typed ERD + accurate use cases).

Caller: repository gates (.venv/bin/python scripts/render_report_diagrams.py); Callee:
report_diagram_layout data + matplotlib Agg primitives writing docs/report/assets/*.png.
Hardcoded layouts (no randomness); English labels; schema truth is the canonical DDL.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Ellipse, Rectangle

from report_diagram_layout import (
    ADMIN, ARROWS, BW, DOMAINS, HH, LH, PD, STUDENT, TABLES,
)

ASSETS = Path(__file__).resolve().parents[1] / "docs" / "report" / "assets"
DPI = 200
FC, EC, TFC, TC = "#F7F9FC", "#2C3E50", "#DCE6F1", "#1B2631"
AC, PC, UKC, GRC = "#34495E", "#1F618D", "#6C3483", "#4D5656"
PUR = "#8E44AD"


def box_geo(name):
    """Return rectangle geometry (l/r/t/b/cx/cy/h) for one fully-typed table box.

    Caller: draw_tables, edge_point; Callee: TABLES lookup.
    """
    cx, top, rows = TABLES[name]
    h = HH + PD + len(rows) * LH
    return {"l": cx - BW / 2, "r": cx + BW / 2, "t": top, "b": top - h,
            "cx": cx, "cy": top - h / 2, "h": h}


def edge_point(g, side, off):
    """Return an anchor point on one box edge, offset by a fraction of the half-extent.

    Caller: draw_fk_arrows; Callee: none.
    """
    if side == "top":
        return (g["cx"] + off * BW / 2, g["t"])
    if side == "bottom":
        return (g["cx"] + off * BW / 2, g["b"])
    if side == "left":
        return (g["l"], g["cy"] + off * g["h"] / 2)
    return (g["r"], g["cy"] + off * g["h"] / 2)


def tag_color(tag):
    """Map a column tag to its ink color (PK navy, FK teal, UK purple, plain gray).

    Caller: draw_tables; Callee: none.
    """
    if "PK" in tag:
        return PC
    if "FK" in tag:
        return "#148F77"
    if "UK" in tag:
        return UKC
    return GRC


def draw_tables(ax):
    """Draw all 15 rounded table boxes; tags flow after measured text extents.

    Caller: render_erd; Callee: box_geo, tag_color.
    """
    pending = []
    for name, (cx, top, rows) in TABLES.items():
        g = box_geo(name)
        ax.add_patch(FancyBboxPatch((g["l"], g["b"]), BW, g["h"],
                                    boxstyle="round,pad=0,rounding_size=1.6",
                                    fc=FC, ec=EC, lw=1.1, zorder=3))
        ax.add_patch(FancyBboxPatch((g["l"], top - HH), BW, HH,
                                    boxstyle="round,pad=0,rounding_size=1.6",
                                    fc=TFC, ec=EC, lw=1.1, zorder=4))
        ax.plot([g["l"], g["r"]], [top - HH, top - HH], color=EC, lw=1.1, zorder=5)
        ax.text(cx, top - HH / 2, name, ha="center", va="center",
                fontsize=7.4, fontweight="bold", color=TC, zorder=6)
        y0 = top - HH - PD - LH / 2
        for i, (col, typ, tag) in enumerate(rows):
            yy = y0 - i * LH
            row = ax.text(g["l"] + 1.5, yy, f"{col} : {typ}", ha="left", va="center",
                          fontsize=5.5, color=tag_color(tag), zorder=6)
            if tag:
                pending.append((row, tag, yy, g))
    ax.figure.canvas.draw()
    inv = ax.transData.inverted()
    for row, tag, yy, g in pending:
        bb = row.get_window_extent()
        x_end = inv.transform((bb.x1, bb.y0))[0]
        ax.text(x_end + 0.9, yy, tag, ha="left", va="center",
                fontsize=5.0, color=tag_color(tag), fontweight="bold", zorder=6)


def edge_label(ax, pa, pb, text, rad, override):
    """Place a white-boxed relationship label on one FK edge (fixed point when given).

    Caller: draw_fk_arrows; Callee: none.
    """
    if override is not None:
        ax.text(override[0], override[1], text, fontsize=5.6, color=AC, ha="center",
                va="center", zorder=6,
                bbox=dict(fc="white", ec="none", alpha=0.9, pad=0.8))
        return
    mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    ln = max((dx * dx + dy * dy) ** 0.5, 1e-6)
    ax.text(mx - dy / ln * 3.0, my + dx / ln * 3.0, text, fontsize=5.6,
            color=AC, ha="center", va="center", zorder=6,
            bbox=dict(fc="white", ec="none", alpha=0.9, pad=0.8))


def draw_fk_arrows(ax):
    """Draw parent-to-child FK arcs annotated with verb phrases and 1:N cardinality.

    Caller: render_erd; Callee: box_geo, edge_point, edge_label.
    """
    for src, dst, verb, ss, ds, sof, dof, rad, lx, ly in ARROWS:
        pa = edge_point(box_geo(src), ss, sof)
        pb = edge_point(box_geo(dst), ds, dof)
        ax.add_patch(FancyArrowPatch(pa, pb, arrowstyle="-|>", mutation_scale=9,
                                     lw=0.9, color=AC, shrinkA=1.5, shrinkB=2.5,
                                     connectionstyle=f"arc3,rad={rad}", zorder=2))
        edge_label(ax, pa, pb, f"{verb} 1:N", rad, None if lx is None else (lx, ly))


def draw_legend(ax):
    """Draw the color-key legend (PK/FK/UK/plain + arrow reading) bottom-center.

    Caller: render_erd; Callee: none.
    """
    ax.add_patch(FancyBboxPatch((130, 33), 54, 21,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                fc="white", ec="#BDC3C7", lw=0.8, zorder=3))
    items = [("id : INTEGER", "PK", PC), ("skill_id : INTEGER", "FK", "#148F77"),
             ("email : VARCHAR", "UK", UKC), ("full_name : VARCHAR", "", GRC)]
    for i, (sample, tag, color) in enumerate(items):
        yy = 50.5 - i * 4.2
        ax.text(132.5, yy, sample, fontsize=5.4, color=color, va="center", zorder=6)
        if tag:
            ax.text(169, yy, tag, fontsize=5.2, color=color, va="center",
                    fontweight="bold", zorder=6)
    ax.text(157, 35.4, "arrow: parent \u2192 child (1:N)", fontsize=5.2, color=GRC,
            ha="center", va="center", zorder=6)


def render_erd():
    """Compose the ERD sheet (domain tags, self-loop, typed tables, verb arrows, legend).

    Caller: main; Callee: draw_tables, draw_fk_arrows, draw_legend.
    """
    fig, ax = plt.subplots(figsize=(14.2, 10.6))
    ax.set_xlim(14, 292)
    ax.set_ylim(28, 258)
    ax.set_aspect("equal")
    ax.axis("off")
    for label, hx, hy in DOMAINS:
        ax.text(hx, hy, label, ha="center", va="center", fontsize=9.5,
                fontweight="bold", color="#7B241C")
    g = box_geo("categories")
    ax.add_patch(FancyArrowPatch((g["r"], g["t"] - 4.0), (g["r"], g["b"] + 4.0),
                                 arrowstyle="-|>", mutation_scale=9, lw=0.9, color=AC,
                                 connectionstyle="arc3,rad=-1.25", zorder=2))
    ax.text(g["r"] + 10.5, g["cy"], "parent of 1:N", fontsize=5.6, color=AC,
            ha="center", va="center", zorder=6,
            bbox=dict(fc="white", ec="none", alpha=0.9, pad=0.8))
    draw_tables(ax)
    draw_fk_arrows(ax)
    draw_legend(ax)
    fig.savefig(ASSETS / "erd.png", dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def draw_actor(ax, x, y, label):
    """Draw one stick-figure actor (head, body, arms, legs) with a name underneath.

    Caller: render_usecase; Callee: none.
    """
    ax.add_patch(Circle((x, y + 8.2), 2.1, fc="white", ec=TC, lw=1.2, zorder=4))
    for xs, ys in [((x, x), (y + 6.1, y - 0.5)),
                   ((x - 3.2, x + 3.2), (y + 3.6, y + 3.6)),
                   ((x, x - 3.2), (y - 0.5, y - 5.6)),
                   ((x, x + 3.2), (y - 0.5, y - 5.6))]:
        ax.plot(xs, ys, color=TC, lw=1.2, zorder=4)
    ax.text(x, y - 8.6, label, ha="center", va="center", fontsize=8.5,
            fontweight="bold", color=TC)


def draw_uc_ellipses(ax, ellipses, extras):
    """Draw use-case ellipses plus extra ellipses; return all centers by index.

    Caller: render_usecase; Callee: none.
    """
    centers = []
    for x, y, txt in ellipses:
        ax.add_patch(Ellipse((x, y), 33, 9.2, fc="#FBFCFE", ec=AC, lw=1.1, zorder=3))
        ax.text(x, y, txt, ha="center", va="center", fontsize=6.2, color=TC, zorder=4)
        centers.append((x, y))
    for x, y, w, h, txt in extras:
        ax.add_patch(Ellipse((x, y), w, h, fc="#F4ECF7", ec=PUR, lw=1.0, zorder=3))
        ax.text(x, y, txt, ha="center", va="center", fontsize=5.6, color="#5B2C6F", zorder=4)
        centers.append((x, y))
    return centers


def draw_assoc(ax, centers, assoc, ay):
    """Draw actor association lines, routing far-column ones through the mid corridor.

    Caller: render_usecase; Callee: none.
    """
    for idx, wp in assoc:
        x, y = centers[idx]
        start = (10.5, ay)
        if wp is None:
            ax.plot([start[0], x - 16.5], [ay, y], color=GRC, lw=0.8, alpha=0.55, zorder=1)
        else:
            ax.plot([start[0], wp[0]], [ay, wp[1]], color=GRC, lw=0.8, alpha=0.55, zorder=1)
            ax.plot([wp[0], x - 16.5], [wp[1], y], color=GRC, lw=0.8, alpha=0.55, zorder=1)


def draw_dash(ax, centers, dash):
    """Draw dashed include/extend arrows (from extension/base per UML) with tags.

    Caller: render_usecase; Callee: none.
    """
    for i, j, tag, rad in dash:
        (x1, y1), (x2, y2) = centers[i], centers[j]
        sx = x1 + (14 if x2 > x1 else -14 if x2 < x1 else 0)
        sy = y1 + (4.0 if abs(x2 - x1) < 2 else -2.5 if y2 < y1 else 2.5)
        tx = x2 - (14 if x2 > x1 else -14 if x2 < x1 else 0)
        ty = y2 - (4.0 if abs(x2 - x1) < 2 else -2.5 if y2 < y1 else 2.5)
        ax.add_patch(FancyArrowPatch((sx, sy), (tx, ty), arrowstyle="-|>",
                                     mutation_scale=8, lw=0.9, linestyle="--",
                                     color=PUR, connectionstyle=f"arc3,rad={rad}",
                                     zorder=2))
        ax.text(sx + (tx - sx) * 0.78, sy + (ty - sy) * 0.78 + 1.8, tag, fontsize=5.6,
                color=PUR, ha="center", va="center", zorder=4,
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))


def render_usecase(cfg, out_name):
    """Render one use-case diagram (actor, boundary, ellipses, assoc, dashed, extras).

    Caller: main; Callee: draw_actor, draw_uc_ellipses, draw_assoc, draw_dash.
    """
    fig, ax = plt.subplots(figsize=(11.5, 9.0))
    ax.set_xlim(0, 118)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((12, 4), 84, 92, fc="#FDFEFF", ec=TC, lw=1.3, zorder=0))
    ax.text(54, 92.6, cfg["title"], ha="center", va="center", fontsize=10,
            fontweight="bold", color=TC)
    draw_actor(ax, cfg["actor"][1], cfg["actor"][2], cfg["actor"][0])
    extras = cfg.get("extra", [])
    centers = draw_uc_ellipses(ax, cfg["ellipses"], extras)
    draw_assoc(ax, centers, cfg["assoc"], cfg["actor"][2])
    draw_dash(ax, centers, cfg["dash"])
    fig.savefig(ASSETS / out_name, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def main():
    """Create the assets directory and render all three report diagrams, printing sizes.

    Caller: CLI (__main__); Callee: render_erd, render_usecase.
    """
    ASSETS.mkdir(parents=True, exist_ok=True)
    render_erd()
    render_usecase(STUDENT, "usecase-student.png")
    render_usecase(ADMIN, "usecase-admin.png")
    for png in sorted(ASSETS.glob("*.png")):
        print(f"{png.name}: {png.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
