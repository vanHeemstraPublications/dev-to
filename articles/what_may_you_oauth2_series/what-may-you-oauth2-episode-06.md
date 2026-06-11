---
title: "What May You OAuth2? 🔬 Ep.6"
published: false
description: "Episode 6: Some authorization crimes are subtle. The alg:none attack strips the signature entirely. The audience bypass replays a valid token at the wrong API. The open redirect leaks codes to attacker-controlled servers. Token theft turns any bearer into an impersonator. The implicit grant broadcasts tokens in browser history. Every attack, every detection, every countermeasure — the OAuth2 cold case files."
tags: [oauth2, security, attacks, vulnerabilities]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-may-you-oauth2-episode-06.png"
series: "What May You OAuth2?"
canonical_url: ""
organization: "the-software-s-journey"
part: 6
---

## Episode 6: Cold Cases

*🎵 What may you? What what, what what? 🎵*

-----

## “These Cases Were Never Solved” 🧊

*A stack of folders drops on Nick Stokes’s desk. COLD CASE stamps across each one.*

**NICK:** “OAuth2 attack vectors. Some of these have been known for years. Some are still being found in production systems every quarter. Every one of them exploits a missing check, a missing parameter, a missing validation step.”

*He opens the first file.*

**NICK:** “Let us go through them all. Because the crime is only committed once. The prevention is forever.”

-----

## 🗂️ SIPOC — The Cold Case Investigation

|**Suppliers**       |**Inputs**                                            |**Process**                                                                           |**Outputs**                                                    |**Customers**                                                  |
|--------------------|------------------------------------------------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------|---------------------------------------------------------------|
|The attacker        |A vulnerability in the OAuth2 implementation          |Exploit: forge token / steal token / intercept code / bypass check                    |Unauthorized access to the Resource Server                     |The victim — whose data is accessed or modified without consent|
|The detection system|Security logs, anomalous patterns, validation failures|Correlate: unexpected `aud`, missing `state`, abnormal `kid`, rapid token reuse       |An alert: this authorization pattern is suspicious             |The security team — which can investigate and remediate        |
|The countermeasures |Implementation best practices                         |Apply: check `alg` whitelist, validate `aud`, require `state`, use PKCE, rotate tokens|An implementation that is resistant to the known attack vectors|All API users — whose authorization system cannot be subverted |

-----

## Cold Case #1: The `alg:none` Attack — The Forged Warrant 🎭

**The crime:** The JWT specification originally allowed `"alg": "none"` — a token with no signature. An attacker can take any JWT, change its payload (e.g., escalate `scope` or change `sub`), set `alg` to `none`, and strip the signature section. Vulnerable libraries accepted this.

```python
# The attack — constructing a forged "none" token
import base64, json

def forge_none_token(original_token: str, new_claims: dict) -> str:
    """
    Demonstrate the alg:none attack.
    (FOR EDUCATION ONLY — to understand what to block)
    """
    header = {"alg": "none", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).rstrip(b"=").decode()

    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(new_claims).encode()
    ).rstrip(b"=").decode()

    # No signature — just a trailing dot
    return f"{header_b64}.{payload_b64}."

# The forged token has sub="admin", scope="admin", but no valid signature
forged = forge_none_token("", {
    "sub": "admin",
    "scope": "admin",
    "iss": "https://auth.acme.com",
    "aud": "https://api.acme.com",
    "exp": 9999999999
})
```

**Detection:** The token has no third section (or an empty one). The `alg` claim is `none`.

**Prevention:**

```python
# In your JWT validation — ALWAYS whitelist algorithms
# NEVER include "none", "HS256" (unless you're an AS sharing the secret)

jwt.decode(
    token,
    signing_key,
    algorithms=["RS256", "ES256", "PS256"],  # Explicit whitelist
    # DO NOT use algorithms=jwt.algorithms.get_algorithms()
    # DO NOT use algorithms=["RS256", "none"]
)

# Explicit pre-check before even trying to verify:
header = jwt.get_unverified_header(token)
ALLOWED_ALGORITHMS = {"RS256", "RS384", "RS512", "ES256", "ES384", "PS256"}
if header.get("alg") not in ALLOWED_ALGORITHMS:
    raise SecurityError(f"Rejected algorithm: {header.get('alg')}")
```

