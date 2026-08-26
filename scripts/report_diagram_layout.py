"""Layout data for the report diagrams: fully-typed 15-table ERD + accurate use-case configs.

Caller: scripts/render_report_diagrams.py; Callee: none (pure data). Schema truth:
src/migrations/003_reduced_schema.sql (columns/types/tags verbatim); feature truth:
AGENTS.md API surface + admin app pages. English-only labels by design.
"""

BW = 38
HH, PD, LH = 4.4, 1.2, 3.0

TABLES = {
    "users": (150, 240, [
        ("id", "INTEGER", "PK"), ("email", "VARCHAR", "UK"),
        ("hashed_password", "VARCHAR", ""), ("full_name", "VARCHAR", ""),
        ("is_admin", "BOOLEAN", ""), ("created_at", "TIMESTAMP", ""),
        ("updated_at", "TIMESTAMP", "")]),
    "categories": (44, 240, [
        ("id", "INTEGER", "PK"), ("name", "VARCHAR(100)", "UK"),
        ("description", "VARCHAR", ""), ("parent_id", "INTEGER", "FK")]),
    "skills": (44, 208, [
        ("id", "INTEGER", "PK"), ("name", "VARCHAR(100)", "UK"),
        ("description", "TEXT", ""), ("difficulty_level", "INTEGER", ""),
        ("estimated_hours", "INTEGER", ""), ("icon", "VARCHAR", ""),
        ("color", "VARCHAR", ""), ("category_id", "INTEGER", "FK")]),
    "skill_prerequisites": (44, 166, [
        ("skill_id", "INTEGER", "PK FK"), ("prerequisite_id", "INTEGER", "PK FK")]),
    "job_roles": (44, 64, [
        ("id", "INTEGER", "PK"), ("title", "VARCHAR(150)", "UK"),
        ("description", "TEXT", ""), ("career_field", "VARCHAR(100)", "")]),
    "job_role_skills": (110, 66, [
        ("job_role_id", "INTEGER", "PK FK"), ("skill_id", "INTEGER", "PK FK")]),
    "resources": (44, 124, [
        ("id", "INTEGER", "PK"), ("title", "VARCHAR(200)", ""),
        ("url", "VARCHAR(2000)", ""), ("type", "VARCHAR(50)", ""),
        ("language", "VARCHAR(10)", ""), ("is_free", "BOOLEAN", ""),
        ("is_official", "BOOLEAN", ""), ("author_or_platform", "VARCHAR(200)", ""),
        ("skill_id", "INTEGER", "FK")]),
    "user_skills": (110, 196, [
        ("user_id", "INTEGER", "PK FK"), ("skill_id", "INTEGER", "PK FK"),
        ("proficiency_level", "INTEGER", ""), ("last_assessed_at", "TIMESTAMP", "")]),
    "paths": (150, 196, [
        ("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK"),
        ("title", "VARCHAR(200)", ""), ("description", "TEXT", ""),
        ("target_role", "VARCHAR(150)", ""), ("status", "VARCHAR(20)", ""),
        ("total_estimated_hours", "INTEGER", ""),
        ("total_estimated_weeks", "INTEGER", ""), ("deleted_at", "TIMESTAMP", ""),
        ("created_at", "TIMESTAMP", ""), ("updated_at", "TIMESTAMP", "")]),
    "path_steps": (150, 144, [
        ("id", "INTEGER", "PK"), ("path_id", "INTEGER", "FK"),
        ("skill_id", "INTEGER", "FK"), ("position", "INTEGER", ""),
        ("title", "VARCHAR(200)", ""), ("description", "TEXT", ""),
        ("estimated_hours", "INTEGER", ""), ("resource_ids", "JSON", ""),
        ("assessment_ids", "JSON", "")]),
    "step_progress": (150, 96, [
        ("user_id", "INTEGER", "PK FK"), ("step_id", "INTEGER", "PK FK"),
        ("completed_at", "TIMESTAMP", ""), ("score", "INTEGER", "")]),
    "assessments": (250, 240, [
        ("id", "INTEGER", "PK"), ("skill_id", "INTEGER", "FK"),
        ("title", "VARCHAR(200)", ""), ("description", "TEXT", ""),
        ("pass_score", "INTEGER", ""), ("created_at", "TIMESTAMP", ""),
        ("updated_at", "TIMESTAMP", "")]),
    "assessment_questions": (250, 196, [
        ("id", "INTEGER", "PK"), ("assessment_id", "INTEGER", "FK"),
        ("position", "INTEGER", ""), ("prompt", "TEXT", ""),
        ("options", "JSON", ""), ("correct_index", "INTEGER", "")]),
    "assessment_results": (250, 156, [
        ("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK"),
        ("assessment_id", "INTEGER", "FK"), ("score", "INTEGER", ""),
        ("passed", "BOOLEAN", ""), ("completed_at", "TIMESTAMP", "")]),
    "activity_log": (250, 116, [
        ("id", "INTEGER", "PK"), ("user_id", "INTEGER", "FK"),
        ("category", "VARCHAR(20)", ""), ("action", "VARCHAR(100)", ""),
        ("entity_type", "VARCHAR(50)", ""), ("entity_id", "VARCHAR(50)", ""),
        ("data", "JSON", ""), ("ip_address", "VARCHAR(45)", ""),
        ("user_agent", "VARCHAR(255)", ""), ("created_at", "TIMESTAMP", "")]),
}

