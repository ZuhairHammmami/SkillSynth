# src/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import models
from backend.database import engine
from backend.routers import auth_router, paths_router

# 1. إنشاء التطبيق
app = FastAPI(title="SkillSynth API")

# 2. تطبيق CORSMiddleware (الحل الأكثر مرونة للتطوير)
# نستخدم "*" للسماح بالطلبات من أي مصدر. هذا مثالي لمرحلة التطوير وسيحل المشكلة فورًا.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # السماح بكل أنواع الطلبات (GET, POST, etc.)
    allow_headers=["*"], # السماح بكل أنواع الهيدرات
)

# 3. ربط الروترات
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(paths_router.router, prefix="/api", tags=["Paths"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SkillSynth API"}

# 4. إنشاء جداول قاعدة البيانات عند بدء التشغيل
@app.on_event("startup")
def on_startup():
    # هذا يضمن أن الجداول يتم إنشاؤها مرة واحدة فقط عند بدء تشغيل التطبيق
    models.Base.metadata.create_all(bind=engine)