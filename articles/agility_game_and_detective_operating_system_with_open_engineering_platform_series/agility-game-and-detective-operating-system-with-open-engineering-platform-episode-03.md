---
title: "Agility Game and Detective Operating System with Open Engineering Platform 🕵️🎮 Ep.3"
published: false
description: "Episode 3: Kotlin contracts are nice, but Kotlin contracts require Kotlin. Kubernetes CustomResourceDefinitions require nothing but the Kubernetes API. This episode walks through the actual CRD YAML for Space, Mission, Agent, Evidence, and Result, and explains why a CRD is an even stronger decoupling boundary than the typed contracts that inspired it."
tags: [kubernetes, crds, kotlin, architecture]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-03.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 3
---

## Episode 3: CRDs — Papering the Cluster

## "What If I Don't Even Like Kotlin?"

That, paraphrased politely, is the actual question the owner of Agility Game asked after Episode 2. Fair question. Maybe Agility Game's runtime is written in C# for Unity. Maybe it's TypeScript for a web client. Maybe, in some parallel and slightly cursed universe, it's COBOL.

It does not matter. Because the *real* contract — the one that actually governs the cluster — was never the Kotlin data class. It was always the Kubernetes **CustomResourceDefinition (CRD)**. The Kotlin contracts from Episode 2 are a typed, compile-time-checked *mirror* of the CRD schema, convenient for anyone writing Kotlin. The CRD itself is the actual law of the land, enforced by the Kubernetes API server, readable and writable by `kubectl`, `curl`, or a Unity C# HTTP client that has never heard of `kotlinx.serialization` in its life.

## 🗂️ SIPOC — The CRD Layer

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| OEP foundation team | The same domain vocabulary as the Kotlin contracts | Author CustomResourceDefinition YAML with an openAPIV3Schema | Five installed CRDs (spaces.oep.io, missions.oep.io, agents.oep.io, evidences.oep.io, results.oep.io) | The Kubernetes API server — which now understands these as native object kinds |
| Kubernetes API server | The installed CRDs | Validate, store, and serve Space/Mission/Agent/Evidence/Result objects exactly like built-in kinds (Pod, Deployment, etc.) | A queryable, watchable, kubectl-able API surface | Detective Operating System's controller, Agility Game's hypothetical controller, kubectl, any HTTP client with cluster credentials |
| additionalPrinterColumns | Selected schema fields (Purpose, Phase, Age) | Render those fields automatically in kubectl get output | Human-friendly kubectl get missions tables | Whoever is debugging at 2am, regardless of which platform they work for |

## The Mission CRD, Verbatim From the Repository

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: missions.oep.io
spec:
  group: oep.io
  scope: Namespaced
  names:
    kind: Mission
    listKind: MissionList
    plural: missions
    singular: mission
    shortNames:
      - mi
  versions:
    - name: v1alpha1
      served: true
      storage: true
      subresources:
        status: {}
      additionalPrinterColumns:
        - name: Purpose
          type: string
          jsonPath: .spec.purpose
        - name: Phase
          type: string
          jsonPath: .status.phase
        - name: Age
          type: date
          jsonPath: .metadata.creationTimestamp
      schema:
        openAPIV3Schema:
          type: object
          required:
            - spec
          properties:
            spec:
              type: object
              required:
                - name
                - purpose
                - spaceRef
                - agentRef
              properties:
                name:
                  type: string
                  description: Human display name for the Mission.
                purpose:
                  type: string
                  description: One-line description of the Mission.
                spaceRef:
                  type: string
                  description: Name of the Space resource this Mission belongs to.
                agentRef:
                  type: string
                  description: Name of the Agent resource assigned to execute this Mission.
            status:
              type: object
              properties:
                phase:
                  type: string
                  enum:
                    - Pending
                    - Running
                    - Completed
                    - Failed
                startedAt:
                  type: string
                  format: date-time
                completedAt:
                  type: string
                  format: date-time
                message:
                  type: string
```

Compare this `enum: [Pending, Running, Completed, Failed]` to the Kotlin `MissionPhase` enum from Episode 2. They describe the same four states from two completely independent technology stacks. If Agility Game's owner ships a Unity client tomorrow that has never imported a Kotlin compiler, they can still validate against this exact same `enum` constraint, because the Kubernetes API server enforces it server-side, not client-side.

## The Other Four CRDs, At a Glance

```
spaces.oep.io       → kind: Space      → spec: { name, purpose }
missions.oep.io     → kind: Mission    → spec: { name, purpose, spaceRef, agentRef }
agents.oep.io       → kind: Agent      → spec: { name, purpose, skills[] }
evidences.oep.io    → kind: Evidence   → spec: { name, purpose, type, source: {repo, path}, data }
results.oep.io      → kind: Result     → spec: { name, purpose, missionRef, kind, findings[] }

All five:
  group: oep.io
  versions: v1alpha1 (served: true, storage: true)
  scope: Namespaced
  subresources: status: {}     ← separate /status endpoint, RBAC-isolatable
