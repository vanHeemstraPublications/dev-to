---
title: "Magic Lamp Ep.5"
published: false
description: "How a Raspberry Pi Zero 2 WH, HiveMind, and Coqui XTTS give Pinokio a synthesised voice — and a NeoPixel ring that breathes with it."
tags: ["python", "raspberrypi", "voiceai", "makers"]
part: 5
series: "Magic Lamp Series"
organization: "the-software-s-journey"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/magic_lamp_series/magic-lamp-episode-05.png"
---

> *"The best trick is the one where they forget they're watching a trick."*

Paul Daniels understood that the moment an audience consciously noticed the mechanism, the illusion was already over. The goal was always to make the prop feel so natural, so present, that the question "how does it work?" never occurred.

Pinokio's voice works the same way. The lamp doesn't speak with a robotic voice-synth cadence. It speaks with a voice shaped to match its emotional state — fragile when it is weak, warm when it is pleased, clipped when it is arrogant. And its head glows in synchrony with every word. The mechanism disappears into the character.

This episode covers how that voice is built.

---

## 🧠 The Architecture: Mac Mini + Raspberry Pi

The voice system is split across two devices:

```
Mac Mini M4 Pro
├── HiveMind server          (port 5678)
├── Coqui XTTS render backend
├── Voice pipeline scripts   (voice/scripts/)
└── Ardour (pre-rendered WAV playback)

Raspberry Pi Zero 2 WH  (lamp head satellite)
├── HiveMind mic-satellite   (connects to Mac)
├── USB microphone
├── Small speaker
├── NeoPixel RGBW ring       (GPIO 18, 12 pixels)
└── Wake word: "Hey A.I."
```

The **thin endpoint principle** governs this split: the Pi is audio I/O only. It captures voice, plays audio, and drives the LED ring. All processing — speech recognition, intent parsing, response generation, TTS synthesis — happens on the Mac Mini. The Pi is a peripheral, not a brain.

This keeps the Pi's software surface minimal and its failure modes predictable. If the Pi crashes, the show reverts to pre-rendered audio. Nothing else breaks.

---

## 🎙️ HiveMind: The Satellite Protocol

**HiveMind** is an open-source voice assistant framework that uses a client-satellite model. The Mac Mini runs the HiveMind core server; the Pi runs a mic-satellite that streams audio to the core for processing and receives synthesised audio back.

**Mac Mini setup** (`mac/scripts/install_hivemind_server.sh`):

```bash
pip install hivemind-core
hivemind-core add-client --name pixstars-lamp --access-key pixstars

# Start the server
hivemind-core listen --port 5678
```

**Pi satellite setup** (`pi/config/env.pi.example`):

```bash
HIVEMIND_HOST=mac-mini.local
HIVEMIND_PORT=5678
HIVEMIND_ACCESS_KEY=pixstars
WAKE_WORD=hey_ai
```

Once paired, the Pi's microphone is transparently bridged to the Mac Mini's speech pipeline. From the application layer's perspective, there is only one voice endpoint.

---

## 🗣️ Coqui XTTS: The Voice Synthesis Pipeline

The lamp's voice is synthesised using **Coqui XTTS v2**, a local, voice-cloneable TTS model that runs entirely on the Mac Mini. No cloud API, no latency, no network dependency during the show.

The pipeline is a seven-stage factory defined in `voice/scripts/`:

```
1. extract_dialogue_template.py  →  voice/data/dialogue.csv
2. build_manifest.py             →  voice/orchestration/state/manifest.json
3. create_render_queue.py        →  voice/orchestration/state/render_queue.json
4. render_candidates.py          →  voice/output/candidates/*.wav
5. evaluate_candidates.py        →  voice/evaluation.csv
6. build_review_queue.py         →  approved / needs_review / rejected
7. publish_approved.py           →  voice/output/final_wav/
```

The render script (`voice/scripts/render_with_coqui_xtts.py`) applies emotional shaping before synthesis:

```python
# voice/scripts/render_with_coqui_xtts.py

EMOTION_SHAPING = {
    "fragile":  lambda t: f"... {t}",
    "warm":     lambda t: f"{t} ...",
    "curious":  lambda t: f"{t}...",
    "arrogant": lambda t: t.upper(),
    "weak":     lambda t: f"... {t} ...",
}

def synthesize(text: str, emotion: str, output: Path, cfg: dict):
    shaped = EMOTION_SHAPING.get(emotion, lambda t: t)(text)

    cmd = [
        "tts",
        "--model_name",    cfg["model"],
        "--speaker_idx",   cfg["speaker_id"],
        "--speaker_wav",   cfg["reference_wav"],
        "--text",          shaped,
        "--out_path",      str(output),
    ]
    subprocess.run(cmd, check=True)
```

The emotional shaping is deliberate low-tech: punctuation and capitalisation influence the XTTS prosody model in predictable ways. Ellipses slow the pace and add breath. Capitalisation adds emphasis. The effect is subtle but audible — `fragile` lines arrive hesitantly; `arrogant` lines land hard.

---

