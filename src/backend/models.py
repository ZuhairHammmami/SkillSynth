# src/backend/models.py

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, Boolean, TIMESTAMP, func, Table, JSON
) # <-- هذا هو السطر الذي تم إصلاحه
from sqlalchemy.orm import relationship
from backend.database import Base

# --- جداول وسيطة (Many-to-Many) ---

# يربط المهارات بالتصنيفات
skill_categories = Table('skill_categories', Base.metadata,
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

# يربط المسارات بالمهارات
path_skills = Table('path_skills', Base.metadata,
    Column('path_id', Integer, ForeignKey('paths.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

# يربط الخطوات بالمصادر
step_resources = Table('step_resources', Base.metadata,
    Column('step_id', Integer, ForeignKey('path_steps.id'), primary_key=True),
    Column('resource_id', Integer, ForeignKey('resources.id'), primary_key=True)
)

# يربط الخطوات بالتقييمات
step_assessments = Table('step_assessments', Base.metadata,
    Column('step_id', Integer, ForeignKey('path_steps.id'), primary_key=True),
    Column('assessment_id', Integer, ForeignKey('assessments.id'), primary_key=True)
)

# يربط الأدوار الوظيفية بالمهارات
job_role_skills = Table('job_role_skills', Base.metadata,
    Column('job_role_id', Integer, ForeignKey('job_roles.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)


# --- الكيانات الأساسية (Entities) ---

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    # حقل لتخزين بروفايل المهارات المحسوب
    skill_profile = Column(JSON, nullable=True)
    
    paths = relationship("Path", back_populates="owner")
    completions = relationship("StepCompletion", back_populates="profile")
    assessment_results = relationship("AssessmentResult", back_populates="profile")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    skills = relationship("Skill", secondary=skill_categories, back_populates="categories")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    categories = relationship("Category", secondary=skill_categories, back_populates="skills")
    paths = relationship("Path", secondary=path_skills, back_populates="skills")
    job_roles = relationship("JobRole", secondary=job_role_skills, back_populates="skills")

class Path(Base):
    __tablename__ = "paths"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    title = Column(String)
    description = Column(Text, nullable=True)
    
    owner = relationship("Profile", back_populates="paths")
    steps = relationship("PathStep", back_populates="path", cascade="all, delete-orphan")
    skills = relationship("Skill", secondary=path_skills, back_populates="paths")

class PathStep(Base):
    __tablename__ = "path_steps"
    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("paths.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    title = Column(String)
    content = Column(Text, nullable=True)
    
    path = relationship("Path", back_populates="steps")
    completions = relationship("StepCompletion", back_populates="step")
    resources = relationship("Resource", secondary=step_resources, back_populates="steps")
    assessments = relationship("Assessment", secondary=step_assessments, back_populates="steps")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    url = Column(String)
    type = Column(String) # 'video', 'article', etc.
    is_free = Column(Boolean, default=True)
    is_official = Column(Boolean, default=False)
    author_or_platform = Column(String, nullable=True)
    
    steps = relationship("PathStep", secondary=step_resources, back_populates="resources")

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    assessment_type = Column(String) # 'placement_test', 'step_quiz', etc.
    
    steps = relationship("PathStep", secondary=step_assessments, back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment")

class JobRole(Base):
    __tablename__ = "job_roles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    
    skills = relationship("Skill", secondary=job_role_skills, back_populates="job_roles")

# --- جداول التتبع ---

class StepCompletion(Base):
    __tablename__ = "step_completions"
    profile_id = Column(Integer, ForeignKey("profiles.id"), primary_key=True)
    step_id = Column(Integer, ForeignKey("path_steps.id"), primary_key=True)
    completed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    profile = relationship("Profile", back_populates="completions")
    step = relationship("PathStep", back_populates="completions")

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    score = Column(Integer)
    submitted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="assessment_results")
    assessment = relationship("Assessment", back_populates="results")