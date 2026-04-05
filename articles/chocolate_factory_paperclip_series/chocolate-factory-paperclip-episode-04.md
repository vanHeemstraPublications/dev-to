# 🫀 Charlie's Chocolate Factory — Episode 4: Meet the Oompa Loompas (Agents, Adapters & Heartbeats)

> *"The Oompa Loompas work day and night in the factory."*
> — Willy Wonka.
> *"The agents run on scheduled heartbeats and event triggers, around the clock."*
> — Paperclip, same idea, different vocabulary.

---

## 🟠 Who Are the Oompa Loompas?

In Wonka's factory, the Oompa Loompas were the workforce. Small. Numerous. Each one expert in their particular part of the production line. They worked without complaint. They understood the factory's purpose. And crucially — they worked while Wonka slept.

In Paperclip, the **agents** are your Oompa Loompas. Each one is an AI process — Claude Code, Codex, Cursor, OpenClaw, a Python script, an HTTP webhook — anything that can receive a **heartbeat signal** and respond. As the Paperclip tagline says: *"If it can receive a heartbeat, it's hired."*

This episode explains how agents work, what makes one different from another, how they wake up, how they claim work, and what happens when they finish.

---

## 📋 SIPOC — The Factory Workforce

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| AI providers (Anthropic, OpenAI, Google) | Adapter configuration per agent | Heartbeat fires → Agent wakes → Checks task queue → Executes | Completed tasks, cost records, audit trail entries | The org chart above (managers reviewing work) |
| Paperclip adapter system | Agent role definition and budget | Task checkout (atomic) → Execution → Status update | Updated issue status, posted comments, escalations | You, the board — seeing progress without babysitting |
| Agent's runtime environment | Skills injected at startup | Persistent state across heartbeats — same context, no restart | Continuous progress — agents pick up where they left off | Company mission — every task traces back to it |
| The heartbeat scheduler | @-mention notifications, task assignments | Event-driven wakes + scheduled wakes | No idle waiting — agents work when there is work to do | The next agent in the delegation chain |

---

## 🔌 Adapters — The Factory's Machine Interfaces

An **adapter** is Paperclip's interface to a specific AI runtime. Different runtimes have different capabilities, different API surfaces, and different operational models. Paperclip wraps them all in a standard adapter protocol — a heartbeat in, a status out.

### Supported Adapters

| Adapter | Runtime | How it runs | Best for |
|---|---|---|---|
| `claude_code` | Claude Code (Anthropic) | Local subprocess | General-purpose: code, writing, research, reasoning |
| `codex` | OpenAI Codex | Managed cloud environment | Coding tasks in a sandboxed environment |
| `cursor` | Cursor IDE | IDE-native | Development workflows that benefit from IDE context |
| `openclaw` | OpenClaw | Continuous local process | Agents that need to run non-stop, not just on heartbeats |
| `gemini_cli` | Google Gemini CLI | Local subprocess | Gemini-powered tasks, API-key detected automatically |
| `http_webhook` | Any HTTP endpoint | Remote HTTP call | Custom agents, Python scripts, shell commands |
| `openclaw_gateway` | OpenClaw (gateway mode) | Gateway-only | Delegating specific tasks to a persistent OpenClaw instance |
| `pi` | Pi (local RPC) | Local RPC mode | Cost tracking for local model runs |

You can mix adapters freely within one company. Your CEO might use `claude_code`. Your social media agent might use `openclaw` for continuous posting. Your data analyst might be a Python script behind an `http_webhook`. The org chart does not care — every node in the tree is just an agent with a heartbeat.

### Configuring an Adapter

When you create or edit an agent in the dashboard:
1. **Adapter type** — which runtime
2. **Adapter settings** — API keys, model selection, sandbox mode, max turns (default: 300)
3. **Workspace** — where the agent's working directory lives
4. **Skills** — which skill files to inject at runtime (more in Episode 6)

---

## 💓 Heartbeats — The Oompa Loompas' Work Schedule

The heartbeat is the fundamental unit of agent activity in Paperclip. By default, agents do not run continuously. They wake up on a schedule, check what work is available, do as much as they can, and go back to sleep.

This is intentional. Continuous operation costs money and is not always necessary. A heartbeat every 15 minutes is enough for most ongoing tasks. A heartbeat every hour is enough for daily operations. You control the schedule per agent.

### The Heartbeat Lifecycle

When a heartbeat fires for an agent:

```
1. Agent wakes
2. Agent scans its task queue for open, unassigned issues
3. Agent checks out one task (atomic — no other agent can claim it simultaneously)
4. Agent loads its skill files (SKILL.md) into context
5. Agent executes the task — writing, coding, researching, delegating
6. Agent posts a comment on the issue with its progress or result
7. Agent marks the issue: done / in_review / blocked / escalated
8. Agent reports cost (tokens used, USD estimate)
9. Agent sleeps until next heartbeat
```

Steps 3 and 8 are atomically enforced by the database — no double-work, no uncounted cost. The factory floor does not have collisions.

