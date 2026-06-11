---
title: "Who Are You CoreDNS? 🔬 Ep.4"
published: false
description: "Episode 4: Every plugin in the Corefile is a forensic instrument. The errors plugin is the crime scene tape. The log plugin is the wiretap. The kubernetes plugin is the entire detective division. The cache plugin is the forensic database. The forward plugin is the informant hotline. The lab is open — every instrument examined, every configuration option explained."
tags: [kubernetes, coredns, configuration, devops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/who-are-you-coredns-episode-04.png"
series: "Who Are You coreDNS?"
canonical_url: ""
organization: "the-software-s-journey"
part: 4
---

## Episode 4: The CSI Lab

*🎵 Who are you? Who who, who who? 🎵*

-----

## “The Lab Never Lies” 🏛️

*Grissom walks the length of the Corefile, reading each plugin line like an evidence manifest.*

**GRISSOM:** “Most engineers treat the Corefile as a configuration file. I treat it as a case file. Every plugin is a specialist brought in to examine the evidence. The order they appear is the chain of custody. Disrupt the chain, contaminate the evidence.”

*He stops at the beginning.*

**GRISSOM:** “Let us meet the team.”

-----

## 🗂️ SIPOC — The Plugin Chain

|**Suppliers** |**Inputs**                                        |**Process**                                                                         |**Outputs**                                                              |**Customers**                                                              |
|--------------|--------------------------------------------------|------------------------------------------------------------------------------------|-------------------------------------------------------------------------|---------------------------------------------------------------------------|
|The Corefile  |Zone declarations, plugin names, plugin parameters|CoreDNS reads the Corefile at startup, builds the plugin chain for each server block|An ordered sequence of plugins that processes every DNS query            |Each incoming DNS query — which travels the chain until answered or dropped|
|Plugin authors|DNS queries, responses, configuration parameters  |Each plugin handles, passes, modifies, or logs the query based on its function      |Modified queries, authoritative responses, forwarded queries, log entries|The next plugin in the chain, or the original requester                    |
|Hot reload    |Updated Corefile in the ConfigMap                 |`reload` plugin detects changes and rebuilds the chain without restarting           |A new plugin chain, in place, within ~30 seconds                         |Running pods — no DNS interruption during configuration updates            |

-----

## The Full Annotated Corefile 📋

Here is a production-ready Corefile with every common plugin and comprehensive configuration:

```
# CoreDNS Corefile — Production Configuration
# ConfigMap: coredns, Namespace: kube-system

.:53 {
    # ── LOGGING AND OBSERVABILITY ────────────────────────────────
    errors                          # Log errors to stdout
    log . {                         # Log ALL queries (use with care in prod)
        class denial                # Only log denied/refused queries
    }

    # ── HEALTH AND READINESS ─────────────────────────────────────
    health {
        lameduck 5s                 # Grace period before marking unhealthy
    }
    ready                           # Readiness probe on :8181/ready

    # ── METRICS ──────────────────────────────────────────────────
    prometheus :9153                # Expose Prometheus metrics

    # ── KUBERNETES INTEGRATION ───────────────────────────────────
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure               # Allow pod DNS records
        fallthrough in-addr.arpa ip6.arpa  # Pass PTR lookups to forward
        ttl 30                      # Override default TTL
        namespaces production staging   # Only serve these namespaces (optional)
        endpoint_pod_names          # Use pod names for headless endpoints
    }

    # ── EXTERNAL DNS FORWARDING ──────────────────────────────────
    forward . /etc/resolv.conf {
        max_concurrent 1000         # Maximum concurrent queries upstream
        prefer_udp                  # Prefer UDP over TCP upstream
        policy random               # Random upstream selection
        health_check 5s             # Check upstream health every 5s
    }

    # ── PERFORMANCE ──────────────────────────────────────────────
    cache 30 {
        success 9984 300            # Cache successful responses (max 9984, max TTL 300s)
        denial  9984 5              # Cache NXDOMAIN etc. briefly (5s) to reduce load
        prefetch 10 1m 10%          # Prefetch popular entries 10s before expiry
    }
    loadbalance round_robin         # Shuffle A/AAAA answers

    # ── SAFETY ───────────────────────────────────────────────────
    loop                            # Detect forwarding loops
    reload                          # Hot-reload Corefile changes
}

# Stub zone for corporate internal DNS
acme.internal:53 {
    errors
    forward . 10.10.0.5 10.10.0.6  # Corporate nameservers for this domain
    cache 60
}
```

-----

## Plugin 1: `errors` — The Crime Scene Tape 🚨

**GRISSOM:** “The first instrument. The simplest. The most important.”

The `errors` plugin logs DNS errors to stdout. Without it, errors are silent.

```
errors
```

**What it logs:**

```
[ERROR] plugin/errors: 2 SERVFAIL payment-service.payments.svc.cluster.local. A
        UDP 47 10.244.1.15:54832 → 10.96.0.10:53 0.234s
```

**What triggers it:** SERVFAIL, FORMERR, REFUSED responses — anything that is not a normal NOERROR or NXDOMAIN.

```bash
# Filter for errors in the CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns \
  | grep '\[ERROR\]'
```

-----

## Plugin 2: `log` — The Wiretap 📻

The `log` plugin records every query. It is the wiretap on the DNS wire.

```
log . {
    class all      # Log everything (denial, error, success, all)
    # class denial # Only log NXDOMAIN and REFUSED (less noisy)
    # class error  # Only log errors
}
```

**Warning:** Logging every query in a high-traffic cluster generates enormous log volume. Use `class denial` in production.

**Sample log output:**

```
[INFO] 10.244.1.15:54832 - "A IN payment-service.payments.svc.cluster.local. udp 54 false 512" NOERROR qr,aa,rd 101 0.000123s
```

**Log format decoded:**

|Field                        |Value                |Meaning                                                |
|-----------------------------|---------------------|-------------------------------------------------------|
|`10.244.1.15:54832`          |Source               |Pod IP and ephemeral port                              |
|`"A IN ... udp 54 false 512"`|Query                |Record type, name, protocol, size, DO-bit, buffer-size |
|`NOERROR`                    |Response code        |Success                                                |
|`qr,aa,rd`                   |Flags                |Query Response, Authoritative Answer, Recursion Desired|
|`101`                        |Response size (bytes)|How large the answer was                               |
|`0.000123s`                  |Latency              |Time to process                                        |

-----

## Plugin 3: `health` — Is the Lab Operational? 🏥

```
health {
    lameduck 5s
}
```

Exposes an HTTP endpoint at `:8080/health`. Returns `OK` when CoreDNS is ready.

```bash
# Check health from inside the CoreDNS pod
kubectl exec -n kube-system $(kubectl get pods -n kube-system \
  -l k8s-app=kube-dns -o name | head -1) -- \
  wget -qO- http://localhost:8080/health

# OK
```

**The `lameduck` option:** When a CoreDNS pod is about to be terminated (during rolling update), it enters lameduck mode for 5 seconds. During this time, the health endpoint returns a 500 error, signaling to the load balancer to stop sending new queries — but the pod keeps processing in-flight queries. This ensures zero dropped queries during updates.

-----

## Plugin 4: `ready` — Is the Lab Ready to Work? 🚦

```
ready
```

Exposes `:8181/ready`. Returns `OK` only when all plugins that implement the `readiness` interface have signaled ready. The `kubernetes` plugin signals ready once it has synced the initial API state.

**Why this matters:** During pod startup, CoreDNS needs a moment to list all Services and Endpoints from the API server. Until that sync completes, it should not serve queries. The `ready` plugin enforces this.

```bash
# The kubernetes deployment uses this for readinessProbe
readinessProbe:
  httpGet:
    path: /ready
    port: 8181
  initialDelaySeconds: 5
  periodSeconds: 5
```

-----

## Plugin 5: `kubernetes` — The Detective Division 🕵️

**SARA:** “This is the heart of the lab. Everything else supports it.”

The `kubernetes` plugin is what makes CoreDNS a Kubernetes-native DNS server. It watches the Kubernetes API server for changes to Services, Endpoints, Pods, and Namespaces, and synthesises DNS records in real time.

```
kubernetes cluster.local in-addr.arpa ip6.arpa {
    pods insecure
    fallthrough in-addr.arpa ip6.arpa
    ttl 30
}
```

**Configuration options:**

|Option                             |Description                                        |Default|
|-----------------------------------|---------------------------------------------------|-------|
|`pods insecure`                    |Serve pod DNS records without verification         |—      |
|`pods verified`                    |Only serve pod record to the pod itself            |—      |
|`pods disabled`                    |No pod DNS records                                 |—      |
|`fallthrough in-addr.arpa ip6.arpa`|Pass PTR queries for these zones to the next plugin|—      |
|`ttl`                              |Override TTL for all synthesised records           |5s     |
|`namespaces ns1 ns2`               |Only serve DNS for listed namespaces               |all    |
|`endpoint_pod_names`               |Use pod names for headless service endpoints       |—      |
|`noendpoints`                      |Do not synthesise endpoint records                 |—      |
|`transfer to *`                    |Allow zone transfer                                |—      |

**What the kubernetes plugin watches:**

```bash
# These API calls back the kubernetes plugin's DNS records:
kubectl get services       --all-namespaces --watch
kubectl get endpointslices --all-namespaces --watch
kubectl get pods           --all-namespaces --watch  # when pods != disabled
kubectl get namespaces     --watch
```

**GRISSOM:** “Every time a Service is created or deleted, the kubernetes plugin updates its in-memory record table within milliseconds. There is no TTL delay on the server side — new services are immediately resolvable. The TTL of 30 seconds applies to the *client’s* cache, not CoreDNS’s knowledge.”

-----

## Plugin 6: `prometheus` — The Forensic Statistics 📊

```
prometheus :9153
```

Exposes Prometheus metrics at `:9153/metrics`. The most useful metrics for investigation:

```bash
# Scrape CoreDNS metrics
kubectl port-forward svc/kube-dns -n kube-system 9153:9153
curl http://localhost:9153/metrics | grep coredns

# Key metrics:
# coredns_dns_requests_total{...}         — Total queries by type, rcode, protocol
# coredns_dns_responses_total{...}        — Total responses by rcode
# coredns_dns_request_duration_seconds{} — Latency histogram
# coredns_cache_hits_total{...}           — Cache hit count
# coredns_cache_misses_total{...}         — Cache miss count
# coredns_forward_requests_total{...}     — Upstream queries
# coredns_forward_healthcheck_failures_total{...} — Upstream health failures
```

```promql
# PromQL: DNS error rate (SERVFAIL)
rate(coredns_dns_responses_total{rcode="SERVFAIL"}[5m])

# PromQL: Cache hit ratio
rate(coredns_cache_hits_total[5m]) /
  (rate(coredns_cache_hits_total[5m]) + rate(coredns_cache_misses_total[5m]))

# PromQL: P99 DNS query latency
histogram_quantile(0.99,
  rate(coredns_dns_request_duration_seconds_bucket[5m]))
```

-----

## Plugin 7: `forward` — The Informant Network 🕵️‍♂️

The `forward` plugin escalates queries that CoreDNS cannot answer internally to upstream nameservers.

```
forward . /etc/resolv.conf {
    max_concurrent 1000
    prefer_udp
    policy random               # random | round_robin | sequential
    health_check 5s
    expire 10s                  # Remove upstream after this many failed checks
    max_fails 3                 # Failures before marking upstream as down
}
```

**What `/etc/resolv.conf` means:** CoreDNS reads the nameservers from the host node’s `/etc/resolv.conf`. This is how cluster DNS connects to your corporate DNS or public resolvers.

**Explicit upstream configuration (recommended for production):**

```
forward . 8.8.8.8 8.8.4.4 {
    max_concurrent 1000
    prefer_udp
    policy round_robin
}
```

**NICK:** “The forward plugin is the informant. When CoreDNS has no answer, it calls its upstream contacts. The `health_check` ensures it stops calling a contact that does not pick up.”

-----

## Plugin 8: `cache` — The Evidence Database 🗄️

```
cache 30 {
    success 9984 300
    denial  9984 5
    prefetch 10 1m 10%
}
```

|Parameter           |Value                         |Meaning                                                                         |
|--------------------|------------------------------|--------------------------------------------------------------------------------|
|`30`                |Default TTL cap               |Never cache longer than 30 seconds regardless of upstream TTL                   |
|`success 9984 300`  |Max 9984 entries, max 300s TTL|Cache for successful (NOERROR) responses                                        |
|`denial 9984 5`     |Max 9984 entries, max 5s TTL  |Cache NXDOMAIN/REFUSED briefly to reduce upstream load                          |
|`prefetch 10 1m 10%`|Prefetch threshold            |If a cache entry is accessed 10+ times in 1 minute, refresh it 10% before expiry|

**CATHERINE:** “The cache is the forensic database. Once an answer is cached, the same question returns instantly without re-querying the detective. But stale cache entries are evidence contamination — an old answer in the cache can mask a real change in the cluster. The 30-second default TTL is the tradeoff.”

-----

## Plugin 9: `loop` — The Circular Alibi Detector 🔄

```
loop
```

Detects forwarding loops. If CoreDNS forwards a query upstream and that upstream sends it back to CoreDNS (creating a loop), the `loop` plugin detects and reports it.

**How it works:** CoreDNS sends a canary query to itself on startup. If the query comes back through the `forward` plugin, a loop exists. CoreDNS logs the error and exits.

```bash
# Loop detected — CoreDNS logs this and crashes
[FATAL] Loop (127.0.0.1:53 → :53) detected for zone "."
```

**Common cause:** The node’s `/etc/resolv.conf` points to a nameserver that is actually CoreDNS itself (e.g., the node has `nameserver 10.96.0.10` and CoreDNS uses that for forwarding).

-----

## Plugin 10: `reload` — The Hot-Reload System ♻️

```
reload
```

Watches the Corefile for changes every 30 seconds. When a change is detected (SHA256 hash comparison), rebuilds the plugin chain without restarting the pod.

```bash
# Edit the Corefile
kubectl edit configmap coredns -n kube-system

# Wait 30 seconds, then check if CoreDNS picked up the change
kubectl logs -n kube-system -l k8s-app=kube-dns \
  | grep -i reload

# [INFO] Reloading
# [INFO] Reloading complete
```

-----

## Plugin 11: `loadbalance` — The Round-Robin Shuffler 🔃

```
loadbalance round_robin
```

Randomises the order of A/AAAA records in responses. When a headless service returns three pod IPs, `loadbalance` shuffles them so different clients connect to different pods without needing intelligent client-side load balancing.

-----

## Plugin 12: `hosts` — The Static Evidence File 📄

Not in the default Corefile, but extremely useful for adding static DNS entries:

```
hosts /etc/coredns/customhosts cluster.local {
    192.168.1.100   special-service.internal
    192.168.1.101   legacy-db.internal
    fallthrough
}
```

**SARA:** “The hosts plugin is for entries that need to be hardcoded. A legacy service with a static IP that will not be in Kubernetes. A migration alias. A temporary override while you fix the real issue.”

-----

## Putting It All Together: The Complete Lab Profile 🔬

```bash
# Validate a new Corefile before applying it
# (CoreDNS does not validate Corefile syntax via kubectl — test it first)

# Option 1: Use the CoreDNS binary directly
docker run --rm -v $(pwd)/Corefile:/Corefile coredns/coredns:latest \
  -conf /Corefile -dryrun

# Option 2: Deploy a test instance
kubectl run coredns-test \
  --image=coredns/coredns:latest \
  --command -- /coredns -conf /dev/stdin <<'EOF'
.:5353 {
  errors
  log
  kubernetes cluster.local {
    pods insecure
  }
  cache 30
}
EOF
```

-----

## What’s Next: The Forensic Database 🗄️

*Warrick points at the Prometheus dashboard.*

**WARRICK:** “We have the lab equipment catalogued. Now we need to use it. Episode 5: the forensic database. Cache internals, TTL mechanics, Prometheus metrics for DNS observability, NodeLocal DNSCache — the distributed evidence archive. And the diagnostic toolkit: how to actually tell what CoreDNS is doing in real time.”

-----

**🔗 Resources**

- **CoreDNS plugin documentation**: [coredns.io/plugins](https://coredns.io/plugins/)
- **kubernetes plugin**: [coredns.io/plugins/kubernetes](https://coredns.io/plugins/kubernetes/)
- **Customising CoreDNS**: [kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/)

-----

*🔬 Who Are You CoreDNS? — a CSI-style investigation into Kubernetes DNS. The evidence is in the Corefile. The answers are in the logs.*
