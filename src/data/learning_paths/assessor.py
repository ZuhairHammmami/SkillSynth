import json
import os
from .db_connector import fetch_skills_for_job_role

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSESSMENTS_PATH = os.path.join(BASE_DIR, 'assessments.json')


def run_assessment(goal, user_answers):
    try:
        with open(ASSESSMENTS_PATH, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
    except FileNotFoundError:
        return {"error": f"Assessments file not found at: {ASSESSMENTS_PATH}"}

    skills_data = fetch_skills_for_job_role(goal)
    if not skills_data:
        return {"error": f"Could not find skills for job role '{goal}' in the database."}

    skill_names = [s['name'] for s in skills_data]

    skill_levels = {}

    for skill_name in skill_names:
        question_group = all_questions.get(skill_name, None)
        if not question_group:
            skill_levels[skill_name.lower()] = 0
            continue

        questions = question_group.get("questions", [])
        if not questions:
            skill_levels[skill_name.lower()] = 0
            continue

        correct_count = 0
        total_for_skill = 0

        for q_idx, question in enumerate(questions):
            qid = f"{skill_name.lower()}_q{q_idx}"
            user_answer_index = user_answers.get(qid)
            if user_answer_index is None:
                continue

            correct_text = question.get("correct", "")
            options = question.get("options", [])
            try:
                correct_index = options.index(correct_text)
            except ValueError:
                continue

            total_for_skill += 1
            if user_answer_index == correct_index:
                correct_count += 1

        if total_for_skill == 0:
            skill_levels[skill_name.lower()] = 0
            continue

        score_pct = (correct_count / total_for_skill) * 100

        if score_pct == 100:
            level = 5
        elif score_pct >= 80:
            level = 4
        elif score_pct >= 60:
            level = 3
        elif score_pct >= 40:
            level = 2
        elif score_pct > 0:
            level = 1
        else:
            level = 0

        skill_levels[skill_name.lower()] = level

    return skill_levels
