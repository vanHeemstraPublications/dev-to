---
title: "Agility Game and Detective Operating System with Open Engineering Platform 🕵️🎮 Ep.4"
published: false
description: "Episode 4: Both platform owners want a Space, but neither wants to know how a Space gets assembled from primitives. Crossplane Compositions are OEP's notary public — they take a simple request (XRefactoringSpace) and stamp out the underlying Space resource through a documented patch-and-transform pipeline, leaving both runtime platforms blissfully uninvolved in the assembly logic."
tags: [crossplane, kubernetes, kotlin, architecture]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-04.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 4
---

## Episode 4: Crossplane Compositions — The Notary Public

## Someone Has to Assemble the Furniture

CRDs (Episode 3) tell the API server what shape a `Space` is allowed to take. They do not tell anyone *how* a Space gets built from smaller pieces, what defaults to apply, or what status fields to bubble back up. For a resource as simple as `Space` — just a `name` and a `purpose` — that hardly matters. But OEP's own four architectural principles include "Crossplane First," and the repository genuinely uses Crossplane **Compositions** to assemble higher-order resources from primitives, even when the primitive in question is delightfully small.

This matters to our two platform owners for a specific reason: neither of them has to write or even read the assembly logic. Crossplane is the notary public who stamps the paperwork. They just submit a request and get a finished, validated `Space` back.

## 🗂️ SIPOC — Crossplane Compositions

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| Platform team | A CompositeResourceDefinition (XRD) describing the public-facing schema | Define XRefactoringSpace as the user-facing composite type | A new, installable API kind: XRefactoringSpace | Whoever wants a Space, without caring how it's built |
| Crossplane function-patch-and-transform | The Composition pipeline definition | Take fields from the composite (spec.name, spec.purpose) and patch them onto a generated Space resource | A concrete Space object, fully populated | The Kubernetes API server — which now has a real Space to serve to controllers |
| The generated Space | The patched fields | Standard OEP Space CRD validation (Episode 3) applies as normal | A validated, namespaced Space resource | Detective Operating System's controller — and, again, anyone else who simply asks the API server for it |

## The Composition, As Written

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xrefactoringspace
spec:
  compositeTypeRef:
    apiVersion: compositions.oep.io/v1alpha1
    kind: XRefactoringSpace
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
              - type: ToCompositeFieldPath
                fromFieldPath: metadata.name
                toFieldPath: status.spaceName
```

Read the patches as a small contract of their own: four fields flow **down** from the composite request into the generated `Space` (`metadata.name`, `metadata.namespace`, `spec.name`, `spec.purpose`), and one field flows **back up** from the generated `Space` into the composite's own status (`status.spaceName`). That single `ToCompositeFieldPath` patch is how the caller finds out "yes, your Space was actually created, and here's its name" without ever reading the underlying `Space` object directly.

## The XRD: The Public Face of the Composition

```yaml
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xrefactoringspaces.compositions.oep.io
spec:
  scope: Namespaced
  group: compositions.oep.io
  names:
    kind: XRefactoringSpace
    listKind: XRefactoringSpaceList
    plural: xrefactoringspaces
    singular: xrefactoringspace
  defaultCompositionRef:
    name: xrefactoringspace
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
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
              properties:
                name:
                  type: string
                  description: Human display name for the Space.
                purpose:
                  type: string
                  description: One-line description of the Space.
            status:
              type: object
              properties:
                spaceName:
                  type: string
