---
title: "Magic Lamp Ep.2"
published: false
description: "Inside the Show Conductor: how a YAML timeline and OSC messages orchestrate five subsystems across a live theatrical performance."
tags: ["python", "osc", "showcontrol", "yaml"]
part: 2
series: "Magic Lamp Series"
organization: "the-software-s-journey"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/magic_lamp_series/magic-lamp-episode-02.png"
---

> *"The trick is knowing the exact moment."*

Paul Daniels was obsessive about timing. A half-second early and the illusion collapsed. A half-second late and the audience had already looked in the wrong place. The magic lived in the gap between the cue and the reveal — and he controlled that gap absolutely.

PIXSTARS has the same requirement. When the drums hit at second 60, the lamp must become `CURIOUS` at that exact moment — not 200ms earlier, not 300ms later. When the music swells into the death sequence at second 380, the light must dim and the lamp must start `DYING` together.

The component that enforces this is the **Show Conductor**.

---

## 🎬 What the Conductor Does

The Conductor is a single Python process (`conductor/main.py`) that:

1. Reads a YAML timeline of 15 cues
2. Waits for the operator to press ENTER (the show start trigger)
3. Runs a tight loop, checking elapsed time every 50ms
4. Dispatches OSC messages to five subsystems when each cue's timestamp is reached
5. Mirrors every cue to the Digital Twin for visualisation

That's it. No GUI, no network dependency, no magic. Just a timer and a dispatch loop.

---

## 📋 The Timeline YAML

The entire 9-minute 15-second show is defined in `conductor/timeline.yaml`. Each cue is a timestamped record with optional keys for each subsystem:

```yaml
cues:
  - time: 0.0
    name: SHOW_START
    lamp: INERT
    projection: BLACKOUT
    lighting: BLACKOUT
    ardour: {command: transport_play}

  - time: 5.0
    name: GNR_LOGO
    projection: GNR_LOGO
    lighting: ROCKSTAR

  - time: 12.0
    name: LAMP_ON
    lamp: FUNCTIONAL
    lighting: LAMP_ONLY

  - time: 60.0
    name: DRUMS_BEGIN
    lamp: CURIOUS

  - time: 120.0
    name: SCENE_TRANSFORM_WALT
    lamp: CURIOUS
    projection: DISNEY_CASTLE
    lighting: DISNEY_SOFT

  - time: 190.0
    name: MICKEY_DRAWING
    lamp: PLEASED
    projection: MICKEY_DRAWING

  - time: 270.0
    name: AI_ITERATION
    lamp: ARROGANT
    projection: AI_ITERATIONS
    lighting: AI_COLD

  - time: 340.0
    name: OVERHEATING
    lamp: OVERHEATING
    lighting: OVERHEAT

  - time: 380.0
    name: LAMP_DEATH
    lamp: DYING
    lighting: DEATH

  - time: 385.0
    name: LAMP_DEAD
    lamp: DEAD
    projection: BLACKOUT

  - time: 460.0
    name: REVEAL_AI
    lamp: WEAK
    projection: AI_SIGNATURE
    lighting: REBIRTH

  - time: 480.0
    name: REVEAL_WALT
    lamp: LEARNING
    projection: WALT_SIGNATURE

  - time: 490.0
    name: REVEAL_AXEL
    lamp: REBORN
    projection: AXEL_SIGNATURE

  - time: 500.0
    name: TEAM_ROCKSTARS
    lamp: CELEBRATE
    projection: TEAM_ROCKSTARS
    lighting: FINALE

  - time: 555.0
    name: SHOW_END
    lamp: OFF
    projection: BLACKOUT
    lighting: BLACKOUT
    ardour: {command: transport_stop}
```

Keys that are absent from a cue simply aren't dispatched — there's no need to send `lamp: CURIOUS` again if the lamp state hasn't changed.

---

## 🔁 The Dispatch Loop

The core of `conductor/main.py` is deliberately simple:

```python
def run_show(
    cues: list[dict],
    sender: OSCSender,
    ardour: ArdourOSC,
    dry_run: bool = False
):
    if not dry_run:
        input("Press ENTER to start the show...")

    show_start = time.time()
    cue_index = 0
    total_cues = len(cues)

    while cue_index < total_cues:
        elapsed = time.time() - show_start
        cue = cues[cue_index]

        if elapsed >= cue["time"]:
            _dispatch_cue(cue, cue_index, total_cues, sender, ardour)
            cue_index += 1
        else:
            remaining = cue["time"] - elapsed
            print(
                f"[{_fmt_time(elapsed)}] "
                f"Next: {cue['name']} in {remaining:.1f}s",
                end="\r"
            )
            time.sleep(0.05)  # 50ms polling interval
```

