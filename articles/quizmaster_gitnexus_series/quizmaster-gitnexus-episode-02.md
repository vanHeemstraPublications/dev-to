-----

## title: “Quizmaster GitNexus! 🎙️ Ep.2: The Quizmaster Does Their Reading”
published: false
description: “Episode 2: Before the show, the Quizmaster reads every file. GitNexus’s 6-phase indexing pipeline — from file walk to hybrid search index — is how your codebase becomes a queryable knowledge graph that answers in one call.”
tags: [ai, productivity, codenewbie, tooling]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/quizmaster-gitnexus-episode-02.png”
series: “Quizmaster GitNexus!”
canonical_url: “”
organization: “the-software-s-journey”

# Quizmaster GitNexus! 🎙️

## Episode 2: The Quizmaster Does Their Reading

*“No great Quizmaster ever walked on stage without doing the preparation.”*

-----

## Before the Show 📚

In Episode 1 we met the Quizmaster — GitNexus, the code intelligence engine that turns your codebase into a queryable knowledge graph so your AI agents can answer architectural questions in one call instead of guessing.

But before the Quizmaster can answer anything, they need to read everything.

Every professional quiz show host has a preparation process. They do not walk in cold. They read the source material, categorise the topics, map the relationships between facts, work out the chains of consequence — “if this answer changes, which other answers does that affect?” — and build the master answer sheet.

`npx gitnexus analyze` is that preparation process. One command. Six phases. The Quizmaster reads your entire codebase and stores everything they learned in LadybugDB — the private filing cabinet under `.gitnexus/` in your project.

This episode opens the filing cabinet.

-----

## 🗂️ SIPOC — The Preparation Process

|**Suppliers**                      |**Inputs**                            |**Process**                                       |**Outputs**                                          |**Consumers**                                      |
|-----------------------------------|--------------------------------------|--------------------------------------------------|-----------------------------------------------------|---------------------------------------------------|
|Your repository root               |Source files in 14 supported languages|Phase 1: Structure — walk the file tree           |Folder/file containment graph                        |Phase 2 (parsing)                                  |
|Tree-sitter (14 language parsers)  |Raw source text                       |Phase 2: Parse — generate ASTs, extract symbols   |Symbol table: functions, classes, methods, interfaces|Phase 3 (resolution)                               |
|Symbol table + import statements   |Cross-file references                 |Phase 3: Resolve — imports, calls, heritage, types|IMPORTS, CALLS, EXTENDS, IMPLEMENTS edges            |Phase 4 (clustering)                               |
|Call graph + edges                 |All resolved relationships            |Phase 4: Cluster — Leiden community detection     |Communities with cohesion scores                     |Phase 5 (processes)                                |
|Entry points + call chains         |Execution flow start points           |Phase 5: Trace processes — BFS from entry points  |Step-by-step execution flows                         |Phase 6 (search)                                   |
|All symbols + embeddings           |Keyword and semantic signals          |Phase 6: Build search index — BM25 + vectors + RRF|Hybrid search index                                  |MCP tools at query time                            |
|LadybugDB (embedded graph database)|Everything above                      |Persist graph to `.gitnexus/`                     |Queryable knowledge graph, ready for MCP server      |Claude Code, Cursor, Windsurf, OpenCode, the Web UI|

-----

## `npx gitnexus analyze` — The One Command 🚀

From your repository root:

```bash
npx gitnexus analyze
```

This single command does all six phases, installs agent skills, registers Claude Code hooks, creates `AGENTS.md` and `CLAUDE.md` context files, and registers the repo in the global registry at `~/.gitnexus/registry.json`.

The global registry is the reason one MCP server can serve multiple indexed repos. Index ten projects; one MCP server answers questions about all of them — no per-project configuration.

```bash
# Index this repo
cd ~/code/my-app
npx gitnexus analyze

# Index another
cd ~/code/my-api
npx gitnexus analyze

# One MCP server, two repos, everything accessible
npx gitnexus mcp
```

Now let us follow the Quizmaster through each phase of their reading.

-----

## Phase 1 — Structure: The File Tree Walk 🗂️

The Quizmaster starts with the table of contents. Before reading any code, GitNexus walks the entire directory tree and maps the containment relationships — which folders hold which files, which files belong to which modules.

This creates the skeleton of the knowledge graph: `CONTAINS` edges from folders to files, from files to their parent directories. The Quizmaster knows the shape of the library before reading a single book.

Files and directories listed in `.gitignore` and `.gitnexusignore` are excluded from this walk. GitNexus respects your boundaries.

