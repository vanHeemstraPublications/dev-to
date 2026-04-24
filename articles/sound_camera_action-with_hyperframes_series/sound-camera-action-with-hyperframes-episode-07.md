---
title: "Sound, Camera, Action! 🎬 Ep.7
published: false
description: "Episode 7: The director calls 'Rolling!' and the cameras start. HyperFrames' render pipeline — local mode for iteration, Docker mode for deterministic production output, quality presets, GPU encoding, parallel workers, and CI/CD integration. Everything from draft rushes to the final print."
tags: [javascript, html, video, devops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/sound_camera_action_with_hyperframes_series/sound-camera-action-with-hyperframes-episode-07.png"
series: "Sound, Camera, Action with HyperFrames Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: Rolling! — The Render Pipeline

> "When the director calls 'rolling', the camera operator confirms the stock is running, the sound recordist confirms the mic is live, and only then does the director call 'action'. Every step is verified before anything irreversible happens."

## From Dailies to the Final Print 🎞️

In the analogue film era, dailies were the raw footage sent to the lab overnight. The next morning, the director and editor watched the previous day's shoot projected on screen — a rough print, not colour-graded, not assembled, but representative. When the edit was locked, the negative went through digital intermediate (DI) — the final colour grade, audio mix, and quality check before the distribution print was struck.

HyperFrames has both. `npx hyperframes preview` is your dailies — instant, in-browser, good enough to judge whether the composition is working. `npx hyperframes render` is the DI — the frame-perfect, configurable, FFmpeg-encoded output.

This episode covers every aspect of the render pipeline: when to use local vs Docker mode, how quality presets affect file size and fidelity, how to tune workers for your hardware, and how to integrate HyperFrames into a CI/CD pipeline for automated video production.

## 🗂️ SIPOC — The Render Pipeline

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| Your composition HTML | Valid index.html passing npx hyperframes lint | npx hyperframes render → Puppeteer (Chromium) loads page, engine seeks each frame, Chrome captures pixel buffer | Frame sequence (JPEG for MP4, PNG+alpha for MOV/WebM) | FFmpeg — receives frame sequence via pipe |
| FFmpeg | Frame sequence + audio from media clips | Encodes with H.264 (MP4), ProRes 4444 (MOV), or VP9 (WebM) using quality preset | Final video file | Media players, video editors, CDNs, social platforms |
| Docker (optional) | docker pull heygen/hyperframes-renderer | Runs chrome-headless-shell inside container with beginFrame API control | Byte-for-byte identical output on every machine | CI/CD pipelines, team shared renders, production automation |

## The Doctor's Check: Before Every Render 🩺

Before rendering, verify your environment:

```bash
npx hyperframes doctor
```

```
✓ Node.js    v22.4.0
✓ FFmpeg      7.1.1
✓ FFprobe     7.1.1
✓ Chrome      (bundled with Puppeteer)
✓ Docker      24.0.5 — available
```

If any item fails, the relevant section of the Troubleshooting guide explains the fix. On macOS: `brew install ffmpeg`. On Ubuntu: `sudo apt install ffmpeg`.

## Local Mode vs Docker Mode: Studio vs Location Shoot 🎬

### Local mode (default) — the location shoot

Renders using your system's Chromium and FFmpeg. Fast startup — no container to pull or initialise. Ideal for rapid iteration during development.

```bash
npx hyperframes render --output output.mp4
```

**Pros:** Fast startup; can use your GPU for hardware-accelerated encoding; no Docker required.

**Cons:** Output may vary slightly across different operating systems and Chrome versions (different font rendering, different Chromium compositor behaviour). Not suitable for production pipelines requiring reproducible output.

### Docker mode — the controlled studio

Renders inside a locked Docker container with a specific Chrome version, specific fonts, and a specific FFmpeg build. Same input always produces byte-for-byte identical output on any machine.

```bash
npx hyperframes render --docker --output output.mp4
```

**Pros:** Deterministic output — the same composition renders identically on your laptop, your colleague's Linux server, and your CI runner. The standard for production pipelines.

**Cons:** First run pulls the Docker image (1 GB). Slower startup (10s). No GPU inside the container.

### When to use each

| Scenario | Mode |
| --- | --- |
| Iterating on a composition | Local |
| Quick preview export | Local |
| Final delivery to client | Docker |
| Sharing a render with the team | Docker |
| AI agent-driven automated rendering | Docker |
| CI/CD pipeline | Docker |
| Benchmarking render performance | Local |

## Quality Presets: From Draft Rushes to the Final Print 🎞️

Three quality presets control the H.264 Constant Rate Factor (CRF) and encoder speed:

| Preset | CRF | x264 preset | Use case | Typical file size (1080p, 10s) |
| --- | --- | --- | --- | --- |
| draft | 28 | ultrafast | Quick iteration — "let me see if it's working" | ~2 MB |
| standard (default) | 18 | medium | General use — visually lossless at 1080p | ~8 MB |
| high | 15 | slow | Final delivery — near-lossless | ~18 MB |

CRF is logarithmic: every 6 points doubles the file size and halves the perceived quality difference. The default `standard` preset at CRF 18 is visually indistinguishable from the source for the vast majority of viewers at 1080p.

```bash
# Fast drafts during iteration
npx hyperframes render --quality draft --output draft.mp4

# Standard (default) — what you deliver for most purposes
npx hyperframes render --output output.mp4

# Near-lossless final delivery
npx hyperframes render --quality high --output final.mp4

# Fine control: override CRF directly
npx hyperframes render --crf 12 --output pristine.mp4

# Target bitrate for size-constrained delivery (streaming platforms)
npx hyperframes render --video-bitrate 8M --output streaming.mp4
```

## All Render Options: The Full Clapperboard 🎬

```bash
npx hyperframes render \
  --output film.mp4        \   # output path (default: renders/<n>.mp4)
  --format mp4             \   # mp4 | mov | webm
  --fps 30                 \   # 24 | 30 | 60
  --quality standard       \   # draft | standard | high
  --workers 4              \   # parallel Chrome processes (default: auto)
  --docker                 \   # deterministic Docker mode
  --gpu                    \   # GPU encoding (NVENC / VideoToolbox / VAAPI)
  --hdr                    \   # detect HDR sources, output HDR10
  --quiet                      # suppress verbose output
```

## Workers: Parallel Camera Units 📸

Each worker is an independent Chrome process that captures frames in parallel. More workers = faster renders on multi-core machines. Each worker consumes ~256 MB RAM.

HyperFrames' default: **half your CPU cores, capped at 4**.

| Machine | CPU cores | Default workers |
| --- | --- | --- |
| 8-core MacBook Pro | 8 | 4 (capped) |
| 4-core laptop | 4 | 2 |
| 2-core VM | 2 | 1 |
| 16-core render server | 16 | 4 (capped) |

```bash
# Explicit worker count — override the default
npx hyperframes render --workers 2 --output output.mp4

# Auto (default) — let HyperFrames decide
npx hyperframes render --workers auto --output output.mp4

# Maximum — use all available cores (on a dedicated render machine)
npx hyperframes render --workers 8 --output output.mp4
```

**When to use 1 worker:**

- Short compositions (under 60 frames / 2 seconds) — parallelism overhead exceeds the benefit
- Low-memory machines (4 GB or less)
- Running alongside other resource-intensive processes

**When to increase workers:**

- Long compositions (30+ seconds) on a well-provisioned machine
- Dedicated render servers or CI runners
- `--workers auto` shows sluggish performance and you have headroom

## GPU Encoding: The High-Speed Camera 🚀

On machines with compatible GPUs, `--gpu` switches from software H.264 encoding to hardware-accelerated encoding:

| Platform | Encoder used |
| --- | --- |
| macOS (Apple Silicon) | VideoToolbox |
| macOS (Intel + AMD/Nvidia) | VideoToolbox |
| Linux (Nvidia) | NVENC |
| Linux (AMD) | VAAPI |

```bash
# GPU-accelerated encoding — significantly faster for long compositions
npx hyperframes render --gpu --output output.mp4

# GPU in Docker mode is not supported (containers have no GPU access by default)
# For GPU + determinism, use a local render with a fixed Chrome version
```

## Frames per Second: Choosing the Film Rate 🎞️

| FPS | Use case |
| --- | --- |
| 24 | Cinematic feel — the Hollywood standard |
| 30 | Web and social media — the standard for YouTube, TikTok |
| 60 | Smooth motion content — gaming, sports, tutorials |

```bash
npx hyperframes render --fps 24 --output cinematic.mp4
npx hyperframes render --fps 60 --output smooth.mp4
```

## Deterministic Rendering: The Film Negative That Never Changes 🎞️

The render pipeline is seek-driven, not clock-driven. For every frame N:

```
frame = floor(time × fps)
time  = frame / fps
```

The engine calls `timeline.seek(time)` on every GSAP timeline, seeks every media element to that exact position, then calls Chrome's `HeadlessExperimental.beginFrame` API to capture the pixel buffer. No wall clock. No `requestAnimationFrame`. No drift.

Same HTML. Same assets. Same Chrome. **Same output** — every time, on every machine, in Docker mode.

```bash
# Prove it: render twice and compare hashes
npx hyperframes render --docker --output run1.mp4
npx hyperframes render --docker --output run2.mp4

md5 run1.mp4 run2.mp4
# MD5 (run1.mp4) = a3f9c2d1e8b04f77...
# MD5 (run2.mp4) = a3f9c2d1e8b04f77...   ← identical
```

This property makes HyperFrames suitable for CI/CD video generation — you can test rendered output the same way you test software.

## CI/CD Integration: Automated Video Production 🤖

HyperFrames CLI is fully non-interactive by default — every input is a flag, every output is plain text, failures exit with non-zero codes. It is designed to be driven by automation.

### GitHub Actions workflow

```yaml
# .github/workflows/render-video.yml
name: Render Marketing Video

on:
  push:
    paths:
      - "my-production/**.html"
      - "my-production/assets/**"

jobs:
  render:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js 22
        uses: actions/setup-node@v4
        with:
          node-version: "22"

      - name: Install FFmpeg
        run: sudo apt-get install -y ffmpeg

      - name: Install Docker (already available on ubuntu-latest)
        run: docker --version

      - name: Lint composition
        working-directory: my-production
        run: npx hyperframes lint

      - name: Render video (Docker mode for reproducibility)
        working-directory: my-production
        run: |
          npx hyperframes render \
            --docker \
            --quality high \
            --output output.mp4 \
            --quiet

      - name: Upload rendered video
        uses: actions/upload-artifact@v4
        with:
          name: rendered-video
          path: my-production/output.mp4
          retention-days: 30
```

### Batch rendering multiple compositions

```bash
#!/bin/bash
# render-all.sh — render every composition in the project

set -e   # exit on first error

for dir in ./compositions/*/; do
  name=$(basename "$dir")
  echo "Rendering: $name"

  npx hyperframes render \
    --docker \
    --quality standard \
    --output "renders/${name}.mp4" \
    --quiet \
    --workers 2

  echo "Done: renders/${name}.mp4"
done

echo "All renders complete."
```

## The Benchmark Command: Know Your Machine 🏎️

```bash
npx hyperframes benchmark
```

HyperFrames runs a standard test composition and reports:

```
Running benchmark (30fps, 1920x1080, 10s = 300 frames)...

  Workers: 4
  Capture time: 12.3s   (24.4 fps capture rate)
  Encode time:  2.1s
  Total:        14.4s

Recommended settings for this machine:
  --workers 4   (optimal for 8-core CPU)
  GPU:           available (VideoToolbox) — add --gpu for 40% faster encode
```

Run the benchmark when you first set up a machine to find optimal worker counts and confirm GPU is available.

In **Episode 8**, the AI script writer joins set. The Catalog of 50+ ready-made blocks, the skills system that teaches AI agents to write correct compositions, and the complete agent-driven video production workflow.

**🔗 Resources**

- **Rendering Guide**: [hyperframes.heygen.com/guides/rendering](https://hyperframes.heygen.com/guides/rendering)
- **Deterministic Rendering**: [hyperframes.heygen.com/concepts/determinism](https://hyperframes.heygen.com/concepts/determinism)
- **CLI Reference**: [hyperframes.heygen.com/packages/cli](https://hyperframes.heygen.com/packages/cli)
- **HDR Rendering**: [hyperframes.heygen.com/guides/hdr](https://hyperframes.heygen.com/guides/hdr)

*🎬 Sound, Camera, Action with HyperFrames Series — a film director's guide to rendering videos with HTML and JavaScript. Open-source. No React required.*