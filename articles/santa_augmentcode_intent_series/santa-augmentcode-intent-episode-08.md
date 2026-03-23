---
title: "Santa Augmentcode Intent Ep.8"
published: false
part: 8
description: "Father Christmas brings the series home: a complete walkthrough of an Intent session from first prompt to merged pull request. Everything comes together. Christmas is delivered."
tags: [augmentcode, intent, devworkflow, aiagents]
series: "Santa Augmentcode Intent Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/santa_augmentcode_intent_series/santa-augmentcode-intent-episode-08.png"
canonical_url: ""
organization: "the-software-s-journey"
---
# The Gifts Are Under the Tree — From Spec to Merged PR 🎄 

> Every year, on the morning of December 25th, I allow myself one quiet moment before the sleigh is unpacked and the Thank-You Letters start arriving. I sit in the empty Workshop, still warm from the night’s work, and look at the bare shelves where the gifts used to be. They are gone because they were delivered. Every one of them. On time, as specified, to the right address. That moment — that quiet confirmation that everything worked — is what we have been building towards in this entire series. Today, we deliver.

## The Complete Picture

Over the past seven episodes, we have assembled all the pieces of the Intent workshop:

- **Episode 1**: The Workshop and what Intent is.
- **Episode 2**: The Living Spec — the source of truth.
- **Episode 3**: Santa the Coordinator and the Specialist Elves.
- **Episode 4**: Isolated workspaces and resumable sessions.
- **Episode 5**: Spec-Driven Development and finishing on time.
- **Episode 6**: The Context Engine — the Workshop Library.
- **Episode 7**: Multi-agent orchestration in waves.

Now we put them all together and walk through a complete Intent session, from the moment Head Elf Pepper opens the application to the moment the pull request is merged.

## The Scenario

**Goal**: Add a real-time gift delivery progress dashboard to the North Pole’s internal web application. The dashboard should show live sleigh position, remaining delivery count, and an estimated completion time. It must work on tablets and update every 30 seconds.

**Constraints**:

- Use the existing Reindeer GPS API (v2)
- No changes to the Delivery Manifest microservice
- Safari / iPad compatible
- Must pass existing end-to-end test suite

## Step 1: Open Intent and Set the Goal

Pepper opens Intent on her MacBook. She types into the Coordinator:

```
We need a real-time gift delivery dashboard. Show sleigh position
on a map, remaining delivery count, and estimated completion time.
Updates every 30 seconds. Must work on iPad Safari.
Use Reindeer GPS API v2. No changes to Delivery Manifest Service.
```

The Coordinator reads this prompt alongside the Context Engine’s analysis of the codebase. It knows the existing frontend stack (React, TypeScript), the API patterns used elsewhere in the project, and the existing test suite structure.

## Step 2: The Coordinator Drafts the Living Spec

Within seconds, the Coordinator produces:

```markdown
## Gift Delivery Dashboard — Living Spec

### Goal
Real-time dashboard showing sleigh position, delivery count,
and ETA. Updates every 30 seconds. iPad Safari compatible.

### Success Criteria
- [ ] Map renders in < 1s on iPad Safari
- [ ] Position updates within 30s of GPS data change
- [ ] Delivery count matches Manifest API response
- [ ] ETA calculated from current position + remaining stops
- [ ] All existing e2e tests pass
- [ ] Lighthouse accessibility score ≥ 90

### Constraints
- Reindeer GPS API v2 (existing auth token pattern)
- Delivery Manifest Service: read-only, no new endpoints
- Safari / iPad: no Chrome-only APIs

### Architecture
- New React component: `<DeliveryDashboard />`
- GPS polling service (30s interval, exponential backoff on fail)
- Map: Leaflet.js (already in dependencies — see package.json)
- Offline fallback: show last known position with staleness indicator

### Tasks
- [ ] GPS Polling Service — GPS Elf
- [ ] Map Component — Map Elf
- [ ] Delivery Count & ETA Widget — Data Elf
- [ ] Safari/iPad CSS fixes — Responsive Elf
- [ ] Integration tests — Test Elf (starts after GPS + Map done)
- [ ] Accessibility audit — A11y Elf (background)

### Decisions
(none yet)
```

