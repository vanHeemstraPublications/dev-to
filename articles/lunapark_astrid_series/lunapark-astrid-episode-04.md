---
title: "Astrid Lunapark 🎡 Ep.4"
published: false
description: "Episode 4: In any great amusement park, the rides don’t talk to each other directly — they run on a shared electrical grid that carries signals everywhere at once. Astrid’s IPC event bus is that grid: a publish-subscribe system where capsules broadcast their news and listen for what matters, without ever needing each other’s phone numbers. Come discover how the park stays in sync."
tags: [rust, ipc, ai, architecture]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/astrid-lunapark-episode-04.png"
series: "Lunapark Astrid Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 4
---

## Episode 4: The Electrical Grid — The IPC Event Bus

> *“It’s kind of fun to do the impossible — like having 20 different rides all talk to each other without any of them knowing the others exist.”*

-----

## The Park’s Invisible Infrastructure ⚡

Have you ever noticed that in a great amusement park, the rides seem to know things about each other? The log flume sends a signal that a boat has departed, and the safety gates on the loading dock open for the next group. The roller coaster’s lift hill motor accelerates and the sound system begins its anticipatory fanfare — all in perfect synchrony.

None of those systems talk to each other *directly*. They all connect to the park’s central electrical grid and signal bus. One ride publishes an event: *“boat departed.”* Every other system that cares about boat departures receives that event and acts accordingly. Systems that do not care simply ignore it.

Astrid’s **IPC event bus** is exactly this: a park-wide publish-subscribe system that lets capsules communicate without ever knowing each other’s addresses, types, or internal implementations. The provider capsule and the orchestrator capsule never import each other. They speak the same language — the event schema — and the bus carries the messages.

-----

## 🗂️ SIPOC — The Electrical Grid

|**Suppliers**               |**Inputs**                                                  |**Process**                                                            |**Outputs**                                                                                                        |**Customers**                                                           |
|----------------------------|------------------------------------------------------------|-----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
|Publishing capsule          |A typed message payload serialised as bytes + a topic string|`astrid_ipc_publish(topic, payload)` — kernel routes to all subscribers|The message delivered to every capsule subscribed to that topic                                                    |All subscribing capsules — which receive the event and act on it        |
|Subscribing capsule         |A topic string to listen on                                 |`astrid_ipc_subscribe(topic)` — kernel registers interest              |A subscription handle; future messages on that topic arrive via `astrid_ipc_recv`                                  |The capsule’s message processing loop                                   |
|The WIT interface definition|Typed message schemas in `.wit` files                       |Capsules agree on the event schema through the WIT interface contract  |Interoperability: any capsule that speaks `astrid:provider/llm-response@0.1` can receive messages from any provider|The entire park — schema agreement enables infinite capsule combinations|

-----

## Why Not Direct Function Calls? 🤔

The most natural question: why not just call the provider capsule’s `generate()` function directly? Why the pub-sub indirection?

Imagine the roller coaster at the park needed to be *programmatically connected* to every other ride. Every ride would need the roller coaster’s exact API. If the roller coaster upgraded, every other ride would need to update its binding. If you wanted to replace the roller coaster, every connected ride would need surgery.

The IPC bus inverts this entirely:

```
Without IPC (direct coupling):
  Orchestrator ──calls──► Provider.generate()
                ──calls──► Tools.execute()
  
  Change Provider? Orchestrator breaks.
  Add a caching layer? Rewrite Orchestrator.
  Run two providers? Orchestrator needs to know about both.

With IPC (loose coupling):
  Orchestrator ──publishes──► "astrid.v1.llm.request"
  Provider ◄──subscribes─── "astrid.v1.llm.request"
  Provider ──publishes──► "astrid.v1.llm.response"
  Orchestrator ◄──subscribes─── "astrid.v1.llm.response"
  
  Change Provider? Different capsule, same topics. Orchestrator unchanged.
  Add a caching layer? Subscribe to the request, intercept before provider.
  Run two providers? Both subscribe to the request topic. A router capsule picks.
```

The bus is the magic. Capsules are co-workers who communicate through the company intranet, not through personal phone numbers.

-----

## The Five IPC Syscalls: The Grid’s Control Panel 🔌

