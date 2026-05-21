---
title: "Big Bad Wolf Meets Nirmata 🐺 Ep.8"
part: 8
published: false
description: "Episode 8: After 156 failed breach attempts, 1 incident report filed against his own user account, and considerable self-reflection, Wolfgang von Misconfiguration writes his memoir. The three piglets secure the entire forest. The full Nirmata picture: multi-cloud, supply chain security, multi-tenancy, cost governance, and why Policy-as-Code is the only house the Wolf cannot blow down."
tags: [kubernetes, nirmata, security, devops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/big-bad-wolf-nirmata-episode-08.png"
series: "Big Bad Wolf Meets Nirmata"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: Happily Ever After

> *“Chapter 1: I thought it would be easy. It was not easy. Chapter 47: I have submitted my CV to a DevSecOps consultancy. They seem interested.”*
> — Wolfgang von Misconfiguration, *Diary of a Reformed Wolf: Memoirs from the Cloud-Native Frontier*

-----

## The Memoir Arrives 📖

Wolfgang’s book was published on a grey November Tuesday. It was called *“I’ll Huff, I’ll Puff, and I’ll 403: My Adventures in Policy-as-Code Resistance.”*

It was, by all accounts, an educational read. Platform engineers read it for the attacker’s perspective. Security teams read it for the exhaustive list of things they had not thought to protect. The three little piglets wrote a glowing blurb: *“Finally, an attacker who explains exactly what stopped him. Required reading.”*

The dedication read: *“To Brenda. You are very good at your job and I mean this sincerely.”*

-----

## 🗂️ SIPOC — Happily Ever After

|**Suppliers**                                             |**Inputs**                                                                    |**Process**                                                              |**Outputs**                                                                          |**Customers**                                                                                            |
|----------------------------------------------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
|The entire forest (every team, every cluster, every cloud)|Diverse infrastructure: EKS, AKS, GKE, Rancher, OpenShift, on-prem, air-gapped|NCH connected, policies deployed, AI agents monitoring, compliance mapped|A unified, governed, continuously-verified estate that scales from 1 cluster to 1,000|CISOs who sleep, auditors who find evidence, developers who get clear error messages, wolves who get 403s|
|The complete Nirmata stack                                |Kyverno OSS + Enterprise Kyverno + NCH + AI Platform Assistant                |Each layer adds capability: enforce → manage → govern → AI-accelerate    |The full journey from “no policies” to “AI-driven continuous governance”             |The entire Kubernetes ecosystem — and the three piglets, who are very happy                              |

-----

## The Forest Grows: Multi-Cloud Governance 🌲

The story started with three clusters. It always starts with three clusters. Then the company grows and suddenly there are 47 clusters across five environments and three cloud providers.

```
THE FOREST (Year 3):

AWS Environments:
  production-us-east-1 (EKS)
  production-eu-west-1 (EKS)
  staging-us-east-1 (EKS)
  
Azure Environments:
  production-azure-westeu (AKS)
  development-azure-westeu (AKS)
  
Google Cloud:
  production-gcp-europe (GKE)
  
On-Premises:
  datacenter-london-1 (Rancher)
  datacenter-amsterdam-1 (OpenShift)
  
Air-Gapped (no internet):
  classified-workloads (custom K8s, NCH lightweight agent)
```

Without NCH, this is 9 separate Kyverno deployments, 9 separate policy libraries that slowly diverge, 9 separate compliance reports that never use the same format, 9 separate spreadsheets tracking violations, and 9 different engineers each doing the same work independently.

With NCH, it is one control plane. Policies are written once and deployed everywhere. Compliance maps to the same frameworks across all environments. Violations are visible in one dashboard. AI agents work across all clusters simultaneously.

Wolfgang’s attempt to find the inconsistency between cluster policies (his theoretical “find the cluster that got missed in the bulk update”) fails because policy updates are applied atomically via GitOps to all connected clusters.

-----

## Pod Security: The Specific Bricks the Wolf Hates Most 🧱

By this point in the series, we know the Wolf’s favourite attacks. Here is the complete wall he runs into:

```
Nirmata/Kyverno: Full Pod Security Coverage
════════════════════════════════════════════

Pod Security Standards — Restricted Level:
  ✓ Privileged containers: BLOCKED
  ✓ Host namespaces (hostPID, hostIPC, hostNetwork): BLOCKED
  ✓ Host path volumes: BLOCKED
  ✓ Privilege escalation (allowPrivilegeEscalation): BLOCKED
  ✓ Root user (runAsUser: 0): BLOCKED
  ✓ All capabilities: DROPPED
  ✓ Seccomp: REQUIRED
  ✓ AppArmor: REQUIRED (where applicable)

Additional Kyverno Policies:
  ✓ Read-only root filesystem: REQUIRED
  ✓ Image from approved registry: ENFORCED
  ✓ Image tag not 'latest': ENFORCED
  ✓ Image signed (Cosign): VERIFIED
  ✓ No known CVEs in image: CHECKED at admission
  ✓ Resource limits: MUTATED IN if missing
  ✓ Required labels: ENFORCED
  ✓ ServiceAccount automount: DISABLED unless explicitly needed
  ✓ Default deny NetworkPolicy: GENERATED on namespace creation
```

Wolfgang’s attack surface: zero.

-----

## Multi-Tenancy: The Village with Multiple Owners 🏘️

The forest is not owned by one team. Engineering, Data, ML, Finance, and Marketing all have their namespaces. This is **Kubernetes multi-tenancy**, and it has its own Wolf-shaped problems:

- The Data team’s runaway training job eating Engineering’s CPU quota
- Finance’s namespace being able to talk to Marketing’s namespace via the network
- A developer in one team accidentally (or not accidentally) reading secrets from another namespace

Kyverno’s multi-tenancy policies enforce the separation:

```yaml
# Policy: namespaces can only communicate within their domain
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: isolate-tenant-namespaces
spec:
  rules:
  - name: generate-network-isolation
    match:
      any:
      - resources:
          kinds: [Namespace]
    generate:
      kind: NetworkPolicy
      name: tenant-isolation
      namespace: "{{request.object.metadata.name}}"
      data:
        spec:
          podSelector: {}
          policyTypes: [Ingress, Egress]
          ingress:
          - from:
            - namespaceSelector:
                matchLabels:
                  tenant: "{{request.object.metadata.labels.tenant}}"
```

When the Data team creates a namespace, it can only receive traffic from other Data team namespaces. When Finance creates a namespace, it can only receive traffic from Finance namespaces. The Wolf cannot move laterally from the compromised Marketing namespace to the Finance secrets. The walls between rooms are part of the house now.

-----

## Software Supply Chain Security: The Wolf in the Dependency 🐺📦

The most sophisticated Wolf attack is not against your cluster directly. It is against your dependencies. The developer who trusts `node-utils:latest` because they used it last year, unaware that it changed ownership at npm and now contains a backdoor.

Nirmata + Kyverno + Sigstore addresses this at multiple layers:

```
Layer 1: Registry restriction
  Only our internal registry (mirrored, scanned) is trusted.
  Public registries blocked at admission control.
  
Layer 2: Image tag pinning
  'latest' tags blocked. Immutable digests required.
  image: company-registry.io/node-utils@sha256:a3f9c2d1... ← exact, unchangeable
  
Layer 3: Image signature verification
  Every image must be signed by our CI/CD pipeline's signing key.
  An image that didn't go through our pipeline: signature fails, admission rejected.
  
Layer 4: SBOM (Software Bill of Materials)
  Kyverno can verify that an SBOM attestation exists for the image.
  No SBOM, no admission. We know what's in every container.
  
Layer 5: CVE scanning at admission
  NCH integrates with vulnerability databases.
  Image with critical CVE: rejected at admission, not discovered at 3am.
```

Wolfgang attempts to slip in via a compromised base image. Layer 2 catches it (different digest). He tries to re-sign it with a forged key. Layer 3 catches it (wrong signing key). He tries to create a fake SBOM. Layer 4 catches it (signature on SBOM also verified).

*“The supply chain is defended at every point,”* Wolfgang writes in his memoir. *“I found this very inconvenient.”*

-----

## The Complete Wolf-Prevention Checklist: The Building Code for Kubernetes 🏗️

For the reader building their own brick house, here is the complete checklist the series has covered:

**Foundation (Episode 2–3):**

- [ ] Kyverno OSS installed in cluster
- [ ] Kyverno CLI integrated in CI/CD pipeline
- [ ] Policies checked at PR time (shift-left)
- [ ] Admission webhook active

**Walls (Episode 4):**

- [ ] Pod Security Standards: Restricted level enforced
- [ ] Image source restrictions enforced
- [ ] `latest` tag blocked
- [ ] Resource limits: mutation policy injects defaults
- [ ] Required labels enforced
- [ ] Policies tested with kyverno-test
- [ ] Policies in git (Policy-as-Code)
- [ ] GitOps deployment (ArgoCD/Flux) with selfHeal: true

**Roof (Episode 5):**

- [ ] Nirmata Control Hub connected to all clusters
- [ ] Violation backlog visible and prioritised
- [ ] AI-generated fix PRs in developer workflow
- [ ] Exception management with owners, reasons, expiry
- [ ] Team integrations (Slack, Jira, GitHub)

**Security System (Episode 6):**

- [ ] AI Platform Assistant generating policies from intent
- [ ] Blast radius analysis before enforcing new policies
- [ ] AI remediation agents reducing violation backlog

**Alarm System (Episode 7):**

- [ ] Background scanning active (continuous, not periodic)
- [ ] Drift detection enabled
- [ ] Compliance frameworks mapped (CIS/PCI/HIPAA/SOC 2)
- [ ] Evidence packages exportable on demand
- [ ] Tamper-proof audit log

**Village (Episode 5 + 8):**

- [ ] Multi-cluster policy governance
- [ ] Multi-tenancy namespace isolation
- [ ] Supply chain security (registry restriction + image signing)
- [ ] ResourceQuotas on all namespaces (Cost Wolf prevention)
- [ ] Air-gapped cluster support (lightweight agents)

-----

## The Upgrade Path: From Straw to Brick 🧱

The three piglets represent three real organisational states. Most teams are somewhere between Penny and Stanley. The upgrade path is incremental:

```
STAGE 1 — START HERE (from straw)
  Install Kyverno OSS
  Deploy Pod Security Standards in Audit mode
  Install Kyverno CLI in CI/CD pipeline
  Observe violations without breaking anything

STAGE 2 — BUILD WALLS (from sticks)
  Write Policy-as-Code repository
  Add tests for all policies
  Deploy GitOps for policy management
  Flip critical policies to Enforce mode
  Fix the violation backlog

STAGE 3 — ADD THE ROOF (from bricks)
  Connect Nirmata Control Hub
  Enable AI remediation agents
  Map to compliance frameworks
  Enable exception management with governance

STAGE 4 — SECURE THE VILLAGE (enterprise scale)
  Multi-cluster governance via NCH
  Multi-tenancy isolation
  Supply chain security
  Air-gapped cluster support
  Continuous compliance evidence generation
```

Each stage represents a meaningful improvement in security posture. Each stage makes the Wolf’s job harder. By Stage 4, the Wolf has given up and written a memoir.

-----

## Wolfgang’s Final Assessment: The Reformed Wolf 🐺📖

From Chapter 47 of *“I’ll Huff, I’ll Puff, and I’ll 403”*:

> *“After many months of operational engagement with Nirmata-protected infrastructure, I have reached several conclusions.*
> 
> *First: Kyverno’s admission control is genuinely comprehensive. There is no class of attack I attempted that was not covered by a policy. When I found a gap, the Policy Studio filled it before I could exploit it.*
> 
> *Second: Continuous monitoring has no gap. I had assumed that attack windows existed between scan cycles. They did not. The background controller runs perpetually. The drift detection is instant. The notifications are real-time. There is no 2am.*
> 
> *Third: The AI remediation agents are disconcertingly fast. The time between my probe and the team receiving a fix PR was, on several occasions, shorter than the time it took me to move to the next attack vector.*
> 
> *Fourth: The compliance frameworks are mapped to actual cluster state in real time, not retrospectively. I had hoped that audit cycles would create windows. They did not.*
> 
> *Fifth: The audit log is actually tamper-proof. I verified this personally.*
> 
> *My recommendation to any Wolf considering cloud-native targets: verify that the target is NOT running Nirmata with NCH and AI Platform Assistant before investing significant operational time. The combination of Kyverno enforcement, continuous monitoring, AI-generated remediation, and tamper-proof audit trails creates a defence profile that renders standard attack playbooks ineffective.*
> 
> *As for myself: I have joined a DevSecOps consultancy. Brenda has agreed to provide a reference. I am writing a course on Kyverno policy design from an attacker’s perspective. My experience, I am told, is valuable in this field.*
> 
> *The three piglets are fine. Their clusters are fine. I am, in retrospect, also fine.*
> 
> *Fin.”*

-----

## The Series in One Fairytale Page 🏠

*Once upon a time, three little piglets lived in the cloud.*

*The first built her cluster from straw — no policies, no controls, privileged pods everywhere. The Wolf walked through the front door. (Episode 2)*

*The second built his cluster from sticks — some RBAC, some manual scans, a spreadsheet. The Wolf found the gaps in the CI/CD pipeline and the unguarded terraform templates. (Episode 3)*

*The third built her cluster from Policy-as-Code bricks — every rule a tested YAML file, deployed via GitOps, enforced at admission, in the pipeline, and continuously. The Wolf huffed. The Wolf puffed. The Wolf got 403 Forbidden. (Episode 4)*

*Then the Village CISO called the Nirmata Control Hub, and connected all three clusters to one central control plane — and the Wolf’s attempt to attack all three simultaneously was visible as a coordinated pattern in under five minutes. (Episode 5)*

*The AI Platform Assistant refused to generate the Wolf’s malicious policy request and filed an incident report. (Episode 6)*

*The continuous monitoring caught the Wolf’s midnight chimney attempt in under one minute. The pot was always boiling. (Episode 7)*

*And they all lived happily ever after, in a fully governed, continuously-compliant, AI-assisted infrastructure.*

*The Wolf published a book. It sold reasonably well.*

*THE END.*

-----

**🔗 Resources**

- **Nirmata home**: [nirmata.com](https://nirmata.com)
- **Kyverno**: [kyverno.io](https://kyverno.io)
- **Nirmata Control Hub**: [nirmata.com/nirmata-control-hub](https://nirmata.com/nirmata-control-hub/)
- **AI Platform Assistant**: [nirmata.com/nctl-ai](https://nirmata.com/nctl-ai/)
- **Supply chain security**: [nirmata.com/supply-chain-security](https://nirmata.com/supply-chain-security/)
- **Multi-tenancy**: [nirmata.com/multi-tenancy](https://nirmata.com/multi-tenancy/)
- **Request a demo**: [nirmata.com/request-a-demo](https://nirmata.com/request-a-demo/)

-----

*🐺 Big Bad Wolf Meets Nirmata — eight episodes, one moral: the only house the Wolf cannot blow down is the one built from Policy-as-Code.*

*🐷🐷🐷 The three piglets lived happily ever after. So did their clusters.*
