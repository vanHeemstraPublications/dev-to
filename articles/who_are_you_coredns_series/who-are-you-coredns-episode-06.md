---
title: "Who Are You CoreDNS? 🔬 Ep.6"
published: false
description: "Episode 6: Some DNS cases never close. Intermittent timeouts with no pattern. SERVFAILs that appear in production but never in testing. Pods that can reach some services but not others. The cold case files. This episode is the complete DNS troubleshooting playbook: the full diagnostic toolkit, the twelve most common failure patterns, and the forensic methodology for moving from symptom to root cause."
tags: [kubernetes, coredns, troubleshooting, debugging]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/who-are-you-coredns-episode-06.png"
series: "Who Are You coreDNS?"
canonical_url: ""
organization: "the-software-s-journey"
part: 6
---

## Episode 6: Cold Cases

*🎵 Who are you? Who who, who who? 🎵*

-----

## “The Case That Almost Got Away” 🧊

*A thick folder lands on Nick Stokes’s desk. COLD CASE stamped across the front. He opens it.*

**NICK:** “DNS investigation, six months old. Pod in the `orders` namespace. Intermittent 5-second timeouts on outbound HTTP calls. No pattern. Happens once every hundred requests. Developers cannot reproduce it. Network team says the network is fine. The case was marked unsolved.”

*He looks at the metadata at the top of the file: `conntrack udp race condition — ndots:5 — nodelocaldns not deployed`.*

**NICK:** “I’ve seen this before. The symptom is random timeouts. The cause is a race condition in the Linux conntrack table, triggered by two concurrent UDP DNS queries from the same source port. Kubernetes DNS default settings make this almost inevitable under load.”

*He picks up his forensic kit.*

**NICK:** “Let us reopen this case. And let us go through every cold case in the book — because most DNS problems look different but come from the same twelve root causes.”

-----

## 🗂️ SIPOC — The Cold Case Investigation

|**Suppliers**              |**Inputs**                                       |**Process**                                                                                                                  |**Outputs**                                                  |**Customers**                                                     |
|---------------------------|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|------------------------------------------------------------------|
|The failing pod            |Symptoms: timeout, NXDOMAIN, SERVFAIL, refused   |Systematic elimination: check resolv.conf → check service existence → check CoreDNS health → check upstream → check conntrack|Root cause + remediation                                     |The engineer — who can now fix the right thing instead of guessing|
|CoreDNS logs               |Error and query log lines                        |Filter by query name, response code, source IP                                                                               |A timeline of what happened and when                         |The investigation — confirms or rules out each hypothesis         |
|`dig` and `nslookup`       |DNS queries sent directly to specific nameservers|Bypasses application-level DNS caching, gives exact resolver behaviour                                                       |Raw DNS response: answer, RCODE, latency, query path         |The investigator — who sees the DNS truth unfiltered              |
|`tcpdump` / network capture|Raw DNS packets on port 53                       |Shows every query and response at the packet level, including retries                                                        |Exact packet sequence: query → response time, retransmissions|The investigation — proves what the network actually sent         |

-----

## The Forensic Toolkit: Instruments of the Trade 🔬

Before investigating specific cases, establish the toolkit:

```bash
# === ESSENTIAL TOOL 1: The Debug Pod ===
# Run this in the affected namespace for maximum accuracy

kubectl run dns-investigator \
  --image=nicolaka/netshoot:latest \
  --restart=Never \
  --rm -it \
  -n <affected-namespace> \
  -- bash

# nicolaka/netshoot has: dig, nslookup, curl, wget, tcpdump,
#   nmap, traceroute, mtr, iperf3, and many more


# === ESSENTIAL TOOL 2: Check CoreDNS health ===
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns --since=10m
kubectl top pods -n kube-system -l k8s-app=kube-dns


# === ESSENTIAL TOOL 3: Direct DNS queries with dig ===
# Inside the debug pod:

# Query specific CoreDNS pod directly (bypass kube-dns service)
COREDNS_IP=$(kubectl get pods -n kube-system -l k8s-app=kube-dns \
  -o jsonpath='{.items[0].status.podIP}')
dig @${COREDNS_IP} payment-service.payments.svc.cluster.local

# Query with verbose output
dig +noall +answer +stats @10.96.0.10 payment-service.payments.svc.cluster.local

# Show all search path attempts
dig +search payment-service

# Force FQDN (trailing dot = no search expansion)
dig @10.96.0.10 payment-service.payments.svc.cluster.local.


# === ESSENTIAL TOOL 4: nslookup for quick checks ===
nslookup payment-service.payments.svc.cluster.local
nslookup payment-service.payments.svc.cluster.local 10.96.0.10


# === ESSENTIAL TOOL 5: tcpdump to watch DNS traffic ===
# Inside debug pod or on the node:
tcpdump -i any -n port 53 -w /tmp/dns-capture.pcap

# Quick live watch:
tcpdump -i any -n port 53 -l | grep -E "(A|AAAA|CNAME)\?"
```

