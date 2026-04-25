---
title: "Globetrotters Identity and Access Management 🌍 Ep.4"
part: 4
published: false
description: "Episode 4: The border officer does not issue visas or manage the filing cabinet. They do one thing: they cross-check the stamp in your passport against the ministry’s records and resolve what you are permitted to do. IDV — Identity Validation — is that officer: the bridge between OAuth tokens and LDAP directories."
tags: [iam, security, ldap, authentication]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters_identity_and_access_management_series/globetrotters-identity_and_access_management-episode-04.png"
series: "Globetrotters Identity and Access Management Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 4: The Border Officer

> *“The officer at the desk does not decide the policy. They look at the stamp, consult the database, and make a binary determination: this person’s paperwork is in order, or it is not.”*

-----

## The Officer at the Desk 👮

The border kiosk issued the entry stamp (Episode 3). The filing cabinet holds every traveller’s full record (Episode 5). Between them stands the officer at the desk: the person who takes your stamped passport, opens the terminal, and checks that the stamp is genuine, that the record in the database matches, that the permitted activities align with what you are trying to do.

The officer does not manage the database. The officer does not issue stamps. The officer translates: from a claim (“I have this stamp, I’m allowed to do X”) to a verified, authoritative fact (“the database confirms this person has the group memberships that correspond to that claim, and those memberships are currently active”).

**IDV — Identity Validation** is that officer. It is the bridge between the OAuth/OIDC world (tokens, claims, bearer headers) and the LDAP world (directory binds, group objects, DN-based identity records). Without IDV, a token is just a string. With IDV, that string becomes a verified identity context with resolved permissions.

-----

## 🗂️ SIPOC — The Border Officer

|**Suppliers**                  |**Inputs**                                                |**Process**                                                                |**Outputs**                                                               |**Customers**                                                                |
|-------------------------------|----------------------------------------------------------|---------------------------------------------------------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------|
|Client application             |Bearer token in `Authorization` header                    |IDV validates JWT signature using RWT’s public key                         |Valid / invalid determination                                             |Protected resource — admits or rejects the request                           |
|RWT (token service)            |JWT with claims: `sub`, `scope`, `acme_roles`             |IDV cross-references token claims against live LDAP directory              |Enriched identity context: verified group memberships, resolved attributes|Protected resource — makes authorisation decisions using the enriched context|
|AUTH GMF PRD (LDAP directories)|User object with current group memberships, account status|LDAP lookup: is this account active? Are these group claims still accurate?|Confirmation that token claims match current directory state              |IDV — returns “yes, these claims are valid as of this moment”                |

-----

## The Two-Stage Validation 🔍

IDV performs validation in two distinct stages. Both must pass for a request to succeed.

### Stage 1: Token Integrity Validation

Before consulting the LDAP directory, IDV validates the token itself:

```
Received: Authorization: Bearer eyJhbGci...

IDV checks:
  ✓ Signature valid?          → Verify using RWT's public key
  ✓ Not expired?              → exp claim > now
  ✓ Audience correct?         → aud claim matches this service's expected audience
  ✓ Issuer trusted?           → iss claim matches RWT PRD or RWT ACC
  ✓ Issued-at plausible?      → iat claim is not in the future

If any check fails:
  → Return HTTP 401 Unauthorized
  → Log: "Token validation failed: [reason]"
  → Do NOT proceed to Stage 2
```

This stage requires no network call to RWT. The JWT’s cryptographic signature guarantees integrity — if RWT’s private key signed it and the signature verifies against the public key, the token is genuine. Stage 1 is entirely local.

### Stage 2: LDAP Attribute Resolution

Once the token’s integrity is confirmed, IDV performs a live lookup against the LDAP directory to:

1. Confirm the account is still active (not disabled by SailPoint since the token was issued)
1. Resolve current group memberships that may have changed since token issuance
1. Retrieve attributes needed for the authorisation decision (department, location, data classification level)

```
Token validated. Proceeding to LDAP resolution.

IDV → LDAP LB-T (port 636, LDAPS):
  BIND: cn=idv-svc,ou=services,dc=gmf,dc=acme,dc=com
  SEARCH: (uid=svc-testfactory-prod)
  BASE: dc=gmf,dc=acme,dc=com
  SCOPE: SUBTREE
  ATTRIBUTES: memberOf, accountStatus, department, l

LDAP returns:
  dn: uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
  memberOf: cn=grp-testfactory,ou=groups,dc=gmf,dc=acme,dc=com
  memberOf: cn=grp-ldap-bind-t,ou=groups,dc=gmf,dc=acme,dc=com
  accountStatus: active
  department: Test Factory
  l: city-a

IDV compares:
  Token claims acme_roles: ["grp-testfactory", "grp-ldap-bind-t"]
  LDAP memberOf:            ["grp-testfactory", "grp-ldap-bind-t"]
  Match: ✓

IDV resolves context:
  identity:   svc-testfactory-prod
  status:     active
  groups:     [grp-testfactory, grp-ldap-bind-t]
  department: Test Factory
  location:   city-a
  permitted:  test:execute, vault:read, ldap:bind
```

This enriched identity context is passed to the protected resource, which uses it to make its own authorisation decision.

-----

## Why Live LDAP Lookup Matters ⚡

