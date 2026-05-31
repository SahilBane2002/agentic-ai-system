from fastapi import APIRouter
from sqlalchemy import text
from app.db import SessionLocal

router = APIRouter()


@router.get("/healthz")
async def healthz():
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "error"
    status = "ok" if db_status == "ok" else "degraded"
    return {"status": status, "db": db_status}
