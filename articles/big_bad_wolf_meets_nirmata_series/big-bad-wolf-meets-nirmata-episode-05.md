---
title: "Big Bad Wolf Meets Nirmata 🐺 Ep.5"
part: 5
published: false
description: "Episode 5: Wolfgang’s brilliant new plan: attack all three clusters at once while Brenda is on holiday. Enter the Nirmata Control Hub — the central control plane that manages Kyverno across every cluster simultaneously, with dashboards, violation detection, AI copilot, exceptions management, and team collaboration. The village now has a mayor’s office."
tags: [kubernetes, nirmata, multicluster, governance]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/big-bad-wolf-nirmata-episode-05.png"
series: "Big Bad Wolf Meets Nirmata"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 5: The Control Tower

> *“The houses are protected individually. But who watches ALL the houses at once? Who notices when three things go wrong simultaneously? WHO IS WATCHING THE WHOLE VILLAGE?!”*
> — Wolfgang von Misconfiguration, delighted by this gap
> *(He had not yet discovered the Nirmata Control Hub)*

-----

## The Wolf’s New Strategy: Divide and Conquer 🐺

Wolfgang had spent three months bouncing off Brenda’s cluster. He had logged 156 rejected attempts. He had a folder on his laptop called “Rejections (Kyverno)” that was distressingly large.

He needed a new approach. He consulted his copy of *The Art of Cloud-Native War* and arrived at a bold conclusion: the piglets were protecting their individual houses. Nobody was watching the entire village.

His new plan:

1. Try to breach Penny’s cluster (now also protected, but less systematically)
1. Simultaneously probe Stanley’s cluster (better protected, but still manual in places)
1. While both teams are distracted, attempt a quiet configuration drift in Brenda’s cluster
1. Wait for Brenda to be on holiday so nobody notices

It was an elegant plan. It assumed nobody had centralised visibility across all three clusters.

It also assumed nobody had the **Nirmata Control Hub**.

He was wrong on both counts.

-----

## 🗂️ SIPOC — The Control Tower

|**Suppliers**                                    |**Inputs**                                                                                     |**Process**                                                                    |**Outputs**                                                                       |**Customers**                                                                           |
|-------------------------------------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
|All three clusters (Penny’s, Stanley’s, Brenda’s)|Policy violations, drift events, resource misconfigs, compliance status across all environments|NCH aggregates data, runs AI analysis, categorises by severity/team/environment|A unified view of the entire village’s security posture — not three separate views|The village CISO who no longer needs to chase three people in three Slack channels      |
|NCH Policy Studio                                |Natural language intent (“pods must not run as root”)                                          |AI copilot generates Kyverno YAML, tests it, shows simulation results          |A ready-to-deploy Kyverno policy created without writing raw YAML                 |Platform teams who write policy intent, not YAML syntax                                 |
|Violation workflow                               |Violations detected across clusters                                                            |NCH groups by service, team, environment; generates AI remediation suggestions |Prioritised violation backlog with AI-generated fix PRs                           |Dev teams who receive specific, actionable fixes rather than cryptic error messages     |
|Exception management                             |“We need to temporarily allow X in namespace Y”                                                |Create time-boxed exception with owner, reason, expiry date, full audit trail  |A governed exception that expires automatically and is fully auditable            |Compliance auditors who ask “why does namespace legacy-app allow privileged containers?”|

-----

## Connecting the Village: NCH Architecture 🗺️

The Nirmata Control Hub is a SaaS (or self-hosted) platform. Each cluster gets a lightweight agent that connects back to NCH. The agent runs in the cluster, watches for policy events, and reports them to the central hub.

```
                    ┌──────────────────────────────┐
                    │    Nirmata Control Hub (NCH)  │
                    │                              │
                    │  ┌──────┐ ┌───────┐ ┌─────┐ │
                    │  │Dash- │ │Policy │ │Comp-│ │
                    │  │board │ │Studio │ │lian.│ │
                    │  └──────┘ └───────┘ └─────┘ │
                    │  ┌──────────────────────────┐ │
                    │  │     AI Copilot           │ │
                    │  └──────────────────────────┘ │
                    └──────────┬───────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼──────┐ ┌───────▼──────┐ ┌──────▼───────┐
    │ Penny's Cluster│ │Stanley's Clus│ │Brenda's Clus │
    │                │ │ter           │ │ter           │
    │ [NCH Agent]    │ │ [NCH Agent]  │ │ [NCH Agent]  │
    │ Kyverno OSS    │ │ Kyverno OSS  │ │ Kyverno OSS  │
    │ + Enterprise   │ │ + Enterprise │ │ + Enterprise │
    └────────────────┘ └──────────────┘ └──────────────┘
```

Wolfgang’s attack on three clusters simultaneously:

```
[NCH Dashboard alert]:
  09:47:13 - Cluster penny-prod: 3 privileged pod attempts blocked
  09:47:14 - Cluster stanley-staging: 7 unapproved image attempts blocked
  09:47:16 - Cluster brenda-prod: Policy drift detected in namespace legacy-app
  
[AI Copilot]: "Simultaneous anomalous activity detected across 3 clusters.
               Pattern matches coordinated probe. Recommending escalation."

[Slack notification to #security-alerts]: 
  🚨 NIRMATA: Coordinated attack pattern detected across all environments.
              See Control Hub dashboard for details.
```

Brenda, who is on holiday in Lisbon, receives this notification on her phone. She opens the NCH mobile view. She sees Wolfgang’s entire attack plan laid out in an incident timeline. She drinks her coffee and marks the incident as under review, since the policies blocked everything automatically.

Wolfgang does not breach a single cluster.

-----

## The Dashboard: A View of the Entire Village 🗺️

The NCH dashboard gives a unified view across all connected clusters:

```
Nirmata Control Hub — Dashboard
════════════════════════════════════════════════════════

CLUSTER OVERVIEW              Policy Coverage
  Clusters connected: 3         penny-prod:    78% ← low
  Total namespaces:   47         stanley-stage: 82%
  Total workloads:    1,247      brenda-prod:   99% ← Brenda
  
TOP VIOLATIONS BY SEVERITY    RECENT ACTIVITY
  Critical:  12 (penny-prod)     09:47 - 47 violations blocked (3 clusters)
  High:     156 (all clusters)   09:23 - New policy deployed via GitOps
  Medium:   389 (all clusters)   08:15 - Compliance report generated
  Low:      742 (all clusters)
  
WOLF ATTEMPT TIMELINE (Today)
  09:47:13 penny-prod  │████ 3 blocked
  09:47:14 stanley-stg │████████ 7 blocked
  09:47:16 brenda-prod │█ 1 drift detected + auto-remediated
```

The key insight: if you have 47 clusters (some organisations do), you cannot manually check each one. NCH gives you the view from above — the mayor’s office looking out at the whole village.

-----

## Policy Studio: Writing Policy in Plain English 🖊️

Before NCH, writing a Kyverno policy looked like this:

```
Engineer: "I need a policy that requires all pods in the production namespace 
           to have a securityContext with runAsNonRoot: true, unless they 
           are in the monitoring namespace. And it should apply to init 
           containers too. And I need a test for it."

*Hours of YAML wrangling later*

Engineer: [discovers the pattern syntax had a typo] [considers career change]
```

With NCH Policy Studio:

```
Engineer: [Opens Policy Studio]
           [Types]: "All pods in production namespaces must run as non-root users,
                    except pods in the monitoring namespace."
           [Clicks: Generate Policy]

NCH AI:   [Generates Kyverno YAML]
           [Runs test simulation: "34 pods in prod would PASS, 3 would FAIL"]
           [Explains: "The 3 failing pods are in legacy-app namespace. 
                       Here are the current configurations..."]
           [Shows diff of what would change]
           [Offers: "Deploy to audit mode first?"]

Engineer: [Clicks: Deploy to Audit Mode]
           [Reviews findings]
           [Clicks: Promote to Enforce Mode]
```

Wolfgang, watching this, realises that policies are being created faster than he can find gaps. The pig is writing policy faster than he can try new attack vectors. This is not how it is supposed to work.

-----

## Violation Management: The Ordered Backlog 📋

Before NCH, a team with 300 violations looked at a flat list of 300 items and felt despair.

NCH’s AI groups and prioritises them:

```
VIOLATION BACKLOG (AI-Categorised)

🔴 CRITICAL — Fix this week (12 violations)
  Service: payment-api | Team: payments-team
  • 3× privileged containers (pods: checkout-*, payment-*)
  • 2× no image signature verification (image: payment-processor:*)
  
  [AI Assessment]: "Payment-api runs as privileged. If compromised,
                    attacker has container escape path. Blast radius: 
                    entire payment namespace + host node."
  
  [Generate Fix PR] ← AI writes the PR for you

🟠 HIGH — Fix this sprint (41 violations)
  [...]

🟡 MEDIUM — Fix next sprint (156 violations)
  [...]
```

The “Generate Fix PR” button is particularly powerful. Click it and NCH generates a pull request to your Git repository with the corrected manifest, the policy annotation, the test, and a description of what was changed and why. The developer just needs to review and merge.

```
AI-Generated PR: "fix: add security context to payment-processor pods"

diff --git a/manifests/payment/deployment.yaml b/manifests/payment/deployment.yaml
--- a/manifests/payment/deployment.yaml
+++ b/manifests/payment/deployment.yaml
   containers:
   - name: payment-processor
     image: payment-processor:v2.1.3
+    securityContext:
+      runAsNonRoot: true
+      runAsUser: 1000
+      allowPrivilegeEscalation: false
+      capabilities:
+        drop:
+          - ALL
+      readOnlyRootFilesystem: true

Test: policy check passes ✓
```

