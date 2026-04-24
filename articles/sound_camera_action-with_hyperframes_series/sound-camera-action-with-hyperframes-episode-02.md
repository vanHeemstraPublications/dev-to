---
title: "Sound, Camera, Action! 🎬 Ep.2"
published: false
description: "Episode 2: Every Hollywood director starts with a screenplay. In HyperFrames, the screenplay is an HTML file. This episode is the grammar course — every data attribute, every clip type, the mandatory three-rule structure, and common mistakes that break the render."
tags: [javascript, html, video, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/sound_camera_action_with_hyperframes_series/sound-camera-action-with-hyperframes-episode-02.png"
series: "Sound, Camera, Action with HyperFrames Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: The Screenplay

> "The screenplay is the blueprint. Every other department reads it and asks: what do I need to make this real?"

## The Director's Script 📄

In Hollywood, the screenplay is the single source of truth. The director of photography reads it and plans shots. The costume department reads it and prepares wardrobe. The sound editor reads it and plans the mix. Every department derives their work from the same document.

In HyperFrames, the HTML composition is that document. The rendering engine reads it and plans frames. The GSAP adapter reads it and plans animation. The FFmpeg pipeline reads the frame output and plans the encode. Every stage of the production pipeline derives from `index.html`.

This episode is a complete grammar course in the screenplay language. By the end, you will be able to read and write any HyperFrames composition with confidence.

## 🗂️ SIPOC — The Script Department

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (script writer) | A video idea with specific timing, assets, and effects | Write HTML with data-* attributes for every timed element | A valid composition index.html that the linter accepts | npx hyperframes render — reads the HTML, produces frames |
| The HyperFrames linter | Your index.html | npx hyperframes lint — validates composition structure, checks data-* attributes | Pass / fail with line-level error messages | You — catch mistakes before the render starts |
| The preview server | Your composition HTML + assets | npx hyperframes preview — live reload in the browser | Real-time visual feedback as you write | You — the director watching rushes |

## The Root Element: Setting the Scene 🎬

Every composition must have a root element. This is the scene declaration — it tells the engine what it is rendering, at what resolution, and for how long.

```html
<!-- REQUIRED: every composition must have this element -->
<div id="root"
     data-composition-id="my-scene"
     data-start="0"
     data-width="1920"
     data-height="1080">
  <!-- clips go here -->
</div>
```

The three mandatory attributes on the root element:

| Attribute | Role | Film metaphor |
| --- | --- | --- |
| data-composition-id | Unique ID for this composition | The scene number in the screenplay |
| data-width | Canvas width in pixels | The aspect ratio of the film stock |
| data-height | Canvas height in pixels | The aspect ratio of the film stock |

Common resolutions for the director:

```
1920 × 1080   →  16:9  landscape (YouTube, TV, web)
1080 × 1080   →  1:1   square    (Instagram)
1080 × 1920   →  9:16  portrait  (TikTok, Reels, Stories)
1920 × 1080   →  16:9  landscape (standard)
3840 × 2160   →  16:9  4K
```

## Clip Types: The Cast and Props 🎭

Every element that appears in the video timeline is a **clip**. There are four clip types — four kinds of cast members the director can put on set:

### 1. `<h1>`, `<p>`, `<div>` — Text and overlay elements

```html
<h1 id="main-title"
    class="clip"
    data-start="0"
    data-duration="5"
    data-track-index="0"
    style="font-size: 72px; color: white; position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);">
  The Director's Cut
</h1>
```

Any HTML element that carries content or acts as an animation target. Text, cards, overlays, lower thirds, progress bars.

### 2. `<video>` — B-roll and A-roll footage

```html
<video id="bg-footage"
       class="clip"
       data-start="0"
       data-duration="10"
       data-track-index="0"
       data-has-audio="false"
       src="assets/city.mp4"
       muted
       playsinline
       style="width: 1920px; height: 1080px; object-fit: cover;">
</video>
```

Key video attributes:

| Attribute | Purpose |
| --- | --- |
| data-duration | Optional — defaults to the source file's duration |
| data-media-start | Trim point: start playing from N seconds into the source |
| data-has-audio | "true" if the video has an audio track to include |
| data-volume | Volume, 0 to 1 |
| muted | Must be present (browsers require muted for autoplay) |

### 3. `<img>` — Static images and overlays

```html
<img id="logo"
     class="clip"
     data-start="2"
     data-duration="3"
     data-track-index="2"
     src="assets/logo.png"
     style="position: absolute; bottom: 60px; right: 80px; width: 200px;" />
```

`data-duration` is **required** for images — unlike video, images have no source duration.

### 4. `<audio>` — Soundtrack and sound effects

```html
<audio id="music"
       class="clip"
       data-start="0"
       data-duration="10"
       data-track-index="3"
       data-volume="0.4"
       src="assets/background-music.wav">
</audio>
```

Audio clips are invisible in the composition but audible in the rendered MP4. Use `data-volume` to balance levels between music, voice-over, and effects.

## The Full Timing Reference 📋

The timing attributes are the director's marks on the floor — every actor (clip) stands on a mark and knows exactly when to enter and exit.

| Attribute | Type | Required? | Notes |
| --- | --- | --- | --- |
| data-start | number or clip ID | Yes | Start time in seconds, or reference to another clip's ID |
| data-duration | number | Required for <img> | Duration in seconds. Optional for <video> and <audio> |
| data-track-index | integer | Yes | Track number for z-ordering. Clips on the same track cannot overlap |
| class="clip" | CSS class | Yes on all timed elements | Tells the runtime to manage this element's visibility |

### What `data-track-index` does

Track index controls two things simultaneously:

**Z-ordering**: higher track index = visually on top. Track 3 sits above Track 2 above Track 1 above Track 0.

**Collision detection**: clips on the same track cannot overlap in time. If you try to place two clips that overlap on Track 0, the linter raises an error.

```html
<!-- CORRECT: each clip on its own track -->
<video id="bg"     data-start="0" data-duration="10" data-track-index="0" ...></video>
<img   id="overlay" data-start="2" data-duration="5"  data-track-index="1" .../>
<h1    id="title"  data-start="3" data-duration="4"  data-track-index="2" ...>Title</h1>
<audio id="music"  data-start="0" data-duration="10" data-track-index="3" ...></audio>

<!-- WRONG: two clips overlap on the same track -->
<video id="clip-a" data-start="0" data-duration="8" data-track-index="0" ...></video>
<video id="clip-b" data-start="5" data-duration="8" data-track-index="0" ...></video>
<!-- linter error: clips on track 0 overlap at t=5..8 -->
```

## Media Attributes: Trim and Volume 🎞️

### `data-media-start` — Trim the source footage

Use `data-media-start` to start playing a video or audio clip from a specific point in the source file:

```html
<!-- Play from 30 seconds into the source -->
<video id="interview"
       class="clip"
       data-start="5"
       data-duration="20"
       data-track-index="0"
       data-media-start="30"
       src="assets/full-interview.mp4"
       muted playsinline>
</video>
```

This places the clip at second 5 in the composition and plays the source from 30 seconds in for 20 seconds. Like the editor trimming the interview in the cutting room.

### `data-volume` — Mix your levels

```html
<!-- Background music at 40% -->
<audio id="bg-music" data-volume="0.4" ...></audio>

<!-- Voice-over at full volume -->
<audio id="vo"       data-volume="1.0" ...></audio>

<!-- Sound effect at 70% -->
<audio id="sfx"      data-volume="0.7" ...></audio>
```

## A Complete Screenplay: The Product Promo 🎥

Here is a realistic 10-second product promo composition — the kind you would generate for a social media ad:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body, html { margin: 0; padding: 0; }

    [data-composition-id="product-promo"] {
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      background: #1a1a2e;
      position: relative;
      font-family: "Arial", sans-serif;
    }

    #product-img {
      position: absolute;
      left: 200px;
      top: 50%;
      transform: translateY(-50%);
      width: 600px;
      height: 600px;
      object-fit: contain;
    }

    #headline {
      position: absolute;
      right: 200px;
      top: 280px;
      font-size: 72px;
      font-weight: 900;
      color: #fff;
      line-height: 1.1;
      text-align: right;
    }

    #tagline {
      position: absolute;
      right: 200px;
      top: 520px;
      font-size: 36px;
      color: #aaa;
      text-align: right;
    }

    #cta {
      position: absolute;
      right: 200px;
      bottom: 160px;
      background: #e94560;
      color: white;
      padding: 18px 48px;
      border-radius: 8px;
      font-size: 28px;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <div id="root"
       data-composition-id="product-promo"
       data-start="0"
       data-width="1920"
       data-height="1080">

    <!-- Background footage: B-roll of the product environment -->
    <video id="bg"
           class="clip"
           data-start="0"
           data-duration="10"
           data-track-index="0"
           data-has-audio="false"
           src="assets/studio-bg.mp4"
           muted playsinline
           style="position: absolute; inset: 0; width: 1920px; height: 1080px; object-fit: cover; opacity: 0.3;">
    </video>

    <!-- Product image: enters at 0.5s -->
    <img  id="product-img"
          class="clip"
          data-start="0.5"
          data-duration="9"
          data-track-index="1"
          src="assets/product.png" />

    <!-- Headline text: enters at 1s -->
    <h2 id="headline"
        class="clip"
        data-start="1"
        data-duration="8"
        data-track-index="2">
      The Future<br/>Is Now
    </h2>

    <!-- Tagline: enters at 2s -->
    <p id="tagline"
       class="clip"
       data-start="2"
       data-duration="7"
       data-track-index="3">
      Redefining what's possible.
    </p>

    <!-- CTA: enters at 4s, lasts until end -->
    <div id="cta"
         class="clip"
         data-start="4"
         data-duration="5.5"
         data-track-index="4">
      Shop Now →
    </div>

    <!-- Background music at low volume -->
    <audio id="music"
           class="clip"
           data-start="0"
           data-duration="10"
           data-track-index="5"
           data-volume="0.3"
           src="assets/ambient.wav">
    </audio>

  </div>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });

    // Product image slides in from the left
    tl.from("#product-img", { x: -300, opacity: 0, duration: 1.0, ease: "power3.out" }, 0.5);

    // Headline drops in word by word
    tl.from("#headline",    { y: -40,  opacity: 0, duration: 0.8, ease: "back.out(1.7)" }, 1.0);

    // Tagline fades up
    tl.from("#tagline",     { y: 20,   opacity: 0, duration: 0.6 }, 2.0);

    // CTA bounces in
    tl.from("#cta",         { scale: 0.6, opacity: 0, duration: 0.5, ease: "back.out(2)" }, 4.0);

    // Final fade-out at 9.2s
    tl.to("#root > *",      { opacity: 0, duration: 0.8 }, 9.2);

    // Extend timeline to full 10s so the composition is 10 seconds long
    tl.set({}, {}, 10);

    window.__timelines = window.__timelines || {};
    window.__timelines["product-promo"] = tl;
  </script>
