---
title: "Nemo finds Hyperframes 🏠 Ep.3"
series: "Nemo finds Hyperframes"
part: 3
organization: "the-software-s-journey"
tags: [hyperframes, cli, scaffolding, project-structure]
---

## Episode 3: The Anemone Nursery: Scaffolding a Project

Every clownfish egg needs an anemone before it needs anything else — a small, stinging, protective home to hatch inside before the wider reef becomes survivable. For our promo, that anemone was one command, run non-interactively since we already knew exactly what we wanted:

```bash
npx hyperframes init nemo-finds-hyperframes \
  --non-interactive --example blank
```

That produced the skeleton this whole repository grew from:

```
nemo-finds-hyperframes/
├── meta.json
├── index.html
├── compositions/
└── assets/
```

We filled in `meta.json` by hand right after scaffolding, since the blank example leaves it minimal and we wanted the project's real dimensions and framerate recorded from day one:

```json
{
  "name": "nemo-finds-hyperframes",
  "id": "nemo-finds-hyperframes",
  "created": "2026-07-16T09:00:00Z",
  "description": "Companion sample video for the 'Nemo finds Hyperframes' dev.to series — a 20s promo composed entirely in HTML, CSS, GSAP and JS.",
  "width": 1920,
  "height": 1080,
  "fps": 30
}
```

`index.html` is the root composition — the video's actual entry point, the egg itself — and at this stage it was still just the blank example's shell: a single `div` with `data-composition-id`, no scenes yet. `compositions/` is where sub-compositions get pulled in via `data-composition-src`; ours would end up holding exactly one file, `captions.html`, which Episode 4 introduces. `assets/` stayed empty for this project — everything on screen is CSS, SVG, and GSAP, no imported video or audio — which is worth calling out on its own: HyperFrames doesn't require media assets at all, just HTML that knows how to draw itself.

Nothing in any of this is bespoke to HyperFrames' own dialect. It's HTML, JSON, and a folder convention, which is exactly why an agent that already knows how to write a web page can write a video composition without learning a second language. And `hyperframes init` installed the skills from Episode 2 automatically as part of scaffolding — there was no separate errand between "create the project" and "hand it to the agent."

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Developer | `npx hyperframes init nemo-finds-hyperframes --non-interactive --example blank` | Run the scaffolding wizard against the blank template | The initial `meta.json`, `index.html`, `compositions/`, `assets/` structure | Episode 4's composition-editing work |
| Hyperframes CLI | `--example blank` template selection | Generate the starting composition structure with no example content | A minimal, unopinionated starting `index.html` | Developer, AI agent |
| Project author | Real project dimensions (1920×1080, 30fps) and description | Hand-edit the scaffolded `meta.json` | A complete, accurate project metadata file | The render pipeline (which reads these defaults later) |

Next stop: the East Australian Current — where a paused GSAP timeline picks Nemo up and carries the first real scene through its animated beats.
