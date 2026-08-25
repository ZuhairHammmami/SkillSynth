"""Admin router — user/catalog management, reports, activity, system ops.

Wires /api/admin to services/admin_service.py + catalog_service.py and the
assess/catalog repositories (Task 2). Every route is admin-only via the
router-level require_admin dependency; consumed by the admin-app pages.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.config.app_settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES, APP_MODE, CORS_ORIGINS, CSRF_ENABLED,
    LOGIN_LOCKOUT_MINUTES, MAX_LOGIN_ATTEMPTS, PASSWORD_MIN_LENGTH,
)
from backend.database import get_db
from backend.dto.admin import AdminCreateUser, PathAdminView
from backend.dto.catalog import ResourceCreate, SkillCreate
from backend.policies.auth_policy import get_current_user, require_admin
from backend.repositories import assess_repository, catalog_repository
from backend.services import admin_service, auth_service, catalog_service

router = APIRouter(dependencies=[Depends(require_admin)])


def _user_out(user) -> dict:
    """Serialize a users row for the admin listing (no skill_profile)."""
    return {
        "id": user.id, "email": user.email, "full_name": user.full_name,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def _resource_out(resource) -> dict:
    """Serialize a resources row for the admin listing."""
    return {
        "id": resource.id, "title": resource.title, "url": resource.url,
        "type": resource.type, "language": resource.language,
        "is_free": resource.is_free, "is_official": resource.is_official,
        "author_or_platform": resource.author_or_platform,
        "skill_id": resource.skill_id,
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


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    """Hard-delete a user (self-delete guarded). Calls admin_service.delete_user;
    router-level require_admin already gates access."""
    ok, error = admin_service.delete_user(db, user_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=400 if "yourself" in (error or "") else 404,
                            detail=error)
    return {"detail": "User deleted"}


@router.get("/skills")
def list_skills(db: Session = Depends(get_db)):
    """List all skills. Calls catalog_service.list_skills; admin skills page."""
    return catalog_service.list_skills(db)


@router.post("/skills")
def create_skill(data: SkillCreate, db: Session = Depends(get_db)):
    """Create a skill. Calls catalog_service.create_skill; admin skills dialog."""
    result, error = catalog_service.create_skill(db, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    """Delete a skill. Calls catalog_service.delete_skill."""
    ok, error = catalog_service.delete_skill(db, skill_id)
    if not ok:
        raise HTTPException(status_code=400, detail=error)
    return {"detail": "Deleted successfully"}


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """List all categories. Reads the catalog repository; admin skills dialog."""
    return [{"id": c.id, "name": c.name}
            for c in catalog_repository.get_all_categories(db)]


@router.get("/resources")
def list_resources(db: Session = Depends(get_db)):
    """List all resources. Reads the catalog repository; admin resources page."""
    return [_resource_out(r) for r in catalog_repository.get_all_resources(db)]


@router.post("/resources")
def create_resource(data: ResourceCreate, db: Session = Depends(get_db)):
    """Create a resource. Calls catalog_service.create_resource; admin dialog."""
    return _resource_out(catalog_service.create_resource(db, data))


@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    """Delete a resource. Calls catalog_service.delete_resource."""
    ok, error = catalog_service.delete_resource(db, resource_id)
    if not ok:
        raise HTTPException(status_code=404, detail=error)
    return {"detail": "Deleted successfully"}


@router.get("/assessments")
def list_assessments(db: Session = Depends(get_db)):
    """List all assessments. Reads the assess repository; admin assessments page."""
    return [{"id": a.id, "skill_id": a.skill_id, "title": a.title,
             "assessment_type": a.description,
             "passing_score": a.pass_score or 60}
            for a in assess_repository.get_all_assessments(db)]


@router.delete("/assessments/{assessment_id}")
def delete_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Delete an assessment. Calls the assess repository delete."""
    if not assess_repository.delete_assessment(db, assessment_id):
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"detail": "Deleted successfully"}


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
    """Return the read-only system configuration object for the admin
    feature-flags page (built from config/app_settings)."""
    return {
        "app_mode": APP_MODE,
        "registration_enabled": True,
        "ai_path_generation": True,
        "real_time_updates": True,
        "csrf_protection": CSRF_ENABLED,
        "rate_limiting": True,
        "password_policy": {
            "min_length": PASSWORD_MIN_LENGTH,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digit": True,
            "require_special_char": True,
        },
        "session_timeout_hours": ACCESS_TOKEN_EXPIRE_MINUTES // 60,
        "account_lockout_attempts": MAX_LOGIN_ATTEMPTS,
        "lockout_minutes": LOGIN_LOCKOUT_MINUTES,
        "cors_origins": CORS_ORIGINS,
    }


@router.get("/reports/aggregated")
def aggregated_report(db: Session = Depends(get_db)):
    """Aggregated admin report. Calls admin_service.get_aggregated_report."""
    return admin_service.get_aggregated_report(db)


@router.get("/reports/system-health")
def system_health(db: Session = Depends(get_db)):
    """System health report. Calls admin_service.get_system_health."""
    return admin_service.get_system_health(db)
