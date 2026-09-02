"""Learning repository — paths, path_steps, step_progress access.

Called by services/learning_service.py, services/analytics_service.py
and services/admin_service.py. Pure data access; completion state is a
step_progress row with completed_at NOT NULL (merged table from Task 1).
"""

from datetime import datetime, UTC

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from backend.entities.learning import Path, PathStep, StepProgress, UserSkill


def get_path(db: Session, path_id: int,
             user_id: int | None = None) -> Path | None:
    """Fetch one path, optionally scoped to its owner."""
    query = db.query(Path).filter(Path.id == path_id)
    if user_id is not None:
        query = query.filter(Path.user_id == user_id)
    return query.first()


def get_paths_by_user(db: Session, user_id: int) -> list[Path]:
    """Owner's paths, newest first; dashboards + listings."""
    return (
        db.query(Path).filter(Path.user_id == user_id)
        .order_by(Path.created_at.desc()).all()
    )


def count_paths(db: Session, user_id: int | None = None) -> int:
    """Path count overall or per owner; reports + dashboards."""
    query = db.query(Path)
    if user_id is not None:
        query = query.filter(Path.user_id == user_id)
    return query.count()


def count_paths_since(db: Session, since: datetime) -> int:
    """Paths created after `since`; admin 7-day overview.""" 
    return db.query(Path).filter(Path.created_at >= since).count()


def create_path(db: Session, user_id: int, title: str,
                description: str = "", target_role: str | None = None,
                total_hours: int = 0, total_weeks: int = 0) -> Path:
    """Insert a path shell and flush so steps can attach; commits."""
    path = Path(
        user_id=user_id, title=title, description=description,
        target_role=target_role, status="active",
        total_estimated_hours=total_hours, total_estimated_weeks=total_weeks,
    )
    db.add(path)
    db.commit()
    db.refresh(path)
    return path


def update_path(db: Session, path: Path, fields: dict) -> Path:
    """Apply non-None scalar fields onto a path row; commits."""
    for key, value in fields.items():
        if value is not None:
            setattr(path, key, value)
    db.commit()
    db.refresh(path)
    return path


def delete_path(db: Session, path_id: int, user_id: int) -> bool:
    """Hard-delete an owned path (steps/progress cascade); False if absent.

    Chosen over the soft-delete column to keep list endpoints identical
    to the old wire behavior.
    """
    path = get_path(db, path_id, user_id)
    if not path:
        return False
    db.delete(path)
    db.commit()
    return True


def get_step(db: Session, step_id: int) -> PathStep | None:
    """Fetch one step by PK; complete/undo endpoints resolve ownership."""
    return db.query(PathStep).filter(PathStep.id == step_id).first()


def update_step_current_level(db: Session, step_id: int, level: int) -> PathStep | None:
    """Persist a step's current_level (level-up after grading); returns step."""
    step = get_step(db, step_id)
    if not step:
        return None
    step.current_level = level
    db.commit()
    return step


def update_step_current_level_for_skill(db: Session, user_id: int,
                                        skill_id: int, level: int) -> list[PathStep]:
    """Set current_level on the current user's PathSteps of a skill and
    commit; scoped via Path.user_id so a rating only moves the caller's
    ladder.

    Called by the learning rate-proficiency router; returns the touched
    steps.
    """
    steps = (
        db.query(PathStep)
        .join(Path, PathStep.path_id == Path.id)
        .filter(Path.user_id == user_id, PathStep.skill_id == skill_id)
        .all()
    )
    for step in steps:
        step.current_level = level
    db.commit()
    return steps


def get_steps(db: Session, path_id: int) -> list[PathStep]:
    """A path's steps ordered by position (old step_number)."""
    return (
        db.query(PathStep).filter(PathStep.path_id == path_id)
        .order_by(PathStep.position).all()
    )


def count_steps(db: Session, user_id: int | None = None) -> int:
    """Step count overall or across a user's paths; dashboard math."""
    query = db.query(PathStep)
    if user_id is not None:
        query = query.join(Path).filter(Path.user_id == user_id)
    return query.count()


def skill_in_user_paths(db: Session, user_id: int, skill_id: int) -> bool:
    """True when a skill is already a step target in one of the user's paths.

    Duplicate-guard for catalog path generation (generate_path_for_skill):
    prevents adding the same skill as a target in more than one path."""
    return (
        db.query(PathStep.id)
        .join(Path, PathStep.path_id == Path.id)
        .filter(Path.user_id == user_id, PathStep.skill_id == skill_id)
        .first() is not None
    )


def create_step(db: Session, path_id: int, position: int, title: str,
                description: str = "", estimated_hours: int = 8,
                resource_ids: list[int] | None = None,
                assessment_ids: list[int] | None = None) -> PathStep:
    """Insert one ordered step carrying JSON resource/assessment bridges."""
    step = PathStep(
        path_id=path_id, position=position, title=title,
        description=description, estimated_hours=estimated_hours,
        resource_ids=resource_ids or None, assessment_ids=assessment_ids or None,
    )
    db.add(step)
    db.flush()
    return step


def delete_steps(db: Session, path_id: int) -> None:
    """Drop all steps of a path (regeneration rewrite); caller commits."""
    db.query(PathStep).filter(PathStep.path_id == path_id).delete()


