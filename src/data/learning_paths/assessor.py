

import json
import os

# --- التغيير 1: استيراد أدوات قاعدة البيانات بدلاً من مسار rules.json ---
from .db_connector import fetch_skills_for_job_role

# لم نعد بحاجة إلى RULES_PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSESSMENTS_PATH = os.path.join(BASE_DIR, 'assessments.json')


def run_assessment(goal, user_answers):
    """
    يقوم بتشغيل تقييم للمستخدم بناءً على هدفه الوظيفي (من قاعدة البيانات) وإجاباته.
    """
    # --- التغيير 2: قراءة ملف الأسئلة فقط ---
    try:
        with open(ASSESSMENTS_PATH, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
    except FileNotFoundError:
        return {"error": f"Assessments file not found at: {ASSESSMENTS_PATH}"}

    # --- التغيير 3: تحديد المهارات للاختبار من قاعدة البيانات ---
    # نستدعي الدالة من db_connector لجلب المهارات المرتبطة بالوظيفة
    skills_to_test_data = fetch_skills_for_job_role(goal)
    if not skills_to_test_data:
        return {"error": f"Could not find skills for job role '{goal}' in the database."}
    
    # نستخرج أسماء المهارات فقط من البيانات التي حصلنا عليها
    skills_to_test = [skill['name'].lower() for skill in skills_to_test_data]
    
    skill_levels = {}

    # --- باقي المنطق يبقى كما هو تمامًا ---
    for skill in skills_to_test:
        questions_for_skill = all_questions.get(skill, [])
        if not questions_for_skill:
            skill_levels[skill] = 0
            continue

        correct_count = 0
        total_questions = len(questions_for_skill)

        for question in questions_for_skill:
            question_id = question['id']
            correct_answer_index = question['correct_option_index']
            user_answer_index = user_answers.get(question_id)

            if user_answer_index == correct_answer_index:
                correct_count += 1
        
        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        level = 0
        if score_percentage == 100:
            level = 3
        elif score_percentage >= 50:
            level = 2
        elif score_percentage > 0:
            level = 1
        else:
            level = 0
            
        skill_levels[skill] = level

    return skill_levels
