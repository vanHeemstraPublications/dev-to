---
title: "Species with AtomicServer 🏷️ Ep.10"
series: "Species with AtomicServer"
part: 10
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, gui, resources, tutorial]
---

## Episode 10: Tagging a New Specimen

Every documentary reaches the moment the presenter stops narrating and simply crouches down to tag the animal in front of them. In AtomicServer, that moment is the + button in the sidebar, and everything the previous nine episodes described in the abstract — Atoms, Resources, Properties, Classes — comes together the instant you press it.

Click it, and you are presented with a list of resource types to choose from: Tables, Folders, Documents, and others besides, each one simply a Class already defined by the default ontology, ready to be instantiated. Pick one, and a form appears, built automatically from that Class's required and recommended Properties, exactly as Episode 4 promised — the fields you see are not hand-coded for this particular Class, they are generated from the Property definitions themselves, complete with the right datatype's input control and the description as a helpful hint.

Fill in the fields, and every keystroke is quietly becoming an Atom: this new Resource's Subject as the anchor, each filled field as a Property-Value pair hanging off it. Save it, and — if you've set up your Agent as described in Episode 7 — that save becomes a signed Commit, exactly as Episode 8 described, and the new Resource takes its place in whichever Collection matches its Class, exactly as Episode 9 described. Nothing about this final step is a special case; it is simply the whole taxonomy you've spent nine episodes learning to read, now running once, forward, in the ordinary direction: from an empty form to a tagged, classified, signed, and counted specimen, live in the reserve. And should the built-in resource types not match what you're actually trying to observe, the same + button, routed through an Ontology of your own making, lets you define an entirely new kind of specimen — the reserve does not limit you to the species it already knows.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| AtomicServer GUI (+ button) | A chosen resource type (Table, Folder, Document, or custom Class) | Generate a form from that Class's required/recommended Properties | A ready-to-fill creation form | The person tagging a new specimen |
| Person creating the resource | Filled-in field values | Convert each field into a Property-Value Atom under a new Subject | A newly assembled, unsaved Resource | The save action, the signing Agent |
| Signed-in Agent | The completed new Resource | Sign the creation as a Commit and submit it | A saved, classified, and now-countable Resource | The matching Collection, future visitors to the reserve |

Next stop: our specimen is tagged, but it doesn't live in isolation — the final episode looks outward, to how this reserve connects to every other reserve like it across the wider web.
