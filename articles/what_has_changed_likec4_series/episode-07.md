---
title: "🎬 Telling One Story Without Cluttering the Model"
series: "What has changed, LikeC4?"
part: 7
organization: "the-software-s-journey"
tags: [likec4, dsl, dynamic-views, sequence-diagrams]
---

## 🎬 Telling One Story Without Cluttering the Model

Structure diagrams answer "what exists." Sooner or later, someone in a design review asks a different kind of question — "okay, but what actually happens when a customer places an order?" That's a scenario, a use case, a specific sequence of steps, and I don't want to pollute my structural model with elements and relationships that only exist to answer one narrow question. Dynamic views are LikeC4's answer: a scenario defined entirely inside the view itself.

```
dynamic view example {
  title 'Dynamic View Example'
  customer -> web 'opens in browser'
  web -> auth 'updates bearer token if needed'
  web -> api 'POST request'
  api -> auth // title is derived from the model
  api -> api 'process request' // allow self-call

  // reverse direction, as a response to line 59
  web <- api 'returns JSON'

  // Include elements, that are not participating
  include cloud, ui, backend

  style cloud {
    color muted
    opacity 0%
  }
}
```

There's a shorthand I use constantly once a sequence gets longer than three or four steps — continuous chaining:

```
dynamic view example {
  customer
     -> web
     -> api // same as web -> api
     -> web // same as web <- api
}
```

`A -> B -> A` is shorthand for "A calls B, then B responds back to A" — the backward direction gets inferred automatically, which matters because most real request/response flows are exactly that shape, and typing it out step by step every time gets tedious fast.

For anything with real branching logic, LikeC4 gives me flow-control blocks that read almost like actual code — `parallel`/`par` for concurrent steps, `opt` for a block that might be skipped, `loop` for repetition, `break` to interrupt a loop early, and `alt`/`when`/`else` for genuinely mutually exclusive branches:

```
alt {
  when 'authorized' {
    web -> api 'requests data'
  }
  else 'not authorized' {
    web -> customer 'shows login'
  }
}
```

And for the failure paths I always used to leave out of diagrams because they were annoying to draw by hand, there's `try`/`catch`/`finally`:

```
try {
  api -> db 'query'
} catch 'on failure' {
  api -> web 'shows error'
} finally {
  api -> api 'release resources'
}
```

These blocks nest to any depth — an `alt` containing a `loop` containing further steps, exactly like real control flow. One caveat worth flagging honestly, since I've hit it myself: this whole flow-control feature is marked experimental in the docs, syntax and rendering may still shift, and the LikeC4 team is explicitly asking for feedback in their GitHub discussions — worth checking the current docs before betting a whole architecture review deck on the fanciest branching you can write.

Dynamic views also render two ways — as a `diagram`, the default, or as a classic `sequence` diagram, actor lifelines and all, useful when the stakeholders in the room are more used to reading UML than boxes-and-arrows. One thing to remember with the sequence variant: it only supports leaf elements, ones with no children of their own — makes sense, since a sequence diagram's lifelines don't really have a sensible way to represent "and this lifeline also contains three nested lifelines."

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The architect (me) | A specific scenario or use case worth explaining in isolation | Define it entirely inside a `dynamic view`, without touching the structural model | A scenario diagram with zero pollution of the "what exists" model | Stakeholders asking "what happens when...?" |
| Flow-control blocks (`parallel`, `opt`, `loop`, `alt`, `try`) | Real branching, concurrency, or error-handling logic in the scenario | Express it as nested blocks, rendered as sequence-diagram-style frames | A scenario diagram that actually shows conditional and error paths | Design reviews needing more than a single happy path |
| The `sequence` variant | The same dynamic view definition | Render as a classic sequence diagram instead of the default diagram style | A format familiar to UML-literate stakeholders | Reviewers more comfortable with lifelines than nested boxes |

Next stop: leaving the logical model behind for a moment — the physical layer, deployment nodes, and where things actually run.
