-----

## title: “E.T. by OpenVoiceOS! 👽 Ep.3: E.T. Phone Home”
published: false
description: “Episode 3: Ben Burtt built E.T.‘s voice from 18 sources — Pat Welsh, Debra Winger, raccoons, otters, a USC professor’s burp. OVOS builds synthetic voices from scratch using the same compositional logic: donor TTS → voice conversion → compact offline model. Zero recordings needed.”
tags: [voice, openvoiceos, tts, synthvoice]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/et-openvoiceos-episode-03.png”
series: “E.T. by OpenVoiceOS Series”
canonical_url: “”
organization: “the-software-s-journey”

# E.T. by OpenVoiceOS! 👽

## Episode 3: E.T. Phone Home

> *“His voice was provided by Pat Welsh, an elderly woman who smoked two packs of cigarettes a day. He also recorded sixteen other people and various animals — raccoons, sea otters, horses. The burp came from his USC film professor.”*
> — on sound designer Ben Burtt’s process, from E.T. production notes

-----

## The Most Composite Voice in Cinema 🎙️

The voice of E.T. is one of the most elaborate sonic constructions in film history. Sound designer Ben Burtt did not find a single actor who sounded like an alien — he *assembled* a voice from 18 sources.

The primary contribution came from Pat Welsh, a retired radio actress in her late sixties from Marin County, California. Burtt had overheard her speaking in a camera store and asked if he could record her. Her voice was raspy and resonant from two packs of cigarettes a day. She spent nine and a half hours recording E.T.’s fourteen lines and was paid $380 for her services.

But Pat Welsh alone was not enough. Burtt layered in actress Debra Winger’s voice (used simultaneously), Steven Spielberg’s own voice, his sleeping wife’s voice when she had a cold, a burp from his USC film professor. Then: raccoons, sea otters, horses.

The result is a voice unlike any human’s — recognisable, emotive, warm, and genuinely alien. You cannot identify the components. You only hear the character.

**This is precisely how OpenVoiceOS builds synthetic voices from scratch.**

-----

## 🗂️ SIPOC — Building the Voice

|**Suppliers**                          |**Inputs**                                          |**Process**                                                                                     |**Outputs**                                                          |**Consumers**                                              |
|---------------------------------------|----------------------------------------------------|------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|-----------------------------------------------------------|
|An existing TTS voice (the “donor”)    |Text corpus (sentences, paragraphs)                 |Generate thousands of audio/text pairs — synthetic speech data                                  |A dataset of fake voice + transcripts, no real person recorded       |The voice conversion model                                 |
|A voice conversion system              |The synthetic dataset + target voice characteristics|Transform the donor’s acoustic features into a new voice (different age, gender, accent, timbre)|Converted audio files: same words, different voice                   |The TTS model training pipeline                            |
|The training pipeline (Piper / phoonnx)|Converted audio + transcripts                       |Train a compact neural TTS model — ONNX format                                                  |A small model file (`.onnx`) that synthesises speech in the new voice|`ovos-tts-plugin-piper` on a Raspberry Pi, offline, forever|

-----

## Ben Burtt’s Method and the OVOS Method 🔬

Let us trace the parallel precisely.

### Step 1: The Donor (Pat Welsh → the Donor TTS Voice)

Ben Burtt started with Pat Welsh because she had the *right acoustic quality* — not the right words, not the right language, but the right spectral characteristics. Her voice had texture, resonance, and an unusual timbre that no standard voice had.

OVOS starts with a **donor TTS voice** — an existing text-to-speech model (from any source, any provider) that has the right characteristics. This model can generate speech in the target language. The donor is used not for its output audio quality, but for its phoneme coverage and prosodic patterns.

The donor is then used to generate **thousands of synthetic audio/text pairs** — fake speech and the text that produced it. Just as Burtt recorded Pat Welsh saying E.T.’s lines, the OVOS pipeline uses the donor to “say” huge amounts of text across the full phoneme space of the target language.

### Step 2: Voice Conversion (The Other 17 Sources → the Conversion Process)

Burtt did not simply deliver Pat Welsh’s raw recording. He layered, transformed, and blended. Debra Winger added a different harmonic quality. The raccoon sounds contributed particular vocalisations. The horse-breathing added breathiness. The cold-infected voice added a different resonance quality.

OVOS applies a **voice conversion process** to the donor’s synthetic audio. Voice conversion changes the acoustic character of speech: the pitch contour, the formant frequencies, the breathiness, the vocal weight. The result is audio that carries the same words and prosody as the donor, but in a completely different voice — a new gender, a different age, a different accent, a created character.

The critical property — parallel to Burtt’s process — is that the original source becomes *unrecognisable* in the output. The OVOs blog explicitly notes this: the process makes the voice *less recognisable*, which both creates something genuinely new and protects the acoustic identity of any source material used. Ben Burtt’s E.T. voice contains Pat Welsh, but you cannot identify Pat Welsh in it.

### Step 3: Training the Compact Model (The Final Dub → the ONNX Model)

Spielberg shot the film with stand-in voices (he himself read E.T.’s lines on set). The final voice was dubbed in post-production — assembled, processed, and delivered as the definitive, playable, distributable audio track.

OVOS takes the converted audio/text pairs and trains a **compact neural TTS model** using Piper’s architecture. The result is an ONNX model file — a single file that, given any text as input, produces speech in the new voice. This model:

- Runs **completely offline** on a Raspberry Pi
- Is **small enough** to distribute over the internet
- Produces **natural-sounding speech** in the target language and voice
- Contains **no recorded audio from any human** who did not give permission

-----

## The European Portuguese Proof 🌍

The blog post at the heart of this series — *Making Synthetic Voices From Scratch* — describes applying this technique to **European Portuguese**.

This is significant because European Portuguese had no good open-source, offline voice options. The closest available voices were Brazilian Portuguese models (similar language, very different accent) or proprietary cloud-dependent services. Communities that speak European Portuguese — in Portugal, Mozambique, Cape Verde, Angola — were left without a voice assistant in their own dialect.

The OVOS team applied the three-step process:

1. Used an existing TTS engine as donor, generating synthetic speech in European Portuguese
1. Applied voice conversion to create four distinct voice characters
1. Trained four compact Piper models

Result: **four brand-new, high-quality, offline-capable European Portuguese voices** — without recording a single human speaker.

Four voices in one language that had none. For everyone. Free. Offline. Running on a Raspberry Pi.

The film equivalent: Spielberg giving E.T. a voice that made six-year-olds cry in the cinema, when an alien character had never before been this emotionally legible.

-----

## The Ethics Conversation 🤝

Burtt was meticulous about consent. He asked Pat Welsh. He used his own voice. He recorded animals who cannot consent but are not being misrepresented. He credited everyone properly (Welsh’s credit was unfortunately omitted from the film — a regret noted in interviews).

The OVOS team applies the same care, explicitly:

- **Real person’s voice**: always require explicit, documented permission
- **No permission available**: use public domain recordings or fully synthetic sources
- **Default**: create original voices that do not copy anyone — which is exactly what the synthetic pipeline enables

The voice conversion process has an additional ethical property: it does not produce a clone of the donor. It produces something genuinely new. You cannot reverse-engineer Pat Welsh from E.T.’s voice. You cannot reverse-engineer the donor TTS from the OVOS model. The transformation is one-way.

-----

## The phoonnx Framework: The Next Generation 🚀

Since the synthetic voices blog post, the OVOS team has formalised this work into **phoonnx** — a next-generation TTS framework designed as the primary voice engine for OVOS. It builds on the same synthetic data pipeline with several advances:

- **Multiple phonemizer support**: works with eSpeak (the most common), Cotovia (for Galician), and custom G2P models for low-resource languages
- **Compatible with existing Piper models**: if you already have a Piper voice, phoonnx can run it
- **Better G2P accuracy** via ByT5 transformer-based grapheme-to-phoneme models
- **Usable with any OVOS-compatible plugin**: the model format is ONNX, the same as Piper

In `mycroft.conf`, switching to a phoonnx model via the existing Piper plugin:

```json
{
  "tts": {
    "module": "ovos-tts-plugin-piper",
    "ovos-tts-plugin-piper": {
      "model": "https://huggingface.co/OpenVoiceOS/phoonnx_eu-ES_miro_espeak/resolve/main/miro_eu-ES.onnx",
      "model_config": "https://huggingface.co/OpenVoiceOS/phoonnx_eu-ES_miro_espeak/resolve/main/miro_eu-ES.piper.json"
    }
  }
}
```

Point at a HuggingFace URL. The plugin downloads and caches the model. Done. The voice is available offline from that point.

-----

## The Library of Voices 📚

The OVOS HuggingFace account hosts the growing collection of synthetic voices created by this process: [huggingface.co/OpenVoiceOS](https://huggingface.co/OpenVoiceOS).

Voices for European Portuguese, Basque, Galician, and more — with male and female variants — each created without recording a single real speaker, each running offline on small devices, each freely available to anyone.

Burtt’s assembled E.T. voice appeared in one film and moved billions of people. These voices appear in every OVOS installation where someone chooses them — on living room devices, kitchen assistants, educational tools for children learning to read, accessibility tools for people who need a screen reader in their own language.

The scale is different. The compositional spirit is identical.

-----

In **Episode 4**, we install OVOS and watch it run on a Raspberry Pi — Elliott’s bicycle taking flight over the treeline. The components we have been discussing become a running system.

-----

**🔗 Resources**

- **OVOS blog: Making Synthetic Voices From Scratch**: [blog.openvoiceos.org/posts/2025-06-26-making-synthetic-voices-from-scratch](https://blog.openvoiceos.org/posts/2025-06-26-making-synthetic-voices-from-scratch)
- **OVOS blog: phoonnx announcement**: [blog.openvoiceos.org/posts/2025-10-06-phoonnx](https://blog.openvoiceos.org/posts/2025-10-06-phoonnx)
- **OVOS HuggingFace models**: [huggingface.co/OpenVoiceOS](https://huggingface.co/OpenVoiceOS)
- **Piper TTS voice samples**: [rhasspy.github.io/piper-samples](https://rhasspy.github.io/piper-samples/)

-----

*👽 E.T. by OpenVoiceOS Series is a series about OpenVoiceOS — explained through the metaphor of recreating the voice of E.T. the Extra-Terrestrial. Ben Burtt assembled E.T.’s voice from 18 sources. OVOS assembles yours from an ecosystem of open plugins.*
