# =================== ابدأ النسخ من هنا (ملف الاختبار النهائي والشامل) ===================

import json
from data.learning_paths.generator import generate_path

def run_test_case(title, profile, goal, weekly_hours, preferences):
    """دالة مساعدة لطباعة الاختبارات بشكل منظم"""
    print(f"--- {title} ---")
    path = generate_path(profile, goal, weekly_hours, preferences)
    print(json.dumps(path, indent=2, ensure_ascii=False))
    print("\n" + "="*50 + "\n")

# --- الاختبار الأول: الحالة القياسية - مستخدم جديد يريد فيديوهات مجانية بالإنجليزية ---
run_test_case(
    title="Test Case 1: New Dev, Free English Videos",
    profile={"html": 0, "css": 0},
    goal="frontend_developer",
    weekly_hours=10,
    preferences={"format": "video", "language": "en", "is_free": True}
)

# --- الاختبار الثاني: اختبار تخطي المهارات - مستخدم خبير يريد مقالات مجانية ---
run_test_case(
    title="Test Case 2: Experienced Dev, Free English Articles",
    profile={"html": 4, "css": 3, "javascript": 1},
    goal="frontend_developer",
    weekly_hours=5,
    preferences={"format": "article", "language": "en", "is_free": True}
)

# --- الاختبار الثالث: اختبار تفضيل اللغة والخطة البديلة (Fallback) ---
run_test_case(
    title="Test Case 3: Arabic Preference, Testing Fallback",
    profile={"html": 0},
    goal="frontend_developer",
    weekly_hours=8,
    preferences={"format": "video", "language": "ar", "is_free": True}
)

# --- الاختبار الرابع (جديد): اختبار الأولوية للمصادر الرسمية ---
# هذا المستخدم يفضل المقالات. يجب أن تختار الخوارزمية مقالات MDN/W3Schools
# لأنها تحمل علامة "is_official: true" ولها أولوية أعلى.
run_test_case(
    title="Test Case 4: Prioritizing OFFICIAL Resources",
    profile={"html": 0, "css": 0},
    goal="frontend_developer",
    weekly_hours=7,
    preferences={"format": "article", "language": "en", "is_free": True}
)

# --- الاختبار الخامس (جديد): اختبار طلب المحتوى المدفوع ---
# هذا المستخدم حدد "is_free: false". يجب أن تختار الخوارزمية كورس Udemy المدفوع
# لخطوة React، لأنه المورد الوحيد الذي يطابق هذا الشرط.
run_test_case(
    title="Test Case 5: Requesting PAID Content",
    profile={"react": 0},
    goal="frontend_developer",
    weekly_hours=10,
    preferences={"format": "video", "language": "en", "is_free": False}
)

# =================== انتهى النسخ هنا ===================