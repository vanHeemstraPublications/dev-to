---
title: "Species with AtomicServer 🏷️ Ep.4"
series: "Species with AtomicServer"
part: 4
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, properties, datatypes]
---

## Episode 4: Field Marks and Identifying Traits

A skilled birdwatcher does not identify a species by vague impression. They look for specific, agreed-upon marks — the wing bar, the eye ring, the particular curve of a beak — features that mean the same thing to every observer who has learned to look for them. In this reserve, that agreed-upon field mark is called a Property, and it is, arguably, the single most important concept the whole system is built around.

A Property is itself a Resource — one that describes the relationship between a Subject and a Value. It carries three things a good field mark needs. A description, giving the semantic meaning of the relationship — what, exactly, is being observed. A shortname, a short alias used in everyday reference (the kind of dot-syntax shorthand you would use to say `animal.furColour` rather than spelling out a full URL every time). And a Datatype, which guarantees type safety — a Property defined as a number will never quietly accept the string "brown," the way a trustworthy field guide never lets you confuse a measurement with a description.

This is also why Properties earn their central billing: they enable both the type safety that keeps observations honest and the JSON compatibility that makes those observations easy to read and write in ordinary tools. And because the datatype, shortname, and description are all attached to the Property itself, the AtomicServer GUI can use that same information to build an intuitive form the moment you go to create or edit a Resource — the field asking for fur colour looks like a text field because the Property says so, not because someone hand-built that particular form. Learn to read a Property once, and you can recognize its use anywhere in the reserve, on any specimen, forever.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Property author | A description, a shortname, and a chosen Datatype | Publish the Property as its own resolvable Resource | A shared, reusable field mark with guaranteed type safety | Every Resource that will use this Property |
| Datatype registry | A Property's declared Datatype | Constrain what Values that Property will accept | Predictable, validated data across every specimen | Anyone reading or writing Atoms using that Property |
| AtomicServer GUI | A Property's shortname, description, and Datatype | Render an appropriate input field automatically | An intuitive form for creating or editing a Resource | The person filling in the form |

Next stop: a single field mark rarely tells the whole story — watch how a cluster of Properties, gathered under one name, becomes a recognizable Class.
