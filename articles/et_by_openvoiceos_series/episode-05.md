-----

## title: “E.T. by OpenVoiceOS! 👽 Ep.5: The Government Scientists”
published: false
description: “Episode 5: The government scientists want to study E.T., control him, lock him in a lab. The OVOS plugin system is the locked bedroom door. Every stage — wake word, STT, TTS, skills, hardware — is yours to choose, replace, and protect.”
tags: [voice, openvoiceos, plugins, privacy]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-openvoiceos-episode-05.png”
series: “E.T. by OpenVoiceOS Series”
canonical_url: “”
organization: “the-software-s-journey”

# E.T. by OpenVoiceOS! 👽

## Episode 5: The Government Scientists

> *“They’re communicating with him. That means… he’s communicating with someone.”*
> — government scientist, E.T. the Extra-Terrestrial (1982)

-----

## The Men in the White Vans 🚐

The turn in E.T. comes when the white government vans appear outside Elliott’s house. Scientists in hazmat suits. Men with clipboards and monitoring equipment. Agents who want to take E.T. away from the people who understand him and put him somewhere he can be studied, controlled, optimised, and eventually owned.

The parallel to Big Tech voice assistants is not subtle.

Alexa listens. Google Assistant uploads. Siri integrates with Apple’s ecosystem on Apple’s terms. The trade-off is always the same: convenience in exchange for control. You get a voice assistant. They get your voice data, your query history, your patterns of living. The scientists get E.T.

OpenVoiceOS is the locked bedroom door. The OVOS **plugin system** is the mechanism by which you keep every part of your voice assistant under your control — swapping, auditing, configuring, and replacing every component without asking anyone’s permission.

-----

## 🗂️ SIPOC — The Plugin System

|**Suppliers**                              |**Inputs**                                            |**Process**                                                                           |**Outputs**                                                            |**Consumers**                                                           |
|-------------------------------------------|------------------------------------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------|------------------------------------------------------------------------|
|OVOS Plugin Manager (`ovos-plugin-manager`)|A plugin name and configuration                       |`pip install` + configure in `mycroft.conf`                                           |A swapped-out component: new STT, new TTS, new wake word, new skill    |OVOS core services, now using your chosen implementation at that stage  |
|The community plugin ecosystem             |Your specific hardware, language, privacy requirements|Mix and match: offline for privacy-critical stages, cloud for quality where acceptable|A personalised, auditable pipeline where you understand every data flow|You — with full knowledge of what your assistant does and does not share|

-----

## The Plugin Manager: The Locked Bedroom 🚪

The `ovos-plugin-manager` is the mechanism that makes OVOS modular. Every stage of the voice pipeline is not hardcoded — it is a plugin slot. The Plugin Manager loads the plugin you specify in configuration, instantiates it, and routes data to it.

This means:

- No stage is mandatory
- No vendor is required
- No API key is permanent
- No decision is irreversible

The configuration file (`mycroft.conf`) is a plain JSON file. To change your TTS engine, you change one line. To add a fallback STT, you add two lines. To configure a custom wake word, you add a hotword block. No app stores. No account required. No permission from anyone.

-----

## Your Plugin Choices at Each Stage 🧩

### Wake Word — Who Wakes the Alien

The wake word is the first moment of contact. E.T.‘s recognition always begins with a specific stimulus — the Reese’s Pieces trail, Elliott’s heartbeat resonating in his own chest. Your OVOS installation begins when it hears its wake word.

|Plugin                       |Method              |Privacy|Setup effort              |
|-----------------------------|--------------------|-------|--------------------------|
|`ovos-ww-plugin-precise-lite`|Trained TFLite model|Total  |Medium (need a model file)|
|`ovos-ww-plugin-vosk`        |Text-based (ASR)    |Total  |None (use samples)        |
|`ovos-ww-plugin-pocketsphinx`|Phoneme-based       |Total  |Low (define phonemes)     |

