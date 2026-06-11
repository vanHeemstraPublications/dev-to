---
title: "What May You OAuth2? 🔬 Ep.1"
published: false
description: "Episode 1: *ba-ba-baaaa, ba-ba-baaaaa* — Who are you? Not quite. What MAY you? That is the OAuth2 question. Not identity — authorization. Not who — what you are PERMITTED to do. A token arrives at an API. The API asks not ‘who sent this?’ but ‘what does this token allow?’ Scopes, claims, expiry, audience. The crime lab opens its doors."
tags: [oauth2, security, authorization, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-may-you-oauth2-episode-01.png"
series: "What May You OAuth2?"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: The Opening Credits

*🎵 ba-ba-baaaa, ba-ba-baaaaa… Who are you? Who who, who who? 🎵*

*Wait.*

*Still not quite right.*

*The LDAP series asked: what are you?*

*This series asks something even more specific.*

*🎵 What may you? What what, what what? 🎵*

-----

## The Question That Protects Everything 🚨

*Las Vegas. 11:52pm. An API receives a request. The Authorization header contains a Bearer token — a long string of Base64-encoded data. The request claims to delete a user account.*

*Gil Grissom steps into the server room. He looks at the logs.*

**GRISSOM:** “The LDAP team asked ‘what are you?’ and received a dossier — objectClass, attributes, membership. A classification. An identity profile. That is authentication.”

*He picks up the decoded JWT payload.*

**GRISSOM:** “OAuth2 asks something different. Not who the caller is. Not what type of thing they are. OAuth2 asks: *what may you?* What are you **permitted** to do? On which resource? For how long? On whose behalf? Within what scope?”

*He reads the `scope` claim.*

```json
{
  "sub": "user_42",
  "iss": "https://auth.acme.com",
  "aud": "https://api.acme.com",
  "exp": 1749643200,
  "iat": 1749639600,
  "scope": "read:profile"
}
```

**GRISSOM:** “The token claims `read:profile`. The request is `DELETE /users/42`. Scope mismatch. The action is not permitted — regardless of who the token belongs to. The question ‘what may you?’ has a clear answer: not this.”

*He marks the case file: UNAUTHORIZED.*

**GRISSOM:** “Authorization is not authentication. Authentication confirms identity. Authorization grants permission. OAuth2 is a permission protocol. Every token is a warrant. Every scope is what the warrant covers. Every claim is evidence. Let us begin.”

-----

## 🗂️ SIPOC — The Authorization Framework

|**Suppliers**        |**Inputs**                                              |**Process**                                                                    |**Outputs**                                                       |**Customers**                                                                |
|---------------------|--------------------------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------------|
|Resource Owner (user)|Consent decision: “yes, this app may read my profile”   |Authorization Server records consent, issues authorization code                |A time-limited, scope-bounded authorization grant                 |The Client application — which can now act on behalf of the user             |
|Authorization Server |Client credentials, authorization code, requested scopes|Exchange code for tokens: validate code → check scopes → issue Access Token    |A signed, time-limited Access Token (and optionally Refresh Token)|The Client — which presents the Access Token to the Resource Server          |
|Client application   |Access Token in `Authorization: Bearer` header          |Resource Server validates the token: signature, claims, scope, expiry          |A decision: permit or deny the specific requested operation       |The user — whose protected resource is either accessed correctly or protected|
|Resource Server      |The Access Token                                        |Extract → verify signature (JWKS) → validate claims → check scope → permit/deny|The requested API response (200 OK) or rejection (401/403)        |The consuming application — which performs the authorized operation          |

-----

## The Four Roles: The Crime Scene Cast 👥

Every OAuth2 flow involves four roles. Understanding who is who is the first step in reading any authorization crime scene:

```
┌────────────────────────────────────────────────────────────────────┐
│                    OAUTH2 CRIME SCENE LAYOUT                       │
│                                                                    │
│  Resource Owner                   Authorization Server             │
│  (Alice — the user)               (The Crime Lab)                  │
│  Owns the data.                   Issues warrants (tokens).        │
│  Grants or denies                 Validates identity.              │
│  permission.                      Records consent.                 │
│                                                                    │
│  Client                           Resource Server                  │
│  (The Application)                (The Protected API)              │
│  Wants access to                  Holds the protected              │
│  Alice's data.                    resources. Accepts               │
│  Presents the token.              valid tokens only.               │
└────────────────────────────────────────────────────────────────────┘
```

|Role                         |Real-world example                   |In our story                               |
|-----------------------------|-------------------------------------|-------------------------------------------|
|**Resource Owner**           |Alice — the user logging in          |The person who owns the data               |
|**Client**                   |A mobile app, SPA, or backend service|The application requesting access          |
|**Authorization Server (AS)**|Keycloak, Auth0, Okta, Azure Entra ID|The crime lab — issues and validates tokens|
|**Resource Server (RS)**     |Your API backend                     |The protected evidence room                |

-----

## The Complete OAuth2/CSI Metaphor Table 🔬

|CSI / criminal investigation        |OAuth2 concept                                                   |
|------------------------------------|-----------------------------------------------------------------|
|*“What may you?”* — the series theme|OAuth2 answers: what are you ALLOWED to do?                      |
|The crime scene                     |An unauthorized API call, a stolen token, a scope violation      |
|The victim                          |The protected Resource Server / API                              |
|The suspect                         |The Client application or the bearer token                       |
|The perpetrator                     |A stolen token, a misconfigured scope, a missing `aud` check     |
|The crime lab                       |The Authorization Server (Keycloak, Auth0, Okta…)                |
|The warrant (badge)                 |The Access Token — “I have permission to do X”                   |
|What the warrant covers             |The Scope — `read:data`, `write:users`, `admin`                  |
|The warrant’s validity period       |The `exp` (expiry) claim                                         |
|The issuing authority               |The `iss` (issuer) claim                                         |
|Who the warrant is issued to        |The `aud` (audience) claim — which API this is for               |
|Subject of the investigation        |The `sub` (subject) claim — whose data this covers               |
|The case number                     |The `jti` (JWT ID) — unique per-token, prevents replay           |
|Issue date                          |The `iat` (issued at) claim                                      |
|Valid from date                     |The `nbf` (not before) claim                                     |
|The warrant application             |The Authorization Code flow — user consents, code issued         |
|The front desk                      |The `/authorize` endpoint — first stop for the user              |
|The evidence room                   |The `/token` endpoint — exchange code for tokens                 |
|Running the suspect’s prints        |Token introspection `/introspect` — is this token still valid?   |
|Cancelling a warrant                |Token revocation `/revoke` — invalidate before expiry            |
|The jury of keys                    |JWKS endpoint — public keys to verify JWT signatures             |
|Fingerprint on the warrant          |JWT digital signature — cryptographic proof of authenticity      |
|Fingerprint database                |JWKS — all valid signing keys                                    |
|Warrant forgery                     |JWT `alg:none` attack — signature stripped                       |
|Wrong precinct’s warrant            |Wrong `aud` claim — token issued for API-A used at API-B         |
|Anti-tamper seal on code envelope   |PKCE `code_challenge` — only original requester can exchange     |
|The stakeout                        |Authorization code flow — waiting for the redirect callback      |
|The undercover agent                |Client Credentials grant — machine-to-machine, no user           |
|The informant                       |Refresh Token — long-lived, gets new access tokens               |
|Crime lab report                    |`/userinfo` endpoint — the user’s attribute dossier              |
|Chain of custody                    |Token Exchange (RFC 8693) — delegated token issuance             |
|Officer carrying proof of ID        |Client certificate in mTLS (sender-constrained tokens)           |
|The sting operation                 |DPoP (Demonstrating Proof of Possession) — theft-resistant tokens|
|The known-dangerous gang            |Implicit grant — deprecated, the pattern we do not use anymore   |

-----

## Authentication vs Authorization: The Critical Distinction 🆚

**SARA:** “This is the most common confusion in identity security. Let me draw it clearly.”

```
AUTHENTICATION answers:       AUTHORIZATION answers:
"Who are you?"                "What may you do?"
"Are you who you claim to be?" "Are you allowed to do this?"

Handled by:                   Handled by:
  Passwords, LDAP, SAML,        OAuth2 scopes, ACLs,
  certificates, biometrics,     RBAC roles, claims,
  MFA                           policy engines

Result:                       Result:
  An identity assertion         A permission grant
  "You are Alice"               "Alice may read:profile"

Examples:                     Examples:
  Login page                    Access Token scope
  LDAP bind (Episode series 2)  JWT claims in bearer token
  OpenID Connect ID Token        Resource Server scope check
```

**SARA:** “OpenID Connect (OIDC) extends OAuth2 to add authentication as a layer *on top of* authorization. An ID Token tells you WHO authenticated. An Access Token tells you WHAT they may do. They are different tokens, different purposes, different validation rules.”

-----

## The Grant Types: Six Ways to Apply for a Warrant 📋

OAuth2 defines multiple “grant types” — different ways a client can obtain an access token. Each is suited to a different scenario:

|Grant Type                   |Status                   |Use Case                                    |The CSI Analogy                                         |
|-----------------------------|-------------------------|--------------------------------------------|--------------------------------------------------------|
|**Authorization Code**       |✅ Current best practice  |Web apps, SPAs (with PKCE), mobile          |The full warrant application — user present, code issued|
|**Authorization Code + PKCE**|✅ Mandatory in OAuth 2.1 |Public clients, all code flows              |Tamper-evident warrant envelope                         |
|**Client Credentials**       |✅ Current                |Machine-to-machine, no user                 |Undercover agent — operates without a witness           |
|**Device Authorization**     |✅ Current                |TV apps, CLI tools, IoT                     |Phoning the precinct from a device with no browser      |
|**Token Exchange**           |✅ RFC 8693               |Service-to-service delegation               |Chain of custody — passing the warrant down the chain   |
|**Refresh Token**            |✅ Current                |Renew access tokens silently                |The informant contact — long-term relationship          |
|**Implicit**                 |⛔ Deprecated in OAuth 2.1|Was for SPAs — replaced by Code+PKCE        |The dangerous informant who talks too loudly            |
|**ROPC (Password)**          |⛔ Deprecated in OAuth 2.1|Was for trusted apps — replaced by Code flow|Asking the witness to share their identity card         |

-----

## The Token Hierarchy: A Taxonomy of Warrants 🗂️

OAuth2 uses multiple token types, each with a specific purpose:

```
Authorization Code ← short-lived (seconds), single-use
  "I have the precinct's permission to exchange this for a warrant"

Access Token ← short-lived (minutes to hours), bearer credential
  "I am permitted to: [scopes] on [audience] until [exp]"
  The warrant. Present to the API. API checks validity.

Refresh Token ← longer-lived (days to weeks), confidential
  "I may request a new Access Token without the user re-authenticating"
  The informant contact. Never present to APIs. Only to the AS.

ID Token (OIDC) ← short-lived, contains identity claims
  "The AS confirms this user authenticated as: [sub, name, email...]"
  The identity certificate. Not an authorization token.
```

-----

## What a Scope Actually Is: The Warrant’s Coverage 🎯

A **scope** is a string label that represents a permission boundary. The client requests scopes. The user consents. The AS issues a token with the approved scopes. The RS checks the token’s scope before permitting an operation.

```
Client requests:  scope=read:profile write:posts openid
User consents to: read:profile openid          (user refuses write:posts)
AS issues token with: scope="read:profile openid"
RS enforces:      GET /profile → ALLOWED (read:profile present)
                  POST /posts  → FORBIDDEN (write:posts absent)
                  DELETE /post → FORBIDDEN (write:posts absent)
```

Scope design decisions:

```
Too coarse:  scope=api             ← everything or nothing
Too fine:    scope=read:user:42:email  ← unmaintainable
Just right:  scope=read:users write:users admin:billing
```

**NICK:** “The scope is what the warrant covers. A warrant to search the kitchen does not permit you to search the bedroom. A token with `read:profile` does not permit `write:data`. The Resource Server is the judge — it checks the warrant before granting access.”

-----

## The Series: Eight Cases for “What May You?” 📚

|#|Episode                         |The Case                |What We Investigate                                      |
|-|--------------------------------|------------------------|---------------------------------------------------------|
|1|*This one* — The Opening Credits|Introduction            |OAuth2 philosophy, roles, grant types, scope             |
|2|The Authorization Code          |Getting the Warrant     |Auth code flow, PKCE, state, redirect_uri                |
|3|The Evidence Room               |Tokens and their anatomy|JWT structure, every claim, opaque vs JWT                |
|4|The Crime Lab                   |The Authorization Server|AS configuration, JWKS, OIDC discovery, Keycloak         |
|5|Running the Prints              |Token validation        |RS validation pipeline, introspection, library code      |
|6|Cold Cases                      |Security threats        |Token theft, CSRF, alg:none, aud bypass, open redirect   |
|7|Undercover Operations           |Advanced flows          |Client Credentials, DPoP, mTLS, PAR, Token Exchange      |
|8|Case Closed                     |Production hardening    |OAuth 2.1 checklist, BCP, monitoring, complete deployment|

**GRISSOM:** “OAuth2 is not a product. It is a protocol — a set of rules for how to ask permission and how to grant it. The crime is always the same: something acted that was not permitted, or something was prevented that should have been allowed. The evidence is always in the token.”

*He closes the case file.*

*A Bearer token is waiting at the API gateway.*

*The investigation begins.*

-----

**🔗 Resources**

- **RFC 6749 — OAuth 2.0**: [rfc-editor.org/rfc/rfc6749](https://www.rfc-editor.org/rfc/rfc6749)
- **OAuth 2.0 Security Best Current Practice (RFC 9700)**: [rfc-editor.org/rfc/rfc9700](https://www.rfc-editor.org/rfc/rfc9700)
- **OAuth 2.1 (draft)**: [oauth.net/2.1](https://oauth.net/2.1/)
- **OpenID Connect 1.0**: [openid.net/connect](https://openid.net/connect/)

-----

*🔬 What May You OAuth2? — a CSI-style investigation into authorization. The evidence is in the token. The verdict is in the scope.*