# ── step_progress ─────────────────────────────────────────────────────

def completed_step_ids(db: Session, user_id: int) -> set[int]:
    """Ids of the user's completed steps; is_completed synthesis."""
    rows = db.query(StepProgress.step_id).filter(
        StepProgress.user_id == user_id,
        StepProgress.completed_at.isnot(None)).all()
    return {sid for (sid,) in rows}


def upsert_completion(db: Session, user_id: int, step_id: int) -> StepProgress:
    """Mark a step complete (idempotent); stamps completed_at now."""
    row = db.query(StepProgress).filter(
        StepProgress.user_id == user_id,
        StepProgress.step_id == step_id).first()
    if row is None:
        row = StepProgress(user_id=user_id, step_id=step_id)
        db.add(row)
    if row.completed_at is None:
        row.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(row)
    return row


def delete_completion(db: Session, user_id: int, step_id: int) -> bool:
    """Undo a completion by removing the progress row; False if absent."""
    row = db.query(StepProgress).filter(
        StepProgress.user_id == user_id,
        StepProgress.step_id == step_id).first()
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


def count_completions(db: Session, user_id: int | None = None,
                      since: datetime | None = None) -> int:
    """Completed-step count, optionally scoped by owner and/or window."""
    query = db.query(StepProgress).filter(
        StepProgress.completed_at.isnot(None))
    if user_id is not None:
        query = query.filter(StepProgress.user_id == user_id)
    if since is not None:
        query = query.filter(StepProgress.completed_at >= since)
    return query.count()


def completions_by_step_ids(db: Session,
                            step_ids: list[int]) -> list[StepProgress]:
    """Raw progress rows for a step set; admin path completion flags."""
    if not step_ids:
        return []
    return db.query(StepProgress).filter(
        StepProgress.step_id.in_(step_ids),
        StepProgress.completed_at.isnot(None)).all()


def daily_activity(db: Session, user_id: int,
                   since: datetime) -> list[tuple[str, int]]:
    """Per-day completion counts since `since`, date ascending."""
    rows = (
        db.query(func.date(StepProgress.completed_at),
                 func.count(StepProgress.step_id))
        .filter(StepProgress.user_id == user_id,
                StepProgress.completed_at >= since)
        .group_by(func.date(StepProgress.completed_at))
        .order_by(func.date(StepProgress.completed_at))
        .all()
    )
    return [(str(d), c) for d, c in rows]


def learning_history(db: Session, user_id: int,
                     limit: int = 20) -> list[tuple]:
    """Recent completions joined with step/path titles, newest first.

    Rows: (StepProgress, step_title, path_title, path_id); consumed by
    analytics_service.learning_history.
    """
    return (
        db.query(StepProgress, PathStep.title, Path.title, PathStep.path_id)
        .join(PathStep, StepProgress.step_id == PathStep.id)
        .join(Path, PathStep.path_id == Path.id)
        .filter(StepProgress.user_id == user_id,
                StepProgress.completed_at.isnot(None))
        .order_by(StepProgress.completed_at.desc())
        .limit(limit)
        .all()
    )


def most_completed_steps(db: Session, limit: int = 5) -> list[tuple[str, int]]:
    """Global top steps by completion count; content-engagement report."""
    return (
        db.query(PathStep.title, func.count(StepProgress.step_id))
        .join(StepProgress, StepProgress.step_id == PathStep.id)
        .filter(StepProgress.completed_at.isnot(None))
        .group_by(PathStep.title)
        .order_by(desc(func.count(StepProgress.step_id)))
        .limit(limit)
        .all()
    )


def active_user_count_since(db: Session, since: datetime) -> int:
    """Distinct users completing something since `since`; 7d report."""
    return (
        db.query(func.count(func.distinct(StepProgress.user_id)))
        .filter(StepProgress.completed_at >= since).scalar() or 0
    )


def sum_total_hours(db: Session, user_id: int | None = None) -> float:
    """Sum of path hour estimates, global or per owner."""
    query = db.query(func.sum(Path.total_estimated_hours))
    if user_id is not None:
        query = query.filter(Path.user_id == user_id)
    return query.scalar() or 0
# ── Batch-fetch helpers (N+1 elimination) ──

def get_user_skills_bulk(db: Session, user_id: int,
                         skill_ids: list[int]) -> dict[int, "UserSkill"]:
    """Fetch user_skills for one user by skill ID list."""
    if not skill_ids:
        return {}
    rows = db.query(UserSkill).filter(
        UserSkill.user_id == user_id,
        UserSkill.skill_id.in_(skill_ids),
    ).all()
    return {r.skill_id: r for r in rows}


def get_completed_step_ids_bulk(db: Session, user_id: int,
                                step_ids: list[int]) -> set[int]:
    """Return the set of step_ids completed for a user, filtered to input."""
    if not step_ids:
        return set()
    rows = db.query(StepProgress.step_id).filter(
        StepProgress.user_id == user_id,
        StepProgress.step_id.in_(step_ids),
        StepProgress.completed_at.isnot(None),
    ).all()
    return {r[0] for r in rows}
