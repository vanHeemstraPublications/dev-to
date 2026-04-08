---
title: "Welcome to Container Harbour! 🚢 Ep.16"
part: 16
published: false
description: "Episode 16: The Shipyard Foreman — Jenkins on Kubernetes. Static build servers are over. Every pipeline run gets its own fresh pod, self-destructs when done, and never fights with anyone over shared tools."
tags: [kubernetes, jenkins, devops, cicd]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-16.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 16: The Shipyard Foreman 🔧

### The Build Server That Has Been Running Since 2019 😬

Let me tell you about a build server I once knew.

Nobody knew who set it up. Somebody’s initials were carved into a config file dated February 2019. The machine had Maven 3.2 on it — not because anyone chose Maven 3.2, but because that’s what was on it when someone `apt-get install`-ed it during the Obama administration and nobody had touched it since.

It also had Node 10. Node. *Ten.* A version of Node so old it remembers when `npm install` only took two minutes.

Three teams shared this machine. Team A liked Java 11. Team B *needed* Java 17. Team C was somehow still on Java 8 and had made their peace with God about it. Every Friday afternoon, someone would push a build and it would mysteriously fail because Team B had overwritten the `JAVA_HOME` during *their* build, which ran at the exact same time as Team A’s, because the scheduler had no idea what isolation meant.

And you know what the fix was? The heroic, production-grade, enterprise-approved solution?

A shared spreadsheet. With build time slots. *Colour-coded.*

I am not making this up. 😩

Today we fix this. Welcome to Jenkins on Kubernetes — where every build gets its own pod, its own tools, its own filesystem, and its own glorious moment of existence. And when it’s done? Gone. Like it never happened. No mess. No shared state. No spreadsheet.

-----

## The SIPOC of the Shipyard Foreman 🗂️

|            |                       |Detail                                                                                                                  |
|------------|-----------------------|------------------------------------------------------------------------------------------------------------------------|
|**Supplier**|Who triggers the build?|Developer push, PR webhook, schedule, upstream pipeline                                                                 |
|**Input**   |What goes in?          |`Jenkinsfile` pipeline definition, source code, pod template spec                                                       |
|**Process** |What happens?          |Jenkins controller schedules a pod → Kubernetes spins it up → JNLP agent connects back → stages execute → pod terminates|
|**Output**  |What comes out?        |Build artifacts, test reports, Docker images, deployment triggers                                                       |
|**Consumer**|Who benefits?          |Developers (fast feedback), ops (no idle agents), finance (zero idle compute cost)                                      |

-----

## The Harbour Metaphor: Static Vs. Dynamic Berths 🚢

In the old world, Jenkins used **static agents** — permanent virtual machines or bare-metal servers, always running, always waiting. Like reserving a specific berth at the harbour for each ship, whether or not any ship is using it. The berth for the *Rotterdam Express* sits empty on Tuesday, Wednesday, and Thursday. You’re still paying dock fees.

The new model: **dynamic pod agents**. The harbour has no reserved berths. When a ship arrives (a pipeline triggers), the harbourmaster spins up a fresh berth on demand. The ship docks, unloads, loads, and leaves. The berth evaporates. The next ship gets a brand-new berth — clean, correctly configured, never contaminated by whatever the previous ship was carrying.

|Static Agents (The Old World)              |Dynamic Pod Agents (The New World)        |
|-------------------------------------------|------------------------------------------|
|Always running, always costing money       |Exist only during a build                 |
|Shared tools — version conflicts guaranteed|Each pod has exactly the tools it declares|
|One build breaks the agent for everyone    |Total isolation — your mess is your own   |
|Manual scaling (buy more servers)          |Kubernetes scales automatically           |
|“Works on my machine” is back              |Fresh environment = reproducible builds   |
|The colour-coded spreadsheet 😰             |No spreadsheet. Ever.                     |

-----

## The Architecture: Three Characters, One Story 🎭

Understanding Jenkins on Kubernetes means understanding three players and how they talk to each other.