-----

## The Twelve Cold Cases 🗂️

### Cold Case #1: NXDOMAIN — “The Service Does Not Exist”

**Symptom:** Application gets `Name does not resolve` or `EAI_NONAME`.

**Investigation:**

```bash
# Is the service actually there?
kubectl get service <service-name> -n <namespace>

# Check the exact name the app uses (common: wrong namespace or typo)
kubectl get services --all-namespaces | grep <partial-name>

# Try the FQDN manually
dig payment-service.payments.svc.cluster.local @10.96.0.10

# If NXDOMAIN — the service genuinely doesn't exist or is in wrong namespace
# If NOERROR — the app is using the wrong name
```

**Most common causes:**

- Service does not exist (not deployed, wrong namespace)
- Application hardcodes wrong service name or namespace
- Service was renamed in deployment but app not updated

-----

### Cold Case #2: SERVFAIL — “The Lab Cannot Process This Request”

**Symptom:** DNS returns SERVFAIL instead of an answer.

```bash
# Check CoreDNS logs for SERVFAIL
kubectl logs -n kube-system -l k8s-app=kube-dns \
  | grep "SERVFAIL"

# [ERROR] plugin/errors: 2 SERVFAIL google.com. A
#   UDP 35 10.244.1.15:12345 → 10.96.0.10:53 0.500s
```

**Common causes:**

|Cause                 |Diagnosis                                         |Fix                                         |
|----------------------|--------------------------------------------------|--------------------------------------------|
|Upstream unreachable  |`dig @8.8.8.8 google.com` from a CoreDNS pod fails|Fix upstream nameserver or network policy   |
|Loop detected         |CoreDNS exits with loop error                     |Fix `/etc/resolv.conf` on nodes             |
|API server unreachable|kubernetes plugin cannot list services            |Check API server health and network policies|
|CoreDNS OOMKilled     |Pod restarts frequently                           |Increase memory limits                      |

```bash
# Test if CoreDNS can reach its upstream
kubectl exec -n kube-system $(kubectl get pods -n kube-system \
  -l k8s-app=kube-dns -o name | head -1) -- \
  nslookup google.com 8.8.8.8

# If this fails: CoreDNS cannot reach external DNS
# Check: egress network policies, node-level firewall rules
```

-----

### Cold Case #3: Timeout — “The Call Never Came Back”

**Symptom:** DNS queries hang for 5 or 30 seconds, then fail with `EAI_AGAIN`.

The most common source of 5-second timeouts in Kubernetes: the **conntrack UDP race condition**.

```
The Crime:
  1. Pod queries A record for external-service.com
  2. ndots:5 causes two concurrent queries:
     - external-service.com.namespace.svc.cluster.local (NXDOMAIN expected fast)
     - external-service.com. (needs to go upstream)
  3. Both use the same source port (common with some resolvers)
  4. Both arrive at the conntrack table simultaneously
  5. Conntrack drops one (it cannot track two UDP packets with same 5-tuple)
  6. The dropped query waits for retransmit timeout: 5 seconds
```

**Diagnose:**

```bash
# Check for conntrack drops on the node
# (Run on the node hosting the failing pod)
cat /proc/net/stat/nf_conntrack | awk 'NR==1 || NR==2'

# More targeted: count UDP DNS conntrack entries
conntrack -L -p udp --dport 53 2>/dev/null | wc -l

# If NodeLocal DNSCache is not deployed, this is likely the cause
kubectl get daemonset node-local-dns -n kube-system
```

**Fix options:**

```
Option 1 (best): Deploy NodeLocal DNSCache (uses TCP, bypasses conntrack issue)
Option 2: Reduce ndots
  dnsConfig:
    options:
    - name: ndots
      value: "1"
Option 3: Use FQDNs in all application hostnames (trailing dot)
Option 4: Use TCP for DNS explicitly:
  forward . 8.8.8.8 {
    prefer_udp false
  }
```

-----

### Cold Case #4: “Resolves Sometimes, Not Always”

**Symptom:** Intermittent DNS failures, hard to reproduce.

**Investigation:**

```bash
# Loop the query 100 times, count failures
for i in $(seq 1 100); do
  result=$(kubectl exec -n payments dns-investigator -- \
    dig +short payment-service.payments.svc.cluster.local 2>&1)
  if [ -z "$result" ]; then
    echo "FAILED on attempt $i"
  fi
done

# Check if the issue is with a specific CoreDNS pod
# (kube-dns service load-balances between pods)
for pod in $(kubectl get pods -n kube-system -l k8s-app=kube-dns \
  -o jsonpath='{.items[*].metadata.name}'); do
  podIP=$(kubectl get pod $pod -n kube-system \
    -o jsonpath='{.status.podIP}')
  echo -n "Pod $pod ($podIP): "
  dig +short payment-service.payments.svc.cluster.local @$podIP
done
```

