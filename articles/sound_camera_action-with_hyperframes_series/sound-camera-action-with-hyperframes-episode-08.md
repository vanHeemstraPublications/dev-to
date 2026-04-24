---
title: "Sound, Camera, Action! 🎬 Ep.8"
published: false
description: "Episode 8: The AI script writer joins the crew. HyperFrames was designed from day one to be agent-native — the skills system, the non-interactive CLI, the Catalog of 50+ ready-made blocks, and the prompting guide that turns any coding agent into a video director. The complete workflow."
tags: [javascript, html, ai, video]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/sound_camera_action_with_hyperframes_series/sound-camera-action-with-hyperframes-episode-08.png"
series: "Sound, Camera, Action with HyperFrames Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: The AI Script Writer

> "The director gives the script writer a brief. The script writer returns a screenplay. The director hands it to the crew. The crew shoots the film. Nobody types a command twice."

## The AI Writer Joins the Set 🤖

Hollywood has long used script doctors — writers brought in to sharpen dialogue, punch up jokes, or fix structural problems in a screenplay. The director has a vision; the script doctor has the craft to express it on the page quickly.

In HyperFrames, the AI agent is the script doctor. You have a brief: "a 10-second product intro with a fade-in title and ambient music." The agent has the craft: it knows the HyperFrames composition grammar, the GSAP patterns, the three rules, the common mistakes to avoid. It writes the screenplay — the `index.html` — and hands it to the CLI. The CLI renders the film.

HyperFrames was designed from the ground up for this workflow. The composition format is plain HTML — the medium LLMs are most deeply trained on. The CLI is non-interactive by default — every input is a flag, output is plain text, failures are non-zero exit codes. There is no GUI the agent cannot operate, no interactive prompt it cannot answer.

## 🗂️ SIPOC — The AI Script Writer

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| You (the director) | A creative brief: what the video should show, how long, what style | Prompt your coding agent using /hyperframes skill context | A valid index.html composition with GSAP, clips, and timelines | npx hyperframes preview then render — the agent runs both |
| The HyperFrames skills system | npx skills add heygen-com/hyperframes | Skills encode framework-specific patterns as slash commands | /hyperframes, /hyperframes-cli, /gsap — agent invokes them to produce correct output | The agent — skill context prevents the most common mistakes |
| The Catalog | 50+ pre-built blocks (social overlays, transitions, data visualisations, effects) | Browse at hyperframes.heygen.com/catalog or install with CLI | Ready-to-use composition fragments the agent can reference or import | Your composition — builds on proven, tested building blocks |
| The non-interactive CLI | Composition file, flags | Agent runs npx hyperframes render --docker --quiet --output out.mp4 without prompts | output.mp4 with predictable stdout/stderr the agent can parse | You — receive the rendered video without manual intervention |

## Installing the Skills: Teaching the Agent the Grammar 📚

HyperFrames provides a skills package that teaches your AI agent the composition grammar, GSAP patterns, and CLI commands. Install once:

```bash
npx skills add heygen-com/hyperframes
```

This registers three slash commands in Claude Code (and equivalent context in Cursor, Codex, and Gemini CLI):

| Slash command | What it loads |
| --- | --- |
| /hyperframes | Composition authoring: the three rules, data-* attributes, clip types, GSAP setup, common mistakes |
| /hyperframes-cli | CLI commands: init, preview, lint, render, compositions, doctor, all flags |
| /gsap | GSAP-specific patterns: tl.from, tl.to, position parameter, stagger, eases, the extend trick |

Invoking the slash command at the start of a prompt loads the skill context explicitly, which produces correct output on the first attempt rather than after several corrections.

## The Prompting Guide: Directing the AI 🎬

The key to effective agent-driven composition authoring is treating the agent exactly like a human script writer: give a clear brief, specify the constraints, reference the tools available.

### Cold start — describe the video from scratch

```
Using /hyperframes, create a 10-second product intro video (1920x1080) with:
- Dark background (#0a0a1a)
- A product name "DataPulse" in 96px white Georgia serif, centred, fades in at t=0
- A tagline "Real-time analytics for teams" in 36px grey, fades in at t=1
- A background ambient music track at 25% volume from assets/ambient.wav
- The title and tagline fade out at t=8.5
- Render as output.mp4
```

### Warm start — turn existing content into a video

```
Using /hyperframes, summarise the attached PDF (our Q4 report) into a
45-second pitch video. Use a 1920x1080 canvas with a dark navy background.
Show key metrics as large bold text with stagger reveal animations.
Each page of the PDF becomes one scene; use relative timing so
extending one scene doesn't break the others.
```

