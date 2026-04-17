---
title: "Warp of Oz! 🌪️ Ep.3"
published: false
description: "Episode 3: The Tin Man didn't need a new heart — he needed someone who believed he had one. WARP.md, Rules, and Skills give Warp's agent the soul of your project: conventions, patterns, and the memory of how your codebase thinks. Build authentication middleware."
tags: [warp, terminal, ai, productivity]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/warp-of-oz-episode-03.png"
series: "Warp of Oz Series"
canonical_url: ""
organization: "the-software-s-journey"
---
## Episode 3: The Tin Man Gets a Heart

> "Hearts will never be practical until they can be made unbreakable."— The Wizard of Oz (1939)

## The Tin Man's Problem 🤖

The Tin Man worked perfectly. Every joint lubricated, every movement precise. What he lacked was memory — specifically, the memory of what mattered to him, what he cared about, what made his actions more than mechanical. Without a heart, every task was the same. Every command was context-free.

Warp's agent, without guidance, is the Tin Man. It knows how to write Python. It knows FastAPI. It does not know *your* Python, *your* FastAPI conventions — whether you use `snake_case` or camelCase for JSON, whether you prefer dependency injection or module-level singletons, whether `print()` or proper logging is expected, whether you want type hints on everything or only on public functions.

**WARP.md, Rules, and Skills** are the heart. They are the project's memory, given to the agent at the start of every conversation.

## 🗂️ SIPOC — The Heart Is Written Down

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the developer who knows the codebase) | Your conventions, patterns, preferences for this project | Write WARP.md at the project root | A rules file the agent reads at every session start | The agent — no longer guesses your style |
| Warp Drive (team knowledge) | Reusable guidelines for common behaviours | Create a Rule in Warp Drive Settings | A cloud-synced rule applied across all sessions for your team | Every team member's agent — consistent behaviour |
| You (defining repeatable workflows) | A multi-step task that always follows the same pattern | Write a SKILL.md in .warp/skills/ | An instruction set the agent invokes when the task matches | Agent Mode — invokes the skill automatically |
| The agent (with WARP.md loaded) | A prompt to "add authentication middleware" | Agent follows project conventions from WARP.md | Auth middleware that matches the existing codebase style | src/middleware/auth.py — code that does not need refactoring |

## `WARP.md`: The Project's Constitution 📜

`WARP.md` is Warp's equivalent of `CLAUDE.md` or `AGENTS.md` — a Markdown file at the root of your project that the agent reads at the start of every session. It is your project's constitution: the rules, the conventions, the things that would take a new developer two weeks to learn through osmosis.

Create it now in `~/projects/warp-of-oz-tasks/`:

```bash
cat > ~/projects/warp-of-oz-tasks/WARP.md << 'MARKDOWN'
# Warp of Oz Tasks — Agent Rules

## Project Overview
A FastAPI task management API built in Python 3.12.
Currently using in-memory storage (dict), will migrate to PostgreSQL in a later episode.
Built on a Mac Mini M4 Pro using `uv` as the package manager.

## Technology Stack
- Python 3.12 with `from __future__ import annotations`
- FastAPI 0.115+
- Pydantic v2 for validation (use `model_dump()` not `dict()`)
- `uv` for package management (`uv add`, `uv run`, never `pip`)

## Code Conventions
- Type hints on all function signatures (parameters and return types)
- Docstrings on all public functions and classes (short — one line is fine)
- `snake_case` for all identifiers; `SCREAMING_SNAKE_CASE` for constants
- JSON responses use `snake_case` keys (Pydantic default — do not change this)
- Async functions for all FastAPI route handlers (`async def`, not `def`)
- Import order: stdlib → third-party → local (enforce with `ruff`)

## Error Handling
- Use `HTTPException` for API errors with meaningful `detail` messages
- Never suppress exceptions silently — log them first
- 404s use the format: f"Resource {id!r} not found."
- Validation errors handled by FastAPI/Pydantic automatically

## Project Structure Rules
- New features go in: `src/models/`, `src/schemas/`, `src/repositories/`, `src/routers/`
- No business logic in routers — routers call repositories/services only
- Middleware goes in `src/middleware/`
- Configuration goes in `src/config.py` using Pydantic Settings

## Testing
- Tests go in `tests/` mirroring the `src/` structure
- Use `pytest` with `pytest-asyncio` for async tests
- Test file names: `test_*.py`
- Use `httpx.AsyncClient` for FastAPI integration tests

## Authentication (added in Ep.3)
- API key authentication: `X-API-Key` header
- Valid keys stored in `src/config.py` as a set
- Unauthenticated requests → 401 with detail "Invalid or missing API key"
- The `/health` endpoint is always public (no auth required)

## What NOT to Do
- Do not use `from app import *` — explicit imports only
- Do not use `print()` for logging — use the `logging` module
- Do not hardcode secrets — use environment variables via Pydantic Settings
- Do not ignore return types from repository methods
MARKDOWN
```

