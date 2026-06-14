# scripts/seed.py

import os
import sys
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --- إعداد المسار الصحيح لاستيراد وحدات الباك اند ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# --- استيراد وحدة التشفير ---
from backend.auth import get_password_hash

def seed_database():
    """
    يقوم هذا السكربت بتعبئة قاعدة البيانات ببيانات أولية.
    مسؤوليته هي "حذف البيانات" و "إضافة البيانات"، وليس بناء الهيكل.
    """
    print("--- 🏭 Starting Data Factory: Seeding database (v4.0 - Final) ---")

    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or "postgresql" not in DATABASE_URL:
        raise ValueError("DATABASE_URL for PostgreSQL is not set correctly.")
    
    engine = create_engine(DATABASE_URL)

    # --- 1. تعريف عالم البيانات الكامل ---
    admin_password_hash = get_password_hash("admin123")
    profiles_data = [
        {'id': 1, 'email': 'admin@skillsynth.com', 'full_name': 'Admin User', 'hashed_password': admin_password_hash, 'is_admin': True, 'skill_profile': None, 'subscription_tier': 'admin', 'subscription_expires_at': None}
    ]
    
    categories_data = [{'id': 1, 'name': 'Frontend Development'}, {'id': 2, 'name': 'Backend Development'}]
    
    skills_data = [
        {'id': 1, 'name': 'HTML'}, {'id': 2, 'name': 'CSS'}, {'id': 3, 'name': 'JavaScript'},
        {'id': 4, 'name': 'React'}, {'id': 5, 'name': 'Python'}, {'id': 6, 'name': 'SQL'}
    ]

    resources_data = [
        {'id': 1, 'title': 'MDN Web Docs: HTML', 'url': 'https://developer.mozilla.org/en-US/docs/Web/HTML', 'type': 'article', 'is_free': True, 'is_official': True, 'author_or_platform': 'Mozilla'},
        {'id': 2, 'title': 'CSS-Tricks: A Guide to Flexbox', 'url': 'https://css-tricks.com/snippets/css/a-guide-to-flexbox/', 'type': 'article', 'is_free': True, 'is_official': False, 'author_or_platform': 'CSS-Tricks'},
        {'id': 3, 'title': 'JavaScript.info', 'url': 'https://javascript.info/', 'type': 'book', 'is_free': True, 'is_official': False, 'author_or_platform': 'javascript.info'},
        {'id': 4, 'title': 'React Official Docs Tutorial', 'url': 'https://react.dev/learn', 'type': 'course', 'is_free': True, 'is_official': True, 'author_or_platform': 'Meta'},
    ]
    
    job_roles_data = [{'id': 1, 'title': 'Frontend Developer'}]
    
    skill_categories_data = [{'skill_id': 1, 'category_id': 1}, {'skill_id': 2, 'category_id': 1}, {'skill_id': 3, 'category_id': 1}, {'skill_id': 4, 'category_id': 1}]
    job_role_skills_data = [{'job_role_id': 1, 'skill_id': 1}, {'job_role_id': 1, 'skill_id': 2}, {'job_role_id': 1, 'skill_id': 3}, {'job_role_id': 1, 'skill_id': 4}]

    
    # --- 2. تنفيذ عملية التعبئة ---
    tables_to_delete = [
        "assessment_results", "step_completions", "step_assessments", "step_resources",
        "path_skills", "job_role_skills", "skill_categories", "path_steps", "paths",
        "assessments", "job_roles", "resources", "skills", "categories", "profiles"
    ]
    
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            print("--- 🗑️ Deleting old data (in correct order)... ---")
            for table in tables_to_delete:
                connection.execute(text(f"DELETE FROM {table};"))
                print(f"  - Emptied table: {table}")

            print("--- 📥 Inserting new data... ---")
            
            # إعادة تعيين عدادات الـ ID
            tables_with_sequences = ["profiles", "categories", "skills", "resources", "job_roles", "paths", "path_steps", "assessments", "assessment_results"]
            for table in tables_with_sequences:
                try:
                    connection.execute(text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1;"))
                except Exception: pass

            # إدخال البيانات الجديدة
            connection.execute(text("INSERT INTO profiles (id, email, full_name, hashed_password, is_admin, skill_profile, subscription_tier, subscription_expires_at) VALUES (:id, :email, :full_name, :hashed_password, :is_admin, :skill_profile, :subscription_tier, :subscription_expires_at)"), profiles_data)
            connection.execute(text("INSERT INTO categories (id, name) VALUES (:id, :name)"), categories_data)
            connection.execute(text("INSERT INTO skills (id, name) VALUES (:id, :name)"), skills_data)
            connection.execute(text("INSERT INTO resources (id, title, url, type, is_free, is_official, author_or_platform) VALUES (:id, :title, :url, :type, :is_free, :is_official, :author_or_platform)"), resources_data)
            connection.execute(text("INSERT INTO job_roles (id, title) VALUES (:id, :title)"), job_roles_data)
            connection.execute(text("INSERT INTO skill_categories (skill_id, category_id) VALUES (:skill_id, :category_id)"), skill_categories_data)
            connection.execute(text("INSERT INTO job_role_skills (job_role_id, skill_id) VALUES (:job_role_id, :skill_id)"), job_role_skills_data)
            
            print("  - Data insertion complete.")

            transaction.commit()
            print("--- ✅ Database factory ran successfully! ---")
            
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            transaction.rollback()
            print("--- 🛑 Database factory failed. Transaction was rolled back. ---")

if __name__ == "__main__":
    seed_database()