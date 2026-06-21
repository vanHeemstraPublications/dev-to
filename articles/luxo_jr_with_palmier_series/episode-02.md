---
title: "Luxo Jr. with Palmier! Ep.2: The Desk Is the Timeline"
published: false
description: "Episode 2: Before any lamp can bounce, there needs to be a surface sturdy enough to bounce on. This episode walks the actual editing fundamentals Palmier Pro built from scratch in Swift — multi-track compositing, trim, split, razor, ripple delete, speed, opacity, transform, and the keyframes that turn a flat clip into something with a pulse."
tags: [videoediting, swift, macos, creativity]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/luxo-jr-palmier-episode-02.png"
series: "Luxo Jr. with Palmier"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

# Luxo Jr. with Palmier! 💡
## Episode 2: The Desk Is the Timeline

---

## A Sturdy Desk First, Then the Bouncing

Watch *Luxo Jr.* again and notice something easy to miss on a first viewing: the desk itself never wobbles. The ball bounces. The little lamp leaps, overreaches, stumbles. But the surface beneath all of that chaos is rock solid, lit evenly, completely dependable. That dependability is what lets the playfulness above it feel safe rather than reckless.

A video editor is the same kind of surface. Before any generative AI model conjures a single frame, before any agent touches a single clip through MCP, there has to be a timeline you can actually trust — one that plays back exactly the frame you scrubbed to, that trims exactly where you marked, that doesn't introduce a sync drift three cuts later because something rounded incorrectly. Palmier Pro's answer to "can we trust this desk" is built from scratch in Swift on AVFoundation and Metal, with Adobe Premiere Pro as its explicitly stated north star for editing fundamentals.

This episode is the desk, with no lamps bouncing on it yet.

---

