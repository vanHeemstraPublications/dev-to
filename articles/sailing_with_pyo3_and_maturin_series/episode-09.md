---
title: "Sailing with PyO3 and Maturin 🚀 Ep.9"
series: "Sailing with PyO3 and Maturin"
part: 9
organization: "the-software-s-journey"
tags: [maturin, wheels, abi3, publish, ci]
---

## Episode 9: Launch Day: develop, build, and publish

Every boat has three very different kinds of days: the sea trials, where the crew is still bolting things on between test runs; the actual launch, when the finished vessel gets sealed up and handed to its new owner; and the day it's registered for the whole marina to charter. Maturin has a command for each one, and knowing which day you're actually having matters.

Sea trials — the everyday development loop — is `maturin develop`:

```bash
maturin develop
```

It compiles the Rust side and installs the result directly into your active virtual environment, editable-style, ready to `import vice_engine` immediately. Change a line of Rust, run `maturin develop` again, and the new engine's in the boat within seconds — no packaging step, no wheel file, just the fastest possible loop between "I changed the code" and "let's see if it works." This is where Sonny and Rico live ninety percent of the time, testing one modification against another before anything's considered finished.

Launch day itself is `maturin build`:

```bash
maturin build --release
```

That `--release` flag matters more than it looks — it tells `cargo` to compile with full optimizations, the difference between a dockside test run and the boat actually leaving the harbor at speed. The output is a proper wheel file, sealed and ready:

```
target/wheels/vice_engine-0.1.0-cp39-abi3-manylinux_2_28_x86_64.whl
```

That `abi3` in the filename is worth pausing on, because it's one of the more elegant tricks in this whole hybrid arrangement. Python's C API has a *stable* subset, and Rust code built against it — enabled with one feature flag —

```toml
[dependencies]
pyo3 = { version = "0.22", features = ["extension-module", "abi3-py39"] }
```

— produces a single wheel that runs unmodified on Python 3.9, 3.10, 3.11, and every version after, rather than needing a fresh compile for each one. One hull, seaworthy across every harbor from here on, instead of building a slightly different boat for every port you might visit.

Registering the boat for the whole marina to charter — publishing to PyPI — is the final command, and it's almost anticlimactic after everything that came before it:

```bash
maturin publish
```

One command, and the compiled wheel, along with a source distribution for platforms Maturin doesn't have a prebuilt wheel for, lands on PyPI, installable by anyone, anywhere, with a plain `pip install vice-engine` — no Rust toolchain required on the installing end at all, because the hard work already happened at launch. That's the real payoff of the whole hybrid arrangement this series has been building toward: the person installing your package never needs to know two languages were involved. They just get a boat that happens to go faster than the ones built entirely out of one material.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `maturin develop` | The current Rust source | Compile and install directly into the active virtualenv | An immediately importable, editable local build | Developers iterating rapidly during development |
| `maturin build --release` | Optimized Rust compilation settings, target Python ABI | Produce a fully packaged, optimized wheel file | A distributable `.whl`, often `abi3`-tagged for cross-version compatibility | CI artifacts, manual distribution, `maturin publish` |
| `maturin publish` | A built wheel and source distribution | Upload to PyPI (or a configured alternate index) | A publicly installable package | Anyone running `pip install <package-name>` |

Next stop: leaving your home harbor entirely — cross-compilation, manylinux, and building this boat for every port it might ever need to dock in.

