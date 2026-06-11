---
title: "Who Are You CoreDNS? 🔬 Ep.2"
published: false
description: "Episode 2: The pod is down. DNS is not responding. The on-call engineer suits up and enters the crime scene: /etc/resolv.conf. The victim — a simple hostname lookup — was ambushed by ndots:5, overwhelmed by search domain expansion, and left for dead before the FQDN was ever tried. CSI: Kubernetes processes the scene."
tags: [kubernetes, dns, coredns, troubleshooting]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/who-are-you-coredns-episode-02.png"
series: "Who Are You coreDNS?"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

## Episode 2: The Crime Scene

*🎵 Who are you? Who who, who who? 🎵*

-----

## “Don’t Touch Anything Until I Get There” 🚨

*04:23am. PagerDuty fires. The on-call engineer’s phone lights up: “payment-service unreachable, 5xx rate 100%.”*

*Catherine Willows is already in the building.*

**CATHERINE:** “Okay. What do we have?”

**NICK:** “Pod in the `payments` namespace tried to connect to `payment-db`. DNS query. Forty-second timeout. The pod crashed.”

**CATHERINE:** “Forty seconds. That is not a network problem. That is DNS. Get me inside that pod.”

```bash
kubectl exec -it payment-worker-7f8d9-abc -n payments -- sh
```

*Inside the pod, Catherine walks to the first piece of evidence.*

**CATHERINE:** “Always start with the witness.”

```bash
cat /etc/resolv.conf
```

```
nameserver 10.96.0.10
search payments.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

**CATHERINE:** “There it is. The victim’s last known contact list. Let us read every line.”

-----

## 🗂️ SIPOC — The Crime Scene Analysis

|**Suppliers**              |**Inputs**                                |**Process**                                                                          |**Outputs**                                                                                                       |**Customers**                                                  |
|---------------------------|------------------------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
|kubelet                    |Pod spec, node configuration              |Injects `/etc/resolv.conf` into every pod at creation time                           |A `resolv.conf` with nameserver, search, and options                                                              |Every DNS lookup the pod makes — governed entirely by this file|
|`ndots:5` option           |A hostname to resolve                     |If the hostname has fewer than 5 dots: try all search domains first, then try as FQDN|Up to 6 DNS queries for a name that could be answered in 1                                                        |CoreDNS — which receives the flood of search-expanded queries  |
|Search domain list         |Partially-qualified name like `payment-db`|Linux resolver appends each search domain in turn                                    |`payment-db.payments.svc.cluster.local`, `payment-db.svc.cluster.local`, `payment-db.cluster.local`, `payment-db.`|CoreDNS — which must respond to each one                       |
|CoreDNS `kubernetes` plugin|Fully-qualified cluster names             |Watches Kubernetes API, synthesises DNS records                                      |Correct A record, NXDOMAIN if service does not exist                                                              |The pod — which finally gets or fails to get an answer         |

-----

## Evidence Item 1: The `nameserver` Line 🔬

```
nameserver 10.96.0.10
```

This is the pod’s direct line to the CoreDNS lab. Every DNS query the pod makes goes to `10.96.0.10` — the `kube-dns` ClusterIP service. This IP is stable across the cluster lifetime.

**NICK:** “So every query goes here first. If CoreDNS is down, everything breaks.”

**CATHERINE:** “Correct. And notice — there is only one nameserver. No fallback. If `10.96.0.10` is unreachable, the pod does not try another. The single point of failure is by design — the `kube-dns` Service is backed by multiple CoreDNS pods.”

```bash
# Verify the kube-dns service is healthy
kubectl get endpoints kube-dns -n kube-system

# NAME       ENDPOINTS                          AGE
# kube-dns   10.244.0.5:53,10.244.0.6:53,...    14d
```

-----

## Evidence Item 2: The `search` Line 🔍

```
search payments.svc.cluster.local svc.cluster.local cluster.local
```

This is the search domain list. Three domains. When a pod makes a DNS query for a **partially-qualified** name, the resolver appends each search domain in turn until it gets an answer.

**SARA:** “So if the application code calls `getaddrinfo("payment-db")` — what actually gets queried?”

**CATHERINE:** “Observe.”

```
Query for "payment-db" — expansion sequence:
  1. payment-db.payments.svc.cluster.local     ← namespace first
  2. payment-db.svc.cluster.local              ← cluster services
  3. payment-db.cluster.local                  ← cluster domain
  4. payment-db.                               ← bare hostname (ndots triggers this)
