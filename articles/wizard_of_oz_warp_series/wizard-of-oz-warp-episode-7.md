---
title: "Warp of Oz! 🌪️ Ep.7"
published: false
description: "Episode 7: Glinda told Dorothy she always had the power to go home. The ruby slippers were there all along. Augment Code Intent is that power: spec-driven multi-agent development that, combined with Warp, gives you the full stack of agentic coding. The slippers click three times."
tags: [warp, augmentcode, agents, productivity]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/warp-of-oz-episode-07.png"
series: "Warp of Oz Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: The Ruby Slippers — Augment Code Intent

> "You've always had the power, my dear. You just had to learn it for yourself."— Glinda the Good Witch, The Wizard of Oz (1939)

## The Slippers Were Always There 💎

Throughout the series, we built a capable workflow: Warp's terminal with AI, local agents with pair and dispatch modes, WARP.md giving the agent memory, Oz running cloud agents on schedules. That is a lot of power.

And still, there is something missing in the picture. Warp's agent is excellent at *executing*. What about *planning and coordinating at scale*? What about features that touch eight files across three modules, where one agent might lose the thread of what the other is doing? What about the "living spec" — a document that captures the full intent of a feature and stays accurate as it is built?

That is where **Augment Code Intent** appears, like Glinda at the end of the road.

Intent is Augment's standalone macOS desktop workspace. It is spec-driven multi-agent orchestration: you write a living specification that describes what you want to build. A Coordinator agent breaks the spec into parallel tasks. Specialist agents implement those tasks in isolated git worktrees, each with full understanding of your codebase via Augment's Context Engine. A Verifier agent validates the results against the original spec. The spec itself updates as work is completed — it is always accurate.

In this episode: how Intent and Warp work together, and how to use them to add a non-trivial feature to `warp-of-oz-tasks`.

## 🗂️ SIPOC — The Ruby Slippers

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (writing the spec in Intent) | A natural language feature description with requirements and acceptance criteria | Intent Coordinator agent breaks spec into parallel tasks → Implementor agents execute in isolated worktrees with Context Engine | Code changes across multiple files, validated against the spec | Your codebase — via git merge of the worktrees |
| Augment Context Engine | Your entire codebase (indexed by Intent) | Semantic dependency graph construction: maps cross-file relationships, pattern usage, API contracts | Deep contextual understanding for every agent in the workspace | Every implementor agent — never misses a dependency |
| Warp Terminal (on Mac Mini M4 Pro) | Intent's output: a git branch with the feature implementation | Review diff in Warp's Code Review panel → run tests with uv run pytest → commit | Reviewed, tested, committed feature | Your warp-of-oz-tasks repository |
| WARP.md (from Episode 3) | Project conventions file | Intent can read WARP.md as part of codebase indexing | Agents follow your conventions without re-specifying them | Code that fits the existing codebase style |

## Installing Augment Code Intent 🔧

Intent is a macOS desktop app (currently in public beta):

```bash
# Download from augmentcode.com/product/intent
# Drag to /Applications — runs natively on Apple Silicon

# Or install the Augment CLI for terminal integration
brew install augmentcode/tap/augment
# Then sign in:
augment auth login
```

Intent requires an Augment account. During the beta, it uses regular Augment credits — no separate Intent pricing.

## The Warp + Intent Workflow 🤝

The two tools play different roles. Understanding the division makes you faster:

| Task | Best tool |
| --- | --- |
| Individual command execution | Warp terminal |
| Quick single-file changes | Warp local agent (pair mode) |
| Autonomous multi-step automation | Warp dispatch mode |
| Background/scheduled maintenance | Oz cloud agents |
| Multi-file feature with clear spec | Augment Intent |
| Cross-service changes | Augment Intent |
| PR review automation | Oz + GitHub integration |
| Running tests, linting, git commands | Warp terminal blocks |
| Reviewing any agent's output | Warp Code Review panel |

The pattern: **Intent designs and implements the feature. Warp runs it.**

Intent produces a git branch. You switch to Warp, check out that branch, review the diff in the Code Review panel, run tests in terminal blocks, and commit if satisfied. The terminal is always the final gate.

## Opening `warp-of-oz-tasks` in Intent 📂

1. Launch Intent
2. **New Workspace** → select `~/projects/warp-of-oz-tasks`
3. Intent indexes the codebase (~30 seconds for a small project like this)
4. You see: the file tree, the workspace chat, and the spec panel

Intent reads `WARP.md` automatically — it is part of the codebase context. All the conventions you defined in Episode 3 are already loaded.

## Writing the Living Spec 📄

Intent's most important concept is the **living spec**. Instead of typing a prompt and hoping the agent stays on track, you write a structured specification:

Click `New Spec` in the spec panel. Intent opens a Markdown editor. Write:

