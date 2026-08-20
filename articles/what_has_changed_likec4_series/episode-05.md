---
title: "🔭 One Model, As Many Views As I Need"
series: "What has changed, LikeC4?"
part: 5
organization: "the-software-s-journey"
tags: [likec4, dsl, views, predicates, c4-model]
---

## 🔭 One Model, As Many Views As I Need

This is the moment every stakeholder meeting has been waiting for — an actual diagram. But here's the mental shift that took me a while to internalize: a view isn't something I draw. It's a *projection* of the model I already wrote, defined by predicates — statements about what to include or exclude. The model is the single truth; views are just different flashlights pointed at parts of it.

The simplest possible view, the one I always write first, is the bird's-eye "Landscape":

```
views {
  view index {
    include *
  }
}
```

`include *` at the top level includes only the top-level elements and infers relationships between them from what's nested inside — exactly the inference Episode 4 mentioned. This is my Context-level view: the big picture, why the system exists, who it talks to, aimed at technical and non-technical stakeholders alike.

Want to zoom into one system and see its internals? A second view, scoped with `of`:

```
views {
  view index {
    include *
  }

  view of saas {
    include *
  }
}
```

Now I'm looking at `saas`'s nested components and their relationships — the Container level, the "how responsibilities are distributed across separate running processes" view, aimed more squarely at architects, developers, and ops than at business stakeholders.

Real projects need more control than a blanket `include *`, and this is where predicates start doing real work. From the AWS e-commerce documentation, here's a Context view that deliberately hides internal detail:

```
view index {
  title "System Context - E-commerce Platform"
  include *
  exclude ecommerce.* // Only show the high-level boundaries
}
```

And a focused Container-level view, picking exactly which pieces matter for this particular audience, with an explicit layout hint:

```
view containerView of ecommerce {
  title "AWS Backend Architecture"

  include ecommerce
  include ecommerce.api_gateway
  include ecommerce.order_service
  include ecommerce.inventory_proxy
  include ecommerce.db
  include warehouse_api

  autoLayout LeftRight
}
```

And a third, narrower still — a view built for one specific conversation, the inventory integration, with nothing else cluttering it:

```
view inventoryFlow of ecommerce {
  title "Integration Detail: Inventory Check"
  include
    ecommerce.order_service,
    ecommerce.inventory_proxy,
    warehouse_api
}
```

Three views, one model, zero duplication of the underlying facts. And this is the part that actually answers this series' title question, every single time: because every view is a projection, not a separate drawing, the moment I change a relationship's label or add a new container to the model, *every view referencing it updates automatically* — I don't hunt down three PNGs to fix. I edit one fact, once, and every flashlight pointed at it shows the new truth immediately.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The model (Episodes 2–4) | Every element and relationship already defined | Serve as the single source every view projects from | A model that can support unlimited views without duplication | Every `view` block in the project |
| `include` / `exclude` predicates | A chosen scope (top-level, one system, a hand-picked set of elements) | Filter the model down to exactly what a specific audience needs | A focused diagram matching its intended reader | Stakeholders at Context, Container, or Component granularity |
| The projection model itself | Any later change to the underlying model | Automatically propagate that change into every view referencing it | Diagrams that can never silently go stale relative to the model | Every episode after this one, and every future code review |

Next stop: making these views actually recognizable at a glance — styling, shapes, icons, and tags.
