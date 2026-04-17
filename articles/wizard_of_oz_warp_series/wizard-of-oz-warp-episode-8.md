---
title: "Warp of Oz! 🌪️ Ep.8"
published: false
description: "Episode 8: Dorothy tapped her heels three times and went home. You already have everything you need. MCP servers extend every agent, Warp Drive shares team knowledge, and the complete production workflow closes the yellow brick road. There's no place like home."
tags: [warp, productivity, workflow, mcp]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/warp-of-oz-episode-08.png"
series: "Warp of Oz Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: There's No Place Like Home

> "There's no place like home. There's no place like home. There's no place like home."— Dorothy Gale, The Wizard of Oz (1939)

## The Three Clicks 💎

Dorothy had been in Oz for the entire story. She fought the Wicked Witch. She gathered her companions. She entered the Emerald City. She unmasked the Wizard.

And at the end, Glinda appeared and told her she always had the power to go home.

That is this episode.

You have been in Warp for seven episodes. You installed it, learned blocks, gave the agent a brain (AI features), a heart (WARP.md + Rules), and courage (Agent pair mode + Code Review). You dispatched flying monkeys (dispatch mode). You reached the Emerald City (Oz platform). You found the ruby slippers (Augment Code Intent).

The final episode is the three clicks: **MCP servers** that extend every agent, **Warp Drive** that makes the team's knowledge persistent, and the **complete production workflow** that brings everything home. After this, you have not learned a tool. You have changed how you work.

## 🗂️ SIPOC — Coming Home

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| MCP servers (GitHub, Linear, Sentry, custom) | Your external tooling landscape | Configure MCP servers in Warp → agents can query/act on external systems | Agents that know your issues, PRs, errors — without you pasting context | Every agent conversation — richer context automatically |
| Warp Drive (team workspace) | Workflows, prompts, rules, environment variables | Save once → sync to all team members | Shared team knowledge that every agent uses | Your team — everyone's agent behaves consistently |
| The complete warp-of-oz-tasks API | 7 episodes of iterative development | Run the full test suite, add production config, review the architecture | A tested, documented, production-ready service | The series, complete — you understand every line |
| This series | The Yellow Brick Road walked end to end | A workflow internalised, not just demonstrated | Habits: blocks, AI, WARP.md, pair mode, dispatch, Oz, Intent | Your daily development practice |

## MCP Servers: The Yellow Brick Road Extends Everywhere 🌐

**MCP — Model Context Protocol** — is a standardised way for AI agents to access external tools and data. Instead of you pasting a GitHub issue URL into the agent conversation, the agent queries GitHub directly. Instead of copying a Sentry error, the agent reads it and traces the source.

Configure MCP servers in Warp: **Settings → Agent → MCP Servers**.

### GitHub MCP

```json
// In Warp Settings → Agent → MCP Servers → Add:
{
  "name": "github",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_PAT"
  }
}
```

Now in Agent Mode:

```
# Without MCP:
"Here is the error from issue #42: [paste 200 lines]..."

# With GitHub MCP:
"Fix the bug described in issue #42 in warp-of-oz-tasks"
# Agent reads the issue directly, reads the relevant code, proposes the fix
```

### Sentry MCP: Proactive Bug Fixing

```json
{
  "name": "sentry",
  "command": "npx",
  "args": ["-y", "@sentry/mcp-server-sentry"],
  "env": {
    "SENTRY_AUTH_TOKEN": "$SENTRY_TOKEN",
    "SENTRY_ORG": "your-org"
  }
}
```

With Sentry MCP, the agent can query your error monitoring directly:

```
# In Agent Mode:
Find all Sentry errors tagged with warp-of-oz-tasks from the last 24 hours
and propose fixes for the top 3 most frequent ones.
```

### Linear MCP: Issue-Driven Development

```json
{
  "name": "linear",
  "command": "npx",
  "args": ["-y", "@linear/mcp-server"],
  "env": {
    "LINEAR_API_KEY": "$LINEAR_KEY"
  }
}
```

```
# Start a new feature from a Linear issue:
Implement the feature described in Linear issue OZ-47. Follow WARP.md conventions.
```

The agent reads OZ-47 from Linear, understands the requirements, and starts implementing. No copy-paste. No context loss.

## Warp Drive: The Team's Shared Heart 💛

**Warp Drive** is the team knowledge layer. Everything you save there is synced to all team members and available to every agent session.

What lives in Warp Drive:

| Object type | What it is | Example |
| --- | --- | --- |
| Workflows | Saved commands with parameters | uv run pytest {test_path} -v |
| Prompts | Reusable agent prompts | Perform a security audit on @src/middleware/auth.py |
| Rules | Team-level agent guidelines | Always include tests with new API endpoints |
| Notebooks | Markdown files with runnable commands | Development Setup for New Engineers.md |
| Environment Variables | Shared dev variables (non-sensitive) | API_BASE_URL=http://localhost:8000 |

