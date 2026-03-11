---
title: "Welcome to Container Harbour! 🚢 Ep.2"
published: false
description: "Episode 2: The Humble Freight Container — Meet the Pod, Kubernetes' most fundamental unit. It's smaller than you think and more important than you know!"
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-02.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: The Humble Freight Container — Meet the Pod 📦

### OH. You Thought a Container WAS a Pod? 😂

Let me tell you something. When I first started learning Kubernetes, I thought a container and a Pod were the same thing. I walked into a team meeting and I said — OUT LOUD, in FRONT of people — "Yeah, so we've got like 50 containers running in our cluster."

And this senior engineer just looked at me. Real slow. Like I had just said the earth was flat.

"You mean Pods," she said.

"...same thing?" I said.

Reader, it was not the same thing. 😬

Here is the truth: **a Pod is like a freight container. A Docker container is like the CARGO inside it.** The freight container is the standardised, shippable unit. The cargo is what you actually care about. And sometimes — SOMETIMES — one freight container holds multiple pieces of cargo that need to travel together.

Let's get into it. 🚢

---

## The SIPOC of a Pod 🗂️

Before we go any further, let me introduce a framework that's going to follow us through this ENTIRE series. It's called **SIPOC** — and it's beautiful because it forces you to think about EVERYTHING that matters:

| | What it means | In the harbour | In Kubernetes |
|---|---|---|---|
| **S** | Supplier | Who sends the ship? | `kubectl` / CI pipeline / Helm |
| **I** | Input | What cargo arrives? | Container image + config |
| **P** | Process | What happens at the dock? | Kubernetes schedules & runs the Pod |
| **O** | Output | What leaves the harbour? | A running application serving requests |
| **C** | Consumer | Who receives the goods? | End users / other services |

Every time we explain something new in this series, we'll map it to SIPOC. Because if you can't explain what goes IN, what happens, and what comes OUT — you don't really understand it yet. 🎯

---

## So What IS a Pod, Exactly? 📦

A **Pod** is the smallest deployable unit in Kubernetes. Not a container. A **Pod**.

Think of it like this. You're at Rotterdam harbour. A freight container arrives. That container has:

- Its own **identity** (a serial number, a manifest)
- Its own **network address** (so people can call it)
- Its own **storage** (shelves inside the container)
- One or more **pieces of cargo** (the actual contents)

A Pod is EXACTLY that:

- Its own **name** and **identity** in the cluster
- Its own **IP address** (so other Pods can talk to it)
- Its own **storage volumes** (if needed)
- One or more **Docker containers** running inside it

```yaml
# This is a Pod. Your first one. Look at it. Beautiful. 😍
apiVersion: v1
kind: Pod
metadata:
  name: banana-shipment        # The container's serial number
  labels:
    cargo: bananas             # What's inside (useful for routing)
    origin: rotterdam          # Where it came from
spec:
  containers:
  - name: banana-app           # The cargo inside the container
    image: nginx:latest        # The image (what kind of cargo?)
    ports:
    - containerPort: 80        # The loading dock door number
```

Apply this to your cluster:

```bash
# Fire this up in your local harbour (kind or minikube)
kubectl apply -f banana-pod.yaml

# Check it arrived safely
kubectl get pods

# NAME               READY   STATUS    RESTARTS   AGE
# banana-shipment    1/1     Running   0          12s

# Look INSIDE the container (like opening the freight door)
kubectl describe pod banana-shipment
```

IT'S ALIVE! 🎉 Your first Pod is running. You're basically a Harbourmaster now. Well — assistant Harbourmaster. Don't push it.

---

## One Container per Pod — The Normal Case 🍌

Most of the time — and I'm talking like 95% of real-world workloads — a Pod has **one container** inside it.

One freight container. One type of cargo. Simple.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: single-cargo-pod
spec:
  containers:
  - name: my-web-app
    image: my-company/web-app:v1.2.3
    ports:
    - containerPort: 8080
    env:
    - name: PORT
      value: "8080"
    - name: LOG_LEVEL
      value: "info"
    resources:
      requests:
        memory: "64Mi"    # Minimum storage space in the container
        cpu: "250m"       # Minimum forklift power (250 millicores)
      limits:
        memory: "128Mi"   # Maximum — don't you DARE go over this
        cpu: "500m"       # Maximum CPU — share the forklift!
```

```bash
# See your Pod running
kubectl get pod single-cargo-pod -o wide

# NAME                READY   STATUS    IP           NODE
# single-cargo-pod    1/1     Running   10.244.0.5   worker-node-1

# Get the logs (what is this container SAYING?)
kubectl logs single-cargo-pod

