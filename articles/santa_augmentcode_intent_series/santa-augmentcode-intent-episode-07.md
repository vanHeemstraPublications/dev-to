---
title: "Santa Augmentcode Intent Ep.7"
published: false
part: 7
description: "Father Christmas explains how Intent orchestrates multiple agents running simultaneously without collisions, missed handoffs, or Christmas catastrophes. Waves, dependencies, and the art of elegant parallelism."
tags: [augmentcode, intent, multiagent, orchestration]
series: "Santa Augmentcode Intent"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/santa_augmentcode_intent/santa-augmentcode-intent-episode-07.png"
canonical_url: ""
organization: "the-software-s-journey“
---

# Parallel Elves, Zero Chaos — Multi-Agent Orchestration 🎁 — Augment Intent, Episode 7

> *The secret to running a smooth Workshop is understanding the difference between work that can happen at the same time and work that cannot. You cannot paint a toy before it is carved. You cannot test a toy before it is assembled. But you can absolutely carve a hundred toys simultaneously, paint them in parallel once each is carved, and run quality checks in a third wave. The key is knowing the dependencies. The key, always, is the spec.*

-----

## From Solo Agent to Agent Orchestra

In the early days of AI-assisted coding, the workflow was simple: one developer, one agent, one task at a time. The agent typed fast, but the work was serial. Task A finished before Task B started.

This is like running the North Pole Workshop with one Elf. Technically sufficient. Practically absurd.

The shift to multi-agent work is not simply “run more agents.” It is a fundamentally different coordination challenge. Fred Brooks described it for humans in *The Mythical Man-Month*: adding more workers to a project does not automatically accelerate it, because communication overhead grows and integration becomes the dominant cost. AI agents do not repeal this dynamic — they accelerate it.

Intent’s multi-agent orchestration is the answer to Brooks’ challenge, applied to AI agents.

-----

## The Three-Wave Pattern

Father Christmas has observed that most Workshop tasks fall into three waves of parallelism. Intent reflects this naturally.

**Wave 1 — Parallel Implementation**
Tasks that are independent of each other can start simultaneously. The Auth Token Elf and the Gateway Middleware Elf do not need each other’s output. They start at the same time, work on separate worktrees, and finish independently.

**Wave 2 — Dependent Integration**
Tasks that depend on Wave 1 completing. The Test Suite Elf cannot write meaningful integration tests until both implementation Elves are done. It waits for its inputs, then starts immediately when they arrive.

**Wave 3 — Verification and Review**
The Verifier and Code Review Elves run after Wave 2. They check everything against the spec, catch remaining issues, and produce the final verdict.

```
Wave 1 (parallel):
  Auth Token Elf ─────────────────────── done ──┐
  Gateway Middleware Elf ──────────────── done ──┤

Wave 2 (parallel, starts after Wave 1):          │
  Test Suite Elf ◄──────────────────────────────┤
  Docs Generator Elf ◄──────────────────────────┘

Wave 3 (after Wave 2):
  Verifier Elf ◄──────────────── checks all ──► Report
  Code Review Elf ◄────────────────────────── Review
```

The Coordinator manages these waves automatically, based on the dependency graph in the spec. No human needs to tell it when Wave 2 can start. The spec encodes that information.

-----

## Background Agents: The Night Shift

Intent also supports **background agents** — Elves who work quietly while you are focused elsewhere.

In the JWT authentication example from Episode 3, while the two main implementation Elves are doing their headline work, three background Elves are running simultaneously:

- **Lint & Type Check Elf**: continuously checking that changes do not break type safety or style rules.
- **Test Suite Elf**: writing tests in the background as interfaces are published.
- **Docs Generator Elf**: updating API documentation as endpoint signatures emerge.

These background agents do not block the main flow. They run in their own worktrees, produce their own commits, and report back to the Coordinator when done. The Coordinator integrates their output into the final pull request.

In the Workshop, these are the Elves who quietly restock materials, update the inventory, and prepare the packaging while the headline crafting is happening. They are not glamorous. They are indispensable.

-----

## Handling Handoffs Gracefully

The most fragile moment in any multi-agent workflow is the **handoff**: when one agent’s output becomes another agent’s input.