</body>
</html>
```

### Preview and render

```bash
npx hyperframes preview
# review in browser — scrub the timeline, check all timings

npx hyperframes render --output promo.mp4
# ✔ Capturing frames... 300/300
# ✔ promo.mp4 (1920x1080, 10.0s, 30fps)
```

## The Linter: The Script Editor 📝

Before rendering, run the linter to catch structural mistakes:

```bash
npx hyperframes lint
```

The linter checks:

- Root element has `data-composition-id`, `data-width`, `data-height`
- All `class="clip"` elements have `data-start`, `data-duration`, `data-track-index`
- No overlapping clips on the same track
- No circular timing references
- Timeline registration on `window.__timelines`

```
✓ Composition "product-promo" is valid
✓ 6 clips found on 6 tracks
✓ No timing overlaps detected
✓ Timeline registration found
```

Run the linter before every render. It is faster than waiting for a failed render to tell you the same thing.

## Common Mistakes to Avoid 🚫

**Mistake 1: Forgetting **`class="clip"`Elements without `class="clip"` are always visible — they do not appear and disappear with the timeline. The runtime cannot manage their lifecycle.

**Mistake 2: Animating **`<video>`** dimensions directly**GSAP animating `width`, `height`, `top`, or `left` on a `<video>` element causes the browser to stop rendering frames. Wrap the video in a `<div>` and animate the wrapper.

**Mistake 3: Creating the GSAP timeline without **`{ paused: true }`A non-paused timeline will immediately play in the browser preview, desynchronising from the frame capture. Always `gsap.timeline({ paused: true })`.

**Mistake 4: Calling **`video.play()`** or **`video.pause()`** in scripts**The framework owns media playback. Any script that manually calls `.play()`, `.pause()`, or `.currentTime` on a media element will conflict with the render engine.

In **Episode 3**, the continuity supervisor joins set. Relative timing — referencing clip IDs rather than absolute seconds — keeps your screenplay flexible when you extend one scene and need the rest to shift automatically.

**🔗 Resources**

- **Data Attributes reference**: [hyperframes.heygen.com/concepts/data-attributes](https://hyperframes.heygen.com/concepts/data-attributes)
- **Compositions**: [hyperframes.heygen.com/concepts/compositions](https://hyperframes.heygen.com/concepts/compositions)
- **Common Mistakes**: [hyperframes.heygen.com/guides/common-mistakes](https://hyperframes.heygen.com/guides/common-mistakes)

*🎬 Sound, Camera, Action with HyperFrames Series — a film director's guide to rendering videos with HTML and JavaScript.*