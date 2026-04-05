---
title: "Charlie's Chocolate Factory Paperclip — Ep.2"
part: 2
published: false
description: ""
tags: [paperclip]
series: "Chocolate Factory Paperclip Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/chocolate_factory_paperclip_series/chcolate-factory-paperclip-episode-02.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🏭 Finding the Factory (Installation & Onboarding)

> *"The factory is yours, Charlie. The whole factory — and everything in it."*
> — Willy Wonka.
> *"The instance is yours. The whole deployment — and everything in it."*
> — Paperclip, after `npx paperclipai onboard`.

---

## 🗺️ The Address on the Envelope

Charlie found the factory by following his nose — that extraordinary smell of chocolate that drifted across the whole town. You find Paperclip by following a `curl` command. Less romantic. Equally life-changing.

This episode is the hands-on tour: install Paperclip, run the onboarding wizard, set up your first company, and reach the live dashboard with a running CEO agent. By the end, your factory will have its gates open and its first worker standing at the machine.

---

## 📋 SIPOC — Opening the Gates

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Node.js (v18+) + npm | A machine with Node.js installed | `npx paperclipai onboard` → guided wizard | Paperclip server at `http://localhost:3100` | You, opening the dashboard for the first time |
| Embedded PostgreSQL (PGlite) | Your API key(s) for AI providers | Create company → Create CEO agent → Set mission | A running company with one agent ready to work | Every episode after this one |
| pnpm (for source builds) | A terminal and 15 minutes | `paperclipai start` or `pnpm dev` | Embedded Postgres auto-provisioned, no separate DB needed | Your future self, not configuring infrastructure |
| Docker (optional, for production) | A browser | Navigate to `http://localhost:3100` | The Paperclip dashboard — your factory's control room | Your company's first heartbeat |

---

## ✅ Prerequisites

Before opening the factory gates, you need:

- **Node.js v18 or later** — check with `node --version`
- **npm** (comes with Node.js) — check with `npm --version`
- **An AI provider API key** — Anthropic (Claude Code), OpenAI (Codex), or Google (Gemini CLI) are all supported. Anthropic's Claude is the recommended starting point; Claude Code is Paperclip's native execution engine.
- **Git** (for source builds or contributing)

The local development setup uses **PGlite** — an embedded PostgreSQL that runs inside the Node.js process. You do not need to install or configure a separate database. The factory builds its own basement.

---

## 🚀 Option A — Quick Start (Recommended)

The fastest path to a running factory:

```bash
# Install the Paperclip CLI globally
npm install -g paperclipai

# Run the onboarding wizard
paperclipai onboard
```

The onboarding wizard walks you through four steps:

**Step 1 — Database setup:** PGlite is provisioned automatically. In production (later), you can point this at your own PostgreSQL instance.

**Step 2 — Authentication:** Set your admin credentials. This becomes your board-level login.

**Step 3 — Company creation:** Give your company a name and a mission statement. The mission is important — agents at every level of the org chart trace their work back to it. More on this in Episode 5.

**Step 4 — First agent adapter:** The wizard asks which AI provider powers your first agent. Select the one matching your API key. Paperclip installs the appropriate adapter and injects a `SKILL.md` into the agent's configuration directory (`~/.claude/skills/` for Claude Code, for example).

When the wizard completes:

```bash
# Start the Paperclip server
paperclipai start
```

Navigate to `http://localhost:3100`. Your factory is open.

> 🔍 **What `paperclipai onboard` actually does behind the scenes:** It creates a `.paperclip/` directory in your home folder, writes your configuration there, bootstraps the database schema (applying all migrations), registers your company, and pre-loads the runtime skills your agents need to understand Paperclip's heartbeat protocol.

---

## 🏗️ Option B — Source Build (For Contributors)

If you want to contribute to Paperclip, or prefer to run from source:

```bash
# Clone the repository
git clone https://github.com/paperclipai/paperclip.git
cd paperclip

# Install dependencies (pnpm is required)
npm install -g pnpm
pnpm install

# Run the full development stack (API + UI with hot reload)
pnpm dev
```

The `pnpm dev` command starts:
- The **Express API server** on port `3100`
- The **React UI** (served from the API server in dev mode)
- **File watching** on both server and UI

For server-only development:

```bash
pnpm dev:server
```

The embedded PGlite database is created automatically when the server first starts. If you have a remote PostgreSQL instance, set the `DATABASE_URL` environment variable before starting.

