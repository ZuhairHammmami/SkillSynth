import os
import secrets
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

MODE = os.getenv("MODE", "dev")
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.method in SAFE_METHODS:
            response: Response = await call_next(request)
            if MODE == "prod" and request.url.path not in ("/api/auth/csrf",):
                token = secrets.token_hex(32)
                response.set_cookie(
                    key=CSRF_COOKIE_NAME,
                    value=token,
                    httponly=False,
                    samesite="strict",
                    secure=MODE == "prod",
                    max_age=3600,
                    path="/",
                )
            return response

        if MODE == "prod":
            csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)
            csrf_header = request.headers.get(CSRF_HEADER_NAME)

            if not csrf_cookie or not csrf_header:
                raise HTTPException(status_code=403, detail="CSRF token missing")

            if not secrets.compare_digest(csrf_cookie, csrf_header):
                raise HTTPException(status_code=403, detail="CSRF token mismatch")

        response: Response = await call_next(request)
        return response
