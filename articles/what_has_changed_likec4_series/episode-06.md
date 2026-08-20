---
title: "What has changed, LikeC4? 🎨 Ep.6"
series: "What has changed, LikeC4?"
part: 6
organization: "the-software-s-journey"
tags: [likec4, dsl, styling, icons, tags]
---

## Episode 6: Making It Recognizable at a Glance

A technically correct diagram that nobody can parse in under thirty seconds has failed at its actual job. Once the structure's right, I spend a genuinely small amount of effort making things recognizable — shapes, icons, colors, tags — because a database that looks like a database saves every reader a moment of translation.

Shapes come first, usually set right in the element definition:

```
saas = system 'Our SaaS' {
  component ui 'Frontend' {
    description 'Nextjs application, hosted on Vercel'
    style {
      icon tech:nextjs
      shape browser
    }
  }
  component backend 'Backend Services' {
    description '
      Implements business logic
      and exposes as REST API
    '
  }
}
```

`shape browser` on the frontend, an icon straight from a built-in technology set — `tech:nextjs` — and suddenly this box doesn't just say "Frontend," it *looks* like a frontend. On the e-commerce model, the database gets the same treatment with a different, equally recognizable shape:

```
db = container "Products & Orders" "DynamoDB" {
  description "Stores product catalog and order information."
  style {
    shape cylinder
  }
}
```

Relationships can carry emphasis too — I've taken to wrapping an important label in `==` to make it visually heavier than the surrounding arrows:

```
ui -> backend =='fetches via HTTPS'==
```

Color gets a more restrained use from me — mostly for de-emphasizing something that's relevant to the story but not the focus of *this particular* view:

```
view of saas {
  include *

  style customer {
    color muted
  }
}
```

That `style` block inside a specific view, not the model, is worth noticing — I'm not permanently recoloring `customer` everywhere, only muting it in this one view, where the point is the SaaS system's internals, not the customer relationship that's already obvious.

And then there are tags — the mechanism I lean on hardest for anything AWS-shaped, because a consistent tag like `#aws-lambda` lets me apply one styling rule across every Lambda function in the model at once, rather than repeating `style { icon tech:aws-lambda }` on every single container:

```
order_service = container "Order Lambda" "Node.js / TypeScript" {
  #aws-lambda
}

inventory_proxy = container "Inventory Lambda" "Python" {
  #aws-lambda
}
```

Tags do double duty beyond styling, too — they're how I mark things `#legacy`, `#deprecated`, or `#team-payments`, and later, when I bring an AI agent into this workflow (a few episodes from now), tags become one of the main things I ask it to filter on. "List all elements tagged legacy from team1 project" turns out to be a genuinely useful question to be able to ask out loud, and tags are what makes the answer possible.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The architect (me) | A chosen shape, icon, or color for an element or relationship | Set it via a `style` block, either on the element or scoped to one view | A visually distinct, quickly recognizable diagram element | Anyone reading the rendered view |
| Built-in technology icon sets (`tech:*`) | A known technology (Next.js, PostgreSQL, AWS Lambda, Kubernetes) | Apply a recognizable icon without custom asset work | Instant technology recognition across diagrams | Stakeholders scanning a diagram quickly |
| Tags (`#aws-lambda`, `#legacy`, etc.) | A category applied to one or many elements at once | Enable consistent bulk styling and later, structured querying | A model that's both visually consistent and machine-queryable | Bulk style rules now, MCP-based AI queries later in this series |

Next stop: diagrams that don't just show structure, but show a sequence of events — dynamic views.
