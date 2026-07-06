---
title: "Globetrotters with Domain Naming Service 🏘️ Ep.5"
series: "Globetrotters with Domain Naming Service"
part: 5
organization: "the-software-s-journey"
tags: [dns, ddns, dhcp, ipam, infoblox, automation]
---

## Episode 5: The Village That Issues Its Own Papers

Some guests will not settle for a room at the hotel. They need a key to their own front door, on their own street, reachable directly by anyone with the right business — an SSH session from Jenkins, a straight SCP transfer, some other traffic that has no interest in going through a shared lobby. That guest needs Option B: a whole village with the authority to issue and revoke its own residence papers, without bothering the national registry every time someone moves in.

The shape: a dedicated neighborhood, `devbench.company.internal`, is delegated out of central DNS to a platform-owned local registry office. Central DNS keeps only the `NS` signpost pointing at that neighborhood — it never sees who actually lives there. That local office is fed by an integrated `DDNS` / `DHCP` / `IPAM` operation, the same class of machinery (`InfoBlox`) already running the SUT side. When a DevBench moves in, the control plane assigns it a deterministic address (`db-<uuid8>.devbench.company.internal`), draws an IP from the neighborhood's housing pool, hands over a `DHCP` lease tied to that name, and the `DHCP` office files a `DDNS` update (`RFC 2136`) that writes both the forward listing (`A`) and the reverse listing (`PTR`). When the DevBench moves out, the same office reverses every step — lease released, `DDNS` deletes filed, the plot returned to the pool. Every listing in this neighborhood carries a short shelf life, 30–60 seconds, so that even a missed move-out check ages itself out well within one DevBench's two-hour stay, and a scheduled inspector walks the neighborhood on a timer, evicting any listing whose lease no longer exists.

The trade-offs run the other way from Option A. Write volume is high, but it stays entirely inside the village — central DNS never feels it. Passport arrangements can go either way: a personal passport per resident, issued through the SUT-side PKI Client's `ACME Adapter`, which is cleanest for an audit trail, or a shared family visa for the whole neighborhood, which is cheaper to run. Every resident is reachable directly, on any protocol, with no shared lobby in the way — and because there is no lobby, TLS terminates exactly where the guest actually is, satisfying the strictest reading of end-to-end trust.

Option B is the right call when DevBenches must answer to non-HTTP knocks (SSH from Jenkins is the textbook case) and funneling that traffic through a front desk simply is not an option; when every test run needs a certificate traceable to one specific resident for audit purposes; and when some team is already willing to own the village — its registry office, its automation, its inspector rounds.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| DevBench control plane | Create event | Allocate deterministic hostname + reserve IP from IPAM pool | Bound hostname/IP pair | DHCP server, requesting DevBench |
| DHCP server | Lease bound to hostname | Issue DDNS add (forward `A` + reverse `PTR`) | Live, short-TTL DNS record pair | Jenkins, SSH/SCP clients, delegated zone |
| Scavenger job | Scheduled scan of the delegated zone | Compare records against live leases/IPAM entries | Removal of orphaned records | Delegated zone integrity, downstream clients |

Next stop: the tempting shortcut that looks like it avoids all this bookkeeping — and why it quietly makes things worse.
