---
title: "Sound, Camera, Action! 🎬 Ep.1"
part: 1
published: false
description: "Episode 1: Every great Hollywood film starts with a director who has a vision and a crew who knows the tools. HyperFrames turns HTML into deterministic video — no React, no proprietary DSL, just the web stack you already know. Meet the studio."
tags: [javascript, html, video, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/sound_camera_action_with_hyperframes_series/sound-camer-action-with-hyperframes-episode-01.png"
series: "Sound, Camera, Action with HyperFrames Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 1: Lights, Camera, HyperFrames!

> *“Every frame is a painting. Every painting tells a story.”*
> — Anonymous film director

-----

## The Director Takes the Chair 🎬

Walk onto any Hollywood set and you will find a director with a clapperboard, a vision, and a crew that translates that vision into frames. The director does not build the camera. The director does not mix the sound in post. The director writes — or at least directs — the story, and the pipeline takes it from there.

**HyperFrames** is that pipeline. You write HTML. It renders video.

Not “sort of HTML” with a build step and a bundler and a framework you need to learn. Plain HTML — the language every web developer already speaks. `<div>`, `<video>`, `<audio>`, `<img>`, a handful of `data-*` attributes, and a GSAP animation timeline. The CLI captures frame by frame using headless Chrome and encodes the result with FFmpeg into a final MP4.

HyperFrames is the studio lot. You are the director. This series is your craft school.

-----

## 🗂️ SIPOC — The Studio Opens

|**Suppliers**       |**Inputs**                                                  |**Process**                                                                |**Outputs**                                                     |**Customers**                                  |
|--------------------|------------------------------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------|-----------------------------------------------|
|You (the director)  |An idea for a video — title card, product promo, social reel|Write `index.html` with composition structure + `data-*` attributes        |A valid HyperFrames composition                                 |The render engine — reads HTML, produces frames|
|HyperFrames CLI     |The composition HTML file + assets                          |`npx hyperframes render` → headless Chrome captures frames → FFmpeg encodes|`output.mp4` — deterministic, frame-perfect video               |Any media player, video editor, social platform|
|Node.js 22+ + FFmpeg|Runtime dependencies                                        |Scaffold, preview, lint, render — all via `npx hyperframes`                |Developer experience: live preview, error messages, health check|You — iteration is fast, errors are clear      |

-----

## Why Not Remotion? 🤔

HyperFrames was built by the HeyGen team after years running Remotion in production pipelines. The honest comparison:

|                     |HyperFrames                                |Remotion                        |
|---------------------|-------------------------------------------|--------------------------------|
|Authoring            |HTML + CSS + GSAP                          |React (TSX)                     |
|Build step           |None — `index.html` plays as-is            |Required (bundler)              |
|GSAP / Anime.js      |Frame-accurate (seek-driven)               |Wall-clock drift during render  |
|Paste any web page   |Yes — the DOM is the composition           |Rewrite as JSX first            |
|AI agents            |Native — HTML is what LLMs know best       |React surface is a smaller slice|
|Visual editor        |Natural — editor and renderer share the DOM|Source is code + build step     |
|Distributed rendering|Single machine today                       |Remotion Lambda (mature)        |
|Licence              |Apache 2.0 (free)                          |Commercial                      |

The critical difference: GSAP timelines in Remotion play at wall-clock speed during render, so animations race through before all frames are captured. HyperFrames *pauses* GSAP and *seeks* it to `frame / fps` before capturing each frame. Same animation code, frame-perfect output.

The other reason: every LLM was trained on more plain HTML than on React-specific video composition patterns. Ask an agent to write a HyperFrames composition and it reaches for a wider creative range. Ask it for Remotion and it spends tokens learning framework rules before it can be creative.

-----

## The Hollywood Metaphor 🎥

Before writing a line of code, understand the metaphor this series runs on. Every HyperFrames concept maps to a film production concept:

|Hollywood film production|HyperFrames                                                         |
|-------------------------|--------------------------------------------------------------------|
|The screenplay           |The HTML composition file (`index.html`)                            |
|Scene directions         |`data-*` attributes — when, how long, which track                   |
|The film timeline        |The composition timeline                                            |
|A shot / scene           |A clip element (`<video>`, `<img>`, `<div class="clip">`, `<audio>`)|
|Soundtrack               |`<audio>` clip with `data-volume`                                   |
|Calling “Action!”        |`npx hyperframes render`                                            |
|Dailies / rushes review  |`npx hyperframes preview`                                           |
|The cutting room         |Editing timings in `index.html`                                     |
|Special effects          |GSAP animations                                                     |
|Second unit              |Nested sub-compositions                                             |
|Track marks on the floor |`data-track-index` — clips on the same track cannot overlap         |
|Post-production grading  |Render flags: `--quality`, `--crf`, `--hdr`                         |
|Studio vs. location      |Local mode vs. Docker mode                                          |
|The continuity supervisor|Relative timing — `data-start="clip-id"`                            |
|Transparent overlay      |`--format mov` (ProRes 4444 transparency)                           |
|The director’s cut       |The final `output.mp4`                                              |
|AI script writer         |AI agent writing compositions via `/hyperframes` skill              |

By the end of Episode 8, you will have walked every foot of the studio lot.

-----

## Prerequisites 🔧

```bash
# Check Node.js version — must be 22 or later
node --version
# v22.x.x

# Install FFmpeg (required for rendering)
# macOS:
brew install ffmpeg

# Ubuntu / Debian:
sudo apt install ffmpeg

# Windows: download from ffmpeg.org

# Verify
ffmpeg -version
# ffmpeg version 7.x ...
```

-----

## Your First Composition: The Title Card 🎬

Every Hollywood film opens with a title card. So will ours.

### Scaffold the project

```bash
npx hyperframes init my-first-film
cd my-first-film
```

The wizard runs. For our purposes, choose **blank** to start from a clean slate:

```bash
# Non-interactive (skip the wizard)
npx hyperframes init my-first-film --non-interactive --example blank
cd my-first-film
```

The scaffolded structure:

```
my-first-film/
├── meta.json         ← project metadata
├── index.html        ← the screenplay (your composition)
├── compositions/     ← sub-compositions (nested scenes)
└── assets/           ← video, audio, image files
```

### Write the title card

Open `index.html` and replace its contents:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body, html { margin: 0; padding: 0; background: #0a0a0a; }

    [data-composition-id="title-card"] {
      position: relative;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      background: #0a0a0a;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: "Georgia", serif;
    }

    #title {
      font-size: 96px;
      color: #f0e6c8;   /* warm golden-white */
      text-align: center;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    #subtitle {
      position: absolute;
      bottom: 180px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 32px;
      color: #888;
      letter-spacing: 0.3em;
      text-transform: uppercase;
    }
  </style>
</head>
<body>
  <!-- ROOT COMPOSITION: the director's shot sheet -->
  <div id="root"
       data-composition-id="title-card"
       data-start="0"
       data-width="1920"
       data-height="1080">

    <!-- CLIP 1: the main title — appears for 5 seconds -->
    <h1 id="title"
        class="clip"
        data-start="0"
        data-duration="5"
        data-track-index="0">
      My First Film
    </h1>

    <!-- CLIP 2: subtitle — appears after 0.5s, lasts 4s -->
    <p id="subtitle"
       class="clip"
       data-start="0.5"
       data-duration="4"
       data-track-index="1">
      A HyperFrames Production
    </p>

  </div>

  <!-- GSAP: the special effects department -->
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    // Rule 1: Always create timelines with { paused: true }
    // The framework controls playback — never call tl.play()
    const tl = gsap.timeline({ paused: true });

    // Animate the title: fade up from below
    tl.from("#title",    { opacity: 0, y: 60,  duration: 1.2 }, 0);
    // Animate the subtitle: fade in slightly later
    tl.from("#subtitle", { opacity: 0, y: 20,  duration: 0.8 }, 0.4);
    // Fade everything out at the end
    tl.to("#title",    { opacity: 0, duration: 0.8 }, 4.0);
    tl.to("#subtitle", { opacity: 0, duration: 0.8 }, 4.0);

    // Rule 2: Register the timeline with the composition ID as the key
    window.__timelines = window.__timelines || {};
    window.__timelines["title-card"] = tl;
  </script>

</body>
</html>
```

### Preview in the browser

```bash
npx hyperframes preview
```

The dev server opens your composition in the browser. You see the title fading up, the subtitle appearing, everything fading out. The preview is interactive — a scrubber bar lets you seek to any point in the timeline.

Edit `index.html`, save, and the preview updates instantly. No build step. No compilation. The dailies review is live.

### Run the diagnostics check

```bash
npx hyperframes doctor
```

```
✓ Node.js    v22.x
✓ FFmpeg      7.x
✓ FFprobe     7.x
✓ Chrome      (bundled)
✓ Docker      available
```

### Render to MP4

```bash
npx hyperframes render --output title-card.mp4
```

```
✔ Capturing frames... 150/150
✔ Encoding MP4...
✔ title-card.mp4 (1920x1080, 5.0s, 30fps)
```

Open `title-card.mp4`. There it is — your director’s cut. Frame-perfect. Deterministic. The same HTML will produce the same MP4 every single time.

-----

## The Three Rules Every Director Follows 📋

These three rules underpin every composition you will ever write in HyperFrames. Violate one and the render breaks. Memorise them now:

**Rule 1: The root element must identify itself.**
Every composition needs a root `<div>` with `data-composition-id`, `data-width`, and `data-height`. Without these, the engine cannot find the composition.

**Rule 2: Timed elements must be dressed for the timeline.**
Any element that appears and disappears during the video needs `class="clip"`, `data-start`, `data-duration`, and `data-track-index`. These are the director’s marks on the floor.

**Rule 3: GSAP timelines must be paused and registered.**
Create all timelines with `{ paused: true }` and register them on `window.__timelines["your-composition-id"]`. The engine seeks the timeline frame by frame — it owns playback, not you.

-----

## The Series Map: Eight Episodes 🗺️

|#|Episode                      |Film metaphor             |HyperFrames concept                                           |
|-|-----------------------------|--------------------------|--------------------------------------------------------------|
|1|*This one* — The Studio Opens|Lights, camera!           |Install, first composition, three rules                       |
|2|The Screenplay               |Writing the script        |HTML anatomy, `data-*` attributes, clip types                 |
|3|Casting and Timing           |Track marks and continuity|Track indices, relative timing, gaps/overlaps                 |
|4|Special Effects              |The VFX department        |GSAP animation, supported properties, timeline registration   |
|5|B-Roll and the Cutting Room  |Media compositing         |Video, audio, `data-volume`, transparent overlays             |
|6|Second Unit                  |Parallel shooting         |Nested compositions, `data-composition-src`, project structure|
|7|Rolling!                     |Final render              |Render flags, Docker, quality, GPU, workers                   |
|8|The AI Script Writer         |AI on set                 |Skills, agent workflow, the Catalog of 50+ blocks             |

In **Episode 2**, the screenplay. We dissect the HTML composition structure line by line — every attribute, every clip type, the complete grammar of the script.

-----

**🔗 Resources**

- **HyperFrames home**: [hyperframes.heygen.com](https://hyperframes.heygen.com)
- **Introduction**: [hyperframes.heygen.com/introduction](https://hyperframes.heygen.com/introduction)
- **Quickstart**: [hyperframes.heygen.com/quickstart](https://hyperframes.heygen.com/quickstart)
- **GitHub**: [github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)

-----

*🎬 Sound, Camera, Action with HyperFrames Series — a film director’s guide to rendering videos with HTML and JavaScript. Open-source. No React required.*
