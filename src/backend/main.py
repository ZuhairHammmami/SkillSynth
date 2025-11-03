# src/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import models
from backend.database import engine
from backend.routers import auth_router, paths_router

app = FastAPI(title="SkillSynth API")

# --- هذا هو التعديل الوحيد المطلوب ---
# قائمة المصادر المسموح لها بإرسال الطلبات

origins = [
    "http://localhost:3000",  # هذا هو عنوان تطبيق الفرونت اند المحلي
    "http://localhost:8000",  # للسماح لصفحة /docs بالعمل
    "http://127.0.0.1:8000", # عنوان بديل لـ localhost
    # في المستقبل، سنضيف هنا رابط الفرونت اند بعد نشره على الإنترنت
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ربط الرواترز
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(paths_router.router, prefix="/api", tags=["Paths"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SkillSynth API"}

# إنشاء جداول قاعدة البيانات عند بدء التشغيل
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)