-----

## Cold Case #2: Bearer Token Theft — The Stolen Warrant 🥷

**The crime:** OAuth2 access tokens are **bearer tokens** — whoever holds the token can use it. If Alice’s token is stolen (via XSS, logging, TLS interception, insecure storage), the attacker can impersonate Alice until the token expires.

```
Attack vectors for token theft:
  1. XSS: script reads sessionStorage/localStorage, exfiltrates token
  2. Log injection: access_token appears in server logs
  3. Referrer leakage: token in URL → appears in Referer header to third parties
  4. Insecure storage: token stored in cookie without HttpOnly/Secure flags
  5. Man-in-the-middle: TLS misconfiguration allows interception
  6. Token leakage in URL: ?access_token=... in query string
```

**Detection:** Impossible to detect directly — the thief has a valid token.

**Prevention:**

```python
# 1. NEVER put tokens in URLs
# BAD:
redirect_url = f"https://app.acme.com/dashboard?access_token={token}"
# GOOD:
# Use POST/fragment for SPA, or server-side session for web apps

# 2. Store tokens in server-side sessions, not localStorage
# Flask example — server-side session only
session["access_token"] = tokens["access_token"]  # HttpOnly cookie
# Never: localStorage.setItem("token", access_token)

# 3. Short token lifetimes reduce the theft window
# access_token lifetime: 15 minutes for sensitive operations
# refresh_token: rotate on each use

# 4. Bind tokens to the client using DPoP (Episode 7)
# A stolen DPoP-bound token cannot be used without the private key

# 5. Use Sender-Constrained Tokens (mTLS) for high-security scenarios
```

-----

## Cold Case #3: The Audience Bypass — The Wrong Precinct’s Warrant 🏛️

**The crime:** An attacker obtains a valid token for API-A (perhaps their own account). They then replay it against API-B. If API-B does not validate the `aud` claim, it accepts the token — even though it was never issued for API-B.

```python
# Attack scenario:
# Attacker has a valid token for api-a.acme.com with scope="read:data"
# They try the same token at api-b.acme.com
# api-b.acme.com forgets to check "aud"

# VULNERABLE api-b code (missing aud validation):
claims = jwt.decode(
    token,
    signing_key,
    algorithms=["RS256"],
    # MISSING: audience="https://api-b.acme.com"
    # MISSING: options={"verify_aud": True}
)
# This accepts the api-a.acme.com token at api-b.acme.com! Vulnerability!

# SECURE api-b code:
claims = jwt.decode(
    token,
    signing_key,
    algorithms=["RS256"],
    audience="https://api-b.acme.com",   # REQUIRED
    options={"verify_aud": True},         # Explicit
)
# Now the api-a token is rejected: InvalidAudienceError
```

**Design requirement: Every Resource Server must have a unique audience identifier.**

```
api-a.acme.com → audience: "https://api-a.acme.com"
api-b.acme.com → audience: "https://api-b.acme.com"
reports.acme.com → audience: "https://reports.acme.com"

Token for api-a ONLY works at api-a.
Token for api-b ONLY works at api-b.
```

-----

## Cold Case #4: CSRF via Missing State — The Precinct Swap 🔀

**The crime:** Without the `state` parameter, an attacker can force a victim’s browser to complete an authorization flow that the attacker controls. The victim’s account gets connected to the attacker’s identity.

```
Attack sequence (without state):
  1. Attacker initiates an OAuth2 flow → gets authorization_code=ATTACKER_CODE
  2. Attacker stops before the callback
  3. Attacker constructs: https://app.acme.com/callback?code=ATTACKER_CODE
  4. Attacker tricks Alice into clicking this URL (email, malicious site)
  5. App receives callback, exchanges ATTACKER_CODE
  6. App is now linked to Attacker's account
  7. When Attacker logs into the app, they see Alice's session (or vice versa)
```

**Prevention:**

