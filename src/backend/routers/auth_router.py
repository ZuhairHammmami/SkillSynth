# src/backend/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# --- هذا هو التعديل الوحيد والمهم ---
# لقد أضفنا 'models' إلى قائمة الاستيراد
from backend import crud, schemas, auth, models
from backend.database import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.Profile)
def register_user(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    db_profile = crud.get_profile_by_email(db, email=profile.email)
    if db_profile:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_profile(db=db, profile=profile)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_profile_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.Profile)
def read_users_me(current_user: models.Profile = Depends(auth.get_current_user)):
    # الآن هذا السطر سيعمل لأن 'models' أصبحت معروفة
    return current_user