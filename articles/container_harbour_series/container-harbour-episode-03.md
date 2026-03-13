---
title: "Welcome to Container Harbour! 🚢 Ep.3"
published: false
description: "Episode 3: The Dockyard Blueprint — Nodes and the Cluster. The quays, the cranes, the management tower, and what happens when a whole section falls into the sea."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-03.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: The Dockyard Blueprint — Nodes and the Cluster 🏗️

### The Moment I Realised I Had NO IDEA Where My App Was Running 😂

True story. I had a Kubernetes cluster. My app was running. Users were happy. Life was good.

Then my manager walked over and said: "Which server is your app on?"

And I just... stood there. With my mouth open. Like a fish. A very confused, very employed fish.

Because here's the thing about Kubernetes — IT DECIDES where your app runs. Not you. Not your manager. Not Dave. **Kubernetes.** And the crazy part? That's not a bug. That's THE WHOLE POINT.

Let me show you the dockyard blueprint and explain why this is actually GENIUS. 🧠

---

## The SIPOC of the Cluster 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who defines the infrastructure? | Cloud provider / on-prem team / you with `kind` |
| **Input** | What goes into the cluster? | Nodes (servers) with CPU, memory, storage |
| **Process** | What does the cluster do? | Receives Pods, schedules them onto nodes, monitors health |
| **Output** | What comes out? | Running workloads distributed across healthy nodes |
| **Consumer** | Who benefits? | Your applications — and the users hammering F5 on your website |

---

## The Dockyard: A Cluster Is the Whole Thing 🌊

A **cluster** is your entire harbour complex. Everything. The water, the quays, the cranes, the management tower, the security gates, the warehouses — ALL of it.

Inside a cluster, you have two types of things:

1. **The Control Plane** — the management tower (Episode 4 goes deep here)
2. **The Worker Nodes** — the actual quays where containers are stacked

```
🏗️  KUBERNETES CLUSTER (The Whole Harbour)
│
├── 🏢  Control Plane (Harbourmaster's Tower)
│       Manages EVERYTHING. Makes all decisions.
│       API Server, Scheduler, etcd, Controller Manager
│
├── 🚢  Worker Node 1 (North Quay)
│       ├── 📦 Pod: web-app
│       ├── 📦 Pod: cache
│       └── 📦 Pod: worker-job
│
├── 🚢  Worker Node 2 (East Quay)
│       ├── 📦 Pod: web-app (another copy!)
│       ├── 📦 Pod: database
│       └── 📦 Pod: api-service
│
└── 🚢  Worker Node 3 (South Quay)
        ├── 📦 Pod: web-app (yet ANOTHER copy!)
        └── 📦 Pod: monitoring
```

Notice that `web-app` is running on THREE nodes. Redundancy. Resilience. If one quay floods — the other two keep working and nobody even notices. 💪

---

## Worker Nodes: The Quays Where Pods Live 🏗️

A **worker node** is just a server. A computer. It could be:
- A VM in Azure, AWS, or GCP ☁️
- A physical server in your data centre 🖥️
- Your laptop running `kind` or `minikube` 💻

Every worker node has three things running on it that make it part of the cluster:

```
Worker Node (The Quay)
│
├── 🤖  kubelet
│       The quay foreman. Talks to the Control Plane.
│       "What Pods should I be running?"
│       "Are my Pods healthy? Let me check... yes. Reporting in."
│
├── 🔌  kube-proxy
│       The quay's network crew.
│       Makes sure traffic gets to the right Pod.
│       Maintains network rules so Pods can talk to each other.
│
└── 🐳  Container Runtime (usually containerd)
        Actually RUNS the containers.
        Like the forklift that physically moves and opens containers.
```

```bash
# See all your nodes
kubectl get nodes

# NAME           STATUS   ROLES           AGE   VERSION
# control-plane  Ready    control-plane   5d    v1.28.0
# worker-1       Ready    <none>          5d    v1.28.0
# worker-2       Ready    <none>          5d    v1.28.0
# worker-3       Ready    <none>          5d    v1.28.0

# Get the full spec of a node -- like reading the quay's equipment manifest
kubectl describe node worker-1
```

---

## Node Resources: The Quay Capacity Report 📊

Every quay has a maximum capacity. You can't stack infinite containers on it. Same with nodes.

```bash
# See how loaded each node is
kubectl top nodes

# NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
# worker-1   245m         12%    1823Mi          47%
# worker-2   891m         44%    3012Mi          77%   <- getting busy!
# worker-3   102m         5%     891Mi           23%

# See which Pods are on which node
kubectl get pods -o wide --all-namespaces

# NAMESPACE   NAME          READY   NODE       IP
# default     web-app-1     1/1     worker-1   10.244.1.5
# default     web-app-2     1/1     worker-3   10.244.3.2
# default     database      1/1     worker-1   10.244.1.6
```

The Scheduler (in the Control Plane tower) looks at this capacity information and decides: *"worker-2 is at 77% memory — let's put this new Pod on worker-3 instead."*

