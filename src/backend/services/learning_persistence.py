"""Learning persistence — plan persistence and proficiency lookup.

Helpers for path generation: persisting paths+steps, picking resources,
and looking up existing user proficiency. Called by learning_service.
"""

from backend.entities.catalog import Resource
from backend.entities.learning import UserSkill
from backend.repositories import catalog_repository
from backend.repositories import learning_repository as lrepo

MASTERY_LEVEL = 3


def user_proficiency_by_name(db, user_id: int, skill_rows: list) -> dict[str, int]:
    """Map skill name -> existing proficiency from user_skills; 0 unknown."""
    rows = db.query(UserSkill).filter_by(user_id=user_id).all()
    by_id = {r.skill_id: r.proficiency_level for r in rows}
    return {s.name: by_id.get(s.id, 0) for s in skill_rows}


def pick_resource_ids(pool: list[Resource], skill, preferences: dict) -> list[int]:
    """Up to two resource ids for a step: skill-owned first, then any
    pool entries matching is_free/format/language preferences.

    Caller pre-fetches the pool once (batch) instead of per-step queries.
    """
    preferences = preferences or {}
    owned = [r for r in pool if r.skill_id == skill.id]
    free = preferences.get("is_free", True)
    candidates = [r for r in pool if not free or r.is_free]
    fmt = preferences.get("format") or "any"
    if fmt != "any":
        if isinstance(fmt, list):
            candidates = [r for r in candidates if r.type in fmt]
        else:
            candidates = [r for r in candidates if r.type == fmt]
    lang = preferences.get("language") or "en"
    matched = [r for r in candidates if r.language == lang] or candidates
    ordered = owned + [r for r in matched if r not in owned]
    return [r.id for r in ordered[:2]]


def persist_plan(db, user_id: int, title: str, description: str,
                 target_role: str | None, plan: list,
                 levels: dict[str, int], current: dict[str, int],
                 preferences: dict):
    """Create path + ordered steps (+ resource bridges); commits.

    levels/current are name-keyed; selected_level starts at the desired
    level (levels) falling back to the user's current proficiency.
    Returns the created Path.
    """
    total_hours = sum((s.estimated_hours or 10) for s in plan)
    path = lrepo.create_path(
        db, user_id=user_id, title=title, description=description,
        target_role=target_role, total_hours=total_hours,
        total_weeks=max(1, round(total_hours / max(preferences.get("weekly_hours", 10), 1))))
    resource_pool = catalog_repository.get_all_resources(db)
    prefs = preferences.get("prefs") or {}
    for position, skill in enumerate(plan, start=1):
        resource_ids = pick_resource_ids(resource_pool, skill, prefs)
        selected = levels.get(skill.name, current.get(skill.name, 0))
        step = lrepo.create_step(
            db, path_id=path.id, position=position,
            title=f"Master {skill.name}",
            description=(f"Achieve proficiency in {skill.name}. "
                         f"Current level: {selected}. "
                         f"Target: {MASTERY_LEVEL}."),
            estimated_hours=skill.estimated_hours or 8,
            resource_ids=resource_ids)
        step.skill_id = skill.id
        step.selected_level = selected
        step.current_level = selected
    db.commit()
    return path
