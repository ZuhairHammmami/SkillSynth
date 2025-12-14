# scripts/seed.py

import os
import sys
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --- إعداد المسار ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def seed_database():
    """
    يقوم هذا السكربت ببناء عالم كامل من البيانات الأولية في قاعدة البيانات.
    إنه "مدمر" ويقوم بحذف البيانات القديمة أولاً لضمان بداية نظيفة.
    """
    print("--- 🏭 Starting Data Factory: Seeding database... ---")

    # 1. تحميل متغيرات البيئة والاتصال
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or "postgresql" not in DATABASE_URL:
        raise ValueError("DATABASE_URL for PostgreSQL is not set correctly in the .env file.")

    engine = create_engine(DATABASE_URL)

    # --- 2. تعريف البيانات الأولية الواقعية ---

    # -- الكيانات الأساسية --
    categories = [
        {'id': 1, 'name': 'Frontend Development'},
        {'id': 2, 'name': 'Backend Development'},
        {'id': 3, 'name': 'Data Science'},
        {'id': 4, 'name': 'DevOps'},
    ]

    skills = [
        {'id': 1, 'name': 'HTML'}, {'id': 2, 'name': 'CSS'}, {'id': 3, 'name': 'JavaScript'},
        {'id': 4, 'name': 'React'}, {'id': 5, 'name': 'Python'}, {'id': 6, 'name': 'SQL'},
        {'id': 7, 'name': 'FastAPI'}, {'id': 8, 'name': 'Pandas'}, {'id': 9, 'name': 'Docker'},
        {'id': 10, 'name': 'Git'}, {'id': 11, 'name': 'TypeScript'},
    ]

    resources = [
        {'id': 1, 'title': 'MDN Web Docs: HTML', 'url': 'https://developer.mozilla.org/en-US/docs/Web/HTML', 'type': 'article', 'is_free': True, 'is_official': True, 'author_or_platform': 'Mozilla'},
        {'id': 2, 'title': 'CSS-Tricks: A Guide to Flexbox', 'url': 'https://css-tricks.com/snippets/css/a-guide-to-flexbox/', 'type': 'article', 'is_free': True, 'is_official': False, 'author_or_platform': 'CSS-Tricks'},
        {'id': 3, 'title': 'JavaScript.info: The Modern JavaScript Tutorial', 'url': 'https://javascript.info/', 'type': 'book', 'is_free': True, 'is_official': False, 'author_or_platform': 'javascript.info'},
        {'id': 4, 'title': 'React Official Docs: Tic-Tac-Toe Tutorial', 'url': 'https://react.dev/learn', 'type': 'course', 'is_free': True, 'is_official': True, 'author_or_platform': 'Meta'},
        {'id': 5, 'title': 'The Official Python Tutorial', 'url': 'https://docs.python.org/3/tutorial/', 'type': 'book', 'is_free': True, 'is_official': True, 'author_or_platform': 'Python Software Foundation'},
        {'id': 6, 'title': 'SQLBolt: Interactive SQL Tutorial', 'url': 'https://sqlbolt.com/', 'type': 'course', 'is_free': True, 'is_official': False, 'author_or_platform': 'SQLBolt'},
        {'id': 7, 'title': 'FastAPI Official Documentation', 'url': 'https://fastapi.tiangolo.com/', 'type': 'article', 'is_free': True, 'is_official': True, 'author_or_platform': 'Tiangolo'},
        {'id': 8, 'title': 'Pandas User Guide: 10 minutes to pandas', 'url': 'https://pandas.pydata.org/docs/user_guide/10min.html', 'type': 'article', 'is_free': True, 'is_official': True, 'author_or_platform': 'Pandas Core Team'},
        {'id': 9, 'title': 'Docker Get Started Tutorial', 'url': 'https://docs.docker.com/get-started/', 'type': 'course', 'is_free': True, 'is_official': True, 'author_or_platform': 'Docker'},
    ]

    job_roles = [
        {'id': 1, 'title': 'Frontend Developer'},
        {'id': 2, 'title': 'Backend Developer (Python)'},
        {'id': 3, 'title': 'Full-Stack Developer'},
    ]

    assessments = []
    ASSESSMENTS_FILE_PATH = os.path.join(PROJECT_ROOT, "src/data/learning_paths/assessments.json")
    if os.path.exists(ASSESSMENTS_FILE_PATH):
        with open(ASSESSMENTS_FILE_PATH, 'r', encoding='utf-8') as f:
            all_assessments_json = json.load(f)
            assessment_id_counter = 1
            for skill_name, questions in all_assessments_json.items():
                assessments.append({
                    'id': assessment_id_counter,
                    'title': f"{skill_name.capitalize()} Assessment",
                    'assessment_type': 'placement_test'
                })
                assessment_id_counter += 1
    else:
        print("WARNING: 'assessments.json' not found. Skipping assessment seeding.")


    # -- الجداول الوسيطة (العلاقات) --
    skill_categories = [
        {'skill_id': 1, 'category_id': 1}, {'skill_id': 2, 'category_id': 1}, 
        {'skill_id': 3, 'category_id': 1}, {'skill_id': 3, 'category_id': 2},
        {'skill_id': 4, 'category_id': 1}, {'skill_id': 5, 'category_id': 2},
        {'skill_id': 5, 'category_id': 3}, {'skill_id': 6, 'category_id': 2},
        {'skill_id': 6, 'category_id': 3}, {'skill_id': 7, 'category_id': 2},
        {'skill_id': 8, 'category_id': 3}, {'skill_id': 9, 'category_id': 4},
        {'skill_id': 10, 'category_id': 1},{'skill_id': 10, 'category_id': 2},
        {'skill_id': 10, 'category_id': 3},{'skill_id': 10, 'category_id': 4},
        {'skill_id': 11, 'category_id': 1}, {'skill_id': 11, 'category_id': 2},
    ]

    job_role_skills = [
        # Frontend Developer
        {'job_role_id': 1, 'skill_id': 1}, {'job_role_id': 1, 'skill_id': 2},
        {'job_role_id': 1, 'skill_id': 3}, {'job_role_id': 1, 'skill_id': 4},
        {'job_role_id': 1, 'skill_id': 10}, {'job_role_id': 1, 'skill_id': 11},
        # Backend Developer
        {'job_role_id': 2, 'skill_id': 5}, {'job_role_id': 2, 'skill_id': 6},
        {'job_role_id': 2, 'skill_id': 7}, {'job_role_id': 2, 'skill_id': 9},
        {'job_role_id': 2, 'skill_id': 10},
        # Full-Stack Developer
        {'job_role_id': 3, 'skill_id': 1}, {'job_role_id': 3, 'skill_id': 2},
        {'job_role_id': 3, 'skill_id': 3}, {'job_role_id': 3, 'skill_id': 4},
        {'job_role_id': 3, 'skill_id': 5}, {'job_role_id': 3, 'skill_id': 6},
        {'job_role_id': 3, 'skill_id': 7}, {'job_role_id': 3, 'skill_id': 9},
        {'job_role_id': 3, 'skill_id': 10}, {'job_role_id': 3, 'skill_id': 11},
    ]


    # --- 3. تنفيذ عملية التعبئة ---

    # قائمة الجداول التي سيتم حذف بياناتها بالترتيب الصحيح
    # الجداول التي تعتمد عليها جداول أخرى تأتي أولاً
    tables_to_delete = [
        "assessment_results", "step_completions", "step_assessments", "step_resources",
        "path_skills", "job_role_skills", "skill_categories", "path_steps", "paths",
        "assessments", "job_roles", "resources", "skills", "categories", "profiles"
    ]
    
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # حذف البيانات القديمة بالترتيب
            print("--- 🗑️ Deleting old data... ---")
            for table in tables_to_delete:
                connection.execute(text(f"DELETE FROM {table};"))
                print(f"  - Emptied table: {table}")

            # إدخال البيانات الجديدة
            print("--- 📥 Inserting new data... ---")
            
            # ملاحظة: نستخدم 'text()' للتأكد من أن SQLAlchemy يتعامل مع الأوامر بأمان
            connection.execute(text("INSERT INTO categories (id, name) VALUES (:id, :name)"), categories)
            print("  - Seeded categories")
            
            connection.execute(text("INSERT INTO skills (id, name) VALUES (:id, :name)"), skills)
            print("  - Seeded skills")

            connection.execute(text("INSERT INTO resources (id, title, url, type, is_free, is_official, author_or_platform) VALUES (:id, :title, :url, :type, :is_free, :is_official, :author_or_platform)"), resources)
            print("  - Seeded resources")

            connection.execute(text("INSERT INTO job_roles (id, title) VALUES (:id, :title)"), job_roles)
            print("  - Seeded job_roles")
            
            if assessments:
                connection.execute(text("INSERT INTO assessments (id, title, assessment_type) VALUES (:id, :title, :assessment_type)"), assessments)
                print("  - Seeded assessments from JSON file")

            connection.execute(text("INSERT INTO skill_categories (skill_id, category_id) VALUES (:skill_id, :category_id)"), skill_categories)
            print("  - Seeded skill_categories relationships")
            
            connection.execute(text("INSERT INTO job_role_skills (job_role_id, skill_id) VALUES (:job_role_id, :skill_id)"), job_role_skills)
            print("  - Seeded job_role_skills relationships")

            # تأكيد العملية
            transaction.commit()
            print("--- ✅ Database factory ran successfully! ---")
            
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            transaction.rollback()
            print("--- 🛑 Database factory failed. Transaction was rolled back. ---")

if __name__ == "__main__":
    seed_database()