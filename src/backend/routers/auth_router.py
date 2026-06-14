# src/backend/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt

# نستورد كل الوحدات التي نحتاجها
from backend import crud, schemas, auth, models, email_service
from backend.database import get_db

router = APIRouter()

# --- نقاط نهاية التسجيل وتسجيل الدخول ---
@router.post("/register", response_model=schemas.Profile, summary="Register a new user")
def register_user(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    db_profile = crud.get_profile_by_email(db, email=profile.email)
    if db_profile:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_profile(db=db, profile=profile)

@router.post("/token", response_model=schemas.Token, summary="Login and get access token")
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

# --- نقاط نهاية إدارة الحساب (للمستخدم المسجل دخوله) ---
@router.get("/users/me", response_model=schemas.Profile, summary="Get current user data")
def read_users_me(current_user: models.Profile = Depends(auth.get_current_user)):
    return current_user

@router.put("/users/me", response_model=schemas.Profile, summary="Update current user data")
def update_current_user(
    profile_data: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.Profile = Depends(auth.get_current_user)
):
    return crud.update_profile(db, profile_id=current_user.id, profile_data=profile_data)

# تم نقل هذه النقطة إلى هنا لتكون تحت /api/auth
@router.post("/change-password", summary="Change current user's password")
def change_current_user_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.Profile = Depends(auth.get_current_user)
):
    if not auth.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    new_password_hash = auth.get_password_hash(password_data.new_password)
    crud.update_password(db, profile_id=current_user.id, new_password_hash=new_password_hash)
    
    return {"message": "Password updated successfully"}

# --- نقاط نهاية استعادة كلمة المرور (للمستخدم الذي نسي كلمة المرور) ---
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/request-password-reset", summary="Request a password reset link")
def request_password_reset(email_data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_profile_by_email(db, email=email_data.email)
    if user:
        reset_token = auth.create_password_reset_token(email=user.email)
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        email_service.send_password_reset_email(recipient_email=user.email, reset_link=reset_link)
    
    return {"message": "If an account with this email exists, a password reset link has been sent."}

class PasswordReset(BaseModel):
    token: str
    new_password: str

@router.post("/reset-password", summary="Reset user password with a token")
def reset_password_with_token(reset_data: PasswordReset, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(reset_data.token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token has expired or is invalid")

    user = crud.get_profile_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    new_password_hash = auth.get_password_hash(reset_data.new_password)
    crud.update_password(db, profile_id=user.id, new_password_hash=new_password_hash)
    
    return {"message": "Password has been reset successfully."}