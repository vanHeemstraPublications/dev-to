---
title: "Quizmaster GitNexus! 🎙️ Ep.4"
part: 4
published: false
description: "Episode 4: The show gets serious. `impact` calculates blast radius — exactly what breaks before you change anything. `detect_changes` maps your git diff to affected symbols and processes. `rename` coordinates multi-file renames with full preview."
tags: [ai, productivity, codenewbie, tooling]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/quizmaster-gitnexus-episode-04.png"
series: "Quizmaster GitNexus Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 4: The Lightning Round

*“No time to think. Just answer. What breaks if you change this?”*

-----

## The Stakes Get Higher ⚡

In Episode 3, the quiz warmed up nicely. We named symbols, explored their 360° context, discovered what calls what. The Quizmaster answered every question in one call.

Now the lightning round begins. These are the high-stakes questions — the ones where getting it wrong costs time, credibility, or production stability.

- *What breaks if I change this function’s signature?*
- *My git diff is large. Which processes are actually affected?*
- *I need to rename this class across 47 files. Show me every location before I touch a single one.*

Three tools. Three rounds. No guessing.

-----

## 🗂️ SIPOC — The Lightning Round

|**Suppliers**           |**Inputs**                   |**Process**                                              |**Outputs**                                                                  |**Consumers**                                                    |
|------------------------|-----------------------------|---------------------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------|
|A symbol name or path   |Upstream/downstream direction|`impact` tool — graph traversal with depth grouping      |Callers, caller-callers, grouped by proximity; confidence scores; risk rating|AI agent deciding whether to proceed, refactor first, or escalate|
|Current git working tree|Uncommitted changes or a diff|`detect_changes` tool — maps changed files to graph nodes|Affected symbols, processes disrupted, direct vs. transitive impact          |AI agent understanding the scope of in-progress work             |
|A symbol name + new name|Preview flag (optional)      |`rename` tool — graph-assisted multi-file rename         |All locations requiring update, grouped by file, with preview                |AI agent or developer executing a safe coordinated rename        |

-----

## `impact` — The Blast Radius Round 💥

*“If this changes, what falls?”*

This is the question every developer asks before a refactor and sometimes forgets to answer before a deploy. `impact` does the blast radius calculation that previously required either deep codebase familiarity or an uncomfortable amount of faith.

```
Tool: impact
Input: "UserService.authenticate"
Direction: upstream (what calls this, transitively)
Repo: my-app

Response:
  Blast Radius Analysis: UserService.authenticate
  Risk: HIGH

  Direct callers (depth 1):
    AuthController.login          src/controllers/auth.ts:23     confidence: 0.95
    AuthController.refreshToken   src/controllers/auth.ts:89     confidence: 0.91
    TestHelper.loginAsAdmin       tests/helpers/auth.ts:14       confidence: 0.88

  Transitive callers (depth 2):
    Express router → AuthController.login    (via route registration)
    IntegrationTest.testLogin → TestHelper.loginAsAdmin

  Processes disrupted:
    Authentication Flow — core step (step 2 of 8)
    Token Refresh Flow  — core step (step 2 of 5)

  Risk assessment:
    2 production callers in critical processes
    1 test helper (lower risk)
    No isolated callers
    Recommended: review AuthController.login and .refreshToken before changing signature
```

**Direction matters.** `impact` supports two directions:

- **Upstream** (`upstream`): what calls this symbol? Who depends on it? What breaks if you change it? Use this before modifying a function.
- **Downstream** (`downstream`): what does this symbol call? What does it depend on? Use this when you suspect a bug is coming from a dependency.

**Risk ratings** are assigned based on how many callers are in named processes, at what depth, and with what confidence:

- `LOW` — few callers, mostly in tests, low process involvement
- `MEDIUM` — multiple production callers, some process involvement
- `HIGH` — callers in critical processes, deep transitive chain

The Quizmaster does not just tell you *what* depends on a symbol. They tell you *how dangerous* the dependency chain is, and *which specific callers* to review.

### Impact in practice: the refactor check

