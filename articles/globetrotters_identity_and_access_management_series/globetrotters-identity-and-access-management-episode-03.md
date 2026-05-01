---
title: "Globetrotters Identity and Access Management 🌍 Ep.3"
part: 3
published: false
description: "Episode 3: The border kiosk does not check your entire life history every time you pass a checkpoint. It issues an entry stamp — a time-limited token that downstream checkpoints can verify without calling the ministry again. RWT is that kiosk. OAuth bearer tokens are that stamp. This is how modern authentication scales."
tags: [iam, oauth, security, authentication]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters_identity_and_access_management_series/globetrotters-identity-and-access-management-episode-03.png"
series: "Globetrotters Identity and Access Management Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: The Entry Stamp

> *“The entry stamp in your passport is not a full background check. It is proof that a full background check already happened — and that you passed.”*

-----

## The Stamp That Travels With You 🖊️

Imagine an airport without boarding passes. Every time you move from the check-in desk to security, from security to the gate, from the gate to the aircraft, you present your passport and someone calls the airline to verify your ticket. The calls stack up. Every checkpoint is slower than the one before. The system grinds to a halt.

Boarding passes exist precisely to avoid this. The airline checks your ticket once — at check-in — and issues a boarding pass. That pass is a tamper-evident, time-limited artefact that every subsequent checkpoint can verify locally without calling the airline again. Security scans the barcode. The gate scans it again. The aircraft crew validates the seat number. One verification event, many downstream checkpoints, zero repeated calls to the origin.

The OAuth access token is that boarding pass. **RWT** is the check-in desk that issues it.

-----

## 🗂️ SIPOC — The Border Kiosk

|**Suppliers**                      |**Inputs**                                                        |**Process**                                                                                     |**Outputs**                                             |**Customers**                                                                    |
|-----------------------------------|------------------------------------------------------------------|------------------------------------------------------------------------------------------------|--------------------------------------------------------|---------------------------------------------------------------------------------|
|Client application / service       |Client credentials (client_id + client_secret) or user credentials|OAuth 2.0 token request → RWT validates credentials against identity data sourced from SailPoint|Access token (JWT) + optional refresh token             |Client — presents the access token as a Bearer header on every subsequent request|
|SailPoint PRD                      |Provisioned scopes and claims for each identity                   |RWT uses SailPoint’s entitlement data to populate token claims                                  |JWT payload: subject, scopes, roles, expiry             |Every protected resource that receives the token                                 |
|Protected resource (API or service)|Bearer token in `Authorization: Bearer <token>` header            |IDV validates the token signature and resolves claims → Episode 4                               |Allowed or denied access, with resolved identity context|The resource owner’s business logic                                              |

-----

## OAuth 2.0: The Entry Stamp Protocol 📋

OAuth 2.0 is the protocol. RWT is ACME’s implementation of the OAuth 2.0 authorisation server. The core flow — for machine-to-machine (M2M) communication, which is what the Test Factory uses — is the **Client Credentials Grant**:

```
┌────────────────┐                          ┌──────────────┐
│ Client          │  1. POST /token          │   RWT PRD    │
│ (Test Factory   │ ─────────────────────►   │   (Auth      │
│  or other app)  │   client_id              │    Server)   │
│                 │   client_secret          │              │
│                 │   grant_type=            │              │
│                 │   client_credentials     │              │
│                 │   scope=test:execute     │              │
│                 │                          │              │
│                 │  2. 200 OK               │              │
│                 │ ◄─────────────────────── │              │
│                 │   access_token: <JWT>    │              │
│                 │   expires_in: 3600       │              │
│                 │   token_type: Bearer     │              │
└────────────────┘                          └──────────────┘
          │
          │  3. GET /api/protected
          │     Authorization: Bearer <JWT>
          ▼
┌────────────────┐
│ Protected      │
│ Resource / SUT │  → IDV validates the token (Episode 4)
└────────────────┘
```

### Step 1: The credential exchange