**Nodes created:** `File`, `Directory`
**Edges created:** `CONTAINS`

-----

## Phase 2 — Parse: The Deep Read 📖

Now the Quizmaster reads every book. Not summaries — every page.

GitNexus uses **Tree-sitter** to parse each source file into an Abstract Syntax Tree (AST). Tree-sitter is a production-grade, multi-language parser used by GitHub, Neovim, and Helix. It reads source code and produces a precise structural representation — every function declaration, every class definition, every method signature, every interface.

**14 languages supported:** TypeScript, JavaScript, Python, Java, C#, Go, Rust, PHP, Ruby, Swift, C, C++, Dart, COBOL.

From each AST, GitNexus extracts the **symbol table**: every named entity in your codebase with its kind, location, language, and visibility (exported/private).

```
Extracted symbols:
  Function:  UserService.authenticate   (src/services/user.ts:42)
  Class:     UserService                (src/services/user.ts:10)
  Method:    UserService.findById       (src/services/user.ts:67)
  Interface: IUserRepository            (src/interfaces/user.ts:3)
  Function:  validateToken              (src/auth/token.ts:15)
```

**Nodes created:** `Function`, `Class`, `Method`, `Interface`
**Edges created:** `DEFINES` (file → symbol), `MEMBER_OF` (method → class)

-----

## Phase 3 — Resolve: The Cross-Reference Check 🔗

A single book is not a knowledge graph. Knowledge becomes a graph when you track the *relationships between books*.

Phase 3 is the Quizmaster’s cross-referencing pass — reading every footnote, every citation, every “see also.” GitNexus resolves:

**Imports** — which file imports which other file, and what it takes from it:

```typescript
// import { UserService } from './services/user'
// → IMPORTS edge: AuthController → UserService
// → Named binding: { UserService } with alias tracking
```

**Calls** — which function calls which other function, resolved across files:

```typescript
// this.userRepo.findById(id)
// → CALLS edge: UserService.authenticate → UserRepository.findById
// → Receiver type resolved via TypeEnvironment (self/this/super)
```

**Heritage** — class inheritance, interface implementation, mixins:

```typescript
// class SqlUserRepository extends BaseRepository implements IUserRepository
// → EXTENDS edge: SqlUserRepository → BaseRepository
// → IMPLEMENTS edge: SqlUserRepository → IUserRepository
```

**Type annotations** — explicit type extraction for receiver resolution, return type inference, doc-comment parsing.

**Exports** — which symbols are public vs. private, with re-export tracking across barrel files.

This is the phase where GitNexus moves from “a list of symbols” to “a map of how they relate.” The Quizmaster has not just read the books — they have charted which facts in which chapters depend on which facts in which other chapters.

**Edges created:** `IMPORTS`, `CALLS`, `EXTENDS`, `IMPLEMENTS`

-----

## Phase 4 — Cluster: The Topic Sorter 🗃️

A trivia night has rounds. You do not mix “History” questions with “Science” questions with “Pop Culture” questions randomly — you group them by topic so contestants can orient themselves.

Phase 4 runs the **Leiden community detection algorithm** on the resolved call graph to find natural functional communities — clusters of code that talk to each other more than they talk to the outside world.

Each cluster gets:

- A **heuristic label** (e.g., “Authentication”, “Payment Processing”, “Data Access Layer”)
- A **cohesion score** — how tightly coupled the cluster members are (0.0–1.0)
- A **symbol count** — how many functions/classes/methods belong to it

Tiny clusters (fewer than 5 symbols) are filtered out. The top 20 clusters by symbol count are surfaced in the MCP resources. Sub-communities sharing the same heuristic label are merged.

The clusters become the Quizmaster’s topic categories. When an agent asks “what communities does this codebase have?”, the Quizmaster can answer immediately: “Seven clusters — here they are, by size and cohesion.”

**Nodes created:** `Community`
**Edges created:** `MEMBER_OF` (symbol → community)

-----

## Phase 5 — Trace Processes: The “Follow the Chain” Round ⛓️

Some quiz questions are not about a single fact — they are about a sequence. “Walk me through the steps of the login flow, from HTTP request to database write.” That requires tracing an execution path.

Phase 5 identifies **entry points** — public functions, API endpoints, exported top-level symbols — and traces execution flows from each one through the call graph using Breadth-First Search.

Each traced flow becomes a **Process node** with step-by-step trace:

