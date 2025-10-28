import os
import sys
from dotenv import load_dotenv
import uvicorn

# 1. تحميل متغيرات البيئة
load_dotenv()

# 2. إصلاح المسار
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)
os.environ["PYTHONPATH"] = SRC_PATH

# 3. إعدادات الخادم
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("MODE", "prod").lower() == "dev"

# 4. تشغيل Uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info"
    )
