---
title: "Globetrotters with Keyfactor ACME 🌐 Ep.9"
series: "Globetrotters with Keyfactor ACME"
part: 9
organization: "the-software-s-journey"
tags: [keyfactor, acme, load-balancing, high-availability, windows]
---

## Episode 9: The Frequent Flyer Alliance

A single travel agency counter can only serve so many travelers before the line stretches out the door. The fix is not a bigger counter, it is more counters, all reading from the same shared ledger so that no matter which desk a traveler walks up to, their file looks the same. That is Keyfactor ACME load balancing.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Infrastructure team | Multiple Windows servers, shared SQL database | Configure each Keyfactor ACME instance against the same database and hostname | A pool of interchangeable ACME server instances | ACME clients hitting any instance in the pool |
| Database server | Common ACME schema, port 1433 | Serve account, claim, and certificate data consistently to every instance | Consistent state across the whole pool | All Keyfactor ACME server instances |
| Operations engineer | Configure command parameters (shared hostname, database, OAuth settings) | Run configure on each node with matching connection details | Load-balanced, horizontally scaled ACME service | End users depending on certificate availability |

### One ledger, many counters

Multiple Keyfactor ACME servers can use a common database to allow for load balancing, which means the records room from Episode 7 is not duplicated per office; every counter reads and writes to the same shared file cabinet. Communication with that SQL server runs over the default port 1433, and since the agency talks to Keyfactor Command over ordinary API calls with no strict timeouts set on either side, a slower embassy response at one counter does not necessarily stall the whole alliance.

### Configuring the pool

Setting up each additional counter is mostly a repeat of the Configure Command from Episode 4, pointed at the same database, the same shared hostname, and the same OAuth authorities on both the client-facing and Command-facing sides. Every node in the pool needs to agree on those values, the same way every airport counter in an alliance needs to recognize the same frequent flyer number regardless of which city the traveler checks in from.

### A quiet convenience

It is even possible to push Keyfactor Command metadata through the ACME server as part of this shared setup, tagging every certificate that passes through any counter in the pool with the same tracking information. That is the alliance working as intended: from the traveler's side, there is only ever one Keyfactor ACME agency, no matter how many counters are actually running behind the scenes.

That closes the Globetrotters route map: from packing the office's paperwork through to a whole alliance of counters serving travelers at scale, Keyfactor ACME turns the RFC 8555 protocol into a working, automated border crossing for certificates.

