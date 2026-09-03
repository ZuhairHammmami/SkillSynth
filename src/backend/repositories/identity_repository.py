"""Identity repository — all `users` table access.

Called by services/auth_service.py and services/admin_service.py.
Pure data access: no business rules, no serialization.
"""

from datetime import datetime, timedelta, UTC

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.entities.identity import User
from backend.entities.learning import Path, StepProgress

LOCKOUT_WINDOW_DAYS = 7


def get_by_email(db: Session, email: str) -> User | None:
    """Fetch one user by exact email; called by auth + admin services."""
    return db.query(User).filter(User.email == email).first()


def get_by_email_excluding(db: Session, email: str,
                           exclude_user_id: int) -> User | None:
    """Case-insensitive email lookup skipping one user row.

    Called by admin_service.update_user so renames cannot collide with
    another account's email while keeping the user's own address legal.
    """
    return db.query(User).filter(
        User.email.ilike(email), User.id != exclude_user_id).first()


def get_by_id(db: Session, user_id: int) -> User | None:
    """Fetch one user by PK; called by admin_service.update/delete."""
    return db.query(User).filter(User.id == user_id).first()


def count_all(db: Session) -> int:
    """Total user rows; called by admin_service.system_health."""
    return db.query(User).count()


def count_created_since(db: Session, since: datetime) -> int:
    """Users created after `since`; feeds 24h/7d activity counts."""
    return db.query(User).filter(User.created_at >= since).count()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Paged user listing ordered by id; called by admin_service."""
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()


def create(db: Session, email: str, hashed_password: str,
           full_name: str | None = None, is_admin: bool = False) -> User:
    """Insert a user with an already-hashed password; commits."""
    user = User(email=email, hashed_password=hashed_password,
                full_name=full_name, is_admin=is_admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_fields(db: Session, user: User, fields: dict) -> User:
    """Apply a whitelist dict onto a user row; hashed_password allowed."""
    for key, value in fields.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def update_password(db: Session, user_id: int, password_hash: str) -> None:
    """Overwrite only the password hash; called by auth flows."""
    db.query(User).filter(User.id == user_id).update(
        {"hashed_password": password_hash})
    db.commit()


def delete(db: Session, user_id: int) -> bool:
    """Hard-delete a user (FKs cascade); returns False if missing."""
    user = get_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def get_user_counts(db: Session) -> tuple[int, int, int, int]:
    """(total, new_24h, new_7d, users_with_paths); admin activity report.

    Called by admin_service.get_user_activity; users_with_paths counts
    distinct paths.user_id instead of the old Profile.paths relationship.
    """
    now = datetime.now(UTC)
    total = db.query(User).count()
    new_24h = count_created_since(db, now - timedelta(days=1))
    new_7d = count_created_since(db, now - timedelta(days=7))
    users_with_paths = db.query(func.count(func.distinct(Path.user_id))).scalar() or 0
    return total, new_24h, new_7d, users_with_paths


def get_users_by_ids(db: Session, ids: list[int]) -> dict[int, User]:
    """Batch-fetch users by ID list; returns {id: User}. Skips missing."""
    if not ids:
        return {}
    rows = db.query(User).filter(User.id.in_(ids)).all()
    return {r.id: r for r in rows}


def most_active_users(db: Session, limit: int = 10) -> list[tuple[str, int]]:
    """Top emails by completed-step count via step_progress join.

    Called by admin_service.get_aggregated_report to build
    most_active_users[{user_email, completed_steps}].
    """
    return (
        db.query(User.email, func.count(StepProgress.user_id).label("count"))
        .join(StepProgress, StepProgress.user_id == User.id)
        .group_by(User.email)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
