---
title: "What May You OAuth2? 🔬 Ep.8"
published: false
description: "Episode 8: The finale. Eight episodes of authorization investigation end here — a hardened, observable, production-ready OAuth2 deployment that answers every dimension of ‘what may you?’ correctly and securely. The OAuth 2.1 checklist. The Security BCP implementation. Token lifetime strategy. Audience isolation architecture. Monitoring and alerting. The complete production pattern. Case closed."
tags: [oauth2, security, production, authorization]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-may-you-oauth2-episode-08.png"
series: "What May You OAuth2?"
canonical_url: ""
organization: "the-software-s-journey"
part: 8
---

## Episode 8: Case Closed

*🎵 What may you? What what, what what? 🎵*

-----

## “Lock the Evidence Room — Permanently” 🔒

*The final briefing. All four investigators, the complete case board behind them. Every episode. Every attack. Every flow.*

**GRISSOM:** “We have investigated eight cases. The Authorization Code flow. JWT anatomy. The crime lab configuration. The validation pipeline. The cold case attacks. The undercover operations. In every case, the answer to ‘what may you?’ was determined by the token — its claims, its scopes, its audience, its expiry, its signature.”

*He turns to face the board.*

**GRISSOM:** “But knowing the answers is not enough. In production, a correct OAuth2 implementation must survive attack, scale under load, and remain auditable when something inevitably goes wrong. Episode 8 is not about features. It is about hardening. The checklist. The production pattern. And closing every case file we opened.”

-----

## 🗂️ SIPOC — The Production Hardening Operation

|**Suppliers**             |**Inputs**                                             |**Process**                                                                                      |**Outputs**                                                          |**Customers**                                                                       |
|--------------------------|-------------------------------------------------------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|------------------------------------------------------------------------------------|
|OAuth 2.1 compliance      |All grant types, security requirements                 |Audit: remove implicit, remove ROPC, add PKCE to all code flows, confirm redirect_uri exact match|An implementation that passes OAuth 2.1 conformance                  |Every client and RS — which interoperate with a compliant AS                        |
|Security BCP (RFC 9700)   |Known attack vectors and their mitigations             |Apply: state always, PKCE always, aud always, scope minimum, token rotation                      |An implementation resistant to the documented attack catalogue       |All authorization decisions — which cannot be subverted by known attacks            |
|Token lifecycle management|Access token and refresh token issuance                |Calibrate lifetimes: short access (15min), rotating refresh, revocation on logout                |A token lifecycle that minimises theft window and maximises usability|Users — who stay logged in appropriately; attackers — who have a narrow theft window|
|Monitoring and alerting   |Token validation failure logs, introspection call rates|Alert on: high validation failures, unexpected `aud` mismatches, abnormal token reuse            |Operational visibility into authorization behaviour                  |Security operations — which detect attacks in real time                             |

-----

## Part 1: The OAuth 2.1 Checklist ✅

OAuth 2.1 (currently a draft) consolidates the best practices that have emerged since RFC 6749 in 2012:

```
OAuth 2.1 Mandatory Requirements:

 [✓] PKCE required for ALL authorization code flows
     (no longer optional for confidential clients)

 [✓] Implicit grant REMOVED
     (use Authorization Code + PKCE instead)

 [✓] Resource Owner Password Credentials REMOVED
     (use Authorization Code flow instead)

 [✓] redirect_uri exact string match required
     (no prefix matching, no wildcards)

 [✓] Bearer tokens MUST NOT appear in URI query strings
     (use Authorization: Bearer header only)

 [✓] Refresh tokens MUST be sender-constrained
     OR rotated on every use
     (prevent refresh token theft)

 [✓] Authorization servers MUST support PKCE
     (clients may mandate S256)
```

**Audit your implementation:**

```python
def audit_oauth2_1_compliance(client_config: dict) -> list[str]:
    """
    Audit a client configuration for OAuth 2.1 compliance.
    Returns a list of violations.
    """
    violations = []

    # 1. PKCE must be configured
    if not client_config.get("pkce_required"):
        violations.append("PKCE not required — mandate code_challenge_method=S256")

    # 2. Implicit grant must be disabled
    if "implicit" in client_config.get("grant_types", []):
        violations.append("Implicit grant enabled — remove it")

    # 3. ROPC must be disabled
    if "password" in client_config.get("grant_types", []):
        violations.append("Resource Owner Password Credentials enabled — remove it")

    # 4. Redirect URIs must be exact
    for uri in client_config.get("redirect_uris", []):
        if "*" in uri or uri.endswith("/"):
            violations.append(f"Redirect URI not exact: {uri}")

    # 5. Refresh token rotation
    if not client_config.get("refresh_token_rotation"):
        violations.append("Refresh token rotation not enabled")

    return violations
```

