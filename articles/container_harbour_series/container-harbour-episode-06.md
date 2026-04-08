---
title: "Welcome to Container Harbour! 🚢 Ep.6"
part: 6
published: false
description: "Episode 6: The Harbour Gates — Services and How Traffic Gets In. Pod IPs change every five minutes. Services don't. That's literally the entire genius."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-06.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 6: The Harbour Gates — Services and How Traffic Flows In 🚦

### The Pod IP Address Problem Is Going to Make You CRY 😭

OK. Your Deployment is running. Three beautiful Pods. You're feeling good. You feel like a Kubernetes PROFESSIONAL.

Then someone asks: "What's the URL of your application?"

You check the Pod IPs.

```bash
kubectl get pods -o wide
# NAME                    IP
# web-app-abc123          10.244.1.5
# web-app-def456          10.244.2.8
# web-app-ghi789          10.244.3.2
```

"It's... one of these three?" you say. "Pick one. 10.244.1.5 probably?"

WRONG. For three reasons:

1. **Which one?** There are THREE Pods. Traffic should go to ALL of them. Not just one. Load balancing! Hello!
2. **These IPs change.** Every time a Pod dies and gets recreated — new IP. The IP you just gave someone? Gone in five minutes.
3. **External traffic can't reach Pod IPs.** These are internal cluster IPs. They don't exist outside the cluster.

You're standing at a harbour where the quays keep MOVING and the addresses keep CHANGING and you're trying to tell ships where to dock by GUESSING.

This is where **Services** come in. And they are BEAUTIFUL. 🌟

---

## The SIPOC of a Service 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who defines the Service? | You, your platform team, Helm charts |
| **Input** | What goes in? | A label selector pointing to target Pods |
| **Process** | What does the Service do? | Maintains a stable IP/DNS name, load-balances traffic across matching Pods |
| **Output** | What comes out? | A single stable endpoint that routes to healthy Pods |
| **Consumer** | Who uses it? | Other Pods, Ingress controllers, external users, your monitoring stack |

---

## What a Service Actually Is 🎯

A Service gives your Pods a **stable identity**. A fixed address. A name that doesn't change even when every single Pod behind it gets replaced.

Think of the harbour gate. The physical gate doesn't move even if the ships behind it change every day. Ships coming IN always go through Gate 7. Gate 7 figures out which berth to send them to. Gate 7 is always there. Always at the same location. The berths? Those change. The gate? Never.

```
External traffic
      |
      v
🚦 Service: "web-app"
   Stable IP: 10.96.45.12
   Stable DNS: web-app.default.svc.cluster.local
      |
      |--- load balances to --->  📦 Pod: 10.244.1.5 (web-app-abc123)
      |                           📦 Pod: 10.244.2.8 (web-app-def456)
      |                           📦 Pod: 10.244.3.2 (web-app-ghi789)

# Pod abc123 dies. New pod web-app-jkl012 with IP 10.244.1.9 appears.
# The SERVICE IP? Still 10.96.45.12. Nothing changed from the outside. 🎩
```

---

## How Services Find Pods: Label Selectors 🏷️

A Service doesn't care about specific Pod names or IPs. It uses **labels**. Any Pod with the matching labels gets included automatically.

```yaml
# Your Deployment gave every Pod this label:
labels:
  app: web-app

# Your Service finds Pods using that label:
selector:
  app: web-app
```

```bash
# Labels are how everything connects in Kubernetes.
# See the labels on your Pods:
kubectl get pods --show-labels
# NAME                    LABELS
# web-app-abc123          app=web-app,pod-template-hash=7d9f8b4c9f
# web-app-def456          app=web-app,pod-template-hash=7d9f8b4c9f

# See which Pods a Service is routing to (the Endpoints):
kubectl get endpoints web-app
# NAME      ENDPOINTS                                       AGE
# web-app   10.244.1.5:80,10.244.2.8:80,10.244.3.2:80    5m
```

When a Pod dies, its IP disappears from the Endpoints list. When a new Pod appears with the matching label, its IP gets ADDED. The Service always points to exactly the healthy Pods. 🪄

---

## The Three Types of Service: Gate Options 🔑

### Type 1: ClusterIP — The Internal Gate 🏠

Default type. Only accessible **inside** the cluster. Other Pods can reach it. External traffic cannot.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  type: ClusterIP           # Default. Internal only.
  selector:
    app: web-app
  ports:
  - protocol: TCP
    port: 80                # Port on the Service (what callers use)
    targetPort: 80          # Port on the Pod (what your app listens on)
