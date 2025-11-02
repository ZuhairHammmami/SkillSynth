from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from backend import crud, schemas, auth
from backend.database import get_db

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=schemas.Profile)
def register_user(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    db_profile = crud.get_profile_by_email(db, email=profile.email)
    if db_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
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
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
@router.get("/users/me", response_model=schemas.Profile)
def read_users_me(current_user: models.Profile = Depends(auth.get_current_user)):
    """
    نقطة نهاية محمية تعيد بيانات المستخدم المسجل دخوله حاليًا.
    الفرونت اند سيستدعي هذه النقطة بعد تسجيل الدخول مباشرة 
    لعرض اسم المستخدم في الشريط العلوي.
    """
    return current_user