---
title: "Who Are You CoreDNS? 🔬 Ep.1"
published: false
description: "Episode 1: *ba-ba-baaaa, ba-ba-baaaaa* — Who are you? Who who, who who? A DNS query hits the wire. A pod needs an answer. And in the shadows of kube-system, the CoreDNS lab is already processing evidence. Welcome to the most overlooked crime scene in Kubernetes: the DNS stack. Every resolution failure is a case. Every timeout is a cold case. Every Corefile is a case file."
tags: [kubernetes, dns, coredns, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/who-are-you-coredns-episode-01.png"
series: "Who Are You coreDNS?"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: The Opening Credits

*🎵 ba-ba-baaaa, ba-ba-baaaaa… Who are you? Who who, who who? 🎵*

-----

## The Case Is Open 🚨

*Las Vegas. 11:47pm. A pod in namespace `production` tries to reach `payment-service`. The connection hangs. Thirty seconds pass. The application logs a timeout.*

*Someone pages the on-call engineer.*

*The engineer pulls up their terminal. Types `kubectl exec`. Runs `nslookup`.*

*The DNS query returns nothing.*

*Gil Grissom leans against the doorframe of the kube-system namespace.*

**GRISSOM:** “Every DNS failure tells a story. The packet left the pod, traveled to the nameserver, and then… something happened. What happened — that is the question. And the answer is always in the evidence.”

*He picks up the Corefile.*

**GRISSOM:** “Let’s process the scene.”

-----

## 🗂️ SIPOC — The DNS Investigation

|**Suppliers**        |**Inputs**                             |**Process**                                                    |**Outputs**                                                         |**Customers**                                                        |
|---------------------|---------------------------------------|---------------------------------------------------------------|--------------------------------------------------------------------|---------------------------------------------------------------------|
|Application pods     |DNS queries: A, AAAA, SRV, PTR         |CoreDNS plugin chain processes each query in configured order  |DNS responses: IP addresses, CNAMEs, SRV records, NXDOMAIN, SERVFAIL|Every pod in the cluster — service discovery depends on this entirely|
|Kubernetes API server|Service, Endpoint, Pod objects         |`kubernetes` plugin watches API, builds DNS records dynamically|Synthesised DNS records matching current cluster state              |Clients querying `<svc>.<ns>.svc.cluster.local`                      |
|Upstream resolvers   |Forwarded queries for non-cluster names|`forward` plugin sends unresolvable queries upstream           |External DNS answers                                                |Pods needing to reach the internet or corporate DNS                  |
|The Corefile         |Plugin configuration, zones, timeouts  |CoreDNS applies configuration on startup (or hot-reload)       |A running DNS server embodying the policy                           |The cluster — its DNS behaviour is entirely defined by the Corefile  |

-----

## Who Is CoreDNS? The Forensic Profile 🔬

Every investigation begins with a subject profile. Here is CoreDNS:

**Full name:** CoreDNS  
**Location:** `kube-system` namespace, Deployment named `coredns`  
**Service alias:** `kube-dns` (ClusterIP, typically `10.96.0.10`)  
**Architecture:** A DNS server built as a **plugin chain** — a sequence of processing steps, each implemented as a Go plugin  
**Configuration file:** The **Corefile** — a ConfigMap in `kube-system`  
**First appeared:** Kubernetes 1.11 (replaced kube-dns as default)  
**Current status:** The default, production DNS server for every Kubernetes cluster

```bash
# Locate the lab
kubectl get pods -n kube-system -l k8s-app=kube-dns

# NAME                       READY   STATUS    RESTARTS   AGE
# coredns-5d78c9869d-2xkpg   1/1     Running   0          14d
# coredns-5d78c9869d-7nqtl   1/1     Running   0          14d

# Read the case file
kubectl get configmap coredns -n kube-system -o yaml
```

-----

## The Default Corefile: The Master Case File 📋

Every Kubernetes cluster ships with a default Corefile. This is the foundation of every DNS investigation:

```
# The default Kubernetes Corefile
# ConfigMap: coredns, Namespace: kube-system

.:53 {
    errors
    health {
        lameduck 5s
    }
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
        fallthrough in-addr.arpa ip6.arpa
        ttl 30
    }
    prometheus :9153
    forward . /etc/resolv.conf {
        max_concurrent 1000
    }
    cache 30
    loop
    reload
    loadbalance
}
```

**GRISSOM:** “Every line is a piece of evidence. Let us catalogue them.”

|Line         |Plugin           |Role in the investigation                               |
|-------------|-----------------|--------------------------------------------------------|
|`.:53`       |Server block     |This server handles ALL zones (`.`) on port 53          |
|`errors`     |Error logger     |Writes errors to stdout — the crime scene report        |
|`health`     |Health endpoint  |HTTP :8080/health — is the lab operational?             |
|`ready`      |Readiness probe  |HTTP :8181/ready — is the lab ready for queries?        |
|`kubernetes` |K8s integration  |The primary detective — watches Services and Endpoints  |
|`prometheus` |Metrics          |Forensic statistics — query rates, error counts, latency|
|`forward`    |Upstream relay   |Escalates unsolved cases to external nameservers        |
|`cache`      |Evidence database|Stores recent answers — avoids repeating investigations |
|`loop`       |Loop detector    |Catches cases that would loop forever                   |
|`reload`     |Hot reload       |Updates the case file without stopping the lab          |
|`loadbalance`|Answer shuffler  |Randomises A record order for load distribution         |

-----

## The Kubernetes DNS Landscape: The City Map 🗺️

Before investigating cases, understand the jurisdiction:

```
Cluster: mycluster
Domain:  cluster.local

Full DNS hierarchy:
  cluster.local
    └── svc.cluster.local
         └── production.svc.cluster.local
              └── payment-service.production.svc.cluster.local  ← ClusterIP A record
              └── _http._tcp.payment-service.production.svc.cluster.local  ← SRV record
         └── kube-system.svc.cluster.local
              └── kube-dns.kube-system.svc.cluster.local  ← The lab itself
    └── pod.cluster.local  (when pods insecure enabled)
         └── production.pod.cluster.local
              └── 10-0-1-42.production.pod.cluster.local  ← Pod A record
```

**NICK STOKES:** “So every service in the cluster has a fully qualified domain name. The pod queries the name, CoreDNS looks it up, returns the ClusterIP. Clean and simple.”

**GRISSOM:** “When it works. Cases only come to us when it doesn’t.”

-----

## The Plugin Chain: Chain of Custody 🔗

The most important concept in CoreDNS is the **plugin chain**. When a DNS query arrives, it travels through each plugin in the Corefile order. Each plugin can:

1. Handle the query and return a response (case closed)
1. Pass the query to the next plugin (escalate)
1. Modify the query before passing it on (evidence processing)
1. Write to the log (document findings)

```
Query arrives: "What is the IP of payment-service.production.svc.cluster.local?"
│
├─ [1] errors plugin         — passthrough, watches for errors
├─ [2] health plugin         — passthrough (not a query handler)
├─ [3] ready plugin          — passthrough
├─ [4] kubernetes plugin     ← MATCH! This is a cluster.local name.
│       └── Checks API server data
│       └── Finds: payment-service in production namespace, ClusterIP 10.100.42.88
│       └── Returns: A record 10.100.42.88
│       Case closed at plugin 4. Plugins 5-10 are never reached.
│
└─ (for an external name like google.com)
    ├─ [1] errors             — passthrough
    ...
    ├─ [4] kubernetes         — NOT a cluster.local name, passes through
    ├─ [5] prometheus         — passthrough
    ├─ [6] forward            ← MATCH! Sends to upstream resolver.
    │       └── Queries /etc/resolv.conf nameservers
    │       └── Returns answer from upstream
    └─ (cache, loop, etc. — post-processing)
```

**SARA SIDLE:** “The chain of custody is critical. If a plugin mishandles evidence — intercepts a query it should not, or lets a query fall through that it should answer — the case result is wrong.”

-----

## Pod DNS: How the Witness Calls the Lab 📞

Every pod in Kubernetes is born with a pre-configured `/etc/resolv.conf`. This is the pod’s direct line to the CoreDNS lab:

```bash
# Inside any pod:
cat /etc/resolv.conf

nameserver 10.96.0.10        # The kube-dns ClusterIP — the lab's main line
search production.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

These three lines — `nameserver`, `search`, and `options ndots:5` — are the source of the most DNS crimes in Kubernetes. We will investigate them in forensic detail in **Episode 2**.

**WARRICK BROWN:** “The witness called the lab. The lab is `10.96.0.10`. The question is: what happened to the call?”

-----

## Deploying the Lab: The Forensic Infrastructure 🏛️

CoreDNS is already deployed in every Kubernetes cluster, but knowing its structure is essential for investigation:

```bash
# The CoreDNS deployment
kubectl get deployment coredns -n kube-system -o yaml | grep -A 20 spec:

# The service that pods dial (kube-dns)
kubectl get service kube-dns -n kube-system

# NAME       TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
# kube-dns   ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   14d

# The ConfigMap (the Corefile)
kubectl get configmap coredns -n kube-system -o jsonpath='{.data.Corefile}'
```

The RBAC configuration gives CoreDNS the access it needs to watch cluster resources:

```yaml
# CoreDNS ClusterRole — what the lab is allowed to examine
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: system:coredns
rules:
- apiGroups: [""]
  resources: ["endpoints", "services", "pods", "namespaces"]
  verbs: ["list", "watch"]
- apiGroups: ["discovery.k8s.io"]
  resources: ["endpointslices"]
  verbs: ["list", "watch"]
```

**GRISSOM:** “The lab has eyes on every Service, every Pod, every Endpoint in the cluster. It watches, but does not interfere. It answers when asked.”

-----

## The Theme: Eight Cases, One Lab 🔦

Every episode of this series is a case file. Here is the full docket:

|#|Episode                         |The Case               |What We Investigate                                 |
|-|--------------------------------|-----------------------|----------------------------------------------------|
|1|*This one* — The Opening Credits|Introduction           |CoreDNS architecture, the Corefile, plugin chain    |
|2|The Crime Scene                 |DNS resolution failure |`/etc/resolv.conf`, ndots:5, search domains         |
|3|Fingerprints and DNA            |Record types           |A, AAAA, CNAME, SRV, PTR in Kubernetes              |
|4|The CSI Lab                     |The Corefile in depth  |Every plugin examined and explained                 |
|5|The Forensic Database           |Cache and observability|Cache, TTL, Prometheus metrics, NodeLocal DNS       |
|6|Cold Cases                      |Troubleshooting        |Diagnosis toolkit: `dig`, `nslookup`, `kubectl logs`|
|7|Undercover Operations           |Advanced DNS           |Rewrites, stubs, split-horizon, templates           |
|8|Case Closed                     |Production hardening   |RBAC, limits, anti-affinity, multi-cluster          |

**GRISSOM:** “The evidence doesn’t lie. People do. DNS failures don’t lie either — they leave traces. Learn to read the traces.”

*He picks up his kit.*

*A DNS query is waiting.*

*The case is open.*

-----

**🔗 Resources**

- **CoreDNS official documentation**: [coredns.io/manual/toc](https://coredns.io/manual/toc/)
- **CoreDNS plugins**: [coredns.io/plugins](https://coredns.io/plugins/)
- **Kubernetes DNS spec**: [kubernetes.io/docs/concepts/services-networking/dns-pod-service](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)

-----

*🔬 Who Are You CoreDNS? — a CSI-style investigation into Kubernetes DNS. The evidence is in the Corefile. The answers are in the logs.*
