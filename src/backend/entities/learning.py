"""Learning layer — learner skill inventory, paths and progress.

Defines user_skills (replaces profile_skills), paths, path_steps and
step_progress (merges step_completions + step_progress). Depends on the
identity and catalog layers; DDL twin lives in
src/migrations/003_reduced_schema.sql.
"""

from sqlalchemy import Column, ForeignKey, Index, Integer, String, Text, JSON, TIMESTAMP, func

from backend.entities.base import Base


class UserSkill(Base):
    """Per-user skill proficiency; replaces profile_skills with real FKs."""

    __tablename__ = "user_skills"
    __table_args__ = (
        Index('idx_user_skills_skill_id', 'skill_id'),
    )

    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete='CASCADE'), primary_key=True)
    proficiency_level = Column(Integer, default=1)
    last_assessed_at = Column(TIMESTAMP(timezone=True), nullable=True)


class Path(Base):
    """A learner's generated plan; owns ordered PathStep rows."""

    __tablename__ = "paths"
    __table_args__ = (
        Index('idx_paths_user_id', 'user_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_role = Column(String(150), nullable=True)
    status = Column(String(20), default='active')
    total_estimated_hours = Column(Integer, default=0, nullable=False)
    total_estimated_weeks = Column(Integer, default=0, nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PathStep(Base):
    """One ordered step inside a Path; carries JSON bridges for
    resource/assessment references (documented exception to strict 3NF)."""

    __tablename__ = "path_steps"
    __table_args__ = (
        Index('idx_path_steps_path_id', 'path_id'),
        Index('idx_path_steps_skill_id', 'skill_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("paths.id", ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete='SET NULL'), nullable=True)
    position = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    estimated_hours = Column(Integer, default=8)
    resource_ids = Column(JSON, nullable=True)
    assessment_ids = Column(JSON, nullable=True)


class StepProgress(Base):
    """Per-user completion state of a PathStep; merges the former
    step_completions and step_progress tables."""

    __tablename__ = "step_progress"
    __table_args__ = (
        Index('idx_step_progress_step_id', 'step_id'),
    )

    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)
    step_id = Column(Integer, ForeignKey("path_steps.id", ondelete='CASCADE'), primary_key=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    score = Column(Integer, nullable=True)
