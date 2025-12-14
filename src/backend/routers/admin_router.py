# src/backend/routers/admin_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend import crud, models, schemas, auth
from backend.database import get_db

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Dashboard"],
    dependencies=[Depends(auth.get_current_admin_user)]
)

# --- التقارير (Reports) ---
@router.get("/dashboard-summary", summary="Get a summary for the admin dashboard")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    [Admin Only] يعيد تقريرًا سريعًا بأعداد الكيانات الرئيسية في النظام.
    """
    total_users = db.query(models.Profile).count()
    total_paths = db.query(models.Path).count()
    total_skills = db.query(models.Skill).count()
    total_resources = db.query(models.Resource).count()
    return {
        "total_users": total_users,
        "total_paths_generated": total_paths,
        "total_skills_managed": total_skills,
        "total_resources_available": total_resources,
    }

# --- إدارة المستخدمين (Profiles Management) ---
@router.get("/profiles/", response_model=List[schemas.Profile], summary="List all user profiles")
def read_all_profiles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    [Admin Only] يعرض قائمة بجميع المستخدمين في النظام.
    """
    profiles = crud.get_profiles(db, skip=skip, limit=limit)
    return profiles

# --- إدارة المهارات (Skills Management) ---
@router.post("/skills/", response_model=schemas.Skill, status_code=status.HTTP_201_CREATED)
def create_new_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    if crud.get_skill_by_name(db, name=skill.name):
        raise HTTPException(status_code=400, detail="Skill already exists.")
    return crud.create_skill(db=db, skill=skill)

@router.get("/skills/", response_model=List[schemas.Skill])
def read_all_skills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_skills(db, skip=skip, limit=limit)

# --- إدارة التصنيفات (Categories Management) ---
@router.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_new_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if crud.get_category_by_name(db, name=category.name):
        raise HTTPException(status_code=400, detail="Category already exists.")
    return crud.create_category(db=db, category=category)

@router.get("/categories/", response_model=List[schemas.Category])
def read_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

# --- إدارة المصادر (Resources Management) ---
@router.post("/resources/", response_model=schemas.Resource, status_code=status.HTTP_201_CREATED)
def create_new_resource(resource: schemas.ResourceCreate, db: Session = Depends(get_db)):
    return crud.create_resource(db=db, resource=resource)

@router.get("/resources/", response_model=List[schemas.Resource])
def read_all_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_resources(db, skip=skip, limit=limit)

# --- إدارة الأدوار الوظيفية (JobRoles Management) ---
@router.post("/job-roles/", response_model=schemas.JobRole, status_code=status.HTTP_201_CREATED)
def create_new_job_role(job_role: schemas.JobRoleCreate, db: Session = Depends(get_db)):
    if crud.get_job_role_by_title(db, title=job_role.title):
        raise HTTPException(status_code=400, detail="Job role already exists.")
    return crud.create_job_role(db=db, job_role=job_role)

@router.get("/job-roles/", response_model=List[schemas.JobRole])
def read_all_job_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_job_roles(db, skip=skip, limit=limit)