"""Learning serialization — step/path formatting helpers.

Pure functions for converting PathStep rows into wire-format dicts.
Imported by learning_service.py; zero DB access in this module (all
data arrives via pre-fetched maps from batch helpers).
"""

from backend.entities.catalog import Resource, Skill
from backend.entities.learning import PathStep, UserSkill


def collect_ids_from_steps(steps: list[PathStep]) -> tuple[set[int], set[int]]:
    """Collect all resource and skill ids from a list of steps."""
    resource_ids, skill_ids = set(), set()
    for step in steps:
        for rid in (step.resource_ids or []):
            resource_ids.add(rid)
        if step.skill_id:
            skill_ids.add(step.skill_id)
    return resource_ids, skill_ids


def serialize_step(step, completed_ids: set[int], resource_map: dict,
                   skill_map: dict, user_skill_map: dict) -> dict:
    """One steps[] entry; content mirrors description and is_completed
    comes from the completed-step id set. Zero DB queries — all data
    arrives via pre-fetched maps. Emits skill linkage, ordering, duration
    and current_topic (first weak_point still open, else first topic)."""
    resources = []
    for rid in (step.resource_ids or []):
        r = resource_map.get(rid)
        if r:
            resources.append({"id": r.id, "title": r.title,
                              "url": r.url, "type": r.type})
    skill = None
    current_topic = None
    if step.skill_id:
        sk = skill_map.get(step.skill_id)
        if sk:
            skill = {"id": sk.id, "name": sk.name,
                      "difficulty_level": sk.difficulty_level}
            topics = [str(x) for x in (sk.topics or []) if str(x).strip()]
            if topics:
                us = user_skill_map.get(sk.id)
                weak = set(us.weak_points or []) if us else set()
                current_topic = next(
                    (t for t in topics if t in weak), topics[0])
    return {
        "id": step.id, "step_number": step.position, "title": step.title,
        "content": step.description, "is_completed": step.id in completed_ids,
        "skill_id": step.skill_id, "order_index": step.position,
        "duration_hours": step.estimated_hours, "skill": skill,
        "current_topic": current_topic,
        "selected_level": step.selected_level,
        "current_level": step.current_level,
        "resources": resources, "resource_ids": step.resource_ids or [],
        "assessment_ids": step.assessment_ids or [],
    }


def path_progress(steps: list[dict]) -> float:
    """Fraction (0..1) of steps marked is_completed; 0 when empty.

    Caller passes already-serialized steps so the same logic serves both
    the detail and list serializers without re-querying completions.
    """
    if not steps:
        return 0
    done = sum(1 for s in steps if s.get("is_completed"))
    return round(done / len(steps), 4)


def path_skills(skill_map: dict, steps: list[PathStep]) -> list[dict]:
    """Distinct [{id,name}] skill list derived from step skill links
    (the reduced schema has no separate path-skill mapping)."""
    seen, out = set(), []
    for step in steps:
        if step.skill_id and step.skill_id not in seen:
            seen.add(step.skill_id)
            sk = skill_map.get(step.skill_id)
            if sk:
                out.append({"id": sk.id, "name": sk.name})
    return out


def selected_levels_by_step(skill_map: dict, steps: list[PathStep]) -> dict[str, int]:
    """Skill name -> selected_level for a path's steps; frontend contract."""
    out = {}
    for step in steps:
        if step.skill_id:
            sk = skill_map.get(step.skill_id)
            if sk:
                out[sk.name] = step.selected_level
    return out