## 🗂️ SIPOC — The Editing Core

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| AVFoundation (Apple's media framework) | Raw and generated video/audio assets | Decode, sample, and present frames with sample-accurate timing | A playback engine that knows exactly which frame is on screen at any timestamp | Palmier Pro's timeline UI and its frame-accurate scrubber |
| Metal (Apple's GPU framework) | Multiple overlapping video tracks, transforms, opacity values | Composite tracks in real time on the GPU | A live, multi-track preview that updates as you edit, with no render-and-wait step | The editor — watching the result change as they work, not after they export |
| The editor's actions | Mouse clicks, keyboard shortcuts, drag gestures | Trim, split (razor), ripple delete, change speed/opacity, apply transforms, set keyframes | An edited sequence of clips and parameter changes | The timeline's underlying project state — which both the human and, later, the MCP-connected agent can read and modify |

---

## Multi-Track Compositing: Several Desks Stacked Into One

A single video track is a filing cabinet drawer. Multi-track compositing is the whole cabinet — video on top of video, audio layered beneath both, each track independently editable, all of them rendering together in real time on the GPU via Metal.

```
TIMELINE STRUCTURE — what "multi-track" actually means

  Track 3 (top, visually):   [title card]      [lower-third graphic]
  Track 2 (middle):          [B-roll clip A][B-roll clip B][B-roll clip C]
  Track 1 (bottom, base):    [main interview footage, continuous]
  Audio 1:                   [interview audio, continuous]
  Audio 2:                   [music bed, continuous, lower volume]

  At any given playhead position, Metal composites whichever tracks
  have content there — top track wins where opaque, lower tracks show
  through where the top track is transparent or simply absent.
```

This is the literal desk surface from our metaphor: a flat plane where multiple things can sit at once, lit consistently, with the lamp (Palmier Pro) responsible for making sure nothing flickers or desyncs as you stack more on top.

---

## The Core Edit Operations

```
TRIM
  Drag a clip's edge to shorten or lengthen its visible range
  without moving where it sits on the timeline.

  Before: [=========clip=========]
  After:  [====clip====]            (trimmed from the right edge)


SPLIT / RAZOR
  Cut one clip into two independent clips at the playhead position.
  Each half can now be edited, moved, or deleted separately.

  Before: [===========clip===========]
                       ▲ playhead
  After:  [====clip A====][====clip B====]


RIPPLE DELETE
  Remove a clip AND close the gap it leaves behind, shifting
  everything after it earlier — as opposed to a plain delete,
  which would leave a hole.

  Before: [clip A][clip B][clip C]
  Ripple delete clip B:
  After:  [clip A][clip C]          ← clip C shifted left to close the gap


SPEED
  Change playback rate of a clip independent of the rest of
  the timeline — slow motion, time-lapse, or a quick punch-in.

  100% speed: [=====clip plays at normal rate=====]
  50% speed:  [=====clip plays twice as long, half as fast=====]


OPACITY
  Blend a clip with what's beneath it on lower tracks —
  the mechanism behind dissolves, overlays, and watermarks.

  100% opacity: fully covers tracks below
    50% opacity: half-transparent, tracks below show through
     0% opacity: fully transparent, invisible


TRANSFORM
  Reposition, scale, or rotate a clip's visible frame within
  the canvas — picture-in-picture, pan-and-scan, reframing.
```

Every one of these is a primitive the rest of the series depends on. When Episode 5 shows an MCP-connected agent "trimming footage" or "organizing clips," it is invoking these exact same operations — there is no separate, simplified "AI version" of trim. The small lamp uses the same tools as the big one.

---

## Keyframes: Giving a Static Value a Pulse

A clip with one opacity value all the way through is flat — present, but inert. Keyframes are how you give any parameter a timeline of its own, so it changes *as* the clip plays rather than sitting fixed.

```
KEYFRAMES ON THE OPACITY PARAMETER

  Time:        0s        1s        2s        3s
  Opacity:    [0%] ───── [100%] ──────────── [100%] ──── [0%]
               ▲                                          ▲
          keyframe: fade in                      keyframe: fade out
          (0% at 0s, ramping
           to 100% by 1s)

  Between keyframes, Palmier Pro interpolates automatically —
  you set the moments that matter, the engine fills in the motion.
```

This is, not coincidentally, the exact animation principle that made the original *Luxo Jr.* short possible in the first place: you don't hand-draw every single frame of the lamp's bounce. You set key positions — fully compressed at the bottom of the bounce, fully extended at the peak — and let interpolation carry the motion between them. Pixar's animators were keyframing a lamp's leap in 1986. Palmier Pro's editors are keyframing a clip's opacity, scale, or position in exactly the same conceptual sense, four decades later, on the same underlying idea.

---

## Frame-Accurate Playback: Why "Close Enough" Isn't Good Enough

```
THE PROBLEM FRAME-ACCURACY SOLVES

  A 30fps clip has a new frame every 33.33ms.
  If your scrubber, your trim handles, and your export all
  round timestamps slightly differently, a cut that looked
  perfect in preview can land one frame early or late on export.

  Frame-accurate playback means:
    scrub to frame 451  →  see EXACTLY frame 451
    trim at frame 451   →  the cut point IS frame 451
    export              →  frame 451 lands exactly where you set it

  AVFoundation's sample-accurate timing model is what makes this
  guarantee possible — Palmier Pro inherits frame precision from
  the same framework that powers Final Cut Pro's playback core.
```

For a human editor, frame accuracy is the difference between a clean cut and an almost-clean cut. For an MCP-connected agent doing precise trims based on a transcript timestamp (Episode 5 will show exactly this), frame accuracy is the difference between "the agent's cut works" and "the agent's cut is subtly, maddeningly wrong in a way nobody can quite explain." The desk has to be exact, or nothing built on top of it can be trusted.

---

## What This Desk Looks Like, Empty

```
┌──────────────────────────────────────────────────────────────────┐
│  Palmier Pro — Untitled Project                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│            ┌──────────────────────────────────┐                  │
│            │                                  │                  │
│            │         Preview / Canvas          │                  │
│            │      (Metal-composited frame)      │                  │
│            │                                  │                  │
│            └──────────────────────────────────┘                  │
│                                                                    │
│  ◄ ▮▮ ►   00:00:00:00 / 00:00:00:00          [frame-accurate]    │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  Track 3  │                                                       │
│  Track 2  │                                                       │
│  Track 1  │                                                       │
│  Audio 1  │                                                       │
│  Audio 2  │                                                       │
│           └──────────────────────────────────────────────────────│
│             (empty — nothing has bounced onto this desk yet)      │
└──────────────────────────────────────────────────────────────────┘
```

Quiet. Sturdy. Waiting. Exactly how the original short's desk looks for the first three seconds, before anything moves.

---

## What's Next: The Ball That Glows

In **Episode 3**, the desk stops being empty. We bring in the rubber ball — Palmier Pro's built-in generative AI, where Seedance, Kling, and Nano Banana Pro generate video and images directly inside this same timeline, with no import, no export, no separate website tab. The first bounce is about to happen.

---

**🔗 Resources**
- **AVFoundation**: [developer.apple.com/av-foundation](https://developer.apple.com/av-foundation/)
- **Metal**: [developer.apple.com/metal](https://developer.apple.com/metal/)
- **Palmier Pro features**: [github.com/palmier-io/palmier-pro#features](https://github.com/palmier-io/palmier-pro#features)

---

*💡 Luxo Jr. with Palmier — one big lamp, one small lamp, one timeline lit together.*
