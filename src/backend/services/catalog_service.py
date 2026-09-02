"""Catalog service — skill/category/resource/job-role CRUD + wizard.

Called by routers/catalog_admin.py, routers/admin.py and learning/paths
services. Integrity rules live in services/catalog_integrity.py,
validation in dto/catalog.py, persistence in catalog_repository. Errors
follow routers/error_mapping.status_for_error: '*not found*' → 404,
'already exists' → 409, invalid references/cycles → 400.
"""

from backend.dto.catalog import (
    CategoryCreate, CategoryUpdate, JobRoleCreate, JobRoleUpdate,
    ResourceCreate, ResourceUpdate, SkillCreate, SkillUpdate,
)
from backend.entities.catalog import Category
from backend.repositories import catalog_repository as repo
from backend.services import catalog_integrity as integrity


def _skill_ids(raw: list | None) -> list[int]:
    """Normalize JobRoleCreate.skill_ids entries (dicts or ints)."""
    return [item.get("skill_id") if isinstance(item, dict) else item
            for item in (raw or []) if item]


def _serialize_skill(db, skill, prereq_map=None, resource_map=None) -> dict:
    """Skill row + prerequisite/resource id lists for admin payloads.

    prereq_map/resource_map (batch mode) skip per-skill queries; when
    absent, fall back to single-skill lookups."""
    if prereq_map is not None and resource_map is not None:
        prerequisite_ids = [p.id for p in prereq_map.get(skill.id, [])]
        resource_ids = [r.id for r in resource_map.get(skill.id, [])]
    else:
        from backend.entities.catalog import Resource, SkillPrerequisite
        prerequisite_ids = [row.prerequisite_id for row in db.query(
            SkillPrerequisite).filter(
                SkillPrerequisite.skill_id == skill.id).all()]
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


def _build_skill_maps(db, skills):
    """Batch-fetch prerequisite and resource maps for a list of skills.

    Returns (prereq_map, resource_map) dicts keyed by skill_id.
    Used by list_skills and the catalog router to eliminate N+1 queries."""
    skill_ids = [s.id for s in skills]
    prereq_map = repo.get_prereqs_by_skill_ids(db, skill_ids)
    all_resources = repo.get_all_resources(db)
    resource_map: dict[int, list] = {}
    for r in all_resources:
        if r.skill_id is not None:
            resource_map.setdefault(r.skill_id, []).append(r)
    return prereq_map, resource_map


def _serialize_category(db, category, skill_map=None,
                         prereq_map=None, resource_map=None) -> dict:
    """Category row + its serialized skills; admin category payloads.

    When skill_map is provided, look up skills by category_id from the
    pre-built map instead of querying per category (batch mode)."""
    if skill_map is not None:
        skills = [s for s in skill_map.values()
                  if s.category_id == category.id]
    else:
        skills = repo.get_skills_by_category(db, category.id)
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "parent_id": category.parent_id,
        "skills": [_serialize_skill(db, s, prereq_map, resource_map)
                   for s in skills],
    }


def list_skills(db) -> list[dict]:
    """All skills serialized; admin skills page.

    Batch-fetches prerequisites and resources to eliminate N+1 queries."""
    skills = repo.get_all_skills(db)
    prereq_map, resource_map = _build_skill_maps(db, skills)
    return [_serialize_skill(db, s, prereq_map, resource_map)
            for s in skills]


def create_skill(db, data: SkillCreate) -> tuple[dict | None, str | None]:
    """Duplicate-name + FK-guarded creation; (payload, error) tuple.

    Called by routers/catalog_admin.create_skill; catalog_integrity
    validates category/prerequisite refs before any insert."""
    if repo.get_skill_by_name(db, data.name):
        return None, "Skill already exists"
    error = integrity.ensure_category_exists(db, data.category_id)
    if error:
        return None, error
    error = integrity.ensure_skills_exist(
        db, data.prerequisite_ids, "prerequisite_ids")
    if error:
        return None, error
    return _serialize_skill(db, repo.create_skill(db, data)), None


