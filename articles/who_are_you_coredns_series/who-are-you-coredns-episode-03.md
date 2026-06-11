---
title: "Who Are You CoreDNS? 🔬 Ep.3"
published: false
description: "Episode 3: Every DNS record type is a different kind of forensic evidence. An A record is a fingerprint — one IP, one identity. A CNAME is an alias — the suspect has an alias. A headless service has multiple identities. An ExternalName service claims to be someone it is not. The CSI lab examines every record type in the Kubernetes DNS catalog."
tags: [kubernetes, dns, coredns, networking]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/who-are-you-coredns-episode-03.png"
series: "Who Are You coreDNS?"
canonical_url: ""
organization: "the-software-s-journey"
part: 3
---

## Episode 3: Fingerprints and DNA

*🎵 Who are you? Who who, who who? 🎵*

-----

## “Every Record Tells a Story” 🧬

*The CSI lab. Morning. Sara Sidle stands at the analysis station, multiple DNS query captures displayed across the monitors.*

**SARA:** “DNA is unambiguous. A fingerprint is unambiguous. But a DNS record? A DNS record can say ‘I am this IP,’ or ‘I am actually this other name,’ or ‘I am twelve different IPs depending on who you ask.’ Identity in DNS is… complicated.”

*She pulls up the first case.*

**SARA:** “Let us start with the basics. The A record. The fingerprint of the internet.”

-----

## 🗂️ SIPOC — The Record Type Investigation

|**Suppliers**                       |**Inputs**                                                      |**Process**                                                                             |**Outputs**                                                      |**Customers**                                                     |
|------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------|-----------------------------------------------------------------|------------------------------------------------------------------|
|Kubernetes API                      |Service objects (ClusterIP, Headless, ExternalName), Pod objects|CoreDNS `kubernetes` plugin synthesises DNS records dynamically as cluster state changes|A, AAAA, CNAME, SRV, PTR records — each matching the service type|Pods querying the DNS — each record type encodes different meaning|
|ClusterIP Service                   |A single virtual IP assigned by Kubernetes                      |CoreDNS returns a single A record pointing to the ClusterIP                             |One IP — kube-proxy routes to actual pods                        |Client pods — they get one IP, kube-proxy load-balances behind it |
|Headless Service (`clusterIP: None`)|No ClusterIP — individual pod IPs directly                      |CoreDNS returns multiple A records, one per ready pod                                   |Multiple IPs — the client load-balances directly                 |Stateful sets, databases — clients need to choose a specific pod  |
|ExternalName Service                |A `spec.externalName` field pointing to an external hostname    |CoreDNS returns a CNAME pointing to the externalName value                              |A CNAME — not an IP                                              |Pods that need to reach external services with internal names     |

-----

## The A Record: The Fingerprint 🖐️

The A record is the most fundamental DNS record: **hostname → IPv4 address**.

In Kubernetes, every ClusterIP service gets an A record automatically:

```bash
# Query for an A record — the standard ClusterIP service
kubectl exec dns-investigator -n payments -- \
  dig A payment-service.payments.svc.cluster.local

# ;; QUESTION SECTION:
# ;payment-service.payments.svc.cluster.local.  IN A
#
# ;; ANSWER SECTION:
# payment-service.payments.svc.cluster.local. 30 IN A 10.100.42.88
#
# ;; Query time: 1 msec
# ;; SERVER: 10.96.0.10#53
```

**SARA:** “One IP. `10.100.42.88` — the ClusterIP. Behind this IP, there could be three pods, ten pods, or zero pods. The kube-proxy rules on every node translate this virtual IP to actual pod IPs. The DNS record never changes, even when pods scale up or down.”

|Field|Value                                        |Meaning                                  |
|-----|---------------------------------------------|-----------------------------------------|
|Name |`payment-service.payments.svc.cluster.local.`|Full service FQDN                        |
|TTL  |`30`                                         |Cache for 30 seconds — Kubernetes default|
|Class|`IN`                                         |Internet class                           |
|Type |`A`                                          |IPv4 address record                      |
|Value|`10.100.42.88`                               |The ClusterIP                            |

