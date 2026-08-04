---
title: "Figurines like Picos 🏷️ Ep.4"
series: "Figurines like Picos"
part: 4
organization: "the-software-s-journey"
tags: [channels, eci, event-exchange, pico]
---

## Episode 4: The Little Address Label on Every Display Case

Here's a small but delightful detail that every serious collector eventually appreciates: a figurine on a shelf is only useful to visit if it has an address. Not a vague "somewhere in that cabinet," but a specific, precise little label you can point to and say "this one, exactly this one." In the pico world, that label is called an ECI — an Event Channel Identifier — and every pico has at least one, minted for it by Wrangler the moment it's created.

A channel is the mechanism; an ECI is the specific string that names one particular channel on one particular pico. Knock on a pico without the right ECI and, quite properly, nothing answers — the figurine doesn't respond to strangers waving at the cabinet from across the room, only to whoever holds the actual claim ticket for its channel. This is what lets two figurines that have never been introduced through any shared parent still talk directly, point to point, in that actor-like style Episode 1 promised: give one figurine the other's ECI, and a conversation can begin.

Raising an event or asking a question always goes through this address label, and the two roads in are the ones we'll use directly ourselves in the next episode:

```
POST /sky/event/{eci}/{eid}/{domain}/{type}   → raise an event on this pico
GET  /sky/cloud/{eci}/{ruleset}/{function}    → query a function on this pico
```

`{eci}` is the address label itself. `{domain}` and `{type}` are the event's own little category tags — remember `select when figurine greet` from Episode 2? That's a rule listening for domain `figurine`, type `greet`, and it will only ever fire for events arriving at the ECI it's actually installed on. `{eid}` is simply an identifier the sender chooses for their own event, handy for correlating a response later. Collect enough ECIs for enough figurines, and you effectively hold a whole address book for your collection — which, as it happens, is precisely what Manifold keeps for you in a tidy, organized form, coming up in Episode 6.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Wrangler | A newly created pico | Mint one or more channels and assign each an ECI | An addressable label for that specific figurine | Anyone who needs to reach this pico directly |
| Sender (another pico, an app, or a person) | An ECI plus an event's domain/type or a query's ruleset/function | POST to `/sky/event/{eci}/...` or GET `/sky/cloud/{eci}/...` | A raised event or a returned query result | The pico installed at that ECI |
| Pico's installed rulesets | An incoming event matched against the pico's own ECI | Fire the matching `select when` rule | The rule's action (a directive, a state change, a further event) | The original sender, other listening rules |

Next stop: time to stop talking about knocking on doors and actually knock — Python, the requests library, and our very own remote control.
