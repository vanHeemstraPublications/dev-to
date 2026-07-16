---
title: "Nemo finds Hyperframes 🐟 Ep.2"
series: "Nemo finds Hyperframes"
part: 2
organization: "the-software-s-journey"
tags: [hyperframes, skills, claude-code, cli, npx]
---

## Episode 2: Just Keep Swimming: Installing the Skills

Dory's genius was never really about memory. It was about motion — the refusal to stop paddling just because the way forward wasn't obvious yet. `npx skills add heygen-com/hyperframes` is that same refusal, compressed into one line. This is the very first command we ran against the `hyperframes` repository before writing a single scene:

```bash
cd hyperframes
npx skills add heygen-com/hyperframes
```

The installer surfaces a picker of everything an agent might need to know about composing video. We took the core set — the school of fish that moves as one — and skipped the workflow skills, since a twenty-second promo doesn't need `/talking-head-recut` or `/pr-to-video`:

```bash
npx skills add heygen-com/hyperframes --all=false
# picker → select: hyperframes, hyperframes-core, hyperframes-animation,
#                  hyperframes-creative, hyperframes-cli, hyperframes-registry
```

`/hyperframes` is the entry skill — read first, always — the one that orients the agent to the whole reef and routes a request like "make me a video" to the correct workflow rather than leaving it drifting. `/hyperframes-core` carries the composition contract itself: the HTML structure, the `data-*` attributes, the clips, the tracks — everything `index.html` in our repo depends on. `/hyperframes-animation` teaches every animation runtime the reef supports; we only needed the GSAP adapter for this project. `/hyperframes-creative` is the one with an eye for the reef's colour — it's why our title card uses a radial ocean gradient instead of a flat navy rectangle. `/hyperframes-cli` is the dev-loop current — init, lint, preview, render, doctor. `/hyperframes-registry` installs catalog blocks on request, which we'll lean on directly in Episode 7 when we wire in `flash-through-white` and `data-chart`.

Invoking a slash command loads its context explicitly — which is the entire point. An agent that has read `/hyperframes-core` before touching `index.html` writes `data-composition-id`, `class="clip"`, and a paused, registered GSAP timeline correctly on the first attempt, the way a fish that has actually seen the current knows exactly when to stop paddling and let it carry you. That's not a metaphor for the next episode — it's literally what we needed before scaffolding the project.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| HyperFrames skills registry | `npx skills add heygen-com/hyperframes` invocation | Present a picker of core and workflow skills | Installed slash commands registered in the AI agent | AI coding agent (Claude Code, Cursor, Gemini CLI, Codex, and others) |
| `/hyperframes` entry skill | The request "build the Nemo finds Hyperframes promo" | Orient the agent and route to the matching workflow skill | A correctly-selected authoring path (core skills only, no workflow skill) | The remaining core skills used in this series |
| Developer (this series' author) | Choice between core-only and `--all` installation | Select the skill set matching a single, self-contained promo | A minimal, tailored skill installation | `hyperframes` repository, subsequent episodes |

Next stop: before anything can swim anywhere, Nemo needs an anemone — the scaffolded project structure our promo is actually born into.
