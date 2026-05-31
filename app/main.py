import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings, validate_required_settings
from app.db import init_db
from app.middleware.auth import APIKeyMiddleware
from app.routers import health, workflows, auth

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "msg": %(message)s}',
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_required_settings()
    init_db()
    logger.info('"startup complete, env=%s"', settings.app_env)
    yield
    logger.info('"shutdown"')


app = FastAPI(title="Agentic AI System", version="1.0.0", lifespan=lifespan)

_cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(APIKeyMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    ms = (time.monotonic() - start) * 1000
    logger.info(
        '"method": "%s", "path": "%s", "status": %d, "ms": %.1f',
        request.method, request.url.path, response.status_code, ms,
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"error": "Internal server error", "detail": str(exc)})


app.include_router(health.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(workflows.router, prefix="/workflows")
