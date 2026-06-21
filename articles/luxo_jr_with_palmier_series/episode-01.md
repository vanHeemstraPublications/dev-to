---
title: "Luxo Jr. with Palmier! Ep.1: Two Lamps in One Desk Lamp"
published: false
description: "Episode 1: In 1986, a small desk lamp bounced across a Pixar test stage and changed animation forever. In 2026, a small MCP server bounces across your timeline and changes video editing. This episode introduces Palmier Pro through the lens of Luxo Jr. — the curious little lamp, the steady big lamp, and the light they make together."
tags: [ai, videoediting, mcp, creativity]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/luxo-jr-palmier-episode-01.png"
series: "Luxo Jr. with Palmier"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

# Luxo Jr. with Palmier! 💡
## Episode 1: Two Lamps in One Desk Lamp

---

## A Lamp Learns to Bounce

In 1986, a young animation studio called Pixar released a ninety-second short film with no dialogue, no plot in the traditional sense, and no characters in the traditional sense either — just two desk lamps. A big one. A small one. A rubber ball.

The small lamp — *Luxo Jr.* — bounces in, curious, full of energy, and starts playing with the ball. It deflates the big ball with an enthusiastic leap. It finds a smaller ball instead. It bounces on that one too, gleefully, undeterred, full of the same restless creative joy. The big lamp watches. Doesn't take over. Doesn't scold. Just stays lit, steady, present — illuminating the desk so the small one has somewhere safe to play.

That ninety-second film is, by wide consensus, the moment computer animation proved it could carry genuine character and emotion through nothing but light, motion, and craft. It is also, unexpectedly, the perfect way to understand what happens when you open **Palmier Pro** and connect an AI agent to its timeline through MCP.

You are the big lamp. Steady. Present. Holding the creative vision. Your agent is Luxo Jr. — bouncing, eager, generating clips, trying ideas, occasionally overreaching and finding the right-sized ball. And the desk between you, lit by both of you together, is the timeline.

---

