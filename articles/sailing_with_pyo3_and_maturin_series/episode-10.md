---
title: "🗺️ Crossing Borders: manylinux and Every Port at Once"
series: "Sailing with PyO3 and Maturin"
part: 10
organization: "the-software-s-journey"
tags: [maturin, manylinux, ci, cross-compilation, github-actions]
---

## 🗺️ Crossing Borders: manylinux and Every Port at Once

A boat that only sails in its home harbor isn't much of a yacht. The whole point is making port in places you've never been, on machines with different chips, different operating systems, different libraries already installed — or not installed — on the dock. This is where most hybrid Python/Rust packages either quietly fail or quietly succeed, and the difference almost always comes down to whether someone bothered to actually build for every port ahead of time, rather than hoping the harbor you land in looks like the one you left.

Linux is the trickiest port of all, because "Linux" isn't one destination — it's hundreds of subtly different distros with subtly different system libraries. `manylinux` is the industry's answer: a set of standardized, deliberately old, deliberately conservative build environments that produce wheels compatible with almost every Linux distro in circulation, regardless of what's actually installed on the machine that eventually runs `pip install`. Maturin builds against these targets directly, most easily inside a container built exactly for the purpose:

```bash
docker run --rm -v $(pwd):/io ghcr.io/pyo3/maturin build --release --manylinux 2_28
```

For anyone shipping packages regularly, though, the real answer isn't a manual Docker invocation — it's CI, and PyO3's own project ships a purpose-built GitHub Action for exactly this:

```yaml
# .github/workflows/build.yml
name: Build wheels
on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - name: Build wheels
        uses: PyO3/maturin-action@v1
        with:
          target: ${{ matrix.os == 'ubuntu-latest' && 'x86_64-unknown-linux-gnu' || '' }}
          args: --release --out dist
          manylinux: auto
      - uses: actions/upload-artifact@v4
        with:
          name: wheels-${{ matrix.os }}
          path: dist
```

Run that matrix, and one push to your repository quietly builds seaworthy wheels for Linux, macOS, and Windows, each one properly tagged, each one landing in its own `dist/` folder, ready to be gathered up and published together. Add architecture targets — `aarch64-unknown-linux-gnu` for ARM Linux, `aarch64-apple-darwin` for Apple Silicon — and the same action builds for those ports too, cross-compiling from a single CI runner without ever needing a physical machine of that architecture sitting in the harbor.

This is, honestly, one of the more underrated benefits of choosing PyO3 and Maturin over hand-rolled C extensions: the packaging and cross-platform story is a genuinely solved problem here, not an afterthought bolted on by whoever drew the short straw. A boat that makes every port on the map, built once, from one set of source files, on one CI run — that's not a small thing to get for free.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `manylinux` build environment | Rust and Python source, targeting a standardized old-glibc baseline | Compile a wheel compatible with a very wide range of Linux distros | A broadly portable Linux wheel | Any Linux user running `pip install`, regardless of distro |
| `PyO3/maturin-action` (GitHub Actions) | A CI matrix across OSes and architectures | Build wheels for each target in parallel, automatically | A full set of platform-specific wheels per release | Package maintainers, PyPI, end users on any platform |
| Cross-compilation targets (`aarch64-*`, etc.) | A target triple different from the build host | Cross-compile without needing native hardware of that architecture | Wheels for ARM Linux, Apple Silicon, and more, from one CI runner | Users on architectures the maintainer may not personally own |

Next stop: pulling back into harbor for the last time — why this whole two-deck arrangement earns its keep, and where it shows up in boats you may already be sailing.

