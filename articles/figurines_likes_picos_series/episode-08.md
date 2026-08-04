---
title: "Figurines like Picos 🔔 Ep.8"
series: "Figurines like Picos"
part: 8
organization: "the-software-s-journey"
tags: [manifold, notifications, twilio, prowl, pico]
---

## Episode 8: The Bell That Rings Across the Whole Cabinet

Here's a small scenario every collector eventually lives through: one figurine on a back shelf has quietly toppled over, and you'd very much like to know about it without personally inspecting every single item in the cabinet every single day. Manifold's answer is a genuinely lovely piece of design — a single, centralized bell, hung on the Manifold pico itself, that every thing and community in the collection is allowed to ring, but only Manifold is allowed to actually answer with a phone call.

The rule is refreshingly strict, and I love it for that: domain rulesets should never call Twilio or Prowl directly. Instead, any pico with something to report raises one event — `manifold add_notification` — carrying a subject `picoId`, a human-readable `message`, and a few identifying attributes, and lets Manifold decide how loudly to ring the bell:

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

Manifold then fans that single alert out across whichever channels the *subject* pico — not the reporting one — has opted into: an in-app inbox entry always, plus SMS through Twilio and push through Prowl if the owner has switched those on using their own credentials, never the reporting ruleset's. Toggling a channel is its own tidy little event:

```python
def enable_sms_notifications(manifold_eci: str, thing_pico_id: str) -> dict:
    resp = requests.post(
        f"{BASE}/sky/event/{manifold_eci}/py-collector/manifold/change_notification_setting",
        json={"id": thing_pico_id, "option": "SMS"},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()

def get_my_notifications(manifold_eci: str) -> list[dict]:
    resp = requests.get(
        f"{BASE}/sky/cloud/{manifold_eci}/io.picolabs.notifications/getNotifications",
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json().get("result", [])
```

What makes this worth admiring, beyond the sheer convenience, is the privacy discipline baked into it: channels are opt-in *per subject pico*, and the owner's Twilio number and Prowl key live only on the Manifold pico, never scattered across every thing that might someday need to ring the bell. A hundred figurines can all report trouble; only one pico ever actually knows your phone number.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Any thing or community pico | A situation worth reporting | Raise `manifold add_notification` with a subject picoId and message | A single, standardized alert event | The Manifold pico (`io.picolabs.notifications`) |
| Manifold notification orchestrator | An incoming `add_notification` event | Check the subject pico's opted-in channels and fan out accordingly | In-app inbox entry, SMS, and/or Prowl push | The owner, via `getNotifications()` or their phone |
| Owner | A `change_notification_setting` event | Toggle a channel on or off per subject pico | An updated, owner-controlled notification preference | Future `add_notification` events for that pico |

Next stop: we've organized the whole collection in software — now let's talk about ordering the actual physical display case it all lives inside, courtesy of Crossplane.
