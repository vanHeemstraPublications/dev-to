---
title: "Luxo Jr. with Palmier! Ep.3: The Ball That Glows"
published: false
description: "Episode 3: Luxo Jr. finds a ball and the whole short film comes alive. This episode introduces Palmier Pro's built-in generative AI — Seedance, Kling, and Nano Banana Pro generating video and images directly inside the timeline — and the in-line replace workflow that means footage never has to leave the project to become something new."
tags: [generativeai, videoediting, creativity, ai]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/luxo-jr-palmier-episode-03.png"
series: "Luxo Jr. with Palmier"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

# Luxo Jr. with Palmier! 💡
## Episode 3: The Ball That Glows

---

## The Moment the Short Film Comes Alive

For two seconds, *Luxo Jr.* is just a lamp standing on an empty desk. Then the ball rolls in. Everything that makes the film *the film* — the personality, the joy, the small dramatic arc about a creature finding something the right size to play with — happens because of that ball. The desk was necessary. The ball is where the story actually lives.

Palmier Pro's desk, as we built it in Episode 2, is necessary too — sturdy, frame-accurate, multi-track. But the part that makes people sit up is the ball: built-in generative AI that produces real video and image content using state-of-the-art models — Seedance, Kling, Nano Banana Pro — without ever leaving the timeline you're already working in.

---

## 🗂️ SIPOC — Generative AI on the Timeline

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Seedance, Kling, Nano Banana Pro (the hosted generative models) | Text prompts, reference images, existing project footage | Generate new video clips, still images, or variations directly from a prompt panel inside Palmier Pro | New media assets that land in the project's media pool, ready to drop onto the timeline | The timeline — which can use generated footage exactly like imported footage |
| The project's media pool | All footage — generated and imported, side by side | Treat both kinds of footage as first-class citizens with no format distinction | A single unified library, no "generated" vs "real" folder split | The editor — who edits by what looks right, not by where a clip came from |
| In-line replace | An existing clip on the timeline, a new generation request | Swap the underlying media for a clip without rebuilding its trims, transforms, or position | The same edit, instantly re-skinned with new footage | The timeline's structure — preserved untouched through the swap |

---

## Why "Inside the Timeline" Is the Whole Point

Every generative video tool before this category existed worked the same frustrating way: open a website, write a prompt, wait, download an MP4, open your actual editor, import the file, drop it on the timeline, realize the timing is off by a beat, tab back to the website, regenerate, download again, re-import again. Palmier Pro's README states the alternative plainly: *"All footage lives inside the same project. Regenerate and edit clips without the back-and-forth import/export to your timeline editor."*

```
THE OLD WAY (separate generation platform + separate editor)

  Browser tab: type prompt → generate → wait → download .mp4
       │
       ▼
  Finder: locate download → drag into editor's import dialog
       │
       ▼
  Editor: import → place on timeline → notice it's 0.4 seconds
          too long → ...back to the browser tab. Again.


THE PALMIER PRO WAY (generation lives ON the timeline)

  Timeline: select a gap, or an existing clip → open prompt panel
       │
       ▼
  Generate → clip appears directly in the project's media pool
       │
       ▼
  Drop it where it belongs, or it's already in-line →
       Don't like the take? Regenerate. Same slot. Same prompt panel.
       No browser tab. No download. No re-import.
```

---

## The Three Models, At a Glance

```
SEEDANCE        — text-to-video and image-to-video generation
KLING           — text-to-video, strong on motion coherence and longer clips
NANO BANANA PRO — image generation/editing, useful for stills, frames,
                   reference plates, and thumbnail-style assets

All three are accessed through the SAME prompt panel inside Palmier Pro.
The editor doesn't need to know which API format each model expects —
Palmier Pro's generative layer normalizes the request, the same way
its MCP server (Episode 4) normalizes tool calls for any agent client.
```