Pepper reads the spec. She adds one clarification: *“ETA should display in local Workshop time, not UTC.”* The Coordinator updates the spec and records the decision.

**Review time: 4 minutes. No code written yet. One important decision already captured.**

## Step 3: Intent Creates Isolated Workspaces

The Coordinator identifies the dependency graph:

- GPS Elf and Map Elf can start in parallel immediately.
- Data Elf can start immediately (it only reads from the Manifest API).
- Responsive Elf can start once Map Elf has a working component.
- Test Elf starts after GPS Elf and Map Elf complete.
- A11y Elf runs as a background agent throughout.

Intent creates five Git worktrees:

```
feat/dashboard-gps-service        ← GPS Elf
feat/dashboard-map-component      ← Map Elf
feat/dashboard-data-widgets       ← Data Elf
feat/dashboard-responsive         ← Responsive Elf (waiting)
feat/dashboard-tests              ← Test Elf (waiting)
```

Wave 1 agents — GPS Elf, Map Elf, Data Elf — start simultaneously. The A11y Elf begins in the background.

## Step 4: Wave 1 Runs

Pepper watches the Intent window. Three agent conversations are active. Code appears in the Changes panel. The spec’s task list updates as work progresses.

**GPS Elf** implements the polling service, using the existing auth token pattern it found via the Context Engine:

```typescript
// gps-polling.service.ts
export class GpsPollingService {
  private interval = 30_000;
  private backoff = 1;

  async startPolling(onUpdate: (pos: SleighPosition) => void) {
    const poll = async () => {
      try {
        const pos = await reindeerGpsApi.getCurrentPosition();
        onUpdate(pos);
        this.backoff = 1;
      } catch {
        this.backoff = Math.min(this.backoff * 2, 8);
      }
      setTimeout(poll, this.interval * this.backoff);
    };
    poll();
  }
}
```

The spec updates: ✅ GPS Polling Service — GPS Elf — done.

**Map Elf** creates the `<DeliveryMap />` component using Leaflet.js, which it found already installed in `package.json` via the Context Engine. It does not install a duplicate library.

**Data Elf** builds the delivery count and ETA widget, correctly calling the Manifest API’s read-only endpoint and displaying ETA in Workshop local time (it read the spec decision).

## Step 5: Handoffs and Wave 2

Both GPS Elf and Map Elf report completion. The spec records the interfaces they produced:

```markdown
### Decisions
- GPS service exposes: `startPolling(cb: (SleighPosition) => void)`
- Map component props: `{ position: SleighPosition; zoom?: number }`
```

The Coordinator briefs Responsive Elf with the updated spec and the actual component structure. No guesswork. Test Elf receives both the GPS service interface and the Map component props, plus the existing e2e test patterns from the Context Engine.

Wave 2 begins. Responsive Elf adds Safari/iPad CSS. Test Elf writes integration tests.

## Step 6: The Verifier Checks Everything

Wave 2 complete. The Coordinator spawns the Verifier Elf with the full spec and all five implementations.

Verifier’s report:

```
✅ Map renders in < 1s on iPad Safari — confirmed (Lighthouse: 0.7s)
✅ Position updates within 30s — confirmed
✅ Delivery count matches Manifest API — confirmed
✅ ETA in Workshop local time — confirmed
✅ Existing e2e tests pass — confirmed
✅ Lighthouse accessibility score ≥ 90 — confirmed (score: 94)
⚠️  Minor: GPS service does not log polling errors to existing
    structured logger (see logger.ts — used throughout codebase)
```

The warning is real and useful. The Context Engine told the Verifier about `logger.ts`. A generic agent would have missed it.

The Coordinator sends the GPS Elf back for a five-minute fix. It adds one line:

```typescript
} catch (err) {
  logger.warn('GPS polling failed', { error: err, backoff: this.backoff });
```

Re-verification: all green.

## Step 7: The Pull Request

