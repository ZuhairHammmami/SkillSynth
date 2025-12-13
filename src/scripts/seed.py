# =================== ابدأ النسخ من هنا (ملف scripts/seed.py الكامل والنهائي) ===================

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def seed_database():
    """
    يقوم هذا السكربت بإعادة بناء وتعبئة قاعدة البيانات بمسار نموذجي متكامل.
    """
    print("--- Starting database seeding (v3.2 - With System Profile) ---")

    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in the .env file.")

    engine = create_engine(DATABASE_URL)

    # --- 1. تعريف البيانات التجريبية ---

    # --- التغيير 1: إضافة بيانات المستخدم التجريبي ---
    profiles_data = [
        {'id': 1, 'email': 'system@skillsynth.com', 'full_name': 'System User', 'hashed_password': 'dummy_password'}
    ]

    skills_data = [ {'id': 1, 'name': 'HTML'}, {'id': 2, 'name': 'CSS'}, {'id': 3, 'name': 'JavaScript'}, {'id': 8, 'name': 'React'} ]
    resources_data = [ {'id': 1, 'title': 'MDN - HTML Basics', 'url': '...', 'type': 'article', 'is_free': True, 'is_official': True, 'author_or_platform': 'Mozilla'}, {'id': 2, 'title': 'freeCodeCamp - Learn CSS', 'url': '...', 'type': 'course', 'is_free': True, 'is_official': False, 'author_or_platform': 'freeCodeCamp'}, {'id': 3, 'title': 'JavaScript.info', 'url': '...', 'type': 'book', 'is_free': True, 'is_official': True, 'author_or_platform': 'javascript.info'}, {'id': 8, 'title': 'React Official Tutorial', 'url': '...', 'type': 'course', 'is_free': True, 'is_official': True, 'author_or_platform': 'Meta'} ]
    paths_data = [ {'id': 1, 'profile_id': 1, 'title': 'Frontend Developer', 'description': 'A comprehensive path for frontend developers.'} ]
    path_steps_data = [ {'id': 1, 'path_id': 1, 'step_number': 1, 'title': 'HTML Basics', 'content': '...'}, {'id': 2, 'path_id': 1, 'step_number': 2, 'title': 'CSS Styling', 'content': '...'}, {'id': 3, 'path_id': 1, 'step_number': 3, 'title': 'JavaScript Essentials', 'content': '...'}, {'id': 4, 'path_id': 1, 'step_number': 4, 'title': 'React Framework', 'content': '...'} ]
    path_skills_data = [ {'path_id': 1, 'skill_id': 1}, {'path_id': 1, 'skill_id': 2}, {'path_id': 1, 'skill_id': 3}, {'path_id': 1, 'skill_id': 8} ]
    step_resources_data = [ {'step_id': 1, 'resource_id': 1}, {'step_id': 2, 'resource_id': 2}, {'step_id': 3, 'resource_id': 3}, {'step_id': 4, 'resource_id': 8} ]
    job_roles_data = [ {'id': 1, 'title': 'Frontend Developer'} ]
    job_role_skills_data = [ {'job_role_id': 1, 'skill_id': 1}, {'job_role_id': 1, 'skill_id': 2}, {'job_role_id': 1, 'skill_id': 3}, {'job_role_id': 1, 'skill_id': 8} ]


    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            print("--- Deleting old data in correct reverse order of dependency ---")
            
            # الترتيب الصحيح للحذف (يشمل الآن paths)
            connection.execute(text("DELETE FROM step_resources;"))
            connection.execute(text("DELETE FROM path_skills;"))
            connection.execute(text("DELETE FROM path_steps;"))
            connection.execute(text("DELETE FROM paths;")) # <-- يجب حذف المسارات قبل المستخدمين الذين أنشأوها
            connection.execute(text("DELETE FROM profiles WHERE id = 1;")) # نحذف المستخدم التجريبي فقط
            
            connection.execute(text("DELETE FROM job_role_skills;"))
            connection.execute(text("DELETE FROM skill_categories;"))
            connection.execute(text("DELETE FROM resources;"))
            connection.execute(text("DELETE FROM skills;"))
            connection.execute(text("DELETE FROM job_roles;"))

            print("--- Inserting new data into tables ---")
            
            # --- التغيير 2: إدخال المستخدم التجريبي أولاً ---
            connection.execute(text("INSERT INTO profiles (id, email, full_name, hashed_password) VALUES (:id, :email, :full_name, :hashed_password) ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email;"), profiles_data)
            
            # الآن يمكننا إدخال باقي البيانات التي تعتمد عليه
            connection.execute(text("INSERT INTO skills (id, name) VALUES (:id, :name) ON CONFLICT (id) DO NOTHING;"), skills_data)
            connection.execute(text("INSERT INTO resources (id, title, url, type, is_free, is_official, author_or_platform) VALUES (:id, :title, :url, :type, :is_free, :is_official, :author_or_platform) ON CONFLICT (id) DO NOTHING;"), resources_data)
            connection.execute(text("INSERT INTO paths (id, profile_id, title, description) VALUES (:id, :profile_id, :title, :description) ON CONFLICT (id) DO NOTHING;"), paths_data)
            connection.execute(text("INSERT INTO path_steps (id, path_id, step_number, title, content) VALUES (:id, :path_id, :step_number, :title, :content) ON CONFLICT (id) DO NOTHING;"), path_steps_data)
            connection.execute(text("INSERT INTO job_roles (id, title) VALUES (:id, :title) ON CONFLICT (id) DO NOTHING;"), job_roles_data)
            
            connection.execute(text("INSERT INTO path_skills (path_id, skill_id) VALUES (:path_id, :skill_id) ON CONFLICT DO NOTHING;"), path_skills_data)
            connection.execute(text("INSERT INTO step_resources (step_id, resource_id) VALUES (:step_id, :resource_id) ON CONFLICT DO NOTHING;"), step_resources_data)
            connection.execute(text("INSERT INTO job_role_skills (job_role_id, skill_id) VALUES (:job_role_id, :skill_id) ON CONFLICT DO NOTHING;"), job_role_skills_data)
            
            transaction.commit()
            print("✅ Database seeding completed successfully!")

        except Exception as e:
            print(f"❌ An error occurred during seeding: {e}")
            transaction.rollback()
            print("--- Database seeding failed. Transaction was rolled back. ---")

if __name__ == "__main__":
    seed_database()

# =================== انتهى النسخ هنا ===================