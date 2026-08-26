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

_DEFAULT_CORS_ORIGINS = {
    "prod": ["https://skillsynth.vercel.app"],
    "dev": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
}
# CORS_ORIGINS env (comma-separated) overrides the mode default in every
# environment; deployments should set it to their real front-end origins.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        ",".join(_DEFAULT_CORS_ORIGINS[APP_MODE])).split(",")
    if origin.strip()
]

CSRF_ENABLED = APP_MODE == "prod"
PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15

# ── SS-AI local LLM (ADR-015) ────────────────────────────────────────
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"
AI_MODEL_PATH = os.getenv(
    "AI_MODEL_PATH",
    "src/data/Llama-3.2-3B-Instruct-uncensored.Q6_K.gguf")
AI_N_GPU_LAYERS = int(os.getenv("AI_N_GPU_LAYERS", "-1"))
AI_N_CTX = int(os.getenv("AI_N_CTX", "4096"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))
AI_REPEAT_PENALTY = float(os.getenv("AI_REPEAT_PENALTY", "1.15"))
AI_TOP_P = float(os.getenv("AI_TOP_P", "0.95"))
AI_MAX_NEW_TOKENS = int(os.getenv("AI_MAX_NEW_TOKENS", "700"))