-----

## Part 2: Token Lifetime Strategy — The Warrant Expiry Schedule ⏱️

```python
# Recommended token lifetimes by sensitivity

TOKEN_LIFETIMES = {
    # Access tokens — short-lived
    "access_token_standard":       3600,    # 1 hour for normal APIs
    "access_token_sensitive":       900,    # 15 minutes for payment/health
    "access_token_high_security":   300,    # 5 minutes for admin/audit

    # Authorization codes — very short
    "authorization_code":           300,    # 5 minutes — exchange immediately

    # Refresh tokens — longer, but rotate on use
    "refresh_token_web":          86400,    # 24 hours for web apps
    "refresh_token_mobile":     2592000,    # 30 days for mobile (inactive = revoke)
    "refresh_token_m2m":           None,    # No refresh for Client Credentials

    # ID tokens — match access token
    "id_token":                    3600,    # Same as access token
}

# Keycloak realm settings
KEYCLOAK_TOKEN_SETTINGS = {
    "accessTokenLifespan":           3600,
    "accessCodeLifespan":             300,
    "refreshTokenMaxReuse":             0,  # 0 = rotate on every use
    "revokeRefreshToken":            True,  # Revoke old refresh on rotation
    "ssoSessionMaxLifespan":        86400,
    "ssoSessionIdleTimeout":        86400,
    "offlineSessionMaxLifespan":  2592000,
}
```

-----

## Part 3: Audience Isolation Architecture 🏗️

Every Resource Server gets a unique audience identifier. Tokens are scoped to specific APIs.

```python
# Production audience isolation design
AUDIENCE_MAP = {
    "user-api":       "https://user.api.acme.com",
    "payment-api":    "https://payment.api.acme.com",
    "reporting-api":  "https://reporting.api.acme.com",
    "admin-api":      "https://admin.api.acme.com",
    "internal-api":   "https://internal.api.acme.com",
}

# Each RS validates ONLY its own audience
class UserAPIResourceServer:
    EXPECTED_AUDIENCE = "https://user.api.acme.com"
    validator = TokenValidator(OAuth2Config(
        issuer="https://auth.acme.com",
        audience=EXPECTED_AUDIENCE,
        jwks_uri="https://auth.acme.com/.well-known/jwks.json",
        algorithms=["RS256"],
    ))

class PaymentAPIResourceServer:
    EXPECTED_AUDIENCE = "https://payment.api.acme.com"
    validator = TokenValidator(OAuth2Config(
        issuer="https://auth.acme.com",
        audience=EXPECTED_AUDIENCE,  # Different from user-api
        jwks_uri="https://auth.acme.com/.well-known/jwks.json",
        algorithms=["RS256"],
    ))

# A token for user-api CANNOT be used at payment-api (aud mismatch)
# A token for payment-api CANNOT be used at reporting-api (aud mismatch)
# Complete audience isolation in the token validation layer
```

-----

## Part 4: Scope Minimisation — The Minimum Necessary Warrant 🎯

```python
# The principle of least privilege applied to OAuth2

# BAD: Request all scopes the client might ever need
GREEDY_SCOPES = ["read:users", "write:users", "read:data",
                  "write:data", "admin", "billing:read"]

# GOOD: Request only what is needed for this specific operation
def get_scopes_for_operation(operation: str) -> list[str]:
    """Return minimum scopes required for a specific operation."""
    scope_map = {
        "view_profile":    ["openid", "read:users"],
        "update_profile":  ["openid", "write:users"],
        "view_reports":    ["openid", "read:data"],
        "admin_panel":     ["openid", "admin"],
    }
    return scope_map.get(operation, ["openid"])

# Downscoping: get a token with reduced scope for a specific downstream call
def get_downscoped_token(
    token_endpoint: str,
    access_token: str,
    required_scope: str,
) -> str:
    """Get a narrower-scoped token for a specific operation."""
    # Using Token Exchange (RFC 8693) to downscope
    response = httpx.post(
        token_endpoint,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": access_token,
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "scope": required_scope,  # Narrower than the original
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    return response.json()["access_token"]
```

-----

## Part 5: The Complete Resource Server Pattern 🏛️

