---
title: "Sound, Camera, Action! 🎬 Ep.4"
published: false
description: "Episode 4: No Hollywood blockbuster ships without special effects. In HyperFrames, GSAP is the VFX department — paused timelines the engine seeks frame by frame, registered on window.__timelines. Learn every supported method, every banned pattern, and why frame-accuracy depends on a single rule."
tags: [javascript, gsap, video, animation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/sound_camera_action_with_hyperframes_series/sound-camera-action-with-hyperframes-episode-04.png"
series: "Sound, Camera, Action with HyperFrames Series"
canonical_url: ""
organization: "the-software-s-journey"
---
## Episode 4: The VFX Department

> "Special effects are just a new kind of reality."— Stanley Kubrick

## The Special Effects Crew Arrives 🎭

In Episode 1, the title card faded in. In Episodes 2 and 3, we understood the screenplay structure and how timing chains across scenes. But no Hollywood blockbuster is just static text fading in. The VFX department makes the impossible real: text that shatters into letters, logos that bounce into frame, lower thirds that slide in from the wings.

In HyperFrames, the VFX department is **GSAP** — the GreenSock Animation Platform. GSAP is the industry-standard JavaScript animation library, used in everything from award-winning websites to interactive data visualisations. In HyperFrames it powers every motion: fades, slides, scales, rotations, stagger effects, custom eases.

There is one rule that distinguishes GSAP inside HyperFrames from GSAP anywhere else. Understand it, and everything works. Violate it, and your animation races through in the first second of the render.

## 🗂️ SIPOC — The VFX Department

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (VFX supervisor) | Animation intent: fade in title at t=1, slide product in at t=2, scale CTA at t=4 | Write GSAP timeline with { paused: true }, register on window.__timelines | A seekable animation timeline | HyperFrames engine — calls tl.seek(frame / fps) for every frame |
| HyperFrames engine | Frame number N, fps | Calls window.__timelines["composition-id"].seek(N / fps) | DOM state exactly correct for that frame | Headless Chrome — captures the pixel buffer at that moment |
| GSAP | Timeline seek position t | Interpolates all properties to their values at time t | Every animated element positioned and styled correctly | The frame capture — visually accurate, frame-perfect |

## The One Rule: The Engine Owns Playback ⚡

GSAP normally runs on its own internal clock — `performance.now()` ticks in real time. If you load a page with a GSAP animation, it plays at wall-clock speed regardless of what the browser is doing.

HyperFrames does something different. For every frame it captures, it:

1. Calls `window.__timelines["your-id"].seek(frameNumber / fps)`
2. Lets the DOM settle
3. Captures the pixel buffer via Chrome's `beginFrame` API
4. Moves to the next frame

This means GSAP is **never running** — it is being *seeked to a position* for each frame. The engine scrubs the timeline like a director scrubbing through film on a flatbed editor. Forward, backward, any frame in any order.

This is why GSAP must always be created with `{ paused: true }`. If you create a non-paused timeline, GSAP will play at wall-clock speed as the page loads, racing through the entire animation before the engine has captured frame 2.

```javascript
// CORRECT: engine controls playback by seeking
const tl = gsap.timeline({ paused: true });

// WRONG: GSAP races at wall-clock speed during render
const tl = gsap.timeline();   // missing { paused: true } !
```

And the timeline must be registered so the engine can find it:

```javascript
// CORRECT: registered with the composition's ID as the key
window.__timelines = window.__timelines || {};
window.__timelines["my-composition"] = tl;

// WRONG: key does not match data-composition-id on the root element
window.__timelines["wrong-name"] = tl;
```

## The Full GSAP Setup: Four Required Lines 🔧

Every HyperFrames composition that uses animation needs these four elements, in order:

```html
<!-- 1. Load GSAP from CDN (or locally) -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>

<script>
  // 2. Create the paused timeline
  const tl = gsap.timeline({ paused: true });

  // 3. Add your animations (using absolute position parameter — see below)
  tl.from("#title", { opacity: 0, y: -60, duration: 1.0 }, 0);
  tl.to("#logo",    { scale: 1.1, duration: 0.3 },          2.5);

  // 4. Register on window.__timelines with the composition ID as key
  window.__timelines = window.__timelines || {};
  window.__timelines["my-composition"] = tl;
</script>
```

## Supported Methods: The Director's VFX Toolkit 🎬

GSAP exposes four methods on a timeline, all of which HyperFrames supports:

| Method | Description | When to use |
| --- | --- | --- |
| tl.to(target, vars, position) | Animate to the given values | Outro: fade something out, move something off screen |
| tl.from(target, vars, position) | Animate from the given values to current | Intro: fade something in, fly it onto screen |
| tl.fromTo(target, fromVars, toVars, position) | Explicit from→to | When you need precise start and end values |
| tl.set(target, vars, position) | Instantaneous property change | Snap to a value at a specific time |

### The position parameter (3rd argument) is critical

The third argument to every GSAP method is the **position** — the time in seconds within the timeline at which this animation starts. Always use absolute seconds. Do not rely on GSAP's default chaining behaviour (which appends each tween to the end of the previous one) because HyperFrames seeks the timeline independently of animation order.

```javascript
// CORRECT: always specify the position parameter
tl.from("#title",    { opacity: 0, y: -40, duration: 0.8 },  0.5);
tl.from("#subtitle", { opacity: 0,         duration: 0.6 },  1.0);
tl.to("#logo",       { scale: 1.1,         duration: 0.4 },  3.2);
tl.to("#title",      { opacity: 0,         duration: 0.5 },  4.5);

// AVOID: no position parameter — relies on implicit chaining
tl.from("#title",    { opacity: 0, y: -40, duration: 0.8 });   // starts at 0 implicitly
tl.from("#subtitle", { opacity: 0,         duration: 0.6 });   // starts at 0.8 implicitly
// Works fine if you add tweens in strict order, but fragile when editing later
```

## Supported Animatable Properties 🎨

GSAP can animate any CSS-animatable property. These are the most useful in video compositions:

| Property | Example value | Notes |
| --- | --- | --- |
| opacity | 0 → 1 | Fades — the most common effect |
| x, y | 100, -50 | Translate in pixels (faster than left/top) |
| scale | 0.8 → 1.0 | Uniform scale from centre |
| scaleX, scaleY | 0 → 1 | Asymmetric scale (wipe effects) |
| rotation | 0 → 360 | Degrees |
| width, height | 0 → 500 | On wrappers, not on <video> elements |
| color | "#fff" | CSS colour strings |
| backgroundColor | "rgba(0,0,0,0.5)" | With rgba() for transparency |
| fontSize | "48px" → "96px" | Text sizing |
| borderRadius | "0px" → "50%" | Shape morphing |
| visibility | "visible" | Snap show/hide (use opacity for gradual) |

### Easing: the cinematographer's f-stop 🎥

Eases control the acceleration curve of an animation — the difference between a robotic linear slide and a natural, physical-feeling motion.

```javascript
// Common eases for video production work:
tl.from("#title",   { y: -80, duration: 1.0, ease: "power3.out"      }, 0);   // decelerating drop
tl.from("#card",    { x: 200, duration: 0.8, ease: "back.out(1.7)"   }, 0.5); // overshoot bounce
tl.to("#logo",      { scale: 0, duration: 0.5, ease: "back.in(2)"    }, 3.0); // pull-back exit
tl.to("#overlay",   { opacity: 0, duration: 0.6, ease: "power2.inOut"}, 4.0); // smooth fade
```

## Stagger: Multiple Actors Entering the Scene 🎭

The stagger feature animates multiple elements with a time offset between each one — like actors entering one at a time from the wings:

```javascript
// Stagger all list items: each one fades up 0.15s after the previous
tl.from(".stat-item", {
  opacity: 0,
  y: 30,
  duration: 0.6,
  stagger: 0.15,
  ease: "power2.out"
}, 1.5);
```

Stagger is ideal for: bullet point reveals, animated bar charts, letter-by-letter title reveals.

### Letter-by-letter title reveal

```html
<h1 id="hero-title" class="clip" data-start="0" data-duration="6" data-track-index="2"
    style="font-size: 96px; font-weight: 900; color: white; letter-spacing: 0.08em;">
  <!-- Each letter wrapped in a span by JavaScript -->
</h1>
```

```javascript
// Split the title text into individual letter spans
const title = document.getElementById("hero-title");
title.innerHTML = title.textContent
  .split("")
  .map(c => c === " " ? " " : `<span class="letter">${c}</span>`)
  .join("");

const tl = gsap.timeline({ paused: true });

// Letters fly in from above with stagger
tl.from(".letter", {
  y: -100,
  opacity: 0,
  rotation: -15,
  duration: 0.5,
  stagger: 0.05,
  ease: "back.out(1.5)"
}, 0.3);

// Hold, then letters fall away
tl.to(".letter", {
  y: 200,
  opacity: 0,
  rotation: 20,
  duration: 0.4,
  stagger: 0.04,
  ease: "power3.in"
}, 4.0);

// Extend timeline to clip duration
tl.set({}, {}, 6);

window.__timelines = window.__timelines || {};
window.__timelines["hero-reveal"] = tl;
```

## The Timeline Duration Rule: Never Cut Your Film Short ✂️

A composition's duration in the render is determined by how long its GSAP timeline runs. This is the most common mistake in HyperFrames:

**If your last GSAP tween ends at 4 seconds, your composition is 4 seconds — even if you have a video clip that runs for 30 seconds.**

```javascript
// VIDEO CLIP: data-duration="30" — 30 seconds
// LAST TWEEN: ends at 4 seconds
tl.from("#lower-third", { x: -640, duration: 0.6 }, 3.2);
// Timeline ends at 3.8 seconds → render cuts off at 3.8s!

// FIX: extend the timeline to match the composition's intended duration
tl.set({}, {}, 30);   // zero-duration tween at t=30 — extends the timeline
```

The `tl.set({}, {}, 30)` pattern — targeting an empty object with an empty vars object at position 30 — is the canonical way to extend a HyperFrames timeline without animating anything.

## What NOT to Do: The Director's Banned List 🚫

```javascript
// BANNED: Playing media in script — the engine owns media playback
document.getElementById("my-video").play();
document.getElementById("audio").currentTime = 5;

// BANNED: Non-paused timeline
const tl = gsap.timeline();   // missing { paused: true }

// BANNED: Manually nesting sub-timelines
const master = window.__timelines["root"];
master.add(window.__timelines["intro-anim"], 0);   // engine does this automatically

// BANNED: Animating dimensions on <video> directly
tl.to("#my-video", { width: 800, height: 450, duration: 1 }, 2);
// FIX: wrap the video in a <div> and animate the wrapper

// BANNED: Wall-clock dependencies
tl.call(() => { console.log(Date.now()); }, [], 2);   // Date.now() is non-deterministic
```

## A Complete VFX Composition: The Social Media Hook 📱

A 9:16 portrait composition (TikTok/Reels style) with a kinetic text hook, staggered emoji, and animated call-to-action:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body, html { margin: 0; padding: 0; background: #0d0d0d; }
    [data-composition-id="social-hook"] {
      width: 1080px; height: 1920px;
      overflow: hidden; position: relative;
      background: linear-gradient(160deg, #1a0533, #0d0d2b);
      font-family: "Arial Black", "Impact", sans-serif;
    }
    #hook-line {
      position: absolute; top: 480px; left: 60px; right: 60px;
      font-size: 96px; font-weight: 900; color: #fff;
      line-height: 1.05; text-align: left;
    }
    .word { display: inline-block; }
    #stat-block {
      position: absolute; top: 900px; left: 60px; right: 60px;
      font-size: 64px; font-weight: 900;
      color: #f5c518; text-align: left;
    }
    #cta {
      position: absolute; bottom: 280px; left: 60px; right: 60px;
      background: #e94560; border-radius: 20px;
      padding: 36px 48px;
      font-size: 52px; font-weight: 900; color: white;
      text-align: center;
    }
  </style>