```
┌─────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                │
│                                                     │
│  ┌─────────────────────────┐                        │
│  │   Jenkins Controller    │  ← the boss            │
│  │   Pod (StatefulSet)     │    schedules jobs,     │
│  │   Port 8080 (UI)        │    holds config,       │
│  │   Port 50000 (JNLP)     │    never does builds   │
│  │   PVC → /var/jenkins_home│                       │
│  └────────────┬────────────┘                        │
│               │ "hey, I need an agent"              │
│               ▼  Kubernetes API                     │
│  ┌─────────────────────────┐                        │
│  │  Dynamic Agent Pod      │  ← spun up per build   │
│  │  ┌──────────────────┐   │    lives for one job,  │
│  │  │  jnlp container  │   │    then self-destructs │
│  │  │  (the connector) │   │                        │
│  │  ├──────────────────┤   │                        │
│  │  │  build container │   │                        │
│  │  │  (your tools)    │   │                        │
│  │  └──────────────────┘   │                        │
│  └─────────────────────────┘                        │
└─────────────────────────────────────────────────────┘
```

**The Jenkins Controller** is the harbourmaster. It lives in a StatefulSet, backed by a PVC (so config and job history survive pod restarts), and it never actually builds anything. It schedules. It delegates. It sits in its tower with a coffee and points at things.

**The Kubernetes Plugin** is the translator. Installed in Jenkins, it speaks both Jenkins (jobs, pipelines, labels) and Kubernetes (pods, containers, namespaces). When Jenkins says “I need an agent with Node 18 and a Maven sidecar,” the plugin turns that into a pod spec and fires it at the Kubernetes API.

**The Dynamic Agent Pod** is the temporary crew. It runs for exactly one build. It contains at minimum one `jnlp` container (the mandatory connector that phones home to the controller) and however many build containers your `Jenkinsfile` declares. When the build finishes, Kubernetes deletes it. Clean. Gone. Beautiful.

> 🔑 **The golden rule:** The `jnlp` container is non-negotiable. It must be present in every agent pod, and it must be named exactly `jnlp`. Miss this and your build hangs at “Waiting for agent to connect” for ten minutes before timing out, and you will feel things.

-----

## Part 1 — Deploy the Jenkins Controller with Helm

### Step 1 — Prerequisites

```bash
# You need a running Kubernetes cluster (kind, minikube, or real)
# And Helm 3+
helm version
# version.BuildInfo{Version:"v3.x.x", ...}

# Add the official Jenkins Helm repo
helm repo add jenkins https://charts.jenkins.io
helm repo update
```

### Step 2 — Namespace and RBAC

Jenkins needs permission to create and delete pods in its namespace. Without this, the Kubernetes plugin cannot provision agent pods and your builds will sit in a queue forever, like a ship in a harbour with no available berths.

```yaml
# jenkins-rbac.yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: jenkins
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jenkins
  namespace: jenkins
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: jenkins-agent-runner
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "pods/exec"]
    verbs: ["create", "delete", "get", "list", "watch", "patch"]
  - apiGroups: [""]
    resources: ["secrets", "configmaps"]
    verbs: ["get", "list"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: jenkins-agent-runner-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: jenkins-agent-runner
subjects:
  - kind: ServiceAccount
    name: jenkins
    namespace: jenkins
```

```bash
kubectl apply -f jenkins-rbac.yaml
```

### Step 3 — Persistent Storage

The controller’s home directory (`/var/jenkins_home`) holds all your jobs, credentials, plugin configs, and build history. It must survive pod restarts.

```yaml
# jenkins-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jenkins-pvc
  namespace: jenkins
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  # Use your cluster's default StorageClass, or name one explicitly:
  # storageClassName: standard
```

```bash
kubectl apply -f jenkins-pvc.yaml
```

### Step 4 — Helm values

Create a `jenkins-values.yaml` to wire everything together — the ServiceAccount, the PVC, the Kubernetes Cloud configuration, and the initial plugin list.

```yaml
# jenkins-values.yaml
controller:
  serviceType: LoadBalancer       # Use NodePort for local clusters (kind/minikube)
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"

  # The Kubernetes plugin must be installed for dynamic agents to work
  installPlugins:
    - kubernetes:latest
    - workflow-aggregator:latest   # Pipeline support
    - git:latest
    - configuration-as-code:latest

  # Wire Jenkins to its ServiceAccount so the plugin can call the k8s API
  serviceAccount:
    name: jenkins

persistence:
  enabled: true
  existingClaim: jenkins-pvc

# The Kubernetes Cloud is pre-configured by the Helm chart
# pointing at the in-cluster API server automatically
agent:
  enabled: true
  defaultsProviderTemplate: ""
  namespace: jenkins
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "2000m"
      memory: "2Gi"
```

