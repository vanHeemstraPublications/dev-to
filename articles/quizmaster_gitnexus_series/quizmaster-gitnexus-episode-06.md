---
title: "Quizmaster GitNexus! 🎙️ Ep.6"
part: 6
published: false
description: "Episode 6: The broadcast studio — the Web UI, Bridge mode, the PolyForm Noncommercial licence, and the complete Quizmaster workflow from cold repo to graph-aware AI agent. The show is on the air."
tags: [ai, productivity, codenewbie, tooling]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/quizmaster-gitnexus-episode-06.png"
series: “"uizmaster GitNexus Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 6: Going Live

*“And we’re live in 3… 2… 1…”*

-----

## The Broadcast Studio 📺

Five episodes of preparation. The Quizmaster has read every book (indexing), answered every category of question (tools), revealed the advanced rounds (resources, prompts, skills), and taught your AI agents how to use the full system.

Now the show goes out to a wider audience.

This final episode covers two things: the **Web UI** — the broadcast studio where anyone can watch without a backstage pass — and the full picture: how all the pieces fit together into a complete Quizmaster workflow, from cold repository to graph-aware AI coding session.

Plus: the licence. Know what you have before you ship to production.

-----

## 🗂️ SIPOC — Going Live

|**Suppliers**                 |**Inputs**                                          |**Process**                                                 |**Outputs**                                                                |**Consumers**                                                                               |
|------------------------------|----------------------------------------------------|------------------------------------------------------------|---------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
|`gitnexus.vercel.app`         |A GitHub repo URL or a ZIP file                     |Browser-native indexing: Tree-sitter WASM + LadybugDB WASM  |Interactive knowledge graph + AI chat. No install. No upload to any server.|Any developer — exploring an unfamiliar repo, demoing to a colleague, quick one-off analysis|
|`gitnexus serve` (Bridge mode)|All CLI-indexed repos in `~/.gitnexus/registry.json`|Local HTTP server auto-detected by the Web UI               |Web UI shows all CLI repos, with full AI chat, without re-uploading        |Web UI users who want to explore their persistent CLI-indexed repos                         |
|PolyForm Noncommercial 1.0.0  |Your use case                                       |Licence check: is this personal, open-source, or commercial?|Clarity on whether you need a separate commercial licence                  |You, before deploying to production for a paying client                                     |
|The complete system           |A repository, an editor, an API key                 |`analyze` + `setup` + MCP + skills + hooks                  |A fully graph-aware AI coding session                                      |Every developer tired of their AI agent shipping broken dependencies                        |

-----

## The Web UI — The Broadcast Studio 🎬

The Web UI lives at `gitnexus.vercel.app`. No account. No install. No upload to any server. Drag in a GitHub repo URL or a ZIP file, and within seconds you have:

- An **interactive knowledge graph** visualised with Sigma.js (WebGL-accelerated) showing every symbol, edge, cluster, and process
- An **AI chat interface** with Graph RAG built in — ask questions about the codebase and get answers backed by the knowledge graph, not just the raw text
- The **complete indexing pipeline** — the same six phases from Episode 2 — running entirely in WebAssembly in your browser

The Web UI is the broadcast studio. The show runs without a production van. Anyone in the audience can tune in without a backstage credential.

### Limits of the Web UI

Browser memory places a practical ceiling. The Web UI handles approximately 5,000 files before hitting memory pressure. For larger repos, you need CLI mode or Bridge mode.

The AI chat is limited by your browser session — nothing persists when you close the tab. Each session starts fresh.

### When to use the Web UI

- **Quick exploration**: you just found an interesting open-source repo and want to understand its structure without cloning it
- **Demos**: showing a colleague what GitNexus does, with zero setup on their machine
- **One-off analysis**: investigating a dependency’s internals before deciding whether to adopt it
- **Interview prep**: understanding a codebase you will be asked questions about

-----

## Bridge Mode — The Production Van 🚐

The broadcast studio and the backstage preparation are separate by default. The Web UI and the CLI each run their own indexing pipeline. If you have indexed a large repo with the CLI (with all its persistent LadybugDB storage and full knowledge graph), the Web UI does not automatically see it — you would have to re-upload.

Bridge mode connects them.

```bash
# Start the local bridge server
npx gitnexus serve
```