**The beauty of multiple hotwords**: OVOS supports *simultaneous* active wake words. You can have *“Hey Mycroft”* and *“Hey E.T.”* and *“Computer”* all active at once, each potentially triggering a different STT language or action:

```json
{
  "hotwords": {
    "hey_mycroft": {
      "module": "ovos-ww-plugin-precise-lite",
      "model": "https://...hey_mycroft.tflite",
      "listen": true
    },
    "hey_et": {
      "module": "ovos-ww-plugin-vosk",
      "listen": true,
      "samples": ["hey et"],
      "stt_lang": "en-us"
    },
    "computador": {
      "module": "ovos-ww-plugin-vosk",
      "listen": true,
      "lang": "pt-pt",
      "samples": ["computador"],
      "stt_lang": "pt-pt"
    }
  }
}
```

Three wake words, three languages. The alien understands more than one dialect.

### STT — Understanding the Language

|Plugin                        |Offline              |Quality  |Language support               |
|------------------------------|---------------------|---------|-------------------------------|
|`ovos-stt-plugin-vosk`        |Yes                  |Good     |20+ languages, models available|
|`ovos-stt-plugin-whisper`     |Yes (needs RAM)      |Excellent|90+ languages                  |
|`ovos-stt-plugin-server`      |No (community server)|Very good|Multiple                       |
|`ovos-stt-plugin-google-cloud`|No                   |Excellent|60+                            |
|`ovos-stt-plugin-azure`       |No                   |Excellent|60+                            |

Privacy architecture with fallback:

```json
{
  "stt": {
    "module": "ovos-stt-plugin-vosk",
    "fallback_module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "url": "https://stt.openvoiceos.com/stt"
    }
  }
}
```

Vosk first — no internet, no cloud, all local. If Vosk fails (model not loaded, recognition error), fall back to the community-hosted server. The government scientists never see the data if Vosk succeeds. If it fails, data goes to a server run by the OVOS community — not Amazon, not Google.

### TTS — The Voice Character

This is where the synthetic voice creation from Episode 3 becomes concrete. The voice your OVOS installation speaks with is a choice — a plugin configuration pointing at a model file.

**Available voice character options via Piper:**

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

The `voice` field can be:

- A built-in Piper voice name (e.g., `en_US-lessac-medium`, `en_GB-alan-medium`)
- A direct URL to a `.onnx` model file (for OVOS custom voices on HuggingFace)
- A local file path (for voices you have trained yourself)

For the OVOS-created synthetic voices (including European Portuguese):

```json
{
  "tts": {
    "module": "ovos-tts-plugin-piper",
    "ovos-tts-plugin-piper": {
      "model": "https://huggingface.co/OpenVoiceOS/phoonnx_pt-PT_anabela_espeak/resolve/main/anabela_pt-PT.onnx",
      "model_config": "https://huggingface.co/OpenVoiceOS/phoonnx_pt-PT_anabela_espeak/resolve/main/anabela_pt-PT.piper.json"
    }
  }
}
```

Point at a HuggingFace URL, restart `ovos-audio`, and your assistant now speaks European Portuguese in a natural, offline, synthetically created voice that had never existed before.

-----

## Skills: The Vocabulary of the Alien 📚

E.T. gradually acquired vocabulary throughout the film. His initial utterances were grunts and rasping sounds. By the end, he could express complex emotions — *“I’ll be right here”* — across a language barrier.

OVOS skills are the acquired vocabulary. Each skill adds a domain of understanding:

```bash
# Install a skill via pip
pip install ovos-skill-homeassistant

# Or use the OVOS skill installer (if available)
ovos-config install ovos-skill-homeassistant
```

Skills register themselves automatically when installed — no manual registration. `ovos-core` discovers them via Python entry points and makes them available immediately.

**Essential skills to install:**

