---
title: "Sound, Camera, Action! 🎬 Ep.3"
published: false
description: "Episode 3: The continuity supervisor ensures every actor enters and exits on cue. HyperFrames' relative timing system — referencing clip IDs instead of absolute seconds — keeps your composition flexible. Change one scene's duration and the whole film reflows automatically."
tags: [javascript, html, video, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/hyperframessound_camera_action_with_hyperframes_series/sound-camera-action-with-hyperframes-episode-03.png"
series: "Sound, Camera, Action with HyperFrames Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: Casting and Timing

> "The continuity supervisor's job is to make sure that when the camera cuts from scene 12 to scene 13, the actor's coffee cup is in the right hand. Every frame must follow from the last."

## The Continuity Problem ⏱️

Imagine you have written a 30-second product video. Scene 1 is 8 seconds. Scene 2 starts at second 8, lasts 7 seconds. Scene 3 starts at second 15, lasts 10 seconds. Scene 4 starts at second 25.

Then the client asks you to extend Scene 1 by 3 seconds. Suddenly Scene 2 starts at 8 — still — but it should start at 11. And Scene 3, 4, 5 all need to shift forward by 3 seconds. You open the file and edit every `data-start` value manually. For a complex composition, this is exhausting and error-prone.

The continuity supervisor on a Hollywood set prevents exactly this problem by maintaining a shot list where each scene refers to the previous one: Scene 2 starts after Scene 1, Scene 3 starts after Scene 2, and so on. If Scene 1 runs longer, everything else automatically adjusts.

HyperFrames has the same mechanism: **relative timing**.

## 🗂️ SIPOC — The Continuity Department

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the director) | A multi-scene composition where scenes chain sequentially | Write data-start="clip-id" to reference another clip's end time | Resolved absolute timings computed by the framework at render time | The render engine — receives resolved timings for frame-accurate capture |
| The timing resolver | Chain of data-start references | Topological sort → resolve each reference to an absolute second | Every clip's absolute data-start in seconds | The GSAP adapter and media playback engine |
| You (editing) | A change to one scene's data-duration | Framework re-resolves all downstream references automatically | All downstream clips shift without any manual edits | You — compositional flexibility without maintaining absolute seconds |

## Relative Timing: The Chain Reference 🔗

Instead of writing absolute seconds, reference another clip's `id` in `data-start`. The framework interprets this as: "start when that clip ends."

```html
<!-- Scene 1: intro shot (absolute — always starts at 0) -->
<video id="intro"
       class="clip"
       data-start="0"
       data-duration="8"
       data-track-index="0"
       src="assets/intro.mp4" muted playsinline>
</video>

<!-- Scene 2: starts when 'intro' ends (resolves to second 8) -->
<video id="main"
       class="clip"
       data-start="intro"
       data-duration="12"
       data-track-index="0"
       src="assets/main.mp4" muted playsinline>
</video>

<!-- Scene 3: starts when 'main' ends (resolves to second 20) -->
<video id="outro"
       class="clip"
       data-start="main"
       data-duration="5"
       data-track-index="0"
       src="assets/outro.mp4" muted playsinline>
</video>
```

Now if the client extends the intro from 8 to 11 seconds — just change `data-duration="11"` on `#intro`. `main` resolves to second 11, `outro` resolves to second 23. No other attributes to touch.

## Gaps and Overlaps: The Director's Pauses 🎬

Sometimes you want a gap between scenes. Sometimes you want a deliberate overlap — like a crossfade transition where one scene begins before the previous has fully ended.

Add `+ N` or `- N` after the clip ID:

```html
<!-- 2-second BLACK GAP between intro and main -->
<video id="main"
       class="clip"
       data-start="intro + 2"
       data-duration="12"
       data-track-index="0"
       src="assets/main.mp4" muted playsinline>
</video>

<!-- Scene B overlaps Scene A by 0.5 seconds (for a crossfade) -->
<!-- NOTE: overlapping clips must be on DIFFERENT tracks -->
<video id="scene-a"
       class="clip"
       data-start="0"
       data-duration="10"
       data-track-index="0"
       src="assets/scene-a.mp4" muted playsinline>
</video>
<video id="scene-b"
       class="clip"
       data-start="scene-a - 0.5"
       data-duration="8"
       data-track-index="1"
       src="assets/scene-b.mp4" muted playsinline>
</video>
```

The overlap is on **Track 1** for Scene B while Scene A is on **Track 0**. They can coexist in time because they are on separate tracks. Both are visible during the 0.5-second overlap — one fading out (animatable with GSAP), one fading in.

