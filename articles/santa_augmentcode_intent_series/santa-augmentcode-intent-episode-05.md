---
title: "Santa Augmentcode Intent Ep.5"
published: true
part: 5
description: "Father Christmas explains Spec-Driven Development: why the plan must become the product, how living specs prevent late-night disasters, and why the North Pole has always been spec-driven."
tags: [augmentcode, intent, specdriven, softwaredevelopment]
series: "Santa Augmentcode Intent Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/santa_augmentcode_intent_series/santa-augmentcode-intent-episode-05.png"
canonical_url: ""
organization: "the-software-s-journey"
---
# Finishing Before Christmas — Spec-Driven Development 📜

Accompanying source code repository: [`Santa Augmentcode Intent`](https://github.com/software-journey/augmentcode-intent)

> Do you know why Christmas always arrives on time? Not because I am superhuman. Not because the reindeer are faster than physics should allow. Christmas arrives on time because of one inviolable rule in the North Pole: nothing gets built until we agree, in writing, on what done looks like. We call it the Master Gift List. The world calls it Spec-Driven Development. The result is the same: no surprises on Christmas morning.

## The Old Way: Code First, Regret Later

There is a seductive pattern in software development that I call **Build First, Discover Later**. It goes like this:

1. Someone has a rough idea.
2. A developer (or, increasingly, an agent) starts building immediately.
3. Halfway through, the stakeholder sees a demo and says: *“That is not what I meant at all.”*
4. Everything is reworked. The deadline slips. Someone’s Christmas is ruined.

I have witnessed this pattern in the Workshop. A zealous Elf, eager to begin, starts carving a rocking horse before Father Christmas has decided whether it should be red or blue, large or small, with or without a mane. Three hours later, the horse is red, large, and maned — and the child’s letter clearly specified *blue, small, no mane*.

The problem is not the Elf’s carving ability. The problem is that work began before intent was explicit.

## What Is Spec-Driven Development?

Spec-Driven Development (SDD) is a workflow practice, not a programming paradigm. It has one central principle:

> The spec is the primary artifact. Code is the result of executing it.

In SDD, you do not write code and then document it. You write a spec — a precise, executable description of what you intend to build — and then agents (or humans) implement it. The spec comes first. The spec stays current. The spec is what gets reviewed.

Augment Intent was built around this principle. Their product manifesto states it plainly: **at that point, the plan becomes the product.**

## The Three Pillars of SDD in Intent

### Pillar 1: Write the Spec Before Any Code

The Coordinator Agent will not spawn Specialists until a spec exists. This is not bureaucracy — it is discipline. A spec written before implementation captures the human’s **intent** (what success looks like, what constraints exist, what decisions have been made) rather than narrating code that has already been written.

A good pre-implementation spec answers:

- What is the goal, measured how?
- What must not change (frozen modules, existing contracts, budget)?
- What does “done” look like in a test?
- Which parts depend on which others?

### Pillar 2: The Spec Updates as Work Progresses

A spec that does not evolve becomes fiction. Intent’s living spec updates automatically as agents complete tasks, record decisions, and encounter new constraints. When you return to the spec after a day of agent work, it reflects **what was actually built**, not what was originally planned.

This closes the gap that traditionally exists between the plan and the product. In most organisations, that gap is enormous and filled with undocumented decisions, tribal knowledge, and polite disagreements about what the requirements “really meant.”

### Pillar 3: Review the Spec, Not Just the Code

Code review is expensive. Reviewing a 2,000-line pull request is difficult, slow, and error-prone. Reviewing a spec is cheap. A well-structured spec can be reviewed in minutes, catching fundamental misalignments before a single line of code is written.

SDD moves the review point earlier in the pipeline. You review **intent** first. Implementation follows. This is why Intent has the Verifier Agent checking output against the spec — because the spec is the ground truth, and the code is measured against it.

## The Christmas Deadline as a Forcing Function

Father Christmas has one advantage over most product teams: **an unmovable deadline**. Christmas is December 25th. Always. Everywhere. It does not slip. It does not move to accommodate a stakeholder who changed their mind in November.

This deadline is a gift (pun intended). It forces the Workshop to be explicit about scope from the very beginning. We cannot add “one more toy” on December 20th without removing something else. Every addition requires a trade-off. The Master Gift List enforces this.

SDD imposes the same discipline on software teams. When the spec defines the scope, additions are **visible**. You can see exactly what is in and what is out. Scope creep does not happen silently — it requires a spec change, which requires a decision, which requires a conversation. That conversation, had early, is cheap. Had at 11pm on December 24th, it is catastrophic.

## SDD vs Traditional Approaches

| Aspect | Traditional | Spec-Driven |
| --- | --- | --- |
| Source of truth | Code | Living Spec |
| When specs are written | After or alongside code | Before code |
| Spec accuracy over time | Drifts (document rot) | Stays current (auto-updated) |
| Agent alignment | Re-explain each session | Automatic via spec |
| Review point | Code review only | Spec review + code review |
| Scope control | Implicit, often invisible | Explicit, requires spec change |
| Refactoring cost | Break and fix | Spec-guided |

## SIPOC: Spec-Driven Development Workflow

|  | S — Suppliers | I — Inputs | P — Process | O — Outputs | C — Customers |
| --- | --- | --- | --- | --- | --- |
| Who/What | Product owner, developer, Coordinator Agent | Business goal, constraints, success criteria | Write spec → Review spec → Spawn agents → Agents implement → Spec updates → Verifier checks | Working software that matches intent, accurate documentation, decision log | Engineering team, product owner, QA, end users |
| Workshop | Management, Head Elf Pepper, Father Christmas | Child’s wish list, Workshop constraints, quality standards | Write the Master List → Agree on scope → Elves build → List updates → QC checks | Gifts that match the wish list, accurate gift manifest, no surprises | Children, parents, Father Christmas himself |

## A Worked Example: The Christmas Eve Delivery App

Let us say Head Elf Pepper wants to build a real-time delivery tracker for the sleigh. The old way:

```
Pepper: "Build a delivery tracker."
Agent: [builds something]
Pepper: "That is not what I wanted."
[Repeat until December 24th.]
```

The SDD way:

```markdown
## Christmas Eve Delivery Tracker — Spec

### Goal
Real-time map showing sleigh position and remaining deliveries,
updating every 30 seconds, accessible on elves' tablets.

### Success Criteria
- [ ] Map renders in < 1 second on standard tablet browser
- [ ] Position updates within 30s of sleigh movement
- [ ] Remaining house count is accurate (matches manifest)
- [ ] Works offline (last known position shown if signal lost)

### Constraints
- Must use existing Reindeer GPS API (v2)
- No server-side changes to Delivery Manifest Service
- Must work in Safari (elves use iPads)

### Out of Scope (v1)
- Historical route replay
- Per-gift tracking
- Weather overlay

### Tasks
- [ ] Implement GPS polling service — Tracker Elf
- [ ] Build map component — Map Elf
- [ ] Integrate manifest API — Data Elf
- [ ] Offline fallback — Resilience Elf
- [ ] Integration tests — Test Elf
```

This spec takes ten minutes to write and saves days of rework. The Elves know exactly what to build. Pepper reviews the spec and agrees it is correct before a line of code is written. The Verifier knows exactly what to check.

This is SDD. This is how Christmas gets delivered on time.

## What Comes Next

In Episode 6, Father Christmas will explain the **Context Engine** — the magical knowledge base that ensures every Elf in the Workshop understands every toy design, every material property, and every past decision. Without it, SDD is impossible at scale.

> The plan is the product. Everything else is wrapping paper.Ho ho ho! 🎅

*Part of the [Santa Augmentcode Intent](https://dev.to/wvanheemstra/series/37310) series. Published on [dev.to](https://dev.to) under the [the-software-s-journey](https://dev.to/the-software-s-journey) organisation.*
