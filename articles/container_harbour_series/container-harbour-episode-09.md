---
title: "Welcome to Container Harbour! 🚢 Ep.9"
part: 9
published: false
description: "Episode 9: The Long-Term Warehouse — Persistent Volumes and Storage. Your Pods die constantly. Your database refuses to. Somebody has to build the warehouse."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-09.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 9: The Long-Term Warehouse — Persistent Volumes and Storage 🏭

### The Database That Lost Its Mind When the Pod Restarted 😱

"My database keeps losing all its data every time I redeploy."

I have heard this sentence more times than I care to count. Always from someone with the same haunted look. The look of a person who has deployed PostgreSQL as a Deployment, watched it run perfectly for six hours, done a rolling update, and returned to find: empty tables. Fresh install. No data. Zero. Gone.

And they know. Somewhere deep inside, they KNOW what happened. They just don't want to say it.

The Pod restarted. The pod's filesystem was ephemeral. Everything that wasn't persisted — died with the Pod.

This is not a bug. This is by design. Pods are FREIGHT CONTAINERS. When the container leaves the harbour, the contents go with it. If you want something to STAY — you need a WAREHOUSE.

That's Persistent Volumes. Let's build the warehouse. 🏗️

---

## The SIPOC of Storage 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who provides the storage infrastructure? | Cloud provider (Azure Disk, AWS EBS), NFS server, storage admin |
| **Input** | What goes in? | A storage request (PVC) with size and access mode requirements |
| **Process** | What happens? | Kubernetes finds/provisions matching storage, binds it to the claim |
| **Output** | What comes out? | A mounted filesystem inside the Pod, persistent across restarts |
| **Consumer** | Who uses it? | Stateful Pods — databases, file storage, message queues |

---

## The Three Players: PV, PVC, StorageClass 🎭

```
🏭  WAREHOUSE SYSTEM:

StorageClass          PersistentVolume (PV)      PersistentVolumeClaim (PVC)
"What kind of         "The actual warehouse       "I need 10GB of warehouse
 warehouse is         unit. Physical storage.     space with fast access.
 available?"          Ready and waiting."         Who has it?"
      |                       |                          |
      |<-- defines type ----  |<-- satisfies claim ---->|
      |                       |                          |
      v                       v                          v
Azure Disk SSD          10GB Azure Disk          Your PostgreSQL Pod mounts it
```

You almost never create PVs manually anymore. You use **StorageClasses** to dynamically provision them. Like calling a warehouse company and saying "I need 10GB, fast disks" — and they build the warehouse for you on demand.

---

## PersistentVolumes: The Warehouse Unit 🏢

A PV represents a piece of real storage. In older setups, admins created these manually:

```yaml
# pv-manual.yaml (the old way -- rarely done manually now)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: manual-pv-10gi
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce           # One Pod can read+write at a time
  persistentVolumeReclaimPolicy: Retain   # Keep data when PVC is deleted
  storageClassName: manual
  hostPath:
    path: /data/warehouse   # On the node's filesystem (dev/testing only!)
```

Access modes — the warehouse's usage rules:

| AccessMode | Meaning | Use case |
|---|---|---|
| `ReadWriteOnce` (RWO) | One node, read+write | Databases (most common) |
| `ReadOnlyMany` (ROX) | Many nodes, read only | Static file serving |
| `ReadWriteMany` (RWX) | Many nodes, read+write | Shared file systems (NFS) |
| `ReadWriteOncePod` | ONE Pod, read+write | Strict single-writer guarantee |

---

## PersistentVolumeClaims: Requesting Warehouse Space 📋

A PVC is your REQUEST for storage. You say what you need, Kubernetes finds or creates it:

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-storage
  namespace: production
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi           # "I need 10GB"
  storageClassName: managed-premium   # "Fast Azure SSD please"
```

```bash
kubectl apply -f pvc.yaml

kubectl get pvc postgres-storage
# NAME               STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS
# postgres-storage   Bound    pvc-a1b2c3d4-e5f6-7890-abcd-ef1234567890   10Gi       RWO            managed-premium
# STATUS=Bound means Kubernetes found matching storage and it's ready!
```

---

## StorageClasses: The Warehouse Catalogue 📚

StorageClasses define TYPES of storage. They're how Kubernetes knows how to dynamically provision PVs:

```bash
# See available StorageClasses in your cluster
kubectl get storageclasses

# In AKS you might see:
# NAME                    PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE
# default                 disk.csi.azure.com         Delete          WaitForFirstConsumer
# managed-premium         disk.csi.azure.com         Delete          WaitForFirstConsumer
# azurefile               file.csi.azure.com         Delete          Immediate
# azurefile-premium       file.csi.azure.com         Delete          Immediate
```

```yaml
# Create a custom StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: disk.csi.azure.com
reclaimPolicy: Retain          # Keep disk when PVC deleted (important for prod data!)
volumeBindingMode: WaitForFirstConsumer   # Don't provision until Pod needs it
parameters:
  skuName: Premium_LRS         # Azure Premium SSD
  cachingmode: ReadOnly
allowVolumeExpansion: true     # Allow growing the disk later
```

---

## Using PVCs in Pods: Mounting the Warehouse 🔌

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: production
spec:
  replicas: 1           # Note: 1 replica! ReadWriteOnce can't be shared!
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
        env:
        - name: POSTGRES_DB
          value: "harbour_db"
        - name: POSTGRES_USER
          value: "harbourmaster"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data   # Where Postgres stores data

      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: postgres-storage           # Our PVC from above
```

