# 🛗 Charlie's Chocolate Factory — Episode 7: The Great Glass Elevator (Clipmart & Company Templates)

> *"Up and out!"*
> — Willy Wonka, in the Great Glass Elevator.
> *"Import and run!"*
> — Paperclip, on Clipmart.

---

## 🛗 Beyond the Factory Gates

The Great Glass Elevator did not just go up and down. It went sideways. Diagonally. At any angle. It could go *anywhere* — including places that had not been anticipated when the elevator was built.

Clipmart is Paperclip's Great Glass Elevator.

It is the coming marketplace where you can download and import **entire pre-built companies** — full org structures, agent configurations, skill files, and project templates — and run them in your Paperclip instance immediately. No configuration from scratch. No designing your org chart. No writing skills from zero. Download a battle-tested team and start producing.

This episode covers the current state of portable companies (the import/export system already in Paperclip), what Clipmart will look like when it launches, the existing community template repositories, and why portable companies might be the most consequential feature on the Paperclip roadmap.

---

## 📋 SIPOC — The Factory in a Box

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Community contributors (Clipmart) | A Paperclip instance (already running) | Download template → Import → Configure API keys → Run | A fully configured AI company, ready to work | You, skipping the setup phase entirely |
| Your existing Paperclip configuration | An exported company package | Export company → Scrub secrets → Share / archive | A portable, shareable company template with no credentials | Other teams, clients, or your future self |
| The `paperclipai/companies` GitHub repository | Template YAML + agent configs + skills | Clone or download template → Import via UI | Pre-built org with CEO, managers, workers, and skills | Anyone who needs a specific type of AI company |
| Paperclip's import/export system | Company name, collision handling preferences | Import → Resolve conflicts → Activate heartbeats | An isolated company with complete data separation | Your dashboard — a new company, ready to go |

---

## 📦 The Export/Import System — What Exists Today

Clipmart is coming. The underlying system that will power it — the **company export/import** feature — is already in Paperclip today.

### Exporting a Company

Any company you have configured in Paperclip can be exported as a portable package. In the dashboard:

**Settings → Company → Export Company**

The export produces a file containing:
- The company's org chart structure (agent roles, hierarchy, reporting lines)
- All agent configurations (adapter type, model, settings, budget)
- All project definitions (names, goals, descriptions)
- All skill files and their contents
- Heartbeat schedules and routine configurations

**What the export does NOT include:**
- API keys and secrets (these are scrubbed automatically)
- Current task state and issue data (the open task board is not exported)
- Audit log history
- Spent budget data

The result is a clean template — the structure and knowledge of the company, stripped of its operational state and credentials. Like a blueprint of the factory, without the machinery currently running inside it.

### Importing a Company

To import a company from a template:

**Companies → Import Company**

Upload the exported file. Paperclip:
1. Creates a new, isolated company from the template
2. Presents you with any naming conflicts (agents, projects with the same names as existing ones)
3. Asks you to supply API keys for each adapter used
4. Creates all agents, projects, and skills as configured in the template
5. **Leaves heartbeat timers disabled** — you activate them manually after reviewing the configuration

The deliberate disable of heartbeats on import is a safety feature. A freshly imported company with twenty agents and multiple schedules should not start executing autonomously until you have verified everything is configured correctly. Review the org chart. Check the skill files. Confirm the budgets. Then enable heartbeats.

> 🚀 **Portability note:** The export/import system includes **secret scrubbing** (no credentials leave your instance) and **collision handling** (overlapping names are resolved without overwriting existing data). One deployment can run dozens of imported companies with complete data isolation.

---

## 🏪 Clipmart — The Coming Marketplace

Clipmart is Paperclip's planned marketplace for community-contributed company templates. Think of it as an app store, but the apps are entire AI companies.

**What Clipmart will offer:**
- **Browse** pre-built company templates by category (software development, content creation, customer support, e-commerce, research)
- **Preview** the org chart, agents, and skills before importing
- **One-click import** into your running Paperclip instance
- **Community ratings** and version history
- **Fork and customise** — import a template, modify it, export your version

