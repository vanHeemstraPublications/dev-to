---
title: "Magic Lamp Ep.1"
published: false
description: "How a lifeless desk lamp becomes a vivid stage character through Python, OSC, servo control, and voice AI — a technical origin story."
tags: ["python", "hardware", "showcontrol", "makers"]
part: 1
series: "Magic Lamp Series"
organization: "the-software-s-journey"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/magic_lamp_series/magic-lamp-episode-01.png"
---

> *"You'll like it — not a lot, but you'll like it."*
> — Paul Daniels

Paul Daniels never actually made things appear from nowhere. The secret to his act was subtler: he made *you* see life in the lifeless. A silk handkerchief folded just so. A coin that hesitated before vanishing. The magic wasn't in the props — it was in the relationship between performer and object. The audience believed because the performer believed first.

This is a project that works the same way.

---

## 🎭 The Performance

**PIXSTARS** is a 20-minute silent theatrical piece for a live event. The setup is deliberately sparse:

- One performer on stage
- One animatronic desk lamp named **Pinokio**
- A live piano
- A deconstructed rendering of Guns N' Roses' *November Rain*
- No dialogue. Not a single word.

The lamp is not a prop. It is a co-performer. It has 14 distinct personality states — from `INERT` to `ARROGANT` to `DYING` to `REBORN` — and moves through them on choreographed cues as the music plays. The performer holds three simultaneous character identities (Rockstar, Creator, Witness). The lamp holds the mirror.

Think Kim Ki-duk, not Cirque du Soleil. Sparse. Patient. Emotionally loaded.

---

## 🪄 The Paul Daniels Problem

When Paul Daniels placed a lifeless prop on his table, it was just an object. The moment he began working with it — tilting, pausing, reacting — it became a *character*. The prop hadn't changed. The frame around it had.

Building Pinokio means solving the same problem in code: how do you cross the line from *object that moves* to *character that lives*?

The answer, it turns out, is architecture.

A lamp that moves on command is a prop. A lamp that has **emotional states**, **reacts to music**, **speaks with its body**, and **wakes up on cue** — that's a character. The difference is not hardware. It's the layer of abstraction between the mechanical and the theatrical.

This series documents exactly how that abstraction is built.

---

## 🏗️ The Stack

Before we get into code, here is the complete hardware and software picture.

**Hardware:**

| Component | Role |
|-----------|------|
| Mac Mini M4 Pro | Show control host, runs everything |
| Pololu Mini Maestro 24-ch USB servo controller | Lamp motion brain |
| 4x MG996R servos | Large articulation: base, shoulder, elbow, head tilt |
| 2x MG90S servos | Fine motion |
| MEAN WELL LRS-50-5 PSU | 5V servo rail, isolated from logic |
| Arduino Nano | NeoPixel serial bridge (the Maestro doesn't speak NeoPixel) |
| NeoPixel RGBW ring | Lamp head LED indicator |
| Logitech C920 webcam | Mounted near lamp — gaze source or projection input |
| Raspberry Pi Zero 2 WH | Satellite node: mic, speaker, LED — no soldering required |
| Enttec DMX USB Pro | Stage lighting control |

**Software subsystems** (all on the Mac Mini):

```
┌─────────────────────────────────────────────────────┐
│                   SHOW CONDUCTOR                    │
│           conductor/main.py  (YAML timeline)        │
└────────┬──────────┬──────────┬──────────┬───────────┘
         │ OSC      │ OSC      │ OSC      │ OSC
         ▼          ▼          ▼          ▼
    Port 3819   Port 9001   Port 9002   Port 9003
    ┌───────┐  ┌────────┐  ┌──────────┐  ┌─────────┐
    │Ardour │  │  Lamp  │  │Projection│  │Lighting │
    │  DAW  │  │adapter │  │(pygame)  │  │  (DMX)  │
    └───────┘  └────────┘  └──────────┘  └─────────┘
                                  all mirrored to
                              Port 9004 / WS 8765
                         ┌──────────────────────┐
                         │    Digital Twin      │
                         │  (BabylonJS + Deno)  │
                         └──────────────────────┘
```

Every subsystem speaks **OSC** (Open Sound Control) over UDP on localhost. The conductor doesn't know or care whether the lamp adapter talks to real servos or a simulator — it just sends `/lamp/state CURIOUS` and moves on.

That decoupling is the key architectural decision. More on that in episode 2.

---

## 🎛️ OSC: The Nervous System

OSC is the protocol that holds the show together. It's a UDP-based message format originally designed for musical instruments and live sound, which makes it a natural fit for real-time stage control. Messages look like:

```
/lamp/state        CURIOUS
/projection/scene  DISNEY_CASTLE
/lighting/state    DISNEY_SOFT
/toggle_roll       (Ardour play/stop)
```

Each subsystem listens on its own port. The conductor dispatches all messages for a single cue within the same 50ms polling tick. The result is near-simultaneous state transitions across audio, video, light, and motion.

The complete port map:

```python
# conductor/config.py
ARDOUR_OSC_PORT     = 3819   # Ardour 9 control surface
LAMP_OSC_PORT       = 9001   # Lamp personality adapter
PROJECTION_OSC_PORT = 9002   # Pygame display
LIGHTING_OSC_PORT   = 9003   # Enttec DMX USB Pro
TWIN_OSC_PORT       = 9004   # Digital Twin OSC bridge
TWIN_WS_PORT        = 8765   # Digital Twin WebSocket (browser)
```

---

## ⏱️ The Timeline: 15 Cues, 9 Minutes 15 Seconds

The entire show lives in a single YAML file. Here's a slice:

```yaml
# conductor/timeline.yaml (excerpt)
cues:
  - time: 0.0
    name: SHOW_START
    lamp: INERT
    projection: BLACKOUT
    lighting: BLACKOUT
    ardour: {command: transport_play}

  - time: 60.0
    name: DRUMS_BEGIN
    lamp: CURIOUS

  - time: 340.0
    name: OVERHEATING
    lamp: OVERHEATING
    lighting: OVERHEAT

  - time: 380.0
    name: LAMP_DEATH
    lamp: DYING
    lighting: DEATH

  - time: 460.0
    name: REVEAL_AI
    lamp: WEAK
    projection: AI_SIGNATURE
    lighting: REBIRTH
```

At second 0, the lamp is `INERT` and Ardour begins playing. By second 60, the drums enter and the lamp becomes `CURIOUS`. By second 380, it is `DYING`. The arc from object to character to death to rebirth — all scripted, all precise, all driven by this YAML.

Paul Daniels rehearsed his timing with a stopwatch. So does Pinokio.

---

## 🔮 What's Coming in This Series

| Episode | Topic |
|---------|-------|
| **1** (this one) | Architecture overview — the magic prop metaphor |
| **2** | The Show Conductor — OSC dispatching and timeline execution |
| **3** | 14 Personalities in a Lampshade — servo states and motion vocabulary |
| **4** | Light the Stage — DMX control, pygame projection, and the digital twin |
| **5** | Finding Its Voice — HiveMind, Coqui XTTS, and the Raspberry Pi satellite |

By the end of episode 5, Pinokio will have gone from a desk lamp on a table to a character capable of reacting to music, shifting emotional states on cue, speaking in a synthesised voice, and lighting up its own head in synchrony with its mood — all orchestrated from a single Python process on a Mac Mini.

Not a lot. But you'll like it.

---

*Next: Episode 2 — The Show Conductor: how 15 YAML cues orchestrate five subsystems in real time.*
