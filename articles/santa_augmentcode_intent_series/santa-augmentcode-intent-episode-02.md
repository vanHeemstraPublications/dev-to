---
title: "Santa Augmentcode Intent Ep.2"
published: false
part: 2
description: "Father Christmas explains Living Specs — the beating heart of Intent that stays accurate as Elves work, and why your old PRD is like last year’s Christmas catalogue."
tags: [augmentcode, intent, specdriven, aiagents]
series: "Santa Augmentcode Intent Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/santa_augmentcode_intent_series/santa-augmentcode-intent-episode-02.webp"
canonical_url: ""
organization: "the-software-s-journey"
---
# The Master Gift List That Writes Itself 🎄 

> Every year, on the first of December, I sit at my great oak desk and open the Master Gift List. In the old days, I wrote it once and hoped for the best. By the fifteenth, it bore little resemblance to reality. An Elf had improvised. A supplier had changed a toy’s colour. Three children had written amended letters. The List lied to me — and I only found out on Christmas Eve.No more.

## The Problem With Static Specifications

In software, as in Christmas, requirements arrive in waves. The product owner changes her mind. The designer refines the mockup. The security review adds three new constraints.

Traditional specifications — whether a Confluence page, a Notion doc, or a PDF handed over at the start of a sprint — share one fatal flaw: **they are written once and then abandoned**. The moment the first line of code is committed, the spec begins to drift. By the time you ship, nobody is quite sure what the original intention was.

Fred Brooks called this “document rot.” Father Christmas calls it “the Lying List,” and it has ruined more Christmas Eves than I care to admit.

## The Living Spec: What Intent Does Differently

In Augment Intent, the specification is not a document you write and forget. It is a **living spec** — a Markdown file that lives inside your workspace and evolves as work progresses.

Here is how it works:

**1. You seed the spec.** Head Elf Pepper (that is you) types a goal into the Coordinator. The Coordinator drafts an initial spec: requirements, architecture decisions, task breakdown, success criteria.

**2. The spec is the source of truth.** Every Specialist Agent receives the spec as its briefing. Not a copy of a chat history. Not a vague summary. The actual, versioned spec.

**3. As Elves complete tasks, the spec updates.** When the Auth Agent finishes the token service, the spec marks that task complete. When the API Agent discovers a complication, the spec records the decision. The spec stays accurate because it is being written by the same agents that are doing the work.

**4. When you change your mind, the update propagates.** If Pepper changes a constraint mid-flight, the Coordinator updates the spec and re-briefs any Elves whose work is affected. No more Elves building to an outdated design.

## A Tale of Two Lists

Let me show you the difference in concrete terms.

**The Old Way (Static List):**

```
Ticket XMAS-1234
Title: Improve gift delivery speed
Description: Make it faster. Children are waiting.
Assigned to: @delivery-elf
```

This ticket is, forgive my language, **useless to an agent**. What does “faster” mean? Faster than last year? Faster than a competitor? Faster per route, or faster in aggregate? An Elf handed this will make a reasonable guess — and the guess may be entirely wrong.

**The New Way (Living Spec):**

```markdown
## Gift Delivery Optimisation — Living Spec

### Goal
Reduce average per-route delivery time by 20% vs Christmas 2024.

### Success Criteria
- [ ] Route calculation completes in < 200ms
- [ ] Zero missed deliveries in smoke test (1,000 houses)
- [ ] Sleigh fuel consumption unchanged or reduced

### Constraints
- Must work with existing reindeer harness API (v3.2)
- No changes to the chimney-descent module (frozen until Jan)

### Tasks
- [x] Profile current route-calculation bottleneck — Dasher Agent
- [ ] Implement A* pathfinding — Prancer Agent (in progress)
- [ ] Integration test against 2024 route dataset — Blitzen Agent
- [ ] Update delivery manifest schema — Rudolph Agent

### Decisions
- 2025-12-03: Chose A* over Dijkstra for weighted graph support
- 2025-12-05: Excluded Antarctic routes from v1 scope
```

This spec is **machine-executable**. Every Elf knows what “done” means. Every constraint is explicit. Every decision is recorded. And when Prancer finishes A*, the spec will tick that box and Blitzen will know it is time to start testing.

## SIPOC: The Living Spec Process

|  | S — Suppliers | I — Inputs | P — Process | O — Outputs | C — Customers |
| --- | --- | --- | --- | --- | --- |
| Who/What | Developer (Head Elf Pepper), Coordinator Agent, Specialist Agents | Initial goal statement, codebase context, model selection | Goal → Coordinator drafts spec → Agents execute & update → Spec reflects reality | Always-accurate living spec, completed task list, decision log | All Specialist Agents, human reviewers, future contributors |
| Workshop | Pepper, Father Christmas, the Elves | “Deliver all gifts 20% faster” | Santa writes the List → Elves build → List updates as gifts are wrapped | A gift list that is always true | Every Elf, every Quality Inspector, the Head of Logistics |

## Why This Matters for Parallel Work

Here is the key insight. When three Elves work simultaneously on different parts of the toy, each one needs to know:

- What the other two are building.
- Which interfaces they must respect.
- What has already been decided.

Without a living spec, each Elf improvises. The train set’s power connector uses a different voltage than the controller the second Elf built. Integration collapses at the last minute.

With a living spec, those interfaces are declared upfront. When the first Elf changes something, the spec records it, and the second Elf’s briefing updates. **The spec is the coordination mechanism**.

As Augment’s manifesto puts it: once you are running multiple agents in parallel, the spec stops being process and starts being infrastructure.

## Practical Notes: Writing a Good Spec Seed

Father Christmas has learned, through decades of painful experience, that the quality of the output depends entirely on the quality of the intent put in. Here are my rules for seeding a Living Spec:

1. **Name the goal, not the solution.** Write *“reduce onboarding drop-off by 20%”*, not *“add a progress bar to the onboarding screen”*.
2. **State the constraints explicitly.** Frozen modules, existing APIs, budget limits — write them down before any Elf starts.
3. **Define done.** A measurable success criterion is worth a hundred vague requirements.
4. **Record decisions as they are made.** An undocumented decision is an ambiguity waiting to cause a merge conflict.

## What Is Coming Next

In Episode 3, Father Christmas will introduce the most important relationship in the Workshop: **Santa the Coordinator and the Elves as Specialist Agents**. We will examine who does what, how handoffs work, and why the Verifier Elf might be the most important Elf in the building.

> The Master Gift List is only as good as the team that follows it. Fortunately, my team is excellent.Ho ho ho! 🎅

*Part of the *[*Santa Augmentcode Intent*](#)* series. Published on *[*dev.to*](https://dev.to)* under the *[*the-software-s-journey*](https://dev.to/the-software-s-journey)* organisation.*