---
title: "Panic Room — Ep.7"
part: 7
published: false
description: "The panic room doesn't need Meg to operate it — it locks itself, the cameras run themselves, the ventilation maintains itself. Your smart home should work the same way. This is automations."
tags: [homeassistant, automations, scenes, smarthome]
series: "Panic Room Home Assistant Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/panic_room_home_assistant_series/panic-room-home-assistant-episode-07.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🔐 The House Thinks for Itself (Automations & Scenes)

> *"This room was built to protect whatever's inside it. Automatically."*
> — Burnham, Panic Room.
> *"This home automation was built to protect whatever's inside it. Automatically."*
> — Home Assistant, Episode 7.

---

## 🤖 The Autonomous Panic Room

The panic room in the film does not require Meg to manually operate every system. The steel door locks itself when closed. The ventilation runs on its own cycle. The cameras record continuously without anyone pressing a button. The room is **autonomous** — it does its job whether or not a human is paying attention.

This is the goal of home automation done right. Not a sophisticated remote control that lets you turn lights on from the coffeeshop (though that is useful). But a home that *acts* — that responds to context, time, presence, and events — without needing you to initiate every action.

This episode is about building that autonomous layer. Triggers, conditions, actions. Scenes for common states. Scripts for repeatable sequences. The full vocabulary of Home Assistant automations.

---

## 📋 SIPOC — The Autonomous Home

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Home Assistant automation engine | Device states, sensor readings, time, GPS presence | Trigger → Condition → Action chains | Autonomous home behaviour | The household, without lifting a finger |
| Your integrations (lights, sensors, climate) | Person entities (Willem, Rianne) | Build automation library → Test → Refine | Lights that respond to presence, climate that anticipates needs | Rianne, impressed for the first time |
| iOS push notification system | Time schedules and solar events (sunrise, sunset) | Create scenes for common states | Clean, readable home states with one tap | Guests who ask "how did that just happen?" |
| Your imagination | Motion sensors, door sensors, energy monitors | Use blueprints for common patterns → Customise | A home that has opinions about itself | Future you, who has long since forgotten manual switches |

---

## 📚 The Vocabulary

Before we build, a quick primer on the Home Assistant automation vocabulary:

| Term | What It Means | Panic Room Equivalent |
|---|---|---|
| **Trigger** | The event that starts the automation | The door sensor detecting a breach |
| **Condition** | A test that must pass for the action to run | Is it after 22:00? Is anyone home? |
| **Action** | What happens when trigger fires and conditions pass | Lock the door, alert Meg, turn on cameras |
| **Scene** | A saved set of device states | "Movie Mode" — lights dimmed, TV on |
| **Script** | A reusable sequence of actions | The "Goodnight" routine |
| **Blueprint** | A shareable automation template | Pre-built panic room schematics |

---

## 🌅 Automation 1 — The Sunrise/Sunset Cycle

The most fundamental automation: lights that follow the sun.

**Sunset — Evening Lighting**
```yaml
automation:
  - alias: "Evening: Activate living room lighting at sunset"
    triggers:
      - trigger: sun
        event: sunset
        offset: "-00:30:00"   # 30 minutes before sunset
    conditions:
      - condition: or
        conditions:
          - condition: state
            entity_id: person.willem
            state: home
          - condition: state
            entity_id: person.rianne
            state: home
    actions:
      - action: light.turn_on
        target:
          area_id: living_room
        data:
          brightness_pct: 70
          color_temp_kelvin: 3000   # Warm white, evening ambience
```

**Sunrise — Morning Fade-in**
```yaml
automation:
  - alias: "Morning: Gently brighten kitchen at sunrise"
    triggers:
      - trigger: sun
        event: sunrise
        offset: "+00:15:00"   # 15 minutes after sunrise
    conditions:
      - condition: state
        entity_id: person.willem
        state: home
    actions:
      - action: light.turn_on
        target:
          area_id: kitchen
        data:
          brightness_pct: 40
          color_temp_kelvin: 5000   # Cool white, morning energy
          transition: 120           # Fade in over 2 minutes
```

---

## 🏠 Automation 2 — Presence-Based Welcome Home

When either Willem or Rianne arrives home (detected via Companion App GPS), the house prepares:

