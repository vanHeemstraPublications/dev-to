---
title: "🚫 Why Option C Fails: The Anti-Pattern Challenge"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 9
organization: "the-software-s-journey"
tags: [acme, anti-pattern, wildcard-dns, security, dns]
---

## 🚫 Why Option C Fails: The Anti-Pattern Challenge

Option C is not a deployment recommendation; it is drawn only to show why the ACME challenge cannot be arranged soundly on top of a wildcard-to-pool DNS shape. It is explicitly ruled out by the recommended architecture: never point a wildcard at a pool of DevBench IPs. The shape is a single wildcard record, `*.devbench.company.internal`, resolving to a round-robin set of DevBench IPs rather than a single VIP. Because the wildcard returns the same answer set regardless of the queried name, the certificate authority's verifier — fetching the proof over that name — may land on a different DevBench than the one that actually placed the proof.

Trace it through: the SUT-side PKI Client's ACME Adapter asks Keyfactor for a certificate identifying `db-a1b2c3.devbench.company.internal` and places the challenge token on that specific DevBench, `DB1`. Keyfactor's verifier queries the wildcard-to-pool DNS for that same name and gets back the whole round-robin set — `[DB1, DB2, … DBN]` — with no way to know which member the requester actually controls. If the verifier's resolver happens to pick `DB1`, the challenge succeeds, but only by luck, not by design. If it picks `DB2` or any other unrelated pool member instead, the challenge fails outright — even though the requester genuinely controls the name in the wildcard sense. Either outcome is a red flag: a proof that can succeed by chance is not a proof at all.

Even in the lucky case, the deeper problem does not go away. Because clients cannot predict which pool member they will be sent to, every DevBench in the pool would have to present a certificate covering the queried wildcard name — forcing the shared-wildcard identity onto every DevBench and erasing the per-bench audit property that Option B's model is built to provide. Naming, routing, and identity stop lining up: a wildcard is a hostname-matching mechanism, not a routing mechanism, and layering an identity-critical proof on top of a routing model that has no per-name identity means the certificate can be right by accident and wrong for the same reason. And if pool membership is not strictly scoped per tenant, the same wildcard-to-pool arrangement that breaks the challenge can also leak IPs across tenants — a security regression stacked directly on top of a broken certificate model, not a simplification of anything.

The lesson to carry forward is the same one that closed out the DNS-only half of this discussion: a wildcard is for matching names to a single, known destination, never for spraying clients — or certificate verifiers — across an undifferentiated pool. Option D avoids this failure mode by construction, because the wildcard on its HTTP(S) leg points at exactly one VIP, and per-bench identity on its direct leg is proven at the DevBench itself. Neither leg reproduces the shape that makes Option C unsound.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Wildcard-to-pool DNS (anti-pattern) | Query for any `db-<id>.devbench.company.internal` name | Return an undifferentiated round-robin answer set | Non-deterministic, non-identity-preserving address | Unwitting ACME verifier or client |
| Keyfactor ACME Server (as verifier in this broken shape) | Fetch attempt against a randomly-resolved pool member | Verify (or fail to verify) a challenge placed on a different member | Unreliable pass/fail result, not tied to actual control | PKI Client's ACME Adapter, and ultimately no trustworthy certificate |
| Architecture review (this analysis) | Documented failure modes | Rule the pattern out explicitly | Clear rationale for choosing Option A, B, or D instead | Platform architects, security reviewers |

Next stop: back to the sound designs — how Option D runs both proof models side by side without ever touching this failure mode.
