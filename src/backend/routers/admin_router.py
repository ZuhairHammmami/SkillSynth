# src/backend/routers/admin_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# نستورد كل ما نحتاجه
from backend import crud, models, schemas, auth
from backend.database import get_db

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Dashboard - Full"], # اسم موحد وشامل
    dependencies=[Depends(auth.get_current_admin_user)] # حماية كل نقاط النهاية
)

# ===============================================================
#  القسم 1: مركز التقارير (Intelligence Center)
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

# ===============================================================
#  القسم 2: مركز إدارة المحتوى (Content Management)
# ===============================================================

# --- إدارة المستخدمين ---
@router.get("/users", response_model=List[schemas.Profile], summary="List All Users")
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """[Admin Only] يعرض قائمة بجميع المستخدمين."""
    return crud.get_profiles(db, skip=skip, limit=limit)

# --- إدارة المهارات ---
@router.post("/skills", response_model=schemas.Skill, status_code=status.HTTP_201_CREATED, summary="Create a new skill")
def create_new_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    if crud.get_skill_by_name(db, name=skill.name):
        raise HTTPException(status_code=400, detail="Skill already exists.")
    return crud.create_skill(db=db, skill=skill)

@router.get("/skills", response_model=List[schemas.Skill], summary="List all skills")
def read_all_skills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_skills(db, skip=skip, limit=limit)

# --- إدارة التصنيفات ---
@router.post("/categories", response_model=schemas.Category, status_code=status.HTTP_201_CREATED, summary="Create a new category")
def create_new_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if crud.get_category_by_name(db, name=category.name):
        raise HTTPException(status_code=400, detail="Category already exists.")
    return crud.create_category(db=db, category=category)

@router.get("/categories", response_model=List[schemas.Category], summary="List all categories")
def read_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

# --- إدارة المصادر ---
@router.post("/resources", response_model=schemas.Resource, status_code=status.HTTP_201_CREATED, summary="Create a new resource")
def create_new_resource(resource: schemas.ResourceCreate, db: Session = Depends(get_db)):
    return crud.create_resource(db=db, resource=resource)

@router.get("/resources", response_model=List[schemas.Resource], summary="List all resources")
def read_all_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_resources(db, skip=skip, limit=limit)

# --- إدارة الأدوار الوظيفية ---
@router.post("/job-roles", response_model=schemas.JobRole, status_code=status.HTTP_201_CREATED, summary="Create a new job role")
def create_new_job_role(job_role: schemas.JobRoleCreate, db: Session = Depends(get_db)):
    if crud.get_job_role_by_title(db, title=job_role.title):
        raise HTTPException(status_code=400, detail="Job role already exists.")
    return crud.create_job_role(db=db, job_role=job_role)

@router.get("/job-roles", response_model=List[schemas.JobRole], summary="List all job roles")
def read_all_job_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_job_roles(db, skip=skip, limit=limit)