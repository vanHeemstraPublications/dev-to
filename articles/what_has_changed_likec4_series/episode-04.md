---
title: "What has changed, LikeC4? ➡️ Ep.4"
series: "What has changed, LikeC4?"
part: 4
organization: "the-software-s-journey"
tags: [likec4, dsl, relationships, best-practices]
---

## Episode 4: The Arrows Between the Boxes

A model full of boxes with no arrows between them isn't an architecture — it's an inventory. Relationships are where LikeC4 earns the name "architecture as code" rather than "component list as code," and they're refreshingly simple to write:

```
model {
  customer = actor 'Customer'

  saas = system 'Our SaaS' {
    ui = component 'Frontend'
    backend = component 'Backend'

    ui -> backend
  }

  customer -> ui
}
```

Any link between elements counts — interactions, calls, delegations, dependencies, flows. I'm free to define them however makes sense for the system, and I almost always give them a label, because "ui -> backend" tells me nothing an "ui -> backend 'requests'" doesn't tell me better:

```
ui -> backend 'fetches via HTTPS'
```

Here's a placement convention I picked up from watching how experienced LikeC4 users structure real projects, and I've never gone back once I adopted it: define the relationship *inside* the source element, the one initiating the call, not off on its own line somewhere else. On the AWS e-commerce project, every outgoing call is written from the caller's own perspective:

```
customer = actor "Customer" "A retail customer" {
  description "A user who browses and purchases products via the e-commerce platform."

  -> ecommerce "Uses"
  -> ecommerce.static_assets "Browses via Browser"
}

ecommerce = system "E-commerce Platform" {
  -> warehouse_api "Checks stock availability from"

  order_service = container "Order Lambda" "Node.js / TypeScript" {
    -> db "Reads/Writes data"
    -> inventory_proxy "Requests stock check"
  }

  inventory_proxy = container "Inventory Lambda" "Python" {
    -> warehouse_api "Fetches stock levels via REST API"
  }
}
```

Reading this months later, half-asleep before a design review, I don't have to hunt across the file for every place `order_service` might be mentioned as a target — I open `order_service`'s own braces and every outgoing relationship it owns is sitting right there, described from its own point of view. It reads like a sentence: "the order service reads and writes data, and requests a stock check." That's not an accident of formatting. It's the model staying honest about *whose responsibility* each call actually is.

One more thing worth knowing early: I don't have to draw a relationship between `customer` and the whole `saas` system explicitly if `customer` already has a relationship with something nested inside it. LikeC4 infers it — `customer` has a known relationship with `saas.ui`, so `customer` has *some* relationship with `saas` too, automatically, the first time I ask for a landscape view. I don't manage that inference. I just get to trust it.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The architect (me) | An actual call, dependency, or interaction between two elements | Write it as `source -> target 'label'`, defined inside the source element | A labeled relationship, attributed to whichever side initiates it | Every view rendering this connection |
| The "define at the source" convention | Relationships scattered across a growing model | Consistently place each one inside its initiating element's braces | A model where responsibility is easy to trace by reading, not searching | Future readers, including future me |
| LikeC4's relationship inference | A known relationship between a nested element and an outside element | Infer an implied relationship between the outside element and the parent container | Landscape-level views that stay honest without manual duplication | High-level Context views (next episode) |

Next stop: turning this model into actual diagrams — views, predicates, and the C4 levels they correspond to.
