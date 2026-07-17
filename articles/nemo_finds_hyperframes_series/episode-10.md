---
title: "Nemo finds Hyperframes 🌅 Ep.10"
series: "Nemo finds Hyperframes"
part: 10
organization: "the-software-s-journey"
tags: [hyperframes, opensource, github, community, wrapup]
---

## Episode 10: Sydney Harbour: Nemo Rejoins the Open Reef

The story never really ends with Nemo swimming home alone. It ends with the whole reef a little more connected than it was at the start, because the trip through the ocean turned strangers into a community that knows how to help each other. There's one piece of the codebase this series has mentioned every episode but never actually shown: `compositions/captions.html`, running quietly on its own track for the full twenty seconds. Here it is in full, closing out the repository:

```html
<div id="captions" data-composition-id="captions" data-start="0" data-width="1920" data-height="1080">

  <div class="cap clip" data-start="0.5"  data-duration="3"   data-track-index="0">Every video starts as an idea an AI agent can write down.</div>
  <div class="cap clip" data-start="4.3"  data-duration="5"   data-track-index="0">The composition contract: data-composition-id, clips, and tracks.</div>
  <div class="cap clip" data-start="10.3" data-duration="5"   data-track-index="0">Catalog blocks mean you rarely animate an effect from scratch.</div>
  <div class="cap clip" data-start="16.3" data-duration="3.4" data-track-index="0">Open source, from HeyGen, built for the community.</div>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });
    document.querySelectorAll('#captions .cap').forEach((el) => {
      const start = parseFloat(el.dataset.start);
      const dur = parseFloat(el.dataset.duration);
      tl.to(el, { opacity: 1, duration: 0.25 }, start);
      tl.to(el, { opacity: 0, duration: 0.25 }, start + dur - 0.25);
    });
    window.__timelines = window.__timelines || {};
    window.__timelines['captions'] = tl;
  </script>
</div>
```

It's loaded from the root composition with one line — a fifth `data-composition-src` clip sitting on its own track, never colliding with the four scenes on track 0:

```html
<div class="clip" data-start="0" data-duration="20" data-track-index="1"
     data-composition-src="compositions/captions.html"></div>
```

That's every file in the repository now accounted for:

```
nemo-finds-hyperframes/
├── meta.json                  # 1920×1080, 30fps, project description
├── index.html                 # root composition — 4 scenes, 1 master GSAP timeline
├── compositions/
│   └── captions.html          # sub-composition, its own timeline, its own track
└── assets/                    # empty — no imported media in this project
```

None of it required learning a proprietary timeline editor. All of it was HTML, CSS, JS, and a small, well-documented set of `data-*` attributes that an AI agent already knew how to write the moment it read the right skill in Episode 2. `/hyperframes` routed the request. The composition contract from Episode 4 kept the structure honest. The catalog from Episode 7 kept us from reinventing what was already solved. The renderer from Episodes 8 and 9 guaranteed that what we watched in preview is exactly what shipped.

The full project is public at [github.com/software-journey/hyperframes](https://github.com/software-journey/hyperframes) under the Apache 2.0 license — clone it, render it yourself, or pull `flash-through-white` and `data-chart` straight into your own composition the same way we did. That's what an open catalog and a public repository are for: the next person's Nemo doesn't have to start from an empty ocean.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `github.com/software-journey/hyperframes` (Apache 2.0) | The complete, ten-episode-built codebase | Host and version the finished project publicly | A clonable, renderable reference implementation | Every future reader of this series, other developers |
| `compositions/captions.html` | Four timed caption strings | Fade each caption in and out on its own track and timeline | Synchronized captions running alongside the four visual scenes | The rendered `nemo-finds-hyperframes.mp4`, viewers relying on captions |
| The reader of this series | The nine preceding episodes plus this repository | Clone, render, and adapt the project for their own composition | A working HyperFrames video of their own | Their own audience, downstream publishing channels |
