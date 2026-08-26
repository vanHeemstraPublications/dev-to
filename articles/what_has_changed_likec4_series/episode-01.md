---
title: "What has changed, LikeC4? 🗺️ Ep.1"
series: "What has changed, LikeC4?"
part: 1
organization: "the-software-s-journey"
tags: [likec4, architecture-as-code, c4-model, introduction]
---

## Episode 1: The Question I Ask Every Monday Morning

I've been a software architect long enough to know the real enemy isn't complexity. It's staleness. Give me the most tangled distributed system in the world and I'll draw you an honest picture of it — once. The problem is never the first diagram. The problem is the diagram from six sprints ago, still pinned to the wiki, still confidently lying to every new hire who opens it, because nobody remembered to update the PNG after the payments service got split in two.

So every Monday morning, before standup, I ask the same question, out loud, to whatever's watching my repository: *what has changed, LikeC4?*

LikeC4 is architecture-as-code — you describe your system architecture in a small, expressive DSL, and it visualizes, validates, and shares it, all from a single source of truth. Not a drawing tool that happens to export to a version-controlled format. A language, first, for describing components, relationships, and boundaries — and diagrams that fall out of that description automatically, the same way a chart falls out of a spreadsheet's data rather than being drawn by hand on top of it.

Here's the shape of the promise, straight from LikeC4's own front door:

```
model {
  customer = actor 'Customer'

  cloud = system 'Our SaaS' {
    ui = component 'Frontend'
    api = component 'Backend'

    ui -> api 'requests'
  }

  customer -> ui
}
```

Write. See. Ship. Three steps, and I mean that literally — `likec4 build` builds a static site, `likec4 generate react` generates embeddable components, `likec4 serve` serves it all locally with hot reload. Everything downstream — every diagram, every export, every embedded view in my documentation — traces back to text I can diff in a pull request.

This series is my answer to that Monday-morning question, worked all the way through: how I define what my system *is* in LikeC4's DSL, how I project that definition into diagrams at whatever level of detail my audience needs — the classic C4 levels, Context down to Component — how I capture the physical deployment alongside the logical model, how I keep the whole thing from drifting the moment I stop paying attention, and how, eventually, I stopped asking that Monday question myself and let CI and an AI agent answer it for me instead.

Claudio Taverna, an architect who's put this into real production use on AWS, put the underlying case better than I could: with diagrams as code, there are no stale diagrams, because the diagram source files live in version control right alongside the code they represent, and are therefore always up to date with it. That's not a nice-to-have. That's the whole reason I stopped drawing rectangles by hand.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| LikeC4 (open source, MIT licensed) | A textual DSL for describing architecture | Parse, validate, and render diagrams from that description | Visual, interactive, always-current architecture diagrams | Architects, developers, and stakeholders reading them |
| The architect (me) | A system's actual structure, as it exists in code today | Write it down once, in `.c4` files, committed to the same repository | A single source of truth for "what this system is" | Every diagram, export, and query that follows |
| Version control (Git) | Every change to the `.c4` source files | Track, diff, and review architecture changes like any other code change | A full history of "what has changed," answerable at any time | This series' entire premise |

Next stop: the very first file I write for any new system — the specification that defines my own vocabulary before I draw a single box. See the accompanying repository [likec4](https://github.com/software-journey/likec4) for the source code of this series.
