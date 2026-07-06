---
title: "Globetrotters with Domain Naming Service 📪 Ep.6"
series: "Globetrotters with Domain Naming Service"
part: 6
organization: "the-software-s-journey"
tags: [dns, wildcard, anti-pattern, security, tls]
---

## Episode 6: The Shared Mailbox Disaster

Every well-traveled itinerary has a shortcut that looks brilliant on paper and falls apart the moment a real guest tries to use it. Here it is: keep one wildcard listing, `*.devbench.company.internal`, but instead of pointing it at a single front door, point it at a round-robin pool of DevBench addresses directly. One listing, many possible answers, no bookkeeping. It sounds like the best of both worlds. It is not, for six independent reasons.

A wildcard hands back the same answer set no matter which name was actually asked for — a request for `db-a1b2c3` and a request for `db-9z8y7x` get identical mail. The name in the address has stopped meaning anything; it merely triggers the wildcard. From there, the guest's own resolver picks an answer more or less at random, with no way to know which one the platform actually intended — best case, it lands on the right doorstep one time in N; every other time, it walks straight into a different guest's room, quite possibly belonging to a different tenant entirely. TLS still checks the name it was given, which means every single tent in the pool would now need to carry a passport covering the whole wildcarded street, erasing the one benefit — traceable, individual identity — that a per-resident passport was supposed to buy. There is no clean way to check a guest out either: a struck tent's address either lingers in the answer set (a stale, dangerous leftover) or the whole wildcard has to be rewritten, which defeats the entire "no bookkeeping" promise in the first place. If the pool is not tightly scoped per tenant, addresses can leak across tenant lines — a straight security regression against either honest option. And because resolvers cache the wildcard's answer set for its full lifetime, shortening that lifetime only pushes the churn downstream without fixing the underlying wrongness of the answer.

The lesson worth carrying forward: a wildcard is a name-matching trick, not a way to find a specific address. Option A uses it correctly — pointed at exactly one front door, which then does the real routing. Aiming it at many doors at once mixes up two jobs that were never meant to share a listing.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Naive wildcard configuration | Query for any `*.devbench…` name | Return round-robin pool answer, ignoring the specific name asked | Non-deterministic, tenant-blind address | Unwitting client, wrong-tenant DevBench |
| Recursive resolver | Cached wildcard answer set | Serve cached pool for the TTL window | Amplified propagation of a wrong or stale answer | Every downstream client sharing that resolver |
| Anti-pattern reviewer (this analysis) | Observed failure modes | Document and reject the pattern | Clear rationale for choosing Option A or B instead | Architecture decision-makers |

Next stop: the itinerary that actually works, combining both honest routes into one journey.
