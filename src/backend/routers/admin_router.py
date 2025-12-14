# src/backend/routers/admin_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend import crud, models, schemas, auth
from backend.database import get_db

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Dashboard - Full"],
    dependencies=[Depends(auth.get_current_admin_user)]
)

# ===============================================================
#  1. مركز التقارير (Intelligence Center)
# ===============================================================

@router.get("/reports/user-activity", response_model=schemas.UserActivityReport)
def get_user_activity_report(db: Session = Depends(get_db)):
    """
    [Admin Only] تقرير عن نشاط المستخدمين:
    - إجمالي عدد المستخدمين.
    - المستخدمون الجدد في آخر 24 ساعة / 7 أيام.
    - عدد المستخدمين الذين بدأوا مسارًا واحدًا على الأقل.
    """
    return crud.get_user_activity_stats(db)

@router.get("/reports/content-engagement", response_model=schemas.ContentEngagementReport)
def get_content_engagement_report(db: Session = Depends(get_db)):
    """
    [Admin Only] تقرير عن تفاعل المحتوى:
    - إجمالي عدد المسارات والخطوات المنشأة.
    - إجمالي عدد عمليات إكمال الخطوات.
    - أكثر 5 خطوات تم إكمالها (لقياس المحتوى الأكثر شعبية/فعالية).
    """
    return crud.get_content_engagement_stats(db)

@router.get("/reports/system-health", response_model=schemas.SystemHealthReport)
def get_system_health_report(db: Session = Depends(get_db)):
    """
    [Admin Only] تقرير عن صحة النظام.
    - يتحقق من الاتصال بقاعدة البيانات.
    """
    try:
        # استعلام بسيط جدًا للتأكد من أن الاتصال يعمل
        db.query(models.Profile).first()
        db_status = "Connected"
    except Exception:
        db_status = "Connection Error"
    
    return {"database_status": db_status}

# ===============================================================
#  2. مركز إدارة المحتوى (Content Management)
# ===============================================================

# --- إدارة المهارات (Skills) ---
@router.post("/skills", response_model=schemas.Skill, status_code=status.HTTP_201_CREATED)
def create_new_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    if crud.get_skill_by_name(db, name=skill.name):
        raise HTTPException(status_code=400, detail="Skill already exists.")
    return crud.create_skill(db=db, skill=skill)

@router.get("/skills", response_model=List[schemas.Skill])
def read_all_skills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_skills(db, skip=skip, limit=limit)
    
# (يمكنك إضافة PUT و DELETE هنا بنفس النمط)

# --- إدارة التصنيفات (Categories) ---
@router.post("/categories", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_new_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if crud.get_category_by_name(db, name=category.name):
        raise HTTPException(status_code=400, detail="Category already exists.")
    return crud.create_category(db=db, category=category)

@router.get("/categories", response_model=List[schemas.Category])
def read_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

# (يمكن إضافة بقية نقاط النهاية لإدارة Resources, JobRoles بنفس الطريقة)

# ===============================================================
#  3. مركز إدارة المستخدمين (User Management)
# ===============================================================
@router.get("/users", response_model=List[schemas.Profile])
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    [Admin Only] يعرض قائمة بجميع المستخدمين في النظام.
    """
    profiles = crud.get_profiles(db, skip=skip, limit=limit)
    return profiles

# يمكنك إضافة نقاط نهاية هنا لـ "حظر مستخدم" أو "ترقية مستخدم إلى مسؤول"
# مثال: PUT /users/{user_id}/promote