> ⚠️ **Troubleshooting:** If anything goes wrong during setup, run:
> ```bash
> pnpm paperclipai doctor --repair
> ```
> This diagnoses the most common issues — permission errors, stale instances, database migration problems — and repairs them automatically. Think of it as the factory's maintenance engineer.

---

## 🐳 Option C — Docker (For Production Deployments)

Paperclip ships a `Dockerfile` for production use:

```bash
# Build the image
docker build -t paperclip .

# Run with an external PostgreSQL database
docker run -p 3100:3100 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/paperclip \
  -e PAPERCLIP_SECRET=your-secret-key \
  paperclip
```

A `docker-compose.yml` in the `docker/` directory provides a complete local stack with PostgreSQL included.

For solo operators who want to access Paperclip remotely, the official docs note that Tailscale works perfectly for this — install it on your server, join your tailnet, and access `http://your-server:3100` from anywhere without exposing the port publicly. A hint at the wider infrastructure picture this tool fits into.

---

## 🖥️ The Onboarding Wizard — What Each Step Means

When you open `http://localhost:3100` for the first time, the **Onboarding Wizard** appears — a four-step guided setup. Here is what each step is actually doing:

### Step 1 — Create Your Company

You provide:
- **Company name** — identifies this company in the dashboard (one Paperclip instance can run many companies)
- **Mission statement** — a plain-English description of what this company exists to do

The mission statement is not cosmetic. It is embedded in every agent's context as goal ancestry — when a worker agent is assigned a task, it can see the full chain from its task → department goal → company mission. Agents always know the *why*, not just the *what*.

This is the equivalent of writing the sign on the factory gate. Every Oompa Loompa can read it.

### Step 2 — Hire Your CEO Agent

The CEO is the top of your org chart. It:
- Receives the company's high-level goals
- Decomposes them into department-level objectives
- Recommends which additional agents to hire
- Reports upward to you (the board)

The wizard asks you to choose an **adapter** — the runtime that powers this agent:

| Adapter | Runtime | Best for |
|---|---|---|
| `claude_code` | Claude Code (Anthropic) | General-purpose coding + reasoning |
| `codex` | OpenAI Codex | Coding tasks (managed environment) |
| `cursor` | Cursor IDE | IDE-native development workflows |
| `openclaw` | OpenClaw | Continuous autonomous operation |
| `gemini_cli` | Google Gemini CLI | Gemini-powered tasks |
| `http_webhook` | Any HTTP endpoint | Custom agents and scripts |

Start with `claude_code` if you have an Anthropic API key. You can add more adapters (and more agents with different adapters) at any time.

### Step 3 — Set Your First Goal

Enter a high-level business goal for the CEO. Example goals from the Paperclip documentation:

- *"Build and maintain a personal landing page that showcases my projects"*
- *"Respond to all incoming customer support emails within 2 hours"*
- *"Publish three blog posts per week on topics relevant to our industry"*
- *"Review all pull requests within one business day"*

The CEO will decompose this goal into tasks on its first heartbeat.

### Step 4 — Set a Budget

Assign a monthly token budget to the CEO agent. Paperclip enforces this atomically — when the agent reaches 80% utilisation, you receive a soft warning. At 100%, the agent auto-pauses. No runaway spend. No Augustus Gloop situations.

A reasonable starting budget for a CEO agent on a small project: `$10–$20/month`. You can adjust this at any time from the dashboard. As the board, you can always override the limit and resume the agent immediately.

---

## ✅ Your Factory Is Open

When the wizard completes, you land on the **Paperclip dashboard** — the factory control room.

You should see:
- Your company name and mission statement
- One agent (your CEO) in the org chart
- The agent's status: `idle` (waiting for its first heartbeat)
- A budget tracker showing $0.00 / your configured limit

In **Episode 3**, we walk through everything this dashboard shows you, how to navigate it, and how to read the org chart, task board, audit log, and cost monitor.

The factory is open. The first worker is at the machine. The first heartbeat is coming.

> *"So much time and so little to do! Wait a minute. Strike that. Reverse it."*
> — Willy Wonka.
> *"So many agents and so little toil! For you, anyway. The agents handle the toil."*
> — Paperclip, accurately.

---

*🍫 Charlie's Chocolate Factory is a series about building zero-human companies with Paperclip — the open-source AI agent orchestration platform.*
