"""Learning service — graph, path generation and step progress.

Called by the learning/progress/path routers (Task 3). Generation is
deterministic: goals are gap-filled against user_skills, ordered by a
Kahn topo-sort over skill_prerequisites, then persisted as
path + path_steps + user_skills rows. Wire keys stay frozen (int
path ids, steps[].is_completed); gap analysis lives in analytics_service.
"""

from collections import defaultdict, deque
from datetime import datetime, timedelta, UTC

from backend.dto.learning import StepCompletionResponse
from backend.entities.learning import Path, UserSkill
from backend.repositories import assess_repository, catalog_repository
from backend.repositories import learning_repository as lrepo
from backend.services.assess_service import normalize_key

MASTERY_LEVEL = 3


def build_graph(db) -> dict:
    """Knowledge-graph payload (nodes/edges/categories) for
    GET /learning/graph; node decoration comes from catalog counts."""
    counts = catalog_repository.count_skill_resources(db)
    categories = catalog_repository.get_all_categories(db)
    nodes = [{
        "id": s.id, "name": s.name, "difficulty": s.difficulty_level or 1,
        "icon": s.icon, "color": s.color,
        "category_ids": [s.category_id] if s.category_id else [],
        "resource_count": counts.get(s.id, 0),
    } for s in catalog_repository.get_all_skills(db)]
    edges = [{"source": p, "target": sid, "type": "prerequisite"}
             for sid, prereqs in
             catalog_repository.get_prerequisite_graph(db).items()
             for p in prereqs]
    return {"nodes": nodes, "edges": edges,
            "categories": [{"id": c.id, "name": c.name} for c in categories]}


def topological_sort(db) -> list[int]:
    """Kahn topo-sort over all skills; deterministic id tie-break."""
    return [s.id for s in _order_by_prereqs(
        db, catalog_repository.get_all_skills(db))]


def _order_by_prereqs(db, skill_rows: list) -> list:
    """Topo-order a skill subset so prerequisites come first."""
    graph = catalog_repository.get_prerequisite_graph(db)
    ids = {s.id for s in skill_rows}
    by_id = {s.id: s for s in skill_rows}
    indeg = {sid: len([p for p in graph.get(sid, []) if p in ids]) for sid in ids}
    dependents: dict[int, list[int]] = defaultdict(list)
    for sid in ids:
        for prereq in graph.get(sid, []):
            if prereq in ids:
                dependents[prereq].append(sid)
    queue = deque(sorted(sid for sid, deg in indeg.items() if deg == 0))
    ordered = []
    while queue:
        sid = queue.popleft()
        ordered.append(by_id[sid])
        for dep in sorted(dependents[sid]):
            indeg[dep] -= 1
            if indeg[dep] == 0:
                queue.append(dep)
    ordered.extend(by_id[sid] for sid in sorted(ids - {s.id for s in ordered}))
    return ordered


def _score_answers(db, skill_rows: list, answers: dict[str, int],
                   user_id: int, persist: bool = True) -> dict[int, int]:
    """Proficiency per skill from wizard answers (upserts user_skills).

    Graded against assessment_questions.correct_index using ids built
    by assess_service.normalize_key. A skill keeps its existing level
    when the user gave no answers for it (empty answers must never
    downgrade mastery); answered skills take the computed level.
    persist=False makes the pass read-only for /wizard/analysis.
    """
    ids = [s.id for s in skill_rows]
    assessments = assess_repository.get_assessments_for_skills(db, ids)
    current = assess_repository.get_skill_profile(db, user_id)
    levels: dict[int, int] = {}
    for skill in skill_rows:
        assessment = assessments.get(skill.id)
        questions = (assess_repository.get_questions(db, assessment.id)
                     if assessment else [])
        answered = {
            i: answers[f"{normalize_key(skill.name).lower()}_q{i}"]
            for i in range(len(questions))
            if f"{normalize_key(skill.name).lower()}_q{i}" in answers
        }
        if questions and answered:
            correct = sum(
                1 for i, q in enumerate(questions)
                if i in answered and answered[i] == q.correct_index)
            level = max(0, min(5, round(correct / len(questions) * 5)))
        else:
            level = current.get(skill.name, 0)
        levels[skill.id] = level
        if persist:
            assess_repository.upsert_user_skill(db, user_id, skill.id, level)
    return levels


