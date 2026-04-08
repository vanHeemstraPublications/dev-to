---
title: "Welcome to Container Harbour! 🚢 Ep.15"
part: 15
published: false
description: "Episode 15: Leaving Harbour Gracefully — Rolling Updates and Zero Downtime Deployments. The grand finale. Change everything. Break nothing. Amaze everyone."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-15.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 15: Leaving Harbour Gracefully 🌅

### The Production Deployment That Used to Require a 2am Saturday Maintenance Window 😤

Every engineer who has been around long enough has a war story. Mine involves:

- A 2am Saturday maintenance window
- A 45-minute planned outage
- A deployment script that nobody had tested end-to-end
- A rollback that took longer than the deployment
- One very understanding on-call team
- Three energy drinks
- A fundamental reassessment of my life choices

We took the service DOWN. We deployed. We brought it UP. Users couldn't access their accounts for 45 minutes. On a Saturday night. Because that's when "traffic was lowest."

Today? Our deployments happen at 2pm on a Tuesday. During peak traffic. While the team is in a retro. Nobody notices. The service never goes down.

This is the final episode of Container Harbour. Let's make it count. 🎯

---

## The SIPOC of Zero-Downtime Deployment 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who triggers the deployment? | Developer, CI/CD pipeline, GitOps (ArgoCD, Flux) |
| **Input** | What goes in? | New container image, updated Deployment spec |
| **Process** | What happens? | Rolling update with health checks, traffic management, graceful shutdown |
| **Output** | What comes out? | New version running, zero user impact, immediate rollback capability |
| **Consumer** | Who notices? | Nobody. That's the point. |

---

## The Anatomy of Zero Downtime: Five Moving Parts 🔧

For a truly zero-downtime deployment, you need FIVE things working together:

```
1. 🔄 Rolling Update Strategy    -- Replace Pods gradually, not all at once
2. 🩺 Readiness Probes           -- New Pods only get traffic when truly ready
3. ⏰ terminationGracePeriod     -- Old Pods get time to finish in-flight requests
4. 🎯 PodDisruptionBudget        -- Guarantee minimum availability during disruption
5. 🏷️  preStop Hook              -- Signal the app to stop gracefully
```

Miss any one of these and you will have downtime. They work as a system. 🎯

---

## Part 1: The Rolling Update Strategy 🔄

We covered this in Episode 5. Here's the production-grade version:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0     # ZERO unavailable. Never drop below desired count.
      maxSurge: 1           # Create one extra Pod during update. Costs slightly more temporarily.
```

With `maxUnavailable: 0` and `maxSurge: 1`:

```
Before update: [v1][v1][v1]          3 Pods serving

Step 1:        [v1][v1][v1][v2]      Add 1 new (surge). v2 starts, not ready yet.
Step 2:        [v1][v1][v2]          v2 passes readiness. Remove 1 v1.
Step 3:        [v1][v1][v2][v2]      Add another v2 (surge).
Step 4:        [v1][v2][v2]          v2 passes readiness. Remove 1 v1.
Step 5:        [v1][v2][v2][v2]      Add final v2 (surge).
Step 6:        [v2][v2][v2]          v2 passes readiness. Remove last v1.

After update:  [v2][v2][v2]          3 Pods serving. Done. Zero downtime.
```

Traffic ONLY goes to v2 Pods AFTER they pass the readiness probe. v1 Pods ONLY get terminated AFTER v2 is confirmed ready. This is the contract. 🤝

---

## Part 2: Readiness Probes (the Gatekeeper) 🩺

From Episode 11, but now in the context of deployments:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
  successThreshold: 2     # Must pass readiness check TWICE consecutively before getting traffic
```

The `successThreshold: 2` is important: a Pod must prove it's ready twice in a row before traffic is routed to it. Prevents a Pod that passes once on a fluke from immediately receiving production load.

---

## Part 3: Graceful Shutdown — Letting In-Flight Requests Land ✈️

When Kubernetes decides to terminate a Pod, here's what happens:

```
1. Kubernetes sends SIGTERM to the container process
2. Container has terminationGracePeriodSeconds to finish work and exit
3. If it doesn't exit: SIGKILL (force kill) after the grace period
4. Pod is removed from Service endpoints BEFORE or DURING this process
```

