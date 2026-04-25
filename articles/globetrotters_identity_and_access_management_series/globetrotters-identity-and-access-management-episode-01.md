---
title: "Globetrotters Identity and Access Management 🌍 Ep.1"
part: 1
published: false
description: "Episode 1: Every international traveller faces the same sequence — passport, visa, checkpoint, stamp, entry. Identity and Access Management is that sequence, industrialised. Meet ACME’s IAM stack: SailPoint, RWT, IDV, LDAP, and the load balancer that serves as our Test Factory starting point."
tags: [iam, security, ldap, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters_identity_and_access_management_series/globetrotters-identity-and-access-management-episode-01.png"
series: "Globetrotters Identity and Access Management Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 1: The Border Crossing

> *“A passport does not tell you who the person is. It tells you who the issuing government says they are — and that a government with a verifiable seal vouches for it.”*

-----

## Why Every Organisation Needs Border Control 🛂

Consider what happens when you arrive at an international border. You present your passport. The officer checks it is genuine — the holographic seal, the biometric chip, the issuing authority’s signature. Then the officer checks the immigration database: has a valid visa been issued? Is there a travel ban? Has the entry permit expired? Only if every check passes do you hear the stamp, the “welcome,” and the wave through.

Remove any one of those layers and the border collapses. A passport without a visa database is theatre. A database without a genuine document is guesswork. A stamp without expiry is permanent access to everywhere.

**Identity and Access Management** is that border control, applied to every system, service, API, and directory in an organisation. It answers three questions: who are you, what are you allowed to do, and can I verify that claim right now?

ACME’s IAM stack — the subject of this series — answers those three questions across five architectural layers. This episode maps every layer to a border-crossing concept, lays out the complete topology, and explains how the Test Factory Secure Interface Enablement solution enters the system.

-----

## 🗂️ SIPOC — The Border Crossing

|**Suppliers**         |**Inputs**                                        |**Process**                                                    |**Outputs**                                                  |**Customers**                                                 |
|----------------------|--------------------------------------------------|---------------------------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------|
|HR / identity events  |Onboarding, role changes, offboarding triggers    |SailPoint governs lifecycle: provision, deprovision, certify   |Entitlements pushed to downstream systems (RWT, LDAP)        |Every service and system that relies on accurate identity data|
|Clients / applications|Authentication requests with credentials or tokens|RWT issues tokens; IDV validates them; LDAP resolves attributes|A verified identity context: who this is and what they may do|Protected APIs, LDAP-bound services, test execution containers|
|ACME Root CA          |Certificate signing requests                      |PKI issues and validates X.509 certificates                    |Trusted TLS/mTLS connections across the infrastructure       |Every LDAPS connection, every mTLS handshake in the topology  |

-----

## The Globetrotter Metaphor: Every IAM Concept, Explained Once 🌐

Before a single technical detail, commit this table to memory. Every episode returns to it.

|Border / travel concept                             |IAM / ACME concept                                                                        |
|----------------------------------------------------|------------------------------------------------------------------------------------------|
|Your passport                                       |Your digital identity — the authoritative record of who you are                           |
|The immigration ministry                            |**SailPoint PRD** — the governance platform that decides who gets what access             |
|Issuing a new visa                                  |Provisioning — creating or granting access entitlements                                   |
|Revoking a visa                                     |Deprovisioning — removing access when it is no longer needed                              |
|The annual visa review                              |Access certification — are these permissions still valid?                                 |
|The border kiosk                                    |**RWT** (Read/Write Token service) — issues and validates OAuth access tokens             |
|The entry stamp in your passport                    |An OAuth bearer token — present it at each checkpoint                                     |
|The border officer                                  |**IDV** (Identity Validation) — cross-checks your stamp against the ministry’s records    |
|The ministry’s filing cabinet                       |**LDAP directories** — the authoritative record of every identity, group, and attribute   |
|The checkpoint booth dispatcher                     |**LDAP LB-T** — the load balancer that routes queries to the next available LDAP server   |
|Two border offices in different cities              |**gds-city-a / gds-city-b** — dual-DC LDAP servers for high availability                  |
|Sealed diplomatic pouch                             |**LDAPS (port 636)** — encrypted LDAP; no one reads it in transit                         |
|Open postcard                                       |**LDAP (port 389)** — unencrypted; readable by anyone on the network                      |
|The nation’s document-issuing authority             |**ACME Root CA** — the cryptographic root that makes certificates trustworthy             |
|Biometric ID card                                   |**Client certificate (Keyfactor-issued)** — cryptographically unforgeable machine identity|
|Both parties showing credentials                    |**mTLS** — both the client and server present certificates                                |
|The visa categories (tourist/business/diplomatic)   |**LDAP groups and roles** — what you are authorised to access                             |
|The dedicated inspection lane for registered freight|**LDAP LB-T** — the test-designated entry point for our Test Factory solution             |

-----

## ACME’s Five-Layer IAM Stack 🏛️

The topology has five layers, read top-to-bottom. Think of them as the five zones of a large international airport: governance upstairs, token services at the gate, identity validation at the desk, the load balancer as the queue management system, and the LDAP directories as the immigration records room.

```
Layer 1 — Identity Governance
  ┌──────────────────────────┐
  │      SailPoint PRD       │  The immigration ministry
  │  (Identity Lifecycle,    │  Decides who gets what, for how long
  │   Certification, Roles)  │
  └────────┬──────────┬──────┘
           │          │
           ▼          ▼

Layer 2 — Token Services
  ┌──────────┐    ┌──────────┐
  │ RWT PRD  │    │ RWT ACC  │  The border kiosks (PRD and ACC lanes)
  │ (OAuth   │    │ (OAuth   │  Issue and validate bearer tokens
  │ Tokens)  │    │ Tokens)  │
  └────┬─────┘    └────┬─────┘
       │               │
       ▼               ▼

Layer 3 — Identity Validation
  ┌──────────┐    ┌──────────┐
  │ IDV PRD  │    │ IDV ACC  │  The border officers
  │(Token ↔  │    │(Token ↔  │  Cross-check stamps against the filing cabinet
  │ LDAP     │    │ LDAP     │
  │ bridge)  │    │ bridge)  │
  └────┬─────┘    └──────────┘
       │
       ▼

Layer 4 — LDAP Load Balancer
  ┌──────────────────────────┐
  │   GMF PRD LDAP LB-T     │  ← ★ OUR STARTING POINT
  │  (Test Load Balancer)    │  The checkpoint booth dispatcher
  └────────┬──────────┬──────┘
           │          │
           ▼          ▼

Layer 5 — LDAP Directory Servers
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │AUTH GMF PRD  │  │AUTH GMF PRD  │  │AUTH GMF ACC  │
  │  city-a      │  │  city-b      │  │(Acceptance)  │
  │(CITY-A DC)   │  │(CITY-B DC)   │  │              │
  └──────────────┘  └──────────────┘  └──────────────┘
```

-----

## Layer 1: SailPoint — The Immigration Ministry 🏛️

SailPoint PRD is the immigration ministry. It is the source of truth for who should have access to what and for how long. Critically, it does not handle real-time authentication — just as the immigration ministry does not stand at the border checking passports, it works in the background, issuing and revoking the permissions that downstream systems enforce.

What SailPoint governs:

- **Provisioning** — when someone joins the organisation or changes roles, SailPoint issues the correct entitlements downstream
- **Deprovisioning** — when they leave or change roles, SailPoint revokes what is no longer warranted
- **Access certification** — periodic reviews: does this person still need this level of access?
- **Role management** — defining the categories of access (tourist, business, diplomatic) and who qualifies for each

## Layer 2: RWT — The Border Kiosk 🛂

RWT (Read/Write Token service) sits at the gate. When a client application needs to authenticate, it approaches RWT and exchanges credentials for an OAuth access token — the entry stamp. SailPoint has already established what that identity is allowed to do; RWT translates that into a runtime bearer token that the client can present at each protected resource.

PRD and ACC kiosks serve different lanes. The acceptance kiosk issues stamps only valid in the acceptance zone.

## Layer 3: IDV — The Border Officer 👮

IDV (Identity Validation) is the officer at the desk who looks at your stamp and checks it against the ministry’s records. When a token is presented to a protected resource, IDV validates that it is genuine and cross-references the LDAP directory to resolve group memberships and attribute claims. IDV is the bridge between the OAuth/OIDC world and the LDAP world.

## Layer 4: LDAP LB-T — The Checkpoint Dispatcher 🚦

The GMF PRD LDAP LB-T is the dispatcher — the person at the checkpoint who says “booth three is free, please proceed.” It distributes LDAP queries across the two production GDS instances for load and availability. The “T” marks it as the test-designated dispatcher — the lane our Test Factory solution uses.

This is our **starting point**.

## Layer 5: AUTH GMF PRD — The Filing Cabinet 🗄️

At the bottom of the stack are the physical LDAP servers — the filing cabinets that hold every user object, group membership, and authentication credential for the General Manufacturing (GMF) domain. Two of them, in two different cities, so that if one data centre is unavailable, the other serves all queries.

-----

## Our Solution’s Entry Point 🏁

The Test Factory Secure Interface Enablement solution enters the IAM stack at **GMF PRD LDAP LB-T** — directly at Layer 4, bypassing the full OAuth flow for service authentication and using LDAPS (port 636) for an encrypted, direct directory bind.

```
┌──────────────────┐   LDAPS :636   ┌──────────────────┐   LDAP   ┌──────────────────┐
│  Test Factory    │ ─────────────► │  GMF PRD         │ ───────► │  AUTH GMF PRD    │
│  Container       │                │  LDAP LB-T       │          │  city-a / city-b │
│  (our solution)  │                │  ★ START HERE    │          │  (gds-city-a/b)  │
└──────────────────┘                └──────────────────┘          └──────────────────┘
```

-----

## The Series Map: Eight Episodes 🗺️

|#|Episode                         |Border metaphor         |IAM concept                                         |
|-|--------------------------------|------------------------|----------------------------------------------------|
|1|*This one* — The Border Crossing|Arriving at the airport |ACME IAM topology overview                          |
|2|The Immigration Ministry        |The ministry of visas   |SailPoint: governance, provisioning, certification  |
|3|The Entry Stamp                 |The border kiosk        |OAuth 2.0 / OIDC, RWT, bearer tokens                |
|4|The Border Officer              |The desk validation     |IDV: token-to-LDAP bridge, attribute resolution     |
|5|The Ministry’s Filing Cabinet   |The records room        |LDAP: directory structure, objects, groups          |
|6|The Checkpoint Dispatcher       |The queue manager       |LDAP LB-T: load balancing, HA, test isolation       |
|7|Sealed Diplomatic Pouches       |Tamper-evident documents|PKI, TLS, mTLS, certificates, trust chains          |
|8|The Dedicated Test Lane         |The inspection lane     |Test Factory entry point, auth paths, implementation|

In **Episode 2**, the immigration ministry. SailPoint PRD — how identity governance works, what provisioning and deprovisioning mean in practice, and why access certification is the audit that keeps the border honest.

-----

**🔗 Resources**

- **SailPoint documentation**: [documentation.sailpoint.com](https://documentation.sailpoint.com)
- **OAuth 2.0 RFC 6749**: [rfc-editor.org/rfc/rfc6749](https://www.rfc-editor.org/rfc/rfc6749)
- **LDAP RFC 4511**: [rfc-editor.org/rfc/rfc4511](https://www.rfc-editor.org/rfc/rfc4511)

-----

*🌍 Globetrotters Identity and Access Management Series — crossing the IAM border one checkpoint at a time, using ACME’s real-world SailPoint, RWT, IDV, and LDAP topology as the map.*
