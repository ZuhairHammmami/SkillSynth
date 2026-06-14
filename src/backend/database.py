# src/backend/database.py

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# --- الخطوة 1: تحميل متغيرات البيئة من ملف .env ---
# هذا السطر يبحث عن ملف .env في المجلد الرئيسي ويقوم بتحميل محتوياته
# كمتغيرات بيئة يمكن الوصول إليها عبر os.getenv()
load_dotenv()

# --- الخطوة 2: تحديد رابط قاعدة البيانات بذكاء ---
# نقرأ متغير MODE من ملف .env. إذا لم يكن موجودًا، نعتبره 'dev'.
APP_MODE = os.getenv("MODE", "dev").lower()

# نقرأ رابط قاعدة بيانات PostgreSQL.
DATABASE_URL_PROD = os.getenv("DATABASE_URL")

# نحدد قاعدة البيانات التي سنستخدمها.
if APP_MODE == "prod" and DATABASE_URL_PROD:
    # في وضع الإنتاج، نستخدم PostgreSQL.
    print("INFO:     Connecting to PostgreSQL database...")
    SQLALCHEMY_DATABASE_URL = DATABASE_URL_PROD
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # في وضع التطوير (أو إذا كان الرابط غير موجود)، نستخدم SQLite.
    print("INFO:     Using local SQLite database...")
    # يجب تحديد المسار الكامل لملف قاعدة البيانات لضمان عدم حدوث أخطاء
    # عند تشغيل التطبيق من أماكن مختلفة.
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    DB_PATH = os.path.join(PROJECT_ROOT, "skillsynth.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# --- الخطوة 3: إعداد جلسات قاعدة البيانات (يبقى كما هو) ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency Injection for database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()