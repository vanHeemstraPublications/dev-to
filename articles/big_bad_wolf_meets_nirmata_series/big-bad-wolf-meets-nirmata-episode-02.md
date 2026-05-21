---
title: "Big Bad Wolf Meets Nirmata 🐺 Ep.2"
part: 2
published: false
description: "Episode 2: Penny built her Kubernetes cluster out of straw — no policies, no admission control, privileged pods as far as the eye can see. The Wolf did not even need to huff. He knocked politely and walked in. This episode explains what Kyverno OSS is, how admission control works, and what happens when you have absolutely none of it."
tags: [kubernetes, kyverno, security, policyascode]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/big-bad-wolf-nirmata-episode-02.png"
series: "Big Bad Wolf Meets Nirmata"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: Straw by Straw

> *“Why would I need policies? My developers are very trustworthy.”*
> — Penny the Promptless, approximately six minutes before the breach

-----

## The Tour of the Straw House 🌾

Penny was, by all accounts, an excellent developer. Her application code was clean, her tests passed, her documentation was thorough. Her Kubernetes cluster, however, looked like someone had assembled it from memory while slightly distracted.

*“It works,”* she said proudly, gesturing at the `kubectl get pods --all-namespaces` output scrolling past like the opening credits of a disaster movie.

```bash
$ kubectl get pods --all-namespaces

NAMESPACE     NAME                          STATUS    SECURITY CONTEXT
production    web-app-7f8d9                 Running   privileged: true ← 🐺
production    database-proxy-3k2j           Running   runAsRoot: true ← 🐺
production    image-processor-9m1x          Running   image: registry.suspicious.io/proc:latest ← 🐺
staging       testing-pod-1234              Running   no resource limits ← 🐺
default       leftover-debug-pod-dont-delete Running   hostNetwork: true ← 🐺🐺🐺
```

Wolfgang the Wolf, standing behind a nearby potted plant wearing reading glasses, took careful notes.

-----

## 🗂️ SIPOC — The Straw House Situation

|**Suppliers**                         |**Inputs**                                          |**Process**                                                                                    |**Outputs**                                                                                  |**Customers**                                     |
|--------------------------------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|--------------------------------------------------|
|Penny (well-meaning, busy)            |`kubectl apply -f whatever.yaml` with no guard rails|Kubernetes API server accepts everything — no validation, no mutation, no admission control    |Every misconfigured pod, every privileged container, every unverified image runs unquestioned|Wolfgang — who can barely believe his luck        |
|Kyverno OSS (what Penny does NOT have)|Policy YAML, admission webhook, cluster connection  |Every create/update/delete call intercepted → evaluated against policies → validated or blocked|Only compliant resources created; all violations logged or rejected                          |What Penny should have — but does not yet         |
|The CISO (off-screen, worried)        |Quarterly security reviews                          |Manual checks, spreadsheet findings, increasingly urgent emails to Penny                       |A growing list of Critical findings and one very tight jaw                                   |Compliance auditors, who are flying in on Thursday|

-----

## What Happens Without Admission Control 🚪

Kubernetes is democratic by design. By default, if you have the right RBAC permissions, you can deploy almost anything. Want a container that runs as root? Fine. Want to mount the host filesystem? Absolutely. Want to pull an image from a registry called `definitely-not-malware.io`? Kubernetes will not even raise an eyebrow.

Admission control is the mechanism that puts sensible adults in charge of this democracy. Without it, every `kubectl apply` is a direct democracy of one: whoever is running the command gets exactly what they ask for, for better or catastrophically worse.

Here is what Wolfgang found in Penny’s cluster:

### Problem 1: Privileged Containers

```yaml
# What Penny deployed (innocently)
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: my-app
    image: my-app:latest
    securityContext:
      privileged: true  # 🐺 This is basically "sudo for containers"
```

A privileged container can escape the container sandbox and access the host system. It is the equivalent of building a house where the front door is a conceptual suggestion rather than a physical barrier.

### Problem 2: Running as Root

```yaml
spec:
  containers:
  - name: my-app
    securityContext:
      runAsUser: 0  # 🐺 Root. UID 0. The maximum-power user.
```

If an attacker compromises this container, they are root inside it. If container isolation has any weakness, they become root outside it too.

### Problem 3: No Resource Limits

```yaml
spec:
  containers:
  - name: resource-goblin
    # No "resources:" section at all
    # 🐺 Can eat 100% of CPU. All of it. Goodbye, other pods.
```

