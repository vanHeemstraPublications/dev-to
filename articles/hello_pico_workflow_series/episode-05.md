---
title: "🌉 Gate 2: Crossing the PyO3 Bridge"
series: "Hello Pico Workflow"
part: 5
organization: "the-software-s-journey"
tags: [open-engineering, pico, pyo3, rust, python, maturin]
---

## 🌉 Gate 2: Crossing the PyO3 Bridge

The instruction I found most useful going in: the PyO3 crate should be thin. It's not where logic lives — it's a boundary, a translator, nothing more. Conceptually, the shape looks like this:

```
Python
    HelloPico
       │
      PyO3
       │
       ▼
pico_core::HelloPico
```

And here's `crates/pico-native/src/lib.rs` in full — the whole boundary, owning the PyO3 object and protecting the Rust state behind a mutex so it's safe to touch from Python's threading model:

```rust
use pico_core::HelloPico as CorePico;
use pyo3::prelude::*;
use std::sync::Mutex;

#[pyclass]
struct HelloPico {
    inner: Mutex<CorePico>,
}

#[pymethods]
impl HelloPico {
    #[new]
    fn new(id: String, version: String) -> Self {
        Self {
            inner: Mutex::new(CorePico::new(id, version)),
        }
    }

    fn hello(&self, name: String) -> PyResult<String> {
        let mut pico = self
            .inner
            .lock()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err(
                "Pico state lock poisoned"
            ))?;
        serde_json::to_string(&pico.hello(&name))
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(e.to_string())
            })
    }

    fn state(&self) -> PyResult<String> {
        let pico = self
            .inner
            .lock()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err(
                "Pico state lock poisoned"
            ))?;
        serde_json::to_string(&pico.state())
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(e.to_string())
            })
    }
}

#[pymodule]
fn pico_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<HelloPico>()?;
    Ok(())
}
```

Notice what this crate does *not* do: it doesn't reimplement the state machine, doesn't add new behavior, doesn't decide what "hello" means. It just wraps `pico_core::HelloPico`, locks it safely, and serializes the result to a JSON string Python can parse. Every method returns `PyResult<String>`, and every failure path — a poisoned lock, a serialization error — becomes a proper Python `RuntimeError` rather than a crash.

PyO3's recommended packaging path is Maturin, and `maturin develop` is specifically meant for exactly this development loop — compile the Rust extension and install it straight into your active virtualenv:

```bash
uv sync
source .venv/bin/activate
maturin develop
```

Then, to actually see it work from Python:

```bash
python - <<'PY'
from pico_native import HelloPico
pico = HelloPico("hello-pico", "0.1.0")
print(pico.state())
print(pico.hello("Willem"))
print(pico.state())
PY
```

The second printed line should read:

```
Hello, Willem! I am Pico hello-pico.
```

See that, and that's **Gate 2**: the exact same logic verified in Rust back in Episode 4 is now callable, correctly, from ordinary Python — no reimplementation, no drift between what Rust does and what Python sees.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `pico-native` crate author | The `pico-core::HelloPico` type from Episode 4 | Wrap it in a `#[pyclass]`, protected by a `Mutex`, exposing `new`/`hello`/`state` | A Python-importable class backed by native Rust state | Python code calling `from pico_native import HelloPico` |
| `maturin develop` | The `pico-native` crate and an active virtualenv | Compile the extension and install it directly into the venv | An immediately importable native module, no packaging step | The developer's Python REPL, and later Manifold |
| The manual Python smoke test | `HelloPico("hello-pico", "0.1.0")` plus a `hello("Willem")` call | Exercise the full Rust-via-Python path once, by hand | Gate 2: proof that Python can drive the Rust state machine correctly | The next episode, building Manifold on top of this |

Next stop: giving this native module a real host — the Manifold runtime, and its first HTTP endpoints.
