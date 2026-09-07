#!/usr/bin/env python3
"""Generate high-quality ERD (PNG + PDF) for SkillSynth 15-table schema.

Core-only columns (no JSON/CK/timestamps), all FK links fixed, domain
clusters, cardinality labels (1/N) at each edge end, and a legend.

Caller: run standalone — `python tools/generate_erd.py`
Callee: graphviz Python package + system `dot` binary

Note: Documented exception to the 300-line limit — data-heavy generation
script with inline schema definitions (like seed_v4.py).
"""

from __future__ import annotations

import graphviz
from pathlib import Path

# ── Output paths ────────────────────────────────────────────────────
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "40-diagrams"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PNG_PATH = OUT_DIR / "skillsynth-erd.png"
PDF_PATH = OUT_DIR / "skillsynth-erd.pdf"

# ── Domain palette ──────────────────────────────────────────────────
# (header_bg, header_fg, cluster_fill)
DOMAIN_STYLE: dict[str, tuple[str, str, str]] = {
    "Identity":   ("#334155", "#FFFFFF", "#F1F5F9"),
    "Catalog":    ("#15803D", "#FFFFFF", "#F0FDF4"),
    "Assessment": ("#B45309", "#FFFFFF", "#FFFBEB"),
    "Learning":   ("#7E22CE", "#FFFFFF", "#FAF5FF"),
    "Engagement": ("#475569", "#FFFFFF", "#F8FAFC"),
}

# ── Schema: table → (domain, [(column, type, badge), ...]) ──────────
# Badges: "PK", "FK", "UK", or "PK,FK" for junction tables.
# Core-only: no JSON, no CHECK-annotated, no timestamps, no cosmetic cols.
SCHEMA: dict[str, tuple[str, list[tuple[str, str, str]]]] = {
    # ── Identity ────────────────────────────────────────────────────
    "users": (
        "Identity",
        [
            ("id",         "INTEGER", "PK"),
            ("email",      "VARCHAR", "UK"),
            ("full_name",  "VARCHAR", ""),
            ("is_admin",   "BOOLEAN", ""),
        ],
    ),
    # ── Catalog ─────────────────────────────────────────────────────
    "categories": (
        "Catalog",
        [
            ("id",          "INTEGER", "PK"),
            ("name",        "VARCHAR", "UK"),
            ("parent_id",   "INTEGER", "FK"),
        ],
    ),
    "skills": (
        "Catalog",
        [
            ("id",               "INTEGER", "PK"),
            ("name",             "VARCHAR", "UK"),
            ("difficulty_level", "INTEGER", ""),
            ("estimated_hours",  "REAL",    ""),
            ("category_id",      "INTEGER", "FK"),
        ],
    ),
    "skill_prerequisites": (
        "Catalog",
        [
            ("skill_id",        "INTEGER", "PK,FK"),
            ("prerequisite_id", "INTEGER", "PK,FK"),
        ],
    ),
    "job_roles": (
        "Catalog",
        [
            ("id",           "INTEGER", "PK"),
            ("title",        "VARCHAR", "UK"),
            ("career_field", "VARCHAR", ""),
        ],
    ),
    "job_role_skills": (
        "Catalog",
        [
            ("job_role_id", "INTEGER", "PK,FK"),
            ("skill_id",    "INTEGER", "PK,FK"),
        ],
    ),
    "resources": (
        "Catalog",
        [
            ("id",        "INTEGER", "PK"),
            ("title",     "VARCHAR", ""),
            ("type",      "VARCHAR", ""),
            ("skill_id",  "INTEGER", "FK"),
        ],
    ),
    # ── Assessment ──────────────────────────────────────────────────
    "assessments": (
        "Assessment",
        [
            ("id",          "INTEGER", "PK"),
            ("skill_id",    "INTEGER", "FK"),
            ("title",       "VARCHAR", ""),
            ("pass_score",  "INTEGER", ""),
        ],
    ),
    "assessment_questions": (
        "Assessment",
        [
            ("id",            "INTEGER", "PK"),
            ("assessment_id", "INTEGER", "FK"),
            ("position",      "INTEGER", ""),
            ("prompt",        "TEXT",    ""),
            ("correct_index", "INTEGER", ""),
        ],
    ),
    "assessment_results": (
        "Assessment",
        [
            ("id",            "INTEGER", "PK"),
            ("user_id",       "INTEGER", "FK"),
            ("assessment_id", "INTEGER", "FK"),
            ("score",         "INTEGER", ""),
            ("passed",        "BOOLEAN", ""),
        ],
    ),
    # ── Learning ────────────────────────────────────────────────────
    "user_skills": (
        "Learning",
        [
            ("user_id",           "INTEGER", "PK,FK"),
            ("skill_id",          "INTEGER", "PK,FK"),
            ("proficiency_level", "INTEGER", ""),
        ],
    ),
    "paths": (
        "Learning",
        [
            ("id",          "INTEGER", "PK"),
            ("user_id",     "INTEGER", "FK"),
            ("title",       "VARCHAR", ""),
            ("status",      "VARCHAR", ""),
            ("target_role", "VARCHAR", ""),
        ],
    ),
    "path_steps": (
        "Learning",
        [
            ("id",              "INTEGER", "PK"),
            ("path_id",         "INTEGER", "FK"),
            ("skill_id",        "INTEGER", "FK"),
            ("position",        "INTEGER", ""),
            ("title",           "VARCHAR", ""),
            ("estimated_hours", "INTEGER", ""),
        ],
    ),
    "step_progress": (
        "Learning",
        [
            ("user_id", "INTEGER", "PK,FK"),
            ("step_id", "INTEGER", "PK,FK"),
            ("score",   "INTEGER", ""),
        ],
    ),
    # ── Engagement ──────────────────────────────────────────────────
    "activity_log": (
        "Engagement",
        [
            ("id",       "INTEGER", "PK"),
            ("user_id",  "INTEGER", "FK"),
            ("category", "VARCHAR", ""),
            ("action",   "VARCHAR", ""),
        ],
    ),
}

