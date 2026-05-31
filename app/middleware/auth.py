from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

_PUBLIC = {"/healthz", "/docs", "/openapi.json", "/redoc"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.api_key or request.url.path in _PUBLIC:
            return await call_next(request)
        key = request.headers.get("X-API-Key", "")
        if key != settings.api_key:
            return JSONResponse(status_code=401, content={"error": "Invalid or missing API key"})
        return await call_next(request)
