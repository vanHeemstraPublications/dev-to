---
title: "Who Are You CoreDNS? 🔬 Ep.5"
published: false
description: "Episode 5: The CSI lab keeps records of every case it has ever processed. The DNS cache is that records system — fast, bounded, time-limited. This episode opens the forensic database: cache internals, TTL mechanics, prefetching, Prometheus metrics that reveal what DNS is actually doing, and the NodeLocal DNSCache that distributes the evidence archive to every node in the cluster."
tags: [kubernetes, coredns, prometheus, observability]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/who-are-you-coredns-episode-05.png"
series: "Who Are You coreDNS?"
canonical_url: ""
organization: "the-software-s-journey"
part: 5
---

## Episode 5: The Forensic Database

*🎵 Who are you? Who who, who who? 🎵*

-----

## “The Lab Never Forgets — Unless the TTL Expires” 🗄️

*Warrick Brown stands in front of three monitors, each showing Prometheus graphs. One peaks sharply at 03:00am. He points.*

**WARRICK:** “Cache miss rate spiked at 3am. Hit rate dropped from 87% to 12% in two minutes. And look at the query rate — it went from 400 requests per second to 4,000.”

**NICK:** “Something flushed the cache.”

**WARRICK:** “Everything flushed the cache. A rolling deployment touched every pod in the cluster simultaneously. Every pod got a new IP for the payment service. Every cached DNS record expired at once. Four thousand pods all queried CoreDNS at the same second.”

**NICK:** “A thundering herd.”

**WARRICK:** “Exactly. The forensic database was empty when the herd arrived. Episode 5 — we learn how the database works, how to prevent cache stampedes, and how to read the evidence before a stampede becomes an outage.”

-----

## 🗂️ SIPOC — The Forensic Database

|**Suppliers**      |**Inputs**                                    |**Process**                                                                    |**Outputs**                                                     |**Customers**                                                                              |
|-------------------|----------------------------------------------|-------------------------------------------------------------------------------|----------------------------------------------------------------|-------------------------------------------------------------------------------------------|
|DNS query responses|NOERROR answers with TTL, NXDOMAIN responses  |`cache` plugin stores response keyed by (name, type, class)                    |Cached response returned immediately for matching queries       |All subsequent queries for the same record — no round-trip to kubernetes plugin or upstream|
|TTL values         |Source TTL from the record, configured max TTL|Cache uses `min(record_TTL, max_TTL)`                                          |A bounded cache lifetime — records expire and must be re-fetched|Cache hit ratio — determines how much load CoreDNS offloads from the API                   |
|Prometheus scraper |Metric endpoints at :9153/metrics             |Aggregates counters, histograms, gauges from all CoreDNS pods                  |Time-series data for dashboards and alerting                    |SREs and platform engineers investigating DNS behaviour                                    |
|NodeLocal DNSCache |DNS queries from pods, DaemonSet on each node |Intercepts DNS queries before they reach kube-dns, serves from node-local cache|Ultra-low latency DNS (sub-millisecond from node cache)         |All pods on the node — they hit local cache before crossing the network                    |

-----

## Cache Architecture: How Evidence Is Filed 📁

The CoreDNS cache stores DNS responses in memory, keyed by the tuple `(name, qtype, qclass)`.

```
Cache Entry:
  Key:   "payment-service.payments.svc.cluster.local. A IN"
  Value: "10.100.42.88"
  TTL:   expires at 2026-06-11 14:23:45 UTC (30 seconds from query time)
  Flags: NOERROR, authoritative

Cache Entry:
  Key:   "nonexistent.payments.svc.cluster.local. A IN"
  Value: NXDOMAIN
  TTL:   expires at 2026-06-11 14:23:50 UTC (5 seconds — denial cache)
```

**The two cache compartments:**

```
cache 30 {
    success 9984 300   # Positive compartment: up to 9984 entries, max 300s TTL
    denial  9984 5     # Negative compartment: up to 9984 entries, max 5s TTL
}
```

**SARA:** “Two separate stores. The denial cache is intentionally short-lived. A `NXDOMAIN` response today might be wrong tomorrow — services get created, pods come online. You never want to cache `does not exist` for long. But successful responses? Cache them aggressively.”

