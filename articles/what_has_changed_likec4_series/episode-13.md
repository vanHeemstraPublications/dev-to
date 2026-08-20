---
title: "What has changed, LikeC4? 🧭 Ep.13"
series: "What has changed, LikeC4?"
part: 13
organization: "the-software-s-journey"
tags: [likec4, wrapup, architecture-as-code]
---

## Episode 13: The Habit This Whole Series Was Really About

Twelve episodes ago I opened with a Monday-morning question I used to ask nervously, half-expecting the answer to be "you have no idea, and neither does anyone else." I want to close by admitting what actually changed, and it wasn't really about diagrams.

I define my vocabulary first, in a `specification` block, so nobody on the team invents a fifth kind of "service" out of habit. I build the model as nested elements, matching the system's real decomposition, not a canvas layout I have to manually keep tidy. I write relationships inside the element that initiates them, so responsibility is always readable, never something I have to search for. I project that one model into as many views as different audiences need — Landscape, Container, a narrow integration-focused view for one specific conversation — without ever duplicating a fact across them. I make things recognizable with shapes, icons, and tags, and I use tags a second time, later, as the exact filter an AI agent needs to answer a scoped question honestly. I capture scenarios as dynamic views, entirely separate from the structural model, so a sequence diagram never has to lie about what "exists" just to explain what "happens." I keep a physical deployment layer genuinely distinct from the logical one, because "what this system is" and "where this system runs" are different questions with different, equally valid, equally worth-recording answers. I ship the whole thing as a real, embeddable, deep-linkable website, not a folder of PNGs nobody can search. I run `likec4 validate` and `likec4 format --check` as CI gates, with the exact same seriousness I'd apply to a failing test. And now, finally, I ask the model itself what's changed, in plain language, through an MCP server that's reading the actual current state rather than my memory of it.

None of that is really about the diagrams. It's about closing the gap between what I claim my system looks like and what my system actually is — a gap that used to be measured in months, and is now measured in however long CI takes to run. Claudio Taverna's framing has stuck with me since I first read it: architecture defined in a text file, versioned alongside the code it describes, reviewed the same way, is architecture that finally gets to be a first-class citizen of the repository instead of a Confluence page nobody trusts. That's the whole shift. Not fancier diagrams. Just diagrams that are no longer allowed to lie.

So — what has changed, LikeC4? These days, I genuinely don't have to guess. I ask, and it tells me.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The full LikeC4 toolchain (DSL, CLI, CI integration, MCP server) | Twelve episodes' worth of individually-introduced practices | Combine them into one continuous architecture-as-code workflow | A documentation practice that can never silently go stale | The architect (me), and every stakeholder reading the result |
| This series | The complete path from an empty specification to an AI-queryable model | Walk it in order, with real code samples at every stop | A reusable habit, not just a one-time tutorial | Any reader adopting LikeC4 for their own systems |
| The reader | Everything covered across this series | Apply it to their own architecture, in their own repository | A team that stops asking "is this diagram still accurate?" nervously | Their own stakeholders, developers, and future selves |