```

That `subresources: status: {}` line matters more than its brevity suggests. It splits each object into two independently writable halves: `spec` (what the user wants) and `status` (what the controller observed). This is the same convention every native Kubernetes resource uses (a Deployment's `spec.replicas` versus its `status.availableReplicas`), and it is precisely what lets RBAC rules grant Detective Operating System's controller permission to *write status* on a Mission while denying it permission to *write spec* — a much narrower blast radius than "give the controller full write access to everything."

## Architecture Diagram: The CRD as the Actual Boundary

```
        ┌─────────────────────┐         ┌──────────────────────────┐
        │ Detective Operating │         │   Agility Game            │
        │       System         │         │  (any language, any      │
        │  (Kotlin / fabric8   │         │   client capable of       │
        │   Kubernetes client) │         │   speaking HTTPS + JSON) │
        └──────────┬────────────┘         └────────────┬──────────────┘
                   │ kubectl-equivalent calls           │ kubectl-equivalent calls
                   │ via fabric8 KubernetesClient        │ via literally anything
                   ▼                                    ▼
        ┌──────────────────────────────────────────────────────────────┐
        │              KUBERNETES API SERVER                          │
        │                                                              │
        │   Knows about Mission/Space/Agent/Evidence/Result because    │
        │   the CRDs in crds/*.yaml were applied with `kubectl apply`  │
        │                                                              │
        │   Validates spec shape, enum constraints, required fields    │
        │   Stores objects in etcd                                     │
        │   Serves watch streams to both controllers independently     │
        └──────────────────────────────────────────────────────────────┘

  Neither runtime platform talks to the other directly.
  Neither runtime platform even needs to know the other EXISTS.
  Both talk only to the API server, which enforces the CRD schema
  as the actual, server-side, language-agnostic contract.
```

## Installing the CRDs — One Command, Zero Drama

```bash
# From the repository root — applies all five CRDs at once
kubectl apply -f crds/space/space.yaml
kubectl apply -f crds/mission/mission.yaml
kubectl apply -f crds/agent/agent.yaml
kubectl apply -f crds/evidence/evidence.yaml
kubectl apply -f crds/result/result.yaml

# Verify they registered
kubectl get crds | grep oep.io
# agents.oep.io        2026-06-19T08:01:02Z
# evidences.oep.io     2026-06-19T08:01:02Z
# missions.oep.io      2026-06-19T08:01:03Z
# results.oep.io       2026-06-19T08:01:03Z
# spaces.oep.io        2026-06-19T08:01:01Z
```

At this point — and this is the punchline of the whole episode — **neither Detective Operating System's controller nor any future Agility Game controller has been deployed yet.** The CRDs exist on their own. The Kubernetes API server now understands `kind: Mission` the same way it understands `kind: Pod`, with zero runtime platform code running anywhere. You could `kubectl apply` a Mission right now and it would simply sit there, `status.phase` unset, patiently waiting for *somebody's* controller to notice it. That somebody does not need to be Detective Operating System. It could, architecturally, be Agility Game.

```bash
# Apply a Mission with NO controller running. It just... exists.
kubectl apply -f domains/repository/missions/analyze-repository/mission.yaml

kubectl get mission analyze-repository -n oep-domain
# NAME                 PURPOSE                                          PHASE   AGE
# analyze-repository   Analyze a source repository to surface...                5s
#
# Notice: PHASE column is empty. No controller is watching yet.
# This is not a bug. This is the proof that CRDs and controllers
# are genuinely separable layers.
```

## Why This Is a Stronger Boundary Than the Kotlin Contracts

```
COMPARISON: Kotlin Contracts vs Kubernetes CRDs as a decoupling mechanism

  Kotlin Contracts (Episode 2)              Kubernetes CRDs (this episode)
  ───────────────────────────────           ───────────────────────────────
  Require: a JVM or Kotlin/Native           Require: an HTTPS client and
  runtime to even compile against           a Kubernetes service account
                                              token. That's it.

  Enforced at: compile time, for             Enforced at: admission time,
  whoever imports the module                 by the API server, for EVERY
                                              client regardless of language

  Versioning: Gradle module version           Versioning: CRD `versions[]`
  bump, semver discipline needed              block, API server can even
                                              serve multiple versions
                                              simultaneously with conversion

  Agility Game must adopt this if:            Agility Game must adopt this
  it is written in Kotlin and wants            literally always, the moment
  type safety                                  it wants to touch a Mission,
                                               regardless of implementation
                                               language

  CONCLUSION: the CRD is the load-bearing contract. The Kotlin contracts
  module is a convenience layer ON TOP of that contract for Kotlin
  consumers. Lose the Kotlin contracts and the system still works.
  Lose the CRDs and nothing works, for anyone, in any language.
```

## What's Next: Crossplane Compositions — The Notary Public

In **Episode 4**, we go one layer up from plain CRDs into Crossplane **Compositions** — the `XRefactoringSpace` composite resource that assembles a `Space` object via a patch-and-transform pipeline. We'll see how Crossplane lets the platform team define *how* a higher-order resource gets built from primitives, without either Detective Operating System or Agility Game needing to know the assembly recipe.

**🔗 Resources**

- **Kubernetes CRDs**: [kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
- **CRD versioning and conversion**: [kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/)
- **CRD status subresources**: [kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#status-subresource](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one cluster.*