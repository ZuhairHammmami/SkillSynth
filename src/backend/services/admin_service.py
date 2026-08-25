"""Admin service — user CRUD, reports, activity feed, system ops.

Called by the admin routers (Task 3). Report key sets are frozen
(AggregatedReportOut contract); completions now come from step_progress
rows with completed_at NOT NULL. Backups/inspector target SQLite dev.
"""

import glob
import os
import shutil
from collections import Counter
from datetime import datetime, timedelta, UTC

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.dto.admin import PathAdminView
from backend.entities.identity import User
from backend.entities.learning import Path as PathEntity
from backend.repositories import assess_repository, catalog_repository
from backend.repositories import engagement_repository as erepo
from backend.repositories import identity_repository as irepo
from backend.repositories import learning_repository as lrepo


# ── User management ───────────────────────────────────────────────────

def list_users(db, skip: int = 0, limit: int = 100) -> list[User]:
    """Paged users for GET /admin/users; routers serialize AdminUserOut."""
    return irepo.get_all(db, skip, limit)


def create_user(db, data, hasher) -> tuple[User | None, str | None]:
    """Admin user creation; `hasher` is auth_service.hash_password
    (injected to avoid a circular service import)."""
    if irepo.get_by_email(db, data.email):
        return None, "Email already registered"
    user = irepo.create(
        db, email=data.email, hashed_password=hasher(data.password),
        full_name=data.full_name or "", is_admin=data.is_admin or False)
    return user, None


def update_user(db, user_id: int, data, hasher) -> tuple[User | None, str | None]:
    """Apply AdminUserUpdate; password swaps in pre-hashed."""
    user = irepo.get_by_id(db, user_id)
    if not user:
        return None, "User not found"
    fields = {k: v for k, v in data.model_dump(exclude_unset=True).items()
              if v is not None}
    if "password" in fields:
        fields["hashed_password"] = hasher(fields.pop("password"))
    if "full_name" in fields and not fields["full_name"]:
        fields["full_name"] = ""
    return irepo.update_fields(db, user, fields), None


def delete_user(db, user_id: int, admin_id: int) -> tuple[bool, str | None]:
    """Self-deletion guard + hard delete; (ok, error) tuple."""
    if user_id == admin_id:
        return False, "Cannot delete yourself"
    if not irepo.delete(db, user_id):
        return False, "User not found"
    return True, None


# ── Reports (frozen keys) ─────────────────────────────────────────────

def get_user_activity(db) -> dict:
    """user_activity block; new-user windows use created_at."""
    total, new_24h, new_7d, with_paths = irepo.get_user_counts(db)
    return {"total_users": total, "new_users_last_24h": new_24h,
            "new_users_last_7d": new_7d, "users_with_paths": with_paths}


def get_content_engagement(db) -> dict:
    """content_engagement block; completions from step_progress."""
    most_completed = lrepo.most_completed_steps(db)
    return {
        "total_paths": lrepo.count_paths(db),
        "total_steps": lrepo.count_steps(db),
        "total_completions": lrepo.count_completions(db),
        "most_completed_steps": [{"title": t, "completions": c}
                                 for t, c in most_completed],
    }


def get_system_health(db) -> dict:
    """system_health block (+ additive details map)."""
    return {
        "database_status": "Connected",
        "api_version": "1.0.0",
        "total_users": irepo.count_all(db),
        "total_paths": lrepo.count_paths(db),
        "total_assessments": assess_repository.count_assessments(db),
        "details": {},
    }


def _most_requested_skills(db) -> list[tuple[str, int]]:
    """Top job-role-mapped skills by mapping count ({skill_name,
    path_count} items keep their historical names)."""
    counts = Counter(catalog_repository.get_path_skill_ids(db))
    out = []
    for sid, cnt in counts.most_common(10):
        skill = catalog_repository.get_skill(db, sid)
        if skill:
            out.append((skill.name, cnt))
    return out


def get_aggregated_report(db) -> dict:
    """GET /admin/reports/aggregated payload — EXACT nested key contract;
    average_completion_rate = global completions ÷ total steps."""
    total_completions = lrepo.count_completions(db)
    total_steps = lrepo.count_steps(db)
    avg_score = assess_repository.average_score(db)
    return {
        "user_activity": get_user_activity(db),
        "content_engagement": get_content_engagement(db),
        "system_health": get_system_health(db),
        "most_active_users": [{"user_email": email, "completed_steps": cnt}
                              for email, cnt in irepo.most_active_users(db)],
        "most_requested_skills": [{"skill_name": n, "path_count": c}
                                  for n, c in _most_requested_skills(db)],
        "total_hours_learned": float(lrepo.sum_total_hours(db)),
        "average_completion_rate":
            round(total_completions / total_steps * 100, 1) if total_steps else 0,
        "total_assessment_attempts": assess_repository.count_results(db),
        "average_assessment_score": round(float(avg_score), 1),
    }


