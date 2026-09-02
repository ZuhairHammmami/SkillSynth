"""Learning service — path generation and step progress.

Called by the learning/progress/path routers (Task 3). Generation is
deterministic: goals are gap-filled against user_skills, ordered by a
Kahn topo-sort over skill_prerequisites, then persisted as
path + path_steps + user_skills rows. Wire keys stay frozen (int
path ids, steps[].is_completed); gap analysis lives in analytics_service.
"""

from datetime import datetime, timedelta, UTC

from backend.dto.learning import StepCompletionResponse
from backend.entities.learning import Path, PathStep
from backend.repositories import assess_repository, catalog_repository
from backend.repositories import learning_repository as lrepo
from backend.services.assess_service import normalize_key
from backend.services.learning_graph import _order_by_prereqs, build_graph, topological_sort
from backend.services.learning_persistence import (
    persist_plan, user_proficiency_by_name,
)
from backend.services.learning_serialization import (
    collect_ids_from_steps, path_progress, path_skills,
    selected_levels_by_step, serialize_step,
)

MASTERY_LEVEL = 3


def _score_answers(db, skill_rows: list, answers: dict[str, int],
                   user_id: int, persist: bool = True) -> dict[int, int]:
    """Proficiency per skill from wizard answers (upserts user_skills).

    Self-reported levels arrive as {skill.name: 0..5} and take priority
    (clamped then rounded). Legacy quiz answers keyed "<norm(name)>_q<i>"
    are graded against correct_index when present. A skill keeps its
    existing level when the user gave no signal for it. persist=False
    stays read-only for /wizard/analysis. Caller: generate_path.
    """
    ids = [s.id for s in skill_rows]
    assessments = assess_repository.get_assessments_for_skills(db, ids)
    current = assess_repository.get_skill_profile(db, user_id)
    levels: dict[int, int] = {}
    for skill in skill_rows:
        name = skill.name
        val = answers.get(name)
        if isinstance(val, (int, float)) and 0 <= val <= 5:
            level = int(round(val))
        else:
            assessment = assessments.get(skill.id)
            questions = (assess_repository.get_questions(db, assessment.id)
                         if assessment else [])
            norm = normalize_key(name).lower()
            answered = {i: answers[f"{norm}_q{i}"]
                        for i in range(len(questions)) if f"{norm}_q{i}" in answers}
            if questions and answered:
                correct = sum(1 for i, q in enumerate(questions)
                              if i in answered and answered[i] == q.correct_index)
                level = round(correct / len(questions) * 5)
            else:
                level = current.get(name, 0)
        levels[skill.id] = level
        if persist:
            assess_repository.upsert_user_skill(db, user_id, skill.id, level)
    return levels


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
    scored_by_name = {s.name: scored[s.id] for s in skill_rows}
    current = user_proficiency_by_name(db, user.id, skill_rows)
    levels = {**scored_by_name, **(data.levels or {})}
    path = persist_plan(
        db, user.id, f"{role.title} Learning Path",
        f"Personalized path toward {role.title}. Estimated {hours}h over {weeks} weeks.",
        role.title, plan, levels, current, preferences)
    return format_path_detail(db, path, user.id), None


def generate_path_for_skill(db, user, skill_id: int,
                            weekly_hours: int = 10,
                            preferences: dict | None = None
                            ) -> tuple[dict | None, str | None]:
    """Catalog path generation for POST /generate-path/skill/{id}.

    Builds a plan from the target skill plus its prerequisite closure,
    drops prerequisites already mastered (>= MASTERY_LEVEL), duplicate-
    guards the target so a skill can't open two paths, then reuses
    persist_plan/format_path_detail. Caller: routers/catalog.
    """
    skill = catalog_repository.get_skill(db, skill_id)
    if not skill:
        return None, "Skill not found"
    if lrepo.skill_in_user_paths(db, user.id, skill_id):
        return None, "Skill is already in one of your paths"
    chain = catalog_repository.get_prerequisite_chain(db, skill_id)
    rows = catalog_repository.get_skills_by_ids(db, chain)
    current = user_proficiency_by_name(db, user.id, rows)
    plan_rows = [s for s in rows if current[s.name] < MASTERY_LEVEL]
    if skill not in plan_rows:
        plan_rows.append(skill)
    plan = _order_by_prereqs(db, plan_rows)
    if not plan:
        return None, "You have already mastered this skill and its prerequisites"
    weekly = max(weekly_hours, 1)
    prefs = {"weekly_hours": weekly, "prefs": (preferences or {})}
    hours = sum((s.estimated_hours or 10) for s in plan)
    weeks = max(1, round(hours / weekly))
    levels = {s.name: current[s.name] for s in rows}
    path = persist_plan(
        db, user.id, f"Master {skill.name}",
        f"Learning path for {skill.name}. Estimated {hours}h over {weeks} weeks.",
        None, plan, levels, current, prefs)
    return format_path_detail(db, path, user.id), None


def _batch_fetch_context(db, steps: list[PathStep],
                         user_id: int) -> tuple[dict, dict, dict]:
    """Batch-fetch resources, skills and user_skills for a set of steps.

    Returns (resource_map, skill_map, user_skill_map) dicts keyed by id.
    """
    resource_ids, skill_ids = collect_ids_from_steps(steps)
    resource_map = catalog_repository.get_resources_by_map(db, resource_ids)
    skill_map = catalog_repository.get_skills_by_map(db, skill_ids)
    user_skill_map = lrepo.get_user_skills_bulk(db, user_id, skill_ids)
    return resource_map, skill_map, user_skill_map


