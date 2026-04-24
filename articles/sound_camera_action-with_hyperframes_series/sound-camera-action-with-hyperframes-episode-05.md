---
title: "Sound, Camera, Action! 🎬 Ep.5"
published: false
description: "Episode 5: The editor assembles the film. Real video B-roll, audio score, volume mixing, media trimming, and the Hollywood technique that makes overlays work: transparent ProRes 4444 MOV renders. HyperFrames handles the compositing pipeline — you write the cuts."
tags: [javascript, html, video, ffmpeg]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/sound_camera_action_with_hyperframes_series/sound-camera-action-with-hyperframes-episode-05.png"
series: "Sound, Camera, Action with HyperFrames Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 5: The Cutting Room

> "Editing is not cutting film. Editing is creating a new reality from pieces of other realities."— Walter Murch

## The Editor's Domain ✂️

After the shoot, the director hands the raw footage to the editor. The editor sits in the cutting room with reels of B-roll, the recorded score, the voice-over takes, and the visual effects output. The editor assembles the film: select the right take of each shot, trim the heads and tails, mix the audio levels so the score supports the narration without drowning it, and drop in the VFX overlays in the right places.

In HyperFrames, this is all HTML. `<video>` clips for footage, `<audio>` for the mix, `data-media-start` for trimming, `data-volume` for levels. And for the overlays — the lower thirds, the subscribe buttons, the animated text that floats above footage — there is a dedicated render format: **transparent MOV (ProRes 4444)**, the industry standard for compositing.

## 🗂️ SIPOC — The Cutting Room

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| Footage library | Video files in assets/ (mp4, mov, webm) | Reference with <video src="..."> + data-media-start to trim | B-roll and A-roll at the right in/out points in the timeline | The render engine — seeks each media element per frame |
| Audio library | Music, voice-over, SFX files in assets/ | Reference with <audio src="..."> + data-volume to mix | A balanced multi-track audio mix baked into the MP4 | The final video — levels match the director's intent |
| Overlay compositions | A separate index.html for the overlay (no background) | npx hyperframes render --format mov | A .mov ProRes 4444 file with transparent background | CapCut, Final Cut, Premiere, DaVinci — drag it onto a track above footage |
| You (the editor) | Timing decisions for every cut | Edit data-start, data-duration, data-media-start in HTML | A complete multi-clip timeline | The render pipeline |

## B-Roll: Placing Video Clips on the Timeline 🎥

A `<video>` clip is declared with the same `data-*` attributes as any other timed element, with a few video-specific additions:

```html
<!-- Full-frame B-roll: city flyover -->
<video id="city-flyover"
       class="clip"
       data-start="0"
       data-duration="8"
       data-track-index="0"
       data-has-audio="false"
       src="assets/city.mp4"
       muted
       playsinline
       style="position: absolute; inset: 0;
              width: 1920px; height: 1080px;
              object-fit: cover;">
</video>
```

Key points:

- `muted` is **required** — browsers require it for autoplay. Audio from video is handled by `data-has-audio`, not the HTML `muted` attribute.
- `playsinline` prevents mobile browsers from going fullscreen.
- `data-duration` is **optional** for `<video>` — it defaults to the source file's duration. Provide it if you want to trim the clip shorter than the source.
- `data-has-audio="true"` tells the engine to include the video's audio track in the render.

## Trimming Footage: `data-media-start` 🎞️

`data-media-start` is the in-point: how many seconds into the source file the clip begins playing. This is the editor's trim handle:

```html
<!-- Source: a 2-minute interview.mp4
     We want 20 seconds of footage starting at the 45-second mark -->
<video id="interview-clip"
       class="clip"
       data-start="3"
       data-duration="20"
       data-track-index="1"
       data-media-start="45"
       data-has-audio="true"
       src="assets/interview.mp4"
       muted playsinline
       style="position: absolute; inset: 0;
              width: 1920px; height: 1080px;
              object-fit: cover;">
</video>
```

This places the clip at second 3 in the composition, plays the source from second 45, and runs for 20 seconds. The editor has trimmed both the head (44 seconds discarded) and the tail (the rest after 65 seconds discarded).

## Building a Multi-Cut Edit: The Interview Sequence 🎬

Three cuts from a single interview, separated by B-roll inserts:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body, html { margin: 0; padding: 0; background: #000; }
    [data-composition-id="interview-edit"] {
      width: 1920px; height: 1080px;
      overflow: hidden; position: relative;
    }
    .fullframe {
      position: absolute; inset: 0;
      width: 1920px; height: 1080px;
      object-fit: cover;
    }
    #lower-third {
      position: absolute;
      bottom: 120px; left: 0;
      padding: 22px 60px 22px 60px;
      background: linear-gradient(90deg, rgba(0,80,200,0.92) 0%, transparent 100%);
    }
    #lt-name { font-size: 38px; font-weight: 700; color: #fff; margin: 0; }
    #lt-title { font-size: 26px; color: #cde; margin: 4px 0 0; }
  </style>