### Format-specific — social media

```
Using /hyperframes, make a 9:16 TikTok-style hook video (1080x1920) about
the benefits of open-source software. 6 seconds. Large bold text, punchy words
staggering in with back.out eases. Bright red CTA button at the bottom sliding
up at t=4. No background footage — solid dark background only.
```

### Iterate like a film director

```
The title is too small — make it 2x bigger.

Add a horizontal red rule line under the title that animates from scaleX=0 to 1
over 0.6 seconds at t=0.8.

The CTA needs a pulse effect — scale to 1.05 and back twice after it appears.

Change the background to a subtle gradient from #1a0533 to #0d0d2b top-to-bottom.
```

Each of these is a single sentence. The agent reads the current `index.html`, applies the change, and previews or re-renders. This is the edit loop — director and script doctor working together.

## The Catalog: The Prop Master's Warehouse 🗄️

The Catalog at `hyperframes.heygen.com/catalog` contains 50+ ready-to-use blocks — pre-built composition fragments for the most common video elements. Each block is a snippet of HTML, CSS, and GSAP the agent can import directly or customise.

Categories of blocks available:

| Category | Example blocks |
| --- | --- |
| Social overlays | Instagram follow button, YouTube subscribe card, TikTok username lower third, LinkedIn profile card |
| Text effects | Typewriter reveal, letter stagger, word-by-word fade, kinetic text shake |
| Transitions | Cross-fade, iris wipe, slide wipe, zoom in/out |
| Data visualisations | Animated bar chart, count-up number, progress ring, percentage reveal |
| Cinematic effects | Film grain overlay, vignette, letterbox crop, chromatic aberration |
| Lower thirds | News bar, name card, broadcast-style ticker, minimal subtitle strip |
| Call to action | Pulse button, bouncing arrow, subscribe bell animation, link card |

### Using a Catalog block with an agent

```
Using /hyperframes, add the Instagram follow button block from the Catalog
to the bottom-right of our current composition at t=5, for 4 seconds.
The username should be "@datapulse_app".
```

The agent fetches the Catalog block template, customises the username, positions it correctly, and adds it to `index.html` at the right track index and timing.

### Browsing and installing blocks

```bash
# List all available Catalog blocks
npx hyperframes catalog list

# Preview a specific block in the browser
npx hyperframes catalog preview instagram-follow

# Add a block to your composition (copies the block HTML to clipboard or stdout)
npx hyperframes catalog add instagram-follow
```

## A Complete Agent-Driven Workflow: From Brief to MP4 🎬

Here is a complete, reproducible workflow for AI-driven video production — from brief to rendered file, using Claude Code as the agent:

### Step 1: Install skills (once per machine)

```bash
npx skills add heygen-com/hyperframes
```

### Step 2: Initialise the project

```bash
npx hyperframes init product-launch --non-interactive --example blank
cd product-launch
```

### Step 3: Open the project in your agent

```bash
# Claude Code:
claude

# Or Cursor, Codex, Gemini CLI — all work the same way
```

### Step 4: Brief the agent

```
Using /hyperframes, create a 15-second product launch video (1920x1080):

Visual style: dark (#0d0d1a) background with a subtle blue gradient
Font: Arial Black throughout

Timeline:
- 0–4s: "Introducing" in 56px grey fades in, then "DataPulse" in 96px white
  slides up from below at t=0.5. Both fade out at t=3.5.
- 4–10s: Three feature cards stagger in (left, centre, right):
  "Real-time" / "Collaborative" / "Scalable"
  Each is a white rounded card with a feature title in 40px dark text.
  Cards slide up from y=100 with stagger 0.15s, ease back.out.
  They all fade out at t=9.
- 10–15s: CTA screen — red background (#e94560), "Get started free"
  in 88px white bold, and the URL "datapulse.io" in 44px below.
  Both punch in with scale from 0.5 at t=10.3.

Assets: no video or audio files needed.
After writing the composition, run npx hyperframes lint to check it,
then npx hyperframes preview so I can review it.
```

The agent writes `index.html`, runs `lint`, and opens the preview. You review in the browser.

### Step 5: Iterate

```
The three cards need more padding — 32px on all sides.
The URL text should be white at 70% opacity, not full white.
Add a subtle GSAP pulse to the red CTA background — animate
background-color between #e94560 and #c73550 every 1.5 seconds.
```

### Step 6: Render

```
Using /hyperframes-cli, render this composition:
- Docker mode for reproducibility
- Quality: high
- Output: product-launch-final.mp4
- Quiet mode
Tell me the file size and duration when done.
```

