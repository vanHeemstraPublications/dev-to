---
title: "Welcome to Container Harbour! 🚢 Ep.5"
part: 5
published: false
description: "Episode 5: Forklift Operators Who Never Sleep — ReplicaSets and Deployments. Because manually managing Pods is a one-way ticket to a nervous breakdown."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-05.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 5: Forklift Operators Who Never Sleep 🔁

### The Day I Manually Managed 20 Pods and Lost My MIND 😤

Picture this. Early in my Kubernetes journey. I have 20 Pods running my web application. Everything is BEAUTIFUL.

Then three of them crash simultaneously. So I run `kubectl apply` three times. Fine.

Then another two crash. I run `kubectl apply` twice. Less fine.

Then my COLLEAGUE accidentally deletes five of them thinking they were his test Pods. At this point I am talking to my monitor. Loudly. In Dutch. Using vocabulary I didn't know I had. 😤

My manager walked over and said: "Why aren't you using Deployments?"

Friends. I was not using Deployments. I did not know about Deployments. I was managing Pods. MANUALLY. Like someone trying to run a harbour by standing at the water's edge and catching every container by hand.

Never again. Let me show you the right way. 🎯

---

## The SIPOC of a Deployment 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who submits the Deployment? | You, your CI/CD pipeline, Helm, ArgoCD |
| **Input** | What goes in? | Deployment spec: image, replicas, strategy, labels |
| **Process** | What happens? | Deployment creates ReplicaSet → ReplicaSet manages Pods → Controller Manager watches everything |
| **Output** | What comes out? | N healthy, identical Pods serving your application |
| **Consumer** | Who uses them? | Services (Episode 6) routing traffic to your Pods |

---

## The Hierarchy: Deployment > ReplicaSet > Pod 🏗️

Here is the chain of command:

```
📋 Deployment
   "I want 3 replicas of web-app:v2.1, rolling update strategy"
        |
        v
📊 ReplicaSet
   "OK, I'll make sure exactly 3 Pods exist at all times"
        |
        v
📦 Pod   📦 Pod   📦 Pod
"Hi! I'm running web-app:v2.1"
```

- **Deployment** = the POLICY. What do you want, how should updates happen?
- **ReplicaSet** = the ENFORCER. Makes sure the right number of Pods exist.
- **Pod** = the WORKER. Actually runs your container.

You almost NEVER create ReplicaSets directly. You create Deployments, and they create ReplicaSets for you. Automatically. Like a good harbour manager who creates the work roster without you having to schedule each forklift operator individually.

---

## Your First Deployment 🚀

```yaml
# web-app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web-app
spec:
  replicas: 3           # "I want THREE freight containers, always."

  selector:
    matchLabels:
      app: web-app      # "Manage Pods with THIS label"

  template:             # "Here's what each Pod should look like:"
    metadata:
      labels:
        app: web-app    # Every Pod gets this label (must match selector!)
    spec:
      containers:
      - name: web-app
        image: nginx:1.24           # Version pinned. ALWAYS pin versions in production.
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        readinessProbe:             # "Only send traffic when I'm truly ready"
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
```

```bash
kubectl apply -f web-app-deployment.yaml

# Check the Deployment
kubectl get deployments
# NAME      READY   UP-TO-DATE   AVAILABLE   AGE
# web-app   3/3     3            3           30s

# Check the ReplicaSet it created
kubectl get replicasets
# NAME                 DESIRED   CURRENT   READY   AGE
# web-app-7d9f8b4c9f   3         3         3       30s

# Check the Pods it created
kubectl get pods -l app=web-app
# NAME                       READY   STATUS    RESTARTS   AGE
# web-app-7d9f8b4c9f-2xkpq   1/1     Running   0          30s
# web-app-7d9f8b4c9f-8vntm   1/1     Running   0          30s
# web-app-7d9f8b4c9f-b4dmx   1/1     Running   0          30s
```

Three Pods. Running. Healthy. You did ONE `kubectl apply`. That's the deal.

---

## The ReplicaSet: The Forklift Operator That Never Sleeps 🤖

The ReplicaSet has ONE job: **make sure the right number of Pods exist.**

That's it. That's the whole job. Count the Pods. If fewer than desired, create more. If more than desired, delete some. Repeat forever.

```bash
# PROVE IT. Delete a Pod and watch the ReplicaSet respond.
kubectl delete pod web-app-7d9f8b4c9f-2xkpq

# Immediately watch what happens:
kubectl get pods -l app=web-app --watch

# NAME                       READY   STATUS        RESTARTS   AGE
# web-app-7d9f8b4c9f-2xkpq   1/1     Terminating   0          5m   <- you deleted this
# web-app-7d9f8b4c9f-8vntm   1/1     Running       0          5m   <- fine
# web-app-7d9f8b4c9f-b4dmx   1/1     Running       0          5m   <- fine
# web-app-7d9f8b4c9f-q7pns   0/1     Pending       0          0s   <- REPLACEMENT INCOMING
# web-app-7d9f8b4c9f-q7pns   1/1     Running       0          3s   <- BACK TO THREE! 🎉
```