Wolfgang does not even need to breach this cluster. He can deploy one pod that steals all the resources and watches everything else crash.

### Problem 4: Images from Anywhere

```yaml
spec:
  containers:
  - name: app
    image: random-docker-hub-thing:latest  # 🐺 Who maintains this? What is in it?
```

The supply chain wolf rubs his paws together. A `latest` tag that could be updated by anyone. No signature verification. No provenance. Absolutely delightful.

### Problem 5: The Debug Pod That Never Left

```yaml
spec:
  hostNetwork: true      # 🐺 Shares host network stack
  hostPID: true          # 🐺 Sees all host processes
  containers:
  - name: debug
    image: ubuntu:latest
    command: ["/bin/sh", "-c", "sleep infinity"]
    # This was "temporary" in March. It is now November.
```

Wolfgang moved into this one three weeks ago. He has rearranged the furniture.

-----

## Enter Kyverno: The Policy Engine That Should Have Been There 🦸

**Kyverno** (from the Greek κυβερνώ — “to govern”) is a Kubernetes-native policy engine. It is a CNCF project, actively maintained, with over 3 billion downloads. It lives inside your cluster as a set of pods and a **dynamic admission webhook** — which means it is called by the Kubernetes API server on every create, update, and delete operation.

Think of it as the world’s most attentive building inspector. Before any brick is placed in Penny’s house — before any resource is admitted to the cluster — Kyverno reads the blueprints and either approves, modifies, or rejects them.

```
Developer → kubectl apply → Kubernetes API Server
                                      ↓
                             Kyverno Admission Webhook
                                      ↓
                    ┌─────────────────────────────────┐
                    │   Is this resource compliant?   │
                    └─────────────────────────────────┘
                         ↙              ↓              ↘
                    VALIDATE        MUTATE           GENERATE
                  (check rules)  (fix it up)    (create helpers)
                    ↙     ↘           ↓                ↓
                PASS    REJECT    Return fixed      Return new
                  ↓        ↓      resource          resource
               Created  403 Error
```

### Kyverno’s Four Superpowers

**1. Validate — The Inspector’s Checklist ✅**

Block non-compliant resources before they exist:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-containers
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-privileged
    match:
      any:
      - resources:
          kinds: [Pod]
    validate:
      message: "Privileged containers are not allowed. The Wolf says thank you, but we decline."
      pattern:
        spec:
          containers:
          - =(securityContext):
              =(privileged): "false"
```

Wolfgang submits his privileged pod. Kyverno reads it, checks the rule, and returns:

```
Error from server: admission webhook "kyverno-resource.kyverno.svc" denied the request:
policy Pod/default/wolfgangs-pod for resource violations:
  disallow-privileged-containers/check-privileged:
  Privileged containers are not allowed. The Wolf says thank you, but we decline.
```

Wolfgang stares at the terminal. This is new.

**2. Mutate — The Helpful Auto-Corrector 🔧**

Rather than blocking, automatically fix resources to meet standards:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-default-resource-limits
spec:
  rules:
  - name: add-limits
    match:
      any:
      - resources:
          kinds: [Pod]
    mutate:
      patchStrategicMerge:
        spec:
          containers:
          - (name): "*"
            resources:
              limits:
                +(cpu): "500m"
                +(memory): "512Mi"
```

This automatically inserts sensible resource limits on any pod that does not specify them. Even Wolfgang’s debug pod gets limits. He cannot eat all the CPU anymore.

**3. Generate — The Helpful Creator 🏗️**

Automatically create companion resources:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-network-policy-on-namespace-create
spec:
  rules:
  - name: default-deny-all
    match:
      any:
      - resources:
          kinds: [Namespace]
    generate:
      kind: NetworkPolicy
      name: default-deny-all
      namespace: "{{request.object.metadata.name}}"
      data:
        spec:
          podSelector: {}
          policyTypes: [Ingress, Egress]
```

Every time a new namespace is created, a default-deny NetworkPolicy is automatically created alongside it. Wolfgang cannot move laterally between namespaces because the policy was waiting for him before he arrived.

**4. Report — The Paper Trail 📋**

Even in Audit mode (not yet blocking), Kyverno produces Policy Reports:

```yaml
apiVersion: wgpolicyk8s.io/v1alpha2
kind: PolicyReport
results:
- message: "Privileged containers are not allowed."
  policy: disallow-privileged-containers
  resources:
  - kind: Pod
    name: wolfgangs-suspicious-pod
    namespace: default
  result: fail   # 🐺 Found him!
  scored: true
  severity: high
