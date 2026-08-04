---
title: "Figurines like Picos 🔖 Ep.7"
series: "Figurines like Picos"
part: 7
organization: "the-software-s-journey"
tags: [manifold, registries, nfc, qr, skills, pico]
---

## Episode 7: The Sign-In Sheet at the Cabinet Door

Every collector who's ever labelled a shelf with tiny sticky tags knows the particular joy of scanning a barcode and having the right catalogue entry pop straight up — no hunting, no guessing which box holds which figurine. Manifold gives your pico collection exactly this convenience, twice over, in the form of two registries: the Tag Registry and the Skills Registry.

The Tag Registry is the literal version of the sticker on the shelf. It maps physical tag identifiers — NFC chips, QR codes, the kind of thing you might stick on the bottom of an actual physical figurine or backpack — to the specific thing pico they belong to, plus a redirect URL for good measure. Scan the tag with a phone, and the registry resolves it straight to the correct pico's page, the way a well-run museum's little placards always know exactly which exhibit they're standing beside:

```krl
rule register_new_tag {
  select when tag_registry register_tag
  pre {
    tagId = event:attr("tagId")
    thingEci = event:attr("thingEci")
    redirectUrl = event:attr("redirectUrl")
  }
  always {
    ent:tags{tagId} := { "thingEci": thingEci, "redirectUrl": redirectUrl }
  }
}
```

The Skills Registry is the less literal, more delightful cousin: a queryable directory of named capabilities — ruleset RIDs, optional install URLs, even MCP tool metadata — that can be bolted onto any thing pico after the fact. Think of it as a catalogue of accessory packs: "glow-in-the-dark paint," "articulated wings," "the sensor-reading skill," each one a ruleset waiting to be installed on demand rather than baked in at creation time.

```python
def list_available_skills(skills_eci: str) -> list[dict]:
    resp = requests.get(
        f"{BASE}/sky/cloud/{skills_eci}/io.picolabs.manifold.skills_registry/listSkills",
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json().get("result", [])

def install_skill_on_thing(thing_eci: str, skill_rid: str) -> dict:
    resp = requests.post(
        f"{BASE}/sky/event/{thing_eci}/py-collector/thing/install_skill",
        json={"rid": skill_rid},
        timeout=5,
    )
    resp.raise_for_status()
    return resp.json()
```

Registering the tag registry with the owner has to happen once, and it has to happen *before* you start tagging actual things — the documentation is quite insistent about this, and rightly so: a tag scanned before the registry knows who owns it is a sticker with nothing behind it yet. Get the order right, though, and every future figurine you tag or every future accessory you bolt on resolves instantly, exactly the way a proper catalogue should.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Tag Registry (`io.picolabs.new_tag_registry`) | A physical tag ID, a thing's ECI, and a redirect URL | Store the mapping so future scans resolve instantly | An NFC/QR tag that correctly identifies its thing | Apps like SafeAndMine, anyone scanning a physical tag |
| Skills Registry (`io.picolabs.manifold.skills_registry`) | A named skill's ruleset RID and metadata | Publish it in a queryable directory | A catalogue of installable capabilities | Any thing pico looking to gain a new skill |
| Manifold bootstrap | The owner registering the tag registry (`manifold:new_tag_server`) | Link the registry to the owner before any tagging begins | A registry that's actually ready to answer scans | Every thing tagged afterward |

Next stop: a collection this organized deserves to actually tell you when something happens — the notification bell that rings across the whole cabinet.