**Examples of templates likely to appear:**

| Template name | What it does |
|---|---|
| **GStack** | Full software startup — CEO, CTO, engineers, QA, release manager (based on Gary Tan's configuration) |
| **Content Agency** | Writers, editors, social media specialists, SEO analysts |
| **Support Desk** | 24/7 customer support team with escalation protocols |
| **Research Lab** | Literature review agents, data analysts, report writers |
| **Game Studio** | Creative director, producer, technical director, asset creation agents |

The concept being explored for Clipmart is the **acqui-hire analogy**: instead of spending weeks configuring your AI company from scratch, you download a proven team, configure your credentials, and start running. The skills (recipes) come pre-written. The org chart is pre-designed. The heartbeat schedules are pre-configured.

You are not building a factory. You are buying one.

---

## 📚 Current Community Templates — What's Available Now

While Clipmart is in development, the community maintains templates in two places:

### The `paperclipai/companies` Repository

The official community template repository at `github.com/paperclipai/companies` contains growing catalog of templates including:

- **GStack** — A technology startup configuration based on Gary Tan's documented approach: CEO, CTO, QA engineer, release engineer, and staff engineer roles. Well-suited for software products.
- **Agency Agents** — Over 100 pre-built agent personas for various business functions.
- **Scientific Research** — Research-oriented company with specialised knowledge agents for literature review and data synthesis.

To use a community template:
```bash
# Clone the community templates repository
git clone https://github.com/paperclipai/companies.git

# Import via the Paperclip UI
# Companies → Import Company → Upload the template file
```

### The `paperclipper` CLI Tool

The `paperclipper` CLI is a companion tool for bootstrapping companies from templates:

```bash
# Install the paperclipper CLI
npm install -g paperclipper

# Bootstrap a company from a template
paperclipper bootstrap --template gstack

# Preview what will be created before importing
paperclipper bootstrap --template gstack --dry-run
```

The CLI handles the template download, credential prompting, and import in one guided flow — even faster than the UI workflow.

---

## 🔒 The Security of Portability

Exporting and importing companies raises an obvious question: what about credentials?

Paperclip's answer is strict:
- **API keys are never included in exports.** The scrubbing step is automatic and not bypassable.
- **Environment variable references** are preserved (e.g., `ANTHROPIC_API_KEY`) so the importing party knows what credentials to supply.
- **Imported companies are created in complete isolation** — they cannot access data from other companies on the same instance.
- **Heartbeats start disabled** — you cannot accidentally start running an imported company that you have not reviewed.

The factory blueprint does not include the master keys. You provide your own.

---

## 📤 Building and Sharing Your Own Templates

Once you have a working Paperclip company — whether built from scratch or refined from a community template — you can share it:

1. **Export the company** (Settings → Company → Export)
2. **Review the export** — check that no sensitive information has leaked (the scrubber handles API keys, but verify any domain-specific secrets in skill files)
3. **Submit to the community** — open a PR to `github.com/paperclipai/companies` with your template, a README explaining what it does, and a sample org chart diagram

The community templates ecosystem is genuinely early. The most useful templates are the ones built for real use cases by people who have run them in production. If you build something that works, share it.

---

## 🛸 What's Next

In **Episode 8** — the final episode — we put everything together. We run a complete zero-human company from mission statement to delivered output. The full flow: set a goal, watch the CEO decompose it, approve the strategy, monitor heartbeats, review completed work, and reflect on what it means to be the board of an AI-operated business.

The Great Glass Elevator is taking us up — and out.

> *"There's so much more room up here."*
> — Charlie Bucket, looking at the world from the elevator.
> *"There's so much more output now, with twenty agents running in parallel."*
> — You, monitoring the Paperclip dashboard.

---

*🍫 Charlie's Chocolate Factory is a series about building zero-human companies with Paperclip — the open-source AI agent orchestration platform.*
