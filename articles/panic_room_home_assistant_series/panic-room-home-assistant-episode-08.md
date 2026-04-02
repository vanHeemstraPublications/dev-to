---
title: "Panic Room — Ep.8"
part: 8
published: false
description: "The panic room had a real alarm system. So does your house. This episode integrates Ajax Security into Home Assistant — via SIA for listening, and the SpaceControl relay hack for control."
tags: [homeassistant, ajax, security, alarm]
series: "Panic Room Home Assistant Series"
cover_image: ""
canonical_url: ""
organization: "the-software-s-journey"
---

# 🔐 The Real Alarm System (Ajax Security Integration)

> *“The room had its own security system. Independent. Hardwired. Not connected to anything the intruders could reach.”*
> — Panic Room (2002).

## 🚨 The Real Alarm

In the film, the panic room has its own independent security layer — sensors, door contacts, hardwired logic that does not depend on the house’s main systems. Meg can watch the intruders on her cameras precisely because the panic room’s infrastructure is separate, resilient, and honest about what it is.

**Ajax Systems** is the real-world equivalent for a growing number of homeowners. It is a Grade 2 certified wireless alarm system — tamper-proof, interference-resistant, backed by its own radio protocol (Jeweller/Fibra), and designed for professional-grade protection. Banks use it. Commercial properties use it. An increasing number of Dutch houses use it.

It is also, by design, a **closed ecosystem**. Ajax does not want you to hook it up to third-party platforms. There is good reason for that — an alarm system that lets arbitrary external code arm and disarm it is not, strictly speaking, an alarm system.

And yet.

Home Assistant and Ajax can coexist. They can even cooperate — with honesty about what each side contributes, and what the limits are. This episode explains how.

-----

## 📋 SIPOC — The Real Alarm System

|**Suppliers**                |**Inputs**                                     |**Process**                                                |**Outputs**                                                 |**Customers**                                              |
|-----------------------------|-----------------------------------------------|-----------------------------------------------------------|------------------------------------------------------------|-----------------------------------------------------------|
|Ajax Systems (hub + sensors) |Ajax Hub 2 (or compatible) on your home network|Configure Ajax to send SIA events → HA listens on a port   |Real-time alarm states in Home Assistant                    |Your automations (lights, notifications, Tailscale alerts) |
|HA SIA Integration (built-in)|A spare TCP port on your HA instance           |Add SIA integration → Match account ID and port            |`alarm_control_panel` entities per zone/group               |Your iPad Mini dashboard — alarm status visible remotely   |
|Ajax SpaceControl key fob    |A 4-channel Wi-Fi relay with dry-contact output|Wire relay to SpaceControl button contacts → Control via HA|Arm, Disarm, Night Mode from Home Assistant                 |Automations that arm when you leave, disarm when you arrive|
|ESPHome or Zigbee2MQTT       |Soldering skills and a little patience         |Flash ESPHome to relay → Expose as HA switches             |`switch.ajax_arm`, `switch.ajax_disarm`, `switch.ajax_night`|Presence-based arming automations (Episode 7)              |

-----

## 🔒 Understanding Ajax — A Closed System by Design

Before any configuration: a frank account of what Ajax is and is not.

Ajax is built around three principles that make it excellent as a security system and awkward as a smart home component:

**Certified Devices Only.** The hub communicates exclusively with registered Ajax devices using the proprietary Jeweller radio protocol. You cannot add a third-party sensor. You cannot spoof an Ajax device. The ecosystem is closed at the hardware layer.

**Cloud Locked.** The official Ajax app controls the system via Ajax’s cloud. There is no local API. There is no published SDK for consumer use. Ajax does offer an enterprise API — but it requires an alarm installer company account, has strict rate limits (100 calls per minute), and is not suitable for a self-hosted Home Assistant integration. If you are not a professional installer, the enterprise API is not a realistic path.

