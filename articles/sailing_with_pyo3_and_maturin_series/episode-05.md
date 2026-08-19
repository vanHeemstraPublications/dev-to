---
title: "Sailing with PyO3 and Maturin 🛞 Ep.5"
series: "Sailing with PyO3 and Maturin"
part: 5
organization: "the-software-s-journey"
tags: [pyo3, gil, allow_threads, concurrency, python]
---

## Episode 5: The One-Wheel Rule: the GIL and Letting the Engine Room Run

Every boat this size has a rule that sounds restrictive until you understand why it exists: only one person touches the wheel at a time. Not because the crew can't be trusted, but because two hands fighting the same wheel in a storm is worse than one hand, alone, holding a steady course. Python has the exact same rule, and it's got a name everyone eventually learns to either love or resent: the Global Interpreter Lock, the GIL. Only one thread executes Python bytecode at a time, full stop, no exceptions — which is precisely why a pure-Python program rarely benefits from more CPU cores, no matter how many threads you throw at it.

PyO3 makes you feel this rule directly, right there in the function signature, the moment you need to actually touch Python objects from Rust:

```rust
use pyo3::prelude::*;

#[pyfunction]
fn greet_crew<'py>(py: Python<'py>, name: &str) -> PyResult<String> {
    Ok(format!("Evening, Detective {name}."))
}
```

That `Python<'py>` token isn't decoration — it's proof, checked at compile time, that you're holding the wheel. You cannot construct one out of nowhere; PyO3 hands it to you because the GIL is currently yours, and any Python object you touch through it is guaranteed safe to touch, precisely because nobody else can be touching Python at the same moment.

Here's where it gets genuinely interesting, and where the whole point of putting an engine room below a Python bridge starts to pay for itself. Say the Rust side has real work to do — a long, CPU-heavy computation that touches no Python objects at all once it's started. Holding the wheel for that entire stretch would mean every other Python thread sits idle, waiting its turn, even though the actual work has nothing left to do with Python. `py.allow_threads()` is how you hand the wheel back for exactly that stretch:

```rust
#[pyfunction]
fn plot_long_course(py: Python<'_>, waypoints: Vec<(f64, f64)>) -> PyResult<f64> {
    let total_distance = py.allow_threads(|| {
        // No Python objects touched in here — pure Rust, pure CPU.
        waypoints
            .windows(2)
            .map(|pair| {
                let (lat1, lon1) = pair[0];
                let (lat2, lon2) = pair[1];
                ((lat2 - lat1).powi(2) + (lon2 - lon1).powi(2)).sqrt()
            })
            .sum()
    });
    Ok(total_distance)
}
```

Inside that closure, the GIL is released — other Python threads can run freely, genuinely in parallel, on other cores, while this one stretch of pure computation chews away below deck at full native speed. The instant the closure returns, PyO3 reacquires the GIL automatically before handing control back to Python. That's the whole trick: the bridge doesn't sit there holding the wheel out of habit while the engine room does its own self-contained work. It hands the wheel back, lets the crew below run flat out, and takes it back the moment Python needs it again. One rule, respected carefully, and the whole boat moves faster for it.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Python interpreter | The GIL itself | Guarantee only one thread executes Python bytecode at a time | Memory-safe, race-free access to Python objects | Every Python thread in the process |
| `Python<'py>` token (PyO3) | A function currently holding the GIL | Prove, at compile time, safe access to Python objects | A type-checked guarantee no unsafe Python access slips through | Rust functions manipulating Python data |
| `py.allow_threads()` | A GIL-free closure doing pure Rust computation | Release the GIL for the closure's duration, reacquire it after | True parallel execution alongside other Python threads | CPU-bound Rust code, and any other Python thread waiting on the GIL |

Next stop: what actually rides in the cargo hold — passing lists, dicts, and richer data structures back and forth across the boundary.