### Creating a Team Workflow

```bash
# Warp Drive → + → Workflow
# Name: "Full Project Test Run"
# Command:
cd ~/projects/warp-of-oz-tasks && \
  uv run pytest tests/ -v --tb=short 2>&1 | tee test-results.txt && \
  echo "Tests complete: $(grep -c 'PASSED' test-results.txt) passed, $(grep -c 'FAILED' test-results.txt) failed"

# Tags: #testing #ci
# Description: "Run the complete test suite with output summary"
```

Now every team member can find "Full Project Test Run" in the Command Palette (`Cmd-P`), run it with one click, and get a block with the full test output.

### The Team's Shared Rule

```markdown
# Warp Drive → + → Rule → "Team: Code Review Gate"

Before committing any code that the agent wrote:
1. Open the Code Review panel (Cmd-Shift-+)
2. Review EVERY changed file — not just the diff summary
3. Check that type hints are present on all new functions
4. Verify no TODO or placeholder comments remain
5. Run the full test suite with the "Full Project Test Run" workflow
6. Only after all checks: git commit

This is the Toto Rule — always lift the curtain before accepting.
```

Every developer on the team gets this rule. Every agent on the team follows it. The Tin Man's heart, distributed.

## The Production `warp-of-oz-tasks` Service 🚀

Let's add the final production configurations and run the complete test suite:

### `.env.example` — environment template

```bash
cat > ~/projects/warp-of-oz-tasks/.env.example << 'ENV'
# Copy to .env and fill in values — never commit .env
API_KEYS=your-api-key-here,second-key-if-needed
LOG_LEVEL=INFO
ENV

# Create .env for local development
cat > ~/projects/warp-of-oz-tasks/.env << 'ENV'
API_KEYS=dev-key-oz
LOG_LEVEL=DEBUG
ENV

echo ".env" >> ~/projects/warp-of-oz-tasks/.gitignore
```

### `src/config.py` — final version

```python
"""Application configuration — Episode 8: production-ready settings."""
from __future__ import annotations
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Settings loaded from environment variables or .env file.

    Required in production:
        API_KEYS: comma-separated list of valid API keys
        LOG_LEVEL: DEBUG | INFO | WARNING | ERROR (default: INFO)
    """
    api_keys:  set[str]  = {"dev-key-oz"}
    log_level: str       = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def configure_logging(self) -> None:
        """Apply log level from settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper(), logging.INFO),
            format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        )

settings = Settings()
```

### The final `src/main.py`

```python
"""
warp-of-oz-tasks — Episode 8: production-ready.
Built across 8 episodes of the Warp of Oz series on a Mac Mini M4 Pro.
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from src.config import settings
from src.middleware.auth import APIKeyMiddleware
from src.repositories.task_repo import task_repo
from src.routers.tasks import router as tasks_router
from src.routers.processing import router as processing_router

settings.configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    task_repo.start_worker()
    yield
    if task_repo._worker_task:
        task_repo._worker_task.cancel()

app = FastAPI(
    title="Warp of Oz Tasks",
    description=(
        "A task management API built across 8 episodes of the Warp of Oz series. "
        "Powered by FastAPI, Python 3.12, and a Mac Mini M4 Pro. "
        "There's no place like home."
    ),
    version="0.8.0",
    lifespan=lifespan,
)

app.add_middleware(APIKeyMiddleware)
app.include_router(tasks_router)
app.include_router(processing_router)

@app.get("/health")
async def health_check():
    """Public health endpoint — always responds, no auth."""
    q = task_repo.queue_status()
    return {
        "status": "alive",
        "message": "There's no place like home.",
        "version": app.version,
        "timestamp": datetime.utcnow().isoformat(),
        "queue_depth": q["queue_length"],
        "endpoints": [
            "GET  /health",
            "GET  /tasks",
            "POST /tasks",
            "GET  /tasks/{id}",
            "PATCH /tasks/{id}",
            "DELETE /tasks/{id}",
            "POST /tasks/{id}/process",
            "GET  /tasks/queue/status",
        ],
    }
```

### Run the full test suite

```bash
cd ~/projects/warp-of-oz-tasks
uv run pytest tests/ -v --tb=short

# Expected output:
# tests/conftest.py — setup
# tests/test_task_updates.py::test_update_refreshes_updated_at PASSED
# tests/test_tags.py::test_tags_normalised_to_lowercase PASSED
# tests/test_tags.py::test_filter_by_single_tag PASSED
# tests/test_tags.py::test_filter_by_multiple_tags_and_logic PASSED
# tests/test_tags.py::test_tags_exceed_limit_rejected PASSED
# tests/test_processing.py::test_task_can_be_enqueued PASSED
# tests/test_processing.py::test_queue_status_reflects_enqueued_tasks PASSED
# tests/test_processing.py::test_nonexistent_task_process_returns_404 PASSED
#
# =================== 8 passed in 2.xS ===================
```