# ── Relationship edges ──────────────────────────────────────────────
# (from_table, from_port, to_table, to_port, label, optional, mn)
# optional=True → dashed line (SET NULL FK), False → solid (CASCADE).
# mn=True → edge participates in a many-to-many junction relationship.
EDGES: list[tuple[str, str, str, str, str, bool, bool]] = [
    ("categories",  "id",       "categories",  "parent_id",  "has child",       True,  False),
    ("categories",  "id",       "skills",      "category_id","classifies",      True,  False),
    ("skills",      "id",       "skill_prerequisites", "skill_id", "M:N prerequisite DAG", False, True),
    ("skills",      "id",       "resources",   "skill_id",   "linked to",       True,  False),
    ("skills",      "id",       "assessments", "skill_id",   "assessed by",     True,  False),
    ("job_roles",   "id",       "job_role_skills","job_role_id","M:N composed of",False, True),
    ("skills",      "id",       "job_role_skills","skill_id","M:N required by", False, True),
    ("users",       "id",       "user_skills", "user_id",    "M:N has proficiency",False,True),
    ("skills",      "id",       "user_skills", "skill_id",   "M:N mastered by", False, True),
    ("users",       "id",       "paths",       "user_id",    "owns",            False, False),
    ("users",       "id",       "assessment_results","user_id","attempts",      False, False),
    ("users",       "id",       "step_progress","user_id",   "completes",       False, False),
    ("users",       "id",       "activity_log","user_id",    "logs",            True,  False),
    ("assessments", "id",       "assessment_questions","assessment_id","contains",False,False),
    ("assessments", "id",       "assessment_results","assessment_id","scored by",False,False),
    ("paths",       "id",       "path_steps",  "path_id",    "contains",        False, False),
    ("skills",      "id",       "path_steps",  "skill_id",   "scheduled in",    True,  False),
    ("path_steps",  "id",       "step_progress","step_id",   "tracked by",      False, False),
]


