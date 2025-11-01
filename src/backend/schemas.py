# src/backend/schemas.py

from pydantic import BaseModel, EmailStr, Field # <-- هذا هو التعديل الوحيد والمهم
from typing import List, Optional

class PathStepBase(BaseModel):
    step_number: int
    title: str
    content: Optional[str] = None

class PathStep(PathStepBase):
    id: int
    class Config:
        from_attributes = True

class PathBase(BaseModel):
    title: str
    description: Optional[str] = None

class Path(PathBase):
    id: int
    steps: List[PathStep] = []
    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class ProfileCreate(ProfileBase):
    password: str

class Profile(ProfileBase):
    id: int
    paths: List[Path] = []
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class GeneratePathInput(BaseModel):
    # الآن الكود سيعمل لأننا قمنا باستيراد Field
    goal: str = Field(..., example="frontend_developer")
    weekly_hours: int = Field(..., example=10)
    preferences: dict = Field(..., example={"format": "video", "skills": {"html": 2}})