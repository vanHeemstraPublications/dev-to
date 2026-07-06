---
title: "Globetrotters with Domain Naming Service 🗺️ Ep.1"
series: "Globetrotters with Domain Naming Service"
part: 1
organization: "the-software-s-journey"
tags: [dns, devops, tls, pki, kubernetes, networking]
---

## Episode 1: The World's Address Book Opens

Every seasoned globetrotter knows the same truth: a place is only reachable once it has a name someone else can look up. A city without an address book is a city nobody can visit twice. In the Virtual Fab, that address book is the Domain Naming Service, and it turns out three very different kinds of travelers rely on it every single day.

The first traveler is the tour bus full of external visitors — clients and the `F5 LTM` gateway out front — who need to find the `NGinX Ingress Controller` by name to get into the cluster at all. This is the sleepy corner of the address book: a handful of stable listings that almost never change, the equivalent of the national tourist office's own street address.

The second traveler is local: the SUT-side `InfoBlox` / `DNS` / `DHCP` stack that hands out names and addresses to the SUT-local Kubernetes cluster and to the SUT PKI Client. Its `Core` checks in over `DHCP` on arrival and gets a stable identity, the way a long-term resident gets a fixed entry in the town register so the local `ACME Adapter` can present itself consistently at every checkpoint (`Firewall(s)`) it needs to cross.

The third traveler is the interesting one, and it is the one this whole series is really about: the DevBench. Every DevBench needs a name for two reasons — the platform (Jenkins, the DevBench Creator) has to be able to find it to reach in over SSH/SCP, and as HTTPS coverage spreads, whatever fronts the DevBench has to show a passport (a TLS certificate) whose photo page (`Subject Alternative Name`) matches the name the visitor used to ask for it. DevBenches, unlike the tour bus stop or the long-term resident, check in and out of the address book constantly — and that churn is the scaling problem this series exists to solve.

One more housekeeping note before the journey starts: the `dns.svg` map that ships alongside this analysis is, for now, a signpost rather than a full city map — it anchors the discussion to the right neighborhood (the DDI plane) without yet drawing every street. The real itinerary lives in the prose that follows.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Corporate networking team | Stable `A` record for the ingress | Register north/south hostname | Resolvable cluster entrypoint | External clients, `F5 LTM` |
| SUT-side `InfoBlox` DDI stack | `DHCP` lease request from SUT PKI Client `Core` | Bootstrap stable network identity | Bootstrapped identity for `ACME Adapter` | SUT-local Kubernetes cluster, SUT PKI Client |
| DevBench control plane | DevBench create/destroy events | Register and retire DevBench names | Addressable, short-lived hostname | Jenkins, DevBench Creator, TLS clients |

Next stop: why a name, and not just an address, is the one thing a certificate actually cares about.