```python
# Generate state before redirect (Episode 2 covered this in detail)
import secrets

state = secrets.token_urlsafe(32)
session["oauth_state"] = state

# In callback — ALWAYS check state FIRST
def callback():
    if not secrets.compare_digest(
        request.args.get("state", ""),
        session.pop("oauth_state", "")
    ):
        abort(400, "State mismatch — CSRF protection triggered")
    # Only then process the code
```

-----

## Cold Case #5: Open Redirect Attack — Misdirecting the Code Delivery 📮

**The crime:** If the client has a badly configured `redirect_uri` (e.g., a wildcard, a partial match, or an open redirect on the client’s own domain), an attacker can intercept the authorization code.

```
Vulnerable registration:
  Registered redirect_uri: https://app.acme.com/callback
  
  Attacker crafts:
  https://auth.acme.com/authorize?
    client_id=legitimate-app&
    redirect_uri=https://app.acme.com/callback?next=https://evil.com

  If app.acme.com/callback has an open redirect:
  → code arrives at app.acme.com/callback
  → app.acme.com redirects to https://evil.com?code=AUTH_CODE
  → evil.com captures the authorization code
```

**Prevention:**

```python
# 1. Register EXACT redirect URIs (no wildcards, no open-ended paths)
# BAD: redirect_uri="https://app.acme.com/callback*"
# BAD: redirect_uri="https://app.acme.com/"  (too broad)
# GOOD: redirect_uri="https://app.acme.com/oauth/callback"

# 2. AS must perform exact string comparison, not prefix/suffix match
# If registered: "https://app.acme.com/callback"
# Received: "https://app.acme.com/callback?injected=param"
# → REJECT (not exact match)

# 3. PKCE prevents code theft even if redirect_uri is compromised
# Even if the attacker gets the code, they cannot exchange it
# because they don't have the code_verifier
```

-----

## Cold Case #6: Authorization Code Injection — The Forged Handoff 💉

**The crime:** An attacker intercepts or steals an authorization code from one victim and injects it into another victim’s authorization flow. Without PKCE, the code is usable by anyone who has it.

**Why PKCE solves this:**

```
Without PKCE:
  1. Victim A starts auth flow → gets code=VICTIM_CODE
  2. Attacker intercepts VICTIM_CODE
  3. Attacker injects code into Victim B's callback URL
  4. Victim B's app exchanges VICTIM_CODE for tokens
  5. Victim B's app is now logged in as Victim A

With PKCE:
  1. Victim B starts their own flow with code_challenge=HASH(B_VERIFIER)
  2. Attacker injects VICTIM_CODE into Victim B's callback URL
  3. Victim B's app sends: code=VICTIM_CODE + code_verifier=B_VERIFIER
  4. AS checks: SHA256(B_VERIFIER) == VICTIM_CODE's stored challenge?
     → NO (B_VERIFIER corresponds to B's challenge, not Victim A's)
  5. Token exchange REJECTED
```

-----

## Cold Case #7: The Implicit Grant — The Loud Informant 📢

**The crime:** The implicit grant (now deprecated in OAuth 2.1) returns the access token directly in the URL fragment after the redirect:

```
https://app.acme.com/callback#access_token=VERY_SECRET_TOKEN&...
                              ↑
                    The token is IN THE URL
```

**Why this is dangerous:**

```
1. Browser history: the URL (with token) is stored in browser history
2. Server logs: if the JS app makes ANY request with this URL as Referer,
   the token appears in server access logs
3. Shared browsers: another user on the same machine can see the history
4. No refresh tokens: implicit grant never issues refresh tokens
5. No client authentication: no way to verify which client got the token
6. Token binding: nothing ties the token to a specific session
```

**The fix:** Use Authorization Code + PKCE instead. This is why OAuth 2.1 explicitly removes the implicit grant.

```python
# DO NOT use:
params = {"response_type": "token", ...}  # Implicit grant — DEPRECATED

# USE INSTEAD:
params = {"response_type": "code", "code_challenge": ..., ...}  # Code + PKCE
```

-----

## Cold Case #8: Mix-Up Attack — Impersonating the Authorization Server 🎭

**The crime:** When a client is registered with multiple Authorization Servers (common in multi-tenant setups), an attacker can manipulate the client into sending credentials to the wrong AS, or redirect the response from the wrong AS to their own callback.

