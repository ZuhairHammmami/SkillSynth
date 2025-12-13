# =================== ابدأ النسخ من هنا (generator.py - الإصدار المصحح والآمن) ===================

from .db_connector import fetch_template_path_by_title

def generate_path(profile, goal, weekly_hours, preferences):
    # --- الخطوة 1: جلب المسار النموذجي الكامل من قاعدة البيانات ---
    template_path = fetch_template_path_by_title(goal)
    if not template_path:
        return {"error": f"Could not find a template path for goal '{goal}'."}

    path_steps = []
    total_estimated_hours = 0
    
    # تقديرات وهمية للساعات (سيتم تحسينها لاحقًا)
    default_hours = {"html": 6, "css": 8, "javascript": 20, "react": 25}

    # --- الخطوة 2: تخصيص المسار بناءً على ملف المستخدم ---
    for step in template_path['steps']:
        # --- الإصلاح هنا: التحقق قبل الاستخدام ---
        # 1. نتحقق أولاً مما إذا كان مفتاح 'skill_name' موجودًا في القاموس 'step'
        # 2. نتحقق أيضًا من أن قيمته ليست None
        if 'skill_name' in step and step['skill_name']:
            skill_name = step['skill_name'].lower()
        else:
            # إذا لم تكن هناك مهارة مرتبطة بهذه الخطوة، نتخطى منطق التخصيص
            # ونضيف الخطوة كما هي.
            skill_name = None

        # الآن، نتحقق من ملف المستخدم فقط إذا كانت هناك مهارة مرتبطة بالخطوة
        if skill_name and profile.get(skill_name, 0) >= 3:
            continue
        # -------------------------------------------

        available_resources = step.get('resources', [])
        
        # يمكنك إضافة منطق الفلترة والأولوية الكامل هنا إذا أردت
        selected_resource = available_resources[0] if available_resources else None
        
        # نستخدم اسم المهارة (إذا كان موجودًا) للحصول على الساعات، وإلا نستخدم قيمة افتراضية
        estimated_hours = default_hours.get(skill_name, 10) if skill_name else 10
        
        path_steps.append({
            "index": step['step_number'],
            "title": step['title'],
            "estimated_hours": estimated_hours,
            "resource": selected_resource
        })
        total_estimated_hours += estimated_hours

    total_weeks = round(total_estimated_hours / weekly_hours) if weekly_hours > 0 else 0

    return {
        "path_title": f"{template_path['title']} - {total_weeks}w",
        "steps": path_steps,
        "metadata": {"method": "db-template-customization-v1.1-safe"}
    }

# =================== انتهى النسخ هنا ===================   