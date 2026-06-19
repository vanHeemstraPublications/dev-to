---
title: "Agility Game and Detective Operating System with Open Engineering Platform 🕵️🎮 Ep.7"
published: false
description: "Episode 7: It's one thing to design loose coupling on paper. It's another to actually deploy it. This episode walks through deploy/ — two independent Kubernetes Deployments (oep-controller and god-object-detector), their RBAC, their Services, and the MiniKube + Crossplane bootstrap script that brings the whole cluster up from nothing."
tags: [kubernetes, minikube, crossplane, devops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-07.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

## Episode 7: Deploying Two Strangers Into the Same Cluster

## Paper Architecture vs. Real Pods

Six episodes of contracts, CRDs, compositions, and a suspiciously well-behaved HTTP boundary have built a convincing argument on paper. This episode checks whether `deploy/` backs it up with actual, runnable Kubernetes manifests — because a diagram with no Deployment behind it is just modern art.

Good news: it does. `deploy/` contains exactly what the architecture promised — two separate, independently deployable workloads in the same namespace, talking only over Service DNS, with their own RBAC and their own probes.

## 🗂️ SIPOC — The Deployment Layer

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| deploy/minikube/ | A Mac Mini M4 Pro (per INTENT.md) with Docker/Podman available | install.sh installs MiniKube + kubectl; start.sh boots the local cluster | A running local Kubernetes control plane | Everything downstream — Crossplane, the controller, the detector |
| deploy/crossplane/ | A running MiniKube cluster | install.sh installs the Crossplane operator and the function-patch-and-transform function | A cluster that understands Compositions (Episode 4) | The XRefactoringSpace composite and any future composites |
| deploy/controller/ + deploy/god-object-detector/ | Container images, RBAC, Service definitions | kubectl apply -k (kustomize) per component | Two running Deployments in oep-system, each with its own ServiceAccount | Detective Operating System's controller and the Python detector, fully independent of each other's lifecycle |
| deploy/samples/ | The actual domain objects from Episode 1 (Space, Mission, Agent, Evidence) | kubectl apply -f deploy/samples/ | A populated oep-domain namespace, ready for the controller to reconcile | A human running the MVP for the first time, or a CI pipeline doing the same |

## Architecture Diagram: The Full Deployment Topology

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    MiniKube Cluster (local, Mac Mini M4 Pro)             │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    crossplane-system namespace                      │ │
│  │   Crossplane operator + function-patch-and-transform                │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                       oep-system namespace                          │ │
│  │                                                                     │ │
│  │  ┌─────────────────────────────┐   ┌─────────────────────────────┐  │ │
│  │  │ Deployment: oep-controller  │   │ Deployment: god-object-     │  │ │
│  │  │                             │   │             detector        │  │ │
│  │  │ ServiceAccount:             │   │ ServiceAccount:             │  │ │
│  │  │   oep-controller            │   │   god-object-detector       │  │ │
│  │  │                             │   │                             │  │ │
│  │  │ Service :8080 (http)        │   │ Service :8000 (http)        │  │ │
│  │  │ image: oep/controller       │   │ image: oep/god-object-      │  │ │
│  │  │        :0.1.0-SNAPSHOT      │   │        detector:0.1.0-SNAP. │  │ │
│  │  │                             │   │                             │  │ │
│  │  │ env: OEP_DETECTOR_URL ──────┼──►│   (the ONLY coupling:       │  │ │
│  │  │   http://god-object-        │   │    a DNS name in an env var)│  │ │
│  │  │   detector.oep-system.svc.  │   │                             │  │ │
│  │  │   cluster.local:8000        │   │                             │  │ │
│  │  └─────────────────────────────┘   └─────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                       oep-domain namespace                          │ │
│  │   Space: refactoring            Mission: analyze-repository         │ │
│  │   Agent: code-smell-detective   Evidence: source-code-evidence      │ │
│  │   Result: case-file                                                  │ │
│  │   (plain CRD objects — Episode 3 — watched by oep-controller)       │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

Look at where the arrow lives in that diagram: it connects `oep-controller` to `god-object-detector` through a Service DNS name, configured as an **environment variable**, not compiled into either image. Swap the detector's Deployment for a different image entirely — written in Rust, Go, whatever — and as long as the new image answers `POST /detect` with the same JSON shape, `oep-controller`'s container image does not need to be rebuilt, redeployed, or even restarted.

## The Controller's Deployment Manifest

```yaml
# deploy/controller/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oep-controller
  namespace: oep-system
  labels:
    app.kubernetes.io/name: oep-controller
    app.kubernetes.io/part-of: oep
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app.kubernetes.io/name: oep-controller
  template:
    metadata:
      labels:
        app.kubernetes.io/name: oep-controller
        app.kubernetes.io/part-of: oep
    spec:
      serviceAccountName: oep-controller
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: controller
          image: oep/controller:0.1.0-SNAPSHOT
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          env:
            - name: OEP_NAMESPACE
              value: oep-domain
            - name: PORT
              value: "8080"
            - name: OEP_DETECTOR_URL
              value: http://god-object-detector.oep-system.svc.cluster.local:8000
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits:   { cpu: 500m, memory: 512Mi }
          livenessProbe:
            httpGet: { path: /healthz, port: http }
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet: { path: /readyz, port: http }
            initialDelaySeconds: 5
            periodSeconds: 5
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            capabilities:
              drop: ["ALL"]
```

Every hardening line here — `runAsNonRoot`, `readOnlyRootFilesystem`, `capabilities.drop: ["ALL"]` — applies equally to both Deployments in this namespace, and neither owner had to coordinate on writing it twice; it's just the platform team's baseline `securityContext`, copy-pasted (or templated) the same way for any workload that joins `oep-system`. The Python detector's own deployment manifest follows the identical pattern, on its own image, on its own port:

```yaml
# deploy/god-object-detector/deployment.yaml (excerpt)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: god-object-detector
  namespace: oep-system
spec:
  replicas: 1
  template:
    spec:
      serviceAccountName: god-object-detector
      containers:
        - name: detector
          image: oep/god-object-detector:0.1.0-SNAPSHOT
          ports:
            - name: http
              containerPort: 8000
          resources:
            requests: { cpu: 100m, memory: 128Mi }
```

Note what is absent from the detector's manifest: any `env` entry pointing back at `oep-controller`. The detector does not know the controller's DNS name, its namespace, or that it even exists. The dependency is strictly one-directional — Detective Operating System depends on the detector being reachable; the detector depends on nobody.

## Bootstrapping the Whole Cluster, Start to Finish

```bash
# deploy/minikube/install.sh + start.sh — bring up the local cluster
brew install minikube kubectl   # macOS, per the Mac Mini M4 Pro target
minikube start --cpus=4 --memory=8192 --driver=docker

# deploy/crossplane/install.sh — install Crossplane itself
helm repo add crossplane-stable https://charts.crossplane.io/stable
helm install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system --create-namespace

kubectl apply -f https://raw.githubusercontent.com/crossplane-contrib/function-patch-and-transform/main/package.yaml

# Install all five OEP CRDs (Episode 3)
kubectl apply -f crds/space/space.yaml
kubectl apply -f crds/mission/mission.yaml
kubectl apply -f crds/agent/agent.yaml
kubectl apply -f crds/evidence/evidence.yaml
kubectl apply -f crds/result/result.yaml

# Install the Crossplane Composition + XRD (Episode 4)
kubectl apply -f compositions/refactoring-space/xrd.yaml
kubectl apply -f compositions/refactoring-space/composition.yaml
kubectl apply -f compositions/rbac.yaml

# Create the namespaces
kubectl create namespace oep-system
kubectl create namespace oep-domain

# Deploy BOTH runtime components — order does not matter,
# because neither depends on the other being ready first
kubectl apply -k deploy/controller/
kubectl apply -k deploy/god-object-detector/

# Wait for both to report Ready independently
kubectl -n oep-system rollout status deployment/oep-controller
kubectl -n oep-system rollout status deployment/god-object-detector
```

That comment — *"order does not matter, because neither depends on the other being ready first"* — is worth sitting with. `oep-controller`'s readiness probe only checks whether its own Kubernetes client connected; it does not check whether the detector is reachable. If the detector pod is still pulling its image, `oep-controller` happily reports Ready and simply fails individual `handleRunning()` calls (transitioning the affected Mission to `Failed`) until the detector catches up. No crash loop, no deadlock, no circular wait.

## RBAC: Narrow Permissions, Narrow Trust

```yaml
# deploy/controller/rbac.yaml (representative excerpt)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: oep-controller
  namespace: oep-domain
rules:
  - apiGroups: ["oep.io"]
    resources: ["missions", "spaces", "agents", "evidences", "results"]
    verbs: ["get", "list", "watch", "patch"]
  - apiGroups: ["oep.io"]
    resources: ["missions/status", "results/status"]
    verbs: ["patch"]
```

`oep-controller`'s ServiceAccount can read every OEP domain kind and patch status on Missions and Results — and nothing else. It cannot, for instance, delete a Space, modify cluster-wide RBAC, or touch any resource Agility Game's hypothetical controller might create under a different API group. If Agility Game's owner deploys their own controller into the same cluster tomorrow with its own ServiceAccount and its own narrowly-scoped Role, the two RBAC policies sit beside each other exactly as cleanly as the two Deployments do.

## Applying the Sample Domain Objects

```bash
# deploy/samples/ — the actual Space, Agent, Mission, Evidence, Result
kubectl apply -f deploy/samples/space.yaml
kubectl apply -f deploy/samples/agent.yaml
kubectl apply -f deploy/samples/evidence.yaml
kubectl apply -f deploy/samples/mission.yaml
# (Result is typically created by the controller, not applied directly,
#  but a sample exists for reference / manual testing)

# deploy/samples/verify.sh runs exactly the watch loop a human would
kubectl get missions -n oep-domain -w
```

## The Punchline, Restated as a Deployment Fact

**OWNER OF AGILITY GAME:** "So if I wanted to add my own controller to this cluster, I'd just... write my own Deployment, my own ServiceAccount, my own Role, point it at the same CRDs, and not touch a single YAML file in `deploy/controller/` or `deploy/god-object-detector/`?"

**OWNER OF DETECTIVE OPERATING SYSTEM:** "Correct. You could even put it in a third namespace if you wanted extra distance between us. The CRDs are cluster-scoped; the controllers and their RBAC are namespace-scoped. You inherit none of my Deployment's resource limits, none of my container image, none of my crash loops. We'd just both be watching the same five kinds of objects, independently, like two detectives reading the same public police blotter without sharing a desk."

## What's Next: Running One Real Investigation

In **Episode 8**, the finale, we run the entire MVP end to end: `kubectl apply -f deploy/samples/`, watch the Mission crawl through `Pending → Running → Completed`, watch the Result follow it from `Draft → Final`, and read the actual `Case File` that comes out the other end — closing the loop on everything contracts, CRDs, compositions, controllers, and the cross-language HTTP boundary were built to support.

**🔗 Resources**

- **MiniKube**: [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io)
- **Crossplane installation**: [docs.crossplane.io/latest/software/install](https://docs.crossplane.io/latest/software/install/)
- **Kustomize**: [kustomize.io](https://kustomize.io)
- **Kubernetes RBAC**: [kubernetes.io/docs/reference/access-authn-authz/rbac](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

*🕵️🎮 Agility Game and Detective Operating System with Open Engineering Platform — two platforms, zero shared dependencies, one cluster.*