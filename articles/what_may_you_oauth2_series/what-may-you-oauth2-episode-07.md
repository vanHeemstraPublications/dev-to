---
title: "What May You OAuth2? 🔬 Ep.7"
published: false
description: "Episode 7: Not every authorization involves a user. Machine-to-machine services operate without witnesses. TV apps phone the precinct from devices that have no keyboard. Service chains pass warrants down the chain of custody. Tokens bound to cryptographic keys resist theft. Pushed authorization requests seal the evidence before the redirect. The undercover operations of OAuth2 — advanced flows for complex environments."
tags: [oauth2, security, advanced, dpop]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-may-you-oauth2-episode-07.png"
series: "What May You OAuth2?"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

## Episode 7: Undercover Operations

*🎵 What may you? What what, what what? 🎵*

-----

## “Some Operations Have No Witnesses” 🕵️

*The briefing room. Grissom at the whiteboard. The roster of grant types on the board.*

**GRISSOM:** “Authorization Code is the standard flow. User present. Consent given. Redirect happens. But there are entire classes of authorization that have no user at all. A microservice authenticating to another microservice at 3am. A data pipeline running without any human in the loop. A television that cannot open a browser.”

*He circles Client Credentials on the board.*

**GRISSOM:** “These are the undercover operations. No witness. No consent screen. No redirect. Just a service account with a client_id and client_secret — or a private key — proving identity to the Authorization Server and receiving a token in return.”

*He pauses.*

**GRISSOM:** “And then there are the operations that are about trust, not just identity. Token Exchange: I have a token, I need a different token for a downstream service. DPoP: I want my token to be unusable if stolen. PAR: I want to seal the authorization request before the redirect even happens. These are the advanced cases. Let us examine each one.”

-----

## 🗂️ SIPOC — The Undercover Operations

|**Suppliers**                       |**Inputs**                                              |**Process**                                                             |**Outputs**                                                             |**Customers**                                                    |
|------------------------------------|--------------------------------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------------|-----------------------------------------------------------------|
|Service (Client Credentials)        |`client_id`, `client_secret` or private key             |POST to /token with `grant_type=client_credentials`                     |An access token with machine-identity scope (no user `sub`)             |The calling service — which uses the token to call other services|
|Device with no browser (Device Auth)|`device_code` from AS                                   |User completes auth on separate device; service polls until complete    |An access token once the user approves on another device                |CLI tools, smart TVs, IoT devices — any input-constrained device |
|DPoP-bound client                   |A DPoP proof JWT (short-lived, signed with client key)  |RS validates DPoP proof: checks `htm`, `htu`, `iat`, token binding `ath`|Token usage is bound to the holder of the private key — theft is useless|High-security APIs — cannot be replayed by a token thief         |
|PAR client                          |Authorization parameters (client_id, scopes, PKCE, etc.)|POST all params to AS directly before redirect; get `request_uri`       |A short-lived `request_uri` used instead of query params in the redirect|Applications where query parameter exposure is a security concern|

-----

## Operation 1: Client Credentials — The Undercover Agent 🤖

Machine-to-machine authorization. No user. No consent screen. The client is both the actor and the identity.

```python
import httpx

def get_machine_token(
    token_endpoint: str,
    client_id: str,
    client_secret: str,
    scopes: list[str],
) -> str:
    """
    Client Credentials grant — machine-to-machine token acquisition.
    No user, no redirect, no consent.
    """
    response = httpx.post(
        token_endpoint,
        data={
            "grant_type": "client_credentials",
            "scope": " ".join(scopes),
        },
        auth=(client_id, client_secret),  # HTTP Basic Auth
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5.0,
    )
    response.raise_for_status()
    return response.json()["access_token"]


# Usage: a data pipeline calling an internal reporting API
access_token = get_machine_token(
    token_endpoint="https://auth.acme.com/oauth/token",
    client_id="data-pipeline-service",
    client_secret="pipeline-secret-from-vault",
    scopes=["read:internal-data", "write:reports"],
)
# The returned token's "sub" is "data-pipeline-service" (the client_id)
# There is no user sub — this is a service identity
```

**Client Credentials token claims:**