```

**SARA:** “Four queries for one hostname. That is… a lot of traffic.”

**CATHERINE:** “And expensive when services have high query rates. Now look at this application.”

```python
# The application code — perfectly innocent
import psycopg2
conn = psycopg2.connect(host="payment-db", ...)
```

```
# What the resolver actually sends to CoreDNS:
→ payment-db.payments.svc.cluster.local?       ← NXDOMAIN (service is payment-db-service)
→ payment-db.svc.cluster.local?                ← NXDOMAIN
→ payment-db.cluster.local?                    ← NXDOMAIN
→ payment-db.?                                 ← NXDOMAIN (no such external host)
# All four fail. Connection timeout after ~40 seconds.
```

**CATHERINE:** “The service exists. Its name is `payment-db-service`. The application used `payment-db`. No match. Four queries. Forty-second timeout. Case closed — but the wrong way.”

-----

## Evidence Item 3: `options ndots:5` — The Most Dangerous Setting 💀

```
options ndots:5
```

**GRISSOM:** *enters the room* “This is where most DNS crimes in Kubernetes originate.”

`ndots:5` means: if the hostname being queried contains **fewer than 5 dots**, treat it as a **relative name** and try all search domains first. Only after all search domains fail does the resolver try the name as a fully-qualified domain name (FQDN).

**The critical threshold:**

|Hostname          |Dots            |ndots:5 behavior                              |
|------------------|----------------|----------------------------------------------|
|`payment-db`      |0               |Try all 3 search domains first, then bare     |
|`google.com`      |1               |Try all 3 search domains first, then bare     |
|`api.example.com` |2               |Try all 3 search domains first, then bare     |
|`api.example.com.`|2 + trailing dot|**FQDN** — query directly, no search expansion|
|`a.b.c.d.e`       |4               |Try all 3 search domains first, then bare     |
|`a.b.c.d.e.f`     |5               |**FQDN** — query directly                     |

**GRISSOM:** “The default ndots:5 in Kubernetes was set for a reason: it allows short service names to resolve via search domains. But it creates a tax on every external DNS query. `google.com` becomes five queries before it resolves correctly.”

```bash
# Watch the crime happen in real time
# In one terminal:
kubectl exec -it debug-pod -n payments -- tcpdump -i eth0 -n port 53

# In another terminal:
kubectl exec -it debug-pod -n payments -- curl http://api.external-service.com

# tcpdump output — notice ALL the search attempts:
# 04:23:15 DNS Query: api.external-service.com.payments.svc.cluster.local
# 04:23:15 DNS Response: NXDOMAIN
# 04:23:15 DNS Query: api.external-service.com.svc.cluster.local
# 04:23:15 DNS Response: NXDOMAIN
# 04:23:15 DNS Query: api.external-service.com.cluster.local
# 04:23:15 DNS Response: NXDOMAIN
# 04:23:15 DNS Query: api.external-service.com.
# 04:23:15 DNS Response: A 203.0.113.1   ← Finally!
```

**WARRICK:** “So every external HTTP call from inside a pod makes three garbage DNS queries before the real one. At scale, that is enormous unnecessary load on CoreDNS.”

-----

## The Correct Way to Call the Lab: FQDNs 📞

The single most powerful fix for DNS performance problems in Kubernetes is using **fully-qualified domain names** with a trailing dot, or at least providing enough dots to clear the ndots threshold:

```python
# The inefficient way — 4 queries
conn = psycopg2.connect(host="payment-db", ...)

# The efficient way — full service name, still 4 queries (4 < 5 dots)
conn = psycopg2.connect(host="payment-db-service.payments.svc.cluster.local", ...)

# The most efficient way — trailing dot forces FQDN, 1 query
conn = psycopg2.connect(host="payment-db-service.payments.svc.cluster.local.", ...)
```

The trailing dot signals “this is already fully qualified, do not search-expand it.” One query. One response. Done.

-----

## DNS Policies: How Pods Choose Their Search Path 🗺️

Not every pod uses the same `/etc/resolv.conf`. The `dnsPolicy` field in the Pod spec controls this:

```yaml
apiVersion: v1
kind: Pod
spec:
  dnsPolicy: ClusterFirst   # The default — use CoreDNS
  # Other options:
  # ClusterFirstWithHostNet — CoreDNS even when using host network
  # Default              — use the node's resolv.conf (not cluster DNS!)
  # None                 — provide your own dnsConfig entirely
```

```yaml
# DNS policy "None" — the Witness Protection Program
# Pod uses entirely custom nameservers, ignores cluster DNS
apiVersion: v1
kind: Pod
spec:
  dnsPolicy: None
  dnsConfig:
    nameservers:
      - 1.1.1.1
    searches:
      - mycompany.internal
    options:
      - name: ndots
        value: "2"    # Lower ndots — fewer search attempts
