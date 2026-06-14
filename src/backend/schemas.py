from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
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
    created_at: Optional[datetime] = None
    profile_id: Optional[int] = None
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

class SkillBase(BaseModel):
    name: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int
    category: Optional[str] = None
    class Config:
        from_attributes = True

class SkillUpdate(SkillBase):
    pass

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    skills: List[Skill] = [] # لعرض المهارات المرتبطة
    class Config:
        from_attributes = True

# --- نماذج المصادر (Resources) ---

class ResourceBase(BaseModel):
    title: str
    url: str
    type: str
    is_free: bool = True
    is_official: bool = False
    author_or_platform: Optional[str] = None

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(ResourceBase):
    pass

class Resource(ResourceBase):
    id: int
    class Config:
        from_attributes = True

# --- نماذج الأدوار الوظيفية (JobRoles) ---

class JobRoleBase(BaseModel):
    title: str

class JobRoleCreate(JobRoleBase):
    pass

class JobRoleUpdate(JobRoleBase):
    pass

class JobRole(JobRoleBase):
    id: int
    skills: List[Skill] = [] # لعرض المهارات المرتبطة
    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class ProfileCreate(ProfileBase):
    password: str
    
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    skill_profile: Optional[dict] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# نموذج عرض المستخدم، مع إضافة حقل is_admin
class Profile(ProfileBase):
    id: int
    is_admin: bool
    skill_profile: Optional[dict] = None
    subscription_tier: str = "free"
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class UserActivityReport(BaseModel):
    total_users: int
    new_users_last_24h: int
    new_users_last_7d: int
    users_with_paths: int

class ContentEngagementReport(BaseModel):
    total_paths: int
    total_steps: int
    total_completions: int
    most_completed_steps: List[dict] # Will contain {"title": str, "completions": int}

class SystemHealthReport(BaseModel):
    database_status: str
    last_seed_run: Optional[datetime] = None # Will be implemented later

class PathAdminView(BaseModel):
    id: int
    title: str
    user_email: str
    total_estimated_hours: Optional[int] = None
    is_completed: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None # اختياري، إذا أراد الأدمن تغيير كلمة المرور
    is_admin: Optional[bool] = None # لتغيير الصلاحية

    class Config:
        from_attributes = True