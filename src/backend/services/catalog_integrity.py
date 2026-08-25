"""Catalog integrity enforcement — FK checks, cycle rules, delete guards.

Called by services/catalog_service.py during create/update/delete of
skills, categories, resources and job roles; dependent counts come from
repositories/integrity_repository.py. Error strings follow the shared
router contract (routers/error_mapping.status_for_error): '*not found*'
→ 404, 'already exists' → 409, unknown references and cycle violations
→ 400.
"""

from sqlalchemy.orm import Session

from backend.entities.catalog import Category, Skill
from backend.repositories import catalog_repository as repo
from backend.repositories import integrity_repository as irepo


def ensure_category_exists(db: Session, category_id: int | None) -> str | None:
    """FK guard for skills.category_id writes.

    Called by catalog_service.create/update_skill; a set but unknown
    category_id must surface as 400 before any INSERT happens.
    """
    if category_id is None:
        return None
    exists = db.query(Category.id).filter(Category.id == category_id).first()
    return None if exists else f"Unknown category_id={category_id}"


def ensure_resource_skill_exists(db: Session,
                                 skill_id: int | None) -> str | None:
    """FK guard for resources.skill_id writes.

    Called by catalog_service.create/update_resource; mirrors the
    category guard so bad references never reach the database layer.
    """
    if skill_id is None:
        return None
    exists = db.query(Skill.id).filter(Skill.id == skill_id).first()
    return None if exists else f"Unknown skill_id={skill_id}"


def ensure_skills_exist(db: Session, skill_ids: list[int],
                        label: str) -> str | None:
    """Batch FK guard for skill-id lists (prereqs, job-role links).

    Called by catalog_service.create/update_skill (label
    'prerequisite_ids') and create/update_job_role (label 'skill_ids');
    names every missing id in one 400-mapped message.
    """
    requested = [int(sid) for sid in (skill_ids or [])]
    if not requested:
        return None
    known = {row for (row,) in
             db.query(Skill.id).filter(Skill.id.in_(requested)).all()}
    missing = sorted({sid for sid in requested if sid not in known})
    if missing:
        return f"{label} contains unknown skill ids: {missing}"
    return None


def ensure_parent_rules(db: Session, category_id: int | None,
                        parent_id: int | None) -> str | None:
    """Self-parent, existence and ancestor-cycle guard for categories.

    Called by catalog_service.create/update_category; walks the
    categories.parent_id chain from the proposed parent — re-reaching
    `category_id` proves the new edge would close a loop. Pass
    category_id=None for brand-new rows (self-parent impossible).
    """
    if parent_id is None:
        return None
    seen = {category_id} if category_id is not None else set()
    current = parent_id
    while current is not None:
        row = db.query(Category).filter(Category.id == current).first()
        if row is None:
            return f"Unknown parent_id={parent_id}"
        if current in seen:
            if current == parent_id and category_id == parent_id:
                return "A category cannot be its own parent"
            return "Category parent assignment would create a cycle"
        seen.add(current)
        current = row.parent_id
    return None


def ensure_prerequisite_rules(db: Session, skill_id: int | None,
                              prerequisite_ids: list[int]) -> str | None:
    """Self-prereq, FK-existence and DAG-cycle guard for skill writes.

    Called by catalog_service.update_skill with the real skill id;
    adding edges skill→candidates creates a cycle iff the DFS over
    repo.get_prerequisite_graph starting at the candidates reaches
    skill_id again (skill_id=None on create skips that check).
    """
    if skill_id is not None and skill_id in set(prerequisite_ids or []):
        return "A skill cannot be its own prerequisite"
    fk_error = ensure_skills_exist(db, prerequisite_ids, "prerequisite_ids")
    if fk_error:
        return fk_error
    if skill_id is None:
        return None
    graph = repo.get_prerequisite_graph(db)
    stack, seen = list(dict.fromkeys(prerequisite_ids or [])), set()
    while stack:
        node = stack.pop()
        if node == skill_id:
            return "Adding these prerequisites would create a cycle"
        if node in seen:
            continue
        seen.add(node)
        stack.extend(graph.get(node, []))
    return None


def _delete_conflict(counts: dict[str, int], entity: str) -> dict | None:
    """Build the structured 409 payload when dependents exist.

    Shared by the three *_delete_conflict wrappers below; empty census
    means the delete may proceed unrestricted.
    """
    if not counts:
        return None
    return {
        "dependents": counts,
        "message": f"Cannot delete {entity}: it is referenced by other "
                   f"records. Retry with ?force=true to delete anyway.",
    }


def skill_delete_conflict(db: Session, skill_id: int) -> dict | None:
    """Restricted-delete payload for skills (all referencing tables).

    Called by catalog_service.delete_skill before the hard delete.
    """
    return _delete_conflict(
        irepo.count_skill_dependents(db, skill_id), "skill")


def category_delete_conflict(db: Session, category_id: int) -> dict | None:
    """Restricted-delete payload for categories (child-skill census).

    Called by catalog_service.delete_category before the hard delete.
    """
    return _delete_conflict(
        irepo.count_category_skills(db, category_id), "category")


def job_role_delete_conflict(db: Session, job_role_id: int) -> dict | None:
    """Restricted-delete payload for job roles (mapping-row census).

    Called by catalog_service.delete_job_role before the hard delete.
    """
    return _delete_conflict(
        irepo.count_job_role_dependencies(db, job_role_id), "job role")
