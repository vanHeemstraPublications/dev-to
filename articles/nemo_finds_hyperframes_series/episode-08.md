---
title: "Nemo finds Hyperframes 🕸️ Ep.8"
series: "Nemo finds Hyperframes"
part: 8
organization: "the-software-s-journey"
tags: [hyperframes, rendering, docker, gpu, determinism]
---

## Episode 8: The Jellyfish Forest: Deterministic Rendering

"Just don't touch the jellyfish" is the entire safety briefing, and the whole point of a HyperFrames render is that you shouldn't have to give it either. The rendering pipeline is frame-by-frame and seek-driven: headless Chrome seeks to each frame of `index.html`, captures it, and FFmpeg encodes the captured frames into the finished file.

While iterating on this project, every draft render used local mode, since we cared about speed, not cross-machine guarantees:

```bash
npx hyperframes render --output draft.mp4 --quality draft
```

```
⠋ Rendering composition "nemo-finds-hyperframes" (30fps, draft quality)
✓ Captured 600 frames in 4.1s
✓ Encoded to draft.mp4 (20.0s, 1920x1080, 1.8MB)
```

Local mode uses Puppeteer's bundled Chromium and whatever FFmpeg is already installed on the machine — it's the fast lane for the edit/save/watch loop from Episode 5. Once the four scenes and the captions track were locked, we switched to Docker mode for the version that actually ships, since "it looked right on my machine" isn't a standard worth publishing under:

```bash
npx hyperframes render --output nemo-finds-hyperframes.mp4 \
  --docker --quality high
```

Docker mode uses `chrome-headless-shell` with `BeginFrame` control for frame-perfect, deterministic capture, with an exact Chrome version and font set locked into the container — the mode for production renders and CI, where every clone of the repository needs to produce the same bytes. The `--quality` flag selects a preset controlling the H.264 CRF and encoder speed; `--crf` and `--video-bitrate` are there if a preset isn't precise enough:

```bash
# near-lossless override, if `high` still isn't enough
npx hyperframes render --output nemo-finds-hyperframes.mp4 \
  --docker --crf 16 --video-bitrate 12M
```

For this project, sizing the right settings wasn't a guess — `npx hyperframes benchmark` measured the actual system and recommended a starting point before we touched `--quality` at all:

```bash
npx hyperframes benchmark
```

Each render worker launches its own Chrome process, so multiple frames capture in parallel regardless of mode, and `--gpu` sped up the local draft renders noticeably once the catalog-blocks scene's five animated bars were added — more animated elements per frame means more to composite, which is exactly where GPU acceleration pays for itself. `--no-browser-gpu` or full Docker mode is still the right call whenever exact reproducibility matters more than raw local speed, which is why the version in the repository's `README.md` recommends Docker for anyone re-rendering it.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Hyperframes render engine (local mode) | `--quality draft` during active editing | Seek and capture frames fast, using local Chromium and FFmpeg | Quick draft MP4s for reviewing scene timing | Developer iterating on the composition |
| Hyperframes render engine (Docker mode) | `--docker --quality high` for the shipped version | Capture frames with `chrome-headless-shell` and a locked Chrome/font set | A byte-identical, CI-grade `nemo-finds-hyperframes.mp4` | Anyone cloning the repository, CI pipelines |
| `npx hyperframes benchmark` | The local system's hardware characteristics | Measure and recommend render settings before manual tuning | A starting `--quality`/`--gpu` configuration | Developer choosing render flags for this project |

Next stop: the render finishes, and it's time to see what actually swims out the other side — the finished MP4, ready for open water.
