import json
import re
from typing import Dict, Any

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings
from app.core.intents import classify, Intent

SYSTEM_PROMPT = """You are a task routing assistant for an agentic AI system.
Given a user goal, respond with a JSON object (no markdown, no explanation) that has:
- "agent": one of "calendar", "communication", "research", or "unknown"
- "plan": an ordered list of steps to fulfill the goal

Available step types and their payloads:
  calendar.find_slots           payload: {"window": "next_week"}
  communication.classify_inbox  payload: {}
  communication.draft_email     payload: {"template": "propose_times" | "generic_reply"}
  communication.send_email      payload: {}
  research.web_search           payload: {}
  research.summarize            payload: {}

Rules:
- Scheduling / meetings → calendar agent; always end with draft + send email steps
- Email / inbox / reply → communication agent
- Research / summarize / pricing / report → research agent
- Only include steps relevant to the goal
- Return valid JSON only"""

FALLBACK_PLANS: Dict[Intent, Dict[str, Any]] = {
    Intent.SCHEDULE: {
        "agent": "calendar",
        "plan": [
            {"type": "calendar.find_slots", "payload": {"window": "next_week"}},
            {"type": "communication.draft_email", "payload": {"template": "propose_times"}},
            {"type": "communication.send_email", "payload": {}},
        ],
    },
    Intent.COMMUNICATE: {
        "agent": "communication",
        "plan": [
            {"type": "communication.classify_inbox", "payload": {}},
            {"type": "communication.draft_email", "payload": {"template": "generic_reply"}},
        ],
    },
    Intent.RESEARCH: {
        "agent": "research",
        "plan": [
            {"type": "research.web_search", "payload": {}},
            {"type": "research.summarize", "payload": {}},
        ],
    },
    Intent.UNKNOWN: {"agent": "unknown", "plan": []},
}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
async def _call_groq(user_text: str) -> Dict[str, Any]:
    from app.services.groq_client import get_groq_client

    client = get_groq_client()
    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0,
        max_tokens=512,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


class ControllerAgent:
    name = "controller"

    async def route(self, user_text: str) -> Dict[str, Any]:
        if settings.groq_api_key:
            try:
                return await _call_groq(user_text)
            except Exception:
                pass
        return self._route_with_keywords(user_text)

    def _route_with_keywords(self, user_text: str) -> Dict[str, Any]:
        intent = classify(user_text)
        return FALLBACK_PLANS.get(intent, FALLBACK_PLANS[Intent.UNKNOWN])
