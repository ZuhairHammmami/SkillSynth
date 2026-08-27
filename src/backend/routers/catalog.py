"""Catalog router — learner-facing browse API.

Wires /api/catalog to services/catalog_service.py (Task 3). All endpoints
require a signed-in user; consumed by the learner catalog UI.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.entities.catalog import Category
from backend.policies.auth_policy import get_current_user
from backend.repositories import catalog_repository as repo
from backend.services import catalog_service

router = APIRouter()


@router.get("/categories")
def list_categories(db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    """Return every category serialized with its skills. Calls
    catalog_service._serialize_category for each repo.get_all_categories(db)."""
    return [catalog_service._serialize_category(db, c)
            for c in repo.get_all_categories(db)]


@router.get("/categories/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    """Return one category serialized with its skills. Raises 404 when the
    category id does not exist; consumed by the catalog detail view."""
    category = db.query(Category).get(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return catalog_service._serialize_category(db, category)


@router.get("/skills")
def list_skills(db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    """Return every skill serialized individually. Calls
    catalog_service._serialize_skill for each repo.get_all_skills(db)."""
    return [catalog_service._serialize_skill(db, s)
            for s in repo.get_all_skills(db)]
