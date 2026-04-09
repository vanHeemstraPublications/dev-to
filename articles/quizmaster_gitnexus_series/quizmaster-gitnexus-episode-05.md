---
title: “Quizmaster GitNexus! 🎙️ Ep.5: The Bonus Round”
part: 5
published: false
description: "Episode 5: The advanced tier. `cypher` gives raw graph query access. Seven MCP resources provide instant orientation. Two guided prompts structure complex workflows. Four auto-installed agent skills teach your AI to use the Quizmaster’s full capabilities."
tags: [ai, productivity, codenewbie, tooling]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/quizmaster-gitnexus-episode-05.png"
series: "Quizmaster GitNexus Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 5: The Bonus Round

*“Congratulations. You have made it to the bonus round. The questions are harder. The payoff is bigger. And the Quizmaster has a few surprises left.”*

-----

## Beyond the Standard Rounds 🎁

Episodes 3 and 4 covered the seven MCP tools — the primary interface between your AI agent and GitNexus’s knowledge graph. For the majority of coding tasks, `query`, `context`, `list_repos`, `impact`, `detect_changes`, and `rename` will be everything you need.

But GitNexus exposes more than tools. There are also:

- **7 MCP resources** — instant, low-latency orientation data your agent reads before asking questions
- **2 guided prompts** — structured workflows for pre-commit impact analysis and architecture documentation
- **4 auto-installed agent skills** — Markdown instruction files that teach your AI *how to use* the Quizmaster

And one more tool that belongs in the bonus round: **`cypher`** — raw graph query access for power users who want to write their own questions.

-----

## 🗂️ SIPOC — The Bonus Round

