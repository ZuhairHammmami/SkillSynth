# src/backend/auth.py
import os # <-- هذا هو السطر الجديد والمهم
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# إعداد سياق التشفير لكلمات المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- الإعدادات الأمنية ---
# هام: في تطبيق حقيقي، يجب قراءة هذا المفتاح من متغيرات البيئة
SECRET_KEY = os.getenv("SECRET_KEY", "a-secure-default-secret-key-for-development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # مدة صلاحية التوكن ساعة واحدة

# --- مخطط OAuth2 ---
# هذا المخطط هو ما تستخدمه FastAPI لعرض قفل الأمان في واجهة /docs
# الرابط "tokenUrl" يجب أن يكون نسبيًا لمكان الروتر (بدون / في البداية)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """يتحقق من تطابق كلمة المرور المدخلة مع النسخة المشفرة في قاعدة البيانات."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """يقوم بتشفير (hashing) كلمة المرور قبل حفظها."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """ينشئ توكن JWT جديد."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt