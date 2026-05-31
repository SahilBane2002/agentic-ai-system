# Agentic AI System

A multi-agent orchestration backend that accepts a plain-English goal, routes it to a specialist agent, executes a step-by-step plan using AI and external tools, and returns structured results — all over a REST API.

## How It Works

```
POST /workflows/run  { "goal": "research competitor pricing" }
         │
         ▼
  ControllerAgent
  (Groq LLM → keyword fallback)
         │
         ▼
  WorkflowEngine executes plan steps
  ┌─────────────────────────────┐
  │ research.web_search         │
  │ research.summarize          │
  └─────────────────────────────┘
         │
         ▼
  Results persisted to DB + returned
```

**Supported agents:**

| Agent | What it does |
|---|---|
| `research` | DuckDuckGo web search + summarization |
| `calendar` | Finds free time slots via Google Calendar |
| `communication` | Classifies inbox, drafts and sends emails via Gmail |

---

## Tech Stack

- **FastAPI** — async REST API
- **SQLAlchemy 2 + Alembic** — ORM and schema migrations (SQLite for dev, PostgreSQL for prod)
- **Groq API** (LLaMA 3.3-70B) — LLM-based goal routing
- **Arcade SDK** — Gmail and Google Calendar integrations (mocks used when key is absent)
- **DuckDuckGo Search** — web research tool
- **Docker / docker-compose** — containerized local stack
- **Fly.io / Railway** — deployment targets

---

## Project Structure

```
app/
├── main.py                  # FastAPI app, middleware, startup hooks
├── config.py                # All settings via env vars (Pydantic)
├── db.py                    # SQLAlchemy ORM: Workflow + Task tables
├── models.py                # Pydantic schemas used by the engine
│
├── agents/
│   ├── controller.py        # Routes goals to specialist agents
│   ├── research.py          # Web search + summarization
│   ├── calendar.py          # Google Calendar free-slot finder
│   └── communication.py     # Gmail inbox classifier + draft/send
│
├── core/
│   ├── workflow.py          # Step execution engine
│   ├── intents.py           # Keyword intent classifier (LLM fallback)
│   └── memory.py            # In-process key-value store (shared_memory)
│
├── routers/
│   ├── health.py            # GET /healthz
│   ├── workflows.py         # POST /workflows/run, GET /workflows, GET /workflows/{id}
│   └── auth.py              # GET /auth/gmail/start, GET /auth/calendar/start
│
├── services/
│   ├── groq_client.py       # Groq async client singleton
│   └── arcade.py            # Arcade SDK client singleton
│
├── tools/
│   ├── registry.py          # Tool registry (name → async handler)
│   ├── web_search.py        # DuckDuckGo search tool
│   ├── gmail_arcade.py      # Real Gmail via Arcade
│   ├── gcal_arcade.py       # Real Google Calendar via Arcade
│   ├── gmail_mock.py        # Mock Gmail (used when ARCADE_API_KEY not set)
│   └── gcal_mock.py         # Mock Google Calendar (same)
│
└── middleware/
    └── auth.py              # X-API-Key header validation

alembic/                     # DB migration scripts
tests/                       # pytest test suite
```

---

## API Endpoints

### `POST /workflows/run`
Run a workflow from a natural language goal.

**Request**
```json
{
  "goal": "research the latest AI pricing trends",
  "context": { "query": "AI pricing 2024" }
}
```

**Response**
```json
{
  "route": { "agent": "research", "plan": [...] },
  "workflow": { "id": "...", "status": "done", "tasks": [...] },
  "final": { "summary": "..." }
}
```

---

### `GET /workflows`
List all past workflows, newest first.

Query params: `limit` (default 20), `offset` (default 0)

---

### `GET /workflows/{id}`
Get a single workflow with all its task results. Returns `404` if not found.

---

### `GET /healthz`
Returns `{"status": "ok"}` or `{"status": "degraded"}` based on DB connectivity. No auth required.

---

### `GET /auth/gmail/start` · `GET /auth/calendar/start`
Initiates OAuth for Gmail / Google Calendar via Arcade. Returns an authorization URL to visit in the browser.

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-org/agentic-ai-system
cd agentic-ai-system
pip install -e .
```

### 2. Configure environment

```bash
cp .env.sample .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_key          # required — used for LLM routing
API_KEY=your_api_key                # required in prod — protects the API
ARCADE_API_KEY=your_arcade_key      # optional — Gmail/Calendar fall back to mocks if absent
ARCADE_USER_ID=you@example.com
DATABASE_URL=sqlite:///./dev.db     # default SQLite; swap for PostgreSQL in prod
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

---

## Docker (local full stack)

Starts PostgreSQL + the API service:

```bash
docker-compose up --build
```

The API is available at `http://localhost:8000`. PostgreSQL data is persisted in a named volume.

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Tests use an in-memory SQLite DB and mock all external calls (Groq, Arcade, DuckDuckGo).

---

## Deployment

### Fly.io

```bash
fly launch        # first time
fly deploy        # subsequent deploys
```

Set secrets:
```bash
fly secrets set GROQ_API_KEY=... API_KEY=... ARCADE_API_KEY=... DATABASE_URL=...
```

### Railway

Connect the repo in the Railway dashboard. Set the same env vars. The `railway.toml` and `Dockerfile` handle the rest.

---

## How Routing Works

The `ControllerAgent` tries two strategies in order:

1. **Groq LLM** — sends the goal to LLaMA 3.3-70B with a system prompt that instructs it to return a JSON `{agent, plan}` object. The plan is a list of step types and payloads.
2. **Keyword fallback** — if Groq is unavailable or fails, classifies the goal by matching keywords (`schedule`, `meeting`, `email`, `research`, etc.) and returns a hardcoded plan for that intent.

---

## Graceful Degradation

- **No `ARCADE_API_KEY`** — Gmail and Google Calendar tools automatically fall back to mock implementations. The app starts and runs normally; no crashes.
- **No `GROQ_API_KEY`** — startup fails with a clear error message listing the missing variable.
- **No `API_KEY`** — auth middleware is disabled in dev; required in prod (`APP_ENV=prod`).
