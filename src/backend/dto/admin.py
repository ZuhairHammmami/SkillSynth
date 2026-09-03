"""Admin DTOs — user management, aggregated reports and activity feed.

Consumed by services/admin_service.py and the admin routers (Task 3).
AggregatedReportOut nested keys are frozen (admin-app consumes them);
ActivityItemOut keeps the legacy profile_id/user keys and adds
user_email/user_agent from the merged activity_log table.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.dto.auth import PasswordValidator


def _sanitize(value: str) -> str:
    """Strip angle/quote characters from free text; requires non-empty."""
    value = value.strip()
    if not value:
        raise ValueError("Value must not be empty")
    return re.sub(r"[<>'\"\\]", "", value)


class AdminCreateUser(BaseModel):
    """POST /admin/users body; password follows the shared policy."""

    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_admin: bool = False

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Field rule: validate password."""
        return PasswordValidator.validate(v)

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup from full name."""
        if v is None:
            return None
        return PasswordValidator.sanitize_name(v)


class AdminUserUpdate(BaseModel):
    """PUT /admin/users/{id} body; None fields left untouched."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Field rule: validate password."""
        return PasswordValidator.validate(v) if v is not None else v

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup from full name."""
        if v is None:
            return None
        return PasswordValidator.sanitize_name(v)


class AdminUserOut(BaseModel):
    """Serialized users row for admin listing (no skill_profile)."""

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserActivityReport(BaseModel):
    """AggregatedReportOut.user_activity block (keys frozen)."""

    total_users: int
    new_users_last_24h: int
    new_users_last_7d: int
    users_with_paths: int


class ContentEngagementReport(BaseModel):
    """AggregatedReportOut.content_engagement block (keys frozen)."""

    total_paths: int
    total_steps: int
    total_completions: int
    most_completed_steps: List[dict]


class SystemHealthReport(BaseModel):
    """AggregatedReportOut.system_health block (keys frozen + additive
    `details` map for extra diagnostics)."""

    database_status: str
    api_version: str = "1.0.0"
    total_users: int
    total_paths: int
    total_assessments: int
    details: dict = {}


class PathAdminView(BaseModel):
    """Admin listing row for paths with owner email + completion flag."""

    id: int
    title: str
    user_email: str
    total_estimated_hours: Optional[int] = None
    is_completed: bool = False
    created_at: datetime


class EventUserInfo(BaseModel):
    """Nested actor info on activity items (role_name now always None
    since the roles layer was removed in Task 1)."""

    full_name: Optional[str] = None
    email: Optional[str] = None
    role_name: Optional[str] = None
    is_admin: bool = False


class ActivityItemOut(BaseModel):
    """Serialized activity_log row for the admin events/audit feed.

    Keeps legacy `profile_id` + `user` block; adds `user_email` and
    `user_agent` surfaced by engagement_repository.get_filtered."""

    id: int
    category: str
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    data: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None
    profile_id: Optional[int] = None
    user: Optional[EventUserInfo] = None
    user_email: Optional[str] = None
    user_agent: Optional[str] = None


class AggregatedReportOut(BaseModel):
    """GET /admin/reports/aggregated response — EXACT key contract.

    most_active_users items: {user_email, completed_steps};
    most_requested_skills items: {skill_name, path_count}.
    """

    user_activity: UserActivityReport
    content_engagement: ContentEngagementReport
    system_health: SystemHealthReport
    most_active_users: List[dict]
    most_requested_skills: List[dict]
    total_hours_learned: float
    average_completion_rate: float
    total_assessment_attempts: int
    average_assessment_score: float


AdminDashboardResponse = AggregatedReportOut


# ── Evaluations (assessments + questions) ─────────────────────────────

class AssessmentCreate(BaseModel):
    """POST /admin/assessments body; links an assessment to one skill."""

    skill_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    pass_score: int = Field(60, ge=0, le=100)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Strip markup via the shared sanitizer."""
        return _sanitize(v)

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup from description text."""
        if v is None:
            return None
        v = v.strip()
        return _sanitize(v) if v else None


class AssessmentUpdate(BaseModel):
    """PUT /admin/assessments/{id} body; None fields left untouched."""

    skill_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    pass_score: Optional[int] = Field(None, ge=0, le=100)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup when a new value is supplied."""
        return _sanitize(v) if v is not None else v

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup from description text."""
        if v is None:
            return None
        v = v.strip()
        return _sanitize(v) if v else None


class QuestionCreate(BaseModel):
    """POST /admin/assessments/{id}/questions body (position optional).

    Semantic option/index rules are enforced by evaluations_service so
    they surface as a 400 (mapped), not a 422 field error."""

    prompt: str = Field(..., min_length=1, max_length=2000)
    options: List[str]
    correct_index: int = Field(..., ge=0)
    position: Optional[int] = Field(None, ge=1)

    @field_validator("prompt")
    @classmethod
    def sanitize_prompt(cls, v: str) -> str:
        """Strip markup via the shared sanitizer."""
        return _sanitize(v)

    @field_validator("options")
    @classmethod
    def sanitize_options(cls, v: List[str]) -> List[str]:
        """Strip, sanitize, and enforce max length on each option string."""
        if not v or len(v) < 2:
            raise ValueError("At least 2 options are required")
        cleaned = []
        for opt in v:
            opt = opt.strip()
            if not opt:
                raise ValueError("Options must not be empty strings")
            if len(opt) > 500:
                raise ValueError("Each option must be 500 characters or fewer")
            cleaned.append(_sanitize(opt))
        return cleaned


class QuestionUpdate(BaseModel):
    """PUT /admin/assessments/{id}/questions/{qid} body; None left as-is."""

    prompt: Optional[str] = Field(None, min_length=1, max_length=2000)
    options: Optional[List[str]] = None
    correct_index: Optional[int] = Field(None, ge=0)
    position: Optional[int] = Field(None, ge=1)

    @field_validator("prompt")
    @classmethod
    def sanitize_prompt(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup when a new value is supplied."""
        return _sanitize(v) if v is not None else v

    @field_validator("options")
    @classmethod
    def sanitize_options(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Strip, sanitize, and enforce max length on each option string."""
        if v is None:
            return None
        if len(v) < 2:
            raise ValueError("At least 2 options are required")
        cleaned = []
        for opt in v:
            opt = opt.strip()
            if not opt:
                raise ValueError("Options must not be empty strings")
            if len(opt) > 500:
                raise ValueError("Each option must be 500 characters or fewer")
            cleaned.append(_sanitize(opt))
        return cleaned


class AssessmentQuestionOut(BaseModel):
    """Serialized question row within an assessment detail payload."""

    id: int
    assessment_id: int
    position: int
    prompt: str
    options: List[str]
    correct_index: int


class AssessmentDetailOut(BaseModel):
    """GET /admin/assessments/{id} — metadata + ordered questions."""

    id: int
    skill_id: Optional[int] = None
    skill_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    assessment_type: Optional[str] = None
    passing_score: int
    question_count: int = 0
    questions: List[AssessmentQuestionOut] = []
