---
title: "Agility Game and Detective Operating System with Open Engineering Platform! Ep.16: Two Owners, One Ontology, Zero New Excuses"
published: false
description: "Episode 16: The finale of the second wave. Every piece introduced since Episode 9 -- the ontology, the Journey contract, the Investigation Composition, the Go CLI, the honest gap in Flux's wiring, the Backstage Catalog and Scaffolder, the dashboards -- comes together in one complete run, from a Backstage click to an Outcome on a screen. The moral gets restated, now with twice as many moving parts and exactly the same number of shared dependencies: zero."
tags: [kubernetes, gitops, backstage, architecture]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-16.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

# Agility Game and Detective Operating System with Open Engineering Platform! 🕵️🎮
## Episode 16: Two Owners, One Ontology, Zero New Excuses

---

## Everything, Once, in Order

Seven episodes built the case for MVP 2 piece by piece. This finale runs the whole thing as one journey -- pun fully, finally, unapologetically intended -- and watches every layer from Episode 9 through Episode 15 earn its keep in a single pass, the same way the original series' eighth episode closed its own loop.

The success criteria, restated from `INTENT_MVP_2.md` section 15, in the order we'll actually demonstrate them: a user can create an Investigation through Backstage, the same Investigation could equally have been created through the CLI, Crossplane automatically composes resources, controllers automatically execute resources, results become available, outcomes become available, and no Kubernetes expertise was required anywhere in that sentence.

---

