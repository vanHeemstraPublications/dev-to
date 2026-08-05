---
title: "Figurines like Picos 🏗️ Ep.9"
series: "Figurines like Picos"
part: 9
organization: "the-software-s-journey"
tags: [crossplane, kubernetes, azure, infrastructure, pico]
---

## Episode 9: Ordering the Actual Display Case

Now, here is a confession every serious collector eventually makes: at some point, you stop caring about the individual figurines for a moment and start caring, quite intensely, about the cabinet itself. Where does it sit? How much weight can the shelf take? Who's paying for the glass? Manifold organizes what goes *inside* the cabinet beautifully, but something still has to order the cabinet in the first place — and around here, that something is Crossplane.

Everything in the last eight episodes assumes a pico engine is already running somewhere, quietly hosting your figurines. Crossplane is how I provision that "somewhere" declaratively, on Azure, the same way I'd declare anything else in a Kubernetes cluster — by writing down what I want and letting a control plane go make it true. First, a CompositeResourceDefinition — the shape of the order form itself, a custom "PicoCase" resource type any team can request:

```yaml
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xpicocases.figurines.example.org
spec:
  scope: Namespaced
  group: figurines.example.org
  names:
    kind: XPicoCase
    plural: xpicocases
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
                location:
                  type: string
                  default: westeurope
                cpu:
                  type: number
                  default: 1
                memoryGB:
                  type: number
                  default: 2
                image:
                  type: string
                  default: "picolabs/pico-engine:latest"
              required: [location, image]
```

And then the Composition — the actual instructions the display-case manufacturer follows, written in pipeline mode with a Composition Function doing the patching, exactly the way Crossplane v2 wants it done:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: picocase-azure-container-instance
spec:
  compositeTypeRef:
    apiVersion: figurines.example.org/v1alpha1
    kind: XPicoCase
  mode: Pipeline
  pipeline:
    - step: compose-container-group
      functionRef:
        name: function-patch-and-transform
      input:
        apiVersion: pt.fn.crossplane.io/v1beta1
        kind: Resources
        resources:
          - name: pico-engine-case
            base:
              apiVersion: containerinstance.azure.upbound.io/v1beta1
              kind: ContainerGroup
              spec:
                forProvider:
                  osType: Linux
                  restartPolicy: Always
                  container:
                    - name: pico-engine
                      cpu: 1
                      memory: 2
                      ports:
                        - port: 8080
                          protocol: TCP
            patches:
              - fromFieldPath: spec.location
                toFieldPath: spec.forProvider.location
              - fromFieldPath: spec.cpu
                toFieldPath: spec.forProvider.container[0].cpu
              - fromFieldPath: spec.memoryGB
                toFieldPath: spec.forProvider.container[0].memory
              - fromFieldPath: spec.image
                toFieldPath: spec.forProvider.container[0].image
```

Apply the XRD, apply the Composition, and then requesting a whole new display case for a new collection becomes exactly as satisfying as filling out a very short order form:

```yaml
apiVersion: figurines.example.org/v1alpha1
kind: XPicoCase
metadata:
  name: my-figurine-collection
  namespace: cabinets
spec:
  location: westeurope
  cpu: 2
  memoryGB: 4
  image: "picolabs/pico-engine:latest"
```

Apply that, and Crossplane's control plane reconciles a real Azure Container Instance into existence, running the pico engine image, with the exact CPU and memory you asked for — the actual glass-and-shelving cabinet, ordered the same declarative way I'd order anything else running in the cluster. Once it's up, hand its address off to Manifold's bootstrap from Episode 6, and the whole collection — tag registry, skills registry, owner, every future thing and community — takes shape inside a cabinet that Crossplane, not a person with a screwdriver, actually built.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Platform team (XRD/Composition authors) | The desired shape of a "PicoCase" and how to fulfil it on Azure | Author the CompositeResourceDefinition and pipeline-mode Composition | A reusable, requestable infrastructure type | Any team wanting to run a pico engine |
| Crossplane control plane | An applied `XPicoCase` claim | Run the Composition Function pipeline, patch and create the ContainerGroup | A real, running Azure Container Instance hosting `pico-engine` | The collection's future Manifold bootstrap |
| function-patch-and-transform | Field-path patches from the composite spec to the provider resource | Map `location`/`cpu`/`memoryGB`/`image` onto the Azure resource | A correctly-configured `ContainerGroup` manifest | The Crossplane reconciliation loop, the Azure provider |

Next stop: the whole toy chest, closed up and admired — persistence, decentralization, and why every figurine in this collection was worth unboxing in the first place.
 
