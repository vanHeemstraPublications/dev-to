---
title: "Agility Game and Detective Operating System with Open Engineering Platform 🕵️🎮 Ep.1"
published: false
description: "Episode 1: The owner of Agility Game and the owner of Detective Operating System have been assigned the same Kubernetes cluster. Neither wants to import the other's code. Neither has to. This episode introduces the Open Engineering Platform (OEP) — a Crossplane-first, contract-first foundation that lets two completely separate runtime platforms collaborate without ever depending on one another."
tags: [kubernetes, crossplane, architecture, kotlin]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-01.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: Two Platforms Walk Into a Namespace

## A Forced Marriage of Two Platforms

The owner of **Agility Game** builds playful, gamified workflows. The owner of **Detective Operating System** builds an investigative platform that hunts code smells like a 1940s gumshoe hunts alibis. They have never met. They do not want to share a `build.gradle.kts`. They definitely do not want to share a JAR.

And yet: their platform lead has just announced that both runtime platforms will live on the **same Kubernetes cluster**, consuming the **same domain resources**, governed by the **same foundation**.

Cue the dramatic silence.

Then someone hands both owners a copy of `INTENT.md` from the **Open Engineering Platform (OEP)** source repository, and everyone calms down. Because OEP was built, from its very first line, around exactly this problem: how do two runtime platforms collaborate without becoming each other's liability?

The answer, straight from the project's own architecture document:

> "Each layer depends only on the layer below it. Higher layers must remain loosely coupled and communicate through shared contracts."

That's it. That's the whole peace treaty. Let's unpack it.

## 🗂️ SIPOC — The Platform Coexistence Agreement

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| Open Engineering Platform (foundation) | Contracts, CRDs, schemas | Define Kotlin Multiplatform data types and Kubernetes CRDs that any runtime platform can consume | A stable, versioned vocabulary (Space, Mission, Agent, Evidence, Result) | Repository Domain — built entirely on these types |
| Repository Domain | OEP contracts + CRDs | Implement concrete domain resources (a Refactoring Space, an Analyze Repository Mission, a Code Smell Detective Agent) | Kubernetes objects that exist independently of any runtime platform | Detective Operating System and Agility Game — both consume the same domain resources |
| Detective Operating System | Repository Domain resources via the Kubernetes API | Run a Kotlin/Ktor controller that reconciles Missions and Results | Investigations, findings, Case Files | The cluster operator, and indirectly, every developer whose repository gets investigated |
| Agility Game (architecturally, same tier) | Repository Domain resources via the Kubernetes API | Whatever Agility Game wants to do with the same Space/Mission/Agent objects — OEP does not need to know or care | Game mechanics layered on top of the same domain | Its own players, fully isolated from Detective Operating System's internals |

## The Architecture, As Actually Documented

This is not a marketing diagram. This is the literal layering described in the repository's own `docs/ARCHITECTURE.md` (which itself defers to `INTENT.md` as the source of truth):

```
┌─────────────────────────────────────────────────────────────────┐
│                         APPLICATIONS                            │
│                                                                  │
│   ┌─────────────────────┐                                       │
│   │ Code Smell Detective│   ← a concrete experience, built ON   │
│   └──────────┬───────────┘     a runtime platform                │
└──────────────┼───────────────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────────────┐
│                       RUNTIME PLATFORMS                          │
│                                                                  │
│   ┌─────────────────────────┐    ┌──────────────────────────┐   │
│   │ Detective Operating     │    │ Agility Game             │   │
│   │ System                  │    │                           │   │
│   │ (THIS repo implements   │    │ (architecturally a peer, │   │
│   │  the controller for     │    │  consumes the same       │   │
│   │  this one)              │    │  domain — does not exist │   │
│   │                         │    │  as code in this repo)   │   │
│   └────────────┬─────────────┘    └──────────────┬────────────┘   │
│                │   Both consume the SAME layer below,            │
│                │   NEITHER imports the other's code              │
└────────────────┼─────────────────────────────────┼────────────────┘
                 │                                 │
┌────────────────▼─────────────────────────────────▼────────────────┐
│                      REPOSITORY DOMAIN                            │
│                                                                    │
│   Space   ·   World   ·   Mission   ·   Agent   ·   Skill          │
│   Evidence   ·   Result                                            │
│                                                                    │
│   (concrete domain resources — e.g. the "Refactoring" Space,       │
│    the "Analyze Repository" Mission — implemented as plain         │
│    Kubernetes objects in domains/repository/)                      │
└─────────────────────────────────┬──────────────────────────────────┘
                                  │
┌─────────────────────────────────▼──────────────────────────────────┐
│                  OPEN ENGINEERING PLATFORM (foundation)            │
│                                                                    │
│   Contracts (Kotlin Multiplatform @Serializable data classes)      │
│   CRDs (Kubernetes CustomResourceDefinition YAML)                  │
│   Schemas, SDKs                                                    │
└──────────────────────────────────────────────────────────────────┘

RULE (verbatim from docs/ARCHITECTURE.md):
"Each layer depends only on the layer below it.
 Higher layers must remain loosely coupled and
 communicate through shared contracts."
```

Notice what is missing from this diagram: an arrow from Detective Operating System to Agility Game, or vice versa. There isn't one. There never will be one. They are **siblings**, not **dependencies**.

## What This Repository Actually Contains