## 🗂️ SIPOC — The Two-Lamp Workspace

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Palmier Pro (the big lamp) | A macOS 26 (Tahoe) machine, raw and generated footage | Native Swift app built on AVFoundation + Metal renders a multi-track timeline | A real-time, frame-accurate editing surface | The editor — who finally has somewhere to put the light |
| Generative AI models (the rubber ball) | Text prompts, reference images, existing clips | Seedance, Kling, and Nano Banana Pro generate video/image/audio directly inside the project | New footage that lives natively on the timeline, no import/export needed | The same timeline — instantly, without leaving the app |
| MCP server (Luxo Jr.'s hidden wiring) | A running Palmier Pro project, an MCP-capable agent (Claude Code, Codex, Cursor, Claude Desktop) | Expose the project's tools over `http://127.0.0.1:19789/mcp` | A live, addressable timeline that an agent can read, generate into, and edit | Your AI agent — who can now bounce around your project on its own |
| The human editor (the big lamp) | Creative intent, taste, final judgment | Direct the agent, review its bounces, keep the light steady | A finished, intentional cut | The eventual audience — who never sees any of this, only the result |

---

## What Palmier Pro Actually Is

Strip away the lamp metaphor for one paragraph of plain technical honesty: Palmier Pro is an open-source macOS video editor, built from scratch in Swift on top of AVFoundation and Metal, with Premiere Pro as its north star for editing fundamentals — multi-track compositing, trim, split, razor, ripple delete, speed, opacity, transform, keyframes, frame-accurate playback. What makes it different is that generative AI lives *inside* the timeline rather than on some separate website you tab over to. And what makes *that* interesting for developers specifically is that every open project exposes a local MCP server, which means your coding agent — yes, the same one reviewing your pull requests — can also edit your video.

```
Palmier Pro, the plain-language version:

  Platform:    macOS 26 (Tahoe) — native app, not Electron, not a web wrapper
  Stack:       Swift + AVFoundation (media) + Metal (rendering)
  Editor core: multi-track timeline, keyframes, frame-accurate playback
  Generative:  Seedance, Kling, Nano Banana Pro — generate INSIDE the project
  Agent layer: a local MCP server per open project
                http://127.0.0.1:19789/mcp
  Open source: the editor AND the MCP server (GPL-3.0)
  NOT open:    the generative AI processing itself (runs as a hosted service)
```

---

## The Architecture, Drawn as a Desk

```
┌──────────────────────────────────────────────────────────────────────┐
│                         YOUR macOS DESK                             │
│                                                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              Palmier Pro (the big lamp)                     │   │
│   │                                                               │   │
│   │   ┌───────────────────────────────────────────────────────┐ │   │
│   │   │              The Timeline (the desk surface)           │ │   │
│   │   │                                                         │ │   │
│   │   │   track 1: ▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭     │ │   │
│   │   │   track 2:     ▭▭▭▭▭▭▭▭         ▭▭▭▭▭▭▭▭▭▭▭▭▭          │ │   │
│   │   │   track 3:              ▭▭▭▭▭▭▭▭▭▭                     │ │   │
│   │   │                                                         │ │   │
│   │   │   AVFoundation playback engine — frame-accurate          │ │   │
│   │   │   Metal compositing — multi-track render                 │ │   │
│   │   └───────────────────────────────────────────────────────┘ │   │
│   │                                                               │   │
│   │   ┌───────────────────────────────────────────────────────┐ │   │
│   │   │     Generative AI (the rubber ball, Episode 3)         │ │   │
│   │   │     Seedance · Kling · Nano Banana Pro                  │ │   │
│   │   └───────────────────────────────────────────────────────┘ │   │
│   │                                                               │   │
│   │   ┌───────────────────────────────────────────────────────┐ │   │
│   │   │     MCP server (Luxo Jr.'s hidden wiring, Ep. 4)        │ │   │
│   │   │     http://127.0.0.1:19789/mcp                          │ │   │
│   │   └───────────────────────┬───────────────────────────────┘ │   │
│   └─────────────────────────────┼─────────────────────────────────┘   │
│                                 │ MCP (HTTP)                          │
│         ┌──────────────────────┼──────────────────────┐              │
│         ▼                      ▼                      ▼              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────────┐      │
│  │ Claude Code │      │   Cursor    │      │ Claude Desktop   │      │
│  │ (Luxo Jr.)  │      │ (Luxo Jr.)  │      │  (Luxo Jr.)      │      │
│  └─────────────┘      └─────────────┘      └─────────────────┘      │
│                                                                       │
│         All three are the SAME small lamp, just bouncing in           │
│         through different doors. They all reach the same desk.       │
└──────────────────────────────────────────────────────────────────────┘
```

Notice the shape of that diagram: the MCP server sits at the bottom of Palmier Pro, not bolted onto the side. It is not a plugin pretending to understand the timeline from the outside — it *is* the same surface, exposed. When your agent generates a clip, organizes footage, or trims a cut through MCP, it is doing the literal same operation a human would do by clicking inside the app. There is no shadow API, no second source of truth. One desk. Two lamps. Same light.

---

## Why This Comparison Isn't Just Cute

It would be easy to dismiss the Luxo Jr. framing as decoration. It isn't, and here's the specific reason: the original short's entire emotional arc is about **scale-appropriate enthusiasm**. Luxo Jr. doesn't get told to stop playing. It gets shown a ball it can actually handle. That is, with uncanny precision, the design philosophy a good MCP integration needs.

An AI agent connected to your video project via MCP is going to be enthusiastic. It will want to generate things, reorganize things, try ideas. The question every tool-builder faces is not "how do we make the agent more powerful" — it's "how do we make sure the ball it's given fits the room it's playing in." Palmier Pro's MCP server, as we'll see across this series, answers that question by exposing scoped, specific tools — generate this clip, trim this range, organize this footage — rather than handing the agent a deflated giant ball labeled "full filesystem access, good luck."

---

## What You'll Need on Your Desk

```
Requirements to follow along with this series:

  macOS:          26 (Tahoe) or later — Palmier Pro's stated minimum
  Download:       github.com/palmier-io/palmier-pro/releases/latest
                    (look for PalmierPro.dmg)
  Optional:        an Anthropic API key, if you want the in-app side-chat
                    (Episode 6) in addition to an external MCP agent
  MCP client:      one of —
                     Claude Code
                     Codex
                     Cursor
                     Claude Desktop (bundled .mcpb one-click install)
```

---

## The Series Ahead

| # | Episode | The Lamp Moment | What We Cover |
|---|---|---|---|
| 1 | *This one* — Two Lamps in One Desk Lamp | The opening shot | What Palmier Pro is, the architecture, the metaphor |
| 2 | The Desk Is the Timeline | Setting the stage | Multi-track compositing, trim/split/razor, keyframes |
| 3 | The Ball That Glows | Luxo Jr. finds the ball | Generative AI inside the timeline — Seedance, Kling, Nano Banana Pro |
| 4 | Plugging In Luxo Jr. | The wiring under the desk | The MCP server itself, connecting every agent client |
| 5 | Teaching the Small Lamp to Bounce | Luxo Jr. learns the moves | MCP tools in practice — generate, edit, organize, transcribe |
| 6 | A Second Conversation With the Same Lamp | A quieter corner of the desk | The side-chat panel, your own Anthropic key |
| 7 | Two Lamps, One Light Source | What's open, what's borrowed | Open source boundary, exporting to Premiere/Resolve |
| 8 | The Final Pull-Back Shot | The lamps both light up | A full real workflow, start to finish, human and agent together |

In **Episode 2**, we step onto the desk itself — the timeline — and get our hands on the editing fundamentals Palmier Pro built from scratch in Swift: multi-track compositing, trims, splits, ripple deletes, and the keyframes that make a static clip start to breathe.

*The lamp bounces once, testing the floor. The light holds steady.*

---

**🔗 Resources**
- **Palmier Pro on GitHub**: [github.com/palmier-io/palmier-pro](https://github.com/palmier-io/palmier-pro)
- **Download**: [github.com/palmier-io/palmier-pro/releases/latest](https://github.com/palmier-io/palmier-pro/releases/latest)
- **Palmier Pro website**: [palmier.io](https://www.palmier.io)
- **Pixar's *Luxo Jr.* (1986)**: the film that inspired this whole series's sense of scale and steadiness

---

*💡 Luxo Jr. with Palmier — one big lamp, one small lamp, one timeline lit together.*
