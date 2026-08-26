"""Admin DTOs — user management, aggregated reports and activity feed.

Consumed by services/admin_service.py and the admin routers (Task 3).
AggregatedReportOut nested keys are frozen (admin-app consumes them);
ActivityItemOut keeps the legacy profile_id/user keys and adds
user_email/user_agent from the merged activity_log table.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator

from backend.dto.auth import PasswordValidator


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