The ReplicaSet noticed the count dropped to 2. It created a new Pod. You had maybe 3 seconds of degradation. Your users probably never noticed. This is why Kubernetes exists. 🎩

---

## Scaling: Adding More Forklift Operators 📈

Traffic spike incoming! Deploy the extra crew!

```bash
# Scale up to 10 replicas (more ships arriving, open more bays!)
kubectl scale deployment web-app --replicas=10

# Watch them appear
kubectl get pods -l app=web-app --watch

# Or update the YAML and apply (recommended for GitOps)
# Change replicas: 3 to replicas: 10 in your yaml, then:
kubectl apply -f web-app-deployment.yaml

# Verify
kubectl get deployment web-app
# NAME      READY   UP-TO-DATE   AVAILABLE   AGE
# web-app   10/10   10           10          10m

# Traffic died down. Scale back.
kubectl scale deployment web-app --replicas=3

# Seven Pods will gracefully terminate. Three survive.
```

---

## Rolling Updates: Swapping Cargo Without Closing the Harbour 🔄

This is THE killer feature. You have version 1.24 of nginx running. You want version 1.25. In the old world, you'd take the service down, deploy the new version, bring it back up. Users scream. Support tickets pile up.

In Kubernetes: **zero downtime rolling update**. While users are being served by v1.24 Pods, Kubernetes quietly replaces them one by one with v1.25 Pods. Users never know. 🤫

```yaml
# Update your deployment spec to control HOW the update rolls out
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1   # "At most 1 Pod can be down at any time"
      maxSurge: 1         # "You can create 1 extra Pod during the update"
```

```bash
# Update the image (the new version of cargo arriving!)
kubectl set image deployment/web-app web-app=nginx:1.25

# OR update your yaml file and:
kubectl apply -f web-app-deployment.yaml

# Watch the rolling update in real time -- this is MAGIC
kubectl rollout status deployment/web-app
# Waiting for deployment "web-app" rollout to finish: 1 out of 3 new replicas have been updated...
# Waiting for deployment "web-app" rollout to finish: 2 out of 3 new replicas have been updated...
# Waiting for deployment "web-app" rollout to finish: 1 old replicas are pending termination...
# deployment "web-app" successfully rolled out

# See the new ReplicaSet that was created for v1.25
kubectl get replicasets
# NAME                    DESIRED   CURRENT   READY
# web-app-8b9c7f2d6a      3         3         3     <- NEW (nginx:1.25)
# web-app-7d9f8b4c9f      0         0         0     <- OLD (nginx:1.24, kept for rollback)
```

Notice Kubernetes KEEPS the old ReplicaSet around. With zero Pods. Like parking an old freight container on the dock — just in case you need to go back to it. 👀

---

## Rolling Back: OH NO OH NO OH NO 🚨

nginx:1.25 is broken. Or your new app version has a catastrophic bug. Or Dave deployed to production at 4pm on a Friday (classic Dave). You need to roll back. NOW.

```bash
# PANIC MODE: Immediate rollback to previous version
kubectl rollout undo deployment/web-app

# Rollout status
kubectl rollout status deployment/web-app
# deployment "web-app" successfully rolled out

# See what version you're running now
kubectl describe deployment web-app | grep Image
# Image: nginx:1.24  <- We're back! 

# Check rollout history (your deployment logbook)
kubectl rollout history deployment/web-app
# REVISION  CHANGE-CAUSE
# 1         <none>   <- nginx:1.24
# 2         <none>   <- nginx:1.25 (the disaster)
# 3         <none>   <- rollback to nginx:1.24

# Roll back to a SPECIFIC revision
kubectl rollout undo deployment/web-app --to-revision=1

# PRO TIP: Use --record to add notes to your history
kubectl set image deployment/web-app web-app=nginx:1.25 --record
# REVISION  CHANGE-CAUSE
# 2         kubectl set image deployment/web-app web-app=nginx:1.25
```

```bash
# Full deployment inspection -- your incident report
kubectl describe deployment web-app

# Look for the "Events" and "Conditions" sections
# They'll tell you exactly what happened and when
```

---

## Deployment Strategies: How You Want the Swap to Happen 🎯

You have two main strategies:

### Strategy 1: RollingUpdate (the default) 🔄

Replace old Pods gradually. Some of both versions run simultaneously during the update. Zero downtime.

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1    # Max Pods that can be unavailable during update
    maxSurge: 1          # Max extra Pods that can be created during update
```

### Strategy 2: Recreate (the sledgehammer) 💥

Kill ALL old Pods first. Then create new ones. There WILL be downtime. Only use this when old and new versions absolutely cannot run at the same time (database schema changes, etc.).

```yaml
strategy:
  type: Recreate
  # No rollingUpdate section needed -- it kills all then restarts all