```

-----

## Audit Mode vs Enforce Mode: The Building Inspector’s Modes 🏠

Kyverno policies have two key failure actions:

|Mode       |`validationFailureAction`|What happens                                                      |The Wolf’s experience                               |
|-----------|-------------------------|------------------------------------------------------------------|----------------------------------------------------|
|**Audit**  |`Audit`                  |Violation is logged in Policy Report but resource is still created|“I can still get in, but someone is writing it down”|
|**Enforce**|`Enforce`                |Violation causes the request to be rejected with a 403 error      |“The door is locked. The Wolf cannot enter.”        |

The sensible approach is to start in Audit mode — gather data on existing violations without breaking anything — then flip to Enforce once you understand the blast radius of starting to block things.

```yaml
spec:
  validationFailureAction: Audit   # Start here: "tell me what's wrong"
  # Then flip to:
  validationFailureAction: Enforce  # "actually enforce it now"
```

Kyverno also supports **Dry Run** for testing new policies against live cluster data without any impact — like a rehearsal before the building inspector arrives for real.

-----

## Installing Kyverno: The First Bricks 🧱

```bash
# Via Helm (recommended)
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update
helm install kyverno kyverno/kyverno -n kyverno --create-namespace

# Verify installation
kubectl get pods -n kyverno
# NAME                                             READY   STATUS
# kyverno-admission-controller-7b9c45b7f9-xk2mp   1/1     Running
# kyverno-background-controller-6d8f9b4c-2m4np     1/1     Running
# kyverno-cleanup-controller-5c7b8d9f-4q1rp        1/1     Running
# kyverno-reports-controller-8f9c7d6b-8s3tp        1/1     Running
```

Four controllers, each with a specific job:

- **Admission controller** — the main webhook; validates/mutates every API call in real time
- **Background controller** — scans existing resources and applies generate rules
- **Cleanup controller** — handles time-based resource cleanup policies
- **Reports controller** — manages Policy Reports and compliance reporting

Wolfgang walks up to Penny’s (newly protected) cluster and submits his privileged pod. The admission controller wakes up. The rule fires. The response arrives immediately.

```
Error: admission webhook denied the request.
```

Wolfgang blinks. He submits it again. Same result.

He tries his debug pod with `hostNetwork: true`. Also rejected.

He tries `image: registry.suspicious.io/badstuff:latest`. Blocked. Kyverno has a rule that only permits images from `company-registry.io/*`.

*“This is not how it was in the brochure,”* says Wolfgang, quietly.

-----

## What Penny Learns 🐷

After installing Kyverno with the Pod Security Standards policy library (freely available at kyverno.io/policies), Penny’s first audit scan reveals:

```
Policy Report Summary:
  CRITICAL: 47 violations (privileged containers, root users)
  HIGH:     112 violations (no resource limits, missing labels)
  MEDIUM:   38 violations (missing network policies)
  LOW:      23 violations (missing annotations)
  
Total violations: 220
Wolf entry attempts blocked since install: 0 (Audit mode — still logging)
Wolf entry attempts that WOULD have been blocked: 47 critical, immediately
```

She switches the Pod Security policies to Enforce mode.

Wolf attempts: 47 blocked in the first hour.

*“Huh,”* says Penny. *“I should have done this in the first sprint.”*

-----

In **Episode 3**, we visit Stanley’s stick house. He has RBAC. He has a spreadsheet. He has absolutely no Policy-as-Code. The Wolf finds the gaps between the sticks and starts working on the supply chain.

-----

**🔗 Resources**

- **Kyverno quickstart**: [kyverno.io/docs/introduction/quick-start](https://kyverno.io/docs/introduction/quick-start/)
- **Kyverno policy samples**: [kyverno.io/policies](https://kyverno.io/policies/)
- **Pod Security Standards with Kyverno**: [kyverno.io/docs/pod-security](https://kyverno.io/docs)
- **Kyverno GitHub**: [github.com/kyverno/kyverno](https://github.com/kyverno/kyverno)

-----

*🐺 Big Bad Wolf Meets Nirmata — in which 220 violations are discovered and the Wolf meets an admission webhook for the first time.*