</head>
<body>
  <div id="root"
       data-composition-id="interview-edit"
       data-start="0"
       data-width="1920"
       data-height="1080">

    <!-- ── CUT 1: Interview A-roll (0→10s, from 0:20 in source) ── -->
    <video id="aroll-1"
           class="clip fullframe"
           data-start="0"
           data-duration="10"
           data-track-index="0"
           data-media-start="20"
           data-has-audio="true"
           src="assets/interview.mp4"
           muted playsinline>
    </video>

    <!-- ── B-ROLL INSERT over cut 1 (2→6s), visually over A-roll ── -->
    <video id="broll-insert"
           class="clip fullframe"
           data-start="2"
           data-duration="4"
           data-track-index="1"
           data-has-audio="false"
           src="assets/broll-office.mp4"
           muted playsinline>
    </video>

    <!-- ── LOWER THIRD: appears at 0.5s, lasts 5s ── -->
    <div id="lower-third"
         class="clip"
         data-start="0.5"
         data-duration="5"
         data-track-index="2">
      <p id="lt-name">Jane Smith</p>
      <p id="lt-title">Head of Product, Acme Corp</p>
    </div>

    <!-- ── CUT 2: Interview A-roll continues (10→18s, from 0:35 in source) ── -->
    <video id="aroll-2"
           class="clip fullframe"
           data-start="aroll-1"
           data-duration="8"
           data-track-index="0"
           data-media-start="35"
           data-has-audio="true"
           src="assets/interview.mp4"
           muted playsinline>
    </video>

    <!-- ── CUT 3: Interview close (18→26s, from 1:02 in source) ── -->
    <video id="aroll-3"
           class="clip fullframe"
           data-start="aroll-2"
           data-duration="8"
           data-track-index="0"
           data-media-start="62"
           data-has-audio="true"
           src="assets/interview.mp4"
           muted playsinline>
    </video>

    <!-- ── BACKGROUND MUSIC: under full edit at 25% ── -->
    <audio id="score"
           class="clip"
           data-start="0"
           data-duration="26"
           data-track-index="5"
           data-volume="0.25"
           src="assets/score.wav">
    </audio>

  </div>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });

    // Lower third slides in from left at t=0.5
    tl.from("#lower-third", { x: -700, duration: 0.5, ease: "power3.out" }, 0.5);
    // Lower third slides out at t=5.5
    tl.to("#lower-third",   { x: -700, duration: 0.4, ease: "power3.in"  }, 5.5);

    // B-roll insert fades in
    tl.from("#broll-insert", { opacity: 0, duration: 0.4 }, 2.0);
    tl.to("#broll-insert",   { opacity: 0, duration: 0.4 }, 5.6);

    // Final fade-out
    tl.to([".clip"], { opacity: 0, duration: 0.8 }, 25.2);

    // Extend to 26s
    tl.set({}, {}, 26);

    window.__timelines = window.__timelines || {};
    window.__timelines["interview-edit"] = tl;
  </script>
</body>
</html>
```

## Audio Mixing: The Sound Stage 🎵

Every `<audio>` and `<video>` element with `data-has-audio="true"` contributes to the final audio mix. Balance them with `data-volume`:

```html
<!-- Music bed at 25% — present but never dominant -->
<audio id="music" data-volume="0.25" src="assets/score.wav" ...></audio>

<!-- Interview A-roll audio at full volume — the main signal -->
<video id="aroll"  data-volume="1.0" data-has-audio="true" src="assets/interview.mp4" ...></video>

<!-- Sound effect hit at 70% -->
<audio id="sfx"   data-volume="0.7" src="assets/whoosh.wav" ...></audio>

