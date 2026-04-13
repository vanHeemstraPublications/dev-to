---
title: "Luxo Jr. ThingsBoard 🎬 Ep.8"
part: 8
published: false
description: "Episode 8: The moment the lamp hops onto the screen and stamps the letter ‘I’ — the production is live. ThingsBoard Edge for on-premises processing, production deployment considerations, and the full series map of everything you have built."
tags: [iot, thingsboard, production, homeautomation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/stage-props-thingsboard-episode-08.png"
series: "Luxo Jr. ThingsBoard Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: The Pixar Logo

> *“Every Pixar film begins the same way: the lamp hops in, looks at the camera, jumps on the letter ‘I’, and stamps it flat. That moment — performed billions of times before billions of films — is the production going live.”*

-----

## The Moment the Lamp Hops On Stage 🎬

In 1986, Luxo Jr. was an experiment. A demo reel. A proof of concept. Six thousand people screamed at SIGGRAPH when the lamp moved, not because they thought it was a finished product, but because they could *see* what it could become.

Then, in 1995, *Toy Story* opened. And before the credits rolled, Luxo Jr. hopped onto the screen and stamped the Pixar logo for the first time in a feature film.

That is the production going live.

This episode is about taking your ThingsBoard deployment from “proof of concept with demo data” to “production system processing real device telemetry reliably, securely, and at scale.” It covers ThingsBoard Edge for on-premises processing, production deployment patterns, and the choices that matter when the lamp hops on in front of a real audience.

-----

## 🗂️ SIPOC — Going Live

|**Suppliers**                           |**Inputs**                                                   |**Process**                                                                         |**Outputs**                                                                     |**Customers**                                                              |
|----------------------------------------|-------------------------------------------------------------|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------------|
|Real devices (replacing emulators)      |Actual telemetry from physical sensors and actuators         |Swap device credentials: disconnect emulators, connect real devices to same profiles|Live production data in the dashboards, alarm rules active on real thresholds   |Real operators, facilities managers, homeowners — not demo data viewers    |
|ThingsBoard Edge (on-premises component)|Local device telemetry in a site with unreliable connectivity|Edge processes locally, buffers during outages, syncs to cloud                      |Low-latency local reaction + cloud-level visibility and management              |Industrial sites, homes with unreliable uptime requirements, edge scenarios|
|Security configuration                  |TLS certificates, API keys, user accounts                    |Enable TLS on MQTT (port 8883), configure role-based access, rotate tokens          |Secured communication channels, auditable user actions, no plaintext credentials|Production security requirements; compliance; audit                        |

-----

## Swapping Out the Stand-Ins 🎭

The AI Solution Creator (Episode 6) created emulators — software stand-ins that published realistic demo data. Now the real devices arrive on set.

**The swap is simpler than it sounds.** Because the emulators connect to the same Device Profiles you use for real devices, and because ThingsBoard stores credentials per device (not per profile), you:

1. Disable or delete the emulator device(s)
1. Register real devices with the same profiles
1. Configure real devices with their ThingsBoard access tokens
1. The dashboards, alarm rules, and calculated fields continue working — they reference profiles, not specific device instances

The stage set does not change. The props do.

-----

## ThingsBoard Edge: The Animatronic on Location 🤖

At Disney’s Hollywood Studios, a 1.8-metre animatronic Luxo Jr. once performed at the entrance to Toy Story Midway Mania. Not a screen. Not a projection. A physical prop on-site, performing locally, independently of any studio connection.

**ThingsBoard Edge** is the same idea applied to IoT.

Edge is an on-premises component of ThingsBoard — a lightweight deployment that runs at the network edge (on a local server, industrial PC, or Raspberry Pi) and processes device data *locally*, without requiring a cloud connection for every operation.

### Why Edge Matters

**Low latency:** An alarm that requires `temperature > 30°C → turn off heater` cannot wait for a cloud round-trip. Edge processes the rule locally in milliseconds, not seconds.

**Resilience:** If the internet connection between your factory and the cloud goes down, Edge keeps processing. Data is buffered locally and synchronised to the cloud when connectivity is restored.

**Data sovereignty:** Some deployments cannot send raw telemetry to a cloud server — regulatory requirements, proprietary data, or simply network bandwidth constraints. Edge processes locally and sends only aggregated or summarised data upward.

**Distributed management:** Multiple Edge instances (one per building, one per factory floor) are managed from a single ThingsBoard Cloud dashboard. The Pixar logo plays at every cinema, but the projection equipment is local to each venue.

### The Edge Architecture

```
ThingsBoard Cloud (the studio)
  │  Sync: entity configs, rule chains, dashboards
  │  Receive: telemetry, alarm events, aggregated data
  │
  ├── Edge Instance A (Building A, Floor 1-5)
  │   ├── Local MQTT broker
  │   ├── Local Rule Engine (fast reactions)
  │   ├── Local dashboard (works offline)
  │   └── Devices 1–200
  │
  ├── Edge Instance B (Building B)
  │   └── Devices 201–400
  │
  └── Edge Instance C (Home — Mac Mini)
      ├── Processes HA telemetry locally
      ├── Sends summaries to cloud
      └── Home Assistant Gateway device
```

For the home deployment (connecting HA from Episode 7), Edge on the Mac Mini means:

- HA data stays local until you actively sync it to cloud
- Local alarm rules fire instantly without cloud round-trip
- Full local dashboard available even when internet is down (the Tailscale connection makes this moot in most cases, but valuable for reliability)

### Setting Up ThingsBoard Edge

Edge is available as a separate download ([thingsboard.io/docs/edge/](https://thingsboard.io/docs/edge/)):

```bash
# Docker-based Edge deployment
docker pull thingsboard/tb-edge:latest

docker run -d \
  --name tb-edge \
  --restart always \
  -p 1883:1883 \
  -p 8080:8080 \
  -v ~/.tb-edge/data:/data \
  -e CLOUD_ROUTING_KEY=YOUR_EDGE_KEY \
  -e CLOUD_ROUTING_SECRET=YOUR_EDGE_SECRET \
  -e CLOUD_RPC_HOST=thingsboard.cloud \
  thingsboard/tb-edge:latest
```

In ThingsBoard Cloud:

1. **Edge Management → Instances → + Add Edge**
1. Generate routing key and secret (credentials for the Edge → Cloud connection)
1. Assign which entities the Edge should manage (devices, rule chains, dashboards)

The Edge instance syncs its configuration from the Cloud and begins processing locally.

-----

## Production Security: The Lamp Does Not Run Unsigned 🔐

In production, several security practices are non-negotiable:

**Enable TLS for MQTT (port 8883):**

```bash
# Device connects with TLS
mosquitto_pub \
  -h "thingsboard.cloud" \
  -p 8883 \
  --cafile ca.crt \   # ThingsBoard's CA certificate
  -u "YOUR_ACCESS_TOKEN" \
  -t "v1/devices/me/telemetry" \
  -m '{"temperature": 24.5}'
```

**Use API Keys for server-side integrations** (ThingsBoard 4.3+):
Rather than sharing admin user credentials for REST API access, create API keys with specific scopes and expiry dates. Ideal for the Home Assistant → ThingsBoard bridge and CI/CD automation.

**Rotate access tokens regularly:**
Especially for devices in exposed or accessible locations. ThingsBoard supports multiple active credentials per device during the rotation window.

**Principle of least privilege for user roles:**
Customer users see only their assigned dashboards. Floor managers see only their floor. Alarm management is restricted to authorised roles. Review role assignments when staff change.

**Audit log review:**
ThingsBoard records all user actions. Periodically review the audit log for unexpected attribute changes, dashboard modifications, or credential management events.

-----

## The Home + ThingsBoard Production Stack: Full Picture 🏠

For the complete home automation + ThingsBoard integration covered in this series:

```
Physical Layer:
  ├── Ajax alarm system (SIA protocol)
  ├── UniFi network (UDM Pro + Express)
  ├── Nest Hub (Google Cast)
  ├── Smart plugs, sensors, lights
  └── Beau & Elvis tracking

Home Assistant (Parallels VM on Mac Mini):
  ├── Integrates all physical devices
  ├── Local automations (lights, scenes, ALARMO)
  ├── Companion App on iPad Mini
  ├── Tailscale add-on (secure remote access)
  └── MQTT → ThingsBoard Gateway (Episode 7)

ThingsBoard (Cloud or local Edge):
  ├── Ingests all HA entity states
  ├── Entity hierarchy: Home → Rooms → HA Devices
  ├── Enterprise dashboards (role-based access)
  ├── Alarm rules with email/notification routing
  ├── Calculated fields (energy totals, avg temps)
  ├── Full telemetry history (beyond HA's local storage)
  └── AI Solution Creator: 10-minute PoC generation
```

Two stages. One show. The lamp bounces between them.

-----

## The Complete Series Map: What You Have Built 🗺️

Eight episodes. Here is the complete prop house inventory and the stage it built:

|Stage props concept                |ThingsBoard concept              |Episode|
|-----------------------------------|---------------------------------|-------|
|Inert prop in the prop house       |Hardware with no platform        |1      |
|Giving the prop joints             |Device + Device Profile          |2      |
|The set — hierarchy of places      |Assets + Relations               |2      |
|The prop’s observable state        |Telemetry (time-series data)     |3      |
|The prop’s fixed characteristics   |Attributes (static properties)   |3      |
|The prop receiving a cue           |RPC command                      |3      |
|The prompt book                    |Dashboard + Widgets              |4      |
|Drill-down chapters                |Dashboard States                 |4      |
|The cue sheet — automated reactions|Rule Engine + Rule Chains        |5      |
|A lighting cue (alarm trigger)     |Alarm Rule                       |5      |
|Shadow maps (derived data)         |Calculated Fields                |5      |
|The director’s radio               |Notification Centre              |5      |
|Animating the lamp in 10 minutes   |AI Solution Creator              |6      |
|Rehearsal with stand-ins           |Demo data emulators              |6      |
|Luxo Jr. bouncing the ball         |HA → ThingsBoard MQTT bridge     |7      |
|The ball returned                  |ThingsBoard → HA RPC             |7      |
|The animatronic on location        |ThingsBoard Edge                 |8      |
|Production opening night           |Real devices + secured deployment|8      |
|The Pixar logo                     |Your live, working IoT solution  |8      |

-----

## The Lamp Hops On Stage 🎬

Lasseter did not set out to create a mascot. He set out to prove that computer animation could convey personality, emotion, and story through an inanimate object. The lamp was the test subject. The test succeeded so comprehensively that the lamp became the face of the studio that changed animation forever.

Your IoT devices are the same test subjects. A temperature sensor is inert hardware. An MQTT message is just bytes. A ThingsBoard device profile is just configuration.

But combine them: register the device, connect it, define its profile, build the dashboard, wire the alarm rules, bridge it to Home Assistant, process it at the edge, deploy it to production — and the sensor becomes something alive. It speaks. It reacts. It is watched by the right people, at the right time, who take the right action.

The lamp hops onto the stage. The show begins.

-----

**🔗 Resources**

- **ThingsBoard Edge documentation**: [thingsboard.io/docs/edge](https://thingsboard.io/docs/edge/)
- **ThingsBoard production installation**: [thingsboard.io/docs/user-guide/install/pe/installation-options](https://thingsboard.io/docs/user-guide/install/pe/installation-options/)
- **Security best practices**: [thingsboard.io/docs/user-guide/device-credentials](https://thingsboard.io/docs/user-guide/device-credentials/)
- **ThingsBoard Community Edition GitHub**: [github.com/thingsboard/thingsboard](https://github.com/thingsboard/thingsboard)

-----

*🎬 Stage Props! is a series about ThingsBoard — the IoT platform that gives your devices joints, personality, and behaviour, the way John Lasseter gave Luxo Jr. a soul.*
*Thank you for watching the production.*
