from typing import Any, List

class GCalMock:
    name = "gcal"
    async def run(self, **kwargs) -> Any:
        action = kwargs.get("action")
        if action == "freebusy":
            # pretend three open slots next week
            return [
                {"start": "2025-11-03T15:00:00Z", "end": "2025-11-03T15:30:00Z"},
                {"start": "2025-11-04T16:00:00Z", "end": "2025-11-04T16:30:00Z"},
                {"start": "2025-11-05T17:00:00Z", "end": "2025-11-05T17:30:00Z"},
            ]
        if action == "create":
            return {"event_id": "e1", "status": "created"}
        return {"ok": True}

tool = GCalMock()