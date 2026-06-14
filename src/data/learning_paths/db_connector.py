# =================== ملف data/learning_paths/db_connector.py (الكامل والنهائي) ===================

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
APP_MODE = os.getenv("MODE", "dev").lower()
DATABASE_URL_PROD = os.getenv("DATABASE_URL")
IS_SQLITE = True
if APP_MODE == "prod" and DATABASE_URL_PROD:
    DATABASE_URL = DATABASE_URL_PROD
    IS_SQLITE = False
else:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    DB_PATH = os.path.join(PROJECT_ROOT, "skillsynth.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL)

def fetch_skills_for_job_role(job_title: str) -> list:
    if not engine: return []
    like_op = "LIKE" if IS_SQLITE else "ILIKE"
    query = text(f"""
        SELECT s.id, s.name FROM skills s
        JOIN job_role_skills jrs ON s.id = jrs.skill_id
        JOIN job_roles jr ON jr.id = jrs.job_role_id
        WHERE jr.title {like_op} :title
    """)
    skills = []
    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"title": job_title})
            skills = [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"Error fetching skills for '{job_title}': {e}")
    return skills

def fetch_resources_for_skill(skill_id: int) -> list:
    if not engine: return []
    query = text("""
        SELECT r.* FROM resources r
        JOIN skill_resources sr ON r.id = sr.resource_id
        WHERE sr.skill_id = :id
    """)
    resources = []
    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"id": skill_id})
            resources = [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"Error fetching resources for skill_id '{skill_id}': {e}")
    return resources