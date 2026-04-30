from fastapi import APIRouter
from typing import Dict, Any
from app.core.workflow import engine
from app.agents.controller import ControllerAgent
from app.agents.communication import CommunicationAgent
from app.agents.calendar import CalendarAgent
from app.agents.research import ResearchAgent
from app.core.memory import Memory
from app.tools.registry import registry
# from app.tools.gmail_mock import tool as gmail_tool
# from app.tools.gcal_mock import tool as gcal_tool
from app.tools.web_mock import tool as web_tool
# from app.tools.gmail_arcade import tool as gmail_tool
# from app.tools.gcal_arcade import tool as gcal_tool
# Register mock tools once
# if not registry.has("gmail"): registry.register(gmail_tool)
# if not registry.has("gcal"): registry.register(gcal_tool)
if not registry.has("web"): registry.register(web_tool)

# Bind workflow steps
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
    from app.agents.communication import CommunicationAgent
    return await CommunicationAgent().send_email(context)



router = APIRouter()

@router.post("/run")
async def run_workflow(payload: Dict[str, Any]):
    try:
        goal = payload.get("goal", "")
        context: Dict[str, Any] = payload.get("context", {})

        controller = ControllerAgent()
        route = await controller.route(goal)
        plan = route.get("plan", [])

        wf = await engine.run(name=f"wf:{route.get('agent','unknown')}", plan=plan, context=context)
 
        final = {}
        if route.get("agent") == "calendar":
            final = {"proposed_times": context.get("proposed_times", [])}
        elif route.get("agent") == "communication":
            final = {"inbox": "classified", "draft": "created"}
        elif route.get("agent") == "research":
            final = {"summary": context.get("summary", "")}

        return {"route": route, "workflow": wf.model_dump(), "final": final}
    except Exception as e:
        # Show the underlying error instead of a 500 HTML
        return {"status": "error", "error": str(e)}
