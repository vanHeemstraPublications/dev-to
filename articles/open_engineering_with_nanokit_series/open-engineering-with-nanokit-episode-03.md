---
title: "Open Engineering with Nano Kit 🧭 Ep.3"
series: "Open Engineering with Nano Kit"
part: 3
organization: "the-software-s-journey"
tags: [open-engineering, nanokit, navigation, information-architecture, live-editing]
---

## Episode 3: Mapping the Navigation

A hero section can explain the ecosystem in one glance, but a visitor still needs a way to walk into it. This is the point where the draft page from Episode 2 gets a proper set of doors: Platform, Architecture, Operating Systems, Applications, and the supporting sections around them.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Ecosystem architect | The recommended site structure (Platform, Architecture, Operating Systems, Applications, Conventions, Documentation, Registry, Community, Blog) | Lay out top-level navigation and nested sub-pages to match | A navigation tree mirroring the GitHub ecosystem | Site visitors, contributors browsing by topic |
| Nano Kit editor | Generated draft page | Edit anything, anywhere, seeing every change in real time | A restructured page matching the intended information architecture | Content migration step (Episode 4) |
| Platform team | Sub-item lists (Vision, Kernel, Capsules, AI Assistants under Platform; DOS/GOS/ROS/SOS under Operating Systems) | Decide which items become top navigation and which become sub-pages | A two-level navigation depth that stays scannable | First-time and returning visitors alike |

### Editing anything, anywhere

Nano Kit's live customization is built around the idea that a page can be edited anywhere, with the result visible immediately rather than after a rebuild step. That is exactly the workflow needed to go from a generic generated draft to the specific tree that already exists on paper: Home, then Platform with its seven children (Vision, Architecture, Kernel, Operating Systems, Capsules, AI Assistants, Applications), then Architecture, Operating Systems, Applications, and the flatter sections, Conventions, Documentation, Registry, Community, Blog.

### Two levels, not five

The recommended structure deliberately keeps most of the depth to two levels: a top-level section and, where needed, a handful of named children under it. Detective OS, Game OS, Runner OS, and Star OS sit directly under Operating Systems; Code Smell Detectives, Repository Detectives, Agility Games, Show Runners, PKI Runners, IAM Runners, and PixStars sit under Applications. Nothing forces a visitor three clicks deep before finding real content.

### Doors that match the diagram

Because this navigation mirrors the very stack shown in the Episode 2 hero illustration, a visitor who paused on that diagram already half-recognizes the menu that follows it. Episode 4 turns to what happens once someone actually opens one of those doors: the GitHub README waiting to become a real page.

