---
title: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service 🌐 Ep.2"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 2
organization: "the-software-s-journey"
tags: [dns, tls, sni, f5, wildcard-certificate, load-balancing]
---

## Episode 2: The HTTPS Leg: Wildcard-to-VIP in Detail

Follow a single `curl https://db-a1b2c3.devbench.company.internal/…` from a Virtual Fab Client and six things happen in order. First, name resolution: the client queries `db-a1b2c3.devbench.company.internal`, the query lands on Central DNS, and the wildcard `*.devbench A 10.20.30.40` matches — every name under `*.devbench.company.internal`, regardless of which DevBench it names, returns the same VIP. Second, TCP and TLS setup to the VIP: the client opens a connection to `10.20.30.40:443` and sends `SNI=db-a1b2c3.devbench.company.internal` in the `ClientHello`, along with `Host: db-a1b2c3.devbench.company.internal` on the HTTP request itself. Third, TLS termination at the F5: it presents the wildcard certificate (`CN/SAN: *.devbench.company.internal`), and because the SAN wildcard covers the whole subdomain, hostname validation under `RFC 6125`/`RFC 9525` succeeds for any `db-<id>.devbench.company.internal` name. Fourth, SNI/Host-based routing: the F5 inspects `SNI` (and `Host` for HTTP/2 or muxed connections) and looks up the specific DevBench in a routing table that the DevBench control plane keeps current — DNS plays no role in this per-DevBench step. Fifth, the backend hop: the F5 forwards across the firewall(s) to the HTTP(S) reverse proxy inside the SUT and on to the target DevBench, over a leg that is either plaintext-inside-a-trusted-network or a re-encrypt with an internal certificate — no per-bench external certificate is required here. Sixth, the response returns along the same established TLS session.

The key property to hold onto: on this leg, DNS answers exactly one question — "where is the ingress?" — and the identity of the specific DevBench travels in `SNI`/`Host`, not in the resolved IP. The F5 owns the VIP, terminates TLS with the wildcard certificate, and is the single point where naming, TLS, and routing meet for every DevBench under HTTP(S). The wildcard certificate lives only on the F5 VIP; it is never distributed to individual DevBenches. It is issued and rotated through the same `Keyfactor ACME Server → Keyfactor Command → Configured CA` chain already used elsewhere in the environment, with an `ACME Challenge` step (covered later in this series) proving control of `*.devbench.company.internal` before issuance.

In plain terms: web traffic uses a stable, shared front door — a single entry point every DevBench name resolves to, protected by one shared certificate. Every guest looks the same on the way in; the receptionist (the F5) does the routing after the fact, not DNS.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Central DNS | Query for any `db-<id>.devbench.company.internal` | Match the wildcard `A` record | Single stable VIP address (10.20.30.40) | Virtual Fab Client |
| cert-manager + Keyfactor ACME chain | Certificate request for `*.devbench.company.internal` | Issue and renew one wildcard certificate | Valid wildcard certificate installed on the F5 | F5 LTM VIP |
| DevBench control plane | Lifecycle create/destroy events | Update F5 SNI/Host routing table | Current name-to-backend mapping | F5 LTM, HTTP(S) Reverse Proxy, DevBench |

Next stop: the leg that does not go through the front door at all — SSH, SCP, and any other traffic that needs to reach a DevBench directly.