The Coordinator integrates all five worktrees into a single branch `feat/delivery-dashboard` and opens a pull request. The PR description is generated from the Living Spec:

```markdown
## Gift Delivery Dashboard

Implements real-time dashboard (sleigh position, delivery count, ETA).

### Changes
- New: `GpsPollingService` with 30s polling + exponential backoff
- New: `<DeliveryMap />` using existing Leaflet.js dependency
- New: `<DeliveryStats />` widget with ETA in Workshop local time
- New: iPad/Safari responsive CSS
- New: Integration test suite (12 tests, all passing)

### Verified Against Spec
All 6 success criteria confirmed by Verifier Agent.
Existing e2e suite: all passing.

### Decisions Recorded
- ETA displayed in Workshop local time (not UTC) — per Pepper, Dec 3
- Used existing Leaflet.js (not installed new mapping library)
- GPS errors logged via existing structured logger (logger.ts)
```

Pepper reviews the spec (4 minutes). She reviews the diff (10 minutes, because the spec told her exactly what to look for). She approves.

**Total elapsed time: 47 minutes. Zero rework. Christmas safe.**

## What We Built Together

Over this series, Father Christmas and Head Elf Pepper have explained every layer of Intent:

| Concept | What It Does | Workshop Equivalent |
| --- | --- | --- |
| Living Spec | Source of truth, auto-updated | Master Gift List |
| Coordinator Agent | Plans, delegates, manages handoffs | Father Christmas |
| Specialist Agents | Execute focused tasks in parallel | Craft Elves |
| Isolated Workspaces | No collisions between parallel agents | Private workbenches |
| Spec-Driven Development | Plan first, code follows | Write the List before carving begins |
| Context Engine | Deep codebase knowledge for every agent | The Workshop Library |
| Multi-Agent Orchestration | Waves, handoffs, background agents | Workshop floor choreography |
| Resumable Sessions | State preserved across restarts | Workshop never forgets |

## SIPOC: The Complete Intent Workflow

|  | S — Suppliers | I — Inputs | P — Process | O — Outputs | C — Customers |
| --- | --- | --- | --- | --- | --- |
| Who/What | Developer, Coordinator, Specialists, Context Engine, AI models | Goal statement, codebase, constraints, model selection | Spec → Review → Wave 1 agents → Handoffs → Wave 2 → Verifier → PR | Verified code, living spec, decision log, merged PR | Engineering team, product owner, CI/CD, end users |
| Workshop | Pepper, Father Christmas, all Elves, the Library | Gift order, Workshop constraints, quality standards | Write List → Agree → Parallel building → Handoffs → QC → Sleigh | All gifts delivered correctly, on time, to every child | Children of the world |

## Getting Started

Intent is available in **public beta for macOS**. [Download it here](https://www.augmentcode.com/product/intent). It uses your existing Augment credits. You can also bring Claude Code, Codex, or OpenCode if you already have subscriptions.

Augment’s documentation is at [docs.augmentcode.com](https://docs.augmentcode.com). Their manifesto — *The End of Linear Work* — is worth reading before your first session.

## A Final Word from Father Christmas

> I have been doing this for over a thousand years. Every century, the tools improve. The quill gave way to the telegraph, the telegraph to the computer, and now the computer gives way to the agent. But the fundamental challenge has never changed: how do you coordinate complex, parallel work towards a shared goal, on an unmovable deadline, without chaos?The answer, in 1025 and in 2025, is the same: a clear plan, a good team, and the discipline to keep the plan honest.Augment Intent is the first software I have encountered that truly understands this. It puts the plan first. It keeps the plan honest. It coordinates the team without the Elves colliding. And it finishes on time.I am proud of everything we have built in this Workshop. I hope you will build something wonderful in yours.Merry Christmas, and Happy Coding.Ho ho ho! 🎅

*This concludes the *[*Santa Augmentcode Intent*](#)* series. All eight episodes are available on *[*dev.to*](https://dev.to)* under the *[*the-software-s-journey*](https://dev.to/the-software-s-journey)* organisation.*

*Thank you for reading. May your specs be living and your merges be clean.*