### Step 5 — Install

```bash
helm install jenkins jenkins/jenkins \
  --namespace jenkins \
  --values jenkins-values.yaml \
  --wait

# Wait for the controller pod to be Ready (this takes 2-3 minutes — first boot)
kubectl get pods -n jenkins -w
# NAME        READY   STATUS    RESTARTS   AGE
# jenkins-0   2/2     Running   0          3m12s

# Retrieve the auto-generated admin password
kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- \
  /bin/cat /run/secrets/additional/chart-admin-password && echo
```

Open the Jenkins UI at the LoadBalancer IP (or `kubectl port-forward svc/jenkins 8080:8080 -n jenkins` for local clusters). Log in with `admin` and the password above.

-----

## Part 2 — Verify the Kubernetes Cloud Configuration

The Helm chart pre-configures the Kubernetes Cloud for you, but always verify.

**Manage Jenkins → Manage Nodes and Clouds → Configure Clouds → Kubernetes**

The key fields:

- **Kubernetes URL**: blank (uses in-cluster config automatically when Jenkins runs inside Kubernetes)
- **Jenkins URL**: `http://jenkins.jenkins.svc.cluster.local:8080`
- **Jenkins tunnel**: `jenkins.jenkins.svc.cluster.local:50000` — this is the JNLP port agents use to phone home

Hit **Test Connection**. You should see `Connected to Kubernetes v1.x.x`. If you see an RBAC error, revisit the ClusterRoleBinding from Step 2.

-----

## Part 3 — Your First Pipeline with a Dynamic Pod Agent

Create a new **Pipeline** job in Jenkins. Paste this `Jenkinsfile`:

```groovy
pipeline {
  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
    resources:
      requests:
        cpu: "200m"
        memory: "256Mi"
  - name: node
    image: node:20-alpine
    command:
    - sleep
    args:
    - infinity
    resources:
      requests:
        cpu: "200m"
        memory: "256Mi"
"""
    }
  }
  stages {
    stage('Verify tools') {
      steps {
        container('node') {
          sh 'node --version'
          sh 'npm --version'
        }
      }
    }
    stage('Do some work') {
      steps {
        container('node') {
          sh 'echo "Hello from a fresh, ephemeral pod. I will be gone when this build ends."'
        }
      }
    }
  }
}
```

Click **Build Now**. While it runs, open a second terminal:

```bash
# Watch the agent pod appear in real time
kubectl get pods -n jenkins -w

# You'll see something like:
# NAME                         READY   STATUS    RESTARTS   AGE
# jenkins-0                    2/2     Running   0          15m
# jenkins-pipeline-abc12-xyz   0/2     Pending   0          2s
# jenkins-pipeline-abc12-xyz   0/2     Init:0/1  0          4s
# jenkins-pipeline-abc12-xyz   1/2     Running   0          8s
# jenkins-pipeline-abc12-xyz   2/2     Running   0          12s
# ... build runs ...
# jenkins-pipeline-abc12-xyz   0/2     Terminating 0        45s
# (gone)
```

There it is. Born at build start. Dead at build end. No mess. No teardown scripts. No Java 8 haunting your dreams.

> 🔑 **Why `command: sleep` and `args: infinity`?** Your build container needs to stay alive while Jenkins sends it commands. Without this, the container starts, finishes its default entrypoint, and exits — and Jenkins has nothing to run your pipeline steps in.

-----

## Part 4 — Multi-Container Pods: Different Tools Per Stage

The real power of pod-based agents. Each build can have a custom fleet of sidecars — Node for your frontend, Maven for your backend, `kubectl` for deployment — all sharing the same pod filesystem through a workspace volume that the Kubernetes plugin mounts automatically.