```json
{
  "sub":       "data-pipeline-service",
  "iss":       "https://auth.acme.com",
  "aud":       "https://reports.acme.com",
  "exp":       1749643200,
  "iat":       1749639600,
  "scope":     "read:internal-data write:reports",
  "client_id": "data-pipeline-service",
  "grant_type": "client_credentials"
}
```

**Using private_key_jwt instead of client_secret:**

```python
import jwt as pyjwt
import time
import uuid
from cryptography.hazmat.primitives.serialization import load_pem_private_key

def get_machine_token_pkjwt(
    token_endpoint: str,
    client_id: str,
    private_key_pem: bytes,
    key_id: str,
    scopes: list[str],
) -> str:
    """
    Client Credentials with private_key_jwt authentication.
    More secure than client_secret — key never leaves the service.
    """
    private_key = load_pem_private_key(private_key_pem, password=None)
    now = int(time.time())

    # Build the client assertion JWT
    client_assertion = pyjwt.encode(
        {
            "iss": client_id,
            "sub": client_id,
            "aud": token_endpoint,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + 60,  # Short-lived — 60 seconds
        },
        private_key,
        algorithm="RS256",
        headers={"kid": key_id},
    )

    response = httpx.post(
        token_endpoint,
        data={
            "grant_type": "client_credentials",
            "scope": " ".join(scopes),
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": client_assertion,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    return response.json()["access_token"]
```

-----

## Operation 2: Device Authorization Flow — Phoning the Precinct 📱

For devices that cannot open a browser: smart TVs, CLI tools, IoT devices. The device shows a code; the user authenticates on their phone or computer.

```python
import httpx
import time

def device_authorization_flow(
    device_endpoint: str,
    token_endpoint: str,
    client_id: str,
    scopes: list[str],
) -> dict:
    """
    Device Authorization Grant (RFC 8628).
    Shows a code to the user; polls until authenticated.
    """

    # Step 1: Request device code
    device_response = httpx.post(
        device_endpoint,
        data={
            "client_id": client_id,
            "scope": " ".join(scopes),
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    device_response.raise_for_status()
    device_data = device_response.json()

    # Step 2: Display instructions to the user
    print(f"\nTo authenticate:")
    print(f"  1. Visit: {device_data['verification_uri']}")
    print(f"  2. Enter code: {device_data['user_code']}")
    print(f"\nOr go directly to: {device_data.get('verification_uri_complete')}")
    print(f"\nWaiting for authentication (expires in {device_data['expires_in']}s)...")

    # Step 3: Poll until user authenticates or code expires
    interval   = device_data.get("interval", 5)
    expires_in = device_data["expires_in"]
    started_at = time.time()

    while time.time() - started_at < expires_in:
        time.sleep(interval)

        poll_response = httpx.post(
            token_endpoint,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_data["device_code"],
                "client_id": client_id,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        poll_data = poll_response.json()

        if poll_response.status_code == 200:
            print("\nAuthenticated!")
            return poll_data  # Contains access_token, refresh_token

        error = poll_data.get("error")
        if error == "authorization_pending":
            continue  # Keep waiting
        elif error == "slow_down":
            interval += 5  # Back off
            continue
        elif error == "access_denied":
            raise Exception("User denied the request")
        elif error == "expired_token":
            raise Exception("Device code expired — restart the flow")
        else:
            raise Exception(f"Unexpected error: {error}")

    raise Exception("Device code expired")


# Usage in a CLI tool:
tokens = device_authorization_flow(
    device_endpoint="https://auth.acme.com/oauth/device/authorize",
    token_endpoint="https://auth.acme.com/oauth/token",
    client_id="acme-cli",
    scopes=["openid", "read:data", "write:data"],
)
print(f"Access token expires in: {tokens['expires_in']}s")
```

-----

## Operation 3: Refresh Token — The Long-Term Informant 🔄

Refresh tokens allow the client to obtain new access tokens without requiring the user to re-authenticate:

```python
def refresh_access_token(
    token_endpoint: str,
    refresh_token: str,
    client_id: str,
    client_secret: str,
    scopes: list[str] | None = None,
) -> dict:
    """
    Exchange a refresh token for a new access token.
    The AS should rotate the refresh token (issue a new one).
    """
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    if scopes:
        data["scope"] = " ".join(scopes)

    response = httpx.post(
        token_endpoint,
        data=data,
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 400:
        error = response.json().get("error")
        if error == "invalid_grant":
            raise TokenExpiredError("Refresh token is invalid, expired, or revoked")
        raise OAuth2Error(response.json())

    response.raise_for_status()
    new_tokens = response.json()

    # IMPORTANT: The AS issues a new refresh token on each use (rotation)
    # Store the NEW refresh_token — the old one is now invalid
    return new_tokens  # Contains new access_token + new refresh_token


# Proactive token refresh — refresh before expiry
def get_valid_token(tokens: dict) -> str:
    """Returns a valid access token, refreshing if needed."""
    import jwt, time
    try:
        claims = jwt.decode(
            tokens["access_token"],
            options={"verify_signature": False}
        )
        # Refresh 60 seconds before expiry
        if claims["exp"] - time.time() < 60:
            new_tokens = refresh_access_token(...)
            tokens.update(new_tokens)
    except Exception:
        new_tokens = refresh_access_token(...)
        tokens.update(new_tokens)

    return tokens["access_token"]
```

-----

## Operation 4: Token Revocation — Cancelling the Warrant 🚫

```python
def revoke_token(
    revocation_endpoint: str,
    token: str,
    token_type_hint: str,  # "access_token" or "refresh_token"
    client_id: str,
    client_secret: str,
) -> None:
    """
    Revoke a token (RFC 7009).
    The AS invalidates the token immediately.
    """
    response = httpx.post(
        revocation_endpoint,
        data={
            "token": token,
            "token_type_hint": token_type_hint,
        },
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    # RFC 7009: always returns 200 even if token was not found
    response.raise_for_status()
    # Token is now revoked — discard locally too
```

-----

## Operation 5: DPoP — The Sting Operation 🎯

**DPoP (Demonstrating Proof of Possession, RFC 9449)** binds a token to a specific cryptographic key pair. Even if the token is stolen, it cannot be used without the corresponding private key.

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat, NoEncryption, PrivateFormat
)
import jwt, uuid, time, hashlib, base64

# Generate a DPoP key pair (per-session, not stored long-term)
private_key = ec.generate_private_key(ec.SECP256R1())
public_key  = private_key.public_key()

# Serialize the public key to JWK format
public_numbers = public_key.public_numbers()
dpop_public_jwk = {
    "kty": "EC",
    "crv": "P-256",
    "x": base64.urlsafe_b64encode(
        public_numbers.x.to_bytes(32, "big")
    ).rstrip(b"=").decode(),
    "y": base64.urlsafe_b64encode(
        public_numbers.y.to_bytes(32, "big")
    ).rstrip(b"=").decode(),
}

def make_dpop_proof(
    http_method: str,
    http_uri: str,
    access_token: str | None = None,
) -> str:
    """
    Create a DPoP proof JWT for a specific HTTP request.
    Must be created fresh for EACH request (jti is unique, iat is now).
    """
    header = {
        "typ": "dpop+jwt",
        "alg": "ES256",
        "jwk": dpop_public_jwk,  # Public key embedded in header
    }

    claims = {
        "jti": str(uuid.uuid4()),    # Unique per request
        "htm": http_method,          # HTTP method: "GET", "POST"...
        "htu": http_uri,             # Target URI
        "iat": int(time.time()),     # Issued at (AS validates freshness)
    }

    if access_token:
        # Bind the proof to a specific access token
        # ath = BASE64URL(SHA256(access_token))
        token_hash = hashlib.sha256(access_token.encode()).digest()
        claims["ath"] = base64.urlsafe_b64encode(token_hash).rstrip(b"=").decode()

    return jwt.encode(claims, private_key, algorithm="ES256",
                      headers={"typ": "dpop+jwt", "jwk": dpop_public_jwk})


# Step 1: Request a DPoP-bound token
dpop_proof_for_token = make_dpop_proof("POST", "https://auth.acme.com/oauth/token")

token_response = httpx.post(
    "https://auth.acme.com/oauth/token",
    data={
        "grant_type": "authorization_code",
        "code": authorization_code,
        "code_verifier": code_verifier,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
    },
    headers={
        "DPoP": dpop_proof_for_token,    # ← DPoP proof header
        "Content-Type": "application/x-www-form-urlencoded",
    },
)
dpop_access_token = token_response.json()["access_token"]