Wolfgang watches a developer approve this PR in 45 seconds. The violation is resolved. *“They are not even writing the fixes themselves,”* he grumbles. *“The machine writes the fix. They just approve it. This is inefficient for ME.”*

-----

## Exception Management: The Governed Side Door 🚪

Sometimes you need a temporary exception. The legacy application that genuinely cannot run without certain privileges until it is refactored. The third-party vendor image that is not signed. The migration that requires elevated access for 48 hours.

Without governance, exceptions become permanent. Without NCH, the “temporary” privileged container runs for three years because nobody remembered to remove it and nobody can find the Jira ticket.

NCH Exception Management:

```
Request Exception
═══════════════════════════════════════════
Policy:      disallow-privileged-containers
Resource:    Pod/legacy-payment/checkout-v1
Namespace:   legacy-payment
Reason:      Legacy vendor app requires privileged access during 
             migration. Vendor ticket #12847 filed. Refactor
             scheduled for Q3 2026.
Owner:       james.dev@company.com
Duration:    30 days  ←  EXPIRES AUTOMATICALLY
Approval:    Required from: security-team@company.com

[Request Exception]
```

The exception is logged, the owner is named, the reason is recorded, the expiry is enforced. When 30 days pass, the exception expires and the policy is re-enforced. If James needs more time, he has to explicitly re-request it.

Wolfgang dreams of exceptions that never expire. NCH specifically prevents this.

-----

## Team Collaboration: The Village Communication Network 📢

Security is not a single team’s job. NCH integrates with:

```
Integrations:
  ✓ Slack   → #security-alerts, #platform-team, #compliance
  ✓ Jira    → Auto-create tickets from violations
  ✓ GitHub  → PRs with fixes generated by AI
  ✓ GitLab  → Same, but GitLab
  ✓ ServiceNow → Enterprise ticketing integration
```

When NCH detects a critical violation in the payments namespace:

```
Slack #payments-team:
  🚨 @james.dev @sarah.arch NIRMATA CRITICAL: 
  payment-processor pod running as privileged in production.
  
  Blast radius: payment namespace, host node access
  Impact: HIGH — immediate exploitation risk
  
  [View in NCH] [Generate Fix PR] [Request Exception]

  — Nirmata Control Hub
```

James sees it. Sarah sees it. The PR is generated. The fix is reviewed and merged. The whole cycle completes in under an hour. Wolfgang, who was counting on nobody noticing for at least three days, recalculates.

-----

## Wolfgang’s Afternoon Summary 📝

At 5pm, Wolfgang closes his laptop and reviews the day:

```
ATTACK PLAN: Village-Wide Simultaneous Probe
═══════════════════════════════════════════════════════
Target 1: penny-prod cluster
  Attempts: 3 privileged pod deployments
  Result: All 403'd. NCH detected. Notified team. PR generated.
  Time to fix: 47 minutes.

Target 2: stanley-staging cluster
  Attempts: 7 unapproved image pulls
  Result: All 403'd. NCH detected. Violations categorised as High.
  Time to remediation: 1 sprint.

Target 3: brenda-prod cluster (while on holiday)
  Attempts: 1 configuration drift (deleted a NetworkPolicy)
  Result: NCH detected drift. ArgoCD restored it. Alert sent to Brenda.
  Time to discovery: 3 minutes.
  Time to restore: 3 minutes.
  Brenda's response: "Lol"

OVERALL RESULT: 0 successful intrusions.
                11 violations blocked by admission control.
                1 drift detected and auto-remediated.
                3 teams notified in <5 minutes.

ANALYSIS: They have centralised visibility. Simultaneous attacks are visible 
          as a pattern. The AI spots the pattern. Humans are notified.
          
NEXT STEPS: Need to think bigger. Perhaps the AI itself has weaknesses.
            Perhaps if I write a very convincing policy description...
```

In **Episode 6**, Wolfgang tries his cleverest move yet: writing a disguised natural language policy request. He has heard the AI will write the policy for him. He has a plan. It goes poorly.

-----

**🔗 Resources**

- **Nirmata Control Hub**: [nirmata.com/nirmata-control-hub](https://nirmata.com/nirmata-control-hub/)
- **NCH Solution Brief**: [nirmata.com](https://nirmata.com)
- **Multi-cluster governance**: [nirmata.com](https://nirmata.com)
- **AI Remediation Agents**: [nirmata.com](https://nirmata.com)

-----

*🐺 Big Bad Wolf Meets Nirmata — Wolfgang discovers that attacking three houses at once is not the advantage he thought it was when someone can see all three houses simultaneously.*
