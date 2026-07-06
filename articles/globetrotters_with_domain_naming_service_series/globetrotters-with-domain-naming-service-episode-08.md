---
title: "Globetrotters with Domain Naming Service 🧹 Ep.8"
series: "Globetrotters with Domain Naming Service"
part: 8
organization: "the-software-s-journey"
tags: [dns, operations, ttl, observability, ownership]
---

## Episode 8: Housekeeping and the Night Audit

Every well-run hotel and every well-run village both live or die on the housekeeping nobody sees. This episode is the shift-change checklist for the whole DevBench naming operation.

Front-door listings (Lane A's VIP records) barely move, so a TTL of 300 seconds is plenty — long enough to spare the resolvers extra work, short enough not to slow a real failover. Village listings (Lane B, per-resident records) live much faster lives; because a stay lasts about two hours, a TTL of 30–60 seconds ensures a stale listing ages out well before its address gets handed to the next resident. The village itself should be a proper delegation — `devbench.company.internal` handed off to a platform-owned registry office, an `InfoBlox` tenant on the DDI plane being the natural choice — so that central DNS never even sees the churn. Every check-in and check-out should be automated end to end, whether by `RFC 2136` DDNS straight from the `DHCP` server or by an API call from the DevBench control plane; no human should ever be standing at the desk for a single resident's arrival or departure.

The scavenger is the night auditor: a scheduled walk through every listing in the delegated zone, comparing it against live leases and IPAM entries, evicting anything whose resident has already left. Someone has to own the whole operation outright — the delegated zone, its housing pool, the wildcard VIP listing, and the wildcard passport — and that someone should be the DevBench platform team, full stop, so there is never a question of who answers the phone when something drifts. Change management should hold the line too: zero change requests against central DNS for anything resident-level; central DNS only gets touched for the delegation itself or the VIP record. Every check-out event should trigger both an IPAM release and a DDNS delete, with the control plane retrying until both land — a resident is not considered gone until both records agree they are. Reverse listings (`PTR`) deserve the same care as forward ones; they are easy to forget and some visitors — logging tools, security tooling — depend on them quietly. If any guest from outside the fab network needs to reach these names at all, publish a separate, external view of the zone containing only the VIP entry — outsiders should never see a single resident-level listing.

Finally, none of this works without instruments on the dashboard: a metric on every DDNS add and delete, a metric on every scavenger run, and an alert the moment scavenger removals start climbing above a small, known baseline — that rising count is the earliest sign the automation itself is starting to slip.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| DevBench platform team | Ownership assignment | Hold accountability for zone, pool, VIP record, and wildcard cert | Single accountable owner for the whole naming surface | Auditors, on-call engineers, the platform itself |
| Scavenger job | Scheduled scan interval | Compare zone records to live leases/IPAM, evict orphans | Self-healing DNS state | Delegated zone, downstream clients |
| Observability pipeline | DDNS add/delete events, scavenger run results | Emit metrics, evaluate alert thresholds | Early warning of lifecycle-automation drift | On-call engineers, platform team |

Next stop: how all of this housekeeping quietly decides where every passport in the system comes from.
