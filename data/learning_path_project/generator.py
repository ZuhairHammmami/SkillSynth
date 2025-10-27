import json

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
    # 1. قراءة قواعد المسارات من ملف JSON
    with open('rules.json', 'r', encoding='utf-8') as f:
        rules = json.load(f)

    # 2. قراءة الموارد المتاحة من ملف JSON
    with open('resources.json', 'r', encoding='utf-8') as f:
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