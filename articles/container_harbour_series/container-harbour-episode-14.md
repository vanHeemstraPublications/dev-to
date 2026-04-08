---
title: "Welcome to Container Harbour! 🚢 Ep.14"
part: 14
published: false
description: "Episode 14: Reserved Berths for Divas — StatefulSets. Databases need the same berth, the same name, the same storage, every single time. High maintenance? Absolutely. Worth it? Ask your data."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-14.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 14: Reserved Berths for Divas — StatefulSets 🎭

### The Database That Would NOT Behave Like a Normal Deployment 😤

We were young. We were naive. We thought: "It's just another container. Deploy it as a Deployment. It'll be fine."

We deployed PostgreSQL as a Deployment with 3 replicas.

What we got was three separate PostgreSQL instances, each with their own data, none of them aware the others existed, all happily accepting writes, none of them replicating anything.

Users were writing to replica 1. Reading from replica 2. Seeing different data. Going insane. Filing bug reports. Questioning reality.

It was not fine.

Databases are not stateless web servers. They are DIVAS. They need their own reserved berth, their own storage, their own persistent identity, and they need to start up in the RIGHT ORDER.

StatefulSets give them exactly that. 🎭

---

## The SIPOC of StatefulSets 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who manages the StatefulSet? | The StatefulSet controller in the Controller Manager |
| **Input** | What goes in? | StatefulSet spec with ordinal naming, volumeClaimTemplates, headless Service |
| **Process** | What happens? | Pods created in order (0, 1, 2...), each gets stable identity + dedicated storage |
| **Output** | What comes out? | Stable, individually addressable Pods with persistent storage |
| **Consumer** | Who uses it? | Databases, message queues, distributed systems that need identity |

---

## StatefulSet vs Deployment: The Core Difference 🔄

```
DEPLOYMENT:                          STATEFULSET:
                                     
web-app-abc123   (Pod 1)             postgres-0   (Pod 0)
web-app-def456   (Pod 2)             postgres-1   (Pod 1)
web-app-ghi789   (Pod 3)             postgres-2   (Pod 2)

- Random names ✗                     - Ordered names (0,1,2...) ✓
- Random scheduling ✗                - Stable network identity ✓
- Shared or no storage ✗             - Each gets own dedicated PVC ✓
- Start/stop in any order ✗          - Start in order, stop in reverse ✓
- Replaceable, anonymous ✓           - Each Pod has a persistent identity ✓
```

The StatefulSet guarantees:
1. **Stable Pod names**: `postgres-0`, `postgres-1`, `postgres-2`
2. **Stable DNS names**: `postgres-0.postgres.production.svc.cluster.local`
3. **Dedicated storage**: `postgres-0` always gets `data-postgres-0` PVC
4. **Ordered operations**: Pods start in order 0→1→2, scale down in reverse 2→1→0

---

## A Minimal StatefulSet: Three-Node PostgreSQL 🐘

First, the **headless Service** — required for stable DNS names:

```yaml
# headless-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres            # This name becomes part of the DNS
  namespace: production
spec:
  clusterIP: None           # "None" = headless! No virtual IP.
  selector:
    app: postgres
  ports:
  - port: 5432
    name: postgres
```

Now the StatefulSet:

```yaml
# postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: production
spec:
  serviceName: postgres       # Must match the headless Service name!
  replicas: 3
  selector:
    matchLabels:
      app: postgres

  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
          name: postgres

        env:
        - name: POSTGRES_DB
          value: "harbour_db"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name    # Inject "postgres-0", "postgres-1", etc.
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: POSTGRES_PASSWORD

        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data

  # THIS is the magic: each Pod gets its OWN PVC!
  volumeClaimTemplates:
  - metadata:
      name: data                 # Creates PVCs named: data-postgres-0, data-postgres-1, data-postgres-2
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: managed-premium
      resources:
        requests:
          storage: 20Gi
```

