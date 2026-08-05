---
title: "Figurines like Picos 🔨 Ep.3"
series: "Figurines like Picos"
part: 3
organization: "the-software-s-journey"
tags: [wrangler, pico, krl, lifecycle]
---

## Episode 3: The Workshop That Assembles Every Figurine

Every serious figurine collection eventually needs a proper workshop — a workbench with the right tools where new figurines get assembled, existing ones get their accessories swapped, and retired ones get carefully boxed back up. In the pico world, that workshop is called Wrangler, and it's honestly one of my favourite parts of the whole toy chest, because it turns "I'd like a new figurine" into something you can actually ask for, out loud, in a rule.

Wrangler used to go by the name CloudOS, and functionally it still behaves like a tiny operating system for your collection: it provides the services that sit above the bare pico engine, the same way an OS sits above bare metal. Ask Wrangler nicely, and it will create a brand-new child pico for you — a new figurine, snapped onto the display stand right next to its parent:

```krl
rule spawn_new_figurine {
  select when figurine spawn_child
  pre {
    childName = event:attr("name")
  }
  fired {
    raise wrangler event "new_child_request"
      attributes { "name": childName, "rulesets": ["io.example.greeter"] }
  }
}
```

That one `raise wrangler event "new_child_request"` line is the whole workshop transaction: a brand new pico gets minted, the `io.example.greeter` ruleset from the previous episode gets installed on it automatically, and it takes its place as a child of whichever pico asked for it. Parent and child here isn't a strict hierarchy the way a shelf display might suggest, either — it's simply how the figurine was assembled, a lineage you can trace, not a cage it's stuck inside.

Wrangler's other great service is channels — the little labelled hooks Wrangler installs on a figurine so other figurines (or you, from outside the display case entirely) know exactly where to knock. We'll get to those properly in Episode 4, but it's worth saying now: without Wrangler quietly running the workshop, every pico you ever create would need to be wired up, named, and connected entirely by hand. With it, "spawn a new figurine and wire it up" is just another rule away.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Wrangler | A `new_child_request` event with a name and ruleset list | Create a new child pico, install the requested rulesets, register the parent/child relationship | A freshly assembled, ready-to-use figurine | The requesting pico, future rules addressing the child |
| Parent pico | A rule raising a Wrangler event | Delegate figurine creation instead of hand-assembling one | A one-line request instead of manual engine plumbing | Wrangler |
| Pico Engine | Wrangler's installed rulesets | Provide the underlying host and event bus Wrangler operates on | The runtime substrate Wrangler's services depend on | Wrangler, every pico it manages |

Next stop: every figurine needs its own little address label so the right hand knocks on the right door — meet Channels and ECIs.
 
