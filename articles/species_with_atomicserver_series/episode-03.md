---
title: "Species with AtomicServer 🐾 Ep.3"
series: "Species with AtomicServer"
part: 3
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, resources, data-model]
---

## Episode 3: A Specimen in the Field

No naturalist studies a single cell and calls it a day. Cells cluster into tissue, tissue into an organism, and it is the whole organism — observable, distinct, identifiable — that ends up in the field notes. In this reserve, that whole organism is called a Resource: a bundle of Atoms that all happen to share the same Subject, the same home address. Formally, it is a graph. Informally, it is the animal standing in front of you.

A Resource can be almost anything worth observing — a Person, a Blogpost, a Todo item, or, closer to home for our metaphor, a single tagged specimen in the reserve's records. It must contain at least one Atom, meaning it always carries at least one Property and one Value — an organism observed but not described at all would hardly count as observed. And here the reserve enforces a rule any careful record-keeper would recognize on sight: a Property can only occur once per Resource. You cannot record two different fur colours for the same animal in the same breath; if a second observation comes in, it corrects the first, it does not sit beside it in quiet contradiction.

Think of a Resource the way you might think of a single row in a spreadsheet, except this row is not trapped inside one particular spreadsheet at all — its Subject is a URL, which means the row can be found, followed, and read by anyone with the address, from anywhere on the reserve or beyond it. When you open the AtomicServer GUI and click on any item in the sidebar, what you are looking at is precisely this: one Resource, rendered as a readable page, its Atoms translated into the fields and values you see on screen. Every specimen in this reserve, no matter how it is later classified or related to others, starts here — as a Subject with something, however small, already known about it.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Data author | A collection of Atoms sharing one Subject URL | Assemble the Atoms into a single addressable Resource | One observable specimen with a fixed home address | The AtomicServer GUI, any client following the Subject |
| AtomicServer | A Resource's Subject URL request | Enforce Subject-Property uniqueness and serve the current Atom set | A consistent, non-contradictory record for that specimen | Anyone reading or editing the Resource |
| AtomicServer GUI | A Resource selected from the sidebar | Render its Atoms as readable fields and values | A human-readable page for that specimen | The person browsing the reserve |

Next stop: a specimen is only useful to future observers if its traits are recorded using field marks everyone recognizes — enter the Property.
