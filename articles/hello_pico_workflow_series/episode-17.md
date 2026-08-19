---
title: "Hello Pico Workflow 💾 Ep.17"
series: "Hello Pico Workflow"
part: 17
organization: "the-software-s-journey"
tags: [open-engineering, pico, persistence, kubernetes, readiness-probes]
---

## Episode 17: Persistence and Real Readiness

Two refinements this episode, both about making the system honest rather than merely functional — because as it stands right now, there's a gap between what our Pico *claims* and what it actually guarantees.

First: persistence. Right now, the state we've been building up — `event_count`, `message`, `last_run` — lives entirely in the Manifold pod's memory. That means:

```
Pod restart
    ↓
state resets
```

Every event we've sent so far would simply vanish the moment Kubernetes rescheduled the pod for any reason. The fix is to introduce actual storage:

```
Manifold
   │
   ▼
/data/pico-state.json
   │
   ▼
PersistentVolumeClaim
```

Manifold writes its state to a file backed by a PVC rather than keeping it only in process memory. With that in place, you can genuinely test durability rather than just assume it:

```bash
kubectl delete pod ...
```

followed by:

```bash
wrangler pico get hello-pico
```

and it should still report:

```
event_count: 7
message: ...
last_run: ...
```

exactly as it stood before the pod was destroyed. This demonstrates one of the defining ideas behind the whole Pico concept, worth stating plainly: **a Pico is a long-lived reactive entity, not merely a function invocation.** A function forgets everything the instant it returns. A Pico remembers, on purpose, across restarts, because its whole reason for existing is to hold state and react to events over time.

Second refinement: readiness that actually means something. Right now, Kubernetes considers the Deployment "ready" the moment the container process starts — regardless of whether Manifold, PyO3, or the Rust core underneath it have actually finished initializing successfully. Add real probes to the Crossplane Composition's Deployment template:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8080
```

and:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
```

With these in place, Crossplane should not report:

```
READY=True
```

until the actual Manifold runtime — the whole `/health` endpoint we built back in Episode 6 — is genuinely responding. That gives us one more chain worth appreciating in full:

```
Rust loaded
 ↓
PyO3 loaded
 ↓
Manifold started
 ↓
health endpoint ready
 ↓
Kubernetes Deployment ready
 ↓
Crossplane Pico READY=True
```

So when `kubectl get picos` reports `READY=True`, that status now means something real — every layer beneath it, from the Rust core outward, has actually succeeded — rather than merely "a container process exists."

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| A PersistentVolumeClaim mounted at `/data` | Manifold's in-memory state after every transition | Write state to `/data/pico-state.json` on every change, read it back on startup | State that survives pod restarts and rescheduling | `wrangler pico get`, and any consumer expecting durable state |
| The readiness and liveness probes | Manifold's `/health` endpoint | Gate Kubernetes's own "ready" status on an actual application-level check | A `READY=True` status that reflects real application health | Crossplane, `kubectl get picos`, and anyone trusting that status |
| `kubectl delete pod` (as a deliberate test) | A running Pico with accumulated event history | Force a pod restart and observe whether state survives | Proof (or disproof) that persistence actually works | The person verifying the Pico is a genuinely long-lived entity |

Next stop: tying the whole developer experience together with the final `just` interface, and bringing an AI coding agent into the loop.
