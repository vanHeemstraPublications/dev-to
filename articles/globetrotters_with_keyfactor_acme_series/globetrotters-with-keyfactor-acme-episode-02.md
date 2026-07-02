---
title: "Globetrotters with Keyfactor ACME 🧳 Ep.2"
series: "Globetrotters with Keyfactor ACME"
part: 2
organization: "the-software-s-journey"
tags: [keyfactor, acme, pki, preparation, oauth, templates]
---

## Episode 2: Packing for the Trip

No seasoned globetrotter shows up at the airport without checking their documents first. Before the Keyfactor ACME agency can open its doors, someone has to prepare the office: gather the right paperwork templates, agree on how staff will authenticate with headquarters, and set up the physical counter itself.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| PKI administrator | Keyfactor API details, security role definitions | Grant the ACME service account the right permissions in Keyfactor Command | A service account able to enroll, and optionally revoke, certificates | Keyfactor ACME server |
| Certificate template owner | Template configuration | Configure templates to grant Read and Enroll permissions to the ACME user, and support CSR enrollment | Approved travel-document templates | ACME clients requesting certificates |
| Windows/IIS administrator | Authentication method (OAuth, Windows, or Basic) | Decide and configure how the agency authenticates to headquarters | A working, verified connection to Keyfactor Command | Keyfactor ACME server |

### The paperwork nobody skips

If the agency plans to let travelers cancel a trip, it needs revoke rights: granting the ACME user Certificates > Collections > Revoke permissions in Keyfactor Command. If it will only ever issue new documents, that permission can stay out of the stack. Either way, the certificate templates used must grant Read and Enroll permissions to the ACME service account and must be configured to support CSR enrollment, the equivalent of making sure the visa application form itself is accepted at the counter.

### Choosing how staff sign in

For Windows IIS installs, the connection from the agency to headquarters can be authenticated with OAuth, Windows authentication, or Basic authentication, and the right choice depends entirely on how Keyfactor Command itself is configured. Since version 25.1, the server exclusively supports OAuth for client authentication, so Active Directory can no longer be used to hand out new travel credentials. Existing AD accounts that were already in the system keep working after an upgrade, migrated quietly into claims of type Active Directory User, but new travelers must check in through OAuth.

### A packed bag, not a full itinerary

None of this preparation issues a single certificate yet. It simply makes sure that when the doors open, the agency already knows which embassies it can call, which forms are pre-approved, and how it proves its own identity. Episode 3 is moving day: getting the office itself built, whether on a Windows server or inside a Kubernetes cluster.

