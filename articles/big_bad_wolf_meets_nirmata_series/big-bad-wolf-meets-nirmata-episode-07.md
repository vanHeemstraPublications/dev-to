---
title: "Big Bad Wolf Meets Nirmata 🐺 Ep.7"
part: 7
published: false
description: "Episode 7: In the original tale, the Wolf tries to sneak down the chimney at night — only to land in a pot of boiling water. Wolfgang’s equivalent: configuration drift at 2am, quiet as a mouse, confident that compliance scanning only runs on Tuesdays. Nirmata’s continuous compliance, drift control, and always-on verification suggest otherwise. The pot is always boiling."
tags: [kubernetes, compliance, nirmata, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/big-bad-wolf-nirmata-episode-07.png"
series: "Big Bad Wolf Meets Nirmata"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: The Boiling Pot

> *“In the original story, the Wolf climbs down the chimney and lands in a boiling pot. I have always considered this metaphor. The chimney is the gap between security checks. The pot is continuous monitoring. The lesson is: there is no gap between security checks anymore.”*
> — Brenda, during a security architecture review

-----

## The Midnight Chimney Attempt 🌙

Wolfgang had been doing research. Real research. Library research. He had read the original Three Little Pigs. He had noted, carefully, that the Wolf only wins when there is an unguarded entry point. He had also noted that in the original story, when the brick house proved impenetrable, the Wolf tried the chimney.

The Kubernetes equivalent of the chimney was this: **time**.

Admission control blocked things at creation time. But what about things that were already running? What about drift — things that changed after creation? What about the configuration that was compliant at 9am and not compliant at 2am because someone ran a “quick fix” in production?

What about compliance frameworks that check controls on a schedule — say, weekly or monthly? There was a window between checks. If he moved quietly enough, quickly enough, he could be in and out before the Tuesday scan.

He set his alarm for 2am.

He climbed the metaphorical chimney.

He landed in the boiling pot.

-----

## 🗂️ SIPOC — The Boiling Pot

|**Suppliers**                |**Inputs**                                                             |**Process**                                                                                     |**Outputs**                                                             |**Customers**                                                                    |
|-----------------------------|-----------------------------------------------------------------------|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|---------------------------------------------------------------------------------|
|Kyverno background controller|All existing cluster resources (not just new ones)                     |Continuous background scan → compare every resource against every policy → update Policy Reports|Always-current compliance snapshot, no stale data                       |NCH dashboard: real-time, not weekly                                             |
|NCH drift detection          |Desired state (from git), actual state (from cluster)                  |Constant comparison: is the cluster what git says it should be?                                 |Drift alert the moment anything deviates from the desired state         |Operations teams who do not want to discover drift at audit time                 |
|Compliance framework mapping |CIS, PCI-DSS, HIPAA, SOC 2 control definitions; cluster policy evidence|NCH maps Kyverno policies to framework controls → generates evidence                            |A compliance report with real evidence, not “we have a policy somewhere”|Compliance auditors who are flying in on Thursday and will ask specific questions|
|Audit log (tamper-proof)     |Every policy event, every change, every exception, every remediation   |Written to immutable audit trail — cannot be modified after the fact                            |An evidence trail showing exactly what happened, when, and to what      |Legal teams, auditors, incident response teams                                   |

-----

## The Background Controller: The Night Watchman 🔦

Kyverno does not only check things at creation time. The **background controller** runs continuously, scanning all existing resources against all policies, all the time.

Wolfgang deleted a NetworkPolicy at 2:17am:

```bash
# 2:17am - Wolfgang deletes NetworkPolicy
$ kubectl delete networkpolicy default-deny-all -n payment

# 2:17am - Kyverno background controller notices:
PolicyReport updated:
  policy: require-network-policy
  resource: Namespace/payment
  result: FAIL  ← Changed from PASS to FAIL
  timestamp: 02:17:43

# 2:17am - NCH receives the policy report update:
Dashboard: FAIL spike detected in compliance coverage
Alert: #security-alerts: Payment namespace NetworkPolicy deleted

# 2:18am - ArgoCD detects drift:
Resource NetworkPolicy/payment/default-deny-all missing from cluster
  Expected: (from git)
  Actual: (not present)
  
# 2:21am - ArgoCD restores it:
NetworkPolicy/payment/default-deny-all created
PolicyReport: PASS restored

# 2:21am - Wolfgang's lateral movement window: 4 minutes.
# Wolfgang's lateral movement attempt: blocked by existing per-pod NetworkPolicies.
# Wolfgang: staring at terminal.
```

The chimney was boiling the entire time.

-----

## Drift Control: The Self-Restoring House 🏠

Drift is when what the cluster **is** diverges from what it **should be** according to the git repository. The two most common causes:

1. **Heroic 2am incidents**: developer directly patches a production pod to fix an urgent issue, forgets to update the manifest
1. **Malicious deletion**: the Wolf deletes a security control to open a window

NCH’s drift detection is the combination of:

- **Kyverno background scanning**: Is this resource still compliant?
- **ArgoCD/Flux GitOps**: Is this cluster still what git says it should be?
- **NCH dashboard**: What drifted, when, and has it been fixed?

```
NCH DRIFT REPORT: Last 24 Hours
══════════════════════════════════════════════════════

Drifts detected: 3
Drifts auto-remediated: 3
Drifts requiring human intervention: 0

Timeline:
  02:17 - NetworkPolicy deleted in payment namespace
            Source: kubectl (user: wolfgang-definitely-not-a-wolf@company.com)
            Detection time: <1 minute
            Remediation: ArgoCD auto-restored in 4 minutes
            Status: Resolved ✓

  08:43 - Deployment resource limits removed in staging
            Source: helm upgrade (missing values file, accidental)
            Detection time: <2 minutes
            Remediation: Kyverno mutation re-applied defaults
            Status: Resolved ✓

  14:22 - RBAC ClusterRoleBinding modified manually
            Source: kubectl patch (user: james@company.com)
            Detection time: <1 minute
            Remediation: Policy FAIL flagged, ArgoCD queued restore
            Requires human review: james applied a needed access grant
            Status: Under review (james has been notified)
```

-----

## Continuous Compliance: Never Trust a Weekly Scan 📊

The auditor asked: *“Are your clusters compliant with CIS Kubernetes Benchmark?”*

In the old world, the answer was: *“We ran a scan last Tuesday and everything looked fine.”*

The problem with Tuesday scans: the Wolf moves on Wednesday.

NCH maps Kyverno policies to specific compliance control requirements and verifies them continuously:

```
CIS KUBERNETES BENCHMARK — LIVE COMPLIANCE STATUS
══════════════════════════════════════════════════

As of: 02 May 2026, 14:47:23 UTC (2 minutes ago)

Cluster: brenda-prod
  1.1  Control Plane Node Configuration     ████████████ 97% (41/42 controls)
  2.1  Worker Node Configuration            ████████████ 100% (18/18 controls)
  3.1  RBAC and Service Accounts            ████████████ 94% (16/17 controls)
  4.1  Pod Security Standards               ████████████ 100% (12/12 controls)
  5.1  Network Policies                     ████████████ 100% (8/8 controls)
  5.2  Secrets Management                   ███████████░ 91% (10/11 controls)
  
OVERALL: 97.4% compliant (107/110 controls)

GAPS (3 controls):
  1.1.21 - Audit log max size not configured  → Fix PR available
  3.1.8  - Service account token expiry       → 89 days remaining
  5.2.3  - Secrets encrypted at rest          → External KMS integration pending
```

The compliance percentage updates in real time. If Wolfgang deletes a NetworkPolicy, the percentage drops within seconds. It is not Tuesday’s number. It is *now’s* number.

-----

## CIS, PCI-DSS, HIPAA, SOC 2: The Regulatory Frameworks 📋

Different organisations have different compliance requirements. NCH maps to all the major ones:

|Framework                   |What it checks                         |Who needs it                           |
|----------------------------|---------------------------------------|---------------------------------------|
|**CIS Kubernetes Benchmark**|Kubernetes hardening best practices    |Everyone running Kubernetes (should be)|
|**PCI-DSS**                 |Controls for handling payment card data|Fintech, retail, any payment processing|
|**HIPAA**                   |Controls for healthcare information    |Healthcare, health insurance           |
|**SOC 2**                   |Service organisation controls for trust|SaaS companies, cloud services         |
|**NIST SP 800-190**         |Container security guidance            |US government contractors              |

NCH does not just list the controls. It maps each control to specific Kyverno policies and provides evidence:

```
PCI-DSS COMPLIANCE EVIDENCE PACKAGE — Generated on demand
══════════════════════════════════════════════════════════

Requirement 6.3 - Security Vulnerabilities
  Control 6.3.3: Protect systems from known vulnerabilities
  
  Evidence:
    ✓ Policy: disallow-images-with-critical-cves (enforced)
    ✓ Proof: 0 pods running images with critical CVEs as of 14:47:23
    ✓ Audit log: Last 90 days of policy enforcement events (attached)
    ✓ Remediation record: 12 CVE violations found and fixed in Q1 2026
    
  Status: COMPLIANT
  Last verified: 02 May 2026, 14:47:23 UTC

Requirement 7.2 - Least Privilege Access
  Control 7.2.1: Restrict access to system components
  
  Evidence:
    ✓ Policy: disallow-cluster-admin-binding (enforced)
    ✓ Policy: restrict-service-account-permissions (enforced)
    ✓ Proof: 0 service accounts with cluster-admin as of 14:47:23
    ✓ RBAC audit log: All permission changes in last 90 days (attached)
    
  Status: COMPLIANT

[DOWNLOAD FULL EVIDENCE PACKAGE — 47 controls, 312 evidence items]
```

The auditor arrives on Thursday. The evidence package was generated in 45 seconds. The auditor, who expected to spend a week gathering evidence, is done by lunch.

Wolfgang, who had hoped the audit would reveal gaps his attack could exploit, watches this happen and makes a note in his journal: *“They can produce compliance evidence for 47 controls in under a minute. This is not the gap I was looking for.”*

-----

## The Tamper-Proof Audit Log: The Permanent Record 📚

Everything NCH tracks goes into an audit log that cannot be modified after the fact:

```
AUDIT LOG: 02 May 2026
══════════════════════════════════════════════════════

02:17:43 | VIOLATION | User: wolfgang-[redacted] | kubectl delete networkpolicy
           Namespace: payment | Policy: require-network-policy
           Action: Deleted NetworkPolicy default-deny-all
           
02:17:44 | ALERT | NCH: Policy failure detected in payment namespace

02:21:12 | REMEDIATION | ArgoCD | NetworkPolicy restored: default-deny-all

02:21:13 | RESOLUTION | NCH: Policy compliance restored in payment namespace

[...]

AUDIT LOG INTEGRITY:
  Signed: ✓ (cryptographic hash chain)
  Tamper detection: ✓ (any modification invalidates the hash chain)
  Export format: JSON, CSV, PDF (for auditors)
  Retention: 90 days default (configurable)
```

Wolfgang deleted a NetworkPolicy. The deletion is in the audit log forever. His user account is in the audit log forever. The timestamp is in the audit log forever. The restoration is in the audit log forever.

*“This is,”* Wolfgang says quietly, *“a really thorough audit log.”*

-----

## The Cost Wolf: An Unexpected Guest 💸

In the middle of Episode 7, a lesser-known villain appears: the Cost Wolf. This one does not breach clusters. He just runs expensive workloads in them.

```
NCH RESOURCE GOVERNANCE ALERT
══════════════════════════════════════════════════════

QUOTA VIOLATIONS DETECTED:

Namespace: machine-learning-experiments
  CPU requested: 47 cores (quota: 8 cores)
  RAM requested: 384 GB (quota: 64 GB)
  
  Root cause: 3 researchers launched large training jobs simultaneously
  Cost impact: ~$8,400/hour if this cluster is on cloud credits
  
  Action: ResourceQuota enforced — additional pods blocked
  
  Orphaned resources detected:
    PVC: training-data-2024-backup (12TB, unused 90+ days)
    Cost impact: ~$240/month storage
    Owner: departed-employee@company.com
    Recommended action: Delete after 30-day notice
  
  [Generate Cleanup PR] [Notify Team] [Extend Quota Temporarily]
```

Kyverno’s ResourceQuota generation (from Episode 4) capped the namespace. No researcher can request more than the quota allows. The $8,400/hour experiment was blocked by a 6-line YAML policy.

The Cost Wolf growls. ResourceQuotas are his natural enemy.

-----

## Wolfgang’s Final Chimney Attempt: A Statistical Summary 📊

```
OPERATION CHIMNEY: Attempted configuration drift at off-hours
══════════════════════════════════════════════════════════════

Attack window targeted: 2:00am–6:00am (assumed low monitoring)
Attack result: Detection in <1 minute (background controller never sleeps)
Auto-remediation: 4 minutes
Alert notifications: 3 (NCH, Slack, SIEM)
Audit log entries: 7 (creation, violation, alert, remediation x2, closure)

Analysis: 
  - "Off-hours" provides no advantage against continuous monitoring
  - Drift window was 4 minutes, insufficient for operational impact
  - Audit trail is tamper-proof and permanent
  - Compliance percentage recovered immediately
  - No compliance framework controls were negatively impacted

Conclusion: The pot was boiling when I arrived. The pot was boiling when 
            I left. There was no moment when the pot was not boiling.

Career reflection: Perhaps I should have gone into legitimate DevSecOps
                   consulting. I appear to have extensive expertise.
```

-----

In **Episode 8**, Wolfgang puts down his hacking tools and picks up a pen. He writes his memoir. The three piglets secure the whole forest. And we revisit every concept from the series in one final fairytale summary.

-----

**🔗 Resources**

- **Continuous compliance**: [nirmata.com/nirmata-control-hub](https://nirmata.com/nirmata-control-hub/)
- **CIS Kubernetes Benchmark**: [nirmata.com](https://nirmata.com)
- **Drift control**: [nirmata.com](https://nirmata.com)
- **Cost governance**: [nirmata.com/cost-savings](https://nirmata.com/cost-savings/)

-----

*🐺 Big Bad Wolf Meets Nirmata — the chimney was also covered. The pot is always boiling.*
