from typing import Any, Dict, List, Iterable
from app.services.arcade import get_arcade_client, ARCADE_USER_ID

FIND_SLOTS_CANDIDATES: Iterable[str] = (
    "GoogleCalendar.FindTimeSlotsWhenEveryoneIsFree",
    "FindTimeSlotsWhenEveryoneIsFree",
)
CREATE_EVENT_CANDIDATES: Iterable[str] = (
    "GoogleCalendar.CreateEvent",  # you may not have this yet
    "CreateEvent",
    "UpdateEvent",                 # fallback
)

def _to_dict(x: Any) -> Dict[str, Any]:
    if hasattr(x, "to_dict"):
        return x.to_dict()
    return x if isinstance(x, dict) else {"raw": str(x)}

def _resolve_tool(candidates: Iterable[str]) -> str:
    client = get_arcade_client()
    last_err = None
    for name in candidates:
        try:
            res = client.tools.authorize(tool_name=name, user_id=ARCADE_USER_ID)
            _ = _to_dict(res)
            return name
        except Exception as e:
            last_err = e
    raise RuntimeError(f"No matching Calendar tool found. Tried: {list(candidates)}; last_error={last_err}")

async def authorize_calendar() -> Dict[str, Any]:
    client = get_arcade_client()
    tool = _resolve_tool(FIND_SLOTS_CANDIDATES)
    try:
        res = client.tools.authorize(tool_name=tool, user_id=ARCADE_USER_ID)
        data = _to_dict(res)
        status = data.get("status") or data.get("state") or "pending"
        url = data.get("url") or data.get("authorization_url")
        if status != "completed":
            return {"status": status, "url": url, "tool_name": tool}
        return {"status": "completed", "tool_name": tool}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def find_time_slots(start_iso: str, end_iso: str,
                          duration_minutes: int = 30,
                          attendees: List[str] | None = None,
                          time_zone: str = "America/New_York") -> List[Dict[str, Any]]:
    client = get_arcade_client()
    tool = _resolve_tool(FIND_SLOTS_CANDIDATES)
    payload = {
        "start": start_iso,
        "end": end_iso,
        "duration_minutes": duration_minutes,
        "participants": attendees or [],
        "time_zone": time_zone,
    }
    res = client.tools.execute(tool_name=tool, user_id=ARCADE_USER_ID, input=payload)
    data = _to_dict(res)
    out = data.get("output", data)

    # ---- NORMALIZE to: [{"start": ISO, "end": ISO}, ...] ----
    def normalize(o) -> List[Dict[str, Any]]:
        # Case A: dict with top-level "slots"
        if isinstance(o, dict) and "slots" in o and isinstance(o["slots"], list):
            return normalize(o["slots"])

        # Case B: dict with "value" -> "free_slots" (shape from your log)
        if isinstance(o, dict) and "value" in o and isinstance(o["value"], dict):
            v = o["value"]
            if "free_slots" in v and isinstance(v["free_slots"], list):
                return normalize(v["free_slots"])

        # Case C: already a list
        if isinstance(o, list):
            flat = []
            for s in o:
                if not isinstance(s, dict):
                    continue
                # C1: {"start":"...", "end":"..."}
                if "start" in s and isinstance(s["start"], str):
                    flat.append({"start": s["start"], "end": s.get("end")})
                    continue
                # C2: {"start":{"datetime":"..."}, "end":{"datetime":"..."}}
                if "start" in s and isinstance(s["start"], dict):
                    st = s["start"].get("datetime") or s["start"].get("start") or s["start"].get("iso")
                    en = s.get("end", {})
                    if isinstance(en, dict):
                        en = en.get("datetime") or en.get("end") or en.get("iso")
                    flat.append({"start": st, "end": en})
                    continue
            return [x for x in flat if x.get("start") and x.get("end")]

        # Fallback: unknown shape → return empty list
        return []

    slots = normalize(out)
    return slots

async def create_or_update_event(title: str, start_iso: str, end_iso: str,
                                 attendees: List[str] | None = None,
                                 location: str | None = None,
                                 description: str | None = None) -> Dict[str, Any]:
    client = get_arcade_client()
    tool = _resolve_tool(CREATE_EVENT_CANDIDATES)
    payload = {
        "summary": title,
        "start": start_iso,
        "end": end_iso,
        "attendees": attendees or [],
        "location": location,
        "description": description,
    }
    res = client.tools.execute(tool_name=tool, user_id=ARCADE_USER_ID, input=payload)
    data = _to_dict(res)
    return data.get("output", data)
