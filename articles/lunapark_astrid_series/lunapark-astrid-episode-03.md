---
title: "Astrid Lunapark 🎡 Ep.3"
published: false
description: "Episode 3: Every wonderful thing about the Astrid Lunapark lives in its rides — the capsules. Each one is an isolated WASM process with its own manifest, its own sandboxed memory, and a beautifully typed contract declaring exactly what it provides and what it needs. Come discover Capsule.toml, the #[capsule] proc macro, WASM isolation, and the topological sort that boots the whole park in perfect order."
tags: [rust, wasm, ai, capsules]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/astrid-lunapark-episode-03.png"
series: "Lunapark Astrid Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 3
---

## Episode 3: Rides and Attractions — The Capsule System

> *“The way to get started is to quit talking and begin doing — but if you’re building a capsule, start with the Capsule.toml and let the proc macro do the doing.”*

-----

## The Rides Begin! 🎢

In Episode 2, we admired the Grand Central Pavilion — the kernel that never changes. Now the rides arrive! The trucks back in through the maintenance gate, the installation crews get to work, and piece by brilliant piece the attractions of the Astrid Lunapark take shape.

Every ride in this park is a **capsule**: an isolated WebAssembly process, described by a `Capsule.toml` manifest, communicating with the rest of the park through a typed, kernel-mediated interface. You cannot directly call another capsule’s functions. You cannot read another capsule’s memory. You can only publish to the IPC bus and subscribe to it — and the kernel makes sure every message respects the capability rules.

This is not restriction. This is the safety harness that makes it possible to trust every ride.

-----

## 🗂️ SIPOC — The Rides Come to Life

|**Suppliers**              |**Inputs**                                                      |**Process**                                                                                 |**Outputs**                                                                     |**Customers**                                                      |
|---------------------------|----------------------------------------------------------------|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------|
|Capsule author             |Rust source code + `Capsule.toml` manifest                      |`astrid-build` compiles to WASM Component Model binary, BLAKE3 hash computed                |A `.wasm` file + manifest, ready to install                                     |The kernel — loads, hash-verifies, sandboxes, and boots the capsule|
|The `#[capsule]` proc macro|`impl MyTools` with `#[astrid::tool]` methods                   |Generates all WASM ABI boilerplate: extern “C” exports, JSON serialisation, dispatch routing|A valid WASM Component binary with the full capsule entry-point surface         |Wasmtime — which executes the capsule as an isolated guest         |
|The dependency resolver    |All installed capsule manifests (`[imports]`/`[exports]` tables)|Topological sort: build a graph, detect cycles, determine boot order                        |An ordered list of capsules to start, each only after its dependencies are ready|The boot sequence — perfect startup order, every time              |

-----

## The Ride’s Instruction Manual: `Capsule.toml` 📋

Every attraction at the park comes with an instruction manual. For capsules, that manual is `Capsule.toml`. It tells the kernel three things: *who I am*, *what I need from other rides*, and *what I offer to the park*.

```toml
# Capsule.toml — the ride's instruction manual
[capsule]
name    = "tools-github"
version = "0.4.1"
engine  = "wasm"         # This ride runs on the WASM sandbox engine

[imports]
# What this ride needs from the park infrastructure
"astrid:kernel/http@0.1"   = "http_client"   # I need the park's HTTP service
"astrid:kernel/config@0.1" = "kernel_config" # I need access to configuration

[exports]
# What this ride offers to other attractions
"astrid:tools/github@0.4" = "GitHubTools"   # I provide GitHub tool capabilities

[capabilities]
# What host ABI permissions this ride is granted
fs_read    = ["workspace://"]   # Can read the workspace
http_hosts = ["api.github.com"] # Can call GitHub API (and only GitHub)

[skills]
# Natural language skill descriptions
search_issues  = "Search GitHub issues by query"
create_pr      = "Create a pull request with a title, body, and branch"
```

Notice the `[capabilities]` section. Like a carnival ride that is only permitted to operate on its designated footprint, the `tools-github` capsule can only make HTTP requests to `api.github.com` and only read from the workspace. Trying to call `api.evil-domain.com`? The kernel’s HTTP airlock rejects it before the request ever leaves.

-----

## Three Flavours of Ride Engine 🎠

Capsules can run three types of engines — three ways the attraction can power itself:

### 1. WASM — The Full Thrill Ride

```toml
[capsule]
engine = "wasm"
# Full WASM Component Model isolation
# 64 MB memory ceiling
# 5-minute wall-clock timeout
# BLAKE3 hash verification on the binary
# Complete host ABI access (49 syscall functions)
```

The flagship experience. Maximum isolation. Maximum capability. Compiled Rust code running inside Wasmtime with no syscalls, no file descriptors, no host memory access — only the carefully controlled 49-function ABI that the kernel exposes.

### 2. MCP — The Pop-Up Carnival Stand

