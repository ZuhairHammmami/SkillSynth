"""Analytics service — learner dashboards, skill growth, gap analysis.

Called by the analytics and learning routers (Task 3). All aggregates
derive from step_progress (completed_at NOT NULL) and user_skills;
dashboard/skill-growth key sets are frozen for wire compatibility.
"""

from datetime import datetime, timedelta, UTC

from backend.entities.catalog import Category
from backend.repositories import assess_repository, catalog_repository
from backend.repositories import learning_repository as lrepo

MASTERY_LEVEL = 3


def _status_for(level: int) -> str:
    """Shared mastered/learning/not_started bucketing rule."""
    if level >= MASTERY_LEVEL:
        return "mastered"
    return "learning" if level > 0 else "not_started"


def _path_progress_list(db, user_id: int, paths: list) -> list[dict]:
    """Per-path completion blocks used inside learner_dashboard."""
    all_ids = [s.id for p in paths for s in lrepo.get_steps(db, p.id)]
    comps = lrepo.completions_by_step_ids(db, all_ids)
    done = {c.step_id for c in comps if c.user_id == user_id}
    out = []
    for p in paths:
        steps = lrepo.get_steps(db, p.id)
        completed = sum(1 for s in steps if s.id in done)
        out.append({
            "path_id": p.id, "path_title": p.title,
            "total_steps": len(steps), "completed_steps": completed,
            "percentage": round(completed / len(steps) * 100, 1)
            if steps else 0,
        })
    return out


def learner_dashboard(db, user_id: int) -> dict:
    """GET /analytics/dashboard payload — EXACT legacy keys including
    mastered_skills/learning_skills/total_skill_areas/completion_rate.
    Compatibility keys added (non-breaking): learning_hours, paths_count,
    completion_percentage alias the existing total_hours/total_paths/
    completion_rate values the student UI expects."""
    total_paths = lrepo.count_paths(db, user_id)
    total_completed = lrepo.count_completions(db, user_id)
    total_steps = lrepo.count_steps(db, user_id)
    seven_ago = datetime.now(UTC) - timedelta(days=7)
    weekly = lrepo.count_completions(db, user_id, since=seven_ago)
    total_hours = lrepo.sum_total_hours(db, user_id)
    profile = assess_repository.get_skill_profile(db, user_id)
    completion_rate = round(total_completed / total_steps * 100, 1) if total_steps else 0
    mastered = sum(1 for v in profile.values() if v >= MASTERY_LEVEL)
    learning = sum(1 for v in profile.values() if 0 < v < MASTERY_LEVEL)
    completed_hours = round(total_hours * (completion_rate / 100), 1) if completion_rate > 0 else 0
    paths = lrepo.get_paths_by_user(db, user_id)
    monthly = lrepo.count_completions(
        db, user_id, since=datetime.now(UTC) - timedelta(days=30))
    return {
        "total_paths": total_paths,
        "total_completed_steps": total_completed,
        "completed_steps": total_completed,
        "total_steps": total_steps, "completion_rate": completion_rate,
        "mastered_skills": mastered, "learning_skills": learning,
        "total_skill_areas": len(profile),
        "weekly_completions": weekly, "total_hours": total_hours,
        "completed_hours": completed_hours,
        "remaining_hours": round(total_hours - completed_hours, 1),
        "learning_velocity": round(monthly / (30 / 7), 1) if monthly > 0 else 0,
        "recent_activity": _recent_activity(db, user_id),
        "path_progress": _path_progress_list(db, user_id, paths),
        "learning_hours": total_hours,
        "paths_count": total_paths,
        "completion_percentage": completion_rate,
    }


def _recent_activity(db, user_id: int, limit: int = 5) -> list[dict]:
    """recent_activity items rendered by analytics + dashboard pages:
    {type, description, date} built from the latest step completions."""
    return [
        {
            "type": "step_completed",
            "description": f'Completed "{step_title}" in {path_title}',
            "date": row.completed_at.isoformat() if row.completed_at else None,
        }
        for row, step_title, path_title, _path_id
        in lrepo.learning_history(db, user_id, limit=limit)
    ]


