---
title: "🎫 Proving Control on the Direct Leg: The Per-Bench Challenge"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 8
organization: "the-software-s-journey"
tags: [acme, dns-01, http-01, per-bench-certificate, pki-client]
---

## 🎫 Proving Control on the Direct Leg: The Per-Bench Challenge

On the direct-access leg, the proof is placed once per DevBench, at each DevBench's own service door, rather than once for the whole subdomain. The certificate being issued is a per-bench certificate whose name matches exactly the DevBench being claimed — `db-a1b2c3.devbench.company.internal` — and it lives on that specific machine. The requester is the SUT-side PKI Client's ACME Adapter, driven by the same DevBench lifecycle event that already creates the name in the platform-authoritative DNS.

The prerequisite is that the DDNS add for `db-a1b2c3` has already been published by DHCP/IPAM. From there: the DevBench control plane asks the PKI Client's ACME Adapter for a certificate (step one, ask), which crosses the firewall(s) to reach Keyfactor — the ACME Adapter is the only component on the SUT side that makes this crossing. Keyfactor replies with a challenge, either `HTTP-01` or `DNS-01` (step two). Under `HTTP-01`, the ACME Adapter places the token at `/.well-known/acme-challenge/<token>` on the DevBench itself, and Keyfactor's verifier fetches it over the resolved name via the delegated DNS (step three). Under `DNS-01`, the ACME Adapter instead issues a DDNS add for `_acme-challenge.db-a1b2c3.devbench.company.internal TXT=<token>` on the platform-authoritative DNS, and Keyfactor's verifier reads that `TXT` record directly, after which the temporary record is retracted. Either way, once verification succeeds, Keyfactor Command signs the certificate against the configured CA, and the ACME Adapter installs the resulting certificate — `SAN=db-a1b2c3.devbench.company.internal` — on the DevBench, pinned to its roughly two-hour lifetime.

`DNS-01` sits most naturally alongside this pipeline, because the same automation that publishes the DevBench's `A` record can also publish the temporary challenge record — no additional operational surface beyond what Option B already introduces for naming. `HTTP-01` is equally viable but requires the certificate authority to be able to reach the DevBench directly for the challenge step. What makes this proof comfortable is that the challenge is answered by the same machine the certificate will identify, so the proof step and the certificate SAN line up one-to-one: an auditor can tie any past test to a specific certificate, and therefore to a specific DevBench, which is impossible to achieve with a shared wildcard. Because certificate lifetime tracks DevBench lifetime, short-lived certificates are effectively self-revoking — issued at DDNS add, gone at DDNS delete, with no separate revocation step required in the normal case.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| SUT-side PKI Client ACME Adapter | newOrder for `db-a1b2c3.devbench.company.internal` | Ask Keyfactor ACME Server for a per-bench certificate | HTTP-01 or DNS-01 challenge with a fresh token | Keyfactor ACME Server |
| DevBench (HTTP-01) or Platform-Authoritative DNS (DNS-01) | Challenge token to place | Serve the token at the well-known location, or publish it as a TXT record | Verifiable proof of control over that specific name | Keyfactor ACME Server (verifier) |
| Keyfactor Command + Configured CA | Verified order and CSR | Sign the per-bench certificate | Installed certificate pinned to DevBench lifetime | The specific DevBench, and any auditor tracing that test run |

Next stop: the shortcut that looks like a compromise between these two proof models — and why it breaks the whole idea of proof.
