---
title: "⚖️ Central DNS vs Platform-Authoritative DNS: The Responsibility Split"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 4
organization: "the-software-s-journey"
tags: [dns, infoblox, delegation, ownership, dns-planes]
---

## ⚖️ Central DNS vs Platform-Authoritative DNS: The Responsibility Split

Option D deliberately splits the DNS surface into two authoritative planes with disjoint responsibilities. Central DNS, hosted on the top-centre InfoBlox instance, holds exactly two record shapes relevant to DevBenches: one wildcard `A` record (`*.devbench A 10.20.30.40`) and one `NS` delegation (`devbench. ... NS platform-auth-dns. ...`). It changes at a rate of roughly zero writes per day, and it is owned by the corporate networking team. Its role is to answer the HTTP(S) leg directly via the wildcard match, and to refer the SSH leg onward to the platform-authoritative DNS via the delegation.

The platform-authoritative DNS, hosted on the top-right InfoBlox instance, holds the per-bench `A` and `PTR` records — `db-<uuid>.devbench…` — each carrying a TTL of 30–60 seconds. Its change rate is thousands of adds and deletes per day per fab, driven entirely by DDNS from the DHCP/IPAM stack, and it is owned by the DevBench platform team, not the corporate networking team. Its role is to answer the SSH leg with the specific per-bench IP; it is never queried on the HTTP(S) leg at all, because the wildcard match at Central DNS is sufficient on its own.

Two consequences follow directly from this split. Central DNS is unloaded: it sees zero per-DevBench operations, and corporate change-management SLAs — typically measured in hours or days, not seconds — are removed from the DevBench lifecycle entirely. And the wildcard and the delegation coexist safely, because DNS resolution rules prefer the more specific match: for `db-a1b2c3.devbench.company.internal`, the `devbench` delegation is more specific than the `*.devbench` wildcard, so the SSH leg reaches the platform-authoritative DNS and gets the per-bench answer, while the HTTP(S) leg is served by the wildcard on Central DNS. In practice, Option D deployments make this deterministic by keeping the wildcard-to-VIP answer on Central DNS and the per-bench answers on the platform-authoritative side, so each leg is consistently served by the plane that actually owns it.

In the analogy that makes this easiest to hold onto: the campus directory (Central DNS) carries only two entries — the main entrance's address, and a note saying "for the direct service routes, ask the on-site facilities office." The facilities office (the platform-authoritative DNS) is the only place that knows which specific building a given service team needs, and it is never asked about guests heading to the main entrance.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Corporate networking team | Wildcard `A` and `NS` delegation requests | Publish and maintain exactly two static entries | Near-zero-churn Central DNS zone | HTTP(S) clients, platform-authoritative DNS (via referral) |
| DevBench platform team | DDNS add/delete events from DHCP/IPAM | Maintain per-bench `A`/`PTR` records with short TTLs | High-churn, self-contained delegated zone | SSH/SCP clients, direct-access consumers |
| DNS resolution rules (RFC-defined specificity) | Wildcard record + delegation record for overlapping names | Resolve each query to the more specific matching record | Deterministic leg selection per traffic class | Both HTTP(S) and direct-access clients |

Next stop: weighing what this hybrid actually buys you against what it costs to run — the pros, the cons, and the operational fine print.