|Skill                     |What it adds                                     |
|--------------------------|-------------------------------------------------|
|`ovos-skill-homeassistant`|Smart home control via Home Assistant (Episode 6)|
|`ovos-skill-weather`      |Weather queries via OpenWeatherMap               |
|`ovos-skill-date-time`    |Time and date queries                            |
|`ovos-skill-timer`        |Countdown timers and alarms                      |
|`ovos-skill-wolfram-alpha`|Factual questions via Wolfram Alpha              |
|`ovos-skill-wikipedia`    |Wikipedia lookups                                |
|`ovos-skill-news`         |Current news summaries                           |
|`ovos-skill-alarm`        |Alarm clock functionality                        |

-----

## PHAL: The Body That Inhabits the World 🦾

`ovos-phal` (Platform/Hardware Abstraction Layer) is the part of OVOS that interacts with the physical environment — not the voice pipeline, but the hardware and OS around it. PHAL plugins handle:

- **Display control**: brightness, screen on/off, what is shown on the GUI
- **Network management**: Wi-Fi configuration, connection status
- **Audio routing**: select which speakers or Bluetooth device to use
- **Hardware buttons**: physical buttons on a Mark II or custom hardware
- **System events**: battery level, temperature, power state

For a headless Raspberry Pi running OVOS as a kitchen assistant, PHAL plugins handle things like: reduce the volume when the microphone picks up ambient noise above a threshold. Dim the LED ring when in sleep mode. Restart the audio service if it crashes.

```bash
# Install common PHAL plugins
pip install ovos-phal-plugin-network-manager
pip install ovos-phal-plugin-system
```

-----

## Audio Transformers: Cleaning the Voice Before STT 🎛️

Between the microphone and the STT engine, OVOS supports **audio transformer plugins** that process the raw audio. This is analogous to Burtt’s post-production treatment of the recorded voices — cleaning, enhancing, filtering — before the final composite is created.

```bash
pip install ovos-audio-transformer-plugin-denoiser
```

```json
{
  "listener": {
    "audio_transformers": {
      "ovos-audio-transformer-plugin-denoiser": {}
    }
  }
}
```

The denoiser removes background noise before STT sees the audio. In a noisy kitchen or living room (Beau and Elvis barking, Rianne running the dishwasher), this meaningfully improves STT accuracy.

-----

## The Privacy Audit: What Goes Where 🔒

With OVOS fully configured for offline operation, the data flow is entirely local:

```
Your voice
  → [microphone] → [ovos-listener, local process]
  → [Vosk STT, local model] → [text transcript, local only]
  → [ovos-core, local process] → [skill handler, local only]
  → [Piper TTS, local model] → [audio bytes, local only]
  → [speaker]
```

Nothing leaves the device. Nothing is logged to a cloud server. Nothing is used to train someone else’s model. The government scientists cannot get in because there is no door to knock on — there is no outbound connection.

This is what E.T. needed: a protected space where he could exist on his own terms, understood by the people who mattered, inaccessible to those who would exploit him.

Your voice assistant, running in your home, is that space.

-----

In **Episode 6**, E.T. makes his most meaningful connection — Home Assistant. *“I’ll be right here.”* OVOS and Home Assistant together create something neither could be alone.

-----

**🔗 Resources**

- **OVOS Plugin Manager**: [github.com/OpenVoiceOS/ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager)
- **OVOS skills on PyPI**: search `ovos-skill-` on [pypi.org](https://pypi.org)
- **All OVOS plugins** (GitHub): [github.com/OpenVoiceOS?q=ovos-](https://github.com/OpenVoiceOS?q=ovos-)
- **OVOS HuggingFace** (voice models): [huggingface.co/OpenVoiceOS](https://huggingface.co/OpenVoiceOS)

-----

*👽 E.T. by OpenVoiceOS Series is a series about OpenVoiceOS — explained through the metaphor of recreating the voice of E.T. the Extra-Terrestrial.*
