---
title: "Figurines like Picos 🎪 Ep.10"
series: "Figurines like Picos"
part: 10
organization: "the-software-s-journey"
tags: [pico, decentralization, wrapup, krl, python, crossplane]
---

## Episode 10: The Whole Toy Chest, Closed Up and Admired

And here we are, at the end of the toy chest, everything finally out on the table at once. Let's do the thing every collector does at the end of a good unboxing session — line every piece up and admire how it all fits together.

A pico is the figurine itself: persistent, unique, online, rule-based. KRL is the instruction sheet that gives it a pose to strike. Wrangler is the workshop that assembles new figurines and hooks up their channels. An ECI is the little address label that lets anyone — another figurine, a Python script, an entire application — knock on exactly the right door. Manifold is the collector's cabinet system, turning individual figurines into an organized hierarchy of things and communities, with a sign-in sheet at the door for tags and skills, and one shared bell that rings responsibly instead of a hundred separate phone calls. And Crossplane is the cabinet manufacturer, called in before any of the rest of it can happen, to actually build the shelf the whole collection stands on.

What I love most, and the reason this series exists at all, is the philosophy sitting quietly underneath every single layer: decentralization, heterarchy, interoperability. No single pico engine owns the whole collection. A figurine hosted on one engine can talk, point to point, to a figurine hosted on a completely different engine, with no prior relationship required between the two hosts — the same way two collectors at different conventions can still trade figurines without their respective display cases ever having met. That's not an accident of the design; Phil Windley built picos specifically so that the Internet of Things wouldn't end up looking like one company's cabinet with everyone else's figurines locked inside it.

Let's close with the full stack, top to bottom, in one small scene: Crossplane has already built the cabinet, Manifold has already organized it, and now a Python script pokes a thing pico, which raises an event that Manifold's notification bell relays straight to the owner's phone.

```python
import requests

BASE = "http://my-picocase.westeurope.azurecontainer.io:8080"
THING_ECI = "thing-pico-eci-here"

def report_status(status: str) -> dict:
    resp = requests.post(
        f"{BASE}/sky/event/{THING_ECI}/py-collector/thing/sensor_triggered",
        json={"reading": status},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()

print(report_status("tipped_over"))
# → the thing's rule fires, raises manifold add_notification,
#   and the owner's phone buzzes a moment later.
```

```krl
rule report_toppled_figurine {
  select when thing sensor_triggered
  pre {
    reading = event:attr("reading")
  }
  if reading == "tipped_over" then noop()
  fired {
    raise manifold event "add_notification"
      attributes {
        "picoId": meta:picoId,
        "message": "Uh oh — this figurine has tipped over!",
        "thing": meta:picoId,
        "app": "cabinet-watch",
        "ruleset": meta:rid
      }
  }
}
```

One Python poke, one KRL rule, one cabinet built by Crossplane, one bell rung by Manifold — the whole toy chest, working together, exactly as designed. Go build a collection of your own. There is always room on the shelf for one more figurine.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The full pico stack (Crossplane, Pico Engine, Wrangler, KRL, Manifold) | Nine episodes' worth of individually-introduced layers | Combine infrastructure provisioning, ruleset execution, and network organization | A complete, working, decentralized pico network | Anyone who has followed this series start to finish |
| Python (`requests`) | An ECI and a JSON event payload | Poke a specific pico from entirely outside the pico ecosystem | A fired rule and its downstream effects | The reader, ready to write their own remote control |
| Decentralized architecture (Windley's original design goal) | Independently-hosted pico engines with no prior relationship | Allow point-to-point pico communication across engine boundaries | An Internet of Things nobody company owns outright | Every future collector building their own cabinet |
