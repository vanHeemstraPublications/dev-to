---
title: "Big Bad Wolf Meets Nirmata 🐺 Ep.4"
part: 4
published: false
description: "Episode 4: Brenda builds her house out of Policy-as-Code bricks. Every brick is a Kyverno policy — tested, versioned, peer-reviewed, GitOps-managed, enforced in the pipeline AND the cluster. The Wolf huffs. The Wolf puffs. The Wolf gets a 403 Forbidden. This episode explains what a properly built Kyverno house looks like."
tags: [kubernetes, kyverno, policyascode, gitops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/big-bad-wolf-nirmata-episode-04.png"
series: "Big Bad Wolf Meets Nirmata"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 4: Bricks and Policy-as-Code

> *“I’ll huff, and I’ll puff, and I’ll—”*
> `Error from server: admission webhook denied the request.`
> *”…Oh.”*
> — The Big Bad Wolf, outside Brenda’s cluster

-----

## The Brick House: A Love Story in YAML 🧱

Brenda had a philosophy. She had encountered two production incidents at previous employers — one caused by a privileged container and one by a `latest` tag — and she had emerged from both experiences with the conviction that **if it is not code, it does not exist**.

Security intentions written in a spreadsheet? Not code.
Security checks done manually on Tuesdays? Not code.
An unwritten agreement that “developers won’t do anything too weird”? Definitely not code.

**Policy-as-Code** was the answer: write every security rule as a YAML file, commit it to a git repository, test it, review it, and deploy it just like application code. Have Kyverno enforce it at every point where something can go wrong. The Wall that could not be blown down was not made of good intentions. It was made of version-controlled YAML with code review.

Wolfgang surveyed the house from the treeline. It had no obvious entry points. This was unusual. He checked his notes. He had 47 techniques. He would try them all.

-----

## 🗂️ SIPOC — The Brick House

|**Suppliers**                            |**Inputs**                                            |**Process**                                                                                            |**Outputs**                                                                                                                   |**Customers**                                                                                  |
|-----------------------------------------|------------------------------------------------------|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
|Brenda (systematic, possibly caffeinated)|Business requirements expressed as security rules     |Write policies → test with kyverno-test → PR + review → GitOps deploy → enforce in pipeline and cluster|A cluster where every resource was validated before admission, every bad thing was blocked, every missing thing was mutated in|The CISO who finally sleeps, the compliance auditor who finds evidence, the Wolf who finds 403s|
|GitOps (ArgoCD/Flux)                     |Policy files in git, signed commits, branch protection|Auto-deploy policy changes to all clusters when main branch updates                                    |Policy drift is impossible — cluster always reflects git                                                                      |Multi-cluster consistency without manual management                                            |
|Kyverno (enforce mode)                   |Valid and invalid resource requests                   |Admission webhook enforces every validated policy                                                      |A 403 error for every non-compliant resource, with a clear explanation                                                        |Developers (immediate feedback), the Wolf (a very confusing afternoon)                         |

-----

## The Policy Repository: The Blueprint Office 📐

Brenda’s first move was not writing a single policy. Her first move was creating a `policies/` git repository:

```
company-kubernetes-policies/
├── README.md
├── .github/
│   └── workflows/
│       ├── test-policies.yaml     ← Run kyverno-test on every PR
│       └── deploy-policies.yaml  ← Deploy to clusters via ArgoCD
├── pod-security/
│   ├── disallow-privileged.yaml
│   ├── require-non-root.yaml
│   ├── require-resource-limits.yaml
│   └── restrict-host-paths.yaml
├── images/
│   ├── disallow-latest-tag.yaml
│   ├── restrict-registries.yaml
│   └── verify-signatures.yaml
├── networking/
│   ├── default-deny-all.yaml
│   └── require-network-policy.yaml
├── labels-annotations/
│   ├── require-team-label.yaml
│   └── require-environment-label.yaml
├── namespaces/
│   ├── require-resource-quota.yaml
│   └── default-limitrange.yaml
└── tests/
    ├── pod-security/
    │   ├── disallow-privileged_test.yaml  ← Pass cases + fail cases
    │   └── require-non-root_test.yaml
    └── images/
        └── disallow-latest-tag_test.yaml
```

Every policy has a test. Every test has both pass cases (good pod — should work) and fail cases (bad pod — should be blocked). This is how you know your policy is actually doing what you think it is doing.

-----

## Writing Policies That Actually Work: The Quality Bricks 🧱

### Policy 1: Require Non-Root Users

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-run-as-nonroot
  annotations:
    policies.kyverno.io/title: Require Non-Root User
    policies.kyverno.io/description: >-
      Containers must not run as root. The Wolf runs as root.
      That is not a coincidence. This is why we have this policy.
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: check-containers
    match:
      any:
      - resources:
          kinds: [Pod]
    validate:
      message: "Running as root (uid 0) is not permitted. Please configure runAsNonRoot: true."
      pattern:
        spec:
          =(initContainers):
          - =(securityContext):
              =(runAsNonRoot): true
          containers:
          - securityContext:
              runAsNonRoot: true
```

### Policy 2: Require Resource Limits (with Mutation Fallback)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: mutate-add-resource-limits
  annotations:
    policies.kyverno.io/title: Add Default Resource Limits
spec:
  rules:
  - name: add-limits-if-missing
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
                +(memory): "512Mi"
                +(cpu): "500m"
              requests:
                +(memory): "128Mi"
                +(cpu): "100m"
```

This mutates pods *before* they are created, injecting sensible defaults if none are specified. The developer never even knows they were missing. The Wolf cannot eat all the CPU. Everyone wins. (Except the Wolf.)

### Policy 3: Require Team Label (with Generation companion)

```yaml
---
# VALIDATION: require the label
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-team-label
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-team-label
    match:
      any:
      - resources:
          kinds: [Deployment, StatefulSet, DaemonSet]
    validate:
      message: "All workloads must have a 'team' label. Who owns this? The Wolf?"
      pattern:
        metadata:
          labels:
            team: "?*"
---
# GENERATION: when namespace created, generate default ResourceQuota
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: generate-namespace-quota
spec:
  rules:
  - name: create-default-quota
    match:
      any:
      - resources:
          kinds: [Namespace]
    generate:
      apiVersion: v1
      kind: ResourceQuota
      name: default-quota
      namespace: "{{request.object.metadata.name}}"
      data:
        spec:
          hard:
            pods: "20"
            requests.cpu: "4"
            requests.memory: "8Gi"
            limits.cpu: "8"
            limits.memory: "16Gi"
```

The ResourceQuota is generated automatically when a namespace is created. No namespace can have unlimited resources. The Cost Wolf is specifically allergic to ResourceQuotas.

-----

## Testing Policies: Quality Control Before the Build 🔬

```yaml
# tests/pod-security/require-run-as-nonroot_test.yaml
name: require-run-as-nonroot
policies:
  - ../../pod-security/require-run-as-nonroot.yaml
resources:
  - good-pod.yaml    # Should PASS
  - bad-pod.yaml     # Should FAIL
results:
  - policy: require-run-as-nonroot
    rule: check-containers
    resource: good-pod
    result: pass
  - policy: require-run-as-nonroot
    rule: check-containers
    resource: bad-pod
    result: fail
```

```bash
# Run tests
kyverno test tests/

# Output:
Executing require-run-as-nonroot ...
Applying 1 rule to 2 resources...
----------------------------------------------------------------------
PASS: require-run-as-nonroot/check-containers (good-pod - pass as expected)
PASS: require-run-as-nonroot/check-containers (bad-pod - fail as expected)
----------------------------------------------------------------------
Test Summary: 2 tests passed | 0 tests failed
```

If a policy test fails, the PR is blocked. Nobody deploys an untested policy. The Wolf cannot hope that someone accidentally wrote a policy with a logical error that lets him through.

-----

## GitOps: The Signed Delivery Van 🚚

Brenda’s policies are deployed via **ArgoCD** (or Flux — same concept):

```yaml
# argocd/apps/kyverno-policies.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kyverno-policies
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/company/kubernetes-policies
    targetRevision: main
    path: policies/
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true  # If anyone tries to manually delete a policy,
                      # ArgoCD restores it immediately. Nice try, Wolf.
```

The `selfHeal: true` setting is particularly important. If Wolfgang somehow gets cluster access and tries to delete a Kyverno policy to create a window for his attack:

```bash
$ kubectl delete clusterpolicy disallow-privileged-containers
clusterpolicy.kyverno.io "disallow-privileged-containers" deleted
```

ArgoCD detects the drift within 3 minutes and restores it:

```bash
$ kubectl get clusterpolicy disallow-privileged-containers
NAME                            AGE
disallow-privileged-containers  47s   ← Restored by ArgoCD
```

Wolfgang deleted the policy. The policy is back. He deleted it again. It came back again. This continues until Wolfgang gives up, which takes approximately four repetitions.

-----

## The Admission Webhook: The Permanently Vigilant Doorman 🚪

The moment Kyverno is deployed in Enforce mode, the admission webhook becomes the doorman who never leaves, never sleeps, never accepts bribes, and has memorised every policy by heart.

Every `kubectl apply`, every Helm install, every ArgoCD sync, every automated deployment — every one of them passes through this doorman:

```
Developer: "I'd like to deploy this pod."
Kyverno:   "One moment. [checks 47 policies] Three violations found: 
            no security context, latest tag, missing team label."
Developer: "...Oh. Let me fix those."
[5 minutes later]
Developer: "How about now?"
Kyverno:   "Pass. Welcome to the cluster."
---
Wolfgang:  "I'd like to deploy THIS pod. It has a... forged... team label."
Kyverno:   "One moment. [checks 47 policies] Privileged: true. Rejected."
Wolfgang:  "Fine. What about WITHOUT the privileged flag?"
Kyverno:   "Missing resource limits. Rejected."
Wolfgang:  "I ADDED limits!"
Kyverno:   "Image from unapproved registry. Rejected."
Wolfgang:  [long pause]
Wolfgang:  "Is there ANY pod you will accept?"
Kyverno:   "A properly configured, non-privileged, non-root container from 
            an approved registry with a valid tag, resource limits, 
            and the required labels? Yes. Absolutely."
Wolfgang:  "That is not the pod I have."
Kyverno:   "I know."
```

-----

## Pod Security Standards: The Building Code 📋

Rather than writing individual policies for every pod security concern, Kyverno has built-in support for Kubernetes **Pod Security Standards** — pre-packaged policy bundles at three levels:

|Level         |What it blocks                         |Wolf access                   |
|--------------|---------------------------------------|------------------------------|
|**Privileged**|Nothing (same as no policy)            |Walks straight in 🐺           |
|**Baseline**  |Most known privilege escalation vectors|Slowed down but not stopped 🐺😤|
|**Restricted**|All of the above + many more           |Completely locked out 🚫🐺      |

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: pod-security-standards-restricted
spec:
  validationFailureAction: Enforce
  background: true
  rules:
  - name: restricted
    match:
      any:
      - resources:
          kinds: [Pod]
    validate:
      podSecurity:
        level: restricted
        version: latest
```

One policy, Restricted level. Covers: disallowing privileged containers, disallowing host path mounts, requiring non-root users, requiring read-only root filesystem, dropping capabilities, requiring seccomp profiles. Wolfgang’s entire attack toolkit for container escape is dismantled by six lines of YAML.

-----

## The Result: The House That Will Not Blow Down 🏠

After three months of Brenda’s Policy-as-Code approach:

```
Wolf attack attempts vs Brenda's cluster:
  Privileged container: 403 Forbidden
  Root user container: 403 Forbidden
  Latest tag image: 403 Forbidden
  Unapproved registry: 403 Forbidden
  No resource limits: Mutated automatically (defaults injected)
  Missing team label: 403 Forbidden
  Delete a policy: Restored by ArgoCD in <3 minutes
  Supply chain attack: Image signature invalid. 403 Forbidden.
  New namespace without quota: Quota generated automatically
  Lateral movement between namespaces: Default-deny NetworkPolicy generated

Total successful Wolf intrusions: 0
Total Wolf attempts: 156 (he is very persistent)
Total CISO sleepless nights caused by this cluster: 0
```

Wolfgang, sitting outside the brick house in the rain, writes in his notebook:

*“This cluster has no viable entry points. The policies are tested, version-controlled, and self-healing. The admission control intercepts everything. The images are verified. The quotas are enforced. I need to think bigger. Perhaps I can attack the management plane. Perhaps I can attack multiple clusters simultaneously. Perhaps I can attack the compliance reporting…”*

He looks up. The light in Brenda’s window goes off.

*“She is probably not worried about me at all,”* he thinks bitterly. He is correct.

-----

In **Episode 5**, Wolfgang makes his boldest move yet: he attempts to attack the village — all three clusters simultaneously — while Brenda is on holiday. Enter the Nirmata Control Hub.

-----

**🔗 Resources**

- **Kyverno policies**: [kyverno.io/policies](https://kyverno.io/policies/)
- **Kyverno test framework**: [kyverno.io/docs/testing-policies](https://kyverno.io/docs/testing-policies/)
- **GitOps with Kyverno**: [nirmata.com](https://nirmata.com)
- **Pod Security Standards**: [kyverno.io/docs/pod-security](https://kyverno.io/docs)
- **Nirmata Enterprise Kyverno**: [nirmata.com/nirmata-enterprise-for-kyverno](https://nirmata.com/nirmata-enterprise-for-kyverno/)

-----

*🐺 Big Bad Wolf Meets Nirmata — 156 attempts. 0 successes. The Wolf needs a bigger plan.*
