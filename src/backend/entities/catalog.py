"""Catalog layer — skills, taxonomy and learning resources.

Defines categories, skills (+ prerequisites), job_roles (+ mappings) and
resources. Referenced by the learning, assessment and engagement layers;
DDL twin lives in src/migrations/003_reduced_schema.sql.
"""

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Index, Integer, JSON, String, Text
from backend.entities.base import Base


class Category(Base):
    """Self-nesting taxonomy node; groups Skill rows via skills.category_id."""

    __tablename__ = "categories"
    __table_args__ = (
        Index('idx_categories_parent_id', 'parent_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete='SET NULL'), nullable=True)


class Skill(Base):
    """Learnable unit; referenced by resources, assessments, paths,
    path_steps, user_skills and both mapping tables."""

    __tablename__ = "skills"
    __table_args__ = (
        Index('idx_skills_category_id', 'category_id'),
        CheckConstraint(
            'difficulty_level >= 1 AND difficulty_level <= 10',
            name='chk_difficulty',
        ),
        CheckConstraint('estimated_hours >= 0', name='chk_hours'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(Integer, default=5)
    estimated_hours = Column(Integer, default=10)
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete='SET NULL'), nullable=True)
    topics = Column(JSON, nullable=True)


class SkillPrerequisite(Base):
    """Ordered-pair edge in the prerequisite DAG between two skills."""

    __tablename__ = "skill_prerequisites"
    __table_args__ = (
        Index('idx_skill_prerequisites_prerequisite_id', 'prerequisite_id'),
    )

    skill_id = Column(Integer, ForeignKey("skills.id", ondelete='CASCADE'), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey("skills.id", ondelete='CASCADE'), primary_key=True)


class JobRole(Base):
    """Career target whose required skills are listed in JobRoleSkill."""

    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    career_field = Column(String(100), nullable=True)


class JobRoleSkill(Base):
    """Mapping of a job_role to one required skill (no importance rank)."""

    __tablename__ = "job_role_skills"
    __table_args__ = (
        Index('idx_job_role_skills_skill_id', 'skill_id'),
    )

    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete='CASCADE'), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete='CASCADE'), primary_key=True)


class Resource(Base):
    """External learning material attached to at most one Skill."""

    __tablename__ = "resources"
    __table_args__ = (
        Index('idx_resources_skill_id', 'skill_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(2000), nullable=False)
    type = Column(String(50), nullable=False)
    language = Column(String(10), default='en')
    is_free = Column(Boolean, default=True)
    is_official = Column(Boolean, default=False)
    author_or_platform = Column(String(200), nullable=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete='SET NULL'), nullable=True)
