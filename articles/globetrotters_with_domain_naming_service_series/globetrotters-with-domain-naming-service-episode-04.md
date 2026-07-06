---
title: "Globetrotters with Domain Naming Service 🏨 Ep.4"
series: "Globetrotters with Domain Naming Service"
part: 4
organization: "the-software-s-journey"
tags: [dns, wildcard, load-balancing, tls, f5, sni]
---

## Episode 4: One Reception Desk for a Thousand Rooms

The first way to tame the pop-up campsite is to stop listing every tent in the national address book at all, and instead list one grand hotel with a single, unchanging front door. That is Option A: keep the address book almost entirely static, and push all the per-guest routing into a reception desk sitting in front of the rooms.

The shape is simple. One delegated street name, `*.devbench.company.internal`, resolves through a single wildcard entry to a stable Virtual IP — the hotel's front door — owned by the platform. That door is staffed by the existing `F5 LTM Load Balancer` (or an equivalent reverse proxy), which answers every knock with the same passport check, a single family-visa certificate covering `*.devbench.company.internal`. The guest's actual room number travels in the name they used to knock (`db-a1b2c3.devbench.company.internal`) or in a header, and the reception desk — using `SNI` plus a room chart kept current by the DevBench control plane — walks them to the right room.

The payoff shows up immediately in the numbers. DNS write rate drops to almost zero, because the wildcard and the front-door records almost never change. Passport overhead shrinks to one certificate (or a small family of them) for the whole hotel, renewed through the same `cert-manager` + `Keyfactor ACME Server` pipeline already running for the cluster. The guest never needs a direct line of sight to their room — they only ever need to reach the front door — which means a hiccup at the desk stays contained to the desk; DNS is nowhere near the hot path when a lifecycle event fires.

Option A earns its keep whenever the traffic is the kind a front desk can actually route: HTTP(S) traffic that can be muxed by `SNI` or `Host` header (the `ADELequipmentConfig` and `Connect` interactions fit neatly here), and where no guest needs to knock on an arbitrary door directly with an arbitrary kind of key — SSH being the one guest who insists on that, which is why it gets its own episode next. The one condition Option A asks for in return is that the platform accepts a reverse proxy as a hard dependency for reaching a DevBench at all.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Platform team | Wildcard DNS record request | Register `*.devbench.company.internal` → stable VIP | Static, near-zero-churn DNS entry | Central DNS, all HTTPS clients |
| cert-manager + Keyfactor ACME Server | Certificate request for the wildcard name | Issue and rotate one wildcard certificate | Valid `*.devbench.company.internal` certificate | F5 LTM VIP |
| DevBench control plane | Lifecycle events (create/destroy) | Update the SNI/Host routing table | Current name-to-backend mapping | F5 LTM VIP, incoming HTTPS clients |

Next stop: the guest who refuses to check in at the front desk and insists on a key to their own door.