**One Monitoring Station.** The Ajax hub supports exactly one SIA-capable monitoring station at a time. Normally this is the Alarm Receiving Centre (ARC) — the security company that dispatches a response when your alarm triggers. If you configure Home Assistant as the SIA monitoring station, you cannot simultaneously use a professional ARC. This is the most important trade-off to understand before proceeding.

> 🔐 **The panic room analogy:** Ajax is the steel door. It has one keyhole. You can choose what goes into that keyhole — a professional monitoring service, or Home Assistant, but not both simultaneously. If you already pay for professional monitoring, read the section on ALARMO (later in this episode) for a different architectural approach.

With those constraints clearly on the table, here is what we *can* do:

1. **Listen** to Ajax via the SIA protocol — receive alarm state changes, sensor events, arm/disarm events
1. **Control** Ajax — arm, disarm, and set night mode — via a hardware relay wired to a SpaceControl key fob

Both approaches are described below, in sequence.

-----

## 📡 Part 1 — Listening: SIA Protocol Integration

### What Is SIA?

The **Security Industry Association (SIA) DC-09 protocol** is the standard used by professional alarm systems to communicate with monitoring centres. Ajax supports it natively — it is the same protocol Ajax uses to talk to professional ARCs. By configuring Home Assistant as the monitoring station, your HA instance receives all alarm events in real time, over your local network, with no cloud involved.

The HA SIA integration is listen-only: Ajax sends events; Home Assistant receives and processes them. It cannot send commands back.

What Home Assistant receives via SIA:

|SIA Code|Event                            |
|--------|---------------------------------|
|`CL`    |Closing — system armed           |
|`OP`    |Opening — system disarmed        |
|`NL`    |Night lock — night mode armed    |
|`BA`    |Burglary alarm triggered         |
|`TA`    |Tamper alarm                     |
|`CA`    |Cancel — alarm cancelled         |
|`RP`    |Automatic test report (heartbeat)|
|`BR`    |Burglary restore — alarm cleared |

These become entity state changes and HA events — triggerable by automations.

-----

### Step 1 — Configure Groups in the Ajax App

The SIA integration receives events per **group**, not per individual sensor. A group in Ajax is a logical partition — a set of sensors that arm and disarm together.

Open the Ajax app:

1. Go to **Control** → **Settings (cog)** → **Groups** → **+ Add Group**.
1. Create groups that make sense for your home. Common groupings:
- *Ground Floor* (door contacts, motion sensors downstairs)
- *First Floor* (bedroom motion sensors)
- *Perimeter* (all door and window contacts)
1. Assign each sensor to a group.

> 📌 **Hub group limits matter.** The Ajax Hub (non-Plus) supports up to 9 groups. The Hub Plus supports 25. If you have more sensors than your group limit can individually accommodate, combine sensors from the same room into one group. Home Assistant will show one `alarm_control_panel` entity per group per zone — the granularity of what HA sees maps directly to your Ajax group configuration.

-----

### Step 2 — Configure the Ajax Hub to Send SIA Events

In the Ajax app:

1. Go to **Devices** → **Your Hub** → **Settings (cog)** → **Security Companies**.
1. Tap **CMS Connection** → **Add monitoring station**.
1. Configure:

|Setting          |Value                                                                       |
|-----------------|----------------------------------------------------------------------------|
|Protocol         |**SIA**                                                                     |
|Connect on demand|**Enabled**                                                                 |
|Account ID       |A 3–16 character hex string — e.g. `AAA`                                    |
|IP Address       |Your Home Assistant IP address (the HAOS VM’s tailnet IP, or LAN IP)        |
|Port             |A TCP port not used by anything else on your HA host — e.g. `12312`         |
|Preferred network|**Ethernet** (if hub is wired to your router)                               |
|Periodic reports |**1 minute** (HA marks the hub unavailable after ping_interval + 30 seconds)|
|Encryption       |**Optional but recommended** — 16, 24, or 32 ASCII hex characters           |


