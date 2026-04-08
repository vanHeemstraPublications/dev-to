---
title: "Welcome to Container Harbour! 🚢 Ep.12"
part: 12
published: false
description: "Episode 12: Rush Hour at the Harbour — Autoscaling Under Pressure. Traffic doubled overnight and nobody woke up. HPA, VPA, and Cluster Autoscaler explained."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-12.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 12: Rush Hour at the Harbour — Autoscaling Under Pressure 📈

### The Night Traffic Tripled and NOBODY Woke Up 🌙

3:47am. A major news outlet shared our link. Traffic went from 500 requests/second to 1,800 in four minutes.

Old world: servers would collapse. On-call engineer would get paged. Panicked scaling. Users angry. Post-mortem on Monday.

New world (our world, with Kubernetes autoscaling): traffic hits. CPU spikes. HPA notices. Creates 12 new Pods. Cluster Autoscaler notices nodes are full. Provisions two new nodes. New Pods land on new nodes. Traffic handled. Nobody woke up. New Pods confirmed healthy.

By 5am, traffic normalised. HPA scaled back down. Cluster Autoscaler removed the extra nodes. Cloud bill returned to normal.

I found out about this event the next morning. From a graph. Not from a pager.

I went back to sleep.

This is autoscaling. 😎

---

## The SIPOC of Autoscaling 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who triggers scaling? | Metrics Server (CPU/memory), Prometheus (custom metrics), KEDA (events) |
| **Input** | What signals scaling? | CPU utilisation, memory pressure, queue depth, request rate |
| **Process** | What happens? | HPA adjusts replica count; Cluster Autoscaler adds/removes nodes |
| **Output** | What comes out? | More capacity when needed, less when not. Automatically. |
| **Consumer** | Who benefits? | Your users (no downtime), your finance team (no wasted capacity) |

---

## Three Autoscalers, Three Jobs 🎯

```
📊 Metrics Server
   "Collecting CPU and memory metrics from every Pod and Node"
          |
          v
🔄 HPA (Horizontal Pod Autoscaler)
   "Adjusting the NUMBER of Pods based on metrics"
   "Traffic up? More Pods. Traffic down? Fewer Pods."
          |
          v
📐 VPA (Vertical Pod Autoscaler)
   "Adjusting the SIZE of Pods based on actual usage"
   "This Pod needs more memory. Update its requests/limits."
          |
          v
🏗️  Cluster Autoscaler
   "Adjusting the NUMBER of NODES based on Pod scheduling needs"
   "Pods can't be scheduled? Add a node. Nodes are empty? Remove them."
```

---

## Prerequisites: Metrics Server 📊

HPA needs metrics. Metrics Server collects them:

```bash
# Install Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# In minikube:
minikube addons enable metrics-server

# Verify it's working (may take 60 seconds):
kubectl top nodes
# NAME       CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
# worker-1   180m         9%     1823Mi          47%

kubectl top pods
# NAME              CPU(cores)   MEMORY(bytes)
# web-app-abc123    12m          45Mi
```

---

## HPA: The Horizontal Pod Autoscaler 🔄

HPA watches metrics and adjusts replica count. Here's the simplest form:

```yaml
# hpa-cpu.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app           # Scale THIS Deployment

  minReplicas: 3            # Never fewer than 3 (maintain availability)
  maxReplicas: 20           # Never more than 20 (control costs)

  metrics:
  # Scale on CPU usage:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70    # Keep average CPU at 70%. More? Scale up. Less? Scale down.

  # Scale on memory too:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60     # Wait 60s before scaling up again
      policies:
      - type: Pods
        value: 4                          # Add max 4 pods at a time
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300    # Wait 5 min before scaling down (prevents flapping!)
      policies:
      - type: Percent
        value: 25                         # Remove max 25% of pods at a time
        periodSeconds: 60
```

```bash
kubectl apply -f hpa-cpu.yaml

# See HPA status:
kubectl get hpa web-app-hpa
# NAME          REFERENCE            TARGETS   MINPODS   MAXPODS   REPLICAS
# web-app-hpa   Deployment/web-app   45%/70%   3         20        3

# TARGETS shows: current metric / target metric
# 45%/70% means CPU is at 45%, target is 70%. No need to scale yet.

# Describe for full details:
kubectl describe hpa web-app-hpa
```

---

## Load Testing: Watch HPA in Action 🔥

```bash
# Terminal 1: Watch HPA
kubectl get hpa web-app-hpa --watch

# Terminal 2: Watch Pods
kubectl get pods -l app=web-app --watch

# Terminal 3: Generate load!
kubectl run load-generator \
  --image=busybox:latest \
  --rm -it \
  --restart=Never \
  -- sh -c "while true; do wget -q -O- http://web-app.production.svc.cluster.local; done"

# Watch HPA respond:
# NAME          TARGETS    REPLICAS
# web-app-hpa   45%/70%    3          <- normal
# web-app-hpa   78%/70%    3          <- above target!
# web-app-hpa   78%/70%    5          <- scaling up!
# web-app-hpa   65%/70%    5          <- stabilising
# web-app-hpa   55%/70%    5          <- under control

# Stop the load generator (Ctrl+C)
# Wait 5 minutes (stabilizationWindowSeconds for scale-down)
# web-app-hpa   32%/70%    5
# web-app-hpa   22%/70%    3          <- scaled back down!
```

---

## VPA: The Vertical Pod Autoscaler 📐

HPA adds more Pods. VPA makes each Pod the RIGHT SIZE. Different problem, different tool.

