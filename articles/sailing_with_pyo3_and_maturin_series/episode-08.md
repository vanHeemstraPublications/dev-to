---
title: "Sailing with PyO3 and Maturin 🧰 Ep.8"
series: "Sailing with PyO3 and Maturin"
part: 8
organization: "the-software-s-journey"
tags: [cargo, dependencies, pip, pyproject-toml, rust]
---

## Episode 8: Provisioning the Yacht: Two Supply Lists, One Boat

Before any real trip, somebody's got two separate supply lists going — one for what the bridge needs (charts, fuel receipts, the espresso machine Sonny insists on), one for what the engine room needs (filters, gaskets, spare belts). Different lists, different suppliers, and nobody confuses which crate goes where. A hybrid PyO3 project runs the exact same way: `Cargo.toml` provisions the engine room, `pyproject.toml` provisions the bridge, and Maturin is the one making sure both lists get loaded before the boat leaves the dock.

Below deck, Rust dependencies come from crates.io, declared in the now-familiar `Cargo.toml`:

```toml
[dependencies]
pyo3 = { version = "0.22", features = ["extension-module"] }
rayon = "1.10"       # data parallelism for the engine room
serde = { version = "1", features = ["derive"] }
```

Bring in `rayon`, and suddenly the below-deck crew can split a heavy computation across every core the boat has, entirely inside Rust, with no Python involved at all until the final answer surfaces:

```rust
use rayon::prelude::*;

#[pyfunction]
fn total_haul(catches: Vec<f64>) -> f64 {
    catches.par_iter().sum()
}
```

Above deck, ordinary Python dependencies live exactly where they always have — declared in `pyproject.toml`'s `[project.dependencies]`, installed with `pip`, resolved by whatever Python packaging tooling you already trust:

```toml
[project]
name = "vice-engine"
version = "0.1.0"
dependencies = [
    "numpy>=1.24",
    "click>=8.1",
]
```

Neither list needs to know much about the other. The Rust crate `pyo3` doesn't appear anywhere in `pyproject.toml`'s dependency list — it's an implementation detail of *how* the extension gets built, not something an end user installing your package via `pip install vice-engine` ever has to think about, provision, or even see. And a Python dependency like `numpy` doesn't need a matching `Cargo.toml` entry unless the Rust side specifically wants to talk to NumPy's own C API directly — which, as it happens, is exactly what the `numpy` crate (a Rust crate, confusingly and delightfully sharing a name with its Python counterpart) is for, letting Rust below deck read and write NumPy arrays without copying the data at all:

```toml
[dependencies]
numpy = "0.22"
```

```rust
use numpy::{PyArray1, PyReadonlyArray1};

#[pyfunction]
fn scale_readings<'py>(
    py: Python<'py>,
    readings: PyReadonlyArray1<'py, f64>,
    factor: f64,
) -> Bound<'py, PyArray1<f64>> {
    let scaled: Vec<f64> = readings.as_array().iter().map(|v| v * factor).collect();
    PyArray1::from_vec_bound(py, scaled)
}
```

Two supply lists, two suppliers, one boat that leaves the dock fully provisioned on both decks, without either crew ever needing to raid the other's stores.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| crates.io (via `Cargo.toml`) | Rust dependency declarations (e.g. `pyo3`, `rayon`, `numpy`) | Resolve and compile Rust dependencies at build time | A fully provisioned engine room, baked into the compiled extension | The Rust side of the codebase |
| PyPI (via `pyproject.toml`) | Python dependency declarations (e.g. `numpy`, `click`) | Resolve and install Python dependencies via `pip` | A fully provisioned bridge, installed alongside the package | End users' Python environments |
| The `numpy` Rust crate | A Python `numpy.ndarray` passed across the boundary | Read/write NumPy array data directly from Rust, no copy | Zero-copy numerical interop between decks | Performance-sensitive numerical code |

Next stop: launch day — `maturin develop`, `maturin build`, and `maturin publish`, and finally seeing this boat actually leave the dock.

