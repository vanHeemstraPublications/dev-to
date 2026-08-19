---
title: "Sailing with PyO3 and Maturin 🌊 Ep.7"
series: "Sailing with PyO3 and Maturin"
part: 7
organization: "the-software-s-journey"
tags: [pyo3, error-handling, pyerr, exceptions, rust]
---

## Episode 7: Handling Rough Seas: Errors Across the Boundary

Rico doesn't radio up "everything's fine" when the engine's actually flooding. He calls it exactly as it is, in terms Sonny can act on immediately, from the bridge, without climbing down to see for himself. That's what good error handling across the Python/Rust boundary looks like — a below-deck problem surfacing above deck as a proper Python exception, not a silent failure or, worse, a crash that takes the whole boat down.

Rust's native error type is `Result<T, E>`, and PyO3's whole design leans on it directly — return a `PyResult<T>`, which is just `Result<T, PyErr>`, and any `Err` you produce becomes a real, catchable Python exception the moment it crosses the boundary:

```rust
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyfunction]
fn set_course(heading: f64) -> PyResult<f64> {
    if !(0.0..360.0).contains(&heading) {
        return Err(PyValueError::new_err(
            format!("heading {heading} is out of range — must be 0..360")
        ));
    }
    Ok(heading)
}
```

```python
>>> vice_engine.set_course(450.0)
Traceback (most recent call last):
  ...
ValueError: heading 450.0 is out of range — must be 0..360
```

Sonny catches that exactly like any other Python `ValueError`, no special handling required — `try`/`except` works precisely as it always has, because as far as Python's concerned, it *is* an ordinary exception. PyO3 ships mappings for most of Python's built-in exception types out of the box — `PyValueError`, `PyTypeError`, `PyKeyError`, `PyRuntimeError`, and a good deal more — so most rough seas are handled with nothing more exotic than picking the right one off the shelf.

Sometimes, though, the boat needs its own specific alarm — something a caller can catch precisely, distinct from every other kind of trouble. PyO3 lets you define entirely custom exception types, registered right into the module:

```rust
use pyo3::create_exception;
use pyo3::exceptions::PyException;

create_exception!(vice_engine, EngineFailure, PyException);

#[pyfunction]
fn full_throttle(fuel_percent: f64) -> PyResult<()> {
    if fuel_percent < 5.0 {
        return Err(EngineFailure::new_err("not enough fuel for full throttle"));
    }
    Ok(())
}

#[pymodule]
fn vice_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("EngineFailure", m.py().get_type_bound::<EngineFailure>())?;
    m.add_function(wrap_pyfunction!(full_throttle, m)?)?;
    Ok(())
}
```

```python
>>> from vice_engine import EngineFailure
>>> try:
...     vice_engine.full_throttle(2.0)
... except EngineFailure as e:
...     print(f"Alarm from below: {e}")
Alarm from below: not enough fuel for full throttle
```

Now Sonny can catch `EngineFailure` specifically, distinct from a `ValueError` or a `RuntimeError` — a precise alarm for a precise problem, exactly the kind of clarity you want from an engine room three decks down in a storm.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Rust function returning `PyResult<T>` | An `Err(PyErr)` produced during execution | Propagate the error across the language boundary | A raised Python exception, catchable normally | Python code wrapping the call in `try`/`except` |
| PyO3's built-in exception types | A Rust-side error condition matching a common case | Map it to `PyValueError`, `PyTypeError`, `PyKeyError`, etc. | A familiar, standard Python exception type | Python code expecting conventional exception handling |
| `create_exception!` macro | A need for a domain-specific alarm | Define and register a custom exception class in the module | A precisely catchable, purpose-built exception type | Python code distinguishing this failure from all others |

Next stop: what's actually stocked in the hold before departure — Cargo dependencies below deck, `pip` dependencies above, and how the two provisioning lists coexist.

