---
title: "Globetrotters Identity and Access Management 🌍 Ep.2"
part: 2
published: false
description: "Episode 2: The immigration ministry does not stand at the border checking passports — it decides, in advance, who is allowed to enter and under what conditions. SailPoint PRD is ACME’s immigration ministry: provisioning, deprovisioning, access certification, and the role catalogue that defines every visa category."
tags: [iam, sailpoint, security, governance]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters_identity_and_access_management_series/globetrotters-identity-and-access-management-episode-02.png"
series: "Globetrotters Identity and Access Management Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Globetrotters IAM! 🌍

## Episode 2: The Immigration Ministry

> *“The visa officer never stands at the border. Their work happens weeks earlier, in an office, reviewing applications, issuing permits, and updating the database that the border officer will consult when the traveller arrives.”*

-----

## The Ministry That Never Sleeps 🏛️

There is a common misconception about how immigration control works. Most people visualise the border officer — the person who checks your passport, scans it, and waves you through. But the border officer is the last link in a very long chain. The real work happened at the visa office, months earlier: the application reviewed, the background check completed, the permit issued or denied, the record entered in the national database.

The border officer does not decide anything. The officer merely enforces what the ministry has already decided.

SailPoint PRD is ACME’s immigration ministry. It does not authenticate users in real time. It does not validate passwords or check tokens. What it does is far more important: it is the authoritative, upstream source of truth about who should have access to what, for how long, and under what conditions. Every downstream component — RWT, IDV, LDAP — enforces decisions that SailPoint has already made.

-----

## 🗂️ SIPOC — The Immigration Ministry

|**Suppliers**                   |**Inputs**                                                                                |**Process**                                                                     |**Outputs**                                                                            |**Customers**                                                                                           |
|--------------------------------|------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
|HR system / business events     |Hire event, role change, departure, contract end                                          |Identity lifecycle management: provision, update, deprovision                   |Updated entitlements in downstream systems (LDAP groups, RWT scopes, application roles)|RWT (token scopes derived from SailPoint entitlements), LDAP (group memberships), protected applications|
|Access request system           |“I need access to X” submitted by employee or manager                                     |Approval workflow: manager → data owner → automated provisioning                |Access granted or denied; new LDAP group membership or application role                |The requesting employee; audit trail for compliance                                                     |
|Certification campaign scheduler|Quarterly / annual review trigger                                                         |Send certification task to each access owner; record approve / revoke decision  |Revoked entitlements for anyone not re-certified; clean access inventory               |Compliance teams; downstream LDAP reflects the outcome                                                  |
|Role catalogue                  |Business role definitions (“junior analyst”, “platform engineer”, “test factory operator”)|Map roles to entitlement sets; assign roles to identities based on HR attributes|Automatic provisioning of the correct entitlement bundle for each role                 |New starters get the right access on day one without manual intervention                                |

-----

## What SailPoint Governs: The Four Functions 🗂️

### 1. Provisioning — Issuing the Visa

When a new traveller joins ACME, they need a visa. Not one visa — typically a bundle: access to the email system, the VPN, the test environment, the source control platform. The correct bundle depends on their role, their team, and their data centre location.

Provisioning is the act of creating that bundle and pushing it to the downstream systems that enforce it. SailPoint receives the trigger (an HR event: “new hire, role = Platform Engineer, team = Test Factory”), evaluates the role catalogue, determines which entitlements that role requires, and pushes them:

- To the LDAP directory: “add this user object to these groups”
- To RWT: “this identity is allowed these OAuth scopes”
- To application-level systems: “grant this account in these applications”

From the traveller’s perspective, they arrive at the border on day one and every checkpoint already knows they are expected, their visa is valid, and their lane is ready.

```
HR Event: New hire
    │
    ▼
SailPoint evaluates role catalogue
    │
    ├──► LDAP: create user object, add to groups
    │         (auth.acme.com: CN=Jane.Smith,OU=TestFactory,DC=gmf,DC=acme,DC=com)
    │
    ├──► RWT: register allowed OAuth scopes for this identity
    │         (scopes: test:execute, vault:read, ldap:bind)
    │
    └──► Application systems: grant role in each SUT
```

### 2. Deprovisioning — Revoking the Visa

A traveller’s permit has expired. They have changed roles. They have left ACME. The ministry revokes the visa. Not eventually, not “when someone notices” — immediately, triggered by the same HR event stream.

Deprovisioning is the act of removing entitlements from every downstream system simultaneously. This is where many IAM implementations fail: access is granted promptly but revoked slowly. An effective SailPoint implementation ensures that when a departure event fires, within minutes the LDAP groups are updated, the OAuth scopes are narrowed, and the application roles are removed.

The border officer who checked the database yesterday may have waved this traveller through. The one who checks today will see an expired record.

```
HR Event: Departure / role change
    │
    ▼
SailPoint evaluates what must be removed
    │
    ├──► LDAP: remove user from groups, optionally disable account
    ├──► RWT: revoke or narrow OAuth scopes
    └──► Application systems: remove role or disable account
```

### 3. Access Certification — The Annual Visa Review

Every visa has a review date. The ministry periodically asks: “Do you still need this?” Not because they distrust the traveller, but because entitlements accumulate. Engineers get temporary access to a system during an incident and the access is never removed. A tester gets elevated rights for a project and keeps them when the project ends. Over time, the directory becomes a museum of outdated permissions.

