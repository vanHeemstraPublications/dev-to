---
title: "Astrid Lunapark 🎡 Ep.8"
published: false
description: "Episode 8: The grand finale! Every great park eventually invites its visitors to become its builders. In this final episode we write a capsule from scratch, compile it with astrid-build, install it, assemble a complete Distro.toml park configuration, connect MCP-powered vendor stands, and open the OpenClaw gate to the JavaScript and TypeScript world. The construction yard is the most magical place in the park."
tags: [rust, ai, wasm, capsules]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/astrid-lunapark-episode-08.png"
series: "Lunapark Astrid Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 8: Build Your Own Ride

> *“All our dreams can come true, if we have the courage to pursue them. And if we have a Capsule.toml and the astrid-build toolchain.”*
> — *Walt Disney, lightly amended*

-----

## The Construction Yard Opens 🏗️

Welcome, welcome, to the most special corner of the Astrid Lunapark — the place where visitors become builders.

Every great park eventually reaches the moment where the team of brilliant imagineers opens the construction yard to the community. *“You have ridden every ride. You have seen every attraction. Now — what would YOU build?”* At Walt Disney Imagineering, this is the moment junior designers bring their first concept sketches to the table. At the Astrid Lunapark, this is the moment you open your editor, type `cargo new my-capsule`, and start adding `#[astrid::tool]` attributes.

Over the past seven episodes, you have learned the park from every angle:

- The **kernel** that never changes (Episode 2)
- The **capsule system** with its WASM isolation and manifests (Episode 3)
- The **IPC event bus** that lets rides talk without phone numbers (Episode 4)
- The **five-layer security model** with its safety inspector (Episode 5)
- The **capability tokens** and approval system (Episode 6)
- The **VFS overlay** and its copy-on-write magic (Episode 7)

Now we build. From scratch. A capsule that adds weather checking to the park. Then a complete `Distro.toml` that packages an entire agent configuration. Then a third-party MCP stand. Then the OpenClaw gate for JavaScript and TypeScript.

*Let us create something wonderful.*

-----

## 🗂️ SIPOC — The Construction Yard

|**Suppliers**         |**Inputs**                                                     |**Process**                                                                 |**Outputs**                                                                |**Customers**                                                        |
|----------------------|---------------------------------------------------------------|----------------------------------------------------------------------------|---------------------------------------------------------------------------|---------------------------------------------------------------------|
|You (the ride builder)|Rust source + `Capsule.toml` manifest                          |`astrid-build` compiles to WASM Component Model binary, computes BLAKE3 hash|A `.wasm` binary + `Capsule.toml` + hash, ready for installation           |`capsule install` — the kernel loads, verifies, and sandboxes it     |
|`astrid-sdk`          |Typed host ABI wrappers for fs, http, ipc, kv, env             |SDK generates `extern "C"` entry points via `#[capsule]` proc macro         |All WASM ABI boilerplate eliminated — you write pure business logic        |Your capsule — which feels like writing normal Rust                  |
|`Distro.toml`         |A list of capsule names, versions, and configuration           |`astrid distro apply distro.toml` resolves and boots the declared stack     |A fully configured, reproducible agent environment                         |Your users — who get the right set of rides pre-installed, every time|
|OpenClaw / MCP        |A TypeScript or JavaScript package, or an MCP-compatible server|Declared in `Capsule.toml` as `engine = "mcp"` or via `openclaw-mcp-bridge` |A third-party attraction in the park, governed by the same safety inspector|The agent — which gains tools from the JS/TS ecosystem               |

-----

## Step 1: The Capsule Skeleton 🦴

Every new ride starts with the same bones. Create the project:

```bash
# Create a new Rust library project for the capsule
cargo new --lib weather-tools
cd weather-tools

# Add the astrid-sdk dependency
# (In Cargo.toml)
```