```markdown
# Feature: Task Tags and Filtering

## Overview
Add a tagging system to the task API so that tasks can be categorised 
with multiple tags and then filtered by tag.

## Requirements

### Data Model
- A task can have zero or more tags (list of strings, e.g. ["urgent", "backend"])
- Tags are stored as a list on the Task model
- Maximum 10 tags per task, each max 50 characters
- Tags are case-insensitive (stored as lowercase)

### API Changes
- POST /tasks — accept optional `tags` field (list of strings)
- PATCH /tasks/{id} — allow updating tags (full replacement, not merge)
- GET /tasks — add `?tag=urgent` query parameter to filter by single tag
- GET /tasks — add `?tags=urgent,backend` to filter by multiple tags (AND logic)

### Conventions (from WARP.md)
- Pydantic v2 validation on all new fields
- snake_case JSON, async def endpoints
- Tags normalised to lowercase in the repository, not in the router
- New validation: raise 422 if more than 10 tags or any tag > 50 chars

## Acceptance Criteria
- [ ] POST /tasks with tags: ["URGENT", "Backend"] stores ["urgent", "backend"]
- [ ] GET /tasks?tag=urgent returns only tasks with "urgent" in their tags
- [ ] GET /tasks?tags=urgent,backend returns tasks with BOTH tags
- [ ] PATCH with tags=[] clears all tags on a task
- [ ] Tags exceeding 10 or 50-char limit are rejected with 422
- [ ] All acceptance criteria are covered by pytest tests
- [ ] Tests pass with `uv run pytest tests/ -v`
```

Click **Create Spec**. Intent reads it, analyses the codebase, and begins planning.

## The Coordinator Plans the Work 🗂️

Intent's Coordinator agent breaks the spec into parallel tasks:

```
Coordinator planning...

Analysed codebase. Dependencies identified:
  - src/models/task.py → update Task model
  - src/schemas/task.py → update TaskCreate, TaskUpdate
  - src/repositories/task_repo.py → update list_all to support filtering
  - src/routers/tasks.py → update create/update/list routes
  - tests/test_tags.py → new test file (no dependencies — can start immediately)

Parallel plan:
  Worktree A: Update model + schema (foundation — blocks others)
  Worktree B: Write tests (can start from spec — no dependency on implementation)

  After Worktree A merges:
  Worktree C: Update repository (depends on updated model)
  Worktree D: Update router (depends on updated schema + repository interface)

  After all merge:
  Verifier: Run tests and validate against acceptance criteria
```

Each worktree is an isolated git checkout. Agents work in parallel without conflicting.

## Watching Intent Work 🔭

Intent's workspace view shows:

- **Spec panel**: the living spec, with checkboxes ticking as criteria are met
- **Agent panels**: one per active implementor, showing what each is doing
- **File tree**: changed files highlighted as agents modify them
- **Messages**: the Coordinator's commentary as the plan evolves

You can send messages to the Coordinator mid-run:

```
> Make sure the tag normalisation happens in the repository layer, 
  not in the Pydantic validator. WARP.md says business logic stays out of routers.
```

The Coordinator reads your message, adjusts the plan, and instructs the relevant implementor.

## The Code Intent Produces 📝

### Updated `src/models/task.py`

```python
class Task(BaseModel):
    id:                str                     = Field(default_factory=lambda: str(uuid.uuid4()))
    title:             str                     = Field(..., max_length=200)
    description:       str | None              = None
    status:            TaskStatus              = TaskStatus.TODO
    tags:              list[str]               = Field(default_factory=list)  # NEW
    processing_status: ProcessingStatus | None = None
    created_at:        datetime                = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at:        datetime                = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Updated `src/schemas/task.py`

```python
from pydantic import BaseModel, Field, field_validator

class TaskCreate(BaseModel):
    title:       str           = Field(..., min_length=1, max_length=200)
    description: str | None    = None
    status:      TaskStatus    = TaskStatus.TODO
    tags:        list[str]     = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("A task may have at most 10 tags.")
        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"Tag {tag!r} exceeds maximum length of 50 characters.")
        return v   # normalisation happens in the repository, not here

class TaskUpdate(BaseModel):
    title:       str | None        = Field(None, max_length=200)
    description: str | None        = None
    status:      TaskStatus | None = None
    tags:        list[str] | None  = None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("A task may have at most 10 tags.")
        for tag in v:
            if len(tag) > 50:
                raise ValueError(f"Tag {tag!r} exceeds maximum length of 50 characters.")
        return v
```

### Updated `src/repositories/task_repo.py` — `create`, `update`, `list_all`

```python
def create(self, data: TaskCreate) -> Task:
    dumped = data.model_dump()
    # Normalise tags to lowercase — business logic lives here, not in the router
    dumped["tags"] = [t.lower() for t in dumped.get("tags", [])]
    task = Task(**dumped)
    self._store[task.id] = task
    return task

