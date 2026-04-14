---
title: "E.T. by OpenVoiceOS 👽 Ep.2"
part: 2
published: false
description: "Episode 2: E.T. learned to speak by listening. OVOS listens for its wake word, converts speech to text, parses intent, and speaks a reply — entirely on your device. The complete voice pipeline, explained through E.T.’s journey from grunts to sentences."
tags: [voice, openvoiceos, tts, stt]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et_by_openvoiceos_series/et-openvoiceos-episode-02.png"
series: "E.T. by OpenVoiceOS Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: He Can Talk! He Can Talk!

> *“E.T. phone home.”*
> — E.T. the Extra-Terrestrial (1982)

*Fourteen spoken lines. That is all E.T. says in the entire film. But each one lands with extraordinary weight because of how they were constructed — a composite voice assembled from 18 sources by sound designer Ben Burtt. In OVOS, the equivalent pipeline turns your words into meaning and speaks back to you with the same compositional care.*

-----

## From Grunts to Sentences 🎙️

When E.T. first arrives, he communicates only in rasping, startled sounds. Then Elliott starts leaving Reese’s Pieces trails, and something remarkable happens: the alien begins to absorb language. By mid-film, E.T. can point to a television and say *“phone.”* By the end, he speaks in full sentences — *“I’ll be right here.”*

The OVOS voice pipeline is the technical embodiment of that learning arc. It starts with raw sound — audio bytes from a microphone — and produces language, meaning, and finally a spoken response. This episode maps every stage.

-----

## 🗂️ SIPOC — The Voice Pipeline

|**Suppliers**                    |**Inputs**                         |**Process**                                         |**Outputs**                                        |**Consumers**              |
|---------------------------------|-----------------------------------|----------------------------------------------------|---------------------------------------------------|---------------------------|
|Your microphone (`ovos-listener`)|Raw audio stream (PCM bytes, 16kHz)|VAD → wake word detection → buffer capture          |An audio buffer: your utterance after the wake word|The STT engine             |
|STT plugin                       |Audio buffer                       |Speech-to-text inference (local model or remote API)|A text transcript of what you said                 |`ovos-core` intent parser  |
|`ovos-core` + skills             |Text transcript                    |Intent parsing → skill matching → handler execution |A text response from the skill                     |The TTS engine             |
|TTS plugin                       |Text response                      |Text-to-speech synthesis (local model or cloud)     |An audio file: the synthesised speech              |`ovos-audio` → your speaker|

-----

## Stage 1: Hearing — The Wake Word 👂

E.T.’s enormous eyes and oversized ears are his most expressive features. He is, above all, a *listener*. He tilts his head. He absorbs everything. He knows when something important is happening before anyone else does.

`ovos-listener` is OVOS’s ear. It runs continuously, sampling the microphone at 16kHz, always awake, always waiting — but not recording, not transmitting. It listens for one thing: the **wake word**.

### What is a wake word?

A wake word is a trigger phrase — a specific combination of sounds that tells the system *“pay attention now, the user is about to speak a command.”* The default OVOS wake word is `hey mycroft`, but it is completely configurable: any phrase, in any language.

### Wake word plugins

OVOS has three primary wake word engines, selectable via plugin:

**`ovos-ww-plugin-precise-lite`** — the default. Uses a tiny TensorFlow Lite model trained specifically on the wake word. Fast, accurate, low false-positive rate. Perfect for `hey mycroft` out of the box. Requires a model file — you can train custom models.

**`ovos-ww-plugin-vosk`** — uses the Vosk ASR library for text-based detection. No model training required. Slower, more false positives, but *zero setup*. Type `"hey et"` and it will detect it. Perfect for getting started or collecting data.

**`ovos-ww-plugin-pocketsphinx`** — a phoneme-based detector. Useful for wake-up words (`wake up`) and languages where phoneme dictionaries exist.

### Configuring the wake word

In `mycroft.conf` (OVOS’s configuration file):

