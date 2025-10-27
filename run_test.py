import json

# هذه هي الطريقة الجديدة لاستيراد الدالة
# نقول لبايثون: "اذهب إلى حزمة data، ثم إلى الحزمة الفرعية learning_paths،
# ومن هناك، من ملف generator، أحضر لي الدالة التي اسمها generate_path"
from data.learning_paths.generator import generate_path

# =========================================================
# هنا يمكنك تغيير المدخلات كما تشاء لاختبار سيناريوهات مختلفة
# =========================================================

# السيناريو الأول: مستخدم مبتدئ يريد تعلم تطوير الواجهات الأمامية
print("--- Running Test Case 1: New Frontend Developer ---")
user_profile_1 = {"html": 0, "css": 0}
user_goal_1 = "frontend_developer"
user_weekly_hours_1 = 10 # يدرس 10 ساعات في الأسبوع
user_preferences_1 = {"format": "video"} # يفضل الفيديوهات

# استدعاء الدالة وطباعة النتيجة
path_1 = generate_path(user_profile_1, user_goal_1, user_weekly_hours_1, user_preferences_1)
print(json.dumps(path_1, indent=2, ensure_ascii=False))
print("\n" + "="*50 + "\n") # لطباعة فاصل

# السيناريو الثاني: مستخدم لديه خبرة في HTML و CSS
print("--- Running Test Case 2: Experienced Frontend Developer ---")
user_profile_2 = {"html": 4, "css": 3, "javascript": 1} # مستواه عالٍ في HTML و CSS
user_goal_2 = "frontend_developer"
user_weekly_hours_2 = 5 # لديه وقت أقل للدراسة
user_preferences_2 = {"format": "article"} # يفضل المقالات

# استدعاء الدالة وطباعة النتيجة
path_2 = generate_path(user_profile_2, user_goal_2, user_weekly_hours_2, user_preferences_2)
print(json.dumps(path_2, indent=2, ensure_ascii=False))