-----

## TTL Mechanics: The Evidence Expiry Stamp ⏱️

Every DNS record has a TTL — Time To Live — measured in seconds. The TTL tells caches how long to trust the answer.

**In CoreDNS’s `kubernetes` plugin:**

```
kubernetes cluster.local in-addr.arpa ip6.arpa {
    ttl 30    # All synthesised records get a 30-second TTL
}
```

**The TTL decision tree:**

```
1. Kubernetes synthesised record (from kubernetes plugin)
   → TTL = min(configured_ttl, 30)  — typically 30 seconds

2. Upstream answer (from forward plugin)
   → TTL = min(upstream_ttl, cache_max_ttl)  — min(upstream, 300s)

3. NXDOMAIN response
   → TTL = min(SOA_minimum_ttl, denial_max_ttl)  — typically 5 seconds
```

**Why 30 seconds for cluster services?**

```
Service changes in Kubernetes:
  - Deployment scales from 3 to 5 pods
  - Endpoint slice updates almost immediately
  - CoreDNS kubernetes plugin sees the change within ~1 second
  - But clients may have the OLD ClusterIP cached for up to 30 seconds
  - The ClusterIP itself never changes — only pod IPs behind it change
  - Therefore: 30s TTL is safe because the ClusterIP is stable
```

**GRISSOM:** “The ClusterIP is the invariant. Kubernetes guarantees it does not change for the lifetime of the service. CoreDNS caches the ClusterIP. The TTL of 30 seconds is generous — it could be much longer. The TTL that matters most is the headless service TTL: those records DO change when pods come and go.”

-----

## The Thundering Herd: Cache Stampede Mechanics 🐃

The thundering herd problem:

```
Normal operation (cache warm):
  - 100 pods each query "payment-service" every 30 seconds
  - Cache hit rate: ~98%
  - CoreDNS actual queries/second to kubernetes plugin: ~2/s (cache misses only)
  
After full cluster restart or mass-simultaneous TTL expiry:
  - 100 pods all start simultaneously
  - All 100 query "payment-service" within 1 second
  - Cache is cold (pods just started, cache is empty)
  - CoreDNS receives 100 queries in 1 second
  - kubernetes plugin processes all 100 (cache miss = check API)
  - API server gets 100 list calls in 1 second
  - Response latency spikes
  - Some pods time out
  - PagerDuty fires
```

**The prefetch solution:**

```
cache 30 {
    success 9984 300
    denial  9984 5
    prefetch 10 1m 10%
    # meaning: if a cached entry is fetched 10 times in 1 minute,
    # refresh it when 10% of its TTL remains (3 seconds for 30s TTL)
    # This keeps hot entries in cache continuously — no expiry gap
}
```

**CATHERINE:** “The prefetch option is pre-emptive evidence gathering. Before the cache entry expires, CoreDNS quietly refreshes it in the background. The client never sees a cache miss. The thundering herd never forms.”

-----

## Prometheus Metrics: Reading the Evidence Room 📊

The `prometheus` plugin at `:9153` exposes everything the lab has processed:

### The Essential Metrics Dashboard

```promql
# === QUERY VOLUME ===

# Total queries per second (rate)
rate(coredns_dns_requests_total[5m])

# Queries broken down by type (A, AAAA, SRV, PTR)
rate(coredns_dns_requests_total[5m]) by (type)

# Queries broken down by namespace (requires log plugin with labels)
rate(coredns_dns_requests_total[5m]) by (server)


# === RESPONSE CODES ===

# Error rate (SERVFAIL is always bad)
rate(coredns_dns_responses_total{rcode="SERVFAIL"}[5m])

# NXDOMAIN rate (can indicate misconfigured service names)
rate(coredns_dns_responses_total{rcode="NXDOMAIN"}[5m])

# Success rate
rate(coredns_dns_responses_total{rcode="NOERROR"}[5m])


# === CACHE PERFORMANCE ===

# Cache hit rate
rate(coredns_cache_hits_total[5m]) /
(
  rate(coredns_cache_hits_total[5m]) +
  rate(coredns_cache_misses_total[5m])
)

# Cache hit rate by type (success vs denial cache)
rate(coredns_cache_hits_total[5m]) by (type)


# === LATENCY ===

# P50 latency
histogram_quantile(0.50,
  rate(coredns_dns_request_duration_seconds_bucket[5m])
)

# P99 latency — the outliers that cause timeouts
histogram_quantile(0.99,
  rate(coredns_dns_request_duration_seconds_bucket[5m])
)


# === UPSTREAM FORWARDING ===

# Forward request rate
rate(coredns_forward_requests_total[5m])

# Forward health check failures
rate(coredns_forward_healthcheck_failures_total[5m])

# Forward response by upstream and rcode
rate(coredns_forward_responses_total[5m]) by (to, rcode)
```