def _pick_resource_ids(db, skill, preferences: dict) -> list[int]:
    """Up to two resource ids for a step: skill-owned first, then any
    pool entries matching is_free/format/language preferences.

    format accepts a single string (exact match), "any"/empty (accept all),
    or a list of strings (resource type in that list).
    """
    preferences = preferences or {}
    pool = catalog_repository.get_all_resources(db)
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


def _user_proficiency_by_name(db, user_id: int, skill_rows: list) -> dict[str, int]:
    """Map skill name -> existing proficiency from user_skills; 0 unknown."""
    rows = db.query(UserSkill).filter_by(user_id=user_id).all()
    by_id = {r.skill_id: r.proficiency_level for r in rows}
    return {s.name: by_id.get(s.id, 0) for s in skill_rows}


def _persist_plan(db, user_id: int, title: str, description: str,
                  target_role: str | None, plan: list,
                  levels: dict[str, int], current: dict[str, int],
                  preferences: dict) -> Path:
    """Create path + ordered steps (+ resource bridges); commits.

    levels/current are name-keyed; selected_level starts at the desired
    level (levels) falling back to the user's current proficiency.
    """
    total_hours = sum((s.estimated_hours or 10) for s in plan)
    path = lrepo.create_path(
        db, user_id=user_id, title=title, description=description,
        target_role=target_role, total_hours=total_hours,
        total_weeks=max(1, round(total_hours / max(preferences.get("weekly_hours", 10), 1))))
    for position, skill in enumerate(plan, start=1):
        resource_ids = _pick_resource_ids(db, skill, preferences.get("prefs") or {})
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


def generate_path(db, user, data) -> tuple[dict | None, str | None]:
    """Wizard generation for POST /generate-path (full detail payload).

    Resolves the goal job role, scores data.answers into user_skills
    and returns a wire-compatible path-detail dict.
    """
    role = catalog_repository.get_job_role_by_title(db, data.goal)
    if not role:
        return None, f"Could not find skills for job role '{data.goal}'."
    skill_rows = catalog_repository.get_skills_by_ids(
        db, catalog_repository.get_job_role_skill_ids(db, role.id))
    if not skill_rows:
        return None, f"Could not find skills for job role '{data.goal}'."
    preferences = {"weekly_hours": data.weekly_hours,
                   "prefs": data.preferences.model_dump(exclude_unset=True)}
    scored = _score_answers(db, skill_rows, data.answers or {}, user.id)
    plan = _order_by_prereqs(db, [s for s in skill_rows
                                  if scored[s.id] < MASTERY_LEVEL])
    hours = sum((s.estimated_hours or 10) for s in plan)
    weeks = max(1, round(hours / max(data.weekly_hours, 1)))
    current = _user_proficiency_by_name(db, user.id, skill_rows)
    path = _persist_plan(
        db, user.id, f"{role.title} Learning Path",
        f"Personalized path toward {role.title}. Estimated {hours}h over {weeks} weeks.",
        role.title, plan, data.levels, current, preferences)
    return format_path_detail(db, path, user.id), None


def _serialize_step(db, step, completed_ids: set[int], user_id: int) -> dict:
    """One steps[] entry; content mirrors description and is_completed
    comes from the completed-step id set. Emits skill linkage, ordering
    and duration so the frontend detail view renders without remapping.
    current_topic is the first of the skill's topics still in the
    learner's weak_points (the topic to master now); falls back to the
    skill's first topic when no weak points remain."""
    resources = []
    for resource in catalog_repository.get_resources_by_ids(
            db, step.resource_ids or []):
        resources.append({"id": resource.id, "title": resource.title,
                          "url": resource.url, "type": resource.type})
    skill = None
    current_topic = None
    if step.skill_id:
        sk = catalog_repository.get_skill(db, step.skill_id)
        if sk:
            skill = {"id": sk.id, "name": sk.name,
                      "difficulty_level": sk.difficulty_level}
            topics = [str(x) for x in (sk.topics or []) if str(x).strip()]
            if topics:
                us = db.query(UserSkill).filter_by(
                    user_id=user_id, skill_id=sk.id).first()
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


def _path_progress(steps: list[dict]) -> float:
    """Fraction (0..1) of steps marked is_completed; 0 when empty.

    Caller passes already-serialized steps so the same logic serves both
    the detail and list serializers without re-querying completions.
    """
    if not steps:
        return 0
    done = sum(1 for s in steps if s.get("is_completed"))
    return round(done / len(steps), 4)


