---
title: "Nemo finds Hyperframes 🐠 Ep.1"
series: "Nemo finds Hyperframes"
part: 1
organization: "the-software-s-journey"
tags: [hyperframes, heygen, ai-agents, video, html, opensource]
---

## Episode 1: 42 Wallaby Way, the Reef Where Videos Are Born
 
Somewhere past the drop-off, past the tank in the dentist's window, there is a reef where nothing gets made by hand anymore. You don't paint the coral or carve the anemone. You describe the reef you want, and the current itself writes the HTML, the CSS, and the JS that grows it. That reef is HyperFrames — HeyGen's open-source answer to the question of what happens when you let an AI agent edit video the way a developer edits a web page: by vibe-coding it, one composition at a time.

This series does not stay theoretical. Starting with this episode, everything we build lives in one real, running project — a twenty-second promo literally titled "Nemo finds Hyperframes," composed from nothing but HTML, CSS, and a GSAP timeline. The full codebase backing every episode is public at [github.com/software-journey/hyperframes](https://github.com/software-journey/hyperframes). Clone it now if you want to follow along scene by scene as we build it up:

```bash
git clone https://github.com/software-journey/hyperframes.git
cd hyperframes
```

By the end of this series that repository holds a complete, four-scene composition: a title card where Nemo swims on screen, a mock code editor typing out the composition contract, a catalog-blocks showcase with a white-flash transition and an animated bar chart, and an outro card closing on the project's own open-source license. Every code sample printed in these episodes is copied verbatim from that repository — nothing here is pseudocode.

Marlin is the AI agent in this telling — Claude Code, Cursor, Gemini CLI, Codex, and their kin — a good, careful, protective parent that would rather not let the video idea out of sight, and HyperFrames' whole design is built around making that overprotectiveness unnecessary. One `npx skills add heygen-com/hyperframes` and the agent has everything it needs to route "make me a video" to the right current and carry it home safely. The rest of this series follows Nemo — our composition — from the anemone where it is scaffolded, through the East Australian Current of animation timelines, past Bruce and the tank gang, and out into Sydney Harbour as a finished render, with real code at every stop.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| HeyGen / HyperFrames open-source project | Apache 2.0 codebase and documentation | Publish the HyperFrames runtime, CLI, and skills | Publicly available video-composition framework | AI coding agents, developers, video creators |
| `github.com/software-journey/hyperframes` | This series' running example | Host the full, buildable composition referenced by every episode | A clonable, renderable sample project | Readers following along, future contributors |
| AI coding agent (Claude Code, Cursor, etc.) | Natural-language video description | Write HTML/CSS/JS compositions following the HyperFrames contract | A composition file ready to preview and render | HyperFrames dev server, the person requesting the video |

Next stop: Dory shows up with three words of advice that turn out to be the entire installation story — just keep swimming.
