---
title: "Species with AtomicServer 📓 Ep.8"
series: "Species with AtomicServer"
part: 8
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, commits, audit-trail]
---

## Episode 8: Entries in the Field Journal

A ranger's signature is only worth something if it is attached to an actual entry — a specific correction, a specific new specimen logged, a specific date and hand behind it. That entry, in AtomicServer, is the Commit: a signed record of a change made to a Resource, and the mechanism by which every edit in the reserve becomes both real and verifiable.

You can watch this happen with your own hands the first time you set up a root Agent. Hover over a Resource's description field, click the edit icon, make a small change, and save it — an ordinary enough action, except that behind the scenes, that action has just produced a Commit, signed by your Agent, and attached permanently to that Resource's history. Curious what that looks like underneath the friendly form? Press the menu button — three dots, top left — and select `Data view`. There, beside the description you just edited, you'll find your own Agent listed after the `write` field: the reserve's own quiet way of saying "this ranger has permission to log entries here, and here is proof of the most recent one."

This is the same discipline any respectable field journal enforces, just automated. A specimen's record does not simply mutate in place, unaccountably, from one observation to the next; each change is a discrete, attributed, checkable entry, and the full sequence of them is what lets a future naturalist reconstruct not just what is currently known about a specimen, but who came to know it, and in what order. Commits are what makes AtomicServer's data trustworthy over time rather than merely current — the difference between a field guide you can cite and a rumour passed along the trail.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---:|---|
| Agent | An edited field on a Resource (e.g. a changed description) | Sign the change as a Commit using the Agent's private key | A verifiable, attributed entry added to the Resource's history | The Resource's ongoing record, future readers |
| AtomicServer | An incoming signed Commit | Validate the signature against the Agent's public key/DID and apply the change | An updated Resource with an auditable trail | Anyone viewing the Resource afterward |
| AtomicServer GUI (Data view) | A request to inspect a Resource's underlying data | Surface the `write` field and the Agent attached to it | A transparent view of who may edit, and who has | The person auditing or trusting the record |

Next stop: individual specimens are interesting, but a naturalist eventually wants to know the whole population at a glance — enter the Collection.
