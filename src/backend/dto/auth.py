"""Auth DTOs — registration, profile and password payloads.

Consumed by routers/auth_router.py (Task 3) and services/auth_service.py.
ProfileOut is the wire shape of /auth/me + /auth/register; its flat
`skill_profile` dict is synthesized by auth_service.build_profile_out.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class PasswordValidator:
    """Shared password policy (ported verbatim from old password_service)."""

    @staticmethod
    def validate(v: str) -> str:
        """Raise ValueError unless the password satisfies the full policy."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\\[\]~`]", v):
            raise ValueError("Password must contain at least one special character")
        if re.search(r"\s", v):
            raise ValueError("Password must not contain whitespace")
        common = ["password", "123456", "qwerty", "admin", "skillsynth", "letmein"]
        if any(p in v.lower() for p in common):
            raise ValueError("Password contains common patterns")
        return v

    @staticmethod
    def sanitize_name(v: Optional[str]) -> Optional[str]:
        """Strip HTML-ish characters from free-text names."""
        if v is None:
            return v
        v = re.sub(r"[<>'\"\\]", "", v)
        if len(v) > 100:
            raise ValueError("Name must not exceed 100 characters")
        return v


class RegisterInput(BaseModel):
    """POST /auth/register body; validated by auth_service.register."""

    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Delegate to the shared PasswordValidator policy."""
        return PasswordValidator.validate(v)

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Delegate to the shared name sanitizer."""
        return PasswordValidator.sanitize_name(v)


class ProfileOut(BaseModel):
    """Wire shape of /auth/me and /auth/register (keys frozen).

    skill_profile maps skills.name -> proficiency_level via user_skills;
    synthesized in auth_service.build_profile_out, never stored on User.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_admin: bool = False
    skill_profile: dict[str, int] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProfileUpdate(BaseModel):
    """PUT /auth/me body; applied by auth_service.update_profile."""

    full_name: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        """Delegate to the shared name sanitizer."""
        return PasswordValidator.sanitize_name(v)


class PasswordChange(BaseModel):
    """POST /auth/change-password body."""

    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Field rule: validate new password."""
        return PasswordValidator.validate(v)


class ResetRequest(BaseModel):
    """POST /auth/forgot-password body (email only, no enumeration)."""

    email: EmailStr


class ResetConfirm(BaseModel):
    """POST /auth/reset-password body; token issued by request_reset."""

    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Field rule: validate new password."""
        return PasswordValidator.validate(v)


class Token(BaseModel):
    """POST /auth/token response (login handled as form fields in router)."""

    access_token: str
    token_type: str
