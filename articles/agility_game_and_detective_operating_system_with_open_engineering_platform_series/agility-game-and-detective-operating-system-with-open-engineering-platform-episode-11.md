---
title: "Agility Game and Detective Operating System with Open Engineering Platform! Ep.11: One XR to Rule the Chain"
published: false
description: "Episode 11: MVP 1 gave us a Crossplane Composition that assembled exactly one Space. MVP 2 grows that idea up: a single Investigation XR that composes a Space, an Agent, AND a Mission together in one patch-and-transform pipeline, with the new kindRef and capabilityRefs fields patched straight through from the composite request."
tags: [crossplane, kubernetes, kotlin, architecture]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-11.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

# Agility Game and Detective Operating System with Open Engineering Platform! 🕵️🎮
## Episode 11: One XR to Rule the Chain

---

## The Composition That Grew Up

In the original series, Crossplane's job was modest and a little adorable: take an `XRefactoringSpace` request, patch four fields, and hand back exactly one `Space` object. A single piece of furniture, assembled from a single box.

MVP 2's `Investigation` Composition is the same notary public, asked to assemble an entire starter apartment in one delivery: a `Space`, an `Agent`, and a `Mission`, wired to each other automatically, with the new ontology fields from Episode 9 patched straight through from the moment the request comes in. Same Crossplane. Same patch-and-transform function. Considerably more furniture.

---

## SIPOC -- The Investigation Composition

| Suppliers | Inputs | Process | Outputs | Customers |
|---|---|---|---|---|
| A user, the OEP CLI, or Backstage (Episode 12 onward) | An Investigation XR request: name, purpose, kindRef, capabilityRefs | Crossplane's function-patch-and-transform pipeline runs three resource templates in sequence | A Space, an Agent, and a Mission, all created and cross-wired automatically | Detective Operating System's MissionReconciler, which finds a fully-formed Mission ready to reconcile, exactly as if a human had typed three separate kubectl applies |
| The composite's own status | metadata.name from each generated resource | ToCompositeFieldPath patches bubble each generated name back up | status.spaceName, status.agentName, status.missionName on the Investigation XR | Whoever submitted the request -- confirming all three pieces actually got created, by name |
| The new ontology fields (Episode 9) | spec.kindRef, spec.capabilityRefs on the Investigation request | Patched onto the generated Space's spec, same fields, same names | A Space that carries its ontology classification from day one | Any future code (a dashboard, a catalog provider) that wants to know what KIND of Space this is, without re-deriving it |

---

## The Composition, As Written

```yaml
# compositions/investigation/composition.yaml (abbreviated to the
# Space and Mission resource templates; Agent follows the same shape)

apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xinvestigation
spec:
  compositeTypeRef:
    apiVersion: compositions.oep.io/v1alpha1
    kind: Investigation
  mode: Pipeline
  pipeline:
    - step: patch-and-transform
      functionRef:
        name: function-patch-and-transform
      input:
        apiVersion: pt.fn.crossplane.io/v1beta1
        kind: Resources
        resources:

          - name: space
            base:
              apiVersion: oep.io/v1alpha1
              kind: Space
              spec:
                name: ""
                purpose: ""
            patches:
              - type: FromCompositeFieldPath
                fromFieldPath: metadata.name
                toFieldPath: metadata.name
              - type: FromCompositeFieldPath
                fromFieldPath: metadata.namespace
                toFieldPath: metadata.namespace
              - type: FromCompositeFieldPath
                fromFieldPath: spec.name
                toFieldPath: spec.name
              - type: FromCompositeFieldPath
                fromFieldPath: spec.purpose
                toFieldPath: spec.purpose
              - type: FromCompositeFieldPath
                fromFieldPath: spec.kindRef
                toFieldPath: spec.kindRef
              - type: FromCompositeFieldPath
                fromFieldPath: spec.capabilityRefs
                toFieldPath: spec.capabilityRefs
              - type: ToCompositeFieldPath
                fromFieldPath: metadata.name
                toFieldPath: status.spaceName

          - name: agent
            base:
              apiVersion: oep.io/v1alpha1
              kind: Agent
              spec:
                name: ""
                purpose: ""
                skills:
                  - Repository Reader
            patches:
              - type: FromCompositeFieldPath
                fromFieldPath: metadata.name
                toFieldPath: metadata.name
              - type: FromCompositeFieldPath
                fromFieldPath: metadata.namespace
                toFieldPath: metadata.namespace
              - type: FromCompositeFieldPath
                fromFieldPath: spec.name
                toFieldPath: spec.name
              - type: FromCompositeFieldPath
                fromFieldPath: spec.purpose
                toFieldPath: spec.purpose
              - type: ToCompositeFieldPath
                fromFieldPath: metadata.name
                toFieldPath: status.agentName

          - name: mission
            base:
              apiVersion: oep.io/v1alpha1
              kind: Mission
              spec:
                name: ""
                purpose: ""
                spaceRef: ""
                agentRef: ""
            patches:
              - type: FromCompositeFieldPath
                fromFieldPath: metadata.name
                toFieldPath: metadata.name
              - type: FromCompositeFieldPath
                fromFieldPath: metadata.namespace
                toFieldPath: metadata.namespace
              - type: FromCompositeFieldPath
                fromFieldPath: spec.name
                toFieldPath: spec.name
              - type: FromCompositeFieldPath
                fromFieldPath: spec.purpose
                toFieldPath: spec.purpose
              - type: FromCompositeFieldPath
                fromFieldPath: metadata.name
                toFieldPath: spec.spaceRef
              - type: FromCompositeFieldPath
                fromFieldPath: metadata.name
                toFieldPath: spec.agentRef
```