```bash
kubectl apply -f headless-service.yaml
kubectl apply -f postgres-statefulset.yaml

# Watch Pods start IN ORDER:
kubectl get pods -l app=postgres --watch
# NAME         READY   STATUS    RESTARTS
# postgres-0   0/1     Pending   0          <- 0 first
# postgres-0   1/1     Running   0          <- 0 ready before 1 starts
# postgres-1   0/1     Pending   0          <- 1 starts after 0 is ready
# postgres-1   1/1     Running   0
# postgres-2   0/1     Pending   0          <- 2 starts after 1 is ready
# postgres-2   1/1     Running   0

# See the individual PVCs created for each Pod:
kubectl get pvc -n production
# NAME              STATUS   VOLUME                  CAPACITY
# data-postgres-0   Bound    pvc-abc123...           20Gi    <- postgres-0's private storage
# data-postgres-1   Bound    pvc-def456...           20Gi    <- postgres-1's private storage
# data-postgres-2   Bound    pvc-ghi789...           20Gi    <- postgres-2's private storage
```

---

## Stable DNS: Addressing Individual Pods 📞

With a headless Service and a StatefulSet, EACH Pod gets a stable DNS name:

```
Pattern: <pod-name>.<service-name>.<namespace>.svc.cluster.local

postgres-0.postgres.production.svc.cluster.local   -> postgres-0's IP (ALWAYS)
postgres-1.postgres.production.svc.cluster.local   -> postgres-1's IP (ALWAYS)
postgres-2.postgres.production.svc.cluster.local   -> postgres-2's IP (ALWAYS)
```

```bash
# From inside the cluster, prove it works:
kubectl run dns-test --image=busybox --rm -it --restart=Never -- sh

# Inside the pod:
nslookup postgres-0.postgres.production.svc.cluster.local
# Address: 10.244.1.5   <- Always this Pod's IP, regardless of restarts

nslookup postgres.production.svc.cluster.local
# Address: 10.244.1.5   <- All Pod IPs returned
# Address: 10.244.2.3
# Address: 10.244.3.7
```

If `postgres-1` is killed and recreated, it comes back as `postgres-1` at the SAME DNS name with the SAME storage. The identity survives the death of the Pod. ♻️

---

## Scaling StatefulSets: Ordered and Careful 📈

```bash
# Scale up (adds postgres-3 after postgres-2 is healthy)
kubectl scale statefulset postgres --replicas=4

# Scale DOWN (removes postgres-3 FIRST, then postgres-2, etc.)
kubectl scale statefulset postgres --replicas=2

# WHY ordered scale-down? Databases! The newest replicas are typically
# the ones with least data, and removing them first is safest.

# Watch ordered scale-down:
kubectl get pods -l app=postgres --watch
# postgres-0   1/1   Running    # stays
# postgres-1   1/1   Running    # stays
# postgres-2   1/1   Running    # last in, first out
# postgres-2   1/1   Terminating
# (postgres-2 gone)
# postgres-1   1/1   Running    # still here (we only went to 2 replicas)
```

---

## Update Strategies for StatefulSets 🔄

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2    # Only update Pods with ordinal >= 2 (canary strategy!)
```

```bash
# Canary update: only update the highest ordinal Pods first
# Set partition=2: only postgres-2 gets the new version
kubectl patch statefulset postgres -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":2}}}}'
kubectl set image statefulset/postgres postgres=postgres:16

# postgres-2 gets postgres:16. postgres-0 and postgres-1 stay on postgres:15.
# Test on postgres-2. Happy? Lower the partition.
kubectl patch statefulset postgres -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":0}}}}'
# Now all Pods update in reverse order: 1, then 0.
```

---

## StatefulSet Lifecycle: What Happens When a Pod Dies 💀

```bash
# Delete postgres-1 (simulate crash)
kubectl delete pod postgres-1

# Watch what happens:
kubectl get pods -l app=postgres --watch
# postgres-1   1/1   Terminating
# postgres-1   0/1   Pending       <- NEW postgres-1 starting (same name!)
# postgres-1   1/1   Running       <- Back, same identity

# The new postgres-1:
# - Has the SAME name: postgres-1
# - Has the SAME DNS: postgres-1.postgres.production.svc.cluster.local
# - Has the SAME storage: data-postgres-1 PVC
# - Is on potentially DIFFERENT node (Kubernetes chooses)

