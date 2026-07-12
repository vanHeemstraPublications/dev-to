---
title: "🤝 Option D's Combined Challenge Model: Two Proofs, One Certificate Authority"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 10
organization: "the-software-s-journey"
tags: [acme, keyfactor, architecture, decision-making, tls]
---

## 🤝 Option D's Combined Challenge Model: Two Proofs, One Certificate Authority

Option D does not invent a new challenge model. It runs Option A's shared wildcard proof on the HTTP(S) leg and Option B's per-bench proof on the direct leg, at the same time, both terminating at the same `Keyfactor ACME Server → Keyfactor Command → Configured CA` chain. Only the proof spot and the renewal cadence differ between the two.

On the HTTP(S) leg, `cert-manager` asks for a certificate covering `*.devbench.company.internal`, receives a `DNS-01` challenge (required for a wildcard SAN), publishes the `_acme-challenge.devbench.company.internal` TXT record on Central DNS, and installs the resulting wildcard certificate on the F5 VIP once verified — exactly the flow from earlier in this series, on a slow and predictable renewal cadence. On the direct leg, the SUT-side PKI Client's ACME Adapter asks for a certificate for the specific DevBench, crosses the firewall to reach Keyfactor, receives either an `HTTP-01` or `DNS-01` challenge, answers it either by serving the token from the DevBench itself or by publishing a `TXT` record in the platform-authoritative delegated zone, and installs the resulting per-bench certificate pinned to that DevBench's lifetime. Neither sub-flow adds anything to Central DNS: the wildcard entry and the delegation `NS` remain the only DevBench-related entries it ever carries, on either the DNS side or the certificate side.

Each traffic class gets the proof shape that actually fits its identity model — one cheap, wide proof for web traffic; one proof per machine, provable in an audit, for direct-access traffic. Neither shape is forced to do the other's job, and the Option C anti-pattern is avoided by construction, because the wildcard on the HTTP(S) leg still points at a single VIP (Option A's rule) and per-bench identity on the direct leg is still proven at the DevBench itself (Option B's rule). No new PKI vendor and no new ACME endpoint is introduced by adopting Option D — it is a configuration of infrastructure already in place, not a new product.

Four decisions belong to leadership before this goes into production, and they carry over directly from the earlier discussion of the naming architecture itself: confirming that the F5 team owns the front door for DevBench HTTP(S) traffic and can meet the required availability; confirming that a single shared certificate for `*.devbench.company.internal` is acceptable on the HTTP(S) leg from a compliance standpoint; confirming that the DevBench platform team owns the delegated name area, its DDNS/IPAM automation, and its per-bench certificate issuance as a real, staffed service; and confirming with the corporate DNS owner that the wildcard rule and the delegation can coexist on Central DNS without ambiguity. Get those four confirmations, and Option D delivers what neither half could alone: web access that stays simple and cheap, and direct access that stays traceable, end-to-end encrypted, and honest about identity — with Central DNS never seeing more than two lines, on either the naming side or the certificate side, no matter how many DevBenches come and go underneath it.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| cert-manager (HTTPS-leg requester) | Wildcard certificate request | Complete DNS-01 challenge against Central DNS | Renewed wildcard certificate on the F5 VIP | HTTP(S) clients across every DevBench |
| SUT-side PKI Client ACME Adapter (direct-leg requester) | Per-bench certificate request | Complete HTTP-01 or DNS-01 challenge against the DevBench or delegated zone | Per-bench certificate pinned to DevBench lifetime | Direct-access clients, compliance auditors |
| Leadership / platform stakeholders | The four open confirmations above | Decide on F5 ownership, wildcard cert acceptability, platform team ownership, and DNS coexistence | A signed-off Option D deployment | DevBench platform team, security reviewers, Virtual Fab engineers |
