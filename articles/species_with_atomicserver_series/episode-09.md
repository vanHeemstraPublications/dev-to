---
title: "Species with AtomicServer 🦓 Ep.9"
series: "Species with AtomicServer"
part: 9
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, collections, queries]
---

## Episode 9: Counting the Herd

A naturalist does not only study individuals. Sooner or later comes the census — how many of this species are actually out here, gathered in one place, countable at a glance. In AtomicServer, that census is called a Collection, and you met your very first one back in Episode 1 without quite realizing it: the `collections` resource sitting in the sidebar from the moment the Drive first loaded.

A Collection is, at heart, a dynamic, queryable grouping of every Resource that shares a given Class — the herd, gathered and counted automatically, with no ranger needed to manually tally each sighting. Tag a new specimen with `isA` pointing to "Species," and it does not need to be separately added to some master list; it simply appears in that Class's Collection the moment it exists, because the Collection is a live query over the reserve's Resources, not a hand-maintained roster. Watch the count in the sidebar shift as new specimens are logged, and you are watching the herd being recounted in real time, automatically, every time.

This is where the earlier episodes' groundwork quietly pays for itself. Because every Resource declares its Class through the same `isA` Atom, and every Class is itself just another resolvable Resource, the server can answer "show me everything that is a Species" without needing a bespoke database table built in advance for exactly that question. The census works because the taxonomy was built to be queried from the start — the same reason a well-organized field guide lets you flip straight to "all the warblers" instead of hunting page by page through an undifferentiated list of every bird ever seen.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| AtomicServer | Every Resource on the server declaring a Class via `isA` | Continuously group Resources by their declared Class | A live, queryable Collection per Class | Anyone browsing `collections` in the sidebar |
| New Resource author | A newly tagged specimen with an `isA` Atom | Add the Resource to the reserve | Automatic inclusion in the matching Collection, no manual listing | The Collection's future viewers |
| AtomicServer GUI | The `collections` resource | Render a browsable list of collections for every known Class | An at-a-glance population census of the whole reserve | The person exploring what already exists |

Next stop: enough observing — it's time to tag a specimen of our own and watch a brand-new Resource take shape from the + button onward.
