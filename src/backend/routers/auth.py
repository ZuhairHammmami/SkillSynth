"""Auth router — register, login, profile and password lifecycle.

Wires the /api/auth surface to services/auth_service.py (Task 2). Every
endpoint maps one service call and documents the frontend hook that
consumes it (useAuthApi.ts). Login stays form-encoded for wire compat.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dto.auth import (
    PasswordChange, ProfileOut, ProfileUpdate, RegisterInput,
    ResetConfirm, ResetRequest, Token,
)
from backend.limiter import limiter
from backend.policies.auth_policy import get_current_user
from backend.services import auth_service, settings_schema

router = APIRouter()


@router.post("/register", response_model=ProfileOut)
@limiter.limit("5/minute")
def register(request: Request, data: RegisterInput, db: Session = Depends(get_db)):
    """Create a student account; 403 when registration is disabled.

    Gates on the live registration_enabled flag (read per request), then
    calls auth_service.register; consumed by useAuthApi.useAuth()
    registerMutation on the register page."""
    if not settings_schema.get_runtime_flag("registration_enabled"):
        raise HTTPException(status_code=403,
                            detail="Registration is currently disabled")
    user, error = auth_service.register(db, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return auth_service.build_profile_out(db, user)


@router.post("/token", response_model=Token)
@limiter.limit("10/minute")
def login_for_access_token(request: Request, db: Session = Depends(get_db),
                           form: OAuth2PasswordRequestForm = Depends()):
    """Form-encoded login (username/password). Calls
    auth_service.authenticate; consumed by useAuthApi.useAuth().loginMutation."""
    ip = request.client.host if request.client else None
    user, error = auth_service.authenticate(db, form.username, form.password, ip)
    if error:
        status = 429 if error.startswith("Account locked") else 401
        raise HTTPException(status_code=status, detail=error)
    token = auth_service.create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=ProfileOut)
def read_current_user(db: Session = Depends(get_db),
                      current_user=Depends(get_current_user)):
    """Return the signed-in profile with its skill_profile map. Calls
    auth_service.build_profile_out; consumed by useAuthApi.useProfile()."""
    return auth_service.build_profile_out(db, current_user)


@router.put("/me", response_model=ProfileOut)
def update_current_user(data: ProfileUpdate, db: Session = Depends(get_db),
                        current_user=Depends(get_current_user)):
    """Apply ProfileUpdate fields. Calls auth_service.update_profile;
    consumed by useAuthApi.useUpdateProfile()."""
    updated = auth_service.update_profile(db, current_user.id,
                                          data.model_dump(exclude_unset=True))
    return auth_service.build_profile_out(db, updated)


@router.post("/change-password")
def change_current_user_password(data: PasswordChange, db: Session = Depends(get_db),
                                 current_user=Depends(get_current_user)):
    """Rotate the password after verifying current. Calls
    auth_service.change_password; consumed by useAuthApi.useChangePassword()."""
    ok, message = auth_service.change_password(
        db, current_user, data.current_password, data.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, data: ResetRequest,
                    db: Session = Depends(get_db)):
    """Issue a stateless reset token (always 200). Calls
    auth_service.request_reset; consumed by useAuthApi.useForgotPassword()."""
    return auth_service.request_reset(db, data.email)


@router.post("/reset-password")
@limiter.limit("3/minute")
def reset_password(request: Request, data: ResetConfirm,
                   db: Session = Depends(get_db)):
    """Consume a reset token and set a new password. Calls
    auth_service.reset_password; consumed by useAuthApi.useResetPassword()."""
    ok, message = auth_service.reset_password(db, data.token, data.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@router.post("/sse-token")
def get_sse_token(current_user=Depends(get_current_user)):
    """Issue a 5-minute SSE stream token ({token, expires_in: 300}). Calls
    auth_service.create_sse_token; consumed by useSSE.ts EventSource URL."""
    return {"token": auth_service.create_sse_token(current_user.id),
            "expires_in": 300}
