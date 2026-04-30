from typing import Any, List, Dict

class GmailMock:
    name = "gmail"
    async def run(self, **kwargs) -> Any:
        action = kwargs.get("action")
        if action == "classify":
            # naive classifier output
            return [{"id": "m1", "subject": "Meeting request", "label": "meeting"}, {"id": "m2", "subject": "Newsletter", "label": "newsletter"}]
        if action == "draft":
            to = kwargs.get("to", "someone@example.com")
            body = kwargs.get("body", "")
            return {"draft_id": "d1", "to": to, "body": body}
        return {"ok": True}

tool = GmailMock()