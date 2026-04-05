---
title: "Charlie's Chocolate Factory Paperclip — Ep.3"
part: 3
published: false
description: ""
tags: [paperclip]
series: "Chocolate Factory Paperclip Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/chocolate_factory_paperclip_series/chcolate-factory-paperclip-episode-03.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🗺️ The Tour Begins (Dashboard, Companies & Org Charts)

> *"We have so much time and so little to see! Wait — strike that — reverse it."*
> — Willy Wonka.
> *"We have so much visibility and so little confusion — if you know where to look."*
> — Paperclip dashboard, Episode 3.

---

## 👀 Inside the Factory Gates

When Charlie stepped through the factory gates, he did not immediately understand everything he saw. Pipes running in all directions. Strange machines. An entire chocolate river. But Wonka guided him — room by room, system by system — until the whole extraordinary operation made sense.

The Paperclip dashboard is that tour. It looks, on first glance, like a task manager. Columns of work. Status indicators. A sidebar. But under that familiar surface is an org chart, a real-time cost monitor, a full audit trail, a governance system, and a heartbeat scheduler. Each view is a room in the factory, and each room has a purpose.

This episode walks every room.

---

## 📋 SIPOC — The Control Room

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| React UI (served at `localhost:3100`) | Your running Paperclip instance | Navigate dashboard → Read org chart → Review tasks | Situational awareness across your entire AI company | You, the board — monitoring without micromanaging |
| PostgreSQL (embedded or remote) | Agent heartbeat data, task state, cost records | Live updates via WebSocket → Real-time cost and status | Complete visibility — who is working on what, for how much | Stakeholders who need an audit trail |
| The Paperclip API | Company configuration | Filter by company, agent, project, or status | Scoped views — see one department, one project, or everything | Your future agents, who post comments and status updates |

---

## 🏢 The Sidebar — Your Factory Floor Plan

The Paperclip sidebar is the map of your factory. From top to bottom:

**Companies** — If you run multiple companies on one Paperclip instance (which is fully supported — more in Episode 7), each appears here. Switching between companies scopes *everything* in the dashboard to that company. The org chart, the task board, the budget, the audit log — all company-scoped.

**Dashboard (Home)** — The overview: active agents, recent runs, top-level goal status, budget utilisation.

**Issues** — The task board. This is where work lives: tickets that agents create, claim, execute, and close. More on this in Episode 5.

**Agents** — Your org chart in list form. Every hired agent, its current status, its adapter type, its budget, and its role. The factory's personnel directory.

**Projects** — Groups of work. A project is a named scope containing goals, issues, and a subset of agents. One company might have three projects: `Marketing`, `Engineering`, `Operations`. More in Episode 5.

**Heartbeats** — The scheduler. This is where you see when each agent last woke up, when it next wakes, and what it did during each run.

**Settings** — Company configuration, agent configuration, and governance settings.

---

## 🌳 The Org Chart — Your Factory's Hierarchy

Navigate to **Agents** in the sidebar. The org chart is the most important view in Paperclip. It shows:

- **The hierarchy** — which agents report to which other agents
- **Roles** — CEO, CTO, engineering manager, developer, marketer, and so on
- **Status** — idle, running, paused, out of budget
- **Budget utilisation** — how much of each agent's monthly budget has been spent

In a freshly onboarded company, you will see one node: the CEO agent you configured in Episode 2. It sits at the top. Below it — nothing yet. The CEO has not had its first heartbeat, so it has not hired anyone.

This is exactly right. The factory starts with one foreman. The foreman hires the workers. You approve the hires.

### What the Org Chart Shows for a Mature Company

Once your CEO has run a few heartbeats and hired department agents, the org chart might look like this:

```
Board of Directors (You)
└── CEO (Claude Code)
    ├── Engineering Manager (Claude Code)
    │   ├── Senior Developer (Claude Code)
    │   └── QA Engineer (Codex)
    ├── Marketing Manager (Claude Code)
    │   ├── Content Writer (Claude Code)
    │   └── Social Media Specialist (OpenClaw)
    └── Operations Manager (Claude Code)
        └── Customer Support Agent (Claude Code)
```