def skill_growth(db, user_id: int) -> dict:
    """GET /analytics/skill-growth payload; items keep the historical
    {skill, level, status} shape with title-cased display names."""
    profile = assess_repository.get_skill_profile(db, user_id)
    growth = sorted(
        [{"skill": name.replace("_", " ").title(), "level": level,
          "status": _status_for(level)} for name, level in profile.items()],
        key=lambda x: x["level"], reverse=True)
    mastered = [s for s in growth if s["status"] == "mastered"]
    learning = [s for s in growth if s["status"] == "learning"]
    return {
        "skills": growth, "mastered_count": len(mastered),
        "in_progress_count": len(learning),
        "not_started_count": sum(1 for s in growth if s["status"] == "not_started"),
        "weak_skills": learning[:3], "strong_skills": mastered[:3],
        "knowledge_gaps": [s["skill"] for s in growth if s["status"] == "not_started"],
    }


def get_path_progress(db, path_id: int, user_id: int) -> dict | None:
    """GET /analytics/path-progress/{id} payload (None when not owner)."""
    path = lrepo.get_path(db, path_id, user_id)
    if not path:
        return None
    steps = lrepo.get_steps(db, path_id)
    comp_ids = lrepo.completed_step_ids(db, user_id)
    total, done = len(steps), sum(1 for s in steps if s.id in comp_ids)
    hours = path.total_estimated_hours or 0
    return {
        "path_id": path_id, "total_steps": total, "completed_steps": done,
        "completion_percentage": round(done / total * 100, 1) if total else 0,
        "total_estimated_hours": hours,
        "completed_hours": round(hours * (done / total), 1) if total else 0,
        "remaining_hours": round(hours * (1 - done / total), 1) if total else 0,
        "estimated_weeks": path.total_estimated_weeks or 0,
        "goal_role": path.target_role or "",
        "step_progress": [{"step": s.position, "title": s.title,
                           "completed": s.id in comp_ids} for s in steps],
    }


def learning_history(db, user_id: int) -> dict:
    """GET /analytics/learning-history payload (recent activity + daily)."""
    seven_ago = datetime.now(UTC) - timedelta(days=7)
    completions = lrepo.learning_history(db, user_id)
    daily = lrepo.daily_activity(db, user_id, seven_ago)
    return {
        "recent_activity": [
            {"step_title": st, "path_title": pt, "step_id": sc.step_id,
             "path_id": pid,
             "completed_at": sc.completed_at.isoformat()
             if sc.completed_at else None}
            for sc, st, pt, pid in completions],
        "total_completions": lrepo.count_completions(db, user_id),
        "weekly_completions": lrepo.count_completions(db, user_id, since=seven_ago),
        "daily_activity": [{"date": d, "count": c} for d, c in daily],
    }


def learning_velocity(db, user_id: int) -> dict:
    """GET /analytics/learning-velocity payload (weekly/monthly pace)."""
    now = datetime.now(UTC)
    weekly = lrepo.count_completions(db, user_id, since=now - timedelta(days=7))
    monthly = lrepo.count_completions(db, user_id, since=now - timedelta(days=30))
    total = lrepo.count_completions(db, user_id)
    return {
        "weekly_velocity": weekly, "monthly_velocity": monthly,
        "total_completions": total, "total_hours": lrepo.sum_total_hours(db, user_id),
        "average_per_week": round(monthly / (30 / 7), 1) if monthly > 0 else 0,
    }


# ── Gap / weakness analysis (moved from learning_service) ────────────

def analyze_gaps(db, user_id: int, goal_skills: list[str] | None = None,
                 target_role: str | None = None) -> dict:
    """GET /learning/skill-gaps payload; keys preserved from the old
    LearningAnalyzer. Goals are explicit skill names or a job role
    resolved through job_role_skills."""
    names = list(goal_skills or [])
    if target_role and not names:
        role = catalog_repository.get_job_role_by_title(db, target_role)
        ids = catalog_repository.get_job_role_skill_ids(db, role.id) if role else []
        names = [s.name for s in catalog_repository.get_skills_by_ids(db, ids)]
    profile = assess_repository.get_skill_profile(db, user_id)
    by_name = {s.name: s for s in catalog_repository.get_all_skills(db)}
    return {"goal_skills": names,
            "gaps": [_describe_gap(name, by_name.get(name), profile, db)
                     for name in names]}


def _describe_gap(name: str, skill, profile: dict, db) -> dict:
    """One gaps[] entry; unknown names degrade to status=unknown and
    known ones carry the unmet prerequisite chain."""
    if skill is None:
        return {"skill": name, "status": "unknown", "current_level": 0,
                "prerequisites": []}
    current = profile.get(skill.name, 0)
    prereqs = []
    for sid in catalog_repository.get_prerequisite_chain(db, skill.id):
        ps = catalog_repository.get_skill(db, sid)
        if ps and ps.name != skill.name:
            prereqs.append({"id": ps.id, "name": ps.name,
                            "current_level": profile.get(ps.name, 0),
                            "needed": ps.difficulty_level or 1})
    return {
        "skill": skill.name, "skill_id": skill.id, "current_level": current,
        "target_level": MASTERY_LEVEL, "gap": max(0, MASTERY_LEVEL - current),
        "difficulty": skill.difficulty_level or 1, "prerequisites": prereqs,
        "status": _status_for(current),
    }


