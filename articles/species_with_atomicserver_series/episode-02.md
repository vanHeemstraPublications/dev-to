---
title: "Species with AtomicServer 🔬 Ep.2"
series: "Species with AtomicServer"
part: 2
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, atoms, data-model]
---

## Episode 2: The Atom, Life's Smallest Unit

Every naturalist, sooner or later, learns to look past the whole animal and study the cell — the smallest unit at which life still means something. In this reserve, that unit is called, fittingly, the Atom. It is the smallest possible piece of meaningful information the system recognizes, and every single thing you will ever observe here — every specimen, every trait, every relationship — is, underneath, built entirely out of these.

An Atom has three parts, and a careful observer will notice they always travel together. The Subject is a URL — the address at which this particular piece of information lives, and, crucially, the address the creator of that information is responsible for keeping available. Follow that link, download what is there, and you receive every Atom that shares that Subject. The Property is the second part: also a URL, one that must resolve to an Atomic Property definition — think of it as the specific field mark being recorded, "has-fur-colour" or "lives-in-habitat," never invented on the spot but always pointing back to a shared, public definition of what that mark means. And the Value is simply what was observed — the actual fur colour, the actual habitat — shaped by whatever datatype the Property specifies, so that "brown" is recorded as a string and "3" is recorded as a number, never confused with one another.

What makes this worth pausing on is not the simplicity but the consequence of it. Because a Property is itself just a URL that must resolve publicly, the meaning of any given Atom is never locked inside a single database — it can always be looked up, verified, cross-referenced against the same definition every other observer in the world is using. A field mark recorded this way is legible to any other naturalist on the network, not just the one who first wrote it down.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Data author | A Subject URL, a Property URL, and an observed Value | Combine the three into a single Atom | One unit of meaningful, typed information | Resources built from that Atom |
| Atomic Property registry | A Property URL to resolve | Publicly resolve the Property to its datatype, shortname, and description | A shared, verifiable definition of what the Atom's Value means | Any client or observer reading the Atom |
| Subject host | A Subject URL others wish to follow | Serve every Atom sharing that Subject when the URL is requested | The complete, current set of known facts about that Subject | Anyone querying the Subject |

Next stop: a single Atom rarely travels alone for long — watch how a whole cluster of them comes together to form a single, observable specimen: the Resource.