```

```bash
kubectl apply -f service-clusterip.yaml

kubectl get service web-app
# NAME      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
# web-app   ClusterIP   10.96.45.12    <none>        80/TCP    5s

# Test it from INSIDE the cluster:
kubectl run test-pod --image=busybox --rm -it --restart=Never -- wget -O- http://web-app
# Downloads the nginx page! The Service DNS works!
```

DNS for services inside the cluster follows this pattern:
`<service-name>.<namespace>.svc.cluster.local`

So `web-app` in the `production` namespace is reachable at:
`web-app.production.svc.cluster.local`

From the SAME namespace? Just `web-app` works. No need for the full address. Kubernetes is helpful like that. 🤝

---

### Type 2: NodePort — The Gate With a Door on the Outside 🚪

Exposes the Service on a specific port on **every node** in the cluster. External traffic can reach it through `<NodeIP>:<NodePort>`.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app-nodeport
spec:
  type: NodePort
  selector:
    app: web-app
  ports:
  - protocol: TCP
    port: 80             # ClusterIP port (internal)
    targetPort: 80       # Pod port (your app)
    nodePort: 30080      # External port on every node (30000-32767 range)
```

```bash
kubectl apply -f service-nodeport.yaml

kubectl get service web-app-nodeport
# NAME               TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)
# web-app-nodeport   NodePort   10.96.45.13   <none>        80:30080/TCP

# Access it via any node's IP on port 30080:
curl http://<any-node-ip>:30080

# With minikube:
minikube service web-app-nodeport --url
# http://127.0.0.1:30080
```

NodePort works but it's **not elegant**. It's like telling everyone "come to Rotterdam Harbour, Gate 30080." Possible? Yes. Professional? Questionable. 😬

NodePort is mostly useful for development and testing. For production external access, you want LoadBalancer or Ingress (Episode 7).

---

### Type 3: LoadBalancer — The VIP Entrance 🌟

Provisions an actual **cloud load balancer** (Azure Load Balancer, AWS ELB, GCP CLB) with a public IP. The professional way to expose services externally.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app-lb
spec:
  type: LoadBalancer
  selector:
    app: web-app
  ports:
  - protocol: TCP
    port: 80           # Public-facing port
    targetPort: 80     # Pod port
```

```bash
kubectl apply -f service-loadbalancer.yaml

# Watch for the external IP to be assigned (takes 30-90 seconds in cloud)
kubectl get service web-app-lb --watch
# NAME         TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)
# web-app-lb   LoadBalancer   10.96.45.14   <pending>       80:31234/TCP
# web-app-lb   LoadBalancer   10.96.45.14   20.123.45.67    80:31234/TCP  <- Got it!

# Now anyone can reach your app at:
curl http://20.123.45.67
# 🎉 Your app is live on the public internet!
```

One LoadBalancer Service = one cloud load balancer = **money**. If you have 20 services that need external access, that's 20 load balancers. That's an expensive harbour gate. 💸

This is why **Ingress** exists (Episode 7) — one load balancer to rule them all.

---

## ExternalName: The Forwarding Address 📬

A fourth, special service type. Not for routing to Pods — for routing to something **outside** the cluster. Like a redirect.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-database
  namespace: production
spec:
  type: ExternalName
  externalName: my-database.azure.com   # The actual external DNS name
```

Now Pods inside the cluster can call `external-database` and get routed to `my-database.azure.com`. Clean DNS aliasing. Useful when migrating services out of the cluster or referencing managed cloud services. 🎯

---

## Headless Services: No Gate, Just a Directory 📋

Sometimes you don't WANT load balancing. You want to talk to specific Pods directly — for stateful applications like databases where you need to know which replica you're talking to.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database-headless
spec:
  clusterIP: None        # "None" = headless! No virtual IP assigned.
  selector:
    app: database
  ports:
  - port: 5432
```

```bash
# With a headless service, DNS returns the IPs of ALL matching Pods directly:
kubectl run test --image=busybox --rm -it --restart=Never -- nslookup database-headless
# Name:     database-headless.default.svc.cluster.local
# Address:  10.244.1.8   <- pod 1 IP
# Address:  10.244.2.4   <- pod 2 IP
# Address:  10.244.3.1   <- pod 3 IP
# (All Pod IPs returned — caller picks which one to use)
```

Headless Services are used heavily with **StatefulSets** (Episode 14) where each replica needs a stable individual DNS name. 🎯

---

## Port Forwarding: The Service Bypass for Debugging 🔧

In development, you often want to reach a Service or Pod directly from your laptop without going through an Ingress or NodePort. Port forwarding to the rescue:

```bash
# Forward your laptop's port 8080 to the Service's port 80
kubectl port-forward service/web-app 8080:80