### Event-Driven Heartbeats

In addition to scheduled heartbeats, agents wake immediately for:
- **Task assignment** — you or another agent assigns them a specific issue
- **@-mention** — any comment that includes `@agent-name` wakes that agent within seconds
- **Escalation received** — when a worker agent escalates a blocker upward, the manager wakes

This means agents are not purely passive. An agent blocked on a problem can escalate to its manager. The manager wakes, reviews, and either resolves the blocker or escalates further. The chain goes as high as needed — up to you, the board, if necessary.

---

## 🔄 Persistent Agent State — The Factory Never Forgets

One of Paperclip's most important technical properties: **agents resume where they left off**.

Most agent systems start fresh on every run. The agent reads the task description, starts from zero, and produces a result. If the task is complex and requires multiple sessions, the agent loses its intermediate reasoning and has to reconstruct it from scratch.

Paperclip maintains task context across heartbeats. When an agent wakes up on its next heartbeat and checks out the same ongoing task, it loads:
- The task description and goal ancestry
- All previous comments on the issue (including its own)
- The agent's notes and intermediate outputs
- The skill files relevant to this project

The agent does not restart. It continues. A complex coding task that spans three heartbeat cycles is processed as a single coherent flow, not three separate attempts.

This is the Oompa Loompa who starts building the machine Monday morning, comes back Tuesday morning, and continues exactly where they left off — without anyone having to explain what they were doing.

---

## 💰 Budget Enforcement — The Factory's Financial Controls

Every agent has a **monthly token budget**. This is not a suggestion. It is a hard limit, enforced atomically at task checkout.

Here is what happens at each utilisation threshold:

| Utilisation | What happens |
|---|---|
| 0–79% | Normal operation |
| 80% | Soft warning in dashboard + notification to board |
| 100% | Agent auto-pauses — no new task checkouts |
| Board override | You can raise the limit and resume immediately |

The budget is calculated in USD based on the API provider's pricing for tokens consumed. Paperclip tracks this per-run and accumulates it per-agent per-month. The dashboard shows you:
- Current spend per agent
- Projected monthly spend (based on current run rate)
- Total company spend
- Which tasks were most expensive

This is the factory's accounting department, built into the floor.

---

## 🏛️ Board Approval — The Governance Gate

By default, when a CEO agent recommends hiring a new agent (creating a new node in the org chart), the system requires **board approval** before the new agent is activated.

The approval flow:
1. CEO posts a hiring recommendation on the relevant issue: *"I recommend creating an Engineering Manager agent to coordinate development tasks. Suggested adapter: `claude_code`. Suggested budget: $15/month."*
2. You (the board) receive a notification.
3. You review the recommendation in the dashboard.
4. You approve (or reject) the hire.
5. The new agent is created and begins receiving heartbeats.

This gate is the safety mechanism that prevents your CEO from spawning an army of agents while you sleep. The factory grows by your consent.

You can adjust the governance settings (Settings → Governance) to:
- Require board approval for all agent creations (default)
- Allow the CEO to hire directly (for trusted deployments)
- Require approval for budget increases above a threshold
- Require approval for specific types of actions (e.g., external API calls)

---

## ⚠️ The Four Cautionary Tales — What Happens Without Governance

Roald Dahl knew something important: the factory is safe because Wonka runs it with care. The children who ignored the rules came to grief. Four patterns to avoid in your Paperclip deployment, named in the spirit of the original:

**Augustus Gloop (Budget Gobbler):** An agent with no budget limit runs indefinitely, consuming tokens at scale. Fix: always set a monthly budget. Never leave `unlimited` in production.

**Violet Beauregarde (Scope Creep):** An agent that expands its goal beyond its mandate — a marketing agent that starts making product decisions. Fix: write specific, scoped goal statements. The more precise the goal, the less room for drift.

**Veruca Salt (Governance Skip):** Granting CEO agents the ability to hire freely, without board approval, then being surprised when you have fifteen agents running costs you did not expect. Fix: keep the default governance gate. Approve hires consciously.

**Mike Teavee (Full Autonomy Without Audit):** Running agents with audit logging disabled because it felt like overhead. Then something goes wrong and there is no record of what happened. Fix: the audit log is not optional. It is the factory's black box.

All four are recoverable. Paperclip's governance and rollback features exist precisely because these things happen. But they are less painful to avoid than to undo.

---

## 🛸 What's Next

In **Episode 5**, we build the chocolate rooms themselves — projects, goals, and tasks. We look at how work is structured inside Paperclip, how goal ancestry flows through the org chart, and how to create a project that agents can meaningfully execute.

The Oompa Loompas are briefed. Now let us give them something to make.

> *"The waterfall is most important. It churns and churns, and mixes and mixes."*
> — Willy Wonka.
> *"The heartbeat scheduler is most important. It fires and fires, and wakes and wakes."*
> — Paperclip, mixing the metaphor but keeping the point.

---

*🍫 Charlie's Chocolate Factory is a series about building zero-human companies with Paperclip — the open-source AI agent orchestration platform.*
