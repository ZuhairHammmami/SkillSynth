from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend import models
from backend.database import engine
from backend.routers import auth_router, paths_router
import os
import sys
import uvicorn
from dotenv import load_dotenv

# -------------------------------
# تحميل متغيرات البيئة
# -------------------------------
load_dotenv()

# -------------------------------
# إصلاح المسار لضمان رؤية الموديولات
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.dirname(BASE_DIR)
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)
os.environ["PYTHONPATH"] = SRC_PATH

# -------------------------------
# إعداد قاعدة البيانات
# -------------------------------
models.Base.metadata.create_all(bind=engine)

# -------------------------------
# إنشاء تطبيق FastAPI
# -------------------------------
app = FastAPI(title="SkillSynth API")

origins = ["http://localhost", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# إضافة الروترات
# -------------------------------
app.include_router(auth_router.router, prefix="/api/auth")
app.include_router(paths_router.router, prefix="/api")

# -------------------------------
# Endpoint افتراضي
# -------------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to SkillSynth API"}

# -------------------------------
# تشغيل الخادم
# -------------------------------
if __name__ == "__main__":
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    RELOAD = os.getenv("MODE", "prod").lower() == "dev"

    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info"
    )
