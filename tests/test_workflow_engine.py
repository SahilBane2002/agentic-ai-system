import pytest
from app.core.workflow import WorkflowEngine


@pytest.fixture
def wf_engine():
    e = WorkflowEngine()

    @e.step("test.add")
    async def add(context, x=0, y=0):
        context["result"] = x + y
        return {"sum": x + y}

    @e.step("test.fail")
    async def fail(context):
        raise ValueError("intentional")

    return e


@pytest.mark.asyncio
async def test_step_executes_and_returns_done(wf_engine):
    ctx = {}
    wf = await wf_engine.run("t", [{"type": "test.add", "payload": {"x": 2, "y": 3}}], ctx)
    assert wf.status == "done"
    assert wf.tasks[0].state == "done"
    assert ctx["result"] == 5


@pytest.mark.asyncio
async def test_unknown_step_is_skipped(wf_engine):
    wf = await wf_engine.run("t", [{"type": "nonexistent", "payload": {}}], {})
    assert wf.status == "done"
    assert wf.tasks[0].state == "skipped"


@pytest.mark.asyncio
async def test_failing_step_marks_workflow_error(wf_engine):
    wf = await wf_engine.run("t", [{"type": "test.fail", "payload": {}}], {})
    assert wf.status == "error"
    assert wf.tasks[0].state == "error"
    assert "intentional" in wf.tasks[0].result["error"]


@pytest.mark.asyncio
async def test_error_aborts_remaining_steps(wf_engine):
    plan = [
        {"type": "test.fail", "payload": {}},
        {"type": "test.add", "payload": {"x": 1, "y": 1}},
    ]
    wf = await wf_engine.run("t", plan, {})
    assert wf.status == "error"
    assert wf.tasks[0].state == "error"
    # engine breaks on first error — second task is never created
    assert len(wf.tasks) == 1
