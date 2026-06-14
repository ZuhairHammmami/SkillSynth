# =================== ملف data/learning_paths/generator.py (الكامل والنهائي) ===================

from .db_connector import fetch_skills_for_job_role, fetch_resources_for_skill

def generate_path(profile, goal, weekly_hours, preferences):
    # --- الخطوة 1: فهم الهدف والحصول على مخطط البناء ---
    skills_for_path = fetch_skills_for_job_role(goal)
    if not skills_for_path:
        return {"error": f"I couldn't find a career path for '{goal}'. It might be a new and exciting field I'm still learning about!"}

    path_steps = []
    total_estimated_hours = 0
    step_index = 1
    
    # مكتبة تقديرات الساعات (يمكن توسيعها)
    default_hours = {"html": 6, "css": 8, "javascript": 20, "react": 25, "git": 5, "python": 30, "sql": 15, "fastapi": 12, "pandas": 18}

    # --- الخطوة 2: بناء كل خطوة في الرحلة بلمسة إبداعية ---
    for skill in skills_for_path:
        skill_name = skill['name'].lower()
        skill_id = skill['id']
        
        if profile.get(skill_name, 0) >= 3:
            continue # تخطي المهارات المتقنة

        # --- الخطوة 3: البحث عن أفضل الموارد ---
        available_resources = fetch_resources_for_skill(skill_id)
        
        # --- اللمسة السحرية: اختيار المورد الرئيسي والموارد الإضافية ---
        main_resource = None
        additional_resources = []
        
        # فلترة حسب اللغة
        lang = preferences.get("language", "en")
        lang_resources = [r for r in available_resources if r.get('language') == lang]
        # خطة بديلة: إذا لم توجد موارد باللغة المطلوبة، استخدم الإنجليزية
        if not lang_resources:
            lang_resources = [r for r in available_resources if r.get('language') == 'en']

        # اختيار المورد الرئيسي (الأولوية للرسمي ثم الدورة التعليمية)
        if lang_resources:
            official_courses = [r for r in lang_resources if r.get('is_official') and r.get('type') == 'course']
            official_others = [r for r in lang_resources if r.get('is_official')]
            unofficial_courses = [r for r in lang_resources if r.get('type') == 'course']
            
            if official_courses: main_resource = official_courses[0]
            elif official_others: main_resource = official_others[0]
            elif unofficial_courses: main_resource = unofficial_courses[0]
            else: main_resource = lang_resources[0]

            # كل الموارد الأخرى تعتبر إضافية
            additional_resources = [r for r in lang_resources if r != main_resource]

        # --- صياغة عنوان الخطوة الملهم ---
        step_titles = {
            "html": f"Step {step_index}: Build Your First Web Skeleton (HTML)",
            "css": f"Step {step_index}: Bring Your Web to Life with Style (CSS)",
            "javascript": f"Step {step_index}: Add Brains to Your Project (JavaScript)",
            "react": f"Step {step_index}: Master Modern UI with React",
            "python": f"Step {step_index}: Unlock the Power of Python",
            "sql": f"Step {step_index}: Learn to Speak the Language of Data (SQL)",
            "git": f"Step {step_index}: Master Time Travel with Git"
        }

        path_steps.append({
            "index": step_index,
            "title": step_titles.get(skill_name, f"Step {step_index}: Explore {skill['name']}"),
            "skill_name": skill['name'],
            "estimated_hours": default_hours.get(skill_name, 10),
            "main_resource": main_resource,
            "additional_resources": additional_resources
        })
        total_estimated_hours += default_hours.get(skill_name, 10)
        step_index += 1

    total_weeks = round(total_estimated_hours / weekly_hours) if weekly_hours > 0 else 0

    # --- رسالة المقدمة الملهمة ---
    intro_message = f"Welcome to your personalized journey to becoming a {goal.title()}! This {total_weeks}-week path is designed to take you from your current level to job-ready. Let's begin!"

    return {
        "path_title": f"Your Custom Path to Becoming a {goal.title()}",
        "intro_message": intro_message,
        "estimated_weeks": total_weeks,
        "total_estimated_hours": total_estimated_hours,
        "steps": path_steps,
        "metadata": {"method": "smart-mentor-v1"}
    }