The problem: there's a race condition. The Pod might get removed from the Service endpoints AFTER it receives SIGTERM, meaning it might still get traffic for a few seconds while it's shutting down.

The solution: **preStop hook**. Add a sleep before SIGTERM processing:

```yaml
spec:
  terminationGracePeriodSeconds: 60    # Give 60 seconds total to shut down

  containers:
  - name: web-app
    image: my-app:latest

    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 15"]
          # Wait 15 seconds before the app starts shutting down
          # This gives kube-proxy time to update iptables rules
          # and stop routing new traffic to this Pod

    # Your app also needs to handle SIGTERM gracefully:
    # 1. Stop accepting new requests
    # 2. Finish in-flight requests
    # 3. Close database connections
    # 4. Exit cleanly
```

```python
# Python example: handling SIGTERM gracefully
import signal
import sys
from flask import Flask

app = Flask(__name__)
shutdown_requested = False

def handle_sigterm(*args):
    global shutdown_requested
    print("SIGTERM received. Finishing in-flight requests...")
    shutdown_requested = True

signal.signal(signal.SIGTERM, handle_sigterm)

@app.route('/ready')
def readiness():
    if shutdown_requested:
        return "Shutting down", 503    # Stop getting new traffic!
    return "OK", 200

@app.route('/')
def index():
    if shutdown_requested:
        return "Service shutting down", 503
    # ... normal processing
    return "Hello from the harbour!"
```

---

## Part 4: PodDisruptionBudget — The Minimum Crew Guarantee 🛡️

A **PodDisruptionBudget** (PDB) tells Kubernetes: "Never take more than N Pods down simultaneously." This protects you during:

- Node maintenance (`kubectl drain`)
- Cluster upgrades
- Cluster Autoscaler removing underutilised nodes
- Any voluntary disruption

```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
  namespace: production
spec:
  # Option 1: Minimum available Pods
  minAvailable: 2           # At least 2 Pods must always be running

  # Option 2: Maximum unavailable Pods (choose one!)
  # maxUnavailable: 1       # At most 1 Pod can be down at any time

  selector:
    matchLabels:
      app: web-app
```

```bash
kubectl apply -f pdb.yaml

# See the PDB status
kubectl get pdb web-app-pdb
# NAME          MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
# web-app-pdb   2               N/A               1                     5m
# "1 disruption allowed" = you have 3 Pods and min is 2, so 1 can be taken down.

# When draining a node:
kubectl drain worker-2 --ignore-daemonsets
# If draining would violate the PDB: drain WAITS until it can proceed safely
# evicting pod web-app-abc123
# error: Cannot evict pod as it would violate the pod's disruption budget.
# (Kubernetes waits for another Pod to start before evicting this one)
```

---

## Part 5: Blue-Green Deployments — The Whole Harbour Switch 🔵🟢

Sometimes you want an even more controlled switch. Blue-Green means running both versions simultaneously, then switching ALL traffic at once:

```yaml
# Blue deployment (current production)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app-blue
spec:
  replicas: 5
  selector:
    matchLabels:
      app: web-app
      slot: blue
  template:
    metadata:
      labels:
        app: web-app
        slot: blue
        version: v1
    spec:
      containers:
      - name: web-app
        image: my-app:v1

---
# Green deployment (new version, running but not serving)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app-green
spec:
  replicas: 5
  selector:
    matchLabels:
      app: web-app
      slot: green
  template:
    metadata:
      labels:
        app: web-app
        slot: green
        version: v2
    spec:
      containers:
      - name: web-app
        image: my-app:v2
```

```yaml
# Service points to BLUE:
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  selector:
    app: web-app
    slot: blue          # <- all traffic goes to blue
  ports:
  - port: 80
    targetPort: 8080
```

```bash
# Deploy green, test it with direct access:
kubectl apply -f web-app-green.yaml
kubectl port-forward deployment/web-app-green 8080:8080
# Test manually. Run integration tests. Happy? Switch.

# THE SWITCH: Update Service selector from blue to green
kubectl patch service web-app -p '{"spec":{"selector":{"slot":"green"}}}'
# ALL traffic switches instantly. Zero downtime. One command.

# Something wrong? Switch back instantly:
kubectl patch service web-app -p '{"spec":{"selector":{"slot":"blue"}}}'
# Back to blue in milliseconds. Rollback time: < 1 second.

# Green confirmed good? Scale down blue:
kubectl scale deployment web-app-blue --replicas=0
```

