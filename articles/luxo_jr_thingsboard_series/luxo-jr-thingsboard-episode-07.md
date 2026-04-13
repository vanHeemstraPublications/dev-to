---
title: "Luxo Jr. ThingsBoard 🎬 Ep.7"
part: 7
published: false
description: "Episode 7: Luxo Jr. bounces the ball between two stages. Home Assistant is your personal stage; ThingsBoard is the enterprise stage. Connect them via MQTT — HA publishes entity states, ThingsBoard ingests, visualises, and reacts at scale."
tags: [iot, thingsboard, homeassistant, mqtt]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/stage-props-thingsboard-episode-07.png"
series: "Luxo Jr. ThingsBoard Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: Two Stages, One Show

> *“In Luxo Jr., the ball passes between Luxo Sr. and Luxo Jr. — from one performer to another. Neither lamp holds the ball forever. The story is in the passing.”*

-----

## Two Stages, One Production 🎭

Home Assistant is a remarkable piece of software. Local-first, privacy-respecting, integrated with hundreds of device types. It is your personal stage — intimate, configurable, running on a Mac Mini in a Parallels VM, serving dashboards to a Nest Hub in the living room.

But Home Assistant has its limits. Its dashboards are designed for personal use, not enterprise-scale monitoring. Its history retention is bounded by local storage. Its alarm system is excellent for home automation but not designed for multi-tenant, multi-building deployments. Its audit trail is lightweight.

ThingsBoard is the enterprise stage. Built for scale. Multi-tenant. Professional dashboards with role-based access. A Rule Engine that can correlate data from a thousand devices. A Notification Centre that routes alarms to the right people across an organisation.

These two stages do not compete. They complement. In Episode 7, we pass the ball between them.

**Home Assistant** → reads all your smart home devices (dachshunds’ tracking zones, the Ajax alarm, the Nest Hub, the Tailscale-connected network) and publishes their states via MQTT.

**ThingsBoard** → ingests those states as device telemetry, stores them with full history, displays them alongside professional IoT data, runs alarm rules, and routes notifications to the right people.

Luxo Jr. bounces the ball between two lamps. The show is richer for it.

-----

## 🗂️ SIPOC — Two Stages, One Show

|**Suppliers**          |**Inputs**                                                         |**Process**                                                                          |**Outputs**                                                                  |**Customers**                                                          |
|-----------------------|-------------------------------------------------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------|
|Home Assistant         |HA entity states (lights, sensors, binary sensors, alarms, persons)|HA MQTT integration publishes state changes                                          |MQTT messages on ThingsBoard-format topics                                   |ThingsBoard Rule Engine, which processes and stores as device telemetry|
|ThingsBoard MQTT broker|Incoming MQTT messages from HA                                     |ThingsBoard processes as telemetry from pre-registered HA gateway device             |Time-series data stored per HA entity; alarms triggered per Rule Engine rules|Dashboards showing full home state; notification rules routing alerts  |
|ThingsBoard Rule Engine|HA telemetry + ThingsBoard alarm rules                             |Correlation rules: “no motion for 4 hours AND persons away → create Unoccupied alarm”|Multi-device correlation that HA alone cannot perform                        |Security team, family members, building manager                        |

-----

## Architecture: How the Bridge Works 🌉

The cleanest architecture for HA → ThingsBoard integration uses MQTT in one of two patterns:

### Pattern 1: HA as a Gateway Device (Recommended)

ThingsBoard’s **Gateway MQTT API** allows one MQTT connection to represent multiple devices. Home Assistant acts as the gateway — one MQTT client publishes data for all HA entities as individual “child devices”.

```
Home Assistant (Mac Mini, Parallels VM)
  │
  │  MQTT connection (port 1883 or 8883 TLS)
  │  Client ID: ha-gateway
  │  Username: HA_GATEWAY_ACCESS_TOKEN
  │
  ▼
ThingsBoard (Cloud or self-hosted)
  │
  ├── Auto-created: "living_room_temperature" (Device)
  ├── Auto-created: "front_door_contact" (Device)
  ├── Auto-created: "ajax_alarm" (Device)
  ├── Auto-created: "rianne_location" (Device)
  └── ... (one per HA entity you publish)
```

