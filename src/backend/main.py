"""SkillSynth application factory.

Wires the seven Task-3 routers onto the reduced 15-table core, applies
security/compression/CORS/CSRF middleware, exposes the root welcome JSON,
the cached /api/public/stats (30s TTL inline dict), /api/auth/csrf and the
/api/events SSE alias. Lifespan creates tables and auto-seeds the admin
user when ADMIN_PASSWORD is set (no scheduler — infrastructure deleted).
"""

import logging
import os
import secrets
import threading
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config.app_settings import APP_MODE, CORS_ORIGINS, CSRF_ENABLED
from backend.database import SessionLocal, engine, get_db
from backend.entities.base import Base
from backend.entities.catalog import Resource, Skill
from backend.entities.identity import User
from backend.entities.learning import Path
from backend.events.publisher import event_generator
from backend.limiter import limiter
from backend.middlewares.compression import CompressionMiddleware
from backend.middlewares.csrf import CSRFMiddleware
from backend.middlewares.security import SecurityHeadersMiddleware
from backend.repositories import identity_repository
from backend.routers import admin, analytics, assessments, auth, catalog, catalog_admin
from backend.routers import ai, evaluations_admin, learning, paths, realtime
from backend.services import llm_engine, settings_schema, settings_service
from backend.services.auth_service import decode_token, hash_password

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Inline public-stats cache (replaces the deleted cache/SimpleCache layer).
_stats_cache: dict[str, Any] = {"value": None, "ts": 0.0}
_stats_lock = threading.Lock()
_STATS_TTL = 30


def _public_stats(db: Session) -> dict:
    """Compute the four public counters from the reduced schema."""
    return {
        "users": db.query(func.count(User.id)).scalar() or 0,
        "skills": db.query(func.count(Skill.id)).scalar() or 0,
        "paths": db.query(func.count(Path.id)).scalar() or 0,
        "resources": db.query(func.count(Resource.id)).scalar() or 0,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the 15 tables, mirror the rate_limiting flag onto slowapi,
    then auto-create the admin user when needed."""
    Base.metadata.create_all(bind=engine)
    limiter.enabled = bool(settings_schema.get_runtime_flag("rate_limiting"))
    admin_email = os.getenv("ADMIN_EMAIL", "admin@skillsynth.io")
    admin_pw = os.getenv("ADMIN_PASSWORD", "")
    db = SessionLocal()
    try:
        if not identity_repository.get_by_email(db, admin_email) and admin_pw:
            identity_repository.create(
                db, email=admin_email, hashed_password=hash_password(admin_pw),
                full_name="Super Admin", is_admin=True)
            logger.info("Admin user created: %s", admin_email)
    finally:
        db.close()
    if settings_service.is_ai_enabled():

        def _warmup_async() -> None:
            """Warm the SS-AI engine off the request path.

            Called by a daemon thread at startup; delegates to llm_engine.
            warmup() and logs non-fatally so the app starts serving instantly
            while the model loads in the background (single-purpose wrapper).
            """
            try:
                if not llm_engine.warmup():
                    logger.warning(
                        "SS-AI warmup did not complete at startup; the model "
                        "will lazy-load on the first AI request when VRAM frees.")
            except Exception as exc:  # noqa: BLE001 — non-fatal startup step
                logger.warning("SS-AI warmup error (non-fatal): %s", exc)

        threading.Thread(target=_warmup_async, daemon=True).start()
    yield


app = FastAPI(title="SkillSynth API", lifespan=lifespan)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Requested-With"],
    expose_headers=["X-Request-ID"],
    max_age=600,
)
app.add_middleware(CompressionMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
if CSRF_ENABLED:
    app.add_middleware(CSRFMiddleware)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(learning.router, prefix="/api/learning", tags=["Learning Engine"])
app.include_router(paths.router, prefix="/api", tags=["Paths & Progress"])
app.include_router(assessments.router, prefix="/api", tags=["Assessments"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(catalog_admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(evaluations_admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(realtime.router, prefix="/api/realtime", tags=["Real-time"])
app.include_router(ai.router, prefix="/api", tags=["AI"])


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom 429 JSON for slowapi limit breaches."""
    return JSONResponse(status_code=429,
                        content={"detail": "Rate limit exceeded. Please try again later."})


@app.exception_handler(IntegrityError)
def integrity_conflict_handler(request: Request, exc: IntegrityError):
    """Central safety net: uncaught DB constraint breaches become 409.

    Fires when malformed input slips past service validation (e.g.
    duplicate job_role_skills junction rows); the request-scoped session
    rolls back when the get_db dependency closes it."""
    logger.warning("Integrity conflict on %s %s: %s",
                   request.method, request.url.path,
                   getattr(exc, "orig", exc))
    return JSONResponse(
        status_code=409,
        content={"detail": "Database conflict: the operation violates a "
                           "data constraint."})


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Flatten pydantic errors into a single detail string + body."""
    messages = [e.get("msg", str(e)) for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(messages) if messages else "Validation error"})


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    """Log and return a generic 500 (no internals leaked)."""
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def read_root():
    """Root welcome JSON."""
    return {"message": "Welcome to SkillSynth API", "version": "1.0.0",
            "status": "operational"}


@app.get("/api/public/stats")
def public_stats(db: Session = Depends(get_db)):
    """Public counters, cached in-process for 30s (TTL dict + lock)."""
    now = time.time()
    with _stats_lock:
        if _stats_cache["value"] is None or (now - _stats_cache["ts"]) > _STATS_TTL:
            _stats_cache["value"] = _public_stats(db)
            _stats_cache["ts"] = now
        return _stats_cache["value"]


@app.get("/api/auth/csrf")
def get_csrf_token(request: Request):
    """Issue a CSRF token cookie + body (also consumed by tests)."""
    token = secrets.token_hex(32)
    response = JSONResponse({"csrf_token": token})
    response.set_cookie(
        key="csrf_token", value=token, httponly=False, samesite="strict",
        secure=APP_MODE == "prod", max_age=3600, path="/")
    return response


@app.get("/api/events")
async def sse_events(request: Request, token: str | None = None):
    """SSE alias forwarding the publisher stream for a token's user.

    Accepts the 24h access token (integer `user_id` claim) or the
    5-minute SSE token (numeric `sub`); mirrors realtime._extract_profile_id.
    When real_time_updates is off the stream stays open but the generator
    drops data frames (quiet-but-open).
    """
    raw = token or request.headers.get("Authorization", "").replace("Bearer ", "")
    if not raw:
        raw = request.cookies.get("authToken", "")
    if not raw:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(raw)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    if user_id is None:
        sub = payload.get("sub")
        if sub is None or not str(sub).isdigit():
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = int(sub)
    quiet = not settings_schema.get_runtime_flag("real_time_updates")
    return StreamingResponse(
        event_generator(int(user_id), quiet=quiet),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive",
                 "X-Accel-Buffering": "no"})