A token issued an hour ago carries claims that were accurate an hour ago. But in that hour:

- SailPoint may have run a deprovisioning event (the account was terminated)
- An access certification campaign may have revoked a group membership
- A security incident may have disabled the account

The token is still cryptographically valid — RWT’s signature is genuine. But the claims it carries may no longer be accurate. Stage 2’s live LDAP lookup detects this:

```
Token claims: acme_roles: ["grp-testfactory", "grp-elevated-rights"]
LDAP actual:  memberOf:    ["grp-testfactory"]

Discrepancy detected: "grp-elevated-rights" was revoked since token issuance
IDV decision: reject the request, return HTTP 403 Forbidden
```

This is the border officer catching the traveller whose visa was revoked after the stamp was issued. The stamp looks genuine. But the database says otherwise.

-----

## IDV PRD vs IDV ACC: Separate Officers for Separate Lanes 👮‍♀️👮

ACME operates two IDV instances, mirroring the RWT separation:

|Instance   |Validates tokens from|Queries LDAP server         |Enforces                  |
|-----------|---------------------|----------------------------|--------------------------|
|**IDV PRD**|RWT PRD              |AUTH GMF PRD city-a / city-b|Production identity claims|
|**IDV ACC**|RWT ACC              |AUTH GMF ACC                |Acceptance identity claims|

IDV ACC never queries the production LDAP servers. A test token from RWT ACC is validated against the acceptance directory — even if the claim subject matches a production account, IDV ACC resolves the acceptance-environment version of that account.

This prevents acceptance token fraud from affecting production authorisation decisions.

-----

## IDV in the Full Connection Flow 🔗

The SVG connection flow, read through IDV’s lens:

```
SailPoint PRD
    │
    ▼
RWT PRD ──── issues token ────────────────────────────► Client
                                                         │
                                          Bearer token   │
                                                         ▼
                                               Protected Resource
                                                         │
                              "validate this token"      │
                                                         ▼
                                                      IDV PRD
                                                    ┌────────┐
                           Stage 1: local JWT verify │        │
                           Stage 2: LDAP lookup      │        │
                                                     └──┬─────┘
                                                        │
                              LDAP bind + search        │
                                                        ▼
                                                    GMF PRD LDAP LB-T
                                                    (distributes to city-a / city-b)
```

Note what this means for our Test Factory solution: when we use the **direct LDAP path** (LDAP LB-T), we bypass RWT and IDV entirely. Our solution binds directly to LDAP LB-T as a service account, using its own LDAP credentials. There is no token involved and no IDV in the path.

IDV becomes relevant for our solution in the **OAuth path** — when a SUT exposes an API that requires Bearer token authentication. In that case, we obtain a token from RWT and the SUT’s API layer calls IDV to validate it.

-----

## Token vs Direct LDAP: The Bridge and the Direct Road 🛤️

IDV exists because some applications speak OAuth (they expect tokens) while others speak LDAP (they bind directly against the directory). IDV is the bridge for the OAuth-speaking applications:

```
OAuth application          Direct LDAP application
      │                            │
      │  Bearer token              │  LDAP bind (DN + password)
      ▼                            ▼
   IDV PRD                    LDAP LB-T
      │                            │
      │  LDAP lookup               │  Direct query
      ▼                            ▼
 AUTH GMF PRD               AUTH GMF PRD
   (city-a/b)                 (city-a/b)
```

Both paths end at the same LDAP servers. IDV adds the token validation layer for applications that do not speak LDAP natively.

-----

## Practical Implications for the Test Factory 🔧

**Current architecture (direct LDAP):** Our solution uses LDAP LB-T directly. IDV is not in our current path. This is simpler and more performant for service account authentication.

**Future expansion (OAuth path):** If ACME requires our test execution workloads to authenticate to SUTs using Bearer tokens (rather than mTLS client certificates), we will need:

1. A registered OAuth client in RWT (client_id + client_secret, stored in the secrets vault)
1. Token acquisition logic before each test session (POST to RWT PRD’s /token endpoint)
1. Token caching and refresh logic (tokens expire — typically after 1 hour)
1. Correct audience configuration (the SUT’s audience claim must match what IDV expects)
1. IDV must be reachable from the SUT’s network segment

The key design principle: if the SUT uses IDV for token validation, IDV must be able to reach the same LDAP servers that hold our service account’s group memberships. Failure to resolve our groups in LDAP means IDV will reject our token.

-----

In **Episode 5**, we open the ministry’s filing cabinet. LDAP directories — the authoritative source of identity records, group memberships, and authentication credentials — are the foundation everything else stands on.

-----

**🔗 Resources**

- **JWT validation best practices**: [datatracker.ietf.org/doc/html/rfc8725](https://datatracker.ietf.org/doc/html/rfc8725)
- **OAuth 2.0 Token Introspection RFC 7662**: [rfc-editor.org/rfc/rfc7662](https://www.rfc-editor.org/rfc/rfc7662)
- **LDAP authentication and authorisation**: [rfc-editor.org/rfc/rfc4511](https://www.rfc-editor.org/rfc/rfc4511)

-----

*🌍 Globetrotters Identity and Access Management Series — crossing the IAM border one checkpoint at a time.*
