# scripts/seed.py

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --- إعداد المسار ---
# هذا الجزء يضيف المجلد الرئيسي للمشروع إلى مسار بايثون
# حتى نتمكن من استيراد أي شيء من 'src' إذا احتجنا لذلك (ممارسة جيدة)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

def seed_database():
    """
    يقوم هذا السكربت بتعبئة قاعدة البيانات ببيانات أولية.
    إنه "مدمر" بمعنى أنه سيحذف البيانات القديمة في الجداول المستهدفة أولاً.
    """
    print("--- Starting database seeding ---")

    # 1. تحميل متغيرات البيئة والاتصال بقاعدة البيانات
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in the .env file.")

    # تأكد من أننا نستخدم رابط PostgreSQL
    if "postgresql" not in DATABASE_URL:
        print("WARNING: Seeding is designed for PostgreSQL. Skipping.")
        return

    engine = create_engine(DATABASE_URL)

    # --- 2. تعريف البيانات التجريبية ---

    categories_data = [
        (1, 'Frontend'),
        (2, 'Backend'),
        (3, 'Data Science')
    ]

    skills_data = [
        (1, 'HTML'), (2, 'CSS'), (3, 'JavaScript'),
        (4, 'Python'), (5, 'SQL'), (6, 'FastAPI'),
        (7, 'Pandas'), (8, 'React')
    ]

    skill_categories_data = [
        (1, 1), # HTML -> Frontend
        (2, 1), # CSS -> Frontend
        (3, 1), # JavaScript -> Frontend
        (3, 2), # JavaScript -> Backend (for Node.js)
        (4, 2), # Python -> Backend
        (4, 3), # Python -> Data Science
        (5, 2), # SQL -> Backend
        (5, 3), # SQL -> Data Science
        (6, 2), # FastAPI -> Backend
        (7, 3), # Pandas -> Data Science
        (8, 1)  # React -> Frontend
    ]

    resources_data = [
        (1, 'MDN - HTML Basics', 'https://developer.mozilla.org/en-US/docs/Web/HTML', 'article', True, True, 'Mozilla'),
        (2, 'freeCodeCamp - Learn CSS', 'https://www.freecodecamp.org/learn/responsive-web-design/', 'course', True, False, 'freeCodeCamp'),
        (3, 'JavaScript.info', 'https://javascript.info/', 'book', True, True, 'javascript.info'),
        (4, 'Official Python Tutorial', 'https://docs.python.org/3/tutorial/', 'book', True, True, 'Python Software Foundation'),
        (5, 'SQLBolt - Interactive SQL', 'https://sqlbolt.com/', 'course', True, False, 'SQLBolt'),
        (6, 'FastAPI Official Documentation', 'https://fastapi.tiangolo.com/', 'article', True, True, 'Tiangolo'),
        (7, 'Pandas Official User Guide', 'https://pandas.pydata.org/docs/user_guide/index.html', 'book', True, True, 'Pandas Core Team'),
        (8, 'React Official Tutorial', 'https://react.dev/learn', 'course', True, True, 'Meta')
    ]
    
    job_roles_data = [
        (1, 'Frontend Developer'),
        (2, 'Backend Developer (Python)')
    ]

    job_role_skills_data = [
        (1, 1), (1, 2), (1, 3), (1, 8), # Frontend Developer -> HTML, CSS, JS, React
        (2, 4), (2, 5), (2, 6) # Backend Developer -> Python, SQL, FastAPI
    ]


    # --- 3. تنفيذ أوامر SQL ---

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            print("Seeding data... (This will delete existing data in these tables)")

            # حذف البيانات بالترتيب العكسي لتجنب مشاكل المفاتيح الخارجية
            connection.execute(text("DELETE FROM job_role_skills;"))
            connection.execute(text("DELETE FROM skill_categories;"))
            connection.execute(text("DELETE FROM job_roles;"))
            connection.execute(text("DELETE FROM resources;"))
            connection.execute(text("DELETE FROM skills;"))
            connection.execute(text("DELETE FROM categories;"))

            # إدخال البيانات الجديدة
            connection.execute(text("INSERT INTO categories (id, name) VALUES (:id, :name)"), [{"id": d[0], "name": d[1]} for d in categories_data])
            connection.execute(text("INSERT INTO skills (id, name) VALUES (:id, :name)"), [{"id": d[0], "name": d[1]} for d in skills_data])
            connection.execute(text("INSERT INTO resources (id, title, url, type, is_free, is_official, author_or_platform) VALUES (:id, :title, :url, :type, :is_free, :is_official, :author)"), 
                               [{"id": d[0], "title": d[1], "url": d[2], "type": d[3], "is_free": d[4], "is_official": d[5], "author": d[6]} for d in resources_data])
            connection.execute(text("INSERT INTO job_roles (id, title) VALUES (:id, :title)"), [{"id": d[0], "title": d[1]} for d in job_roles_data])
            connection.execute(text("INSERT INTO skill_categories (skill_id, category_id) VALUES (:skill_id, :category_id)"), [{"skill_id": d[0], "category_id": d[1]} for d in skill_categories_data])
            connection.execute(text("INSERT INTO job_role_skills (job_role_id, skill_id) VALUES (:job_role_id, :skill_id)"), [{"job_role_id": d[0], "skill_id": d[1]} for d in job_role_skills_data])

            transaction.commit()
            print("✅ Database seeding completed successfully!")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            transaction.rollback()
            print("Database seeding failed. Transaction was rolled back.")

if __name__ == "__main__":
    seed_database()