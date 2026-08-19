---
title: "🔧 Below-Deck Machinery: Building Classes with pyclass"
series: "Sailing with PyO3 and Maturin"
part: 4
organization: "the-software-s-journey"
tags: [pyo3, pyclass, rust, python, oop]
---

## 🔧 Below-Deck Machinery: Building Classes with pyclass

A single function shouted down a tube only gets you so far. Real engine rooms have machinery with state — a throttle that remembers its own position, a fuel gauge that tracks what's actually left in the tank. PyO3's `#[pyclass]` is how a whole piece of below-deck machinery gets a proper handle installed above deck, one Sonny can operate without ever climbing down the ladder.

```rust
use pyo3::prelude::*;

#[pyclass]
struct Throttle {
    #[pyo3(get, set)]
    position: f64,
    max_rpm: u32,
}

#[pymethods]
impl Throttle {
    #[new]
    fn new(max_rpm: u32) -> Self {
        Throttle { position: 0.0, max_rpm }
    }

    fn advance(&mut self, amount: f64) -> PyResult<()> {
        self.position = (self.position + amount).clamp(0.0, 1.0);
        Ok(())
    }

    fn current_rpm(&self) -> u32 {
        (self.position * self.max_rpm as f64) as u32
    }

    fn __repr__(&self) -> String {
        format!("Throttle(position={:.2}, max_rpm={})", self.position, self.max_rpm)
    }
}
```

`#[pyclass]` on the struct is what makes `Throttle` a real Python type, not just a Rust one — instantiable, inspectable, garbage-collected on the Python side even though the actual data lives in native Rust memory. `#[pymethods]` is the block where every Python-visible method gets defined, and the annotations inside it read almost exactly like the dunder methods any Python developer already knows: `#[new]` is `__init__`, `__repr__` is exactly what you think it is, and `#[pyo3(get, set)]` on a field turns it into a proper Python property, readable and writable, no manual getter or setter boilerplate required on either side.

From above deck, none of this looks like Rust at all:

```python
>>> from vice_engine import Throttle
>>> t = Throttle(max_rpm=6000)
>>> t.advance(0.75)
>>> t.position
0.75
>>> t.current_rpm()
4500
>>> t
Throttle(position=0.75, max_rpm=6000)
```

Sonny sets `.position` like it's an ordinary attribute on an ordinary Python object, calls `.advance()` like an ordinary method, and gets a clean `repr()` in the console — never once needing to know that underneath, every call crosses the language boundary, runs in Rust's own memory model, with no garbage collector pausing the engine mid-throttle and no chance of a dangling pointer sinking the boat. That's the actual promise of `#[pyclass]`: real, stateful, safe machinery below deck, wearing a handle above deck that feels exactly like home.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Rust struct author | A struct with fields meant to hold state | Annotate with `#[pyclass]` and expose fields via `#[pyo3(get, set)]` | A Rust type usable as a real Python class | Python code instantiating and inspecting it |
| `#[pymethods]` block | Constructor (`#[new]`), methods, and dunder overrides | Register them as the class's Python-visible API | A fully-featured object with `__init__`, `__repr__`, and custom methods | Any Python code calling methods on an instance |
| Rust's ownership model | Native struct memory, no garbage collector | Manage memory safety and lifetime automatically at compile time | Fast, safe object state with no GC pauses | The whole running program, especially hot loops |

Next stop: who's allowed to touch the wheel at any given moment — the GIL, and how to let the engine room run flat out without waiting for the bridge's permission.