```toml
# weather-tools/Cargo.toml
[package]
name    = "weather-tools"
version = "0.1.0"
edition = "2024"

[lib]
crate-type = ["cdylib"]   # Must be cdylib — WASM requires a dynamic library

[dependencies]
astrid-sdk = "0.7"
serde      = { version = "1", features = ["derive"] }
serde_json = "1"

[profile.release]
opt-level = "z"      # Optimise for WASM binary size
strip     = true     # Strip debug symbols
```

-----

## Step 2: Writing the Capsule Logic 🛠️

Now the fun part — the actual ride:

```rust
// weather-tools/src/lib.rs
use astrid_sdk::prelude::*;

/// The capsule's main structure.
/// #[derive(Default)] is required by the proc macro.
#[derive(Default)]
pub struct WeatherTools;

// The #[capsule] proc macro generates all WASM entry points.
// You write Rust. The macro writes WebAssembly ABI boilerplate.
#[capsule]
impl WeatherTools {

    /// Get the current weather for a location.
    ///
    /// The #[astrid::tool] attribute:
    ///   - Registers this as a callable tool in the orchestrator's tool list
    ///   - Generates the dispatch code in the WASM entry point
    ///   - Makes the docstring available as the tool's description
    #[astrid::tool]
    fn get_weather(&self, args: GetWeatherArgs) -> Result<WeatherResult, SysError> {
        // env::var reads from the capsule's scoped environment
        // NOT from std::env — the host environment is not accessible
        let api_key = env::var("OPENWEATHER_API_KEY")
            .map_err(|_| SysError::Config("OPENWEATHER_API_KEY not set".into()))?;

        // http::get uses the sandboxed HTTP client.
        // The kernel checks: is "api.openweathermap.org" in this
        // capsule's declared http_hosts capability?
        let url = format!(
            "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric",
            args.location, api_key
        );

        let response = http::get(&url)?;
        let data: serde_json::Value = response.json()?;

        // Extract the relevant fields from the API response
        let temp        = data["main"]["temp"].as_f64().unwrap_or(0.0);
        let description = data["weather"][0]["description"]
            .as_str()
            .unwrap_or("unknown")
            .to_string();
        let humidity    = data["main"]["humidity"].as_u64().unwrap_or(0);
        let city        = data["name"].as_str().unwrap_or(&args.location).to_string();

        Ok(WeatherResult { city, temp, description, humidity })
    }

    /// Get a 5-day weather forecast for a location.
    #[astrid::tool]
    fn get_forecast(&self, args: GetWeatherArgs) -> Result<ForecastResult, SysError> {
        let api_key = env::var("OPENWEATHER_API_KEY")?;

        let url = format!(
            "https://api.openweathermap.org/data/2.5/forecast?q={}&appid={}&units=metric&cnt=5",
            args.location, api_key
        );

        let response = http::get(&url)?;
        let data: serde_json::Value = response.json()?;

        let days = data["list"]
            .as_array()
            .unwrap_or(&vec![])
            .iter()
            .map(|entry| ForecastDay {
                date:        entry["dt_txt"].as_str().unwrap_or("").to_string(),
                temp:        entry["main"]["temp"].as_f64().unwrap_or(0.0),
                description: entry["weather"][0]["description"]
                    .as_str().unwrap_or("").to_string(),
            })
            .collect();

        Ok(ForecastResult { days })
    }
}

// These are standard serde types — no Astrid-specific annotations needed.
// The SDK handles JSON serialisation at the WASM boundary automatically.

#[derive(serde::Deserialize)]
pub struct GetWeatherArgs {
    /// The city name or "City,CountryCode" format
    pub location: String,
}

#[derive(serde::Serialize)]
pub struct WeatherResult {
    pub city:        String,
    pub temp:        f64,
    pub description: String,
    pub humidity:    u64,
}

#[derive(serde::Serialize)]
pub struct ForecastResult {
    pub days: Vec<ForecastDay>,
}

#[derive(serde::Serialize)]
pub struct ForecastDay {
    pub date:        String,
    pub temp:        f64,
    pub description: String,
}
```

