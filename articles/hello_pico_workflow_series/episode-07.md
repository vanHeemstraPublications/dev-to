---
title: "Hello Pico Workflow 📡 Ep.7"
series: "Hello Pico Workflow"
part: 7
organization: "the-software-s-journey"
tags: [open-engineering, pico, mqtt, home-assistant, discovery]
---

## Episode 7: MQTT and Home Assistant Discovery

Here's a design decision I appreciated once I understood it: the Pico itself should never know anything about Home Assistant. Not its existence, not its entity model, nothing. Instead, there's a clean relay:

```
Pico
 ↓
event/state
 ↓
Manifold
 ↓
MQTT
 ↓
Home Assistant
```

Manifold is the only layer that knows both languages. It talks to the Pico in plain function calls, and it talks to the outside world in MQTT, using three topics — the same ones declared back in `pico.yaml`'s `channels.mqtt` block in Episode 3:

```
openengineering/pico/hello-pico/state
openengineering/pico/hello-pico/command
openengineering/pico/hello-pico/availability
```

After every state transition, Manifold publishes the new state, retained so a freshly-connecting subscriber immediately sees the current value rather than waiting for the next change:

```python
client.publish(
    "openengineering/pico/hello-pico/state",
    json.dumps(state),
    retain=True,
)
```

And it subscribes to the command topic, so the Pico can be told to do something *from* MQTT, not just report state *to* it:

```python
if payload["type"] == "hello":
    state = json.loads(
        pico.hello(payload["name"])
    )
    publish_state(state)
```

That gives us both directions of traffic, cleanly:

```
Pico ───── state ─────► Home Assistant
Pico ◄──── event ───── Home Assistant
```

Now, rather than hand-defining five separate Home Assistant sensors — status, message, version, event count, last run — Manifold publishes one retained MQTT discovery message describing the whole device at once:

```
homeassistant/device/hello-pico/config
```

Home Assistant enables MQTT discovery by default once its MQTT integration is configured, using the standard `homeassistant` discovery prefix — so this one retained message is genuinely all it takes. The device it describes exposes:

```
Hello Pico
├── Status
├── Message
├── Version
├── Event Count
└── Last Run
```

all reading from that same common state topic, `openengineering/pico/hello-pico/state`. Current Home Assistant guidance specifically recommends *device* discovery for exactly this situation — one device offering multiple related components — rather than publishing five unrelated, independently-discovered sensors that happen to share a name prefix. That's precisely the semantic model we want: Pico becomes one coherent Home Assistant device, not a scattering of coincidentally related entities.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Manifold (state publisher) | The Pico's state after every transition | Publish a retained JSON message to the state topic | An always-current state snapshot on MQTT | Home Assistant, and any other MQTT subscriber |
| Manifold (command subscriber) | Incoming messages on the command topic | Parse the payload and call the matching Pico method | A triggered state transition, originating from outside HTTP | The Pico core, and the state topic it republishes to |
| Manifold's discovery publisher | A description of the Pico's fields (status, message, version, event count, last run) | Publish one retained discovery message under `homeassistant/device/hello-pico/config` | A single Home Assistant device with five related entities | Home Assistant's MQTT integration |

Next stop: proving the Python binding actually works with a real test, and setting up the `just` commands that will carry us through the rest of this series.
