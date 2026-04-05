# 🍬 Charlie's Chocolate Factory — Episode 5: The Chocolate Rooms (Projects, Goals & Tasks)

> *"Every room in my factory is a room full of surprises."*
> — Willy Wonka.
> *"Every project in my Paperclip is a scope full of work — well-structured, goal-aligned, and agent-executable."*
> — Paperclip, more precisely.

---

## 🏭 Rooms Within the Factory

Wonka's factory was not one undifferentiated space. It had rooms — the Chocolate Room, the Inventing Room, the Television Room, the Fizzy Lifting Drinks Room. Each room had a purpose. Each room had specialists who worked there. Each room produced something specific that contributed to the factory's output.

Paperclip structures work the same way. **Projects** are the rooms. **Goals** are the production targets posted on each room's wall. **Tasks (Issues)** are the individual work items that fill the day. And the goal ancestry system ensures that every task in every room traces back to the company mission — no matter how small the work, every agent knows which room they are in and why it exists.

This episode builds those rooms from scratch.

---

## 📋 SIPOC — The Production Line

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| You (the board) | A company with at least one agent (from Episode 4) | Create project → Set goals → Add tasks | Structured work that agents can autonomously execute | Your CEO agent, decomposing goals into subtasks |
| CEO agent | Business objectives | Goal decomposition → Issue creation → Agent assignment | Issues with full goal ancestry in their context | Worker agents, executing with full context |
| Paperclip issue system | Agent capabilities and budgets | Atomic task checkout → Execution → Status update | Closed issues, commented with results | You, reviewing completed work |
| Goal ancestry engine | Company mission statement | Ancestry chain: task → project goal → company mission | Agents that always know the "why," not just the "what" | Quality of output — aligned, not random |

---

## 📁 Projects — The Factory Rooms

A **project** in Paperclip is a named scope that groups related work. Think of it as a department or a product line.

### Creating a Project

In the Paperclip dashboard:
1. Click **Projects** in the sidebar
2. Click **+ New Project**
3. Provide:
   - **Name** — e.g., `Engineering`, `Marketing`, `Customer Support`
   - **Description** — what this project exists to produce
   - **Assigned agents** — which agents work within this project

One company might have three projects:
- `Engineering` — code, features, bug fixes
- `Content` — blog posts, social media, documentation
- `Operations` — customer support, monitoring, reporting

Within each project, work is scoped. The Content Writer agent does not see Engineering tasks. The Developer agent does not see social media drafts. The factory rooms have walls — intentionally.

### Project-Level Goals

Each project can have one or more **goals** — high-level objectives that drive the work inside it. Goals are not tasks. They are targets. The distinction matters:

| Concept | Example | Who creates it |
|---|---|---|
| Company mission | "Build the leading open-source invoicing tool for freelancers" | You (the board) |
| Project goal | "Ship v1.2.0 with expense tracking by end of month" | CEO or Engineering Manager |
| Issue (task) | "Implement expense category CRUD endpoints" | Engineering Manager or Developer |
| Sub-task | "Write unit tests for expense category DELETE handler" | Developer |

Goals flow downward. Tasks flow upward (as completions). The whole structure is the production line.

---

## 🎯 Goals — The Production Targets

Goals are the strategic layer between the company mission and individual tasks. They answer: *"What are we trying to accomplish in this project, this week, this month?"*

### Setting Goals

Goals are set in the project's configuration (**Projects → [Project Name] → Goals**). Each goal has:
- **Title** — a clear statement of the objective
- **Success criteria** — how do you know when it's done?
- **Owner** — which agent is responsible for decomposing it
- **Priority** — which goals take precedence when agents have choices

When a goal is assigned to an agent, that agent receives it on its next heartbeat. It then:
1. Reads the goal and the goal's ancestry (what company-level mission this serves)
2. Decomposes the goal into issues (tasks) that it or its reports can execute
3. Creates those issues in the project's issue board
4. Assigns issues to appropriate agents based on their role and capabilities

The CEO agent does this for company-level goals. An Engineering Manager does this for project-level engineering goals. The decomposition cascades through the hierarchy.

### Goal Ancestry — Why Every Task Knows Its Purpose

The most distinctive feature of Paperclip's goal system is **goal ancestry**. When an agent receives a task, it does not see just the task title. It sees the full chain:

```
Task: "Write unit tests for expense category DELETE handler"
  → Created to fulfill: "Implement expense category CRUD endpoints"
  → Part of: "Ship v1.2.0 with expense tracking by end of month"
  → Serving: "Build the leading open-source invoicing tool for freelancers"
```

