-----

## title: “Stage Props! 🎬 Ep.5: The Director’s Cue Sheet”
published: false
description: “Episode 5: Luxo Jr. did not wait to be told to react — the slump when the ball deflated was automatic. ThingsBoard’s Rule Engine is the cue sheet: filter, transform, alarm, notify, command — automated reactions to anything your devices report.”
tags: [iot, thingsboard, ruleengine, homeautomation]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/stage-props-thingsboard-episode-05.png”
series: “Stage Props!”
canonical_url: “”
organization: “the-software-s-journey”

# Stage Props! 🎬

## Episode 5: The Director’s Cue Sheet

> *“Luxo Jr. did not wait for Lasseter to tell it to slump. When the ball deflated, the lamp drooped. The reaction was built into the animation. Automatic. Inevitable. Expressive.”*

-----

## Automation Is Expression 🎭

The most emotionally powerful moments in Luxo Jr. were *automatic*. The curious head-tilt when the ball arrived: not scripted frame by frame — the animator defined the behaviour, and the physics did the rest. The dejected droop after the pop: built into the character’s response system.

ThingsBoard’s **Rule Engine** is the same thing for your IoT deployment. You do not watch the dashboard waiting for the temperature to exceed 30°C. You define the rule: *when temperature > 30°C → create CRITICAL alarm → send email → log event*. The system reacts automatically, every time, without anyone watching.

This is what transforms a collection of monitored devices into a production that manages itself.

-----

## 🗂️ SIPOC — The Cue Sheet

|**Suppliers**                  |**Inputs**                                                             |**Process**                                          |**Outputs**                                                                       |**Customers**                                                                                     |
|-------------------------------|-----------------------------------------------------------------------|-----------------------------------------------------|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
|Any device publishing telemetry|An incoming message (telemetry, attribute update, RPC, lifecycle event)|Root Rule Chain → filter → transform → action        |Alarm created, email sent, REST call made, RPC dispatched, Kafka message published|Operators receiving alerts; dashboards displaying active alarms; external systems receiving events|
|Alarm Rules configuration      |Threshold conditions (temperature > 30)                                |Alarm evaluation on each incoming telemetry message  |Active alarm propagated up entity hierarchy                                       |Notification Centre, alarm table widget, email recipients                                         |
|Calculated Fields              |Raw telemetry keys                                                     |Formula evaluation (e.g., power = brightness × 0.012)|A new derived telemetry key stored alongside originals                            |Dashboard widgets using derived values; alarm rules on calculated metrics                         |

-----

## The Rule Engine Architecture 🔧

The Rule Engine is a **visual flow-based processing system**. Every incoming message — telemetry, attribute update, device lifecycle event, REST API event — enters the **Root Rule Chain** and travels through a directed graph of **Rule Nodes**, each performing one operation.

```
Device publishes telemetry
        ↓
[ Root Rule Chain ]
        ↓
[ Message Type Switch ]  ← filters by message type
     ↓           ↓
[ Save Timeseries ]   [ Alarm Creation Node ]
     ↓                     ↓
[ Success ]           [ Email Node ]
                           ↓
                      [ Log Node ]
```

### Rule Nodes — The Stage Crew

Rule nodes come in five categories:

**Filter nodes** — decide which messages proceed:

- `Message Type Switch` — route by type: Post Telemetry, Post Attributes, RPC, etc.
- `Script filter` — custom JS/TBEL expression: `return msg.temperature > 30`
- `Asset type filter`, `Device type filter`

**Enrichment nodes** — add context to the message:

- `Originator attributes` — fetch the device’s server attributes into the message metadata
- `Related entity data` — fetch attributes from related assets (e.g., the room this device is in)
- `Customer details` — add customer context

**Transformation nodes** — reshape the message:

- `Script transformation` — rewrite the payload: derive new fields, rename keys, convert units
- `To email` — convert a message to email format using a template

**Action nodes** — do something:

- `Create alarm` — instantiate an alarm of specified type and severity
- `Clear alarm` — resolve an existing alarm
- `Save timeseries` — persist telemetry to the database
- `RPC call request` — send a command to a device
- `REST API call` — call an external HTTP endpoint
- `Send email` — send an email using configured SMTP

**External nodes** — integrate with external systems:

- `Kafka` — publish to a Kafka topic
- `RabbitMQ` — publish to a queue
- `AWS SNS` / `AWS SQS`

-----

## Alarm Rules: The Lighting Cue 🚨

The simplest and most common Rule Engine use case is **creating alarms when telemetry crosses a threshold**. ThingsBoard provides two ways to do this:

### Method 1: Device Profile Alarm Rules (Recommended for common cases)

In the Device Profile (Episode 2), the **Alarm Rules** tab lets you define conditions without touching the Rule Engine directly:

1. **Profiles → Device Profiles** → open your profile
1. **Alarm Rules** tab → **+** → **Add alarm rule**
1. Configure:
- **Alarm type**: `High Temperature`
- **Severity**: `CRITICAL`
- **Create condition**: `temperature > 30` (threshold in °C)
- **Duration**: `temperature > 30 for 60 seconds` (avoids transient spikes)
- **Clear condition**: `temperature < 28` (hysteresis — do not clear until meaningfully below threshold)
- **Propagate**: enable to propagate alarm up through asset hierarchy

This applies automatically to every device using this profile. The director has set the lighting cue; it fires for every lamp on stage.

### Method 2: Rule Chain Alarm Nodes (For complex conditions)

For multi-signal alarms (“alert if temperature > 30 AND humidity > 80”), use the Rule Engine directly:

1. **Rule Chains** → open **Root Rule Chain** (or create a dedicated chain)
1. Add a **Script Filter** node:
   
   ```javascript
   // TBEL expression — fires on High Temp + High Humidity combined
   return msg.temperature > 30 && msg.humidity > 80;
   ```