**Common causes:**

- One of the CoreDNS pods is unhealthy but still receiving traffic
- Resource limits causing CoreDNS pod to throttle
- Race condition in etcd or API server response

-----

### Cold Case #5: REFUSED — “The Lab Won’t Take This Case”

**Symptom:** DNS returns REFUSED instead of NXDOMAIN or NOERROR.

```bash
dig payment-service.payments.svc.cluster.local
# ;; status: REFUSED
```

**Cause:** The query was for a zone that CoreDNS is not authoritative for, and there is no `forward` plugin covering it, or an `acl` plugin is blocking it.

```bash
# Check if the zone is handled
# Look at the Corefile
kubectl get configmap coredns -n kube-system -o jsonpath='{.data.Corefile}'

# If the query is for a zone not in any server block, CoreDNS refuses it
# Fix: add a catch-all forward
# .:53 {
#   forward . /etc/resolv.conf
# }
```

-----

### Cold Case #6: ExternalName CNAME Loop

**Symptom:** ExternalName service resolves to another ExternalName service, which points back to the first.

```bash
# Detect: follow the CNAME chain
dig +trace external-alias.payments.svc.cluster.local

# If you see the same name appear twice in the CNAME chain: loop detected
```

**Fix:**

```bash
# Audit ExternalName services
kubectl get services --all-namespaces \
  -o json | jq '.items[] | select(.spec.type=="ExternalName") |
  {name: .metadata.name, ns: .metadata.namespace,
   target: .spec.externalName}'
```

-----

### Cold Case #7: Wrong DNS Policy on Host-Networked Pods

**Symptom:** A pod using `hostNetwork: true` gets the node’s DNS configuration, not cluster DNS.

```yaml
# Pods with hostNetwork: true use host DNS by default
spec:
  hostNetwork: true
  # dnsPolicy defaults to "Default" (host DNS) for hostNetwork pods
  # Must explicitly set to ClusterFirstWithHostNet for cluster DNS
  dnsPolicy: ClusterFirstWithHostNet   # ← Fix
```

```bash
# Check which pods are using hostNetwork
kubectl get pods --all-namespaces \
  -o jsonpath='{range .items[?(@.spec.hostNetwork==true)]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}'
```

-----

### Cold Case #8: CoreDNS Crashlooping

**Symptom:** CoreDNS pods repeatedly restart.

```bash
# Check restart count and reason
kubectl get pods -n kube-system -l k8s-app=kube-dns
# NAME                       READY   STATUS    RESTARTS   AGE
# coredns-5d78c9869d-2xkpg   0/1     CrashLoop  12         4h

# Check the last crash
kubectl logs -n kube-system coredns-5d78c9869d-2xkpg --previous

# Common crash causes:
# [FATAL] Loop (127.0.0.1:53 → :53) detected
#   Fix: remove the loop back address from /etc/resolv.conf on nodes

# [FATAL] Corefile: <syntax error>
#   Fix: validate Corefile syntax before applying

# OOMKilled
kubectl describe pod coredns-5d78c9869d-2xkpg -n kube-system \
  | grep -A 5 "OOM"
#   Fix: increase memory limits in CoreDNS deployment
```

-----

### Cold Case #9: Split-Brain — Different Pods Get Different Answers

**Symptom:** The same DNS query returns different results from different pods.

```bash
# Test from two different pods in different nodes
kubectl exec pod-a -n test -- dig payment-service.payments.svc.cluster.local
kubectl exec pod-b -n test -- dig payment-service.payments.svc.cluster.local

# If answers differ:
# 1. Check which CoreDNS pod each query hit
# 2. Check if one CoreDNS pod has a stale cache
# 3. Check if kubernetes plugin state is different per pod (should not be)

# Force queries to a specific CoreDNS pod
COREDNS_POD_A_IP=10.244.0.5
COREDNS_POD_B_IP=10.244.0.6

kubectl exec pod-a -- dig @${COREDNS_POD_A_IP} payment-service.payments.svc.cluster.local
kubectl exec pod-a -- dig @${COREDNS_POD_B_IP} payment-service.payments.svc.cluster.local
```

-----

### Cold Case #10: Slow Kubernetes API → Slow DNS

**Symptom:** DNS for cluster services is slow (>10ms) but external DNS is fast.

