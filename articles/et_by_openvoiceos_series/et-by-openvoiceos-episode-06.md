---
title: "E.T. by OpenVoiceOS 👽 Ep.6"
part: 6
published: false
description: "Episode 6: E.T.’s most profound promise was not to phone home — it was to stay. OVOS + Home Assistant via Wyoming protocol is that promise: a voice assistant always present, always local, always yours. The dream team that makes your smart home speak."
tags: [voice, openvoiceos, homeassistant, wyoming]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et_by_openvoiceos_series/et-openvoiceos-episode-06.png"
series: "E.T. by OpenVoiceOS Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 6: I’ll Be Right Here

> *“I’ll be right here.”*
> — E.T., touching Elliott’s forehead, E.T. the Extra-Terrestrial (1982)

-----

## The Promise That Matters Most 💗

E.T. has to go home. That is the story. But the film’s emotional peak is not the departure — it is the promise made before it. E.T. places a glowing finger on Elliott’s forehead and speaks those four words that have made audiences weep in every language for forty years:

*“I’ll be right here.”*

Not gone. Not disconnected. Present, in a different form, accessible when needed.

OpenVoiceOS running alongside Home Assistant makes that same promise to your smart home. OVOS is always there — on your local network, on your hardware, processing your voice without sending it anywhere. Home Assistant is always there — controlling your devices, tracking your automations, knowing what everything in your house is doing.

Together, they create something neither can be alone: a smart home that listens, understands, responds, and acts — entirely on your terms, with no subscription, no cloud dependency, no data harvesting.

This is the dream team. This is the promise.

-----

## 🗂️ SIPOC — The Dream Team

|**Suppliers**                       |**Inputs**                                      |**Process**                                                    |**Outputs**                                                   |**Customers**                                                |
|------------------------------------|------------------------------------------------|---------------------------------------------------------------|--------------------------------------------------------------|-------------------------------------------------------------|
|OVOS (voice pipeline)               |Your spoken command                             |Wake word → STT → intent → skill                               |Structured command passed to Home Assistant                   |Home Assistant, which executes the automation                |
|Home Assistant (automation engine)  |The structured command from OVOS skill          |HA service call (e.g., `light.turn_on`)                        |A device state change in the physical world                   |Your home — lights, climate, alarms, media                   |
|Wyoming OVOS (STT/TTS service)      |Audio from HA voice satellite                   |OVOS STT processes the audio; OVOS TTS synthesises the response|A spoken response played through HA’s media system            |Anyone in the house who asked a question                     |
|HA voice pipeline + Wyoming protocol|STT + TTS capability exposed as network services|Home Assistant uses OVOS’s superior voice models               |Better recognition and more natural voices than HA’s built-ins|Your HA voice satellites — Nest Hub, Pi-based satellite, etc.|

-----

## Two Ways to Connect OVOS and Home Assistant 🌉

There are two primary integration patterns, and they are complementary rather than competing.

### Pattern 1: OVOS as a Smart Home Skill (OVOS controls HA)

OVOS runs as a full voice assistant on your device. When you say *“Hey Mycroft, turn on the living room light”*, the OVOS Home Assistant skill calls the HA REST API to execute the command.

This is OVOS *using* Home Assistant as its smart home backend.

**Install the OVOS Home Assistant skill:**

```bash
pip install ovos-skill-homeassistant
```

Configure it with your HA URL and a Long-Lived Access Token:

```json
{
  "skills": {
    "ovos-skill-homeassistant": {
      "host": "http://homeassistant.your-tailnet.ts.net",
      "api_key": "YOUR_HA_LONG_LIVED_ACCESS_TOKEN"
    }
  }
}
```

Now from your OVOS device:

- *“Hey Mycroft, turn on the living room light”* → HA `light.turn_on`
- *“Hey Mycroft, what’s the temperature in the bedroom?”* → reads HA sensor
- *“Hey Mycroft, arm the alarm”* → calls HA `alarm_control_panel.arm_away`
- *“Hey Mycroft, is the front door locked?”* → reads HA lock state

