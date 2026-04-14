---
title: "E.T. by OpenVoiceOS 👽 Ep.1"
part: 1
published: false
description: "Episode 1: In 1982, an alien arrived in a California suburb. In 2020, OpenVoiceOS arrived in the open-source landscape. Both were trying to phone home — to connect, to be understood, to belong. Meet OVOS: the voice assistant that is truly yours."
tags: [voice, openvoiceos, ai, homeautomation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et_by_openvoiceos_series/et-by-openvoiceos-episode-01.png"
series: "E.T. by OpenVoiceOS Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 1: E.T. Has Arrived

> *“He’s a man from outer space and we’re taking him to his spaceship.”*
> *“Well, can’t he just beam up?”*
> *“This is reality, Greg.”*
> — Elliot and Greg, E.T. the Extra-Terrestrial (1982)

-----

## A Small, Strange Visitor in the Suburbs 🏠

The opening of Spielberg’s 1982 masterpiece is unforgettable. A dark California forest. A humming, glowing spaceship. Small, wide-eyed creatures moving quietly among the trees. Then headlights. Men with walkie-talkies. The ship lifts away — and one creature is left behind, alone in the forest, in a world that does not speak its language and does not yet know it exists.

That alien, of course, finds its way to a suburban garage. Where a frightened boy named Elliott discovers it. And everything changes.

In 2020, something similar arrived in the open-source software world.

**OpenVoiceOS** — OVOS — arrived after Mycroft AI, the company that had promised an open-source voice assistant, slowly closed off the very infrastructure its community had built. The company went bankrupt in 2023. But the community that had been maintaining patches, building plugins, and working around Mycroft’s constraints had already quietly rebuilt everything from scratch. Not a fork born of anger — a survival move by people who needed it to work. Privately. Locally. On their terms.

OVOS is that alien: strange-looking to those used to Alexa and Google Assistant, speaking a language of plugins and message buses rather than cloud APIs and proprietary backends. But once you understand it, the connection is extraordinary.

-----

## 🗂️ SIPOC — The Arrival

|**Suppliers**                    |**Inputs**                                       |**Process**                                                   |**Outputs**                                                                        |**Consumers**                                                 |
|---------------------------------|-------------------------------------------------|--------------------------------------------------------------|-----------------------------------------------------------------------------------|--------------------------------------------------------------|
|You (speaking to your device)    |Your voice, in your language                     |Wake word detection → STT → Intent parsing → Skills → TTS     |A spoken response from your own device, processed entirely locally                 |You — not Amazon, not Google, not a cloud server              |
|The OVOS plugin ecosystem        |Your chosen STT, TTS, wake word models           |Plugin Manager routes each stage to your chosen implementation|A modular stack where every component is yours to choose and replace               |Developers, tinkerers, privacy advocates, language communities|
|The community (not a corporation)|Contributions from dozens of developers worldwide|Collaborative, open development under Apache 2.0 licence      |A voice assistant that is genuinely open — not just in licence, but in architecture|Everyone who was promised this by Big Tech and never got it   |

-----

## What OVOS Is — and What It Is Not 🎭

OVOS is not a product. There is no OVOS Inc. writing product requirements and shipping quarterly releases with a marketing team. OVOS is a **community-maintained, open-source voice assistant framework** — a set of modular components that you assemble and configure into a voice assistant that fits your hardware, your language, your privacy requirements, and your use case.

What it is **not**:

- Not cloud-dependent (it *can* use cloud services if you choose, but nothing requires them)
- Not locked to a specific microphone, speaker, or device
- Not locked to English
- Not controlled by any single company
- Not sending your voice data anywhere you have not explicitly configured

What it **is**:

- A modular Python framework, fully compatible with the Mycroft skill ecosystem
- Running on any Linux machine, from a Raspberry Pi to a server rack
- Built around a **message bus** architecture — every component talks to every other component through a common language of events
- Extendable by plugins at every stage: wake word detection, speech-to-text, text-to-speech, skills, platform integrations, GUI

-----

## The Five Components of the OVOS System 🔧

Like E.T.’s biological systems — chest glowing red, heart rate spiking near Elliott, fingers extending to heal — OVOS has five core components that together create the experience of a living, listening, speaking assistant:

**`ovos-messagebus`** — The nervous system. Every component — listener, core, audio, GUI, skills — communicates by publishing and subscribing to messages on this bus. Nothing calls another component directly. Everything is an event. When E.T.’s heart glows, it is not his brain commanding his skin — it is a signal propagating through a system. The messagebus is that signal infrastructure.

**`ovos-core`** — The brain. Handles all skills, manages intent parsing, routes utterances to the correct skill handler. Fully compatible with Mycroft skills — the ecosystem of abilities your assistant can have. If E.T.’s vocabulary grows from two words to full sentences during the film, this is the component responsible.

**`ovos-listener`** — The ears. Manages the microphone, runs wake word detection, performs Voice Activity Detection (VAD), and passes audio to the Speech-to-Text engine. When E.T.’s head tilts up and those enormous eyes widen in recognition — that is the listener doing its job.

**`ovos-audio`** — The voice. Manages the speaker. Receives the text response from the skill, passes it to the Text-to-Speech engine, plays the audio. When E.T. rasps *“E.T. phone home”*, this is the component responsible.

**`ovos-phal`** — The body. Platform/Hardware Abstraction Layer. Handles everything that is device-specific: screen brightness, network management, hardware buttons, battery status, camera integration. The part of E.T. that knows how to operate in a *physical* environment — including the suburban house he finds himself in.

-----

## The Origin Story: Mycroft and the Government Scientists 🚐

The parallel to E.T. is uncomfortably accurate. In the film, government scientists eventually arrive and try to claim E.T. — they want to study him, control him, isolate him from the people who love him. The corporate analogy is uncomfortable but apt.

Mycroft AI promised an open-source voice assistant. Community developers contributed code, plugins, fixes, and improvements for years. Then Mycroft kept the infrastructure closed — the Selene backend, the STT service, the TTS service. Critical patches enabling local-first alternatives were rejected. The company controlled the voice while the community did the work.

*“They’re here. They’re already here,”* as Elliott realises in the film.

In 2020, the community did the only thing they could: they took everything they had built independently and made it official. OpenVoiceOS was born. Not as a rebellion — as a survival move. The same year the government scientists arrived, the bikes took to the air.

The OVOS blog post on this history is titled *“OVOS and Mycroft: A Fork That Wasn’t Meant to Be.”* The title alone is an entire story.

-----

## The E.T. Metaphor: A Series Map 👽

In the seven episodes of this series, we follow the same journey E.T. takes in the film — from arrival through connection, communication, and finally, going home:

|#|Episode                  |E.T. parallel                   |OVOS concept                         |
|-|-------------------------|--------------------------------|-------------------------------------|
|1|*This one* — arrival     |E.T. lands in the forest        |What OVOS is; architecture overview  |
|2|He can talk!             |E.T. learns to speak            |Wake word → STT → TTS pipeline       |
|3|E.T. phone home          |Ben Burtt creates the voice     |Synthetic voices from scratch        |
|4|Elliott’s bicycle        |The bike rises over the treeline|Installing OVOS; running offline     |
|5|The government scientists|Scientists try to control E.T.  |Plugins; choosing your own everything|
|6|“I’ll be right here”     |E.T.’s final promise            |OVOS + Home Assistant via Wyoming    |
|7|E.T. goes home           |The ship returns                |HiveMind; phoonnx; community         |

The alien has arrived in your garage. In Episode 2, we learn how it communicates.

-----

**🔗 Resources**

- **OpenVoiceOS website**: [openvoiceos.org](https://www.openvoiceos.org)
- **OVOS GitHub**: [github.com/OpenVoiceOS](https://github.com/OpenVoiceOS)
- **OVOS Technical Manual**: [openvoiceos.github.io/ovos-technical-manual](https://openvoiceos.github.io/ovos-technical-manual)
- **OVOS Blog**: [blog.openvoiceos.org](https://blog.openvoiceos.org)
- **OVOS HuggingFace** (TTS models): [huggingface.co/OpenVoiceOS](https://huggingface.co/OpenVoiceOS)

-----

*👽 E.T. by OpenVoiceOS Series is a series about OpenVoiceOS — explained through the metaphor of recreating the voice of E.T. the Extra-Terrestrial. Like Ben Burtt assembling E.T.’s voice from 18 sources, OVOS assembles a fully private, fully offline voice assistant from an ecosystem of open plugins.*
