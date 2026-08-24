"""Catalog DTOs — skills, categories, resources and job roles.

Consumed by services/catalog_service.py and the admin catalog routers
(Task 3). Sanitizers are shared helpers; wire keys follow the old
dto/skill|category|resource|job_role modules minus dead relation lists.
"""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _sanitize(value: str) -> str:
    """Strip angle/quote characters and require non-empty text."""
    value = value.strip()
    if not value:
        raise ValueError("Value must not be empty")
    return re.sub(r"[<>'\"\\]", "", value)


class CategoryCreate(BaseModel):
    """POST /admin/categories body."""

    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Strip markup via the shared sanitizer."""
        return _sanitize(v)


class CategoryOut(CategoryCreate):
    """Serialized categories row (id added)."""

    id: int


class CategoryUpdate(BaseModel):
    """PUT /admin/categories/{id} body."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup when a new value is supplied."""
        return _sanitize(v) if v is not None else v


class SkillCreate(BaseModel):
    """POST /admin/skills body.

    Accepts both the legacy `category_ids` list and the reduced-schema
    single `category_id` (first list entry wins) for router compatibility.
    """

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    estimated_hours: Optional[int] = Field(None, ge=0)
    icon: Optional[str] = None
    color: Optional[str] = None
    category_id: Optional[int] = None
    category_ids: Optional[list[int]] = None
    prerequisite_ids: list[int] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Strip markup via the shared sanitizer."""
        return _sanitize(v)


class SkillOut(BaseModel):
    """Serialized skills row; prerequisite_ids/resource_ids synthesized
    from skill_prerequisites and resources.skill_id joins."""

    id: int
    name: str
    description: Optional[str] = None
    difficulty_level: Optional[int] = None
    estimated_hours: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    category_id: Optional[int] = None
    prerequisite_ids: list[int] = []
    resource_ids: list[int] = []


class SkillUpdate(BaseModel):
    """PUT /admin/skills/{id} body; None fields left untouched."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    estimated_hours: Optional[int] = Field(None, ge=0)
    icon: Optional[str] = None
    color: Optional[str] = None
    category_id: Optional[int] = None
    prerequisite_ids: Optional[list[int]] = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup when a new value is supplied."""
        return _sanitize(v) if v is not None else v


class ResourceCreate(BaseModel):
    """POST /admin/resources body; skill_id links to the new FK column."""

    title: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., max_length=2000)
    type: str = Field(..., max_length=50)
    language: Optional[str] = Field(default="en", max_length=10)
    is_free: bool = True
    is_official: bool = False
    author_or_platform: Optional[str] = Field(None, max_length=200)
    skill_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Field rule: sanitize title."""
        return _sanitize(v)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Require http(s) scheme on resource URLs."""
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class ResourceOut(ResourceCreate):
    """Serialized resources row (id added)."""

    id: int


class ResourceUpdate(BaseModel):
    """PUT /admin/resources/{id} body; None fields left untouched."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = Field(None, max_length=2000)
    type: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    is_free: Optional[bool] = None
    is_official: Optional[bool] = None
    author_or_platform: Optional[str] = Field(None, max_length=200)
    skill_id: Optional[int] = None


class JobRoleCreate(BaseModel):
    """POST /admin/job-roles body; skill_ids accepts ints or dicts."""

    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    career_field: Optional[str] = Field(None, max_length=100)
    skill_ids: Optional[list] = None

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Field rule: sanitize title."""
        return _sanitize(v)

    @field_validator("skill_ids")
    @classmethod
    def validate_skill_ids(cls, v: Optional[list]) -> Optional[list]:
        """Require positive-int skill ids (dicts or ints)."""
        if v is not None:
            for item in v:
                sid = item.get("skill_id") if isinstance(item, dict) else item
                if sid is not None and (not isinstance(sid, int) or sid < 1):
                    raise ValueError("Skill IDs must be positive integers")
        return v


class JobRoleOut(BaseModel):
    """Serialized job_roles row; skill_ids from job_role_skills join."""

    id: int
    title: str
    description: Optional[str] = None
    career_field: Optional[str] = None
    skill_ids: list[int] = []


class JobRoleUpdate(BaseModel):
    """PUT /admin/job-roles/{id} body; None fields left untouched."""

    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    career_field: Optional[str] = Field(None, max_length=100)
    skill_ids: Optional[list] = None

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        """Field rule: sanitize title."""
        return _sanitize(v) if v is not None else v