```yaml
automation:
  - alias: "Welcome home: activate on arrival"
    triggers:
      - trigger: state
        entity_id:
          - person.willem
          - person.rianne
        from: "not_home"
        to: "home"
    conditions:
      - condition: sun
        after: sunset           # Only run if it is dark outside
    actions:
      - action: scene.turn_on
        target:
          entity_id: scene.welcome_home
      - action: notify.mobile_app_ipad_mini
        data:
          message: >
            Welcome home, {{ trigger.to_state.attributes.friendly_name }}.
            Temperature inside: {{ states('sensor.living_room_temperature') }}°C.
```

The **Welcome Home scene** (`scene.welcome_home`) might include:
- Living room lights at 65%, warm white
- Hallway lights at 100% for 5 minutes (then auto-off)
- Thermostat set to comfort temperature
- Any "away mode" security changes reversed

Create the scene under **Settings → Scenes → + Add Scene**, then add all the device states you want included.

---

## 🌙 Automation 3 — The Goodnight Script

Rather than an automation, use a **Script** for the bedtime routine — because you want to be able to trigger it manually (from the dashboard or a button) as well as automatically:

```yaml
script:
  goodnight:
    alias: "Goodnight"
    sequence:
      # Turn off all lights except bedroom
      - action: light.turn_off
        target:
          area_id:
            - living_room
            - kitchen
            - hallway
            - office
      # Set bedroom to dim red (sleep-friendly)
      - action: light.turn_on
        target:
          area_id: bedroom
        data:
          brightness_pct: 10
          color_name: red
      # Lock the front door
      - action: lock.lock
        target:
          entity_id: lock.front_door
      # Set thermostat to night mode
      - action: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: 18
      # Confirm via notification
      - action: notify.mobile_app_ipad_mini
        data:
          message: "🌙 Goodnight. The house is secured."
          title: "Home Assistant"
```

Add a **Tile card** button to your iPad Mini dashboard labelled "Goodnight" that calls this script. One tap before bed. The panic room seals itself.

---

## 🔒 Automation 4 — Leaving Home Security Mode

When the last person leaves the house:

```yaml
automation:
  - alias: "Leaving: activate away mode when house is empty"
    triggers:
      - trigger: state
        entity_id: group.everyone
        to: "not_home"
        for: "00:05:00"   # 5 minutes grace period to avoid false triggers
    actions:
      # Turn off all non-essential devices
      - action: homeassistant.turn_off
        target:
          area_id:
            - living_room
            - kitchen
            - office
      # Enable security sensors
      - action: input_boolean.turn_on
        target:
          entity_id: input_boolean.away_mode
      # Confirm
      - action: notify.mobile_app_ipad_mini
        data:
          title: "🏠 House is empty"
          message: >
            Away mode activated at {{ now().strftime('%H:%M') }}.
            All lights off. Security sensors active.
```

The `group.everyone` entity requires a group definition:

```yaml
# configuration.yaml
group:
  everyone:
    name: Everyone
    entities:
      - person.willem
      - person.rianne
```

---

## 🔔 Automation 5 — The Panic Room Alarm

The security automation: when a door or window sensor opens while away mode is active, alert immediately.

```yaml
automation:
  - alias: "Security: alert on entry while away"
    triggers:
      - trigger: state
        entity_id:
          - binary_sensor.front_door
          - binary_sensor.back_door
          - binary_sensor.ground_floor_window
        to: "on"
    conditions:
      - condition: state
        entity_id: input_boolean.away_mode
        state: "on"
    actions:
      - action: notify.mobile_app_ipad_mini
        data:
          title: "🚨 Security alert"
          message: >
            {{ trigger.to_state.attributes.friendly_name }} opened at
            {{ now().strftime('%H:%M') }}.
          data:
            push:
              sound: "default"
              interruption-level: critical   # Bypasses Do Not Disturb on iOS
            actions:
              - action: "VIEW_CAMERAS"
                title: "View cameras"
              - action: "ALL_CLEAR"
                title: "All clear"
```

The `interruption-level: critical` flag is important: this notification **bypasses iOS Do Not Disturb and Focus modes**. When your house has a potential intruder, you want to know — even if your iPad is on silent.

This is the panic room calling Meg's phone. It does not wait for her to check her messages.

---

## 🎬 Scenes — Common States at a Touch

Scenes capture a moment: a specific configuration of lights, climate, and media that corresponds to an activity or mood. Build these for your most common use cases:

| Scene | What It Sets |
|---|---|
| **Movie Mode** | Living room lights at 5% dim red, TV on, thermostat 21°C |
| **Working from Home** | Office lights 100% cool white, do-not-disturb notification, thermostat 20°C |
| **Dinner** | Kitchen and dining lights at 80% warm, TV off |
| **Welcome Home** | Hallway full, living room warm, thermostat comfort |
| **Goodnight** | (covered by the script above) |
| **Away** | All lights off, thermostat eco, away mode on |