> 🔐 If you already use a professional ARC, this configuration replaces that connection. You cannot have both. The decision is yours: professional monitoring or HA integration. If both matter, proceed to the ALARMO architecture section at the end of this episode.

-----

### Step 3 — Add the SIA Integration in Home Assistant

In Home Assistant:

1. Go to **Settings → Devices & Services → + Add Integration**.
1. Search for **SIA Alarm Systems**.
1. Configure:

|Field          |Value                                           |
|---------------|------------------------------------------------|
|Port           |Same port you set in the Ajax app (`12312`)     |
|Account        |Same account ID (`AAA`)                         |
|Encryption key |Same key as in Ajax, if you enabled encryption  |
|Ping interval  |`1` (match what you set in Ajax app, in minutes)|
|Number of zones|The number of groups you created in Ajax        |

Click **Submit**. Home Assistant creates:

- One `alarm_control_panel` entity per zone/group combination
- One set of `binary_sensor` entities tracking alarm states

The entity names follow the pattern: `alarm_control_panel.{account}_{zone}_alarm`

For example, with account `AAA` and 2 zones:

```
alarm_control_panel.aaa_zone_1_alarm
alarm_control_panel.aaa_zone_2_alarm
```

-----

### Step 4 — Verify the Connection

Arm and disarm your Ajax system using the physical keypad or the Ajax app. Watch the entity states in **Developer Tools → States**, filtered on `alarm_control_panel`. You should see the states change:

- `armed_away` — system fully armed
- `disarmed` — system disarmed
- `armed_night` — night mode
- `triggered` — alarm sounding

If states do not update: check that the Ajax hub can reach your HA IP on the configured port. If your HAOS runs in a Parallels VM (as per Episode 3), ensure the VM is on **bridged networking** (not NAT) — the Ajax hub needs to reach the HA instance’s real LAN IP, not a Parallels internal address.

-----

## 🎛️ Part 2 — Control: The SpaceControl Relay Hack

SIA gives you eyes. The relay hack gives you hands.

The **Ajax SpaceControl** is a four-button wireless key fob — Arm, Disarm, Night Mode, and a fourth programmable button. Each button press sends a Jeweller-protocol command directly to the Ajax hub. Ajax trusts the SpaceControl implicitly; it is a registered, certified device.

The community-discovered approach: open a SpaceControl, identify the button contact pads, and wire a **4-channel relay** across those contacts. When the relay closes, it simulates a button press. Home Assistant controls the relay. Ajax receives a legitimate command from a legitimate registered device.

Ajax’s security guarantees remain intact — no firmware modification, no spoofing, no protocol reverse-engineering. You are simply pressing buttons electronically rather than with your thumb.

### What You Need

- **Ajax SpaceControl** key fob
- **4-channel Wi-Fi smart relay** with dry-contact (normally-open) outputs — brands that work well: Sonoff 4CH, Nous A8T, any ESPHome-compatible 4-channel relay module
- Basic soldering equipment
- A D1 Mini (Wemos ESP8266) or similar microcontroller running **ESPHome**, if your relay does not natively support Home Assistant

> ⚠️ **Opening the SpaceControl voids its warranty.** The device remains fully functional if you do not damage the PCB. The modification is reversible. Electrically, you are adding parallel contacts across existing button pads — the physical buttons continue to work normally.

-----

### Step 1 — Identify the Button Contacts on the SpaceControl PCB

Open the SpaceControl (two screws, plastic clip). The PCB has four button tactile switches corresponding to Arm, Disarm, Night, and the programmable button. Each switch has two legs. Identify the pads.

A multimeter on continuity mode, with the button pressed, will confirm which pads complete the circuit. You need access to both legs of each button contact — one will be common ground, the others will be the individual button signals.