def format_path_detail(db, path: Path, user_id: int) -> dict:
    """Full path payload (int ids, goal_job_role, skills[], steps[]).

    Batch-fetches all resources, skills and user_skills for the path's
    steps before serialization to avoid per-step N+1 queries.
    """
    completed = lrepo.completed_step_ids(db, user_id)
    steps = lrepo.get_steps(db, path.id)
    resource_map, skill_map, user_skill_map = _batch_fetch_context(
        db, steps, user_id)
    serialized = [serialize_step(s, completed, resource_map, skill_map,
                                 user_skill_map) for s in steps]
    return {
        "id": path.id, "profile_id": path.user_id,
        "title": path.title or "", "description": path.description,
        "status": path.status or "active",
        "progress": path_progress(serialized),
        "total_estimated_hours": path.total_estimated_hours,
        "total_hours": path.total_estimated_hours,
        "total_estimated_weeks": path.total_estimated_weeks,
        "goal_job_role": path.target_role,
        "created_at": path.created_at.isoformat() if path.created_at else None,
        "skills": path_skills(skill_map, steps),
        "levels": selected_levels_by_step(skill_map, steps),
        "steps": serialized,
    }


def _serialize_path_block(path, completed, resource_map, skill_map,
                          user_skill_map, db) -> dict:
    """One path entry for the progress dashboard paths[] block.

    Separate function to keep progress_dashboard under 40 lines.
    """
    steps = lrepo.get_steps(db, path.id)
    psteps = [serialize_step(s, completed, resource_map, skill_map,
                             user_skill_map) for s in steps]
    return {
        "id": path.id, "title": path.title or "", "description": path.description,
        "total_estimated_hours": path.total_estimated_hours,
        "total_hours": path.total_estimated_hours,
        "total_estimated_weeks": path.total_estimated_weeks,
        "goal_job_role": path.target_role,
        "created_at": path.created_at.isoformat() if path.created_at else None,
        "steps": psteps, "progress": path_progress(psteps),
    }


def progress_dashboard(db, user_id: int) -> dict:
    """GET /progress/dashboard payload — frontend-owned key contract.

    Completions come from step_progress.completed_at. Batch-fetches
    all resources/skills/user_skills across every path to avoid N+1.
    """
    seven_ago = datetime.now(UTC) - timedelta(days=7)
    paths = lrepo.get_paths_by_user(db, user_id)
    completed = lrepo.completed_step_ids(db, user_id)
    total_steps = lrepo.count_steps(db, user_id)
    completed_steps = lrepo.count_completions(db, user_id)
    pct = round(completed_steps / total_steps * 100, 1) if total_steps else 0
    total_hours = lrepo.sum_total_hours(db, user_id)
    completed_hours = round(total_hours * (pct / 100), 1) if pct > 0 else 0
    all_steps = []
    for p in paths:
        all_steps.extend(lrepo.get_steps(db, p.id))
    resource_map, skill_map, user_skill_map = _batch_fetch_context(
        db, all_steps, user_id)
    path_blocks = [_serialize_path_block(
        p, completed, resource_map, skill_map, user_skill_map, db
    ) for p in paths]
    return {
        "total_paths": len(paths),
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "completion_percentage": pct,
        "remaining_hours": round(max(0.0, total_hours - completed_hours), 1),
        "total_hours": total_hours,
        "weekly": lrepo.count_completions(db, user_id, since=seven_ago),
        "paths": path_blocks,
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
    """All of a user's paths as full detail payloads (GET /paths/).

    Batch-fetches resources/skills/user_skills across ALL paths first
    so each build call uses the shared pre-fetched maps.
    """
    paths = lrepo.get_paths_by_user(db, user_id)
    completed = lrepo.completed_step_ids(db, user_id)
    all_steps = []
    for p in paths:
        all_steps.extend(lrepo.get_steps(db, p.id))
    resource_map, skill_map, user_skill_map = _batch_fetch_context(
        db, all_steps, user_id)
    return [_build_path_detail(p, db, user_id, completed, resource_map,
                               skill_map, user_skill_map) for p in paths]


def _build_path_detail(path: Path, db, user_id: int, completed: set[int],
                       resource_map: dict, skill_map: dict,
                       user_skill_map: dict) -> dict:
    """Build a single path detail dict using pre-fetched context maps.

    Separate function to keep list_user_paths under the 40-line limit.
    """
    steps = lrepo.get_steps(db, path.id)
    serialized = [serialize_step(s, completed, resource_map, skill_map,
                                 user_skill_map) for s in steps]
    return {
        "id": path.id, "profile_id": path.user_id,
        "title": path.title or "", "description": path.description,
        "status": path.status or "active",
        "progress": path_progress(serialized),
        "total_estimated_hours": path.total_estimated_hours,
        "total_hours": path.total_estimated_hours,
        "total_estimated_weeks": path.total_estimated_weeks,
        "goal_job_role": path.target_role,
        "created_at": path.created_at.isoformat() if path.created_at else None,
        "skills": path_skills(skill_map, steps),
        "levels": selected_levels_by_step(skill_map, steps),
        "steps": serialized,
    }
