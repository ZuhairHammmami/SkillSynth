"""Admin router — user management, assessments, reports, system ops.

Wires /api/admin to services/admin_service.py and the assess repository;
catalog CRUD (skills/categories/resources/job-roles) lives in
routers/catalog_admin.py, mounted under the same /api/admin prefix by
backend/main.py. Every route is admin-only via the router-level
require_admin dependency; consumed by the admin-app pages.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

import logging

from backend.database import get_db
from backend.dto.admin import AdminCreateUser, AdminUserUpdate, PathAdminView
from backend.limiter import limiter
from backend.policies.auth_policy import get_current_user, require_admin
from backend.routers.error_mapping import status_for_error
from backend.services import admin_service, auth_service
from backend.services import llm_engine, settings_schema, settings_service

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_admin)])


def _user_out(user) -> dict:
    """Serialize a users row for the admin listing (no skill_profile)."""
    return {
        "id": user.id, "email": user.email, "full_name": user.full_name,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


@router.get("/users")
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Paged user listing. Calls admin_service.list_users; admin users page."""
    return [_user_out(u) for u in admin_service.list_users(db, skip, limit)]


@router.post("/users")
def create_user(data: AdminCreateUser, db: Session = Depends(get_db)):
    """Create a user. Calls admin_service.create_user with the auth hasher;
    admin users create dialog."""
    user, error = admin_service.create_user(db, data, auth_service.hash_password)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return _user_out(user)


@router.put("/users/{user_id}")
def update_user(user_id: int, data: AdminUserUpdate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    """Update a user (profile, admin flag, optional password reset).

    Calls admin_service.update_user with the acting admin id so the
    demote-self guard can fire; 'not found' maps to 404, uniqueness/
    demotion conflicts to 409 via the shared error mapper."""
    user, error = admin_service.update_user(db, user_id, data,
                                            auth_service.hash_password,
                                            acting_admin_id=current_user.id)
    if error:
        raise HTTPException(status_code=status_for_error(error), detail=error)
    return _user_out(user)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, force: bool = False,
                db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    """Restricted-delete a user (self-delete + dependent census guarded).
    Calls admin_service.delete_user; router-level require_admin gates
    access and the structured 409 payload surfaces dependent rows."""
    ok, error = admin_service.delete_user(db, user_id, current_user.id, force)
    if not ok:
        if isinstance(error, dict):
            raise HTTPException(status_code=409, detail=error)
        raise HTTPException(status_code=400 if "yourself" in (error or "") else 404,
                            detail=error)
    return {"detail": "User deleted"}


@router.get("/paths", response_model=list[PathAdminView])
def list_paths(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Admin path listing. Calls admin_service.get_all_paths_admin."""
    return admin_service.get_all_paths_admin(db, skip, limit)


@router.get("/events")
def get_events(limit: int = Query(default=50, le=200),
               offset: int = Query(default=0, ge=0),
               category: str | None = Query(default=None),
               action: str | None = Query(default=None),
               db: Session = Depends(get_db)):
    """Activity feed. Calls admin_service.activity_feed; admin events page."""
    return admin_service.activity_feed(db, offset, limit, category, action)


@router.get("/backups")
def list_backups(request: Request):
    """List DB backup files. Calls admin_service.list_backups."""
    return admin_service.list_backups()


@router.post("/backups")
def create_backup(request: Request, db: Session = Depends(get_db)):
    """Create a DB backup snapshot. Calls admin_service.backup_database."""
    result = admin_service.backup_database()
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Backup failed"))
    return result


@router.get("/db-inspector")
def db_inspector(db: Session = Depends(get_db)):
    """Inspect tables, rows, columns and integrity. Calls admin_service.db_inspector."""
    return admin_service.db_inspector(db)


@router.get("/feature-flags")
def feature_flags():
    """Return the flat 13-key runtime flag map for the admin feature-flags
    page. Produced by settings_schema.build_runtime_flags() so the merged
    persisted/runtime values live only in settings_schema; admin page."""
    return settings_schema.build_runtime_flags()


@router.get("/feature-flags/schema")
def feature_flags_schema():
    """Return the serializable FLAG_SCHEMA (per-key type, editable, live,
    restart, min/max/min_length/max_length, default) so the admin
    feature-flags page can render schema-driven per-type controls. Values
    are plain JSON; no functions/nested objects."""
    return settings_schema.FLAG_SCHEMA


@router.put("/feature-flags")
def update_feature_flags(payload: dict[str, Any]):
    """Validate and persist a bulk feature-flag update, then apply runtime
    side effects and return the updated flat 13-key map.

    Called by PUT /api/admin/feature-flags from the admin page; gated by
    the router-level require_admin dependency. Delegates validation to
    settings_schema.validate_update (422 with per-key messages on error) and
    persistence to settings_service.set_setting per cleaned key. On ai_enabled
    change keeps the warmup-on-enable / reset_load_failure-on-disable
    behavior; on rate_limiting change flips limiter.enabled."""
    cleaned, errors = settings_schema.validate_update(payload)
    if errors:
        raise HTTPException(status_code=422, detail=errors)
    for key, value in cleaned.items():
        settings_service.set_setting(key, value)
    if "ai_enabled" in cleaned:
        if cleaned["ai_enabled"]:
            try:
                llm_engine.warmup()
            except Exception as exc:  # noqa: BLE001 — non-fatal toggle side-effect
                logger.warning("feature-flags: AI warmup on enable failed: %s", exc)
        else:
            llm_engine.reset_load_failure()
    if "rate_limiting" in cleaned:
        limiter.enabled = bool(cleaned["rate_limiting"])
    return settings_schema.build_runtime_flags()


@router.get("/reports/aggregated")
def aggregated_report(db: Session = Depends(get_db)):
    """Aggregated admin report. Calls admin_service.get_aggregated_report."""
    return admin_service.get_aggregated_report(db)


@router.get("/reports/system-health")
def system_health(db: Session = Depends(get_db)):
    """System health report. Calls admin_service.get_system_health."""
    return admin_service.get_system_health(db)