def _esc(text: str) -> str:
    """Escape HTML entities for Graphviz HTML labels."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _badge_html(badges: str) -> str:
    """Render badge string as coloured inline HTML FONT elements."""
    if not badges:
        return ""
    tokens: list[str] = []
    for b in (b.strip() for b in badges.split(",")):
        if b == "PK":
            tokens.append('<FONT FACE="Courier" COLOR="#DC2626"><B>PK</B></FONT>')
        elif b == "FK":
            tokens.append('<FONT FACE="Courier" COLOR="#2563EB">FK</FONT>')
        elif b == "UK":
            tokens.append('<FONT FACE="Courier" COLOR="#7C3AED">UK</FONT>')
    return "  ".join(tokens)


def _build_table_html(name: str, domain: str, columns: list[tuple[str, str, str]]) -> str:
    """Build a Graphviz HTML TABLE label with column PORT attributes for each row."""
    bg, fg, _ = DOMAIN_STYLE[domain]
    rows: list[str] = []
    rows.append(
        f'<TR><TD COLSPAN="3" BGCOLOR="{bg}" ALIGN="CENTER">'
        f'<FONT POINT-SIZE="13" COLOR="{fg}"><B>{_esc(name)}</B></FONT>'
        f'</TD></TR>'
    )
    rows.append(
        f'<TR><TD COLSPAN="3" BGCOLOR="{bg}" ALIGN="CENTER">'
        f'<FONT POINT-SIZE="9" COLOR="{fg}">{_esc(domain)}</FONT>'
        f'</TD></TR>'
    )
    rows.append(
        '<TR><TD COLSPAN="3" BGCOLOR="#CBD5E1"></TD></TR>'
    )
    for col, col_type, badge in columns:
        badge_html = _badge_html(badge)
        rows.append(
            f'<TR>'
            f'<TD PORT="{col}" ALIGN="LEFT"><FONT FACE="Courier" POINT-SIZE="11">'
            f'{_esc(col)}</FONT></TD>'
            f'<TD ALIGN="LEFT"><FONT FACE="Courier" POINT-SIZE="10" COLOR="#6B7280">'
            f'{_esc(col_type)}</FONT></TD>'
            f'<TD ALIGN="RIGHT">{badge_html}</TD>'
            f'</TR>'
        )
    tbl = "\n".join(rows)
    return (
        f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5"'
        f' BGCOLOR="#FFFFFF">'
        f'\n{tbl}\n</TABLE>>'
    )


def _build_legend_html() -> str:
    """Build a Graphviz HTML TABLE label for the ERD legend."""
    badges = (
        '<FONT FACE="Courier" COLOR="#DC2626"><B>PK</B></FONT>'
        '  <FONT FACE="Courier" COLOR="#2563EB">FK</FONT>'
        '  <FONT FACE="Courier" COLOR="#7C3AED">UK</FONT>'
    )
    lines = (
        '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="4" CELLPADDING="3">'
        '<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="12"><B>Legend</B></FONT></TD></TR>'
        '<TR><TD COLSPAN="2"></TD></TR>'
        f'<TR><TD ALIGN="LEFT">{badges}</TD>'
        '<TD ALIGN="LEFT"><FONT POINT-SIZE="10">= Primary Key / Foreign Key / Unique Key</FONT></TD></TR>'
        '<TR><TD COLSPAN="2"></TD></TR>'
        '<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">────</FONT></TD>'
        '<TD ALIGN="LEFT"><FONT POINT-SIZE="10">Required FK (CASCADE / NOT NULL)</FONT></TD></TR>'
        '<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">- - -</FONT></TD>'
        '<TD ALIGN="LEFT"><FONT POINT-SIZE="10">Optional FK (SET NULL)</FONT></TD></TR>'
        '<TR><TD COLSPAN="2"></TD></TR>'
        '<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">1 ─── N</FONT></TD>'
        '<TD ALIGN="LEFT"><FONT POINT-SIZE="10">One-to-Many cardinality</FONT></TD></TR>'
        '<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">N : N</FONT></TD>'
        '<TD ALIGN="LEFT"><FONT POINT-SIZE="10">Many-to-Many (junction table, composite PK)</FONT></TD></TR>'
        '</TABLE>'
    )
    return f'<{lines}>'


def build_graph() -> graphviz.Digraph:
    """Construct the ERD digraph with domain clusters, port-based edges, and legend."""
    dot = graphviz.Digraph(
        "SkillSynth_ERD",
        format="png",
        engine="dot",
        graph_attr={
            "rankdir":   "TB",
            "bgcolor":   "#FFFFFF",
            "dpi":       "300",
            "pad":       "0.6",
            "nodesep":   "0.7",
            "ranksep":   "1.2",
            "splines":   "ortho",
            "fontname":  "Helvetica",
            "label": (
                "SkillSynth — Entity Relationship Diagram"
                "\\n15 tables · strict 3NF · SQLite / PostgreSQL"
                "\\nSolid = required FK · Dashed = optional FK · "
                "N:N = many-to-many junction · 1:N = one-to-many"
            ),
            "labelloc":  "t",
            "labeljust": "c",
            "fontsize":  "14",
        },
        node_attr={"shape": "none", "fontname": "Helvetica"},
        edge_attr={
            "fontname":   "Helvetica",
            "fontsize":   "9",
            "color":      "#94A3B8",
            "arrowsize":  "0.6",
            "minlen":     "2",
            "labeldistance": "1.8",
            "labelangle": "-15",
        },
    )

    # ── Add table nodes (grouped by domain cluster) ─────────────
    for domain in DOMAIN_STYLE:
        fill = DOMAIN_STYLE[domain][2]
        with dot.subgraph(name=f"cluster_{domain}") as s:
            s.attr(
                label=f"  {domain}  ",
                style="rounded,filled",
                color="#CBD5E1",
                fillcolor=fill,
                fontname="Helvetica",
                fontsize="13",
                fontcolor="#334155",
                penwidth="1.5",
            )
            # Widest spacing inside Catalog cluster: it hosts the skills hub
            if domain == "Catalog":
                s.attr(nodesep="1.1", ranksep="1.4", compound="true")
            for tbl_name, (tbl_domain, cols) in SCHEMA.items():
                if tbl_domain == domain:
                    s.node(tbl_name, label=_build_table_html(tbl_name, tbl_domain, cols))

    # ── Add relationship edges (port-to-port; M:N junction => both ends N) ──
    # Use xlabel for the verb: ortho splines drop edge `label`, but xlabel renders
    # independently of path geometry. taillabel/headlabel keep the 1/N markers.
    for from_tbl, from_port, to_tbl, to_port, label, optional, mn in EDGES:
        edge_style = "dashed" if optional else "solid"
        if mn:
            taillabel = "N"
            headlabel = "N"
        else:
            taillabel = "1"
            headlabel = "N"
        dot.edge(
            f"{from_tbl}:{from_port}",
            f"{to_tbl}:{to_port}",
            xlabel=f"  {label}  ",
            style=edge_style,
            dir="none",
            taillabel=taillabel,
            headlabel=headlabel,
        )

    # ── Legend (unconnected, forced to bottom rank) ─────────────
    dot.node("legend", label=_build_legend_html(), shape="none", rank="sink")
    dot.body.append('  { rank=sink; legend }')

    return dot


def main() -> None:
    """Render ERD to PNG and PDF."""
    print("Building SkillSynth ERD graph...")
    dot = build_graph()

    print(f"Rendering PNG → {PNG_PATH}")
    dot.format = "png"
    dot.render(str(PNG_PATH.with_suffix("")), cleanup=True)
    print(f"  ✓ {PNG_PATH} ({PNG_PATH.stat().st_size / 1024:.0f} KB)")

    print(f"Rendering PDF → {PDF_PATH}")
    dot.format = "pdf"
    dot.render(str(PDF_PATH.with_suffix("")), cleanup=True)
    print(f"  ✓ {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.0f} KB)")

    print("\nDone. ERD generated successfully.")


if __name__ == "__main__":
    main()
