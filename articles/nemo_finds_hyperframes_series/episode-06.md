---
title: "Nemo finds Hyperframes 🦈 Ep.6"
series: "Nemo finds Hyperframes"
part: 6
organization: "the-software-s-journey"
tags: [hyperframes, ai-agents, skills, claude-code, workflow]
---

## Episode 6: Fish Are Friends, Not Food: Trusting the Skills

Bruce runs a support group for sharks trying not to eat what swims past them, and the joke has always been that the effort is entirely genuine — the intent really is to help, not to devour. HyperFrames' AI agent skills work from the same premise: an agent that has actually read the skill isn't guessing at your composition and hoping it survives contact with the renderer.

Here's a concrete moment from building this repository. Partway through Episode 4's title scene, the first draft of the fish animation — written before `/hyperframes-animation` had been consulted for this particular tween — looked like this:

```javascript
// what an unguided first attempt tends to reach for
document.getElementById('nemo-fish').animate(
  [{ transform: 'translateX(-400px)', opacity: 0 },
   { transform: 'translateX(0)', opacity: 1 }],
  { duration: 1000, fill: 'forwards' }
);
```

It's not wrong, exactly — the Web Animations API is a real, documented HyperFrames adapter. But it runs on its own clock the moment the page loads, completely disconnected from `window.__timelines`, which means the render pipeline has no way to seek to a specific frame and know where Nemo should be. Scrub to second 2.5 during a render and this animation has either already finished or hasn't started, depending on when the page happened to load relative to the capture — exactly the kind of non-determinism Episode 8 will explain why HyperFrames refuses to ship.

`/hyperframes-animation` heads this off by teaching the agent the registered-timeline pattern before the first tween is ever written, which is what actually ended up in `index.html`:

```javascript
const tl = gsap.timeline({ paused: true });
tl.from('#nemo-fish', { x: -400, opacity: 0, duration: 1, ease: 'power2.out' }, 0.2);
window.__timelines = window.__timelines || {};
window.__timelines['nemo-finds-hyperframes'] = tl;
```

Same visual result, but this version is seek-driven: the renderer can jump straight to second 2.5, ask GSAP where Nemo is supposed to be at that exact timestamp, and get a deterministic answer every single time. `/hyperframes-core` plays the same role for structure — it's why every scene in our composition uses `class="clip"` with explicit `data-start`/`data-duration` instead of `setTimeout` calls the agent might otherwise reach for. `/hyperframes-registry`, which Episode 7 leans on directly, plays it for effects — it's why we didn't hand-roll the white-flash transition from raw CSS keyframes. In each case the skill isn't correcting a mistake after the fact; it's making the correct pattern the first thing reached for, so the mistake above never made it past a first draft.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `/hyperframes-animation` skill | A request to animate `#nemo-fish` | Apply the registered-timeline pattern instead of an unregistered Web Animations API call | A seek-driven, deterministic tween on the master timeline | The render pipeline, this composition's title scene |
| AI coding agent | The loaded skill plus the specific animation request | Write GSAP code matching the documented contract on the first attempt | Correct, renderable animation code | Developer reviewing the diff |
| Developer (this series' author) | The unguided first draft vs. the skill-guided version | Compare both and keep the one that survives a seek-driven render | A documented example of why the skill matters | Future readers deciding whether skills are worth installing |

Next stop: the tank gang — the HyperFrames Catalog, and the two blocks we actually installed instead of hand-rolling.