---

## Canary Releases: Test with Real Traffic 🐦

A canary release sends a PERCENTAGE of traffic to the new version:

```bash
# Blue: 9 replicas (90% of traffic)
# Canary: 1 replica (10% of traffic)
# Service selects BOTH with label: app=web-app

kubectl scale deployment web-app-blue --replicas=9
kubectl scale deployment web-app-canary --replicas=1

# The Service routes to all Pods with label app=web-app
# 10 pods total: 1 canary pod gets ~10% of requests
# Monitor errors, latency on the canary

# Happy? Gradually increase canary:
kubectl scale deployment web-app-blue --replicas=5
kubectl scale deployment web-app-canary --replicas=5   # 50/50

kubectl scale deployment web-app-blue --replicas=0
kubectl scale deployment web-app-canary --replicas=10  # 100% canary

# Clean up:
kubectl delete deployment web-app-blue
```

---

## The Complete Zero-Downtime Deployment YAML 🏆

```yaml
# production-deployment.yaml -- The gold standard
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
  annotations:
    kubernetes.io/change-cause: "v2.1.0 -- performance improvements, CVE-2024-1234 patched"
spec:
  replicas: 5
  revisionHistoryLimit: 5

  selector:
    matchLabels:
      app: web-app

  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0          # Never reduce capacity during update
      maxSurge: 2                # Allow 2 extra Pods during update

  template:
    metadata:
      labels:
        app: web-app
        version: "2.1.0"

    spec:
      terminationGracePeriodSeconds: 60

      containers:
      - name: web-app
        image: my-company/web-app:2.1.0
        ports:
        - containerPort: 8080

        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "1000m"
            memory: "512Mi"

        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]  # Allow iptables to drain

        startupProbe:
          httpGet:
            path: /healthz
            port: 8080
          failureThreshold: 20
          periodSeconds: 5

        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          periodSeconds: 15
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          periodSeconds: 5
          failureThreshold: 3
          successThreshold: 2

---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
  namespace: production
spec:
  minAvailable: 3     # Always at least 3 of 5 Pods running
  selector:
    matchLabels:
      app: web-app
```

---

## The Deployment Playbook: How to Ship Safely 📋

```bash
# 1. Check current state before you start
kubectl get deployments,pods,hpa -n production
kubectl rollout history deployment/web-app -n production

# 2. Apply the new version
kubectl apply -f production-deployment.yaml

# 3. Watch the rollout
kubectl rollout status deployment/web-app -n production
# Waiting for deployment "web-app" rollout to finish: 2 out of 5 new replicas updated...
# Waiting for deployment "web-app" rollout to finish: 4 out of 5 new replicas updated...
# deployment "web-app" successfully rolled out

# 4. Verify the new version is running
kubectl get pods -n production -l app=web-app -o jsonpath='{.items[*].spec.containers[0].image}'
# my-company/web-app:2.1.0 x5

# 5. Check error rates in your monitoring dashboard
# (This is where you integrate with Prometheus, Datadog, etc.)

# 6. If something's wrong: ROLLBACK. Immediately. No heroics.
kubectl rollout undo deployment/web-app -n production
```

---

## The Full Harbour: What We Built Together 🗺️

We've come a long way from Episode 1. Let's look at the complete harbour:

```
🌊 KUBERNETES CLUSTER — Container Harbour
│
├── 🏢 Control Plane (Ep.4)
│   ├── kube-apiserver     -- The reception desk for everything
│   ├── etcd               -- The sacred filing cabinet (back it up!)
│   ├── kube-scheduler     -- 18-step algorithm to place every Pod
│   └── kube-controller-manager -- Never stops checking if desired = actual
│
├── 🏗️  Worker Nodes (Ep.3)
│   ├── kubelet           -- The quay foreman
│   ├── kube-proxy        -- The network crew
│   └── containerd        -- The forklift that actually runs containers
│
├── 📦 Pods (Ep.2)          -- Freight containers. Born to die. That's OK.
├── 🔄 Deployments (Ep.5)   -- Forklift operators who never sleep
├── 🎭 StatefulSets (Ep.14) -- Reserved berths for demanding databases
├── 🌙 CronJobs (Ep.13)     -- The night shift that never calls in sick
│
├── 🚦 Services (Ep.6)      -- The harbour gates. Stable addresses.
├── 🛃 Ingress (Ep.7)       -- One customs office. Infinite routes. One bill.
│
├── 📋 ConfigMaps (Ep.8)    -- The unsealed cargo manifests
├── 🔐 Secrets (Ep.8)       -- The SEALED cargo manifests
├── 🏭 Persistent Volumes (Ep.9) -- The long-term warehouse
│
├── 🪪 RBAC (Ep.10)         -- The ID badge system. Dave gets READ ONLY.
├── 🩺 Probes (Ep.11)       -- Health inspectors. Mandatory.
├── 📈 Autoscaling (Ep.12)  -- The harbour that grows and shrinks itself
│
└── 🌅 Zero-Downtime (Ep.15) -- Ships leave gracefully. Always.
```