```json
{
  "listener": {
    "wake_word": "hey_et"
  },
  "hotwords": {
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

The `samples` array defines what Vosk should match. The `fuzzy` rule accepts close matches. Within minutes, your OVOS installation wakes up when you say *“Hey E.T.”*

Ben Burtt found E.T.’s voice by accident — overhearing Pat Welsh in a camera store. You configure your wake word deliberately. But both serve the same purpose: the moment of recognition. The head turns. The eyes widen. Attention is paid.

-----

## Stage 2: Understanding — Speech-to-Text 📝

Once the wake word fires, `ovos-listener` captures the audio that follows — everything you say until silence indicates you have finished — and sends it to the **STT (Speech-to-Text) plugin**.

The STT plugin transcribes your voice into text. This is where *“Turn off the living room light”* becomes the string `"turn off the living room light"`. The intelligence of this conversion depends entirely on the model you choose.

### STT plugins available in OVOS

|Plugin                        |How it runs                    |Quality                |Privacy                           |
|------------------------------|-------------------------------|-----------------------|----------------------------------|
|`ovos-stt-plugin-vosk`        |Fully local                    |Good for short commands|Total — nothing leaves your device|
|`ovos-stt-plugin-whisper`     |Fully local (requires more RAM)|Excellent              |Total                             |
|`ovos-stt-plugin-server`      |Remote, community-hosted       |Very good              |Sent to community server          |
|`ovos-stt-plugin-google-cloud`|Google Cloud API               |Excellent              |Sent to Google                    |

For total privacy — the OVOS philosophy — `ovos-stt-plugin-vosk` runs locally on a Raspberry Pi. For higher accuracy on the same hardware, `ovos-stt-plugin-whisper` is remarkable but requires more memory.

### The fallback chain

OVOS supports **fallback STT plugins** — if the primary fails (model not loaded, network unavailable), it automatically tries the next one:

```json
{
  "stt": {
    "module": "ovos-stt-plugin-vosk",
    "fallback_module": "ovos-stt-plugin-server"
  }
}
```

Offline first, online fallback. E.T. had his own communication methods, but he could use Elliott’s phone when needed.

-----

## Stage 3: Thinking — Intent and Skills 🧠

The transcribed text arrives at `ovos-core`. Now the brain takes over.

**Intent parsing** is the process of determining *what the user wants* from what they *said*. The words *“turn off the living room light”* need to be understood as: `intent: turn_off_lights`, `location: living room`. This is fundamentally different from keyword matching — OVOS understands variations: *“switch off the living room”*, *“can you darken the living room”*, *“the living room is too bright”*.

OVOS supports multiple intent parsers (Padatious, Adapt, OpenIE) and can chain them — if the primary parser does not recognise the intent, the next one tries. Skills register their intent patterns, and when a match is found, the corresponding skill handler executes.

A skill is a Python module that defines:

- What utterances it handles (intent patterns or regexes)
- What it does when triggered (call an API, control a device, answer a question)
- What it says back (the response text)

OVOS is fully compatible with the Mycroft skill ecosystem — thousands of community skills available for weather, timers, smart home control, music, news, Wikipedia, and more.

-----

## Stage 4: Speaking — Text-to-Speech 🔊

The skill produces a text response. `ovos-core` passes it to the TTS engine via the messagebus. `ovos-audio` calls the **TTS plugin**, which converts the text into an audio file. The audio plays through your speaker.

### TTS plugins available in OVOS

|Plugin                      |Voice quality     |Runs offline        |Languages|
|----------------------------|------------------|--------------------|---------|
|`ovos-tts-plugin-piper`     |Excellent (neural)|Yes, on Raspberry Pi|30+      |
|`ovos-tts-plugin-mimic3`    |Very good (neural)|Yes                 |30+      |
|`ovos-tts-plugin-espeak`    |Robotic but fast  |Yes                 |100+     |
|`ovos-tts-plugin-google-tts`|Excellent         |No — cloud          |60+      |

The star of the OVOS TTS story is **Piper** (and its successor, **phoonnx**) — a fast, neural, offline TTS system that runs surprisingly well on a Raspberry Pi and supports voices in dozens of languages. Including languages that had *no* good offline voice options before OVOS created them from scratch — more on this in Episode 3.

-----

## The Complete Pipeline in Configuration 🔧

Here is a minimal `mycroft.conf` wiring the complete voice pipeline:

```json
{
  "listener": {
    "wake_word": "hey_et"
  },
  "hotwords": {
    "hey_et": {
      "module": "ovos-ww-plugin-vosk",
      "listen": true,
      "lang": "en-us",
      "samples": ["hey et", "hey e.t."]
    }
  },
  "stt": {
    "module": "ovos-stt-plugin-vosk",
    "fallback_module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "url": "https://stt.openvoiceos.com/stt"
    }
  },
  "tts": {
    "module": "ovos-tts-plugin-piper",
    "ovos-tts-plugin-piper": {
      "voice": "en_US-lessac-medium"
    }
  }
}
```

Four sections. Four stages of the pipeline. Each swappable independently — change your TTS voice without touching the wake word. Change your STT engine without touching the skills. Change everything without changing anything else.

This is the architecture that Mycroft should have been. This is what the community built.

-----

## The Messagebus: E.T.’s Glowing Heart 💗

All of these stages — wake word, STT, intent, skill, TTS — never call each other directly. They all communicate through `ovos-messagebus` by publishing and subscribing to named events.

When the wake word fires, the listener publishes: `recognizer_loop:wakeword`.

When STT completes, it publishes: `recognizer_loop:utterance` with the transcript in the payload.

When the skill responds, it publishes: `speak` with the text.

When `ovos-audio` finishes playing, it publishes: `mycroft.audio.speech.end`.

Any component can subscribe to any event. A skill can listen for wake word events. A GUI component can show a visual indicator when speech starts. An integration can trigger external actions when a specific utterance is recognised.

In the film, when E.T.‘s chest glows red, everyone around him reacts — Elliott’s chest glows too. The emotion propagates. The messagebus is that propagation system for your voice assistant: one event touches everything that cares about it.

-----

In **Episode 3**, we go deeper into the voice — specifically, how OVOS *creates* new voices from scratch. Ben Burtt recorded raccoons and otters to build E.T.’s voice. The OVOS team built four brand-new European Portuguese voices without recording a single human speaker. The techniques rhyme.

-----

**🔗 Resources**

- **OVOS Technical Manual — Listener**: [openvoiceos.github.io/ovos-technical-manual/101-speech_service](https://openvoiceos.github.io/ovos-technical-manual/101-speech_service/)
- **Wake Word plugins**: [openvoiceos.github.io/ovos-technical-manual/312-wake_word_plugins](https://openvoiceos.github.io/ovos-technical-manual/312-wake_word_plugins/)
- **OVOS STT plugins** (GitHub): [github.com/OpenVoiceOS?q=ovos-stt](https://github.com/OpenVoiceOS?q=ovos-stt)
- **OVOS TTS plugins** (GitHub): [github.com/OpenVoiceOS?q=ovos-tts](https://github.com/OpenVoiceOS?q=ovos-tts)

-----

*👽 E.T. by OpenVoiceOS Series is a series about OpenVoiceOS — explained through the metaphor of recreating the voice of E.T. the Extra-Terrestrial.*
