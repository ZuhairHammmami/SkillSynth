# src/backend/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# استيراد النماذج وقاعدة البيانات فقط (تجنبنا استيراد crud لمنع التداخل)
from backend import models
from backend.database import get_db

# إعداد سياق التشفير (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# إعدادات الأمان والتوكن
SECRET_KEY = os.getenv("SECRET_KEY", "a-secure-default-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # جعلناها أسبوعاً لسهولة التطوير

# رابط نقطة النهاية للحصول على التوكن (يستخدمه Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """التحقق من صحة كلمة المرور."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """تشفير كلمة المرور."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """إنشاء رمز وصول (JWT Token)."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_password_reset_token(email: str) -> str:
    """إنشاء توكن خاص لاستعادة كلمة المرور (صلاحية قصيرة)."""
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    استخراج المستخدم الحالي من التوكن.
    يتم حقن هذا الاعتماد في المسارات المحمية.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # استخدام استعلام مباشر هنا بدلاً من crud لتجنب الاستيراد الدائري
    user = db.query(models.Profile).filter(models.Profile.email == email).first()
    
    if user is None:
        raise credentials_exception
    
    return user

def get_current_admin_user(current_user: models.Profile = Depends(get_current_user)):
    """
    حارس إضافي للتأكد من أن المستخدم مسؤول (Admin).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have administrative privileges"
        )
    return current_user