Just like the Harbourmaster looks at the quay capacity board and says: *"North Quay is stacked to the ceiling — route the next ship to South Quay."* 🎯

---

## Node Conditions: Is the Quay Actually Operational? 🔍

Nodes can be healthy, struggling, or completely dead. Kubernetes tracks this with **conditions**:

```bash
kubectl describe node worker-2 | grep -A 20 "Conditions:"

# Conditions:
#   Type                 Status  Message
#   ----                 ------  -------
#   MemoryPressure       False   kubelet has sufficient memory available
#   DiskPressure         False   kubelet has sufficient disk space available
#   PIDPressure          False   kubelet has sufficient PID available
#   Ready                True    kubelet is posting ready status
```

When a node goes `Ready=False` — it's like the quay foreman calling the tower and saying: *"Uh, boss? Our crane is broken. Don't send any more ships to North Quay."*

Kubernetes will **stop scheduling new Pods** to that node, and if the node stays unhealthy long enough — it'll **evict the existing Pods** and move them elsewhere.

The harbour keeps running. The broken quay gets repaired. Zero drama for the customers. 🎩

---

## Taints and Tolerations: VIP Quays and Special Cargo 🎫

Sometimes a quay is reserved for SPECIAL cargo only. Maybe it's got refrigeration for temperature-sensitive goods. Maybe it's a high-security zone. Maybe it's just for Dave's experimental containers and nobody else wants them near their stuff.

In Kubernetes, this is **taints and tolerations**:

- A **taint** on a node says: *"Only special cargo can dock here. Everyone else: go away."*
- A **toleration** on a Pod says: *"I am special cargo. I can handle that taint. Let me in."*

```bash
# Add a taint to a node: "gpu-only" cargo allowed, all others get NoSchedule
kubectl taint nodes worker-3 hardware=gpu:NoSchedule

# Now ONLY Pods with this toleration will be scheduled on worker-3:
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-training-job
spec:
  tolerations:
  - key: "hardware"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
  containers:
  - name: ml-trainer
    image: tensorflow/tensorflow:latest-gpu
    resources:
      limits:
        nvidia.com/gpu: 1   # This Pod needs a GPU!
```

```bash
# Remove the taint when the VIP quay is open to everyone again
kubectl taint nodes worker-3 hardware=gpu:NoSchedule-
#                                                   ^ that minus sign removes it
```

---

## Node Selectors and Affinity: Choosing Your Quay 🧭

Sometimes a Pod wants to be on a SPECIFIC type of node. Not because other nodes have taints — but because the Pod has PREFERENCES.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: fast-storage-app
spec:
  # Simple: only run on nodes labelled with ssd storage
  nodeSelector:
    storage-type: ssd

  # Or sophisticated affinity rules:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/os
            operator: In
            values:
            - linux
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values:
            - eu-west          # Prefer EU nodes, but don't REQUIRE it

  containers:
  - name: fast-app
    image: my-app:latest
```

```bash
# Label your nodes so Pods can find the right quay
kubectl label node worker-1 storage-type=ssd
kubectl label node worker-2 storage-type=hdd
kubectl label node worker-3 storage-type=ssd zone=eu-west

# See node labels
kubectl get nodes --show-labels
```

---

## What Happens When a Node DIES? 💀

OK. This is the moment. The drama. The reason you went through all this pain to learn Kubernetes.

**A node dies.** The quay floods. The server crashes. Power goes out. Dave tripped on the cable. Whatever.

```bash
# Simulate a node failure: cordon it (no new Pods) then drain it (evict existing Pods)
kubectl cordon worker-2    # "Close this quay to new ships"
kubectl drain worker-2 --ignore-daemonsets --delete-emptydir-data

# Watch what happens to Pods:
kubectl get pods -o wide --watch

# NAME        READY   STATUS        NODE       
# web-app-1   1/1     Running       worker-1   # Fine!
# web-app-2   1/1     Terminating   worker-2   # Evacuating!
# web-app-3   1/1     Running       worker-3   # Fine!
# web-app-4   0/1     Pending       <none>     # New replacement being scheduled...
# web-app-4   1/1     Running       worker-1   # Placed on worker-1! 🎉
```

The moment `worker-2` goes down, Kubernetes:
1. Detects the node isn't responding (about 5 minutes by default)
2. Marks the node `NotReady`
3. Evicts all Pods from that node
4. Schedules replacement Pods on healthy nodes
5. Updates Services so traffic stops going to the dead node

**Your users experienced... nothing.** Maybe a tiny blip if you only had one replica. But with three replicas? Zero. Nothing. The cargo ship sailed into a different quay and nobody on the receiving end even noticed the detour. 🚢➡️🚢

---

## Namespaces: Different Zones in the Same Harbour 🗺️

One more thing about cluster organisation. A big harbour has different ZONES. The cargo area. The passenger terminal. The maintenance bay. The area where Dave isn't allowed.

In Kubernetes, **namespaces** are these zones:

```bash
# See existing namespaces
kubectl get namespaces