```python
# production_resource_server.py — Complete production RS middleware

from dataclasses import dataclass
from typing import Callable
import httpx
import jwt
import time
import logging
import prometheus_client as prom

logger = logging.getLogger("oauth2.rs")

# ── Prometheus metrics ────────────────────────────────────────────
TOKEN_VALIDATIONS = prom.Counter(
    "oauth2_token_validations_total",
    "Total token validation attempts",
    ["result", "error_type"]
)
TOKEN_VALIDATION_LATENCY = prom.Histogram(
    "oauth2_token_validation_duration_seconds",
    "Time spent validating tokens"
)
SCOPE_VIOLATIONS = prom.Counter(
    "oauth2_scope_violations_total",
    "Attempts with insufficient scope",
    ["required_scope"]
)

@prom.histogram_timer(TOKEN_VALIDATION_LATENCY)
def validate_token_with_metrics(token: str, config: OAuth2Config) -> dict:
    try:
        claims = TokenValidator(config).validate(token)
        TOKEN_VALIDATIONS.labels(result="success", error_type="").inc()
        return claims
    except TokenValidationError as e:
        TOKEN_VALIDATIONS.labels(result="failure", error_type=e.error).inc()
        raise


# ── Production middleware with logging ───────────────────────────
def require_auth_production(required_scope: str | None = None):
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()

            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                logger.warning(
                    "Missing Bearer token",
                    extra={"path": request.path, "method": request.method,
                           "remote_addr": request.remote_addr}
                )
                return make_bearer_error("invalid_request", "Missing Bearer token")

            token = auth_header[7:]

            try:
                claims = validate_token_with_metrics(token, VALIDATOR_CONFIG)

                if required_scope:
                    if required_scope not in set(claims.get("scope", "").split()):
                        SCOPE_VIOLATIONS.labels(required_scope=required_scope).inc()
                        logger.warning(
                            "Scope violation",
                            extra={"sub": claims.get("sub"), "scope": claims.get("scope"),
                                   "required": required_scope}
                        )
                        return make_bearer_error(
                            "insufficient_scope",
                            f"Required: {required_scope}",
                            required_scope
                        )

            except TokenValidationError as e:
                logger.warning(
                    "Token validation failed",
                    extra={"error": e.error, "description": e.description,
                           "path": request.path}
                )
                return make_bearer_error(e.error, e.description)

            elapsed = time.perf_counter() - start
            logger.info(
                "Authorized request",
                extra={"sub": claims["sub"], "scope": claims.get("scope"),
                       "path": request.path, "validation_ms": round(elapsed * 1000, 2)}
            )
            g.claims = claims
            return f(*args, **kwargs)
        return wrapper
    return decorator
```

-----

## Part 6: Monitoring and Alerting 📊

```python
# Prometheus alerting rules for OAuth2

OAUTH2_ALERTS = """
groups:
- name: oauth2
  rules:

  - alert: HighTokenValidationFailureRate
    expr: >
      rate(oauth2_token_validations_total{result="failure"}[5m]) /
      rate(oauth2_token_validations_total[5m]) > 0.05
    for: 2m
    annotations:
      summary: "OAuth2 token validation failure rate above 5%"
      description: >
        Failure rate is {{ $value | humanizePercentage }}.
        May indicate: expired tokens not being refreshed, token theft attempts,
        or a mis-configured client.

  - alert: UnexpectedAudienceMismatch
    expr: >
      rate(oauth2_token_validations_total{error_type="invalid_token"}[5m]) > 0.1
    for: 1m
    annotations:
      summary: "High rate of invalid_token errors — possible audience bypass attempt"

  - alert: ScopeViolationSpike
    expr: >
      rate(oauth2_scope_violations_total[5m]) > 1
    for: 2m
    annotations:
      summary: "Elevated scope violation rate — client requesting unauthorized operations"
"""

# Key metrics to monitor:
# oauth2_token_validations_total{result="failure"} — failed validations
# oauth2_token_validations_total{result="success"} — successful
# oauth2_scope_violations_total — attempts with wrong scope
# oauth2_token_validation_duration_seconds — validation latency
# jwks_cache_hits_total — JWKS cache performance
# jwks_fetch_total — how often JWKS is refetched
```

-----

## Part 7: The Production Security Checklist 🔐

```
Authorization Server:
  [✓] HTTPS only on all endpoints
  [✓] HSTS header on all responses
  [✓] PKCE required for all authorization code flows
  [✓] Implicit grant disabled
  [✓] ROPC disabled
  [✓] redirect_uri exact string match
  [✓] Short authorization code lifetime (<5 minutes)
  [✓] Refresh token rotation enabled
  [✓] Signed JWTs with RS256 or ES256
  [✓] Key rotation schedule (rotate JWKS keys periodically)
  [✓] Rate limiting on /token endpoint (prevents brute force)
  [✓] Audit logging on all operations
  [✓] Consent screen always shown (no silent authorization)
  [✓] CORS configured — only allow legitimate client origins

Resource Server:
  [✓] ALWAYS validate signature (JWKS-based)
  [✓] ALWAYS whitelist algorithms (never include "none")
  [✓] ALWAYS check iss
  [✓] ALWAYS check aud (unique per RS)
  [✓] ALWAYS check exp with reasonable leeway (≤60s)
  [✓] ALWAYS check scope before permitting operation
  [✓] Return WWW-Authenticate header on 401/403
  [✓] Cache JWKS with TTL (avoid fetching per request)
  [✓] Handle JWKS key rotation gracefully
  [✓] Log all validation failures with error type

Client Application:
  [✓] Use Authorization Code + PKCE (never Implicit)
  [✓] Always generate and verify state
  [✓] Store tokens in server-side session (web apps)
  [✓] Use HttpOnly, Secure, SameSite=Strict cookies
  [✓] Never put tokens in URLs or logs
  [✓] Implement token refresh before expiry
  [✓] Revoke tokens on logout
  [✓] Request minimum necessary scopes
  [✓] Register exact redirect_uri (no wildcards)
```

