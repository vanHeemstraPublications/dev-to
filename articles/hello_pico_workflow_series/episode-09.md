---
title: "🎡 Gate 3: Building the Wheel"
series: "Hello Pico Workflow"
part: 9
organization: "the-software-s-journey"
tags: [open-engineering, pico, maturin, wheel, packaging]
---

## 🎡 Gate 3: Building the Wheel

Everything so far has run in development mode — `maturin develop`, installing the native extension straight into an active virtualenv for fast iteration. That's great for writing code, and completely inadequate for proving the thing you'll actually ship works. This episode is about leaving development mode and building the real artifact.

```bash
maturin build --release
```

That produces something roughly like:

```
target/wheels/
└── hello_pico-0.1.0-...whl
```

Here's the part I initially wanted to skip, and shouldn't have: test the *artifact*, not the source tree you already know works. A fresh virtualenv, installing only the built wheel, with none of the development-mode shortcuts in play:

```bash
uv venv /tmp/hello-pico-test
source /tmp/hello-pico-test/bin/activate
pip install target/wheels/*.whl
python - <<'PY'
from pico_native import HelloPico
p = HelloPico("hello-pico", "0.1.0")
print(p.hello("Wheel"))
PY
```

If that prints a sensible greeting, that's **Gate 3**: proof that the packaged artifact — the thing that will actually get installed inside a container a few episodes from now — behaves identically to the development-mode version we've been testing against all along. It's a small, cheap check, and it catches a real class of mistake: code that works when `maturin develop` links things together on your machine, but subtly breaks once it's a standalone wheel installed somewhere else, with none of your local development environment's assumptions still holding true.

This is also a good moment to notice the pattern forming across this series. Each gate checks one boundary crossing in isolation, before the next one gets added on top: Gate 1 was "does the Rust logic work, alone." Gate 2 was "can Python drive that logic correctly." Gate 3 is "does the *packaged* version of that Python-callable logic still work, outside the development environment that built it." Every gate that follows keeps building on this same habit — never trust the next layer until the layer beneath it has been checked on its own terms.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `maturin build --release` | The `pico-native` crate, compiled with full optimizations | Produce a distributable wheel file | `target/wheels/hello_pico-0.1.0-...whl` | The isolated test environment, and eventually the Docker build |
| A fresh, isolated virtualenv | The built wheel, installed with `pip install`, none of the dev environment | Run the exact same smoke test used in Episode 5, against the packaged artifact | Confirmation the wheel behaves identically outside the dev environment | Gate 3's pass/fail signal |
| Gate 3 itself | A successful import and `hello()` call from the isolated environment | Certify the artifact is ready to be containerized | Confidence to proceed to Linux/Docker packaging | The next episode, building the actual container image |

Next stop: Gate 4 — building this same wheel for Linux, inside Docker, since our development machine almost certainly isn't running the same architecture as the eventual Kubernetes cluster.
