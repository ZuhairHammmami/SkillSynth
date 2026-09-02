"""Assessment layer — quizzes, questions and scored results.

Defines assessments, assessment_questions (questions moved out of the old
JSON column) and assessment_results. Depends on identity and catalog
layers; DDL twin lives in src/migrations/003_reduced_schema.sql.
"""

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, JSON, TIMESTAMP, func

from backend.entities.base import Base


class Assessment(Base):
    """A quiz bound to at most one skill; owns ordered questions."""

    __tablename__ = "assessments"
    __table_args__ = (
        Index('idx_assessments_skill_id', 'skill_id'),
        CheckConstraint(
            'pass_score >= 0 AND pass_score <= 100',
            name='chk_pass_score',
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete='SET NULL'), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    pass_score = Column(Integer, default=60)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AssessmentQuestion(Base):
    """Single multiple-choice question; options stay JSON by documented
    exception (value list, never queried relationally)."""

    __tablename__ = "assessment_questions"
    __table_args__ = (
        Index('idx_assessment_questions_assessment_id', 'assessment_id'),
        CheckConstraint('correct_index >= 0', name='chk_correct'),
    )

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete='CASCADE'), nullable=False)
    position = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_index = Column(Integer, nullable=False)


class AssessmentResult(Base):
    """Scored attempt of an Assessment by a User."""

    __tablename__ = "assessment_results"
    __table_args__ = (
        Index('idx_assessment_results_user_id', 'user_id'),
        Index('idx_assessment_results_assessment_id', 'assessment_id'),
        Index('idx_assessment_results_user_completed', 'user_id', 'completed_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
