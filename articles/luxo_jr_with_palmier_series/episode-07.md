---
title: "Luxo Jr. with Palmier! Ep.7: Two Lamps, One Light Source"
published: false
description: "Episode 7: Not everything that makes light needs to be visible to see how it works. This episode looks at the boundary Palmier Pro draws between what is genuinely open source -- the editor and the MCP server, under GPL-3.0 -- and what runs as a hosted service -- the generative AI processing itself -- and follows a finished cut out the door via MP4, ProRes, and NLE XML export."
tags: [opensource, videoediting, gpl, workflow]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/luxo-jr-palmier-episode-07.png"
series: "Luxo Jr. with Palmier"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

# Luxo Jr. with Palmier!
## Episode 7: Two Lamps, One Light Source

---

## Not Every Bulb Needs to Be See-Through

You can take apart a desk lamp and understand exactly how the switch, the cord, and the shade work. The filament glowing inside the bulb is a different matter -- you can see the light it produces perfectly well without the bulb itself being transparent. That's a reasonable design, not a betrayal: the parts you touch and operate are fully inspectable; the part doing the actual incandescent work is sealed for good engineering reasons.

Palmier Pro draws its open-source line in almost exactly that place. The README states it without hedging: "Open source. The video editor and the MCP server are completely open-source. The generative AI processing is not." This episode is about understanding why that's the right boundary, not a disappointing one, and then following a finished cut out of Palmier Pro entirely, into whatever comes next in your pipeline.

---

## SIPOC -- The Open Source Boundary

| Suppliers | Inputs | Process | Outputs | Customers |
|---|---|---|---|---|
| The Palmier Pro project (GPL-3.0) | The editor's Swift source, the MCP server's source | Publish both publicly on GitHub under a copyleft license | A codebase anyone can read, audit, fork, and modify | Developers who want to verify exactly how their timeline and their agent's tool calls actually work |
| The hosted generative service | Seedance, Kling, Nano Banana Pro requests | Run model inference on Palmier's infrastructure, return finished media | Generated video, image, and audio assets | The same open-source editor -- consuming a closed service through an open client |
| The finished project | A completed timeline | Export to a standard interchange or delivery format | An MP4, ProRes file, or NLE XML | Whatever comes next -- a publish step, or a different professional editor entirely |

---

## What's Actually Open, Read Plainly

```
OPEN SOURCE (GPL-3.0, public on GitHub):

  Sources/PalmierPro/      <- the Swift app itself: timeline,
                              compositing, the editing primitives
                              from Episode 2, the UI

  (the MCP server)          <- the tool definitions, the HTTP
                              endpoint logic, everything Episodes
                              4 and 5 walked through calling

  Tests/PalmierProTests/    <- the test suite covering the above

  You can read every trim, every keyframe interpolation, every
  MCP tool's exact parameter schema, line by line, right now.


NOT OPEN SOURCE (hosted, closed):

  The actual model inference for Seedance, Kling, Nano Banana Pro
  -- the part that turns a text prompt into pixels.

  This is consistent with how those models are made available
  everywhere else too: they are not Palmier's models to open-source
  in the first place. Palmier Pro is the open client; the closed
  part is the same closed part everyone using those models works
  with, regardless of which editor they're sitting in.
```

The GPL-3.0 license itself is worth a sentence of plain explanation for anyone newer to open-source licensing: it's a copyleft license, meaning if you take Palmier Pro's source and build a modified version that you distribute to others, your modified version has to stay open under the same terms. It's a license chosen specifically to keep the lamp's visible wiring visible, permanently, for anyone downstream too.

---

## Why This Boundary Is the Honest One

A reasonable worry, raised gently here because it deserves a direct answer rather than a dodge: "open source" can sometimes be used as a marketing word for a project that's mostly a shell around a closed core, with the interesting parts hidden. Is that what's happening here?

The fairest test is simple: can you actually do useful, complete work with only the open parts, with zero dependency on the closed generative service? Looking back at Episodes 2 and 2 alone -- multi-track compositing, trim, split, razor, ripple delete, speed, opacity, transform, keyframes, frame-accurate playback -- the answer is clearly yes. None of that requires Seedance, Kling, or Nano Banana Pro to exist at all. The README's own framing supports this directly: "The video editor without AI is free." The generative layer is a genuinely additive feature bolted onto a complete, independently useful, fully open editor -- not a thin open wrapper hiding the only part that matters.

```
CAN YOU USE PALMIER PRO WITH ZERO GENERATIVE AI INVOLVEMENT?

  Import real footage you shot yourself        -> yes
  Multi-track compositing                      -> yes
  Trim / split / razor / ripple delete          -> yes
  Speed, opacity, transform, keyframes          -> yes
  Frame-accurate playback                       -> yes
  Export a finished cut                         -> yes

  Generate AI video/image/audio inside the timeline  -> this is
  the part that needs the hosted, closed service. Everything
  above it does not.
```

---

## Exporting: Where the Finished Light Goes

A finished cut doesn't have to live inside Palmier Pro forever. Two export paths cover the two realistic destinations: a final delivered file, or a project handed to a different professional NLE entirely.

```
DELIVERY FORMATS (final, watchable files)

  MP4 (H.264)   -- the universal default; smallest files,
                   widest compatibility, the right choice for
                   web delivery, social platforms, quick sharing

  MP4 (H.265)   -- better compression at similar quality than
                   H.264, smaller files for the same fidelity,
                   slightly less universally supported on
                   older playback devices

  ProRes        -- Apple's high-quality, lightly-compressed
                   codec, the standard choice when the file is
                   headed into a further finishing pass (color
                   grading, VFX) rather than straight to an
                   audience


INTERCHANGE FORMAT (project structure, not just pixels)

  NLE XML       -- exports the actual timeline structure: clip
                   positions, trims, multi-track layout -- into
                   a format Premiere Pro and DaVinci Resolve can
                   open directly, preserving the EDIT rather than
                   flattening it into a single video file
```

```
EXPORT DECISION, IN PLAIN TERMS

  "I just need to post this" -> MP4 (H.264)
  "This needs maximum quality for further finishing" -> ProRes
  "I (or a colleague) need to keep editing this in
   Premiere Pro or DaVinci Resolve" -> NLE XML
```

That NLE XML path matters more than it might first appear, precisely because of everything this series has been building toward: a project that started with an MCP-connected agent generating and arranging footage doesn't have to stay locked inside Palmier Pro to be taken seriously by a professional finishing pipeline. The two-lamp collaboration from Episode 1 can hand its finished work off to a third room entirely, structure intact.

---

## What's Next: The Final Pull-Back Shot

Every piece is now on the desk: the editing core, the generative ball, the MCP wiring, four doors and one in-app room for an agent to walk through, and the honest boundary between what's open and what's hosted. In Episode 8, the finale, we run one complete workflow start to finish -- an empty project to an exported cut -- with the human and the agent genuinely collaborating at every step, and close with the lesson the original short was quietly teaching the whole time.

---

**Resources**
- Palmier Pro -- "And more" / open source section: github.com/palmier-io/palmier-pro#and-more
- GNU GPL-3.0: gnu.org/licenses/gpl-3.0.html
- Palmier Pro -- export formats: github.com/palmier-io/palmier-pro

---

*Luxo Jr. with Palmier -- one big lamp, one small lamp, one timeline lit together.*
