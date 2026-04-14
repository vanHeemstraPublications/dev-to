---
title: "E.T. by OpenVoiceOS 👽 Ep.4"
part: 4
published: false
description: "Episode 4: The moment Elliott’s bicycle rises over the treeline — the impossible becomes real. Installing OpenVoiceOS on a Raspberry Pi and watching it run fully offline is that moment. A complete voice assistant, on your desk, talking to no one but you."
tags: [voice, openvoiceos, raspberrypi, selfhosted]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et_by_openvoiceos_series/et-openvoiceos-episode-04.png"
series: "E.T. by OpenVoiceOS Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 4: Elliott’s Bicycle

> *“I’ll believe in you all my life, every day.”*
> — Elliott, E.T. the Extra-Terrestrial (1982)

*The silhouette against the full moon. The bicycle wheels lifting from the road. The impossible made real. When you say “Hey, E.T.” for the first time to your Raspberry Pi and it answers you — locally, privately, without phoning any cloud home — you will understand exactly what that moment felt like.*

-----

## The Moon Behind the Treeline 🌕

The most iconic image in E.T. is not the creature itself — it is the silhouette of Elliott’s bicycle against the full moon. That moment works because it makes the impossible *viscerally, physically real*. The bicycle is there. The moon is there. Something that should not be happening is plainly, undeniably happening.

Getting OVOS running on a Raspberry Pi creates the same feeling. A Raspberry Pi 4 costs about $55. It draws 5 watts of power. It fits in your palm. And it runs a complete, offline, neural-network-powered voice assistant that processes everything locally, speaks to you in a natural voice, and understands your commands — without sending a single byte to Amazon, Google, or any cloud service.

Something that was impossible ten years ago is now plainly, undeniably real. And it runs on hardware you can buy at a hobby shop.

-----

## 🗂️ SIPOC — The Installation

|**Suppliers**                           |**Inputs**                                      |**Process**                                                          |**Outputs**                                                                |**Consumers**                                                          |
|----------------------------------------|------------------------------------------------|---------------------------------------------------------------------|---------------------------------------------------------------------------|-----------------------------------------------------------------------|
|The OVOS installer script (one command) |A Linux system (Raspberry Pi OS, Ubuntu, Debian)|`curl` + `bash` — downloads, configures, and starts all OVOS services|A running OVOS instance with all five core services                        |You, speaking “Hey Mycroft” and hearing a response from your own device|
|The OVOS plugin ecosystem (pip packages)|Your `mycroft.conf` configuration               |Plugin Manager installs your chosen STT, TTS, wake word plugins      |A fully configured pipeline matching your hardware and privacy requirements|Your voice assistant, running as systemd services, starting on boot    |
|The HuggingFace model repository        |A Piper/phoonnx model URL                       |First TTS call downloads and caches the model                        |A local model file; all subsequent calls are fully offline                 |Every TTS response, now and forever, without an internet connection    |

-----

## Prerequisites 🛠️

**Hardware:**

- Raspberry Pi 4 (2GB RAM minimum; 4GB recommended for better TTS quality)
- A USB microphone (or USB headset with integrated microphone)
- A speaker (3.5mm audio, HDMI, or Bluetooth)
- A microSD card (16GB minimum; 32GB recommended)
- Power supply (official Pi 4 PSU, 5V 3A)

**Software:**

- Raspberry Pi OS (64-bit, Lite recommended for headless; Full for GUI)
- Python 3.9+ (comes with Pi OS)
- Internet access for initial installation and model downloads

For headless operation (no screen, SSH only), Pi OS Lite is ideal — OVOS itself does not need a desktop environment. It runs as background services.

-----

## Installation: The One-Command Method 🚀

The OVOS installer handles everything:

```bash
sh -c "curl -s https://raw.githubusercontent.com/OpenVoiceOS/ovos-installer/main/installer.sh \
  -o installer.sh && chmod +x installer.sh && sudo ./installer.sh && rm installer.sh"
```

The installer:

1. Detects your platform (Raspberry Pi, x86_64, ARM, etc.)
1. Installs required system dependencies
1. Creates a Python virtual environment for OVOS
1. Installs `ovos-core`, `ovos-listener`, `ovos-audio`, `ovos-phal`, `ovos-messagebus`
1. Configures systemd services for all components
1. Creates a default `mycroft.conf`

After installation, all five services start automatically:

```bash
# Check service status
sudo systemctl status ovos-messagebus
sudo systemctl status ovos-listener
sudo systemctl status ovos-core
sudo systemctl status ovos-audio
sudo systemctl status ovos-phal

# View logs for a service
sudo journalctl -u ovos-core -f
```

-----

## First Voice Test 🎙️

With the default configuration, your OVOS instance uses:

- Wake word: `hey mycroft` (via Vosk, no model download needed for basic detection)
- STT: `ovos-stt-plugin-server` (community-hosted, requires internet for first tests)
- TTS: `ovos-tts-plugin-mimic3` or the default eSpeak fallback

Say **“Hey Mycroft, what time is it?”**