def update_skill(db, skill_id: int,
                 data: SkillUpdate) -> tuple[dict | None, str | None]:
    """Validated partial skill update; (payload, error) tuple.

    Called by routers/catalog_admin.update_skill; enforces case-
    insensitive rename uniqueness excluding this row plus category FK
    and prerequisite DAG rules before persisting."""
    skill = repo.get_skill(db, skill_id)
    if not skill:
        return None, "Skill not found"
    fields = data.model_dump(exclude_unset=True)
    fields.pop("category_ids", None)
    if "name" in fields and fields["name"].lower() != skill.name.lower():
        if repo.get_skill_by_name(db, fields["name"]):
            return None, "Skill already exists"
    if "category_id" in fields:
        error = integrity.ensure_category_exists(db, fields["category_id"])
        if error:
            return None, error
    if "prerequisite_ids" in fields:
        error = integrity.ensure_prerequisite_rules(
            db, skill.id, fields["prerequisite_ids"])
        if error:
            return None, error
    return _serialize_skill(db, repo.update_skill(db, skill, fields)), None


def delete_skill(db, skill_id: int,
                 force: bool = False) -> tuple[bool, str | dict | None]:
    """Restricted delete with dependent census; (ok, error) tuple.

    Called by routers/catalog_admin.delete_skill; ?force=true skips the
    catalog_integrity census so DB cascade/set-null rules apply."""
    skill = repo.get_skill(db, skill_id)
    if not skill:
        return False, "Skill not found"
    if not force:
        conflict = integrity.skill_delete_conflict(db, skill_id)
        if conflict:
            return False, conflict
    repo.delete_skill(db, skill_id)
    return True, None


# ── Categories ────────────────────────────────────────────────────────

