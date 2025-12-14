from pydantic import BaseModel, EmailStr
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

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

class DetailedPreferences(BaseModel):
    # الحقول التي طلبها الفرونت اند وفريق الذكاء الاصطناعي
    is_free: Optional[bool] = True
    format: Optional[str] = "any"
    language: Optional[str] = "en"
    skills: Optional[dict] = {} # يبقى كخيار احتياطي

class GeneratePathInput(BaseModel):
    goal: str = Field(..., example="Frontend Developer")
    weekly_hours: int = Field(..., example=10)
    preferences: DetailedPreferences
    answers: dict[str, int] = Field(..., example={"html_q1": 0, "css_q1": 1})

class UserAnswer(BaseModel):
    # مثال: {"html_q1": 0, "css_q2": 1}
    answers: dict[str, int]

class AssessmentSubmit(BaseModel):
    goal: str
    user_answers: UserAnswer

class WizardPreferencesOptions(BaseModel):
    formats: List[str]
    languages: List[str]

class WizardOptionsResponse(BaseModel):
    job_roles: List[str]
    preferences: WizardPreferencesOptions

class AssessmentQuestionResponse(BaseModel):
    id: str
    skill: str
    text: str
    options: List[str]



class StepCompletionResponse(BaseModel):
    profile_id: int
    step_id: int
    completed_at: datetime

class Config:
    from_attributes = True