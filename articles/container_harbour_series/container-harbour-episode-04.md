---
title: "Welcome to Container Harbour! 🚢 Ep.4"
part: 4
published: false
description: "Episode 4: The Harbourmaster's Tower — the Control Plane explained. API Server, etcd, Scheduler, and Controller Manager walk into a bar. The bar is your cluster."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-04.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 4: The Harbourmaster's Tower — The Control Plane ☕

### Nobody Told Me the Harbourmaster's Tower Had FOUR People In It 😂

When I first heard "Control Plane," I thought — OK, one thing. One component. THE brain. Simple.

Then I found out it's FOUR separate components, each with their own job, and if you lose the wrong one the entire harbour grinds to a halt.

I said "how is any of this simpler than just SSHing into a server?"

My colleague said "you'll understand eventually."

I did not understand for another three months.

But YOU — YOU are going to understand TODAY. Because I'm going to take you inside the Harbourmaster's Tower, introduce you to every single person working there, and explain EXACTLY what they do and why they matter.

Buckle up. This tower has CHARACTERS. 🎭

---

## The SIPOC of the Control Plane 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who sends requests in? | `kubectl`, CI pipelines, operators, your shaking hands at 2am |
| **Input** | What arrives at the tower? | YAML manifests, API calls, state change requests |
| **Process** | What does the tower do? | Validates → Stores → Schedules → Reconciles → Reports |
| **Output** | What comes out? | Pods scheduled on nodes, cluster state matching desired state |
| **Consumer** | Who uses the output? | Worker nodes (kubelet), monitoring systems, you checking if it worked |

---

## Meet the Tower Staff 🏢

```
🏢  THE HARBOURMASTER'S TOWER (Control Plane)
│
├── 📞  kube-apiserver
│       The Reception Desk. ALL communication goes through here.
│       Nothing happens in this harbour without talking to this desk.
│
├── 🗄️  etcd
│       The Filing Cabinet. The single source of truth.
│       EVERYTHING is written here. Lose this, lose EVERYTHING.
│
├── 🧭  kube-scheduler
│       The Logistics Genius. Decides which Pod goes to which node.
│       Runs complex algorithms so you don't have to.
│
└── 🔄  kube-controller-manager
        The Obsessive Checker. Never sleeps. Never stops watching.
        "Is the desired state matching actual state? IS IT?!"
```

Let's meet them properly. 🤝

---

## kube-apiserver: The Reception Desk That Never Sleeps 📞

EVERYTHING in Kubernetes goes through the API Server. I mean EVERYTHING.

