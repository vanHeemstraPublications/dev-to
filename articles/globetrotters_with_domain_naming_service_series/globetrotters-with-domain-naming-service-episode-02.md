---
title: "Globetrotters with Domain Naming Service 🛂 Ep.2"
series: "Globetrotters with Domain Naming Service"
part: 2
organization: "the-software-s-journey"
tags: [dns, tls, pki, certificates, security, rfc6125]
---

## Episode 2: Papers Please: Names, Not Faces

Border control does not recognize travelers by their face. It recognizes them by what is printed on the document they hand over, checked against the name they gave at the counter. TLS works the same way: it is name-based, not address-based, and every client opening a connection to a DevBench checks three things against the passport it is handed.

First, does the passport trace back to an authority the border trusts — the `Root Certificate Authority`, distributed to every checkpoint via the `Trust Store`. Second, is the document still valid — not expired, not revoked. Third, and this is the one globetrotters most often get wrong, does the name the traveler actually asked for appear on the passport's photo page, the `Subject Alternative Name` (`SAN`), either written out in full or covered by a family visa (a wildcard entry like `*.devbench.company.internal`). Modern border posts — every current browser, every current TLS library — no longer even glance at the old nickname field on the cover (the `Common Name`); they go straight to the `SAN` page, per `RFC 6125` and its successor `RFC 9525`.

This has two consequences a travel planner cannot ignore. A DevBench that only has an IP address and no name is a traveler with no passport at all — no modern checkpoint will let it through over HTTPS without switching off name-checking entirely, and switching off name-checking is precisely the shortcut the project's Downgrade Guard (FR-08) exists to block. And whatever name the traveler actually uses at the counter has to be the same name printed in the address book (DNS) and on the passport (the certificate). If DevBenches travel under disposable aliases like `db-a1b2c3.devbench.company.internal`, either every alias needs its own passport, or every alias needs to funnel through a single checkpoint that carries one family visa covering the whole street. The next two episodes cover each of those routes in turn.

In short: the address book is the foundation the border post's trust is built on. Any naming decision for DevBenches is, quietly, also a passport decision.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Root Certificate Authority / Trust Store | Trusted root chain | Anchor certificate trust | Verifiable chain of trust | Every TLS client |
| Certificate issuer (cert-manager / ACME) | Requested hostname(s) | Issue certificate with matching SAN | Certificate whose SAN matches the queried name | DevBench, reverse proxy |
| TLS client | Hostname typed by the user/tooling | Validate chain, validity window, and SAN match | Accept or reject the connection | Any consumer of the DevBench (Jenkins, testers, tooling) |

Next stop: what happens to that address book when thousands of travelers check in and out of a pop-up campsite every single day.