Add scene buttons to your iPad Mini dashboard as large, easy-to-tap Tile cards. One tap to shift the entire house into a new state.

---

## ⏲️ Time-Based Automations Worth Adding

A few more patterns that make the house genuinely intelligent:

**Turn off forgotten lights automatically:**
```yaml
automation:
  - alias: "Auto-off: lights on when no one in room"
    triggers:
      - trigger: state
        entity_id: binary_sensor.living_room_motion
        to: "off"
        for: "00:30:00"
    actions:
      - action: light.turn_off
        target:
          area_id: living_room
```

**Dog feeding reminder (Beau & Elvis):**
```yaml
automation:
  - alias: "Dog feeding reminder — morning"
    triggers:
      - trigger: time
        at: "07:30:00"
    conditions:
      - condition: state
        entity_id: person.willem
        state: home
    actions:
      - action: notify.mobile_app_ipad_mini
        data:
          message: "🐾 Time to feed Beau and Elvis."
```

**Energy monitor — high consumption alert:**
```yaml
automation:
  - alias: "Energy: alert on unusual consumption"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.home_power_consumption
        above: 3000   # Watts — adjust for your home
    actions:
      - action: notify.mobile_app_ipad_mini
        data:
          message: >
            ⚡ High power consumption: {{ states('sensor.home_power_consumption') }}W.
            Something high-draw is running.
```

---

## 📖 Using Blueprints

You do not need to write every automation from scratch. The Home Assistant community maintains a library of **blueprints** — shareable, configurable automation templates.

Access them at **Settings → Automations & Scenes → Blueprints → Import Blueprint**.

The community Blueprint Exchange ([community.home-assistant.io](https://community.home-assistant.io/c/blueprints-exchange/53)) has thousands of ready-made automations for:
- Motion-activated lighting with timeout
- Away-mode security alerts
- Battery low notifications for all sensors
- Presence-based thermostat control
- Notification-based door lock management

Import a blueprint, fill in your entity names, and you have a tested, community-proven automation running in minutes.

---

## 🔐 The Panic Room Is Fully Operational

Over seven episodes, we have built:

| Component | Status |
|---|---|
| HAOS in Parallels on Mac Mini M4 Pro | ✅ Running 24/7 |
| Onboarded, areas defined, integrations connected | ✅ Devices visible and controllable |
| Tailscale add-on installed | ✅ Accessible from anywhere on Earth |
| iPad Mini Companion App configured | ✅ Remote dashboard and presence detection |
| Automations: presence, time, security, alerts | ✅ House acts autonomously |
| Push notifications with critical alerts | ✅ House communicates with you |

The panic room is fully operational. The steel door is solid. The independent phone line is live. The surveillance feeds are running. And the house — your house in Eersel, containing Rianne and the dachshunds and the lights and the sensors and the energy monitor — does not simply sit there waiting to be controlled.

It thinks for itself.

> *"You have no idea how unprepared they were for someone who was prepared."*
> — Burnham, Panic Room.
> *"You have no idea how well your home handles things when you have prepared it properly."*
> — This series.

---

## 🔭 What Comes Next (Beyond This Series)

The panic room has been built. But a well-prepared home is never truly finished — it evolves as new devices arrive, new integrations become available, and new automations suggest themselves. Some directions worth exploring:

- **Zigbee/Z-Wave**: add a USB coordinator stick to the Parallels VM for direct local radio device control (no cloud bridge needed for supported devices)
- **Frigate**: local AI-powered camera object detection — person/animal/vehicle recognition, stored on your own hardware
- **Whisper + Piper**: fully local voice assistant — speak to your home without any cloud API
- **ESPHome**: flash custom firmware to cheap ESP32/ESP8266 microcontrollers and add sensors anywhere in the house for under €5 per unit
- **Energy Dashboard**: track solar generation, grid import/export, per-device consumption
- **HACS** (Home Assistant Community Store): custom integrations, custom dashboard cards, community-maintained extensions

The panic room has a solid foundation. Build from here.

> *"Come on. Let's go home."*
> — Meg Altman, Panic Room. (Final line of the film.)
> *"It's already home. And it's already ready."*
> — Your smart home, Episode 7.

---

*🔐 Panic Room is a series about building a secure, local-first smart home using Home Assistant — installed on a Mac Mini M4 Pro via Parallels, connected via Tailscale, and controlled from an iPad Mini anywhere in the world.*