This starts a local HTTP server (default: `http://localhost:3000`). The Web UI at `gitnexus.vercel.app` auto-detects it. All repos in your CLI registry (`~/.gitnexus/registry.json`) become available in the Web UI — no re-upload, no re-indexing.

**What Bridge mode gives you:**

- Web UI access to all your CLI-indexed repos (including repos larger than 5,000 files)
- Full AI chat backed by your persistent, up-to-date CLI graph
- The visual graph explorer for repos you normally access only via MCP tools
- Share your local server with teammates on the same network (for collaborative exploration)

**Bridge mode architecture:**

```
gitnexus.vercel.app (Web UI)
  ↓ detects localhost:3000
  ↓ reads registry: ~/.gitnexus/registry.json
  ↓ queries: LadybugDB in .gitnexus/lbug/ for each repo
  ↓ serves: full knowledge graph via local API
```

The production van connects the studio to the backstage. All the Quizmaster’s preparation work is accessible from both the professional setting (Claude Code, Cursor, MCP tools) and the broadcast studio (the visual Web UI with AI chat).

-----

## The Licence: What the Quizmaster Charges 💳

GitNexus is open source — the code is public, the repository is on GitHub, contributions are welcome. But it is not *permissively* open source. It uses the **PolyForm Noncommercial 1.0.0** licence.

What this means in plain terms:

|Use case                                                |Licence required                                           |
|--------------------------------------------------------|-----------------------------------------------------------|
|Personal development (your own projects)                |Free, PolyForm Noncommercial covers it                     |
|Open-source contributions (contributing to OSS projects)|Free, PolyForm Noncommercial covers it                     |
|Learning, research, education                           |Free, PolyForm Noncommercial covers it                     |
|A company using it internally on their own codebase     |**Check with the project** — may require commercial licence|
|A consultancy using it on client codebases              |**Commercial licence required**                            |
|A SaaS product that includes GitNexus as a feature      |**Commercial licence required**                            |
|Enterprise deployment (self-hosted, production)         |**Commercial licence — contact the project**               |

The PolyForm Noncommercial text is unambiguous: any use that generates revenue, directly or indirectly, falls outside the noncommercial licence.

**What this means for you:**

- **Solo developer, personal projects**: use freely
- **Evaluating for your team**: the evaluation period is covered
- **Regular daily development at a company**: check whether your company’s use case requires a commercial licence
- **Client work or SaaS**: reach out through the GitHub repo or Discord for commercial licensing options

The Quizmaster charges for broadcast rights. The audience watches for free. The production company pays.

-----

## The Complete Workflow: Cold Repo to Graph-Aware Session 🗺️

Here is the full journey — every step, from nothing to a complete Quizmaster setup:

### Step 1 — Install the CLI (once)

```bash
npm install -g gitnexus
```

### Step 2 — Index your repo (per repo)

```bash
cd ~/code/my-project
npx gitnexus analyze
# Optionally: npx gitnexus analyze --skills
# (generates per-community skill files)
```

This runs all six phases, installs skills, registers Claude Code hooks, writes `AGENTS.md` and `CLAUDE.md`, and adds the repo to the global registry.

### Step 3 — Configure your editor (once per machine)

```bash
npx gitnexus setup
# Auto-detects Claude Code, Cursor, Windsurf, OpenCode
# Writes MCP config for each detected editor
```

Or manually for Claude Code:

```bash
claude mcp add gitnexus -- npx -y gitnexus@latest mcp
```

### Step 4 — Verify

In Claude Code (or your editor of choice), ask the AI to call `list_repos` via the GitNexus MCP. You should see your indexed repo listed, with its path, git hash, and freshness status.

### Step 5 — The session pattern

Every coding session with a GitNexus-aware agent should follow this pattern:

```
1. Agent reads gitnexus://repo/{name}/context
   → How large? How many symbols? Index fresh?

2. Agent reads gitnexus://repo/{name}/clusters
   → What are the major communities?

3. Agent reads gitnexus://repo/{name}/processes  
   → What are the main execution flows?

4. Now: specific task begins

5. Before any edit: impact() on affected symbols
   → What is the blast radius?

6. After editing: detect_changes()
   → Did I touch what I intended? Anything unexpected?

7. Before committing: detect_impact prompt
   → Full pre-commit report.
```