1. Connect its `True` output to a **Create Alarm** node
1. Configure the alarm: type `High Temp + High Humidity`, severity `MAJOR`
1. Connect the `False` output to a **Clear Alarm** node (same alarm type)

-----

## Viewing and Managing Alarms 🔔

Active alarms appear in:

- **Alarms** page in the left nav (tenant-wide view)
- **Alarm table widget** on any dashboard
- **Notification Centre** (bell icon, top right)

For each alarm you can:

- **Acknowledge** — “I am aware and investigating”
- **Clear** — “Issue resolved”
- **Comment** — add a note visible to all users watching the alarm
- **Assign** — assign the alarm to a specific user for investigation

Alarm **propagation** means a CRITICAL alarm on a single temperature sensor in Room 401 is visible not just on that device, but also on the Room 401 asset dashboard, the Floor 4 dashboard, and the Building A overview — the right people at each level see the right alarms without each level’s dashboard needing to enumerate every possible device.

-----

## Calculated Fields: The Shadow Map 🌑

Lasseter described Luxo Jr.‘s self-shadowing as “a perfect matching of technology and subject matter.” The lamp’s own light created its own shadow — a *derived* visual output computed from the primary data.

ThingsBoard **Calculated Fields** do the same: compute new telemetry values from existing ones using formulas. The derived value is stored alongside the raw telemetry and can be charted, alarmed on, and displayed in widgets.

**Setup: Entities → Devices → [device] → Calculated Fields → + Add**

Examples:

```
# Power consumption derived from brightness
power_watts = brightness * 0.012

# Average temperature from multiple sensor keys
avg_temp = (temp_north + temp_south) / 2

# Efficiency ratio
efficiency = actual_output / max_output * 100
```

Multi-source calculated fields can draw from different devices — compute the total energy consumption of a floor by summing power readings from all its smart meters.

-----

## The Notification Centre: Stage Manager’s Radio 📻

ThingsBoard’s **Notification Centre** centralises all alerts. Configure:

- **Which events trigger notifications**: alarms created, device going inactive, device created, rule engine errors
- **Which users receive them**: tenant admins, customer users, specific individuals
- **How they are delivered**: in-app notification bell, email, Slack (PE feature), SMS

Configure notification rules:

1. **Notification Centre → Rules → + Add rule**
1. Trigger: `Alarm created`
1. Filter: severity = `CRITICAL` or `MAJOR`
1. Template: email body using entity variables: `Device ${deviceName} reported ${alarmType} at ${alarmTime}`
1. Recipients: `All tenant administrators`, or specific users

-----

## A Complete Rule Chain: Luxo Jr.’s Alarm System 🎬

Here is a full Rule Chain configuration for the Luxo Jr. lamp:

```
Incoming telemetry from Luxo Jr. Lamp
            ↓
[ Message Type Switch ]
    ↓ "Post telemetry"
[ Originator Attributes ]  ← fetch maxTempThreshold from server attributes
    ↓ Success
[ Script Filter ]
  Code: return msg.ambientTemp > metadata.maxTempThreshold;
    ↓ True                     ↓ False
[ Create Alarm ]          [ Clear Alarm ]
  type: "High Temperature"   type: "High Temperature"
  severity: CRITICAL
    ↓ Created
[ To Email node ]
  Subject: "⚠ Luxo Jr. Lamp - High Temperature Alert"
  Body: "Temperature: ${msg.ambientTemp}°C exceeded threshold ${metadata.maxTempThreshold}°C"
    ↓
[ Send Email ]
```

Key insight: the threshold (`maxTempThreshold`) is fetched from the device’s server-side attributes at rule-time — not hardcoded. Change the attribute on the device and the alarm threshold changes without modifying the rule chain. The set designer’s blueprint is separated from the lighting cue.

-----

## Home Assistant Integration Preview: Rules That Bridge Systems 🏠

When we connect Home Assistant in Episode 7, the Rule Engine becomes the intelligence layer that HA lacks at scale:

- **Ajax alarm triggered in HA** → MQTT → ThingsBoard → Rule Engine → Create `Intruder Alert` alarm → Email security team
- **Garden temperature below 2°C** → HA sensor → ThingsBoard → Rule Engine → Send push notification → *“Risk of frost — cover the plants”*
- **No motion in the house for 4 hours** → HA binary sensor → ThingsBoard → Rule Engine → Check if persons are home → if no: create `Unoccupied` alarm → turn off unnecessary devices via RPC

ThingsBoard adds the enterprise intelligence layer that Home Assistant (a local-first system) cannot easily provide at scale: multi-device correlation, alarm propagation, notification routing, audit logging.

-----

In **Episode 6**, we see what happens when you skip all this manual setup. The AI Solution Creator builds the entire set, props, cue sheet, and prompt book from a single conversation. In 10 minutes.

-----

**🔗 Resources**

- **Rule Engine overview**: [thingsboard.io/docs/user-guide/rule-engine-2-0/overview](https://thingsboard.io/docs/user-guide/rule-engine-2-0/overview/)
- **Working with alarms**: [thingsboard.io/docs/user-guide/alarms](https://thingsboard.io/docs/user-guide/alarms/)
- **Notification Centre**: [thingsboard.io/docs/user-guide/notifications](https://thingsboard.io/docs/user-guide/notifications/)
- **Calculated Fields**: [thingsboard.io/docs/user-guide/calculated-fields](https://thingsboard.io/docs/user-guide/calculated-fields/)

-----

*🎬 Stage Props! is a series about ThingsBoard — the IoT platform that gives your devices joints, personality, and behaviour.*