---

## The Harbourmaster's Final Log 📋

*It is the last entry. The harbour is running. Fifteen episodes, fifteen components, one coherent whole.*

*The team that started this journey didn't know what a Pod was. Now they write Deployments from memory, debug RBAC issues without Stack Overflow, and wake up to Slack messages that say "autoscaler handled it, no action required."*

*We deployed to production at 2pm on a Tuesday. The team was in a retro. I watched the rollout complete on my phone under the table. Nobody noticed.*

*That is the goal. When Kubernetes is working correctly, you don't notice it. The cargo moves. The gates stay open. The health inspectors sign off. The night crew processes the batches. The harbour expands for rush hour and contracts when it's quiet.*

*You notice it only when it's NOT working. And when that happens — you have the tools now. `kubectl describe`. `kubectl logs`. `kubectl rollout undo`. The entire vocabulary of a harbour in your hands.*

*The seagulls, as promised, are not part of the architecture. They were never part of the architecture.*

*Set sail. Build things. Deploy often. Break nothing.*

*Welcome to Container Harbour.* ⚓🚢

---

## What's Next? Your Kubernetes Journey Continues 🗺️

This series covered the fundamentals. The harbour is vast — here's the ocean beyond it:

- **GitOps**: ArgoCD and Flux — deploy by pushing to Git, not running kubectl
- **Service Mesh**: Istio and Linkerd — mTLS between services, traffic shaping, observability
- **Operators**: Custom controllers that automate complex stateful application management
- **Crossplane**: Kubernetes-native cloud infrastructure provisioning (hint: your author knows a lot about this)
- **Observability**: Prometheus + Grafana + Loki — the monitoring harbour watchtower
- **Security**: OPA/Gatekeeper, Falco, image scanning — the harbour security team
- **Multi-cluster**: Federation and fleet management at scale

The container ships keep coming. The harbour keeps growing.

You're ready. ⚓

---

**🎯 Series Key Takeaways — The Complete Picture:**

| Episode | Topic | The One Thing |
|---|---|---|
| 1 | Overview | Kubernetes = the Harbourmaster of your container fleet |
| 2 | Pods | Smallest unit. Ephemeral. Not a container — WRAPS containers. |
| 3 | Nodes & Cluster | Quays and the harbour. Nodes fail; cluster survives. |
| 4 | Control Plane | API Server + etcd + Scheduler + Controller Manager. Back up etcd. |
| 5 | Deployments | Never manage bare Pods. Always use Deployments. Always. |
| 6 | Services | Stable IP for ephemeral Pods. The gate that never moves. |
| 7 | Ingress | One load balancer. Many services. Your CFO will be pleased. |
| 8 | ConfigMaps/Secrets | Never bake config or secrets into images. Never. |
| 9 | Persistent Volumes | Databases need warehouses. emptyDir is not a warehouse. |
| 10 | RBAC | Least privilege. Dave gets read-only. This is non-negotiable. |
| 11 | Probes | Running ≠ Ready ≠ Alive. Test all three. In production. Always. |
| 12 | Autoscaling | HPA scales Pods. Cluster Autoscaler scales Nodes. Sleep better. |
| 13 | Jobs/CronJobs | Every crontab you have belongs in a CronJob. |
| 14 | StatefulSets | Databases are divas. Give them reserved berths and stable identity. |
| 15 | Zero Downtime | `maxUnavailable: 0`, readiness probes, preStop hook, PDB. All five. |

*Thank you for sailing with Container Harbour. May your Pods always pass their readiness probes.* 🚢⚓