Without orchestration, handoffs fail silently. Agent A finishes and commits. Agent B starts and discovers Agent A’s interface is different from what the spec described. Confusion, rework, delay.

Intent handles handoffs through the spec. When Agent A completes, it **updates the spec** with the actual interface it produced. The Coordinator reads this update and re-briefs Agent B with the accurate information before it starts. Agent B always starts with the truth.

This is analogous to a baton in a relay race. The baton is the spec. The Coordinator ensures it is passed correctly. No dropped batons. No Christmas Eve disasters.

-----

## When to Use Which Specialist

Intent ships with a default set of Specialists. Here is Father Christmas’s guide to deploying them:

|Specialist     |When to Use                                  |North Pole Role                       |
|---------------|---------------------------------------------|--------------------------------------|
|**Investigate**|Before writing the spec — explore feasibility|Scout Elves assessing a new toy design|
|**Implement**  |Core code production                         |Craft Elves at their workbenches      |
|**Verify**     |After implementation — check against spec    |Quality Control Elves                 |
|**Critique**   |Review the spec before coding starts         |Senior Elves challenging the design   |
|**Debug**      |When tests fail or behaviour is wrong        |Repair Elves                          |
|**Code Review**|Automated PR review with codebase context    |Senior Elves reviewing finished work  |

The rule is: **never skip Investigate for genuinely novel tasks**, and **never skip Verify before merging**. Skipping these is how gifts arrive with missing parts.

-----

## Bringing Your Own Elves

Intent is designed to be open. You can bring your own specialist agents — Claude Code, OpenAI Codex, or OpenCode — and integrate them into the orchestration. If your team has built a custom agent that specialises in your domain (a “Security Review Elf” that knows your specific compliance requirements, for example), it can be plugged in as a Specialist.

Father Christmas respects specialisation. The best Toy Locomotive Elf is not the best Rag Doll Elf. The Workshop thrives because it matches the right Elf to the right toy.

-----

## SIPOC: Multi-Agent Orchestration

|            |S — Suppliers                                           |I — Inputs                                                     |P — Process                                                                                                                         |O — Outputs                                                  |C — Customers                              |
|------------|--------------------------------------------------------|---------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|-------------------------------------------|
|**Who/What**|Coordinator, all Specialist Agents, Context Engine, spec|Task dependency graph, agent roster, model selections, codebase|Identify parallelism → Wave 1 agents start → Handoffs via spec → Wave 2 starts → Background agents run → Verifier checks → PR ready |Verified, integrated pull request; updated spec; decision log|Developer, CI/CD, code reviewers, end users|
|**Workshop**|Father Christmas, all Elves, the Library                |Dependency chart, Elf skills, material availability            |Independent tasks start together → Handoffs recorded in Master List → Dependent tasks start when inputs ready → QC checks everything|All gifts built correctly, verified, packaged, on the sleigh |Children, parents, Christmas morning       |

-----

## The Mythical Man-Month, Solved (Partially)

Brooks was right: coordination is the dominant cost. Adding more agents to a poorly organised task makes it worse.

But Brooks was writing about human coordination, with its communication overhead and context-switching costs. Intent changes the calculus. When the spec is the coordination layer — when every agent is briefed from the same living document, when handoffs are managed by the Coordinator, when each agent has its own isolated workspace — the overhead of adding an agent is dramatically lower than adding a human.

Not zero. Not magic. But dramatically lower.

This is how the North Pole gets better every year. We do not just add Elves. We improve the coordination. The Workshop gets smarter, not just bigger.

-----

## What Comes Next

In our final episode, Father Christmas walks you through the complete journey: from first prompt to **merged pull request**. We bring together the spec, the Coordinator, the Elves, the workbenches, the Context Engine, and the orchestration — and we ship.

> *An orchestra without a conductor is noise. With a conductor, it is music. The spec is the score. The Coordinator is the conductor. The Elves are the musicians. And the result, when everything works, is Christmas.*
> 
> **Ho ho ho! 🎅**

-----

*Part of the [Santa Augmentcode Intent](#) series. Published on [dev.to](https://dev.to) under the [the-software-s-journey](https://dev.to/the-software-s-journey) organisation.*
