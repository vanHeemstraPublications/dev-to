---
title: "📢 The Speaking Tube: pyfunction and pymodule"
series: "Sailing with PyO3 and Maturin"
part: 3
organization: "the-software-s-journey"
tags: [pyo3, pyfunction, pymodule, rust, python]
---

## 📢 The Speaking Tube: pyfunction and pymodule

Old ships had a brass tube running from the bridge straight down to the engine room — shout an order in one end, it comes out clear on the other, no radio required, no translation lost. PyO3's `#[pyfunction]` macro is that tube, and it's almost suspiciously simple to install.

```rust
use pyo3::prelude::*;

#[pyfunction]
fn distance_to_shore(lat: f64, lon: f64, coast_lat: f64, coast_lon: f64) -> f64 {
    let dlat = lat - coast_lat;
    let dlon = lon - coast_lon;
    ((dlat * dlat) + (dlon * dlon)).sqrt() * 111.0  // rough km per degree
}
```

That's ordinary Rust, doing ordinary Rust arithmetic — nothing about it screams "Python." The one line of ceremony, `#[pyfunction]`, is what tells PyO3 "wire this into the speaking tube." From there, it still needs registering into a module before Python can hear it at all:

```rust
#[pymodule]
fn vice_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(distance_to_shore, m)?)?;
    Ok(())
}
```

`#[pymodule]` marks the entry point Python actually calls `import` on — the name here, `vice_engine`, has to match what's declared in `pyproject.toml`, or Python goes looking for a module that never answers. `wrap_pyfunction!` is the literal act of connecting the tube's Rust end to its Python end. Build it with Maturin, and from above deck, it's just a function call, full stop:

```python
import vice_engine

print(vice_engine.distance_to_shore(25.7617, -80.1918, 25.79, -80.13))
```

Sonny doesn't need to know a word of Rust to use this. He shouts a question down the tube, a number comes back, and as far as he's concerned, that's the whole contract. But the tube carries more than plain numbers — PyO3 handles the translation of ordinary Python types automatically, strings, lists, dicts, and tuples included:

```rust
#[pyfunction]
fn crew_roster(names: Vec<String>) -> Vec<String> {
    names
        .into_iter()
        .map(|n| format!("Detective {n}"))
        .collect()
}
```

```python
>>> vice_engine.crew_roster(["Crockett", "Tubbs"])
['Detective Crockett', 'Detective Tubbs']
```

A Python `list[str]` goes in, PyO3 converts it into a Rust `Vec<String>` on the way down the tube, the Rust code does its work in native, garbage-collector-free memory, and the result gets converted right back into a Python `list[str]` on the way up. Neither side had to think about the conversion. That's the whole point of a well-built speaking tube: it disappears the moment you trust it.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Rust function author | An ordinary Rust function | Annotate it with `#[pyfunction]` | A Rust function eligible to be exposed to Python | The module's `#[pymodule]` registration block |
| `#[pymodule]` entry point | One or more `wrap_pyfunction!` registrations | Assemble them into a single importable Python module | A compiled module Python's `import` statement can find | Python code calling `import vice_engine` |
| PyO3's type conversion layer | Python arguments (`list`, `str`, `dict`, etc.) | Convert to and from native Rust types automatically | Seamless calls across the language boundary | Both Rust and Python developers, neither hand-writing conversions |

Next stop: below deck properly — turning a Rust struct into a full Python class with `#[pyclass]`, methods and all.

