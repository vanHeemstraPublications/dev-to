---
title: "What May You OAuth2? 🔬 Ep.3"
published: false
description: "Episode 3: The token arrives. Three sections, separated by dots, each Base64URL encoded. The header declares the algorithm. The payload holds every claim — sub, iss, aud, exp, iat, nbf, jti, scope. The signature is the cryptographic fingerprint. Open the evidence room. Every claim answers a different dimension of ‘what may you?’"
tags: [oauth2, jwt, tokens, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-may-you-oauth2-episode-03.png"
series: "What May You OAuth2?"
canonical_url: ""
organization: "the-software-s-journey"
part: 3
---

## Episode 3: The Evidence Room

*🎵 What may you? What what, what what? 🎵*

-----

## “Open the Evidence Bag” 🗄️

*Sara Sidle holds a JWT up to the light. A long string of characters. Three sections separated by dots.*

```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtleS0xIn0.
eyJzdWIiOiJ1c2VyXzQyIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmFjbWUuY29tIiwiYXVkIjoiaHR0cHM6Ly9hcGkuYWNtZS5jb20iLCJleHAiOjE3NDk2NDMyMDAsImlhdCI6MTc0OTYzOTYwMCwianRpIjoiYWJjZGVmMTIzNDU2Iiwic2NvcGUiOiJyZWFkOnByb2ZpbGUgcmVhZDpkYXRhIn0.
SIGNATURE_BYTES_HERE
```

**SARA:** “Three sections. Three stories. The header tells you how it was signed. The payload tells you who, what, for whom, and until when. The signature is the cryptographic proof that neither section was tampered with.”

*She opens the evidence bag.*

**SARA:** “Let us examine every piece.”

-----

## 🗂️ SIPOC — The Token Examination

|**Suppliers**       |**Inputs**                                                      |**Process**                                                                    |**Outputs**                                                                         |**Customers**                                                           |
|--------------------|----------------------------------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------|------------------------------------------------------------------------|
|Authorization Server|Authenticated user session, approved scopes, client registration|Sign the JWT: build header + payload → sign with private key → Base64URL encode|A signed JWT containing claims answering every dimension of “what may you?”         |The Client — which presents it; the Resource Server — which validates it|
|Resource Server     |The JWT from the Authorization header                           |Validate: decode header → fetch JWKS → verify signature → check each claim     |A binary decision: allow the requested operation (200) or deny (401/403)            |The user/client — which either gets the response or receives an error   |
|JWT claims          |`sub`, `iss`, `aud`, `exp`, `iat`, `nbf`, `jti`, `scope`, custom|Each claim answers a specific authorization question (see below)               |A complete authorization context: who? allowed what? for which resource? until when?|Policy engines, access control logic, audit systems                     |

-----

## JWT Structure: The Three-Part Evidence File 📋

```
[HEADER].[PAYLOAD].[SIGNATURE]
    │          │          │
    │          │          └── Cryptographic proof: header+payload
    │          │               signed with AS private key
    │          └────────────── The claims: authorization context
    └───────────────────────── Algorithm and key metadata
```

Each section is **Base64URL encoded** (not encrypted — anyone can decode the header and payload).

-----

## Section 1: The Header — Algorithm Declaration 📌

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-1"
}
```

|Field|Value  |Meaning                                               |
|-----|-------|------------------------------------------------------|
|`alg`|`RS256`|RSA + SHA-256 — asymmetric, public key verifiable     |
|`typ`|`JWT`  |Token type                                            |
|`kid`|`key-1`|Key ID — which key in the JWKS to use for verification|

**Algorithm types:**

|Algorithm|Type             |Key used to verify    |Recommended                         |
|---------|-----------------|----------------------|------------------------------------|
|`RS256`  |RSA + SHA-256    |Public key (from JWKS)|✅ Yes                               |
|`RS384`  |RSA + SHA-384    |Public key            |✅ Yes                               |
|`ES256`  |ECDSA + P-256    |Public key            |✅ Yes (smaller, faster)             |
|`PS256`  |RSA-PSS + SHA-256|Public key            |✅ Yes                               |
|`HS256`  |HMAC + SHA-256   |Shared secret         |⚠️ Only if AS and RS share the secret|
|`none`   |No signature     |—                     |🚫 **NEVER ACCEPT** (attack vector)  |

**SARA:** “The `kid` field is the key indicator. The Resource Server fetches the JWKS (the public key set) from the AS and finds the key matching this kid. That key verifies the signature. If the kid does not exist in the JWKS, the token is invalid. If the signature does not verify with that key, the token is forged or tampered.”

-----

## Section 2: The Payload — The Claims Dossier 📁

```json
{
  "sub":   "user_42",
  "iss":   "https://auth.acme.com",
  "aud":   "https://api.acme.com",
  "exp":   1749643200,
  "iat":   1749639600,
  "nbf":   1749639600,
  "jti":   "abcdef123456",
  "scope": "read:profile read:data",
  "client_id": "my-webapp",
  "name":  "Alice Smith",
  "email": "alice@acme.com",
  "roles": ["engineer", "viewer"]
}
```

### The Core Claims — Every Dimension of “What May You?”

**`sub` — Subject: WHO does this token represent?**

```json
"sub": "user_42"
```

The unique identifier of the entity the token represents. For user tokens: the user’s stable ID (not their username — usernames change). For machine tokens (Client Credentials): typically the `client_id`.

-----

**`iss` — Issuer: WHO issued this warrant?**

```json
"iss": "https://auth.acme.com"
```

The URL of the Authorization Server that issued this token. Must exactly match the `issuer` value in the AS’s OIDC discovery document. The RS must verify this — a token from a different AS must be rejected.

-----

**`aud` — Audience: WHICH resource is this warrant for?**

```json
"aud": "https://api.acme.com"
```

The intended recipient(s) of this token. If the RS’s own identifier is not in `aud`, the token is not for this RS — it must be rejected. This is critical: a token issued for `api-a.acme.com` must not be accepted by `api-b.acme.com`.

Can be a string or an array of strings:

```json
"aud": ["https://api.acme.com", "https://reports.acme.com"]
```

**GRISSOM:** “The audience claim is the most commonly missed validation check. An attacker who steals a valid token for API-A can try to replay it against API-B. If API-B does not check `aud`, it accepts the stolen token. The audience check is the warrant checking that it is addressed to the right precinct.”

-----

**`exp` — Expiration: WHEN does the warrant expire?**

```json
"exp": 1749643200
```

Unix timestamp (seconds since epoch). The token must be rejected after this time. Allows a small clock skew tolerance (typically 30-60 seconds) for distributed systems.

```python
import time

