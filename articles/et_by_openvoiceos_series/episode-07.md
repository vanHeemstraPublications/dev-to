-----

## title: “E.T. by OpenVoiceOS! 👽 Ep.7: E.T. Goes Home”
published: false
description: “Episode 7: The ship returns. But E.T.’s promise stays. HiveMind distributed satellites, phoonnx next-gen TTS, protocol interoperability, and the community building voice for everyone. The alien went home. The voice stayed.”
tags: [voice, openvoiceos, hivemind, community]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-openvoiceos-episode-07.png”
series: “E.T. by OpenVoiceOS Series”
canonical_url: “”
organization: “the-software-s-journey”

# E.T. by OpenVoiceOS! 👽

## Episode 7: E.T. Goes Home

> *“Be good.”*
> — E.T.’s last words to Elliott, E.T. the Extra-Terrestrial (1982)

*Two words. The most economical farewell in cinema. E.T. does not say goodbye. He does not ask Elliott to remember him. He gives an instruction — as if he knows Elliott will be fine, as if the connection they built will persist beyond the departure. As if the bicycle will always be able to fly.*

-----

## The Ship Returns 🛸

In the film’s closing act, E.T.‘s people come back for him. The ship descends into the forest. The rainbow appears in the sky. Spielberg lets John Williams’s score do almost all the work — the music swells, the goodbye is wordless, the child watching from the ground looks up at something leaving that changed him forever.

What was left behind was not loss. It was transformation.

Seven episodes of this series have traced the same arc. OVOS arrived in a California suburb — metaphorically, in an open-source landscape that did not yet know it existed. It learned to speak. It assembled its voice from composite sources, just as Ben Burtt assembled E.T.’s. It ran offline on hardware you can hold in one hand. It connected to Home Assistant and promised to stay.

This episode is about what E.T. left behind: **HiveMind**, **phoonnx**, the **protocol interoperability** work, and the **community** that ensures the ship can always come back.

-----

## 🗂️ SIPOC — Going Home

|**Suppliers**                             |**Inputs**                                     |**Process**                                                     |**Outputs**                                                              |**Consumers**                                                                          |
|------------------------------------------|-----------------------------------------------|----------------------------------------------------------------|-------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
|HiveMind (network layer)                  |Multiple OVOS devices on the same network      |Satellite devices offload STT/TTS/skills to a central OVOS core |Light satellite devices (Pi Zero, microcontroller) that only handle audio|Every room with a microphone and speaker, without running full OVOS everywhere         |
|phoonnx (TTS framework)                   |Low-resource language + synthetic data pipeline|Train ONNX TTS model using donated or synthetic speech          |New voice for a language that had none; runs offline on Pi               |Communities worldwide who could not previously have a voice assistant in their language|
|Protocol interoperability (MCP, UTCP, A2A)|External AI agents and tools                   |OVOS exposes its STT, TTS, skills as standard protocol endpoints|A universal voice layer that any agent can plug into                     |Any project wanting voice capability without reinventing the pipeline                  |

-----

## HiveMind: The Ship Connecting Everything 🛸

E.T.’s ship communicated with the alien without E.T. needing to carry the transmitter himself. He stretched out his finger and made the connection over any distance.

**HiveMind** is OVOS’s equivalent — a network layer that extends the OVOS messagebus over the network, connecting distributed voice devices.

In a typical HiveMind deployment:

```
Living Room Pi Zero 2W (satellite)
  └── microphone + speaker only
  └── HiveMind client: sends audio, receives audio

Kitchen Pi Zero 2W (satellite)
  └── microphone + speaker only
  └── HiveMind client: sends audio, receives audio

Home Server (Mac Mini, HiveMind core)
  └── Full OVOS: core, skills, STT model, TTS model
  └── HiveMind server: processes requests from all satellites
```

The satellite devices are tiny and cheap — a Pi Zero 2W costs $15. They do not need to run Vosk, Piper, or any OVOS skills locally. They just capture audio and receive audio back. All the processing happens on the central OVOS server.

This is exactly the architecture described in the CNX Software article about OVOS: “lift all the heavy duty over to a beefy server and have small low-resource satellites to talk to it.”

For a home with multiple rooms, this means one OVOS installation serves every room. Say *“Hey Mycroft, turn off all the lights”* from the kitchen — the satellite sends the audio to the Mac Mini, OVOS processes it, the HA skill executes the command, the TTS response comes back to the kitchen speaker.

The entire house has a voice assistant. Elliott’s whole family gets to talk to E.T.

-----

## phoonnx: The Voice That Will Keep Growing 🌍

We described **phoonnx** in Episode 3 as the formal framework for OVOS’s synthetic voice pipeline. In Episode 7, we look forward.

The OVOS/TigreGotico collaboration has already produced voices for European Portuguese, Basque, and Galician — languages that had no good offline TTS options. The phoonnx pipeline makes this replicable: any language with a donor TTS system and a text corpus can now have synthetic voices.

The roadmap includes:

- **ByT5 G2P models** — transformer-based grapheme-to-phoneme models for more accurate pronunciation in low-resource languages where pronunciation rules are irregular or not well-documented
- **A dedicated `ovos-tts-plugin-phoonnx`** — replacing the current Piper plugin wrapper with a first-class phoonnx plugin
- **Expanded language coverage** — more languages, more voice characters per language

