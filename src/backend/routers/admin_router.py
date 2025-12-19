# src/backend/routers/admin_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend import crud, models, schemas, auth
from backend.database import get_db

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Dashboard - Professional"],
    dependencies=[Depends(auth.get_current_admin_user)]
)

# ===============================================================
#  القسم 1: مركز الاستخبارات (Intelligence Center)
# ===============================================================

@router.get("/reports/user-activity", response_model=schemas.UserActivityReport, summary="Get User Activity Report")
def get_user_activity_report(db: Session = Depends(get_db)):
    """[Admin Only] تقرير عن نشاط المستخدمين."""
    return crud.get_user_activity_stats(db)

@router.get("/reports/content-engagement", response_model=schemas.ContentEngagementReport, summary="Get Content Engagement Report")
def get_content_engagement_report(db: Session = Depends(get_db)):
    """[Admin Only] تقرير عن تفاعل المحتوى."""
    return crud.get_content_engagement_stats(db)

@router.get("/reports/system-health", response_model=schemas.SystemHealthReport, summary="Get System Health Report")
def get_system_health_report(db: Session = Depends(get_db)):
    """[Admin Only] تقرير عن صحة النظام."""
    try:
        db.query(models.Profile).first()
        db_status = "Connected"
    except Exception:
        db_status = "Connection Error"
    return {"database_status": db_status}

@router.get("/reports/most-active-users", summary="Get Most Active Users Report")
def get_most_active_users_report(db: Session = Depends(get_db)):
    """[Admin Only] تقرير بأكثر 10 مستخدمين نشاطًا."""
    active_users = crud.get_most_active_users(db)
    return [{"user_email": email, "completed_steps": count} for email, count in active_users]

@router.get("/reports/most-requested-skills", summary="Get Most Requested Skills Report")
def get_most_requested_skills_report(db: Session = Depends(get_db)):
    """[Admin Only] تقرير بأكثر 10 مهارات طلبًا."""
    requested_skills = crud.get_most_requested_skills(db)
    return [{"skill_name": name, "path_count": count} for name, count in requested_skills]

# ===============================================================
#  القسم 2: مركز إدارة المحتوى (CRUD الكامل)
# ===============================================================

# --- إدارة المستخدمين ---
@router.get("/users/", response_model=List[schemas.Profile], summary="List All Users")
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_profiles(db, skip=skip, limit=limit)

# --- إدارة المهارات (CRUD الكامل) ---
@router.post("/skills/", response_model=schemas.Skill, status_code=status.HTTP_201_CREATED)
def create_new_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    if crud.get_skill_by_name(db, name=skill.name):
        raise HTTPException(status_code=400, detail="Skill already exists.")
    return crud.create_skill(db=db, skill=skill)

@router.get("/skills/", response_model=List[schemas.Skill])
def read_all_skills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_skills(db, skip=skip, limit=limit)

@router.put("/skills/{skill_id}", response_model=schemas.Skill)
def update_a_skill(skill_id: int, skill_data: schemas.SkillUpdate, db: Session = Depends(get_db)):
    db_skill = crud.update_skill(db, skill_id, skill_data)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return db_skill

@router.delete("/skills/{skill_id}", response_model=schemas.Skill)
def delete_a_skill(skill_id: int, db: Session = Depends(get_db)):
    db_skill = crud.delete_item_by_id(db, models.Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return db_skill
    
# --- إدارة التصنيفات (CRUD الكامل) ---
@router.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_new_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if crud.get_category_by_name(db, name=category.name):
        raise HTTPException(status_code=400, detail="Category already exists.")
    return crud.create_category(db=db, category=category)

@router.get("/categories/", response_model=List[schemas.Category])
def read_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

@router.put("/categories/{category_id}", response_model=schemas.Category)
def update_a_category(category_id: int, category_data: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    db_category = crud.update_category(db, category_id, category_data)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/categories/{category_id}", response_model=schemas.Category)
def delete_a_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.delete_item_by_id(db, models.Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# --- إدارة المصادر (CRUD الكامل) ---
@router.post("/resources/", response_model=schemas.Resource, status_code=status.HTTP_201_CREATED)
def create_new_resource(resource: schemas.ResourceCreate, db: Session = Depends(get_db)):
    return crud.create_resource(db, resource)

@router.get("/resources/", response_model=List[schemas.Resource])
def read_all_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_resources(db, skip, limit)

@router.put("/resources/{resource_id}", response_model=schemas.Resource)
def update_a_resource(resource_id: int, resource_data: schemas.ResourceUpdate, db: Session = Depends(get_db)):
    db_resource = crud.update_resource(db, resource_id, resource_data)
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return db_resource

@router.delete("/resources/{resource_id}", response_model=schemas.Resource)
def delete_a_resource(resource_id: int, db: Session = Depends(get_db)):
    db_resource = crud.delete_item_by_id(db, models.Resource, resource_id)
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return db_resource

# --- إدارة الأدوار الوظيفية (CRUD الكامل) ---
@router.post("/job-roles/", response_model=schemas.JobRole, status_code=status.HTTP_201_CREATED)
def create_new_job_role(job_role: schemas.JobRoleCreate, db: Session = Depends(get_db)):
    if crud.get_job_role_by_title(db, title=job_role.title):
        raise HTTPException(status_code=400, detail="Job role already exists.")
    return crud.create_job_role(db=db, job_role=job_role)

@router.get("/job-roles/", response_model=List[schemas.JobRole])
def read_all_job_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_job_roles(db, skip=skip, limit=limit)

@router.put("/job-roles/{job_role_id}", response_model=schemas.JobRole)
def update_a_job_role(job_role_id: int, job_role_data: schemas.JobRoleUpdate, db: Session = Depends(get_db)):
    db_job_role = crud.update_job_role(db, job_role_id, job_role_data)
    if not db_job_role:
        raise HTTPException(status_code=404, detail="Job role not found")
    return db_job_role

@router.delete("/job-roles/{job_role_id}", response_model=schemas.JobRole)
def delete_a_job_role(job_role_id: int, db: Session = Depends(get_db)):
    db_job_role = crud.delete_item_by_id(db, models.JobRole, job_role_id)
    if not db_job_role:
        raise HTTPException(status_code=404, detail="Job role not found")
    return db_job_role