The client presents its identity to RWT: `client_id` (who it claims to be) and `client_secret` (proof of that claim). The `scope` parameter specifies what the client is asking to do: `test:execute`, `vault:read`, `ldap:bind`.

RWT checks these credentials against the identity data provisioned by SailPoint. If the client_id is registered, the secret matches, and the requested scopes are authorised for this identity, RWT issues a token.

### Step 2: The stamp

RWT returns a **JSON Web Token (JWT)** — a base64-encoded, cryptographically signed payload containing:

```json
{
  "iss": "https://rwtprd.acme.com",
  "sub": "svc-testfactory-prod",
  "aud": "https://sut.acme.com",
  "exp": 1745510400,
  "iat": 1745506800,
  "scope": "test:execute vault:read",
  "acme_roles": ["grp-testfactory", "grp-ldap-bind-t"],
  "environment": "PRD"
}
```

|JWT claim        |Meaning                                       |Border analogy                          |
|-----------------|----------------------------------------------|----------------------------------------|
|`iss` (issuer)   |Which RWT server issued this token            |Which consulate issued the visa         |
|`sub` (subject)  |Who this token represents                     |The passport holder’s name              |
|`aud` (audience) |Which systems this token is valid for         |Which countries this visa covers        |
|`exp` (expiry)   |Unix timestamp when the token expires         |The visa expiry date                    |
|`iat` (issued at)|When the token was issued                     |The date the visa was stamped           |
|`scope`          |What actions the token permits                |The visa category and permissions       |
|`acme_roles`     |LDAP group memberships resolved from SailPoint|The endorsements stamped in the passport|

The token is **signed** with RWT’s private key. Any recipient can verify the signature using RWT’s public key — without calling RWT again. This is the cryptographic equivalent of a holographic seal.

### Step 3: Presenting the stamp

The client presents the token as a Bearer header on every subsequent request:

```http
GET /api/protected-resource HTTP/1.1
Host: sut.acme.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

“Bearer” means: whoever bears this token is granted access. It is the wristband at the event — show it to enter each zone without re-proving your identity. This is why token security matters so much: a stolen token is a stolen wristband.

-----

## PRD vs ACC: Two Kiosks, Two Lanes 🛂

ACME operates two RWT instances:

|Instance   |Lane      |Stamps valid for  |Source of identity data                             |
|-----------|----------|------------------|----------------------------------------------------|
|**RWT PRD**|Production|Production systems|SailPoint PRD (production identities)               |
|**RWT ACC**|Acceptance|Acceptance systems|SailPoint PRD (same governance, separate ACC stamps)|

The same immigration ministry (SailPoint PRD) governs both lanes. But a stamp from the production kiosk is only valid in the production zone, and an acceptance stamp only works in acceptance. The `aud` (audience) claim enforces this: a token issued by RWT ACC with `aud: sut-acc.acme.com` will be rejected by a production system that expects `aud: sut-prd.acme.com`.

This separation protects production from acceptance-environment incidents. A compromise of the acceptance kiosk does not automatically compromise the production lane.

-----

## Token Lifecycle: The Stamp That Expires ⏱️

Every entry stamp has a validity period. Tokens are no different.

```
Token issued (iat)
│
├── Token valid period (typically 1 hour = 3600 seconds)
│   │
│   ├── Client uses token for API calls
│   │   (no repeated calls to RWT — the stamp is self-sufficient)
│   │
│   └── Token expires (exp)
│       │
│       ├── Client requests a new token (repeats Step 1)
│       │   OR
│       └── Client uses refresh token (if issued) to get a new access token
│           without repeating credential exchange
```

The **expiry** is a security control. A stolen token is only valid until it expires. If tokens lasted forever, a single compromise would be permanent. Short-lived tokens (minutes to hours) limit the blast radius of a credential theft.

**For the Test Factory solution**, token management requires:

1. Storing the client_id and client_secret securely (in a secrets vault — not hardcoded)
1. Caching the token for its valid period to avoid unnecessary round-trips to RWT
1. Detecting expiry (the `exp` claim) and refreshing before the token expires mid-test
1. Handling RWT being temporarily unavailable (token refresh failures during test execution)

-----

## OpenID Connect (OIDC): The Passport Extension 🪪

OAuth 2.0 is an authorisation protocol — it answers “what can you do?” OpenID Connect (OIDC) is an identity layer on top of OAuth 2.0 — it also answers “who are you?” by adding an **ID token** alongside the access token.

The ID token is a second JWT carrying identity claims: the user’s name, email, department, and any other attributes the identity provider (in ACME’s case, backed by SailPoint) has asserted about this identity.

For machine-to-machine use cases (like Test Factory), the OIDC ID token is less relevant — we know who the service account is. OIDC becomes important when human users authenticate to systems that need to personalise the experience or make user-specific authorisation decisions.

-----

## The RWT ↔ SailPoint Relationship in ACME’s Topology 🔗

The SVG shows bidirectional arrows between SailPoint PRD and both RWT PRD and RWT ACC. These arrows represent:

**Downward (SailPoint → RWT):** SailPoint continuously synchronises identity data to RWT — which scopes are authorised for which identities, what claims should be included in tokens issued for each subject.

**Upward (RWT → SailPoint):** Token usage events, authentication failures, and scope elevation requests flow back to SailPoint for governance visibility. If a service account requests scopes beyond what SailPoint has provisioned, RWT rejects the request and logs the attempt.

```
SailPoint PRD
  ↕  (identity data sync down; audit events up)
