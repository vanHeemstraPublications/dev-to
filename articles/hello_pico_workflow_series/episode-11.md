---
title: "⚙️ Installing Crossplane and Its Templating Function"
series: "Hello Pico Workflow"
part: 11
organization: "the-software-s-journey"
tags: [open-engineering, pico, crossplane, kubernetes, helm]
---

## ⚙️ Installing Crossplane and Its Templating Function

Everything up to now has lived on my own machine. This episode is where Kubernetes gets a new kind of API installed into it — one that understands what a Pico is. As of 19 August 2026, Crossplane's current documentation is v2.3, and the recommended installation path is Helm:

```bash
helm repo add crossplane-stable \
  https://charts.crossplane.io/stable
helm repo update
```

Then install it:

```bash
helm upgrade --install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace
```

Wait for it to actually be ready before moving on:

```bash
kubectl wait \
  --for=condition=Available \
  deployment/crossplane \
  -n crossplane-system \
  --timeout=180s
```

And confirm:

```bash
kubectl get pods -n crossplane-system
```

Crossplane itself, though, doesn't know how to turn "here's a Pico" into "here's a ConfigMap, a Deployment, and a Service" — that translation logic needs a Composition Function. This course uses `function-go-templating`, specifically because it keeps the resulting Composition readable: it lets a Composition look like ordinary Kubernetes YAML wrapped in Go/Helm-style templates, rather than a forest of individual patch-and-transform steps. The latest surfaced release at time of writing is `v0.12.3`, from June 2026.

`platform/crossplane/function.yaml`:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-go-templating
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-go-templating:v0.12.3
```

Apply it:

```bash
kubectl apply \
  -f platform/crossplane/function.yaml
```

And wait for it to come up:

```bash
kubectl get functions
```

until you see:

```
INSTALLED=True
HEALTHY=True
```

Worth understanding *why* this function matters, rather than just installing it and moving on: Crossplane v2 Compositions are built around function pipelines — a Composition doesn't directly describe resources anymore, it describes a pipeline of functions that each transform or generate resources in sequence. `function-go-templating` is the one function in that pipeline we're relying on for this whole course, and it's the reason the Composition we write two episodes from now will look like recognizable Kubernetes YAML rather than an unfamiliar patch-transform DSL.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Crossplane Helm chart | The `crossplane-stable` repository | Install the Crossplane control plane into `crossplane-system` | A running Crossplane deployment inside Minikube | Every Crossplane resource (Functions, XRDs, Compositions) that follows |
| `function-go-templating` package | The Function custom resource in `function.yaml` | Install a templating engine as a Crossplane Composition Function | A pipeline step Compositions can call into | The Composition we'll write once the XRD (next episode) exists |
| `kubectl wait` / `kubectl get functions` | The installed Crossplane deployment and Function | Confirm both are actually healthy, not just applied | A verified, ready-to-use platform foundation | The rest of this series, which assumes both are working |

Next stop: creating the Open Engineering namespace, and defining Pico as a real, namespaced Crossplane API.
