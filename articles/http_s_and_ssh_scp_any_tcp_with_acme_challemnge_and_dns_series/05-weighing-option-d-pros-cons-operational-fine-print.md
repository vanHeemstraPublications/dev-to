---
title: "🧮 Weighing Option D: Pros, Cons, and the Operational Fine Print"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 5
organization: "the-software-s-journey"
tags: [dns, operations, risk, ttl, observability, decision-making]
---

## 🧮 Weighing Option D: Pros, Cons, and the Operational Fine Print

Option D earns its recommendation on eight counts. It fits the traffic to the pattern rather than forcing one shape onto everything — HTTP(S) uses wildcard-to-VIP, SSH and arbitrary TCP use the delegated subzone, and neither is forced onto traffic it does not suit. Central DNS is unloaded completely, holding only one wildcard record and one `NS` delegation. The wildcard is used correctly — pointed at a single VIP that does the actual routing, never at a pool of DevBench IPs. Both TLS validation models work end to end on their respective legs, so any strict-verify client keeps working unmodified and the Downgrade Guard never needs to fire. Per-bench identity is available exactly where it is needed, without forcing that cost onto traffic that does not need it. Everything is lifecycle-driven, with no manual operator step in normal operation. Blast radius is split by leg — an F5 outage takes down HTTP(S) but not SSH; a platform-authoritative DNS outage takes down direct-name resolution but not HTTP(S). And the whole design reuses existing infrastructure: both DDI planes are InfoBlox, and both certificate types issue through the existing Keyfactor ACME chain.

The honest costs run in parallel. Running two moving parts means two sets of automation, two failure modes, and two on-call surfaces. Two certificate lifecycles — a rarely-renewed, high-blast-radius wildcard and frequently-renewed, bench-lifetime-pinned per-bench certificates — share the same Keyfactor chain but have different operational rhythms. Resolution-path ambiguity becomes a real design responsibility: Central DNS holds both a wildcard and a delegation for names inside the same subdomain, and deployments must keep the wildcard-to-VIP answer on Central DNS and the per-bench answers on the platform-authoritative side so each leg is served by the plane that owns it — getting this wrong sends HTTP(S) traffic to a per-bench IP or SSH traffic to a VIP that will not answer SSH. The wildcard certificate concentrates risk on the HTTP(S) leg: one private key, one rotation window, affecting all HTTPS access at once. Direct-leg firewalling has to be scoped per subnet or per-bench IPAM pool rather than to a single VIP. The DDNS/IPAM/scavenger stack is a real service that silently degrades if missed deletes, IPAM leaks, or scavenger misconfiguration go unwatched. TLS on the HTTP(S) leg is not end-to-end from the client's perspective — it terminates at the VIP, with the backend hop either plaintext-on-trusted-network or re-encrypted. And clients have to know, even if only implicitly through the URL scheme, that HTTP(S) and direct TCP take different paths with different identity models.

A handful of assumptions have to hold for any of this to work: traffic classes must be cleanly separable by protocol; Central DNS must support the wildcard-plus-delegation combination and honour both correctly; the platform-authoritative DDI stack must be available or provisioned, with a team willing to own it; the F5 tier must be sized and operable at DevBench request volumes; both certificate types must issue through the same Keyfactor ACME chain with no manual step; and split-horizon behaviour must be defined so that external clients only ever see the wildcard-to-VIP answer.

On the operations side, the numbers worth remembering: 300-second TTL on the wildcard VIP record, 30–60-second TTL on per-bench records, a scavenger run on a schedule (every five minutes is a reasonable starting point) with alerting on any rise above a small baseline, per-bench certificates pinned to the roughly two-hour DevBench lifetime, and metrics on wildcard-cert days-to-expiry, F5 routing-table size and change rate, DDNS add/delete rate, IPAM allocation depth, scavenger removals per run, and per-bench certificate issuance rate and failures. A rising handshake-failure rate at the VIP is the earliest signal of a wildcard-rotation problem; a rising scavenger count is the earliest signal of a DDNS-lifecycle problem.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Architecture review (this analysis) | Option D design as deployed | Weigh strengths against operational costs | A documented pros/cons list for decision-makers | Platform architects, security reviewers |
| Operations team | TTL, scavenger, and certificate-lifetime parameters | Configure and monitor both DNS planes and both certificate lifecycles | Self-healing, observable DevBench naming surface | On-call engineers, platform team |
| Observability pipeline | Metrics from both legs (DNS, F5, DDNS, IPAM, certificates) | Emit and alert on drift indicators | Early warning of lifecycle-automation or rotation failures | Platform on-call, security team |

Next stop: turning to the certificate side of this story — what the ACME challenge actually proves, and why it exists at all.
