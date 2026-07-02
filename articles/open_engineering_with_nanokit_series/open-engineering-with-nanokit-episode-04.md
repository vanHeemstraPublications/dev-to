---
title: "Open Engineering with Nano Kit 📖 Ep.4"
series: "Open Engineering with Nano Kit"
part: 4
organization: "the-software-s-journey"
tags: [open-engineering, nanokit, documentation, content-migration, github]
---

## Episode 4: Turning READMEs into Pages

Most of Open Engineering already exists in writing. It just lives in the wrong format: GitHub README files describing the Detective Operating System, the Game Operating System, the Runner and Star Operating Systems, the convention repositories, PKIStars, PixStars, Code Smell Detectives, and Agility Games. None of that needs to be rewritten from scratch, it needs to be moved.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| GitHub repositories | Existing README files across the ecosystem | Select each README as the source for its corresponding website page | A mapped list of README-to-page conversions | Documentation and Operating Systems sections |
| Nano Kit editor | Raw README content, page structure from Episode 3 | Adapt and format the content directly inside the live editor | Published pages under Platform, Operating Systems, and Applications | Site visitors reading documentation |
| Content owner | House style and terminology (Ontology, Kernel, Capsules) | Review adapted pages for consistency with the rest of the ecosystem | Consistent voice across pages sourced from different repositories | Contributors comparing docs across projects |

### Reuse before rewrite

The instinct with any content migration is to rewrite everything to fit the new home. Here the opposite approach holds: each GitHub README can become the source for its corresponding website page rather than being reinvented in a different voice. The Detective OS README becomes the Detective OS page; the QR code and networking convention repositories become the Conventions pages. The words already did their job once in GitHub; Nano Kit's job is to give them a second home.

### Documentation-friendly by design

This only works because the destination does not fight the source format. Markdown-shaped README content, headings, bullet lists, code blocks, drops into a live-edited page without needing a conversion pipeline, matching the same instinct that made Nano Kit worth choosing in the first place: fast iteration and a documentation-friendly workflow rather than a rigid content model.

### The pages that will need more than a paste

Not every README travels unchanged. The Platform's Ontology, Product Model, Systems of Record, and Runtime Architecture pages sit closer to the core diagram from Episode 2 and may need framing sentences that only make sense once a visitor has already seen that hero illustration. Those get a light edit pass; the deeper application-level docs, Code Smell Detectives, Repository Detectives, Show Runners, PKI Runners, IAM Runners, mostly just need a new home.

With content flowing in, Episode 5 turns outward to where each of these pages will actually live: the domain and subdomain map.

