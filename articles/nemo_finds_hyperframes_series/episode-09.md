---
title: "Nemo finds Hyperframes 🐋 Ep.9"
series: "Nemo finds Hyperframes"
part: 9
organization: "the-software-s-journey"
tags: [hyperframes, render, mp4, output-formats, cli]
---

## Episode 9: A Whale of a Render: From Composition to MP4

Being swallowed by the whale looks, from the outside, like the end of the story. From the inside, it's actually the last leg of the trip — dark, loud, and then suddenly a very deliberate exhale that deposits you exactly where you needed to be. For our project, that exhale was the same Docker-mode command from the previous episode, run one final time against the finished four-scene composition:

```bash
npx hyperframes render --output nemo-finds-hyperframes.mp4 --docker --quality high
```

```
⠋ Rendering composition "nemo-finds-hyperframes" (30fps, high quality, Docker)
✓ Captured 600 frames in 26.4s
✓ Encoded to nemo-finds-hyperframes.mp4 (20.0s, 1920x1080, 11.6MB)
```

Everything the earlier episodes set up gets swallowed whole and comes back out as that one file: the title scene's paused GSAP timeline, the code scene's typewritten lines, the catalog blocks' flash and bar chart, the outro's fade, and the `captions.html` sub-composition running quietly on its own track the whole way through. Six hundred frames at 20 seconds and 30fps is exactly `20 × 30` — no rounding, no surprise — because every number the renderer used was already sitting in the composition before the render ever started.

That's the detail worth pulling apart: the frame count, the resolution, and the duration were never negotiated at render time. They trace straight back to attributes we wrote in Episodes 3 and 4 — `data-width="1920"` and `data-height="1080"` on the root element, and the fact that the last scene's `data-start="16"` plus `data-duration="4"` adds up to exactly 20. Change any scene's timing and the total shifts automatically; there's no separate "video length" setting to keep in sync by hand.

MP4 was the right target for this project, but it isn't the only shore the whale can reach — the same command works with `--format webm`, `--format mov`, `--format gif`, or `--format png-sequence` for a lightweight embed, a production pipeline, or a compositing hand-off, all from the identical `index.html`. Nothing about the composition itself changes; only the container the frames land in does.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Hyperframes CLI (Docker mode) | `npx hyperframes render --output nemo-finds-hyperframes.mp4 --docker --quality high` | Capture all 600 frames per the composition's declared timing and encode to MP4 | The finished, playable `nemo-finds-hyperframes.mp4` | Anyone cloning `github.com/software-journey/hyperframes` |
| Composition attributes (`data-width`, `data-height`, scene `data-start`/`data-duration`) | Values authored across Episodes 3, 4, and 7 | Determine resolution (1920×1080), frame count (600), and duration (20s) at render time | A render whose specs trace exactly back to the authored HTML | The render engine, this episode's confirmation output |
| Render mode and quality preset (Episode 8) | `--docker --quality high` | Apply deterministic capture and near-final encoding | A CI-grade file suited for publishing rather than review | The person or pipeline consuming the rendered file |

Next stop: the reef comes into view — how this finished project rejoins the open-source ocean it came from.