def get_all_paths_admin(db, skip: int = 0, limit: int = 100) -> list[PathAdminView]:
    """Admin path listing with owner email + all-steps-completed flag."""
    paths = (
        db.query(PathEntity)
        .order_by(PathEntity.created_at.desc()).offset(skip).limit(limit).all()
    )
    all_ids = [s.id for p in paths for s in lrepo.get_steps(db, p.id)]
    comps = lrepo.completions_by_step_ids(db, all_ids)
    by_user: dict[int, set[int]] = {}
    for c in comps:
        by_user.setdefault(c.user_id, set()).add(c.step_id)
    views = []
    for p in paths:
        steps = lrepo.get_steps(db, p.id)
        done = by_user.get(p.user_id, set())
        owner = irepo.get_by_id(db, p.user_id) if p.user_id else None
        views.append(PathAdminView(
            id=p.id, title=p.title,
            user_email=owner.email if owner else "Unknown",
            total_estimated_hours=p.total_estimated_hours,
            is_completed=bool(steps) and all(s.id in done for s in steps),
            created_at=p.created_at))
    return views


# ── Activity feed ─────────────────────────────────────────────────────

def activity_feed(db, offset: int = 0, limit: int = 50,
                  category: str | None = None,
                  action: str | None = None) -> list[dict]:
    """/admin/events payload; legacy profile_id/user keys kept plus
    additive user_email/user_agent surfaced by the engagement repo."""
    rows = erepo.get_filtered(db, offset, limit, category, action)
    items = []
    for row, user in rows:
        entry = {
            "id": row.id, "profile_id": row.user_id,
            "category": row.category, "action": row.action,
            "entity_type": row.entity_type,
            "entity_id": int(row.entity_id)
            if row.entity_id and str(row.entity_id).isdigit() else row.entity_id,
            "data": row.data, "ip_address": row.ip_address,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "user_email": user.email if user else None,
            "user_agent": row.user_agent,
        }
        if user:
            entry["user"] = {"full_name": user.full_name, "email": user.email,
                             "role_name": None, "is_admin": user.is_admin}
        items.append(entry)
    return items


# ── System operations ────────────────────────────────────────────────

def _format_bytes(size: float) -> str:
    """Human-readable byte formatter shared by backups + inspector."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def list_backups() -> list[dict]:
    """GET /admin/backups — newest-first skillsynth_*.db snapshots."""
    os.makedirs("backups", exist_ok=True)
    backups = []
    for path in sorted(glob.glob(os.path.join("backups", "skillsynth_*.db")),
                       reverse=True):
        stat = os.stat(path)
        backups.append({
            "path": path, "size_bytes": stat.st_size,
            "size_formatted": _format_bytes(stat.st_size),
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return backups


def backup_database() -> dict:
    """POST /admin/backups — file copy of the SQLite database."""
    db_path = "skillsynth.db"
    if not os.path.exists(db_path):
        return {"success": False, "error": "Database file not found"}
    os.makedirs("backups", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join("backups", f"skillsynth_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    size = os.path.getsize(backup_path)
    return {"success": True, "path": backup_path, "size_bytes": size,
            "size_formatted": _format_bytes(size), "created_at": timestamp}


def db_inspector(db: Session) -> dict:
    """GET /admin/db-inspector — tables, row counts, columns, integrity."""
    tables = db.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    ).scalars().all()
    table_info = []
    for tbl in tables:
        row_count = db.execute(text(f'SELECT COUNT(*) FROM "{tbl}"')).scalar()
        columns = db.execute(text(f'PRAGMA table_info("{tbl}")')).all()
        table_info.append({
            "table": tbl, "rows": row_count,
            "columns": [{"name": c.name, "type": c.type,
                         "notnull": bool(c.notnull), "pk": bool(c.pk)}
                        for c in columns],
        })
    db_path = "skillsynth.db"
    size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    try:
        integrity_ok = bool(db.execute(text("PRAGMA integrity_check")).scalar())
    except Exception:
        integrity_ok = False
    return {
        "database": os.path.basename(db_path), "size_bytes": size_bytes,
        "size_formatted": _format_bytes(size_bytes),
        "wal_mode": os.path.exists(db_path + "-wal"),
        "integrity_check": integrity_ok, "total_tables": len(table_info),
        "tables": table_info,
    }
