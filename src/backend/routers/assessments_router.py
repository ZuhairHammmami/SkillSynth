# src/backend/routers/assessments_router.py

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path

# استيراد الوحدات الضرورية
from backend import crud, models, schemas, auth
from backend.database import get_db

# استيراد وحدات الذكاء الاصطناعي الجديدة
from data.learning_paths.assessor import run_assessment
from data.learning_paths.generator import generate_path

router = APIRouter()

# تحديد مسار ملف بيانات التقييمات
ASSESSMENTS_FILE_PATH = Path("src/data/learning_paths/assessments.json")


# --- المهمة الأولى: مزود الأسئلة ---
@router.get("/assessments/{goal}")
def get_assessment_questions(goal: str):
    """
    يقرأ بنك الأسئلة ويعيد الأسئلة المتعلقة بهدف معين، بدون الإجابات.
    """
    if not ASSESSMENTS_FILE_PATH.exists():
        raise HTTPException(status_code=500, detail="Assessments file not found.")

    with open(ASSESSMENTS_FILE_PATH, 'r', encoding='utf-8') as f:
        all_assessments = json.load(f)

    if goal not in all_assessments:
        raise HTTPException(status_code=404, detail=f"Assessment for goal '{goal}' not found.")

    questions_for_goal = all_assessments[goal]

    # معالجة الأسئلة لإزالة الإجابات قبل إرسالها
    sanitized_questions = []
    for q in questions_for_goal:
        sanitized_questions.append({
            "id": q["id"],
            "text": q["text"],
            "options": q["options"]
        })

    return sanitized_questions


# --- المهمة الثانية: مصحح الإجابات ومولد المسارات ---
@router.post("/assessments/submit", response_model=schemas.Path)
def submit_assessment_and_generate_path(
    assessment_data: schemas.AssessmentSubmit, # استخدم نموذج Pydantic الذي ستنشئه
    db: Session = Depends(get_db),
    current_user: models.Profile = Depends(auth.get_current_user)
):
    """
    1. يستقبل إجابات المستخدم.
    2. يستدعي 'run_assessment' لحساب بروفايل المهارات.
    3. (مستقبلاً) يحفظ البروفايل في قاعدة البيانات.
    4. يستدعي 'generate_path' لإنشاء مسار مخصص.
    5. يحفظ المسار ويعيده.
    """
    # 1. حساب بروفايل المهارات
    skill_profile = run_assessment(
        goal=assessment_data.goal,
        user_answers=assessment_data.user_answers.answers
    )

    # TODO (مهمة مستقبلية): حفظ skill_profile في جدول 'profiles' للمستخدم current_user

    # 2. توليد المسار باستخدام البروفايل الدقيق
    # (هنا نفترض أن weekly_hours و preferences تأتي من مكان آخر أو لها قيم افتراضية)
    generated_data = generate_path(
        profile=skill_profile,
        goal=assessment_data.goal,
        weekly_hours=10, # قيمة افتراضية مؤقتة
        preferences={}    # قيمة افتراضية مؤقتة
    )

    if "error" in generated_data:
        raise HTTPException(status_code=400, detail=generated_data["error"])

    # 3. حفظ المسار في قاعدة البيانات (نفس المنطق من paths_router)
    # ... (انسخ والصق منطق حفظ المسار والخطوات هنا) ...
    
    # ... (بعد الحفظ) ...
    # return db_path
    pass # للتوضيح فقط، يجب إكمال المنطق هنا