-----

## The AAAA Record: The Twin 👥

The AAAA record is A’s sibling — it maps a hostname to an **IPv6 address**. In dual-stack clusters, services get both A and AAAA records.

```bash
# Query for AAAA (IPv6) records
kubectl exec dns-investigator -- \
  dig AAAA payment-service.payments.svc.cluster.local

# In a single-stack IPv4 cluster:
# ;; ANSWER SECTION: (empty)
# ;; AUTHORITY SECTION:
# cluster.local. 30 IN SOA ns.dns.cluster.local. hostmaster.cluster.local. ...

# In a dual-stack cluster:
# ;; ANSWER SECTION:
# payment-service.payments.svc.cluster.local. 30 IN AAAA fd00::42:88
```

**WARRICK:** “The AAAA record is where many innocent DNS queries go to die in IPv4-only clusters. An application that queries both A and AAAA simultaneously — some do — gets a fast A response and a `NXDOMAIN` on AAAA. That NXDOMAIN can cause application-level errors if the resolver is not handled carefully.”

```bash
# Check: is your cluster dual-stack?
kubectl get nodes -o jsonpath='{.items[*].status.addresses}' | python3 -m json.tool

# Check AAAA queries that return NXDOMAIN in logs
kubectl logs -n kube-system -l k8s-app=kube-dns | grep "AAAA.*NXDOMAIN"
```

-----

## The CNAME Record: The Alias — “I’m Actually Someone Else” 🎭

A CNAME (Canonical Name) record says: “I am not who you asked for — I am actually this other name.” The resolver must then look up that other name.

In Kubernetes, CNAMEs arise in two places:

### ExternalName Services — The Identity Thief

```yaml
# An ExternalName service — the most common CNAME source
apiVersion: v1
kind: Service
metadata:
  name: legacy-db
  namespace: payments
spec:
  type: ExternalName
  externalName: db.legacy-system.corp.internal
  # No ports. No selectors. No ClusterIP.
  # Just a redirect.
```

```bash
# Query this service
kubectl exec dns-investigator -n payments -- \
  dig legacy-db.payments.svc.cluster.local

# ;; ANSWER SECTION:
# legacy-db.payments.svc.cluster.local. 30 IN CNAME db.legacy-system.corp.internal.
# db.legacy-system.corp.internal.  60 IN A 192.168.100.50
```

**GRISSOM:** “The ExternalName service is a legal alias. The pod asks for `legacy-db.payments.svc.cluster.local`. CoreDNS returns a CNAME pointing to `db.legacy-system.corp.internal`. The resolver then queries your corporate DNS for *that* name. Useful for migrating from external services to internal ones — you change the CNAME target without touching application code.”

**The ExternalName chain of custody:**

```
Pod asks: legacy-db.payments.svc.cluster.local
    ↓
CoreDNS (kubernetes plugin): CNAME → db.legacy-system.corp.internal
    ↓
CoreDNS (forward plugin): query forwarded to corporate nameserver
    ↓
Corporate nameserver: A → 192.168.100.50
    ↓
Pod receives: 192.168.100.50
```

**NICK:** “But what happens when the external name doesn’t resolve?”

**GRISSOM:** “The CNAME points nowhere. The pod gets NXDOMAIN on the final A lookup. The application sees a connection failure — and the CNAME in the response makes it look like a network issue, not a DNS issue. That is why ExternalName misconfigurations are so hard to debug.”

-----

## The SRV Record: The Full Identity — Address AND Port 🎯

The SRV (Service) record is the most information-dense DNS record type: it encodes **service name, protocol, priority, weight, port, and target hostname** in a single record.

Kubernetes synthesises SRV records for named ports on services:

```yaml
# A service with named ports — gets SRV records
apiVersion: v1
kind: Service
metadata:
  name: payment-api
  namespace: payments
spec:
  selector:
    app: payment-api
  ports:
  - name: http       # Named port — this generates an SRV record
    port: 8080
    protocol: TCP
  - name: grpc
    port: 50051
    protocol: TCP
```