```

Notice that `XRefactoringSpace`'s schema is almost embarrassingly similar to `Space`'s own schema (`name`, `purpose`). For the MVP that's exactly the point — Crossplane is establishing the *pattern* of composite-resource-assembles-primitive-resource, even when the primitive is this simple. The same pattern is what lets the `analyze-repository` composition (right next door in `compositions/analyze-repository/`) assemble something more interesting later without anyone changing how the pattern itself works.

## Architecture Diagram: Where Crossplane Sits

```
        ┌─────────────────────┐         ┌──────────────────────────┐
        │ Detective Operating │         │   Agility Game           │
        │       System         │         │  (could ALSO submit an   │
        │                       │         │   XRefactoringSpace if   │
        │  applies an           │         │   it wanted its own      │
        │  XRefactoringSpace     │         │   refactoring space)     │
        └──────────┬────────────┘         └────────────┬──────────────┘
                   │ kubectl apply -f my-space-request.yaml
                   ▼                                    ▼
        ┌──────────────────────────────────────────────────────────────┐
        │                  CROSSPLANE COMPOSITION ENGINE              │
        │                                                              │
        │   XRefactoringSpace (the public, user-facing request)        │
        │              │                                               │
        │              │  pipeline: function-patch-and-transform       │
        │              ▼                                               │
        │   Generates and patches a concrete Space resource             │
        │              │                                               │
        │              │  ToCompositeFieldPath patches status back up  │
        │              ▼                                               │
        │   status.spaceName populated on the XRefactoringSpace        │
        └──────────────────────────────┬───────────────────────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────┐
                        │   Space (oep.io/v1alpha1)    │
                        │   the SAME CRD from Ep.3      │
                        └─────────────────────────────┘

  Neither platform owner wrote or needs to read the patch-and-transform
  pipeline. They request a composite; Crossplane notarises the request
  into a primitive Space that both platforms already know how to read.
```

## Requesting a Space Through the Composition

```yaml
# my-refactoring-request.yaml
apiVersion: compositions.oep.io/v1alpha1
kind: XRefactoringSpace
metadata:
  name: refactoring-via-composition
  namespace: oep-domain
spec:
  name: Refactoring
  purpose: Investigations related to improving software design and maintainability.
```

```bash
kubectl apply -f my-refactoring-request.yaml

# Crossplane's pipeline runs, the underlying Space gets created
kubectl get space -n oep-domain
# NAME                          PURPOSE
# refactoring-via-composition   Investigations related to improving...

# And the composite reports it found its own creation
kubectl get xrefactoringspace refactoring-via-composition -n oep-domain -o yaml | grep -A2 status
# status:
#   spaceName: refactoring-via-composition
```

For the MVP, the repository actually ships the `Refactoring` Space the simpler way too — applied directly as a plain `Space` object in `domains/repository/spaces/refactoring/space.yaml`, no composition required. Both paths produce an identical, indistinguishable `Space` resource from Detective Operating System's controller's point of view, which is exactly the architectural point: **the composition is optional plumbing, not a mandatory dependency**. Detective Operating System's `MissionReconciler` (Episode 5) reads `Space` objects regardless of whether Crossplane, a human with `kubectl`, or Agility Game's owner's pet shell script created them.

## The Joke That Writes Itself

**OWNER OF AGILITY GAME:** "So if I submit my own `XRefactoringSpace`, does that... talk to Detective Operating System somehow? Do I need its permission?"

**OWNER OF DETECTIVE OPERATING SYSTEM:** "You need the CRDs installed and an RBAC role that lets you create `xrefactoringspaces.compositions.oep.io`. You do not need my permission. You do not need my email address. My controller will simply notice your Space exists the next time it lists Spaces, exactly the way it notices any other Space, because that's literally all a controller does — it watches the API server, not the other tenants."

**OWNER OF AGILITY GAME:** "...that's almost disappointingly simple."

**OWNER OF DETECTIVE OPERATING SYSTEM:** "Welcome to Contract First."

## What's Next: The Detective's Actual Brain

In **Episode 5**, we stop talking about YAML and finally read real, running Kotlin: the `MissionReconciler` and `ResultReconciler` classes that make Detective Operating System an actual *controller* rather than a folder of good intentions. We will watch a fabric8 `SharedIndexInformer` notice a new Mission, drive it from `Pending` to `Running` to `Completed`, and hand findings off to a `Result` reconciler that finalises a Case File. None of this code, at any point, mentions Agility Game.

**🔗 Resources**

- **Crossplane Compositions**: [docs.crossplane.io/latest/concepts/compositions](https://docs.crossplane.io/latest/concepts/compositions/)
- **function-patch-and-transform**: [github.com/crossplane-contrib/function-patch-and-transform](https://github.com/crossplane-contrib/function-patch-and-transform)
- **CompositeResourceDefinitions (XRDs)**: [docs.crossplane.io/latest/concepts/composite-resource-definitions](https://docs.crossplane.io/latest/concepts/composite-resource-definitions/)

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one cluster.*