With the Gateway API, ThingsBoard auto-creates devices on first message. No pre-registration needed for each HA entity.

### Pattern 2: Direct Device MQTT (Simpler but more manual)

Each HA entity publishes as its own ThingsBoard device with its own access token. More setup, but more explicit control over which entities are in ThingsBoard.

We use Pattern 1 (Gateway) in this episode — it requires registering only one gateway device, and ThingsBoard auto-provisions the rest.

-----

## Step 1: Create the Gateway Device in ThingsBoard 🔌

1. **Entities → Devices → +** → Add new device
1. Name: `Home Assistant Gateway`
1. Device type: check **Is Gateway** (this enables gateway MQTT API)
1. Manage credentials → Access Token → copy the token

Note the token. This is the MQTT username for the HA connection.

-----

## Step 2: Configure Home Assistant MQTT Integration 📡

Home Assistant’s built-in MQTT integration connects to an MQTT broker. ThingsBoard Cloud acts as the MQTT broker.

In `configuration.yaml` (or via the UI MQTT integration settings):

```yaml
mqtt:
  broker: thingsboard.cloud   # or your self-hosted TB host
  port: 1883                   # use 8883 for TLS
  username: YOUR_GATEWAY_ACCESS_TOKEN
  password: ""                 # leave blank for access token auth
  client_id: ha-thingsboard-gateway
```

Or if using the UI integration:

1. **Settings → Devices & Services → MQTT → Configure**
1. Broker: `thingsboard.cloud`
1. Port: `1883`
1. Username: your gateway access token
1. Password: leave blank

-----

## Step 3: Publish HA Entity States as Gateway Telemetry 📤

ThingsBoard’s Gateway API uses specific MQTT topic and payload formats. HA’s standard MQTT integration can publish to custom topics using automations or templates.

**Gateway telemetry topic:** `v1/gateway/telemetry`

**Gateway telemetry payload format:**

```json
{
  "living_room_temperature": [
    {"ts": 1744400000000, "values": {"temperature": 22.3}}
  ],
  "front_door_contact": [
    {"ts": 1744400000000, "values": {"state": "off", "contact_closed": true}}
  ],
  "ajax_alarm": [
    {"ts": 1744400000000, "values": {"state": "armed_away", "triggered": false}}
  ]
}
```

Each key in the outer object becomes a ThingsBoard device name. Each device’s telemetry is an array of timestamped readings.

### Automating the publish from Home Assistant

Use an HA automation triggered by state changes to publish to ThingsBoard:

```yaml
# configuration.yaml or automations.yaml

automation:
  - alias: "Publish HA State to ThingsBoard"
    trigger:
      - platform: state
        entity_id:
          - sensor.living_room_temperature
          - sensor.living_room_humidity
          - binary_sensor.front_door
          - alarm_control_panel.alarmo
          - person.rianne
          - person.willem
    action:
      - service: mqtt.publish
        data:
          topic: "v1/gateway/telemetry"
          payload_template: >
            {
              "{{ trigger.entity_id | replace('.', '_') }}": [
                {
                  "ts": {{ now().timestamp() | int * 1000 }},
                  "values": {
                    "state": "{{ trigger.to_state.state }}",
                    "friendly_name": "{{ trigger.to_state.attributes.friendly_name | default('') }}"
                  }
                }
              ]
            }
```

For sensors with numeric values, add the value to the payload:

```yaml
- service: mqtt.publish
  data:
    topic: "v1/gateway/telemetry"
    payload: >
      {
        "living_room_temperature": [
          {
            "ts": {{ now().timestamp() | int * 1000 }},
            "values": {
              "temperature": {{ states('sensor.living_room_temperature') | float }},
              "unit": "°C"
            }
          }
        ]
      }
```

-----

## Step 4: Verify in ThingsBoard 🔍

After the first automation fires:

1. **Entities → Devices** — you see auto-created devices: `living_room_temperature`, `front_door_contact`, etc.
1. Open any device → **Latest Telemetry** — the HA state is there
1. Device status: **Active**

The ball is in the air. HA passed it. ThingsBoard caught it.

-----