Access certification is the process that prevents this. At scheduled intervals, SailPoint sends a certification campaign to every access owner: “Review the following people who have access to your system. Approve or revoke.” If the owner does not respond, the access is revoked by default (certify-or-lose).

The outcome is pushed to LDAP and the application layer. Anyone who was not explicitly re-certified loses access.

```
Certification campaign triggered
    │
    ▼
SailPoint generates certification tasks for each access owner
    │
    ├──► Owner approves → access retained in LDAP and applications
    └──► Owner revokes / does not respond → access removed from LDAP and applications
```

**From a Test Factory perspective**: test environments routinely accumulate over-privileged service accounts. Certification campaigns catch these accumulations. A service account that was granted elevated rights for a specific test engagement should not retain those rights indefinitely.

### 4. Role Management — The Visa Category Catalogue

The immigration ministry does not issue custom, one-off visas for every traveller. It defines categories: tourist, business, diplomatic, transit, work permit. Each category carries a standard set of rights and restrictions.

SailPoint’s role catalogue defines ACME’s equivalent categories. A “Platform Engineer” role carries one entitlement bundle. A “Test Factory Operator” role carries another. A “Read-Only Auditor” role carries a third. When an identity is assigned a business role, SailPoint automatically provisions the entire entitlement bundle — no individual line-item approvals needed.

|Business role         |LDAP groups provisioned             |OAuth scopes                   |Typical use case                     |
|----------------------|------------------------------------|-------------------------------|-------------------------------------|
|Platform Engineer     |`grp-platform-eng`, `grp-test-infra`|`platform:admin`, `vault:write`|Full infrastructure access           |
|Test Factory Operator |`grp-testfactory`, `grp-ldap-bind-t`|`test:execute`, `vault:read`   |Test execution against LB-T          |
|Read-Only Auditor     |`grp-audit-read`                    |`audit:read`                   |Compliance review access             |
|Service Account — Test|`grp-svc-test-bind`                 |`ldap:bind`                    |Machine-to-machine LDAP bind via LB-T|

-----

## What SailPoint Does NOT Do: The Ministry’s Limits 🚫

Understanding SailPoint requires understanding what it deliberately does not do:

**SailPoint does not authenticate in real time.** It does not check passwords, does not validate tokens at request time, does not respond to authentication events. Authentication is handled by RWT (tokens) and the LDAP servers (directory bind).

**SailPoint does not stand at the border.** When a user authenticates against LDAP or presents a token to RWT, SailPoint is not in that request path. It has already done its work: the LDAP groups are correct, the token scopes are correct, the ministry’s filing cabinet is up to date. The border officer (IDV) enforces the ministry’s prior decisions without calling the ministry in real time.

**SailPoint is upstream, not inline.** This is a critical architectural distinction. Adding SailPoint to the authentication path would be like having every traveller call the visa office during the passport check — impossibly slow. Instead, SailPoint keeps the filing cabinet accurate, and the filing cabinet handles real-time queries.

-----

## The SailPoint → LDAP Relationship in ACME’s Topology 🔗

```
SailPoint PRD
    │
    │  Bidirectional arrows in the SVG to RWT PRD and RWT ACC:
    │  SailPoint provisions identity claims and scopes into the token service
    │
    ├──► RWT PRD (Production token service)
    │       "This identity is authorised for these OAuth scopes"
    │
    └──► RWT ACC (Acceptance token service)
            "Same governance, different environment lane"

SailPoint also writes directly to LDAP:
    └──► AUTH GMF PRD (via GDS replication)
            Groups and user attributes reflect SailPoint's governance decisions
```

The bidirectional arrows in ACME’s SVG between SailPoint and RWT reflect the ongoing synchronisation: SailPoint provisions entitlement data into RWT’s identity store, and RWT reports back token usage events that SailPoint can use for audit and certification decisions.

-----

## Practical Implications for the Test Factory 🔧

For the Test Factory Secure Interface Enablement solution, SailPoint governance has three direct implications:

**Service account lifecycle.** The service account our solution uses to bind to LDAP LB-T (Layer 4) is managed by SailPoint. Its creation, its group memberships (`grp-svc-test-bind`), and its decommissioning when the project ends are all SailPoint lifecycle events — not manual LDAP edits.

**Role certification.** If our service account is granted elevated test rights during an engagement, the access certification campaign will require the access owner to explicitly re-approve those rights quarterly. If they do not, the rights are removed — and our bind will fail. We must track certification cycles and ensure our service accounts are re-certified before each certification window closes.

**Scope of access.** The OAuth scopes our solution may eventually require (for the RWT path — Episode 3) are defined by SailPoint’s role catalogue. We need to ensure that the “Test Factory Operator” role includes the correct scopes before the first token request.

-----

In **Episode 3**, we leave the ministry and arrive at the border kiosk. RWT issues the entry stamp — the OAuth bearer token — and we examine exactly how that stamp works, what it contains, and when it expires.

-----

**🔗 Resources**

- **SailPoint Identity Lifecycle**: [documentation.sailpoint.com/identityiq/help](https://documentation.sailpoint.com/identityiq/help/)
- **SailPoint Access Certification**: [documentation.sailpoint.com/identityiq/help/certification](https://documentation.sailpoint.com/identityiq/help/)
- **Role-Based Access Control (NIST)**: [csrc.nist.gov/projects/role-based-access-control](https://csrc.nist.gov/projects/role-based-access-control)

-----

*🌍 Globetrotters Identity and Access Management Series — crossing the IAM border one checkpoint at a time.*
