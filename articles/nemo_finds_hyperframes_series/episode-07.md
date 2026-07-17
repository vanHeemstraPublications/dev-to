---
title: "Nemo finds Hyperframes 🐡 Ep.7"
series: "Nemo finds Hyperframes"
part: 7
organization: "the-software-s-journey"
tags: [hyperframes, catalog, blocks, registry, components]
---

## Episode 7: The Tank Gang and the Catalog of Blocks

Gill, Bloat, Bubbles, Peach, Gurgle, Jacques, Deb — the tank gang's whole personality is that every one of them has already solved a specific problem long before Nemo ever shows up needing help. That's the role the HyperFrames Catalog played for our third scene, which showcases exactly two catalog blocks rather than reinventing either from scratch:

```bash
npx hyperframes add flash-through-white   # shader transition
npx hyperframes add data-chart            # animated bar chart
```

The `/hyperframes-registry` skill from Episode 2 is what actually reaches into the catalog and wires the block into the project when an agent asks for it. In our composition, the transition shows up as a simple full-frame overlay that flashes and clears at the top of the scene, and the chart shows up as five bars that grow to their target heights in sequence:

```html
<section id="scene-catalog" class="scene clip" data-start="10" data-duration="6" data-track-index="0">
  <div class="flash"></div>
  <div class="card" id="card-transition">
    <h3>flash-through-white</h3>
    <p>npx hyperframes add flash-through-white</p>
  </div>
  <div class="card" id="card-chart">
    <h3>data-chart</h3>
    <p>npx hyperframes add data-chart</p>
    <div class="bars">
      <div class="bar" data-h="60"></div>
      <div class="bar" data-h="110"></div>
      <div class="bar" data-h="80"></div>
      <div class="bar" data-h="140"></div>
      <div class="bar" data-h="95"></div>
    </div>
  </div>
</section>
```

```javascript
tl.to('#scene-catalog', { opacity: 1, duration: 0.01 }, 10);
tl.to('.flash', { opacity: 1, duration: 0.15 }, 10);
tl.to('.flash', { opacity: 0, duration: 0.35 }, 10.15);
tl.to('#card-transition', { opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(1.7)' }, 10.6);
tl.to('#card-chart', { opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(1.7)' }, 11.0);

document.querySelectorAll('#scene-catalog .bar').forEach((bar, i) => {
  tl.to(bar, { height: bar.dataset.h + 'px', duration: 0.6, ease: 'power2.out' }, 11.6 + i * 0.15);
});
```

Notice that neither block required a single custom keyframe. The flash is a `.flash` div that starts at `opacity: 0` in the stylesheet, jumps to fully opaque over 0.15s, then clears over 0.35s — the transition's actual visual logic — and the bars simply animate their own `height` up to a value already stored in a `data-h` attribute on each element. That's the deeper value of pulling from the catalog rather than improvising: a block already follows the composition contract correctly, already has its animation registered on the right timeline, and installing it is the whole job, the same way the tank gang's group sessions work precisely because everyone already knows the routine and doesn't need to relearn it mid-crisis.

The card styling itself — the frosted-glass `backdrop-filter: blur(6px)` panel, the `scale(0.9)` to `scale(1)` pop-in with a `back.out` ease — is ordinary CSS and GSAP, not something a catalog block dictates. The catalog gives you the effect; how you frame it around your own content is still yours to decide.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| HyperFrames Catalog | `npx hyperframes add flash-through-white` and `npx hyperframes add data-chart` | Install both blocks into the project, contract-compliant | Two ready-to-use effects wired into `#scene-catalog` | This composition, `/hyperframes-registry` |
| `/hyperframes-registry` skill | A request for a transition and a chart effect | Locate and install the matching catalog blocks | Blocks already correctly timed on the master timeline | The AI agent authoring the scene |
| Composition author | The installed blocks plus original card styling | Frame the effects with custom CSS and GSAP pop-in animation | The finished `#scene-catalog` section shown above | The rendered video, readers of this series |

Next stop: not every current is friendly — the jellyfish forest is where rendering gets complicated, and where quality presets, Docker mode, and GPU acceleration actually matter.
