from sqlalchemy.orm import Session
from backend import models, schemas, auth
from typing import List
from sqlalchemy import func, desc
from datetime import datetime, timedelta

def get_profile_by_email(db: Session, email: str):
    return db.query(models.Profile).filter(models.Profile.email == email).first()

def create_profile(db: Session, profile: schemas.ProfileCreate):
    hashed_password = auth.get_password_hash(profile.password)
    db_profile = models.Profile(
        email=profile.email,
        full_name=profile.full_name,
        hashed_password=hashed_password
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def create_path_for_profile(db: Session, title: str, description: str, profile_id: int):
    db_path = models.Path(title=title, description=description, profile_id=profile_id)
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    return db_path

def get_paths_by_profile(db: Session, profile_id: int):
    return db.query(models.Path).filter(models.Path.profile_id == profile_id).all()

def get_path_by_id(db: Session, path_id: int, profile_id: int):
    """
    يسترجع مسارًا واحدًا محددًا بالـ ID، 
    ويتأكد من أنه ينتمي للمستخدم الحالي لمنع الوصول غير المصرح به.
    """
    return db.query(models.Path).filter(
        models.Path.id == path_id,
        models.Path.profile_id == profile_id
    ).first()

def update_profile_skills(db: Session, profile_id: int, skill_profile: dict):
    """
    يقوم بتحديث حقل skill_profile (من نوع JSON) لمستخدم معين.
    """
    db.query(models.Profile).filter(models.Profile.id == profile_id).update({"skill_profile": skill_profile})
    db.commit()
    return db.query(models.Profile).filter(models.Profile.id == profile_id).first()

def mark_step_as_complete(db: Session, profile_id: int, step_id: int) -> models.StepCompletion:
    """
    يقوم بإنشاء سجل جديد في جدول step_completions لتوثيق إكمال المستخدم لخطوة.
    إذا كان السجل موجودًا بالفعل، فإنه يعيده ببساطة (لا يسبب خطأ).
    """
    # أولاً، تحقق مما إذا كان السجل موجودًا بالفعل
    db_completion = db.query(models.StepCompletion).filter(
        models.StepCompletion.profile_id == profile_id,
        models.StepCompletion.step_id == step_id
    ).first()

    if db_completion:
        # إذا كانت الخطوة قد اكتملت بالفعل، أعد السجل الموجود
        return db_completion

    # إذا لم يكن موجودًا، أنشئ سجلًا جديدًا
    db_completion = models.StepCompletion(profile_id=profile_id, step_id=step_id)
    db.add(db_completion)
    db.commit()
    db.refresh(db_completion)
    return db_completion

def update_profile(db: Session, profile_id: int, profile_data: schemas.ProfileUpdate):
    db.query(models.Profile).filter(models.Profile.id == profile_id).update(profile_data.dict(exclude_unset=True))
    db.commit()
    return db.query(models.Profile).filter(models.Profile.id == profile_id).first()

def update_password(db: Session, profile_id: int, new_password_hash: str):
    db.query(models.Profile).filter(models.Profile.id == profile_id).update({"hashed_password": new_password_hash})
    db.commit()

def get_skill_by_name(db: Session, name: str) -> models.Skill | None:
    """يبحث عن مهارة بالاسم."""
    return db.query(models.Skill).filter(models.Skill.name.ilike(f"%{name}%")).first()

def get_skills(db: Session, skip: int = 0, limit: int = 100) -> List[models.Skill]:
    """يسترجع قائمة بالمهارات مع إمكانية التصفح (pagination)."""
    # الآن هذا السطر سيعمل لأن 'List' أصبحت معروفة
    return db.query(models.Skill).offset(skip).limit(limit).all()

def create_skill(db: Session, skill: schemas.SkillCreate) -> models.Skill:
    """ينشئ مهارة جديدة في قاعدة البيانات."""
    db_skill = models.Skill(name=skill.name)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

def update_skill(db: Session, skill_id: int, skill_data: schemas.SkillUpdate) -> models.Skill | None:
    """يقوم بتحديث بيانات مهارة موجودة."""
    db_skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if db_skill:
        update_data = skill_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_skill, key, value)
        db.commit()
        db.refresh(db_skill)
    return db_skill

def delete_skill(db: Session, skill_id: int) -> models.Skill | None:
    """يحذف مهارة من قاعدة البيانات."""
    db_skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
    if db_skill:
        db.delete(db_skill)
        db.commit()
    return db_skill

def update_profile(db: Session, profile_id: int, profile_data: schemas.ProfileUpdate):
    db_profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if db_profile:
        update_data = profile_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_profile, key, value)
        db.commit()
        db.refresh(db_profile)
    return db_profile

# --- دوال CRUD للمسؤول (Admin) ---

# -- Skills --
def get_skill_by_name(db: Session, name: str):
    return db.query(models.Skill).filter(models.Skill.name.ilike(name)).first()

def get_skills(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Skill).offset(skip).limit(limit).all()

def create_skill(db: Session, skill: schemas.SkillCreate):
    db_skill = models.Skill(name=skill.name)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

# -- Categories --
def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name.ilike(name)).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).order_by(models.Category.name).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# -- Resources --
def get_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Resource).offset(skip).limit(limit).all()

def create_resource(db: Session, resource: schemas.ResourceCreate):
    db_resource = models.Resource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

# -- JobRoles --
def get_job_role_by_title(db: Session, title: str):
    return db.query(models.JobRole).filter(models.JobRole.title.ilike(title)).first()

def get_job_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.JobRole).order_by(models.JobRole.title).offset(skip).limit(limit).all()

def create_job_role(db: Session, job_role: schemas.JobRoleCreate):
    db_job_role = models.JobRole(title=job_role.title)
    db.add(db_job_role)
    db.commit()
    db.refresh(db_job_role)
    return db_job_role

# -- Profiles (للمسؤول) --
def get_profiles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Profile).offset(skip).limit(limit).all()

def get_user_activity_stats(db: Session) -> dict:
    total_users = db.query(models.Profile).count()
    
    time_24h_ago = datetime.utcnow() - timedelta(days=1)
    new_users_last_24h = db.query(models.Profile).filter(models.Profile.created_at >= time_24h_ago).count()
    
    time_7d_ago = datetime.utcnow() - timedelta(days=7)
    new_users_last_7d = db.query(models.Profile).filter(models.Profile.created_at >= time_7d_ago).count()

    users_with_paths = db.query(models.Profile).filter(models.Profile.paths.any()).count()

    return {
        "total_users": total_users,
        "new_users_last_24h": new_users_last_24h,
        "new_users_last_7d": new_users_last_7d,
        "users_with_paths": users_with_paths
    }

def get_content_engagement_stats(db: Session) -> dict:
    total_paths = db.query(models.Path).count()
    total_steps = db.query(models.PathStep).count()
    total_completions = db.query(models.StepCompletion).count()

    # استعلام معقد للحصول على أكثر 5 خطوات تم إكمالها
    most_completed_steps_query = db.query(
        models.PathStep.title,
        func.count(models.StepCompletion.step_id).label('completions')
    ).join(
        models.StepCompletion, models.PathStep.id == models.StepCompletion.step_id
    ).group_by(
        models.PathStep.title
    ).order_by(
        desc('completions')
    ).limit(5).all()

    most_completed_steps = [{"title": title, "completions": count} for title, count in most_completed_steps_query]

    return {
        "total_paths": total_paths,
        "total_steps": total_steps,
        "total_completions": total_completions,
        "most_completed_steps": most_completed_steps
    }