def is_token_expired(exp_claim: int, leeway_seconds: int = 60) -> bool:
    return time.time() > (exp_claim + leeway_seconds)
    # Note: leeway is for the clock skew tolerance (servers disagree on exact time)
    # Do not use large leeway values — they reduce security
```

-----

**`iat` — Issued At: WHEN was the warrant stamped?**

```json
"iat": 1749639600
```

Unix timestamp when the token was issued. Used to detect abnormally old tokens and to calculate token age. `exp - iat` is the token lifetime.

-----

**`nbf` — Not Before: WHEN does the warrant become valid?**

```json
"nbf": 1749639600
```

The token must not be accepted before this time. Usually equals `iat`. Used for pre-issued tokens that should only become valid in the future.

-----

**`jti` — JWT ID: The unique case number**

```json
"jti": "abcdef123456"
```

A unique identifier for this specific token. Used to prevent replay attacks — store used `jti` values and reject tokens with previously seen `jti`. Only necessary for high-security scenarios (most RSes do not implement jti tracking due to the storage requirement).

-----

**`scope` — The Permission Declaration: WHAT is permitted?**

```json
"scope": "read:profile read:data"
```

A space-separated string of granted scopes. The RS must check that the required scope for the requested operation is present.

```python
def check_scope(token_claims: dict, required_scope: str) -> bool:
    granted_scopes = set(token_claims.get("scope", "").split())
    return required_scope in granted_scopes

# OR for multiple required scopes (all must be present):
def check_all_scopes(token_claims: dict, required_scopes: list[str]) -> bool:
    granted_scopes = set(token_claims.get("scope", "").split())
    return all(s in granted_scopes for s in required_scopes)
```

-----

### Custom Claims — The Extended Profile

Beyond the standard claims, the AS can include any application-specific claims:

```json
{
  "sub":   "user_42",
  "scope": "read:data",
  "roles": ["engineer", "admin"],
  "department": "Engineering",
  "tenant_id": "tenant-acme",
  "clearance_level": "elevated",
  "acr": "urn:mfa:duo",           // Authentication Context Reference
  "amr": ["pwd", "otp"],          // Authentication Methods Reference
  "azp": "my-webapp"              // Authorized party (client_id that got this token)
}
```

**CATHERINE:** “Custom claims answer the question ‘what may you?’ beyond just scopes. Roles answer ‘what role does this token represent?’ Department answers ‘what organisational context?’ Clearance level answers ‘what privilege level has this user established?’ Every custom claim is a dimension of authorisation that the Resource Server can use in its policy decisions.”

-----

## Section 3: The Signature — The Cryptographic Fingerprint 🔏

The signature is computed over the encoded header and payload:

```
SIGNATURE = RSA_SHA256(
    PRIVATE_KEY,
    BASE64URL(header) + "." + BASE64URL(payload)
)
```

To verify:

```
1. Re-encode header and payload as BASE64URL(header).BASE64URL(payload)
2. Fetch the public key from JWKS matching the "kid" in the header
3. Verify: RSA_VERIFY(PUBLIC_KEY, encoded_header_payload, SIGNATURE)
4. If verification passes: the token was signed by the holder of the private key
5. If verification fails: REJECT IMMEDIATELY — the token is forged or tampered
```

-----

## Opaque vs JWT Tokens: Two Evidence Formats 📄

OAuth2 does not mandate JWT. The AS can issue opaque (reference) tokens instead:

|Characteristic  |JWT (structured)                     |Opaque (reference)                 |
|----------------|-------------------------------------|-----------------------------------|
|Format          |`eyJ...` — self-contained            |`abc123xyz` — random string        |
|Validation      |Local: verify signature + claims     |Remote: call `/introspect`         |
|Revocation      |Difficult (token is valid until exp) |Immediate (delete from AS database)|
|Information     |All claims embedded — self-describing|No information — must introspect   |
|Network calls   |Zero for validation                  |One per request (unless cached)    |
|Token theft risk|Contains data that may be sensitive  |Opaque — attacker sees nothing     |

```python
def detect_token_format(token: str) -> str:
    """Determine if a token is a JWT or opaque."""
    parts = token.split(".")
    if len(parts) == 3:
        try:
            import base64, json
            # Try to decode the header
            header_b64 = parts[0] + "=" * (4 - len(parts[0]) % 4)
            header = json.loads(base64.urlsafe_b64decode(header_b64))
            if "alg" in header:
                return "jwt"
        except Exception:
            pass
    return "opaque"
