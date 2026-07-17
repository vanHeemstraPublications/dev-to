---
title: "Nemo finds Hyperframes 🐢 Ep.5"
series: "Nemo finds Hyperframes"
part: 5
organization: "the-software-s-journey"
tags: [hyperframes, preview, dev-server, hot-reload, studio]
---

## Episode 5: Crush and Squirt Show You the Preview

"Righteous current, dude." Crush doesn't just narrate the EAC, he lets you feel it in real time — and `npx hyperframes preview` is the same instinct built into a dev server. Run it inside the repository and the HyperFrames Studio opens the composition in your browser, already playing:

```bash
npx hyperframes preview
```

We had this running the entire time we built the second scene — a mock code editor that types out the composition contract on screen, as a small joke about a video-authoring tool teaching you HTML by showing you HTML. Here's the scene as it exists in `index.html`:

```html
<section id="scene-code" class="scene clip" data-start="4" data-duration="6" data-track-index="0">
  <div class="editor">
    <div class="path">compositions/index.html</div>
    <pre><span class="line" data-l="1">&lt;<span class="tag">div</span> <span class="attr">data-composition-id</span>=<span class="str">"my-video"</span>&gt;</span>
<span class="line" data-l="2">  &lt;<span class="tag">h1</span> <span class="attr">class</span>=<span class="str">"clip"</span> <span class="attr">data-start</span>=<span class="str">"0"</span> <span class="attr">data-duration</span>=<span class="str">"5"</span>&gt;</span>
<span class="line" data-l="3">    Hello, Hyperframes!</span>
<span class="line" data-l="4">  &lt;/<span class="tag">h1</span>&gt;</span>
<span class="line" data-l="5">&lt;/<span class="tag">div</span>&gt;</span></pre>
  </div>
</section>
```

Each `.line` span starts at `opacity: 0` in the CSS, and the timeline reveals them one at a time — a loop instead of five hand-written tween calls:

```javascript
document.querySelectorAll('#scene-code .line').forEach((line, i) => {
  tl.to(line, { opacity: 1, y: 0, duration: 0.35 }, 4.5 + i * 0.35);
});
```

Every time we saved that change to `index.html`, the preview updated on its own — no manual refresh, no rebuild step. Save the file and the studio reloads instantly, the studio equivalent of Squirt catching the current a beat after his dad without ever losing his place in it. That loop — edit, save, watch, adjust the `i * 0.35` stagger until the typing speed actually looked right, edit again — is the whole rhythm of authoring a HyperFrames video, and it's exactly how this scene's timing got tuned: by watching it in the browser, not by calculating it on paper first.

This is also where the composition contract from the previous episode pays for itself. Because every timed element already declares its own `data-start`, `data-duration`, and `data-track-index`, the preview doesn't need to guess what should be on screen at any given moment — it reads the same attributes the eventual render will read, so what we watched in the browser during preview is exactly what Episode 9's render produces later.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Hyperframes CLI | `npx hyperframes preview` invocation | Start the HyperFrames Studio dev server and open the composition in the browser | A live, browser-rendered preview of the composition as it stood after Episode 4 | Developer authoring the code scene |
| File system watcher | Saved changes to `index.html` (new `#scene-code` section, tweaked stagger timing) | Detect the change and trigger a hot reload | An instantly updated preview, no manual refresh | The person tuning the typewriter animation |
| Composition contract (data-* attributes) | Clip timing declared on `#scene-code` and its `.line` spans | Drive both preview playback and eventual render from the same source of truth | Consistent behavior between preview and final render | The rendering pipeline (Episode 9) |

Next stop: before Nemo can be trusted anywhere near the open water, we need to talk about Bruce — and why "fish are friends, not food" is exactly how HyperFrames wants you to think about its AI agent skills.
