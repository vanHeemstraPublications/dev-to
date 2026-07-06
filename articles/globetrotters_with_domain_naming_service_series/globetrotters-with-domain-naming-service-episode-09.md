---
title: "Globetrotters with Domain Naming Service 🛃 Ep.9"
series: "Globetrotters with Domain Naming Service"
part: 9
organization: "the-software-s-journey"
tags: [dns, pki, tls, acme, certificates, security]
---

## Episode 9: Visas Tied to Your Itinerary

A visa is only useful for as long as the trip it was issued for. Everything this series has built toward lands here: the DevBench naming strategy is not a side concern to the Virtual Fab's HTTPS work, it is the thing that decides what shape every visa takes.

Follow Lane A and the DevBench itself never needs a passport at all — the family visa for `*.devbench.company.internal` lives at the front desk (`F5 LTM` / reverse proxy), which shrinks the whole passport office down to one document per environment instead of one per guest, renewed through the same `cert-manager` + `Keyfactor ACME Server` chain the cluster already trusts. Follow Lane B instead, and the DevBench must carry its own passport, `SAN` naming its own `db-<uuid8>.devbench.company.internal` address — issued by the SUT-side PKI Client's `ACME Adapter`, driven by the same lifecycle events already feeding the village's DDNS updates, whether by DNS-01 (which sits naturally alongside that pipeline) or HTTP-01.

This naming discipline is also what closes off the one failure mode the whole project has been guarding against. `HttpsStrategy`, in the codebase that drives these connections, cannot validate a peer reachable only by raw IP without switching off name-checking — exactly the regression the Downgrade Guard (FR-08) was built to prevent. Keep every DevBench reachable only by a name that resolves through one of these two honest lanes, and `HttpsStrategy` stays fully usable everywhere it needs to run.

And where per-resident passports are actually required, the trip length and the visa length should match exactly: issued the moment the DDNS record goes live, expired or revoked the moment it comes down. A DevBench lives about two hours, which sits comfortably inside what an ACME-driven passport office can turn around without straining its revocation desk — a short enough visa is, in effect, self-expiring. Aligning the two lifespans is what keeps per-resident passports cheap to run; letting a long visa outlive a short trip is exactly what makes them expensive and error-prone instead.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| cert-manager + Keyfactor ACME Server | Wildcard certificate request | Issue and renew `*.devbench.company.internal` cert | Single, environment-wide certificate | F5 LTM VIP (Lane A) |
| SUT-side PKI Client ACME Adapter | Per-DevBench DDNS lifecycle event | Issue per-bench certificate via DNS-01/HTTP-01 | Short-lived, per-resident certificate | Individual DevBench (Lane B) |
| DevBench control plane | Create/destroy lifecycle event | Align certificate issuance/expiry to DevBench lifetime | Certificate churn matched to DNS churn | PKI issuer, downstream TLS clients |

Next stop: the trip report — what worked, what still needs a decision, and what to fix before the next journey.