-----

## The Series: Eight Cases Closed 🏁

*Grissom stands at the complete investigation board.*

**GRISSOM:** “Eight episodes. Eight case files.”

*He walks the board.*

**GRISSOM:** “Episode 1: The question. Not ‘who are you?’ but ‘what may you?’ Not identity — authorization. The four roles. The grant types. The scope as the warrant’s coverage.”

**GRISSOM:** “Episode 2: The warrant application. Authorization code flow. PKCE — the tamper-evident envelope. State — the CSRF guard. The redirect_uri as the delivery address. The five-step dance, implemented correctly.”

**GRISSOM:** “Episode 3: The evidence room. JWT anatomy — header, payload, signature. Every claim: sub, iss, aud, exp, iat, nbf, jti, scope. The ID token versus the access token. Opaque versus structured.”

**GRISSOM:** “Episode 4: The crime lab. OIDC discovery document — the single URL that describes everything. JWKS — the fingerprint database. Client registration. Scope and claims design. Keycloak and ORY Hydra in production.”

**GRISSOM:** “Episode 5: Running the prints. The complete Resource Server validation pipeline — seven mandatory checks, implemented in Python and Node.js. Token introspection for opaque tokens. RFC 6750 error responses.”

**GRISSOM:** “Episode 6: Cold cases. Alg:none — the forged warrant. Audience bypass — the wrong precinct’s token. CSRF via missing state. Open redirect — code delivery to an attacker. Bearer token theft. Authorization code injection. The implicit grant’s fatal flaw.”

**GRISSOM:** “Episode 7: Undercover operations. Client Credentials — the machine-to-machine agent. Device Authorization — the TV set that calls the precinct. Refresh tokens and rotation. DPoP — binding the token to a key, making theft useless. PAR — sealing the authorization request. Token Exchange — the chain of custody.”

**GRISSOM:** “Episode 8: This one. OAuth 2.1 compliance. Production hardening. Monitoring. Token lifetimes. Audience isolation. The complete checklist.”

*He turns.*

**GRISSOM:** “Every token is a warrant. Every scope is what the warrant covers. Every claim is evidence. The question ‘what may you?’ has an answer in every token — if the implementation is correct, the answer is precise, bounded, and verifiable. If it is not — if the audience is unchecked, if PKCE is missing, if the algorithm whitelist is open — the warrant is forgeable.”

*He picks up the last case file.*

**GRISSOM:** “Authorization is not authentication. It is not identity. It is permission — specific, scoped, time-limited, cryptographically signed permission. Get it right and every API operates in a secure, auditable, accountable way. Get it wrong and the most sophisticated attacker in the room is anyone who happens to find a token in a log file.”

*He stamps the file: CASE CLOSED.*

*A token arrives at the API gateway. Seven checks run in 0.6 milliseconds. The scope is present. The audience matches. The signature is valid. The expiry has not passed.*

*The request is permitted.*

*What may you?*

*Exactly this. Nothing more.*

*Case closed.*

*🎵 What may you? What what, what what? 🎵*

-----

**🔗 Resources**

- **OAuth 2.1 draft**: [oauth.net/2.1](https://oauth.net/2.1/)
- **RFC 9700 — OAuth 2.0 Security BCP**: [rfc-editor.org/rfc/rfc9700](https://www.rfc-editor.org/rfc/rfc9700)
- **RFC 7009 — Token Revocation**: [rfc-editor.org/rfc/rfc7009](https://www.rfc-editor.org/rfc/rfc7009)
- **OWASP OAuth Cheat Sheet**: [cheatsheetseries.owasp.org/cheatsheets/OAuth_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/OAuth_Cheat_Sheet.html)
- **oauth.net/2**: [oauth.net/2](https://oauth.net/2/)

-----

*🔬 What May You OAuth2? — eight cases, one authorization protocol, zero unverified tokens. The investigation is complete.*
