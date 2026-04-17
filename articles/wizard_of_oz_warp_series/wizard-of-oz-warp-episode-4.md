---
title: "Warp of Oz! 🌪️ Ep.4"
published: false
description: "Episode 4: The Cowardly Lion had courage all along — he just needed permission to use it. Warp's Agent pair mode lets you review every change before it lands, the code review panel is your safety net, and debugging an intentional error teaches you to read the diff before trusting it."
tags: [warp, debugging, ai, workflow]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/warp-of-oz-episode-04.png"
series: "Warp of Oz Series"
canonical_url: ""
organization: "the-software-s-journey"
---
## Episode 4: The Lion Gets Courage

> "All right, I'll go in there for Dorothy. Wicked Witch or no Wicked Witch, guards or no guards, I'll tear them apart. I may not come out alive, but I'm going in there."— The Cowardly Lion, The Wizard of Oz (1939)

## The Courage Problem 🦁

The Cowardly Lion roared at everything but ran from most things. His problem was not ability — it was trust. He did not trust himself to act without catastrophic consequences.

Many developers using AI agents feel the same way. The agent writes code. It looks plausible. It might be right. Or it might delete your database. You approve commands nervously, or you do not approve them at all, or you spend more time second-guessing than the agent saves.

The answer is not to run blind. The answer is the **Code Review panel**, the **pair mode workflow**, and the habit of reading the diff before accepting it. Courage is not recklessness — it is informed action.

This episode plants an intentional bug, lets the agent find and fix it, and teaches you to read every diff like the Cowardly Lion reading a battle plan before the charge.

## 🗂️ SIPOC — The Courage to Act

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (planting a bug deliberately) | A subtle logic error in task_repo.py | The server starts, tests fail in a non-obvious way | A broken endpoint with a misleading error message | The debugging session — Episode 4's main exercise |
| Warp Active AI | Non-zero exit code + stack trace in the terminal Block | Automatic Suggested Code Diff chip appears | A proposed fix in an expandable diff chip | You — review before accepting |
| Warp Agent Mode (pair) | "Debug the failing task update endpoint" prompt | Agent reads the code, identifies the bug, proposes a fix | A file diff in the Code Review panel | You — review line by line before approving |
| The Code Review panel (Cmd-Shift-+) | The proposed diff from any agent action | Visual before/after split view with syntax highlighting | Informed approval — you understand what lands | Your git history — no mysteries in the diff |

## Planting the Bug: The Wicked Witch Enters 🧙‍♀️

Let's introduce a subtle error in the update method. Not an obvious typo — something that passes a casual read but fails in a specific case.

```bash
# In Warp's built-in file editor, or with your editor of choice:
# We're going to introduce a bug in src/repositories/task_repo.py
```

Open `src/repositories/task_repo.py` and change the `update` method:

```python
# BUG INTRODUCED: model_copy called with `update=` kwarg that shadows the method name
# Also: updated_at is set BEFORE copying, so it doesn't appear in the response
def update(self, task_id: str, data: TaskUpdate) -> Optional[Task]:
    task = self._store.get(task_id)
    if not task:
        return None
    updates = data.model_dump(exclude_unset=True)
    # BUG 1: We mutate `task` directly instead of creating a copy
    # BUG 2: We set updated_at on the original, then copy — order matters in Pydantic v2
    task.updated_at = datetime.now(timezone.utc)   # mutating an immutable model!
    updated = task.model_copy(update=updates)
    self._store[task_id] = updated
    return updated
```

Save it. Now let's confirm the bug:

```bash
# Start the server
uv run uvicorn src.main:app --reload --port 8000

# Create a task
curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-oz" \
  -d '{"title": "Cross the poppy field", "status": "todo"}' \
  | python3 -m json.tool

TASK_ID=$(curl -s http://localhost:8000/tasks -H "X-API-Key: dev-key-oz" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

# Update the task
curl -s -X PATCH "http://localhost:8000/tasks/$TASK_ID" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-oz" \
  -d '{"status": "done"}' \
  | python3 -m json.tool
# The status updates but updated_at is WRONG — it shows the original created_at time
# Because we set updated_at on the original THEN copy, Pydantic v2 field validators fire wrong
```

The bug is subtle: the `updated_at` in the response is not actually updated. The task appears modified but the timestamp lies.

## Active AI to the Rescue: The Suggested Code Diff 🔧

After the PATCH request returns an incorrect timestamp, look at the block output in Warp. Active AI analyses the response — it can infer from context (the Pydantic model definition + the response) that something is off.

A chip appears near the block: **"Suggested Fix — view diff"**. Click it.

Warp shows a unified diff:

```diff
-    task.updated_at = datetime.now(timezone.utc)   # mutating an immutable model!
-    updated = task.model_copy(update=updates)
+    updates["updated_at"] = datetime.now(timezone.utc)
+    updated = task.model_copy(update=updates)
```

That is the correct fix. The `updated_at` should go into the `updates` dict so `model_copy` applies it along with the user-supplied fields.

Click **Apply** in Warp's suggested diff chip. The file is updated.

## Agent Mode for Deeper Debugging 🔍

Sometimes Active AI's surface suggestion is not enough. Use Agent Mode for a thorough investigation:

```
# In Agent Mode (Cmd-I):

The PATCH /tasks/{id} endpoint is misbehaving. When I update a task's status,
the response shows the correct new status, but the updated_at timestamp
appears to be the same as created_at — it's not being refreshed.

Please:
1. Read the current src/repositories/task_repo.py
2. Identify why updated_at is not correctly appearing in the response
3. Fix the bug
4. Write a test in tests/test_task_updates.py that would have caught this
5. Run the test to confirm it passes
```

