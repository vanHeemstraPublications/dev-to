---
title: "Sailing with PyO3 and Maturin 📦 Ep.6"
series: "Sailing with PyO3 and Maturin"
part: 6
organization: "the-software-s-journey"
tags: [pyo3, type-conversion, frompyobject, intopy, rust]
---

## Episode 6: The Cargo Hold Manifest: Passing Data Between Decks

Nothing gets loaded onto this boat without a manifest — a clear, checked description of exactly what's in every crate before it moves between decks. PyO3's type conversion system is that manifest, and it's the reason passing a Python list or dictionary into Rust doesn't feel like smuggling contraband across a border.

The simple cargo — numbers, strings, booleans, lists, tuples, `Vec`, `HashMap` — moves automatically, no manifest required beyond the function signature itself:

```rust
use std::collections::HashMap;

#[pyfunction]
fn tally_evidence(items: HashMap<String, u32>) -> HashMap<String, u32> {
    items
        .into_iter()
        .map(|(k, v)| (k, v * 2))
        .collect()
}
```

```python
>>> vice_engine.tally_evidence({"cash": 3, "boats": 1})
{'cash': 6, 'boats': 2}
```

A Python `dict[str, int]` becomes a Rust `HashMap<String, u32>` on the way in, and the reverse on the way out, with nothing hand-written on either side. But real cargo isn't always that plain, and this is where two traits do the actual manifest-writing: `FromPyObject`, for cargo coming *down* from Python into Rust, and `IntoPy`, for cargo going *up* from Rust into Python. Define a custom Rust type, and you can teach it to cross the boundary on its own terms:

```rust
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[derive(Debug)]
struct Suspect {
    name: String,
    plate: String,
}

impl<'py> FromPyObject<'py> for Suspect {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let dict = ob.downcast::<PyDict>()?;
        let name: String = dict.get_item("name")?.unwrap().extract()?;
        let plate: String = dict.get_item("plate")?.unwrap().extract()?;
        Ok(Suspect { name, plate })
    }
}

#[pyfunction]
fn run_plate(suspect: Suspect) -> String {
    format!("Running plate {} for {}...", suspect.plate, suspect.name)
}
```

```python
>>> vice_engine.run_plate({"name": "Calderone", "plate": "MIA-1984"})
'Running plate MIA-1984 for Calderone...'
```

Python hands over what looks like an ordinary dict; Rust receives a properly typed `Suspect` struct, validated on the way in — miss a key, or hand over the wrong type, and `extract()` fails loudly with a clear Python exception rather than quietly loading a crate with the wrong label on it. That's the real value of a manifest: not just moving cargo, but *refusing* to move cargo that doesn't match what was declared, before it ever causes a problem three decks away from where the mistake was made.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| PyO3's built-in conversions | Common Python types (`list`, `dict`, `str`, numbers) | Convert automatically to and from matching Rust types | Zero-boilerplate cargo movement for ordinary data | Any `#[pyfunction]` or `#[pymethods]` signature |
| `FromPyObject` implementation | A Python object of unknown shape (e.g. a dict) | Validate and extract it into a custom, strongly-typed Rust struct | A checked, typed value Rust code can trust | Rust functions expecting that specific structure |
| `IntoPy` implementation | A native Rust value | Convert it into an appropriate Python object on return | A Python-native result, no manual wrapping needed | The calling Python code |

Next stop: what happens when the cargo manifest doesn't match what's in the crate — Rust's `Result`, Python exceptions, and handling rough seas gracefully.

