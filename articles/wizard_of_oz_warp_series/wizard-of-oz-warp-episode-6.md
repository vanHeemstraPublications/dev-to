---
title: "Warp of Oz! 🌪️ Ep.6: The Emerald City — Oz Platform"
published: false
description: "Episode 6: Dorothy finally sees the Emerald City glowing on the horizon — and it is everything promised. Oz is Warp's cloud agent orchestration platform. Cloud agents, scheduled runs, the Oz CLI, and running a cleanup agent on a schedule. The Emerald City, explained."
tags: [warp, agents, cloud, automation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/warp-of-oz-episode-06.png"
series: "Warp of Oz Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Warp of Oz! 🌪️
## Episode 6: The Emerald City — Oz Platform

> *"There it is, Toto. The Emerald City."*
> — Dorothy, first sighting, The Wizard of Oz (1939)

---

## The City on the Horizon 🏙️

From the poppy field, Dorothy first saw the Emerald City as a green glow on the horizon. It was always there — from the moment she landed in Oz. She just had not reached it yet.

The Oz platform has been on the horizon since Episode 1. We installed Warp, learned its terminal features, gave the agent a brain, a heart, and courage. Now we enter the city itself.

**Oz** (`oz.warp.dev`) is Warp's cloud agent orchestration platform. While local agents run in your terminal on your Mac Mini, cloud agents run in the background — on Warp's infrastructure or your own — triggered by schedules, webhooks, Slack messages, GitHub PRs, or Linear issues. They spin up, do their work, report back, and disappear.

They are not flying monkeys (dispatch mode). They are the infrastructure of the city itself: always running, always watching, always ready.

---

## 🗂️ SIPOC — The Emerald City

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| You (or a trigger) | A prompt + optional environment config | Oz orchestration layer creates a cloud task, spins up environment, runs agent | A completed agent run with full audit trail, PR, or Slack report | Your team — visible at oz.warp.dev and in the Warp app |
| A schedule (cron expression) | A configured Oz schedule + skill/prompt | At the scheduled time, Oz starts an agent with the defined prompt | A scheduled run (e.g., daily at 02:00 UTC) | Automated maintenance — no human needed to kick it off |
| A GitHub PR event (integration) | New PR opened against main | Oz integration catches the event, starts an agent to review the PR | PR review comment from the agent, summary of changes | Your team's PR review queue — AI does first pass |
| The Oz CLI (`oz`) | Agent run command from terminal, CI, or script | Oz CLI authenticates, submits the run, streams output | A tracked, auditable agent run accessible at oz.warp.dev | Any script that needs to launch an agent programmatically |

---

## Installing the Oz CLI 📦

The Oz CLI is already bundled in Warp — you may already have it. Confirm:

```bash
# Check if oz is available
which oz
# /opt/homebrew/bin/oz  or  /Users/you/.local/bin/oz

oz --version
# oz 0.x.x

# If not installed, get it:
brew install warp-dev/tap/oz
# Or download from: docs.warp.dev/agent-platform/cloud-agents/platform#cli
```

### Authenticate

```bash
oz auth login
# Opens browser → sign in with your Warp account
# Token stored locally

oz auth status
# Logged in as: you@example.com
# Team: your-team
```

---

## The Oz Platform Concepts 🏛️

Think of Oz as three layers stacked on the Emerald City:

**Environments** — Docker containers with your code cloned inside. An environment is the "apartment" where the agent lives while working. It has your repositories, startup commands, and secrets injected. You define environments once; every agent run in that environment starts from the same state.

**Triggers** — the events that start agent runs: schedules, integrations (Slack, Linear, GitHub), webhooks, the Oz CLI, or the API. A trigger fires → Oz orchestration layer creates a task → task is assigned to a host → environment spins up → agent executes.

**Skills** — reusable instruction sets (`.md` files) that define what the agent knows how to do in your project. The same `SKILL.md` files you created in Episode 3 work as Oz Skills.

**Hosts** — where agent execution happens. Warp's managed cloud (default), or your own infrastructure (self-hosted, Enterprise feature).

---

## Setting Up an Oz Environment for `warp-of-oz-tasks` 🌿

```bash
# Create a new Oz environment via the CLI
oz env create \
  --name "warp-of-oz-tasks" \
  --repo "https://github.com/yourname/warp-of-oz-tasks" \
  --startup-command "uv sync" \
  --description "FastAPI task API — Warp of Oz series"

# Or via the Oz web app at oz.warp.dev:
# New Environment → add repo URL → startup command → save
```

The environment clones your repository, runs `uv sync` to install dependencies, and is then ready for agent tasks. Every cloud agent run for this project starts from this state.

### Secrets

```bash
# Add the API key as an Oz secret (not hardcoded in the environment)
oz secret set API_KEYS "prod-key-emerald-city"

# Secrets are injected as environment variables when the agent runs
# The agent sees: export API_KEYS="prod-key-emerald-city"
```

---

## Running a Cloud Agent from the CLI 🚀

Let's run a code quality check as a cloud agent:

```bash
# Launch a cloud agent to audit the codebase
oz agent run \
  --env "warp-of-oz-tasks" \
  --prompt "Run ruff check on the entire src/ directory. Report all issues found. If there are fixable issues, apply the fixes with ruff --fix and report what was changed." \
  --model "claude-opus-4-5"

# Output:
# ✓ Task created: task_01abc123
# ✓ Environment warming up...
# ✓ Agent running...
#
# Agent output:
# Running: ruff check src/
# src/routers/tasks.py:3:1: F401 [*] 'fastapi.status' imported but unused
# Found 1 fixable error.
# Applying fix...
# Fixed: src/routers/tasks.py
#
# ✓ Complete. View run: https://oz.warp.dev/runs/task_01abc123
```

You get a link to the full run audit trail. Every command the agent ran, every file it touched, every decision it made — all logged and accessible.

---

## Scheduling a Cleanup Agent 🕐

One of the most useful Oz patterns: scheduled maintenance agents. In our case, we want to clean up "orphaned" failed tasks daily.

### Create the cleanup Skill

```bash
cat > ~/projects/warp-of-oz-tasks/.warp/skills/cleanup-failed-tasks.md << 'MARKDOWN'
# Skill: Clean Up Failed Tasks

Use this skill when asked to clean up failed processing tasks.

## What to do

1. GET /tasks from the API (include X-API-Key header from environment)
2. Filter tasks where `processing_status == "failed"` AND `status != "done"`
3. For each failed task, PATCH its `status` to "done" with a note in description
4. Report: how many tasks were cleaned up, list their IDs
5. If no failed tasks found, report "No failed tasks found — the road is clear."

## Context

- API runs at: $API_BASE_URL (injected from environment)
- Auth header: X-API-Key: $API_KEY
- This is maintenance work — do not create or delete tasks, only update status
MARKDOWN
```

### Create the Oz schedule

```bash
oz schedule create \
  --name "daily-cleanup" \
  --env "warp-of-oz-tasks" \
  --cron "0 2 * * *" \
  --prompt "Use the cleanup-failed-tasks skill to clean up any failed processing tasks." \
  --description "Daily 02:00 UTC — sweep the yellow brick road clean"

# Verify
oz schedule list
# NAME             CRON         STATUS    LAST RUN
# daily-cleanup    0 2 * * *    active    never
```

Or via the Oz web app at `oz.warp.dev`:
- New Schedule → name `daily-cleanup` → cron `0 2 * * *` → environment `warp-of-oz-tasks` → prompt (the cleanup skill instruction) → Save

From now on, every day at 02:00 UTC, Oz spins up an agent in the `warp-of-oz-tasks` environment and cleans up failed tasks. No human intervention. No cron job to maintain. The flying monkeys, running on a schedule.

---

## Integrations: Triggered by External Events 🔔

Oz integrations connect external event sources to agent runs. The most useful for a development team:

### GitHub Integration: PR Review Agent

```bash
# In the Oz web app: Integrations → GitHub → Connect repo
# Select: "When PR is opened → start agent"
# Prompt:
# "Review the code changes in this PR. Check for:
#  1. Compliance with WARP.md conventions
#  2. Missing type hints
#  3. Missing tests for new endpoints
#  4. Security issues in the auth middleware
#  Post a summary comment on the PR."
```

When a developer opens a PR against `main`, Oz automatically spins up an agent, reviews the diff, and posts a comment. The first review is always from a flying monkey.

### Slack Integration: On-Demand Agents

```bash
# Configure in Oz web app: Integrations → Slack
# Trigger: @oz run-cleanup in #dev-ops channel
# → starts the daily-cleanup agent on demand
```

Team members can trigger agents directly from Slack without opening a terminal.

---

## Monitoring Running Agents 👁️

```bash
# List recent runs
oz runs list --env warp-of-oz-tasks --limit 10

# Get details on a specific run
oz runs get task_01abc123

# Stream live output from a running agent
oz runs attach task_01abc123

# List all active runs (across all environments)
oz runs list --status running
```

At `oz.warp.dev`, you can join a running agent session with one click — see what it is doing, provide steering input, or stop it.

From the Warp app itself, open the Oz pane (left sidebar → Oz icon) to see all running and recent cloud agent tasks alongside your local terminal sessions.

---

## The Oz SDK: Programmatic Agent Orchestration 🔧

For teams building internal tools or CI/CD integrations, the Oz SDK lets you trigger and monitor agents from code:

```typescript
// TypeScript SDK example (can be run from CI or a Node.js script)
import { OzClient } from "@warp-dev/oz";

const oz = new OzClient({ apiKey: process.env.OZ_API_KEY! });

// On every CI failure: start a debugging agent
async function onCIFailure(repo: string, prNumber: number) {
  const run = await oz.runs.create({
    environment: "warp-of-oz-tasks",
    prompt: `
      A CI run failed on PR #${prNumber} in ${repo}.
      Please:
      1. Read the CI failure log attached as context
      2. Identify the root cause
      3. Propose a fix with a diff
      4. Post the proposed fix as a PR comment
    `,
    model: "claude-sonnet-4-6",
  });

  console.log(`Agent started: ${run.id}`);
  console.log(`Track at: ${run.sessionUrl}`);
}
```

---

## The Project and the City Together 🏙️

The Emerald City did not replace the Yellow Brick Road — it was the destination. Oz (the platform) does not replace local agents and the terminal — it extends them to the cloud.

Your workflow as of Episode 6:

```
Mac Mini M4 Pro (Warp Terminal)
├── Local development: blocks, AI completions, #key
├── Local agents: pair mode for careful work, dispatch for autonomous tasks
├── Code review panel: always review the diff
└── Oz CLI: trigger, monitor, and join cloud runs from your terminal

oz.warp.dev (Oz Platform)
├── Environment: warp-of-oz-tasks (Docker + git + uv sync)
├── Schedule: daily-cleanup at 02:00 UTC
├── Integration: GitHub PR review on every PR
└── Audit trail: every run, every command, every diff — logged
```

```bash
git add .
git commit -m "feat: add Oz environment, cleanup skill, schedule — Ep.6 Emerald City"
```

In **Episode 7**, the ruby slippers. Augment Code Intent joins the road — spec-driven development that combines Intent's Context Engine with Warp's terminal workflow.

---

**🔗 Resources**
- **Oz platform**: [oz.warp.dev](https://oz.warp.dev)
- **Oz documentation**: [docs.warp.dev/agent-platform](https://docs.warp.dev/agent-platform/)
- **Oz CLI reference**: [docs.warp.dev/agent-platform/cloud-agents/platform#cli](https://docs.warp.dev/agent-platform/cloud-agents/platform)
- **Warp blog: Introducing Oz**: [warp.dev/blog/oz-orchestration-platform-cloud-agents](https://www.warp.dev/blog/oz-orchestration-platform-cloud-agents)

---

*🌪️ Warp of Oz Series — following the Yellow Brick Road through Warp's Agentic Development Environment.*
