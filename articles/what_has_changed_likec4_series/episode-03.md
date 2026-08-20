---
title: "🏗️ Building the Model, One Nested Box at a Time"
series: "What has changed, LikeC4?"
part: 3
organization: "the-software-s-journey"
tags: [likec4, dsl, model, hierarchy]
---

## 🏗️ Building the Model, One Nested Box at a Time

Vocabulary settled, now I actually describe the system. The `model` block is where every element I'll ever draw actually lives, and I start, deliberately, at the top:

```
model {
  customer = actor 'Customer'
  saas = system 'Our SaaS'
}
```

Two named elements, `customer` and `saas` — that name on the left of the `=` is the identifier I'll reference everywhere else in the project; the string on the right is the human-readable label. Nothing about this describes internal structure yet, and that's fine. This is exactly the Context-level thinking the C4 model asks for first: the big picture, before anyone worries about implementation.

Real systems have parts, though, and this is where LikeC4 starts to feel less like a diagramming tool and more like actually modeling the thing. Say `saas` has two main pieces, a UI and a backend:

```
specification {
  element actor
  element system
  element component
}

model {
  customer = actor 'Customer'

  saas = system 'Our SaaS' {
    component ui
    component backend
  }
}
```

`ui` and `backend` are nested directly inside `saas`'s own braces — that nesting *is* the hierarchy. I'm not drawing a box inside another box on a canvas; I'm writing a sentence that says "the SaaS system is made of these parts," and every view that later zooms into `saas` will already know what's inside it, because the model already knows.

On a real project — the AWS e-commerce documentation I mentioned last episode — this same nesting habit is what let me split the model across files without losing the structure. One file for the corporate-level "global context":

```
// docs/workspace.c4
model {
  warehouse_api = system "Warehouse Management System" {
    description "External legacy system providing stock availability."
    style {
      color muted
    }
  }
}
```

And a separate file for the system I actually own, nesting containers the same way `ui` and `backend` were nested above:

```
// docs/ecommerce/model.c4
model {
  ecommerce = system "E-commerce Platform" {
    description "Allows customers to browse and purchase products online."

    spa = container "Web Portal" "React Application"
    api_gateway = container "API Gateway" "REST Interface"
    order_service = container "Order Lambda" "Node.js / TypeScript"
    db = container "Products & Orders" "DynamoDB" {
      style { shape cylinder }
    }
  }
}
```

That `shape cylinder` on the database is worth noticing — it's not a special "database element kind," it's the same ordinary `container` kind from the specification, with one styling override telling it to render like the database everyone already recognizes on sight. The hierarchy carries meaning; the styling carries recognition. I'll come back to both properly in a couple of episodes.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The architect (me) | A system's real internal structure (components, containers, and how they nest) | Write it as nested elements inside `model {}` | A hierarchical model matching the system's actual decomposition | Every view that zooms into any part of this hierarchy |
| Multi-file model organization | Logically separate concerns (corporate landscape vs. one owned system) | Split the model across files (`workspace.c4`, `ecommerce/model.c4`) while keeping one logical model | A model that scales past a single file without losing coherence | Larger teams and larger systems |
| Nested element declarations | Elements declared inside a parent's braces | Automatically establish parent-child structure, no separate "contains" statement needed | A hierarchy views can navigate at any depth | Predicates and views (coming up in Episode 5) |

Next stop: the arrows between the boxes — how relationships are actually written, and the one placement convention I insist on.
