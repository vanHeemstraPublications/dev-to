---
title: "What May You OAuth2? 🔬 Ep.2"
published: false
description: "Episode 2: The authorization code flow is the warrant application process — a carefully choreographed five-step dance between the user, the client, the authorization server, and the resource server. PKCE seals the code envelope so only the original requester can open it. The state parameter is the CSRF guard. And every step has a specific failure mode. The investigation begins at the /authorize endpoint."
tags: [oauth2, security, authorization, pkce]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-may-you-oauth2-episode-02.png"
series: "What May You OAuth2?"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 2: The Authorization Code

*🎵 What may you? What what, what what? 🎵*

-----

## “Apply for the Warrant First” 📋

*Catherine Willows spreads a flow diagram across the analysis table. Five boxes connected by arrows. Each arrow is labelled with an HTTP request.*

**CATHERINE:** “The most important OAuth2 grant type. The authorization code flow. Every web application, every single-page app, every mobile app that needs to act on behalf of a user — this is the process they follow.”

*She points to the first arrow.*

**CATHERINE:** “It begins with the user. The user must be present. The user must consent. You do not get a warrant without showing cause to a judge. In OAuth2, the user is the judge. And they must approve every scope the client requests — before any token is issued.”

-----

## 🗂️ SIPOC — The Warrant Application Process

|**Suppliers**        |**Inputs**                                                   |**Process**                                                                    |**Outputs**                                                                         |**Customers**                                                         |
|---------------------|-------------------------------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------|----------------------------------------------------------------------|
|Resource Owner (user)|Browser, willingness to consent                              |AS presents consent screen; user approves or denies requested scopes           |An authorization code (short-lived, single-use, bound to client and redirect_uri)   |The Client — which receives the code via redirect callback            |
|Client application   |Authorization code, PKCE verifier, client credentials        |POST to `/token`: exchange code for tokens, prove PKCE ownership               |An Access Token (+ Refresh Token if `offline_access` requested)                     |The Client — which uses Access Token to call the Resource Server      |
|Authorization Server |All of the above                                             |Validate code (unused? expired? correct client?), validate PKCE, issue tokens  |Signed, scoped, time-bounded Access Token and optional Refresh Token                |Resource Server — which validates the token before serving the request|
|PKCE mechanism       |`code_verifier` (random), `code_challenge` (hash of verifier)|`code_challenge` sent at authorization time; `code_verifier` sent at token time|Cryptographic proof that the entity exchanging the code is the one that requested it|All public clients — prevents code injection attacks                  |

-----

## The Five-Step Dance: Anatomy of the Flow 💃

```
Step 1: Client → Authorization Server
  Browser redirect to /authorize with:
  - response_type=code
  - client_id=my-app
  - redirect_uri=https://app.acme.com/callback
  - scope=read:profile openid
  - state=CSRF-guard-value
  - code_challenge=PKCE-hash
  - code_challenge_method=S256

Step 2: User → Authorization Server
  User authenticates (password, MFA, SSO...)
  User reviews consent screen
  User clicks "Allow"

Step 3: Authorization Server → Client (via redirect)
  Browser redirects to redirect_uri with:
  - code=authorization-code-abc123
  - state=same-CSRF-guard-value

Step 4: Client → Authorization Server (back-channel)
  POST /token with:
  - grant_type=authorization_code
  - code=authorization-code-abc123
  - redirect_uri=https://app.acme.com/callback
  - client_id=my-app
  - client_secret=my-secret   (confidential clients)
  - code_verifier=PKCE-secret  (all clients)

Step 5: Authorization Server → Client
  JSON response:
  {
    "access_token": "eyJhbGciOiJSUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "rt-opaque-string",
    "scope": "read:profile openid",
    "id_token": "eyJhbGciOiJSUzI1NiJ9..."
  }
```

-----

## Step 1 in Detail: Building the Authorization URL 🔗

```python
import secrets
import hashlib
import base64
import urllib.parse

def build_authorization_url(
    as_authorize_endpoint: str,
    client_id: str,
    redirect_uri: str,
    scopes: list[str],
) -> tuple[str, str, str]:
    """
    Build an OAuth2 authorization URL with PKCE and state.
    Returns (url, state, code_verifier) — store state and verifier in session.
    """

    # ── CSRF protection: the state parameter ─────────────────────
    # Random value, stored in session, checked when code returns
    state = secrets.token_urlsafe(32)

    # ── PKCE: Proof Key for Code Exchange ────────────────────────
    # code_verifier: a high-entropy random string (43-128 chars)
    code_verifier = secrets.token_urlsafe(64)

    # code_challenge: BASE64URL(SHA256(code_verifier))
    # This is what we send with the authorization request
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    # ── Build the URL ────────────────────────────────────────────
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    url = f"{as_authorize_endpoint}?{urllib.parse.urlencode(params)}"

    return url, state, code_verifier


# Usage in a Flask route:
# url, state, verifier = build_authorization_url(
#     as_authorize_endpoint="https://auth.acme.com/authorize",
#     client_id="my-webapp",
#     redirect_uri="https://app.acme.com/callback",
#     scopes=["openid", "profile", "read:data"]
# )
# session["oauth_state"] = state
# session["pkce_verifier"] = verifier
# return redirect(url)
```