-----

## Step 3: The Manifest — The Ride’s Instruction Manual 📋

```toml
# weather-tools/Capsule.toml

[capsule]
name        = "weather-tools"
version     = "0.1.0"
engine      = "wasm"
description = "Current weather and 5-day forecast via OpenWeatherMap API"

# What this capsule needs from other capsules or the kernel
[imports]
"astrid:kernel/http@0.1"   = "http_client"   # Sandboxed HTTP
"astrid:kernel/config@0.1" = "kernel_config" # Environment variables

# What this capsule provides to the park
[exports]
"astrid:tools/weather@0.1" = "WeatherTools"

# Which network hosts this capsule may contact
# The kernel's HTTP airlock rejects any other host
[capabilities]
http_hosts = ["api.openweathermap.org"]

# No filesystem access needed — this capsule only makes HTTP calls
# fs_read and fs_write are intentionally omitted

# IPC topics this capsule uses (for documentation and validation)
[ipc]
subscribes = ["astrid.v1.tools.execute_request"]
publishes  = ["astrid.v1.tools.execute_response"]

# Skills visible in the orchestrator's tool list
[skills]
get_weather   = "Get the current weather for a city (temperature, conditions, humidity)"
get_forecast  = "Get a 5-day weather forecast for a city"
```

-----

## Step 4: Building the Ride 🔨

```bash
# Build the capsule for the WASM Component Model target
astrid-build --manifest Capsule.toml

# What astrid-build does:
#   1. Runs: cargo build --release --target wasm32-wasip2
#   2. Adapts the output for the Component Model (via wasm-tools)
#   3. Computes a BLAKE3 hash of the .wasm binary
#   4. Writes the hash into Capsule.toml as [build.hash]
#   5. Outputs: weather-tools.wasm + Capsule.toml (updated)

# Output:
# ✓ Compiled weather-tools v0.1.0 (target/wasm32-wasip2/release/)
# ✓ Component adapted: weather-tools.wasm (142 KB)
# ✓ BLAKE3 hash: a3f9c2d1e8b04f77...
# ✓ Capsule.toml updated with [build.hash]
# 
# Capsule ready: ./dist/weather-tools.wasm
```

After building, `Capsule.toml` contains the hash:

```toml
# Added by astrid-build — do not edit manually
[build]
hash   = "a3f9c2d1e8b04f77c94b2e3d5f8a1c6b9e2d4f7a0c3b5e8d1a4f7c0b3e6d9a2"
target = "wasm32-wasip2"
sdk    = "0.7.0"
```

The kernel will verify this hash every time the capsule is loaded. Change a single byte in the binary? The hash fails. The ride does not open.

-----

## Step 5: Installing and Running 🎢

```bash
# Install from the local build
capsule install ./dist/weather-tools.wasm

# Or install from a registry (when one exists)
capsule install weather-tools@0.1.0

# Set the required API key (stored in the capsule's scoped env, not the host)
astrid config set-secret weather-tools OPENWEATHER_API_KEY=your_key_here

# Start a conversation — the weather tools are now available!
astrid chat

> What is the weather in Amsterdam right now?

Astrid: The current weather in Amsterdam is 14.2°C, partly cloudy
        with 72% humidity. Typical Dutch weather!
        
> What does the week look like?

Astrid: Here is the 5-day forecast for Amsterdam:
        Mon: 13.1°C — light rain
        Tue: 15.8°C — overcast clouds
        Wed: 17.2°C — clear sky
        Thu: 14.6°C — moderate rain
        Fri: 12.9°C — light rain
        
        Pack an umbrella. It's Amsterdam.
```

The capsule is live. The ride is open. The park is running.

-----

## Distro.toml: Packaging Your Entire Park 🎠

