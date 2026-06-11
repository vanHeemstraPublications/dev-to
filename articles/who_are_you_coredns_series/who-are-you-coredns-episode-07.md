---
title: "Who Are You CoreDNS? 🔬 Ep.7"
published: false
description: "Episode 7: Not all DNS investigations are about finding what went wrong. Some are about deliberately shaping what the answers say. Rewrite a query name mid-flight. Serve different answers to internal vs external callers. Route specific domains to dedicated nameservers. Generate responses from templates without a backing service. The undercover operations of CoreDNS — advanced capabilities for complex environments."
tags: [kubernetes, coredns, advanced, configuration]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/who-are-you-coredns-episode-07.png"
series: "Who Are You coreDNS?"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

## Episode 7: Undercover Operations

*🎵 Who are you? Who who, who who? 🎵*

-----

## “Sometimes the Best Investigation Is an Operation” 🕵️

*The briefing room. Grissom at the whiteboard. The team assembled.*

**GRISSOM:** “Everything we have covered so far has been reactive. DNS fails — we investigate. But some situations require proactive design. A legacy application that hardcodes a hostname we cannot change. A migration where two names must point to the same thing, temporarily. A corporate split-horizon where internal and external callers need different answers for the same question.”

*He writes on the whiteboard: REWRITE. TEMPLATE. STUB. SPLIT-HORIZON.*

**GRISSOM:** “These are not investigations. These are operations. We go in, we change what DNS says, and the application never knows anything changed. The question is no longer ‘who are you?’ — the question is ‘who do you need to appear to be?’”

-----

## 🗂️ SIPOC — The Undercover Operation

|**Suppliers**                             |**Inputs**                               |**Process**                                                                     |**Outputs**                                   |**Customers**                                                       |
|------------------------------------------|-----------------------------------------|--------------------------------------------------------------------------------|----------------------------------------------|--------------------------------------------------------------------|
|`rewrite` plugin                          |DNS query name, type                     |Intercepts the query, modifies name or type before passing to kubernetes/forward|Rewritten query answered by a different record|Application — which asked for one name and got another’s answer     |
|`template` plugin                         |Query pattern (regex or name template)   |Dynamically generates a DNS response without any backing record                 |A synthesised A, CNAME, or SOA response       |Applications that need dynamic responses not backed by real services|
|Stub zone (`forward` with specific domain)|Queries matching a specific domain prefix|Routes those queries to a dedicated nameserver instead of the default upstream  |Answers from the specialist nameserver        |Applications needing split authoritative sources                    |
|`acl` plugin                              |Source IP of the DNS requester           |Allows or denies query based on who is asking                                   |REFUSED for unauthorised callers              |Multi-tenant clusters — namespaces should not query each other’s DNS|

-----

## Operation 1: The `rewrite` Plugin — The Identity Forger 🎭

The `rewrite` plugin intercepts DNS queries and changes them before they are processed by the rest of the plugin chain.

**Use case: Legacy application hardcodes a deprecated hostname**

```
# Application code (cannot be changed): connects to "old-payment-api.internal"
# New service name: "payment-service.payments.svc.cluster.local"
# Mission: make "old-payment-api.internal" point to the new service
# Method: rewrite the query name mid-flight
```

```
.:53 {
    errors
    rewrite name exact old-payment-api.internal \
      payment-service.payments.svc.cluster.local
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
        fallthrough in-addr.arpa ip6.arpa
    }
    forward . /etc/resolv.conf
    cache 30
}
```

**What happens:**

```
Application queries: old-payment-api.internal
    ↓ rewrite plugin intercepts
Rewritten to: payment-service.payments.svc.cluster.local
    ↓ kubernetes plugin answers
Response: 10.100.42.88 (the ClusterIP)
    ↓ response rewritten back
Application receives: old-payment-api.internal → 10.100.42.88
```

**More rewrite examples:**

```
# Rewrite with regex (all subdomains of legacy.corp → service.svc.cluster.local)
rewrite name regex (.*)\.legacy\.corp {1}.production.svc.cluster.local

# Rewrite a specific record type
rewrite type ANY A  # Rewrite ANY queries to A queries

# Stop after rewrite (do not continue down the chain)
rewrite stop name exact old-db.corp payment-db.payments.svc.cluster.local

# Rewrite with answer rewriting (response also modified)
rewrite name exact old-api.internal new-api.production.svc.cluster.local answer auto
```

-----

## Operation 2: The `template` Plugin — The Ghost Writer ✍️

The `template` plugin generates DNS responses dynamically from templates — no backing service or record required.

**Use case: A wildcard domain that should return a fixed IP**

