from fastapi import FastAPI
from app.routers import health, workflows, auth

app = FastAPI(title="Agentic AI System — MVP", version="0.0.1")
app.include_router(health.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(workflows.router, prefix="/workflows")