# Step 2: Use the DPoP-bound token in an API call
# A new DPoP proof is required for EACH API request
dpop_proof_for_api = make_dpop_proof(
    "GET",
    "https://api.acme.com/profile",
    access_token=dpop_access_token,
)

api_response = httpx.get(
    "https://api.acme.com/profile",
    headers={
        "Authorization": f"DPoP {dpop_access_token}",  # Note: "DPoP" not "Bearer"
        "DPoP": dpop_proof_for_api,
    },
)
```

-----

## Operation 6: PAR — Pushed Authorization Requests 🔐

PAR (RFC 9126) allows clients to POST the authorization request directly to the AS before the redirect, receiving a `request_uri` to use instead of query parameters.

```python
def pushed_authorization_request(
    par_endpoint: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: list[str],
    code_challenge: str,
    state: str,
) -> str:
    """
    Push the authorization request to the AS.
    Returns a request_uri to use in the redirect.
    """
    response = httpx.post(
        par_endpoint,
        data={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        },
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    data = response.json()
    return data["request_uri"]  # e.g. "urn:ietf:params:oauth:request_uri:xyz"


# Then redirect the user using request_uri instead of all the parameters
request_uri = pushed_authorization_request(...)

redirect_url = (
    f"https://auth.acme.com/oauth/authorize"
    f"?client_id={client_id}"
    f"&request_uri={urllib.parse.quote(request_uri)}"
)
# The authorization parameters never appear in the URL/browser history
return redirect(redirect_url)
```

-----

## Operation 7: Token Exchange — Chain of Custody (RFC 8693) 🔗

Service A has a token. Service A calls Service B. Service B should get a token scoped to Service B’s resources, on behalf of the original user — not Service A’s token directly.

```python
def exchange_token(
    token_endpoint: str,
    subject_token: str,              # The incoming token (from Service A)
    client_id: str,
    client_secret: str,
    requested_scopes: list[str],
    actor_token: str | None = None,  # Service A's own identity token
) -> str:
    """
    RFC 8693 Token Exchange — obtain a token for a downstream service.
    """
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": subject_token,
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "scope": " ".join(requested_scopes),
    }
    if actor_token:
        data["actor_token"] = actor_token
        data["actor_token_type"] = "urn:ietf:params:oauth:token-type:access_token"

    response = httpx.post(
        token_endpoint,
        data=data,
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    return response.json()["access_token"]


# Service B calls the AS to exchange Service A's token
# for a token scoped to Service B's downstream API
downstream_token = exchange_token(
    token_endpoint="https://auth.acme.com/oauth/token",
    subject_token=request.headers["Authorization"][7:],  # Incoming token
    client_id="service-b",
    client_secret="service-b-secret",
    requested_scopes=["read:downstream-data"],
)
# downstream_token is now scoped to service-b and the specific downstream API
# The original user's identity is preserved in the "sub" claim
# The delegation chain is recorded in the "act" claim
```

-----

## What’s Next: Case Closed 🏁

*Grissom stands at the full investigation board. Every operation. Every attack. Every flow.*

**GRISSOM:** “We have covered every grant type. Every token format. Every attack vector. Every advanced flow. Episode 8 is the final chapter: production hardening. OAuth 2.1 compliance checklist. The security BCP. Token lifetime strategy. Audience isolation architecture. Monitoring. The complete production OAuth2 deployment. Case closed.”

-----

**🔗 Resources**

- **RFC 8628 — Device Authorization**: [rfc-editor.org/rfc/rfc8628](https://www.rfc-editor.org/rfc/rfc8628)
- **RFC 9449 — DPoP**: [rfc-editor.org/rfc/rfc9449](https://www.rfc-editor.org/rfc/rfc9449)
- **RFC 9126 — PAR**: [rfc-editor.org/rfc/rfc9126](https://www.rfc-editor.org/rfc/rfc9126)
- **RFC 8693 — Token Exchange**: [rfc-editor.org/rfc/rfc8693](https://www.rfc-editor.org/rfc/rfc8693)

-----

*🔬 What May You OAuth2? — a CSI-style investigation into authorization. The evidence is in the token. The verdict is in the scope.*