All green. The road is paved.

## The Complete Project Structure: The Full Map 🗺️

```
~/projects/warp-of-oz-tasks/
├── .env                    ← local secrets (gitignored)
├── .env.example            ← template for new developers
├── .gitignore
├── .python-version         ← Python 3.12
├── .warp/
│   └── skills/
│       ├── add-endpoint.md          ← Ep.3: reusable endpoint creation
│       └── cleanup-failed-tasks.md  ← Ep.6: Oz cloud agent skill
├── pyproject.toml
├── WARP.md                 ← Ep.3: project constitution for agents
├── README.md
├── tests/
│   ├── conftest.py         ← Ep.4: test isolation
│   ├── test_tags.py        ← Ep.7: tag filtering tests (Intent-generated)
│   ├── test_task_updates.py ← Ep.4: update bug regression test
│   └── test_processing.py  ← Ep.5: background processing tests
└── src/
    ├── __init__.py
    ├── config.py           ← Ep.3 + Ep.8: Pydantic Settings
    ├── main.py             ← Ep.1 + all updates: health + routers
    ├── middleware/
    │   └── auth.py         ← Ep.3: API key middleware
    ├── models/
    │   └── task.py         ← Ep.2 + Ep.5 + Ep.7: Task model with tags + processing
    ├── schemas/
    │   └── task.py         ← Ep.2 + Ep.7: TaskCreate, TaskUpdate with tag validation
    ├── repositories/
    │   └── task_repo.py    ← Ep.2 + Ep.4 + Ep.5 + Ep.7: full CRUD + queue + tags
    └── routers/
        ├── tasks.py        ← Ep.2 + Ep.7: CRUD + tag filtering
        └── processing.py   ← Ep.5: background task queue endpoints
```

## The Complete Workflow Map: The Road Behind You 🗺️

| Episode | Oz parallel | Warp feature learned | Codebase milestone |
| --- | --- | --- | --- |
| 1 | Dorothy arrives in Oz | Blocks, # key, input editor | Health endpoint |
| 2 | Scarecrow gets a brain | AI completions, Agent Mode, Cmd-I | Full CRUD endpoints |
| 3 | Tin Man gets a heart | WARP.md, Rules, Skills | Auth middleware |
| 4 | Lion gets courage | Pair mode, Code Review panel, debugging | Bug fixed + regression test |
| 5 | Flying monkeys dispatched | Dispatch mode, desktop notifications | Background task processor |
| 6 | The Emerald City | Oz platform, CLI, cloud agents, schedules | Scheduled cleanup agent |
| 7 | The ruby slippers | Augment Code Intent, living spec, Context Engine | Task tags + filtering |
| 8 | There's no place like home | MCP servers, Warp Drive, production config | Complete production service |

## The Three Habits That Change Everything 💎

Walk away from this series with three habits:

**1. Always have a WARP.md.** Every project you start: write the constitution first. Ten minutes at the start saves hours of agent corrections throughout. The Tin Man works because someone wrote down what he cares about.

**2. Always review the diff.** Dispatch mode is powerful. Augment Intent is powerful. The Code Review panel is always the final gate. The Cowardly Lion does not charge blindly — he reads the battle plan. Toto always lifts the curtain.

**3. Use the right tool for the scope.** Single-file quick fix → pair mode. Bounded autonomous task → dispatch. Cross-file feature with spec → Intent. Background automation → Oz. The road has different surfaces for different distances.

## There's No Place Like Home 🏠

```bash
# The final commit
cd ~/projects/warp-of-oz-tasks
git add .
git commit -m "feat: production config, full test suite — Ep.8 There's No Place Like Home"
git tag v1.0.0
git push origin main --tags

# The server, one last time
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# The health check
curl -s http://localhost:8000/health | python3 -m json.tool
```

You arrive at:

```json
{
  "status": "alive",
  "message": "There's no place like home.",
  "version": "0.8.0",
  ...
}
```

The yellow brick road is complete.

**🔗 Resources**

- **Warp documentation**: [docs.warp.dev](https://docs.warp.dev)
- **Oz platform**: [oz.warp.dev](https://oz.warp.dev)
- **Augment Code Intent**: [augmentcode.com/product/intent](https://www.augmentcode.com/product/intent)
- **MCP servers directory**: [mcp.so](https://mcp.so) — browse available MCP servers
- `warp-of-oz-tasks`** repository**: [github.com/Elsa-Yanke/web-dev-project-2026](https://github.com/Elsa-Yanke/web-dev-project-2026) (inspiration)

*🌪️ Warp of Oz Series — eight episodes, one yellow brick road, one Mac Mini M4 Pro, and the realisation that the power was always in your terminal.**There's no place like home.*