- You run `kubectl get pods`? That's an API call.
- A new Pod gets scheduled? The API Server recorded it.
- A node reports it's healthy? Through the API Server.
- Dave accidentally deletes the production namespace? (I'm not saying this happened.) Through the API Server.

```bash
# You're ALWAYS talking to the API Server. Let's prove it.
kubectl get pods -v=8   # Verbose mode -- shows the actual HTTP calls

# You'll see something like:
# GET https://your-cluster:6443/api/v1/namespaces/default/pods
# Response Status: 200 OK
```

The API Server is an **HTTPS REST API**. Everything is a REST call. `kubectl` is just a nice CLI wrapper that translates your commands into REST calls.

```bash
# Talk to the API Server directly (raw curl, no kubectl)
# Get the cluster API server address
kubectl cluster-info
# Kubernetes control plane is running at https://127.0.0.1:6443

# List all API resources (everything Kubernetes can do)
kubectl api-resources

# See all API versions
kubectl api-versions
```

The API Server does three things to every request:

1. **Authentication** — "Who are you? Show me your credentials." 🪪
2. **Authorization** — "Are you ALLOWED to do this? Check RBAC." (Episode 10!)
3. **Admission Control** — "Even if you're allowed, does this request make SENSE?" 🔍

Only after passing all three does the API Server accept your request and write it to etcd. Three bouncers at the club door. Very exclusive club. 🎫

---

## etcd: The Filing Cabinet That Must NEVER Be Deleted 🗄️

etcd is a distributed key-value store. It stores the **entire state of your cluster**.

Every Pod. Every Service. Every ConfigMap. Every node status. Every deployed manifest. Every secret. All of it. In etcd.

I cannot stress this enough: **if you lose etcd without a backup, your cluster is gone.** Not struggling. Not degraded. **GONE.** You would have to rebuild everything from scratch.

```
etcd stores things like:
  /registry/pods/default/web-app-1        -> Pod spec + status
  /registry/services/default/my-service   -> Service spec
  /registry/deployments/default/api       -> Deployment spec
  /registry/secrets/default/db-password   -> Your secrets (encrypted!)
  /registry/nodes/worker-1                -> Node status and capacity
```

```bash
# In a managed cluster (AKS, EKS, GKE) -- the cloud provider backs up etcd for you
# In a self-managed cluster -- YOU are responsible. Back. It. Up.

# If you're running kubeadm, etcd runs as a Pod:
kubectl get pods -n kube-system | grep etcd
# etcd-control-plane   1/1   Running   0   5d

# Check etcd health (in a kubeadm cluster)
kubectl exec -n kube-system etcd-control-plane -- etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/peer.crt \
  --key=/etc/kubernetes/pki/etcd/peer.key \
  endpoint health

# Output:
# https://127.0.0.1:2379 is healthy: successfully committed proposal
```

etcd uses the **Raft consensus algorithm** to stay consistent across multiple replicas. In a production cluster, you run three or five etcd instances (always odd numbers — avoids split-brain voting ties). They elect a leader. They agree on every write before confirming it.

Like a committee of very pedantic filing clerks who refuse to file anything until EVERYONE has agreed it should be filed. Annoying? Yes. Correct? Absolutely. 📋

---

## kube-scheduler: The Logistics Genius 🧭

The Scheduler's job sounds simple: "Given this Pod, which node should run it?"

The reality: it runs through an EIGHTEEN-STEP algorithm to figure that out. Eighteen. Steps.

```
SCHEDULER DECISION PROCESS (simplified):

Step 1:  "Which nodes exist?" (Get all nodes from API Server)
Step 2:  "Filter out nodes that CAN'T run this Pod:"
           - Not enough CPU?         ELIMINATED
           - Not enough memory?      ELIMINATED  
           - Has a taint the Pod     ELIMINATED
             doesn't tolerate?
           - Wrong node selector?    ELIMINATED
           - Disk full?              ELIMINATED
Step 3:  "Score remaining nodes:"
           - Most available CPU?     +points
           - Most available memory?  +points
           - Pod affinity match?     +points
           - Spread across zones?    +points
Step 4:  "Highest score wins. Schedule Pod there."
Step 5:  "Write decision to etcd via API Server."
Step 6:  "Tell kubelet on that node: you've got a new Pod coming."
```

```bash
# Watch the Scheduler make decisions in real time
kubectl get events --sort-by='.lastTimestamp' | grep Scheduled

# Normal  Scheduled  Pod/web-app  Successfully assigned default/web-app to worker-2

# If the Scheduler CAN'T place a Pod:
kubectl describe pod my-pending-pod | grep -A 10 "Events:"
# Warning  FailedScheduling  0/3 nodes are available:
#   1 Insufficient cpu,
#   2 node(s) had taints that the pod didn't tolerate
# (Translation: "The quays are full. This container is waiting in the bay.")
```

You can even write your OWN scheduler if you don't like how Kubernetes does it. Wild, right? You can tell a Pod to use a custom scheduler:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: special-pod
spec:
  schedulerName: my-custom-scheduler   # Use YOUR scheduler, not the default
  containers:
  - name: app
    image: nginx:latest
```

Nobody does this casually. But knowing you CAN is half the fun. 😏

---

## kube-controller-manager: The Obsessive Checker 🔄

This is my FAVOURITE component. The Controller Manager is basically someone who cannot stop asking "but is it STILL OK though?"

It runs a bunch of **control loops** — each one checking a specific aspect of the cluster:

| Controller | What it obsesses over |
|---|---|
| Node Controller | "Are all my nodes still alive?! CHECK." |
| Replication Controller | "Do I have the right number of Pods?! COUNT." |
| Endpoints Controller | "Are Services connected to the right Pods?! VERIFY." |
| Service Account Controller | "Are all namespaces set up with tokens?! CONFIRM." |
| Job Controller | "Did the batch jobs finish?! REPORT." |

Each controller runs a **reconciliation loop**:

```
RECONCILIATION LOOP (runs constantly, forever, without breaks):

1. "What does the DESIRED state say?"   (read from etcd)
2. "What is the ACTUAL state?"          (observe the cluster)
3. "Is actual == desired?"
   - YES:  😴 Go back to step 1. Keep watching.
   - NO:   😤 Fix it. Make actual match desired. Go back to step 1.
```

This is called **declarative infrastructure**. You declare what you WANT. Kubernetes figures out how to get there — and keeps checking forever to make sure it STAYS there.

```bash
# Here's the Controller Manager in action.
# Tell Kubernetes you want 3 replicas of your app:
kubectl scale deployment web-app --replicas=3

# Controller Manager notices: "Desired=3, Actual=1. UNACCEPTABLE."
# It creates 2 new Pods. Now Actual=3.

# Now manually delete one Pod (simulating a crash):
kubectl delete pod web-app-abc123

# Controller Manager notices: "Desired=3, Actual=2. AGAIN?!"
# It creates 1 new Pod. Back to 3.

# Watch it happen:
kubectl get pods --watch
# web-app-abc123   1/1   Running    <- exists
# web-app-abc123   1/1   Terminating  <- you deleted it
# web-app-xyz789   0/1   Pending      <- Controller Manager reacts!
# web-app-xyz789   1/1   Running      <- back to 3. Balance restored.
```

The Controller Manager NEVER stops. Day and night. Weekend. Christmas. Your holiday in Guernsey. It does not care. It just keeps checking. This is actually reassuring once you get used to it. 🎩

---

## How They Work Together: A Day in the Tower 🎬

Let's trace a single `kubectl apply` through all four Control Plane components:

```bash
kubectl apply -f my-deployment.yaml
```

```
YOU                    API SERVER              etcd           SCHEDULER    CONTROLLER MGR
 |                         |                    |                 |              |
 |-- POST /deployments --> |                    |                 |              |
 |                         |-- AuthN? -------> |                 |              |
 |                         |-- AuthZ? -------> |                 |              |
 |                         |-- Admission? ---> |                 |              |
 |                         |-- WRITE --------> |                 |              |
 |                         |<-- ACK ---------- |                 |              |
 |<-- 201 Created -------- |                    |                 |              |
 |                         |                    |                 |              |
 |                         |                    |    WATCH! <---- |              |
 |                         |                    |    "New          |              |
 |                         |                    |    Deployment    |              |
 |                         |                    |    in etcd!"     |              |
 |                         |                    |       |          |              |
 |                         |                    |       |<-- "Which node?" ----  |
 |                         |<-- Schedule Pod ---|-------|          |              |
 |                         |-- WRITE Pod -----> |                 |              |
 |                         |                    |                 |              |
 |                         |                    | WATCH! <--------------------- |
 |                         |                    | "New Pod in etcd!"            |
 |                         |                    | "Desired=1, Actual=0. FIX IT!"|
 |                         |<- Create Pod  ---  |                               |
```

All of this happens in **under a second** in a healthy cluster. The four tower staff communicate constantly, at machine speed, via the API Server. 🚀

---

## Watching the Tower Work in Real Time 👀

```bash
# Watch everything happening in the cluster (like CCTV for the tower)
kubectl get events --watch --sort-by='.lastTimestamp'

# Watch the control plane component logs
kubectl logs -n kube-system kube-scheduler-control-plane --tail=20
kubectl logs -n kube-system kube-controller-manager-control-plane --tail=20

# Check that all control plane components are healthy
kubectl get componentstatuses

# NAME                 STATUS    MESSAGE
# scheduler            Healthy   ok
# controller-manager   Healthy   ok
# etcd-0               Healthy   {"health":"true"}

# Or the newer way:
kubectl get pods -n kube-system
```

---

## The Harbourmaster's Log — Entry 4 📋

*Walked new hire through the Control Plane today.*

*Explained the API Server is the reception desk. She asked what happens if the reception desk goes down. I said: the harbour stops accepting new ships, but existing ones keep working.*

*Explained etcd is the filing cabinet. She asked if we back it up. I said... I sent an urgent Slack message to the infrastructure team.*

*Explained the Scheduler. She immediately asked if it could be configured to avoid placing Pods on worker-3 because "that node always feels sketchy." I said that is EXACTLY what taints and tolerations are for and gave her a high five.*

*Explained the Controller Manager. She said "so it's just... watching. Forever?" I said yes. She said "that sounds exhausting." I said it's a process. It doesn't get tired.*

*She said "lucky."*

*I agreed.* 🎩

---

## Your Mission, Should You Choose to Accept It 🎯

1. Enable verbose logging on kubectl and watch what API calls happen when you run common commands:

```bash
kubectl get pods -v=8      # See the GET request
kubectl apply -f pod.yaml -v=8   # See the POST request
kubectl delete pod my-pod -v=8   # See the DELETE request
```

2. Watch the Scheduler make a decision by creating a Pod that CANNOT be scheduled (request more CPU than any node has), then watch the events:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: impossible-pod
spec:
  containers:
  - name: greedy-app
    image: nginx:latest
    resources:
      requests:
        cpu: "9999"    # Nobody has this. Nobody.
```

```bash
kubectl apply -f impossible-pod.yaml
kubectl describe pod impossible-pod
kubectl get events | grep impossible-pod
# What does the Scheduler say? What's the event message?
```

3. Fix the impossible Pod by reducing the CPU request to something realistic. Watch it get scheduled.

---

## Next Time on "Welcome to Container Harbour" 🎬

In **Episode 5**, we meet the **forklift operators who never sleep** — **ReplicaSets and Deployments**. These are what make Kubernetes actually useful in production. No more manually managing individual Pods. Declare what you want. Kubernetes delivers. Forever.

And if you've ever wondered what happens during a rolling update — we've got you. 🎬

---

*P.S. — etcd was created by CoreOS in 2013. The name comes from two things: the `/etc` directory in Linux (where system configuration lives) and "d" for distributed. It is now one of the most critical pieces of infrastructure on the planet and it has a name that sounds like a medication. "Have you tried etcd? Side effects include: high availability and strong consistency."* 💊

---

**🎯 Key Takeaways:**

- **Control Plane** = the Harbourmaster's Tower with four staff members
- **kube-apiserver** = the reception desk. ALL communication goes through it. Always.
- **etcd** = the filing cabinet. One source of truth. Back it up or suffer eternally.
- **kube-scheduler** = the logistics genius. 18-step algorithm to place every Pod.
- **kube-controller-manager** = the obsessive checker. Reconciles desired vs actual state. Forever.
- Everything is a **declarative API call**: you declare state, Kubernetes achieves it.
- Losing etcd = losing your cluster. Managed clusters (AKS/EKS/GKE) handle this for you.
- `kubectl -v=8` reveals the API calls underneath. Eye-opening. 👀
