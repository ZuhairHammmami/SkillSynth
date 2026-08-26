"""Engagement layer — unified activity telemetry.

Defines activity_log, the merge of the former events and audit_logs
tables. Depends on identity; DDL twin lives in
src/migrations/003_reduced_schema.sql.
"""

from sqlalchemy import Column, ForeignKey, Index, Integer, String, JSON, TIMESTAMP, func

from backend.entities.base import Base


class ActivityLog(Base):
    """One auditable action; category is audit|auth|learning|system|
    realtime. data stays JSON by documented exception."""

    __tablename__ = "activity_log"
    __table_args__ = (
        Index('idx_activity_log_user_id', 'user_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='SET NULL'), nullable=True)
    category = Column(String(20), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(50), nullable=True)
    data = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