This file now lives in the project. Every time you open Agent Mode with this project as the working directory, the agent reads it.

## Rules: Team-Level Memory in Warp Drive ☁️

Rules are stored in Warp Drive and synced across your team. Unlike `WARP.md` (which is project-specific and version-controlled), Rules are persona-level or team-level guidelines that apply everywhere.

### Creating a Rule

1. Open Warp Drive: `Cmd-D` or the Drive icon in the left sidebar
2. Click `+` → **Rule**
3. Name it: `Python Developer Standards`
4. Write the rule body:

```markdown
# Python Developer Standards

When writing Python code:
- Always use type hints (Python 3.12 syntax — `str | None` not `Optional[str]`)
- Prefer dataclasses or Pydantic models over plain dicts for structured data
- Use `pathlib.Path` over `os.path` for filesystem operations
- Prefer f-strings over `.format()` or `%` formatting
- Write tests before or immediately after implementing a feature
- Use `ruff` for linting and `ruff format` for formatting (not `black`)
```

1. Toggle: **Apply to Agent Mode** ✓
2. Save

This rule now applies to all your agent sessions, not just this project. It is the Tin Man's heart — it travels with you.

## Skills: Reusable Workflows the Agent Invokes 📖

A **Skill** is a `SKILL.md` file that teaches the agent how to perform a specific, repeatable task in your project. Unlike Rules (broad guidelines), Skills are step-by-step workflows.

Create the project's first Skill — for adding new API endpoints:

```bash
mkdir -p ~/projects/warp-of-oz-tasks/.warp/skills

cat > ~/projects/warp-of-oz-tasks/.warp/skills/add-endpoint.md << 'MARKDOWN'
# Skill: Add a New API Endpoint

Use this skill when the developer asks to add a new REST endpoint to the FastAPI application.

## Steps

1. **Identify the resource** — determine the resource name (singular, e.g. `task`, `user`, `project`)
2. **Create or update the model** — add `src/models/{resource}.py` with a Pydantic `BaseModel` including `id` (UUID), timestamps, and domain fields
3. **Create schemas** — add `src/schemas/{resource}.py` with `{Resource}Create` and `{Resource}Update` Pydantic models (only the fields the user can set)
4. **Create or update the repository** — add `src/repositories/{resource}_repo.py` with a class exposing `create`, `get`, `list_all`, `update`, `delete`
5. **Create the router** — add `src/routers/{resource}s.py` with prefix `/{resource}s` and full CRUD routes
6. **Register the router** — add `app.include_router(router)` in `src/main.py`
7. **Write tests** — add `tests/test_{resource}s.py` with at minimum: create test, list test, not-found test
8. **Confirm** — run `uv run pytest tests/test_{resource}s.py -v` and report results

## Constraints
- Follow all conventions in WARP.md
- Do not use a database — use the in-memory repository pattern
- All route handlers must be `async def`
- All responses must use the Pydantic model as `response_model`
MARKDOWN
```

Now when you type in Agent Mode:

```
/add-endpoint user
```

Warp auto-invokes the `add-endpoint` Skill and follows its 8-step workflow to create a complete `User` CRUD feature. Every time. Consistent. Correct.

## Using WARP.md to Add Authentication Middleware 🔑

Now let's use the heart we gave the agent. With `WARP.md` in place, ask the agent to add authentication:

```
# In Agent Mode (Cmd-I):

Please add API key authentication to warp-of-oz-tasks.

Based on the rules in WARP.md:
- Add a Pydantic Settings configuration class at src/config.py
- Store valid API keys as a set in the settings (load from environment variable API_KEYS, comma-separated)
- Create src/middleware/auth.py with a FastAPI middleware that checks the X-API-Key header
- The /health endpoint should remain public
- All other endpoints require a valid API key
- Invalid/missing key → 401 with the standard error format from WARP.md
```

Because the agent has read `WARP.md`, it already knows:

