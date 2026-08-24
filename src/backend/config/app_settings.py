import os
from dotenv import load_dotenv

load_dotenv()

APP_MODE = os.getenv("MODE", "dev").lower()

if APP_MODE == "prod":
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production mode")
else:
    SECRET_KEY = os.getenv("SECRET_KEY", "a-secure-default-secret-key-for-development")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

if APP_MODE == "prod":
    CORS_ORIGINS = [
        "https://skillsynth.vercel.app",
    ]
else:
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

CSRF_ENABLED = APP_MODE == "prod"
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15
