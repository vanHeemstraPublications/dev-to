---
title: "Hello Pico Workflow 🏡 Ep.14"
series: "Hello Pico Workflow"
part: 14
organization: "the-software-s-journey"
tags: [open-engineering, pico, mosquitto, home-assistant, mqtt]
---

## Episode 14: Mosquitto and Home Assistant Inside Minikube

The Composition from last episode configures Manifold to look for `mosquitto.home-automation.svc.cluster.local` — but nothing answering that name exists yet. This episode fixes that, and gets Home Assistant running too.

First, a dedicated namespace, `home-automation`, and inside it, Mosquitto listening on its standard port, 1883. One important, deliberately scoped shortcut for this course: I'd permit anonymous MQTT inside this isolated Minikube cluster only — not something to carry into any production configuration, but reasonable for a local teaching environment with no external exposure. Once applied, the internal DNS name becomes exactly what the Composition expects:

```
mosquitto.home-automation.svc.cluster.local
```

That's the hostname Manifold will actually connect to.

Next, Home Assistant itself — and here's a distinction that tripped me up until I understood it properly: use **Home Assistant Container**, not Home Assistant OS. Home Assistant officially supports a container-based installation where you supply the orchestration environment yourself; the trade-off is that Container installations don't include HA OS's Supervisor or Add-on store. That's completely fine here, because Kubernetes *is* our supervisor:

```
Home Assistant Supervisor
        X
Kubernetes
        ✓
```

Deploy the official image:

```
ghcr.io/home-assistant/home-assistant:stable
```

as a Deployment with one replica, exposed on port 8123, backed by a PersistentVolumeClaim mounted at `/home-assistant/config` so its configuration survives pod restarts.

Confirm both are actually running:

```bash
kubectl get pods \
  -n home-automation
```

You should see:

```
home-assistant-...   Running
mosquitto-...        Running
```

Then port-forward Home Assistant's web UI to reach it from your own machine:

```bash
kubectl port-forward \
  -n home-automation \
  svc/home-assistant \
  8123:8123
```

Open `http://localhost:8123` and walk through Home Assistant's first-start setup as normal.

Once that's done, connect it to MQTT from inside the Home Assistant UI: **Settings → Devices & services → Add Integration → MQTT**, with broker `mosquitto.home-automation.svc.cluster.local` and port `1883`. Home Assistant's current MQTT integration is built specifically to support an externally managed broker like this one, and MQTT discovery — the mechanism behind Episode 7's discovery message — is enabled by default the moment this integration is configured.

At this point, Home Assistant is fully ready, and — this is worth noticing rather than treating as a gap — "Hello Pico" doesn't exist yet anywhere in the cluster. That's entirely intentional. We want Wrangler, not a manual `kubectl apply`, to be the thing that causes the Pico's existence. That's next.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Mosquitto Deployment | The `home-automation` namespace, anonymous access enabled for this local cluster only | Run an MQTT broker reachable at a stable internal DNS name | `mosquitto.home-automation.svc.cluster.local:1883` | Manifold (once it exists) and Home Assistant's MQTT integration |
| Home Assistant Container Deployment | The official `ghcr.io/home-assistant/home-assistant:stable` image, a PVC for config | Run Home Assistant with Kubernetes as its supervisor | A reachable Home Assistant instance on port 8123 | The person completing first-start setup |
| Home Assistant's MQTT integration | The Mosquitto broker's address and port | Connect Home Assistant to the MQTT bus, with discovery enabled | A Home Assistant instance ready to auto-discover any Pico that appears | The discovery message Manifold will publish once it starts |

Next stop: Wrangler enters the story properly — the tool that will finally bring Hello Pico into existence.
