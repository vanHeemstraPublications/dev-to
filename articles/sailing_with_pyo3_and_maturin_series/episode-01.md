---
title: "Sailing with PyO3 and Maturin 🛥️ Ep.1"
series: "Sailing with PyO3 and Maturin"
part: 1
organization: "the-software-s-journey"
tags: [pyo3, maturin, rust, python, introduction]
---

## Episode 1: Two Decks, One Boat

Sonny's got the wheel, sunglasses on even though it's past midnight, the neon off the marina smeared across the water like something out of a dream nobody wants to wake up from. Rico's below, checking gauges nobody above deck has ever bothered to learn the names of. Different decks, different jobs, same boat, and neither one of them would trade it for a vessel that only had one.

That's the whole pitch for this series. A pure-Python program is a beautiful boat above deck — expressive, quick to reshape, a joy to stand on and steer. But ask it to outrun something serious, a tight numerical loop, a parser chewing through gigabytes, and you feel the hull start to strain. A pure-Rust program, meanwhile, is all engine — blistering fast, safe against whole categories of memory disaster, and about as much fun to improvise on as trying to redecorate a submarine mid-voyage. Most people don't actually want either extreme. They want Sonny's style above deck and Rico's horsepower below, on the same hull, talking to each other constantly, neither one waiting around for the other to catch up.

PyO3 is the speaking tube between the bridge and the engine room — a set of Rust bindings that let Rust code define real Python functions, real Python classes, real Python modules, callable from ordinary Python exactly as if they'd been written in Python all along. Maturin is the shipwright — the build tool that takes your Rust below decks and your Python above decks and fits them together into a single, importable package, launchable with one command, sellable on PyPI like any other boat in the marina.

```toml
# Cargo.toml — below deck, the engine specification
[package]
name = "vice_engine"
version = "0.1.0"
edition = "2021"

[lib]
name = "vice_engine"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.22", features = ["extension-module"] }
```

```python
# above deck, once the boat is built
import vice_engine

print(vice_engine.sum_as_string(5, 20))
```

Two files, two languages, one working boat by the end of this trip. Over the episodes ahead we'll fit the hull together plank by plank — the shipwright's tools, the speaking tube's grammar, the engine room's classes and error handling, and finally, launch day itself. Sunglasses on. Let's shove off.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| PyO3 project | Rust source defining functions, classes, and a module | Compile Rust into a Python-callable native extension | A `.so`/`.pyd` module importable from plain Python | Python developers wanting native performance |
| Maturin | A project's `Cargo.toml` and `pyproject.toml` | Build, package, and optionally publish the compiled extension | An installable Python wheel | PyPI, `pip install`, CI pipelines |
| Rust toolchain (`cargo`, `rustc`) | PyO3-annotated Rust code | Compile to a `cdylib` linked against the Python C API | The compiled native library Maturin packages | PyO3, and ultimately the Python interpreter loading it |

Next stop: meeting the shipwright properly — Maturin, and how a boat like this actually gets laid out on the drawing board.

