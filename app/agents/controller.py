from typing import Dict, Any, List
from app.core.intents import classify, Intent

class ControllerAgent: 
    name = "controller"

    async def route(self, user_text: str) -> Dict[str, Any]:
        intent = classify(user_text)
        if intent == Intent.SCHEDULE:
            return { "agent": "calendar", "plan": [
                {"type": "calendar.find_slots", "payload": {"window": "next_week"}},
                {"type": "communication.draft_email", "payload": {"template": "propose_times"}},
                {"type": "communication.send_email", "payload": {}}
            ]}
        
        if intent == Intent.COMMUNICATE:
            return {"agent": "communication", "plan": [
                {"type": "communication.classify_inbox", "payload": {}},
                {"type": "communication.draft_email", "payload": {"template": "generic_reply"}}
            ]}
        if intent == Intent.RESEARCH:
            return {"agent": "research", "plan": [
                {"type": "research.web_search", "payload": {}},
                {"type": "research.summarize", "payload": {}}
            ]}
        return {"agent": "unknown", "plan": []}