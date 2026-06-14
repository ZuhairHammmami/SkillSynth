# example_run.py
import json
from generator import generate_path

# مدخلات المستخدم
user_profile = {"javascript": 1, "react": 0, "html": 3} # مستوى HTML مرتفع، سيتم تخطيه
user_goal = "backend_developer"
user_weekly_hours = 8
user_preferences = {"format": "video"}

# استدعاء الدالة
generated_path = generate_path(user_profile, user_goal, user_weekly_hours, user_preferences)

# طباعة النتيجة بصيغة JSON منسقة
print(json.dumps(generated_path, indent=2, ensure_ascii=False))