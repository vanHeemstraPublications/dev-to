---
title: "Open Engineering with Nano Kit 🏘️ Ep.5"
series: "Open Engineering with Nano Kit"
part: 5
organization: "the-software-s-journey"
tags: [open-engineering, nanokit, domains, subdomains, hosting, cdn]
---

## Episode 5: Naming the Neighborhoods

A single page can live at a single address, but an ecosystem needs a street map. Open-engineering.io is the city; www, docs, platform, ontology, conventions, registry, resolver, elements, and api are its neighborhoods, each one reserved for exactly one kind of visitor.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Domain owner | The open-engineering.io domain | Reserve subdomains matching the naming conventions already used in GitHub | A planned map of www, docs, platform, ontology, conventions, registry, resolver, elements, and api | Visitors and services looking for a specific part of the ecosystem |
| Nano Kit hosting | A finished, generated page | Host the page instantly on a global CDN with a single click | A live, publicly reachable neighborhood | www.open-engineering.io landing visitors, docs readers |
| Ecosystem architect | Existing repository and service names | Decide which subdomains launch first and which wait | A staged rollout plan rather than nine simultaneous launches | Future maintainers of platform.open-engineering.io and beyond |

### One click per neighborhood

Nano Kit's hosting story is deliberately unremarkable: host the page instantly with a global CDN, no setup, one click. That plainness is the point here. Each neighborhood, www.open-engineering.io as the landing site, docs.open-engineering.io for documentation, platform.open-engineering.io for the platform pages, does not need its own infrastructure project. It needs one click, repeated as many times as there are neighborhoods to open.

### Not every street opens on day one

The full map already names nine subdomains, but api.open-engineering.io and resolver.open-engineering.io are clearly service-shaped rather than content-shaped, the kind of address that will eventually point at running infrastructure rather than a generated page. The gradual introduction called for here matters: www and docs can open immediately as static, Nano Kit-hosted neighborhoods, while ontology, conventions, and registry wait for their underlying content and services to be ready.

### Zero dependencies, easy to hand off later

Because Nano Kit also allows downloading production-ready HTML and CSS with zero dependencies, none of these early neighborhoods lock the ecosystem in. A subdomain that starts as a simple generated page can later be rebuilt behind api or resolver without anyone needing to migrate off a proprietary format first.

Episode 6 looks at that same zero-dependency export more closely, since it is what lets Open Engineering keep growing past whatever Nano Kit generates today.

