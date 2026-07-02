---
title: "Globetrotters with Keyfactor ACME 🗺️ Ep.5"
series: "Globetrotters with Keyfactor ACME"
part: 5
organization: "the-software-s-journey"
tags: [keyfactor, acme, identifiers, validators, dns01, http01]
---

## Episode 5: Proving Where You Live

An embassy will not hand over a visa just because someone claims to live somewhere. They ask for proof: a utility bill, a lease, something only a real resident could produce. ACME asks domains for the same kind of proof before it will issue a certificate, and in Keyfactor ACME that proof is arranged through the Identifiers command and its validators.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Domain owner | Domain name, DNS or web server access | Respond to the agency's proof-of-residency challenge (HTTP-01 or DNS-01) | A completed domain validation | Keyfactor ACME server |
| Operations engineer | Identifiers command configuration | Configure which validators are enabled and how they resolve challenges | Configured identifier validation rules | ACME clients requesting certificates for those domains |
| DNS infrastructure | TXT records, CNAME chains | Publish or forward the proof records the validator needs to see | Verifiable DNS-01 challenge response | Keyfactor ACME validator |

### Two kinds of proof

Just as a traveler might prove residency with a utility bill (something visible at the address itself) or a notarized letter from their own government (something a third party vouches for), ACME domain validation typically works through HTTP-01, placing a file at a well-known path on the web server, or DNS-01, publishing a TXT record under the domain's own DNS zone. Either way, the agency is checking that whoever is asking for the certificate genuinely controls the address in question.

### Chasing the paper trail through CNAME hops

Real residency proof sometimes gets forwarded through a chain of intermediaries, a landlord who passes mail on to a property manager, who passes it on again. The DNS01 validator handles the equivalent case: it now follows CNAME records through multiple hops, up to a maximum of one hundred, to find the TXT record actually configured for the _acme-challenge subdomain. Large organizations that centralize DNS challenge records behind a chain of delegations do not need to break that chain just to satisfy the validator.

### Why this step cannot be skipped

Skipping proof of residency would mean the agency hands out visas to anyone who simply asks, a fast way to lose the trust of every embassy it works with. The Identifiers and validators step is what lets Keyfactor ACME, and by extension the CAs behind it, keep issuing certificates that mean something. Episode 6 turns to a different kind of paperwork: who is even allowed to walk up to the counter in the first place.