|**Suppliers**               |**Inputs**                             |**Process**                                          |**Outputs**                                                     |**Consumers**                                                      |
|----------------------------|---------------------------------------|-----------------------------------------------------|----------------------------------------------------------------|-------------------------------------------------------------------|
|LadybugDB graph database    |Cypher query string                    |`cypher` tool — direct graph query execution         |Raw graph results (nodes, edges, properties)                    |Power users building custom analysis, debugging graph state        |
|Global registry + graph     |Resource URI (gitnexus://…)            |MCP resource read — low-latency static or cached data|Context overview, cluster listings, process traces, graph schema|AI agent orientating itself at session start                       |
|Prompt template + parameters|User intent (pre-commit / architecture)|MCP prompt — structured multi-step workflow          |Guided sequence of tool calls with explanation at each step     |Developers wanting a coached workflow, not just raw tools          |
|Repository structure        |Entry point community analysis         |Agent skills auto-install during `gitnexus analyze`  |Four Markdown skill files in `.claude/skills/`                  |Claude Code (and compatible agents) reading skills at session start|

-----

## `cypher` — Write Your Own Question 🖊️

The Quizmaster has a master answer sheet. But what if your question is not on the standard paper? What if you need to query the graph in a way none of the built-in tools cover?

`cypher` gives you direct access to LadybugDB using Cypher query syntax — the same query language used by Neo4j. GitNexus exposes a static schema resource (`gitnexus://repo/{name}/schema`) that documents every node type, relationship type, and example query.

```
Tool: cypher
Repo: my-app
Query: |
  MATCH (f:Function)-[:CALLS]->(g:Function)
  WHERE g.name = 'Logger.error'
  RETURN f.name, f.file, f.line
  ORDER BY f.file

Response:
  f.name                    f.file                         f.line
  AuthController.login      src/controllers/auth.ts        47
  PaymentService.charge     src/services/payment.ts        112
  OrderService.submit       src/services/order.ts          89
  UserService.authenticate  src/services/user.ts           58
  [... 12 more]
```

The schema (available via the `gitnexus://repo/{name}/schema` resource) documents:

```yaml
# Nodes
File:        { path, language, exports }
Function:    { name, file, line, visibility, language }
Class:       { name, file, line, visibility, language }
Method:      { name, file, line, visibility, language }
Interface:   { name, file, line, visibility, language }
Community:   { label, cohesion, symbolCount }
Process:     { name, entryPoint, stepCount }

# Relationships
CONTAINS:        (File)-[CONTAINS]->(Function|Class|Interface)
DEFINES:         (File)-[DEFINES]->(Function|Class|Interface)
CALLS:           (Function|Method)-[CALLS { confidence }]->(Function|Method)
IMPORTS:         (File)-[IMPORTS]->(File)
EXTENDS:         (Class)-[EXTENDS { confidence }]->(Class)
IMPLEMENTS:      (Class)-[IMPLEMENTS { confidence }]->(Interface)
MEMBER_OF:       (Method)-[MEMBER_OF]->(Class)
               | (Function|Class)-[MEMBER_OF]->(Community)
STEP_IN_PROCESS: (Function|Method)-[STEP_IN_PROCESS { step }]->(Process)
```

### Example cypher queries

Find all functions with more than 10 callers (high-impact targets for review before refactoring):

```cypher
MATCH ()-[:CALLS]->(f:Function)
WITH f, count(*) AS callerCount
WHERE callerCount > 10
RETURN f.name, f.file, callerCount
ORDER BY callerCount DESC
```

Find all functions that call both `Logger.error` and `Database.rollback` (exception handlers):

```cypher
MATCH (f:Function)-[:CALLS]->(log:Function {name: 'Logger.error'}),
      (f)-[:CALLS]->(db:Function {name: 'Database.rollback'})
RETURN f.name, f.file
```

Find all classes that implement more than two interfaces (potential violation of interface segregation):

```cypher
MATCH (c:Class)-[:IMPLEMENTS]->(i:Interface)
WITH c, count(i) AS interfaceCount
WHERE interfaceCount > 2
RETURN c.name, c.file, interfaceCount
ORDER BY interfaceCount DESC
```

`cypher` is the bonus round for analysts, architects, and anyone who has a question the standard tools do not cover. Most users will not need it most of the time. When you do need it, it is the most powerful tool in the set.

-----

## The Seven MCP Resources — Instant Orientation 📋

MCP resources are not tools — you do not call them with arguments and wait for computation. They are read-only data sources that return quickly from cached or pre-computed state. Your agent reads them at the start of a session to orient itself before asking deeper questions.

Think of resources as the Quizmaster’s briefing notes — handed to each contestant before the show, so they know what topics are in scope and how the evening is structured.

|Resource URI                           |Content                                                                                      |Latency               |
|---------------------------------------|---------------------------------------------------------------------------------------------|----------------------|
|`gitnexus://repos`                     |All indexed repos: names, paths, git hashes, freshness                                       |~1ms (registry read)  |
|`gitnexus://repo/{name}/context`       |Repo overview: file count, language breakdown, symbol totals, community count, indexed commit|~1ms (cached)         |
|`gitnexus://repo/{name}/clusters`      |Top 20 communities by symbol count, with cohesion scores and top members                     |~10–50ms (DB scan)    |
|`gitnexus://repo/{name}/processes`     |All traced execution flows with entry points and step counts                                 |~10–50ms (DB scan)    |
|`gitnexus://repo/{name}/clusters/{id}` |Detail for one cluster: all member symbols, sub-communities                                  |~20–100ms (two-query) |
|`gitnexus://repo/{name}/processes/{id}`|Detail for one process: full step-by-step trace with files                                   |~20–100ms (two-query) |
|`gitnexus://repo/{name}/schema`        |Static graph schema: node types, relationship types, example Cypher queries                  |~0ms (constant string)|

### The recommended agent session start

A well-configured agent (or one using GitNexus’s auto-installed skills) reads resources in this order at the start of every session:

```
1. gitnexus://repo/{name}/context
   → How big is this codebase? How many symbols? Is the index fresh?
   
2. gitnexus://repo/{name}/clusters
   → What are the major functional communities? Which are largest?
   
3. gitnexus://repo/{name}/processes
   → What are the main execution flows? Which are most connected?
```

Three resource reads. Sub-second total. The agent now knows the shape of the entire codebase before writing a single line of code or running a single tool.

-----

## The Two Guided Prompts — Coached Workflows 🎓

MCP prompts are structured multi-step workflows with explanations. They coach the agent through a complex task — not just providing tools, but telling the agent which tools to call in which order and why.

GitNexus ships two:

### `detect_impact` — Pre-Commit Analysis

Guided workflow for assessing the impact of pending changes before commit. Runs automatically in sequence:

1. Read `gitnexus://repo/{name}/context` — verify index freshness
1. Call `detect_changes` — map diff to affected symbols and processes
1. For each high-impact symbol: call `impact` with upstream direction
1. Summarise: processes touched, risk ratings, callers needing review

The agent presents a structured pre-commit report instead of a raw list of changed files.

### `generate_map` — Architecture Documentation

Guided workflow for producing architecture documentation from the knowledge graph:

1. Read `gitnexus://repo/{name}/clusters` — list all communities with sizes
1. Read `gitnexus://repo/{name}/processes` — list all execution flows
1. For each significant cluster and process: call `context` on entry point symbols
1. Generate a Mermaid diagram of the top-level architecture
1. Write a Markdown summary of each major community and its relationships

The result is auto-generated architecture documentation that is guaranteed to reflect the actual code, not a human’s memory of it.

-----

## The Four Agent Skills — Teaching the Quizmaster’s Methods 📖

When you run `npx gitnexus analyze`, GitNexus does not just build the graph — it auto-installs four **agent skills** into `.claude/skills/gitnexus/` (and equivalent directories for other editors). These are Markdown instruction files that Claude Code reads at session start, teaching it how to use the Quizmaster effectively.

Four skills, four workflows:

### Skill 1: Exploring

*Navigate unfamiliar code using graph relationships instead of text search.*

The skill teaches the agent to start with resources (cluster and process listings), then use `query` to locate entry points, then use `context` to follow relationship chains outward. Graph-first navigation instead of file-grepping.

Typical use: onboarding to a new codebase, or investigating an unfamiliar module before making changes.

### Skill 2: Debugging

*Trace bugs through call chains to find root causes.*

Teaches the agent to use `context` to get the 360° view of the failing function, then trace callers upward and callees downward to find where unexpected state might be introduced. Uses `impact` to understand which other functions share the same dependency chain.

Typical use: a test is failing; the agent traces the call chain rather than reading code linearly.

### Skill 3: Impact Analysis

*Calculate blast radius before making changes, with risk-level ratings.*

The pre-change checklist: read clusters and processes first, then run `impact` on every symbol being modified, classify risk (LOW/MEDIUM/HIGH), report to developer before writing any code. No change is made until the blast radius is understood.

Typical use: any non-trivial refactor, any signature change, any interface modification.

### Skill 4: Refactoring

*Plan safe refactors using complete dependency mapping.*

Teaches the combined workflow: `impact` to understand scope, `context` on all affected callers, `rename` with preview before execution, `detect_changes` post-edit to verify coverage. The structured sequence that turns a risky refactor into a methodical operation.

Typical use: large renames, service extractions, interface changes across many callers.

### Per-community skills (with `--skills` flag)

Run `npx gitnexus analyze --skills` to generate additional per-community skill files based on the Leiden clusters detected in your codebase. Each community skill describes:

- The community’s key files and entry points
- Its execution flows and cross-area connections
- Common patterns and gotchas specific to that module

These community skills give Claude Code (and compatible agents) targeted context for the exact area of code being worked on — not just general GitNexus usage, but knowledge of *this specific module in this specific repo*.

-----

## Claude Code — The Deepest Integration 🔗

Of all the editors that support GitNexus, Claude Code gets the most comprehensive integration:

**MCP tools** — all seven tools available in the conversation
**Agent skills** — four base skills + per-community skills auto-loaded at session start
**PreToolUse hooks** — before every `grep`, `glob`, or `bash` call, Claude Code automatically enriches the search with graph context from GitNexus
**PostToolUse hooks** — after every `git commit`, GitNexus automatically re-indexes the repository

The hooks mean Claude Code is never operating on a stale graph. Every commit triggers a re-index. Every search is graph-enriched. Every session starts with fresh architectural context.

To install (one command):

```bash
# macOS / Linux
claude mcp add gitnexus -- npx -y gitnexus@latest mcp

# Windows
claude mcp add gitnexus -- cmd /c npx -y gitnexus@latest mcp
```

The hooks are installed automatically by `npx gitnexus analyze` (not `setup` — you need the analyze step to install hooks for a specific repo).

-----

## Try It: Three Bonus Exercises 🎯

**Exercise 1 — `cypher`**: Write a Cypher query that finds all functions in your codebase that are called by more than 5 other functions but call 0 other functions. These are your “leaf” functions — utility code that everyone depends on. What patterns do you see?

**Exercise 2 — Resources**: Read `gitnexus://repo/{name}/clusters` on one of your indexed repos. Find the cluster with the highest cohesion score. Open the `gitnexus://repo/{name}/clusters/{id}` detail for it. Does the set of member symbols match your mental model of what “belongs together” in that part of the codebase?

**Exercise 3 — Generate Map prompt**: Ask Claude Code (with GitNexus connected) to use the `generate_map` prompt on your repo. Review the generated Mermaid diagram. Does it accurately reflect the major components? What does it get right that would have taken you an hour to document manually?

-----

In **Episode 6**, the final episode, we go live: the Web UI, Bridge mode, and the licence — what GitNexus costs, what it covers, and how to use it in commercial contexts.

The Quizmaster’s show has one more segment. Don’t change the channel.

-----

**🔗 Resources**

- **GitHub**: [github.com/abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus)
- **Cypher query language**: [neo4j.com/docs/cypher-manual](https://neo4j.com/docs/cypher-manual/current/)
- **MCP specification**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **LobeHub skills marketplace**: [lobehub.com](https://lobehub.com)

-----

*🎙️ Quizmaster GitNexus! is a series about GitNexus — the zero-server code intelligence engine that gives AI coding agents the architectural awareness to stop guessing and start knowing.*
