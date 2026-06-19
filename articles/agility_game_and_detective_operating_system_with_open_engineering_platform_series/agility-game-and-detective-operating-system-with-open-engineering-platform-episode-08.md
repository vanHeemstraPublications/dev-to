---
title: "Agility Game and Detective Operating System with Open Engineering Platform 🕵️🎮 Ep.8"
published: false
description: "Episode 8: The finale. Everything from contracts to CRDs to compositions to controllers to the cross-language detector boundary comes together in one real investigation: apply a Mission, watch it crawl through Pending, Running, and Completed, watch a Result follow it from Draft to Final, and read the Case File. The owner of Agility Game finally gets to ask the question they've been holding in for seven episodes."
tags: [kubernetes, kotlin, python, architecture]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-08.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 8
---

## Episode 8: Running One Real Investigation

## The Whole Series, Compressed Into One `kubectl apply`

Seven episodes built the case for loose coupling. This one runs the actual investigation and watches every layer earn its keep at once: contracts (Episode 2) defining the shapes, CRDs (Episode 3) making them real Kubernetes kinds, a Composition (Episode 4) optionally assembling one of them, `MissionReconciler` and `ResultReconciler` (Episode 5) driving the state machines, an HTTP call across a language boundary (Episode 6) doing the actual analysis, and two independent Deployments (Episode 7) making all of it run.

The MVP success criterion, stated once more, verbatim from the repository's own `README.md`:

> "A user applies: Mission: Analyze Repository — inside: Space: Refactoring — The system produces: Result: Case File — with state transitions: Pending → Running → Completed — running on: MiniKube."

Let's make that happen, on screen, with both platform owners watching.