```
Process: Authentication Flow
  Step 1: AuthController.login           (src/controllers/auth.ts:23)
  Step 2: UserService.authenticate        (src/services/user.ts:42)
  Step 3: TokenService.validatePassword   (src/services/token.ts:15)
  Step 4: UserRepository.findByEmail     (src/repos/user.ts:67)
  Step 5: Database.query                  (src/db/connection.ts:12)
```

This precomputed trace is what the `query` MCP tool returns when you search for a symbol — not just the symbol, but which processes it participates in, and at which step.

**Nodes created:** `Process`
**Edges created:** `STEP_IN_PROCESS` (symbol → process, with step order)

-----

## Phase 6 — Index: The Hybrid Search Engine 🔍

The Quizmaster needs to find things fast. A contestant asks about a symbol and the Quizmaster cannot flip through 50,000 cards manually.

Phase 6 builds GitNexus’s **hybrid search index** combining three retrieval signals:

**BM25** — classic keyword retrieval. Fast, precise for exact symbol names. Finds `UserService.authenticate` when you type `authenticate`.

**Semantic vectors** — embedding-based retrieval using `transformers.js` (in-browser) or a compatible local embedder (CLI). Finds conceptually related symbols even when the exact name is different. Searches “login verification” and finds `authenticate`.

**RRF (Reciprocal Rank Fusion)** — merges BM25 and semantic rankings into a single score. The best of both retrieval strategies, without having to choose.

Results from the hybrid search are **grouped by Process** — so when you find `UserService.authenticate`, the response tells you it is in the `Authentication Flow` process at step 2. Context without needing a follow-up query.

-----

## What Gets Stored: The Knowledge Graph Schema 🗄️

After all six phases, LadybugDB contains a complete, queryable knowledge graph:

**Nodes:**

|Type       |What it represents                          |
|-----------|--------------------------------------------|
|`File`     |A source file                               |
|`Function` |A named function                            |
|`Class`    |A class definition                          |
|`Method`   |A class method                              |
|`Interface`|An interface or type alias                  |
|`Community`|A functional cluster (Leiden community)     |
|`Process`  |An execution flow traced from an entry point|

**Edges (via `CodeRelation.type`):**

|Type             |Meaning                                                                |
|-----------------|-----------------------------------------------------------------------|
|`CONTAINS`       |Folder/file contains this symbol                                       |
|`DEFINES`        |File defines this symbol                                               |
|`CALLS`          |This symbol calls that symbol                                          |
|`IMPORTS`        |This file imports from that file                                       |
|`EXTENDS`        |This class extends that class                                          |
|`IMPLEMENTS`     |This class implements that interface                                   |
|`MEMBER_OF`      |This method belongs to this class / this symbol belongs to this cluster|
|`STEP_IN_PROCESS`|This symbol is step N in this execution flow                           |

-----

## LadybugDB — The Private Filing Cabinet 🗃️

GitNexus stores the knowledge graph in **LadybugDB**, a purpose-built embedded graph database with vector support. It replaced KuzuDB in a migration completed in early 2026.

The database lives in `.gitnexus/lbug/` inside your repository. It never leaves your machine through GitNexus.

When the MCP server starts, it reads the global registry (`~/.gitnexus/registry.json`) and opens LadybugDB connections lazily — only when a query arrives for that repo. Connections are evicted after 5 minutes of inactivity. A maximum of 5 repos are held open concurrently.

**Staleness detection:** GitNexus compares the indexed git commit to the current `HEAD`. If the graph is behind, it warns you. Re-run `npx gitnexus analyze` to update.

-----

## The Quizmaster’s Filing Cabinet is Full 📂

After `npx gitnexus analyze` completes, the Quizmaster has done their reading. The filing cabinet — `.gitnexus/` — contains:

- The complete knowledge graph (nodes, edges, properties)
- The hybrid search index (BM25 + semantic vectors)
- The process traces (execution flows from entry points)
- The community clusters (Leiden detection results)
- The repo registration entry in `~/.gitnexus/registry.json`

The show is about to begin. The Quizmaster is ready.

In **Episode 3**, we ask our first questions — `query`, `context`, and `list_repos`. The starter for ten awaits.

-----

**🔗 Resources**

- **GitHub**: [github.com/abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus)
- **Tree-sitter**: [tree-sitter.github.io](https://tree-sitter.github.io)
- **LadybugDB migration notes**: [GitNexus CHANGELOG](https://github.com/abhigyanpatwari/GitNexus/blob/main/CHANGELOG.md)

-----

*🎙️ Quizmaster GitNexus! is a series about GitNexus — the zero-server code intelligence engine that indexes any codebase into a knowledge graph so AI agents stop guessing and start knowing.*
