---
title: "Luxo Jr Thingsboard 🎬 Ep.2"
part: 2
published: false
description: "Episode 2: Before the lamp can perform, the stage must be built. ThingsBoard Devices, Assets, Device Profiles, and Relations — the physical world modelled as a hierarchy of entities, from building to room to sensor, all connected."
tags: [iot, thingsboard, beginners, homeautomation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/stage-props-thingsboard-episode-02.png"
series: "Luxo Jr Thingsboard Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: Building the Set

> *“Before Lasseter could animate the lamp, he needed the model. Every joint, every arm segment, the base, the head, the bulb — each part defined and articulated before a single frame was rendered.”*

-----

## The Set Designer’s Job 🎨

A stage production does not begin with performance. It begins with set design. The set designer decides what objects exist on the stage, where they are positioned, what category each belongs to, and how they relate to each other. A lamp needs a table. A table belongs to a room. A room belongs to a floor. The hierarchy exists before any actor touches anything.

ThingsBoard’s **entity model** is the set design. Before a single telemetry packet arrives, you define the digital representation of your physical world: which devices exist, which assets contain them, what profiles govern their behaviour, and how they relate to each other.

This episode builds the set.

-----

## 🗂️ SIPOC — Building the Set

|**Suppliers**           |**Inputs**                                            |**Process**                                                             |**Outputs**                                                     |**Customers**                                                                    |
|------------------------|------------------------------------------------------|------------------------------------------------------------------------|----------------------------------------------------------------|---------------------------------------------------------------------------------|
|You (the set designer)  |Knowledge of your physical deployment                 |Create Assets: Building → Floor → Room hierarchy                        |A navigable entity tree matching physical reality               |Dashboards that show data in context; alarm rules that propagate up the hierarchy|
|You (the prop master)   |Sensor hardware specs, protocol, alarm thresholds     |Create Device Profile: transport config, alarm rules, attribute defaults|A reusable template for all devices of the same type            |Every device of that type — register once, configure via profile                 |
|You (the prop master)   |Each physical device’s serial number, location, access|Create Device: register device, generate credentials                    |An active device ready to receive telemetry                     |The Rule Engine, which processes all incoming messages from this device          |
|You (the stage director)|The relationship between each prop and its set        |Create Relations: Contains, Manages                                     |A typed directed graph connecting devices to assets to customers|Entity hierarchy navigation; alarm propagation; dashboard drill-down             |

-----

## The Entity Types: Cast of Characters 🎭

ThingsBoard models the physical and organisational world through six primary entity types. Together they create the full cast for your stage production.

### Devices — The Stage Props Themselves

A **Device** is the fundamental IoT entity: a physical sensor, actuator, controller, or tracker. Devices are the Luxo Jr. lamps of your stage — the things that sense, report, and respond.

Every device:

- Has a unique **name** within your tenant
- Belongs to a **Device Profile** (more below)
- Has an **access token** or other credentials for authentication
- Can generate **telemetry** (time-series data)
- Can have **attributes** (static properties)
- Responds to **RPC commands** (instructions from the platform)
- Can be **assigned to a Customer** (for multi-tenancy)

Examples: a temperature sensor in room 401, a smart meter on floor 2, an HVAC controller in building B, a Luxo Jr. animatronic lamp on stage.

### Assets — The Stage Itself

An **Asset** is an abstract entity — it has no network address, sends no telemetry directly, but it *contains* or *manages* devices and other assets. Assets model the physical world structure.

Examples: a building, a floor, a room, a production line, a field (agricultural), a vehicle fleet, a home (containing all your HA devices).

Assets give your data context. A temperature reading of 28°C means little in isolation. A temperature reading of 28°C from room 401 on floor 4 of Building A in the Amsterdam office changes the meaning entirely — and allows the alarm to propagate to the right people.

### The Hierarchy: Building the Set Tree

```
Tenant (your ThingsBoard account)
└── Building A                          ← Asset (type: Building)
    ├── Floor 4                         ← Asset (type: Floor)
    │   ├── Room 401                    ← Asset (type: Room)
    │   │   ├── Temperature Sensor 401  ← Device
    │   │   ├── Humidity Sensor 401     ← Device
    │   │   └── Smart Thermostat 401    ← Device
    │   └── Room 402                    ← Asset (type: Room)
    │       └── Temperature Sensor 402  ← Device
    └── Floor 5                         ← Asset (type: Floor)
        └── ...
```

This hierarchy means:

- A temperature alarm on Sensor 401 can propagate up to Room 401, then Floor 4, then Building A
- A building-level dashboard can aggregate data from all floors, rooms, and sensors automatically
- A customer (a building tenant) can be granted access to their floor without seeing others

For a home setup bridged from Home Assistant:

```
Home                                    ← Asset (type: Home)
├── Living Room                         ← Asset (type: Room)
│   ├── Luxo Jr. Lamp (HA entity)       ← Device
│   ├── Nest Hub (HA entity)            ← Device
│   └── Living Room Temp (HA sensor)    ← Device
├── Garden                              ← Asset (type: Area)
│   └── Garden Motion (HA entity)       ← Device
└── Beau & Elvis tracker (HA zone)      ← Device
```

-----

## Device Profiles — The Prop Master’s Blueprint 📋

A **Device Profile** is a reusable template applied to all devices of the same type. When you have 50 temperature sensors, you do not configure alarm rules 50 times — you configure them once in the profile and all 50 devices inherit them.

A Device Profile defines:

**Transport configuration** — How devices of this type connect: MQTT (default), HTTP, CoAP, LwM2M, or custom. This controls which topics the device uses, whether payload is JSON or Protobuf, QoS settings.

**Alarm rules** — Conditions that trigger alarms. For a temperature sensor profile: “if `temperature` > 30°C for 1 minute → create CRITICAL alarm”. All 50 sensors automatically have this rule without individual configuration.

**Device provisioning settings** — How new devices of this type register themselves. Useful when deploying large numbers of devices — they can self-provision using a shared key.

**Default dashboard** — Which dashboard opens when you click on any device of this type.

### Creating a Device Profile in the UI

1. Navigate to **Profiles → Device Profiles**
1. Click **+** → **Create new device profile**
1. Set:
- **Name**: `Temperature Sensor` (or `Luxo Lamp`, or `HA MQTT Device`)
- **Transport type**: `MQTT`
- **Default dashboard**: *(create this in Episode 4, assign later)*
1. On the **Alarm Rules** tab: add your first rule (Episode 5 covers this fully)
1. Save

-----

## Asset Profiles — The Stage Set Type 🎭

**Asset Profiles** work like Device Profiles but for assets. They define what kind of place or thing an asset is: Building, Floor, Room, Vehicle, Field, Home.

In the UI: **Profiles → Asset Profiles → +**

For our home setup, create:

- `Home` profile
- `Room` profile
- `Area` profile (for garden, garage, etc.)

-----

## Relations — The Stage Manager’s Connections 🔗

A **Relation** is a typed, directed connection between two entities. Relations express the “contains”, “manages”, or “is part of” relationships that make the hierarchy work.

Relation types are strings — you can define any type, but the most common are:

- `Contains` — an asset contains a device or another asset (Building Contains Floor, Floor Contains Room)
- `Manages` — an asset manages a device
- `isPartOf` — a device is part of an asset

### Creating Relations in the UI

1. Open an Asset (e.g., Room 401)
1. Click the **Relations** tab
1. Click **+** → **Add relation**
1. Set:
- **Relation type**: `Contains`
- **Entity type**: `Device`
- **Entity**: `Temperature Sensor 401`
1. Save

Repeat for each device in the room. Then add a relation from Floor 4 to Room 401, and from Building A to Floor 4.

### The Result

ThingsBoard now has a traversable graph. When an alarm fires on Temperature Sensor 401, it can propagate up through the `Contains` relations: Room 401 → Floor 4 → Building A → Tenant. The right people at each level see the right alarms.

-----

## Creating Your First Device 🔌

Now the first lamp takes its place on stage.

1. Navigate to **Entities → Devices**
1. Click **+** → **Add new device**
1. Set:
- **Name**: `Living Room Temp` (or any descriptive name)
- **Device Profile**: `Temperature Sensor` (or `Default`)
1. Click **Add**

After creation:

1. Click the device to open its details
1. Click **Manage credentials** (the key icon)
1. Select **Access token** (simplest for beginners)
1. Note the generated token — you will need this in Episode 3

The device exists in ThingsBoard. It is the Luxo Jr. lamp — modelled, articulated, placed on stage. But it is still dark. No telemetry has arrived yet. No personality has emerged.

That is Episode 3.

-----

## Customers — The Audience Section 👥

One ThingsBoard tenant can serve multiple customers. A customer is an organisation or individual who sees only the assets, devices, and dashboards assigned to them — complete data isolation within the same deployment.

For a home setup, customers are usually not needed — it is one tenant, one user. For multi-site deployments or service providers, customers are how you partition the stage: Client A sees their building; Client B sees theirs; neither sees the other.

**Assign a device to a customer:**

1. Open the device
1. Click the customer icon (person icon in top right of device details)
1. Select the customer

-----

## The Entity Model for a Smart Home (Home Assistant Integration Preview) 🏠

When we connect Home Assistant in Episode 7, each HA entity type becomes a ThingsBoard Device. The suggested mapping:

|Home Assistant entity           |ThingsBoard Device name|Device Profile         |
|--------------------------------|-----------------------|-----------------------|
|`light.living_room`             |`Living Room Light`    |`HA Light`             |
|`sensor.living_room_temperature`|`Living Room Temp`     |`HA Temperature Sensor`|
|`binary_sensor.front_door`      |`Front Door`           |`HA Binary Sensor`     |
|`alarm_control_panel.alarmo`    |`Ajax Alarm`           |`HA Alarm Panel`       |
|`person.rianne`                 |`Rianne Location`      |`HA Person`            |

The Home asset contains Room assets; Room assets contain the HA Device entities. The entire set is built before the MQTT bridge goes live.

-----

In **Episode 3**, we connect the first device. The prop’s head swings up, the bulb illuminates, and the first telemetry packet arrives. The lamp is alive.

-----

**🔗 Resources**

- **ThingsBoard Entities and Relations**: [thingsboard.io/docs/user-guide/entities-and-relations](https://thingsboard.io/docs/user-guide/entities-and-relations/)
- **Device Profiles**: [thingsboard.io/docs/user-guide/device-profiles](https://thingsboard.io/docs/user-guide/device-profiles/)
- **Getting Started guide**: [thingsboard.io/docs/getting-started-guides/helloworld](https://thingsboard.io/docs/getting-started-guides/helloworld/)

-----

*🎬 Stage Props! is a series about ThingsBoard — the IoT platform that gives your devices joints, personality, and behaviour.*