## 🗂️ SIPOC — The End-to-End Investigation

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| A human (or CI pipeline) with kubectl access | deploy/samples/*.yaml — Space, Agent, Evidence, Mission | kubectl apply -f deploy/samples/ | Five new Kubernetes objects in oep-domain, none of them yet reconciled | oep-controller's MissionReconciler, watching the namespace |
| MissionReconciler | The new Mission's spec.spaceRef/spec.agentRef, the Evidence's spec.source | Resolve refs → transition Running → call detector.run() → transition Completed | A Mission with status.phase: Completed and a populated FindingsCache entry | ResultReconciler, watching the same namespace |
| ResultReconciler | The Result's spec.missionRef, the now-Completed Mission, the FindingsCache | Detect Mission is Completed → harvest findings → patch spec.findings → transition Final | A Result with status.phase: Final and populated spec.findings | Whoever reads the Case File — a human, a dashboard, or any future Agility Game integration |

## Step 1 — Apply the Domain Objects

```bash
kubectl apply -f deploy/samples/space.yaml
kubectl apply -f deploy/samples/agent.yaml
kubectl apply -f deploy/samples/evidence.yaml
kubectl apply -f deploy/samples/mission.yaml

# space.created
# agent.created
# evidence.created
# mission.created

kubectl get mission analyze-repository -n oep-domain
# NAME                 PURPOSE                                       PHASE   AGE
# analyze-repository   Analyze a source repository to surface...             2s
#
# PHASE is empty. The controller hasn't run a reconcile pass yet.
```

## Step 2 — Watch the Mission's State Machine

```bash
kubectl get missions -n oep-domain -w
```

```
NAME                 PURPOSE                                  PHASE     AGE
analyze-repository   Analyze a source repository to surface…             0s
analyze-repository   Analyze a source repository to surface…   Pending   1s
analyze-repository   Analyze a source repository to surface…   Running   3s
analyze-repository   Analyze a source repository to surface…   Completed 9s
```

Mapping each transition back to the exact `MissionReconciler` code from Episode 5:

```
PHASE empty -> Pending      reconcileOnce(): current.statusPhase() was null/""
                            -> transitionTo(Pending)

Pending -> Running          handlePending(): spaceRef="refactoring" resolved OK
                            agentRef="code-smell-detective" resolved OK
                            -> transitionTo(Running) { startedAt = now() }

Running -> Completed        handleRunning(): finds the SourceCode Evidence,
                            builds a DetectorRequest, calls detector.run(),
                            gets back a DetectorRun with N findings,
                            findingsCache.put(...),
                            -> transitionTo(Completed) { completedAt = now() }
```

```bash
kubectl get mission analyze-repository -n oep-domain -o yaml | tail -8
# status:
#   phase: Completed
#   startedAt: "2026-06-19T09:14:02Z"
#   completedAt: "2026-06-19T09:14:08Z"
#   message: "Detected 2 god-object candidate(s) via god-object-detector 0.1.0"
```

That `message` field is the exact string `HttpDetectorClient.run()` built in Episode 6 — proof that the HTTP round trip to the Python service actually happened, inside a real reconcile loop, against a real (if small) target repository.

## Step 3 — Watch the Result Follow Along

```bash
kubectl get results -n oep-domain -w
```

```
NAME        PHASE   AGE
case-file           0s
case-file   Draft   1s
case-file   Final   11s
```

```
PHASE empty -> Draft        ResultReconciler.reconcile(): currentPhase was null
                            -> patchStatus(Draft, publishedAt=null)

Draft -> Final              ResultReconciler.reconcile(): currentPhase==Draft,
                            looks up Mission "analyze-repository" by
                            spec.missionRef, sees status.phase==Completed,
                            calls findingsSource (backed by the SAME
                            FindingsCache that MissionReconciler wrote to),
                            patches spec.findings, transitions to Final
```

```bash
kubectl get result case-file -n oep-domain -o yaml
```

```yaml
apiVersion: oep.io/v1alpha1
kind: Result
metadata:
  name: case-file
  namespace: oep-domain
spec:
  name: Case File
  purpose: Case file produced by the Analyze Repository mission.
  missionRef: analyze-repository
  kind: CaseFile
  findings:
    - ruleId: god-object-heuristic
      severity: high
      summary: "GodObject UserManager (app/services/user_manager.py)"
      kind: GodObject
      path: app/services/user_manager.py
      className: UserManager
      score: 3.42
      rationale: "412 lines, 18 methods, 9 fields, 6 distinct imports referenced"
      metrics:
        loc: 412
        methods: 18
        fields: 9
        importsReferenced: 6
status:
  phase: Final
  publishedAt: "2026-06-19T09:14:09Z"
```

That is a complete, closed-loop Case File: a real AST-derived finding, scored by the exact formula from Episode 6 (`412/200 + 18/20 + 9/15 + 6/25 = 2.06 + 0.9 + 0.6 + 0.24 = 3.8`, comfortably `"high"`), carried across the HTTP boundary into Kotlin types, cached, harvested by an entirely separate reconciler, and published as a `Final` Result — without `MissionReconciler` and `ResultReconciler` ever calling each other's methods directly, and without either of them ever importing a line of the Python detector's code.

## The Full Sequence Diagram, One Last Time

```
Dev/CI          kubectl          K8s API                  MissionReconciler   god-object-detector   ResultReconciler
  |                |                 |                            |                    |                    |
  | apply samples  |                 |                            |                    |                    |
  |--------------->|                 |                            |                    |                    |
  |                | create x5       |                            |                    |                    |
  |                |---------------->|                            |                    |                    |
  |                |                 |  watch: Mission Pending    |                    |                    |
  |                |                 |--------------------------->|                    |                    |
  |                |                 |                            | get Space, Agent   |                    |
  |                |                 |<---------------------------| (refs OK)          |                    |
  |                |                 |  patch status=Running      |                    |                    |
  |                |                 |<---------------------------|                    |                    |
  |                |                 |                            | POST /detect       |                    |
  |                |                 |                            |------------------->|                    |
  |                |                 |                            |                    | scan_path(), score |
  |                |                 |                            |<-------------------| findings[]          |
  |                |                 |  patch status=Completed    |                    |                    |
  |                |                 |<---------------------------|                    |                    |
  |                |                 |  watch: Mission Completed  |                    |                    |
  |                |                 |--------------------------------------------------------------------->|
  |                |                 |                            |                    | read Mission status|
  |                |                 |<---------------------------------------------------------------------|
  |                |                 |  patch Result.spec.findings, status=Final                             |
  |                |                 |<---------------------------------------------------------------------|
  |  kubectl get results -w shows Final                           |                    |                    |
  |<---------------|                 |                            |                    |                    |
```

## The Conversation the Whole Series Was Building Toward

**OWNER OF AGILITY GAME:** "Okay. I've watched eight episodes of this. I have one question left. If I write my own Mission CRD usage tomorrow — say, a 'Play Tutorial Level' Mission inside an 'Onboarding' Space, producing a 'High Score' Result — do I need to ask Detective Operating System's owner for anything at all?"

**OWNER OF DETECTIVE OPERATING SYSTEM:** "You need the CRDs installed in the cluster — which are just YAML, already public, already applied. You need your own controller, written in whatever language you like, watching `missions.oep.io` the same way mine does. You do not need my Gradle file, my Docker image, my Service DNS name, or my phone number. The only thing we'd ever technically share is the Kubernetes API server itself, and it was built from day one to host exactly this kind of multi-tenant indifference."

**OWNER OF AGILITY GAME:** "And if your detector's heuristic changes?"

**OWNER OF DETECTIVE OPERATING SYSTEM:** "You'd never know, because you never called it. That's the whole point of a service boundary."

**OWNER OF AGILITY GAME:** "...I came in expecting a turf war. I'm leaving with a CRD and a higher opinion of YAML than I've ever had in my life."

## The Series, Recapped

| # | Episode | What We Proved |
| --- | --- | --- |
| 1 | Two Platforms Walk Into a Namespace | OEP's four layers, and the one-directional dependency rule that makes coexistence possible |
| 2 | The Contracts Are the Treaty | contracts/ is plain @Serializable Kotlin data, tolerant of unknown fields, with zero behaviour |
| 3 | CRDs — Papering the Cluster | The Kubernetes API server, not the Kotlin compiler, is the real enforced contract |
| 4 | Crossplane Compositions — The Notary Public | XRefactoringSpace assembles a Space via patch-and-transform, with composition entirely optional |
| 5 | The Detective's Actual Brain | MissionReconciler and ResultReconciler, real fabric8 informers, real state machines |
| 6 | Crossing the Boundary Without Touching Hands | DetectorClient to HttpDetectorClient to a Python FastAPI service, zero shared code |
| 7 | Deploying Two Strangers Into the Same Cluster | Two independent Deployments, RBAC, and Service DNS as the only coupling |
| 8 | This one — Running One Real Investigation | The whole loop, watched live: Pending to Running to Completed, Draft to Final |

Detective Operating System got its Case File. Agility Game's owner got, free of charge, an architecture they can build an entirely separate platform on top of without a single merge conflict. Nobody had to share a JAR. Nobody had to share a Docker image. They shared exactly four things: a Kubernetes API server, five CRDs, an agreed JSON shape, and, eventually, a mutual respect for `ignoreUnknownKeys = true`.

**🔗 Resources**

- **OEP source repository**: the codebase this entire series is built from
- **Kubernetes controller pattern**: [kubernetes.io/docs/concepts/architecture/controller](https://kubernetes.io/docs/concepts/architecture/controller/)
- **Crossplane**: [crossplane.io](https://crossplane.io)

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one cluster. Case closed.*