# NAME              STATUS   AGE
# default           Active   5d    <- Where your stuff goes if you don't specify
# kube-system       Active   5d    <- Kubernetes internal stuff. Don't touch.
# kube-public       Active   5d    <- Publicly readable info
# kube-node-lease   Active   5d    <- Node heartbeat tracking

# Create your own namespace (your own harbour zone)
kubectl create namespace production
kubectl create namespace staging
kubectl create namespace dave-experiments   # Isolated for everyone's safety

# Deploy a Pod to a specific namespace
kubectl apply -f my-pod.yaml -n production

# See Pods in a specific namespace
kubectl get pods -n production

# See Pods in ALL namespaces (the full harbour board)
kubectl get pods --all-namespaces
```

Namespaces are also how you apply **resource quotas** — like telling Dave his experimental zone gets maximum 2 CPU cores and 4GB memory, no matter how ambitious his ideas get:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dave-quota
  namespace: dave-experiments
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "10"           # Maximum 10 Pods. Dave, this is generous.
```

---

## The SIPOC Flow Across the Cluster 🔄

Let's trace a Pod from creation to running, through the cluster lens:

```
SUPPLIER          INPUT              PROCESS                    OUTPUT           CONSUMER
   |                |                   |                          |                |
kubectl          Pod spec           Control Plane              Running Pod       Web users
apply            (yaml)             receives spec               on worker-3
                                        |
                                   Scheduler checks:
                                   - Node resources
                                   - Taints/tolerations
                                   - Node affinity
                                   - "worker-3 looks good"
                                        |
                                   kubelet on worker-3
                                   pulls image, starts
                                   container, reports
                                   back "Ready!"
```

```bash
# Watch this whole process in real time
kubectl apply -f my-pod.yaml
kubectl get events --sort-by='.lastTimestamp' | tail -20

# 0s    Normal   Scheduled    Pod   Successfully assigned default/my-pod to worker-3
# 1s    Normal   Pulling      Pod   Pulling image "nginx:latest"
# 3s    Normal   Pulled       Pod   Successfully pulled image
# 3s    Normal   Created      Pod   Created container nginx
# 3s    Normal   Started      Pod   Started container nginx
```

Every single step. Right there. The harbour logbook. 📋

---

## The Harbourmaster's Log — Entry 3 📋

*Gave the team a tour of the harbour grounds today. Showed them the three worker quays. Explained that the Control Plane tower is where all decisions get made. Showed them the namespace zones.*

*Then worker-2 went down. Right there. During the demo. Power cable came loose.*

*I watched everyone's faces go from panic to confusion to AMAZEMENT as they watched Kubernetes automatically reschedule everything onto worker-1 and worker-3 in real time.*

*"Did you plan that?" someone asked.*

*"...Absolutely," I said.* 🎩

---

## Your Mission, Should You Choose to Accept It 🎯

1. Spin up a local cluster with `kind` using this multi-node config:

```yaml
# kind-cluster.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
- role: worker
```

```bash
kind create cluster --config kind-cluster.yaml --name harbour
kubectl get nodes   # Should see 1 control-plane + 3 workers
```

2. Label your worker nodes:
```bash
kubectl label node harbour-worker   zone=north
kubectl label node harbour-worker2  zone=east
kubectl label node harbour-worker3  zone=south
```

3. Deploy a Pod with a **nodeSelector** to land it specifically on `zone=south`

4. Then **cordon** that node and watch what happens when you delete the Pod

**Bonus:** Add a taint to `zone=north` and create a Pod that tolerates it. Confirm it lands on `harbour-worker`.

---

## Next Time on "Welcome to Container Harbour" 🎬

In **Episode 4**, we go up the stairs of the Harbourmaster's Tower — the **Control Plane**. We'll meet the API Server (the reception desk that never sleeps), etcd (the filing cabinet that must NEVER be deleted), the Scheduler (the genius that decides where everything goes), and the Controller Manager (the one that never stops checking if things are OK).

It's a cast of characters. It's a drama. It's Episode 4. 🎬

---

*P.S. — The Port of Singapore handles over 37 million containers per year with a staff of about 6,000 people. A Kubernetes cluster handles millions of container starts with a staff of... one YAML file and a laptop. The future is NOW.* 🚢

---

**🎯 Key Takeaways:**

- A **cluster** = the entire harbour. Control Plane + Worker Nodes.
- **Worker nodes** = the quays. Each runs `kubelet`, `kube-proxy`, and a container runtime.
- **Namespaces** = harbour zones. Isolate workloads. Protect Dave from himself.
- **Taints** = "VIP quay, special cargo only." **Tolerations** = "I am special cargo."
- **Node affinity** = Pods can *prefer* or *require* specific nodes
- When a node dies, Kubernetes evacuates and reschedules. Your users notice nothing.
- `kubectl get nodes`, `kubectl describe node`, `kubectl top nodes` = your harbour status board
- Resource quotas stop Dave from using all the CPU in the building 🚫