<!-- Ambient room tone at 15% — subtle texture -->
<audio id="room"  data-volume="0.15" src="assets/room-tone.wav" ...></audio>
```

**Practical mixing guide for video:**

| Track type | Suggested data-volume |
| --- | --- |
| Voice-over / dialogue | 0.9–1.0 |
| Interview A-roll | 1.0 |
| Background music | 0.2–0.35 |
| Sound effects | 0.5–0.8 |
| Ambient / room tone | 0.1–0.2 |
| Music during VO | Drop to 0.1–0.15 |

There is no per-clip envelope or fade curve on volume — volume is constant for the clip's duration. To simulate a music fade-out, use a GSAP tween on the element's CSS property (if supported by the audio adapter). For most use cases, a carefully chosen `data-volume` value is sufficient.

## Transparent Video: The Greenscreen Technique 🟩

Hollywood composites actors filmed against a green screen over separate backgrounds. The result: the actor appears in a location they were never physically in.

HyperFrames has the digital equivalent: **transparent MOV renders**. Render an overlay composition (lower thirds, animated subscribe buttons, text cards) as a ProRes 4444 MOV file with an alpha channel. The transparent areas are literally transparent in the output. Drop it onto a track above your footage in CapCut, Final Cut, Premiere, or DaVinci Resolve, and it composites perfectly.

### Authoring a transparent composition

A transparent composition has no background. The `html`, `body`, and the root composition div must all have no `background` property set:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    /* Critical: do NOT set background on html, body, or root */
    body, html { margin: 0; padding: 0; }

    [data-composition-id="lower-third-overlay"] {
      position: relative;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      /* No background here — stays transparent */
    }

    #lt-bar {
      position: absolute;
      bottom: 120px; left: 0; right: 0;
      height: 110px;
      background: linear-gradient(90deg, #003399 0%, rgba(0,51,153,0) 70%);
    }
    #lt-name  { position: absolute; bottom: 160px; left: 60px;
                font-size: 36px; font-weight: 700; color: #fff; font-family: Arial; }
    #lt-title { position: absolute; bottom: 126px; left: 60px;
                font-size: 24px; color: #c8d8ff; font-family: Arial; }
  </style>
</head>
<body>
  <!-- ROOT: no background — transparent -->
  <div id="root"
       data-composition-id="lower-third-overlay"
       data-start="0"
       data-width="1920"
       data-height="1080">

    <div  id="lt-bar"   class="clip" data-start="0" data-duration="6" data-track-index="0"></div>
    <p    id="lt-name"  class="clip" data-start="0" data-duration="6" data-track-index="1">Jane Smith</p>
    <p    id="lt-title" class="clip" data-start="0" data-duration="6" data-track-index="2">Head of Product, Acme Corp</p>

  </div>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });

    // Slide in from left
    tl.from(["#lt-bar", "#lt-name", "#lt-title"], {
      x: -900, duration: 0.6, stagger: 0.06, ease: "power3.out"
    }, 0.2);

    // Slide out to left at t=5.2
    tl.to(["#lt-bar", "#lt-name", "#lt-title"], {
      x: -900, duration: 0.5, stagger: 0.04, ease: "power3.in"
    }, 5.2);

    tl.set({}, {}, 6);
    window.__timelines = window.__timelines || {};
    window.__timelines["lower-third-overlay"] = tl;
  </script>
</body>
</html>
```

### Render as transparent MOV

```bash
# --format mov → ProRes 4444 with alpha channel
npx hyperframes render --format mov --output lower-third.mov
```

```
✔ Capturing frames (PNG + alpha)... 180/180
✔ Encoding ProRes 4444...
✔ lower-third.mov (1920x1080, 6.0s, ~24 MB)
```

The resulting `.mov` file is large (ProRes is a lossless intermediate codec, not a delivery codec). That is expected — the same trade-off every professional post-production pipeline makes.

### Format comparison for overlays

| Format | Transparency | Use in video editors | File size |
| --- | --- | --- | --- |
| MOV (ProRes 4444) | Yes ✓ | CapCut, Final Cut, Premiere, DaVinci, After Effects | Large |
| WebM (VP9 alpha) | Yes ✓ | Chrome browser only | Small |
| MP4 (H.264) | No | All editors | Small |

Always use MOV for professional overlay work. WebM's alpha channel is only visible in Chromium-based browsers — video editors ignore it and render transparency as black.

## Verifying Transparency ✅

```bash
# 1. Render a WebM version for quick browser check
npx hyperframes render --format webm --output lower-third-check.webm

# 2. Open in Chrome — transparent areas show as checkerboard
# 3. Satisfied? The MOV version is what you deliver to the editor.
```

In **Episode 6**, the second unit starts work. Nested compositions — separate HTML files that load inside the main composition — let you organise complex projects into reusable, independently editable scenes.

**🔗 Resources**

- **Data Attributes — media**: [hyperframes.heygen.com/concepts/data-attributes#media-attributes](https://hyperframes.heygen.com/concepts/data-attributes#media-attributes)
- **Rendering — Transparent Video**: [hyperframes.heygen.com/guides/rendering#transparent-video](https://hyperframes.heygen.com/guides/rendering#transparent-video)
- **HTML Schema Reference**: [hyperframes.heygen.com/reference/html-schema](https://hyperframes.heygen.com/reference/html-schema)

*🎬 Sound, Camera, Action with HyperFrames Series — a film director's guide to rendering videos with HTML and JavaScript. Open-source. No React required.*