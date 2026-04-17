---
title: "Wizard of Oz Warp 🌪️ Ep.2"
published: false
description: "Episode 2: The Scarecrow didn't need a brain — he needed someone to tell him he had one. Warp's AI features work the same way: the # key, Active AI, Next Command, and Agent Mode turn your terminal session into a thinking collaborator. Build the task CRUD endpoints."
tags: [warp, ai, terminal, python]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/wizard_of_oz_warp_series/wizard-of-oz-warp-episode-02.png"
series: "Wizard of Oz Warp Series"
canonical_url: ""
organization: "the-software-s-journey"
---
## Episode 2: The Scarecrow Gets a Brain

> "If I only had a brain."— The Scarecrow, The Wizard of Oz (1939)

## The Straw Man in Your Terminal 🌾

The Scarecrow knew things. He talked in riddles. He solved problems with hay and guesswork. What he lacked was confidence in his own intelligence — and a way to articulate it clearly.

Most developers feel like this in the terminal. They know the thing they want to do. They cannot remember the exact flags. They paste from Stack Overflow, wonder if it still applies to macOS Sequoia, and run it nervously. The knowledge is there. The articulation is straw.

Warp's AI features are the Wizard's gift to the Scarecrow. Not a transplant — a recognition. The brain was always there.

## 🗂️ SIPOC — The Brain Arrives

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (typing # + natural language) | A description of what you want to do | Warp LLM converts intent to shell command | A ready-to-run command, review before pressing Enter | You — no more Stack Overflow for basic commands |
| Warp Active AI | Terminal session context (recent commands, exit codes, errors) | Proactive analysis → Suggested Code Diffs, Prompt Suggestions, Next Command | Inline suggestions and fix proposals | You — the terminal anticipates the next step |
| Warp Agent Mode (local) | A multi-turn conversation prompt | Agent reads your codebase, writes code, runs commands, reviews diffs | Code changes applied to your repository | The warp-of-oz-tasks codebase — grows with each agent turn |
| DRF serializers (project context) | Conversation context + task model definition | Agent generates CRUD endpoints + tests | src/tasks/ module with models, router, schemas | The running FastAPI server |

## The `#` Key: Natural Language in the Terminal 🧠

The `#` key is Warp's simplest and most transformative feature. Type `#` and the cursor shifts into natural language mode. Describe what you want. Press Enter. Warp proposes a shell command.

```bash
# Try these exactly as typed, including the #:

# create a virtual environment and install dependencies from pyproject.toml
# uv sync

# run the fastapi server on port 8000 with auto-reload
# uv run uvicorn src.main:app --reload --port 8000

# show me the last 20 lines of uvicorn's output
# tail -20 uvicorn.log

# find all files modified in the last 24 hours under the src directory
# find src -mtime -1 -type f

# count the lines of Python in this project
# find . -name "*.py" ! -path "./.venv/*" | xargs wc -l | tail -1
```

Each of these produces a command you review before running. You can accept, edit, or dismiss. The Scarecrow thinks out loud; you decide what to speak.

### Active AI: The Terminal That Watches You Work

Active AI runs in the background, observing your session. When it detects something worth responding to, it surfaces a chip you can act on:

**Next Command** — after you run `uv add fastapi`, Warp notices you might next want `uv run uvicorn...`. The suggestion appears at the right of your input. Press `→` to accept, `Ctrl-F` to adopt without running.

**Suggested Code Diffs** — when a command exits with a non-zero code, Warp analyses the error output and proposes a fix. You see a diff chip. Click it to expand the proposed change.

**Prompt Suggestions** — after complex output, Warp suggests follow-up questions you could ask the agent. These appear as clickable chips; press `Cmd-Enter` to send the suggestion directly to Agent Mode.

```bash
# Trigger Active AI deliberately: run something that will fail
ls /nonexistent/path

# Warp will surface: "Directory does not exist — did you mean...?"
# Or propose creating the directory. Click the chip.
```

## Agent Mode: The Conversation 💬

Agent Mode is Warp's built-in local agent. Open it with `Cmd-I` (or click the agent icon). This switches from terminal mode to a multi-turn conversation view.

The agent:

- Reads files in your working directory
- Runs shell commands (with your approval in pair mode)
- Edits files
- Tracks a task list for complex workflows
- Reviews its own output against your requirements

Let's use it to build the task CRUD endpoints.

### Starting the conversation

```
# In Agent Mode (Cmd-I):

I have a FastAPI application at ~/projects/warp-of-oz-tasks.
It currently only has a health endpoint at GET /health.

I want to add a complete CRUD API for tasks. A task has:
- id: UUID (auto-generated)
- title: str (required, max 200 chars)
- description: str (optional)
- status: enum("todo", "in_progress", "done")
- created_at: datetime (auto-set)
- updated_at: datetime (auto-updated)

Please:
1. Create a Pydantic model for Task (in src/models/task.py)
2. Create Pydantic schemas for TaskCreate and TaskUpdate (in src/schemas/task.py)
3. Create an in-memory task repository (src/repositories/task_repo.py) using a dict
4. Create a FastAPI router with full CRUD (src/routers/tasks.py)
5. Register the router in src/main.py

Do not use a database yet — keep it simple with in-memory storage for now.
```

The agent creates a plan — a checklist of tasks — before doing any work:

```
Plan:
□ Create src/models/task.py — Task model with UUID, enums, timestamps
□ Create src/schemas/task.py — TaskCreate, TaskUpdate, TaskResponse Pydantic models
□ Create src/repositories/task_repo.py — In-memory dict store with CRUD operations
□ Create src/routers/tasks.py — FastAPI router: GET /, POST /, GET /{id}, PATCH /{id}, DELETE /{id}
□ Update src/main.py — Register /tasks router
□ Test: curl the endpoints
```

After approval, the agent executes each step, proposing file edits you review in the **Code Review panel** (`Cmd-Shift-+`).

## The Code the Agent Writes 📝

Let's trace what the agent produces. (You can write these manually if you prefer to understand them first.)

### `src/models/task.py`

```python
"""Task domain model."""
from __future__ import annotations
import uuid
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    TODO        = "todo"
    IN_PROGRESS = "in_progress"
    DONE        = "done"

class Task(BaseModel):
    id:          str         = Field(default_factory=lambda: str(uuid.uuid4()))
    title:       str         = Field(..., max_length=200)
    description: str | None  = None
    status:      TaskStatus  = TaskStatus.TODO
    created_at:  datetime    = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at:  datetime    = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

### `src/schemas/task.py`

```python
"""Request / response schemas — separate from the domain model."""
from pydantic import BaseModel, Field
from .models.task import TaskStatus

class TaskCreate(BaseModel):
    title:       str           = Field(..., min_length=1, max_length=200)
    description: str | None    = None
    status:      TaskStatus    = TaskStatus.TODO

class TaskUpdate(BaseModel):
    title:       str | None    = Field(None, max_length=200)
    description: str | None    = None
    status:      TaskStatus | None = None
```

### `src/repositories/task_repo.py`

```python
"""In-memory task repository — replaced by PostgreSQL in a later episode."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Optional
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskUpdate

class TaskRepository:
    def __init__(self) -> None:
        self._store: Dict[str, Task] = {}

    def create(self, data: TaskCreate) -> Task:
        task = Task(**data.model_dump())
        self._store[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[Task]:
        return self._store.get(task_id)

    def list_all(self) -> list[Task]:
        return list(self._store.values())

    def update(self, task_id: str, data: TaskUpdate) -> Optional[Task]:
        task = self._store.get(task_id)
        if not task:
            return None
        updates = data.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.now(timezone.utc)
        updated = task.model_copy(update=updates)
        self._store[task_id] = updated
        return updated

    def delete(self, task_id: str) -> bool:
        if task_id not in self._store:
            return False
        del self._store[task_id]
        return True

# Module-level singleton for this episode
task_repo = TaskRepository()
```

### `src/routers/tasks.py`

```python
"""Task CRUD router."""
from fastapi import APIRouter, HTTPException, status
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskUpdate
from src.repositories.task_repo import task_repo

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=list[Task])
async def list_tasks():
    """Return all tasks — the whole yellow brick road."""
    return task_repo.list_all()

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate):
    """Add a new task to the journey."""
    return task_repo.create(data)

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Retrieve a single task by its UUID."""
    task = task_repo.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found.")
    return task

@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: str, data: TaskUpdate):
    """Update a task's status or details."""
    task = task_repo.update(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found.")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Remove a task — even Glinda has to let go."""
    if not task_repo.delete(task_id):
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found.")
```

### Updated `src/main.py`

```python
"""
warp-of-oz-tasks — Episode 2: CRUD endpoints for tasks.
"""
from fastapi import FastAPI
from datetime import datetime
from src.routers.tasks import router as tasks_router

app = FastAPI(
    title="Warp of Oz Tasks",
    description="Follow the yellow brick road — one endpoint at a time.",
    version="0.2.0",
)

app.include_router(tasks_router)

@app.get("/health")
async def health_check():
    return {
        "status": "alive",
        "message": "Toto, I've a feeling we're not in Kansas anymore.",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version,
    }
```

## Testing the CRUD Endpoints 🧪

With the server running (`uv run uvicorn src.main:app --reload --port 8000`):

```bash
# Create a task — the first brick on the road
curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Reach the Emerald City", "description": "Follow the yellow brick road", "status": "todo"}' \
  | python3 -m json.tool

# List all tasks
curl -s http://localhost:8000/tasks | python3 -m json.tool

# Update status — the Scarecrow has his brain
TASK_ID=$(curl -s http://localhost:8000/tasks | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
curl -s -X PATCH "http://localhost:8000/tasks/$TASK_ID" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}' \
  | python3 -m json.tool

# Delete a task
curl -s -X DELETE "http://localhost:8000/tasks/$TASK_ID"
echo "Deleted: $?"
```

Each `curl` in Warp is a Block. You can copy the output, navigate back to it, or `Cmd-Click` it to get AI analysis of the JSON response.

## The Code Review Panel: Toto Lifts the Curtain 🐕

When the agent finishes making changes, open the Code Review panel with `Cmd-Shift-+`. You see a split view: before on the left, after on the right. Changed lines highlighted.

The agent might write something subtly wrong. The code review panel is your Toto — it lifts the curtain. Always review before committing:

```bash
# From the terminal (after reviewing the diff):
cd ~/projects/warp-of-oz-tasks
git add .
git commit -m "feat: add task CRUD endpoints — Ep.2 Scarecrow"
```

## The Project Structure Now 📁

```
~/projects/warp-of-oz-tasks/
├── .python-version
├── pyproject.toml
├── README.md
└── src/
    ├── __init__.py
    ├── main.py              ← health + tasks router ✓
    ├── models/
    │   └── task.py          ← Task model with UUID + enum ✓
    ├── schemas/
    │   └── task.py          ← TaskCreate, TaskUpdate ✓
    ├── repositories/
    │   └── task_repo.py     ← In-memory CRUD store ✓
    └── routers/
        └── tasks.py         ← Full CRUD router ✓
```

In **Episode 3**, the Tin Man joins the road. He needs a heart — not a new organ, but someone who cares enough to write down the rules. WARP.md, Rules, and Skills give Warp's agent the soul of your project.

**🔗 Resources**

- **Warp Agent Mode**: [docs.warp.dev/agent-platform/local-agents](https://docs.warp.dev/agent-platform/local-agents/)
- **Active AI**: [docs.warp.dev/agent-platform/local-agents/active-ai](https://docs.warp.dev/agent-platform/local-agents/active-ai)
- **FastAPI docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

*🌪️ Warp of Oz Series — following the Yellow Brick Road through Warp's Agentic Development Environment, with Augment Code Intent as the ruby slippers.*