```bash
# Query SRV records
kubectl exec dns-investigator -n payments -- \
  dig SRV _http._tcp.payment-api.payments.svc.cluster.local

# ;; ANSWER SECTION:
# _http._tcp.payment-api.payments.svc.cluster.local. 30 IN SRV 0 100 8080 payment-api.payments.svc.cluster.local.

# The SRV record format:
# priority=0  weight=100  port=8080  target=payment-api.payments.svc.cluster.local.
```

**SARA:** “The SRV record is a complete identity document: port, priority, weight, and hostname. Service mesh clients, gRPC load balancers, and Consul-aware applications use SRV records to discover services without hardcoding port numbers. It is the most complete fingerprint in the DNS evidence catalog.”

|SRV field  |Value                                                     |Meaning                                    |
|-----------|----------------------------------------------------------|-------------------------------------------|
|Name format|`_port-name._protocol.service.namespace.svc.cluster.local`|Fully identifies the endpoint type         |
|Priority   |`0`                                                       |Lower number = higher priority             |
|Weight     |`100`                                                     |Relative weight among same-priority records|
|Port       |`8080`                                                    |The actual TCP/UDP port to connect to      |
|Target     |`payment-api.payments.svc.cluster.local.`                 |The hostname to resolve next               |

-----

## The PTR Record: Reverse DNS — “Who Are You, Really?” 🔄

The PTR (Pointer) record answers the reverse question: given an **IP address**, who does it belong to?

```bash
# Reverse DNS lookup for a pod IP
# Pod IP: 10.244.1.42
# Reversed:  42.1.244.10.in-addr.arpa

kubectl exec dns-investigator -- \
  dig PTR 42.1.244.10.in-addr.arpa

# ;; ANSWER SECTION:
# 42.1.244.10.in-addr.arpa. 30 IN PTR 10-244-1-42.payments.pod.cluster.local.
```

**The CoreDNS `kubernetes` plugin handles PTR lookups for:**

- Pod IPs → `<ip-dashes>.<namespace>.pod.cluster.local`
- Service ClusterIPs → `<service>.<namespace>.svc.cluster.local`

```bash
# Reverse lookup for a service ClusterIP
# Service ClusterIP: 10.100.42.88
# Reversed: 88.42.100.10.in-addr.arpa

kubectl exec dns-investigator -- \
  dig PTR 88.42.100.10.in-addr.arpa

# ;; ANSWER SECTION:
# 88.42.100.10.in-addr.arpa. 30 IN PTR payment-service.payments.svc.cluster.local.
```

**CATHERINE:** “Reverse DNS is how security tools identify who is talking. A network monitoring system sees traffic from `10.244.1.42`. It does a PTR lookup. It gets back `10-244-1-42.payments.pod.cluster.local`. Now it knows: that traffic came from a pod in the `payments` namespace. Without PTR records, your network forensics are blind.”

-----

## The Headless Service: Multiple Identities — The Gang 👥

A headless service (`clusterIP: None`) is the most forensically interesting service type. Instead of a single virtual IP, it returns multiple A records — one per ready pod.

```yaml
# A headless service — no ClusterIP
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: payments
spec:
  clusterIP: None      # This is what makes it headless
  selector:
    app: postgres
  ports:
  - port: 5432
```

```bash
# Query the headless service
kubectl exec dns-investigator -n payments -- \
  dig A postgres.payments.svc.cluster.local

# ;; ANSWER SECTION:
# postgres.payments.svc.cluster.local. 30 IN A 10.244.1.10    ← postgres-0
# postgres.payments.svc.cluster.local. 30 IN A 10.244.1.11    ← postgres-1
# postgres.payments.svc.cluster.local. 30 IN A 10.244.1.12    ← postgres-2

# And individual pod DNS (StatefulSet pods get stable DNS):
kubectl exec dns-investigator -n payments -- \
  dig A postgres-0.postgres.payments.svc.cluster.local

# ;; ANSWER SECTION:
# postgres-0.postgres.payments.svc.cluster.local. 30 IN A 10.244.1.10
```

