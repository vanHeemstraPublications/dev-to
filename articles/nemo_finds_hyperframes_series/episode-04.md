---
title: "Nemo finds Hyperframes 🌊 Ep.4"
series: "Nemo finds Hyperframes"
part: 4
organization: "the-software-s-journey"
tags: [hyperframes, gsap, animation, composition, data-attributes]
---

## Episode 4: The East Australian Current: Clips, Tracks, and Timelines
 
The EAC doesn't ask a sea turtle to swim — it asks the turtle to let go and be carried, which is a very different skill. HyperFrames' animation model works the same way. You don't hand-animate frame by frame; you build a timeline, pause it, register it, and let the renderer carry every clip through the current at exactly the beat you specified.

The composition contract has exactly three rules, and our root element in `index.html` follows all three:

```html
<div id="nemo-finds-hyperframes"
     data-composition-id="nemo-finds-hyperframes"
     data-start="0" data-width="1920" data-height="1080">
```

Every timed element needs `data-start`, `data-duration`, `data-track-index`, and `class="clip"`. Here's the actual title scene — the first four seconds of the video, where Nemo swims in from the left and the title fades up behind him:

```html
<section id="scene-title" class="scene clip" data-start="0" data-duration="4" data-track-index="0">
  <div class="fish" id="nemo-fish">
    <svg viewBox="0 0 220 140">
      <ellipse cx="110" cy="70" rx="90" ry="46" fill="#ff7a1a"/>
      <ellipse cx="110" cy="70" rx="90" ry="46" fill="none" stroke="#fff" stroke-width="10" stroke-dasharray="8 130"/>
      <path d="M195 70 L220 40 L220 100 Z" fill="#ff7a1a"/>
      <circle cx="70" cy="58" r="9" fill="#0a0a0a"/>
    </svg>
  </div>
  <div style="text-align:center">
    <h1 id="title-text">Nemo finds Hyperframes</h1>
    <div class="sub" id="title-sub">a video, composed entirely in HTML</div>
  </div>
</section>
```

Nemo himself is nothing more elaborate than an SVG ellipse, a stripe, and a triangle for a tail fin — proof that HyperFrames doesn't need imported artwork to put a character on screen. And the GSAP timeline that drives him must be created paused and registered under the composition's own ID, so the render pipeline is the one steering, not the browser's own clock:

```javascript
const tl = gsap.timeline({ paused: true });

tl.to('#scene-title', { opacity: 1, duration: 0.01 }, 0);
tl.from('#nemo-fish', { x: -400, opacity: 0, duration: 1, ease: 'power2.out' }, 0.2);
tl.to('#nemo-fish', { x: 40, duration: 2.6, ease: 'sine.inOut', yoyo: true, repeat: 1 }, 0.4);
tl.from('#title-text', { opacity: 0, y: 30, duration: 0.8 }, 0.6);
tl.from('#title-sub', { opacity: 0, y: 20, duration: 0.8 }, 1.0);
tl.to('#scene-title', { opacity: 0, duration: 0.4 }, 3.6);

window.__timelines = window.__timelines || {};
window.__timelines['nemo-finds-hyperframes'] = tl;
```

Every number in that block is an absolute second on the master timeline, not a relative offset — `0.2` means "0.2 seconds into the whole video," which is what lets four separate scenes share one timeline object without stepping on each other. Nemo drifts in from `x: -400` at 0.2s, settles into a gentle side-to-side sway from 0.4s using `yoyo: true, repeat: 1`, and the whole scene fades to make room for Episode 5's code scene at 3.6s — 0.4 seconds before the section's own `data-duration="4"` runs out, so the cut lands clean. The animation runtime isn't limited to GSAP either — Lottie, Three.js, Anime.js, plain CSS, WAAPI, and TypeGPU all register through equivalent adapters — but for a promo this size, one GSAP timeline was all we needed.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Composition author | The root element and the `#scene-title` section | Apply `data-composition-id`/`data-width`/`data-height` on the root, `class="clip"` plus `data-start`/`data-duration`/`data-track-index` on the scene | A structurally valid first scene | The GSAP timeline, the render pipeline |
| GSAP (via CDN) | The paused timeline definition above | Animate `#nemo-fish`, `#title-text`, and `#title-sub` at their absolute timeline positions | Motion synchronized to the scene's 0–4s window | The render pipeline, the eventual video output |
| `window.__timelines` registry | The named, paused `nemo-finds-hyperframes` timeline object | Expose the timeline for the renderer to drive frame by frame | A renderer-controlled, deterministic animation source | `hyperframes render`, `hyperframes preview` |

Next stop: Crush and Squirt take the helm for the dev loop — watching Nemo actually swim, live, before committing to anything.
