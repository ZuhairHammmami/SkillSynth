from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend import crud, models, schemas, auth
from backend.database import get_db
from data.learning_paths.generator import generate_path

router = APIRouter(tags=["Learning Paths"])

def get_current_user(db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)) -> models.Profile:
    """التحقق من المستخدم الحالي من خلال JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth.decode_access_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = crud.get_profile_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@router.post("/generate-path/", response_model=schemas.Path)
def generate_new_path(path_input: schemas.GeneratePathInput, db: Session = Depends(get_db), current_user: models.Profile = Depends(get_current_user)):
    user_skill_profile = path_input.preferences.get("skills", {})

    generated_data = generate_path(
        user_profile=user_skill_profile,
        user_goal=path_input.goal,
        user_weekly_hours=path_input.weekly_hours,
        user_preferences=path_input.preferences
    )

    db_path = crud.create_path_for_profile(
        db, 
        title=generated_data.get('title', 'Generated Path'), 
        description=generated_data.get('description', ''),
        profile_id=current_user.id
    )

    for step_data in generated_data.get('steps', []):
        db_step = models.PathStep(
            step_number=step_data.get('step_number'),
            title=step_data.get('title'),
            content=step_data.get('content'),
            path_id=db_path.id
        )
        db.add(db_step)

    db.commit()
    db.refresh(db_path)
    return db_path

@router.get("/paths/", response_model=List[schemas.Path])
def read_paths_for_current_user(db: Session = Depends(get_db), current_user: models.Profile = Depends(get_current_user)):
    return crud.get_paths_by_profile(db, profile_id=current_user.id)