The agent runs:

```bash
npx hyperframes render \
  --docker \
  --quality high \
  --output product-launch-final.mp4 \
  --quiet
```

And reports back:

```
product-launch-final.mp4 rendered successfully.
Duration: 15.0s | Resolution: 1920x1080 | Size: 24.3 MB
```

## What the Skills Prevent: Common Agent Mistakes 🚫

Without the skills, agents commonly make these mistakes. The skills encode corrections:

| Mistake | What happens | Skills correction |
| --- | --- | --- |
| gsap.timeline() without { paused: true } | Animation races at wall-clock speed during render | Skill explicitly states: always { paused: true } |
| Wrong key in window.__timelines | Engine cannot find timeline — no animation | Skill: key must match data-composition-id on root |
| Forgetting class="clip" on timed elements | Elements always visible, not lifecycle-managed | Skill: every timed element needs class="clip" |
| data-duration omitted on <img> | Image has no duration — never appears | Skill: data-duration is required for images |
| Animating <video> dimensions directly | Browser stops rendering frames | Skill: wrap <video> in a <div>, animate the wrapper |
| Manually nesting sub-timelines | Duplicate nesting conflicts with engine | Skill: never masterTL.add(subTL) — engine does it |
| Using data-start without a reference clip having a known duration | Timing resolver throws an error | Skill: referenced clip must have explicit or source duration |
| Timeline ends before composition media | Video cuts off early | Skill: always tl.set({}, {}, totalDuration) to extend |

## The Website-to-Video Workflow 🌐

One of HyperFrames' most powerful agent-native features: turning any existing web page into a video.

```
Using /hyperframes, take a look at https://datapulse.io/features
and create a 30-second video that:
1. Shows each feature section of the page as a 5-second scene
2. Animates the transition between sections with a slide-up wipe
3. Adds a data-driven animated counter for the "10x faster" stat
4. Includes the logo in the bottom right throughout
```

Because HyperFrames compositions are plain HTML, the agent can paste a page's CSS directly into the composition and animate its existing elements without rewriting them as JSX components. What would require significant translation work in Remotion takes the agent minutes in HyperFrames.

## The Full Series Map: The Complete Production 🎬

Eight episodes, one complete craft school:

| # | Episode | Film role | HyperFrames concept |
| --- | --- | --- | --- |
| 1 | Lights, Camera, HyperFrames! | Director's first day | Install, philosophy, first composition |
| 2 | The Screenplay | Script writer | HTML anatomy, data-* attributes, clip types |
| 3 | Casting and Timing | Continuity supervisor | Track indices, relative timing, gaps, overlaps |
| 4 | The VFX Department | Special effects crew | GSAP, paused timelines, stagger, eases, mistakes |
| 5 | The Cutting Room | Film editor | Video B-roll, audio mixing, transparent MOV |
| 6 | The Second Unit | Parallel production | Nested compositions, data-composition-src, project structure |
| 7 | Rolling! | Camera crew + DI | Render modes, quality, GPU, workers, CI/CD |
| 8 | This one — The AI Script Writer | AI on set | Skills, Catalog, agent workflow, prompting guide |

## Getting Started Today 🎬

```bash
# 1. Install HyperFrames + skills
npx hyperframes init my-film --non-interactive --example blank
cd my-film
npx skills add heygen-com/hyperframes

# 2. Open in your agent and describe your video
# "Using /hyperframes, create a 10-second intro with..."

# 3. Preview
npx hyperframes preview

# 4. Render
npx hyperframes render --docker --output my-film.mp4

# 5. Distribute
# The director's cut is ready.
```

The brief is yours. The grammar is learned. The crew is assembled. The camera is rolling.

**Sound. Camera. Action.**

**🔗 Resources**

- **HyperFrames home**: [hyperframes.heygen.com](https://hyperframes.heygen.com)
- **The Catalog**: [hyperframes.heygen.com/catalog](https://hyperframes.heygen.com/catalog)
- **Prompting Guide**: [hyperframes.heygen.com/guides/prompting](https://hyperframes.heygen.com/guides/prompting)
- **Skills package**: `npx skills add heygen-com/hyperframes`
- **GitHub**: [github.com/heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)
- **Website-to-Video Guide**: [hyperframes.heygen.com/guides/website-to-video](https://hyperframes.heygen.com/guides/website-to-video)

*🎬 Sound, Camera, Action with HyperFrames Series — a film director's guide to rendering videos with HTML and JavaScript. Open-source. No React required.*