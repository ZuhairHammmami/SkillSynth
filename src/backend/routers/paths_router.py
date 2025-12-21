# src/backend/routers/paths_router.py

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import crud, models, schemas, auth
from backend.database import get_db
from data.learning_paths.assessor import run_assessment
from data.learning_paths.generator import generate_path

router = APIRouter()

# --- دالة مساعدة جديدة للتعامل مع الموارد ---
def get_or_create_resource(db: Session, resource_data: dict) -> models.Resource | None:
    """
    تبحث عن مورد بالـ URL. إذا لم تجده، تقوم بإنشائه.
    تعيد كائن المورد من قاعدة البيانات.
    """
    if not resource_data or not resource_data.get('url'):
        return None

    # ابحث عن المورد أولاً
    db_resource = db.query(models.Resource).filter(models.Resource.url == resource_data['url']).first()
    
    if db_resource:
        return db_resource
    
    # إذا لم يكن موجودًا، قم بإنشائه
    new_resource_data = schemas.ResourceCreate(
        title=resource_data.get('title', 'Untitled Resource'),
        url=resource_data['url'],
        type=resource_data.get('type', 'article'),
        is_free=resource_data.get('is_free', True),
        is_official=resource_data.get('is_official', False),
        author_or_platform=resource_data.get('author_or_platform')
    )
    return crud.create_resource(db, resource=new_resource_data)


@router.post("/generate-path/", response_model=schemas.Path)
def generate_new_path(
    path_input: schemas.GeneratePathInput,
    db: Session = Depends(get_db),
    current_user: models.Profile = Depends(auth.get_current_user)
):
    """
    ينسق العملية الكاملة لتوليد مسار مخصص بناءً على "المرشد الذكي".
    """
    try:
        # 1. استدعاء وحدة التقييم (يبقى كما هو)
        skill_profile = run_assessment(goal=path_input.goal, user_answers=path_input.answers)
        if "error" in skill_profile:
            raise HTTPException(status_code=400, detail=f"Assessment error: {skill_profile['error']}")
        
        # 2. حفظ بروفايل المهارات (يبقى كما هو)
        crud.update_profile(db, profile_id=current_user.id, profile_data=schemas.ProfileUpdate(skill_profile=skill_profile))

        # 3. استدعاء مولد المسارات (يبقى كما هو)
        goal_key = path_input.goal.lower().replace(" ", "_")
        generated_data = generate_path(
            profile=skill_profile,
            goal=goal_key,
            weekly_hours=path_input.weekly_hours,
            preferences=path_input.preferences.dict()
        )
        if "error" in generated_data:
            raise HTTPException(status_code=400, detail=f"Path generation error: {generated_data['error']}")
        
        # 4. حفظ المسار بالكامل في قاعدة البيانات (المنطق المحدث)
        db_path = crud.create_path_for_profile(
            db, 
            title=generated_data.get('path_title', 'Generated Path'), 
            description=generated_data.get('intro_message', ''), # <-- استخدام intro_message
            profile_id=current_user.id
        )
        
        for step_data in generated_data.get('steps', []):
            # إنشاء الخطوة
            db_step = models.PathStep(
                step_number=step_data.get('index'),
                title=step_data.get('title'),
                content=step_data.get('description'), # استخدام لوصف الخطوة
                path_id=db_path.id
            )
            db.add(db_step)
            db.flush() # flush للحصول على id الخطوة قبل commit

            # --- معالجة الموارد الرئيسية والإضافية ---
            main_resource_obj = get_or_create_resource(db, step_data.get('main_resource'))
            if main_resource_obj:
                db_step.resources.append(main_resource_obj)

            for res_data in step_data.get('additional_resources', []):
                additional_res_obj = get_or_create_resource(db, res_data)
                if additional_res_obj:
                    db_step.resources.append(additional_res_obj)
            # --- نهاية منطق الموارد ---

        db.commit()
        db.refresh(db_path)
        
        return db_path

    except Exception as e:
        print(f"!!! CRITICAL ERROR in generate_path endpoint: {e}")
        db.rollback() 
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


@router.get("/paths/{path_id}", response_model=schemas.Path)
def read_single_path(path_id: int, db: Session = Depends(get_db), current_user: models.Profile = Depends(auth.get_current_user)):
    db_path = crud.get_path_by_id(db, path_id=path_id, profile_id=current_user.id)
    if db_path is None:
        raise HTTPException(status_code=404, detail="Path not found")
    return db_path


@router.get("/paths/", response_model=List[schemas.Path])
def read_paths_for_current_user(
    db: Session = Depends(get_db), 
    current_user: models.Profile = Depends(auth.get_current_user)
):
    return crud.get_paths_by_profile(db, profile_id=current_user.id)