---
title: "Quizmaster GitNexus! 🎙️ Ep.3"
part: 3
published: false
description: "Episode 3: The show begins. The `query`, `context`, and `list_repos` MCP tools are the first three rounds — hybrid search with process grouping, 360° symbol analysis, and multi-repo discovery. One question. One complete answer."
tags: [ai, productivity, codenewbie, tooling]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/quizmaster-gitnexus-episode-03.png"
series: "Quizmaster GitNexus Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Quizmaster GitNexus! 🎙️

## Episode 3: Name That Symbol

*“Fingers on buzzers. Your time starts… now.”*

-----

## The Show Begins 🎬

The Quizmaster has done their reading (Episode 2). The knowledge graph is built. The MCP server is running. Your editor — Claude Code, Cursor, Codex, Windsurf, OpenCode — is connected.

Now the audience asks questions.

In a real quiz show, there are rounds. Each round has a different format — some are about identifying a subject, some are about exploring a topic in depth, some are about navigating a catalogue of options. GitNexus’s MCP tools work the same way.

This episode covers the first three tools: **`query`**, **`context`**, and **`list_repos`** — the foundational rounds that your AI agent will use dozens of times per session.

-----

## 🗂️ SIPOC — The First Three Rounds

|**Suppliers**                         |**Inputs**                   |**Process**                                              |**Outputs**                                                      |**Consumers**                                                         |
|--------------------------------------|-----------------------------|---------------------------------------------------------|-----------------------------------------------------------------|----------------------------------------------------------------------|
|MCP client (Claude Code, Cursor, etc.)|Natural language query string|`query` tool — hybrid BM25 + semantic + RRF search       |Matching symbols, grouped by process, with execution flow context|AI agent reasoning about what exists and how things connect           |
|Symbol name or path                   |Exact or partial identifier  |`context` tool — 360° symbol analysis via graph traversal|Callers, callees, clusters, processes, file location, edges      |AI agent planning an edit, refactor, or investigation                 |
|No input required                     |—                            |`list_repos` tool — reads global registry                |All indexed repo names, paths, git states, freshness             |AI agent choosing which codebase to query, or verifying index currency|

-----

## `list_repos` — The Catalogue 📚

Before asking any question, a good contestant checks they are in the right section of the library. `list_repos` answers: “What codebases does the Quizmaster have on file?”

```
Tool: list_repos
Input: (none)

Response:
  Indexed repositories:
  - my-app   (/Users/willem/code/my-app)   git: a3f9c12   fresh
  - my-api   (/Users/willem/code/my-api)   git: d8e1a07   stale (3 commits behind)
  - atlas-idp (/Users/willem/code/atlas)   git: f1c4b22   fresh
```

Three things in every response:

- **Repository name and path** — what is indexed and where
- **Git commit hash** — the exact commit the graph was built from
- **Freshness** — is the graph current with `HEAD`, or has code been committed since the last `analyze`?

The staleness warning is the Quizmaster being honest: “I read the book as of chapter 12, but three more chapters have been written since then.” Run `npx gitnexus analyze` to catch up.

When only one repo is indexed, the `repo` parameter becomes optional on all other tools. The Quizmaster assumes you mean the only book on the shelf.

-----

## `query` — The “Name That Symbol” Round 🔍

`query` is the hybrid search tool — the front door of the knowledge graph. Give it a natural language description or a symbol name. It returns matching symbols grouped by the execution processes they participate in.

This is the most-used tool. Agents call it before every substantive code operation.

### Keyword search

```
Tool: query
Input: "authenticate user"
Repo: my-app

Response:
  Process: Authentication Flow (3 symbols matching)
    Step 2: UserService.authenticate     src/services/user.ts:42
            — Validates credentials against database, returns JWT
            — Callers: 4  |  Callees: 3
    Step 3: TokenService.createToken     src/services/token.ts:15
            — Generates signed JWT from user payload
            — Callers: 1  |  Callees: 2
    Step 5: AuthController.login         src/controllers/auth.ts:23
            — HTTP POST handler for /auth/login endpoint
            — Callers: 0  |  Callees: 3

  Other matches (not in named process):
    validateAuthHeader  src/middleware/auth.ts:8
```

The Quizmaster does not just name the symbol — they place it in its execution context. You know immediately that `UserService.authenticate` is step 2 of the Authentication Flow, not an isolated function.

### Semantic search

`query` is not limited to exact names. Describe what you are looking for:

```
Tool: query
Input: "where do we handle failed login attempts and rate limiting"
Repo: my-app

Response:
  Process: Authentication Flow
    RateLimiter.recordFailedAttempt   src/middleware/rate-limit.ts:34
    RateLimiter.isBlocked             src/middleware/rate-limit.ts:52
    AuthController.login              src/controllers/auth.ts:23 (step 5)
```

The semantic layer finds conceptually related symbols even when the exact words do not match. BM25 catches keyword hits; the vector index catches meaning; RRF fusion merges both rankings. You get relevance without having to know the exact symbol name.

### What the response always includes

Every `query` result surfaces, for each matching symbol:

- **Symbol name, type, and file location** with line number
- **Brief description** extracted from doc comments (if present)
- **Caller count** — how many things call this
- **Callee count** — how many things this calls
- **Process membership** — which execution flows this symbol participates in, and at which step

One call. Orientation provided.

-----

## `context` — The 360° Deep Dive Round 🔬

A contestant who can name a symbol gets one point. A contestant who can explain everything about a symbol — what it calls, what calls it, which module it belongs to, which processes flow through it, how confident the graph is about each relationship — wins the round.