### Alerting Rules: When to Page the On-Call 🚨

```yaml
# PrometheusRule for CoreDNS alerts
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: coredns-alerts
  namespace: kube-system
spec:
  groups:
  - name: coredns
    rules:

    - alert: CoreDNSDown
      expr: absent(coredns_build_info)
      for: 5m
      annotations:
        summary: "CoreDNS is not running"
        description: "No CoreDNS instances detected for 5 minutes"

    - alert: CoreDNSHighSERVFAILRate
      expr: >
        rate(coredns_dns_responses_total{rcode="SERVFAIL"}[5m]) > 0.1
      for: 2m
      annotations:
        summary: "CoreDNS SERVFAIL rate above threshold"
        description: >
          CoreDNS returning SERVFAIL at
          {{ $value | humanize }} req/s.
          Likely cause: upstream unreachable or kubernetes plugin error.

    - alert: CoreDNSLowCacheHitRate
      expr: >
        (
          rate(coredns_cache_hits_total[5m]) /
          (rate(coredns_cache_hits_total[5m]) +
           rate(coredns_cache_misses_total[5m]))
        ) < 0.5
      for: 5m
      annotations:
        summary: "CoreDNS cache hit rate below 50%"
        description: >
          Cache hit rate is {{ $value | humanizePercentage }}.
          Normal is >80%. May indicate cache thrashing or
          extremely high cardinality of DNS queries.

    - alert: CoreDNSHighLatency
      expr: >
        histogram_quantile(0.99,
          rate(coredns_dns_request_duration_seconds_bucket[5m])
        ) > 0.1
      for: 2m
      annotations:
        summary: "CoreDNS P99 latency above 100ms"
        description: >
          CoreDNS P99 latency is
          {{ $value | humanizeDuration }}. Normal P99
          should be under 10ms for cluster queries.
```

-----

## NodeLocal DNSCache: The Distributed Evidence Archive 🏛️

**WARRICK:** “CoreDNS runs in `kube-system`. Every pod on every node sends DNS queries across the network to `kube-dns`. At scale, this network traversal adds latency and creates a bottleneck.”

**The solution:** NodeLocal DNSCache — a DaemonSet that runs a local DNS cache on every node, intercepting DNS queries before they cross the network.

```
Without NodeLocal DNSCache:
  Pod → (network) → kube-dns Service → CoreDNS pod
  Latency: 1-5ms typical (network hop + processing)

With NodeLocal DNSCache:
  Pod → localhost:53 (link-local address 169.254.20.10) → Node-local cache
  Latency: 0.1ms typical (same host, no network hop)
  
  Node-local cache fills from CoreDNS on misses:
  Node-local cache → (network) → CoreDNS pod → kubernetes plugin
  This upstream call happens much less frequently (cache warm)
```

**Architecture diagram:**

```
Cluster Node
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Pod A             Pod B             Pod C              │
│  nameserver:       nameserver:       nameserver:        │
│  169.254.20.10     169.254.20.10     169.254.20.10      │
│       │                 │                 │             │
│       └─────────────────┼─────────────────┘             │
│                         │                               │
│          ┌──────────────▼───────────────┐               │
│          │   node-local-dns DaemonSet   │               │
│          │   (link-local IP 169.254.20.10)               │
│          │   Cache: warm for this node  │               │
│          └──────────────┬───────────────┘               │
│                         │ (cache miss only)             │
└─────────────────────────┼───────────────────────────────┘
                          │
                   (network hop)
                          │
                   kube-dns Service
                          │
                   CoreDNS pod
```

