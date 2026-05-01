---
title: "Sound, Camera, Action with HyperFrames 🎬 Ep.6"
published: false
description: "Episode 6: Big productions run multiple simultaneous shooting units. HyperFrames' nested compositions work the same way — external HTML files loaded into a parent composition via data-composition-src. Modular, reusable, independently editable scenes wired together in index.html."
tags: [javascript, html, video, architecture]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/sound_camera_action_with_hyperframes_series/sound-camera-action-with-hyperframes-episode-06.png"
series: "Sound, Camera, Action with HyperFrames Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 6: The Second Unit

> "When the main unit is shooting the dialogue, the second unit is filming the explosions. They work independently, they deliver the footage, and the editor assembles the film."

## When One Set Is Not Enough 🎬

A major Hollywood production has multiple simultaneous shooting units. The main unit films dialogue with the principal actors. The second unit films action sequences and stunts with stunt doubles. A third unit shoots exterior establishing shots in a different city. Each unit delivers footage. The editor assembles everything into a seamless whole.

HyperFrames has the same architecture: **nested compositions**. Your `index.html` is the main unit — the master production. Each sub-composition is a specialist unit: an animated intro, a caption overlay, an animated outro card. Each lives in its own HTML file, has its own GSAP timeline, and is independently editable. The parent composition loads them all and positions them on the timeline.

This is what makes large, complex productions manageable. Instead of one 500-line `index.html` with twelve animation timelines, you have six focused files of 80 lines each.

## 🗂️ SIPOC — The Second Unit

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| Each sub-composition HTML file | A focused, self-contained composition with its own GSAP timeline | data-composition-src="compositions/intro-anim.html" in the parent | Loaded, mounted, and timeline-registered at render time | The parent's timeline — sub-timelines nested automatically based on data-start |
| The parent index.html | References to multiple sub-composition files | Framework fetches each file, extracts <template> content, mounts and executes scripts | A unified render where all sub-compositions appear at the right moment | The render engine — one seamless timeline across all nested compositions |
| You (the director) | A complex production split into scenes | One index.html with data-composition-src references, multiple compositions/*.html | A maintainable project structure: edit each scene independently | Your future self — each file is small, focused, and easy to reason about |

## External Nested Compositions: The Recommended Approach 📁

Reference another HTML file with `data-composition-src`. The framework fetches it, extracts the `<template>` content, mounts it in the parent DOM, and registers its timeline:

```html
<!-- In index.html: load the intro animation as a sub-composition -->
<div id="intro-scene"
     data-composition-id="intro-anim"
     data-composition-src="compositions/intro-anim.html"
     data-start="0"
     data-track-index="0">
</div>
```

The sub-composition file wraps everything in a `<template>` tag:

```html
<!-- compositions/intro-anim.html -->
<template id="intro-anim-template">
  <div data-composition-id="intro-anim"
       data-width="1920"
       data-height="1080">

    <style>
      /* Scope styles to this composition */
      [data-composition-id="intro-anim"] .logo-mark {
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        font-size: 120px; font-weight: 900;
        color: white; letter-spacing: 0.05em;
        font-family: "Georgia", serif;
      }
    </style>

    <div class="logo-mark">ACME</div>

    <script>
      // Each sub-composition registers its OWN timeline
      const tl = gsap.timeline({ paused: true });

      tl.from(".logo-mark", {
        scale: 0.3, opacity: 0, rotation: -15,
        duration: 1.2, ease: "back.out(1.5)"
      }, 0);

      tl.to(".logo-mark", {
        opacity: 0, scale: 1.4,
        duration: 0.8
      }, 2.5);

      // Register with THIS composition's ID
      window.__timelines = window.__timelines || {};
      window.__timelines["intro-anim"] = tl;
    </script>

  </div>
</template>
```

**Key rules for external composition files:**

- Wrap all content in a `<template id="[composition-id]-template">` tag
- Include `<style>` and `<script>` inside the template
- Scope all CSS selectors to `[data-composition-id="your-id"]` to avoid leaking styles into the parent
- Register the timeline with the sub-composition's own `data-composition-id` — not the parent's

## How Sub-Timeline Nesting Works ⚙️

The framework automatically nests sub-composition timelines into the parent at render time. You do **not** manually add sub-timelines to the master timeline:

```javascript
// WRONG: manual nesting — the engine does this automatically
const master = window.__timelines["root"];
master.add(window.__timelines["intro-anim"], 0);   // DO NOT DO THIS