`context` is that second level. It takes a symbol (by name, by path, or by the ID returned from `query`) and returns a complete architectural portrait.

```
Tool: context
Input: "UserService.authenticate"
Repo: my-app

Response:
  Symbol: UserService.authenticate
  Type: Method
  File: src/services/user.ts, line 42
  Class: UserService (MEMBER_OF)
  Cluster: Authentication (cohesion: 0.87)
  Visibility: public (exported)

  Callers (things that call this):
    AuthController.login          src/controllers/auth.ts:23      confidence: 0.95
    AuthController.refreshToken   src/controllers/auth.ts:89      confidence: 0.91
    TestHelper.loginAsAdmin       tests/helpers/auth.ts:14        confidence: 0.88

  Callees (things this calls):
    UserRepository.findByEmail    src/repos/user.ts:67            confidence: 0.97
    TokenService.validatePassword  src/services/token.ts:15       confidence: 0.93
    Logger.audit                  src/logging/audit.ts:8          confidence: 0.85

  Processes:
    Authentication Flow — Step 2 of 8
    Token Refresh Flow  — Step 2 of 5

  Heritage:
    Class UserService has no extends
    UserService implements IUserService (src/interfaces/user.ts:3)

  Related symbols in same cluster:
    TokenService.createToken, AuthController.login,
    UserRepository.findByEmail, JwtValidator.verify
    (... 12 more in Authentication cluster)
```

Every relationship is annotated with a **confidence score** — how certain the static analysis was about resolving this edge. High-confidence edges (0.90+) mean the call was resolved directly from type annotations. Lower-confidence edges indicate inferred relationships where the receiver type was ambiguous.

### What `context` is used for

- **Before editing**: “What calls this? If I change the signature, who breaks?”
- **During debugging**: “This function is failing — who calls it and what are they passing?”
- **During onboarding**: “I just joined this project. Tell me everything about this service.”
- **During refactoring**: “I need to move this class. What depends on it?”

The Quizmaster answers all four questions in one call.

-----

## Traditional Graph RAG vs. GitNexus: The Buzzer Comparison ⚡

Here is what the same question costs under each approach:

**Traditional Graph RAG (the contestant who only got half the question paper):**

```
Agent query: "What depends on UserService?"

Query 1 → "Find nodes labelled UserService"
  → 47 node IDs returned
Query 2 → "What are the file paths for these nodes?"
  → 12 file paths returned
Query 3 → "Filter out test files"
  → 8 production files
Query 4 → "Which of these are high-risk call sites?"
  → LLM interprets...
  → Answer after 4+ round trips, context fragmented across responses
```

**GitNexus `context` tool (the Quizmaster):**

```
Agent query: context("UserService")
  → One response:
     3 callers in production (AuthController ×2, AdminController ×1)
     All 90%+ confidence
     AuthController.login is in Authentication Flow step 5
     AdminController.impersonate is in Admin Flow step 2
     Complete. Done.
```

Token cost: dramatically lower. Latency: one round trip. Context fragmentation: zero. Smaller model required: yes.

-----

## Connecting Your Editor — The Setup 🔌

To use these tools, the MCP server must be running and your editor configured to reach it.

**One-command setup** (auto-detects all installed editors):

```bash
npx gitnexus setup
```

**Manual: Claude Code**

```bash
claude mcp add gitnexus -- npx -y gitnexus@latest mcp
# macOS/Linux

# Windows:
claude mcp add gitnexus -- cmd /c npx -y gitnexus@latest mcp
```

**Manual: Cursor** (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "gitnexus": {
      "command": "npx",
      "args": ["-y", "gitnexus@latest", "mcp"]
    }
  }
}
```

**Manual: Windsurf** (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "gitnexus": {
      "command": "npx",
      "args": ["-y", "gitnexus@latest", "mcp"]
    }
  }
}
```

**Manual: OpenCode** (`~/.config/opencode/config.json`):

```json
{
  "mcp": {
    "gitnexus": {
      "command": "npx",
      "args": ["-y", "gitnexus@latest", "mcp"]
    }
  }
}
```

Once configured, you do not need to start the MCP server manually — the editor launches it on demand via `npx`.

-----

## Try It: Three Exercises 🎯

**Exercise 1 — `list_repos`**: Index a repo you know well with `npx gitnexus analyze`. Run `list_repos`. Verify the path, commit, and freshness shown. Commit one more change. Run `list_repos` again. Observe the staleness indicator.

**Exercise 2 — `query`**: Ask your editor (via the MCP tool) to `query` for “where is the main entry point of this application”. Compare the process-grouped result to what you would have gotten from a plain text search.

**Exercise 3 — `context`**: Find a service or class with several callers. Run `context` on it. Look at every caller’s confidence score. Find the lowest-confidence edge. Open the file. Understand why the static analysis was less certain about that one.

-----

In **Episode 4**, the show moves to the lightning round: `impact` (blast radius analysis), `detect_changes` (git-diff to affected symbols), and `rename` (coordinated multi-file rename with preview). The questions get harder. The Quizmaster does not flinch.

-----

**🔗 Resources**

- **GitHub**: [github.com/abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus)
- **Web UI**: [gitnexus.vercel.app](https://gitnexus.vercel.app)
- **MCP tool reference**: [github.com/abhigyanpatwari/GitNexus — README](https://github.com/abhigyanpatwari/GitNexus#mcp-tools)

-----

*🎙️ Quizmaster GitNexus! is a series about GitNexus — the zero-server code intelligence engine that gives AI coding agents the architectural awareness to stop guessing and start knowing.*
