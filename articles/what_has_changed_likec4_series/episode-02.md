---
title: "What has changed, LikeC4? 📐 Ep.2"
series: "What has changed, LikeC4?"
part: 2
organization: "the-software-s-journey"
tags: [likec4, dsl, specification, c4-model]
---

## Episode 2: Defining My Own Vocabulary First

Before I draw anything, I define what I'm even allowed to draw. That's the `specification` block, and it's the first thing in every LikeC4 project I've ever started. It's not decoration — it's me declaring the vocabulary my whole team will use to talk about this system, so nobody invents a fourth kind of "service" halfway through a diagram three months from now.

The smallest possible specification I've written needs only two kinds of things — an `actor` and a `system`:

```
specification {
  element actor
  element system
}
```

That's genuinely enough to start a Context-level diagram — the outermost, "Level 1" view in the classic C4 model, the one that shows *why* this system exists and *who* it interacts with, aimed at technical and non-technical stakeholders alike. But real systems have internal structure, so I extend the vocabulary as I go, adding `component` for the pieces living inside a system, or, on a project I documented recently for an AWS e-commerce platform, `container` for the deployable units — the Lambda functions, the API Gateway, the DynamoDB table:

```
// docs/specs.c4
specification {
  element actor {
    style { shape person }
  }
  element system
  element container
}
```

Notice the `style` block nested right there under `actor` — I'm not just naming a kind of element, I'm giving every instance of it a default appearance, `shape person`, so every actor in every diagram across the whole project looks consistent without me repeating that choice every time I use one.

I can also declare relationship kinds in the specification, when the plain arrow needs a label of its own — say, distinguishing synchronous calls from asynchronous ones:

```
specification {
  element actor {
    style { shape person }
  }
  element system
  element component
  relationship async
}
```

Here's the discipline this buys me, and it's the whole reason I insist on writing this file first, every time, before touching the model: every element and every relationship in this system has to be *one of these declared kinds*. There's no ad-hoc labeling, no "well I called it a microservice here and a service over there." The vocabulary is fixed, up front, in one file everyone on the team can read in ten seconds — and because it's just DSL, LikeC4's language server flags it immediately if I try to use a kind I never declared.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The architect (me) | The kinds of things worth distinguishing in this system (actor, system, component, container) | Declare each as an `element` kind in `specification`, with optional default styling | A fixed, shared vocabulary for the whole project | Everyone writing or reading the model afterward |
| `style` blocks nested in element kinds | A chosen default shape, color, or icon per kind | Apply that default automatically to every instance of the kind | Consistent visual language with zero repeated styling | Every diagram rendered from this project |
| LikeC4's language server | Model code referencing an undeclared element or relationship kind | Flag it immediately as a validation error | Fast, in-editor feedback before a bad reference ships | The architect and every contributor to the model |

Next stop: turning that vocabulary into an actual model — real elements, arranged in a real hierarchy.
