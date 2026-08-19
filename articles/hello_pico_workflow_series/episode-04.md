---
title: "🦀 Gate 1: The Rust Core"
series: "Hello Pico Workflow"
part: 4
organization: "the-software-s-journey"
tags: [open-engineering, pico, rust, testing]
---

## 🦀 Gate 1: The Rust Core

Here's where I finally write code, and — I found this reassuring as someone who'd never touched Rust seriously before — none of it involves Python, Kubernetes, MQTT, or Crossplane yet. Just the state transition itself, in `crates/pico-core/src/lib.rs`:

```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PicoState {
    pub id: String,
    pub version: String,
    pub status: String,
    pub message: String,
    pub event_count: u64,
    pub last_run: Option<DateTime<Utc>>,
}

pub struct HelloPico {
    state: PicoState,
}

impl HelloPico {
    pub fn new(id: impl Into<String>, version: impl Into<String>) -> Self {
        Self {
            state: PicoState {
                id: id.into(),
                version: version.into(),
                status: "ready".into(),
                message: "Hello, Pico!".into(),
                event_count: 0,
                last_run: None,
            },
        }
    }

    pub fn hello(&mut self, name: &str) -> PicoState {
        self.state.event_count += 1;
        self.state.last_run = Some(Utc::now());
        self.state.message =
            format!("Hello, {name}! I am Pico {}.", self.state.id);
        self.state.clone()
    }

    pub fn state(&self) -> PicoState {
        self.state.clone()
    }
}
```

Reading this as a newcomer, the shape is genuinely approachable: `PicoState` is exactly the JSON structure from Episode 1, `HelloPico::new` builds the initial ready state, and `hello()` is the entire state transition — bump the count, stamp the time, rewrite the message. Nothing here knows or cares who's going to call it. That's deliberate; this crate's only job is to be a correct, deterministic state machine.

And here's the unit test proving it, right alongside the implementation:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hello_event_changes_state() {
        let mut pico = HelloPico::new("hello-pico", "0.1.0");
        let state = pico.hello("Willem");
        assert_eq!(
            state.message,
            "Hello, Willem! I am Pico hello-pico."
        );
        assert_eq!(state.event_count, 1);
        assert!(state.last_run.is_some());
    }
}
```

Run it:

```bash
cargo test --workspace
```

That's **Gate 1**. No Python, Kubernetes, MQTT, or Crossplane is involved yet — just proof that the core state transition behaves exactly as the target behavior from Episode 1 described. Every episode from here on is really just building progressively larger, more connected scaffolding *around* this one small, already-correct piece of logic. It's worth sitting with that for a second: the hardest-to-get-wrong part of the whole system — the actual business logic — is also the smallest, the fastest to test, and the first thing we finished.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `pico-core` crate author | The target behavior from Episode 1 (state shape, `hello` transition) | Implement `PicoState` and `HelloPico` in pure Rust | A deterministic, dependency-free state machine | `pico-native` (Episode 5), and ultimately Manifold |
| The unit test module | A known input (`"Willem"`) and expected output | Assert the state transition behaves exactly as specified | A passing/failing signal with zero external dependencies | `cargo test --workspace`, and anyone verifying the core is correct |
| `cargo test --workspace` | The compiled crate and its test module | Run every test across the workspace | Gate 1: a green build, proving the core logic alone | The next episode, which builds a Python-facing boundary around this |

Next stop: Gate 2 — crossing the PyO3 bridge, so this same Rust logic becomes callable from Python.