## Step 5: Build the Entity Hierarchy 🏗️

The auto-created devices are flat — no hierarchy yet. Now apply what you learned in Episode 2:

1. Create Assets: `Home`, `Living Room`, `Garden`, `Front Hall`
1. Add Relations: `Home` Contains `Living Room`, `Living Room` Contains `living_room_temperature`, etc.
1. Assign Device Profiles appropriate to each HA entity type

This gives the ThingsBoard dashboards meaningful context — temperature in the `Living Room` asset, not just a flat list of device names.

-----

## Step 6: Assign Alarm Rules to HA Devices 🚨

The Luxo Jr. lamp in Home Assistant has a temperature sensor. Now in ThingsBoard, it also has alarm rules:

In the Device Profile for HA temperature sensors:

```
High Room Temperature:
  Condition: temperature > 25°C for 10 minutes
  Severity: WARNING
  Clear: temperature < 23°C

Heat Risk:
  Condition: temperature > 28°C
  Severity: CRITICAL
  Clear: temperature < 26°C
  Notify: email to facilities@home
```

Home Assistant can trigger an automation when the temperature crosses a threshold. ThingsBoard *also* triggers an alarm. Why both?

- HA automation: local, instant, triggers lights and notifications within the home
- ThingsBoard alarm: logged, propagated up the hierarchy, routed to the appropriate person via the Notification Centre, visible on the enterprise dashboard, auditable

They serve different purposes. HA reacts fast. ThingsBoard records, routes, and escalates.

-----

## Receiving Commands from ThingsBoard in Home Assistant 📥

The bridge also works in reverse. ThingsBoard can send RPC commands to the gateway, which HA can translate into HA service calls.

**ThingsBoard → MQTT RPC → HA → `light.turn_on`**

On the HA side, subscribe to the gateway RPC topic:

```yaml
automation:
  - alias: "Receive ThingsBoard RPC"
    trigger:
      - platform: mqtt
        topic: "v1/gateway/rpc"
    action:
      - service: >
          {% set data = trigger.payload_json %}
          {% if data.method == 'turnOnLight' %}
            light.turn_on
          {% elif data.method == 'setThermostat' %}
            climate.set_temperature
          {% endif %}
        data_template:
          entity_id: "{{ trigger.payload_json.params.entity_id }}"
```

This creates a **bidirectional bridge**: ThingsBoard dashboard has a control widget → sends RPC → HA receives → executes service call → HA state updates → publishes to ThingsBoard → dashboard reflects the change.

The ball bounces back and forth between the two stages. The show is coherent.

-----

## Practical Mapping: Beau and Elvis 🐶

Your dachshunds Beau and Elvis have tracking via HA zones. In ThingsBoard:

1. HA publishes `person.beau` and `person.elvis` (or zone sensors) as gateway telemetry
1. ThingsBoard creates devices `beau_location` and `elvis_location`
1. Alarm rule: if both are outside the `Home` zone for more than 60 minutes → `WARNING: Dogs may be unsupervised`
1. Map widget on the ThingsBoard dashboard shows their last known zones as geographic positions

This is the kind of multi-device correlation (both dogs, for duration, with geofence awareness) that Home Assistant automation can do but ThingsBoard makes persistent, auditable, and routeable.

-----

In **Episode 8**, the final episode, we take the production to the Pixar logo moment — the live system, scaled. ThingsBoard Edge for on-premises processing. Production deployment considerations. And a reflection on what it means when a lamp truly comes alive.

-----

**🔗 Resources**

- **ThingsBoard Gateway MQTT API**: [thingsboard.io/docs/reference/gateway-mqtt-api](https://thingsboard.io/docs/reference/gateway-mqtt-api/)
- **Home Assistant MQTT Integration**: [home-assistant.io/integrations/mqtt](https://www.home-assistant.io/integrations/mqtt/)
- **HA community discussion**: [community.home-assistant.io — ThingsBoard MQTT](https://community.home-assistant.io/t/configuring-outbound-mqtt-connection-to-thingsboard/169500)

-----

*🎬 Stage Props! is a series about ThingsBoard — the IoT platform that gives your devices joints, personality, and behaviour.*