## Track Indices: Floor Marks and Z-Order 🎭

Track index is the director's floor mark for each actor — where they stand spatially and temporally. Two rules govern it:

**Rule 1: Clips on the same track cannot overlap in time.**This is enforced by the linter. If two clips on Track 0 have overlapping time ranges, you get an error. The resolution is always to move one to a different track.

**Rule 2: Higher track index = visually in front.**Track 3 sits on top of Track 2, which sits on top of Track 1, which sits on top of Track 0. This is the Z-order hierarchy.

### Designing a typical multi-track composition

```
Track 0:  Background video / solid colour layer        (lowest, behind everything)
Track 1:  Secondary video / image overlay
Track 2:  Text elements, cards, lower thirds
Track 3:  Logo, watermark, persistent overlay          (always in front)
Track 4+: Sound effects, music (audio — invisible)
```

### A practical multi-track layout

```html
<!-- TRACK 0: Background video (full frame) -->
<video id="bg"
       class="clip"
       data-start="0"
       data-duration="15"
       data-track-index="0"
       src="assets/background.mp4" muted playsinline
       style="position:absolute; inset:0; width:1920px; height:1080px; object-fit:cover;">
</video>

<!-- TRACK 1: Product shot overlay (right half of frame) -->
<img id="product"
     class="clip"
     data-start="2"
     data-duration="12"
     data-track-index="1"
     src="assets/product.png"
     style="position:absolute; right:100px; top:50%; transform:translateY(-50%); height:600px;" />

<!-- TRACK 2: Lower third text bar -->
<div id="lower-third"
     class="clip"
     data-start="3"
     data-duration="5"
     data-track-index="2"
     style="position:absolute; bottom:120px; left:0; right:0; padding:20px 60px; background:rgba(0,0,0,0.7);">
  <p style="margin:0; font-size:32px; color:white;">John Smith — CEO, Acme Corp</p>
</div>

<!-- TRACK 3: Logo watermark (always visible) -->
<img id="logo"
     class="clip"
     data-start="0"
     data-duration="15"
     data-track-index="3"
     src="assets/logo.png"
     style="position:absolute; top:40px; right:60px; height:60px; opacity:0.8;" />

<!-- TRACK 4: Background music -->
<audio id="music"
       class="clip"
       data-start="0"
       data-duration="15"
       data-track-index="4"
       data-volume="0.3"
       src="assets/music.wav">
</audio>

<!-- TRACK 5: Voice-over -->
<audio id="vo"
       class="clip"
       data-start="2"
       data-duration="10"
       data-track-index="5"
       data-volume="1.0"
       src="assets/voiceover.mp3">
</audio>
```

## A Full Sequential Composition: The Three-Act Video 🎬

Let us put it all together — a three-act product video with relative timing, gaps, and a crossfade between acts:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body, html { margin: 0; padding: 0; background: #000; }
    [data-composition-id="three-act"] {
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      position: relative;
    }
    /* All clips use absolute positioning */
    .clip { position: absolute; inset: 0; }
    video { width: 1920px; height: 1080px; object-fit: cover; }

    #act1-title, #act2-title, #act3-title {
      display: flex; align-items: center; justify-content: center;
      font-family: "Georgia", serif;
      font-size: 80px; color: white;
      background: rgba(0,0,0,0.5);
    }
  </style>
