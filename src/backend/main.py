# src/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend import models
from backend.database import engine
from backend.routers import (
    auth_router,
    paths_router,
    options_router,
    assessments_router,
    progress_router,
    admin_router,
)

app = FastAPI(title="SkillSynth API")

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ربط الروترات ببادئة موحدة
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(paths_router.router, prefix="/api", tags=["Paths"])
app.include_router(options_router.router, prefix="/api", tags=["Wizard Options"])
app.include_router(assessments_router.router, prefix="/api", tags=["Assessments"])
app.include_router(progress_router.router, prefix="/api", tags=["Progress Tracking"])

# هنا نحدد البادئة للأدمن مرة واحدة فقط
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin Dashboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SkillSynth API"}

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)

    