```

```bash
# Apply and watch the Recreate strategy
kubectl apply -f deployment-recreate.yaml
kubectl get pods -l app=web-app --watch

# All pods: Terminating, Terminating, Terminating...
# [gap of downtime]
# New pods: Pending, ContainerCreating, Running...
```

---

## Pause and Resume: Staging Multiple Changes 🎛️

Want to make several changes to a Deployment without triggering multiple rolling updates? Pause it, make all your changes, then resume.

```bash
# Pause the deployment (hold updates!)
kubectl rollout pause deployment/web-app

# Make multiple changes
kubectl set image deployment/web-app web-app=nginx:1.25
kubectl set resources deployment/web-app -c=web-app --limits=cpu=200m,memory=256Mi

# Both changes are staged but NOT applied yet
kubectl rollout status deployment/web-app
# Waiting for deployment "web-app" rollout to finish: 0 out of 3 new replicas...

# Apply ALL changes at once
kubectl rollout resume deployment/web-app

# NOW the rolling update begins, with ALL your changes in one go
```

---

## The Full Deployment YAML: Production-Ready 🏆

Here's a production-grade Deployment with everything wired up:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
  labels:
    app: web-app
    version: "1.25"
  annotations:
    kubernetes.io/change-cause: "Upgrade nginx to 1.25 for security patch"
spec:
  replicas: 5
  revisionHistoryLimit: 5    # Keep 5 old ReplicaSets for rollback

  selector:
    matchLabels:
      app: web-app

  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 2

  template:
    metadata:
      labels:
        app: web-app
        version: "1.25"
    spec:
      terminationGracePeriodSeconds: 30   # Give Pods 30s to finish in-flight requests

      containers:
      - name: web-app
        image: nginx:1.25
        ports:
        - containerPort: 80

        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"

        # Liveness: "Is the container alive? If not, restart it."
        livenessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 15
          failureThreshold: 3

        # Readiness: "Is the container READY for traffic? If not, exclude from Service."
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
          failureThreshold: 3

        # Startup: "Is the container still starting up? Give it time."
        startupProbe:
          httpGet:
            path: /healthz
            port: 80
          failureThreshold: 30
          periodSeconds: 10
```

---

## The Harbourmaster's Log — Entry 5 📋

*The forklift operators never call in sick. Never go on strike. Never ask for overtime pay. Never delete the wrong container. (Looking at you, Dave.)*

*Today we updated the fleet from nginx 1.24 to 1.25. No downtime. No emergency calls. No screaming. The rolling update ran while we had our Friday afternoon coffee. By the time we came back, it was done.*

*I showed the team the rollback command. Someone asked: "So we can undo a production deployment in one command?"*

*"Yes," I said.*

*They looked at me like I had performed a magic trick.*

*I told them not to use it on a Monday morning if they could help it.* 🎩

---

## Your Mission, Should You Choose to Accept It 🎯

1. Create a Deployment with 4 replicas of `nginx:1.24`
2. Scale it to 8 replicas
3. Perform a rolling update to `nginx:1.25` — watch it happen with `--watch`
4. Check the rollout history
5. Roll back to `nginx:1.24`
6. Confirm the rollback worked by checking the image version

**Bonus:** Deliberately break a deployment by using a non-existent image (`nginx:this-does-not-exist`) and watch what happens. What status do the new Pods get? Does the rolling update abort? Does the old version keep running? (It should! `maxUnavailable: 1` protects you.)

```bash
kubectl set image deployment/web-app web-app=nginx:this-does-not-exist
kubectl rollout status deployment/web-app   # What does it say?
kubectl get pods -l app=web-app             # What do you see?
kubectl rollout undo deployment/web-app     # Rescue operation!
```

---

## Next Time on "Welcome to Container Harbour" 🎬

In **Episode 6**, your Pods are running. Beautifully. Three of them. But here's the problem: they each have their own IP address, and those IP addresses CHANGE every time a Pod is recreated.

How does anyone find your application?

Enter **Services** — the harbour gates that give your application a stable, permanent address, no matter how many Pods come and go behind it. 🚦

---

*P.S. — In 2022, Discord ran over 800 billion messages through their Kubernetes cluster in a single month. Their Deployments were rolling out updates while you were reading that message. That's the forklift crew in action.* 🤖

---

**🎯 Key Takeaways:**

- **Never** manage bare Pods in production. Always use a **Deployment**.
- **Deployment** = policy (what you want). **ReplicaSet** = enforcer (keeps count). **Pod** = worker.
- **RollingUpdate** strategy = zero downtime updates. The default. Use it always.
- **Recreate** strategy = kill all, restart all. Downtime guaranteed. Use only when necessary.
- `kubectl rollout undo` is your emergency ejector seat. Know where it is BEFORE you need it.
- Pin your image versions (`nginx:1.25` not `nginx:latest`). Latest in production = chaos.
- ReplicaSets keep old versions for rollback. `revisionHistoryLimit` controls how many.
- Pause + resume for batching multiple changes into one rolling update 🎛️