```groovy
pipeline {
  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
  - name: maven
    image: maven:3.9-eclipse-temurin-21
    command: [sleep]
    args: [infinity]
  - name: node
    image: node:20-alpine
    command: [sleep]
    args: [infinity]
  - name: kubectl
    image: bitnami/kubectl:latest
    command: [sleep]
    args: [infinity]
    securityContext:
      runAsUser: 1000
"""
    }
  }
  stages {
    stage('Build backend') {
      steps {
        container('maven') {
          sh 'mvn --version'
          sh 'mvn clean package -DskipTests'
        }
      }
    }
    stage('Build frontend') {
      steps {
        container('node') {
          sh 'npm --version'
          sh 'npm ci && npm run build'
        }
      }
    }
    stage('Deploy to staging') {
      steps {
        container('kubectl') {
          sh 'kubectl version --client'
          sh 'kubectl apply -f k8s/staging/'
        }
      }
    }
  }
}
```

Three completely different runtimes. One pod. No Java version wars. No `JAVA_HOME` spreadsheet. Dave from Team B can have his Java 17 and Team C can have their Java 8 and they will never, *ever* interfere with each other again. 🎉

> ⚠️ **The `kubectl` container gotcha:** When your pipeline runs `kubectl apply`, it runs *inside the cluster* as the pod’s ServiceAccount. Make sure that ServiceAccount has permission to apply to your target namespace. The RBAC you set up for Jenkins must cover whatever `kubectl` commands your pipeline runs.

-----

## Part 5 — PVC Caching: Speeding Up Repeat Builds

Ephemeral pods mean ephemeral dependency caches. Every Maven build re-downloads the internet. Every `npm ci` re-installs `node_modules` from scratch. For small projects this is fine; for large ones, you feel it.

The fix: a shared `PersistentVolumeClaim` mounted into your build containers as a cache volume.

```yaml
# build-cache-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: maven-cache
  namespace: jenkins
spec:
  accessModes:
    - ReadWriteMany    # Multiple pods can read/write simultaneously
  resources:
    requests:
      storage: 10Gi
```

```bash
kubectl apply -f build-cache-pvc.yaml
```

Then reference it in your pod spec:

```groovy
pipeline {
  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  volumes:
  - name: maven-cache
    persistentVolumeClaim:
      claimName: maven-cache
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
  - name: maven
    image: maven:3.9-eclipse-temurin-21
    command: [sleep]
    args: [infinity]
    volumeMounts:
    - name: maven-cache
      mountPath: /root/.m2
"""
    }
  }
  stages {
    stage('Build') {
      steps {
        container('maven') {
          // First run: downloads everything. Subsequent runs: cache hit. 🚀
          sh 'mvn clean package -DskipTests'
        }
      }
    }
  }
}
```

> ⚠️ **`ReadWriteMany` requires a compatible StorageClass.** Not all storage backends support it — NFS-based StorageClasses generally do, while `hostPath` and most block storage do not. Check what your cluster offers with `kubectl get storageclass`.

-----

## Part 6 — Kaniko: Building Docker Images Without Docker-in-Docker

Your pipelines probably build Docker images. But inside Kubernetes, running a Docker daemon inside a container (Docker-in-Docker, DIND) is messy, slow, and requires `privileged: true` — which many clusters disallow for good reason.

The solution: **Kaniko**. Kaniko builds Docker images from a `Dockerfile` entirely in userspace, no daemon required, no privileged mode needed.

```groovy
pipeline {
  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    command: [sleep]
    args: [infinity]
    volumeMounts:
    - name: docker-config
      mountPath: /kaniko/.docker
  volumes:
  - name: docker-config
    secret:
      secretName: docker-registry-credentials
      items:
      - key: .dockerconfigjson
        path: config.json
"""
    }
  }
  stages {
    stage('Build and push image') {
      steps {
        container('kaniko') {
          sh """
            /kaniko/executor \
              --context=\$\{WORKSPACE\} \
              --dockerfile=Dockerfile \
              --destination=registry.example.com/myapp:\$\{BUILD_NUMBER\} \
              --cache=true
          """
        }
      }
    }
  }
}
```

The `docker-registry-credentials` Secret contains your registry authentication. Create it once:

