# =================== ابدأ النسخ من هنا (run_test.py - الإصدار المحدث) ===================

import json

# نستورد الأدوات التي نحتاجها كالمعتاد
from data.learning_paths.generator import generate_path
from data.learning_paths.assessor import run_assessment


def run_complete_journey(title, goal, user_answers, weekly_hours, preferences):
    """
    دالة مساعدة تقوم بتشغيل رحلة المستخدم الكاملة:
    تقييم ثم توليد مسار.
    """
    print(f"--- {title} ---")
    
    print("Step 1: Running Assessment...")
    assessed_profile = run_assessment(goal, user_answers)
    
    print("Assessment Result (Generated Profile):")
    print(json.dumps(assessed_profile, indent=2))
    print("-" * 20)

    if "error" in assessed_profile:
        print("Could not generate path due to an assessment error.")
        print("\n" + "="*50 + "\n")
        return

    print("Step 2: Generating Personalized Path...")
    # نمرر الـ profile الناتج من التقييم إلى دالة توليد المسار
    path = generate_path(assessed_profile, goal, weekly_hours, preferences)
    
    print("Generated Path:")
    print(json.dumps(path, indent=2, ensure_ascii=False))
    print("\n" + "="*50 + "\n")


# --- سيناريو الاختبار الأول: مستخدم مبتدئ ---
print("RUNNING SCENARIO 1: A TRUE BEGINNER")
beginner_answers = {
    "html_q1": 0,
    "css_q1": 0,
    "js_q1": 1
}
run_complete_journey(
    title="Beginner User Journey",
    # --- التغيير هنا ---
    goal="Frontend Developer",  # <-- استخدمنا اسم الوظيفة من قاعدة البيانات
    user_answers=beginner_answers,
    weekly_hours=10,
    preferences={"format": "video", "is_free": True}
)


# --- سيناريو الاختبار الثاني: مستخدم يتقن HTML و CSS ---
print("RUNNING SCENARIO 2: A USER WHO KNOWS HTML/CSS")
expert_answers = {
    "html_q1": 0, "html_q2": 2, "html_q3": 1,
    "css_q1": 1, "css_q2": 1,
    "js_q1": 2, "js_q2": 2
}
run_complete_journey(
    title="Experienced User Journey",
    # --- التغيير هنا ---
    goal="Frontend Developer",  # <-- استخدمنا اسم الوظيفة من قاعدة البيانات
    user_answers=expert_answers,
    weekly_hours=8,
    preferences={"format": "article", "is_free": True}
)

# =================== انتهى النسخ هنا ===================