```
# Mission: Make ANY query for *.localtest.me resolve to 127.0.0.1
# (useful for local development: apps.localtest.me → 127.0.0.1)

.:53 {
    template IN A localtest.me {
        match "^(.*\.)?localtest\.me\.$"
        answer "{{ .Name }} 60 IN A 127.0.0.1"
        fallthrough
    }
    kubernetes cluster.local ...
    forward . /etc/resolv.conf
    cache 30
}
```

**Use case: Returning NX for specific patterns (suppress queries)**

```
# Mission: Stop all PTR queries for RFC 1918 space
# (reduce noise from failed reverse DNS lookups)
template IN PTR 10.in-addr.arpa {
    rcode NXDOMAIN
}
template IN PTR 172.in-addr.arpa {
    rcode NXDOMAIN
}
template IN PTR 192.168.in-addr.arpa {
    rcode NXDOMAIN
}
```

**Use case: Dynamic service discovery for migration**

```
# Mission: Any query for *.v1.api.internal gets the v1 load balancer
# Any query for *.v2.api.internal gets the v2 load balancer
template IN A v1.api.internal {
    match "^(.*)\.v1\.api\.internal\.$"
    answer "{{ .Name }} 60 IN A 10.0.1.100"
}
template IN A v2.api.internal {
    match "^(.*)\.v2\.api\.internal\.$"
    answer "{{ .Name }} 60 IN A 10.0.2.100"
}
```

-----

## Operation 3: Stub Zones — The Specialist Division 🏢

A stub zone routes queries for a specific domain to a dedicated nameserver, while all other queries go to the default upstream.

**The Corefile has multiple server blocks — one per zone:**

```
# Default server block — handles everything
.:53 {
    errors
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
    }
    forward . /etc/resolv.conf
    cache 30
}

# Stub zone for corporate internal domain
acme.internal:53 {
    errors
    forward . 10.10.0.5 10.10.0.6
    cache 60
}

# Stub zone for another team's domain
partner.local:53 {
    errors
    forward . 192.168.100.1
    cache 60
}

# Stub zone for a specific DNS over TLS upstream
secure.example.com:53 {
    forward . tls://1.1.1.1 tls://8.8.8.8 {
        tls_servername cloudflare-dns.com
        health_check 5s
    }
    cache 300
}
```

**What the routing looks like:**

```
Query: payment-service.payments.svc.cluster.local
    → Matches .:53 → kubernetes plugin → ClusterIP returned ✓

Query: legacy-db.acme.internal
    → Matches acme.internal:53 → forward to 10.10.0.5 → corporate DNS ✓

Query: api.partner.local
    → Matches partner.local:53 → forward to 192.168.100.1 ✓

Query: google.com
    → Matches .:53 (catch-all) → forward to /etc/resolv.conf ✓
```

-----

## Operation 4: Split-Horizon DNS — Two Answers for the Same Question 🪞

Split-horizon (also called split-brain) DNS serves different answers to different callers based on where the query originates.

**Use case:** An API service should return an internal ClusterIP to pods inside the cluster, but a public IP to external callers.

CoreDNS does not natively support per-source-IP different answers in the `kubernetes` plugin (that is the load balancer’s job). However, you can implement split-horizon by combining server blocks, `acl` plugin, and view-based forwarding:

```
# Split-horizon: internal callers get cluster DNS, external get public DNS

# Internal cluster domain
cluster.local:53 {
    errors
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
    }
    cache 30
}

# External domain with internal override
.:53 {
    errors
    # For queries coming from cluster pods (RFC 1918 sources)
    # Override specific external hostnames with internal IPs
    hosts /etc/coredns/internal-overrides {
        10.100.42.88    api.mycompany.com    # Internal IP for internal callers
        fallthrough
    }
    forward . /etc/resolv.conf
    cache 30
}
```

```
# /etc/coredns/internal-overrides (mounted via ConfigMap)
# These overrides make internal pods reach the internal service
# while external callers (via /etc/resolv.conf upstream) get the public IP

10.100.42.88   api.mycompany.com
10.100.43.12   payments.mycompany.com
```

-----

## Operation 5: The `acl` Plugin — Jurisdiction Control 🚔

The `acl` plugin controls who can query which zones. Essential for multi-tenant clusters.

```
payments.svc.cluster.local:53 {
    acl {
        allow type A net 10.244.0.0/16   # Allow: cluster pod CIDR
        block                             # Block everything else
    }
    kubernetes cluster.local {
        namespaces payments
    }
    cache 30
}
```

**Practical multi-tenant scenario:**