### Step 6 — Keep the graph current

GitNexus’s PostToolUse hooks in Claude Code trigger automatic re-indexing after every `git commit`. For other editors, re-run `npx gitnexus analyze` when the graph goes stale (the `list_repos` freshness indicator will tell you).

For CI pipelines, add `npx gitnexus analyze` as a step that runs after merge to main. The graph in `~/.gitnexus/registry.json` and `.gitnexus/` can be cached between runs (it is just files — treat it like a build cache).

-----

## The Optional Visual Route: Web UI First 👁️

Not every developer wants to start with the CLI. Here is an alternative first step:

1. Go to `gitnexus.vercel.app`
1. Drop in a GitHub repo URL or ZIP
1. Explore the visual graph — click clusters, follow call chains, run the AI chat
1. Understand the codebase structure *visually* before setting up the CLI

Once you know the shape of the codebase from the Web UI, the CLI setup and MCP integration will feel much more purposeful. You are not setting up abstract tools — you are giving your AI editor the same map you just looked at.

-----

## The Quizmaster’s Final Summary 📋

Six episodes. Here is what the Quizmaster taught:

|Episode|What you learned                                                               |
|-------|-------------------------------------------------------------------------------|
|1      |Why your AI agent was guessing, and what GitNexus does about it                |
|2      |How `npx gitnexus analyze` builds the knowledge graph in 6 phases              |
|3      |`query`, `context`, `list_repos` — orientation and symbol investigation        |
|4      |`impact`, `detect_changes`, `rename` — blast radius, change scope, safe renames|
|5      |`cypher`, resources, prompts, agent skills — the advanced tier                 |
|6      |Web UI, Bridge mode, the licence, the complete workflow                        |

**The complete map of the Quizmaster’s knowledge:**

|Concept                 |GitNexus feature                               |
|------------------------|-----------------------------------------------|
|The Quizmaster          |GitNexus itself                                |
|The master answer sheet |The knowledge graph in LadybugDB               |
|The Quizmaster’s reading|`npx gitnexus analyze` — 6-phase indexing      |
|The audience’s questions|MCP tool calls from Claude Code, Cursor, etc.  |
|“Name that Symbol” round|`query` + `context` + `list_repos`             |
|The Lightning Round     |`impact` + `detect_changes` + `rename`         |
|The Bonus Round         |`cypher` + resources + prompts + agent skills  |
|The broadcast studio    |Web UI at gitnexus.vercel.app                  |
|The production van      |Bridge mode (`gitnexus serve`)                 |
|The briefing notes      |MCP resources (instant orientation data)       |
|Coaching the contestants|Agent skills (teach the AI how to use GitNexus)|
|The studio rules        |PolyForm Noncommercial licence                 |

-----

## Your Next Moves 🎯

1. **Install**: `npm install -g gitnexus`
1. **Index**: `cd your-project && npx gitnexus analyze`
1. **Connect**: `npx gitnexus setup` (or add manually to Claude Code)
1. **Verify**: ask your AI editor to call `list_repos`
1. **Try the Web UI**: `gitnexus.vercel.app` — drop in any public repo URL
1. **Star the repo**: [github.com/abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) — the project moves fast and the star helps the author know the community is watching
1. **Join the Discord**: [discord.gg/AAsRVT6fGb](https://discord.gg/AAsRVT6fGb) — active community, active development

The Quizmaster is ready. Your AI agents have been guessing for too long.

*Time to give them the answer sheet.*

-----

**🔗 Resources**

- **GitHub**: [github.com/abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus)
- **Web UI**: [gitnexus.vercel.app](https://gitnexus.vercel.app)
- **npm**: [npmjs.com/package/gitnexus](https://www.npmjs.com/package/gitnexus)
- **PolyForm Noncommercial licence**: [polyformproject.org/licenses/noncommercial/1.0.0/](https://polyformproject.org/licenses/noncommercial/1.0.0/)
- **Discord**: [discord.gg/AAsRVT6fGb](https://discord.gg/AAsRVT6fGb)

-----

*🎙️ Quizmaster GitNexus! is a series about GitNexus — the zero-server code intelligence engine that gives AI coding agents the architectural awareness to stop guessing and start knowing. Thank you for watching the show.*