## SIPOC -- The Complete MVP 2 Loop

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| A user with zero kubectl experience | A filled-in Backstage Scaffolder form (Episode 14) | Render Journey YAML, open a PR, merge it, apply via --mode server today (Episode 13's honest gap) or Flux tomorrow | A Journey CR sitting in the cluster | The Investigation Composition (Episode 11) |
| The Investigation Composition | The Journey's purposeRef, kindRef, capabilityRefs | Patch-and-transform pipeline assembles Space, Agent, Mission | Three cross-wired resources, ready for a controller | MissionReconciler, completely unchanged from the original series |
| MissionReconciler + ResultReconciler (original series, untouched) | The composed Mission | The same Pending -> Running -> Completed and Draft -> Final state machines as eight episodes ago | A completed Mission, a Final Result | The dashboards (Episode 15), and the OEP CLI's status/result commands (Episode 12) |

---

## Step One: The Form, Not the YAML

```
Backstage UI --> Create OEP Investigation template (Episode 14)

  Name:            quarterly-audit
  Purpose:         improve-maintainability
  Kind:            refactoring        (picked from a REAL EntityPicker,
                                        populated by OepCatalogProvider
                                        reading live Kind CRs)
  Capabilities:    [investigations, reporting]
  Repository:      github.com?owner=open-engineering-platform&repo=source
  Open a Pull Request: yes
```

The user clicks Create. Nobody has typed `apiVersion`, `kind`, or `spec` anywhere. The form's `EntityPicker` for Kind only offered values that genuinely exist in the cluster right now, because the Catalog provider from Episode 14 kept the dropdown honest.

---

## Step Two: A Real Pull Request, Then a Merge

```
Backstage's fetch:template step renders:

repositories/journeys/quarterly-audit.yaml
---
apiVersion: oep.io/v1alpha1
kind: Journey
metadata:
  name: quarterly-audit
  namespace: oep-domain
  annotations:
    oep.io/repo-url: github.com?owner=open-engineering-platform&repo=source
spec:
  purposeRef: improve-maintainability
  kindRef: refactoring
  capabilityRefs:
    - investigations
    - reporting

publish:github:pull-request opens:
  "feat(journey): create quarterly-audit"

A human reviews it (or doesn't -- the same way any PR can be
reviewed lightly or thoroughly) and merges it to main.
```

This is, deliberately, the EXACT SAME file `oep create investigation quarterly-audit --purpose improve-maintainability --kind refactoring ...` would have produced from a terminal. The Backstage path and the CLI path from Episode 12 are not two different products. They are two different doors into the same house, just as the original series' four MCP-equivalent doors in a LATER, unrelated series all led to the same desk.

---

## Step Three: Getting It Into the Cluster, Honestly

```
Per Episode 13's honest accounting, TODAY, in this snapshot, getting
the merged YAML into the cluster still requires ONE of:

  oep run investigation quarterly-audit --mode server --wait
    (the "escape hatch" -- applies directly via client-go, works
     right now, no Flux GitRepository/Kustomization required)

  OR, once flux/sources/ and flux/kustomizations/ are populated
  in a future wave:
    Flux notices the merged commit on its own polling schedule,
    applies it automatically, no CLI invocation needed at all.

Either path produces the IDENTICAL Journey CR sitting in the cluster.
```

---

## Step Four: Crossplane Composes, Controllers Execute

```
The Investigation Composition (Episode 11) -- triggered by a paired
Investigation XR, applied alongside the Journey by the SAME --mode
server / Flux path above -- assembles:

  Space    quarterly-audit   (spec.kindRef: refactoring)
  Agent    quarterly-audit
  Mission  quarterly-audit   (spec.spaceRef + spec.agentRef both
                               pointing at quarterly-audit)

MissionReconciler (UNCHANGED Kotlin code from the original series)
picks up the Mission via its SharedIndexInformer and runs:

  Pending -> Running -> Completed

exactly as it did in Episode 5 of the original series, calling the
SAME HttpDetectorClient, talking to the SAME Python god-object-detector
service over the SAME Service DNS boundary.
```

This is the moment worth pausing on longest: the controller that does the ACTUAL investigative work has not changed in any of these eight new episodes. MVP 2 did not rewrite `MissionReconciler`. It built an entire ontology, a CLI, a GitOps bootstrap, and a developer portal AROUND it, leaving the proven reconciliation logic from the first series completely untouched. That is what "shift left" is supposed to mean when it's done honestly: the hard runtime logic doesn't move. The FRONT DOOR to it gets easier to find.

---

## Step Five: Results, Outcomes, and a Dashboard That Tells the Truth

```
ResultReconciler (also UNCHANGED) drives the paired Result from
Draft to Final, exactly as in the original series.

An Outcome CR, referencing that Result via spec.resultRef, surfaces:

  Title:          Improve Maintainability
  Benefits:       [Reduced Technical Debt, Improved Code Quality]
  Evidence:       [UserManager.py, AccountManager.py]
  Recommendation: Refactor Identified Classes

Checking on it, three different ways, all agreeing:

  oep status investigation quarterly-audit --output json
    {"journey":"quarterly-audit","status":"Completed",
     "results":[{"ruleId":"god-object-heuristic","severity":"high"}],
     "outcomes":[{"title":"Improve Maintainability"}]}

  oep result quarterly-audit
    [ ...the raw findings array... ]

  Backstage OutcomesPage (Episode 15)
    A table row: Title "Improve Maintainability", Phase "Final",
    a link to the Result.
```

Three different surfaces. Three different audiences -- a script piping JSON into `jq`, an engineer archiving a findings array, a non-technical stakeholder glancing at a dashboard. One underlying truth, read independently by all three, because all three are reading the SAME CRD-validated objects from the SAME Kubernetes API.

---

## Architecture Diagram: The Whole Loop, One Picture

```
+-----------------------------------------------------------------------+
|  User (zero kubectl knowledge required)                              |
+----------------------------------+------------------------------------+
                                   |
              +--------------------+--------------------+
              v                                          v
  +-------------------------+                +-------------------------+
  |  Backstage Scaffolder    |                |  OEP CLI                |
  |  (Episode 14)             |                |  (Episode 12)            |
  +-------------+-------------+                +-------------+-----------+
                |                                            |
                +---------------------+----------------------+
                                      v
                    repositories/journeys/<name>.yaml
                    committed and pushed to Git (Episode 13)
                                      |
                +---------------------+----------------------+
                v                                            v
  +-------------------------+                +-------------------------+
  | --mode server            |                | Flux (next wave,         |
  | (works today)            |                |  honestly gapped today)  |
  +-------------+-------------+                +-------------+-----------+
                +---------------------+----------------------+
                                      v
                    Journey + Investigation XR applied to cluster
                                      |
                                      v
              Crossplane: Investigation Composition (Episode 11)
                    composes Space + Agent + Mission
                                      |
                                      v
              MissionReconciler + ResultReconciler
              (ORIGINAL SERIES, completely unchanged)
                    Pending -> Running -> Completed
                    Draft -> Final
                                      |
              +-----------------------+-----------------------+
              v                       v                       v
        oep status              oep result              Backstage
        --output json            --format findings        Dashboards
        (Episode 12)             (Episode 12)              (Episode 15)

  Detective Operating System's controller never changed.
  Agility Game still doesn't exist as code in this repo.
  Neither owner imported a single line of the other's work.
```

---

## The Conversation, One Last Time

OWNER OF AGILITY GAME: "So after eight more episodes, sixteen total, the actual technical relationship between my platform and yours is... still nothing? Still zero shared code?"

OWNER OF DETECTIVE OPERATING SYSTEM: "Still zero. What changed is how MANY doors lead to that zero-coupling architecture. In the first series, you needed kubectl and a willingness to hand-write YAML. Now you've got a CLI with sensible flags, a Backstage form with a real EntityPicker, a Catalog that updates itself, and a dashboard that won't crash the moment a field is missing. The ontology didn't make us more dependent on each other. It made the INDEPENDENCE easier for someone who isn't us to actually use."

OWNER OF AGILITY GAME: "And the empty Flux folder?"

OWNER OF DETECTIVE OPERATING SYSTEM: "Still empty, still honestly disclosed, still scaffolded and ready for whoever picks it up next. Some habits are worth keeping across both waves of a platform's life: ship what's real, label what's planned, and never let a roadmap document quietly become a lie by omission."

OWNER OF AGILITY GAME: "I came back for this finale expecting a turf war over who gets the Backstage homepage. I'm leaving with an EntityPicker, a Catalog provider I can register my own resources with for free, and a renewed appreciation for a well-placed code comment that cites a section number."

---

## The Second Wave, Recapped

| # | Episode | What We Proved |
|---|---|---|
| 9 | The Ontology Moves In | Seven new contracts, two additively-extended ones, zero breakage |
| 10 | Journey, the Word Both Owners Finally Agree On | The Journey contract, its five-stage machine, the CRD/Kotlin cross-validation test |
| 11 | One XR to Rule the Chain | The Investigation Composition assembling Space+Agent+Mission in one pipeline |
| 12 | Go Figure -- The OEP CLI | A deliberately different language, four real commands, the exact INTENT_MVP_2 section 9 JSON shape |
| 13 | GitOps Is Not a Vibe, It's a Function Call | An honest accounting of what Flux automates today versus what's scaffolded for tomorrow |
| 14 | Backstage Learns to Read Minds (and Clusters) | A live Catalog provider, a Scaffolder template that opens real GitHub PRs |
| 15 | Watching Two Strangers' Journeys Without Reading Their Diaries | Dashboard types that mirror raw JSON, never overpromise structure |
| 16 | This one -- Two Owners, One Ontology, Zero New Excuses | The full loop, Backstage to Outcome, with the original controllers untouched |

Detective Operating System still got its Case File. Agility Game's owner still didn't have to write a single line of Kotlin to benefit from any of it. What's different, eight episodes later, is that getting from "I have an idea" to "here is my Outcome" no longer requires either of them to remember what a CustomResourceDefinition even is -- unless, like both of these two, they happen to enjoy reading the YAML anyway.

---

**Resources**
- OEP source repository: the MVP 2 codebase this entire wave is built from
- INTENT_MVP_2.md: the planning document this series follows section by section
- The original eight-episode series: Agility Game and Detective Operating System with Open Engineering Platform, Episodes 1-8

---

*Agility Game and Detective Operating System with Open Engineering Platform -- two platforms, zero shared dependencies, one ontology underneath them both. Case file, volume two, closed.*
