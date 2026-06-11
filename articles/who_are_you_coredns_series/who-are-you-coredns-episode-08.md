---
title: "Who Are You CoreDNS? 🔬 Ep.8"
published: false
description: "Episode 8: The finale. Every investigation leads here — a hardened, observable, highly-available CoreDNS deployment that can withstand the scale and chaos of production Kubernetes. RBAC locked down. Resource limits calibrated. Pod anti-affinity across nodes. NodeLocal DNSCache deployed. Multi-cluster DNS federation configured. The case is closed. The lab is secured."
tags: [kubernetes, coredns, production, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/who-are-you-coredns-episode-08.png"
series: "Who Are You coreDNS?"
canonical_url: ""
organization: "the-software-s-journey"
part: 8
---

## Episode 8: Case Closed

*🎵 Who are you? Who who, who who? 🎵*

-----

## “The Lab Protects the Whole City” 🏙️

*The final briefing. All four investigators around the conference table. A city-wide infrastructure diagram covers the wall: 500 nodes, 10,000 pods, three availability zones, two clusters.*

**GRISSOM:** “Every investigation we have conducted — the cold cases, the undercover operations, the forensic analysis of ndots and cache stampedes — all of it was reactive. We waited for the crime to happen and then processed the scene.”

*He stands.*

**GRISSOM:** “Production infrastructure does not have the luxury of being reactive. If CoreDNS goes down, every pod in the cluster loses service discovery. Every application stops working. Not some applications — every application. The entire city.”

*He turns to face the team.*

**GRISSOM:** “Episode 8 is not an investigation. Episode 8 is prevention. We harden the lab. We harden the deployment. We deploy the distributed evidence archives. We configure multi-cluster federation. And when we are done, the DNS infrastructure is resilient enough that the next incident is ‘some pods experienced a brief latency increase’ rather than ‘total cluster service discovery failure.’”

*The team opens their laptops.*

*The final case begins.*

-----

## 🗂️ SIPOC — The Production Hardening Operation

|**Suppliers**           |**Inputs**                                                    |**Process**                                                                 |**Outputs**                                                        |**Customers**                                                                |
|------------------------|--------------------------------------------------------------|----------------------------------------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------|
|CoreDNS Deployment      |Default deployment with minimal hardening                     |Apply: resource limits, anti-affinity, PodDisruptionBudget, security context|A deployment that tolerates node failures without DNS outage       |Every pod in the cluster — which never experiences DNS downtime              |
|RBAC configuration      |Default ClusterRole with broad permissions                    |Audit and tighten: remove unnecessary verbs, add namespace restrictions     |Least-privilege CoreDNS with only the permissions it actually needs|The cluster — which is safer when CoreDNS cannot escalate its own permissions|
|NodeLocal DNSCache      |The need for sub-millisecond DNS and conntrack race mitigation|Deploy DaemonSet on every node, configure link-local IP                     |Per-node DNS cache that eliminates network hops and conntrack races|All pods — which get faster DNS and fewer random timeouts                    |
|Multi-cluster federation|Multiple clusters needing to discover each other’s services   |Configure CoreDNS stub zones pointing to the other cluster’s DNS service    |Cross-cluster service discovery via DNS                            |Services that span multiple clusters                                         |

-----

## Part 1: Resource Limits — The Lab’s Budget 💰

The most common cause of CoreDNS production failures: resource starvation. CoreDNS is the DNS server for every pod, every service, every node name lookup in the cluster. It processes tens of thousands of queries per second in large clusters. It needs adequate resources.

**Calibrating the limits:**

```yaml
# Observed resource usage at different scales:
# Small cluster (10 nodes, 500 pods):   CPU ~50m, Memory ~70Mi
# Medium cluster (50 nodes, 2000 pods): CPU ~150m, Memory ~120Mi
# Large cluster (200 nodes, 10k pods):  CPU ~500m, Memory ~250Mi

# Production-calibrated resource configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coredns
  namespace: kube-system
spec:
  replicas: 3          # Minimum 2 for HA, 3 for maintenance safety
  template:
    spec:
      containers:
      - name: coredns
        image: registry.k8s.io/coredns/coredns:v1.11.3
        resources:
          requests:
            cpu: 100m         # Guaranteed CPU — should be your p90 usage
            memory: 70Mi      # Guaranteed memory
          limits:
            cpu: 1000m        # Allow burst to 1 CPU during thundering herds
            memory: 170Mi     # Prevent OOM — but do not set too tight
            # If OOMKilled: the pod restarts and the cluster loses one
            # DNS replica. Set limit at 2-3x your typical memory usage.
```

**CATHERINE:** “The memory limit is the critical one. If CoreDNS is OOMKilled, it restarts. During restart, it processes no queries. If both replicas OOM simultaneously — which happens when both encounter the same thundering herd — you have a full DNS outage. The limit should be your observed peak plus a 50% safety margin, not your average usage.”

-----

## Part 2: Pod Anti-Affinity — Not All Investigators in the Same Car 🚗

By default, Kubernetes may schedule both CoreDNS pods on the same node. If that node fails, both replicas go down simultaneously.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coredns
  namespace: kube-system
spec:
  replicas: 3
  template:
    spec:
      affinity:
        podAntiAffinity:
          # Hard anti-affinity: NEVER put two CoreDNS pods on the same node
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: k8s-app
                operator: In
                values:
                - kube-dns
            topologyKey: kubernetes.io/hostname

          # Preferred: also spread across availability zones
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: k8s-app
                  operator: In
                  values:
                  - kube-dns
              topologyKey: topology.kubernetes.io/zone
```

-----

## Part 3: PodDisruptionBudget — Maintenance Without Blackout 🛡️

```yaml
# Guarantee at least 1 CoreDNS replica during voluntary disruptions
# (node drains, cluster upgrades)
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: coredns-pdb
  namespace: kube-system
spec:
  minAvailable: 1      # At least 1 must remain running
  selector:
    matchLabels:
      k8s-app: kube-dns
```

**NICK:** “Without the PDB, a cluster upgrade that drains nodes simultaneously could evict all CoreDNS pods at once. With `minAvailable: 1`, the drain process is blocked until the eviction can complete without violating the budget. One DNS replica always remains running.”

-----

## Part 4: Security Context — The Lab’s Security Protocol 🔐

```yaml
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: coredns
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            add:
            - NET_BIND_SERVICE    # Required to bind port 53 (below 1024)
            drop:
            - ALL                 # Drop everything else
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          runAsGroup: 1000
```

-----

## Part 5: RBAC — Least Privilege for the Lab 🔑

The default CoreDNS ClusterRole is already minimal, but review it:

```yaml
# What CoreDNS actually needs — and nothing more
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: system:coredns
rules:
# Watch services and endpoints to build DNS records
- apiGroups: [""]
  resources:
  - endpoints
  - services
  - pods
  - namespaces
  verbs: ["list", "watch"]

# EndpointSlices API (preferred over Endpoints in modern clusters)
- apiGroups: ["discovery.k8s.io"]
  resources: ["endpointslices"]
  verbs: ["list", "watch"]

# NOT needed and should NOT be present:
# - configmaps (CoreDNS reads its own ConfigMap via file, not API)
# - secrets (CoreDNS does not need secrets)
# - deployments/pods (create/update/delete)
# - Any write operations
```

-----

## Part 6: Complete NodeLocal DNSCache Deployment 🏃

```yaml
# DaemonSet for NodeLocal DNSCache
# Reference: https://github.com/kubernetes/kubernetes/tree/master/cluster/addons/dns/nodelocaldns

apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-local-dns
  namespace: kube-system
  labels:
    k8s-app: node-local-dns
spec:
  selector:
    matchLabels:
      k8s-app: node-local-dns
  template:
    metadata:
      labels:
        k8s-app: node-local-dns
    spec:
      priorityClassName: system-node-critical
      hostNetwork: true      # Required for link-local IP binding
      dnsPolicy: Default     # Use node DNS, not cluster DNS (avoids loop)
      tolerations:
      - key: "CriticalAddonsOnly"
        operator: "Exists"
      - effect: "NoSchedule"
        operator: "Exists"
      - effect: "NoExecute"
        operator: "Exists"
      containers:
      - name: node-cache
        image: registry.k8s.io/dns/k8s-dns-node-cache:1.23.0
        resources:
          requests:
            cpu: 25m
            memory: 5Mi
          limits:
            memory: 30Mi
        args:
        - -localip
        - "169.254.20.10"          # Link-local address — node-local DNS IP
        - -conf
        - /etc/Corefile
        - -upstreamsvc
        - "kube-dns"               # Upstream CoreDNS service name
        securityContext:
          privileged: true         # Required to bind link-local address
        ports:
        - containerPort: 53
          name: dns
          protocol: UDP
        - containerPort: 53
          name: dns-tcp
          protocol: TCP
        - containerPort: 9253
          name: metrics
          protocol: TCP
        livenessProbe:
          httpGet:
            host: 169.254.20.10
            path: /health
            port: 8080
          initialDelaySeconds: 60
          timeoutSeconds: 5
        volumeMounts:
        - mountPath: /run/xtables.lock
          name: xtables-lock
          readOnly: false
        - name: config-volume
          mountPath: /etc/coredns
        - name: kube-dns-config
          mountPath: /etc/kube-dns
      volumes:
      - name: xtables-lock
        hostPath:
          path: /run/xtables.lock
          type: FileOrCreate
      - name: kube-dns-config
        configMap:
          name: kube-dns
          optional: true
      - name: config-volume
        configMap:
          name: node-local-dns
```

**Verify NodeLocal DNSCache is working:**

```bash
# Check that pods are now using 169.254.20.10 as nameserver
kubectl exec -n default any-pod -- cat /etc/resolv.conf
# nameserver 169.254.20.10   ← node-local cache
# (This IP is set by kubelet when NodeLocal DNSCache is active)

# Check cache metrics per node
kubectl exec -n kube-system \
  $(kubectl get pod -n kube-system -l k8s-app=node-local-dns \
    -o name | head -1) \
  -- wget -qO- http://169.254.20.10:9253/metrics \
  | grep coredns_cache
```

-----

## Part 7: Multi-Cluster DNS Federation 🌐

**SARA:** “Two clusters need to discover each other. Cluster A has the payment processing service. Cluster B has the order management system. The order service needs to call payment service by DNS name.”

```
Cluster A:
  payment-service.payments.svc.cluster.local → 10.100.42.88
  CoreDNS service: 10.0.1.10 (exposed via LoadBalancer or NodePort)

Cluster B:
  orders-service.orders.svc.cluster.local → 10.200.15.3
  CoreDNS service: 10.0.2.10
```

**Configure stub zones in each cluster’s Corefile:**

```
# Cluster B's Corefile — add stub zone for Cluster A
cluster-a.local:53 {
    errors
    forward . 10.0.1.10   # Cluster A's CoreDNS LoadBalancer IP
    cache 30
}

# Cluster A's Corefile — add stub zone for Cluster B
cluster-b.local:53 {
    errors
    forward . 10.0.2.10   # Cluster B's CoreDNS LoadBalancer IP
    cache 30
}
```

**Expose CoreDNS for cross-cluster access:**

```yaml
# In Cluster A: expose CoreDNS for Cluster B to query
apiVersion: v1
kind: Service
metadata:
  name: coredns-external
  namespace: kube-system
spec:
  type: LoadBalancer          # Or NodePort if no LB available
  selector:
    k8s-app: kube-dns
  ports:
  - name: dns-udp
    port: 53
    protocol: UDP
  - name: dns-tcp
    port: 53
    protocol: TCP
```

**Now services can be reached across clusters:**

```bash
# From a pod in Cluster B:
dig payment-service.payments.svc.cluster-a.local

# Cluster B's CoreDNS:
#   .:53 matches first → kubernetes plugin: not cluster-b.local → fallthrough
#   cluster-a.local:53 stub zone → forward to Cluster A's CoreDNS
# Cluster A's CoreDNS:
#   kubernetes plugin: payment-service in payments namespace → 10.100.42.88
# Response: 10.100.42.88
```

-----

## Part 8: The Complete Production Deployment Manifest 📋

```yaml
# Complete production CoreDNS deployment
# Apply after backing up your current coredns ConfigMap

apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
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
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coredns
  namespace: kube-system
  labels:
    k8s-app: kube-dns
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      k8s-app: kube-dns
  template:
    metadata:
      labels:
        k8s-app: kube-dns
    spec:
      serviceAccountName: coredns
      priorityClassName: system-cluster-critical
      tolerations:
      - key: "CriticalAddonsOnly"
        operator: "Exists"
      - key: "node-role.kubernetes.io/control-plane"
        effect: NoSchedule
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: k8s-app
                operator: In
                values: [kube-dns]
            topologyKey: kubernetes.io/hostname
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: k8s-app
                  operator: In
                  values: [kube-dns]
              topologyKey: topology.kubernetes.io/zone
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: coredns
        image: registry.k8s.io/coredns/coredns:v1.11.3
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            cpu: 100m
            memory: 70Mi
          limits:
            cpu: 1000m
            memory: 170Mi
        args: ["-conf", "/etc/coredns/Corefile"]
        volumeMounts:
        - name: config-volume
          mountPath: /etc/coredns
          readOnly: true
        ports:
        - containerPort: 53
          name: dns
          protocol: UDP
        - containerPort: 53
          name: dns-tcp
          protocol: TCP
        - containerPort: 9153
          name: metrics
          protocol: TCP
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
            scheme: HTTP
          initialDelaySeconds: 60
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 8181
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            add: [NET_BIND_SERVICE]
            drop: [ALL]
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
      volumes:
      - name: config-volume
        configMap:
          name: coredns
          items:
          - key: Corefile
            path: Corefile
      dnsPolicy: Default
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: coredns-pdb
  namespace: kube-system
spec:
  minAvailable: 1
  selector:
    matchLabels:
      k8s-app: kube-dns
```

-----

## The Post-Hardening Verification 🔬

```bash
# Verify all replicas are running and on different nodes
kubectl get pods -n kube-system -l k8s-app=kube-dns \
  -o wide --sort-by='{.spec.nodeName}'

# NAME                       READY   NODE       
# coredns-xxx-aaa            1/1     node-1     ← Different nodes ✓
# coredns-xxx-bbb            1/1     node-2
# coredns-xxx-ccc            1/1     node-3

# Verify PDB is active
kubectl get pdb coredns-pdb -n kube-system
# NAME          MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS
# coredns-pdb   1               N/A               2

# Verify health endpoints
kubectl exec -n kube-system coredns-xxx-aaa -- \
  wget -qO- http://localhost:8080/health
# OK

kubectl exec -n kube-system coredns-xxx-aaa -- \
  wget -qO- http://localhost:8181/ready
# OK

# Run the full diagnostic
dig @10.96.0.10 kubernetes.default.svc.cluster.local
dig @10.96.0.10 google.com
dig @10.96.0.10 kubernetes.default.svc.cluster.local +short | grep -q "10\." \
  && echo "Cluster DNS: PASS" || echo "Cluster DNS: FAIL"
```

-----

## Series Summary: Eight Cases, One Lab 🏁

*Gil Grissom stands in the empty lab at the end of shift. The monitors show green metrics. Query rates nominal. Cache hit rate 87%. Error rate 0.01%. P99 latency 2ms.*

**GRISSOM:** “Eight episodes. Eight case files.”

He traces the evidence board with one finger.

**GRISSOM:** “Episode 1: We learned who CoreDNS is. A plugin chain. A Corefile. A lab that never closes. Episode 2: We processed the first crime scene — `/etc/resolv.conf` with `ndots:5`. The quiet killer. Episode 3: We catalogued the evidence types — A records, AAAA, CNAME, SRV, PTR. Every record a different kind of identity.”

*He turns.*

**GRISSOM:** “Episode 4: Every instrument in the lab — `errors`, `log`, `health`, `ready`, `kubernetes`, `forward`, `cache`, `loop`, `reload`, `loadbalance`. Episode 5: The forensic database — cache mechanics, TTL expiry, cache stampedes, Prometheus metrics, NodeLocal DNSCache. Episode 6: Cold cases — twelve failure patterns, one investigation methodology.”

*A pause.*

**GRISSOM:** “Episode 7: Undercover operations. Rewrite, template, stub zones, split-horizon. Making DNS say what you need it to say. And Episode 8 — this episode. Production hardening. Because the best crime is the one that never happens.”

*He picks up his kit.*

**GRISSOM:** “DNS is infrastructure. Like electricity or running water — invisible when working, catastrophic when not. CoreDNS is the lab that keeps it working. The Corefile is the case file. The logs are the evidence. And the investigation — the investigation never really ends.”

*He walks out.*

*The lab hums.*

*Somewhere in the cluster, a pod queries `payment-service.production.svc.cluster.local`.*

*CoreDNS answers in 0.8 milliseconds.*

*The case is closed.*

*🎵 Who are you? Who who, who who? 🎵*

-----

**🔗 Resources**

- **CoreDNS production deployment**: [coredns.io/manual/toc](https://coredns.io/manual/toc/)
- **NodeLocal DNSCache**: [kubernetes.io/docs/tasks/administer-cluster/nodelocaldns](https://kubernetes.io/docs/tasks/administer-cluster/nodelocaldns/)
- **Kubernetes DNS best practices**: [kubernetes.io/docs/concepts/services-networking/dns-pod-service](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- **CoreDNS GitHub**: [github.com/coredns/coredns](https://github.com/coredns/coredns)

-----

*🔬 Who Are You CoreDNS? — eight cases, one lab, zero unsolved DNS mysteries. The investigation is complete.*
