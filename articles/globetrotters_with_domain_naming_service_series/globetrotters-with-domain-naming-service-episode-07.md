---
title: "Globetrotters with Domain Naming Service 🚦 Ep.7"
series: "Globetrotters with Domain Naming Service"
part: 7
organization: "the-software-s-journey"
tags: [dns, architecture, tls, dhcp, ipam, recommendation]
---

## Episode 7: Two Lanes at the Border

Any border crossing that handles both tour buses and independent travelers eventually learns to build two lanes instead of forcing everyone through one. The recommended DevBench architecture does exactly that: Option A and Option B running side by side, chosen by traffic type rather than as a single global switch.

The default lane is the hotel from Episode 4. Register `*.devbench.company.internal` as a wildcard pointing at the existing `F5 LTM` VIP, terminate TLS there with the wildcard passport, issue and rotate it through the `cert-manager` + `Keyfactor ACME Server` pipeline already in place for the cluster, and route each arriving guest to the correct DevBench by `SNI` or `Host` header against a chart the DevBench control plane keeps current. Every HTTP/HTTPS DevBench conversation travels through this lane.

The second lane is the village from Episode 5, reserved for direct reachability. Delegate `devbench.company.internal` to a platform-owned registry office — an existing `InfoBlox` tenant fits naturally. On check-in, deterministically assign `db-<uuid8>.devbench.company.internal`, draw an IP from the housing pool, hand out a bound `DHCP` lease, and let the `DHCP` office file the `DDNS` add; on check-out, reverse every step. Short leases (30–60 seconds) and a scheduled inspector keep the neighborhood honest. SSH/SCP from Jenkins, and any other traffic that insists on a direct knock, travels through this lane and only this lane.

Two rules hold the whole crossing together. Central DNS is never allowed to see individual residents — it holds only the delegation `NS` and the wildcard `A`, nothing else, ever. And nobody is ever allowed to aim a wildcard at a pool of residents, the Episode 6 mistake — wildcards exist purely for `SNI`/`Host` fan-in into a single VIP. Underneath both lanes sits one governing principle: DNS is treated as an *output* of the DevBench's lifecycle, never an input. The control plane owns every check-in and check-out; DNS and IPAM simply follow along, and no operator ever edits either by hand.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| DevBench control plane | Lifecycle event (create/destroy) | Emit the matching update on both lanes (routing-table change or DDNS/IPAM change) | Correct DNS/routing state on whichever lane applies | HTTPS clients (Lane A), SSH/direct clients (Lane B) |
| F5 LTM / reverse proxy | HTTPS traffic addressed to `*.devbench…` | Terminate TLS, route by SNI/Host | Delivered HTTPS session to the correct DevBench | HTTPS clients, testers, ADEL equipment config flows |
| Platform-owned InfoBlox tenant | DDNS/DHCP/IPAM events for the delegated zone | Maintain forward/reverse records with short TTLs, run the scavenger | Correct, self-healing direct-reachability records | Jenkins (SSH/SCP), non-HTTP protocol clients |

Next stop: keeping the border crossing honest once it is up and running — the housekeeping that never gets to stop.