Before any non-trivial change, an AI agent equipped with GitNexus should run `impact` first:

```
Agent: I'm going to modify the signature of `processPayment` to add a currency parameter.
       Let me check impact first.

[calls impact("processPayment", "upstream")]

Response: HIGH risk. 7 callers in 3 processes. PaymentController, OrderService, 
          and SubscriptionService all call this directly. 
          Modifying the signature requires updating all three.

Agent: Before changing processPayment, I'll update PaymentController, OrderService, 
       and SubscriptionService to pass the new currency parameter. Then I'll make 
       the signature change. Let me start with the callers.
```

This is the difference between an AI agent that ships broken code and one that thinks architecturally.

-----

## `detect_changes` — The “What Changed Since Last Night?” Round 📰

*“Your git diff is large. But what does it actually affect?”*

You have been working for three hours. Your diff spans twelve files. The changes feel coherent to you — you know what you were trying to accomplish. But your AI agent does not have that context. It sees twelve changed files and has to guess at the ripple effects.

`detect_changes` closes that gap by mapping your uncommitted diff to the knowledge graph:

```
Tool: detect_changes
Repo: my-app
(no other input needed — reads current working tree)

Response:
  Changed files: 12
  
  Directly modified symbols:
    UserService.authenticate    (signature modified — parameter added)
    UserService.findById        (implementation changed)
    TokenService.createToken    (new internal call added)
    PaymentService.charge       (unchanged file but affected by import change)

  Processes disrupted:
    Authentication Flow   — 2 modified symbols (steps 2, 4)
    Payment Processing    — 1 modified symbol (step 3)
    
  Transitive impact:
    AuthController.login calls UserService.authenticate (caller, depth 1)
    AuthController.refreshToken calls UserService.authenticate (caller, depth 1)
    [4 more transitive callers]

  Symbols changed but NOT in any process:
    Logger.formatAuditEntry    src/logging/audit.ts:34  (internal utility, low risk)
    
  Recommendation:
    Review Authentication Flow and Payment Processing for consistency.
    AuthController.login and .refreshToken may need updates to handle new parameter.
```

**When to use `detect_changes`:**

- Before committing a large set of changes — get the full picture of what you actually modified
- When asking an AI agent to review your work — give it the structured context instead of the raw diff
- Before a PR — understand which processes you have touched and whether your test coverage aligns
- When pairing `detect_changes` with `impact` — see both what changed *and* what those changes affect upstream

**What makes `detect_changes` different from `git diff`:**

`git diff` tells you which lines changed. `detect_changes` tells you which *symbols* those lines belong to, which *processes* those symbols participate in, and which other symbols *depend* on what you changed.

The Quizmaster translates the diff from “file changes” into “architectural consequences.”

-----

## `rename` — The Coordinated Update Round 📝

*“Forty-seven files. Every one of them has this name. Change all of them. Get none of them wrong.”*

Renaming a symbol in a large codebase is one of the highest-risk operations a developer performs. IDEs have “rename refactor” features that work for local references. They struggle with dynamic calls, string-based lookups, comment references, and cross-language boundaries.

GitNexus’s `rename` tool uses the knowledge graph to find every location that references a symbol — not just syntactically, but structurally. Every call site. Every import. Every type annotation. Every reference with confidence score.

```
Tool: rename
Input: symbol="UserService", new_name="AccountService"
Repo: my-app
Preview: true  (show me all locations before touching anything)

Response:
  Rename Preview: UserService → AccountService
  Locations requiring update: 34

  src/services/user.ts (class definition)
    Line 10: class UserService {          → class AccountService {
    Line 10: export class UserService {   → export class AccountService {

  src/controllers/auth.ts
    Line 3:  import { UserService }      → import { AccountService }
    Line 18: private userService: UserService  → private userService: AccountService
    Line 23: this.userService = new UserService()  → new AccountService()

  src/controllers/admin.ts
    Line 7:  import { UserService }      → import { AccountService }
    Line 44: const svc = new UserService(config)  → new AccountService(config)

  [... 28 more locations across 11 files]

  References with lower confidence (manual review recommended):
    src/utils/factory.ts:67    container.register('UserService', ...)
      confidence: 0.61 — string-based registration, may need manual update
    
    README.md:23               "See UserService for authentication details"
      confidence: 0.40 — documentation reference, not code

  Summary: 32 high-confidence updates + 2 requiring manual review
```

