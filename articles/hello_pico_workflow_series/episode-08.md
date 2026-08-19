---
title: "✅ Testing, Linting, and the Justfile"
series: "Hello Pico Workflow"
part: 8
organization: "the-software-s-journey"
tags: [open-engineering, pico, testing, justfile, ci]
---

## ✅ Testing, Linting, and the Justfile

Before we move any further into the stack, I wanted a written test proving the Python binding from Episode 5 behaves the way the manual REPL session suggested — not just "I saw the right output once," but something that runs every time. Here's `tests/test_native.py`:

```python
import json
from pico_native import HelloPico

def test_hello_event():
    pico = HelloPico("hello-pico", "0.1.0")
    result = json.loads(
        pico.hello("Willem")
    )
    assert result["event_count"] == 1
    assert result["message"] == (
        "Hello, Willem! I am Pico hello-pico."
    )
```

Run it:

```bash
uv run pytest
```

Straightforward enough on its own — but as the number of moving pieces grows (and it's about to grow considerably), typing out `cargo test`, `cargo clippy`, `cargo fmt --check`, `ruff check`, and `pytest` separately, every time, gets old fast. This is where the canonical development commands come in, defined once in a `Justfile`:

```
develop:
	maturin develop
	uv run pytest

check:
	cargo fmt --check
	cargo clippy --workspace --all-targets -- -D warnings
	cargo test --workspace
	uv run ruff check .
	uv run pytest

build:
	maturin build --release
```

From here on, the whole development loop collapses to three words:

```bash
just develop
just check
just build
```

`just develop` rebuilds the native extension and runs the Python test suite — the everyday inner loop. `just check` is the full gate: Rust formatting, Rust linting (with warnings promoted to errors), every Rust test, Python linting, and every Python test, all in one command, all-or-nothing. `just build` produces the release wheel, which we'll actually use two episodes from now.

There's a reason this matters beyond convenience, and it's one I found genuinely clever once I noticed it: `just check` is a single, unambiguous, machine-checkable definition of "done." Whether a human is writing the next feature or an AI coding agent is (as we'll see much later in this series), the instruction is the same, and it's precise: *implement the feature, and don't consider the task complete until `just check` succeeds.* No ambiguity about which subset of checks counts, no forgetting the linter because the tests passed. One command, one gate.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `tests/test_native.py` | The `pico_native.HelloPico` binding from Episode 5 | Assert the `hello` event produces the exact expected message and count | A repeatable, automated confirmation of Gate 2's behavior | `uv run pytest`, and every future change to `pico-native` |
| The `Justfile` | Every individual formatting, linting, and test command across Rust and Python | Collapse them into `develop`, `check`, and `build` targets | Three simple, memorable commands covering the whole toolchain | Every developer (human or AI) working on this repository |
| `just check` | The full source tree at any point in time | Run formatting, linting, and every test, Rust and Python alike | A single pass/fail signal defining "done" | Anyone deciding whether a change is ready to ship |

Next stop: Gate 3 — leaving development mode behind and building the actual release wheel.