**NICK:** “Three A records for one name. The client has to pick one.”

**GRISSOM:** “That is the point. With a stateful system like a database cluster, the client — the application — needs to implement its own connection logic. It might connect to the primary, round-robin, or use the SRV records to understand which replica handles reads. The DNS layer returns all candidates and defers the choice to the application. The `loadbalance` plugin in CoreDNS randomises the order to distribute load.”

-----

## Pod DNS Records: The Individual Identity Card 🪪

When `pods insecure` is configured in the Corefile (the default), individual pod IPs get DNS records:

```bash
# Pod with IP 10.244.1.42 in namespace payments
kubectl exec dns-investigator -- \
  dig 10-244-1-42.payments.pod.cluster.local

# ;; ANSWER SECTION:
# 10-244-1-42.payments.pod.cluster.local. 30 IN A 10.244.1.42
```

The format: **pod-ip-with-dashes.namespace.pod.cluster.local**

**The `pods insecure` vs `pods verified` configuration:**

```
kubernetes cluster.local in-addr.arpa ip6.arpa {
    pods insecure    # Returns pod records without verifying the requestor
    # pods verified  # Only returns pod record if the requesting IP matches
    # pods disabled  # No pod records at all
}
```

**SARA:** “The `insecure` setting means anyone in the cluster can query pod DNS records for any pod, regardless of namespace. For most clusters, this is acceptable. For high-security environments, `verified` restricts pod record queries to only the pod itself.”

-----

## The DNS Record Reference: The Evidence Catalog 📚

```bash
# Complete DNS record investigation script
# Run inside a debug pod

SERVICE="payment-service"
NAMESPACE="payments"
DOMAIN="cluster.local"
FULL="${SERVICE}.${NAMESPACE}.svc.${DOMAIN}"

echo "=== A Records (IPv4) ==="
dig A ${FULL}

echo "=== AAAA Records (IPv6) ==="
dig AAAA ${FULL}

echo "=== SRV Records (named port discovery) ==="
dig SRV _http._tcp.${FULL}

echo "=== PTR Record (reverse DNS) ==="
CLUSTER_IP=$(kubectl get svc ${SERVICE} -n ${NAMESPACE} \
  -o jsonpath='{.spec.clusterIP}')
REVERSED=$(echo ${CLUSTER_IP} | awk -F. '{print $4"."$3"."$2"."$1".in-addr.arpa"}')
dig PTR ${REVERSED}

echo "=== SOA Record (zone authority) ==="
dig SOA ${DOMAIN}

# SOA output shows:
# cluster.local. 30 IN SOA ns.dns.cluster.local. \
#   hostmaster.cluster.local. 1640000000 7200 1800 86400 30
```

-----

## What’s Next: The CSI Lab 🔬

*Nick pins the record type evidence board to the wall.*

**NICK:** “We know the record types. We know the crime scene. Now we need to go deeper into the lab itself — the Corefile. Every plugin is a forensic instrument. Some are microscopes. Some are tape recorders. Some are the entire evidence chain.”

**GRISSOM:** “Episode 4. Every plugin. Every configuration option. The Corefile dissected.”

*The lab hums. A new DNS query arrives. The investigation continues.*

-----

**🔗 Resources**

- **DNS record types RFC**: [rfc-editor.org/rfc/rfc1035](https://www.rfc-editor.org/rfc/rfc1035)
- **Kubernetes service DNS**: [kubernetes.io/docs/concepts/services-networking/dns-pod-service](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- **Headless services**: [kubernetes.io/docs/concepts/services-networking/service/#headless-services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)

-----

*🔬 Who Are You CoreDNS? — a CSI-style investigation into Kubernetes DNS. The evidence is in the Corefile. The answers are in the logs.*
