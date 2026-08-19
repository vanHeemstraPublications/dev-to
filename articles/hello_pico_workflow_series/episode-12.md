---
title: "🧬 The Open Engineering Namespace and the Pico XRD"
series: "Hello Pico Workflow"
part: 12
organization: "the-software-s-journey"
tags: [open-engineering, pico, crossplane, xrd, namespace]
---

## 🧬 The Open Engineering Namespace and the Pico XRD

Two small setup steps this episode, both foundational to everything after. First, the namespace all of this will live in, `platform/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: open-engineering
```

Apply it:

```bash
kubectl apply \
  -f platform/namespace.yaml
```

Now for the bigger piece: giving Open Engineering an actual Kubernetes API — `pico.open-engineering.io/v1alpha1`, `kind: Pico`. This is defined with a CompositeResourceDefinition (an XRD), and it's deliberately *namespaced*, not cluster-scoped. That's intentional: Crossplane v2 recommends namespaced XRs for most APIs, and a namespaced XR can compose resources within its own namespace — which fits a Pico, a thing that belongs to one team's or one project's namespace, extremely well.

`platform/crossplane/xrd.yaml`:

```yaml
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: picos.pico.open-engineering.io
spec:
  scope: Namespaced
  group: pico.open-engineering.io
  names:
    kind: Pico
    plural: picos
  defaultCompositionRef:
    name: pico-manifold
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                id:
                  type: string
                version:
                  type: string
                runtime:
                  type: object
                  properties:
                    image:
                      type: string
              required:
                - id
                - version
                - runtime
```

Read that schema against `definitions/pico.yaml` from Episode 3, and you'll notice it's deliberately minimal — it only requires `id`, `version`, and `runtime.image`. It doesn't (yet) validate `state`, `handlers`, or `channels` at the schema level; those are read and used by the Composition, but the XRD's own contract stays narrow on purpose, matching exactly what Crossplane itself needs to know to compose the underlying resources.

Apply it:

```bash
kubectl apply \
  -f platform/crossplane/xrd.yaml
```

Then verify:

```bash
kubectl get xrd
```

and wait for:

```
ESTABLISHED=True
```

Once that's true, `kind: Pico` is a genuine, first-class Kubernetes API — something you can `kubectl get`, `kubectl describe`, and `kubectl apply` exactly like a Deployment or a Service, even though nothing about "Pico" existed in Kubernetes's own vocabulary before this file was applied. That's the moment Open Engineering stops being a convention and becomes an actual API.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `platform/namespace.yaml` | A namespace name, `open-engineering` | Create the namespace via `kubectl apply` | An isolated namespace for every Pico-related resource | The XRD, the Composition, and eventually the Pico itself |
| `platform/crossplane/xrd.yaml` | A namespaced schema requiring `id`, `version`, `runtime.image` | Register `Pico` as a genuine, namespaced Kubernetes API | A working `kind: Pico` custom resource type | `kubectl`, Wrangler, and the Composition that acts on it |
| `kubectl get xrd` | The applied XRD | Confirm the API was actually established, not just accepted | An `ESTABLISHED=True` signal | The next episode, which grants RBAC and writes the Composition |

Next stop: giving Crossplane the RBAC it needs, and writing the Composition that turns a Pico into a ConfigMap, a Deployment, and a Service.
