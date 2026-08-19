---
title: "🛡️ RBAC and the Composition"
series: "Hello Pico Workflow"
part: 13
organization: "the-software-s-journey"
tags: [open-engineering, pico, crossplane, rbac, composition]
---

## 🛡️ RBAC and the Composition

Two things stand between "Pico is a real API" (last episode) and "creating a Pico actually produces running resources" (a few episodes from now): permission, and translation logic. This episode covers both.

Crossplane can create some Kubernetes resources on its own, including Deployments — but its documentation is explicit that additional resource types may need RBAC explicitly aggregated to it. Rather than grant broad, vague permissions, we grant exactly what this one Composition requires:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: open-engineering-pico-crossplane
  labels:
    rbac.crossplane.io/aggregate-to-crossplane: "true"
rules:
  - apiGroups:
      - ""
    resources:
      - configmaps
      - services
    verbs:
      - "*"
  - apiGroups:
      - apps
    resources:
      - deployments
    verbs:
      - "*"
```

Apply it:

```bash
kubectl apply \
  -f platform/crossplane/rbac.yaml
```

That `rbac.crossplane.io/aggregate-to-crossplane: "true"` label isn't decoration — Crossplane's own documentation specifically calls it out as the mechanism that actually merges this ClusterRole's rules into Crossplane's effective permissions. Skip the label, and the rules exist but never actually apply.

With permission granted, here's what the Composition does conceptually — it takes a Pico spec:

```yaml
kind: Pico
spec:
  id: hello-pico
  version: 0.1.0
  runtime:
    image: open-engineering/hello-pico:0.1.0
```

and turns it into three real resources:

```
Pico
 │
 ├── ConfigMap
 │     Pico configuration
 │
 ├── Deployment
 │     Manifold runtime
 │
 └── Service
       runtime API
```

This is genuinely where Crossplane earns its place in the architecture — Compositions exist specifically to take one composite resource and expand it into multiple real Kubernetes resources, all managed and reconciled together as a unit. The Deployment it generates uses the exact image built into Minikube back in Episode 10:

```
image: open-engineering/hello-pico:0.1.0
```

and is given environment variables the Manifold runtime reads at startup:

```
PICO_ID=hello-pico
PICO_VERSION=0.1.0
MQTT_HOST=mosquitto.home-automation.svc.cluster.local
MQTT_PORT=1883
```

with `imagePullPolicy: IfNotPresent` set explicitly — worth calling out, because the image lives inside Minikube's own image store rather than a public registry, so Kubernetes needs to be told not to go looking for it anywhere else. `platform/crossplane/composition.yaml` is where all of this — the ConfigMap, Deployment, and Service templates, wired up via `function-go-templating` from Episode 11 — actually lives, applied the same way as everything else:

```bash
kubectl apply \
  -f platform/crossplane/composition.yaml
```

We won't be able to see this Composition actually fire until Mosquitto and Home Assistant exist for it to talk to, and until Wrangler creates a real Pico — both coming up in the episodes ahead.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `platform/crossplane/rbac.yaml` | A ClusterRole scoped to exactly ConfigMaps, Services, and Deployments | Aggregate these permissions into Crossplane via the aggregation label | Crossplane granted precisely the access this Composition needs | Crossplane's reconciler, when it creates real resources |
| `platform/crossplane/composition.yaml` | A `Pico` spec (`id`, `version`, `runtime.image`) | Template a ConfigMap, Deployment, and Service via `function-go-templating` | Three concrete Kubernetes resources per Pico | Whatever Pico gets created, and the Kubernetes API itself |
| The Deployment template | The image from Gate 4, plus `PICO_ID`/`PICO_VERSION`/`MQTT_HOST`/`MQTT_PORT` env vars | Configure the Manifold container correctly for this cluster | A Deployment that starts Manifold pointed at the right MQTT broker | The Manifold runtime, once it starts running |

Next stop: installing Mosquitto and Home Assistant inside Minikube, so there's actually something on the other end of that `MQTT_HOST` value.