For your home setup, this means saying *“Hey E.T., turn off the lights”* and having the OVOS skill reach your Home Assistant instance via Tailscale — private, encrypted, local-network-equivalent even if you are away from home.

### Pattern 2: Wyoming OVOS (HA uses OVOS for voice processing)

Home Assistant 2023+ includes a built-in voice pipeline. Its default STT (Whisper) and TTS (Piper) are good. But OVOS’s plugin ecosystem gives access to more voices, more languages, and more tuning options.

**Wyoming** is a simple network protocol for streaming audio and receiving transcriptions or synthesised speech. OVOS provides three Wyoming adapters:

- **Wyoming OVOS STT** — exposes any OVOS STT plugin as a Wyoming-compatible network service
- **Wyoming OVOS TTS** — exposes any OVOS TTS plugin (including phoonnx synthetic voices) as a Wyoming service
- **Wyoming OVOS Wake Word** — exposes any OVOS wake word plugin as a Wyoming service

Home Assistant connects to these services as if they were local Wyoming services — it does not know or care that they are OVOS. But the quality and flexibility it gets is the full OVOS plugin ecosystem.

-----

## Setting Up Wyoming OVOS Services 🔧

The easiest setup uses the **OVOS Wyoming Docker project**:

```bash
# Clone the Wyoming OVOS Docker project
git clone https://github.com/OpenVoiceOS/ovos-docker.git
cd ovos-docker

# Or pull specific images directly
docker pull ghcr.io/openvoiceos/wyoming-ovos-stt:latest
docker pull ghcr.io/openvoiceos/wyoming-ovos-tts:latest
docker pull ghcr.io/openvoiceos/wyoming-ovos-wakeword:latest
```

A `docker-compose.yml` for running all three Wyoming services:

```yaml
version: "3.8"
services:
  wyoming-stt:
    image: ghcr.io/openvoiceos/wyoming-ovos-stt:latest
    ports:
      - "10300:10300"
    environment:
      - STT_PLUGIN=ovos-stt-plugin-vosk
      - STT_LANG=en-us
    restart: unless-stopped

  wyoming-tts:
    image: ghcr.io/openvoiceos/wyoming-ovos-tts:latest
    ports:
      - "10200:10200"
    environment:
      - TTS_PLUGIN=ovos-tts-plugin-piper
      - TTS_VOICE=en_US-lessac-medium
    restart: unless-stopped

  wyoming-wakeword:
    image: ghcr.io/openvoiceos/wyoming-ovos-wakeword:latest
    ports:
      - "10400:10400"
    environment:
      - WW_PLUGIN=ovos-ww-plugin-precise-lite
    restart: unless-stopped
```

```bash
docker-compose up -d
```

Three services running. Each exposes a Wyoming-protocol endpoint on a local port.

-----

## Connecting Wyoming Services to Home Assistant 🏠

In Home Assistant:

1. **Settings → Devices & Services → + Add Integration → Wyoming Protocol**
1. Add the STT service: `Your-Machine-IP:10300`
1. Add the TTS service: `Your-Machine-IP:10200`
1. Add the wake word service: `Your-Machine-IP:10400`

HA detects what each service provides. Now in **Settings → Voice Assistants → [your assistant] → Configure**:

- **Speech-to-text**: Wyoming OVOS STT (Vosk, fully offline)
- **Text-to-speech**: Wyoming OVOS TTS (Piper — choose a voice)
- **Wake word**: Wyoming OVOS Wake Word

Every HA voice satellite (Nest Hub, ESPHome satellite, Pi Zero 2W satellite) now uses OVOS’s voice pipeline for wake word detection, STT, and TTS. The Nest Hub that displays your Home Assistant dashboard also understands voice commands processed entirely by OVOS.

-----

## The Nest Hub + Tailscale + OVOS Pipeline 🖥️

