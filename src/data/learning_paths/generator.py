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

        # --- الجزء الذي تم تطويره: منطق البحث الذكي مع خطة بديلة ---
        resource_tag = step["tag"]
        preferred_language = preferences.get("language", "en")
        preferred_format = preferences.get("format", "any")
        all_tagged_resources = all_resources.get(resource_tag, [])
        
        selected_resource = None # نبدأ بافتراض أننا لم نجد شيئًا

        # 1. المحاولة الأولى: تطابق مثالي (اللغة + الصيغة)
        perfect_match = [
            res for res in all_tagged_resources
            if res.get("language") == preferred_language and (preferred_format == "any" or res.get("format") == preferred_format)
        ]
        if perfect_match:
            selected_resource = perfect_match[0]
        
        # 2. المحاولة الثانية: إذا فشلت الأولى، تطابق اللغة فقط
        elif not selected_resource:
            language_match = [res for res in all_tagged_resources if res.get("language") == preferred_language]
            if language_match:
                selected_resource = language_match[0]

        # 3. المحاولة الثالثة: إذا فشلت، تطابق الصيغة باللغة الإنجليزية الافتراضية
        elif not selected_resource:
            fallback_match = [
                res for res in all_tagged_resources
                if res.get("language") == "en" and (preferred_format == "any" or res.get("format") == preferred_format)
            ]
            if fallback_match:
                selected_resource = fallback_match[0]
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
            "method": "rule-based-v1",
            "total_estimated_hours": total_estimated_hours,
            "estimated_weeks": total_weeks,
            "user_preferences": preferences
        }
    }

    return result