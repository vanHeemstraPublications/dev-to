---
title: "Magic Lamp Ep.3"
published: false
description: "How 14 named emotional states give an animatronic desk lamp a motion vocabulary — the bridge between servo hardware and theatrical character."
tags: ["python", "hardware", "servos", "robotics"]
part: 3
series: "Magic Lamp Series"
organization: "the-software-s-journey"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/magic_lamp_series/magic-lamp-episode-03.png"
---

> *"The prop doesn't do the trick. You do. The prop just gives you something to react to."*

Paul Daniels' props were never neutral. The way he held them, paused over them, recoiled from them — the prop's apparent personality was entirely constructed by the performer's relationship to it. The object was a mirror.

Pinokio is the mirror that moves back.

---

## 🎭 The Problem with Servo Control

Direct servo control is simple: send a pulse-width value, the motor moves to that angle. But direct control produces *mechanical* motion — precise, repeatable, dead.

Dead is exactly what we need to avoid.

The challenge is that there's no clean mapping from "theatrical intent" to "servo position." You can't write `lamp.be_arrogant()` and have a servo understand what arrogance looks like. So you need an intermediate layer — a vocabulary of named emotional states that encode motion *parameters*, not positions. The motion engine then generates continuous movement within those parameters.

That's what `lamp/states.py` implements.

---

## 📐 The LampState Dataclass

Each of the 14 states is a `LampState` instance with five motion parameters:

```python
# lamp/states.py
from dataclasses import dataclass

@dataclass
class LampState:
    name: str
    energy: float      # 0.0–1.0  overall movement intensity
    speed: float       # 0.0–1.0  how fast transitions happen
    range: float       # 0.0–1.0  amplitude of movement arcs
    jitter: float      # 0.0–1.0  randomness / micro-tremor
    tilt_bias: float   # -1.0–1.0 vertical lean: -1 = drooping, +1 = proud
```

None of these are servo positions. They are *character descriptors* that a downstream motion engine can interpret. The lamp adapter translates them into actual servo commands for the Pololu Mini Maestro controller.

---

## 🎨 All 14 States

```python
# lamp/states.py (complete definitions)

STATES: dict[str, LampState] = {
    "INERT": LampState(
        name="INERT",
        energy=0.0, speed=0.0, range=0.0, jitter=0.0, tilt_bias=0.0
    ),
    "FUNCTIONAL": LampState(
        name="FUNCTIONAL",
        energy=0.1, speed=0.2, range=0.1, jitter=0.02, tilt_bias=0.0
    ),
    "CURIOUS": LampState(
        name="CURIOUS",
        energy=0.4, speed=0.5, range=0.4, jitter=0.05, tilt_bias=0.2
    ),
    "DISMISSIVE": LampState(
        name="DISMISSIVE",
        energy=0.3, speed=0.3, range=0.3, jitter=0.02, tilt_bias=-0.2
    ),
    "PLEASED": LampState(
        name="PLEASED",
        energy=0.5, speed=0.4, range=0.4, jitter=0.03, tilt_bias=0.3
    ),
    "ARROGANT": LampState(
        name="ARROGANT",
        energy=0.7, speed=0.5, range=0.6, jitter=0.04, tilt_bias=0.8
    ),
    "OVERHEATING": LampState(
        name="OVERHEATING",
        energy=0.9, speed=0.8, range=0.7, jitter=0.3, tilt_bias=0.0
    ),
    "DYING": LampState(
        name="DYING",
        energy=0.4, speed=0.2, range=0.3, jitter=0.15, tilt_bias=-0.5
    ),
    "DEAD": LampState(
        name="DEAD",
        energy=0.0, speed=0.0, range=0.0, jitter=0.0, tilt_bias=-1.0
    ),
    "WEAK": LampState(
        name="WEAK",
        energy=0.1, speed=0.1, range=0.1, jitter=0.08, tilt_bias=-0.6
    ),
    "REBORN": LampState(
        name="REBORN",
        energy=0.5, speed=0.4, range=0.5, jitter=0.06, tilt_bias=0.4
    ),
    "LEARNING": LampState(
        name="LEARNING",
        energy=0.4, speed=0.3, range=0.4, jitter=0.05, tilt_bias=0.1
    ),
    "CELEBRATE": LampState(
        name="CELEBRATE",
        energy=0.8, speed=0.7, range=0.7, jitter=0.08, tilt_bias=0.5
    ),
    "OFF": LampState(
        name="OFF",
        energy=0.0, speed=0.0, range=0.0, jitter=0.0, tilt_bias=0.0
    ),
}

def get_state(name: str) -> LampState:
    if name not in STATES:
        raise ValueError(f"Unknown lamp state: {name!r}")
    return STATES[name]
```

---

## 📊 Reading the States as Character

The parameters tell a clear story when you read them as a group:

| State | Energy | Speed | Range | Jitter | Tilt Bias | Character read |
|-------|--------|-------|-------|--------|-----------|----------------|
| INERT | 0.0 | 0.0 | 0.0 | 0.00 | 0.0 | Powered off. Nothing. |
| FUNCTIONAL | 0.1 | 0.2 | 0.1 | 0.02 | 0.0 | Alive but neutral. Minimal idle. |
| CURIOUS | 0.4 | 0.5 | 0.4 | 0.05 | +0.2 | Tilting forward, interested. |
| ARROGANT | 0.7 | 0.5 | 0.6 | 0.04 | +0.8 | Exaggerated proud posture. |
| OVERHEATING | 0.9 | 0.8 | 0.7 | 0.30 | 0.0 | Erratic. Unstable. High jitter. |
| DYING | 0.4 | 0.2 | 0.3 | 0.15 | -0.5 | Slowing. Drooping. Spasms. |
| DEAD | 0.0 | 0.0 | 0.0 | 0.00 | -1.0 | Fully collapsed. |
| WEAK | 0.1 | 0.1 | 0.1 | 0.08 | -0.6 | Barely alive. Faint twitches. |
| REBORN | 0.5 | 0.4 | 0.5 | 0.06 | +0.4 | Rising. Rediscovering. |
| CELEBRATE | 0.8 | 0.7 | 0.7 | 0.08 | +0.5 | Joyful. Rhythmic swinging. |

Notice `OVERHEATING`: energy is highest (0.9), jitter is by far the highest (0.30). This produces the visually distinctive quality of a machine losing control of itself — a very different motion signature from `ARROGANT`, which has high energy but very low jitter (0.04), producing deliberate, imperious movement.

`DYING` and `WEAK` are similarly distinct: `DYING` still has range (0.3) and moderate jitter — it struggles. `WEAK` has almost no range but persistent jitter — it barely flickers. The narrative difference is in the numbers.

---

## 🔌 The Lamp Adapter

`lamp/adapter.py` is the OSC listener that receives state commands and drives the Pololu Mini Maestro controller:

```python
# lamp/adapter.py
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from lamp.states import get_state, LampState

class LampAdapter:
    def __init__(self, port: int = 9001):
        self.port = port
        self.current_state: LampState | None = None

        dispatcher = Dispatcher()
        dispatcher.map("/lamp/state", self._handle_state)
        self.server = BlockingOSCUDPServer(("127.0.0.1", port), dispatcher)

    def _handle_state(self, address: str, *args):
        state_name = str(args[0])
        state = get_state(state_name)      # validates; raises on unknown
        self.current_state = state

        print(f"[LAMP] State -> {state.name} "
              f"(energy={state.energy}, jitter={state.jitter})")

        # Motion engine integration point:
        # When connected to Jess+ DataBorg or direct Maestro serial:
        #   send_to_maestro(state)
        # When connected to HiveMind:
        #   hivemind.master_stream = state.energy
        #   hivemind.rhythm_rate = state.speed

    def start(self):
        print(f"[LAMP] Adapter listening on port {self.port}")
        self.server.serve_forever()
```

The comment block at the motion engine integration point is load-bearing: it documents the exact interface the hardware driver will plug into. The state parameters flow in; servo commands flow out. The adapter stays thin.

---

## ⚙️ Hardware: The Pololu Mini Maestro

The **Pololu Mini Maestro 24-channel USB servo controller** drives the physical lamp. Its channel map:

| Channel | Servo | Joint |
|---------|-------|-------|
| 0 | MG996R | Base rotation |
| 1 | MG996R | Shoulder pitch |
| 2 | MG996R | Elbow flex |
| 3 | MG996R | Head tilt |
| 4 | MG90S | Fine wrist |
| 5 | MG90S | Fine pan |

The Maestro accepts pulse-width values (in quarter-microseconds) over USB serial. A value of 6000 corresponds to 1500us (neutral). The motion engine maps the `LampState` parameters into continuous position commands at runtime.

Power separation is deliberate: the **MEAN WELL LRS-50-5** runs the 5V servo rail independently from the logic supply. Four MG996R servos under simultaneous load can draw up to 10A — sharing a rail with logic would cause servo jitter indistinguishable from a software bug.

---

## 🎭 The Paul Daniels Layer

The state vocabulary — `CURIOUS`, `ARROGANT`, `DYING` — is not accidental. These are theatrical terms, not engineering terms.

This is the Paul Daniels layer: the point where hardware becomes character. Daniels didn't describe his props in terms of weight or material. He described them by how they *behaved*. The same object could be fearful or proud depending on how he held it.

The `LampState` dataclass enforces the same discipline. You cannot set a servo position directly from a cue. You can only set a *named state* — and that state carries a full emotional signature across all five parameters. The motion engine cannot misinterpret `ARROGANT` as `CURIOUS` because they are structurally different: same medium speed, but `tilt_bias` 0.8 vs 0.2, and `range` 0.6 vs 0.4.

The prop doesn't do the trick. The parameters do.

---

*Next: Episode 4 — Light the Stage: DMX lighting states, pygame projection scenes, and the BabylonJS digital twin.*
