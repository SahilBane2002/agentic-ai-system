from fastapi import APIRouter
from app.tools.gmail_arcade import authorize_gmail
from app.tools.gcal_arcade import authorize_calendar

router = APIRouter()

@router.get("/status")
async def auth_status():
    return {"connected": ["gmail? -> run /auth/gmail/start", "gcal? -> run /auth/calendar/start"]}

@router.get("/calendar/start")
async def calendar_start():
    try:
        return await authorize_calendar()
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get("/gmail/start")
async def gmail_start():
    try:
        return await authorize_gmail()
    except Exception as e:
        return {"status": "error", "error": str(e)}