</head>
<body>
  <div id="root"
       data-composition-id="social-hook"
       data-start="0"
       data-width="1080"
       data-height="1920">

    <h2 id="hook-line" class="clip"
        data-start="0" data-duration="6" data-track-index="1">
      <span class="word">Stop</span>
      <span class="word"> wasting</span>
      <span class="word"> time</span>
      <span class="word"> on</span>
      <span class="word"> boring</span>
      <span class="word"> videos.</span>
    </h2>

    <p id="stat-block" class="clip"
       data-start="1.5" data-duration="4" data-track-index="2">
       10x faster with HyperFrames.
    </p>

    <div id="cta" class="clip"
         data-start="3.2" data-duration="2.8" data-track-index="3">
      Try it free →
    </div>

  </div>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });

    // Words slam in one by one
    tl.from(".word", {
      y: 80, opacity: 0, rotation: -6,
      duration: 0.3, stagger: 0.09,
      ease: "back.out(2)"
    }, 0.1);

    // Stat block punches in
    tl.from("#stat-block", {
      scale: 0.4, opacity: 0,
      duration: 0.5, ease: "back.out(2.5)"
    }, 1.5);

    // CTA slides up from below
    tl.from("#cta", {
      y: 120, opacity: 0,
      duration: 0.4, ease: "power3.out"
    }, 3.2);

    // Pulse on CTA
    tl.to("#cta", { scale: 1.04, duration: 0.2, yoyo: true, repeat: 1 }, 3.8);

    // Extend to full 6s
    tl.set({}, {}, 6);

    window.__timelines = window.__timelines || {};
    window.__timelines["social-hook"] = tl;
  </script>
</body>
</html>
```

```bash
# Render in 9:16 portrait
npx hyperframes render --output social-hook.mp4

# The composition declares its own 1080x1920 dimensions —
# HyperFrames uses those automatically.
```

In **Episode 5**, the editor takes over the cutting room. We composite real video and audio files, trim B-roll with `data-media-start`, mix volume levels, and render transparent MOV overlays using ProRes 4444 — the Hollywood standard for greenscreen composites.

**🔗 Resources**

- **GSAP Animation Guide**: [hyperframes.heygen.com/guides/gsap-animation](https://hyperframes.heygen.com/guides/gsap-animation)
- **Frame Adapters**: [hyperframes.heygen.com/concepts/frame-adapters](https://hyperframes.heygen.com/concepts/frame-adapters)
- **GSAP Easing Visualiser**: [gsap.com/ease-visualizer](https://gsap.com/resources/getting-started/Easing)
- **Common Mistakes**: [hyperframes.heygen.com/guides/common-mistakes](https://hyperframes.heygen.com/guides/common-mistakes)

*🎬 Sound, Camera, Action with HyperFrames Series — a film director's guide to rendering videos with HTML and JavaScript. Open-source. No React required.*