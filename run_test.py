# =================== ابدأ النسخ من هنا (الملف النهائي لـ run_test.py) ===================

import json

# --- 1. استيراد كل الأدوات التي نحتاجها ---
# نستورد الآن دالة توليد المسار ودالة التقييم
from data.learning_paths.generator import generate_path
from data.learning_paths.assessor import run_assessment


def run_complete_journey(title, goal, user_answers, weekly_hours, preferences):
    """
    دالة مساعدة تقوم بتشغيل رحلة المستخدم الكاملة:
    تقييم ثم توليد مسار.
    """
    print(f"--- {title} ---")
    
    # --- الخطوة الأولى: تشغيل اختبار تحديد المستوى ---
    print("Step 1: Running Assessment...")
    # نستدعي دالة التقييم ونمرر لها هدف المستخدم وإجاباته
    assessed_profile = run_assessment(goal, user_answers)
    
    # نطبع ملف المهارات (Profile) الذي تم إنشاؤه
    print("Assessment Result (Generated Profile):")
    print(json.dumps(assessed_profile, indent=2))
    print("-" * 20)

    # التحقق من وجود خطأ أثناء التقييم
    if "error" in assessed_profile:
        print("Could not generate path due to an assessment error.")
        print("\n" + "="*50 + "\n")
        return

    # --- الخطوة الثانية: توليد المسار التعليمي المخصص ---
    print("Step 2: Generating Personalized Path...")
    # نستخدم الـ profile الناتج من التقييم كمدخل لدالة توليد المسار
    path = generate_path(assessed_profile, goal, weekly_hours, preferences)
    
    # نطبع المسار النهائي
    print("Generated Path:")
    print(json.dumps(path, indent=2, ensure_ascii=False))
    print("\n" + "="*50 + "\n")


# --- سيناريو الاختبار الأول: مستخدم مبتدئ يجيب على سؤال واحد فقط بشكل صحيح ---
# نتوقع أن يكون مستواه 1 في HTML، و 0 في الباقي. المسار يجب أن يحتوي على كل شيء.
print("RUNNING SCENARIO 1: A TRUE BEGINNER")
beginner_answers = {
    "html_q1": 0,  # إجابة صحيحة
    "css_q1": 0,   # إجابة خاطئة
    "js_q1": 1     # إجابة خاطئة
}
run_complete_journey(
    title="Beginner User Journey",
    goal="frontend_developer",
    user_answers=beginner_answers,
    weekly_hours=10,
    preferences={"format": "video", "is_free": True}
)


# --- سيناريو الاختبار الثاني: مستخدم يتقن HTML و CSS بالكامل ---
# نتوقع أن يكون مستواه 3 في HTML و CSS. المسار يجب أن يتخطى هاتين المهارتين.
print("RUNNING SCENARIO 2: A USER WHO KNOWS HTML/CSS")
expert_answers = {
    # HTML: كل الإجابات صحيحة
    "html_q1": 0,
    "html_q2": 2,
    "html_q3": 1,
    # CSS: كل الإجابات صحيحة
    "css_q1": 1,
    "css_q2": 1,
    # JavaScript: إجابة واحدة صحيحة
    "js_q1": 2,
    "js_q2": 2 # إجابة خاطئة
}
run_complete_journey(
    title="Experienced User Journey",
    goal="frontend_developer",
    user_answers=expert_answers,
    weekly_hours=8,
    preferences={"format": "article", "is_free": True}
)

# =================== انتهى النسخ هنا ===================