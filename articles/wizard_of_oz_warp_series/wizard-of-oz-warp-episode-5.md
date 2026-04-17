---
title: "Warp of Oz! 🌪️ Ep.5: Flying Monkeys — Dispatch Mode"
published: false
description: "Episode 5: The flying monkeys didn't ask permission. They were dispatched, they acted, they reported back. Warp's dispatch mode is the same: autonomous agent execution without approval gates. Add a background task processor to the API — with full autonomy."
tags: [warp, ai, agents, automation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/warp-of-oz-episode-05.png"
series: "Warp of Oz Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Warp of Oz! 🌪️
## Episode 5: Flying Monkeys — Dispatch Mode

> *"Fly! Fly! Fly!"*
> — The Wicked Witch dispatching her monkeys, The Wizard of Oz (1939)

---

## The Moment You Stop Supervising 🙈

In Episodes 2 through 4, every agent action went through you. Plan reviewed. Each command approved. Each diff examined. The agent asked, you answered.

That is **pair mode** — collaborative, visible, safe. It is how you start.

But the flying monkeys did not stop at every tree to ask the Wicked Witch whether to flap their wings. They were given a target and a mandate and they flew. They reported back with the result.

**Dispatch mode** is Warp's equivalent: the agent executes autonomously, without stopping for approval on every step. You set the objective. You come back when it is done. You review the result — not each individual action.

Dispatch mode is earned trust. You use it after you understand what the agent does, after you have WARP.md defining the rules, after you have tests to catch mistakes. You use it for tasks that are well-defined and bounded. And you always review the final diff.

---

## 🗂️ SIPOC — The Flying Monkeys

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| You (dispatching the agent) | A clear, bounded objective + WARP.md constraints | Dispatch mode: agent acts without per-step approval, runs commands, writes files | A complete feature addition: background task processor + endpoints | The codebase — commit-ready after your final review |
| Warp desktop notifications | Long-running agent task completion | Notification when agent needs attention or finishes | Pop-up + in-app notification | You — away from the terminal, get pinged when it matters |
| The code review panel | Complete set of file changes from the dispatch run | `Cmd-Shift-+` shows full diff of everything the agent touched | A reviewable set of changes you accept, reject, or request revision on | Git history — you understand every line that lands |

---

## Enabling Dispatch Mode ⚡

Switch modes in Agent Mode:

- **Pair mode** (default): agent asks approval for each command and file write
- **Dispatch mode** (`Ctrl-Shift-I`): agent operates autonomously until done

The mode indicator appears at the top of the Agent Mode conversation. A lightning bolt icon means dispatch is active.

You can also toggle it mid-conversation:
```
# In Agent Mode:
/dispatch on
```

Or from the keyboard: `Ctrl-Shift-I` toggles between pair and dispatch.

**When to use dispatch:**
- Well-defined tasks with clear success criteria
- Tasks where the scope is bounded (one module, one feature, one test suite)
- After `WARP.md` is in place so the agent has guardrails
- When you are happy to review the final diff rather than each step

**When to stay in pair mode:**
- Security-sensitive changes (auth, secrets, permissions)
- Database schema changes
- Anything touching CI/CD or deployment config
- Anything you would not review quickly in a final diff

---

## The Task: Add a Background Task Processor 🔄

The task management API needs a way to process tasks asynchronously — simulating work that takes time (data processing, external API calls, email sending). This is a well-defined, bounded task. Perfect for dispatch.

The objective:

```
# In Agent Mode, toggle dispatch mode on (Ctrl-Shift-I):

I want to add an asynchronous background task processing system to warp-of-oz-tasks.

Requirements (all per WARP.md conventions):
1. A simple in-memory queue (list) that holds task IDs to process
2. A ProcessingStatus enum: QUEUED, PROCESSING, COMPLETED, FAILED
3. A `processing_status` field added to the Task model (defaults to None)
4. A new endpoint: POST /tasks/{id}/process — adds the task to the queue
5. A new endpoint: GET /tasks/queue/status — returns queue length and IDs
6. A background worker function that simulates processing:
   - Pops a task ID from the queue
   - Sets status to PROCESSING
   - Sleeps 2 seconds (simulating work)
   - Sets status to COMPLETED (or FAILED with 20% probability)
7. Use FastAPI's startup lifecycle to start the worker in an asyncio task
8. Write tests for the /process and /queue/status endpoints

Do NOT use celery, redis, or any external dependencies.
Do NOT touch the authentication middleware.
Keep the worker simple — no persistence, no retries for now.
```

Press `Ctrl-Shift-I` to enable dispatch. Press Enter. The flying monkeys fly.

---

## What Dispatch Mode Looks Like in the Terminal 🐒

In dispatch mode, Warp's block output shows the agent's work as a stream:

```
🤖 Warp Agent [DISPATCH]
━━━━━━━━━━━━━━━━━━━━━━━━

✓ Reading WARP.md...
✓ Reviewing existing codebase structure...
✓ Planning changes:
  □ Update src/models/task.py — add ProcessingStatus enum + processing_status field
  □ Update src/repositories/task_repo.py — add queue + PROCESSING status methods
  □ Add src/routers/processing.py — /process and /queue/status endpoints
  □ Update src/main.py — register processing router + startup event
  □ Write tests/test_processing.py

  Executing plan (dispatch mode — no approval gates)...

  Writing src/models/task.py... ✓
  Writing src/repositories/task_repo.py... ✓
  Writing src/routers/processing.py... ✓
  Updating src/main.py... ✓
  Writing tests/test_processing.py... ✓
  Running: uv run pytest tests/test_processing.py -v... ✓ 3/3 passed

✅ Task complete. Review changes with Cmd-Shift-+ before committing.
```

A desktop notification pops up: **"Warp Agent completed a task"**.

---

## The Code the Agent Produces 📝

### Updated `src/models/task.py`

```python
"""Task domain model — Episode 5: adds ProcessingStatus."""
from __future__ import annotations
import uuid
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO        = "todo"
    IN_PROGRESS = "in_progress"
    DONE        = "done"


class ProcessingStatus(str, Enum):
    QUEUED      = "queued"
    PROCESSING  = "processing"
    COMPLETED   = "completed"
    FAILED      = "failed"


class Task(BaseModel):
    id:                str                      = Field(default_factory=lambda: str(uuid.uuid4()))
    title:             str                      = Field(..., max_length=200)
    description:       str | None               = None
    status:            TaskStatus               = TaskStatus.TODO
    processing_status: ProcessingStatus | None  = None   # None = not queued yet
    created_at:        datetime                 = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at:        datetime                 = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Updated `src/repositories/task_repo.py`

```python
"""In-memory task repository — Episode 5: adds background processing queue."""
from __future__ import annotations
import asyncio
import logging
import random
from collections import deque
from datetime import datetime, timezone
from typing import Deque

from src.models.task import ProcessingStatus, Task
from src.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


class TaskRepository:
    def __init__(self) -> None:
        self._store: dict[str, Task]    = {}
        self._queue: Deque[str]         = deque()   # task IDs awaiting processing
        self._worker_task: asyncio.Task | None = None

    # --- CRUD methods (unchanged from Ep.3) ---
    def create(self, data: TaskCreate) -> Task:
        task = Task(**data.model_dump())
        self._store[task.id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._store.get(task_id)

    def list_all(self) -> list[Task]:
        return list(self._store.values())

    def update(self, task_id: str, data: TaskUpdate) -> Task | None:
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

    # --- Processing queue methods ---
    def enqueue(self, task_id: str) -> Task | None:
        """Add a task to the processing queue. Returns the updated task or None."""
        task = self._store.get(task_id)
        if not task:
            return None
        updated = task.model_copy(update={
            "processing_status": ProcessingStatus.QUEUED,
            "updated_at": datetime.now(timezone.utc),
        })
        self._store[task_id] = updated
        self._queue.append(task_id)
        logger.info("Task %s enqueued for processing. Queue depth: %d", task_id, len(self._queue))
        return updated

    def queue_status(self) -> dict:
        """Return queue depth and pending IDs."""
        return {"queue_length": len(self._queue), "pending_ids": list(self._queue)}

    # --- Background worker ---
    async def _process_next(self) -> None:
        """Pop one task from the queue and simulate processing it."""
        if not self._queue:
            return
        task_id = self._queue.popleft()
        task = self._store.get(task_id)
        if not task:
            logger.warning("Task %s disappeared from store before processing.", task_id)
            return

        # Mark as PROCESSING
        self._store[task_id] = task.model_copy(update={
            "processing_status": ProcessingStatus.PROCESSING,
            "updated_at": datetime.now(timezone.utc),
        })
        logger.info("Processing task %s...", task_id)

        # Simulate work
        await asyncio.sleep(2.0)

        # 80% success, 20% failure
        final_status = (
            ProcessingStatus.COMPLETED
            if random.random() > 0.2
            else ProcessingStatus.FAILED
        )
        self._store[task_id] = self._store[task_id].model_copy(update={
            "processing_status": final_status,
            "updated_at": datetime.now(timezone.utc),
        })
        logger.info("Task %s processing complete: %s", task_id, final_status.value)

    async def worker_loop(self) -> None:
        """Continuous worker: poll the queue every second."""
        logger.info("Background task worker started.")
        while True:
            try:
                await self._process_next()
            except Exception:
                logger.exception("Error in task worker — continuing.")
            await asyncio.sleep(1.0)

    def start_worker(self) -> None:
        """Launch the background worker as an asyncio task."""
        self._worker_task = asyncio.create_task(self.worker_loop())
        logger.info("Worker task created: %s", self._worker_task)


task_repo = TaskRepository()
```

### `src/routers/processing.py`

```python
"""Processing queue router — Episode 5."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, status
from src.models.task import Task
from src.repositories.task_repo import task_repo

router = APIRouter(prefix="/tasks", tags=["processing"])


@router.post("/{task_id}/process", response_model=Task)
async def enqueue_task(task_id: str):
    """Add a task to the background processing queue."""
    result = task_repo.enqueue(task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id!r} not found.",
        )
    return result


@router.get("/queue/status")
async def get_queue_status():
    """Return current queue depth and pending task IDs."""
    return task_repo.queue_status()
```

### Updated `src/main.py` (lifespan for worker startup)

```python
"""warp-of-oz-tasks — Episode 5: background processing added."""
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from src.middleware.auth import APIKeyMiddleware
from src.repositories.task_repo import task_repo
from src.routers.tasks import router as tasks_router
from src.routers.processing import router as processing_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background worker on startup; clean up on shutdown."""
    task_repo.start_worker()
    yield
    if task_repo._worker_task:
        task_repo._worker_task.cancel()


app = FastAPI(
    title="Warp of Oz Tasks",
    version="0.5.0",
    lifespan=lifespan,
)

app.add_middleware(APIKeyMiddleware)
app.include_router(tasks_router)
app.include_router(processing_router)


@app.get("/health")
async def health_check():
    q = task_repo.queue_status()
    return {
        "status": "alive",
        "message": "Toto, I've a feeling we're not in Kansas anymore.",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version,
        "queue_depth": q["queue_length"],
    }
```

---

## Testing in the Terminal 🔬

```bash
# Start server
uv run uvicorn src.main:app --reload --port 8000

# Create a task
TASK_ID=$(curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-oz" \
  -d '{"title": "Process me", "status": "todo"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Queue it for processing
curl -s -X POST "http://localhost:8000/tasks/$TASK_ID/process" \
  -H "X-API-Key: dev-key-oz" | python3 -m json.tool
# processing_status: "queued"

# Check queue depth
curl -s http://localhost:8000/tasks/queue/status \
  -H "X-API-Key: dev-key-oz" | python3 -m json.tool
# {"queue_length": 1, "pending_ids": ["..."]}

# Wait 3 seconds then check the task
sleep 3
curl -s "http://localhost:8000/tasks/$TASK_ID" \
  -H "X-API-Key: dev-key-oz" | python3 -m json.tool
# processing_status: "completed" or "failed"
```

---

## The Final Review: Always Look Behind the Curtain 🔎

After dispatch mode completes, open `Cmd-Shift-+`:
- Verify `src/models/task.py` — is `ProcessingStatus` correctly defined?
- Verify `task_repo.py` — is the worker using `asyncio.sleep` not `time.sleep`?
- Verify `main.py` — is the lifespan context manager correct?

Only after reviewing every file do you commit:

```bash
git add .
git commit -m "feat: add background task processing queue — Ep.5 Flying Monkeys"
```

In **Episode 6**, we enter the Emerald City itself: Oz, Warp's cloud agent platform. Cloud agents, schedules, triggers, and the CLI.

---

**🔗 Resources**
- **Dispatch mode docs**: [docs.warp.dev/agent-platform/local-agents/agent-mode](https://docs.warp.dev/agent-platform/local-agents/agent-mode)
- **FastAPI lifespan events**: [fastapi.tiangolo.com/advanced/events](https://fastapi.tiangolo.com/advanced/events/)
- **asyncio.create_task**: [docs.python.org/3/library/asyncio-task.html](https://docs.python.org/3/library/asyncio-task.html)

---

*🌪️ Warp of Oz Series — following the Yellow Brick Road through Warp's Agentic Development Environment.*
