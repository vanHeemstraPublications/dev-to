---
title: "🧭 Option D Overview: The Recommended Hybrid Architecture"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 1
organization: "the-software-s-journey"
tags: [dns, architecture, tls, acme, devbench, virtual-fab]
---

## 🧭 Option D Overview: The Recommended Hybrid Architecture

Option D is the recommended target architecture for DevBench naming and access in the Virtual Fab. It does not introduce a new DNS pattern of its own — it layers two already-understood patterns, Option A (wildcard-to-VIP) and Option B (delegated subzone with DDNS), into a single deployment and picks the leg per traffic class rather than as a single global switch.

HTTP(S) traffic uses the wildcard-to-VIP leg: `*.devbench.company.internal` resolves in Central DNS to a single stable F5 VIP (`10.20.30.40`), which terminates TLS with a wildcard certificate and does SNI-based routing into the SUT. SSH, SCP, and any other non-HTTP direct traffic uses the delegated-subzone leg: Central DNS delegates `devbench.company.internal` to a platform-authoritative DNS (InfoBlox), fed by DDNS from a DHCP/IPAM stack driven by DevBench lifecycle events. Clients on this leg reach the DevBench directly at L3, with its own per-bench certificate.

Central DNS holds only two things regardless of which leg is in play: the wildcard `A` record and the `NS` delegation. It never sees per-DevBench churn on either leg. The moving parts, left to right, are the Virtual Fab Client (issuing both an HTTP(S) request and a direct SSH/SCP connection), the Central DDI plane (InfoBlox, holding the wildcard and the delegation), the Platform-Authoritative DDI plane (InfoBlox, holding per-bench records with TTL 30–60s and a scavenger), the F5 LTM (owning the VIP and terminating TLS), the Firewall(s) sitting on both legs, the System Under Test (housing the reverse proxy, the local Kubernetes cluster, the PKI Client, and the DevBench itself), and the Keyfactor plane (issuing and renewing both certificate types via the same ACME chain).

The blue path in the accompanying diagram is the HTTP(S) / wildcard-to-VIP leg; the red/pink paths are the delegated-DNS resolution and the direct SSH/SCP leg. Both legs coexist by design: the client picks the leg by protocol, and the DNS layer routes the lookup accordingly. The rest of this series works through each leg in detail, the responsibility split between the two DNS planes, the trade-offs of running both at once, and — in the second half — how the ACME certificate challenge is proven differently (and consistently) on each leg.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| DevBench platform team | Architecture decision to combine Option A and Option B | Deploy wildcard-to-VIP leg and delegated-subzone leg side by side | A single Option D deployment serving both traffic classes | Virtual Fab engineers, testers, Jenkins |
| Central DNS (corporate networking team) | Wildcard `A` record and `NS` delegation | Answer HTTP(S) lookups directly; refer direct-access lookups to the platform-authoritative DNS | Two static entries, zero per-bench churn | F5 LTM VIP, Platform-Authoritative DNS |
| Keyfactor plane | Certificate requests from both legs | Issue and renew wildcard and per-bench certificates via the same ACME chain | Valid certificates matching each leg's identity model | F5 LTM (wildcard), DevBench (per-bench) |

Next stop: a closer look at the HTTP(S) leg — how a single wildcard record and a single certificate carry traffic to thousands of DevBenches without Central DNS ever noticing.