```

**CATHERINE:** “The `None` policy with custom `dnsConfig` is how you give a pod witness protection. It exists in the cluster but uses entirely different nameservers. Useful for compliance requirements, but isolates the pod from cluster service discovery entirely.”

-----

## The Time of Death: DNS Timeout Anatomy ⏱️

When a DNS query fails, the timeline of failure is precise:

```
t=0:    Application calls getaddrinfo("payment-db")
t=0.1:  Query 1: payment-db.payments.svc.cluster.local → NXDOMAIN (fast)
t=0.2:  Query 2: payment-db.svc.cluster.local → NXDOMAIN (fast)
t=0.3:  Query 3: payment-db.cluster.local → NXDOMAIN (fast)
t=0.4:  Query 4: payment-db. → (CoreDNS timeout, no upstream answer)
t=5.4:  Retry query 4 (default retry behavior)
t=10.4: Retry again
...
t=40:   Resolver gives up. getaddrinfo returns EAI_AGAIN.
t=40:   Application receives "Temporary failure in name resolution"
t=40:   Application crashes / returns 503
t=40:   PagerDuty fires. On-call engineer wakes up.
```

**NICK:** “Forty seconds to determine the service does not exist by that name. And in that forty seconds, the application held the connection open, upstream calls queued, users saw errors.”

**GRISSOM:** “DNS failures are not instantaneous. They are patient killers.”

-----

## The Physical Evidence: Full Trace 🧪

Reproduce the crime scene completely:

```bash
# Step 1: Deploy a debug pod
kubectl run dns-investigator \
  --image=nicolaka/netshoot \
  --restart=Never \
  -n payments \
  -- sleep infinity

# Step 2: Examine the witness statement
kubectl exec dns-investigator -n payments -- cat /etc/resolv.conf

# Step 3: Run the first query — watch the search expansion
kubectl exec dns-investigator -n payments -- \
  nslookup -debug payment-db 2>&1 | head -40

# Step 4: Run the FQDN query — watch it resolve immediately
kubectl exec dns-investigator -n payments -- \
  nslookup payment-db-service.payments.svc.cluster.local

# Step 5: Check the CoreDNS logs for the queries
kubectl logs -n kube-system \
  -l k8s-app=kube-dns \
  --since=5m \
  | grep "payment-db"

# Sample log output (with log plugin enabled):
# [INFO] 10.244.1.15:54832 - "A IN payment-db.payments.svc.cluster.local. udp 54 false 512" NXDOMAIN qr,aa,rd 147 0.000123s
# [INFO] 10.244.1.15:54833 - "A IN payment-db.svc.cluster.local. udp 49 false 512" NXDOMAIN qr,aa,rd 142 0.000098s
# [INFO] 10.244.1.15:54834 - "A IN payment-db.cluster.local. udp 46 false 512" NXDOMAIN qr,aa,rd 139 0.000102s
```

-----

## Filing the Report: The Fix 📝

**CATHERINE:** “We have the cause of death. The service name was wrong. The `ndots:5` setting amplified the failure. The fix is in two places.”

**Fix 1: Use the correct service name**

```yaml
# In the application deployment
env:
- name: DB_HOST
  value: "payment-db-service.payments.svc.cluster.local"
  # Or with trailing dot for maximum efficiency:
  value: "payment-db-service.payments.svc.cluster.local."
```

**Fix 2: Lower `ndots` for pods that primarily query external services**

```yaml
spec:
  dnsConfig:
    options:
    - name: ndots
      value: "2"   # External-heavy pods benefit from fewer search attempts
```

**Fix 3: If using service mesh — verify the service actually exists**

```bash
kubectl get service payment-db-service -n payments
# Error: service not found  ← The real root cause
```

**GRISSOM:** “The DNS failure was a symptom. The service not existing was the cause. DNS told us the truth — `payment-db` does not exist. We were too busy watching the DNS traffic to notice the real crime: the service was never deployed.”

*He marks the case file: SOLVED.*

-----

## What’s Next: Fingerprints and DNA 🧬

*Sara Sidle holds up a packet capture file.*

**SARA:** “We got the search domain issue. But there is more to this scene. A, AAAA, CNAME, SRV, PTR — every record type tells a different story. A pod pointing to the wrong endpoint. An ExternalName service with an identity crisis. A headless service that has too many faces. Episode 3 — record types. The fingerprints of DNS.”

-----

**🔗 Resources**

- **Pod DNS configuration**: [kubernetes.io/docs/concepts/services-networking/dns-pod-service](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- **ndots explained**: [practicalzfs.com/book/coredns-ndots](https://practiK8s.io/dns)
- **netshoot debug image**: [github.com/nicolaka/netshoot](https://github.com/nicolaka/netshoot)

-----

*🔬 Who Are You CoreDNS? — a CSI-style investigation into Kubernetes DNS. The evidence is in the Corefile. The answers are in the logs.*
