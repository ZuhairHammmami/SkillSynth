# src/backend/routers/assessments_router.py

import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas
from backend.database import get_db

router = APIRouter()

# تحديد مسار ثابت لملف بيانات التقييمات
# نفترض أننا نشغل الكود من المجلد الرئيسي للمشروع
ASSESSMENTS_FILE_PATH = Path("src/data/learning_paths/assessments.json")

@router.get("/assessments/{job_role_title}", response_model=List[schemas.AssessmentQuestionResponse])
def get_assessment_questions_for_role(job_role_title: str, db: Session = Depends(get_db)):
    """
    يجلب أسئلة اختبار تحديد المستوى بناءً على الهدف الوظيفي.
    1. يحدد المهارات المطلوبة للدور الوظيفي من قاعدة البيانات.
    2. يقرأ بنك الأسئلة من ملف assessments.json.
    3. يفلتر الأسئلة التي تنتمي إلى المهارات المطلوبة.
    4. يعيد الأسئلة المجهزة (بدون الإجابات) للواجهة الأمامية.
    """
    try:
        # 1. ابحث عن الدور الوظيفي في قاعدة البيانات
        job_role = db.query(models.JobRole).filter(models.JobRole.title == job_role_title).first()
        if not job_role:
            raise HTTPException(status_code=404, detail=f"Job role '{job_role_title}' not found.")

        # 2. احصل على أسماء المهارات المطلوبة لهذا الدور
        # بفضل علاقات SQLAlchemy، يمكننا الوصول إليها مباشرة
        required_skills = {skill.name.lower() for skill in job_role.skills}
        if not required_skills:
            # إذا كان الدور الوظيفي موجودًا ولكن لا توجد مهارات مرتبطة به
            return []

        # 3. اقرأ بنك الأسئلة بالكامل
        if not ASSESSMENTS_FILE_PATH.exists():
            raise HTTPException(status_code=500, detail="Assessments data file not found on the server.")
        
        with open(ASSESSMENTS_FILE_PATH, 'r', encoding='utf-8') as f:
            all_questions_by_skill = json.load(f)

        # 4. فلترة الأسئلة وتجهيزها
        questions_to_return = []
        for skill_name, questions in all_questions_by_skill.items():
            if skill_name.lower() in required_skills:
                for question in questions:
                    # تأكد من أن السؤال يحتوي على كل الحقول المطلوبة قبل إضافته
                    if all(k in question for k in ["id", "text", "options"]):
                        questions_to_return.append({
                            "id": question["id"],
                            "skill": skill_name.capitalize(),
                            "text": question["text"],
                            "options": question["options"]
                        })
        
        return questions_to_return

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching assessment questions: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching assessment questions."
        )