# Now in another terminal:
curl http://localhost:8080   # Talks directly to your Service!

# Or forward directly to a specific Pod:
kubectl port-forward pod/web-app-abc123 8080:80

# Ctrl+C to stop the tunnel
```

This is your development debugging shortcut. Not for production. The Harbourmaster frowns upon tunnels that bypass the official gates. 😤

---

## The Full Picture: Traffic Flow Through the Cluster 🗺️

```
Internet
    |
    v
☁️  Cloud Load Balancer (if LoadBalancer type)
    |
    v
🚦 Service (kube-proxy maintains iptables rules on every node)
    |
    |--- 33% --->  📦 Pod: web-app-abc123 (Node 1)
    |--- 33% --->  📦 Pod: web-app-def456 (Node 2)
    |--- 33% --->  📦 Pod: web-app-ghi789 (Node 3)
```

**kube-proxy** is what makes Services work at the network level. It runs on every node and maintains `iptables` (or `ipvs`) rules that redirect traffic from the Service's virtual IP to the actual Pod IPs. When Pods change, kube-proxy updates the rules. All behind the scenes. You never touch it directly.

```bash
# See all Services in your cluster
kubectl get services --all-namespaces

# Get detailed info about a Service
kubectl describe service web-app
# Pay attention to:
#   - Selector: what labels it matches
#   - Endpoints: which Pod IPs are currently routed to
#   - Port: the mapping

# See the Endpoints object separately
kubectl get endpoints web-app
```

---

## The Harbourmaster's Log — Entry 6 📋

*Added Services to the harbour today. Gave every gate a permanent number.*

*Before Services: "I dunno, try 10.244.1.5, or maybe 10.244.2.8, one of those should work, unless they've been recreated since breakfast."*

*After Services: "Hit port 80 on web-app. It'll get there. Always."*

*Someone asked me how the Service knows which Pods are healthy. I explained label selectors and Endpoints. They asked why we don't just use IP addresses directly. I explained that Pod IPs change constantly.*

*They looked horrified. I said: "That's why we're having this conversation."*

*Three developers deleted their bookmark for `http://10.244.1.5` and replaced it with `http://web-app.production.svc.cluster.local`. Progress.* 🎩

---

## Your Mission, Should You Choose to Accept It 🎯

1. Create a Deployment with 3 replicas of `nginx:latest`
2. Create a ClusterIP Service for it
3. Prove it works by exec-ing into a test Pod and curling the Service DNS name
4. Watch the Endpoints update in real time as you kill and replace Pods:

```bash
# Terminal 1: Watch Endpoints change
kubectl get endpoints web-app --watch

# Terminal 2: Kill a Pod
kubectl delete pod web-app-abc123

# See the IP disappear from Endpoints, then a new one appear!
```

5. **Bonus:** Create a NodePort Service and access your application from outside the cluster (use `minikube service` or the node IP directly)

---

## Next Time on "Welcome to Container Harbour" 🎬

In **Episode 7**, we tackle the **Customs Office** — the **Ingress controller**. Because having one LoadBalancer per Service is expensive, and having NodePorts everywhere is embarrassing. Ingress gives you ONE entrance point with intelligent routing: this path goes here, that domain goes there, TLS terminates here. One gate. Infinite destinations. 🛃

---

*P.S. — When you call `web-app.default.svc.cluster.local`, that DNS name is resolved by **CoreDNS** — a small DNS server running inside your cluster as a Deployment. Yes, there's a Kubernetes Deployment managing the DNS that makes your Services work. Kubernetes all the way down.* 🐢

---

**🎯 Key Takeaways:**

- Pod IPs are **ephemeral**. Services are **stable**. Always use Services for communication.
- Services find Pods via **label selectors** — no hardcoded IPs, ever.
- **ClusterIP** = internal only. Default. For Pod-to-Pod communication.
- **NodePort** = exposes on a port on every node. Works. Not pretty. 
- **LoadBalancer** = gets a real public IP from your cloud provider. Costs money per service.
- **ExternalName** = DNS alias to an external resource. For cloud-managed services.
- **Headless** = no virtual IP, DNS returns Pod IPs directly. For StatefulSets and databases.
- `kubectl port-forward` = your development debugging tunnel. Not for production. Ever.
- **kube-proxy** does the actual network magic, invisibly, on every node. 🪄
