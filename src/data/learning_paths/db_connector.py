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
        SELECT s.id, s.name, s.difficulty_level FROM skills s
        JOIN job_role_skills jrs ON s.id = jrs.skill_id
        JOIN job_roles jr ON jr.id = jrs.job_role_id
        WHERE jr.title {like_op} :title
        ORDER BY s.id ASC
    """)
    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"title": job_title})
            return [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"Error fetching skills for '{job_title}': {e}")
        return []

def fetch_resources_for_skill(skill_id: int) -> list:
    if not engine: return []
    query = text("""
        SELECT r.* FROM resources r
        JOIN skill_resources sr ON r.id = sr.resource_id
        WHERE sr.skill_id = :id
    """)
    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"id": skill_id})
            return [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"Error fetching resources for skill_id '{skill_id}': {e}")
        return []

def fetch_prerequisites_for_skills(skill_ids: list) -> dict:
    """Build a map of skill_id -> list of prerequisite skill_ids from DB."""
    if not engine or not skill_ids:
        return {}
    placeholders = ", ".join([f":id_{i}" for i in range(len(skill_ids))])
    params = {f"id_{i}": sid for i, sid in enumerate(skill_ids)}
    query = text(f"""
        SELECT sp.skill_id, sp.prerequisite_skill_id, s.name as prereq_name
        FROM skill_prerequisites sp
        JOIN skills s ON s.id = sp.prerequisite_skill_id
        WHERE sp.skill_id IN ({placeholders})
    """)
    try:
        with engine.connect() as connection:
            result = connection.execute(query, params)
            prereq_map = {sid: [] for sid in skill_ids}
            for row in result:
                sid = int(row.skill_id)
                if sid in prereq_map:
                    prereq_map[sid].append({
                        "id": int(row.prerequisite_skill_id),
                        "name": row.prereq_name
                    })
            return prereq_map
    except Exception as e:
        print(f"Error fetching prerequisites: {e}")
        return {}

def fetch_role_skill_config(job_title: str) -> list:
    """Get skill ordering and hours from role_skill_configs for a job role."""
    if not engine: return []
    like_op = "LIKE" if IS_SQLITE else "ILIKE"
    query = text(f"""
        SELECT rsc.skill_id, rsc."order", rsc.estimated_hours, s.name as skill_name
        FROM role_skill_configs rsc
        JOIN job_roles jr ON jr.id = rsc.job_role_id
        JOIN skills s ON s.id = rsc.skill_id
        WHERE jr.title {like_op} :title
        ORDER BY rsc."order" ASC
    """)
    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"title": job_title})
            return [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"Error fetching role config for '{job_title}': {e}")
        return []

def fetch_all_skill_names() -> dict:
    """Return dict of skill_name.lower() -> {id, name} for resolving names to IDs."""
    if not engine: return {}
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, name FROM skills"))
            return {row.name.lower(): {"id": row.id, "name": row.name} for row in result}
    except Exception as e:
        print(f"Error fetching skill names: {e}")
        return {}