```bash
kubectl apply -f postgres-deployment.yaml

# Write some data
kubectl exec -it postgres-abc123 -- psql -U harbourmaster -d harbour_db -c \
  "CREATE TABLE ships (name TEXT, cargo TEXT); INSERT INTO ships VALUES ('Rotterdam Express', 'Bananas');"

# Delete the Pod (simulate crash/restart)
kubectl delete pod postgres-abc123

# New Pod spins up automatically (Deployment ensures it)
kubectl get pods -l app=postgres --watch

# Connect to the NEW Pod
kubectl exec -it postgres-xyz789 -- psql -U harbourmaster -d harbour_db -c "SELECT * FROM ships;"
# name               | cargo
# Rotterdam Express  | Bananas
# DATA SURVIVED! 🎉 The warehouse kept the goods even when the container changed!
```

---

## Volume Types: What Kind of Warehouse? 🏗️

Different workloads need different storage types:

```yaml
spec:
  volumes:
  # 1. emptyDir: Temporary scratch space. Dies with the Pod.
  - name: temp-scratch
    emptyDir: {}

  # 2. hostPath: Use a path on the node's filesystem (dev only!)
  - name: node-logs
    hostPath:
      path: /var/log/harbour
      type: DirectoryOrCreate

  # 3. configMap and secret: We covered these in Episode 8!
  - name: app-config
    configMap:
      name: web-app-config

  # 4. persistentVolumeClaim: The real warehouse. What we want for stateful apps.
  - name: database-storage
    persistentVolumeClaim:
      claimName: postgres-storage

  # 5. projected: Combine multiple volume types into one mount
  - name: combined
    projected:
      sources:
      - configMap:
          name: app-config
      - secret:
          name: app-secrets
```

---

## Expanding Volumes: The Warehouse Needs More Space 📈

Your database grew. 10GB isn't enough. Time to expand:

```bash
# Only works if StorageClass has allowVolumeExpansion: true

# Edit the PVC and increase the storage request:
kubectl edit pvc postgres-storage
# Change: storage: 10Gi
# To:     storage: 50Gi

# Watch the expansion happen:
kubectl get pvc postgres-storage --watch
# NAME               STATUS   CAPACITY
# postgres-storage   Bound    10Gi        <- before
# postgres-storage   Bound    50Gi        <- after expansion (may take a minute)

# No downtime! The warehouse just got bigger while Postgres was running! 🎉
```

---

## The Reclaim Policy: What Happens When You're Done? 🗑️

When you delete a PVC, what happens to the underlying storage?

| ReclaimPolicy | What happens to the PV/disk? | Use when |
|---|---|---|
| `Delete` | PV and actual disk are deleted | Temporary data, dev environments |
| `Retain` | PV is kept but released, disk survives | Production data — you decide when to delete |
| `Recycle` | PV is scrubbed and made available again | Deprecated. Don't use. |

```yaml
# Production database: always Retain!
storageClassName: fast-ssd-retain

# The StorageClass:
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd-retain
provisioner: disk.csi.azure.com
reclaimPolicy: Retain       # KEEP THE DISK when PVC is deleted
parameters:
  skuName: Premium_LRS
```

---

## The Harbourmaster's Log — Entry 9 📋

*Fixed the mystery of the disappearing database today. Developer had been running PostgreSQL as a Deployment with no PVC. Every restart: fresh database. Six weeks of data. Gone.*

*I showed them Persistent Volumes. I watched realisation cross their face like sunrise.*

*"So the data... lives outside the container? In a separate warehouse?" they asked.*

*"Yes," I said.*

*"And when the container restarts, it reconnects to the same warehouse?"*

*"Yes."*

*"And the data is just... there?"*

*"Yes."*

*They sat quietly for a moment.*

*"I have been doing this wrong for six weeks," they said.*

*"Yes," I said, gently. "But now you know."* 🎩

---

## Your Mission 🎯

1. Create a PVC for 5Gi of storage
2. Deploy PostgreSQL (or any database) using that PVC
3. Insert some data
4. Delete the Pod
5. Wait for the replacement Pod to start
6. Query the data — it should still be there
7. **Bonus:** Expand the PVC from 5Gi to 10Gi without downtime

---

## Next Time 🎬

**Episode 10**: The Security Office — RBAC. Who gets a Harbourmaster badge? Who can only sweep the quay? Why Dave should definitely not have `cluster-admin`. 🪪

---

*P.S. — In 2019, a well-known startup accidentally deleted their entire production database, then discovered their backups were also corrupt. Their Kubernetes cluster had no PVCs — just emptyDir volumes. This is a real thing that happened. This is why we have PVCs. And backups. Always have backups.* 💾

---

**🎯 Key Takeaways:**

- Pods are ephemeral. Their filesystems die with them. **PVCs give you persistence.**
- **StorageClass** = warehouse type. **PV** = the actual warehouse. **PVC** = your reservation.
- Access modes: **RWO** (one node, one writer) for databases; **RWX** (many nodes) for shared files.
- Use `reclaimPolicy: Retain` for production databases — never `Delete`!
- `allowVolumeExpansion: true` lets you grow volumes without downtime.
- `emptyDir` = scratch space that dies with the Pod. For temp files only.
- Always use PVCs for databases. Always. No exceptions. Not even for "just testing." 🔒
