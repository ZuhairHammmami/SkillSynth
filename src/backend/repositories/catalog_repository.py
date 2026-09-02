"""Catalog repository — skills, categories, resources and job roles.

Called by the catalog/learning/wizard services; pure data access, no
business rules and no serialization.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.dto.catalog import SkillCreate
from backend.entities.catalog import (
    Category, JobRole, JobRoleSkill, Resource, Skill, SkillPrerequisite,
)
# ── Skills ──

def get_skill(db: Session, skill_id: int) -> Skill | None:
    """Fetch a skill by PK; called by catalog/learning services."""
    return db.query(Skill).filter(Skill.id == skill_id).first()


def get_skill_by_name(db: Session, name: str) -> Skill | None:
    """Case-insensitive exact-name lookup; used for name→id resolution."""
    return db.query(Skill).filter(Skill.name.ilike(name)).first()


def get_skills_by_ids(db: Session, ids: list[int]) -> list[Skill]:
    """Batch fetch preserving caller order; empty ids -> empty list."""
    if not ids:
        return []
    rows = db.query(Skill).filter(Skill.id.in_(ids)).all()
    order = {sid: i for i, sid in enumerate(ids)}
    return sorted(rows, key=lambda s: order.get(s.id, len(order)))


def get_all_skills(db: Session) -> list[Skill]:
    """Full skill listing; feeds graph nodes + wizard gap analysis."""
    return db.query(Skill).order_by(Skill.id).all()


def get_skills_by_category(db: Session, category_id: int) -> list[Skill]:
    """All skills in one category, id-ordered; called by catalog service."""
    return db.query(Skill).filter(
        Skill.category_id == category_id).order_by(Skill.id).all()


def create_skill(db: Session, data: SkillCreate) -> Skill:
    """Insert a skill plus its prerequisite edges; commits. Called by
    catalog_service.create_skill; legacy category_ids collapses to the
    first entry (single category_id FK in the reduced schema)."""
    category_id = data.category_id
    if category_id is None and data.category_ids:
        category_id = data.category_ids[0]
    skill = Skill(
        name=data.name, description=data.description,
        difficulty_level=data.difficulty_level or 5,
        estimated_hours=data.estimated_hours or 10,
        icon=data.icon, color=data.color, category_id=category_id,
    )
    db.add(skill)
    db.flush()
    for prereq_id in data.prerequisite_ids:
        db.add(SkillPrerequisite(skill_id=skill.id, prerequisite_id=prereq_id))
    db.commit()
    db.refresh(skill)
    return skill


def update_skill(db: Session, skill: Skill, fields: dict) -> Skill:
    """Apply non-None scalar fields, then rebuild prerequisite edges."""
    prerequisite_ids = fields.pop("prerequisite_ids", None)
    for key, value in fields.items():
        setattr(skill, key, value)
    if prerequisite_ids is not None:
        db.query(SkillPrerequisite).filter(
            SkillPrerequisite.skill_id == skill.id).delete()
        for prereq_id in prerequisite_ids:
            db.add(SkillPrerequisite(
                skill_id=skill.id, prerequisite_id=prereq_id))
    db.commit()
    db.refresh(skill)
    return skill


def delete_skill(db: Session, skill_id: int) -> bool:
    """Hard-delete a skill; FK ondelete rules clean up references."""
    skill = get_skill(db, skill_id)
    if not skill:
        return False
    db.delete(skill)
    db.commit()
    return True


def get_prerequisite_graph(db: Session) -> dict[int, list[int]]:
    """skill_id -> [prerequisite_id] map; consumed by the topo sort and
    gap chain walk in learning_service."""
    graph: dict[int, list[int]] = {}
    for row in db.query(SkillPrerequisite).all():
        graph.setdefault(row.skill_id, []).append(row.prerequisite_id)
    return graph


def get_prerequisite_chain(db: Session, skill_id: int) -> list[int]:
    """Depth-first prerequisite closure, deps first; called by
    learning_service.analyze_gaps to attach unmet prereqs."""
    graph = get_prerequisite_graph(db)
    visited: set[int] = set()
    chain: list[int] = []

    def _visit(sid: int) -> None:
        """Recursive DFS appending deps before the node itself."""
        if sid in visited:
            return
        visited.add(sid)
        for prereq_id in graph.get(sid, []):
            _visit(prereq_id)
        chain.append(sid)

    _visit(skill_id)
    return chain


def count_skill_resources(db: Session) -> dict[int, int]:
    """skill_id -> resource_count map; graph node decoration."""
    rows = (
        db.query(Resource.skill_id, func.count(Resource.id))
        .filter(Resource.skill_id.isnot(None))
        .group_by(Resource.skill_id)
        .all()
    )
    return {skill_id: cnt for skill_id, cnt in rows}
# ── Categories ──

def get_all_categories(db: Session) -> list[Category]:
    """Full category listing; admin CRUD + graph categories."""
    return db.query(Category).order_by(Category.id).all()


def get_category_by_name(db: Session, name: str) -> Category | None:
    """Case-insensitive name lookup guarding duplicate categories."""
    return db.query(Category).filter(Category.name.ilike(name)).first()


def create_category(db: Session, name: str, description: str | None = None) -> Category:
    """Insert a top-level category; commits."""
    cat = Category(name=name, description=description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, category: Category, fields: dict) -> Category:
    """Apply non-None fields onto a category row; commits."""
    for key, value in fields.items():
        if value is not None:
            setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    """Hard-delete a category; skills keep NULL category_id via SET NULL."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        return False
    db.delete(cat)
    db.commit()
    return True