```rust
// The complete IPC syscall surface (from the host ABI)
// Available to every capsule via astrid-sdk

use astrid_sdk::ipc;

// 1. Subscribe — register interest in a topic
let handle = ipc::subscribe("astrid.v1.llm.response")?;

// 2. Publish — broadcast a message to all subscribers
ipc::publish(
    "astrid.v1.llm.request",
    &LlmRequest {
        messages: vec![Message { role: "user", content: "Hello!" }],
        model:    "gpt-4o-mini",
        max_tokens: Some(1024),
    }
)?;

// 3. Recv — blocking receive (waits for next message on subscription)
let msg: IpcMessage = ipc::recv(handle)?;
let response: LlmResponse = msg.payload()?;

// 4. Poll — non-blocking receive (returns None if nothing waiting)
if let Some(msg) = ipc::poll(handle)? {
    // process message
}

// 5. Unsubscribe — remove interest in a topic
ipc::unsubscribe(handle)?;
```

-----

## A Complete Conversation: Following a Message Through the Park 🎙️

Let us trace a single user message as it travels through the IPC system from the frontend to the provider and back:

```
╔════════════════════════════════════════════════════════════════════╗
║              IPC MESSAGE JOURNEY: "What is Rust?"                 ║
╠════════════════════════════════════════════════════════════════════╣

[1] USER types: "What is Rust?"
    │
    ▼
[2] frontend-cli PUBLISHES to "astrid.v1.chat.user_message":
    {
      "content": "What is Rust?",
      "session": "sess_abc123",
      "timestamp": 1748966400000
    }

[3] orchestrator RECEIVES from "astrid.v1.chat.user_message"
    (it subscribed during boot)
    │
    ▼
[4] orchestrator decides: this is a question, send to LLM
    orchestrator PUBLISHES to "astrid.v1.llm.request":
    {
      "messages": [
        {"role": "system", "content": "[system prompt]"},
        {"role": "user",   "content": "What is Rust?"}
      ],
      "model": "gpt-4o-mini",
      "session": "sess_abc123"
    }

[5] (optional) interceptor-cache RECEIVES the llm.request
    Cache check: have we seen this prompt before?
    → Cache MISS → let it through, do not publish a response

[6] provider-openai RECEIVES from "astrid.v1.llm.request"
    Calls OpenAI API with the payload
    │
    ▼
[7] provider-openai PUBLISHES to "astrid.v1.llm.response":
    {
      "content": "Rust is a systems programming language...",
      "model":   "gpt-4o-mini",
      "tokens":  { "prompt": 45, "completion": 120 },
      "session": "sess_abc123"
    }

[8] interceptor-cache RECEIVES the response → caches it for next time

[9] orchestrator RECEIVES from "astrid.v1.llm.response"
    Decides: no tool calls needed, forward to user

[10] orchestrator PUBLISHES to "astrid.v1.chat.assistant_message":
     {
       "content": "Rust is a systems programming language...",
       "session": "sess_abc123"
     }

[11] frontend-cli RECEIVES from "astrid.v1.chat.assistant_message"
     Renders the response to the terminal

╚════════════════════════════════════════════════════════════════════╝
```

Eleven steps. Zero direct function calls between capsules. The orchestrator has no idea whether it talked to OpenAI or Ollama. The cache interceptor slipped in between steps 5 and 8 without anyone needing to know it existed. The frontend never touched the LLM.

-----

## The Topic Namespace: The Park’s Broadcasting Frequency 📻

Astrid uses a hierarchical topic naming convention that makes the IPC bus self-documenting:

```
astrid.v1.{domain}.{event}

Examples:
  astrid.v1.chat.user_message          ← User said something
  astrid.v1.chat.assistant_message     ← Agent replied
  astrid.v1.llm.request                ← Orchestrator wants an LLM response
  astrid.v1.llm.response               ← Provider delivers an LLM response
  astrid.v1.llm.stream_chunk           ← Streaming token arriving
  astrid.v1.tools.execute_request      ← Orchestrator wants a tool called
  astrid.v1.tools.execute_response     ← Tool returns its result
  astrid.v1.approval.request           ← Capsule asking for human approval
  astrid.v1.approval.response          ← Human decided
  astrid.v1.admin.principal.created    ← New principal added
  astrid.v1.admin.group.updated        ← Group permissions changed
```

Capsule manifests can declare their IPC topics, making the dependency clear even before the capsule runs:

```toml
# In Capsule.toml — the ride's declared broadcasting and listening frequencies
[ipc]
publishes = [
    "astrid.v1.llm.response",         # I broadcast LLM responses
    "astrid.v1.llm.stream_chunk",      # I also stream tokens
]
subscribes = [
    "astrid.v1.llm.request",           # I listen for requests to process
]
```