RWT PRD ────────────────────────────────────► Issues access tokens to clients
  │
  └──(scope sourced from SailPoint)──► JWT payload reflects SailPoint's governance
```

-----

## What RWT Does NOT Do: The Kiosk’s Limits 🚫

**RWT does not manage identity lifecycle.** It does not create or remove user accounts. It does not decide what scopes an identity should have. Those decisions belong to SailPoint.

**RWT does not validate tokens at every checkpoint.** Once a token is issued, each protected resource validates it locally using RWT’s public key — without calling RWT. RWT is in the path only for token issuance and, occasionally, token introspection.

**RWT does not reach into LDAP directly.** When a client requests a token with role claims, RWT uses identity data synchronised from SailPoint. IDV is the component that bridges tokens to live LDAP lookups — that is Episode 4.

-----

## Two Authentication Paths: Stamp vs Direct Bind 🛤️

ACME’s topology, and specifically our Test Factory solution’s architecture, supports two distinct authentication paths:

|Path             |Protocol         |ACME component   |Use case                                                  |
|-----------------|-----------------|-----------------|----------------------------------------------------------|
|**OAuth / Token**|HTTPS → RWT → IDV|RWT PRD / ACC    |SUT interfaces that require Bearer token auth             |
|**Direct LDAP**  |LDAPS → LDAP LB-T|GMF PRD LDAP LB-T|Service account bind for test execution (our primary path)|

The direct LDAP path is our starting point — Episode 6 and 8 cover it in detail. The OAuth path via RWT becomes relevant if future SUT interfaces require bearer token authentication rather than mTLS.

-----

In **Episode 4**, the border officer. IDV validates the stamp against the filing cabinet — the token-to-LDAP bridge that makes OAuth tokens meaningful in a directory-based infrastructure.

-----

**🔗 Resources**

- **OAuth 2.0 RFC 6749**: [rfc-editor.org/rfc/rfc6749](https://www.rfc-editor.org/rfc/rfc6749)
- **JSON Web Tokens (JWT) RFC 7519**: [rfc-editor.org/rfc/rfc7519](https://www.rfc-editor.org/rfc/rfc7519)
- **OpenID Connect specification**: [openid.net/specs/openid-connect-core-1_0.html](https://openid.net/specs/openid-connect-core-1_0.html)
- **OAuth 2.0 Client Credentials Grant**: [rfc-editor.org/rfc/rfc6749#section-4.4](https://www.rfc-editor.org/rfc/rfc6749#section-4.4)

-----

*🌍 Globetrotters Identity and Access Management Series — crossing the IAM border one checkpoint at a time.*