ARROWS = [
    ("categories", "skills", "has", "bottom", "top", 0.0, 0.0, 0.0, None, None),
    ("skills", "skill_prerequisites", "requires", "bottom", "top", -0.25, -0.25, -0.1, 24.0, 172.0),
    ("skills", "skill_prerequisites", "is prerequisite of", "bottom", "top", 0.25, 0.25, 0.1, 68.0, 172.0),
    ("skills", "user_skills", "measured in", "right", "left", 0.2, 0.3, 0.1, None, None),
    ("users", "user_skills", "has", "left", "right", -0.5, 0.3, -0.1, 118.0, 207.0),
    ("skills", "resources", "has", "right", "right", -0.9, 0.5, -0.12, None, None),
    ("skills", "assessments", "has", "right", "left", 0.55, 0.25, 0.05, 143.0, 203.0),
    ("skills", "path_steps", "taught in", "right", "left", -0.5, 0.3, 0.15, None, None),
    ("skills", "job_role_skills", "listed for", "right", "top", -0.55, -0.3, -0.15, None, None),
    ("job_roles", "job_role_skills", "requires", "right", "left", 0.0, 0.3, -0.1, None, None),
    ("users", "paths", "owns", "bottom", "top", 0.0, 0.0, 0.0, None, None),
    ("users", "step_progress", "makes", "left", "left", -0.7, 0.4, 0.45, None, None),
    ("users", "assessment_results", "earns", "right", "left", 0.5, 0.35, -0.18, None, None),
    ("users", "activity_log", "generates", "right", "left", 0.7, 0.4, -0.28, None, None),
    ("assessments", "assessment_questions", "contains", "bottom", "top", 0.0, 0.0, 0.0, None, None),
    ("assessments", "assessment_results", "yields", "right", "right", 0.5, 0.3, 0.4, 285.0, 186.0),
    ("paths", "path_steps", "consists of", "bottom", "top", 0.0, 0.0, 0.0, None, None),
    ("path_steps", "step_progress", "tracked by", "bottom", "top", 0.0, 0.0, 0.0, None, None),
]

DOMAINS = [
    ("CATALOG", 44, 252), ("IDENTITY", 150, 252), ("LEARNING", 108, 170),
    ("ASSESSMENT", 250, 252), ("ENGAGEMENT", 250, 72),
]

STUDENT = {
    "actor": ("Student", 7, 50),
    "title": "SkillSynth",
    "ellipses": [
        (40, 88, "Register / Login"),
        (80, 88, "Run Diagnostic Wizard"),
        (80, 71, "Take AI Diagnostic Quiz"),
        (40, 71, "Review Analysis Before Path"),
        (40, 54, "Confirm & Generate Learning Path"),
        (80, 54, "Complete Path Step"),
        (80, 37, "Undo Step Completion"),
        (40, 37, "Take Adaptive Practice Test"),
        (40, 20, "Request Result Explanation"),
        (80, 20, "View Learning Analytics"),
    ],
    "assoc": [(0, None), (1, (60.5, 88)), (4, None), (5, (60.5, 54)),
              (7, None), (9, (60.5, 20))],
    "dash": [
        (1, 2, "\u00abinclude\u00bb", 0.0),
        (1, 3, "\u00abinclude\u00bb", -0.25),
        (6, 5, "\u00abextend\u00bb", 0.0),
        (8, 7, "\u00abextend\u00bb", 0.0),
    ],
}

ADMIN = {
    "actor": ("Admin", 7, 50),
    "title": "SkillSynth",
    "ellipses": [
        (40, 88, "Manage Users"),
        (80, 88, "Manage Skills"),
        (40, 74, "Manage Resources"),
        (80, 74, "Manage Categories"),
        (40, 60, "View Audit Log"),
        (80, 60, "Manage Job Roles"),
        (40, 46, "Live Events Feed"),
        (80, 46, "Aggregate Reports"),
        (40, 32, "Feature Flags"),
        (80, 32, "System Health"),
        (40, 18, "Manage Backups"),
        (80, 18, "DB Inspector"),
    ],
    "assoc": [(0, None), (1, (60.5, 88)), (2, None), (3, (60.5, 74)),
              (4, None), (5, (60.5, 60)), (6, None), (7, (60.5, 46)),
              (8, None), (9, (60.5, 32)), (10, None), (11, (60.5, 18))],
    "dash": [
        (12, 1, "\u00abextend\u00bb", 0.12),
        (12, 3, "\u00abextend\u00bb", 0.0),
        (12, 5, "\u00abextend\u00bb", -0.12),
    ],
    "extra": [(60, 9.5, 30, 7, "Force Delete\n(force=true)")],
}
