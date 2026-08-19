---
title: "Sailing with PyO3 and Maturin 🌅 Ep.11"
series: "Sailing with PyO3 and Maturin"
part: 11
organization: "the-software-s-journey"
tags: [pyo3, maturin, wrapup, rust, python]
---

## Episode 11: Pulling Back Into Harbor

Sun's coming up over the marina now, and it's worth standing on the dock a minute looking back at the boat before anyone heads home. Sonny never had to learn Rust's borrow checker to steer this thing. Rico never had to explain to a single passenger why the engine room does what it does. That's not an accident — that's the entire design working exactly as intended.

We laid the hull out with Maturin, a shipwright that understands both a pure-Rust below deck and a pure-Python above deck belong on the same registration papers. We ran the speaking tube with `#[pyfunction]` and `#[pymodule]`, turning ordinary Rust functions into ordinary-feeling Python calls. We installed real machinery below deck with `#[pyclass]`, stateful objects that feel native to Python while living, safely, in Rust's own memory. We learned the one-wheel rule — the GIL — and how `py.allow_threads()` lets the engine room run flat out without the bridge standing around waiting on it. We wrote a proper cargo manifest with `FromPyObject` and `IntoPy`, so data crossing the boundary arrives typed and checked, not smuggled. We handled rough seas honestly, mapping Rust's `Result` onto real, catchable Python exceptions instead of letting failures sink the boat silently. We provisioned both decks from their own supply lines, `Cargo.toml` and `pyproject.toml`, never confusing which crate belonged where. We launched properly, `develop` for sea trials, `build --release` for the real thing, `abi3` so one hull serves every Python version in the harbor. And we crossed borders — `manylinux`, CI matrices, cross-compiled architectures — so the boat we built once could dock anywhere.

None of this is hypothetical, either. This exact two-deck arrangement is already carrying serious cargo across the industry: Polars runs its blazing-fast dataframe engine in Rust below deck with a Python API above it that feels entirely at home next to pandas. `cryptography`, one of the most widely depended-upon packages in the whole Python ecosystem, moved its core primitives to Rust specifically for the memory-safety guarantees that matter most when the code in question is protecting people's actual secrets. Ruff, the linter that made half of Python tooling feel slow by comparison overnight, is a Rust engine wearing a `pip install`-able Python face. `pydantic-core` did the same for validation. None of these projects asked their users to learn Rust. They just asked Rust to do the heavy lifting, quietly, below deck, while Python kept doing what Python's always been good at: being pleasant to actually work in.

That's the whole case for this hybrid, stated plainly: you don't have to choose between a boat that's fun to sail and a boat that's fast. You build one boat, with the right material on each deck, and you let PyO3 and Maturin worry about how the two decks actually talk to each other. Dock's clear. Go build something.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The full PyO3 + Maturin toolchain | Ten episodes' worth of individually-introduced pieces | Combine bindings, packaging, and cross-platform builds into one working system | A production-grade hybrid Python/Rust package | Any developer needing Python's ergonomics with Rust's performance |
| Real-world hybrid projects (Polars, cryptography, Ruff, pydantic-core) | The same PyO3/Maturin pattern, applied at scale | Demonstrate the pattern's viability outside a tutorial | Proof this architecture ships and holds up in production | The wider Python ecosystem, benefiting from native speed without leaving Python |
| The reader of this series | Eleven episodes of the two-deck metaphor, made concrete with code | Apply the pattern to their own performance-critical Python code | A hybrid package of their own, fast below deck, familiar above it | Their own users, who never need to know two languages were involved |

