---
title: "Santa Augmentcode Intent Ep.3"
published: false
part: 3
description: "Father Christmas explains the elegant division of labour inside Intent: the Coordinator Agent plans and delegates, Specialist Agents execute, and the Verifier checks. Just like Christmas."
tags: [augmentcode, intent, aiagents, agentic]
series: "Santa Augmentcode Intent Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/santa_augmentcode_intent_series/santa-augmentcode-intent-episode-03.png"
canonical_url: ""
organization: "the-software-s-journey"
---
# Santa Plans, Elves Build — Coordinator & Specialist Agents 🧝 

> A common misconception about the North Pole is that I build all the toys. I do not. I tried that once in 1742. It was catastrophic. What I do — what I have always done — is understand what needs to be built, break it into sensible pieces, assign the right Elf to each piece, and make sure the whole thing comes together correctly. That is the job of Father Christmas. And, as it turns out, that is also the job of the Coordinator Agent in Augment Intent.

## The Fundamental Division of Labour

There is a reason the Workshop has roles. An Elf who is brilliant at carving wooden horses may be hopeless at soldering circuit boards. Mixing roles creates chaos. Clear roles create Christmas.

Augment Intent formalises this insight into a three-part agent architecture:

| Role | Intent Name | North Pole Equivalent |
| --- | --- | --- |
| Plans, delegates, aligns | Coordinator | Father Christmas |
| Executes a specific task | Specialist / Implementor | Craft Elves |
| Checks output against the spec | Verifier | Quality Control Elves |
| Explores feasibility | Investigate Agent | Scout Elves |
| Finds and fixes failures | Debug Agent | Repair Elves |
| Reviews code quality | Code Review Agent | Senior Elves |

Each role is available as a named Specialist inside Intent. You can use the built-in roster or bring your own.

## What the Coordinator Does

The Coordinator is the first Agent you interact with in Intent. You give it a goal — in plain language — and it does the following:

**Step 1 — Draft the Living Spec.** The Coordinator reads your goal, consults the Context Engine (the Workshop’s knowledge of your entire codebase), and produces a structured spec with requirements, constraints, success criteria, and a proposed task breakdown.

**Step 2 — Decompose into parallel tasks.** The Coordinator identifies which parts of the work can run simultaneously. Building the token service does not depend on the gateway middleware being ready. Both can start at once. The Coordinator maps these dependencies explicitly.

**Step 3 — Spawn and brief Specialists.** For each task, the Coordinator creates a Specialist Agent, hands it the relevant portion of the spec, and grants it access to the appropriate files. The Specialist gets what it needs — nothing more, nothing less.

**Step 4 — Manage handoffs.** When Specialist A finishes and Specialist B depends on that result, the Coordinator orchestrates the handoff. The spec updates, B gets the new context, and work continues without human involvement.

**Step 5 — Run the Verifier.** Once implementation is complete, the Coordinator spawns the Verifier Agent, which checks the output against the spec’s success criteria. If something fails, the Coordinator sends it back to the relevant Specialist.

## What the Specialists Do

Specialists are focused. Each one has a single job and the full Context Engine behind it.

An **Implement Specialist** receives a task like *“add JWT validation middleware to the API gateway”* along with the relevant spec section, the existing middleware code, and the interface contracts agreed with other Specialists. It writes the code, commits it to its isolated branch, and reports back to the Coordinator.

A **Verify Specialist** receives the spec’s success criteria and the completed implementation. It runs tests, checks edge cases, and returns a structured verdict: pass, fail, or pass-with-caveats.

A **Debug Specialist** receives a failing test, a stack trace, and the relevant code. Its only job is to find and fix the root cause.

None of these Specialists needs to know about the other tasks in the session. The Coordinator holds the big picture. The Specialists hold deep focus.

## The Conversation Pattern

Here is a simplified transcript of how a session looks, using the North Pole analogy:

```
Head Elf Pepper → Coordinator:
"We need JWT authentication across the API gateway and auth service.
Tokens issued by auth-service, validated by gateway middleware.
Support refresh tokens and rate-limit the token endpoint."

Coordinator:
"Understood. I have drafted the spec. I am spawning three Elves:
• Auth Token Elf — implements issuance and refresh in auth-service
• Gateway Middleware Elf — implements validation in api-gateway
• Test Suite Elf — writes integration tests (starts after both finish)
Auth Token Elf and Gateway Middleware Elf are running in parallel now."

[20 minutes pass]

Auth Token Elf → Coordinator:
"Token issuance and refresh complete. Endpoints documented in spec."

Gateway Middleware Elf → Coordinator:
"JWT validation middleware complete. RS256 signing, expiry handling done."

Coordinator → Test Suite Elf:
"Both implementation Elves are done. Here is the updated spec.
Please write integration tests covering token issuance, refresh, expiry,
and rate limiting."

[Test Suite Elf runs]

Coordinator → Verify Elf:
"All tasks complete. Please verify against spec success criteria."

Verify Elf → Coordinator:
"Passed: 8/9 criteria. FAILED: rate limiting returns 429 but does not
include Retry-After header (spec line 14)."

Coordinator → Gateway Middleware Elf:
"Please fix: add Retry-After header to 429 responses."
```

No human needed to manage any of that. Pepper set the goal. Father Christmas ran the workshop.

## Choosing the Right Model for Each Role

One of Intent’s most practical features is that you can assign different AI models to different roles. Not every task benefits from the most powerful (and most expensive) model.

| Task | Recommended Model Tier | Why |
| --- | --- | --- |
| Coordinator — initial architecture | Opus (high reasoning) | Complex decomposition requires deep thinking |
| Implementor — routine code | Sonnet (fast, efficient) | Well-scoped tasks need speed, not heavy reasoning |
| Verifier | Sonnet or Opus | Depends on spec complexity |
| Debug | Opus | Root-cause analysis benefits from thorough reasoning |

Father Christmas always uses his best judgment for the biggest decisions and delegates the routine work to whichever Elf is quickest. Intent works the same way.

## SIPOC: Coordinator → Specialists → Verifier

|  | S — Suppliers | I — Inputs | P — Process | O — Outputs | C — Customers |
| --- | --- | --- | --- | --- | --- |
| Who/What | Developer, Context Engine, AI models | Goal statement, living spec, codebase, model selection | Coordinator plans → Specialists implement in parallel → Verifier checks → loop until done | Verified, spec-compliant implementation, merged PR | Engineering team, product owner, end users |
| Workshop | Pepper, the Workshop’s knowledge base, Elf skill roster | “Implement JWT auth” | Santa assigns → Elves build simultaneously → QC Elf inspects → rework if needed | Wrapped, quality-checked gifts ready for the sleigh | Children worldwide |

## What Can Go Wrong (And How Intent Handles It)

Even the best Workshop has incidents. An Elf misunderstands a spec line. A dependency is not available. A test fails unexpectedly.

Intent’s response is always to route the problem back through the spec. The Coordinator does not panic. It reads the failure report, updates the spec with the new constraint or decision, and re-briefs the relevant Specialist. The loop closes cleanly.

The developer only needs to intervene when the Coordinator surfaces a decision that requires **human judgment** — a product question, a risk acceptance, a business constraint that was not in the original spec. Everything else is handled in the Workshop.

## What Comes Next

In Episode 4, we will visit each Elf’s private workbench — the **isolated workspace** that Intent creates for every agent, ensuring no two Elves ever clobber each other’s work. Git worktrees, parallel branches, and the magic of resumable sessions.

> Every great team needs great coordination. I have been coordinating for over a thousand years. I am pleased that software has finally caught up.Ho ho ho! 🎅

*Part of the *[*Santa Augmentcode Intent*](#)* series. Published on *[*dev.to*](https://dev.to)* under the *[*the-software-s-journey*](https://dev.to/the-software-s-journey)* organisation.*