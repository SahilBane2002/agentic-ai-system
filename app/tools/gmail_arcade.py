# TOP OF FILE
from typing import Any, Dict, List, Iterable
from app.services.arcade import get_arcade_client, ARCADE_USER_ID

# ↓ Put YOUR dashboard names first (from the screenshot)
LIST_CANDIDATES: Iterable[str] = (
    "Gmail.ListEmails",
    "ListEmails",
)

DRAFT_CANDIDATES: Iterable[str] = (
    "Gmail.WriteDraftEmail",      # <-- create draft
    "WriteDraftEmail",
)

SEND_CANDIDATES: Iterable[str] = (
    "Gmail.SendDraftEmail",       # <-- send an existing draft
    "SendDraftEmail",
    "Gmail.SendEmail",            # <-- direct send (no draft)
    "SendEmail",
)

def _to_dict(x: Any) -> Dict[str, Any]:
    if hasattr(x, "to_dict"): return x.to_dict()
    return x if isinstance(x, dict) else {"raw": str(x)}

def _resolve_tool(cands: Iterable[str]) -> str:
    client = get_arcade_client()
    last_err = None
    for name in cands:
        try:
            client.tools.authorize(tool_name=name, user_id=ARCADE_USER_ID)
            return name
        except Exception as e:
            last_err = e
    raise RuntimeError(f"No matching Gmail tool found. Tried: {list(cands)}; last_error={last_err}")

def _auth_one(name: str) -> Dict[str, Any]:
    client = get_arcade_client()
    res = client.tools.authorize(tool_name=name, user_id=ARCADE_USER_ID)
    # res may have .status/.url or be dict-like; normalize:
    status = getattr(res, "status", None) or getattr(res, "state", None) or getattr(res, "get", lambda *_: None)("status") or "pending"
    url = getattr(res, "url", None) or getattr(res, "authorization_url", None) or getattr(res, "get", lambda *_: None)("url")
    return {"tool": name, "status": status, "url": url}

async def authorize_gmail() -> Dict[str, Any]:
    # Authorize every tool we might call
    groups: List[Iterable[str]] = [LIST_CANDIDATES, DRAFT_CANDIDATES, SEND_CANDIDATES]
    attempts: List[Dict[str, Any]] = []
    for group in groups:
        for candidate in group:
            try:
                attempts.append(_auth_one(candidate))
                break  # first resolvable in this group is enough
            except Exception as e:
                attempts.append({"tool": candidate, "status": "error", "error": str(e)})
                continue

    # If any are pending, return the first with a URL so you can complete OAuth
    for a in attempts:
        if a.get("status") != "completed" and a.get("url"):
            return {"status": "pending", "tool": a["tool"], "url": a["url"], "details": attempts}

    # Completed or errors
    done = all(a.get("status") == "completed" for a in attempts if "status" in a)
    return {"status": "completed" if done else "partial", "details": attempts}



async def list_emails(q: str = "in:inbox newer_than:7d") -> List[Dict[str, Any]]:
    client = get_arcade_client()
    name = _resolve_tool(LIST_CANDIDATES)
    res = client.tools.execute(tool_name=name, user_id=ARCADE_USER_ID, input={"query": q})
    data = _to_dict(res)
    out = data.get("output", data)
    return out.get("emails", out)

async def create_draft(recipient: str, subject: str, body: str) -> Dict[str, Any]:
    client = get_arcade_client()
    name = _resolve_tool(DRAFT_CANDIDATES)
    # Arcade's WriteDraftEmail@3.3.0 expects "recipient"
    payload = {"recipient": recipient, "subject": subject, "body": body}
    res = client.tools.execute(tool_name=name, user_id=ARCADE_USER_ID, input=payload)
    data = _to_dict(res)
    return data.get("output", data)

async def send_email(
    draft_id: str | None = None,            # backward-compat
    email_id: str | None = None,            # SendDraftEmail expects this
    recipient: str | None = None,
    subject: str | None = None,
    body: str | None = None
) -> Dict[str, Any]:
    client = get_arcade_client()
    name = _resolve_tool(SEND_CANDIDATES)

    # Normalize: if caller gave draft_id, treat it as email_id
    if not email_id and draft_id:
        email_id = draft_id

    if "SendDraftEmail" in name or name.endswith(".SendDraftEmail"):
        if not email_id:
            raise ValueError("email_id is required to send a draft email")
        payload = {"email_id": email_id}   # <-- required by Arcade
    else:
        # Direct send (no draft) path
        payload = {"recipient": recipient, "subject": subject, "body": body}

    res = client.tools.execute(tool_name=name, user_id=ARCADE_USER_ID, input=payload)
    data = _to_dict(res)
    return data.get("output", data)
