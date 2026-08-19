---
title: "🗂️ Laying Out the Repository"
series: "Hello Pico Workflow"
part: 2
organization: "the-software-s-journey"
tags: [open-engineering, pico, project-structure, repository]
---

## 🗂️ Laying Out the Repository

Before writing anything clever, I wanted the whole shape of the project sitting in front of me — every folder, every file, so nothing later feels like it appeared from nowhere. Here's the full `hello-pico/` [repository](https://github.com/software-journey/pico) layout this series builds toward, piece by piece:

```
hello-pico/
├── Cargo.toml
├── Cargo.lock
├── pyproject.toml
├── uv.lock
├── rust-toolchain.toml
├── Justfile
├── Dockerfile
│
├── crates/
│   ├── pico-core/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   │
│   └── pico-native/
│       ├── Cargo.toml
│       └── src/lib.rs
│
├── python/
│   ├── manifold/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── mqtt.py
│   │   └── settings.py
│   │
│   └── wrangler/
│       ├── __init__.py
│       └── cli.py
│
├── definitions/
│   └── pico.yaml
│
├── tests/
│   ├── test_native.py
│   ├── test_manifold.py
│   └── test_integration.py
│
├── platform/
│   ├── crossplane/
│   │   ├── function.yaml
│   │   ├── rbac.yaml
│   │   ├── xrd.yaml
│   │   └── composition.yaml
│   │
│   ├── home-assistant/
│   │   ├── namespace.yaml
│   │   ├── mosquitto.yaml
│   │   └── home-assistant.yaml
│   │
│   └── namespace.yaml
│
└── scripts/
    └── smoke-test.sh
```

Even without opening a single file, this layout already tells a newcomer like me most of the story. `crates/pico-core` and `crates/pico-native` are two separate Rust crates — one holding the actual state-machine logic, one holding only the thin PyO3 boundary around it, which is a distinction we'll see pay off directly in a couple of episodes. `python/manifold` is the runtime host; `python/wrangler` is the lifecycle CLI — two very different jobs, deliberately kept in two different packages. `definitions/pico.yaml` is the one file that describes *what* a Pico is, independent of *how* it runs — the next episode is entirely about that file. `platform/` holds everything Kubernetes-facing: the Crossplane function, RBAC, XRD, and Composition that turn a Pico definition into real running resources, plus the Home Assistant and Mosquitto manifests that make the Pico visible to a human. And `tests/` splits cleanly into native (Rust-via-Python), Manifold (the API layer), and integration (the whole stack together) — a split that mirrors the gates this workflow checks off one at a time.

Nothing here is exotic. It's the layout of a project that expects to grow into several distinct concerns — a state engine, a runtime host, a declarative definition, a platform layer, and a lifecycle tool — without any of them accidentally reaching into each other's business. We'll fill every one of these files in, in order, over the episodes ahead.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Project author | A decision to separate Rust core, PyO3 boundary, Python runtime, definitions, and platform manifests | Lay out the `hello-pico/` directory structure | A scaffolded, empty-but-organized repository | Every episode that follows, filling in one piece at a time |
| `crates/` (pico-core, pico-native) | The intended split between state logic and Python bindings | Reserve separate crates for each concern | Two independently testable Rust crates | Gate 1 (pico-core) and Gate 2 (pico-native) |
| `platform/` | The intended split between Crossplane, Home Assistant, and namespace concerns | Reserve separate manifest groups for each | An organized platform layer, applied incrementally | Later episodes installing Crossplane, Mosquitto, and Home Assistant |

Next stop: `definitions/pico.yaml` — the one file that says what a Pico *is*, without saying a word about how it runs.
