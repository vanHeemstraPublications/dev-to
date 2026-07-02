---
title: "Globetrotters with Keyfactor ACME ✈️ Ep.8"
series: "Globetrotters with Keyfactor ACME"
part: 8
organization: "the-software-s-journey"
tags: [keyfactor, acme, certbot, enrollment, renewal, revocation]
---

## Episode 8: Boarding, Renewing, and Deportation

Every traveler's story follows the same arc: check in, board, and eventually either renew the visa for another trip or have it cancelled outright. Keyfactor ACME carries a certificate through that same arc, from an ACME client's first registration to its eventual revocation.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Traveler (ACME client, e.g. Certbot) | EAB key, account registration request | Register an account with the Keyfactor ACME server | An authenticated ACME account bound to a claim and template | Keyfactor ACME server |
| ACME client | CSR, domain identifiers | Request issuance, or later renewal, of a certificate | An issued or renewed certificate, passed through Keyfactor Command | End service, website, or application |
| Certificate holder | Revocation request | Call the ACME server's revocation endpoint | A revoked certificate reflected in Keyfactor Command | Relying parties checking certificate status |

### Checking in at the gate

Before any boarding pass is issued, the traveler installs their ACME client of choice, such as Certbot, and uses their EAB key to register an account with the Keyfactor ACME server. That registration ties the traveler to a specific claim, and through it, to whichever certificate template governs what kind of document they are entitled to receive.

### Boarding, and re-boarding

Once registered, the client requests a certificate the same way it always has under ACME: submit identifiers, clear the domain validation checks from Episode 5, and receive an issued certificate. Renewal follows the identical path, which is the entire appeal of ACME travel over the old manual visa process: the same automated boarding gate handles the flight out and every return trip after it.

### Deportation, on request

Sometimes a trip needs to be cancelled outright. A POST /Revoke endpoint was added to the Keyfactor ACME API specifically to support certificate revocation, though this route is only open if the CertificateRevocationEnabled application setting has been switched on; otherwise, cancellations have to be handled directly in Keyfactor Command instead. As an added courtesy, EAB keys can now, optionally, be removed automatically when the account tied to them is revoked, so a departed traveler's old sponsorship paperwork does not linger in the system.

The individual traveler's journey is complete. Episode 9 zooms out to the airline alliance level: what happens when more than one Keyfactor ACME office needs to serve the same crowd of travelers at once.

