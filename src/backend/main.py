# src/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field

# لم نعد بحاجة لتعديل المسار، كل شيء يعمل الآن بشكل طبيعي
from backend import models
from backend.database import engine
from backend.routers import auth_router, paths_router

# --- الخطوة 1: إنشاء التطبيق ---
app = FastAPI(title="SkillSynth API")

# --- الخطوة 2: تطبيق CORSMiddleware (الحل الأكثر مرونة) ---

# نستخدم "*" للسماح بأي مصدر. هذا مثالي لمرحلة التطوير.
# في مرحلة الإنتاج، يجب استبدال "*" بقائمة العناوين المحددة.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # السماح بكل أنواع الطلبات
    allow_headers=["*"], # السماح بكل أنواع الهيدرات
)


# --- الخطوة 3: ربط الرواترز ---
# من الأفضل ربط الرواترز بعد تطبيق الـ Middleware
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(paths_router.router, prefix="/api", tags=["Learning Paths"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SkillSynth API"}

# --- الخطوة 4: إنشاء جداول قاعدة البيانات ---
# هذا الأمر آمن لتشغيله عند بدء التشغيل
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)