from typing import Dict, Any
from app.tools import gmail_arcade as gmail  # <-- call wrapper module

class CommunicationAgent:
    name = "communication"

    async def classify_inbox(self, context: Dict[str, Any]):
        emails = await gmail.list_emails()
        labeled = []
        for e in emails:
            subj = (e.get("subject") or "").lower()
            if "meet" in subj:
                label = "meeting"
            elif "news" in subj or "newsletter" in subj:
                label = "newsletter"
            else:
                label = "other"
            labeled.append({**e, "label": label})
        return labeled

    async def draft_email(self, context: Dict[str, Any], template: str = "generic_reply"):
        recipient = context.get("recipient", "alex@example.com")
        if template == "propose_times":
            times = context.get("proposed_times", [])
            body = "Hi Alex, here are a few options:\n" + "\n".join(
                f"- {t['start']} to {t['end']}" for t in times
            )
            subject = "Proposed meeting times"
        else:
            subject = "Re: Your email"
            body = "Thanks for reaching out—see my notes below."

        draft = await gmail.create_draft(recipient=recipient, subject=subject, body=body)

        # capture the id regardless of shape (value.id, id, draft_id)
        draft_id = (
            (draft.get("value") or {}).get("id")
            or draft.get("id")
            or draft.get("draft_id")
        )
        if draft_id:
            context["last_email_id"] = draft_id   # <-- use email_id wording
        return draft


    async def send_email(self, context: Dict[str, Any]):
        email_id = context.get("last_email_id")  # set by draft step
        if email_id:
            return await gmail.send_email(email_id=email_id)
        # fallback: send directly if no draft_id found
        return await gmail.send_email(
            recipient=context.get("recipient"),
            subject=context.get("subject", "Follow-up"),
            body=context.get("body", "Following up on our meeting.")
        )