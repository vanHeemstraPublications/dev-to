---
title: "🔐 The Direct-Access Leg: SSH, SCP, and Any TCP via Delegated DNS"
series: "HTTP(S) and SSH, SCP, or any TCP with ACME Challenge and Domain Naming Service"
part: 3
organization: "the-software-s-journey"
tags: [dns, ddns, dhcp, ipam, ssh, delegated-zone]
---

## 🔐 The Direct-Access Leg: SSH, SCP, and Any TCP via Delegated DNS

Follow an `ssh user@db-a1b2c3.devbench.company.internal` (or `scp …`) from the same Virtual Fab Client, and the path diverges from the very first lookup. Name resolution starts at Central DNS, but Central DNS holds a more-specific match than the wildcard: the delegation `devbench. ... NS platform-auth-dns. ...`. That delegation wins over the wildcard for names under `devbench.company.internal`, and Central DNS returns a referral instead of an answer. The client's resolver then follows that referral to the platform-authoritative DNS, which holds the actual per-bench `A` record — `db-a1b2c3.devbench.company.internal → 10.1.0.11` — published with a short TTL of 30–60 seconds by the DHCP/IPAM stack via an `RFC 2136` DDNS update at lease time.

With a real IP in hand, the client opens its SSH connection (or any other TCP port — the DevBench accepts traffic on any port on this leg) straight across the firewall(s) to the DevBench itself. No shared front door sits in the middle. For protocols that carry a certificate — management HTTPS on the DevBench, mTLS-based SSH cert-auth — the DevBench presents a per-bench certificate whose SAN is exactly `db-a1b2c3.devbench.company.internal`, the same name the client just resolved and the same name published in the DDNS record. For plain SSH host-key authentication, the equivalent identity is the SSH host key, but the name-to-IP binding driving the whole exchange still comes from the platform-authoritative DNS. When the DevBench is destroyed, the DHCP release triggers a DDNS delete and the IPAM entry returns to the pool; any stale resolver cache ages out within one TTL, comfortably inside the roughly two-hour DevBench lifetime.

The key property on this leg is the mirror image of the HTTP(S) leg: DNS is the source of truth for the name-to-IP binding, and Central DNS never sees the per-bench churn — it only ever holds the `NS` delegation. In plain language, this is the direct service route: each DevBench has its own service entrance with its own nameplate, and whoever needs to work inside checks the nameplate against their own name before going in. Every test run reached this way is traceable to a unique, per-bench certificate identity — the audit property a shared wildcard cannot provide.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Central DNS | Query for `db-a1b2c3.devbench.company.internal` | Match the `NS` delegation (more specific than the wildcard) | Referral to the platform-authoritative DNS | Client resolver |
| DHCP/IPAM stack (platform-authoritative DDI) | DevBench create event | Allocate IP, bind DHCP lease, issue DDNS add (RFC 2136) | Short-TTL per-bench `A`/`PTR` record | Platform-authoritative DNS, requesting client |
| SUT-side PKI Client ACME Adapter | DevBench lifecycle event | Issue a per-bench certificate matching the DDNS name | Certificate with SAN = `db-<uuid8>.devbench.company.internal` | DevBench, TLS-carried protocols on the direct leg |

Next stop: how Central DNS and the platform-authoritative DNS divide the work between them without either one stepping on the other's traffic.