The resulting URL:

```
https://auth.acme.com/authorize
  ?response_type=code
  &client_id=my-webapp
  &redirect_uri=https%3A%2F%2Fapp.acme.com%2Fcallback
  &scope=openid+profile+read%3Adata
  &state=mN3kL9pQ7rT2xV4wY8bA5jF1hD6nG0cE
  &code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
  &code_challenge_method=S256
```

-----

## PKCE Deep Dive: The Tamper-Evident Envelope 🔐

**WARRICK:** “PKCE — Proof Key for Code Exchange, RFC 7636. Originally designed for mobile apps that cannot safely store a client secret. Now mandatory for ALL authorization code flows in OAuth 2.1.”

**The problem PKCE solves:**

```
Without PKCE:
  1. Legitimate app requests code
  2. Code arrives at redirect_uri
  3. Attacker intercepts code (via browser history, log files, referrer header)
  4. Attacker POSTs code to /token with THEIR app's credentials
  5. Attacker gets the access token

With PKCE:
  1. Legitimate app generates code_verifier (secret random string)
  2. App computes code_challenge = SHA256(verifier)
  3. App sends code_challenge in /authorize request
  4. AS stores code_challenge with the authorization code
  5. Code arrives at redirect_uri
  6. [Attacker intercepts code — but does NOT have the verifier]
  7. Legitimate app POSTs code + code_verifier to /token
  8. AS confirms: SHA256(verifier) == stored code_challenge? YES → issue tokens
  9. Attacker POSTs code + no verifier / wrong verifier → REJECTED
```

```python
# PKCE mathematics — the full picture
import secrets
import hashlib
import base64

# Step 1: Generate the verifier (high-entropy random)
# MUST be 43-128 characters, URL-safe characters only
code_verifier = secrets.token_urlsafe(64)
# Example: "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"

# Step 2: Compute the challenge
# S256 method: code_challenge = BASE64URL(SHA256(ASCII(code_verifier)))
digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
# Example: "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"

# Step 3: Send challenge (not verifier) to /authorize
# Store verifier in server-side session (never expose in browser)

# Step 4: At callback, retrieve verifier from session and send to /token
# The AS recomputes: SHA256(verifier) == stored_challenge?
```

-----

## The State Parameter: The CSRF Guard 🛡️

**The problem without state:**

```
1. Attacker crafts an authorization URL with THEIR authorization code
   https://app.acme.com/callback?code=ATTACKER_CODE&state=ignored

2. Attacker tricks Alice into visiting this URL (CSRF)

3. App sees the callback, exchanges ATTACKER_CODE for tokens
   → App is now connected to Attacker's account, not Alice's
   → Attacker can now access their own data via Alice's session
```

**The fix:**

```python
import secrets

# Before redirect: generate and store state
state = secrets.token_urlsafe(32)
session["oauth_state"] = state  # Server-side session only

# Include state in authorization URL
params["state"] = state

# In callback: ALWAYS verify state before proceeding
def handle_callback(request):
    received_state = request.args.get("state")
    stored_state = session.pop("oauth_state", None)

    if not stored_state or not secrets.compare_digest(received_state, stored_state):
        # State mismatch — abort the flow immediately
        raise SecurityError("OAuth state mismatch — possible CSRF attack")

    # Only now proceed to exchange the code
    code = request.args.get("code")
    # ...
```

-----

## Step 4 in Detail: The Token Exchange 🔄

```python
import httpx
import time

def exchange_code_for_tokens(
    token_endpoint: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    code_verifier: str,
    client_secret: str | None = None,  # None for public clients
) -> dict:
    """
    Exchange an authorization code for tokens.
    Raises an exception if the exchange fails.
    """

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,  # PKCE proof
    }

    # Confidential clients authenticate with client_secret
    # (use HTTP Basic Auth — most secure form)
    auth = None
    if client_secret:
        auth = (client_id, client_secret)
        # Basic auth sends credentials as Authorization: Basic base64(id:secret)
        # Do NOT put client_secret in the POST body (less secure)

    response = httpx.post(
        token_endpoint,
        data=data,
        auth=auth,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10.0,
    )

    if response.status_code != 200:
        error_data = response.json()
        raise OAuth2Error(
            f"{error_data.get('error')}: {error_data.get('error_description')}"
        )

    tokens = response.json()

    # Validate that we got what we expected
    if "access_token" not in tokens:
        raise OAuth2Error("Token response missing access_token")

    return tokens
```

**Error responses from the token endpoint:**

