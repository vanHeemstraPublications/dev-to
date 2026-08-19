---
title: "🤖 The Just Interface and AI Pair Programming"
series: "Hello Pico Workflow"
part: 18
organization: "the-software-s-journey"
tags: [open-engineering, pico, justfile, ai, opencode, qwen3]
---

## 🤖 The Just Interface and AI Pair Programming

By now, this repository has grown well past the three `Justfile` targets from Episode 8. This episode rounds out the full command surface, and then puts it to an interesting use.

The finished interface:

```
just setup       → install Rust/Python dependencies
just develop      → run maturin develop
just test         → run Cargo and Python tests
just check        → run all formatting/lint/tests
just build        → build the wheel
just image         → build the Linux image into Minikube
just platform      → install Crossplane, the Composition Function,
                       Home Assistant, and Mosquitto
just deploy         → equivalent to:
                       wrangler pico create definitions/pico.yaml
just smoke           → verify XR Ready, Pod Ready, /health, /state,
                       and MQTT state
just destroy         → deletes Hello Pico while retaining the platform
```

Read top to bottom, that's genuinely the whole journey this series has walked, condensed into eight words you could type from a cold start: `just setup`, `just check`, `just image`, `just platform`, `just deploy`, `just smoke` — and when you're done exploring, `just destroy` tears down only the Pico itself, leaving Crossplane, Home Assistant, and Mosquitto standing, ready for the next one.

Now — this is where the current local AI setup becomes genuinely useful rather than a novelty. In a terminal split across two panes:

```
Pane 1                    Pane 2
opencode                  just check
   │
   ▼                      kubectl ...
MLXServe                  wrangler ...
   │
   ▼
Qwen3
```

One pane runs an AI coding agent (OpenCode, backed by a local Qwen3 model via MLXServe); the other runs the actual verification commands and cluster interactions. And the instructions you hand the model can be precise, scoped, and gated on the exact same `just check` command this whole series has been building toward:

> Add persistent event counting to Hello Pico. Implement the logic in pico-core, expose only the necessary interface through pico-native, update Manifold, add tests, and run `just check`. Do not modify the Crossplane API unless necessary.

Then, later:

> Add MQTT Home Assistant discovery for Pico status, message, version, event count and last run. Run the integration tests and `just check`.

Then:

> Update the Crossplane Composition to add health probes. Render or validate the Composition and verify Hello Pico reaches `READY=True`.

Notice what each of these instructions actually is: a scoped task, a named place in the architecture where the change belongs (`pico-core`, not `pico-native`; Manifold, not the Rust core), and a deterministic gate the model can't talk its way around. The LLM is helping *implement* each lesson this series has walked through — but `just check`, `just smoke`, and the actual Kubernetes/MQTT state remain the arbiter of whether the work is actually correct. That's the real value of everything this series built up front: not that an AI agent can write the code, but that once it does, there's an unambiguous, mechanical way to know whether it's telling the truth about having finished.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The full `Justfile` | Every command from setup through destroy | Provide one consistent, memorized interface to the whole system | A repeatable, typo-resistant operator workflow | Every human or AI agent working in this repository |
| An AI coding agent (e.g. OpenCode + a local Qwen3 model) | A scoped, specific instruction naming the right architectural layer | Implement the requested change within that layer | A code change, claimed complete by the model | `just check` and `just smoke`, verifying the claim |
| `just check` / `just smoke` | The AI-authored (or human-authored) change | Run the full deterministic gate against it | An objective pass/fail signal, independent of who wrote the code | The person deciding whether to accept the change |

Next stop: the final episode — standing back and looking at the whole finished journey, start to finish, in one uninterrupted pass.
