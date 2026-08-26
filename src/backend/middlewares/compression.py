import asyncio
import gzip
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class CompressionMiddleware(BaseHTTPMiddleware):
    MIN_SIZE = 1024

    async def dispatch(self, request: Request, call_next):
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return await call_next(request)

        response: Response = await call_next(request)

        if not hasattr(response, "body"):
            return response

        if len(response.body) < self.MIN_SIZE:
            return response

        if response.headers.get("Content-Encoding"):
            return response

        if response.media_type and not response.media_type.startswith(("text/", "application/json", "application/javascript")):
            return response

        try:
            compressed = await asyncio.to_thread(gzip.compress, response.body, compresslevel=6)
            if len(compressed) < len(response.body):
                return Response(
                    content=compressed,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
        except Exception:
            pass

        return response