**Preview mode** (`preview: true`) shows every location without making any changes. Review the complete list. Verify the confidence scores. Check the low-confidence items. Only when satisfied do you run without preview to apply.

**Why confidence scores on rename?** Static analysis cannot resolve every reference with certainty. String-based dependency injection (`container.register('UserService', ...)`), reflection-based lookups, and documentation references all appear in codebases. GitNexus surfaces these at lower confidence rather than silently missing them or silently over-claiming.

The Quizmaster tells you what they know with certainty and flags what requires human judgment. That is the right behaviour.

### The rename workflow in practice

```
Agent: "Rename UserService to AccountService throughout the codebase."

Step 1: rename("UserService", "AccountService", preview=true)
  → Reviews all 34 locations
  → Flags 2 low-confidence references for human review
  → Agent presents list to developer: "I'll update these 32 automatically. 
     These 2 need your eyes — a string-based DI registration and a README reference."

Developer: "Correct. Proceed with the 32."

Step 2: rename("UserService", "AccountService", preview=false)
  → 32 files updated atomically
  → Agent notes: "Update factory.ts line 67 and README.md line 23 manually."
```

A rename that would have taken 45 minutes of find-and-replace, manual verification, and missed-one discoveries takes one structured conversation.

-----

## The Three Rounds Together: A Pre-Commit Workflow 🔄

Here is how `impact`, `detect_changes`, and `rename` work together in a real development session:

```
Developer: "I want to add an optional `currency` parameter to `processPayment`."

1. impact("processPayment", "upstream")
   → Risk: HIGH. 7 callers in 3 processes.
   → Decision: I need to update all callers before changing the signature.

2. context("PaymentController") + context("OrderService") + context("SubscriptionService")
   → Understand each caller's responsibility before touching them.

3. [Developer edits all callers to pass the new parameter with a default]

4. detect_changes()
   → Confirms: 4 files modified, 7 symbols touched, Payment Processing process affected.
   → Transitive impact shows 2 test files will need updating.

5. [Developer updates tests]

6. detect_changes() again
   → All affected areas now covered. Payment Processing flow consistent.
   → "Proceed to commit."
```

Three tools. One coherent pre-commit workflow. No architectural surprises after the merge.

-----

## Try It: Three Lightning Exercises ⚡

**Exercise 1 — `impact`**: Find the most-called function in one of your repos (use `query` to find it by searching for something central). Run `impact` with `upstream`. How deep does the transitive chain go? What is the risk rating?

**Exercise 2 — `detect_changes`**: Make a non-trivial edit to a source file — change a function signature, add a parameter, modify an import. Run `detect_changes`. How many symbols are shown as affected? Are any processes disrupted you did not intend to touch?

**Exercise 3 — `rename`**: On a test branch, run `rename` with `preview: true` on a class that has more than five callers. Look at the confidence scores. Find the lowest-confidence reference. Open that file. Understand why the analysis was uncertain.

-----

In **Episode 5**, we move to the bonus round: `cypher` for raw graph queries, the seven MCP resources for instant orientation, the two guided prompts, and the four auto-installed agent skills that teach your AI how to *use* GitNexus effectively.

*The lightning round is over. The bonus round awaits.*

-----

**🔗 Resources**

- **GitHub**: [github.com/abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus)
- **Leiden community detection**: [leidenalg.readthedocs.io](https://leidenalg.readthedocs.io)
- **MCP specification**: [modelcontextprotocol.io](https://modelcontextprotocol.io)

-----

*🎙️ Quizmaster GitNexus! is a series about GitNexus — the zero-server code intelligence engine that gives AI coding agents the architectural awareness to stop guessing and start knowing.*
