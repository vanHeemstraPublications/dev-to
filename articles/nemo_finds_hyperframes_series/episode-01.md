---
title: "Nemo finds Hyperframes 🐠 Ep.1"
series: "Nemo finds Hyperframes"
part: 1
organization: "the-software-s-journey"
tags: [hyperframes, heygen, ai-agents, video, html, opensource]
---

## Episode 1: 42 Wallaby Way, the Reef Where Videos Are Born

Somewhere past the drop-off, past the tank in the dentist's window, there is a reef where nothing gets made by hand anymore. You don't paint the coral or carve the anemone. You describe the reef you want, and the current itself writes the HTML, the CSS, and the JS that grows it. That reef is HyperFrames — HeyGen's open-source answer to the question of what happens when you let an AI agent edit video the way a developer edits a web page: by vibe-coding it, one composition at a time.

Every clownfish story starts the same way: something small needs to travel a long way through a big, unfamiliar ocean before it turns into something whole. In this telling, the small thing is your video idea — a ten-second product intro, a TikTok hook, a summary of a PDF turned into a forty-five-second pitch — and the ocean is the HyperFrames pipeline that carries it from a sentence typed into an AI coding agent all the way to a rendered MP4. HyperFrames does not ask you to learn a timeline-and-keyframes editor. It asks your agent to write HTML the way it already knows how, with a `data-composition-id` on the root element, `class="clip"` on anything with a start and a duration, and a GSAP timeline paused and registered so the renderer can drive it frame by frame.

Marlin is the AI agent in this telling — Claude Code, Cursor, Gemini CLI, Codex, and their kin — a good, careful, protective parent that would rather not let the video idea out of sight, and HyperFrames' whole design is built around making that overprotectiveness unnecessary. One `npx skills add heygen-com/hyperframes` and the agent has everything it needs to route "make me a video" to the right current and carry it home safely. The rest of this series follows Nemo — your composition — from the anemone where it is scaffolded, through the East Australian Current of animation timelines, past Bruce and the tank gang, and out into Sydney Harbour as a finished render.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| HeyGen / HyperFrames open-source project | Apache 2.0 codebase and documentation | Publish the HyperFrames runtime, CLI, and skills | Publicly available video-composition framework | AI coding agents, developers, video creators |
| AI coding agent (Claude Code, Cursor, etc.) | Natural-language video description | Write HTML/CSS/JS compositions following the HyperFrames contract | A composition file ready to preview and render | HyperFrames dev server, the person requesting the video |
| Prospective video creator | An idea for a video ("10-second product intro…") | Prompt the agent using the `/hyperframes` entry skill | A routed request to the correct authoring workflow | AI coding agent |

Next stop: Dory shows up with three words of advice that turn out to be the entire installation story — just keep swimming.
