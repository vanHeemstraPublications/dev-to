---
title: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service 🏛️ Ep.7"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 7
organization: "the-software-s-journey"
tags: [acme, dns-01, wildcard-certificate, cert-manager, keyfactor]
---

## Episode 7: Proving Control on the HTTPS Leg: The Wildcard Challenge

On the HTTP(S) leg, one shared proof at the front door covers every DevBench name at once. The certificate being issued is a wildcard for `*.devbench.company.internal`, and it lives on the F5 front door, not on any individual DevBench. The requester is `cert-manager`, running in the Virtual Fab cluster, using the same automated path already used elsewhere in the environment. Every renewal goes through the same challenge.

Because the certificate is wildcard-shaped, the challenge type is `DNS-01` — `HTTP-01` cannot cover wildcard identifiers, per `RFC 8555` §7.1.3, so there is no branch to choose here. Concretely: `cert-manager` asks Keyfactor for a certificate covering `*.devbench.company.internal` (step one, ask). Keyfactor replies with a `DNS-01` challenge and a token (step two, challenge). `cert-manager` publishes `_acme-challenge.devbench.company.internal TXT=<token>` in a DNS zone the platform controls (this can be Central DNS itself, since the platform already owns the wildcard entry there). Keyfactor's verifier queries that `TXT` record directly (step three, verify) and, on a match, forwards the finalised order and CSR to Keyfactor Command, which signs it against the configured CA (step four, issue). The resulting wildcard certificate — `CN/SAN: *.devbench.company.internal` — installs on the F5 VIP, with an overlap window on renewal so the F5 is never caught presenting an expired certificate. It is then presented on every TLS handshake for every `db-<id>.devbench.company.internal` name that follows.

The individual DevBenches are not part of this proof at all. They never issue certificates, never see challenges, and never need to be reachable by the certificate authority for this leg's purposes. That is exactly why this proof is comfortable to operate: it happens once, for a name space the platform genuinely controls, on a slow and predictable renewal schedule — one operation, not thousands. What it cannot do is tell an auditor which specific DevBench a given connection actually reached; the certificate covers every DevBench name at once. That trade-off is deliberate, and it is the price this leg pays for its simplicity — the per-bench audit property lives on the other leg instead, which the next episode covers.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| cert-manager | newOrder for `*.devbench.company.internal` | Ask Keyfactor ACME Server for a wildcard certificate | DNS-01 challenge with a fresh token | Keyfactor ACME Server |
| Platform-controlled DNS zone | `_acme-challenge.devbench.company.internal` TXT publish request | Publish and later retract the challenge TXT record | Verifiable proof of subdomain control | Keyfactor ACME Server (verifier) |
| Keyfactor Command + Configured CA | Verified order and CSR | Sign the wildcard certificate | Installed wildcard certificate on the F5 VIP | Every HTTP(S) client reaching any DevBench |

Next stop: the mirror-image proof, done once per DevBench instead of once per subdomain, on the direct-access leg.