Once you have assembled a set of capsules that work well together, a `Distro.toml` lets you declare the complete stack as a reproducible configuration. Think of this as the park’s blueprint — ship it to a colleague and they get the same park, with the same rides, in the same configuration:

```toml
# my-dev-assistant/Distro.toml
# A complete AI development assistant distro

[distro]
name        = "dev-assistant"
version     = "1.0.0"
description = "A coding assistant with GitHub, weather, and web search tools"
author      = "your-name"

# The operating mode for this distro
[agent]
mode = "guided"

# Budget limits appropriate for a development assistant
[agent.budget]
session_tokens   = 50_000
workspace_tokens = 500_000

# Capsules to include — kernel resolves versions and dependencies
[[capsules]]
name    = "provider-openai"
version = "^0.5"
config  = { model = "gpt-4o-mini" }

[[capsules]]
name    = "orchestrator-react"
version = "^0.3"

[[capsules]]
name    = "tools-github"
version = "^0.4"

[[capsules]]
name    = "tools-web-search"
version = "^0.2"
# Requires Vera's web-search capability in Astrid's context

[[capsules]]
name    = "weather-tools"        # ← Our freshly built capsule!
version = "^0.1"

# Pre-granted capability tokens (no approval prompts for these)
[[capabilities]]
principal = "default"
resource  = "workspace://**"
action    = "fs:read"
reason    = "Dev assistant reads the workspace freely"

[[capabilities]]
principal = "default"
resource  = "workspace://src/**"
action    = "fs:write"
reason    = "Dev assistant may write to src/"

# System context injected into every session
[context]
system_prompt = """
You are a helpful development assistant. You have access to:
- GitHub tools for searching issues, creating PRs, and reading code
- Web search for documentation and current information
- Weather tools for when the developer needs a break
- Full read access to the workspace

Be concise, accurate, and proactively helpful.
"""
```

Apply the distro:

```bash
# Apply the distro — installs all capsules and configures the environment
astrid distro apply ./Distro.toml

# Installing capsules...
# ✓ provider-openai@0.5.2
# ✓ orchestrator-react@0.3.1
# ✓ tools-github@0.4.1
# ✓ tools-web-search@0.2.3
# ✓ weather-tools@0.1.0

# Applying capability grants...
# ✓ fs:read on workspace://** for default principal
# ✓ fs:write on workspace://src/** for default principal

# Distro dev-assistant v1.0.0 applied successfully.
# Run: astrid chat
```

Now ship `Distro.toml` to a colleague. One command and they have the identical park — same rides, same configuration, same capability grants. *This* is how enterprise teams deploy consistent agent environments: one distro file, version-controlled, applied reproducibly everywhere.

-----

## MCP Capsules: The Third-Party Vendor Stands 🍭

Not every attraction needs to be a compiled WASM capsule. Astrid supports MCP (Model Context Protocol) servers as native subprocess capsules — perfect for integrating existing tooling:

```toml
# mcp-postgres/Capsule.toml
# A PostgreSQL MCP server as a capsule

[capsule]
name        = "mcp-postgres"
version     = "0.1.0"
engine      = "mcp"           # Not WASM — a native subprocess!
description = "PostgreSQL query tools via MCP"

# The command to launch the MCP server
[mcp]
command = ["npx", "@modelcontextprotocol/server-postgres"]

# Environment variables the subprocess needs
env = [
    "POSTGRES_CONNECTION_STRING",   # Provided via astrid config set-secret
]

# Sandbox configuration (Linux only, via bwrap)
[sandbox]
# On Ubuntu 24.04+, requires kernel.apparmor_restrict_unprivileged_userns=0
# or set ASTRID_SANDBOX_POLICY=off for development
policy = "required"

# Capabilities this MCP server is granted
[capabilities]
# No filesystem access — only network to the postgres host
net_connect = ["postgres-host:5432"]
```

