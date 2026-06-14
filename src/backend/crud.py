# src/backend/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Type, Optional
from datetime import datetime, timedelta
from backend import models, schemas, auth

# --- دوال المستخدم ---
def get_profile_by_email(db: Session, email: str):
    return db.query(models.Profile).filter(models.Profile.email == email).first()

def create_profile(db: Session, profile: schemas.ProfileCreate):
    hashed_password = auth.get_password_hash(profile.password)
    db_profile = models.Profile(
        email=profile.email, 
        full_name=profile.full_name, 
        hashed_password=hashed_password,
        is_admin=False
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def update_profile(db: Session, profile_id: int, profile_data: schemas.ProfileUpdate):
    db_profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if db_profile:
        update_data = profile_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_profile, key, value)
        db.commit()
        db.refresh(db_profile)
    return db_profile

def update_password(db: Session, profile_id: int, new_password_hash: str):
    db.query(models.Profile).filter(models.Profile.id == profile_id).update({"hashed_password": new_password_hash})
    db.commit()

# --- دوال المسارات ---
def create_path_for_profile(db: Session, title: str, description: str, profile_id: int):
    db_path = models.Path(title=title, description=description, profile_id=profile_id)
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    return db_path

def get_paths_by_profile(db: Session, profile_id: int):
    return db.query(models.Path).filter(models.Path.profile_id == profile_id).all()

def get_path_by_id(db: Session, path_id: int, profile_id: int):
    return db.query(models.Path).filter(models.Path.id == path_id, models.Path.profile_id == profile_id).first()

# --- دوال المسؤول (Admin) ---
def get_profiles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Profile).order_by(models.Profile.id).offset(skip).limit(limit).all()

def get_all_paths_admin(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Path).order_by(models.Path.created_at.desc()).offset(skip).limit(limit).all()

def get_item_by_id(db: Session, model: Type[models.Base], item_id: int):
    return db.query(model).filter(model.id == item_id).first()

def delete_item_by_id(db: Session, model: Type[models.Base], item_id: int):
    db_item = get_item_by_id(db, model, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

def update_item(db: Session, model: Type[models.Base], item_id: int, data: schemas.BaseModel):
    db_item = get_item_by_id(db, model, item_id)
    if db_item:
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

# -- إحصائيات التقارير --
def get_user_activity_stats(db: Session):
    total_users = db.query(models.Profile).count()
    time_24h_ago = datetime.utcnow() - timedelta(days=1)
    new_24h = db.query(models.Profile).filter(models.Profile.created_at >= time_24h_ago).count()
    time_7d_ago = datetime.utcnow() - timedelta(days=7)
    new_7d = db.query(models.Profile).filter(models.Profile.created_at >= time_7d_ago).count()
    users_with_paths = db.query(models.Profile).filter(models.Profile.paths.any()).count()
    return {"total_users": total_users, "new_users_last_24h": new_24h, "new_users_last_7d": new_7d, "users_with_paths": users_with_paths}

def get_content_engagement_stats(db: Session):
    total_paths = db.query(models.Path).count()
    total_steps = db.query(models.PathStep).count()
    total_completions = db.query(models.StepCompletion).count()
    most_completed = db.query(models.PathStep.title, func.count(models.StepCompletion.step_id).label('completions')).join(models.StepCompletion).group_by(models.PathStep.title).order_by(desc('completions')).limit(5).all()
    return {"total_paths": total_paths, "total_steps": total_steps, "total_completions": total_completions, "most_completed_steps": [{"title": r[0], "completions": r[1]} for r in most_completed]}

def get_most_active_users(db: Session, limit: int = 10):
    return db.query(models.Profile.email, func.count(models.StepCompletion.profile_id).label('count')).join(models.StepCompletion).group_by(models.Profile.email).order_by(desc('count')).limit(limit).all()

def get_most_requested_skills(db: Session, limit: int = 10):
    # استخدام جدول الربط path_skills للعد
    return db.query(models.Skill.name, func.count(models.path_skills.c.skill_id).label('count')).join(models.path_skills).group_by(models.Skill.name).order_by(desc('count')).limit(limit).all()

# -- مهارات وتصنيفات --
def get_skill_by_name(db: Session, name: str):
    return db.query(models.Skill).filter(models.Skill.name.ilike(name)).first()
def create_resource(db: Session, resource: schemas.ResourceCreate):
    db_resource = models.Resource(
        title=resource.title,
        url=resource.url,
        type=resource.type,
        is_free=resource.is_free,
        is_official=resource.is_official,
        author_or_platform=resource.author_or_platform
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

def create_skill(db: Session, skill: schemas.SkillCreate):
    db_skill = models.Skill(name=skill.name)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill
def get_skills(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Skill).offset(skip).limit(limit).all()

def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name.ilike(name)).first()
def create_category(db: Session, category: schemas.CategoryCreate):
    db_cat = models.Category(name=category.name)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def get_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Resource).offset(skip).limit(limit).all()
def get_job_role_by_title(db: Session, title: str):
    return db.query(models.JobRole).filter(models.JobRole.title.ilike(title)).first()
def create_job_role(db: Session, job_role: schemas.JobRoleCreate):
    db_jr = models.JobRole(title=job_role.title)
    db.add(db_jr)
    db.commit()
    db.refresh(db_jr)
    return db_jr
def get_job_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.JobRole).offset(skip).limit(limit).all()

# دالة الحذف الآمن (لمنع انهيار السيرفر عند وجود ارتباطات)
def delete_item_safely(db: Session, model: Type[models.Base], item_id: int) -> bool:
    db_item = get_item_by_id(db, model, item_id)
    if not db_item:
        return False
    try:
        db.delete(db_item)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False # فشل الحذف بسبب ارتباطات خارجية
    
def mark_step_as_complete(db: Session, profile_id: int, step_id: int):
    existing = db.query(models.StepCompletion).filter(
        models.StepCompletion.profile_id == profile_id,
        models.StepCompletion.step_id == step_id
    ).first()
    if existing:
        return existing
    completion = models.StepCompletion(profile_id=profile_id, step_id=step_id)
    db.add(completion)
    db.commit()
    db.refresh(completion)
    return completion

def update_user_as_admin(db: Session, user_id: int, user_data: schemas.AdminUserUpdate):
    db_user = get_item_by_id(db, models.Profile, user_id)
    if db_user:
        update_data = user_data.dict(exclude_unset=True)
        
        # إذا تم إرسال كلمة مرور جديدة، يجب تشفيرها قبل الحفظ
        if 'password' in update_data and update_data['password']:
            hashed_pw = auth.get_password_hash(update_data['password'])
            update_data['hashed_password'] = hashed_pw
            del update_data['password'] # نحذف حقل كلمة المرور الخام
            
        for key, value in update_data.items():
            setattr(db_user, key, value)
            
        db.commit()
        db.refresh(db_user)
    return db_user