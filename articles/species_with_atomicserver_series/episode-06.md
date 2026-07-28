---
title: "Species with AtomicServer 🗺️ Ep.6"
series: "Species with AtomicServer"
part: 6
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, ontology, schema]
---

## Episode 6: The Taxonomy Compiled

A single field guide entry is useful. A whole taxonomy — every Class defined, every Property described, every relationship between them laid out so a newcomer can trace how "Warbler" relates to "Bird" relates to "Animal" — is what actually lets a discipline function. In this reserve, that compiled taxonomy is called an Ontology, and you have, in fact, already met one: the default ontology, sitting quietly in the sidebar since the moment the Drive first loaded.

An Ontology's job is to define new Classes and Properties and show the relation between them, and it is built to satisfy four commitments worth naming individually. It is decentralized — Classes and Properties can be defined in entirely external systems, resolved over ordinary web protocols, so no single reserve needs to own the whole of taxonomy for its records to make sense. It is typed — every Atom carries a clear datatype, and validated data stays predictable as a result. It is IDE-friendly — despite leaning on URLs throughout, the schema offers shortnames as aliases, so nobody is forced to type a full address just to reference "furColour." And it is self-documenting — encounter a piece of data you don't recognize, and simply following its links explains, on its own, how that data is meant to be understood, without reaching for a separate manual.

Building your own Ontology, in practice, looks like the basic-data-model walkthrough the documentation itself demonstrates: click the + button, start typing a Property name like "heading," and if it doesn't exist yet, create it there and then — give it a description, choose STRING as its datatype (or MARKDOWN, for something like body text, or Resource, for a field that should always point to another specimen of a specific kind, a header image and nothing else). Reuse an existing external Property like "name," and the GUI is honest about the fact that you don't hold edit rights over somebody else's field mark, even while it happily lets you reference it. That's the compiled taxonomy taking shape in front of you, one entry at a time.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Ontology author | A set of related Classes and Properties to define | Compile them into one coherent, publicly resolvable Ontology | A shared taxonomy explaining how a domain's Classes and Properties relate | Every Resource and Class that references it |
| Default ontology (built into AtomicServer) | Server initialization | Provide the core Class/Property vocabulary before any custom Ontology exists | A working taxonomy present from the very first boot | New users creating their first Resource |
| AtomicServer GUI (+ button flow) | A Property name typed by the user | Offer to reuse an existing Property or create a new one with description and Datatype | An extended, custom Ontology built incrementally through the UI | Future Resources using the newly defined Property |

Next stop: a taxonomy is only trustworthy if every entry can be traced back to whoever recorded it — meet the ranger whose signature makes that possible: the Agent.