## 🔴 The NeoPixel Ring: Breathing with the Voice

The lamp's head contains a 12-pixel NeoPixel RGBW ring wired to GPIO 18 on the Pi. It is driven by `pi/scripts/led_hivemind_states_filewatch.py`, which watches a single shared state file at `/tmp/pixstars_lamp_state.txt`.

Five named states drive the LED behaviour:

```python
# pi/scripts/led_hivemind_states_filewatch.py (core logic)

COLOR_MAP = {
    "idle":      (255, 100,  0),    # warm amber
    "listening": (  0,  80, 255),   # blue
    "thinking":  (140,   0, 255),   # purple
    "speaking":  (255, 140,  30),   # warm orange, level-responsive
    "error":     (255,   0,   0),   # red
}

def render_loop(pixels, state_file: Path):
    smoothed_level = 0.0
    while True:
        state = state_file.read_text().strip()
        now   = time.time()

        if state == "idle":
            brightness = breathing_wave(now, period=3.0)
            fill_color(pixels, scale_color(COLOR_MAP["idle"], brightness))

        elif state == "listening":
            brightness = pulse_wave(now, period=1.0)
            fill_color(pixels, scale_color(COLOR_MAP["listening"], brightness))

        elif state == "thinking":
            brightness = pulse_wave(now, period=0.5)
            fill_color(pixels, scale_color(COLOR_MAP["thinking"], brightness))

        elif state == "speaking":
            # Audio-level responsive: follows speech amplitude
            raw_level    = read_audio_level()
            smoothed_level = 0.7 * smoothed_level + 0.3 * raw_level
            brightness   = max(0.03, min(1.0, smoothed_level))
            fill_color(pixels, scale_color(COLOR_MAP["speaking"], brightness))

        elif state == "error":
            brightness = pulse_wave(now, period=0.25)  # fast red pulse
            fill_color(pixels, scale_color(COLOR_MAP["error"], brightness))

        time.sleep(0.02)   # 50Hz refresh
```

The `speaking` state is the interesting one: the LED brightness tracks the real-time audio level of the synthesised speech output, smoothed with a 0.7/0.3 exponential moving average to avoid flickering. The result is a ring that genuinely pulses with the lamp's voice — not a pre-programmed animation, but a live reaction.

---

## 📁 The State File Bridge

The state file at `/tmp/pixstars_lamp_state.txt` is the interface between HiveMind's Python processes and the LED renderer. Any component that knows the current voice state writes to it:

```bash
# mac/scripts/set_state.sh
echo "$1" > /tmp/pixstars_lamp_state.txt
```

```python
# Called from HiveMind skill hooks:
Path("/tmp/pixstars_lamp_state.txt").write_text("thinking")
```

This is intentionally simple. A file watch is robust, requires no inter-process messaging infrastructure, and survives restarts — the LED renderer picks up the last written state immediately on boot.

---

## 🔄 Dual-Mode Voice: Deterministic vs Interactive

The voice system supports two modes, defined in `shared/VOICE_AND_CUES.md`:

| Mode | Trigger | Behaviour |
|------|---------|-----------|
| **Deterministic** | Ardour transport cue | Pre-rendered WAV plays at exact timestamp — musical sync, locked to score |
| **Interactive** | Wake word "Hey A.I." | HiveMind generates live response — spontaneous, audience-reactive |

During the scripted show, pre-rendered lines play via Ardour transport cues. The lamp's voice is part of the score. But between acts — or in an installation context — the wake word activates HiveMind and the lamp responds in real time, with Coqui generating fresh audio on the Mac Mini and the Pi playing it back through its speaker.

This dual-mode design means the piece can be either a fixed-score theatrical performance or a live interactive installation, without changing any hardware.

---

## 🎩 The Full Trick

Paul Daniels' greatest trick was making the audience forget the mechanism entirely. By the end of the act, they weren't watching a performer with props — they were watching something that felt genuinely alive.

Here is the full mechanism behind Pinokio:

1. **Mac Mini** reads a YAML timeline and dispatches OSC cues every 50ms
2. **Ardour** plays the deconstructed score — piano, drums, silence
3. **Pololu Maestro** drives 6 servos through 14 named emotional states
4. **Enttec DMX Pro** sets stage light colour and intensity per cue
5. **pygame** projects images on the back wall in sync with the lamp's arc
6. **BabylonJS twin** visualises the entire show in 3D for pre-vis and monitoring
7. **Raspberry Pi** runs a HiveMind satellite — mic, speaker, NeoPixel ring
8. **Coqui XTTS** synthesises voice lines locally, shaped by emotional state
9. **NeoPixel ring** breathes amber, pulses blue, glows orange with the voice

None of these layers are complex in isolation. The trick is that they all speak the same language — OSC on localhost — and they all start from the same YAML file.

The prop is just a lamp. The character is in the architecture.

---

*This concludes the Magic Lamp Series. The PIXSTARS project targets a live performance in October 2026. Follow along at [dev.to/the-software-s-journey](https://dev.to/the-software-s-journey).*
