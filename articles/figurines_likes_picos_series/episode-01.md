---
title: "🧸 Unboxing Your First Pico"
series: "Figurines like Picos"
part: 1
organization: "the-software-s-journey"
tags: [pico, picolabs, krl, introduction, iot]
---

## 🧸 Unboxing Your First Pico

Oh, there is nothing — *nothing* — quite like the feeling of sliding a brand new figurine out of its box for the first time. The little pop of the packaging, the figurine standing there for the first time, already itself, already whole, ready for a shelf of its own. That feeling is exactly what it's like to create your very first pico, and this whole series is my excuse to grin about it for ten-odd episodes.

A pico — short for Persistent Compute Object — is a little standing figurine in a much bigger software display case. And just like a proper collectible figurine, a pico has a few non-negotiable qualities that make it worth collecting in the first place. It's *persistent* — once it exists, it stays on the shelf, holding its pose and its paint job, until you deliberately decide to retire it. It's *unique* — every figurine gets its own identity tag, immutable no matter how many times you repaint it or swap its accessories. It's *online* — unlike the figurine gathering dust in a cabinet, a pico is reachable, live, ready to respond the moment you knock. It's *concurrent* — a whole shelf of picos can each be doing their own thing at once, nobody blocking anybody else's pose. And it's *event-driven* and *rule-based* — a pico doesn't just sit there looking pretty, it reacts, following little instruction cards called rules that say "when this happens, strike this pose."

Picos talk to each other the way figurines in a diorama relate to one another — not through some universal shared table, but point to point, one figurine addressing another directly, in an actor-like style. String enough of them together and you get a whole diorama, a whole collection with its own internal life — and that, as it happens, is exactly what real-world deployments like the Fuse connected-car system did: an entire fleet modeled as a collection of picos, each one a figurine representing a car, quietly running its own rules.

Over the next several episodes we'll open the whole toy chest: the instruction sheets (KRL) that make a figurine come alive, the workshop (Wrangler) that assembles new ones, the display cabinet system (Manifold) that organizes a whole collection, the little remote control (Python) we'll use to poke a figurine from across the room, and even the display-case manufacturer (Crossplane) we'll commission to build the shelf itself. Go fetch a cup of tea. We're unboxing the whole set.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Pico Engine (open source, Node.js) | A ruleset registered by URL | Host, parse, and run picos that execute that ruleset | A live, addressable pico — a standing figurine | Developers, other picos, applications |
| Ruleset author | Event-condition-action rules written in KRL | Define how the figurine reacts when poked | An installable ruleset (a set of instruction cards) | Any pico that installs the ruleset |
| Collections of picos (e.g. Fuse) | Many individually-created picos | Compose them into a decentralized, heterarchical network | A working diorama of interacting entities | End users of the IoT system being modeled |

Next stop: the instruction sheet every figurine ships with — KRL, and the rules that make a pico come alive.