</head>
<body>
  <div id="root"
       data-composition-id="three-act"
       data-start="0"
       data-width="1920"
       data-height="1080">

    <!-- ═══════════════════════════════════════════════
         ACT 1: The Problem (8 seconds, starts at 0)
         ═══════════════════════════════════════════════ -->
    <video id="act1-video"
           class="clip"
           data-start="0"
           data-duration="8"
           data-track-index="0"
           src="assets/problem.mp4" muted playsinline>
    </video>
    <div id="act1-title"
         class="clip"
         data-start="0.5"
         data-duration="6.5"
         data-track-index="1">
      The Problem
    </div>

    <!-- ═══════════════════════════════════════════════
         TRANSITION: crossfade — Act 2 starts 0.5s before Act 1 ends
         ═══════════════════════════════════════════════ -->

    <!-- ACT 2: The Solution (10 seconds, starts when act1-video ends - 0.5s) -->
    <video id="act2-video"
           class="clip"
           data-start="act1-video - 0.5"
           data-duration="10"
           data-track-index="2"
           src="assets/solution.mp4" muted playsinline>
    </video>
    <div id="act2-title"
         class="clip"
         data-start="act1-video + 0.5"
         data-duration="8"
         data-track-index="3">
      The Solution
    </div>

    <!-- ═══════════════════════════════════════════════
         ACT 3: The Result (7 seconds, starts 1s after Act 2 ends — a deliberate gap)
         ═══════════════════════════════════════════════ -->
    <video id="act3-video"
           class="clip"
           data-start="act2-video + 1"
           data-duration="7"
           data-track-index="0"
           src="assets/result.mp4" muted playsinline>
    </video>
    <div id="act3-title"
         class="clip"
         data-start="act2-video + 1.5"
         data-duration="5.5"
         data-track-index="1">
      The Result
    </div>

    <!-- MUSIC: covers entire composition -->
    <audio id="music"
           class="clip"
           data-start="0"
           data-duration="26"
           data-track-index="6"
           data-volume="0.25"
           src="assets/score.wav">
    </audio>

  </div>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    // Resolved timings for reference (the framework calculates these, we don't):
    // act1-video: 0 → 8
    // act2-video: 7.5 → 17.5   (8 - 0.5)
    // act3-video: 18.5 → 25.5  (17.5 + 1)
    // Total composition: ~25.5s

    const tl = gsap.timeline({ paused: true });

    // Act 1 intro
    tl.from("#act1-title", { opacity: 0, y: 30, duration: 0.8 }, 0.5);
    tl.to("#act1-title",   { opacity: 0,         duration: 0.5 }, 7.0);

    // Crossfade between Act 1 and Act 2:
    // Act 2 video starts at 7.5, so we fade act1-video out and act2-video in
    tl.to("#act1-video",   { opacity: 0,         duration: 0.5 }, 7.5);
    tl.from("#act2-video", { opacity: 0,         duration: 0.5 }, 7.5);

    // Act 2 title
    tl.from("#act2-title", { opacity: 0, y: 30, duration: 0.8 }, 8.5);
    tl.to("#act2-title",   { opacity: 0,         duration: 0.5 }, 16.5);

    // Black gap between Act 2 and Act 3 (17.5 → 18.5 = 1 second black)
    // act3-video fades in from black at 18.5
    tl.from("#act3-video", { opacity: 0,         duration: 0.8 }, 18.5);

    // Act 3 title
    tl.from("#act3-title", { opacity: 0, y: 30, duration: 0.8 }, 20.0);

    // Final fade out
    tl.to([".clip"], { opacity: 0, duration: 1.0 }, 24.5);

    // Extend to cover the full composition duration
    tl.set({}, {}, 25.5);

    window.__timelines = window.__timelines || {};
    window.__timelines["three-act"] = tl;
  </script>
</body>
</html>
```

## Relative Timing Rules: What the Continuity Supervisor Demands 📋

The framework enforces strict rules on relative timing references:

**Same composition only.** You cannot reference a clip ID from a different composition. References resolve within the current parent composition.

**No circular references.** If Clip A references Clip B which references Clip A, the resolver throws an error. The chain must be acyclic.

**The referenced clip must have a known duration.** If you reference a video clip with no `data-duration` and no source file loaded, the resolver cannot determine when it ends.

**Chain depth matters.** You can chain references: A → B → C → D. But deeply nested chains (more than 3–4 levels) make the timeline hard to reason about. Prefer shallower chains.

```html
<!-- GOOD: short chain -->
<video id="intro" data-start="0"     data-duration="5"  ...></video>
<video id="main"  data-start="intro" data-duration="10" ...></video>
<video id="outro" data-start="main"  data-duration="5"  ...></video>

<!-- ACCEPTABLE: 4 levels -->
<video id="a" data-start="0" ...></video>
<video id="b" data-start="a" ...></video>
<video id="c" data-start="b" ...></video>
<video id="d" data-start="c" ...></video>

<!-- AVOID: 6+ levels is hard to maintain -->
```

In **Episode 4**, the special effects department arrives. GSAP animation — paused timelines, `window.__timelines`, supported properties, and every common mistake that breaks the render sync.

**🔗 Resources**

- **Relative timing**: [hyperframes.heygen.com/concepts/data-attributes#relative-timing](https://hyperframes.heygen.com/concepts/data-attributes#relative-timing)
- **Data Attributes**: [hyperframes.heygen.com/concepts/data-attributes](https://hyperframes.heygen.com/concepts/data-attributes)

*🎬 Sound, Camera, Action with HyperFrames Series — a film director's guide to rendering videos with HTML and JavaScript.*