def _path_skills(db, path: Path) -> list[dict]:
    """Distinct [{id,name}] skill list derived from step skill links
    (the reduced schema has no separate path-skill mapping)."""
    seen, out = set(), []
    for step in lrepo.get_steps(db, path.id):
        if step.skill_id and step.skill_id not in seen:
            seen.add(step.skill_id)
            skill = catalog_repository.get_skill(db, step.skill_id)
            if skill:
                out.append({"id": skill.id, "name": skill.name})
    return out


def format_path_detail(db, path: Path, user_id: int) -> dict:
    """Full path payload (int ids, goal_job_role, skills[], steps[])."""
    completed = lrepo.completed_step_ids(db, user_id)
    steps = [_serialize_step(db, s, completed, user_id)
             for s in lrepo.get_steps(db, path.id)]
    return {
        "id": path.id, "profile_id": path.user_id,
        "title": path.title or "", "description": path.description,
        "status": path.status or "active",
        "progress": _path_progress(steps),
        "total_estimated_hours": path.total_estimated_hours,
        "total_hours": path.total_estimated_hours,
        "total_estimated_weeks": path.total_estimated_weeks,
        "goal_job_role": path.target_role,
        "created_at": path.created_at.isoformat() if path.created_at else None,
        "skills": _path_skills(db, path),
        "levels": _selected_levels_by_step(db, path.id),
        "steps": steps,
    }


def _selected_levels_by_step(db, path_id: int) -> dict[str, int]:
    """Skill name -> selected_level for a path's steps; frontend contract."""
    out = {}
    for step in lrepo.get_steps(db, path_id):
        if step.skill_id:
            skill = catalog_repository.get_skill(db, step.skill_id)
            if skill:
                out[skill.name] = step.selected_level
    return out


def progress_dashboard(db, user_id: int) -> dict:
    """GET /progress/dashboard payload — frontend-owned key contract:
    total_paths/total_steps/completed_steps/completion_percentage/
    remaining_hours/total_hours (+ additive weekly + paths blocks).
    Completions come from step_progress.completed_at."""
    seven_ago = datetime.now(UTC) - timedelta(days=7)
    paths = lrepo.get_paths_by_user(db, user_id)
    completed = lrepo.completed_step_ids(db, user_id)
    total_steps = lrepo.count_steps(db, user_id)
    completed_steps = lrepo.count_completions(db, user_id)
    pct = round(completed_steps / total_steps * 100, 1) if total_steps else 0
    total_hours = lrepo.sum_total_hours(db, user_id)
    completed_hours = round(total_hours * (pct / 100), 1) if pct > 0 else 0
    return {
        "total_paths": len(paths),
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "completion_percentage": pct,
        "remaining_hours": round(max(0.0, total_hours - completed_hours), 1),
        "total_hours": total_hours,
        "weekly": lrepo.count_completions(db, user_id, since=seven_ago),
        "paths": [{
            "id": p.id, "title": p.title or "", "description": p.description,
            "total_estimated_hours": p.total_estimated_hours,
            "total_hours": p.total_estimated_hours,
            "total_estimated_weeks": p.total_estimated_weeks,
            "goal_job_role": p.target_role,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "steps": (_psteps := [_serialize_step(db, s, completed, user_id)
                                  for s in lrepo.get_steps(db, p.id)]),
            "progress": _path_progress(_psteps),
        } for p in paths],
    }


def complete_step(db, user_id: int, step_id: int):
    """Mark an owned step complete; returns (response, error, status)."""
    step = lrepo.get_step(db, step_id)
    if not step:
        return None, "Step not found", 404
    path = lrepo.get_path(db, step.path_id, user_id)
    if not path:
        return None, "Path not found", 404
    row = lrepo.upsert_completion(db, user_id, step_id)
    completed_at = row.completed_at or datetime.now(UTC)
    response = StepCompletionResponse(
        profile_id=user_id, step_id=step_id, completed_at=completed_at)
    return response, None, 200


def undo_complete_step(db, user_id: int, step_id: int):
    """Revert a completion by deleting the progress row; returns the
    historical {"status":"reverted","step_id":...} payload."""
    if not lrepo.delete_completion(db, user_id, step_id):
        return None, "Completion not found", 404
    return {"status": "reverted", "step_id": step_id}, None, 200


def list_user_paths(db, user_id: int) -> list[dict]:
    """All of a user's paths as full detail payloads (GET /paths/)."""
    return [format_path_detail(db, p, user_id)
            for p in lrepo.get_paths_by_user(db, user_id)]
