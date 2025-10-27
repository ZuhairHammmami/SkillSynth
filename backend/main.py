# main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# نستورد كل شيء من ملفاتنا الأخرى
import crud, models, schemas
from database import SessionLocal, engine

# هذا الأمر ينشئ كل الجداول في قاعدة البيانات (بناءً على models.py)
# سيقوم بذلك فقط إذا لم تكن الجداول موجودة
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkillSynth API")

# ==================== Dependency ====================
# هذه دالة خاصة ستوفر لنا جلسة قاعدة بيانات لكل طلب.
# FastAPI سيهتم بفتحها وإغلاقها تلقائياً.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== Endpoints ====================

# 1. Endpoint: إنشاء مستخدم جديد
@app.post("/api/profiles/", response_model=schemas.Profile)
def create_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    db_profile = crud.get_profile_by_email(db, email=profile.email)
    if db_profile:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_profile(db=db, profile=profile)
    
# 2. Endpoint: استرجاع المسارات لمستخدم معين
@app.get("/api/paths/", response_model=List[schemas.Path])
def read_paths_for_user(profile_id: int, db: Session = Depends(get_db)):
    paths = crud.get_paths_by_profile(db, profile_id=profile_id)
    return paths

# 3. Endpoint: توليد مسار جديد (الطلب الرئيسي)
@app.post("/api/generate-path/", response_model=schemas.Path)
def generate_new_path(path_input: schemas.GeneratePathInput, db: Session = Depends(get_db)):
    """
    يستقبل طلب توليد مسار، ويستدعي دالة مولّد وهمية، ويعيد المسار.
    """
    # --- هنا يفترض أن يتم استدعاء المولد الحقيقي ---
    # حالياً، سنقوم بإنشاء بيانات وهمية (Mock Data)
    print(f"Generating path for profile {path_input.profile_id} with goal: {path_input.goal}")

    # دالة مولد وهمية
    def mock_generator(goal: str):
        # هذا يحاكي منطق القواعد البسيط الذي طلبته
        if "python" in goal.lower():
            return {
                "title": f"مسار تعلم Python: {goal}",
                "description": "خطة شاملة لتعلم بايثون من الصفر.",
                "steps": [
                    {"step_number": 1, "title": "الأساسيات والمتغيرات"},
                    {"step_number": 2, "title": "هياكل البيانات (List, Dict)"},
                    {"step_number": 3, "title": "البرمجة كائنية التوجه (OOP)"}
                ]
            }
        else:
            return {
                "title": f"مسار عام: {goal}",
                "description": "خطة عامة لتحقيق هدفك.",
                "steps": [
                    {"step_number": 1, "title": "مقدمة وبحث"},
                    {"step_number": 2, "title": "التطبيق العملي"}
                ]
            }
    
    generated_data = mock_generator(path_input.goal)

    # الآن سنحفظ هذه البيانات في قاعدة البيانات
    # أولاً: ننشئ المسار الرئيسي
    path_to_create = schemas.PathCreate(title=generated_data['title'], description=generated_data['description'])
    db_path = crud.create_path_for_profile(db, path=path_to_create, profile_id=path_input.profile_id)
    
    # ثانياً: ننشئ الخطوات ونربطها بالمسار
    for step_data in generated_data['steps']:
        db_step = models.PathStep(**step_data, path_id=db_path.id)
        db.add(db_step)
    
    db.commit()
    db.refresh(db_path)
    
    return db_path

# 4. Endpoint: حفظ مسار (هذا Endpoint إضافي إذا أردت فصل التوليد عن الحفظ)
# لكن تم دمجه في generate-path لتبسيط الطلب
@app.post("/api/paths/", response_model=schemas.Path)
def create_path(profile_id: int, path: schemas.PathCreate, db: Session = Depends(get_db)):
    return crud.create_path_for_profile(db=db, path=path, profile_id=profile_id)