```
# Namespace payments should only be queryable by pods in the payments namespace
# Namespace orders should only be queryable by pods in the orders namespace

.:53 {
    acl {
        # Allow all queries — default permissive for the main zone
        allow net 10.0.0.0/8
    }
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
    }
    forward . /etc/resolv.conf
    cache 30
}

# Block cross-namespace DNS queries for sensitive namespaces
payments.svc.cluster.local:53 {
    acl {
        # Only pods in payments namespace (10.244.5.0/24 in this example)
        allow type A net 10.244.5.0/24
        block
    }
    forward . 10.96.0.10   # Back to main CoreDNS for resolution
    cache 30
}
```

-----

## Operation 6: DNS over TLS and HTTPS — Encrypted Evidence Transmission 🔒

```
# Forward using DNS over TLS (DoT)
.:53 {
    forward . tls://1.1.1.1 tls://1.0.0.1 {
        tls_servername cloudflare-dns.com
        health_check 5s
    }
    cache 30
}

# Forward using DNS over HTTPS (DoH) — via a DoH proxy
.:53 {
    forward . https://dns.google/dns-query {
        bootstrap_address 8.8.8.8
    }
    cache 30
}
```

-----

## Operation 7: The `whoami` Plugin — Confirming Identity 🪪

The `whoami` plugin is a diagnostic tool that returns the source IP and port of the requesting client in the DNS response.

```
whoami.example.com:53 {
    whoami
}
```

```bash
# Query the whoami plugin to see what IP CoreDNS sees for the requester
dig @10.96.0.10 whoami.example.com

# ;; ANSWER SECTION:
# whoami.example.com.  0 IN   A  10.244.1.15    ← Pod's IP
# whoami.example.com.  0 IN TXT "10.244.1.15:54832"
```

**SARA:** “The `whoami` plugin is forensic confirmation. It tells you exactly what source IP CoreDNS is seeing for the query. Useful when NAT or proxying is in the path and you are not sure what IP the query arrives from.”

-----

## Putting It Together: A Production Advanced Corefile 📋

```
# Advanced production Corefile
# Multiple server blocks, stub zones, rewrites, templates

.:53 {
    errors
    log . {
        class denial
    }
    health {
        lameduck 5s
    }
    ready
    prometheus :9153

    # Rewrite: legacy hostname migration
    rewrite stop name exact legacy-api.mycompany.com \
      api-service.production.svc.cluster.local

    # Template: suppress private PTR noise
    template IN PTR 10.in-addr.arpa    { rcode NXDOMAIN }
    template IN PTR 172.in-addr.arpa   { rcode NXDOMAIN }

    # Hosts: split-horizon overrides for select external names
    hosts /etc/coredns/overrides {
        10.100.42.88    api.mycompany.com
        fallthrough
    }

    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
        fallthrough in-addr.arpa ip6.arpa
        ttl 30
    }

    forward . /etc/resolv.conf {
        max_concurrent 1000
        prefer_udp
        policy random
        health_check 5s
    }

    cache 30 {
        success 9984 300
        denial  9984 5
        prefetch 10 1m 10%
    }

    loadbalance round_robin
    loop
    reload
}

# Corporate internal DNS stub zone
corp.internal:53 {
    errors
    forward . 10.10.0.5 10.10.0.6 {
        policy round_robin
    }
    cache 300
}

# High-security encrypted upstream for external queries from secure namespace
secure.cluster.local:53 {
    errors
    forward . tls://1.1.1.1 {
        tls_servername cloudflare-dns.com
    }
    cache 300
}
```

-----

## What’s Next: Case Closed 🏁

*Grissom steps back from the whiteboard.*

**GRISSOM:** “We have covered the operations. Now one final episode — the production-hardening case. RBAC, resource limits, anti-affinity across nodes, NodeLocal DNSCache architecture, and what happens when a Kubernetes cluster grows to thousands of nodes. Episode 8: Case Closed.”

*The theme song plays. The whiteboards are full. The operations are underway.*

-----

**🔗 Resources**

- **rewrite plugin**: [coredns.io/plugins/rewrite](https://coredns.io/plugins/rewrite/)
- **template plugin**: [coredns.io/plugins/template](https://coredns.io/plugins/template/)
- **acl plugin**: [coredns.io/plugins/acl](https://coredns.io/plugins/acl/)
- **Multiple server blocks**: [coredns.io/manual/configuration](https://coredns.io/manual/configuration/)

-----

*🔬 Who Are You CoreDNS? — a CSI-style investigation into Kubernetes DNS. The evidence is in the Corefile. The answers are in the logs.*
