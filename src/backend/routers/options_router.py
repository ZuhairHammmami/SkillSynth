# src/backend/routers/options_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas
from backend.database import get_db

router = APIRouter()

@router.get("/wizard-options", response_model=schemas.WizardOptionsResponse)
def get_wizard_options(db: Session = Depends(get_db)):
    """
    يجلب كل الخيارات الديناميكية اللازمة لبناء واجهة 'Wizard'.
    - يستعلم عن الأدوار الوظيفية من قاعدة البيانات.
    - يعيد قائمة ثابتة لباقي التفضيلات (يمكن تطويرها لاحقًا).
    """
    try:
        # 1. جلب الأدوار الوظيفية من قاعدة البيانات
        job_roles_query = db.query(models.JobRole.title).order_by(models.JobRole.title).all()
        # تحويل النتيجة من قائمة (tuple) إلى قائمة (string)
        job_roles = [role[0] for role in job_roles_query]

        # 2. تعريف الخيارات الثابتة الأخرى
        # في المستقبل، يمكننا نقل هذه القوائم إلى جداول خاصة في قاعدة البيانات
        # إذا احتجنا لجعلها أكثر ديناميكية.
        preference_options = schemas.WizardPreferencesOptions(
            formats=["any", "video", "article", "course", "book"],
            languages=["en", "ar"]
        )

        # 3. تجميع الاستجابة النهائية وإعادتها
        return schemas.WizardOptionsResponse(
            job_roles=job_roles,
            preferences=preference_options
        )

    except Exception as e:
        # معالجة أي خطأ غير متوقع قد يحدث أثناء الاستعلام من قاعدة البيانات
        print(f"Error fetching wizard options: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while fetching wizard options."
        )