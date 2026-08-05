---
title: "Globetrotters go EAB 🛂 Ep.1"
series: "Globetrotters go EAB"
part: 1
organization: "the-software-s-journey"
tags: [acme, eab, certbot, tls, introduction]
---

## Episode 1: Some Borders Want More Than a Passport

Based on https://github.com/ConsortiumGARR/idem-certbot/

Picture our globetrotters, backpacks stuffed, passports freshly stamped, striding up to the border of Let's-Encrypt-Land like they own the place. And why not? Let's Encrypt is famously the easygoing border post of the internet — show up with a domain you control, prove it, and you're in, certificate in hand, no questions asked about who sent you.

Some borders post a sterner sign at the gate: "Members and Sponsored Guests Only." You need a sponsor letter — proof that an organization the CA already trusts has vouched for you. In ACME, that's External Account Binding, EAB, and this series is about our globetrotters learning to travel with one stapled into their passport.

This is exactly the border Consortium GARR's members cross for certificates issued through GARR's own ACME-with-EAB service. Rather than have every sysadmin hand-write the same border-crossing routine every few months, GARR built [`idem-certbot`](https://github.com/ConsortiumGARR/idem-certbot): a fully automated Certbot, running in Docker, that manages both ACME account registration and certificate issuance — with or without a sponsor letter, depending on what the destination border wants.

And here's the detail that makes this trip genuinely interesting rather than a single border crossing: `idem-certbot` doesn't just support solo travelers. It ships with two travel styles built right in. **Standalone mode** — every node manages its own passport and its own visa, independently. **Centralized mode** — one designated node does the actual border crossing, and everyone else's identical papers get couriered to them afterward by rsync, so the whole fleet ends up holding the same valid certificate without every single member queueing at the same gate. We'll cover both properly later in the trip; for now, just know that this suitcase was packed for a group tour as readily as for a solo backpacking trip.

Passports out. Let's go.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| ACME Certificate Authority (EAB-gated) | A request for a new ACME account | Require proof of external sponsorship before issuing anything | An account-creation gate that only opens with valid EAB credentials | Organizations and individuals requesting certificates |
| Consortium GARR (`idem-certbot`) | Domains, admin email, and CA server URL, with or without EAB credentials | Run Certbot inside Docker, in Standalone or Centralized mode | Automated, renewing TLS certificates for the requested domains | GARR members and IDEM-adjacent infrastructure needing certificates |
| Certbot (`certbot/certbot:v5.1.0`, wrapped) | `--eab-kid` / `--eab-hmac-key` flags or their absence | Build the correct ACME account-registration request for the target CA | A registered ACME account, EAB-bound or not | The domain owner's server(s) |

Next stop: what's actually written on that sponsor letter — the Key ID and the HMAC key that make External Account Binding tick.