The 50ms polling interval is a deliberate trade-off: tight enough that cue jitter is imperceptible to a live audience (sub-100ms), loose enough to avoid burning a CPU core.

---

## 📡 The OSC Sender

`conductor/osc_sender.py` wraps `python-osc` and maintains a client per subsystem:

```python
from pythonosc.udp_client import SimpleUDPClient

class OSCSender:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self._ardour_rolling = False

        self.clients = {
            "ardour":     SimpleUDPClient("127.0.0.1", 3819),
            "lamp":       SimpleUDPClient("127.0.0.1", 9001),
            "projection": SimpleUDPClient("127.0.0.1", 9002),
            "lighting":   SimpleUDPClient("127.0.0.1", 9003),
            "twin":       SimpleUDPClient("127.0.0.1", 9004),
        }

    def send(self, target: str, address: str, *args):
        if self.dry_run:
            print(f"[DRY-RUN] -> {target} {address} {args}")
            return
        self.clients[target].send_message(address, list(args))
        # Mirror everything to the digital twin
        if target != "twin":
            self.clients["twin"].send_message(address, list(args))

    def lamp_state(self, state: str):
        self.send("lamp", "/lamp/state", state)

    def projection_scene(self, scene: str):
        self.send("projection", "/projection/scene", scene)

    def lighting_state(self, state: str):
        self.send("lighting", "/lighting/state", state)
```

The mirror-to-twin pattern means the Digital Twin receives every message without any subsystem needing to know it exists. It's purely additive — remove the twin and nothing else changes.

---

## 🎵 The Ardour Integration: One Gotcha

Ardour 9 exposes an OSC control surface, but there's a non-obvious detail that costs real time to discover: `/transport_play` does not produce audio.

The correct command is `/toggle_roll`, which behaves like pressing the spacebar — it starts and stops the transport, and audio flows correctly.

```python
# conductor/ardour_osc.py
class ArdourOSC:
    SAMPLE_RATE = 48000  # Ardour default

    def play(self):
        # Do NOT use /transport_play — it doesn't produce audio in Ardour 9
        self.sender.send("ardour", "/toggle_roll")
        self.sender._ardour_rolling = True

    def stop(self):
        self.sender.send("ardour", "/toggle_roll")
        self.sender._ardour_rolling = False

    def locate_seconds(self, seconds: float, roll: bool = True):
        samples = int(seconds * self.SAMPLE_RATE)
        self.sender.send("ardour", "/locate", samples, 1 if roll else 0)

    def process_cue(self, ardour_data: dict):
        match ardour_data.get("command"):
            case "transport_play":
                self.play()
            case "transport_stop":
                self.stop()
            case "locate":
                self.locate_seconds(ardour_data.get("seconds", 0.0))
```

This is the kind of detail that doesn't appear in documentation but derails a technical rehearsal. The Ardour OSC spec lists `/transport_play` as valid — it is, but it bypasses the audio engine's roll state. `/toggle_roll` is the stage-safe version.

---

## 🚀 Dry-Run Mode

Every cue can be tested without waiting:

```bash
python conductor/main.py --dry-run
```

In dry-run mode, the conductor prints all 15 cues immediately with their OSC messages and target ports, without sleeping or sending UDP packets. A complete show trace in under a second.

```
[DRY-RUN] t=0.0   SHOW_START
  -> ardour /toggle_roll
  -> lamp   /lamp/state INERT
  -> proj   /projection/scene BLACKOUT
  -> light  /lighting/state BLACKOUT

[DRY-RUN] t=60.0  DRUMS_BEGIN
  -> lamp   /lamp/state CURIOUS
...
```

This allows testing the entire cue sequence — including Ardour commands — without the DAW running.

---

## 🏛️ Architecture Decision: Why YAML, Not Code

The timeline could have been written as Python directly. It wasn't, for one reason: **the timeline is a creative document, not a software document**.

During rehearsal, a director (or performer) might say "move the lamp death two seconds earlier." With a YAML file, that's a one-line edit that anyone on the team can make. With Python, it requires understanding the codebase.

The YAML is the score. The conductor reads it. Paul Daniels had a cue sheet, not a program.

---

*Next: Episode 3 — 14 Personalities in a Lampshade: how emotional states drive servo motion vocabulary.*
