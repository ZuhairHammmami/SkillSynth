"""Catalog-admin router — skills, categories, resources, job roles.

Mounted under /api/admin by backend/main.py beside routers/admin.py
(line-budget split; URLs wire-compatible with the original monolith).
Every route is admin-only via the router-level require_admin dependency.
Service errors map through routers/error_mapping.status_for_error:
'*not found*' → 404, 'already exists'/restricted-delete conflicts → 409,
unknown references/cycle violations → 400.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dto.catalog import (
    CategoryCreate, CategoryUpdate, JobRoleCreate, JobRoleUpdate,
    ResourceCreate, ResourceUpdate, SkillCreate, SkillUpdate,
)
from backend.policies.auth_policy import require_admin
from backend.routers.error_mapping import status_for_error
from backend.repositories import catalog_repository
from backend.services import catalog_service

router = APIRouter(dependencies=[Depends(require_admin)])


def _fail(error) -> None:
    """Raise the mapped HTTPException for a service error payload."""
    raise HTTPException(status_code=status_for_error(error), detail=error)


def _fail_create(error) -> None:
    """Error mapping for POST handlers preserving legacy statuses:
    string errors (duplicates, bad refs) → 400 exactly as before
    Task 2; structured restricted-delete/conflict payloads → 409."""
    raise HTTPException(
        status_code=409 if isinstance(error, dict) else 400, detail=error)


def _resource_out(resource) -> dict:
    """Serialize a resources row for the admin listing."""
    return {
        "id": resource.id, "title": resource.title, "url": resource.url,
        "type": resource.type, "language": resource.language,
        "is_free": resource.is_free, "is_official": resource.is_official,
        "author_or_platform": resource.author_or_platform,
        "skill_id": resource.skill_id,
    }


# ── Skills ────────────────────────────────────────────────────────────

@router.get("/skills")
def list_skills(db: Session = Depends(get_db)):
    """List all skills. Calls catalog_service.list_skills; admin page."""
    return catalog_service.list_skills(db)


@router.post("/skills")
def create_skill(data: SkillCreate, db: Session = Depends(get_db)):
    """Create a skill; unknown category/prerequisite refs map to 400."""
    result, error = catalog_service.create_skill(db, data)
    if error:
        _fail_create(error)
    return result


@router.put("/skills/{skill_id}")
def update_skill(skill_id: int, data: SkillUpdate,
                 db: Session = Depends(get_db)):
    """Update a skill (404 missing / 409 rename dup / 400 bad refs)."""
    result, error = catalog_service.update_skill(db, skill_id, data)
    if error:
        _fail(error)
    return result


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, force: bool = False,
                 db: Session = Depends(get_db)):
    """Delete a skill; restricted to 409 while dependents exist unless
    ?force=true lets DB cascade/set-null semantics apply."""
    ok, error = catalog_service.delete_skill(db, skill_id, force)
    if not ok:
        _fail(error)
    return {"detail": "Deleted successfully"}


# ── Categories ────────────────────────────────────────────────────────

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """List all categories. Reads the catalog repository; admin dialog."""
    return [{"id": c.id, "name": c.name}
            for c in catalog_repository.get_all_categories(db)]


@router.post("/categories")
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a category; unknown parent refs map to 400."""
    result, error = catalog_service.create_category(db, data)
    if error:
        _fail_create(error)
    return _category_out(result)


@router.put("/categories/{category_id}")
def update_category(category_id: int, data: CategoryUpdate,
                    db: Session = Depends(get_db)):
    """Update a category (rename dups 409; parent rules 400)."""
    result, error = catalog_service.update_category(db, category_id, data)
    if error:
        _fail(error)
    return _category_out(result)


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, force: bool = False,
                    db: Session = Depends(get_db)):
    """Delete a category; blocked with child skills unless ?force=true."""
    ok, error = catalog_service.delete_category(db, category_id, force)
    if not ok:
        _fail(error)
    return {"detail": "Deleted successfully"}


def _category_out(category) -> dict:
    """Serialize a categories row including its optional parent link."""
    return {"id": category.id, "name": category.name,
            "description": category.description,
            "parent_id": category.parent_id}


# ── Resources ─────────────────────────────────────────────────────────

@router.get("/resources")
def list_resources(db: Session = Depends(get_db)):
    """List all resources. Reads the catalog repository; admin page."""
    return [_resource_out(r) for r in catalog_repository.get_all_resources(db)]


@router.post("/resources")
def create_resource(data: ResourceCreate, db: Session = Depends(get_db)):
    """Create a resource; unknown skill_id maps to 400."""
    result, error = catalog_service.create_resource(db, data)
    if error:
        _fail_create(error)
    return _resource_out(result)


@router.put("/resources/{resource_id}")
def update_resource(resource_id: int, data: ResourceUpdate,
                    db: Session = Depends(get_db)):
    """Update a resource (404 missing / 400 unknown skill_id)."""
    result, error = catalog_service.update_resource(db, resource_id, data)
    if error:
        _fail(error)
    return _resource_out(result)


@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    """Delete a resource. Calls catalog_service.delete_resource."""
    ok, error = catalog_service.delete_resource(db, resource_id)
    if not ok:
        raise HTTPException(status_code=404, detail=error)
    return {"detail": "Deleted successfully"}


# ── Job roles ─────────────────────────────────────────────────────────

@router.get("/job-roles")
def list_job_roles(db: Session = Depends(get_db)):
    """List all job roles serialized with skill_ids; admin CRUD page."""
    return catalog_service.list_job_roles(db)


@router.post("/job-roles")
def create_job_role(data: JobRoleCreate, db: Session = Depends(get_db)):
    """Create a job role; duplicate titles 409, unknown skills 400."""
    result, error = catalog_service.create_job_role(db, data)
    if error:
        _fail_create(error)
    return result


@router.put("/job-roles/{job_role_id}")
def update_job_role(job_role_id: int, data: JobRoleUpdate,
                    db: Session = Depends(get_db)):
    """Update a job role incl. replacing its required-skill links."""
    result, error = catalog_service.update_job_role(db, job_role_id, data)
    if error:
        _fail(error)
    return result


@router.delete("/job-roles/{job_role_id}")
def delete_job_role(job_role_id: int, force: bool = False,
                    db: Session = Depends(get_db)):
    """Delete a job role; blocked while skill mappings exist unless
    ?force=true cascades them away."""
    ok, error = catalog_service.delete_job_role(db, job_role_id, force)
    if not ok:
        _fail(error)
    return {"detail": "Deleted successfully"}
