# crud.py

from sqlalchemy.orm import Session
import models, schemas # نستورد النماذج من الملفين الآخرين

# ============= Profile CRUD Functions =============
def get_profile_by_email(db: Session, email: str):
    return db.query(models.Profile).filter(models.Profile.email == email).first()

def create_profile(db: Session, profile: schemas.ProfileCreate):
    db_profile = models.Profile(email=profile.email, full_name=profile.full_name)
    db.add(db_profile) # أضف الكائن إلى الجلسة
    db.commit() # احفظ التغييرات في قاعدة البيانات
    db.refresh(db_profile) # قم بتحديث الكائن بالبيانات الجديدة من قاعدة البيانات (مثل الـ ID)
    return db_profile

# ============= Path CRUD Functions =============
def create_path_for_profile(db: Session, path: schemas.PathCreate, profile_id: int):
    # أنشئ كائن المسار واربطه بالـ profile_id
    db_path = models.Path(**path.dict(), profile_id=profile_id)
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    return db_path

def get_paths_by_profile(db: Session, profile_id: int):
    return db.query(models.Path).filter(models.Path.profile_id == profile_id).all()