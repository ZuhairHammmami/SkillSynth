"""Render the three deterministic report diagrams (ERD + student/admin use cases) as PNGs.

Caller: repository gates (.venv/bin/python scripts/render_report_diagrams.py); callee: matplotlib
Agg primitives writing fixed-layout figures into docs/report/assets/. Every layout is hardcoded
(no randomness), labels are English-only, so Arabic shaping libraries are intentionally unused.
Schema truth: src/migrations/003_reduced_schema.sql + docs/40-diagrams/ERD.md (15 tables).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Ellipse, Rectangle

ASSETS = Path(__file__).resolve().parents[1] / "docs" / "report" / "assets"
DPI = 200
BW, HH, LH, PD = 32.0, 4.6, 3.1, 1.2
FC, EC, TFC, TC = "#F7F9FC", "#2C3E50", "#DCE6F1", "#1B2631"
AC, PC, UKC, GRC = "#34495E", "#1F618D", "#6C3483", "#4D5656"

TABLES = {
    "users": (120, 170, ["PK id", "UK email", "full_name", "is_admin"]),
    "categories": (36, 170, ["PK id", "UK name", "FK parent_id"]),
    "skills": (70, 126, ["PK id", "UK name", "FK category_id", "difficulty_level"]),
    "skill_prerequisites": (34, 120, ["PK+FK skill_id", "PK+FK prerequisite_id"]),
    "job_roles": (34, 56, ["PK id", "UK title", "career_field"]),
    "job_role_skills": (72, 22, ["PK+FK job_role_id", "PK+FK skill_id"]),
    "resources": (34, 88, ["PK id", "title", "type", "FK skill_id"]),
    "user_skills": (104, 126, ["PK+FK user_id", "PK+FK skill_id", "proficiency_level"]),
    "paths": (152, 126, ["PK id", "FK user_id", "target_role", "status"]),
    "path_steps": (118, 78, ["PK id", "FK path_id", "FK skill_id", "position"]),
    "step_progress": (160, 44, ["PK+FK user_id", "PK+FK step_id", "completed_at", "score"]),
    "assessments": (196, 150, ["PK id", "title", "pass_score", "FK skill_id"]),
    "assessment_questions": (196, 110, ["PK id", "FK assessment_id", "prompt", "JSON options"]),
    "assessment_results": (196, 64, ["PK id", "FK user_id", "FK assessment_id", "score", "passed"]),
    "activity_log": (196, 22, ["PK id", "FK user_id", "action", "JSON data"]),
}

ARROWS = [
    ("categories", "skills", "bottom", "top", -0.10, 0.10, 0.08),
    ("skills", "skill_prerequisites", "left", "right", 0.28, 0.28, -0.18),
    ("skills", "skill_prerequisites", "left", "right", -0.28, -0.28, 0.22),
    ("job_roles", "job_role_skills", "bottom", "top", 0.00, 0.20, 0.06),
    ("skills", "job_role_skills", "bottom", "right", 0.30, 0.00, -0.05),
    ("skills", "resources", "left", "right", -0.50, 0.50, 0.12),
    ("skills", "assessments", "top", "left", 0.30, -0.30, 0.07),
    ("assessments", "assessment_questions", "bottom", "top", 0.0, 0.0, 0.0),
    ("users", "assessment_results", "right", "right", 0.30, 0.35, -0.30),
    ("assessments", "assessment_results", "right", "right", 0.35, 0.10, -0.38),
    ("users", "user_skills", "bottom", "top", -0.35, 0.00, -0.05),
    ("skills", "user_skills", "right", "left", 0.00, 0.00, 0.02),
    ("users", "paths", "bottom", "top", 0.35, 0.20, -0.06),
    ("paths", "path_steps", "bottom", "top", 0.10, -0.10, -0.05),
    ("skills", "path_steps", "bottom", "left", 0.45, 0.35, 0.05),
    ("users", "step_progress", "bottom", "top", 0.15, 0.00, 0.03),
    ("path_steps", "step_progress", "right", "left", 0.20, -0.20, -0.08),
    ("users", "activity_log", "right", "right", -0.10, -0.35, -0.46),
]

DOMAINS = [
    ("IDENTITY", 120, 178),
    ("CATALOG", 55, 178),
    ("LEARNING", 139, 141),
    ("ASSESSMENT", 196, 161),
    ("ENGAGEMENT", 196, 32.5),
]

STUDENT = {
    "actor": ("Student", 7, 50),
    "title": "SkillSynth",
    "ellipses": [
        (40, 80, "Register / Login"), (76, 80, "Run Diagnostic Wizard"),
        (40, 62, "Generate Learning Path"), (76, 62, "Review AI Results"),
        (40, 44, "Complete Steps"), (76, 44, "Take Practice Test"),
        (40, 26, "Request Explanation"), (76, 26, "View Analytics"),
    ],
    "assoc": [0, 1, 2, 4, 5, 6, 7],
    "dash": [(2, 3, "\u00abinclude\u00bb"), (5, 4, "\u00abextend\u00bb"), (6, 4, "\u00abextend\u00bb")],
}

ADMIN = {
    "actor": ("Admin", 7, 50),
    "title": "SkillSynth",
    "ellipses": [
        (38, 86, "Manage Users"), (74, 86, "Manage Skills"),
        (38, 71, "Manage Resources"), (74, 71, "Manage Categories"),
        (38, 56, "View Audit Log"), (74, 56, "Manage Job Roles"),
        (38, 41, "Live Events Feed"), (74, 41, "Aggregate Reports"),
        (38, 26, "Feature Flags"), (74, 26, "DB Inspector"),
    ],
    "assoc": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    "dash": [],
    "note": (56, 12, 30, 8, "Force Delete\nGuarded Entities"),
    "note_arrows": [(1, 54.0), (3, 56.0), (5, 58.0)],
}


def box_geo(name):
    """Return the rectangle geometry (l/r/t/b/cx/cy/h) for one table box.

    Caller: _draw_table, _edge_point; Callee: TABLES lookup.
    """
    cx, top, rows = TABLES[name]
    h = HH + PD + len(rows) * LH
    return {"l": cx - BW / 2, "r": cx + BW / 2, "t": top, "b": top - h,
            "cx": cx, "cy": top - h / 2, "h": h}


def edge_point(g, side, off):
    """Return an anchor point on one box edge, offset by a fraction of the half-extent.

    Caller: _draw_fk_arrows; Callee: box_geo-supplied dict g.
    """
    if side == "top":
        return (g["cx"] + off * BW / 2, g["t"])
    if side == "bottom":
        return (g["cx"] + off * BW / 2, g["b"])
    if side == "left":
        return (g["l"], g["cy"] + off * g["h"] / 2)
    return (g["r"], g["cy"] + off * g["h"] / 2)


def col_color(label):
    """Map a column row label to its ink color (PK navy, FK teal, UK purple, plain gray).

    Caller: _draw_tables; Callee: none.
    """
    if label.startswith("PK"):
        return PC
    if label.startswith("FK"):
        return AC
    if label.startswith("UK"):
        return UKC
    return GRC


def draw_tables(ax):
    """Draw all 15 rounded table boxes with title bars and key-column lists.

    Caller: render_erd; Callee: box_geo, col_color.
    """
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
                fontsize=7.6, fontweight="bold", color=TC, zorder=6)
        y0 = top - HH - PD - LH / 2
        for i, row in enumerate(rows):
            ax.text(g["l"] + 1.6, y0 - i * LH, row, ha="left", va="center",
                    fontsize=6.4, color=col_color(row), zorder=6)


def draw_fk_arrows(ax):
    """Draw the 18 straight/curved parent-to-child FK arrows with 1:N cardinality labels.

    Caller: render_erd; Callee: box_geo, edge_point.
    """
    for src, dst, ss, ds, sof, dof, rad in ARROWS:
        pa = edge_point(box_geo(src), ss, sof)
        pb = edge_point(box_geo(dst), ds, dof)
        ax.add_patch(FancyArrowPatch(pa, pb, arrowstyle="-|>", mutation_scale=9,
                                     lw=0.9, color=AC, shrinkA=1.5, shrinkB=2.5,
                                     connectionstyle=f"arc3,rad={rad}", zorder=2))
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        ln = max((dx * dx + dy * dy) ** 0.5, 1e-6)
        ax.text(mx - dy / ln * 2.4, my + dx / ln * 2.4, "1:N", fontsize=5.6,
                color=AC, ha="center", va="center", zorder=6,
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.6))


def render_erd():
    """Compose the full ERD sheet (domain headers, self-loop, tables, FK arrows) to erd.png.

    Caller: main; Callee: draw_tables, draw_fk_arrows.
    """
    fig, ax = plt.subplots(figsize=(11.8, 9.06))
    ax.set_xlim(-4, 246)
    ax.set_ylim(-6, 186)
    ax.set_aspect("equal")
    ax.axis("off")
    for label, hx, hy in DOMAINS:
        ax.text(hx, hy, label, ha="center", va="center", fontsize=9.5,
                fontweight="bold", color="#7B241C")
    g = box_geo("categories")
    ax.add_patch(FancyArrowPatch((g["r"], g["t"] - 4.2), (g["r"], g["b"] + 4.2),
                                 arrowstyle="-|>", mutation_scale=9, lw=0.9, color=AC,
                                 connectionstyle="arc3,rad=-1.25", zorder=2))
    ax.text(g["r"] + 9.5, g["cy"], "1:N", fontsize=5.6, color=AC, ha="center",
            va="center", bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.6))
    draw_tables(ax)
    draw_fk_arrows(ax)
    fig.savefig(ASSETS / "erd.png", dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def draw_actor(ax, x, y, label):
    """Draw one stick-figure actor with a name label underneath.

    Caller: render_usecase; Callee: none.
    """
    ax.add_patch(Circle((x, y + 8.2), 2.1, fc="white", ec=TC, lw=1.2, zorder=4))
    for xs, ys in [([(x, x)], [(y + 6.1, y - 0.5)]), ([(x - 3.2, x + 3.2)], [(y + 3.6, y + 3.6)]),
                   ([(x, x - 3.2)], [(y - 0.5, y - 5.6)]), ([(x, x + 3.2)], [(y - 0.5, y - 5.6)])]:
        ax.plot(xs, ys, color=TC, lw=1.2, zorder=4)
    ax.text(x, y - 8.6, label, ha="center", va="center", fontsize=8.5,
            fontweight="bold", color=TC)


def draw_uc_ellipses(ax, ellipses):
    """Draw the use-case ellipses and return their centers indexed like the input list.

    Caller: render_usecase; Callee: none.
    """
    centers = []
    for x, y, txt in ellipses:
        ax.add_patch(Ellipse((x, y), 29, 9.2, fc="#FBFCFE", ec=AC, lw=1.1, zorder=3))
        ax.text(x, y, txt, ha="center", va="center", fontsize=6.6, color=TC, zorder=4)
        centers.append((x, y))
    return centers


def draw_uc_links(ax, centers, assoc, dash):
    """Draw solid actor association lines and dashed include/extend arrows between use cases.

    Caller: render_usecase; Callee: none.
    """
    for idx in assoc:
        x, y = centers[idx]
        ax.plot([13.5, x - 14.5], [50, y], color=GRC, lw=0.8, alpha=0.55, zorder=1)
    for i, j, tag in dash:
        (x1, y1), (x2, y2) = centers[i], centers[j]
        ax.add_patch(FancyArrowPatch((x1 + (13 if x1 < x2 else -13), y1),
                                     (x2 + (-13 if x1 < x2 else 13), y2),
                                     arrowstyle="-|>", mutation_scale=8, lw=0.9,
                                     linestyle="--", color="#8E44AD",
                                     connectionstyle="arc3,rad=0.12", zorder=2))
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 1.6, tag, fontsize=5.8,
                color="#8E44AD", ha="center", zorder=4)


def render_usecase(cfg, out_name):
    """Render one use-case diagram (actor, boundary, ellipses, links, optional extend-note).

    Caller: main; Callee: draw_actor, draw_uc_ellipses, draw_uc_links.
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
    centers = draw_uc_ellipses(ax, cfg["ellipses"])
    draw_uc_links(ax, centers, cfg["assoc"], cfg["dash"])
    if "note" in cfg:
        nx, ny, nw, nh, ntxt = cfg["note"]
        ax.add_patch(FancyBboxPatch((nx - nw / 2, ny - nh / 2), nw, nh,
                                    boxstyle="round,pad=0,rounding_size=1.2",
                                    fc="#F4ECF7", ec="#8E44AD", lw=1.0, zorder=3))
        ax.text(nx, ny, ntxt, ha="center", va="center", fontsize=6.0,
                color="#5B2C6F", zorder=4)
        for idx, sx in cfg["note_arrows"]:
            tx, ty = centers[idx]
            ax.add_patch(FancyArrowPatch((sx, ny + nh / 2), (tx - 14.5, ty),
                                         arrowstyle="-|>", mutation_scale=8, lw=0.9,
                                         linestyle="--", color="#8E44AD", zorder=2))
        ax.text(56.5, 47, "\u00abextend\u00bb", fontsize=5.8, color="#8E44AD",
                ha="center", va="center", rotation=90, zorder=4,
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))
    fig.savefig(ASSETS / out_name, dpi=DPI, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def main():
    """Create the assets directory and render all three report diagrams, printing byte sizes.

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
