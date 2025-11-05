# =================== ابدأ النسخ من هنا (الملف الكامل والنهائي) ===================

import json

# نستورد الدالة التي نحتاجها من مكانها الصحيح.
from data.learning_paths.generator import generate_path

# --- السيناريو الأول: مستخدم مبتدئ (الإنجليزية، فيديو) ---
print("--- Running Test Case 1: New Frontend Developer ---")
user_profile_1 = {"html": 0, "css": 0}
user_goal_1 = "frontend_developer"
user_weekly_hours_1 = 10
user_preferences_1 = {"format": "video"}
path_1 = generate_path(user_profile_1, user_goal_1, user_weekly_hours_1, user_preferences_1)
print(json.dumps(path_1, indent=2, ensure_ascii=False))
print("\n" + "="*50 + "\n")

# --- السيناريو الثاني: مستخدم خبير (الإنجليزية، مقال) ---
print("--- Running Test Case 2: Experienced Frontend Developer ---")
user_profile_2 = {"html": 4, "css": 3, "javascript": 1}
user_goal_2 = "frontend_developer"
user_weekly_hours_2 = 5
user_preferences_2 = {"format": "article"}
path_2 = generate_path(user_profile_2, user_goal_2, user_weekly_hours_2, user_preferences_2)
print(json.dumps(path_2, indent=2, ensure_ascii=False))
print("\n" + "="*50 + "\n")

# --- السيناريو الثالث: مستخدم يفضل العربية (لاختبار الخطة البديلة) ---
print("--- Running Test Case 3: New User with Arabic Preference ---")
user_profile_3 = {"html": 0}
user_goal_3 = "frontend_developer"
user_weekly_hours_3 = 8
user_preferences_3 = {"format": "video", "language": "ar"}
path_3 = generate_path(user_profile_3, user_goal_3, user_weekly_hours_3, user_preferences_3)
print(json.dumps(path_3, indent=2, ensure_ascii=False))

# =================== انتهى النسخ هنا ===================