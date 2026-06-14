# src/backend/create_admin.py
from backend.database import SessionLocal, engine
from backend.models import Profile, Base
from backend.auth import get_password_hash

# التأكد من وجود الجداول
Base.metadata.create_all(bind=engine)

def create_super_user():
    db = SessionLocal()
    try:
        email = "admin@skillsynth.com"
        password = "adminpassword123"
        
        # التحقق مما إذا كان موجوداً مسبقاً
        existing_user = db.query(Profile).filter(Profile.email == email).first()
        if existing_user:
            print(f"User {email} already exists!")
            return

        # إنشاء الأدمن
        new_admin = Profile(
            email=email,
            full_name="Super Admin",
            hashed_password=get_password_hash(password),
            is_admin=True,  # <--- هنا السحر
            subscription_tier="pro"
        )
        
        db.add(new_admin)
        db.commit()
        print(f"Success! Admin created.")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_super_user()