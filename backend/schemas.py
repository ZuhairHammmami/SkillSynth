# schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional

# ==================== PathStep Schemas ====================
class PathStepBase(BaseModel):
    step_number: int
    title: str
    content: Optional[str] = None

class PathStepCreate(PathStepBase):
    pass

class PathStep(PathStepBase):
    id: int

    class Config:
        orm_mode = True

# ==================== Path Schemas ====================
class PathBase(BaseModel):
    title: str
    description: Optional[str] = None

class PathCreate(PathBase):
    pass

class Path(PathBase):
    id: int
    steps: List[PathStep] = []

    class Config:
        orm_mode = True

# ==================== Profile Schemas ====================
class ProfileBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    paths: List[Path] = []

    class Config:
        from_attributes = True

# ==================== Input for Path Generation ====================
class GeneratePathInput(BaseModel):
    profile_id: int
    goal: str
    weekly_hours: int
    preferences: dict