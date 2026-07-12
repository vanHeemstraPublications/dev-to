---
title: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service 🔑 Ep.6"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 6
organization: "the-software-s-journey"
tags: [acme, tls, pki, dns-01, http-01, certificates]
---

## Episode 6: The ACME Challenge: What It Proves and How It Works

Before Keyfactor will issue a certificate for a name like `db-a1b2c3.devbench.company.internal`, it insists on one thing: proof that the requester really controls that name today. That proof step is the ACME challenge — the moment "we say we own this name" becomes "we have demonstrated we own this name."

Certificates only mean something if they are hard to fake. A certificate authority will not sign a certificate for a name just because someone asked for it; anyone could otherwise request a certificate for someone else's name and quietly impersonate them. So the authority picks a short-lived secret and asks the requester to place it at a specific spot tied to the name being claimed. Only the party that genuinely controls the name can put the secret in the right spot. If the authority can then fetch that secret from that spot, control is proven and a certificate is issued; if the spot is wrong, empty, or holds the wrong value, no certificate is issued.

Two shapes of "the right spot" matter here. `HTTP-01` places the secret at a specific web location under the name being claimed, and the authority fetches it over HTTP. `DNS-01` places the secret inside a specific DNS entry under the name being claimed, and the authority reads it via a DNS query. Either shape works, but each requires the requester to control something specific — a web endpoint or a DNS zone — for the name in question, and that single requirement is exactly why different DevBench DNS scenarios end up using different challenge shapes.

Every issuance, regardless of scenario, goes through the same four steps: ask ("please issue a certificate for this name"), challenge ("first prove control — here is a fresh secret, place it at the spot tied to that name"), verify (the authority fetches the spot from the outside and checks the secret matches), and issue (if the check passes, the certificate is signed and returned; if it fails, nothing is issued). In the Virtual Fab, the certificate authority is Keyfactor — specifically the Keyfactor ACME Server, followed by Keyfactor Command and the configured CA. The requester is either cert-manager, on the cluster and front-door side, or the SUT-side PKI Client's ACME Adapter, on the DevBench side. Both speak the same standard ACME protocol; only their placement differs. The interesting part is never the four steps themselves — it is where step two places the proof, and who has to control that spot. That is what changes across Options A, B, C, and D, and it is what the next three episodes work through in turn.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| ACME requester (cert-manager or SUT PKI Client) | newOrder request for a given name | Ask the CA for a certificate | Issued challenge with a fresh token | Keyfactor ACME Server |
| Keyfactor ACME Server | Challenge token and proof-spot fetch | Verify the token at the spot tied to the claimed name | Pass/fail verification result | Keyfactor Command, Configured CA |
| Keyfactor Command + Configured CA | Finalised order and CSR after successful verification | Sign the certificate | Issued certificate matching the proven name | ACME requester, and ultimately the identity boundary (F5 VIP or DevBench) |

Next stop: how this four-step lifecycle plays out when the proof is placed once, at the front door, for the whole HTTP(S) leg.
