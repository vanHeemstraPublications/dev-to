---
title: "Santa Augmentcode Intent Ep.4"
published: true
part: 4
description: "Father Christmas explains how Intent gives every agent its own isolated workspace using Git worktrees — so parallel Elves never step on each other’s work."
tags: [augmentcode, intent, git, devtools]
series: "Santa Augmentcode Intent Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/santa_augmentcode_intent_series/santa-augmentcode-intent-episode-04.png"
canonical_url: ""
organization: "the-software-s-journey"
---
# Every Elf Gets a Workbench — Isolated Workspaces 🔨

Accompanying source code repository: [`Santa Augmentcode Intent`](https://github.com/software-journey/augmentcode-intent)

> In the early Workshop days, all the Elves shared one big table. It seemed efficient. It was a disaster. Jingle would sand a wheel just as Jangle reached for it. Twinkle’s paint would end up on Tinkle’s train set. The great Christmas Collision of 1889 — I do not wish to speak of it. The solution was obvious in retrospect: give every Elf their own workbench. Isolated, private, but connected to the same Master Gift List.Augment Intent does the same thing. It just calls them workspaces.

## The Problem With Sharing a Codebase

When multiple agents — or indeed multiple humans — work on the same set of files at the same time, collisions are inevitable. Agent A modifies `auth-middleware.ts` at line 47. Agent B modifies the same file at line 52. Neither agent knows the other is there. The merge conflict that results is not a bug in either agent’s reasoning. It is a **coordination failure** — the absence of isolation.

Git was designed for humans working mostly in series. A branch is opened, worked on for days or weeks, then merged. The assumption is that the pace of change is human-paced.

AI agents are not human-paced. They can modify dozens of files in minutes. Under parallel multi-agent execution, the conflict rate rises faster than any team can manage manually.

Intent solves this with **isolated workspaces backed by Git worktrees**.

## What Is a Git Worktree?

A worktree is a lesser-known Git feature that allows you to check out **multiple branches of the same repository simultaneously**, each in its own directory. Unlike opening two terminal windows and hoping for the best, worktrees are a first-class Git concept: they share the repository’s object store, so no data is duplicated, but each worktree has its own working tree and index.

```bash
# Classic git workflow (one checkout)
git checkout feat/jwt-auth
# ... work, commit, push

# Git worktree (multiple simultaneous checkouts)
git worktree add ../api-gateway-worktree feat/jwt-auth
git worktree add ../auth-service-worktree feat/auth-service
# Both directories exist simultaneously, sharing one .git object store
```

Intent automates all of this. When the Coordinator spawns a Specialist, Intent creates a dedicated worktree for that agent automatically. The Elf gets its own workbench. Other Elves cannot see its in-progress files. The files are isolated until the Elf is done and the Coordinator integrates the work.

## The Elf Workbench in Practice

Imagine the Coordinator has spawned three Specialist Agents for the JWT authentication task from Episode 3:

```
Workshop Floor
├── Auth Token Elf          → worktree: feat/auth-token-service
├── Gateway Middleware Elf  → worktree: feat/gateway-middleware
└── Test Suite Elf          → worktree: feat/integration-tests (waiting)
```

Each worktree contains a copy of the relevant files at the point the Elf starts. Changes made by Auth Token Elf in `auth-service/src/token-service.ts` are **invisible to Gateway Middleware Elf** until they are explicitly integrated. There are no accidental clobberings. No race conditions on file writes.

The Coordinator tracks the state of each worktree. When both implementation Elves complete, it orchestrates the merge — resolving any conflicts at the spec level (because the interface contracts were declared there) rather than discovering them at the file level.

## Resumable Sessions: The Workshop Is Open When You Return

There is another form of isolation that Father Christmas values enormously: **temporal isolation**. The ability to close the Workshop at night and find it exactly as you left it in the morning.

In most AI tools, closing the window ends the session. Context is lost. Agents forget. You start over.

Intent’s workspaces are **resumable**. When you close the application and reopen it the next morning, every agent is exactly where it was. The spec is unchanged. The worktrees are intact. The in-progress commits are safe. The Elves are waiting at their workbenches, ready to continue.

This is possible because Intent uses **auto-commit** — as agents complete units of work, their changes are committed to their branch automatically. The persistent state is the git history itself, which survives any restart.

```
Intent workspace state on close:
├── spec: JWT auth — 6/9 tasks complete
├── Auth Token Elf: feat/auth-token-service — all commits saved
├── Gateway Middleware Elf: feat/gateway-middleware — all commits saved
└── Test Suite Elf: feat/integration-tests — waiting to start

Intent workspace state on reopen (next morning):
└── [identical to above — nothing lost]
```

For Father Christmas, this means I can step away from the Workshop on December 23rd for a brief rest, return on the 24th, and find every Elf at their bench with their gifts half-wrapped exactly as I left them. The Workshop never forgets.

## The Unified Window: Code, Browser, Terminal, Git

Isolation does not mean fragmentation. Intent keeps everything visible in **one window**:

- The **code editor** shows the active agent’s files.
- The **built-in Chrome browser** previews localhost changes in real time.
- The **terminal** runs builds, tests, and scripts.
- **Git integration** handles staging, committing, and branch management.

You do not need to switch between VS Code, iTerm, Chrome, and SourceTree. The Workshop floor is one room with everything on it.

This matters for agent work because agents need to **see results immediately**. A Specialist that modifies a React component can open the browser preview in the same window, verify the rendering, and either commit or adjust — without handing off to a human to check.

## SIPOC: Isolated Workspace Management

|  | S — Suppliers | I — Inputs | P — Process | O — Outputs | C — Customers |
| --- | --- | --- | --- | --- | --- |
| Who/What | Coordinator, Git repository, file system | Task assignment, branch name, starting file state | Coordinator spawns agent → Intent creates worktree → Agent works in isolation → Auto-commit saves progress → Coordinator integrates on completion | Isolated branch per agent, no conflicts, resumable state | Coordinator Agent, Developer, CI/CD pipeline |
| Workshop | Father Christmas, the main toy vault | Elf assignment, workbench materials | Santa assigns bench → Elf gets private materials → works without interruption → gifts stored safely → Santa integrates at end | No collisions, no broken gifts, always resumable | Quality Control, Head Elf Pepper, the Sleigh |

## Practical Tip: When to Merge

Father Christmas has one firm rule about workbenches: an Elf’s work stays on their bench until it is **finished and verified**. Premature merges cause half-built toys to appear in the main inventory, confusing other Elves.

In Intent terms: the Coordinator should not merge a Specialist’s branch until:

1. The Specialist has reported completion.
2. The Verifier Agent has confirmed compliance with the spec.
3. Any interface contracts with other Elves have been respected.

The spec is the checklist. When all boxes are ticked, the merge is safe.

## What Comes Next

In Episode 5, Father Christmas will explain **Spec-Driven Development** — the philosophical shift that puts the living spec at the centre of the workflow and uses it to ensure everything finishes in time for Christmas. This is the *why* behind everything we have built so far.

> A tidy workbench is the sign of an organised mind. And an organised Workshop is the sign of gifts arriving on time.Ho ho ho! 🎅

*Part of the [Santa Augmentcode Intent](https://dev.to/wvanheemstra/series/37310) series. Published on [dev.to](https://dev.to) under the [the-software-s-journey](https://dev.to/the-software-s-journey) organisation.*
