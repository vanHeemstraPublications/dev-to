---
title: "Figurines like Picos 🗄️ Ep.6"
series: "Figurines like Picos"
part: 6
organization: "the-software-s-journey"
tags: [manifold, pico, wrangler, things, communities]
---

## Episode 6: The Collector's Cabinet System

Any collector who's outgrown a single shelf knows the next problem isn't finding more figurines, it's organizing the ones you already have. You need an owner's name on the cabinet, sections for different sets, a shared shelf where the space-themed figurines all stand together, and some sensible way of knowing what's even in the collection without counting by hand every time. That whole organizational layer, for a network of picos, is called Manifold, and it is — genuinely, unreservedly — my favourite part of this toy chest.

Manifold sits on top of the pico engine and Wrangler from Episode 3, and it gives your collection a consistent shape rather than a sprawl. At the very top sits the Root Pico — think of it as the cabinet itself — under which Manifold's bootstrap creates a Tag Registry, a Skills Registry, and an Owner pico, and the Owner in turn gets its own Manifold pico, the operational hub for everything that follows:

```
Root Pico (engine)
  ├─ Tag Registry pico
  ├─ Skills Registry pico
  └─ Owner pico
       └─ Manifold pico (operational hub)
            ├─ Thing picos  ··· subscribe ···► Community picos
            └─ ...
```

A **thing** pico is a single collectible in your cabinet — one backpack, one sensor, one figurine with its own ECI and its own little life. A **community** pico is a labelled shelf section that groups related things together — "travel gear," "home sensors," "the entire 90s cartoon lineup" — and, delightfully, a single thing can belong to more than one shelf section at once, connected by dashed-line subscriptions rather than being physically glued to just one spot.

Setting the whole cabinet up is, mercifully, a single bootstrap step rather than a weekend of manual shelving:

```krl
rule bootstrap_my_collection {
  select when manifold bootstrap_requested
  fired {
    raise wrangler event "install_ruleset_request"
      attributes { "rids": ["io.picolabs.manifold_bootstrap"] }
  }
}
```

Install `io.picolabs.manifold_bootstrap` on the root pico, and it creates the tag registry, the skills registry, and the owner pico — which then creates the Manifold pico itself — in one coordinated motion. Query `getBootstrapStatus()` afterward and you get back the ECIs for every registry and the owner, the complete address book for a collection you just built from nothing.

Creating a new thing, once bootstrapped, is as friendly as asking the cabinet's own hub to fetch you a new item:

```python
def create_thing(manifold_eci: str, name: str) -> dict:
    resp = requests.post(
        f"{BASE}/sky/event/{manifold_eci}/py-collector/manifold/createThing",
        json={"name": name},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()
```

And a thing joining a community is just as friendly the other direction:

```krl
rule join_community {
  select when thing join_request
  pre {
    communityEci = event:attr("communityEci")
  }
  fired {
    raise community event "addThing"
      attributes { "eci": meta:eci } to communityEci
  }
}
```

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `io.picolabs.manifold_bootstrap` | Installed on the root pico | Create the tag registry, skills registry, owner, and Manifold hub in one pass | A fully organized, addressable cabinet structure | The collection's owner, every future thing and community |
| Manifold pico (`io.picolabs.manifold_pico`) | A `createThing` or `createCommunity` event | Delegate to Wrangler, install base rulesets on the new child | A new thing or community pico, already wired into the hierarchy | The requester, the owner's inventory queries |
| Thing pico (`io.picolabs.thing`) | A `join_request` toward a community's ECI | Raise `addThing` on the target community | Membership recorded via subscription | The community pico, `getThings()`/`getCommunities()` inventory |

Next stop: a big collection needs a sign-in sheet at the door — the Tag Registry and Skills Registry that keep track of what's in the cabinet and what each thing can do.
