"""Identity layer — authentication principal of the reduced schema.

Owns the single `users` table that every other layer references via FK.
Re-exported by backend.entities.__init__; DDL twin lives in
src/migrations/003_reduced_schema.sql.
"""

from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, func

from backend.entities.base import Base


class User(Base):
    """Authenticated account; anchor for user_skills, paths,
    assessment_results, step_progress and activity_log rows."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
