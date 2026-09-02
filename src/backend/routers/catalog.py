"""Catalog router — learner-facing browse API.

Wires /api/catalog to services/catalog_service.py. All endpoints require a
signed-in user; consumed by the learner catalog UI. Public (non-admin)
browse: categories, skills, skill detail, and roles. Per-skill path
generation lives in routers/paths at /api/generate-path/skill/{id}.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dto.pagination import paginate
from backend.entities.catalog import Category
from backend.policies.auth_policy import get_current_user
from backend.repositories import catalog_repository as repo
from backend.services import catalog_service

router = APIRouter()


@router.get("/categories")
def list_categories(page: int = 1, page_size: int = 50,
                    db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    """Return categories paginated with envelope. Calls
    catalog_service._serialize_category for each repo.get_all_categories(db)."""
    items = [catalog_service._serialize_category(db, c)
             for c in repo.get_all_categories(db)]
    return paginate(items, page, page_size)


@router.get("/categories/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    """Return one category serialized with its skills. Raises 404 when the
    category id does not exist; consumed by the catalog detail view."""
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return catalog_service._serialize_category(db, category)


@router.get("/skills")
def list_skills(page: int = 1, page_size: int = 50,
                db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    """Return skills paginated with envelope. Calls
    catalog_service._serialize_skill for each repo.get_all_skills(db)."""
    items = [catalog_service._serialize_skill(db, s)
             for s in repo.get_all_skills(db)]
    return paginate(items, page, page_size)


@router.get("/skills/{skill_id}")
def get_skill_detail(skill_id: int, db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    """Return one skill's learner detail with prerequisite + recommended
    strips. Raises 404 when the skill id does not exist; consumed by the
    catalog skill view (endpoint A)."""
    skill = repo.get_skill(db, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return catalog_service.serialize_skill_detail(db, skill)


@router.get("/roles")
def list_roles(db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    """Return lean learner-facing job roles with their ordered skills.
    Calls catalog_service.list_catalog_roles; consumed by the catalog
    role picker (endpoint B)."""
    return catalog_service.list_catalog_roles(db)
