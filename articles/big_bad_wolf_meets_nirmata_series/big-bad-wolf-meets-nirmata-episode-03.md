---
title: "Big Bad Wolf Meets Nirmata 🐺 Ep.3"
part: 3
published: false
description: "Episode 3: Stanley built his house out of sticks. He has RBAC. He has a spreadsheet. He ran a security scan last Tuesday when nothing else was happening. The Wolf finds the gaps between the sticks — specifically, the CI/CD pipeline nobody thought to check, and the IaC templates that were ‘probably fine’. Shift-left security and pipeline scanning enter the story."
tags: [kubernetes, kyverno, security, cicd]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/big-bad-wolf-nirmata-episode-03.png"
series: "Big Bad Wolf Meets Nirmata"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: Sticks and Half-Measures

> *“I definitely meant to finish setting up those security controls. It is on the list. The list is very long, but it is definitely on it.”*
> — Stanley the Slightly-Worried, gesturing at a spreadsheet

-----

## The Tour of the Stick House 🪵

Stanley was proud of his house. It was, objectively, better than Penny’s.

He had namespaces. He had RBAC so developers could not randomly deploy to production. He had a Network Policy on the main application namespace — just the one, but still. He had a Slack channel called `#security-alerts` that had 847 unread messages, which at least meant alerts were being generated.

He also had `TODO_security.xlsx`, a spreadsheet with 47 rows of planned security improvements, colour-coded by priority (mostly red and orange, with a few yellows for optimism), and a “Target Date” column in which every date had been manually slid forward four months at least twice.

*“It is not perfect,”* Stanley admitted to his rubber duck, *“but it is better than nothing.”*

Wolfgang the Wolf, standing in the woods with a clipboard, noted this and began composing a project plan.

-----

## 🗂️ SIPOC — The Stick House Situation

|**Suppliers**                               |**Inputs**                                                                         |**Process**                                                                           |**Outputs**                                                                                                      |**Customers**                                                                                         |
|--------------------------------------------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
|Stanley (well-intentioned, overloaded)      |Partial security controls: RBAC, one NetworkPolicy, occasional scans, a spreadsheet|Manual, ad-hoc, inconsistent security enforcement                                     |Gaps between the sticks: a pipeline nobody checked, IaC templates nobody validated, a `latest` tag nobody noticed|Wolfgang, who has a clipboard and is noting every gap                                                 |
|Kyverno with shift-left (what Stanley needs)|Policy checks in CI/CD pipeline AND cluster admission control                      |Validate manifests before they ever reach the cluster; catch IaC violations at PR time|Violations surfaced at the cheapest possible moment — before deployment                                          |Developers (immediate feedback), security teams (earlier visibility), Stanley’s CISO (fewer surprises)|
|The Kyverno CLI (`kyverno` binary)          |Kubernetes manifests, Helm charts, Kustomize outputs                               |`kyverno apply policy.yaml --resource manifest.yaml` → pass/fail with explanations    |Local and CI/CD policy testing without a running cluster                                                         |Developers who want to know if they broke anything before it reaches production                       |

-----

## The Gaps Between the Sticks 🪵

Stanley’s house had walls, technically. But sticks have gaps. And gaps, as Wolfgang would gleefully demonstrate, are all you need.

### Gap 1: The Unprotected Pipeline 🔧

Stanley secured his cluster. He did not secure the *path to* his cluster. Specifically, his CI/CD pipeline was wide open:

```yaml
# .github/workflows/deploy.yaml
name: Deploy
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f manifests/   # 🐺 No policy check. Just apply. Whatever is in there.
```

Wolfgang committed a manifest with a privileged container to a feature branch, opened a PR, watched it merge, and watched the CI pipeline deploy his privileged pod directly to staging without a single check. The cluster itself had RBAC, but the pipeline had pipeline-level access credentials that bypassed developer restrictions.

*“Fascinating,”* Wolfgang noted. *“The front door is locked. The delivery entrance is propped open with a brick.”*

### Gap 2: The Terraform Template Nobody Checked 🏗️

Stanley’s infrastructure was managed with Terraform. Most of it was sensible. One module, written in 2022 by someone who no longer worked there, configured an EKS node group:

```hcl
# infra/modules/eks-nodegroup/main.tf
resource "aws_security_group_rule" "allow_all_inbound" {
  type        = "ingress"
  from_port   = 0
  to_port     = 65535
  protocol    = "-1"
  cidr_blocks = ["0.0.0.0/0"]  # 🐺 ALL ports, ALL protocols, FROM EVERYWHERE
  description = "temp - remove after testing"  # Written in 2022
}
```