```toml
[capsule]
engine = "mcp"
# A native subprocess proxied via JSON-RPC
# Follows the MCP 2025-11-25 specification
# Good for existing tools with MCP support
# Sandboxed via bwrap (on supported Linux kernels)
command = ["node", "my-mcp-server.js"]
```

Think of this as bringing in a third-party cotton candy stand. The stand operates under the park’s rules (the safety inspector still comes around), but it runs its own machinery. MCP capsules wrap any existing MCP-compatible process — a Node.js server, a Python script — and expose it as a first-class capsule citizen.

### 3. Static — The Information Kiosk

```toml
[capsule]
engine = "static"
# Declarative context injection only
# No code, no process — just configuration
# Injects files, prompts, and context into the agent's environment

[context]
system_prompt = "prompts/system.md"
reference_docs = ["docs/api-reference.md", "docs/architecture.md"]
```

A capsule that does not run code but injects context. Perfect for giving your agent background knowledge without touching the orchestrator.

-----

## The Ride Building: WASM Sandbox Details 🏗️

When the kernel loads a WASM capsule, the sandbox is non-negotiable:

```
WASM Capsule Sandbox Specifications
────────────────────────────────────
Memory ceiling:     64 MB — the ride cannot grow beyond its footprint
Time limit:         5 minutes wall-clock — the coaster always ends
Hash verification:  BLAKE3 on the .wasm binary
                    Wrong hash? Wrong version? The ride does not open.
Host access:        ZERO — no syscalls, no file descriptors, no host memory
                    Everything comes through the 49-function ABI only

The ABI is the only bridge between the ride and the rest of the park.
```

This means a compromised capsule — perhaps one with a supply chain vulnerability — cannot escape its sandbox. It can call `astrid_fs_read` and `astrid_http_request`, but those calls go through the capability checker first. No capability grant? No access. No exceptions. Even if the capsule’s code tries to do something unusual, it has no path to the host.

-----

## Writing a Capsule: The `#[capsule]` Proc Macro ✨

Writing a capsule feels like writing normal Rust. The magic is in the proc macro that transforms your high-level code into the WASM entry points the kernel expects:

```rust
// src/lib.rs — a GitHub tools capsule
use astrid_sdk::prelude::*;

// The capsule's main structure
#[derive(Default)]
pub struct GitHubTools;

// The #[capsule] macro generates all WASM ABI boilerplate:
// - extern "C" exports for every entry point
// - JSON serialisation/deserialisation at the ABI boundary
// - Dispatch routing to the correct method
#[capsule]
impl GitHubTools {

    // #[astrid::tool] marks this as a callable tool
    // The kernel will present this to the orchestrator as an available action
    #[astrid::tool]
    fn search_issues(&self, args: SearchArgs) -> Result<SearchResult, SysError> {
        // env::var comes from the astrid-sdk, not std::env
        // It reads from the capsule's scoped environment, not the host
        let token = env::var("GITHUB_TOKEN")?;

        // http::get is the sandboxed HTTP client
        // The kernel checks: is "api.github.com" in this capsule's http_hosts?
        let resp = http::get(
            &format!("https://api.github.com/search/issues?q={}", args.query)
        )?;

        let result: GitHubSearchResponse = resp.json()?;

        Ok(SearchResult {
            items: result.items
                .into_iter()
                .map(|i| IssueItem { number: i.number, title: i.title, url: i.html_url })
                .collect(),
            total: result.total_count,
        })
    }

    #[astrid::tool]
    fn create_pull_request(&self, args: CreatePrArgs) -> Result<PrResult, SysError> {
        let token = env::var("GITHUB_TOKEN")?;

        let body = serde_json::json!({
            "title": args.title,
            "body":  args.body,
            "head":  args.branch,
            "base":  args.base_branch.unwrap_or_else(|| "main".to_string()),
        });

        let resp = http::post(
            &format!("https://api.github.com/repos/{}/pulls", args.repo),
            &body,
        )?;

        Ok(PrResult { url: resp.json::<serde_json::Value>()?["html_url"]
            .as_str().unwrap_or("").to_string() })
    }
}

// These structs are just regular serde types
// The SDK handles JSON crossing the WASM boundary automatically
#[derive(serde::Deserialize)]
pub struct SearchArgs {
    pub query: String,
}

#[derive(serde::Serialize)]
pub struct SearchResult {
    pub items: Vec<IssueItem>,
    pub total: u64,
}
```

The `#[capsule]` macro handles everything below this level: the `extern "C" capsule_tools_search_issues(ptr: u32, len: u32) -> u64` entry points that Wasmtime calls, the JSON deserialisation from the input bytes, the JSON serialisation of the result, and the dispatch routing that decides which tool is being called.

You write business logic. The macro writes the WASM plumbing.

-----

## The Dependency Graph: Topological Boot Order 📐

When the kernel sees five capsules, each with their own `[imports]` and `[exports]`, it builds a dependency graph:

```
provider-openai     exports: astrid:provider/llm-provider@0.1
                    imports: astrid:kernel/http@0.1  ← kernel always available

orchestrator        exports: astrid:orchestrator/runner@0.2
                    imports: astrid:provider/llm-provider@0.1  ← needs provider!
                             astrid:tools/collection@0.1       ← needs tools!

tools-github        exports: astrid:tools/github@0.4
                    imports: astrid:kernel/http@0.1

tools-collection    exports: astrid:tools/collection@0.1
                    imports: [nothing]

frontend-cli        exports: [nothing — it is the consumer]
                    imports: astrid:orchestrator/runner@0.2    ← needs orchestrator!
```

The topological sort produces:

```
Boot order:
  1. tools-collection    (no dependencies — rides alone)
  2. provider-openai     (needs only kernel services)
  3. tools-github        (needs only kernel services)
  4. orchestrator        (needs provider + tools-collection ✓)
  5. frontend-cli        (needs orchestrator ✓)
```

If the dependency resolution fails — say, `orchestrator` needs `astrid:provider/llm-provider@0.1` but no installed capsule exports that interface — the boot fails with a clear error:

```
error[astrid::capsule::boot]: Dependency resolution failed
  Capsule 'orchestrator' requires:
    astrid:provider/llm-provider@0.1
  No installed capsule exports this interface.

  Hint: Install a provider capsule:
    capsule install provider-openai
    capsule install provider-ollama
```

The park does not open a ride without its power supply. This is the promise.

-----

## Swapping a Ride Without Stopping the Park 🔄

The most delightful aspect of the capsule system: you can replace a ride without touching the others.

```bash
# Currently running provider-openai
# We want to switch to provider-ollama for offline work

capsule uninstall provider-openai
capsule install   provider-ollama

# Restart the agent
astrid chat

# The orchestrator capsule never changed.
# It still requires astrid:provider/llm-provider@0.1
# provider-ollama now satisfies that interface
# Everything else works identically.
```

The orchestrator does not know or care whether the responses come from GPT-4 or Llama 3.2. It only knows the IPC schema. The ride changed. The park kept running.

-----

## The Host ABI: The Park’s 49-Function Syscall Table 🔌

WASM guests cannot import arbitrary host functions. They must use the defined ABI — the park’s 49-function syscall table that the kernel controls:

```
Subsystem   | Functions
────────────┬──────────────────────────────────────────────────────────
Filesystem  │ exists, read_file, write_file, mkdir, readdir, stat, unlink
IPC         │ publish, subscribe, recv (blocking), poll (non-blocking), unsubscribe
Storage     │ kv_get, kv_set, kv_delete, kv_list_keys, kv_clear_prefix
HTTP        │ request, stream_start, stream_read, stream_close
Network     │ bind_unix, accept, poll_accept, read, write, close_stream
            │ + net_connect_tcp (in v0.7.0 — TCP outbound!)
Identity    │ resolve, link, unlink, create_user, list_links
Lifecycle   │ elicit, has_secret, signal_ready, get_caller, get_config
Process     │ spawn_host, spawn_background_host, read_logs, kill_process
Approval    │ request_approval (blocks guest until human responds)
Security    │ check_capsule_capability
Hooks       │ trigger_hook, get_interceptor_handles
Clock       │ clock_ms
Logging     │ log
```

Every parameter crosses the boundary as raw bytes. The `astrid-sdk` wraps these raw syscalls in a typed, ergonomic API that mirrors Rust’s standard library layout:

```rust
// astrid-sdk maps the raw syscalls to familiar Rust patterns

use astrid_sdk::{
    fs,      // fs::read, fs::write, fs::exists — like std::fs
    net,     // net::connect_tcp — added in v0.7.0!
    http,    // http::get, http::post
    ipc,     // ipc::publish, ipc::subscribe
    kv,      // kv::get, kv::set
    env,     // env::var, env::get_config
    time,    // time::now_ms
    log,     // log::info, log::warn, log::error
    approval, // approval::request — ask the human
};
```

The ride author never thinks about `u32` pointers and byte offsets. The SDK handles it. The ride author writes Rust that looks like Rust.

-----

In **Episode 4**, the park’s electrical grid powers up. We explore the IPC event bus — how capsules talk to each other without ever calling each other directly, and why this design makes the park infinitely reconfigurable.

*The Ferris wheel is loading passengers. All aboard!* 🎡

-----

**🔗 Resources**

- **Astrid SDK**: [github.com/unicity-astrid/sdk-rust](https://github.com/unicity-astrid/sdk-rust)
- **Wasmtime**: [wasmtime.dev](https://wasmtime.dev)
- **WebAssembly Component Model**: [component-model.bytecodealliance.org](https://component-model.bytecodealliance.org)
- **Companion Repository**: [github.com/the-software-journey/astrid](https://github.com/the-software-journey/astrid)

-----

*🎡 Astrid Lunapark Series — where every episode is a new attraction, and the magic never stops.*