# ── Resources ──

def get_resource(db: Session, resource_id: int) -> Resource | None:
    """Fetch a resource by PK; called by catalog_service.update/delete."""
    return db.query(Resource).filter(Resource.id == resource_id).first()


def get_all_resources(db: Session) -> list[Resource]:
    """Full resource listing; feeds the recommendation pool."""
    return db.query(Resource).order_by(Resource.id).all()


def get_resources_by_ids(db: Session, ids: list[int]) -> list[Resource]:
    """Batch fetch for step.resource_ids hydration; empty -> []."""
    if not ids:
        return []
    return db.query(Resource).filter(Resource.id.in_(ids)).all()


def get_resources_by_urls(db: Session, urls: list[str]) -> dict[str, Resource]:
    """url -> Resource map; generation dedupes resources by URL."""
    if not urls:
        return {}
    rows = db.query(Resource).filter(Resource.url.in_(urls)).all()
    return {r.url: r for r in rows}


def create_resource(db: Session, fields: dict) -> Resource:
    """Insert a resource from a validated DTO dump or dict; commits."""
    resource = Resource(**fields)
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def update_resource(db: Session, resource: Resource, fields: dict) -> Resource:
    """Apply non-None fields onto a resource row; commits."""
    for key, value in fields.items():
        if value is not None:
            setattr(resource, key, value)
    db.commit()
    db.refresh(resource)
    return resource


def delete_resource(db: Session, resource_id: int) -> bool:
    """Hard-delete a resource; returns False when missing."""
    resource = get_resource(db, resource_id)
    if not resource:
        return False
    db.delete(resource)
    db.commit()
    return True
# ── Job roles + mappings ──

def get_job_role(db: Session, job_role_id: int) -> JobRole | None:
    """Fetch a job role by PK; called by catalog_service.update/delete."""
    return db.query(JobRole).filter(JobRole.id == job_role_id).first()


def get_all_job_roles(db: Session) -> list[JobRole]:
    """Full listing ordered by id; wizard options + admin CRUD."""
    return db.query(JobRole).order_by(JobRole.id).all()


def get_job_role_by_title(db: Session, title: str) -> JobRole | None:
    """Case-insensitive title lookup; path generation entry point."""
    return db.query(JobRole).filter(JobRole.title.ilike(title)).first()


def get_job_role_skill_ids(db: Session, job_role_id: int) -> list[int]:
    """Ordered required-skill ids for one role (insertion order kept).

    Called by learning_service.generate_path to gap-fill from
    job_role_skills and by catalog_service to hydrate skill_ids.
    """
    rows = (
        db.query(JobRoleSkill.skill_id)
        .filter(JobRoleSkill.job_role_id == job_role_id)
        .all()
    )
    return [sid for (sid,) in rows]


