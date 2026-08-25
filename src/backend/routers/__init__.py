from backend.routers import auth
from backend.routers import learning
from backend.routers import paths
from backend.routers import assessments
from backend.routers import analytics
from backend.routers import admin
from backend.routers import realtime

__all__ = [
    "auth", "learning", "paths", "assessments",
    "analytics", "admin", "realtime",
]
