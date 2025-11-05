# =================== ابدأ النسخ من هنا (النسخة النهائية الكاملة والصحيحة) ===================

import json
import os

# نعود إلى قراءة ملفات JSON المحلية للهيكل والموارد في هذه المرحلة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(BASE_DIR, 'rules.json')
RESOURCES_PATH = os.path.join(BASE_DIR, 'resources.json')

def generate_path(profile, goal, weekly_hours, preferences):
    """
    يولد مسارًا تعليميًا مخصصًا بالاعتماد على ملفات JSON للهيكل والموارد.
    """
    try:
        with open(RULES_PATH, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        with open(RESOURCES_PATH, 'r', encoding='utf-8') as f:
            all_resources = json.load(f)
    except FileNotFoundError as e:
        return {"error": f"Configuration file not found: {e}"}

    if goal not in rules:
        return {"error": f"Goal '{goal}' not found in rules."}

    goal_steps = rules[goal]
    path_steps = []
    total_estimated_hours = 0
    step_index = 1

    for step in goal_steps:
        skill_name_from_profile = step["skill"].lower()
        if profile.get(skill_name_from_profile, 0) >= 3:
            continue

        resource_tag = step["tag"]
        # نقرأ الموارد من ملف JSON الذي قمنا بتحميله
        all_tagged_resources = all_resources.get(resource_tag, [])
        
        # منطق الفلترة والأولوية المتقدم يبقى كما هو لأنه يعتمد على قائمة الموارد فقط
        wants_free = preferences.get("is_free", True)
        available_resources = [res for res in all_tagged_resources if res.get("is_free") == wants_free]

        preferred_language = preferences.get("language", "en")
        preferred_format = preferences.get("format", "any")

        priority_searches = [
            {"is_official": True, "language": preferred_language, "format": preferred_format},
            {"is_official": True, "language": preferred_language, "format": "any"},
            {"is_official": False, "language": preferred_language, "format": preferred_format},
            {"is_official": False, "language": preferred_language, "format": "any"},
            {"is_official": True, "language": "en", "format": preferred_format},
            {"is_official": True, "language": "en", "format": "any"},
            {"is_official": False, "language": "en", "format": preferred_format},
            {"is_official": False, "language": "en", "format": "any"},
        ]

        selected_resource = None
        for search_criteria in priority_searches:
            result = [
                res for res in available_resources
                if res.get("is_official") == search_criteria["is_official"]
                and res.get("language") == search_criteria["language"]
                and (search_criteria["format"] == "any" or res.get("format") == search_criteria["format"])
            ]
            if result:
                selected_resource = result[0]
                break

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
            "method": "rule-based-v2-prioritized", # نعود إلى الإصدار الأخير الناجح
            "total_estimated_hours": total_estimated_hours,
            "estimated_weeks": total_weeks,
            "user_preferences": preferences
        }
    }

    return result

# =================== انتهى النسخ هنا ===================