> 📌 **Community-documented pinouts** for the SpaceControl are available in the [AlexeiakaTechnik GitHub repository](https://github.com/AlexeiakaTechnik/AJAX_security-integration-in-Home_Assistant) and the [Angelos Orfanakos blog](https://angelos.dev/2025/02/ajax-systems-alarm-system-in-home-assistant/) — both include photographs of the PCB with annotated contact points. Consult those before soldering.

-----

### Step 2 — Wire the Relay to the SpaceControl

Solder four pairs of wires from the relay’s dry-contact outputs to the four button pairs on the SpaceControl PCB:

|Relay channel|SpaceControl button    |
|-------------|-----------------------|
|Channel 1    |Arm                    |
|Channel 2    |Disarm                 |
|Channel 3    |Night Mode             |
|Channel 4    |Programmable (optional)|

Set each relay channel to **momentary mode** (pulse for 200–500ms rather than toggle). A button press is a momentary contact, not a sustained one. Most relay modules support this in firmware or hardware configuration.

-----

### Step 3 — Flash ESPHome (if using a bare relay module)

If your relay module does not natively support Home Assistant, flash it with **ESPHome**. A minimal configuration for a D1 Mini controlling a 4-channel relay:

```yaml
# esphome/ajax-spacecontrol.yaml
esphome:
  name: ajax-spacecontrol

esp8266:
  board: d1_mini

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret esphome_api_key

ota:
  password: !secret ota_password

switch:
  - platform: gpio
    name: "Ajax Arm"
    id: ajax_arm
    pin:
      number: D1
      inverted: true
    restore_mode: ALWAYS_OFF
    on_turn_on:
      - delay: 300ms
      - switch.turn_off: ajax_arm

  - platform: gpio
    name: "Ajax Disarm"
    id: ajax_disarm
    pin:
      number: D2
      inverted: true
    restore_mode: ALWAYS_OFF
    on_turn_on:
      - delay: 300ms
      - switch.turn_off: ajax_disarm

  - platform: gpio
    name: "Ajax Night"
    id: ajax_night
    pin:
      number: D3
      inverted: true
    restore_mode: ALWAYS_OFF
    on_turn_on:
      - delay: 300ms
      - switch.turn_off: ajax_night
```

The `delay: 300ms` followed by `turn_off` implements the momentary pulse. `restore_mode: ALWAYS_OFF` prevents the relay from activating on power-cycle — you do not want the alarm arming every time the relay module reboots.

Flash via the ESPHome dashboard in Home Assistant (**Settings → Add-ons → ESPHome**). The relay appears in HA as three switch entities.

-----

## 🔗 Part 3 — Tying It Together: The Unified Alarm Interface

With SIA giving you state and the SpaceControl relay giving you control, you now have the inputs and outputs to create a unified alarm interface in Home Assistant.

### Creating a Virtual Alarm Panel with ALARMO

Rather than controlling the SpaceControl switches directly, install **ALARMO** — a community add-on that creates a virtual `alarm_control_panel` entity with its own arm/disarm logic, sensor groups, and exit/entry delay management.

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
1. Add the HACS repository or the ALARMO add-on repository.
1. Install **ALARMO**.
1. In ALARMO, configure your sensors (map your Ajax groups to ALARMO zones).
1. Set ALARMO automations to trigger the SpaceControl relay switches when ALARMO’s state changes.

```yaml
# Example: ALARMO → SpaceControl relay sync
automation:
  - alias: "ALARMO arm → trigger Ajax Arm relay"
    triggers:
      - trigger: state
        entity_id: alarm_control_panel.alarmo
        to: "armed_away"
    actions:
      - action: switch.turn_on
        target:
          entity_id: switch.ajax_arm

  - alias: "ALARMO disarm → trigger Ajax Disarm relay"
    triggers:
      - trigger: state
        entity_id: alarm_control_panel.alarmo
        to: "disarmed"
    actions:
      - action: switch.turn_on
        target:
          entity_id: switch.ajax_disarm

  - alias: "ALARMO night → trigger Ajax Night relay"
    triggers:
      - trigger: state
        entity_id: alarm_control_panel.alarmo
        to: "armed_night"
    actions:
      - action: switch.turn_on
        target:
          entity_id: switch.ajax_night
```

And the reverse — sync SIA state back to ALARMO:

```yaml
automation:
  - alias: "SIA state → sync to ALARMO"
    triggers:
      - trigger: state
        entity_id: alarm_control_panel.aaa_zone_1_alarm
    conditions:
      - condition: template
        value_template: >
          {{ states('alarm_control_panel.aaa_zone_1_alarm') !=
             states('alarm_control_panel.alarmo') }}
    actions:
      - action: alarmo.arm
        data:
          mode: >
            {% set s = states('alarm_control_panel.aaa_zone_1_alarm') %}
            {% if s == 'armed_away' %}away
            {% elif s == 'armed_night' %}night
            {% else %}disarmed{% endif %}
        target:
          entity_id: alarm_control_panel.alarmo
```

This bidirectional sync means ALARMO and Ajax stay in agreement. The physical keypad or SpaceControl updates ALARMO via SIA. ALARMO changing state (from a presence-based automation or from the HA dashboard) triggers the relay to update Ajax.

-----

## 📊 The Dashboard — Your Alarm Panel Card

Add an alarm control panel card to your iPad Mini dashboard:

```yaml
type: vertical-stack
cards:
  - type: alarm-panel
    entity: alarm_control_panel.alarmo
    name: Home Security
    states:
      - arm_home
      - arm_away
      - arm_night

  - type: glance
    title: Ajax Status
    entities:
      - entity: alarm_control_panel.aaa_zone_1_alarm
        name: Ground Floor
      - entity: alarm_control_panel.aaa_zone_2_alarm
        name: First Floor

  - type: grid
    columns: 3
    square: false
    cards:
      - type: button
        name: Arm
        icon: mdi:shield-lock
        tap_action:
          action: call-service
          service: alarm_control_panel.alarm_arm_away
          target:
            entity_id: alarm_control_panel.alarmo
      - type: button
        name: Night
        icon: mdi:shield-moon
        tap_action:
          action: call-service
          service: alarm_control_panel.alarm_arm_night
          target:
            entity_id: alarm_control_panel.alarmo
      - type: button
        name: Disarm
        icon: mdi:shield-off
        tap_action:
          action: call-service
          service: alarm_control_panel.alarm_disarm
          target:
            entity_id: alarm_control_panel.alarmo
```

-----

## 🔔 Practical Automations

### Arm when you leave

```yaml
automation:
  - alias: "Arm Ajax when house is empty"
    triggers:
      - trigger: state
        entity_id: group.everyone
        to: "not_home"
        for: "00:05:00"
    conditions:
      - condition: state
        entity_id: alarm_control_panel.alarmo
        state: "disarmed"
    actions:
      - action: alarm_control_panel.alarm_arm_away
        target:
          entity_id: alarm_control_panel.alarmo
```

### Critical alert when alarm triggers

```yaml
automation:
  - alias: "Alert on alarm trigger"
    triggers:
      - trigger: state
        entity_id: alarm_control_panel.aaa_zone_1_alarm
        to: "triggered"
    actions:
      - action: notify.mobile_app_ipad_mini
        data:
          title: "🚨 ALARM TRIGGERED"
          message: >
            Ajax alarm triggered at {{ now().strftime('%H:%M') }}.
            Zone: Ground Floor.
          data:
            push:
              interruption-level: critical
```

### SIA event bus automation (advanced)

For finer control, trigger automations directly on raw SIA event codes — bypassing the `alarm_control_panel` entity state and reacting to individual SIA messages:

```yaml
automation:
  - alias: "React to SIA burglary event code"
    triggers:
      - trigger: event
        event_type: sia_event_12312_AAA
        event_data:
          code: BA
    actions:
      - action: notify.mobile_app_ipad_mini
        data:
          title: "🚨 Burglary Alarm"
          message: >
            SIA BA code received at {{ trigger.event.data.timestamp }}.
            Zone: {{ trigger.event.data.ri }}.
          data:
            push:
              interruption-level: critical
```

The event type follows the pattern `sia_event_{port}_{account}` — for port `12312` and account `AAA`, that is `sia_event_12312_AAA`.

-----

## ⚖️ The Three Integration Paths — Choosing Yours

The community has explored several approaches. Here is an honest summary:

|Method                      |Arm/Disarm         |Sensor states               |Cloud needed         |ARC compatible       |Complexity                            |
|----------------------------|-------------------|----------------------------|---------------------|---------------------|--------------------------------------|
|**SIA + SpaceControl relay**|✅ Via relay        |✅ Via SIA                   |❌ Fully local        |❌ One connection only|Medium                                |
|**Jeedom + MQTT bridge**    |✅ Via Jeedom plugin|✅ Continuous (even disarmed)|✅ Ajax cloud required|✅ Yes                |High                                  |
|**Enterprise API**          |✅ Full             |✅ Full                      |✅ Required           |✅ Yes                |Very high + requires installer account|
|**foXaCe HACS integration** |✅                  |✅                           |Varies               |Varies               |Low (HACS install)                    |


> 📌 **The [foXaCe HACS integration](https://github.com/foXaCe/ajax-security-hass)** is worth checking — it uses the Ajax API via a modified approach and has an active community. It may suit your setup if the SIA + relay approach feels too involved.

For a home without professional monitoring already in place, **SIA + SpaceControl relay** is the cleanest and most local-first solution. It requires the most hardware work, but produces the most resilient result: no cloud dependency, no third-party service, no monthly fee.

-----

## 🔐 The Panic Room Sensor Grid

With Ajax integrated, your Home Assistant dashboard now shows:

|Entity                                |What it reflects                                    |
|--------------------------------------|----------------------------------------------------|
|`alarm_control_panel.alarmo`          |The unified virtual alarm panel — arm/disarm from HA|
|`alarm_control_panel.aaa_zone_1_alarm`|Ground floor Ajax group state via SIA               |
|`alarm_control_panel.aaa_zone_2_alarm`|First floor Ajax group state via SIA                |
|`switch.ajax_arm`                     |Relay that presses Arm on the SpaceControl          |
|`switch.ajax_disarm`                  |Relay that presses Disarm on the SpaceControl       |
|`switch.ajax_night`                   |Relay that presses Night on the SpaceControl        |

From your iPad Mini — from a coffeeshop, from Guernsey in September, from anywhere in your Tailscale tailnet — you can see whether the alarm is armed, receive critical push notifications if it triggers, and arm or disarm it with a tap.

The panic room has its alarm system. It is independent. It is local. It is watching.

> *“The room knows when someone’s in the house who shouldn’t be.”*
> — Panic Room (2002).
> *“Home Assistant knows when the SIA code says BA.”*
> — Also Panic Room (this episode).

-----

## 🔭 Further Reading

- [HA SIA Integration documentation](https://www.home-assistant.io/integrations/sia/)
- [AlexeiakaTechnik GitHub — full Ajax integration guide](https://github.com/AlexeiakaTechnik/AJAX_security-integration-in-Home_Assistant)
- [AlexeiakaTechnik GitHub — SIA as automation triggers](https://github.com/AlexeiakaTechnik/Use-Ajax-Security-alarm-sensors-as-a-Automation-Triggers-in-Home-Assistant)
- [foXaCe Ajax HACS integration](https://github.com/foXaCe/ajax-security-hass)
- [Angelos Orfanakos — Ajax in HA walkthrough](https://angelos.dev/2025/02/ajax-systems-alarm-system-in-home-assistant/)
- [HA Community thread — Ajax SIA discussion](https://community.home-assistant.io/t/ajax-security-system-integration-in-ha/911193)

-----

*🔐 Panic Room is a series about building a secure, local-first smart home using Home Assistant — installed on a Mac Mini M4 Pro via Parallels, connected via Tailscale, and controlled from an iPad Mini anywhere in the world.*