def analyze_weaknesses(db, user_id: int) -> dict:
    """GET /learning/analysis payload — strengths vs weaknesses with
    average assessment score, keys frozen from the old analyzer."""
    profile = assess_repository.get_skill_profile(db, user_id)
    all_skills = catalog_repository.get_all_skills(db)
    history = assess_repository.results_for_user(db, user_id)
    weaknesses = [
        {"skill_id": s.id, "skill_name": s.name,
         "current_level": profile.get(s.name, 0),
         "difficulty": s.difficulty_level or 1,
         "gap": max(0, MASTERY_LEVEL - profile.get(s.name, 0))}
        for s in all_skills if profile.get(s.name, 0) < 2]
    strengths = [
        {"skill_id": s.id, "skill_name": s.name,
         "current_level": profile.get(s.name, 0),
         "difficulty": s.difficulty_level or 1}
        for s in all_skills if profile.get(s.name, 0) >= MASTERY_LEVEL]
    avg = round(sum(r.score or 0 for r in history) / len(history), 1) if history else 0
    return {
        "weaknesses": sorted(weaknesses, key=lambda w: w["gap"], reverse=True),
        "strengths": sorted(strengths, key=lambda s: s["current_level"], reverse=True),
        "weakness_count": len(weaknesses), "strength_count": len(strengths),
        "total_skills_assessed": len(all_skills),
        "average_assessment_score": avg,
        "total_assessments_taken": len(history),
        "recommended_focus": [w["skill_name"] for w in weaknesses[:5]],
    }


def estimate_time(db, user_id: int, skill_names: list[str],
                  weekly_hours: int = 10) -> dict:
    """GET /learning/time-estimate payload; hours = difficulty*3*(gap+1)
    exactly like the old LearningAnalyzer.estimate_time."""
    profile = assess_repository.get_skill_profile(db, user_id)
    by_name = {s.name: s for s in catalog_repository.get_all_skills(db)}
    total_hours, breakdown = 0, []
    for name in skill_names:
        skill = by_name.get(name)
        if not skill:
            continue
        current = profile.get(name, 0)
        hours = (skill.difficulty_level or 1) * 3 * (max(0, MASTERY_LEVEL - current) + 1)
        total_hours += hours
        breakdown.append({"skill": name, "current_level": current,
                          "target_level": MASTERY_LEVEL,
                          "estimated_hours": hours})
    return {
        "total_estimated_hours": total_hours,
        "total_estimated_weeks": max(1, round(total_hours / max(weekly_hours, 1))),
        "weekly_hours": weekly_hours, "skill_breakdown": breakdown,
    }


def progress_by_category(db, user_id: int) -> dict:
    """GET /learning/progress payload — per-category mastery counts."""
    profile = assess_repository.get_skill_profile(db, user_id)
    categories = db.query(Category).order_by(Category.id).all()
    all_skills = catalog_repository.get_all_skills(db)
    rows = []
    for cat in categories:
        members = [s for s in all_skills if s.category_id == cat.id]
        mastered = sum(1 for s in members if profile.get(s.name, 0) >= MASTERY_LEVEL)
        in_progress = sum(1 for s in members
                          if 0 < profile.get(s.name, 0) < MASTERY_LEVEL)
        total = len(members)
        rows.append({
            "category_id": cat.id, "category_name": cat.name,
            "total_skills": total, "mastered": mastered,
            "in_progress": in_progress, "not_started": total - mastered - in_progress,
            "completion_percentage": round(mastered / total * 100, 1) if total else 0,
        })
    estimate = estimate_time(db, user_id, list(profile.keys()))
    return {
        "categories": rows,
        "overall": {
            "total_skills": len(profile), "mastered":
            sum(1 for v in profile.values() if v >= MASTERY_LEVEL),
            "in_progress": sum(1 for v in profile.values()
                               if 0 < v < MASTERY_LEVEL),
            "not_started": sum(1 for v in profile.values() if v == 0),
        },
        "time_estimate": estimate,
    }