# Jump inside the container — like opening the door and climbing in
kubectl exec -it single-cargo-pod -- /bin/sh
```

---

## Multi-Container Pods — When Cargo Travels Together 🚛

NOW. Here's where it gets interesting. And a little weird. Stay with me.

Sometimes, two pieces of cargo are so tightly related that they **must** travel in the same freight container. They share the same space. They can talk to each other directly. They live and die together.

In Kubernetes, this is a **multi-container Pod** — and the most common pattern is called a **sidecar**.

Imagine this: your web app container generates logs. And you need something to COLLECT those logs and ship them somewhere. You could build that into your app — but then your app is doing TWO jobs. Bad design. 

Instead: pack a **log collector sidecar** in the same Pod. They share a volume (the storage shelf inside the freight container). The app writes logs to the shelf. The sidecar picks them up and ships them. Beautiful teamwork. 🤝

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-sidecar
  labels:
    app: web-with-logging
spec:
  # Shared storage shelf inside the freight container
  volumes:
  - name: shared-logs
    emptyDir: {}          # Empty shelf — created fresh for this Pod

  containers:
  # THE MAIN CARGO: Our web application
  - name: web-app
    image: nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx   # App writes logs HERE

  # THE SIDECAR: Log collector travelling with the main cargo
  - name: log-collector
    image: busybox:latest
    command: ['sh', '-c', 'while true; do cat /logs/*.log | wc -l; sleep 10; done']
    volumeMounts:
    - name: shared-logs
      mountPath: /logs            # Sidecar reads logs FROM HERE
```

```bash
kubectl apply -f app-with-sidecar.yaml

# Check BOTH containers are running (2/2 means two containers, both healthy)
kubectl get pod app-with-sidecar
# NAME                 READY   STATUS    RESTARTS   AGE
# app-with-sidecar     2/2     Running   0          30s

# Get logs from a SPECIFIC container in the pod
kubectl logs app-with-sidecar -c web-app
kubectl logs app-with-sidecar -c log-collector

# They share the same IP address! 
# Inside the pod, containers talk to each other via localhost 
kubectl exec -it app-with-sidecar -c log-collector -- sh
# Inside: ping localhost -- talks directly to the web-app!
```

Two containers. One IP address. One storage shelf. **One Pod.** 🎯

---

## What Happens When a Pod Falls in the Water? 🌊

OK here's where I need you to SIT DOWN because this is IMPORTANT.

Pods are **ephemeral**. That's a fancy word for: **they are born to die**. 💀

A Pod is NOT permanent. It is NOT meant to be permanent. If a Pod falls in the harbour water — if the node it's running on crashes, if the container exits, if Kubernetes decides it needs to move things around — **that Pod is GONE**.

Gone gone. Delete gone. The IP address? Gone. The name? Gone. Whatever was in memory? GONE.

```bash
# Watch this. Delete your pod.
kubectl delete pod banana-shipment

# Now look for it.
kubectl get pods
# NAME               READY   STATUS    RESTARTS   AGE
# (nothing. it's gone. it's really gone.)

# Apply it again — notice the START TIME resets. Fresh pod. New life.
kubectl apply -f banana-pod.yaml
kubectl get pods
# NAME               READY   STATUS    RESTARTS   AGE
# banana-shipment    1/1     Running   0          2s   <- brand new!
```

THIS IS BY DESIGN. Don't panic. 

The harbour doesn't keep a specific freight container in Bay 7 forever. When a job is done, the container leaves. When a new shipment comes, a new container arrives. **The system is designed around containers coming and going**, not around individual containers being precious.

Later in this series, we'll meet **Deployments** (Episode 5) which manage Pods for you — automatically replacing them when they die. That's where the real magic is. 🪄

---

## The SIPOC in Action: Pod Lifecycle 🔄

Let's run the SIPOC for a Pod's full lifecycle:

| | | Detail |
|---|---|---|
| **Supplier** | Who creates the Pod spec? | You, your CI pipeline, a Deployment controller |
| **Input** | What goes in? | Container image, env vars, resource requests, volume mounts |
| **Process** | What happens? | Scheduler picks a node → kubelet pulls image → container starts → health checks run |
| **Output** | What comes out? | A running container with an IP, serving traffic or doing work |
| **Consumer** | Who uses it? | End users, other Pods, Services (we'll meet those in Ep.6) |

```bash
# Watch the PROCESS phase in real time — Pod going through its lifecycle
kubectl get pod banana-shipment --watch

# NAME               READY   STATUS              RESTARTS   AGE
# banana-shipment    0/1     Pending             0          0s   <- Scheduler deciding
# banana-shipment    0/1     ContainerCreating   0          1s   <- Image being pulled
# banana-shipment    1/1     Running             0          3s   <- WE'RE LIVE BABY! 🎉
```

Pending → ContainerCreating → Running. That's the Pod lifecycle in three acts. Like a freight container: ordered → loaded onto ship → arrived and operational.

---

## Pod Status: Reading the Harbour Board 📋

The harbour has a big board showing the status of every container. Kubernetes has one too:

```bash
kubectl get pods -o wide

# NAME                READY   STATUS             RESTARTS   AGE   IP            NODE
# banana-shipment     1/1     Running            0          5m    10.244.0.6    worker-1
# broken-app          0/1     CrashLoopBackOff   4          3m    10.244.0.7    worker-1
# slow-starter        0/1     Init:0/1           0          30s   <none>        worker-2
```

Here's your **harbour board decoder ring** 🔍:

| Status | What it means | What to do |
|---|---|---|
| `Pending` | Scheduler hasn't placed it yet | Check resources — is the quay full? |
| `ContainerCreating` | Image being pulled, volumes mounting | Wait — it's being loaded |
| `Running` | All containers healthy | 🎉 Nothing. Go get coffee. |
| `CrashLoopBackOff` | Container keeps dying and restarting | Check logs! Something is VERY wrong |
| `OOMKilled` | Out of memory — container ate too much | Increase memory limits |
| `Terminating` | Pod is being gracefully shut down | Normal — it's leaving the harbour |
| `ImagePullBackOff` | Can't find the container image | Check your image name and registry |

```bash
# CrashLoopBackOff? First thing you do:
kubectl logs broken-app --previous    # Logs from BEFORE it crashed

# Still confused? Describe it — full incident report:
kubectl describe pod broken-app
# Look for the "Events" section at the bottom. That's your crime scene. 🔍
```

---

## The Harbourmaster's Log — Entry 2 📋

*Bay 7 got its first Pod today. Nginx. Simple job — serve web traffic. Nothing fancy.*

*But I watched it go through its lifecycle. Pending. Creating. Running. And I thought — that's it. That's the whole thing. A sealed unit, with everything it needs, placed exactly where it should be, doing exactly one job.*

*Dave asked if he could run his app and his database in the same Pod.*

*I told him no. Dave looked sad.*

*I explained about the sidecar pattern. Dave looked confused.*

*I drew a picture of a freight container with two things inside it, sharing a shelf. Dave said "OH." and walked away.*

*Progress.* 🎩

---

## Your Mission, Should You Choose to Accept It 🎯

Create a multi-container Pod with:

1. A **main container** running `nginx:latest` serving a simple HTML page
2. A **sidecar container** running `busybox` that every 30 seconds writes the current timestamp to a shared volume
3. Mount the shared volume in nginx so it serves the timestamp file at `/timestamp.txt`

```bash
# Test it with:
kubectl port-forward pod/your-pod-name 8080:80
curl http://localhost:8080/timestamp.txt
# Should show the timestamp your sidecar wrote!
```

Hint: you'll need `emptyDir` volume + `volumeMounts` in both containers. You've seen it. You can do this. 💪

---

## Next Time on "Welcome to Container Harbour" 🎬

In **Episode 3**, we zoom out and look at the whole harbour grounds — the **Nodes and the Cluster**. Who are the worker quays? Who's the management tower? And what happens when an entire quay section falls into the sea?

(Spoiler: Kubernetes shrugs and moves everything to the other quays. It's WILD.) 😎

Until then — keep your Pods healthy, your images tagged, and for the love of everything DO NOT run your database and your web app in the same Pod. 🚢⚓

---

*P.S. — The world record for most containers on a single ship is 24,346 containers, set by the MSC Irina in 2023. Kubernetes won't blink at that. Kubernetes has seen things. 😤*

---

**🎯 Key Takeaways:**

- A **Pod** is the smallest deployable unit in Kubernetes — not a container
- A Pod wraps one or more Docker containers, giving them a **shared IP and shared storage**
- **Most Pods have one container** — keep it simple unless you need a sidecar
- **Sidecar pattern** = second container in the same Pod doing support work (logging, proxying, syncing)
- Pods are **ephemeral** — they die, and that is FINE. Deployments handle replacement (Ep.5)
- **SIPOC for Pods**: image + config IN → Kubernetes schedules it → running app OUT → users happy
- `kubectl logs`, `kubectl describe`, and `kubectl exec` are your three best friends
- `CrashLoopBackOff` means something is broken. Check logs. Breathe. Check logs again. 🔍