def get_job_role_skill_names(db: Session, job_role_id: int) -> list[str]:
    """Required-skill names for one role, ordered by mapping insertion.

    Called by wizard_service.wizard_options to preview a field's skills
    in the frontend combobox; joins JobRoleSkill -> Skill.name."""
    return [
        name for (name,) in db.query(Skill.name)
        .join(JobRoleSkill, JobRoleSkill.skill_id == Skill.id)
        .filter(JobRoleSkill.job_role_id == job_role_id)
        .order_by(JobRoleSkill.skill_id)
        .all()
    ]


def get_path_skill_ids(db: Session) -> list[int]:
    """Every skill id mapped to any job role; most-requested report.

    Replaces the old PathSkill-based query because paths no longer keep
    their own skill mapping table in the reduced schema.
    """
    return [sid for (sid,) in db.query(JobRoleSkill.skill_id).all()]


def create_job_role(db: Session, title: str, description: str | None,
                    career_field: str | None) -> JobRole:
    """Insert a job role without skill links; flushes WITHOUT committing.

    Caller catalog_service.create_job_role commits role+links together,
    so failed inserts roll back orphan-free (409 safety net)."""
    role = JobRole(title=title, description=description,
                   career_field=career_field)
    db.add(role)
    db.flush()
    db.refresh(role)
    return role


def set_job_role_skills(db: Session, job_role_id: int,
                        skill_ids: list[int]) -> None:
    """Replace the role's skill mapping rows atomically; commits."""
    db.query(JobRoleSkill).filter(
        JobRoleSkill.job_role_id == job_role_id).delete()
    for sid in skill_ids:
        db.add(JobRoleSkill(job_role_id=job_role_id, skill_id=sid))
    db.commit()


def update_job_role(db: Session, role: JobRole, fields: dict) -> JobRole:
    """Apply non-None fields onto a job_roles row; flushes only; caller
    catalog_service.update_job_role commits links+scalars atomically."""
    for key, value in fields.items():
        if value is not None:
            setattr(role, key, value)
    db.flush()
    db.refresh(role)
    return role


def delete_job_role(db: Session, job_role_id: int) -> bool:
    """Hard-delete a role; mapping rows cascade away."""
    role = get_job_role(db, job_role_id)
    if not role:
        return False
    db.delete(role)
    db.commit()
    return True
# ── Batch-fetch helpers (N+1 elimination) ──

def get_skills_by_map(db: Session, ids: list[int]) -> dict[int, Skill]:
    """Fetch skills by ID list, return {id: Skill} dict. Skips missing."""
    if not ids:
        return {}
    rows = db.query(Skill).filter(Skill.id.in_(ids)).all()
    return {r.id: r for r in rows}


def get_resources_by_map(db: Session, ids: list[int]) -> dict[int, Resource]:
    """Fetch resources by ID list, return {id: Resource} dict."""
    if not ids:
        return {}
    rows = db.query(Resource).filter(Resource.id.in_(ids)).all()
    return {r.id: r for r in rows}


def get_prereqs_by_skill_ids(db: Session,
                             skill_ids: list[int]) -> dict[int, list[Skill]]:
    """skill_id -> [prerequisite Skills] for batch prerequisite hydration."""
    if not skill_ids:
        return {}
    edges = db.query(SkillPrerequisite).filter(
        SkillPrerequisite.skill_id.in_(skill_ids)).all()
    prereq_ids = {e.prerequisite_id for e in edges}
    prereq_map = get_skills_by_map(db, list(prereq_ids))
    result: dict[int, list[Skill]] = {sid: [] for sid in skill_ids}
    for e in edges:
        skill_obj = prereq_map.get(e.prerequisite_id)
        if skill_obj:
            result[e.skill_id].append(skill_obj)
    return result


def get_categories_map(db: Session) -> dict[int, Category]:
    """Return {id: Category} for all categories; name lookups in loops."""
    rows = db.query(Category).all()
    return {c.id: c for c in rows}


def get_job_role_skill_map(db: Session) -> dict[int, list[int]]:
    """job_role_id -> [skill_id] for all roles; batch role→skill hydration."""
    rows = db.query(JobRoleSkill.job_role_id, JobRoleSkill.skill_id).all()
    result: dict[int, list[int]] = {}
    for role_id, skill_id in rows:
        result.setdefault(role_id, []).append(skill_id)
    return result