“Temp” is eternal. Wolfgang probed port 2379 (etcd), found it listening, and drank from the database of all Kubernetes configuration. This was suboptimal for Stanley.

### Gap 3: The `latest` Tag Time Bomb 💣

```yaml
# manifests/web-app.yaml
containers:
- name: web-app
  image: company/web-app:latest  # 🐺 What is 'latest' today?
```

At 2:17am on a Wednesday, someone updated `company/web-app:latest` in DockerHub to include a small cryptocurrency miner. Nobody noticed because there were no image verification policies. The next pipeline run happily pulled the new `latest`, deployed it, and wondered why CPU usage went up 400%.

-----

## The Solution: Shift-Left Security ⬅️

“Shift-left” is developer-community jargon for “catch problems earlier in the process, where they are cheaper and less embarrassing to fix.”

In the software world:

- Finding a security issue in **production** costs approximately 100 units of pain, money, and grey hairs
- Finding it in **staging** costs 30 units
- Finding it in the **CI/CD pipeline** costs 10 units
- Finding it in the **developer’s IDE** costs 1 unit

Kyverno enables shift-left through the **Kyverno CLI** — a binary that can run policy checks locally or in any CI/CD system, without needing a running Kubernetes cluster:

```bash
# Install Kyverno CLI
brew install kyverno    # macOS
# or
curl -LO "https://github.com/kyverno/kyverno/releases/download/v1.13.0/kyverno_v1.13.0_linux_amd64.tar.gz"

# Test a manifest against policies before deploying
kyverno apply ./policies/ --resource ./manifests/web-app.yaml

# Output:
# Applying 5 policy rule(s) to 1 resource(s)...
# 
# policy disallow-privileged-containers -> resource default/Pod/web-app: PASS
# policy require-non-root-user -> resource default/Pod/web-app: FAIL
#   message: Containers must not run as root. Wolf entry risk: HIGH.
# policy require-resource-limits -> resource default/Pod/web-app: FAIL
#   message: Containers must have CPU and memory limits. 
# policy disallow-latest-tag -> resource default/Pod/web-app: FAIL
#   message: Images must not use the 'latest' tag. Use a specific digest.
# 
# Test Summary: 2 test(s) passed | 3 test(s) failed
```

### Adding Policy Checks to the CI/CD Pipeline

```yaml
# .github/workflows/deploy.yaml — the fixed version
name: Deploy
on: [push]
jobs:
  policy-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Kyverno CLI
      run: |
        curl -LO "https://github.com/kyverno/kyverno/releases/download/v1.13.0/kyverno_linux_amd64.tar.gz"
        tar -xzf kyverno_linux_amd64.tar.gz
        chmod +x kyverno
        sudo mv kyverno /usr/local/bin/
    
    - name: Run Policy Check  # 🧱 THE FIX
      run: |
        kyverno apply ./policies/ --resource ./manifests/ \
          --detailed-results \
          --table
      # Fails the pipeline if any policy violations found
      # Wolfgang's privileged container never makes it to staging
    
  deploy:
    needs: policy-check    # Only runs if policy-check passes
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: kubectl apply -f manifests/
```

Now Wolfgang’s malicious PR fails at the `policy-check` step. The pipeline never reaches `deploy`. The privileged pod never reaches staging. Wolfgang receives a CI/CD failure notification and mutters darkly about pre-commit hooks.

-----

## IaC Scanning: Policy-Checking the Foundations 🏗️

Kyverno does not only check Kubernetes manifests. It can check Infrastructure-as-Code (IaC) at the time the Terraform plan or Helm chart is generated — **before** anything is deployed to any cloud.

### Validating Kubernetes Manifests from Helm

```bash
# Generate the Kubernetes manifests from Helm chart first
helm template my-release ./my-chart > rendered-manifests.yaml

# Then scan them with Kyverno
kyverno apply ./policies/ --resource rendered-manifests.yaml

# If anything looks like an open firewall rule or privileged pod,
# the scan fails and nobody runs terraform apply
```

### Checking Kubernetes Resources for Drift

Even after deployment, Kyverno’s **background controller** continuously scans all existing resources against all policies and updates the Policy Reports:

```bash
kubectl get policyreport --all-namespaces

NAMESPACE     NAME                            PASS   FAIL   WARN   ERROR   SKIP
default       cpol-disallow-privileged         12     0      0      0       0
default       cpol-require-resource-limits     11     1      0      0       0
# ↑ One pod still missing resource limits.
# Wolfgang's previously-running pod, forgotten and now flagged.
```

