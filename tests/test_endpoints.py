from unittest.mock import AsyncMock, patch


def test_health(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] in ("ok", "degraded")


def test_run_workflow_missing_goal(client):
    r = client.post("/workflows/run", json={})
    assert r.status_code == 400
    assert "goal" in r.json()["detail"]


def test_run_workflow_research(client):
    mock_route = {
        "agent": "research",
        "plan": [
            {"type": "research.web_search", "payload": {}},
            {"type": "research.summarize", "payload": {}},
        ],
    }
    mock_search = [{"title": "T", "url": "http://x.com", "snippet": "s"}]

    with (
        patch("app.agents.controller.ControllerAgent.route", new=AsyncMock(return_value=mock_route)),
        patch("app.tools.web_search.WebSearch.run", new=AsyncMock(return_value=mock_search)),
    ):
        r = client.post(
            "/workflows/run",
            json={"goal": "research competitor pricing", "context": {"query": "pricing"}},
        )

    assert r.status_code == 200
    data = r.json()
    assert data["route"]["agent"] == "research"
    assert data["workflow"]["status"] == "done"


def test_run_workflow_unknown_intent(client):
    mock_route = {"agent": "unknown", "plan": []}

    with patch("app.agents.controller.ControllerAgent.route", new=AsyncMock(return_value=mock_route)):
        r = client.post("/workflows/run", json={"goal": "do something vague"})

    assert r.status_code == 200
    assert r.json()["route"]["agent"] == "unknown"


# ---------------------------------------------------------------------------
# GET /workflows  &  GET /workflows/{id}
# ---------------------------------------------------------------------------

def test_list_workflows_empty(client):
    r = client.get("/workflows")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_and_get_workflow(client):
    mock_route = {
        "agent": "research",
        "plan": [
            {"type": "research.web_search", "payload": {}},
            {"type": "research.summarize", "payload": {}},
        ],
    }
    mock_search = [{"title": "T", "url": "http://x.com", "snippet": "s"}]

    with (
        patch("app.agents.controller.ControllerAgent.route", new=AsyncMock(return_value=mock_route)),
        patch("app.tools.web_search.WebSearch.run", new=AsyncMock(return_value=mock_search)),
    ):
        run_r = client.post(
            "/workflows/run",
            json={"goal": "find latest AI news", "context": {"query": "AI news"}},
        )
    assert run_r.status_code == 200
    wf_id = run_r.json()["workflow"]["id"]

    list_r = client.get("/workflows")
    assert list_r.status_code == 200
    ids = [w["id"] for w in list_r.json()]
    assert wf_id in ids

    get_r = client.get(f"/workflows/{wf_id}")
    assert get_r.status_code == 200
    data = get_r.json()
    assert data["id"] == wf_id
    assert data["goal"] == "find latest AI news"
    assert "tasks" in data


def test_get_workflow_not_found(client):
    r = client.get("/workflows/nonexistent-id")
    assert r.status_code == 404


def test_list_workflows_pagination(client):
    r = client.get("/workflows?limit=1&offset=0")
    assert r.status_code == 200
    assert len(r.json()) <= 1


# ---------------------------------------------------------------------------
# Auth middleware
# ---------------------------------------------------------------------------

def test_auth_middleware_blocks_without_key(client, monkeypatch):
    monkeypatch.setattr("app.middleware.auth.settings", type("S", (), {"api_key": "secret"})())
    r = client.get("/workflows")
    assert r.status_code == 401


def test_auth_middleware_passes_with_correct_key(client, monkeypatch):
    monkeypatch.setattr("app.middleware.auth.settings", type("S", (), {"api_key": "secret"})())
    r = client.get("/workflows", headers={"X-API-Key": "secret"})
    assert r.status_code == 200


def test_auth_middleware_skips_public_routes(client, monkeypatch):
    monkeypatch.setattr("app.middleware.auth.settings", type("S", (), {"api_key": "secret"})())
    r = client.get("/healthz")
    assert r.status_code == 200