```bash
# CoreDNS kubernetes plugin latency == kubernetes API latency
# Check API server response time
kubectl get --request-timeout=5s services --all-namespaces \
  -o name > /dev/null && echo "API OK"

# Check kubernetes plugin metrics
curl -s http://localhost:9153/metrics \
  | grep coredns_kubernetes_dns_programming_duration

# If API is slow, CoreDNS will be slow
# Fix: ensure API server has adequate resources
# Fix: reduce watch delay — check if endpointslice watch is working
```

-----

### Cold Case #11: IPv6 AAAA Queries Causing Delays

**Symptom:** Applications that query both A and AAAA records see double the DNS latency.

```bash
# Check if AAAA queries are generating NXDOMAIN delays
kubectl logs -n kube-system -l k8s-app=kube-dns \
  | grep "AAAA" | grep "NXDOMAIN"

# In a single-stack IPv4 cluster, every AAAA query gets NXDOMAIN
# Applications using getaddrinfo() in AF_UNSPEC mode query both simultaneously

# Fix option 1: Ensure the denial cache is short (default 5s is fine)
# Fix option 2: Set single_request in resolv.conf options
# (forces A and AAAA to be sent sequentially, not concurrently)
```

```yaml
spec:
  dnsConfig:
    options:
    - name: single-request-reopen    # Send A and AAAA sequentially
```

-----

### Cold Case #12: Network Policy Blocking DNS

**Symptom:** DNS works for pods without NetworkPolicy, fails for pods with NetworkPolicy applied.

```bash
# Check if the failing pod has a NetworkPolicy
kubectl get networkpolicy -n <namespace>

# A NetworkPolicy that blocks all egress will also block DNS
# DNS port 53 must be explicitly allowed
```

```yaml
# NetworkPolicy that allows DNS egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: payments
spec:
  podSelector: {}   # All pods in namespace
  policyTypes:
  - Egress
  egress:
  # Allow DNS to CoreDNS
  - ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
    to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
```

-----

## The Complete Investigation Protocol 📋

```bash
#!/bin/bash
# DNS investigation script — run from debug pod in affected namespace

SERVICE_NAME=${1:-"my-service"}
NAMESPACE=${2:-default}
FULL_NAME="${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local"

echo "=== DNS INVESTIGATION: ${FULL_NAME} ==="

echo ""
echo "1. Local resolver configuration:"
cat /etc/resolv.conf

echo ""
echo "2. CoreDNS health:"
kubectl get pods -n kube-system -l k8s-app=kube-dns 2>/dev/null || \
  echo "Cannot check from inside pod — run this from kubectl"

echo ""
echo "3. Service existence check:"
kubectl get service ${SERVICE_NAME} -n ${NAMESPACE} 2>/dev/null || \
  nslookup ${FULL_NAME} 10.96.0.10

echo ""
echo "4. Direct DNS query:"
dig +noall +answer +stats ${FULL_NAME} @10.96.0.10

echo ""
echo "5. Search expansion test (watch for multiple queries):"
dig +search ${SERVICE_NAME} +noall +answer +stats

echo ""
echo "6. Reverse DNS (PTR check):"
RESOLVED_IP=$(dig +short ${FULL_NAME} @10.96.0.10 | head -1)
if [ -n "${RESOLVED_IP}" ]; then
  REVERSED=$(echo ${RESOLVED_IP} | awk -F. '{print $4"."$3"."$2"."$1".in-addr.arpa"}')
  dig +short PTR ${REVERSED} @10.96.0.10
fi

echo ""
echo "7. Latency test (10 iterations):"
for i in $(seq 1 10); do
  dig +short ${FULL_NAME} @10.96.0.10 +stats 2>&1 | grep "Query time"
done
```

-----

## What’s Next: Undercover Operations 🕵️

*Nick closes the cold case folder. SOLVED stamped across it.*

**NICK:** “Twelve cases. All solvable. The key is the methodology — start at the pod, work outward. Check `resolv.conf` first. Check service existence second. Check CoreDNS health third. Check upstream fourth.”

*Another file slides across the desk.*

**GRISSOM:** “Episode 7. The advanced cases. DNS rewrites. Stub zones. Split-horizon. Template-generated responses. The undercover operations that let CoreDNS serve different answers to different callers, rewrite query names mid-flight, and maintain entirely separate DNS identities for the same infrastructure.”

*The theme song plays.*

*The investigation continues.*

-----

**🔗 Resources**

- **CoreDNS troubleshooting guide**: [coredns.io/manual/troubleshooting](https://coredns.io/manual/troubleshooting/)
- **nicolaka/netshoot**: [github.com/nicolaka/netshoot](https://github.com/nicolaka/netshoot)
- **Kubernetes DNS debugging**: [kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/)

-----

*🔬 Who Are You CoreDNS? — a CSI-style investigation into Kubernetes DNS. The evidence is in the Corefile. The answers are in the logs.*