def create_category(db, data: CategoryCreate) -> tuple[dict | None, str | None]:
    """Duplicate-name + parent-rule guarded creation; (row, error).

    Called by routers/catalog_admin.create_category; inserts directly
    because catalog_repository.create_category predates parent_id."""
    if repo.get_category_by_name(db, data.name):
        return None, "Category already exists"
    error = integrity.ensure_parent_rules(db, None, data.parent_id)
    if error:
        return None, error
    cat = Category(name=data.name, description=data.description,
                   parent_id=data.parent_id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat, None


def update_category(db, category_id: int,
                    data: CategoryUpdate) -> tuple[dict | None, str | None]:
    """Validated partial update; uniqueness + parent rules enforced.

    Called by routers/catalog_admin.update_category ('Category not
    found' → 404); an explicit null parent_id detaches the node."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        return None, "Category not found"
    fields = data.model_dump(exclude_unset=True)
    if "name" in fields and fields["name"].lower() != cat.name.lower():
        if repo.get_category_by_name(db, fields["name"]):
            return None, "Category already exists"
    if "parent_id" in fields:
        error = integrity.ensure_parent_rules(db, category_id,
                                              fields["parent_id"])
        if error:
            return None, error
    for key, value in fields.items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat, None


def delete_category(db, category_id: int,
                    force: bool = False) -> tuple[bool, str | dict | None]:
    """Restricted delete guarded by child-skill census; (ok, error).

    Called by routers/catalog_admin.delete_category; force applies the
    ON DELETE SET NULL detach instead."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        return False, "Category not found"
    if not force:
        conflict = integrity.category_delete_conflict(db, category_id)
        if conflict:
            return False, conflict
    repo.delete_category(db, category_id)
    return True, None


# ── Resources ─────────────────────────────────────────────────────────

def create_resource(db, data: ResourceCreate) -> tuple[dict | None, str | None]:
    """FK-checked resource insertion; (row, error) tuple.

    Called by routers/catalog_admin.create_resource; unknown skill_id
    surfaces as 400 before the INSERT."""
    error = integrity.ensure_resource_skill_exists(db, data.skill_id)
    if error:
        return None, error
    return repo.create_resource(db, data.model_dump(exclude_unset=True)), None


def update_resource(db, resource_id: int,
                    data: ResourceUpdate) -> tuple[dict | None, str | None]:
    """Partial resource update with skill_id FK guard; (payload, error).

    Called by routers/catalog_admin.update_resource."""
    resource = repo.get_resource(db, resource_id)
    if not resource:
        return None, "Resource not found"
    fields = data.model_dump(exclude_unset=True)
    if "skill_id" in fields:
        error = integrity.ensure_resource_skill_exists(db, fields["skill_id"])
        if error:
            return None, error
    return repo.update_resource(db, resource, fields), None


def delete_resource(db, resource_id: int,
                    force: bool = False) -> tuple[bool, str | dict | None]:
    """Restricted delete guarded by path_steps JSON census; (ok, error).

    Called by routers/catalog_admin.delete_resource; ?force=true skips the
    catalog_integrity census so the referencing path_steps survive with a
    detached resource list.
    """
    resource = repo.get_resource(db, resource_id)
    if not resource:
        return False, "Resource not found"
    if not force:
        conflict = integrity.resource_delete_conflict(db, resource_id)
        if conflict:
            return False, conflict
    if not repo.delete_resource(db, resource_id):
        return False, "Resource not found"
    return True, None


# ── Job roles ─────────────────────────────────────────────────────────

def _serialize_job_role(db, role, role_skill_map=None) -> dict:
    """Job role row + ordered required-skill ids from job_role_skills.

    When role_skill_map is provided (batch mode), look up skill ids
    from the pre-built dict instead of querying per role."""
    if role_skill_map is not None:
        skill_ids = role_skill_map.get(role.id, [])
    else:
        skill_ids = repo.get_job_role_skill_ids(db, role.id)
    return {
        "id": role.id, "title": role.title, "description": role.description,
        "career_field": role.career_field,
        "skill_ids": skill_ids,
    }


def list_job_roles(db) -> list[dict]:
    """All job roles serialized; admin CRUD + wizard source data.

    Batch-fetches role-skill mappings to eliminate N+1 queries."""
    roles = repo.get_all_job_roles(db)
    role_skill_map = repo.get_job_role_skill_map(db)
    return [_serialize_job_role(db, r, role_skill_map) for r in roles]


def create_job_role(db, data: JobRoleCreate) -> tuple[dict | None, str | None]:
    """Title-uniqueness + skill-FK guarded creation; (payload, error).

    Called by routers/catalog_admin.create_job_role; duplicate link ids
    intentionally reach the composite PK so main.py's IntegrityError
    handler answers 409 with the whole insert rolled back."""
    if repo.get_job_role_by_title(db, data.title):
        return None, "Job role already exists"
    ids = _skill_ids(data.skill_ids)
    error = integrity.ensure_skills_exist(db, ids, "skill_ids")
    if error:
        return None, error
    role = repo.create_job_role(db, data.title, data.description,
                                data.career_field)
    if ids:
        repo.set_job_role_skills(db, role.id, ids)
    else:
        db.commit()
        db.refresh(role)
    return _serialize_job_role(db, role), None


def update_job_role(db, job_role_id: int,
                    data: JobRoleUpdate) -> tuple[dict | None, str | None]:
    """Validated partial update incl. replacing required-skill links.

    Called by routers/catalog_admin.update_job_role; renames are
    case-insensitively unique excluding this row and replacement links
    commit atomically with scalar changes."""
    role = repo.get_job_role(db, job_role_id)
    if not role:
        return None, "Job role not found"
    fields = data.model_dump(exclude_unset=True)
    if "title" in fields and fields["title"].lower() != role.title.lower():
        if repo.get_job_role_by_title(db, fields["title"]):
            return None, "Job role already exists"
    raw_ids = fields.pop("skill_ids", None)
    ids = _skill_ids(raw_ids) if raw_ids is not None else None
    if ids is not None:
        error = integrity.ensure_skills_exist(db, ids, "skill_ids")
        if error:
            return None, error
    updated = repo.update_job_role(db, role, fields)
    if ids is not None:
        repo.set_job_role_skills(db, updated.id, ids)
    else:
        db.commit()
        db.refresh(updated)
    return _serialize_job_role(db, updated), None


def delete_job_role(db, job_role_id: int,
                    force: bool = False) -> tuple[bool, str | dict | None]:
    """Restricted delete guarded by mapping census; (ok, error) tuple.

    Called by routers/catalog_admin.delete_job_role; force cascades the
    job_role_skills rows away with the role."""
    role = repo.get_job_role(db, job_role_id)
    if not role:
        return False, "Job role not found"
    if not force:
        conflict = integrity.job_role_delete_conflict(db, job_role_id)
        if conflict:
            return False, conflict
    repo.delete_job_role(db, job_role_id)
    return True, None


# ── Learner catalog (public browse) ───────────────────────────────────

def _skill_link(db, skill_id: int, skill_map=None) -> dict | None:
    """Tiny {id, name} for a skill or None; prerequisite/follower strips.

    When skill_map is provided (batch mode), look up the skill by id
    from the pre-built dict instead of querying the database."""
    if skill_map is not None:
        skill = skill_map.get(skill_id)
    else:
        skill = repo.get_skill(db, skill_id)
    if not skill:
        return None
    details = {"id": skill.id, "name": skill.name,
               "difficulty_level": skill.difficulty_level}
    if skill.difficulty_level is not None:
        details["difficulty_level"] = skill.difficulty_level
    return details


def _category_name(db, category_id: int | None,
                   categories_map=None) -> str | None:
    """Human name for a category id, or None when absent.

    When categories_map is provided (batch mode), look up the category
    by id from the pre-built dict instead of querying the database."""
    if category_id is None:
        return None
    if categories_map is not None:
        cat = categories_map.get(category_id)
    else:
        cat = db.query(Category).filter(Category.id == category_id).first()
    return cat.name if cat else None


def serialize_skill_detail(db, skill) -> dict:
    """Learner-facing skill detail (catalog page).

    Adds prerequisite + follower {id,name} strips and the parent category
    name on top of the admin _serialize_skill shape. Called by routers/
    catalog.get_skill_detail; consumed by the catalog skill view."""
    base = _serialize_skill(db, skill)
    graph = repo.get_prerequisite_graph(db)
    all_skill_ids = set(graph.keys())
    for pres in graph.values():
        all_skill_ids.update(pres)
    skill_map = repo.get_skills_by_map(db, list(all_skill_ids))
    categories_map = repo.get_categories_map(db)
    prereqs = [_skill_link(db, pid, skill_map)
               for pid in sorted(graph.get(skill.id, []))]
    prereqs = [p for p in prereqs if p is not None]
    followers = [fid for fid, pres in graph.items()
                 if skill.id in pres]
    follower_links = [_skill_link(db, fid, skill_map)
                      for fid in sorted(followers)]
    follower_links = [f for f in follower_links if f is not None]
    base["category_name"] = _category_name(
        db, skill.category_id, categories_map)
    base["prerequisites"] = prereqs
    base["recommended"] = follower_links
    return base


def list_catalog_roles(db) -> list[dict]:
    """Lean learner-facing job-role list with ordered skill names.

    Called by routers/catalog.list_roles; drives the catalog role picker
    and RecommendedStrip joins without admin skill_ids plumbing.
    Batch-fetches all role-skill mappings and skills to eliminate N+1."""
    roles = repo.get_all_job_roles(db)
    role_skill_map = repo.get_job_role_skill_map(db)
    all_skill_ids = set()
    for sids in role_skill_map.values():
        all_skill_ids.update(sids)
    skill_map = repo.get_skills_by_map(db, list(all_skill_ids))
    out = []
    for role in roles:
        skill_ids = role_skill_map.get(role.id, [])
        skills = [s for s in (_skill_link(db, sid, skill_map)
                              for sid in skill_ids)
                  if s is not None]
        out.append({
            "id": role.id, "title": role.title,
            "description": role.description,
            "career_field": role.career_field,
            "skills": skills,
        })
    return out