# What did NOT survive:
# - In-memory state (obviously)
# - Anything not in /var/lib/postgresql/data
```

---

## Real World: Cassandra Cluster with StatefulSet 🏗️

StatefulSets shine with distributed databases like Cassandra, where each node needs to know the identity of the seed nodes:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cassandra
spec:
  serviceName: cassandra
  replicas: 3
  selector:
    matchLabels:
      app: cassandra
  template:
    metadata:
      labels:
        app: cassandra
    spec:
      containers:
      - name: cassandra
        image: cassandra:4.1
        ports:
        - containerPort: 9042
          name: cql
        - containerPort: 7000
          name: intra-node
        env:
        - name: CASSANDRA_SEEDS
          # Seeds are the stable DNS names of the first two nodes
          value: "cassandra-0.cassandra.default.svc.cluster.local,cassandra-1.cassandra.default.svc.cluster.local"
        - name: CASSANDRA_CLUSTER_NAME
          value: "HarbourCluster"
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        volumeMounts:
        - name: cassandra-data
          mountPath: /var/lib/cassandra/data
  volumeClaimTemplates:
  - metadata:
      name: cassandra-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: managed-premium
      resources:
        requests:
          storage: 50Gi
```

Cassandra nodes know each other by stable DNS names. When node `cassandra-0` dies and comes back, it rejoins the cluster at the same address. The cluster gossip protocol reconnects it. No manual intervention. 🎯

---

## When to Use StatefulSets vs Deployments 🤔

```
Use DEPLOYMENT for:                  Use STATEFULSET for:
- Web servers                        - Relational databases (PostgreSQL, MySQL)
- API services                       - NoSQL databases (MongoDB, Cassandra, Redis)
- Stateless microservices            - Message queues (Kafka, RabbitMQ)
- Background workers (no storage)    - Distributed coordination (ZooKeeper, etcd)
- Batch processors                   - Any app needing stable network identity
- Anything that doesn't need         - Any app needing per-instance storage
  individual identity
```

When in doubt: if your app keeps data that matters, and it talks to other instances of itself — use StatefulSet. If it's just serving HTTP and doesn't care where it runs — use Deployment. 🎯

---

## The Harbourmaster's Log — Entry 14 📋

*The database team wanted to run a 3-node PostgreSQL cluster. "Just use a Deployment," someone said.*

*I did not say that. I knew better by now.*

*We deployed it as a StatefulSet. postgres-0 started first and became the primary. postgres-1 and postgres-2 started in order and became replicas, connecting to postgres-0 via its stable DNS name.*

*Six weeks later, postgres-1's node failed. The Pod was evicted. A new postgres-1 started on a different node. It reconnected to its persistent volume. It rejoined the replication stream. It caught up. It was ready in four minutes.*

*The database team didn't notice. The monitoring team sent a "Resolved" notification.*

*The users noticed nothing.*

*Databases as divas: confirmed. Worth the reserved berth: absolutely.* 🎩

---

## Your Mission 🎯

1. Deploy a 3-node StatefulSet using `nginx` (for simplicity):

```yaml
volumeClaimTemplates:
- metadata:
    name: webroot
  spec:
    accessModes: ["ReadWriteOnce"]
    resources:
      requests:
        storage: 1Gi
```

2. Exec into `nginx-0` and write a unique file to `/usr/share/nginx/html/`:
```bash
kubectl exec -it nginx-0 -- sh -c 'echo "I am nginx-0" > /usr/share/nginx/html/id.txt'
kubectl exec -it nginx-1 -- sh -c 'echo "I am nginx-1" > /usr/share/nginx/html/id.txt'
```

3. Delete `nginx-0`

4. Wait for it to come back

5. Exec into the new `nginx-0` and read `id.txt` — the file should still be there!

6. **Bonus:** Verify that deleting `nginx-0` does NOT delete the PVC `webroot-nginx-0`. The data survives.

---

## Next Time 🎬

**Episode 15**: Leaving Harbour Gracefully — **Rolling Updates and Zero Downtime Deployments**. The grand finale. Ships don't all leave at once. Neither do your Pods. 🌅

---

**🎯 Key Takeaways:**

- StatefulSets give Pods **stable identities**: stable names, stable DNS, stable storage.
- Each Pod gets its **own PVC** via `volumeClaimTemplates`. Shared storage is NOT what you want.
- Pods start **in order** (0→1→2) and stop **in reverse** (2→1→0). This is intentional.
- A **headless Service** (`clusterIP: None`) is required to enable per-Pod DNS names.
- `pod-name.service-name.namespace.svc.cluster.local` = the stable DNS pattern.
- Deleting a Pod from a StatefulSet creates a replacement with the **same name, same storage**.
- `partition` in updateStrategy enables canary rollouts for StatefulSets.
- Use StatefulSets for: databases, message queues, distributed coordination systems. Nothing else. 🗄️