def update(self, task_id: str, data: TaskUpdate) -> Task | None:
    task = self._store.get(task_id)
    if not task:
        return None
    updates = data.model_dump(exclude_unset=True)
    if "tags" in updates and updates["tags"] is not None:
        updates["tags"] = [t.lower() for t in updates["tags"]]
    updates["updated_at"] = datetime.now(timezone.utc)
    updated = task.model_copy(update=updates)
    self._store[task_id] = updated
    return updated

def list_all(self, tags: list[str] | None = None) -> list[Task]:
    tasks = list(self._store.values())
    if tags:
        normalised = [t.lower() for t in tags]
        tasks = [t for t in tasks if all(tag in t.tags for tag in normalised)]
    return tasks
```

### Updated `src/routers/tasks.py` — `list_tasks` endpoint

```python
@router.get("/", response_model=list[Task])
async def list_tasks(
    tag:  str | None = None,
    tags: str | None = None,
):
    """Return all tasks, optionally filtered by tag(s).

    Use ?tag=urgent for a single tag filter.
    Use ?tags=urgent,backend for multi-tag AND filter.
    """
    tag_filter: list[str] | None = None
    if tags:
        tag_filter = [t.strip() for t in tags.split(",") if t.strip()]
    elif tag:
        tag_filter = [tag]
    return task_repo.list_all(tags=tag_filter)
```

## Intent Updates the Spec as Work Completes 📋

As each acceptance criterion is met, Intent ticks the checkbox in the living spec:

```
## Acceptance Criteria
- [x] POST /tasks with tags: ["URGENT", "Backend"] stores ["urgent", "backend"]
- [x] GET /tasks?tag=urgent returns only tasks with "urgent" in their tags
- [x] GET /tasks?tags=urgent,backend returns tasks with BOTH tags
- [x] PATCH with tags=[] clears all tags on a task
- [x] Tags exceeding 10 or 50-char limit are rejected with 422
- [x] All acceptance criteria are covered by pytest tests
- [ ] Tests pass with `uv run pytest tests/ -v`  ← running now
```

When all boxes are ticked, Intent surfaces: **"Feature complete — ready to review in Warp."**

## Bringing It to Warp: The Final Review 🔎

Intent creates a branch: `intent/task-tags-and-filtering`. Switch to Warp:

```bash
# In Warp terminal:
cd ~/projects/warp-of-oz-tasks
git fetch origin
git checkout intent/task-tags-and-filtering

# Review in Code Review panel
# Cmd-Shift-+  → review every changed file

# Run the tests Intent wrote
uv run pytest tests/ -v

# All green? Merge.
git checkout main
git merge intent/task-tags-and-filtering
git push origin main

git tag v0.7.0
git commit --amend --no-edit
```

The ruby slippers clicked three times. The feature is home.

## The Warp + Intent Integration Pattern: Summary 🗺️

```
INTENT (Augment Code)              WARP (Terminal + Oz)
──────────────────────             ─────────────────────
Write living spec          →       
Context Engine indexes codebase    
Coordinator plans parallel tasks   
Implementors execute in worktrees  
Verifier checks acceptance criteria
Feature complete → branch ready    →  git fetch + checkout

                                   Code Review panel (Cmd-Shift-+)
                                   uv run pytest
                                   Quick fixes in pair/dispatch mode
                                   git merge + git push

                                   Oz schedule checks new merged code
                                   → PR review agent triggered on merge
```

The flow is: Intent for the *why* and *what* (spec-driven). Warp for the *how* and *when* (execution and deployment). Neither replaces the other. Together they are the full yellow brick road.

## Advice: When to Use Intent vs Warp Agent

**Use Intent when:**

- The feature requires changes to 4+ files with interdependencies
- You want a written spec that the team can review before any code is written
- The work benefits from parallel agent execution (speed)
- You want the living spec as documentation

**Use Warp Agent (local or dispatch) when:**

- Single-file changes or simple additions
- Debugging (Agent Mode + code review panel)
- Quick automation or maintenance tasks
- You want to stay in the terminal without switching apps

**Use Oz cloud agents when:**

- Scheduled maintenance tasks
- PR review or CI failure response
- Background processing unrelated to your active work

```bash
git add .
git commit -m "feat: task tags + filtering — Ep.7 Ruby Slippers (Intent + Warp)"
```

In **Episode 8**, we close the loop: the complete production workflow, MCP servers, Warp Drive for teams, and — there's no place like home.

**🔗 Resources**

- **Augment Code Intent**: [augmentcode.com/product/intent](https://www.augmentcode.com/product/intent)
- **Intent documentation**: [augmentcode.com](https://www.augmentcode.com)
- **Spec-driven development manifesto**: [augmentcode.com/product/intent](https://www.augmentcode.com/product/intent)
- **Context Engine**: [augmentcode.com](https://www.augmentcode.com)

*🌪️ Warp of Oz Series — following the Yellow Brick Road through Warp's Agentic Development Environment, with Augment Code Intent as the ruby slippers.*