Stare at those last two patches on the `mission` resource template for a moment, because they're doing something quietly clever: both `spec.spaceRef` and `spec.agentRef` on the generated Mission are patched FROM the SAME `metadata.name` field -- the composite's own name. In this MVP 2 wiring, the Space, Agent, and Mission generated by one Investigation request all share the composite's name as their own name, which is precisely how the Mission's `spaceRef` and `agentRef` end up pointing at the Space and Agent that were JUST created in the same pipeline run, with no separate lookup step required.

---

## Architecture Diagram: One Request, Three Resources, Zero Manual Wiring

```
+-----------------------------------------------------------------------+
|  User / CLI / Backstage submits:                                     |
|                                                                       |
|  apiVersion: compositions.oep.io/v1alpha1                            |
|  kind: Investigation                                                  |
|  metadata:                                                            |
|    name: analyze-repository-sample                                    |
|  spec:                                                                |
|    name: Analyze Repository                                           |
|    purpose: Analyze a source repository for code smells               |
|    kindRef: refactoring                                               |
|    capabilityRefs: [investigations, reporting]                        |
+----------------------------------+------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|              CROSSPLANE: function-patch-and-transform                |
|                                                                       |
|   Template 1: Space                Template 2: Agent                  |
|   metadata.name <- composite name  metadata.name <- composite name    |
|   spec.kindRef <- composite kindRef                                    |
|   spec.capabilityRefs <- composite capabilityRefs                     |
|                                                                       |
|   Template 3: Mission                                                 |
|   spec.spaceRef <- composite metadata.name  (= the Space just made)   |
|   spec.agentRef <- composite metadata.name  (= the Agent just made)   |
|                                                                       |
|   status.spaceName, status.agentName bubble back UP to the composite  |
+----------------------------------+------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    KUBERNETES API SERVER NOW HOLDS:                  |
|                                                                       |
|   Space    analyze-repository-sample   (kindRef: refactoring)         |
|   Agent    analyze-repository-sample                                  |
|   Mission  analyze-repository-sample   (spaceRef + agentRef both ->   |
|                                          analyze-repository-sample)   |
+----------------------------------+------------------------------------+
                                   |
                                   v
              Detective Operating System's MissionReconciler
              (UNCHANGED from the original series) picks up the
              Mission and runs its Pending -> Running -> Completed
              state machine exactly as before.
```

---

## What Crossplane Did Not Have to Know

This is worth saying plainly, because it's the entire reason MVP 2 keeps insisting "Crossplane composes, controllers execute" as a load-bearing sentence rather than a slogan: the `Investigation` Composition above has zero knowledge of `MissionReconciler`, zero knowledge of `HttpDetectorClient`, zero knowledge of the Python `god-object-detector` service. It does not know what happens to a Mission AFTER it's created. Its entire job ends the moment three resources exist in the cluster with the right names pointing at each other.

```
WHAT CROSSPLANE'S INVESTIGATION COMPOSITION DOES:
  - Read an Investigation XR request
  - Generate a Space, an Agent, a Mission
  - Wire their references together
  - Patch ontology fields through
  - Report back what got created

WHAT CROSSPLANE'S INVESTIGATION COMPOSITION DOES NOT DO:
  - Reconcile the Mission's phase
  - Call the detector service
  - Know that Detective Operating System exists at all
  - Know that Agility Game exists at all

  Composition assembles the furniture. It does not live in the house.
```

A hypothetical Agility Game-flavored Composition -- say, an `XOnboardingLevel` that assembles a Space, a different kind of Agent, and a Mission tagged `kindRef: onboarding` -- would use the EXACT SAME Crossplane installation, the EXACT SAME `function-patch-and-transform` function, on the EXACT SAME cluster, sitting right next to this one, never once colliding with it.

---

## The Conversation, Resumed

OWNER OF AGILITY GAME: "So if I wanted a 'Create Onboarding Level' composition, I'd write my own XRD and Composition YAML, install it alongside yours, and Crossplane just... runs both, forever, without either of us touching the other's pipeline?"

OWNER OF DETECTIVE OPERATING SYSTEM: "Correct, with one small caveat worth being honest about: Compositions are matched by `compositeTypeRef`, so as long as your XRD declares a DIFFERENT composite kind than mine -- `XOnboardingLevel` instead of `Investigation` -- there's no possibility of Crossplane getting confused about which pipeline handles which request. You're not patching my Mission template. You're submitting a request to an entirely different template that happens to live in the same cluster."

OWNER OF AGILITY GAME: "And if I wanted MY Mission to ALSO carry a kindRef and capabilityRefs, the way yours does now?"

OWNER OF DETECTIVE OPERATING SYSTEM: "Those fields are already sitting on the shared Mission contract from Episode 9, optional, doing nothing unless you patch them. You'd add three lines to your own Composition's patch list. I wouldn't even need to know you did it."

---

## What's Next: Go Figure -- The OEP CLI

The Investigation Composition is powerful, but it still expects someone to hand it a properly-shaped YAML request. In Episode 12, we meet the tool built specifically so nobody has to hand-craft that YAML by hand ever again: the OEP CLI -- written, notably, in Go rather than Kotlin -- and the four real commands it ships.

---

**Resources**
- OEP source repository: the MVP 2 codebase this episode is built from
- Crossplane Compositions (Pipeline mode): docs.crossplane.io/latest/concepts/compositions
- function-patch-and-transform: github.com/crossplane-contrib/function-patch-and-transform

---

*Agility Game and Detective Operating System with Open Engineering Platform -- two platforms, zero shared dependencies, one ontology underneath them both.*
