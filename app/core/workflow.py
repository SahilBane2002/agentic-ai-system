import uuid
from typing import Dict, Any, List

from app.models import Workflow, Task
from app.core.memory import shared_memory


class WorkflowEngine:
    def __init__(self):
        self._registry: Dict[str, callable] = {}

    def step(self, name: str):
        def deco(fn):
            self._registry[name] = fn
            return fn
        return deco

    async def run(self, name: str, plan: List[Dict[str, Any]], context: Dict[str, Any]):
        context.setdefault("_memory", shared_memory)

        wf = Workflow(id=str(uuid.uuid4()), name=name, tasks=[])
        for s in plan:
            t = Task(id=str(uuid.uuid4()), type=s["type"], payload=s.get("payload", {}))
            wf.tasks.append(t)
            handler = self._registry.get(s["type"])
            if not handler:
                t.state = "skipped"
                t.result = {"reason": "no handler found"}
                continue
            try:
                t.state = "running"
                t.result = await handler(context=context, **t.payload)
                t.state = "done"
            except Exception as e:
                t.state = "error"
                t.result = {"error": str(e)}
                break

        wf.status = "done" if all(t.state in ("done", "skipped") for t in wf.tasks) else "error"
        return wf


engine = WorkflowEngine()