This is worth dwelling on for a moment: state-of-the-art generative models change constantly — new versions ship, new providers emerge, benchmarks shift month to month. By keeping the model selection inside the app rather than baked into your individual workflow scripts, Palmier Pro absorbs that churn so your *editing process* doesn't have to change every time a new model wins the month.

---

## In-Line Replace: Editing the Idea, Not Just the Clip

The feature that turns "generate stuff" into "iterate on a cut" is in-line replace — swapping a clip's underlying footage while keeping every edit you already made to it: its trim points, its transform, its position relative to everything else on the timeline.

```
BEFORE IN-LINE REPLACE

  Timeline position:  00:00:12:00 — 00:00:15:00
  Clip:                "city-skyline-take-1.mp4" (generated via Kling)
  Trim:                in at 0:01, out at 0:04 of the source
  Transform:           scaled 110%, positioned center
  Opacity keyframes:   fade in over first 12 frames


AFTER IN-LINE REPLACE (new generation, same slot)

  Timeline position:  00:00:12:00 — 00:00:15:00     ← unchanged
  Clip:                "city-skyline-take-2.mp4" (regenerated, different prompt nuance)
  Trim:                in at 0:01, out at 0:04 of the source     ← unchanged
  Transform:           scaled 110%, positioned center             ← unchanged
  Opacity keyframes:   fade in over first 12 frames                ← unchanged

  Only the underlying pixels changed. Every decision you made
  ABOUT those pixels — when they appear, how long, how they're
  framed — survives the swap completely intact.
```

Without in-line replace, regenerating a clip means redoing every trim and transform from scratch. With it, you can treat a generated clip the way you'd treat a take from a real shoot — keep auditioning different takes in the exact same slot until one feels right, without the editorial work resetting each time.

---

## A Worked Example: Building a Shot From Nothing

```
GOAL: a five-second establishing shot of rain on a city window,
       to open a short scene. No footage exists for this yet.

Step 1 — Open the prompt panel, select Kling (motion coherence matters
         here — rain needs convincing continuous movement)

Step 2 — Prompt:
  "Slow rain streaking down a window pane, blurred city lights
   bokeh in the background, night, moody blue tone, 5 seconds"

Step 3 — Generate. The clip lands in the media pool, NOT yet on
         the timeline — it's a candidate, not a commitment.

Step 4 — Drag it onto Track 1 at the very start of the sequence.
         Trim its tail by half a second so it lands exactly on
         a beat in the music track beneath it (Episode 2's trim
         tool, used on generated footage exactly like real footage).

Step 5 — Not quite moody enough? Re-open the prompt panel,
         tweak the wording, regenerate. In-line replace swaps the
         footage in that exact timeline slot. The trim from Step 4
         survives untouched.

Step 6 — Add an opacity keyframe fade-in over the first eight frames
         (Episode 2's keyframe tool) so the shot doesn't snap in
         too abruptly.

Total round trips to a separate website: zero.
```

That's the entire creative loop the ball-on-the-desk metaphor is reaching for: something genuinely playful and a little unpredictable (a generative model's output) interacting directly with something genuinely solid and precise (the timeline's editing tools), in the same physical space, without a door in between.

---

## What's Next: Plugging In Luxo Jr.

Generation and editing now share a desk. But so far, only the human is doing the bouncing — clicking the prompt panel, dragging clips, setting keyframes. In **Episode 4**, we plug in the actual small lamp: Palmier Pro's MCP server, running locally per project at `http://127.0.0.1:19789/mcp`, and the four different doors — Claude Code, Codex, Cursor, Claude Desktop — through which an AI agent can walk in and start bouncing on this same desk for itself.

---

**🔗 Resources**
- **Palmier Pro — Built-in Generative AI**: [github.com/palmier-io/palmier-pro#built-in-generative-ai](https://github.com/palmier-io/palmier-pro#built-in-generative-ai)
- **Palmier Pro website**: [palmier.io](https://www.palmier.io)

---

*💡 Luxo Jr. with Palmier — one big lamp, one small lamp, one timeline lit together.*
