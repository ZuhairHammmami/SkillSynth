"""Engagement repository — unified activity_log write + filtered list.

Called by services/auth_service.py (auth events), services/admin_service.py
(activity feed) and any service broadcasting admin SSE events. Replaces
the old event_repository + audit_log writes with the single merged table.
"""

from sqlalchemy.orm import Session

from backend.entities.engagement import ActivityLog
from backend.entities.identity import User


def write(db: Session, category: str, action: str,
          user_id: int | None = None, entity_type: str | None = None,
          entity_id: int | None = None, data: dict | None = None,
          ip_address: str | None = None,
          user_agent: str | None = None) -> ActivityLog:
    """Persist one activity row and return it (committed).

    Called by auth_service.log_auth and admin_service.activity_feed
    producers; data stays a JSON dict by documented exception.
    """
    row = ActivityLog(
        user_id=user_id, category=category, action=action,
        entity_type=entity_type, entity_id=str(entity_id)
        if entity_id is not None else None,
        data=data, ip_address=ip_address, user_agent=user_agent,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_filtered(db: Session, offset: int = 0, limit: int = 50,
                 category: str | None = None,
                 action: str | None = None) -> list[tuple[ActivityLog, User | None]]:
    """Newest-first page of activity rows joined with actor users.

    Called by admin_service.activity_feed; both filters are optional.
    """
    query = db.query(ActivityLog, User).outerjoin(
        User, User.id == ActivityLog.user_id)
    if category:
        query = query.filter(ActivityLog.category == category)
    if action:
        query = query.filter(ActivityLog.action == action)
    return (
        query.order_by(ActivityLog.created_at.desc())
        .offset(offset).limit(limit).all()
    )


def get_audit_page(db: Session, offset: int = 0, limit: int = 100) -> list:
    """Audit-category subset for the admin audit-log page."""
    return get_filtered(db, offset, limit, category="audit")
