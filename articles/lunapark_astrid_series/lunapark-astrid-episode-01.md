---
title: "Astrid Lunapark 🎡 Ep.1"
published: false
description: "Episode 1: Step right through the gates of the most enchanting lunapark in the AI universe! Astrid is an operating system for AI agents — a fixed microkernel surrounded by swappable capsule attractions. Come discover what makes this park unlike any other, how to get your first wristband, and why the rides never stop changing while the park itself stays perfectly in place."
tags: [rust, ai, agents, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/lunapark_astrid_series/astrid-lunapark-episode-01.png"
series: "Lunapark Astrid Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: Welcome to the Most Magical OS on Earth

> *“When you wish upon a star, makes no difference who you are — but when you deploy an AI agent, it makes ALL the difference what OS it runs on.”*

-----

## The Gates Are Open! 🎠

Ladies and gentlemen, children of all ages, and developers of every timezone — welcome, welcome, **WELCOME** to the Astrid Lunapark!

Picture it: a magnificent amusement park stretching as far as your imagination can see. In the centre stands the Grand Central Pavilion — solid, permanent, gleaming. Around it, a dazzling constellation of rides and attractions that can be added, swapped, or redesigned without touching so much as a single brick of the central structure. A roller coaster that talks to Ollama appears on Tuesday. A Ferris wheel of chain-of-thought reasoning rises on Wednesday. A hall of mirrors for caching repeated questions materialises on Thursday.

The park itself never changes. The attractions are wonderfully, endlessly, magically different.

That, dear visitor, is **Astrid** — an operating system for AI agents. The Grand Central Pavilion is the microkernel. Every ride is a capsule. And the magic that holds it all together is more elegant than any wish upon a star.

-----

## 🗂️ SIPOC — The Lunapark Opens Its Gates

|**Suppliers**          |**Inputs**                                                             |**Process**                                                            |**Outputs**                                            |**Customers**                                |
|-----------------------|-----------------------------------------------------------------------|-----------------------------------------------------------------------|-------------------------------------------------------|---------------------------------------------|
|You (the park designer)|Your AI agent use case: offline worker, coding assistant, debate system|Compose a `Distro.toml` selecting which capsule-attractions to run     |A fully personalised AI agent OS                       |Your users, your automation, your imagination|
|The Astrid kernel      |The fixed park foundation: boot, VFS, IPC, capabilities, audit         |Boot sequence resolves capsule dependencies, starts everything in order|A running agent environment with all rides operational |Every capsule in the park                    |
|Capsule authors        |Rust (or TypeScript via OpenClaw) capsule code + `Capsule.toml`        |WASM compilation, manifest declaration, SDK bindings                   |An isolated, sandboxed attraction ready to be installed|Users chatting with `astrid chat`            |

-----

## What Problem Does This Park Solve? 🎯

Most AI agent frameworks are like theme parks where the rides are *welded to the ground*. The LLM provider? Permanently installed. The orchestration loop? Cast in concrete. The tool set? Bolted into the foundation. To change any of it, you need a jackhammer, a forklift, and three sprints.

Astrid inverts this completely. The kernel provides exactly four things that every AI agent needs and never wants to reimplement:

```
🏛️  SANDBOXING    — WASM isolation, 64 MB ceiling, 5-minute timeout
🔌  IPC           — publish/subscribe event bus between capsules
📁  FILESYSTEM    — copy-on-write VFS overlay, path-traversal proof
🔐  GOVERNANCE    — capability tokens, budget, approval, audit chain
```

Everything above this foundation? Swappable capsule. Provider capsule. Orchestrator capsule. Tool capsule. Frontend capsule. Caching capsule. You compose them. You swap them. The kernel watches. The rides go round.

-----

## The Park Layout: Your First Map 🗺️

```
                    ╔═══════════════════════════════════╗
                    ║         ASTRID  LUNAPARK          ║
                    ╠═══════════════════════════════════╣
                    ║                                   ║
     Capsule Park   ║  ┌──────────────────────────────┐ ║
     (all swappable)║  │    Provider Attraction       │ ║
                    ║  │  (OpenAI / Ollama / vLLM)    │ ║
                    ║  └─────────────┬────────────────┘ ║
                    ║                │ IPC              ║
                    ║  ┌─────────────▼────────────────┐ ║
                    ║  │   Orchestrator Attraction    │ ║
                    ║  │ (ReAct / Monte Carlo / MCTS) │ ║
                    ║  └─────────────┬────────────────┘ ║
                    ║                │ IPC              ║
                    ║  ┌─────────────▼────────────────┐ ║
                    ║  │     Tools Attraction         │ ║
                    ║  │  (search, code, filesystem)  │ ║
                    ║  └──────────────────────────────┘ ║
                    ║                                   ║
                    ╠═══════════════════════════════════╣
                    ║   🏛️  THE GRAND CENTRAL KERNEL    ║
                    ║   (fixed — never replaced)        ║
                    ╚═══════════════════════════════════╝
```

One conversation. One chat. Powered by whichever combination of rides you chose to install.

-----

## Getting Your First Wristband: Installation 🎟️

To enter the park, you need a wristband. Here is how to get one:

```bash
# Install Rust if you haven't already (the park runs on Rust magic!)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone the park blueprints
git clone https://github.com/unicity-astrid/astrid.git
cd astrid

# Build the entire park in release mode
cargo build --release

# Or, once packages are published to crates.io:
cargo install astrid-cli
```

The workspace builds 27 crates — the entire park infrastructure from the ticket booth to the roller coaster:

```toml
# Cargo.toml — the park's master blueprint
[workspace]
resolver = "2"

members = [
    "crates/astrid-kernel",       # The Grand Central Pavilion
    "crates/astrid-capsule",      # The ride specification system
    "crates/astrid-approval",     # The safety inspector's office
    "crates/astrid-audit",        # The visitor logbook (tamper-proof!)
    "crates/astrid-capabilities", # The wristband office
    "crates/astrid-vfs",          # The park map
    "crates/astrid-events",       # The park-wide loudspeaker system
    "crates/astrid-crypto",       # The signature verification booth
    "crates/astrid-build",        # The ride construction yard
    # ... 18 more wonders await
]

[workspace.package]
version = "0.7.0"
edition = "2024"
rust-version = "1.95"
license = "MIT OR Apache-2.0"
```

-----

## Your First Conversation: `astrid chat` 🎙️

The only frontend today is the CLI — a magical intercom system directly to the park’s central intelligence:

```bash
# Start a conversation with your AI agent
astrid chat

# The park boots up, capsules load in order, and then...
> Hello, Astrid! What can you do?

Astrid: I am your AI agent, running in safe mode. My current capabilities include:
  - Reading and writing files in your workspace
  - Searching the web (if web-search capsule is installed)
  - Running shell commands (with your approval)
  - Answering questions using [your configured provider]

  What would you like to explore today?
```

Four operation modes control how much the agent can do without asking permission:

|Mode        |The ride safety level                 |What happens                                        |
|------------|--------------------------------------|----------------------------------------------------|
|`safe`      |Full safety harness, inspector present|Agent asks before every action outside workspace    |
|`guided`    |Harness on, inspector checking writes |Auto-allows reads, asks for writes                  |
|`autonomous`|Harness removed by your choice        |Agent acts freely within capability grants          |
|`yolo`      |*“Hold my cotton candy”*              |All guardrails off — for the truly daring Astrinauts|

Configure it in your workspace settings:

```toml
# ~/.astrid/workspace.toml
[agent]
mode = "guided"    # The sweet spot for most visitors
```

-----

## The Capsule Philosophy: Rides That Never Close the Park 🎢

Here is the magic that makes Astrid unlike every other framework. Most frameworks bake their assumptions into the foundation. Astrid puts them in the rides instead:

```toml
# A simple provider capsule manifest
# (Capsule.toml — the ride's instruction manual)
[capsule]
name    = "provider-ollama"
version = "0.3.0"
engine  = "wasm"

[exports]
"astrid:provider/llm-provider@0.1" = "OllamaProvider"

[imports]
"astrid:kernel/config@0.1" = "kernel_config"
"astrid:kernel/http@0.1"   = "http_client"
```

That is it. The orchestrator capsule does not know this manifest exists. It only knows it needs `astrid:provider/llm-provider@0.1` — and the kernel delivers whatever capsule satisfies that interface. Swap `provider-ollama` for `provider-openai` and the orchestrator keeps running unchanged.

The ride changed. The park is still standing.

-----

## The Promise: What This Series Will Show You 🌟

Over the coming episodes, we will ride every attraction in this magnificent park:

|#|Episode                 |The Attraction   |What We Explore                                |
|-|------------------------|-----------------|-----------------------------------------------|
|1|*This one* — Gates Open!|The entrance     |Overview, install, first chat                  |
|2|The Fixed Pavilion      |The kernel itself|Boot, crate inventory, why it never changes    |
|3|Rides and Attractions   |Capsule system   |`Capsule.toml`, WASM, SDK, `#[capsule]` macro  |
|4|The Electrical Grid     |IPC event bus    |Publish, subscribe, receive, event schemas     |
|5|The Safety Inspector    |Security model   |Five layers: Policy→Token→Budget→Approval→Audit|
|6|The Magic Wristbands    |Capability tokens|ed25519 tokens, approval modes, budget         |
|7|The Park Map            |VFS overlay      |Copy-on-write, path safety, file handles       |
|8|Build Your Own Ride     |Capsule authoring|SDK, `astrid-build`, distros, MCP, OpenClaw    |

In **Episode 2**, we tour the Grand Central Pavilion — the kernel that never changes, no matter how many new rides arrive.

*The music swells. The lights sparkle. The adventure has only just begun!* ✨

-----

**🔗 Resources**

- **Astrid Repository**: [github.com/unicity-astrid/astrid](https://github.com/unicity-astrid/astrid)
- **Companion Repository**: [github.com/software-journey/astrid](https://github.com/software-journey/astrid)
- **Rust Installation**: [rustup.rs](https://rustup.rs)

-----

*🎡 Astrid Lunapark Series — where every episode is a new attraction, and the magic never stops.*
