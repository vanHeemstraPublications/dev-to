---
title: "Nemo finds Hyperframes 🐟 Ep.2"
series: "Nemo finds Hyperframes"
part: 2
organization: "the-software-s-journey"
tags: [hyperframes, skills, claude-code, cli, npx]
---

## Episode 2: Just Keep Swimming: Installing the Skills

Dory's genius was never really about memory. It was about motion — the refusal to stop paddling just because the way forward wasn't obvious yet. `npx skills add heygen-com/hyperframes` is that same refusal, compressed into one line. Run it, and an installer surfaces a picker of everything your agent might need to know about composing video, and swimming forward from there is simply a matter of picking the current that suits your trip.

The core set is the one every project needs, and it reads like a school of fish that has learned to move as one. `/hyperframes` is the entry skill — read first, always — the one that orients the agent to the whole reef and routes a request like "make me a video" to the correct workflow rather than leaving it drifting. `/hyperframes-core` carries the composition contract itself: the HTML structure, the `data-*` attributes, the clips, the tracks. `/hyperframes-animation` teaches every animation runtime the reef supports — GSAP, Lottie, Three.js, Anime.js, CSS, WAAPI, TypeGPU. `/hyperframes-creative` is the one with an eye for the reef's colour: palettes, typography, narration, beat planning. `/hyperframes-cli` is the dev-loop current — init, lint, preview, render, doctor. `/hyperframes-media` handles the asset preprocessing that turns raw footage and audio into something the composition can use — TTS, transcription, background removal. `/hyperframes-registry` installs catalog blocks and components on request, and `/general-video` is the fallback current for anything that doesn't match a more specific workflow.

Beyond the core set sit the workflow skills — optional currents you only need if your trip actually goes there: `/product-launch-video`, `/website-to-video`, `/faceless-explainer`, `/pr-to-video`, `/embedded-captions`, `/talking-head-recut`, `/motion-graphics`, `/music-to-video`, `/slideshow`, `/remotion-to-hyperframes`. Install all of them at once with `npx skills add heygen-com/hyperframes --all` if you'd rather not pick and choose, and let `/hyperframes` sort out which current applies once the request actually arrives. Invoking a slash command loads its context explicitly — which is the entire point. An agent that has read the right skill produces a correct composition on the first attempt, the way a fish that has actually seen the current knows exactly when to stop paddling and let it carry you.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| HyperFrames skills registry | `npx skills add heygen-com/hyperframes` invocation | Present a picker of core and workflow skills | Installed slash commands registered in the AI agent | AI coding agent (Claude Code, Cursor, Gemini CLI, Codex, and others) |
| `/hyperframes` entry skill | A natural-language video request | Orient the agent and route to the matching workflow skill | A correctly-selected authoring path | The remaining core and workflow skills |
| Developer or video creator | Choice between core-only and `--all` installation | Select the skill set matching the project's needs | A tailored or comprehensive skill installation | AI coding agent, future composition work |

Next stop: before anything can swim anywhere, Nemo needs an anemone — the scaffolded project structure a new video is born into.