The agent responds with a plan:

```
Investigating...

Reading src/repositories/task_repo.py...
Found issue: updated_at is set directly on the task instance before model_copy().
In Pydantic v2, models are immutable by default. Setting task.updated_at directly
raises a ValidationError silently if model_config forbids mutation, or creates a
copy-on-set that is then discarded when model_copy() runs.

Fix: add updated_at to the updates dict BEFORE calling model_copy().

Writing test...
```

### The test the agent writes: `tests/test_task_updates.py`

```python
"""Tests that confirm updated_at is refreshed on PATCH."""
from __future__ import annotations
import asyncio
import time
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

API_KEY = "dev-key-oz"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

@pytest.mark.asyncio
async def test_update_refreshes_updated_at():
    """updated_at should change when a task is PATCHed."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create task
        create_resp = await client.post(
            "/tasks",
            json={"title": "Cross the poppy field", "status": "todo"},
            headers=HEADERS,
        )
        assert create_resp.status_code == 201
        task = create_resp.json()
        original_updated_at = task["updated_at"]

        # Wait a tiny bit so timestamps differ
        await asyncio.sleep(0.01)

        # Update task
        patch_resp = await client.patch(
            f"/tasks/{task['id']}",
            json={"status": "done"},
            headers=HEADERS,
        )
        assert patch_resp.status_code == 200
        updated = patch_resp.json()

        assert updated["status"] == "done"
        assert updated["updated_at"] != original_updated_at, (
            "updated_at should be refreshed after a PATCH"
        )
```

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio httpx

# Create pytest config
cat >> pyproject.toml << 'TOML'

[tool.pytest.ini_options]
asyncio_mode = "auto"
TOML

# Run the test
uv run pytest tests/test_task_updates.py -v
# PASSED tests/test_task_updates.py::test_update_refreshes_updated_at
```

## The Code Review Panel: Reading Every Diff 📋

Every time the agent makes a file change, open the Code Review panel:

`Cmd-Shift-+`

You see:

- A file tree on the left listing all changed files
- A split diff view: original on the left, proposed on the right
- Added lines in green, removed lines in red
- The ability to leave inline comments (click the `+` in the margin)

Before approving any agent change, scroll through every changed file. Ask yourself:

1. Does this change make sense given what I asked?
2. Are there any lines I did not expect?
3. Does it follow the conventions in `WARP.md`?

The Code Review panel is Toto. It pulls back the curtain. The Wizard is behind there — a very good LLM, but not infallible.

### Inline feedback to the agent

Click the `+` icon on any line in the review panel and type a comment:

```
This function is now 40 lines — can we extract the date logic into a helper?
```

The agent reads your comment and revises. Iterative review. The Cowardly Lion charging in, getting feedback, charging better.

## The Corrected `update` Method 🏆

After the agent's fix and the passing test, here is the correct implementation:

```python
def update(self, task_id: str, data: TaskUpdate) -> Optional[Task]:
    """Update a task's fields. Returns None if not found."""
    task = self._store.get(task_id)
    if not task:
        return None
    updates = data.model_dump(exclude_unset=True)
    updates["updated_at"] = datetime.now(timezone.utc)   # in the dict, not on the instance
    updated = task.model_copy(update=updates)
    self._store[task_id] = updated
    return updated
```

One line moved. One conceptual model corrected: in Pydantic v2, `model_copy(update=...)` is the way to produce a new instance with changed fields. Do not mutate first, then copy.

## Adding a `conftest.py` for Clean Test Isolation 🧹

The agent also notices (if you ask) that tests share the module-level `task_repo` singleton. Tests will bleed into each other. It proposes:

```python
# tests/conftest.py
"""Pytest configuration — reset in-memory stores between tests."""
import pytest
from src.repositories.task_repo import task_repo

@pytest.fixture(autouse=True)
def reset_task_repo():
    """Clear the in-memory task store before each test."""
    task_repo._store.clear()
    yield
    task_repo._store.clear()
```

## The Project Structure Now 📁

```
~/projects/warp-of-oz-tasks/
├── .warp/skills/add-endpoint.md
├── WARP.md
├── pyproject.toml
├── tests/
│   ├── conftest.py            ← test isolation ✓
│   └── test_task_updates.py   ← bug regression test ✓
└── src/
    ├── config.py
    ├── main.py
    ├── middleware/auth.py
    ├── models/task.py
    ├── repositories/task_repo.py    ← bug fixed ✓
    ├── schemas/task.py
    └── routers/tasks.py
```

```bash
git add .
git commit -m "fix: correct updated_at mutation bug in task_repo — Ep.4 Lion"
```

In **Episode 5**, the flying monkeys arrive. They go where the agent cannot go alone. Dispatch mode — autonomous operation without constant approval.

**🔗 Resources**

- **Warp Code Review panel**: [docs.warp.dev/agent-platform/local-agents/agent-mode](https://docs.warp.dev/agent-platform/local-agents/agent-mode)
- **Pair vs. Dispatch mode**: [docs.warp.dev/agent-platform/local-agents](https://docs.warp.dev/agent-platform/local-agents/)
- **pytest-asyncio**: [pytest-asyncio.readthedocs.io](https://pytest-asyncio.readthedocs.io)

*🌪️ Warp of Oz Series — following the Yellow Brick Road through Warp's Agentic Development Environment.*