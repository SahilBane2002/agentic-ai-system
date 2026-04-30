from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from app.tools import gcal_arcade as gcal  # <-- call wrapper module

class CalendarAgent:
    name = "calendar"

    async def find_slots(self, context: Dict[str, Any], window: str = "next_week"):
        today = datetime.now(timezone.utc)
        next_monday = (today + timedelta(days=(7 - today.weekday()))).replace(
            hour=13, minute=0, second=0, microsecond=0
        )
        start = next_monday
        end = (next_monday + timedelta(days=4)).replace(hour=22)

        attendees = context.get("attendees", [])
        tz = context.get("time_zone", "America/New_York")

        slots = await gcal.find_time_slots(
            start_iso=start.isoformat(),
            end_iso=end.isoformat(),
            duration_minutes=30,
            attendees=attendees,
            time_zone=tz,
        )
        context["proposed_times"] = slots
        return {"proposed_times": slots}