// CORRECT: the engine reads data-start="0" on the nested div
// and automatically places the intro-anim timeline at t=0 in the root timeline
```

The nesting is driven by `data-start` on the `<div data-composition-src="...">` element. Whatever second you put there is when the sub-composition's timeline begins within the parent.

## A Complete Modular Production: Three Scenes 🎬

Here is a full production split into three independent composition files plus a master `index.html`:

### Project structure

```
my-production/
├── index.html                  ← master composition
├── meta.json
├── assets/
│   ├── background.mp4
│   ├── score.wav
│   └── logo.png
└── compositions/
    ├── intro-sting.html        ← branded intro (3s)
    ├── main-content.html       ← main message (15s)
    └── outro-card.html         ← call-to-action card (5s)
```

### `compositions/intro-sting.html`

```html
<template id="intro-sting-template">
  <div data-composition-id="intro-sting"
       data-width="1920" data-height="1080">
    <style>
      [data-composition-id="intro-sting"] {
        position: relative; width: 1920px; height: 1080px;
        background: #000; overflow: hidden;
        display: flex; align-items: center; justify-content: center;
      }
      [data-composition-id="intro-sting"] .brand {
        font-size: 96px; font-weight: 900; color: #fff;
        font-family: "Arial Black", sans-serif;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }
      [data-composition-id="intro-sting"] .rule {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 6px; background: #e94560;
        transform-origin: left center;
      }
    </style>

    <h1 class="brand">ACME CORP</h1>
    <div class="rule"></div>

    <script>
      const tl = gsap.timeline({ paused: true });
      tl.from(".brand", { letterSpacing: "0.5em", opacity: 0, duration: 1.2, ease: "power3.out" }, 0);
      tl.from(".rule",  { scaleX: 0, duration: 0.8, ease: "power4.out" }, 0.6);
      tl.to(".brand",   { opacity: 0, duration: 0.5 }, 2.5);
      tl.to(".rule",    { scaleX: 0, transformOrigin: "right", duration: 0.4 }, 2.6);
      tl.set({}, {}, 3);
      window.__timelines = window.__timelines || {};
      window.__timelines["intro-sting"] = tl;
    </script>
  </div>
</template>
```

### `compositions/main-content.html`

```html
<template id="main-content-template">
  <div data-composition-id="main-content"
       data-width="1920" data-height="1080">
    <style>
      [data-composition-id="main-content"] {
        position: relative; width: 1920px; height: 1080px;
        overflow: hidden;
      }
      [data-composition-id="main-content"] .headline {
        position: absolute; top: 320px; left: 120px; right: 120px;
        font-size: 80px; font-weight: 900; color: #fff;
        font-family: "Georgia", serif; line-height: 1.1;
      }
      [data-composition-id="main-content"] .body-text {
        position: absolute; top: 560px; left: 120px; right: 600px;
        font-size: 38px; color: #ccc;
        font-family: Arial, sans-serif; line-height: 1.5;
      }
    </style>

    <h2 class="headline clip"
        data-start="0" data-duration="14" data-track-index="1">
      Build anything.<br/>Ship faster.
    </h2>
    <p class="body-text clip"
       data-start="1" data-duration="13" data-track-index="2">
      HyperFrames turns plain HTML into<br/>
      frame-perfect rendered video.<br/>
      No React. No build step.
    </p>

    <script>
      const tl = gsap.timeline({ paused: true });
      tl.from(".headline",  { y: 60, opacity: 0, duration: 1.0, ease: "power3.out" }, 0);
      tl.from(".body-text", { y: 40, opacity: 0, duration: 0.8 }, 1.2);
      tl.to([".headline", ".body-text"], { opacity: 0, duration: 0.8 }, 13.5);
      tl.set({}, {}, 15);
      window.__timelines = window.__timelines || {};
      window.__timelines["main-content"] = tl;
    </script>
  </div>
</template>
```

### `compositions/outro-card.html`

```html
<template id="outro-card-template">
  <div data-composition-id="outro-card"
       data-width="1920" data-height="1080">
    <style>
      [data-composition-id="outro-card"] {
        position: relative; width: 1920px; height: 1080px;
        background: #e94560; overflow: hidden;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        font-family: "Arial Black", sans-serif;
      }
      [data-composition-id="outro-card"] .cta-main {
        font-size: 88px; font-weight: 900; color: #fff;
        text-align: center; margin-bottom: 40px;
      }
      [data-composition-id="outro-card"] .cta-url {
        font-size: 44px; color: rgba(255,255,255,0.8);
        text-align: center;
      }
    </style>

    <h2 class="cta-main">Get started free</h2>
    <p  class="cta-url">hyperframes.heygen.com</p>

    <script>
      const tl = gsap.timeline({ paused: true });
      tl.from(".cta-main", { scale: 0.5, opacity: 0, duration: 0.7, ease: "back.out(2)" }, 0.3);
      tl.from(".cta-url",  { y: 40,      opacity: 0, duration: 0.5 }, 0.9);
      tl.set({}, {}, 5);
      window.__timelines = window.__timelines || {};
      window.__timelines["outro-card"] = tl;
    </script>
  </div>