```bash
# Install the MCP capsule
capsule install ./mcp-postgres

# Provide the connection string
astrid config set-secret mcp-postgres POSTGRES_CONNECTION_STRING="postgresql://user:pass@localhost/db"

# Now in chat:
astrid chat
> How many users registered this week?

Astrid: I'll query the database for you.
        
        SELECT COUNT(*) FROM users 
        WHERE created_at >= NOW() - INTERVAL '7 days';
        
        Result: 1,247 new users in the last 7 days.
        That's 23% more than last week's 1,013!
```

The MCP server runs as a sandboxed native subprocess. The same five-layer security model applies. The agent’s capability checks fire before any MCP tool call executes. The same audit trail records every query.

-----

## OpenClaw: The JavaScript and TypeScript Gate 🐾

For the JavaScript and TypeScript ecosystem, Astrid provides **OpenClaw** — a bridge that wraps npm packages as Astrid capsules. The `packages/openclaw-mcp-bridge` in the main repository enables this connection:

```toml
# openclaw-slack/Capsule.toml
# A Slack integration capsule written in TypeScript

[capsule]
name        = "openclaw-slack"
version     = "0.2.0"
engine      = "mcp"            # OpenClaw tools appear as MCP capsules
description = "Post messages and read channels via Slack API"

[mcp]
# The openclaw-mcp-bridge hosts the TypeScript plugin
command = ["astrid-openclaw", "run", "openclaw-slack-plugin"]

[capabilities]
http_hosts  = ["slack.com", "api.slack.com", "hooks.slack.com"]
```

The TypeScript plugin itself:

```typescript
// openclaw-slack-plugin/src/index.ts
// TypeScript tools that become Astrid capsule tools via OpenClaw

import { defineTool, AstridPlugin } from "@astrid/openclaw-sdk";

export default {
  name: "slack-tools",
  version: "0.2.0",

  tools: [
    defineTool({
      name: "post_message",
      description: "Post a message to a Slack channel",
      schema: {
        type: "object",
        properties: {
          channel: { type: "string", description: "Channel name or ID" },
          text:    { type: "string", description: "The message text" },
        },
        required: ["channel", "text"],
      },
      async execute({ channel, text }) {
        // The astrid-openclaw-sdk provides a sandboxed http module
        // that routes through the host ABI, not Node's native fetch
        const { http } = await import("@astrid/openclaw-sdk/http");

        const token = await astrid.env.var("SLACK_BOT_TOKEN");
        const resp  = await http.post(
          "https://slack.com/api/chat.postMessage",
          { channel, text },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        return { ok: resp.data.ok, ts: resp.data.ts };
      },
    }),

    defineTool({
      name: "list_channels",
      description: "List public Slack channels",
      schema: { type: "object", properties: {} },
      async execute() {
        const { http } = await import("@astrid/openclaw-sdk/http");
        const token    = await astrid.env.var("SLACK_BOT_TOKEN");
        const resp     = await http.get(
          "https://slack.com/api/conversations.list",
          { headers: { Authorization: `Bearer ${token}` } }
        );
        return { channels: resp.data.channels.map((c: any) => c.name) };
      },
    }),
  ],
} satisfies AstridPlugin;
```

The JavaScript ecosystem’s tools — Slack, Notion, Linear, Jira, anything with an npm package — can become Astrid capsule attractions through OpenClaw. The safety inspector still checks every action. The wristband system still applies. The audit trail still records everything. It is just TypeScript under the hood instead of Rust.

-----

## The Self-Modifying Agent: The Park That Builds Its Own Rides ✨

Here is the most breathtaking possibility in the entire Astrid architecture — the thing that makes it genuinely different from every framework that came before.

An agent can write a new capsule, build it, install it, and use it — all within a running session:

```
Session begins:
  Agent: "I need to query our internal analytics API, 
          but I don't have a tool for that yet."

Agent writes Rust code:
  → Writes capsule source to workspace://capsules/analytics-tools/src/lib.rs
  → Writes Capsule.toml to workspace://capsules/analytics-tools/Capsule.toml
  
Agent builds the capsule:
  → Calls: astrid_spawn_host("astrid-build", ["--manifest", "Capsule.toml"])
  → Waits for build to complete (via IPC or process poll)
  
Agent installs the capsule:
  → Calls: astrid_spawn_host("capsule", ["install", "./dist/analytics-tools.wasm"])
  [Approval prompt: "May I install a new capsule: analytics-tools?"]
  Human: Allow Once
  → Capsule installed
  
Agent uses the new capsule:
  → Publishes to astrid.v1.tools.execute_request with tool="get_analytics"
  → Receives the result via astrid.v1.tools.execute_response

Session ends. The new capsule persists if committed.
```

The agent extended its own operating system at runtime. It added a new tool to its own park. Within the capability sandbox. With human approval at the critical install step. With a permanent audit record of every file written, every build invoked, every capsule installed.

The park’s grandest attraction is the one the agent builds itself.

-----

## The Complete Park: Series Finale 🎡

We have come so far together, visitor. Let us pause at the Grand Central Pavilion and look out at everything we have built:

|Episode|The Attraction                    |What We Built Together                                                                                     |
|-------|----------------------------------|-----------------------------------------------------------------------------------------------------------|
|1      |The Entrance Gates                |We understood what Astrid is: an OS for AI agents                                                          |
|2      |The Grand Central Pavilion        |We explored the fixed, unforkable kernel and its 27 crates                                                 |
|3      |The First Rides                   |We learned the capsule system, WASM isolation, and the `#[capsule]` macro                                  |
|4      |The Electrical Grid               |We traced messages through the IPC publish-subscribe event bus                                             |
|5      |The Safety Inspector              |We walked all five security layers: Policy→Token→Budget→Approval→Audit                                     |
|6      |The Wristband Office              |We minted capability tokens, explored approval modes, and managed budgets                                  |
|7      |The Park Map                      |We understood the copy-on-write VFS overlay and its path safety guarantees                                 |
|8      |*This one* — The Construction Yard|We built a capsule, packaged a distro, added MCP, opened OpenClaw, and watched the agent build its own ride|

-----

## What Comes Next: The Park Never Finishes Growing 🌟

Astrid is a living park. As of v0.7.0, the work continues:

**Coming in the next releases:**

- Outbound TCP connections for capsules (`net_connect_tcp` — already in Unreleased)
- More capsule ecosystem: providers, orchestrators, tool packs
- A registry for discovering and installing community capsules
- Improved unikernel deployment for production workloads
- Richer multi-principal workflows for team environments

The kernel stays fixed. The attractions multiply. The magic never stops.

Every great park began with an idea, a blueprint, and someone willing to pick up a hammer. You have the ideas. Astrid gives you the blueprint. The construction yard is open.

*Go build something wonderful.* 🎡

-----

**🔗 Resources**

- **Astrid Repository**: [github.com/unicity-astrid/astrid](https://github.com/unicity-astrid/astrid)
- **Companion Repository**: [github.com/the-software-journey/astrid](https://github.com/the-software-journey/astrid)
- **Astrid SDK (Rust)**: [github.com/unicity-astrid/sdk-rust](https://github.com/unicity-astrid/sdk-rust)
- **CHANGELOG**: [github.com/unicity-astrid/astrid/blob/main/CHANGELOG.md](https://github.com/unicity-astrid/astrid/blob/main/CHANGELOG.md)
- **Contributing**: [github.com/unicity-astrid/astrid/blob/main/CONTRIBUTING.md](https://github.com/unicity-astrid/astrid/blob/main/CONTRIBUTING.md)

-----

*🎡 Astrid Lunapark Series — eight episodes, one park, infinite possibilities. The gates are always open.*
