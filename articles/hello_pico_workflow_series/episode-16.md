---
title: "🔔 Home Assistant Discovers Pico, and Learns to Say Hello Back"
series: "Hello Pico Workflow"
part: 16
organization: "the-software-s-journey"
tags: [open-engineering, pico, home-assistant, mqtt, events]
---

## 🔔 Home Assistant Discovers Pico, and Learns to Say Hello Back

Nothing manual left to do here — that's rather the point of this episode. Because Manifold publishes its MQTT discovery definition and current state the moment it starts up (Episode 7), all that's left is to go look. In Home Assistant: **Settings → Devices & services → MQTT**, and you should now find:

```
Hello Pico
```

with entities:

```
Status
ready
Message
Hello, Pico!
Version
0.1.0
Event Count
0
Last Run
unknown
```

This is the moment the original Open Engineering goal from Episode 1 actually pays off: the first Pico culminates in a declaratively composed device visible inside Home Assistant, not just terminal output somewhere.

Now let's send it a real event, the way an operator actually would, through Wrangler:

```bash
wrangler pico event \
  hello-pico \
  hello \
  --name Willem
```

Wrangler sends `{"type": "hello", "name": "Willem"}` to Manifold, which runs the exact same chain we verified back in Gate 5 — Python down through PyO3 into `HelloPico::hello()` — and gets back:

```json
{
  "message": "Hello, Willem! I am Pico hello-pico.",
  "event_count": 1,
  "last_run": "..."
}
```

Manifold publishes that changed state to MQTT, and — with no polling, no manual refresh, no Home Assistant REST-API scraping of any kind — Home Assistant updates automatically:

```
Message
Hello, Willem! I am Pico hello-pico.
Event Count
1
Last Run
2026-08-19 ...
```

It's worth sitting with how unusual that is if you're coming from a polling-based mental model, like I was: nobody asked Home Assistant to go check. It changed because the underlying state changed, and that change propagated automatically over MQTT. That's an actual event-driven system, not a dashboard refreshing on a timer.

Now let's close the loop entirely, so Home Assistant isn't just a spectator. Add one more component: `button.hello_pico_say_hello`, with its MQTT command topic set to the same command topic Manifold already subscribes to:

```
openengineering/pico/hello-pico/command
```

Pressing that button sends:

```json
{
  "type": "hello",
  "name": "Home Assistant"
}
```

and the state becomes:

```
Hello, Home Assistant! I am Pico hello-pico.
```

with `event_count = 2`. That gives us a complete event cycle, in both directions:

```
               ┌───────────────┐
               │Home Assistant │
               └───────┬───────┘
                       │
                       │ hello event
                       ▼
                   Mosquitto
                       │
                       ▼
                    Manifold
                       │
                       ▼
                     PyO3
                       │
                       ▼
                   Rust Pico
                       │
                 state transition
                       │
                       ▼
                    Manifold
                       │
                       ▼
                   Mosquitto
                       │
                       ▼
               ┌───────────────┐
               │Home Assistant │
               │ Event Count 2 │
               └───────────────┘
```

Every layer this series has built — Rust, PyO3, Manifold, MQTT, Crossplane, Kubernetes, Wrangler — is now visible in one loop a human can trigger with a single button press. That's an excellent teaching demo, and honestly, the moment the whole architecture clicked for me.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Manifold's discovery message (Episode 7) | The running Pico, publishing on startup | Home Assistant auto-discovers the device with no manual config | A visible "Hello Pico" device with five live entities | Anyone viewing Home Assistant's MQTT integration page |
| `wrangler pico event ... --name Willem` | An operator-issued command | Route the event through Manifold, PyO3, and Rust, then republish state | A live-updating Home Assistant device, no polling involved | The person watching Home Assistant update in real time |
| `button.hello_pico_say_hello` | A press from inside Home Assistant | Publish a `hello` command back onto the command topic | A closed, bidirectional event loop | The Pico itself, completing the full cycle back to Home Assistant |

Next stop: what happens to all of this the moment a pod dies — persistence, and making sure a Pico is a long-lived entity, not just a function call.