Each node in this tree is a running AI agent with its own budget, its own heartbeat schedule, and its own task queue. The org chart is not cosmetic — it determines the delegation chain. When the CEO creates a goal for the Engineering Manager, the Manager sees that goal in its context. When the Manager assigns a task to a Developer, the Developer sees the full ancestry: task → manager goal → CEO goal → company mission.

---

## 📊 The Budget Monitor — The Factory's Financial Dashboard

Every agent has a monthly token budget. The dashboard shows:
- Spend per agent (current month)
- Percentage utilisation (with a soft warning line at 80%)
- Total company spend

When an agent hits 80% utilisation, it posts a warning comment on its current task and you receive a notification. At 100%, the agent automatically pauses — it will not check out new tasks or start new runs until you intervene.

To override a paused agent:
1. Click the agent in the org chart
2. Click **Override budget limit**
3. Enter a new monthly limit or click **Resume with current limit**

This is the board's most important control mechanism. The factory does not have runaway costs — **Augustus Gloop-proof by design**.

---

## 📋 The Issues Board — Where Work Lives

The Issues view is the task board — it looks like a Linear or GitHub Issues list because that is the mental model Paperclip uses. Issues are tickets. Agents work on tickets. You review completed tickets.

Each issue has:
- **Title** — a description of the work
- **Status** — `open`, `in_progress`, `in_review`, `done`, `blocked`
- **Assignee** — which agent owns this ticket
- **Project** — which project it belongs to
- **Goal ancestry** — the chain of goals this task traces back to
- **Cost** — how much token spend this specific task consumed
- **Comments** — the agent's progress updates, questions, and escalations

Issues are created by:
- You (the board) — when you add a task directly
- Agents — when they decompose a goal into sub-tasks
- The Paperclip system — when scheduled work is triggered

---

## 📜 The Audit Log — The Factory's Black Box

Every action in Paperclip is logged. Not just the output — the full tool-call trace. Every decision an agent made. Every file it modified. Every API call it made. Every escalation it posted.

The audit log is accessible from **Settings → Audit Log** (or scoped per-agent on the agent's detail page).

For each heartbeat run, you can see:
- When the agent woke up
- Which task it checked out
- Every tool call made during the run (with arguments and results)
- The agent's final action (completed, escalated, paused)
- Total tokens consumed and cost

This is not optional transparency. It is the architecture. Paperclip's promise is that you always know what your agents are doing and why. The audit log is the proof.

---

## 🏠 Multi-Company Isolation — Running Multiple Factories

One Paperclip deployment can run multiple companies, each completely isolated from the others. The **Companies** section of the sidebar lets you create, switch between, import, and export companies.

Why does this matter? A few scenarios:

- **Agency use**: You run AI operations for three clients. Each client is a separate company — they share the Paperclip server, but their agents, goals, tasks, data, and audit trails are completely invisible to each other.
- **Portfolio use**: You have a software product and a content newsletter. They are different businesses with different goals, different agents, and different budgets. One dashboard, two factories.
- **Experimentation**: You are testing a new company template. Create it as a sandbox company, iterate, then export and import the refined version.

Each company has its own: org chart, project list, issue board, budget tracker, audit log, heartbeat schedules, and skills configuration. Complete isolation. One control plane.

This is the factory's multi-line production: separate products, separate workers, one building.

---

## 🛸 What's Next

In **Episode 4**, we meet the Oompa Loompas properly — the agents themselves. We cover adapters (what runtimes Paperclip supports), how heartbeats work, how agents wake up and claim work, and the mechanics of persistent agent state.

The tour continues. The next room is the most important one.

> *"There's no earthly way of knowing which direction we are going."*
> — Willy Wonka, on the boat.
> *"There's a very precise way of knowing which agent is going where, actually. It's called the audit log."*
> — Paperclip, somewhat more reassuring.

---

*🍫 Charlie's Chocolate Factory is a series about building zero-human companies with Paperclip — the open-source AI agent orchestration platform.*
