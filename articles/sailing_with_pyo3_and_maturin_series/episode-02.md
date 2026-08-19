---
title: "Sailing with PyO3 and Maturin ⚓ Ep.2"
series: "Sailing with PyO3 and Maturin"
part: 2
organization: "the-software-s-journey"
tags: [maturin, project-structure, pyproject-toml, cargo]
---

## Episode 2: The Shipwright's Drawing Board

Rico doesn't build a boat by improvising with whatever's lying around the dock. There's a drawing board first, a layout everyone agrees on before a single plank goes down. Maturin's version of that drawing board is one command:

```bash
maturin new vice_engine
```

Run it, and the yard lays out exactly the hull this whole series has been describing:

```
vice_engine/
├── Cargo.toml          # below deck: the engine's own bill of materials
├── pyproject.toml       # the boat's registration papers
└── src/
    └── lib.rs            # below deck: where the engine actually lives
```

`pyproject.toml` is the registration paperwork every Python boat needs, and the one line that matters most tells `pip` and every other tool exactly which shipwright to call when it's time to build:

```toml
[build-system]
requires = ["maturin>=1.5,<2.0"]
build-backend = "maturin"

[project]
name = "vice-engine"
version = "0.1.0"
requires-python = ">=3.9"

[tool.maturin]
features = ["pyo3/extension-module"]
```

`src/lib.rs` starts life almost embarrassingly simple — a single function, wrapped and registered:

```rust
use pyo3::prelude::*;

#[pyfunction]
fn sum_as_string(a: i64, b: i64) -> String {
    (a + b).to_string()
}

#[pymodule]
fn vice_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
```

Here's the layout worth appreciating on its own: Maturin doesn't force you to choose between a Rust-only hull and a Python-only one. Add a `python/` directory alongside `src/`, and you've got a proper mixed hull — hand-written Python living above deck, right next to the compiled Rust below:

```
vice_engine/
├── Cargo.toml
├── pyproject.toml
├── src/
│   └── lib.rs                 # below deck
└── python/
    └── vice_engine/
        ├── __init__.py         # above deck — re-exports, docstrings, pure-Python helpers
        └── py.typed
```

That `__init__.py` is where Sonny does his best work — importing the compiled below-deck module, wrapping it in a friendlier Python-facing API, adding type stubs, docstrings, and anything else that makes the boat pleasant to actually sail, without a single line of it needing to touch Rust. The drawing board's done. Time to run the speaking tube down to the engine room.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `maturin new` | A chosen project name | Scaffold `Cargo.toml`, `pyproject.toml`, and `src/lib.rs` | A ready-to-build hybrid project skeleton | The developer starting a new PyO3 project |
| `pyproject.toml`'s `[build-system]` | The declaration `build-backend = "maturin"` | Tell `pip`/`build` which tool actually compiles this package | A standards-compliant, buildable Python project | `pip install .`, CI build pipelines |
| Optional `python/` source layout | Hand-written Python alongside the compiled Rust module | Combine a native extension with a pure-Python public API | A "mixed" package, native speed with a Python-authored face | End users importing the finished package |

Next stop: the speaking tube itself — PyO3's `#[pyfunction]` and `#[pymodule]`, and how a shout from the bridge actually reaches the engine room.

