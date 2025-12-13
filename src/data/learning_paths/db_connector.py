# =================== ابدأ النسخ من هنا (ملف data/learning_paths/db_connector.py الكامل) ===================

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --- إعداد الاتصال ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ConnectionError("DATABASE_URL is not set in the .env file.")
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"Failed to create database engine: {e}")
    engine = None

# --- دوال جلب البيانات ---

def fetch_skills_for_job_role(job_title: str) -> list:
    """
    يجلب المهارات المطلوبة لدور وظيفي معين من قاعدة البيانات.
    هذه الدالة تستخدمها وحدة التقييم (assessor).
    """
    if not engine: return []
    query = text("""
        SELECT s.id, s.name FROM skills s
        JOIN job_role_skills jrs ON s.id = jrs.skill_id
        JOIN job_roles jr ON jr.id = jrs.job_role_id
        WHERE jr.title ILIKE :title
    """)
    skills = []
    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"title": job_title})
            for row in result:
                skills.append(dict(row._mapping))
    except Exception as e:
        print(f"Error fetching skills for job role '{job_title}': {e}")
    return skills


def fetch_template_path_by_title(title: str) -> dict | None:
    """
    يجلب المسار النموذجي الكامل (مع خطواته وموارده) بناءً على عنوانه.
    هذه هي الدالة الرئيسية التي يستخدمها مولد المسارات (generator).
    """
    if not engine: return None

    path_query = text("SELECT * FROM paths WHERE title ILIKE :title LIMIT 1")
    steps_query = text("""
        SELECT ps.*, s.name as skill_name FROM path_steps ps
        LEFT JOIN path_skills psk ON ps.path_id = psk.path_id AND ps.step_number = psk.skill_id -- افتراض مؤقت للربط
        LEFT JOIN skills s ON psk.skill_id = s.id
        WHERE ps.path_id = :path_id ORDER BY ps.step_number
    """)
    resources_query = text("""
        SELECT r.* FROM resources r
        JOIN step_resources sr ON r.id = sr.resource_id
        WHERE sr.step_id = :step_id
    """)

    path_data = {}
    try:
        with engine.connect() as connection:
            # 1. جلب بيانات المسار الأساسية
            path_result = connection.execute(path_query, {"title": title}).fetchone()
            if not path_result:
                print(f"No template path found with title '{title}'")
                return None
            
            path_data = dict(path_result._mapping)
            path_data['steps'] = []
            
            # 2. جلب خطوات المسار
            steps_result = connection.execute(steps_query, {"path_id": path_data['id']})
            for step_row in steps_result:
                step_data = dict(step_row._mapping)
                step_data['resources'] = []
                
                # 3. جلب الموارد لكل خطوة
                resources_result = connection.execute(resources_query, {"step_id": step_data['id']})
                for resource_row in resources_result:
                    step_data['resources'].append(dict(resource_row._mapping))
                
                path_data['steps'].append(step_data)
                
    except Exception as e:
        print(f"An error occurred while fetching the template path '{title}': {e}")
        return None
            
    return path_data

# =================== انتهى النسخ هنا ===================