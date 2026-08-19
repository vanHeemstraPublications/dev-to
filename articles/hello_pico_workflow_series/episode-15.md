---
title: "🐴 Gate 5: Wrangler Brings the Pico to Life"
series: "Hello Pico Workflow"
part: 15
organization: "the-software-s-journey"
tags: [open-engineering, pico, wrangler, crossplane, gate5]
---

## 🐴 Gate 5: Wrangler Brings the Pico to Life

Every previous episode built a piece of scaffolding. This one is where those pieces finally connect into a running system — and it starts with understanding *why* Wrangler exists at all, rather than just using `kubectl` for everything.

```
kubectl
    generic Kubernetes tool
Wrangler
    Pico lifecycle tool
```

`kubectl` knows about Kubernetes resources. Wrangler knows about *Picos* — their lifecycle, their validation, their conventions. It should ultimately support commands like:

```bash
wrangler pico create definitions/pico.yaml
wrangler pico get hello-pico
wrangler pico describe hello-pico
wrangler pico event hello-pico hello --name Willem
wrangler pico delete hello-pico
```

For this MVP, Wrangler can use the Kubernetes Python client underneath the hood — but that's an implementation detail learners should never actually need to know. Wrangler owns Pico lifecycle, Pico validation, Pico conventions, Pico deployment, Pico inspection, and Pico events, full stop; `kubectl` stays available underneath for anyone who wants to look directly at the Kubernetes objects, but it's not the primary interface.

Now, the moment this whole series has been building toward:

```bash
wrangler pico create \
  definitions/pico.yaml
```

Underneath, this creates the actual `Pico` custom resource:

```yaml
apiVersion: pico.open-engineering.io/v1alpha1
kind: Pico
metadata:
  name: hello-pico
  namespace: open-engineering
...
```

Crossplane sees it immediately, and the entire chain we've spent this whole series building fires in sequence:

```
Wrangler
   ↓
Pico XR
   ↓
Crossplane
   ↓
Composition
   ↓
ConfigMap
Deployment
Service
   ↓
Manifold starts
   ↓
PyO3 loads
   ↓
Rust Pico created
```

Watch Crossplane reconcile it:

```bash
kubectl get picos \
  -n open-engineering
```

Eventually:

```
NAME         SYNCED   READY
hello-pico   True     True
```

Then check what actually got created:

```bash
kubectl get all \
  -n open-engineering
```

You should see `deployment/hello-pico`, a corresponding pod, and `service/hello-pico`. And:

```bash
kubectl describe pico \
  hello-pico \
  -n open-engineering
```

should show Crossplane reporting the composed resources directly.

Finally, verify Manifold itself is actually alive and correct, port-forwarded straight to your own machine:

```bash
kubectl port-forward \
  -n open-engineering \
  svc/hello-pico \
  8080:8080
```

```bash
curl http://localhost:8080/health
```

```json
{
  "status": "ok"
}
```

```bash
curl http://localhost:8080/state
```

```json
{
  "id": "hello-pico",
  "version": "0.1.0",
  "status": "ready",
  "message": "Hello, Pico!",
  "event_count": 0,
  "last_run": null
}
```

That's **Gate 5**: Rust → PyO3 → Python → OCI → Crossplane → Kubernetes → Manifold, all working together, end to end, triggered by one command against one YAML file.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Wrangler | `definitions/pico.yaml` from Episode 3 | Create the corresponding `Pico` custom resource in the cluster | A `Pico` XR that Crossplane can see and reconcile | Crossplane's reconciliation loop |
| Crossplane + the Composition (Episode 13) | The newly created `Pico` XR | Generate the ConfigMap, Deployment, and Service | A running Manifold pod, correctly configured | Kubernetes's scheduler, and the pod itself |
| `curl` against the port-forwarded service | `/health` and `/state` requests | Confirm Manifold, PyO3, and the Rust core are all actually alive and correct | Gate 5: a fully verified end-to-end stack | The next episode, where Home Assistant discovers this Pico automatically |

Next stop: watching Home Assistant discover this Pico entirely on its own, with no manual sensor configuration at all.