```bash
kubectl create secret docker-registry docker-registry-credentials \
  --docker-server=registry.example.com \
  --docker-username=myuser \
  --docker-password=mypassword \
  --namespace=jenkins
```

Now your pipelines build and push images with no Docker daemon, no privileged containers, and no hair-pulling. Dave from the platform team who keeps telling you `privileged: true` is a security violation will have nothing to say. This is a good day.

-----

## Common Gotchas: The Harbourmaster’s Warning Log 📋

These are the mistakes everyone makes. Make them quickly and move on.

|Gotcha                                        |Symptom                                             |Fix                                                                        |
|----------------------------------------------|----------------------------------------------------|---------------------------------------------------------------------------|
|Missing `jnlp` container                      |Build queues forever, “Waiting for agent to connect”|Add a container named exactly `jnlp` using `jenkins/inbound-agent`         |
|Wrong Jenkins tunnel address                  |Agent connects but immediately drops                |Set tunnel to `jenkins.jenkins.svc.cluster.local:50000`                    |
|Missing RBAC                                  |“Forbidden” in Jenkins logs when spawning pods      |Apply the ClusterRoleBinding from Part 1                                   |
|`imagePullPolicy: Always` on slow nodes       |45-second pod startup per build                     |Set `imagePullPolicy: IfNotPresent` on build containers                    |
|`ReadWriteOnce` PVC used by concurrent builds |Second build hangs waiting for PVC                  |Use `ReadWriteMany` StorageClass for shared caches                         |
|CPU limits too low                            |Builds 3-4× slower than expected                    |Set `limits.cpu` generously; monitor with `kubectl top pods -n jenkins`    |
|Forgetting `command: sleep` / `args: infinity`|Build container exits before pipeline step runs     |Always add `command: [sleep]` and `args: [infinity]` to non-jnlp containers|

-----

## Your Mission: The Shipyard Exercise 🎯

1. **Deploy Jenkins** into your cluster using the steps above. Retrieve the admin password. Log in.
1. **Verify the cloud connection**: Manage Jenkins → Configure Clouds → Kubernetes → Test Connection. See `Connected`.
1. **Run the first dynamic pipeline**. Watch pods appear and vanish in `kubectl get pods -n jenkins -w`. Marvel at this. It does not get old.
1. **Add a second container** to your pod spec. Pick any image you like — `python:3.12`, `golang:1.22`, `terraform:latest`. Add a stage that runs a command in that container.
1. **Bonus**: Create a Maven or npm build that uses a cache PVC. Run it twice. Compare the build times. The second run should be significantly faster.
1. **Hero move**: Replace a `docker build` stage with Kaniko. Push to a local registry (spin up `registry:2` as a Deployment in your cluster if needed).

-----

## The Key Takeaways ⚓

- Jenkins on Kubernetes replaces static, shared build servers with **ephemeral pods — one per build, deleted on completion**
- The **Kubernetes plugin** bridges Jenkins’s job model to Kubernetes’s pod model; every pipeline run becomes a pod spec
- Every agent pod **must** contain a container named `jnlp` using `jenkins/inbound-agent` — this is the connector, not optional
- Build containers need `command: [sleep]` and `args: [infinity]` to stay alive while Jenkins sends them pipeline steps
- **Multi-container pods** give each stage its own runtime without polluting a shared machine
- The **controller’s PVC** (`/var/jenkins_home`) must survive pod restarts — use a proper StorageClass
- **PVC-backed caches** restore dependency cache warmth without abandoning ephemeral agents
- **Kaniko** eliminates Docker-in-Docker for image builds — no privileged mode required
- Bad RBAC, wrong JNLP tunnel, and missing `sleep` are responsible for 90% of new-setup failures

-----

## Next Time 🎬

**Episode 17**: The Harbour’s Watchdog — **Prometheus and Grafana on Kubernetes**. Your pods are running. Your builds are green. But are they *actually* healthy? Numbers don’t lie. Dashboards don’t sleep. And Dave’s 3am mystery outage is about to get a root cause. 📊

-----

*Welcome to Container Harbour is a series about Kubernetes — explained through the metaphor of a busy freight harbour, with the energy of someone who has been there, debugged that, and lived to write about it.* ⚓
