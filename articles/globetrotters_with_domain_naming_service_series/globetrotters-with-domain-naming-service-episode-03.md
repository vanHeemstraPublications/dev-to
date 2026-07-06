---
title: "Globetrotters with Domain Naming Service ⛺ Ep.3"
series: "Globetrotters with Domain Naming Service"
part: 3
organization: "the-software-s-journey"
tags: [dns, scalability, ddi, dhcp, automation]
---

## Episode 3: The Pop-Up Campsite Problem

Imagine a campsite that pitches thousands of tents a day, each one standing for about two hours before it is struck and a different tent goes up on the same patch of ground. Now imagine every single tent needs its own listing in the national address book the moment it goes up, and that listing needs to disappear the moment it comes down. That is the DevBench, and it is exactly the workload a classic central-address-book model was never built to handle.

A DevBench lives for roughly two hours — long enough for its listing to go stale within a single working shift. At the scale the company is targeting, thousands of these tents can be pitched and struck in a single day, which means thousands of address-book creates and thousands of deletes, every day, per fab. Because the ground itself (the IP) gets reused the moment a tent is struck, a listing left behind even briefly points the next visitor at somebody else's tent — or worse, another guest's group entirely. And because the campsite runs continuously, there is no calm season where the address book can catch its breath; it is always mid-churn.

The failure here is not that the address book runs out of pages. It is operational strain on a shared front desk. Central DNS is typically staffed by a corporate networking team working to change-management SLAs measured in hours or days, not seconds — and every uniquely-named tent is a write against that shared desk. Two thousand tents a day is two thousand check-ins and, ideally, two thousand check-outs, every day, per fab, per environment. Miss a check-out — an agent crash, a dropped network link, a lease that expired without telling anyone — and stale listings pile up, quietly pointing new guests at tents that now belong to someone else. A "family visa" covering the whole campsite (a naive wildcard) looks like an easy way out, but a wildcard aimed at a shifting pool of tents is not a way to find a specific one — that pitfall gets its own episode later. And a pre-numbered set of pitches (`db-001` through `db-2000`, pre-wired for power) only works if every stage of the pitch-and-strike cycle — hand out, reclaim, sweep — is fully automated; half-automate it and within days you are left with plots "reserved for someone who packed up weeks ago."

The core observation carries the whole series forward: this is a lifecycle-automation problem wearing a DNS costume. Bigger zone files and faster address-book printers do not fix a gap in who is responsible for striking the tent.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Virtual Fab test-run pipeline | DevBench create/destroy request (per test run) | Provision or tear down a DevBench and its name/IP pair | Short-lived, uniquely addressable DevBench | Test execution, Jenkins, testers |
| Central DNS control plane | High-frequency create/delete writes | Absorb (or reject, if overwhelmed) per-bench registration churn | Change-managed, SLA-bound record updates | Every consumer relying on central DNS |
| Lifecycle automation (or its absence) | DevBench destroy event | Reclaim IP, delete DNS record | Clean address-book state, or a stale record if automation fails | Next tenant to receive the reclaimed IP |

Next stop: the first of two ways to stop a pop-up campsite from overwhelming the front desk.
