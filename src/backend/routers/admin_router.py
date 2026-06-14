# src/backend/routers/admin_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend import crud, models, schemas, auth
from backend.database import get_db
from sqlalchemy import text

# تنويه: البادئة (Prefix) سيتم تحديدها في main.py وليس هنا لتجنب التكرار
router = APIRouter(
    tags=["Admin Dashboard"],
    dependencies=[Depends(auth.get_current_admin_user)]
)

# =========================
#  1. التقارير (Reports)
# =========================

@router.get("/reports/user-activity", response_model=schemas.UserActivityReport)
def get_user_activity_report(db: Session = Depends(get_db)):
    return crud.get_user_activity_stats(db)

@router.get("/reports/content-engagement", response_model=schemas.ContentEngagementReport)
def get_content_engagement_report(db: Session = Depends(get_db)):
    return crud.get_content_engagement_stats(db)

@router.get("/reports/system-health", response_model=schemas.SystemHealthReport)
def get_system_health_report(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"database_status": "Connected"}
    except Exception:
        return {"database_status": "Connection Error"}

@router.get("/reports/most-active-users")
def get_most_active_users_report(db: Session = Depends(get_db)):
    data = crud.get_most_active_users(db)
    # تحويل الـ Tuples إلى JSON
    return [{"user_email": r[0], "completed_steps": r[1]} for r in data]

@router.get("/reports/most-requested-skills")
def get_most_requested_skills_report(db: Session = Depends(get_db)):
    data = crud.get_most_requested_skills(db)
    return [{"skill_name": r[0], "path_count": r[1]} for r in data]

# =========================
#  2. إدارة المستخدمين والمسارات
# =========================

@router.get("/users", response_model=List[schemas.Profile])
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_profiles(db, skip=skip, limit=limit)

@router.get("/paths", response_model=List[schemas.PathAdminView])
def read_all_paths_as_admin(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    paths = crud.get_all_paths_admin(db, skip=skip, limit=limit)
    return [
        {
            "id": p.id,
            "title": p.title,
            "user_email": p.owner.email if p.owner else "Unknown",
            "created_at": p.created_at
        } for p in paths
    ]


@router.put("/users/{user_id}", response_model=schemas.Profile)
def update_user_by_admin(
    user_id: int, 
    user_data: schemas.AdminUserUpdate, 
    db: Session = Depends(get_db)
):
    """
    [Admin Only] تعديل بيانات أي مستخدم (تغيير الاسم، الايميل، كلمة المرور، الصلاحية).
    """
    updated_user = crud.update_user_as_admin(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# =========================
#  3. إدارة المحتوى (CRUD)
# =========================

# --- المهارات (Skills) ---
@router.get("/skills", response_model=List[schemas.Skill])
def read_skills(db: Session = Depends(get_db)):
    return crud.get_skills(db)

@router.post("/skills", response_model=schemas.Skill)
def create_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    if crud.get_skill_by_name(db, skill.name):
        raise HTTPException(status_code=400, detail="Skill already exists")
    return crud.create_skill(db, skill)

@router.put("/skills/{skill_id}", response_model=schemas.Skill)
def update_skill(skill_id: int, skill_data: schemas.SkillUpdate, db: Session = Depends(get_db)):
    # نستخدم الدالة العامة update_item
    item = crud.update_item(db, models.Skill, skill_id, skill_data)
    if not item: 
        raise HTTPException(status_code=404, detail="Skill not found")
    return item

@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    # استخدام الدالة المحسنة التي تحاول الحذف وتلتقط الأخطاء
    if not crud.delete_item_safely(db, models.Skill, skill_id):
        raise HTTPException(status_code=400, detail="Cannot delete skill. It might be in use.")
    return {"detail": "Deleted successfully"}

# --- التصنيفات (Categories) ---
@router.get("/categories", response_model=List[schemas.Category])
def read_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@router.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if crud.get_category_by_name(db, category.name):
        raise HTTPException(status_code=400, detail="Category already exists")
    return crud.create_category(db, category)

@router.put("/categories/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category_data: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    item = crud.update_item(db, models.Category, category_id, category_data)
    if not item:
        raise HTTPException(status_code=404, detail="Category not found")
    return item

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    if not crud.delete_item_safely(db, models.Category, category_id):
        raise HTTPException(status_code=400, detail="Cannot delete category. It might be in use.")
    return {"detail": "Deleted successfully"}

# --- المصادر (Resources) ---
@router.get("/resources", response_model=List[schemas.Resource])
def read_resources(db: Session = Depends(get_db)):
    return crud.get_resources(db)

@router.post("/resources", response_model=schemas.Resource)
def create_resource(resource: schemas.ResourceCreate, db: Session = Depends(get_db)):
    return crud.create_resource(db, resource)

@router.put("/resources/{resource_id}", response_model=schemas.Resource)
def update_resource(resource_id: int, resource_data: schemas.ResourceUpdate, db: Session = Depends(get_db)):
    item = crud.update_item(db, models.Resource, resource_id, resource_data)
    if not item:
        raise HTTPException(status_code=404, detail="Resource not found")
    return item

@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    # المصادر عادة يمكن حذفها بأمان أكبر، لكن سنستخدم الطريقة الآمنة أيضاً
    if not crud.delete_item_safely(db, models.Resource, resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"detail": "Deleted successfully"}

# --- الأدوار الوظيفية (Job Roles) ---
@router.get("/job-roles", response_model=List[schemas.JobRole])
def read_job_roles(db: Session = Depends(get_db)):
    return crud.get_job_roles(db)

@router.post("/job-roles", response_model=schemas.JobRole)
def create_job_role(job_role: schemas.JobRoleCreate, db: Session = Depends(get_db)):
    if crud.get_job_role_by_title(db, job_role.title):
        raise HTTPException(status_code=400, detail="Job role already exists")
    return crud.create_job_role(db, job_role)

@router.put("/job-roles/{job_role_id}", response_model=schemas.JobRole)
def update_job_role(job_role_id: int, job_role_data: schemas.JobRoleUpdate, db: Session = Depends(get_db)):
    item = crud.update_item(db, models.JobRole, job_role_id, job_role_data)
    if not item:
        raise HTTPException(status_code=404, detail="Job role not found")
    return item

@router.delete("/job-roles/{job_role_id}")
def delete_job_role(job_role_id: int, db: Session = Depends(get_db)):
    if not crud.delete_item_safely(db, models.JobRole, job_role_id):
        raise HTTPException(status_code=400, detail="Cannot delete job role. It might be in use.")
    return {"detail": "Deleted successfully"}