</template>
```

### `index.html` — The Master Composition

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body, html { margin: 0; padding: 0; background: #0a0a1a; }
    [data-composition-id="full-production"] {
      width: 1920px; height: 1080px;
      overflow: hidden; position: relative;
    }
  </style>
</head>
<body>
  <div id="root"
       data-composition-id="full-production"
       data-start="0"
       data-width="1920"
       data-height="1080">

    <!-- Background footage: runs the full duration -->
    <video id="bg"
           class="clip"
           data-start="0"
           data-duration="23"
           data-track-index="0"
           data-has-audio="false"
           src="assets/background.mp4"
           muted playsinline
           style="position: absolute; inset: 0; width: 1920px; height: 1080px; object-fit: cover; opacity: 0.4;">
    </video>

    <!-- SCENE 1: Intro sting (0–3s) -->
    <div id="intro"
         data-composition-id="intro-sting"
         data-composition-src="compositions/intro-sting.html"
         data-start="0"
         data-track-index="1">
    </div>

    <!-- SCENE 2: Main content (3–18s) — starts when intro ends -->
    <div id="main"
         data-composition-id="main-content"
         data-composition-src="compositions/main-content.html"
         data-start="intro"
         data-track-index="1">
    </div>

    <!-- SCENE 3: Outro card (18–23s) — starts when main ends -->
    <div id="outro"
         data-composition-id="outro-card"
         data-composition-src="compositions/outro-card.html"
         data-start="main"
         data-track-index="1">
    </div>

    <!-- Score: full composition -->
    <audio id="score"
           class="clip"
           data-start="0"
           data-duration="23"
           data-track-index="5"
           data-volume="0.3"
           src="assets/score.wav">
    </audio>

  </div>

  <!-- GSAP for the master composition (root-level tweens only) -->
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    // The master timeline only handles root-level effects
    // (e.g. a global fade-in at the very start, or fade-out at the very end)
    const tl = gsap.timeline({ paused: true });

    // Fade in the background
    tl.from("#bg", { opacity: 0, duration: 1.0 }, 0);

    // Final fade to black
    tl.to("#root > *", { opacity: 0, duration: 1.0 }, 22.0);

    // Extend to full 23s
    tl.set({}, {}, 23);

    window.__timelines = window.__timelines || {};
    window.__timelines["full-production"] = tl;
  </script>
</body>
</html>
```

### Preview and render

```bash
npx hyperframes preview
# Review all three scenes in sequence

npx hyperframes render --output full-production.mp4
# ✔ Capturing frames... 690/690
# ✔ full-production.mp4 (1920x1080, 23.0s, 30fps)
```

## List All Compositions in a Project 📋

```bash
npx hyperframes compositions
```

```
Compositions found:
  root:           full-production     (index.html)
  sub:            intro-sting         (compositions/intro-sting.html)
  sub:            main-content        (compositions/main-content.html)
  sub:            outro-card          (compositions/outro-card.html)
```

## Inline vs External: Which to Use 🤔

| Approach | When to use |
| --- | --- |
| External file (data-composition-src) | Reusable across multiple productions; longer than ~30 lines; has its own complex GSAP timeline |
| Inline (nested <div> in same file) | Simple, one-off sub-compositions; quick prototyping; less than 20 lines of content |

External files are the professional choice for any production you intend to maintain or reuse. Inline is fine for quick iteration or genuinely simple nested content.

In **Episode 7**, the camera crew calls "Rolling!" — we cover every render option: local vs Docker mode, quality presets, GPU encoding, parallel workers, concurrent renders, and CI/CD pipelines.

**🔗 Resources**

- **Compositions**: [hyperframes.heygen.com/concepts/compositions](https://hyperframes.heygen.com/concepts/compositions)
- **Nested compositions**: [hyperframes.heygen.com/concepts/compositions#nested-compositions](https://hyperframes.heygen.com/concepts/compositions#nested-compositions)
- **CLI reference**: [hyperframes.heygen.com/packages/cli](https://hyperframes.heygen.com/packages/cli)

*🎬 Sound, Camera, Action with HyperFrames Series — a film director's guide to rendering videos with HTML and JavaScript. Open-source. No React required.*