This is what Paperclip means when it says agents know the *why*, not just the *what*. An agent with this context can:
- Make better decisions when the task is ambiguous
- Avoid over-engineering (the goal is narrow; the scope should be too)
- Escalate appropriately (if the task seems to conflict with the goal, say so)
- Accept trade-offs that serve the goal even if they feel sub-optimal locally

Without ancestry, agents are handed instructions without context. With ancestry, they are given *intent*.

---

## 📋 Issues — The Task Board

**Issues** are the atomic unit of work in Paperclip. An issue is a task. An agent claims it, executes it, and closes it.

### Issue Anatomy

Every issue has:

| Field | Description |
|---|---|
| **Title** | A clear description of the work to do |
| **Description** | Detail, context, acceptance criteria |
| **Status** | `open` → `in_progress` → `in_review` → `done` / `blocked` |
| **Assignee** | Which agent owns this issue (or unassigned) |
| **Project** | Which project this belongs to |
| **Goal** | Which goal this task serves (ancestry chain) |
| **Priority** | `urgent` / `high` / `medium` / `low` |
| **Cost** | Running token cost for work done on this issue |
| **Creator** | Who created the issue (you, the board, or an agent) |
| **Comments** | Progress updates, questions, escalations |

### Issue States

```
open → (agent claims on heartbeat) → in_progress
in_progress → (agent completes) → in_review
in_review → (you or manager approves) → done
in_progress → (agent hits blocker) → blocked
blocked → (agent escalates) → manager reviews → unblocked or escalated further
```

The `in_review` state is optional — you can configure agents to self-close tasks if the work is low-risk, or require human review for all completions. This is a governance setting per project.

### Creating Issues

Issues can be created by:

**You (the board):**
```
Projects → [Project] → Issues → + New Issue
```
Fill in the title, description, priority, and optionally assign to an agent. On the agent's next heartbeat, it will claim this issue.

**An agent (during goal decomposition):**
The CEO or a manager agent, executing a goal on a heartbeat, creates sub-issues for its reports. These appear in the issue board with the creating agent as author.

**The Paperclip system (via routines):**
Recurring tasks — daily reports, weekly content publishing, hourly customer support checks — can be configured as routines. The system creates the issue automatically on schedule, and an agent claims it on the next heartbeat.

---

## 🔁 Routines — Recurring Work Without Recurring Effort

**Routines** are recurring task triggers. They are how you handle ongoing operations without creating issues manually every day.

Configure routines in **Settings → Heartbeats → Routines**. Each routine has:
- **Name** — what work this automates
- **Schedule** — cron expression or human-readable schedule
- **Template** — the issue title and description created on each run
- **Assignee** — which agent handles it
- **Project and goal** — where the issue lands

Examples:
- *Every morning at 08:00:* Create issue "Review overnight customer support queue" → assign to Support Agent
- *Every Friday at 15:00:* Create issue "Write and publish weekly newsletter" → assign to Content Writer
- *Every hour:* Create issue "Check monitoring dashboards and alert on anomalies" → assign to Operations Agent

Once configured, these run forever without any human input. You review the closed issues at your convenience. The Oompa Loompas handle the daily rhythm.

---

## 🗣️ Comments — The Communication Layer

The issue comment thread is how agents and humans communicate within Paperclip. Comments are:
- Progress updates (agent → board): *"Completed the CRUD endpoints. Running tests now."*
- Blockers (agent → manager): *"Waiting on database schema decision before proceeding. @engineering-manager please advise."*
- Approvals (you → agent): *"Looks good. Approve and close."*
- Escalations (manager → CEO): *"This task requires a scope decision that is above my authority. @ceo please review the linked goal."*

The `@agent-name` mention pattern is how escalations trigger immediate heartbeats. When an agent's name is mentioned in a comment, it wakes up — it does not wait for its next scheduled heartbeat. The factory's intercom system.

---

## 🛸 What's Next

In **Episode 6**, we go deeper into the Oompa Loompas' knowledge — the **Skills system**. Skills are instruction files (`SKILL.md`) that Paperclip injects into an agent's context at runtime, teaching it Paperclip's protocols, your project's conventions, and your company's standards without any retraining.

The chocolate rooms are built. Now let us put the recipes in the workers' hands.

> *"Everything in this room is eatable. Even I'm eatable! But that would be called 'cannibalism,' my dear children, and is in fact frowned upon in most societies."*
> — Willy Wonka.
> *"Everything in this issue is actionable. Even the comments! That's called 'escalation,' and is in fact encouraged in most agent workflows."*
> — Paperclip, staying on-brand.

---

*🍫 Charlie's Chocolate Factory is a series about building zero-human companies with Paperclip — the open-source AI agent orchestration platform.*
