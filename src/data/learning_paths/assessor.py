
import json
import os

# --- 1. تحديد المسارات للملفات التي سنحتاجها ---
# نستخدم نفس الطريقة الذكية لتحديد المسارات كما في generator.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(BASE_DIR, 'rules.json')
ASSESSMENTS_PATH = os.path.join(BASE_DIR, 'assessments.json')


def run_assessment(goal, user_answers):
    """
    يقوم بتشغيل تقييم للمستخدم بناءً على هدفه وإجاباته،
    ويعيد قاموسًا بمستويات المهارة المقدرة.

    Args:
        goal (str): الهدف التعليمي للمستخدم (مثل 'frontend_developer').
        user_answers (dict): قاموس يحتوي على إجابات المستخدم.
                             الشكل: {"question_id": answer_index}
                             مثال: {"html_q1": 0, "css_q1": 1}

    Returns:
        dict: قاموس يمثل ملف مهارات المستخدم (profile).
              مثال: {"html": 2, "css": 1, "javascript": 0}
    """
    # --- 2. قراءة ملفات القواعد والأسئلة ---
    try:
        with open(RULES_PATH, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        with open(ASSESSMENTS_PATH, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
    except FileNotFoundError as e:
        return {"error": f"Configuration file not found: {e}"}

    if goal not in rules:
        return {"error": f"Goal '{goal}' not found in rules."}

    # --- 3. تحديد المهارات التي يجب اختبارها ---
    # نستخرج قائمة المهارات من ملف القواعد بناءً على هدف المستخدم
    skills_to_test = [step['skill'].lower() for step in rules[goal]]
    
    skill_levels = {}

    # --- 4. حساب مستوى كل مهارة على حدة ---
    for skill in skills_to_test:
        questions_for_skill = all_questions.get(skill, [])
        if not questions_for_skill:
            # إذا لم تكن هناك أسئلة لهذه المهارة، نفترض أن المستوى 0
            skill_levels[skill] = 0
            continue

        correct_count = 0
        total_questions = len(questions_for_skill)

        for question in questions_for_skill:
            question_id = question['id']
            correct_answer_index = question['correct_option_index']
            user_answer_index = user_answers.get(question_id)

            if user_answer_index == correct_answer_index:
                correct_count += 1
        
        # --- 5. منطق تحويل النتيجة إلى مستوى ---
        # هذا هو الجزء الذي يترجم "كم إجابة صحيحة" إلى "ما هو مستواك"
        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        level = 0 # القيمة الافتراضية
        if score_percentage == 100:
            level = 3 # أتقن كل شيء -> خبير (يمكنه تخطي الخطوة)
        elif score_percentage >= 50:
            level = 2 # يعرف نصف الإجابات أو أكثر -> متوسط
        elif score_percentage > 0:
            level = 1 # يعرف شيئًا ما ولكن ليس الكثير -> مبتدئ لديه فكرة
        else:
            level = 0 # لم يجب على أي سؤال بشكل صحيح -> مبتدئ تمامًا
            
        skill_levels[skill] = level

    return skill_levels