The HuggingFace collection at [huggingface.co/OpenVoiceOS](https://huggingface.co/OpenVoiceOS) is the growing library. New models appear as communities collaborate with the OVOS team. The pattern established for European Portuguese — finding a language community, applying the synthetic pipeline, releasing the result freely — can repeat for any language.

Voice for everyone. Like E.T. trying to phone home — reaching across the language barrier to be understood.

-----

## Protocol Interoperability: The Universal Translator 🌐

E.T. understood Elliott even though they did not share a language. He did not demand that Elliott learn alien. He adapted, absorbed, and found a way to connect.

OVOS is doing the same thing with AI protocols. The OVOS blog post *“Building an Open and Interoperable Voice Ecosystem”* (October 2025) describes active work on:

**MCP (Model Context Protocol)** — OVOS plans to both consume MCP-compatible tools and expose its own services (STT, TTS, translation, persona server) over MCP. Any external system that speaks MCP can use OVOS’s voice pipeline.

**UTCP (Universal Tool Calling Protocol)** — a parallel effort with overlapping goals; OVOS supports both.

**A2A (Agent-to-Agent protocol)** — allows multiple agents to discover, communicate, and collaborate dynamically. HiveMind will connect via A2A, allowing OVOS voice satellites to work with *any* A2A agent, not just OVOS core.

**Wyoming** — already live (Episode 6). OVOS services expose the Wyoming protocol that Home Assistant speaks natively.

The vision is OVOS as a universal voice connector: whatever agent, whatever assistant, whatever home automation platform, whatever AI model — if it needs a voice, OVOS can provide it. Offline. Private. In your language. On your hardware.

-----

## The Full Series Map: What E.T. Taught Us 👽

Seven episodes. Here is every metaphor and what it maps to:

|E.T. the film                    |OVOS in practice                                       |Episode|
|---------------------------------|-------------------------------------------------------|-------|
|E.T. arrives in the forest       |OVOS emerges from the Mycroft community                |1      |
|The government scientists        |Big Tech cloud voice assistants                        |1      |
|The locked bedroom door          |OVOS plugin system — nothing forced, nothing cloud     |5      |
|E.T. learning to speak           |The OVOS voice pipeline                                |2      |
|The wake word moment (head turns)|`ovos-listener` wake word detection                    |2      |
|Pat Welsh in the camera store    |A donor TTS voice with the right acoustic quality      |3      |
|The 18-source composite voice    |Donor TTS → voice conversion → compact model           |3      |
|E.T.’s 14 spoken lines           |The trained phoonnx / Piper ONNX model                 |3      |
|E.T.’s unrecognisable voice      |Voice made less recognisable — privacy protection      |3      |
|European Portuguese speakers     |Language communities previously without offline TTS    |3      |
|Elliott’s bicycle over the moon  |OVOS running offline on a Raspberry Pi                 |4      |
|Reese’s Pieces trail             |Installing plugins step by step                        |5      |
|E.T.’s glowing heart             |The OVOS messagebus carrying signals between components|2      |
|*“I’ll be right here”*           |OVOS + Home Assistant via Wyoming — always local       |6      |
|HiveMind                         |The ship connecting all rooms, all satellites          |7      |
|*“Be good”*                      |The community ethic — open, inclusive, user-controlled |7      |
|E.T. going home                  |phoonnx, protocol interoperability, voice for everyone |7      |

-----

## How to Support OVOS 🤝

The alien did not build the spaceship alone. Ben Burtt did not record the voice alone. Pat Welsh was paid (although far too little). The community is the spaceship.

The OVOS foundation is a non-profit. It runs on:

**Donations** — Infrastructure, development resources, and legal protection cost money. Even small recurring amounts make a difference. [openvoiceos.org/donation](https://www.openvoiceos.org/donation)

**Contributing open data** — Speech models need diverse, high-quality audio. If you can share voice samples, transcripts, or datasets under open licences, the synthetic voice pipeline has somewhere to use them.

**Translating** — OVOS is global. Interface strings, documentation, and skill text need translating into every language the platform serves.

**Contributing code** — The plugin ecosystem grows with every new STT engine, TTS model, skill, or PHAL integration that someone writes and releases under an open licence.

**Simply using it and reporting issues** — Finding bugs, documenting edge cases, asking questions in the GitHub discussions. The community that maintains this knows what to fix when users tell them.

-----

## The Bicycle Can Always Fly 🌙

In the final shot of E.T., the bicycle silhouette across the moon has become an indelible image — not just of the film, but of a certain kind of wonder. The wonder of seeing something impossible and then slowly realising that the word *impossible* was just wrong.

A fully private, fully local, multilingual voice assistant that runs on a $55 Raspberry Pi and understands your questions and speaks back in a natural voice synthesised from no real person’s recordings — without cloud dependency, without data harvesting, without subscription fees, maintained by a community of developers building it for people — that sounds impossible.

*“This is reality, Greg.”*

The bicycle is over the moon.

-----

**🔗 Resources**

- **HiveMind project**: [github.com/JarbasHiveMind](https://github.com/JarbasHiveMind)
- **OVOS interoperability blog post**: [blog.openvoiceos.org/posts/2025-10-24-protocol_interoperability](https://blog.openvoiceos.org/posts/2025-10-24-protocol_interoperability)
- **OVOS contribution page**: [openvoiceos.org/contribution](https://www.openvoiceos.org/contribution)
- **OVOS Foundation**: [openvoiceos.org/about](https://www.openvoiceos.org/about)
- **Discord / GitHub discussions**: [github.com/OpenVoiceOS/OpenVoiceOS/discussions](https://github.com/OpenVoiceOS/OpenVoiceOS/discussions)

-----

*👽 E.T. by OpenVoiceOS Series is a series about OpenVoiceOS — explained through the metaphor of recreating the voice of E.T. the Extra-Terrestrial.*
*Ben Burtt assembled E.T.’s voice from 18 sources. OVOS assembles yours from an ecosystem of open plugins. The alien went home. The voice stayed.*