```

-----

## Decoding a JWT in Python 📦

```python
import base64
import json
import time
from typing import Any

def decode_jwt_payload_insecure(token: str) -> dict[str, Any]:
    """
    Decode JWT payload WITHOUT signature verification.
    USE ONLY for debugging. Never use this for authorization decisions.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Not a valid JWT (must have 3 parts)")

    # Base64URL decode — add padding if needed
    payload_b64 = parts[1]
    payload_b64 += "=" * (4 - len(payload_b64) % 4)
    payload_bytes = base64.urlsafe_b64decode(payload_b64)
    return json.loads(payload_bytes)


# Safe production decoding — uses PyJWT with full verification
import jwt  # pip install PyJWT[crypto]
import httpx

def decode_jwt_secure(
    token: str,
    expected_issuer: str,
    expected_audience: str,
    jwks_uri: str,
) -> dict[str, Any]:
    """
    Decode and VERIFY a JWT using JWKS.
    This is what Resource Servers must use.
    """
    # Fetch the JWKS (in production: cache this with TTL)
    jwks_response = httpx.get(jwks_uri, timeout=5.0)
    jwks = jwt.PyJWKClient(jwks_uri)

    # This automatically fetches JWKS and finds the right key by kid
    signing_key = jwks.get_signing_key_from_jwt(token)

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256", "PS256"],  # Never include "none" or "HS256" here!
        audience=expected_audience,
        issuer=expected_issuer,
        options={
            "require": ["exp", "iat", "sub", "iss", "aud"],
            "verify_exp": True,
            "verify_iss": True,
            "verify_aud": True,
            "leeway": 60,  # 60-second clock skew tolerance
        }
    )

    return claims
```

-----

## The ID Token vs Access Token: Two Different Warrants 🆚

OpenID Connect (OIDC) adds the **ID Token** — a second JWT with a different purpose:

```json
// Access Token — "What may you do?"
{
  "sub": "user_42",
  "iss": "https://auth.acme.com",
  "aud": "https://api.acme.com",      // ← the API
  "scope": "read:profile read:data",
  "exp": 1749643200
}

// ID Token — "Who authenticated?"
{
  "sub": "user_42",
  "iss": "https://auth.acme.com",
  "aud": "my-webapp",                 // ← the CLIENT (not the API!)
  "nonce": "random-replay-guard",
  "iat": 1749639600,
  "exp": 1749643200,
  "name": "Alice Smith",
  "email": "alice@acme.com",
  "email_verified": true,
  "amr": ["pwd", "otp"]
}
```

**SARA:** “The ID Token’s `aud` is the client ID — it is a statement from the AS to the client: ‘I authenticated this user.’ It is not a warrant for an API. Never send the ID Token to an API as a bearer token — it is not meant for that purpose and the API’s `aud` check will fail.”

-----

## What’s Next: The Crime Lab 🔬

*Nick Stokes holds up a Keycloak configuration screen.*

**NICK:** “We understand the token anatomy. Now: where do tokens come from? Episode 4 — the crime lab. The Authorization Server: how it is configured, how it exposes its public keys via JWKS, how the OIDC discovery document describes its capabilities, how clients are registered, how scopes and claims are designed. The lab that makes every warrant.”

-----

**🔗 Resources**

- **RFC 7519 — JSON Web Tokens**: [rfc-editor.org/rfc/rfc7519](https://www.rfc-editor.org/rfc/rfc7519)
- **RFC 9068 — JWT Profile for Access Tokens**: [rfc-editor.org/rfc/rfc9068](https://www.rfc-editor.org/rfc/rfc9068)
- **JWT.io (decode + verify)**: [jwt.io](https://jwt.io)
- **PyJWT library**: [pyjwt.readthedocs.io](https://pyjwt.readthedocs.io)

-----

*🔬 What May You OAuth2? — a CSI-style investigation into authorization. The evidence is in the token. The verdict is in the scope.*
