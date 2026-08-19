---
title: "📝 Defining the Pico Declaratively"
series: "Hello Pico Workflow"
part: 3
organization: "the-software-s-journey"
tags: [open-engineering, pico, yaml, declarative]
---

## 📝 Defining the Pico Declaratively

This is the file I found myself rereading a few times, because what it *doesn't* say turned out to matter as much as what it does. Here's `definitions/pico.yaml` in full:

```yaml
apiVersion: pico.open-engineering.io/v1alpha1
kind: Pico
metadata:
  name: hello-pico
  namespace: open-engineering
spec:
  id: hello-pico
  version: 0.1.0
  runtime:
    image: open-engineering/hello-pico:0.1.0
  state:
    status: ready
    message: "Hello, Pico!"
  handlers:
    - event: hello
      action: greet
  channels:
    mqtt:
      stateTopic: openengineering/pico/hello-pico/state
      commandTopic: openengineering/pico/hello-pico/command
      availabilityTopic: openengineering/pico/hello-pico/availability
```

Now notice something important, because it's the whole design principle this series keeps coming back to: **this contains no Deployment, Service, container port, or replica count.** Nothing about *how* this thing gets scheduled, exposed, or scaled. It states an identity (`id`, `version`), the runtime image to use, its initial state, which events it responds to, and which MQTT topics carry its state and commands. That's it.

That's the separation this whole architecture is built around:

```
Pico Definition
      ↓
what it IS
Crossplane Composition
      ↓
how it RUNS
```

As a newcomer, this is the moment the rest of the stack started making sense to me. `pico.yaml` is a contract about identity and behavior — what events does this thing accept, what does it call itself, what does it say when it starts up. Everything about *how* that behavior gets realized as actual Kubernetes objects — a Deployment with however many replicas, a Service on whatever port, a ConfigMap holding whatever environment variables — belongs to a completely different file, one we won't write until Crossplane enters the picture several episodes from now. Keeping those two concerns apart is exactly what lets someone author a Pico without knowing anything about Kubernetes at all, and lets someone operate the Kubernetes side without needing to understand Pico semantics.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Pico author | An identity, initial state, event handlers, and MQTT topic names | Write a `Pico` custom resource in `definitions/pico.yaml` | A declarative description of what the Pico *is* | Wrangler, and eventually Crossplane's Composition |
| The `handlers` list | The `hello` event name mapped to a `greet` action | Declare which events this Pico responds to | A documented, discoverable event contract | Anyone sending events to this Pico, including Home Assistant |
| The `channels.mqtt` block | Three topic names (state, command, availability) | Declare where this Pico's state and commands live on the MQTT bus | A fixed, predictable MQTT contract | Manifold (publishing/subscribing) and Home Assistant (discovering) |

Next stop: Gate 1 — writing the actual Rust state machine this whole declaration is describing.

