---
title: "Figurines like Picos 🎮 Ep.5"
series: "Figurines like Picos"
part: 5
organization: "the-software-s-journey"
tags: [python, requests, sky-cloud, http-api, pico]
---

## Episode 5: The Remote Control You Point at the Cabinet

Confession time: half the joy of collecting figurines with poseable joints is not the posing itself, it's poking them from a slight distance with whatever's handy — a pencil, a chopstick, the cap of a pen — just to watch them react. Python, for our purposes, is that pencil. It doesn't need to know a single word of KRL to make a pico dance; it just needs the ECI from the last episode and the wonderful, humble `requests` library.

Raising an event is a POST, so here's the Python equivalent of walking up to our greeter figurine from Episode 2 and giving it a friendly poke:

```python
import requests

BASE = "http://localhost:8080"
ECI = "your-figurines-eci-goes-here"

def greet(name: str) -> dict:
    resp = requests.post(
        f"{BASE}/sky/event/{ECI}/py-greeter/figurine/greet",
        json={"name": name},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    result = greet("Ada")
    print(result)
```

`py-greeter` there is just our chosen `{eid}` — a label we picked for this particular poke, purely for our own bookkeeping. Run it, and somewhere on a shelf, a figurine we've never touched with our own hands just fired its `wave_hello` rule and sent back a directive.

Queries work the same way, just as a GET, and this is how you ask a figurine a question without changing anything about it — checking how many times it's been greeted, say, without greeting it again:

```python
def greeting_count() -> int:
    resp = requests.get(
        f"{BASE}/sky/cloud/{ECI}/io.example.greeter/greetingCount",
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json().get("result", 0)

print(f"This figurine has been greeted {greeting_count()} times so far!")
```

A small, wonderfully liberating thing about this: nothing about our Python script knows or cares that the figurine on the other end is running on a Node.js pico engine, possibly hosted a continent away, possibly one of thousands of identical greeter figurines each with their own ECI. All Python needs is an address label and the shape of the door to knock on — `/sky/event/...` or `/sky/cloud/...` — and the figurine handles the rest, entirely on its own terms.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Python `requests` script | An ECI, an event or query path, and a JSON payload | POST to raise an event, or GET to run a query | An HTTP call reaching the target pico | The pico installed at that ECI |
| Pico Engine (Sky Cloud API) | An incoming `/sky/event/` or `/sky/cloud/` request | Route it to the matching pico and installed ruleset | A fired rule or a returned function result | The calling Python script |
| Ruleset's `select when` rule / query function | The routed event or query | Execute the matching action or return a value | A directive (for events) or a JSON result (for queries) | The Python script awaiting the response |

Next stop: one figurine is delightful, but a whole organized collection with shelves, sections, and a sign-in sheet is something else entirely — Manifold, the collector's display cabinet system.
