# data/learning_paths/db_connector.py (إصدار متقدم بافتراض وجود جدول وسيط)

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def fetch_resources_by_skill_name(skill_name: str) -> list:
    """
    يجلب كل الموارد المرتبطة باسم مهارة معين
    عن طريق ربط (JOIN) جداول skills, skill_resources, و resources.
    """
    # هذا هو الاستعلام الصحيح الذي يربط ثلاثة جداول معًا
    # 1. يجد الـ skill_id من جدول skills بناءً على الاسم.
    # 2. يستخدم الـ skill_id ليجد كل الـ resource_id المرتبطة به في skill_resources.
    # 3. يستخدم الـ resource_id ليجلب معلومات المورد الكاملة من جدول resources.
    query = text("""
        SELECT r.*
        FROM resources r
        JOIN skill_resources sr ON r.id = sr.resource_id
        JOIN skills s ON s.id = sr.skill_id
        WHERE s.name ILIKE :name
    """)
    
    resources = []
    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"name": skill_name})
            for row in result:
                resources.append(dict(row._mapping))
    except Exception as e:
        # من المهم جدًا طباعة الخطأ لنعرف إذا كان افتراضنا لأسماء الجداول صحيحًا
        print(f"ERROR fetching resources for skill '{skill_name}': {e}")
        print("Please check if the table names 'skill_resources', 'resources', 'skills' and their column names are correct.")

    return resources