Before anyone gets too excited about Agility Game, a clarifying note pulled straight from the filesystem: this repository implements the MVP for **one** runtime platform — the Detective Operating System — plus the entire OEP foundation and Repository Domain underneath it. Agility Game is architecturally documented as a peer runtime platform, but it doesn't ship as code in this repo. That's fine — it's not supposed to. The whole point of OEP is that Agility Game's owner could start an entirely separate repository tomorrow and build against the exact same `Space`/`Mission`/`Agent` contracts without asking Detective Operating System's owner for permission, a code review, or a shared Gradle module.

```
$ find . -maxdepth 1 -type d
./controllers        ← detective-operating-system/ subfolder exists but is
                        currently just a placeholder (.gitkeep)
./contracts          ← the real shared vocabulary (Episode 2)
./crds                ← the Kubernetes-native version of that vocabulary
./compositions        ← Crossplane composite resources (Episode 4)
./controller          ← the ACTUAL Kotlin/Ktor controller code (Episode 5)
./domains              ← concrete Repository Domain resources
./services             ← the Python God Object Detector (Episode 6)
./deploy               ← Kubernetes manifests for MiniKube (Episode 7)
```

**WARRICK (if this were a CSI crossover, which it isn't, but bear with the metaphor for one line):** "The evidence is consistent. Detective Operating System's controller lives in `controller/`. Agility Game lives nowhere in this repo, because it doesn't need to. That's not a missing feature — that's the architecture working exactly as designed."

## The MVP Promise, Word for Word

The repository's own README states the goal in plain, almost defiantly modest language:

> "A user applies: Mission: Analyze Repository — inside: Space: Refactoring — The system produces: Result: Case File — with state transitions: Pending → Running → Completed — running on: MiniKube"

That's the entire MVP success criterion. One Mission. One Space. One Result. No cloud infrastructure, no service mesh, no Temporal, no ArgoCD — the `docs/ARCHITECTURE.md` file explicitly rules those out for the MVP. Just MiniKube, Crossplane, and Kubernetes, running on (per `INTENT.md`) "a local Mac Mini M4 Pro development environment."

If Agility Game's owner wanted to build their own MVP tomorrow — a "Play Minigame" Mission inside a "Tutorial" Space producing a "High Score" Result — they could, using the exact same `Mission` and `Space` CRDs already installed in the cluster, without touching a single line of the Detective Operating System's Kotlin controller.

## The Four Principles That Make This Possible

Straight from `docs/ARCHITECTURE.md`:

```
1. Crossplane First
   Infrastructure and platform resources are modeled as
   Crossplane compositions and managed resources.

2. Kubernetes Native
   Every runtime artifact is a Kubernetes object
   (CRD, controller, manifest).

3. Contract First
   Contracts, CRDs, and schemas are defined BEFORE
   controllers, services, or features.

4. Documentation First
   Intent, architecture, and MVP scope are written down
   before code.

Development order is FIXED:
  Contracts → CRDs → Controllers → Services → Features

Never implement features before contracts.
Never implement controllers before CRDs.
```

This ordering is not a suggestion. It is the mechanism by which Agility Game's owner and Detective Operating System's owner avoid ever needing to ask "wait, which version of your library am I supposed to use?" — because neither of them ships a library the other one consumes. They both consume **contracts**, which are data, not code dependencies.

## Why a Shared JAR Would Have Started a War

Imagine the counterfactual: instead of contracts and CRDs, OEP shipped a single fat Kotlin JAR called `oep-everything.jar`, and both Detective Operating System and Agility Game imported it directly.

```
The Shared-JAR Timeline of Doom (hypothetical, did not happen):

Week 1:  Both platforms import oep-everything.jar v1.0.0. Happy.
Week 3:  Detective OS needs a new field on Mission. Bumps to v1.1.0.
Week 4:  Agility Game's build breaks because v1.1.0 also refactored
         a class Agility Game was using internally (not their fault,
         not Detective OS's fault — that's just what shared JARs do).
Week 5:  A Slack channel called #oep-jar-incident is created.
Week 6:  Someone proposes a "compatibility shim."
Week 7:  The compatibility shim needs its own version.
Week 8:  Detective OS's owner and Agility Game's owner have not
         spoken directly in eleven days.
```

None of that happens with OEP, because:

```
The Contracts-and-CRDs Timeline (what actually happens):

Week 1:  Both platforms read the same Mission CRD schema from the
         Kubernetes API server. Neither imports the other's code.
Week 3:  Detective OS's controller starts setting a new optional
         status field. Old clients ignore fields they don't know
         about (Kubernetes API conventions; Kotlin contracts use
         ignoreUnknownKeys = true in their serializers).
Week 4:  Agility Game's build is unaffected, because Agility Game
         was never compiled against Detective OS's code in the
         first place.
Week 5:  Nobody creates a Slack channel about it.
```

## What's Next: The Contracts Are the Treaty

In **Episode 2**, we open `contracts/` and read the actual Kotlin Multiplatform data classes — `Space`, `Mission`, `Agent`, `Evidence`, `Result` — that serve as the shared vocabulary both platform owners can build against without ever importing each other's runtime. We will see exactly how `ignoreUnknownKeys` and optional fields make this vocabulary resilient to change.

**🔗 Resources**

- **OEP source repository**: `open-engineering-platform` (the codebase this series is built on)
- **Crossplane**: [crossplane.io](https://crossplane.io)
- **Kubernetes CRDs**: [kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one cluster.*