```
Attack:
  1. Client is registered at AS1 and AS2
  2. User initiates flow against AS1
  3. Attacker intercepts the redirect and serves a response claiming to be AS1
     but with a code from AS2
  4. Client exchanges the code at AS1 (because it's still in the AS1 flow)
  5. Token issued by AS1 but with identity from AS2
```

**Prevention:**

```python
# 1. Store which AS the current flow is with, and check the response matches
session["oauth_flow"] = {
    "state": state,
    "as_issuer": "https://auth.acme.com",   # ← which AS we're talking to
    "redirect_uri": redirect_uri,
}

# In callback — verify the issuer if the AS returns it
# OIDC does this via the `iss` response parameter:
# https://app.acme.com/callback?code=...&state=...&iss=https://auth.acme.com

def callback():
    expected_issuer = session["oauth_flow"]["as_issuer"]
    received_issuer = request.args.get("iss")

    if received_issuer and received_issuer != expected_issuer:
        abort(400, "Issuer mismatch — possible mix-up attack")

# 2. Use issuer-specific client registrations (separate client_id per AS)
# 3. Validate iss in the exchanged ID token
```

-----

## Cold Case #9: Token Scope Escalation — The Expanded Warrant 📜

**The crime:** A client requests a token with a limited scope but somehow ends up with a token with broader permissions than requested.

```python
# What should happen:
# Client requests: scope=read:profile
# AS issues token with: scope="read:profile"  (exactly what was requested)
# RS enforces: DELETE /users → FORBIDDEN (scope too narrow)

# What a vulnerable AS might do (BUG):
# Client requests: scope=read:profile
# AS ignores the requested scope, issues: scope="read:profile write:data admin"
# RS accepts this token — scope is present

# Prevention on the AS side:
# - Always restrict issued scope to INTERSECTION of:
#   (a) scopes the client is registered for
#   (b) scopes the user consented to
#   (c) scopes the client requested in this flow
# - Log when a client requests scopes it is not registered for

# Prevention on the RS side:
# - Validate scope with minimum required principle
# - Reject tokens with unnecessary scopes for sensitive operations
```

-----

## The Cold Case Countermeasure Summary 📋

|Attack          |Root cause                 |Countermeasure                               |
|----------------|---------------------------|---------------------------------------------|
|`alg:none`      |No algorithm whitelist     |Explicit `algorithms=["RS256", "ES256"]`     |
|Token theft     |Bearer token = possession  |Short lifetimes + DPoP/mTLS binding          |
|Audience bypass |Missing `aud` check        |Always validate `aud` in RS                  |
|CSRF            |Missing `state`            |Generate and verify `state` in every flow    |
|Open redirect   |Loose `redirect_uri`       |Exact string match, never wildcards          |
|Code injection  |No PKCE                    |Require PKCE for all code flows (OAuth 2.1)  |
|Implicit grant  |Tokens in URL fragment     |Never use implicit grant; use Code+PKCE      |
|Mix-up attack   |No issuer tracking         |Validate `iss` response parameter            |
|Scope escalation|Overly-broad token issuance|Scope intersection at AS, minimum scope at RS|

-----

## What’s Next: Undercover Operations 🕵️

*Grissom closes the last cold case file.*

**GRISSOM:** “The threats are catalogued. The countermeasures are in place. Now the advanced operations. Machine-to-machine flows with no user. TV apps with no browser. Service-to-service token delegation. Tokens bound to cryptographic proofs. Pushed authorization requests. Episode 7 — the undercover operations.”

-----

**🔗 Resources**

- **RFC 9700 — OAuth 2.0 Security BCP**: [rfc-editor.org/rfc/rfc9700](https://www.rfc-editor.org/rfc/rfc9700)
- **OWASP OAuth Cheat Sheet**: [cheatsheetseries.owasp.org/cheatsheets/OAuth_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/OAuth_Cheat_Sheet.html)
- **Mix-Up Attacks RFC**: [rfc-editor.org/rfc/rfc9700#section-4.4](https://www.rfc-editor.org/rfc/rfc9700#section-4.4)

-----

*🔬 What May You OAuth2? — a CSI-style investigation into authorization. The evidence is in the token. The verdict is in the scope.*