```bash
# Install VPA (not included by default)
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

```yaml
# vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: "Off"     # "Off" = just give recommendations, don't auto-update
    # "Auto" = automatically update Pod resource requests (restarts Pods!)
    # "Initial" = set resources at Pod creation, never update existing Pods

  resourcePolicy:
    containerPolicies:
    - containerName: web-app
      minAllowed:
        cpu: 100m
        memory: 64Mi
      maxAllowed:
        cpu: 2
        memory: 2Gi
```

```bash
kubectl apply -f vpa.yaml

# After running for a while, see VPA recommendations:
kubectl describe vpa web-app-vpa
# Recommendation:
#   Container Recommendations:
#     Container Name:  web-app
#     Lower Bound:     cpu: 100m, memory: 128Mi
#     Target:          cpu: 350m, memory: 256Mi   <- "This is what you should request"
#     Upper Bound:     cpu: 1,    memory: 512Mi
```

Use VPA in `Off` mode first — collect recommendations for a week, then update your Deployment spec. Don't blindly enable `Auto` mode unless you're prepared for Pods to be restarted at any time. 🎓

---

## Cluster Autoscaler: Adding and Removing Nodes 🏗️

When HPA wants more Pods but there's no room on existing nodes, Cluster Autoscaler provisions new nodes. When nodes are underutilised, it removes them.

```bash
# In AKS, enable Cluster Autoscaler at cluster creation:
az aks create \
  --resource-group my-rg \
  --name harbour-cluster \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 20 \
  --node-count 5

# Or update existing AKS cluster:
az aks update \
  --resource-group my-rg \
  --name harbour-cluster \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 20
```

```yaml
# The Cluster Autoscaler deployment (if self-managing):
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    spec:
      containers:
      - name: cluster-autoscaler
        image: registry.k8s.io/autoscaling/cluster-autoscaler:v1.28.0
        command:
        - ./cluster-autoscaler
        - --cloud-provider=azure
        - --nodes=3:20:your-node-group-name    # min:max:group
        - --scale-down-delay-after-add=10m     # Wait 10m after adding before considering removal
        - --scale-down-unneeded-time=10m       # Node must be unneeded for 10m before removal
```

```bash
# Watch Cluster Autoscaler logs:
kubectl logs -n kube-system deployment/cluster-autoscaler --tail=50 -f

# See scale events:
kubectl get events -n kube-system | grep -i scale
# Normal  ScaledUpGroup  Scale up: group: workers, max size reached: 10->12
# Normal  ScaleDown      Scale-down: node worker-4 removed (utilization 0.12)
```

---

## KEDA: Event-Driven Autoscaling 🎯

For advanced scenarios — scaling based on queue depth, Kafka lag, database row counts, or HTTP request rate — meet **KEDA** (Kubernetes Event-Driven Autoscaling):

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm install keda kedacore/keda --namespace keda --create-namespace
```

```yaml
# Scale workers based on Azure Service Bus queue depth
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: queue-worker-scaler
spec:
  scaleTargetRef:
    name: queue-worker-deployment
  minReplicaCount: 0          # Can scale to ZERO when queue is empty!
  maxReplicaCount: 50
  triggers:
  - type: azure-servicebus
    metadata:
      queueName: harbour-jobs
      messageCount: "5"       # 1 worker per 5 messages in queue
      connectionFromEnv: SERVICEBUS_CONNECTION_STRING
```

With KEDA, your queue workers can scale from 0 to 50 Pods based on queue depth, and back to 0 when the queue is empty. Zero idle cost. 💰

---

## The Harbourmaster's Log — Entry 12 📋

*Traffic event at 3:47am. 260% traffic spike lasting 80 minutes.*

*HPA scaled from 5 to 17 Pods in 4 minutes. Cluster Autoscaler added 2 nodes in 6 minutes.*

*Average response time stayed under 200ms throughout.*

*No alerts fired. No engineers paged. No post-mortem needed.*

*I found out from the Monday morning metrics review.*

*Someone asked if we should set up an alert for traffic spikes. I said: "Only if the autoscaler can't handle it. If it handles it — that's just the harbour doing its job."*

*This is the moment you know Kubernetes is working.* 🎩

---

## Your Mission 🎯

1. Deploy a CPU-intensive app with explicit resource requests:
```yaml
resources:
  requests:
    cpu: "200m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

2. Create an HPA targeting 50% CPU utilisation, min 2, max 10 replicas

3. Generate load with a busybox loop

4. Watch the HPA scale up

5. Stop the load generator and watch the HPA scale back down (5-minute cooldown)

**Bonus:** Set `minReplicas: 0` and use KEDA to scale your Deployment based on a simple HTTP metric or a counter.

---

## Next Time 🎬

**Episode 13**: The Night Shift Nobody Talks About — **Jobs and CronJobs**. For the cargo that only arrives on Tuesdays at 3am. 🌙

---

**🎯 Key Takeaways:**

- **HPA** scales the NUMBER of Pods based on CPU/memory/custom metrics. Horizontal = more Pods.
- **VPA** scales the SIZE of Pods (resource requests/limits). Vertical = bigger Pods.
- **Cluster Autoscaler** scales the NUMBER of NODES. Infrastructure level.
- **KEDA** = event-driven scaling. Scale to zero. Scale on queue depth. The modern choice.
- Always set `minReplicas >= 2` for production availability (one Pod is always a single point of failure).
- `stabilizationWindowSeconds` for scale-down prevents expensive flapping. Default: 300s.
- Metrics Server is required for HPA. Install it first. Check it works with `kubectl top pods`.
- VPA `Off` mode for a week of data collection before enabling `Auto`. Don't be impatient. 📊
