---
title: "Species with AtomicServer 📖 Ep.5"
series: "Species with AtomicServer"
part: 5
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, classes, isa]
---

## Episode 5: The Field Guide Entry

Every field guide, sooner or later, groups its specimens. Not every bird gets its own private chapter — related birds are gathered under a shared entry, "Warblers" or "Herons," described once by their common traits so the next observer need not start from nothing. In this reserve, that shared entry is called a Class — an abstract type of Resource, such as "Person," or, closer to our reserve's own concerns, "Species."

A Class can recommend or require a set of Properties, behaving rather like a model, or a struct, or an interface — a template describing what a complete observation of this kind of thing ought to include. A specific specimen declares which Class or Classes it belongs to with a single, telling Atom: the `isA` Property, pointing from the Resource to the Class it instantiates. And — this is worth lingering on, because it trips up naturalists used to strict biological taxonomy — a Resource can belong to more than one Class at once, held in an ordered list, but there is no concept of inheritance here. A Class does not quietly hand down properties from some ancestral superclass the way a biological genus contains its species; each Class stands on its own, declared explicitly, every time.

This matters practically the moment two Classes disagree about what a shared Property should be called or require. The resolution is refreshingly procedural rather than philosophical: sort by the order Classes appear in the Resource's own `isA` array, first listed wins; failing that, fall back to alphabetical order on the Property's URL. No committee debate about which taxonomy takes precedence — just a clear, repeatable rule, the sort of thing a field guide's editor would have insisted on from the start.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Class author | A name, a description, and a set of required/recommended Properties | Publish the Class as a resolvable Resource | A reusable template describing "what this kind of specimen looks like" | Every Resource that declares this Class via `isA` |
| Resource author | A specimen's observed Properties | Add an `isA` Atom pointing to one or more Classes, in preference order | A Resource explicitly typed as an instance of those Classes | Anyone reading the Resource, the AtomicServer GUI |
| AtomicServer | Conflicting Property definitions across a Resource's declared Classes | Resolve by `isA` order first, then alphabetically by Property URL | A deterministic, unambiguous field ordering | Form renderers, validators, other clients |

Next stop: individual Classes rarely stand entirely alone — see how a whole set of them, and the Properties they share, gets compiled into a proper field guide: the Ontology.
