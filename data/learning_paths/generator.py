# =================== ابدأ النسخ من هنا ===================

import json
import os # <-- التغيير الأول: لقد استوردنا مكتبة جديدة اسمها "os"

# --- هذا هو الجزء الجديد والمهم جدًا ---
# لقد أضفنا هذا الجزء لنجعل الكود يعرف مكانه على الكمبيوتر
# __file__ هو متغير خاص في بايثون يعني "هذا الملف الذي أعمل فيه الآن"
# os.path.abspath(__file__) يحول اسم الملف إلى مسار كامل (مثال: C:\Users\YourName\SKILLS\data\learning_paths\generator.py)
# os.path.dirname(...) يأخذ المسار الكامل ويعطينا فقط اسم المجلد الذي يحتوي على الملف
# النتيجة: BASE_DIR سيحتوي دائمًا على مسار المجلد "learning_paths"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# الآن، سنقوم بإنشاء مسارات كاملة لملفاتنا باستخدام المسار الأساسي الذي حددناه
# os.path.join هو الطريقة الصحيحة لدمج المسارات مع أسماء الملفات
RULES_PATH = os.path.join(BASE_DIR, 'rules.json')
RESOURCES_PATH = os.path.join(BASE_DIR, 'resources.json')
# ----------------------------------------------------


def generate_path(profile, goal, weekly_hours, preferences):
    """
    توليد مسار تعليمي مخصص بناءً على ملفات القواعد والمستخدم.

    Args:
        profile (dict): قاموس يحتوي على مهارات المستخدم ومستواها.
        goal (str): الهدف التعليمي للمستخدم (مفتاح في ملف القواعد).
        weekly_hours (int): عدد الساعات الأسبوعية التي يخصصها المستخدم للدراسة.
        preferences (dict): تفضيلات المستخدم مثل صيغة المحتوى.

    Returns:
        dict: قاموس بصيغة JSON يحتوي على المسار التعليمي المقترح.
    """
    # التغيير الثاني: سنستخدم الآن المسارات الكاملة التي أنشأناها في الأعلى
    # 1. قراءة قواعد المسارات من ملف JSON
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        rules = json.load(f)

    # التغيير الثالث: نفس الشيء هنا لملف الموارد
    # 2. قراءة الموارد المتاحة من ملف JSON
    with open(RESOURCES_PATH, 'r', encoding='utf-8') as f:
        all_resources = json.load(f)

    # التحقق من وجود الهدف في القواعد
    if goal not in rules:
        return {"error": "Goal not found in rules."}

    goal_steps = rules[goal]
    path_steps = []
    total_estimated_hours = 0
    step_index = 1

    # 3. مقارنة مهارات المستخدم وتحديد الخطوات
    for step in goal_steps:
        skill_name = step["skill"].lower()
        required_level = 3  # المستوى المطلوب لتخطي خطوة

        # تحقق مما إذا كان يجب تخطي الخطوة
        if profile.get(skill_name, 0) >= required_level:
            continue  # تخطى هذه الخطوة وانتقل للتالية

        # 4. اختيار الموارد المناسبة
        resource_tag = step["tag"]
        preferred_format = preferences.get("format", "any") # 'any' كقيمة افتراضية
        
        # فلترة الموارد بناءً على الوسم (tag) والتفضيل (format)
        candidate_resources = [
            res for res in all_resources.get(resource_tag, [])
            if preferred_format == "any" or res.get("format") == preferred_format
        ]
        
        # اختيار المورد الأول المتاح (يمكن تطوير هذا المنطق لاحقًا)
        selected_resource = candidate_resources[0] if candidate_resources else None

        path_steps.append({
            "index": step_index,
            "title": f"{step['skill']} basics",
            "estimated_hours": step["hours"],
            "resource": selected_resource
        })
        total_estimated_hours += step["hours"]
        step_index += 1
    
    # 5. تعديل المدة الزمنية بناءً على الساعات الأسبوعية
    total_weeks = round(total_estimated_hours / weekly_hours) if weekly_hours > 0 else 0

    # 6. بناء النتيجة النهائية
    result = {
        "path_title": f"{goal.replace('_', ' ').title()} - {total_weeks}w",
        "steps": path_steps,
        "metadata": {
            "method": "rule-based-v1",
            "total_estimated_hours": total_estimated_hours,
            "estimated_weeks": total_weeks,
            "user_preferences": preferences
        }
    }

    return result

# =================== انتهى النسخ هنا ===================