from sqlalchemy.orm import Session
from backend import models, schemas, auth

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