**Deploy NodeLocal DNSCache:**

```yaml
# NodeLocal DNSCache Corefile for the node-local daemon
apiVersion: v1
kind: ConfigMap
metadata:
  name: node-local-dns
  namespace: kube-system
data:
  Corefile: |
    cluster.local:53 {
        errors
        cache {
            success 9984 30
            denial  9984 5
        }
        reload
        loop
        bind 169.254.20.10
        forward . __PILLAR__CLUSTER__DNS__ {
            force_tcp
        }
        prometheus :9253
        health 169.254.20.10:8080
    }
    in-addr.arpa:53 {
        errors
        cache 30
        reload
        loop
        bind 169.254.20.10
        forward . __PILLAR__CLUSTER__DNS__ {
            force_tcp
        }
    }
    .:53 {
        errors
        cache 30
        reload
        loop
        bind 169.254.20.10
        forward . __PILLAR__UPSTREAM__SERVERS__
        prometheus :9253
    }
```

**SARA:** “Note the `force_tcp` option. NodeLocal DNSCache uses TCP for its upstream queries to CoreDNS. This is critical — UDP connections are connectionless and cannot be tracked through conntrack properly when using link-local IPs. Using TCP avoids conntrack race conditions that cause intermittent DNS failures in high-traffic clusters.”

**WARRICK:** “Conntrack race conditions are one of the most pernicious DNS bugs in Kubernetes. Symptoms: random 5-second DNS timeouts, no pattern, affects a small percentage of queries. Root cause: two UDP DNS queries from the same source port land in conntrack simultaneously, one gets dropped. NodeLocal DNSCache on TCP eliminates this entire class of failure.”

-----

## Cache Investigation Toolkit 🔬

```bash
# === Method 1: Watch cache metrics live ===
kubectl port-forward svc/kube-dns -n kube-system 9153:9153 &
watch -n 2 'curl -s http://localhost:9153/metrics | grep coredns_cache'

# === Method 2: Force a cache miss and time it ===
# First query (cold cache or after TTL expiry)
time kubectl exec -n payments dns-investigator -- \
  dig payment-service.payments.svc.cluster.local +stats

# ;; Query time: 3 msec  ← cache miss, went to kubernetes plugin

# Second query (warm cache, within TTL)
time kubectl exec -n payments dns-investigator -- \
  dig payment-service.payments.svc.cluster.local +stats

# ;; Query time: 0 msec  ← cache hit, sub-millisecond

# === Method 3: Check if NodeLocal DNSCache is active ===
kubectl get pods -n kube-system -l k8s-app=node-local-dns

# If running, check its metrics
kubectl exec -n kube-system $(kubectl get pod \
  -n kube-system -l k8s-app=node-local-dns -o name | head -1) \
  -- wget -qO- http://169.254.20.10:9253/metrics | grep cache
```

-----

## What’s Next: Cold Cases 🧊

*A technician drops a stack of case files on Warrick’s desk. All unsolved.*

**WARRICK:** “Episode 6. The hard ones. DNS timeouts with no NXDOMAIN. SERVFAILs with no obvious cause. Pods that can’t reach services that definitely exist. The complete troubleshooting toolkit — `kubectl logs`, `dig`, `nslookup`, tcpdump inside pods, and the twelve most common DNS failure patterns in Kubernetes clusters.”

*He picks up the top file.*

*The theme song plays.*

-----

**🔗 Resources**

- **NodeLocal DNSCache**: [kubernetes.io/docs/tasks/administer-cluster/nodelocaldns](https://kubernetes.io/docs/tasks/administer-cluster/nodelocaldns/)
- **CoreDNS cache plugin**: [coredns.io/plugins/cache](https://coredns.io/plugins/cache/)
- **CoreDNS metrics**: [coredns.io/plugins/metrics](https://coredns.io/plugins/metrics/)

-----

*🔬 Who Are You CoreDNS? — a CSI-style investigation into Kubernetes DNS. The evidence is in the Corefile. The answers are in the logs.*