This is the difference between **point-in-time scanning** (a manual Tuesday scan that finds nothing new because nothing changed on Tuesdays) and **continuous scanning** (finding the forgotten pod that has been running since March).

-----

## Supply Chain Security: The Wolf in Image Clothing 🖼️

The most elegant Wolf attack is via the software supply chain. Stanley’s `latest` tag incident is a prime example. Kyverno addresses this directly:

### Disallow `latest` Tags

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: Enforce
  rules:
  - name: require-image-tag
    match:
      any:
      - resources:
          kinds: [Pod]
    validate:
      message: "An image tag is required and 'latest' is not permitted. 
                The Wolf uses 'latest'. That is all you need to know."
      pattern:
        spec:
          containers:
          - image: "*:*[!latest]*"
```

### Restrict to Approved Registries

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-image-registries
spec:
  validationFailureAction: Enforce
  rules:
  - name: approved-registries-only
    match:
      any:
      - resources:
          kinds: [Pod]
    validate:
      message: "Images must only come from company-registry.io or approved-public.io.
                registry.suspicious.io is not on the list. Kindly leave."
      pattern:
        spec:
          containers:
          - image: "company-registry.io/* | approved-public.io/*"
          initContainers:
          - image: "company-registry.io/* | approved-public.io/*"
```

Wolfgang submits `registry.suspicious.io/cryptominer:stable`. The admission controller rejects it with the message. Wolfgang stands in the metaphorical rain, muttering.

### Image Signature Verification (Kyverno + Sigstore/Cosign)

For the most stringent supply chain security, Kyverno integrates with Sigstore’s Cosign to verify cryptographic signatures on images:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  rules:
  - name: check-signature
    match:
      any:
      - resources:
          kinds: [Pod]
    verifyImages:
    - imageReferences:
      - "company-registry.io/*"
      attestors:
      - entries:
        - keys:
            publicKeys: |-
              -----BEGIN PUBLIC KEY-----
              [Company's signing key]
              -----END PUBLIC KEY-----
```

If the image was not signed with the company’s private key, it is rejected. Wolfgang cannot forge the signature. He tries. He cannot. He knows he cannot. He resents this deeply.

-----

## What Stanley Learns After Installing Kyverno with CLI Integration 🐷

```bash
# Pipeline now runs kyverno apply on every PR
# First week results:

Manifests scanned:    847
Policy violations:     94
   Critical:           23  (missing security contexts, root containers)
   High:               41  (no resource limits, latest tags)
   Medium:             30  (missing labels, annotations)
PRs blocked:           17  (would have deployed violations to staging)
Wolf attack attempts via pipeline: 3 (all blocked)
Wolf attack attempts via IaC:      1 (caught at terraform plan stage)
```

Stanley crosses 17 items off `TODO_security.xlsx` in one week.

He is not yet fully protected — the cluster policies are in Audit mode and the IaC scanning is not fully integrated — but for the first time, the Wolf is actually being slowed down.

*“This is… encouraging,”* Stanley admits, in a tone suggesting he has been suppressing optimism for several years.

-----

## The Gap That Remains: Manual Management at Scale 🏗️

Stanley now has Kyverno in his pipeline. He has Kyverno in his cluster. He has policies running in Audit mode with 94 violations he needs to fix.

But he has **one cluster**.

His colleague at the company running 47 clusters across three cloud providers — she is texting him. *“How do you manage policy updates across all the clusters? Which cluster has what policy version? How do you know which clusters are drifting?”*

Stanley opens a new spreadsheet. It is called `cluster_policies_tracking.xlsx`. This is not going to scale either.

In **Episode 4**, the Third Piglet’s approach — Policy-as-Code done properly, with GitOps, enforcement mode, and the brick-by-brick construction of a house that cannot be blown down.

-----

**🔗 Resources**

- **Kyverno CLI**: [kyverno.io/docs/kyverno-cli](https://kyverno.io/docs/kyverno-cli/)
- **Supply Chain Security with Kyverno**: [nirmata.com/supply-chain-security](https://nirmata.com/supply-chain-security/)
- **Pipeline Scanning**: [nirmata.com/pipeline-scanning](https://nirmata.com/pipeline-scanning/)
- **Kyverno Policy Library**: [kyverno.io/policies](https://kyverno.io/policies/)

-----

*🐺 Big Bad Wolf Meets Nirmata — the Wolf finds the delivery entrance. It is now also secured.*
