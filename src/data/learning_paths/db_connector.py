# =================== ملف data/learning_paths/db_connector.py (الكامل والنهائي) ===================

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL: raise ConnectionError("DATABASE_URL not set.")
engine = create_engine(DATABASE_URL)

def fetch_skills_for_job_role(job_title: str) -> list:
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