If the pipeline is working, you will hear a spoken response. The first time, it will be robotic (eSpeak fallback). But the pipeline is live. Elliott’s feet have left the ground.

-----

## Installing Better Plugins 🔧

The default configuration gets you running. The next step is upgrading each stage to your preferred quality and privacy level.

**Install the Vosk STT plugin (fully offline):**

```bash
pip install ovos-stt-plugin-vosk
```

In `~/.config/mycroft/mycroft.conf`:

```json
{
  "stt": {
    "module": "ovos-stt-plugin-vosk"
  }
}
```

On first use, Vosk downloads the English language model (~50MB) and caches it. All subsequent STT is completely offline.

**Install the Piper TTS plugin (neural, offline, excellent quality):**

```bash
pip install ovos-tts-plugin-piper
```

```json
{
  "tts": {
    "module": "ovos-tts-plugin-piper",
    "ovos-tts-plugin-piper": {
      "voice": "en_US-lessac-medium"
    }
  }
}
```

The first TTS call downloads the Lessac voice model (~30MB) and caches it. This is a neural voice — considerably more natural than eSpeak. It runs comfortably on a Pi 4.

**Install the Precise Lite wake word plugin (trained model, lower false positives):**

```bash
pip install ovos-ww-plugin-precise-lite
```

```json
{
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-lite",
      "model": "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.tflite",
      "listen": true
    }
  }
}
```

After restarting the listener service (`sudo systemctl restart ovos-listener`), OVOS uses the trained TFLite model for wake word detection — faster and more accurate than the Vosk text-based approach.

-----

## Setting a Custom Wake Word: “Hey E.T.” 👽

As noted in Episode 2, OVOS makes custom wake words straightforward:

```json
{
  "listener": {
    "wake_word": "hey_et"
  },
  "hotwords": {
    "hey_mycroft": {
      "active": false
    },
    "hey_et": {
      "module": "ovos-ww-plugin-vosk",
      "listen": true,
      "lang": "en-us",
      "rule": "fuzzy",
      "samples": ["hey et", "hey e.t.", "hey extra terrestrial"]
    }
  }
}
```

Restart the listener. Say **“Hey E.T., what’s the weather?”**

The bicycle is over the moon.

-----

## The Offline Test: Pulling the Network Cable 🔌

This is the moment of truth. With Vosk STT and Piper TTS configured and their models cached:

1. Disconnect the Raspberry Pi from the internet (unplug the ethernet cable, disable Wi-Fi)
1. Say “Hey E.T., set a timer for five minutes”
1. OVOS responds: “Okay, timer set for five minutes”

No internet. No cloud. No server. Just your voice, your Raspberry Pi, and a voice model running locally.

*“I’ll be right here,”* E.T. says at the end of the film. He does not need a phone connection to mean it.

-----

## Using a Pre-Built OVOS Image 📀

If you prefer not to run the installer, the OVOS project maintains pre-built images for Raspberry Pi:

Download from: [openvoiceos.org/downloads](https://www.openvoiceos.org/downloads)

Flash to microSD with Balena Etcher or `dd`, boot the Pi, and OVOS starts automatically. The pre-built images are configured with sensible defaults and include a GUI optimised for small touchscreens — useful if you want a device with a display showing what OVOS is doing.

-----

## Skills: What OVOS Can Do Out of the Box 🧠

A running OVOS instance with default skills can:

- Answer questions (*“What time is it?”*, *“What is the capital of the Netherlands?”*)
- Set timers and alarms (*“Set a timer for 20 minutes”*)
- Tell you the weather (*“What is the weather in Eersel?”*)
- Play music (via various streaming plugins)
- Control smart home devices (via Home Assistant skill — covered in Episode 6)
- Convert units (*“How many kilometres in 10 miles?”*)
- Search Wikipedia, DuckDuckGo, Wolfram Alpha

And because OVOS is fully Mycroft-compatible, the entire Mycroft skill marketplace is available. Hundreds of community skills covering everything from news to jokes to IoT device control.

-----

In **Episode 5**, we go deeper — configuring plugins, choosing your own TTS voice character, and building the precise stack you want. The government scientists want to take E.T. back. Your OVOS installation is the locked bedroom door.

-----

**🔗 Resources**

- **OVOS installer**: [github.com/OpenVoiceOS/ovos-installer](https://github.com/OpenVoiceOS/ovos-installer)
- **Downloads page** (pre-built images): [openvoiceos.org/downloads](https://www.openvoiceos.org/downloads)
- **OVOS technical manual**: [openvoiceos.github.io/ovos-technical-manual](https://openvoiceos.github.io/ovos-technical-manual)
- **Piper TTS plugin**: [github.com/OpenVoiceOS/ovos-tts-plugin-piper](https://github.com/OpenVoiceOS/ovos-tts-plugin-piper)

-----

*👽 E.T. by OpenVoiceOS Series is a series about OpenVoiceOS — explained through the metaphor of recreating the voice of E.T. the Extra-Terrestrial.*
