import os
from dotenv import load_dotenv

load_dotenv()

"""backend.config.app_settings — runtime configuration for SkillSynth.

Reads environment variables (optionally from a .env file via python-dotenv)
at import time and exposes them as module-level constants used throughout the
backend. SS-AI (local LLM) settings are OPTIONAL: llama-cpp-python is no longer
a core dependency and is installed separately via requirements-ai.txt or
`pip install -e ".[ai]"`. See ADR-015.
"""

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
# All SS-AI settings are OPTIONAL. The llama-cpp-python dependency is no
# longer a core requirement (removed from requirements.txt); install it via
# requirements-ai.txt or `pip install -e ".[ai]"`. When ai deps are absent the
# app runs normally with AI_ENABLED effectively disabled (gate returns 503).
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"
"""bool: SS-AI feature gate. Env var AI_ENABLED (default "false"). When false,
the /api/ai/* endpoints return 503 and no LLM is loaded. llama-cpp-python is
optional."""
AI_MODEL_PATH = os.getenv(
    "AI_MODEL_PATH",
    "src/data/Llama-3.2-3B-Instruct-Q6_K.gguf")
"""str: GGUF model path used by the local LLM. Env var AI_MODEL_PATH (default
"src/data/Llama-3.2-3B-Instruct-Q6_K.gguf"). Only required when AI_ENABLED is
true; llama-cpp-python is optional."""
AI_N_GPU_LAYERS = int(os.getenv("AI_N_GPU_LAYERS", "-1"))
"""int: GPU layers offloaded to llama.cpp. Env var AI_N_GPU_LAYERS (default -1,
all). No effect without optional llama-cpp-python."""
AI_N_CTX = int(os.getenv("AI_N_CTX", "4096"))
"""int: LLM context window size. Env var AI_N_CTX (default 4096). Optional."""
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))
"""float: sampling temperature. Env var AI_TEMPERATURE (default 0.3). Optional."""
AI_REPEAT_PENALTY = float(os.getenv("AI_REPEAT_PENALTY", "1.15"))
"""float: repetition penalty. Env var AI_REPEAT_PENALTY (default 1.15). Optional."""
AI_TOP_P = float(os.getenv("AI_TOP_P", "0.95"))
"""float: nucleus sampling cutoff. Env var AI_TOP_P (default 0.95). Optional."""
AI_MAX_NEW_TOKENS = int(os.getenv("AI_MAX_NEW_TOKENS", "700"))
"""int: max tokens generated per response. Env var AI_MAX_NEW_TOKENS (default
700). Optional."""