|`error`                 |Meaning                               |Likely cause                         |
|------------------------|--------------------------------------|-------------------------------------|
|`invalid_request`       |Malformed request                     |Missing parameter, wrong content-type|
|`invalid_client`        |Client authentication failed          |Wrong client_secret                  |
|`invalid_grant`         |Code invalid, expired, or used twice  |Code replay, wrong redirect_uri      |
|`unauthorized_client`   |This client cannot use this grant type|Client not registered for auth code  |
|`unsupported_grant_type`|AS doesn’t support this grant         |Wrong grant_type value               |
|`invalid_scope`         |Requested scope not allowed           |Scope not registered for client      |

-----

## The redirect_uri: The Delivery Address 📬

**NICK:** “The `redirect_uri` is the delivery address for the authorization code. If the AS sends the code to the wrong address — an address controlled by an attacker — the attacker gets the code.”

**Security requirements:**

```python
# What the AS MUST enforce:

# 1. redirect_uri must EXACTLY match a pre-registered URI
# "https://app.acme.com/callback" ≠ "https://app.acme.com/callback?extra=param"
# "https://app.acme.com/callback" ≠ "https://evil.com/callback"

# 2. The same redirect_uri used in /authorize must be provided in /token
# This binds the code to the original request

# 3. Never accept localhost with open ports in production
# (fine for development, dangerous in production)

# 4. Never accept wildcards: https://*.acme.com/callback is dangerous
# An attacker who owns "evil.acme.com" can intercept the code

# BAD: redirect_uri registered as https://app.acme.com/
# (too broad — any path on the host would match)

# GOOD: redirect_uri registered as https://app.acme.com/oauth/callback
# (exact match, specific path)
```

-----

## The Complete Callback Handler 🎯

```python
from flask import Flask, request, redirect, session
import httpx
import secrets

app = Flask(__name__)

# OAuth2 configuration
AS_BASE = "https://auth.acme.com"
CLIENT_ID = "my-webapp"
CLIENT_SECRET = "super-secret"  # From secure config, not code
REDIRECT_URI = "https://app.acme.com/oauth/callback"
TOKEN_ENDPOINT = f"{AS_BASE}/oauth/token"
AUTHORIZE_ENDPOINT = f"{AS_BASE}/oauth/authorize"

@app.route("/login")
def login():
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)

    import hashlib, base64
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    session["oauth_state"] = state
    session["pkce_verifier"] = code_verifier

    import urllib.parse
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile read:data",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    })

    return redirect(f"{AUTHORIZE_ENDPOINT}?{params}")


@app.route("/oauth/callback")
def oauth_callback():
    # ── Security check 1: Error in response ─────────────────────
    if "error" in request.args:
        error = request.args["error"]
        desc  = request.args.get("error_description", "No description")
        return f"Authorization failed: {error} — {desc}", 400

    # ── Security check 2: State validation (CSRF guard) ─────────
    received_state = request.args.get("state")
    stored_state   = session.pop("oauth_state", None)
    if not stored_state or not secrets.compare_digest(
        received_state or "", stored_state
    ):
        return "State mismatch — possible CSRF", 400

    # ── Security check 3: Code present ──────────────────────────
    code = request.args.get("code")
    if not code:
        return "No authorization code in callback", 400

    # ── Token exchange ───────────────────────────────────────────
    code_verifier = session.pop("pkce_verifier", None)
    if not code_verifier:
        return "PKCE verifier missing from session", 400

    token_response = httpx.post(
        TOKEN_ENDPOINT,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "code_verifier": code_verifier,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if token_response.status_code != 200:
        return f"Token exchange failed: {token_response.text}", 400

    tokens = token_response.json()
    # Store tokens securely (server-side session, encrypted cookie, etc.)
    session["access_token"] = tokens["access_token"]
    session["refresh_token"] = tokens.get("refresh_token")

    return redirect("/dashboard")
```

-----

## What’s Next: The Evidence Room 🗄️

*Sara Sidle holds up a JWT string.*

**SARA:** “We have the token. A long string of Base64 characters. Three sections separated by dots. The client holds it. The Resource Server will receive it. And somewhere in this string is the answer to ‘what may you?’ — the scope, the audience, the expiry, the subject.”

**SARA:** “Episode 3: the evidence room. We decode the token. We examine every claim. We understand what the JWT header, payload, and signature actually mean — and why each one matters for authorization security.”

-----

**🔗 Resources**

- **RFC 6749 Section 4.1 — Authorization Code Grant**: [rfc-editor.org/rfc/rfc6749#section-4.1](https://www.rfc-editor.org/rfc/rfc6749#section-4.1)
- **RFC 7636 — PKCE**: [rfc-editor.org/rfc/rfc7636](https://www.rfc-editor.org/rfc/rfc7636)
- **OAuth 2.0 Security BCP (state parameter)**: [rfc-editor.org/rfc/rfc9700](https://www.rfc-editor.org/rfc/rfc9700)

-----

*🔬 What May You OAuth2? — a CSI-style investigation into authorization. The evidence is in the token. The verdict is in the scope.*