-----

## The Transparent Caching Capsule: A Magic Trick 🎩

One of the most powerful demonstrations of the IPC architecture is the transparent caching capsule. Here is a capsule that dramatically reduces LLM costs, and the orchestrator and provider have absolutely no idea it exists:

```rust
// A caching capsule — intercepts LLM requests and responses
use astrid_sdk::prelude::*;
use std::collections::HashMap;

#[derive(Default)]
pub struct LlmCache {
    // In a real implementation, this would use astrid_sdk::kv
    // for persistence across sessions
}

#[capsule]
impl LlmCache {
    // This runs as the capsule's main event loop
    #[astrid::run]
    async fn run(&self) -> Result<(), SysError> {
        let req_handle  = ipc::subscribe("astrid.v1.llm.request")?;
        let resp_handle = ipc::subscribe("astrid.v1.llm.response")?;

        loop {
            // Poll both subscriptions non-blocking
            if let Some(msg) = ipc::poll(req_handle)? {
                let req: LlmRequest = msg.payload()?;
                let cache_key = self.compute_cache_key(&req);

                // Check the KV store for a cached response
                if let Ok(cached) = kv::get(&format!("llm_cache:{}", cache_key)) {
                    log::info!("Cache HIT — saving one LLM call!");
                    // Publish the cached response directly
                    // The provider never receives this request
                    ipc::publish("astrid.v1.llm.response", &cached)?;
                    continue; // Skip — provider gets nothing
                }
                // Cache miss — the request flows through to the provider normally
                // We do nothing; provider-openai will get the message via its own subscription
            }

            if let Some(msg) = ipc::poll(resp_handle)? {
                let resp: LlmResponse = msg.payload()?;
                // Store the response for next time
                if let Some(key) = msg.request_correlation() {
                    kv::set(&format!("llm_cache:{}", key), &resp)?;
                }
            }

            // Tiny sleep to avoid busy-looping
            time::sleep_ms(5);
        }
    }

    fn compute_cache_key(&self, req: &LlmRequest) -> String {
        // Hash the messages content for the cache key
        use std::hash::{Hash, Hasher};
        let mut hasher = std::collections::hash_map::DefaultHasher::new();
        format!("{:?}", req.messages).hash(&mut hasher);
        format!("{:x}", hasher.finish())
    }
}
```

Install this capsule and it quietly subscribes to both `llm.request` and `llm.response`. Seen this prompt before? It publishes the cached response and the provider never receives the request. New prompt? It does nothing and the provider handles it normally.

The orchestrator capsule is unchanged. The provider capsule is unchanged. The caching behaviour was added to a running park by installing one new capsule.

*Now THAT is magic.*

-----

## Declaring IPC in the Capsule Manifest: The Park’s Frequency List 📡

The kernel validates IPC usage against capability declarations. If your capsule subscribes to a topic it has not declared in `[ipc]`, the kernel flags it:

```toml
# tools-github/Capsule.toml — full example
[capsule]
name    = "tools-github"
version = "0.4.1"
engine  = "wasm"

[imports]
"astrid:kernel/http@0.1"   = "http_client"
"astrid:tools/executor@0.1" = "tool_executor"

[exports]
"astrid:tools/github@0.4" = "GitHubTools"

[ipc]
subscribes = [
    "astrid.v1.tools.execute_request",   # I listen for tool execution requests
]
publishes = [
    "astrid.v1.tools.execute_response",  # I broadcast tool results
]

[capabilities]
http_hosts = ["api.github.com"]
fs_read    = ["workspace://"]
```

The manifest is the ride’s complete declaration of everything it does. Read the manifest, know the ride. No surprises.

-----

In **Episode 5**, the safety inspector arrives. We walk through all five layers of Astrid’s security model — from the hard-block policy rules that cannot be overridden, all the way to the tamper-proof audit trail that records everything that ever happened.

*The safety inspector’s torch lights up the park. All is accounted for!* 🔦

-----

**🔗 Resources**

- **IPC in Astrid README**: [github.com/unicity-astrid/astrid#the-host-abi](https://github.com/unicity-astrid/astrid#the-host-abi)
- **WIT interface definitions**: [github.com/unicity-astrid/wit](https://github.com/unicity-astrid/wit)
- **Companion Repository**: [github.com/the-software-journey/astrid](https://github.com/the-software-journey/astrid)

-----

*🎡 Astrid Lunapark Series — where every episode is a new attraction, and the magic never stops.*
