---
title: "Luxo Jr. ThingsBoard 🎬 Ep.1"
part: 1
published: false
description: "Episode 1: Luxo Jr. was just a desk lamp until Lasseter gave it joints, personality, and story. Your IoT device is just hardware until ThingsBoard gives it telemetry, attributes, dashboards, and rules. Meet the platform that animates your things."
tags: [iot, thingsboard, beginners, homeautomation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/stage-props-thingsboard-episode-01.png"
series: "Luxo Jr. ThingsBoard Series"
canonical_url: ""
organization: "the-software-s-journey"
---
## Episode 1: The Prop That Came Alive

> “The question is not whether a lamp can have a personality. The question is whether you are willing to do the work to give it one.”— paraphrasing John Lasseter, very liberally

## A Desk Lamp That Changed Everything 💡

In 1986, John Lasseter had a real Luxo brand desk lamp on his drawing table. He had been using it as a rendering model — studying how light fell on its surfaces, how its joints articulated. It was a prop. An inert object. A piece of hardware.

Then he gave it joints. He gave it movement. He gave it *reaction* — a curious tilt of the head when the ball rolled by, a deflated slump when the ball burst, an instant excited pivot when something bigger and bouncier appeared. He gave it a story.

Within two minutes of film, the audience at SIGGRAPH 1986 was on its feet screaming. Not because the lamp was technically impressive — though it was. Because they had forgotten it was a lamp. It had become, impossibly, *something alive*.

This is the precise ambition of the IoT platform **ThingsBoard**: to take your physical hardware — sensors, actuators, meters, controllers — and give them the equivalent of Lasseter’s joints. Telemetry. Attributes. Dashboards. Rules. Relationships. Commands. To animate the inert thing and turn it into something you can watch, understand, and direct.

In this series, we build stage props. We give them personality. By Episode 8, they will perform.

## 🗂️ SIPOC — The Stage

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| Physical devices (sensors, actuators, meters) | Raw telemetry data: temperature, humidity, power, position | ThingsBoard: ingest, store, visualise, process, alert | Live dashboards, alarm notifications, RPC commands, analytics | Operators, homeowners, engineers, stakeholders — anyone who needs to see and act on what devices are doing |
| Home Assistant (Ep.7) | Entity states and sensor readings via MQTT | MQTT bridge: HA → ThingsBoard for enterprise-scale visualisation | Enterprise dashboard showing all HA devices alongside industrial sensors | IT/OT teams bridging consumer smart home with professional IoT |
| ThingsBoard AI Solution Creator (Ep.6) | A plain-language description of your use case | AI agent: generates entity profiles, dashboards, alarm rules, roles | A working prototype of your IoT solution in under 10 minutes | System integrators, explorers, business stakeholders doing PoC |

## The Stage Props Metaphor 🎭

Every stage production has **props** — the physical objects on stage that the cast interacts with: lamps, chairs, telephones, clocks. A prop sitting in the prop house is inert. It has physical properties (weight, colour, shape) but no story, no behaviour, no relationship to anything else.

Bring the prop onto the stage and give it context:

- A **position** (where on the stage it sits)
- A **character** (what role it plays in the story)
- **Joints** (how it can move and change)
- **Cues** (when it does something — the lamp flickers when the villain enters)
- A place on the **prompt book** (the director’s master view of the whole production)

This is exactly what ThingsBoard does to a physical sensor or actuator:

| Stage props world | ThingsBoard world |
| --- | --- |
| An inert prop in the prop house | A sensor with no platform — just hardware |
| Giving the prop joints & articulation | Registering a Device with a Device Profile |
| The prop’s observable state | Telemetry — timestamped key-value data the device sends |
| The prop’s fixed characteristics | Attributes — static properties (location, model number, threshold) |
| Grouping props on the same set | Assets — logical containers (rooms, floors, buildings) |
| The director’s prompt book | The Dashboard — master view of the whole production |
| A lighting cue (“if lamp > 50°C → warn director”) | An Alarm Rule — automated trigger on telemetry threshold |
| The director calling “Action!” | An RPC command — instructing a device to do something |
| The Pixar logo animation | Your finished, running, production-grade IoT solution |

Luxo Jr. had one prop — a desk lamp — and gave it so much personality that it became a mascot seen before every Pixar film for forty years. You have sensors, meters, and controllers. ThingsBoard gives them the same treatment.

## What ThingsBoard Actually Is 🏗️

ThingsBoard is an **open-source IoT platform** for data collection, processing, visualisation, and device management. It is production-grade: companies use it to manage tens of thousands of devices across smart energy, fleet tracking, agriculture, smart buildings, and industrial automation.

### The key capabilities

**Device connectivity** — ThingsBoard speaks MQTT, HTTP, CoAP, LwM2M, and more. Any device that can transmit data via one of these protocols can connect. If it cannot, the ThingsBoard IoT Gateway (Python, open-source) acts as a translator.

**Telemetry and attributes** — Every data point a device sends is stored as a timestamped key-value pair. Device metadata (location, firmware version, thresholds) is stored as attributes — permanent properties rather than time-series values.

**Dashboards and widgets** — A rich, configurable UI for visualising your data: time-series charts, gauges, maps, alarm tables, entity lists, and custom widgets. Dashboards are built by wiring widgets to device telemetry and attributes.

**Rule Engine** — A visual, flow-based processing system. Incoming messages pass through chains of nodes that filter, transform, and react. An alarm fires. An email sends. A command goes back to the device. A Kafka message is published.

**Entity model** — Devices, Assets, Customers, Users, and more — all connected via typed relations. A building contains floors, which contain rooms, which contain devices. The hierarchy is modelled explicitly.

**Alarms** — When telemetry crosses a threshold, ThingsBoard creates an alarm, propagates it up the entity hierarchy, and notifies the appropriate users via the Notification Centre.

### Which edition?

| Edition | Best for | Cost |
| --- | --- | --- |
| Community Edition (CE) | Self-hosted, learning, open-source projects | Free (Apache 2.0) |
| Professional Edition (PE) | Enterprise features: platform integrations, entity groups, white-labelling | Commercial licence |
| Cloud | Zero-setup SaaS — US or EU regions | Free tier + paid plans |

For this series, everything works on Community Edition and Cloud. Where PE-specific features appear, they are labelled.

## ThingsBoard and Home Assistant: Two Stages, One Show 🏠

Home Assistant (HA) is your *personal* stage — the smart home controller that knows Rianne’s heating schedule, whether Beau and Elvis are in the garden, and which lights to turn off at bedtime.

ThingsBoard is the *enterprise* stage — built for industrial-scale telemetry, multi-tenant isolation, hierarchical entity models, and professional dashboards.

They are not competitors. They are collaborators. In Episode 7, we bridge them via MQTT — HA publishes its entity states to ThingsBoard’s MQTT broker. ThingsBoard ingests them as device telemetry, displays them on dashboards alongside other sensors, and applies alarm rules that HA has no native concept of.

The result: your home’s Luxo Jr. lamp plays alongside industrial-scale equipment on the same stage. The prompt book covers both.

## The Series Map: Eight Episodes 🎬

| # | Episode | Stage props concept |
| --- | --- | --- |
| 1 | This one — What ThingsBoard is | The prop house and the stage |
| 2 | Devices, Assets, Profiles, Relations | Building the set |
| 3 | MQTT, HTTP, telemetry, attributes | The prop speaks |
| 4 | Dashboards and widgets | The prompt book |
| 5 | Rule Engine, alarms, notifications | The director’s cue sheet |
| 6 | AI Solution Creator | Animating the lamp in 10 minutes |
| 7 | Home Assistant ↔ ThingsBoard via MQTT | Two stages, one show |
| 8 | Production deployment, ThingsBoard Edge, scaling | The Pixar logo — going live |

The prop house is open. The stage is set. In Episode 2, we build the first set and register our first device.

**🔗 Resources**

- **ThingsBoard website**: [thingsboard.io](https://thingsboard.io)
- **ThingsBoard Cloud** (free tier): [thingsboard.io/installations](https://thingsboard.io/installations/)
- **ThingsBoard docs**: [thingsboard.io/docs](https://thingsboard.io/docs)
- **AI Solution Creator blog post**: [thingsboard.io/blog/ai-solution-creator](https://thingsboard.io/blog/ai-solution-creator/)
- **Luxo Jr. (Wikipedia)**: [en.wikipedia.org/wiki/Luxo_Jr.](https://en.wikipedia.org/wiki/Luxo_Jr._(character))

*🎬 Stage Props! is a series about ThingsBoard — the IoT platform that gives your devices joints, personality, and behaviour, the way John Lasseter gave Luxo Jr. a soul.*