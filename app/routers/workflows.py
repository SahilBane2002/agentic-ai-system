import logging
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.core.workflow import engine
from app.agents.controller import ControllerAgent
from app.agents.communication import CommunicationAgent
from app.agents.calendar import CalendarAgent
from app.agents.research import ResearchAgent
from app.db import get_db, WorkflowORM, TaskORM
from app.tools.registry import registry
from app.tools.web_search import tool as web_tool

if not registry.has("web"):
    registry.register(web_tool)

# Register mock Gmail/Calendar tools when Arcade is not configured so the
# system degrades gracefully instead of crashing at runtime.
if not settings.arcade_enabled:
    from app.tools.gmail_mock import tool as gmail_mock_tool
    from app.tools.gcal_mock import tool as gcal_mock_tool
    if not registry.has("gmail"):
        registry.register(gmail_mock_tool)
    if not registry.has("gcal"):
        registry.register(gcal_mock_tool)

logger = logging.getLogger("app.workflows")


@engine.step("communication.classify_inbox")
async def step_comm_classify(context: Dict[str, Any]):
    return await CommunicationAgent().classify_inbox(context)


@engine.step("communication.draft_email")
async def step_comm_draft(context: Dict[str, Any], template: str = "generic_reply"):
    return await CommunicationAgent().draft_email(context, template=template)


@engine.step("calendar.find_slots")
async def step_cal_find(context: Dict[str, Any], window: str = "next_week"):
    return await CalendarAgent().find_slots(context, window=window)


@engine.step("research.web_search")
async def step_research_search(context: Dict[str, Any]):
    return await ResearchAgent().web_search(context)


@engine.step("research.summarize")
async def step_research_summarize(context: Dict[str, Any]):
    return await ResearchAgent().summarize(context)


@engine.step("communication.send_email")
async def step_comm_send(context: Dict[str, Any]):
    return await CommunicationAgent().send_email(context)


router = APIRouter()


def _orm_to_dict(record: WorkflowORM) -> Dict[str, Any]:
    return {
        "id": record.id,
        "name": record.name,
        "status": record.status,
        "goal": record.goal,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "tasks": [
            {
                "id": t.id,
                "type": t.type,
                "state": t.state,
                "payload": t.payload,
                "result": t.result,
            }
            for t in record.tasks
        ],
    }


def _persist(db: Session, wf, goal: str) -> None:
    record = WorkflowORM(id=wf.id, name=wf.name, status=wf.status, goal=goal)
    for t in wf.tasks:
        record.tasks.append(
            TaskORM(
                id=t.id, workflow_id=wf.id, type=t.type,
                state=t.state, payload=t.payload, result=t.result,
            )
        )
    db.add(record)
    db.commit()


@router.post("/run")
async def run_workflow(payload: Dict[str, Any], db: Session = Depends(get_db)):
    goal = payload.get("goal", "").strip()
    if not goal:
        raise HTTPException(status_code=400, detail="goal is required")

    context: Dict[str, Any] = payload.get("context", {})

    controller = ControllerAgent()
    route = await controller.route(goal)
    plan = route.get("plan", [])

    wf = await engine.run(name=f"wf:{route.get('agent', 'unknown')}", plan=plan, context=context)

    try:
        _persist(db, wf, goal)
    except Exception:
        logger.exception("Failed to persist workflow %s", wf.id)

    final: Dict[str, Any] = {}
    if route.get("agent") == "calendar":
        final = {"proposed_times": context.get("proposed_times", [])}
    elif route.get("agent") == "communication":
        final = {"inbox": "classified", "draft": "created"}
    elif route.get("agent") == "research":
        final = {"summary": context.get("summary", "")}

    return {"route": route, "workflow": wf.model_dump(), "final": final}


@router.get("", response_model=List[Dict[str, Any]])
def list_workflows(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    records = (
        db.query(WorkflowORM)
        .order_by(WorkflowORM.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_orm_to_dict(r) for r in records]


@router.get("/{workflow_id}", response_model=Dict[str, Any])
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    record = db.get(WorkflowORM, workflow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _orm_to_dict(record)
