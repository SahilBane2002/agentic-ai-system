from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class Message(BaseModel):
    role: str
    content: str
    meta: Dict[str, Any] = {}

class Task(BaseModel):
    id: str
    type: str
    description: Optional[str] = ""     # ← add this line (default empty)
    state: str = "pending"
    payload: Dict[str, Any] = {}
    result: Optional[Dict[str, Any]] = None

class Workflow(BaseModel):
    id: str
    name: str
    status: str = "created"
    tasks: List[Task] = []
    