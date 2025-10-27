# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# رابط الاتصال بقاعدة البيانات.
# الصيغة: "postgresql://USER:PASSWORD@HOST/DB_NAME"
# مثال: سنستخدم قاعدة بيانات SQLite مؤقتة للتسهيل في البداية.
# SQLite لا تتطلب خادم، هي مجرد ملف.
SQLALCHEMY_DATABASE_URL = "sqlite:///./skillsynth.db"

# لـ PostgreSQL سيكون الرابط هكذا (سنستخدمه لاحقاً):
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# 1. إنشاء "المحرّك" - هو نقطة الاتصال الأساسية مع قاعدة البيانات.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # هذا السطر خاص بـ SQLite فقط
)

# 2. إنشاء "جلسة" - كل جلسة هي محادثة مستقلة مع قاعدة البيانات.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. إنشاء "الأساس" - سنستخدم هذا الكلاس لترث منه كل نماذج الجداول في models.py
Base = declarative_base()