- To use Pydantic Settings, not raw `os.environ`
- To use `snake_case` JSON keys
- To format 401 errors as `"Invalid or missing API key"`
- To put the middleware in `src/middleware/`
- Not to use `print()` — use `logging`

The code it writes reflects the project's style. No refactoring needed.

Here is what the agent produces:

### `src/config.py`

```python
"""Application configuration — loaded from environment variables."""
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Settings loaded from environment variables.

    Set API_KEYS as a comma-separated list of valid API keys.
    Example: export API_KEYS="key-dorothy,key-scarecrow,key-tinman"
    """
    api_keys: set[str] = {"dev-key-oz"}   # default for development only

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls()

settings = Settings()
```

```bash
# Add pydantic-settings dependency
uv add pydantic-settings
```

### `src/middleware/auth.py`

```python
"""API key authentication middleware."""
from __future__ import annotations
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.config import settings

logger = logging.getLogger(__name__)

# Paths that bypass authentication
PUBLIC_PATHS: set[str] = {"/health", "/docs", "/openapi.json", "/redoc"}

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validate X-API-Key header on all non-public routes."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in settings.api_keys:
            logger.warning(
                "Rejected request: missing/invalid API key | path=%s ip=%s",
                request.url.path,
                request.client.host if request.client else "unknown",
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"},
            )

        logger.debug("Authenticated request: path=%s", request.url.path)
        return await call_next(request)
```

### Updated `src/main.py`

```python
"""
warp-of-oz-tasks — Episode 3: authentication middleware added.
"""
from __future__ import annotations
import logging
from datetime import datetime
from fastapi import FastAPI
from src.middleware.auth import APIKeyMiddleware
from src.routers.tasks import router as tasks_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

app = FastAPI(
    title="Warp of Oz Tasks",
    description="Follow the yellow brick road — one endpoint at a time.",
    version="0.3.0",
)

# Middleware (added before routers)
app.add_middleware(APIKeyMiddleware)

# Routers
app.include_router(tasks_router)

@app.get("/health")
async def health_check():
    """Public health endpoint — no auth required."""
    return {
        "status": "alive",
        "message": "Toto, I've a feeling we're not in Kansas anymore.",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version,
    }
```

## Testing Authentication 🔐

```bash
# Health is still public — no key needed
curl -s http://localhost:8000/health | python3 -m json.tool
# {"status": "alive", ...}

# Tasks without a key → 401
curl -s http://localhost:8000/tasks
# {"detail": "Invalid or missing API key"}

# Tasks with the development key → 200
curl -s http://localhost:8000/tasks \
  -H "X-API-Key: dev-key-oz" \
  | python3 -m json.tool
# []  ← empty list (in-memory store starts fresh)

# Create a task with auth
curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-oz" \
  -d '{"title": "Find the Emerald City", "status": "in_progress"}' \
  | python3 -m json.tool
```

## The Project Structure Now 📁

```
~/projects/warp-of-oz-tasks/
├── .warp/
│   └── skills/
│       └── add-endpoint.md      ← reusable endpoint-creation skill ✓
├── .python-version
├── pyproject.toml
├── WARP.md                      ← project constitution ✓
├── README.md
└── src/
    ├── __init__.py
    ├── main.py                  ← auth middleware registered ✓
    ├── config.py                ← Pydantic Settings ✓
    ├── middleware/
    │   └── auth.py              ← APIKeyMiddleware ✓
    ├── models/task.py
    ├── schemas/task.py
    ├── repositories/task_repo.py
    └── routers/tasks.py
```

```bash
git add .
git commit -m "feat: add WARP.md, Skills, and API key auth — Ep.3 Tin Man"
```

In **Episode 4**, the Cowardly Lion joins the road. He needs courage — the courage to let the agent act without constant supervision. Agent pair mode with code review.

**🔗 Resources**

- **WARP.md / Rules documentation**: [docs.warp.dev/knowledge-and-collaboration/warp-drive/ai-objects](https://docs.warp.dev/knowledge-and-collaboration/warp-drive/ai-objects)
- **Warp Drive**: [docs.warp.dev/knowledge-and-collaboration/warp-drive](https://docs.warp.dev/knowledge-and-collaboration/warp-drive/)
- **pydantic-settings**: [docs.pydantic.dev/latest/concepts/pydantic_settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

*🌪️ Warp of Oz Series — following the Yellow Brick Road through Warp's Agentic Development Environment.*