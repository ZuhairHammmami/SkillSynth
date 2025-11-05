

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(BASE_DIR, 'rules.json')
RESOURCES_PATH = os.path.join(BASE_DIR, 'resources.json')


def generate_path(profile, goal, weekly_hours, preferences):
    try:
        with open(RULES_PATH, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        with open(RESOURCES_PATH, 'r', encoding='utf-8') as f:
            all_resources = json.load(f)
    except FileNotFoundError as e:
        return {"error": f"Configuration file not found: {e}"}

    if goal not in rules:
        return {"error": "Goal not found in rules."}

    goal_steps = rules[goal]
    path_steps = []
    total_estimated_hours = 0
    step_index = 1

    for step in goal_steps:
        skill_name = step["skill"].lower()
        required_level = 3

        if profile.get(skill_name, 0) >= required_level:
            continue

        resource_tag = step["tag"]
        all_tagged_resources = all_resources.get(resource_tag, [])

        # --- الجزء الذي تم تطويره: منطق الفلترة والأولوية الجديد ---

        # 1. استخلاص كل تفضيلات المستخدم مع قيم افتراضية
        preferred_language = preferences.get("language", "en")
        preferred_format = preferences.get("format", "any")
        # نفترض أن المستخدم يريد محتوى مجانيًا ما لم يحدد خلاف ذلك
        wants_free = preferences.get("is_free", True)

        # 2. الفلترة الأولية بناءً على التفضيل الأساسي (مجاني/مدفوع)
        available_resources = [res for res in all_tagged_resources if res.get("is_free") == wants_free]

        # 3. منطق البحث بالأولويات (هذا هو العقل الجديد)
        #    سنبحث عن أفضل مورد متاح بناءً على قائمة من الأولويات.
        
        # قائمة الأولويات: من الأفضل إلى الأقل تفضيلاً
        priority_searches = [
            # الحالة المثالية: رسمي، يطابق اللغة والصيغة
            {"is_official": True, "language": preferred_language, "format": preferred_format},
            # رسمي، يطابق اللغة (بأي صيغة)
            {"is_official": True, "language": preferred_language, "format": "any"},
            # غير رسمي، يطابق اللغة والصيغة
            {"is_official": False, "language": preferred_language, "format": preferred_format},
            # غير رسمي، يطابق اللغة (بأي صيغة)
            {"is_official": False, "language": preferred_language, "format": "any"},
            
            # --- خطط بديلة (Fallback) باللغة الإنجليزية ---
            {"is_official": True, "language": "en", "format": preferred_format},
            {"is_official": True, "language": "en", "format": "any"},
            {"is_official": False, "language": "en", "format": preferred_format},
            {"is_official": False, "language": "en", "format": "any"},
        ]

        selected_resource = None
        for search_criteria in priority_searches:
            # نبحث في الموارد المتاحة عن أي مورد يطابق معايير البحث الحالية
            result = [
                res for res in available_resources
                if res.get("is_official") == search_criteria["is_official"]
                and res.get("language") == search_criteria["language"]
                and (search_criteria["format"] == "any" or res.get("format") == search_criteria["format"])
            ]
            
            if result:
                # إذا وجدنا نتيجة، نختارها ونتوقف عن البحث
                selected_resource = result[0]
                break
        # -------------------------------------------------------------

        path_steps.append({
            "index": step_index,
            "title": f"{step['skill']} basics",
            "estimated_hours": step["hours"],
            "resource": selected_resource
        })
        total_estimated_hours += step["hours"]
        step_index += 1
    
    total_weeks = round(total_estimated_hours / weekly_hours) if weekly_hours > 0 else 0

    result = {
        "path_title": f"{goal.replace('_', ' ').title()} - {total_weeks}w",
        "steps": path_steps,
        "metadata": {
            "method": "rule-based-v2-prioritized", # قمنا بتحديث الإصدار
            "total_estimated_hours": total_estimated_hours,
            "estimated_weeks": total_weeks,
            "user_preferences": preferences
        }
    }

    return result

