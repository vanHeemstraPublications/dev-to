---
title: "Hello Pico Workflow 👋 Ep.1"
series: "Hello Pico Workflow"
part: 1
organization: "the-software-s-journey"
tags: [open-engineering, pico, architecture, introduction]
---

## Episode 1: Welcome to Open Engineering

I'll be honest: the first time I saw the phrase "Open Engineering runtime" I assumed I'd need to already know Rust, Kubernetes, and MQTT before I was allowed to touch any of it. I didn't, and it turns out that's exactly the point of this whole workflow. There's one small, deliberately-designed project — "Hello, Pico!" — built to be the reference vertical slice for the entire stack: just enough behavior to exercise Rust, PyO3, Python, Wrangler, Crossplane, Kubernetes, Manifold, MQTT, and Home Assistant, while staying small enough that every single stage is still understandable to someone (me) walking in cold.

The trick is that "Hello, Pico!" does more than print a string. Our first Pico carries real, if simple, runtime state:

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

It accepts a `hello` event:

```json
{
  "type": "hello",
  "name": "Willem"
}
```

and changes to:

```json
{
  "id": "hello-pico",
  "version": "0.1.0",
  "status": "ready",
  "message": "Hello, Willem! I am Pico hello-pico.",
  "event_count": 1,
  "last_run": "..."
}
```

That one state transition — small as it looks — is the thread this entire series pulls on. The transition itself lives in Rust. Python exposes the runtime and its API. Manifold hosts it. Wrangler manages its lifecycle. Crossplane creates the Kubernetes resources underneath it. MQTT publishes the Pico's state. Home Assistant shows it, and can optionally trigger another `hello` event right back. That's essentially the complete architecture, exercised by one message changing one string.

Here's the shape of it, top to bottom:

```
                    AUTHOR / OPERATOR
                          │
                          ▼
                     ┌─────────┐
                     │ Wrangler│
                     └────┬────┘
                          │ create/update Pico XR
                          ▼
                Kubernetes API / Minikube
                          │
                   ┌──────▼───────┐
                   │  Crossplane  │
                   └──────┬───────┘
                          │ Composition
              ┌───────────┼────────────┐
              ▼           ▼            ▼
          ConfigMap   Deployment    Service
                          │
                          ▼
                 ┌────────────────┐
                 │    Manifold    │
                 │ Python runtime │
                 │       │        │
                 │      PyO3      │
                 │       │        │
                 │ Rust Pico Core │
                 └───────┬────────┘
                         │
                         │ MQTT events/state
                         ▼
                    ┌──────────┐
                    │Mosquitto │
                    └────┬─────┘
                         │
                         ▼
                 ┌────────────────┐
                 │ Home Assistant │
                 │                │
                 │ Hello Pico     │
                 │ Status: Ready  │
                 │ Message: ...   │
                 │ Events: 12     │
                 │ Last Run: ...  │
                 └────────────────┘
```

Two things worth carrying forward before we lay a single file down. For this first course, one Pico equals one Manifold runtime pod — intentionally simpler than the ultimate Manifold architecture, where many Picos eventually live in a persistent actor network without `pico.yaml` or Wrangler's external model needing to change at all. And we're building on Crossplane 2.3 — the currently documented release — where v2 makes *namespaced* XRs the normal pattern, meaning a namespaced XR can compose resources in its own namespace, which fits a Pico extremely well, as we'll see once Crossplane enters the picture properly.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The Open Engineering architecture | A design goal: one small project exercising the whole stack | Define "Hello, Pico!" as the reference vertical slice | A concrete, buildable teaching example | Every newcomer to the ecosystem, including us |
| The "hello" event contract | A stateless request naming who's saying hello | Transition Pico state deterministically | Updated `message`, `event_count`, and `last_run` fields | Every layer downstream: Manifold, MQTT, Home Assistant |
| This series | The full source workflow, section by section | Walk it in order, keeping every code sample intact | A newcomer-readable path from empty repo to a working, visible Pico | You, following along |

Next stop: laying out the actual [repository](https://github.com/software-journey/pico), file by file, before we write a single line of Rust.
