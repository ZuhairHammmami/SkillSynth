"""Catalog service — skill/category/resource/job-role CRUD + wizard.

Called by routers/admin.py (catalog endpoints) and learning/paths services.
Validation lives in dto/catalog.py; persistence in catalog_repository.
"""

from backend.dto.catalog import (
    CategoryCreate, CategoryUpdate, JobRoleCreate, JobRoleUpdate,
    ResourceCreate, ResourceUpdate, SkillCreate, SkillUpdate,
)
from backend.repositories import catalog_repository as repo


def _skill_ids(raw: list | None) -> list[int]:
    """Normalize JobRoleCreate.skill_ids entries (dicts or ints)."""
    return [item.get("skill_id") if isinstance(item, dict) else item
            for item in (raw or []) if item]


def _serialize_skill(db, skill) -> dict:
    """Skill row + synthesized prerequisite/resource id lists."""
    from backend.entities.catalog import Resource, SkillPrerequisite
    prerequisite_ids = [row.prerequisite_id for row in db.query(
        SkillPrerequisite).filter(SkillPrerequisite.skill_id == skill.id).all()]
    resource_ids = [row.id for row in db.query(Resource).filter(
        Resource.skill_id == skill.id).all()]
    return {
        "id": skill.id, "name": skill.name, "description": skill.description,
        "difficulty_level": skill.difficulty_level,
        "estimated_hours": skill.estimated_hours, "icon": skill.icon,
        "color": skill.color, "category_id": skill.category_id,
        "prerequisite_ids": sorted(prerequisite_ids),
        "resource_ids": resource_ids,
    }


def list_skills(db) -> list[dict]:
    """All skills serialized; admin skills page."""
    return [_serialize_skill(db, s) for s in repo.get_all_skills(db)]


def create_skill(db, data: SkillCreate) -> tuple[dict | None, str | None]:
    """Create with duplicate-name guard; (payload, error) tuple."""
    if repo.get_skill_by_name(db, data.name):
        return None, "Skill already exists"
    return _serialize_skill(db, repo.create_skill(db, data)), None


def update_skill(db, skill_id: int, data: SkillUpdate) -> tuple[dict | None, str | None]:
    """Apply provided fields; (payload, error) tuple."""
    skill = repo.get_skill(db, skill_id)
    if not skill:
        return None, "Skill not found"
    fields = data.model_dump(exclude_unset=True)
    fields.pop("category_ids", None)
    updated = repo.update_skill(db, skill, fields)
    return _serialize_skill(db, updated), None


def delete_skill(db, skill_id: int) -> tuple[bool, str | None]:
    """Delete or explain reference conflicts; (ok, error) tuple."""
    if not repo.delete_skill(db, skill_id):
        return False, "Cannot delete skill. It might be in use."
    return True, None


# ── Categories ────────────────────────────────────────────────────────

def create_category(db, data: CategoryCreate) -> tuple[dict | None, str | None]:
    """Duplicate-guarded category creation; returns ORM row or error."""
    if repo.get_category_by_name(db, data.name):
        return None, "Category already exists"
    return repo.create_category(db, data.name), None


def update_category(db, category_id: int, data: CategoryUpdate):
    """Apply provided fields; (payload, error) tuple."""
    from backend.entities.catalog import Category
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        return None, "Category not found"
    fields = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    return repo.update_category(db, cat, fields), None


def delete_category(db, category_id: int) -> tuple[bool, str | None]:
    """Delete or explain reference conflicts; (ok, error) tuple."""
    if not repo.delete_category(db, category_id):
        return False, "Cannot delete category. It might be in use."
    return True, None


# ── Resources ─────────────────────────────────────────────────────────

def create_resource(db, data: ResourceCreate) -> dict:
    """Insert a resource from validated DTO; returns the ORM row."""
    return repo.create_resource(db, data.model_dump(exclude_unset=True))


def update_resource(db, resource_id: int, data: ResourceUpdate):
    """Apply provided fields; (payload, error) tuple."""
    resource = repo.get_resource(db, resource_id)
    if not resource:
        return None, "Resource not found"
    fields = data.model_dump(exclude_unset=True)
    return repo.update_resource(db, resource, fields), None


def delete_resource(db, resource_id: int) -> tuple[bool, str | None]:
    """Delete a resource; (ok, error) tuple for router mapping."""
    if not repo.delete_resource(db, resource_id):
        return False, "Resource not found"
    return True, None


# ── Job roles ─────────────────────────────────────────────────────────

def _serialize_job_role(db, role) -> dict:
    """Job role row + ordered required-skill ids from job_role_skills."""
    return {
        "id": role.id, "title": role.title, "description": role.description,
        "career_field": role.career_field,
        "skill_ids": repo.get_job_role_skill_ids(db, role.id),
    }


def list_job_roles(db) -> list[dict]:
    """All job roles serialized; admin CRUD + wizard source data."""
    return [_serialize_job_role(db, r) for r in repo.get_all_job_roles(db)]


def create_job_role(db, data: JobRoleCreate) -> tuple[dict | None, str | None]:
    """Duplicate-title-guarded creation; links skills when provided."""
    if repo.get_job_role_by_title(db, data.title):
        return None, "Job role already exists"
    role = repo.create_job_role(db, data.title, data.description, data.career_field)
    ids = _skill_ids(data.skill_ids)
    if ids:
        repo.set_job_role_skills(db, role.id, ids)
    return _serialize_job_role(db, role), None


def update_job_role(db, job_role_id: int, data: JobRoleUpdate):
    """Apply provided fields and optionally replace skill links."""
    role = repo.get_job_role(db, job_role_id)
    if not role:
        return None, "Job role not found"
    fields = data.model_dump(exclude_unset=True)
    skill_ids = fields.pop("skill_ids", None)
    updated = repo.update_job_role(db, role, fields)
    if skill_ids is not None:
        repo.set_job_role_skills(db, updated.id, _skill_ids(skill_ids))
    return _serialize_job_role(db, updated), None


def delete_job_role(db, job_role_id: int) -> tuple[bool, str | None]:
    """Delete a role; mapping rows cascade; (ok, error) tuple."""
    if not repo.delete_job_role(db, job_role_id):
        return False, "Cannot delete job role. It might be in use."
    return True, None


# ── Wizard options ────────────────────────────────────────────────────

def wizard_options(db) -> dict:
    """GET /wizard-options payload — shape frozen (wire compat).

    career_fields groups role payloads by their career_field with the
    historical "Other" fallback; formats/languages are the same literals
    as the old AdminCatalogService.get_wizard_options.
    """
    flat_roles: list[dict] = []
    career_fields: dict[str, list[dict]] = {}
    for role in repo.get_all_job_roles(db):
        field = role.career_field or "Other"
        entry = {"title": role.title, "description": role.description,
                 "career_field": field}
        flat_roles.append(entry)
        career_fields.setdefault(field, []).append(entry)
    return {
        "job_roles": flat_roles,
        "career_fields": career_fields,
        "preferences": {
            "formats": ["any", "video", "article", "course", "book"],
            "languages": ["en", "ar"],
        },
    }