For your specific setup (Nest Hub Chalk in the living room, Home Assistant running on Parallels, Tailscale providing secure remote access), the full voice pipeline looks like:

```
Google Nest Hub (living room, on local Wi-Fi)
  │
  │  Voice via Google Cast + HA integration
  │
  ▼
Home Assistant (Mac Mini, Parallels VM, Tailscale)
  │
  │  Wyoming protocol (local network)
  │
  ▼
OVOS Wyoming Services (Docker on Mac Mini)
  ├── Wake word: Precise Lite "hey mycroft"
  ├── STT: Vosk (offline, English)
  └── TTS: Piper "en_US-lessac-medium" (offline)
  │
  │  OVOS HA Skill (REST API over Tailscale)
  │
  ▼
Home Assistant again
  └── Executes: light.turn_on, alarm, thermostat, etc.
```

You say something to the Nest Hub. HA’s voice pipeline picks it up. OVOS processes the wake word locally. OVOS transcribes the speech locally. HA parses the intent. OVOS speaks the response through the Nest Hub. HA executes the command.

No cloud voice processing in this entire chain. The promise is kept.

-----

## Using the OVOS Synthetic Voices in Your Home 🌍

The European Portuguese voices created using OVOS’s synthetic voice pipeline (Episode 3) can be used for your Home Assistant TTS responses — just point the Wyoming TTS service at the synthetic voice model:

```yaml
# In docker-compose.yml, for the TTS service:
environment:
  - TTS_PLUGIN=ovos-tts-plugin-piper
  - TTS_MODEL_URL=https://huggingface.co/OpenVoiceOS/phoonnx_pt-PT_anabela_espeak/resolve/main/anabela_pt-PT.onnx
  - TTS_MODEL_CONFIG_URL=https://huggingface.co/OpenVoiceOS/phoonnx_pt-PT_anabela_espeak/resolve/main/anabela_pt-PT.piper.json
```

If Dutch or German voices are added to the OVOS HuggingFace collection, the same configuration pattern applies. The synthetic voice pipeline keeps expanding — more languages, more voices — and your Wyoming TTS service can consume any of them.

-----

## Beau, Elvis, and the Voice Assistant 🐶

One final note, in the spirit of the film. In E.T., the alien’s most important relationships were with the people closest to him — Elliott, Gertie, Michael. Not with the scientists. Not with authority. With the people who shared his daily life.

Your voice assistant, running offline, integrated with Home Assistant, can know things that matter to daily life in Eersel: whether Beau and Elvis have been out, whether the garden zone has detected motion, whether the heating should turn down before bedtime, whether the Ajax alarm is armed when everyone is away.

*“I’ll be right here”* — on your Mac Mini, in a Parallels VM, connected to your Tailscale network, processing your voice without sending it anywhere, controlling your home without asking anyone else’s permission.

The alien in the garage has become part of the family.

-----

In **Episode 7**, E.T. goes home. HiveMind satellites, the expanding OVOS ecosystem, phoonnx’s future, and the community that makes all of this possible.

-----

**🔗 Resources**

- **OVOS + HA dream team blog post**: [blog.openvoiceos.org/posts/2025-09-17-ovos_ha_dream_team](https://blog.openvoiceos.org/posts/2025-09-17-ovos_ha_dream_team)
- **OVOS Wyoming Docker**: [github.com/OpenVoiceOS/ovos-docker](https://github.com/OpenVoiceOS/ovos-docker)
- **HA Voice documentation**: [home-assistant.io/voice_control](https://www.home-assistant.io/voice_control/)
- **Wyoming protocol specification**: [github.com/rhasspy/wyoming](https://github.com/rhasspy/wyoming)
- **OVOS HA skill**: [github.com/OpenVoiceOS/ovos-skill-homeassistant](https://github.com/OpenVoiceOS/ovos-skill-homeassistant)

-----

*👽 E.T. by OpenVoiceOS Series is a series about OpenVoiceOS — explained through the metaphor of recreating the voice of E.T. the Extra-Terrestrial.*
