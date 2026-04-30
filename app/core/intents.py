from enum import Enum

class Intent(str, Enum):
    SCHEDULE = "schedule"
    COMMUNICATE = "communicate"
    RESEARCH = "research"
    UNKNOWN = "unknown"

KEYS = {
    Intent.SCHEDULE: ["schedule", "meeting", "calendar", "book", "invite"],
    Intent.COMMUNICATE: ["email", "reply", "respond", "compose"],
    Intent.RESEARCH: ["research", "report", "summarize", "pricing"],
}

def classify(text: str) -> Intent:
    t = text.lower()
    for intent, keys in KEYS.items():
        if any(k in t for k in keys):
            return intent
    return Intent.UNKNOWN