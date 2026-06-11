---
title: "What May You OAuth2? 🔬 Ep.5"
published: false
description: "Episode 5: The token arrives at the Resource Server. The API must now answer: is this token valid? Is it mine? Is it still live? Does it permit this operation? The complete validation pipeline — extract from header, fetch JWKS, verify signature, check iss, check aud, check exp, check nbf, check scope — in Python and Node.js. Every step. Every failure code. Running the prints."
tags: [oauth2, security, validation, python]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-may-you-oauth2-episode-05.png"
series: "What May You OAuth2?"
canonical_url: ""
organization: "the-software-s-journey"
part: 5
---

## Episode 5: Running the Prints

*🎵 What may you? What what, what what? 🎵*

-----

## “Run the Prints” 🖐️

*Warrick Brown at the AFIS terminal. A token just arrived at the API gateway. He has fifteen milliseconds to decide: valid or not.*

**WARRICK:** “In the old days, you called back to the precinct to verify every warrant. Slow. Expensive. Didn’t scale. Now we have JWKS — the fingerprint database. The Resource Server downloads the public keys once, caches them, and verifies tokens locally in microseconds. No network call to the Authorization Server on every request.”

*He runs the validation pipeline.*

**WARRICK:** “Seven steps. Miss any one and the investigation is compromised. Let me show you every step — and what happens when you skip one.”

-----

## 🗂️ SIPOC — The Token Validation Pipeline

|**Suppliers**|**Inputs**                            |**Process**                                                                     |**Outputs**                                     |**Customers**                                                   |
|-------------|--------------------------------------|--------------------------------------------------------------------------------|------------------------------------------------|----------------------------------------------------------------|
|HTTP client  |`Authorization: Bearer <token>` header|Extract token from header; reject if missing or malformed                       |The raw token string                            |Step 2: signature verification                                  |
|JWKS cache   |The JWT header `kid` field            |Fetch public key matching `kid` from JWKS (cached); verify JWT signature        |Signature valid / invalid                       |Steps 3-7: claims validation (only proceeds if signature passes)|
|JWT claims   |`iss`, `aud`, `exp`, `nbf`, `scope`   |Sequential claim checks: each failure returns 401 with `WWW-Authenticate` header|Permission granted or denied with specific error|The calling application — which handles the HTTP error response |

-----

## The Complete Validation Checklist 📋

```
Step 1: Extract token from Authorization: Bearer header
Step 2: Decode JWT header — get algorithm and kid
Step 3: Reject "alg": "none" — NEVER accept unsigned tokens
Step 4: Fetch/cache public key from JWKS by kid
Step 5: Verify signature cryptographically
Step 6: Validate iss (issuer) — must match expected AS
Step 7: Validate aud (audience) — must include this RS
Step 8: Validate exp (expiry) — must be in the future
Step 9: Validate nbf (not-before) — must be in the past
Step 10: Validate required claims present (sub, jti...)
Step 11: Validate scope — must contain required permission
Step 12: (Optional) Check revocation via introspection
Step 13: PERMIT the operation
```

-----

## Python: The Complete Resource Server Middleware 🐍

```python
# oauth2_middleware.py — Production-ready OAuth2 token validation

from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from functools import wraps
from typing import Callable

import httpx
import jwt  # PyJWT[crypto]
from jwt import PyJWKClient, InvalidTokenError
from flask import request, jsonify, g

logger = logging.getLogger(__name__)


@dataclass
class OAuth2Config:
    """Configuration for the Resource Server validator."""
    issuer: str                          # e.g. "https://auth.acme.com"
    audience: str                        # e.g. "https://api.acme.com"
    jwks_uri: str                        # e.g. "https://auth.acme.com/.well-known/jwks.json"
    algorithms: list[str]               # e.g. ["RS256", "ES256"]
    leeway_seconds: int = 60             # Clock skew tolerance
    jwks_cache_ttl: int = 3600           # How long to cache the JWKS


class TokenValidator:
    """
    Validates OAuth2 Bearer tokens for a Resource Server.
    Thread-safe. JWKS-caching.
    """

    def __init__(self, config: OAuth2Config):
        self.config = config
        self._jwks_client = PyJWKClient(
            config.jwks_uri,
            cache_jwk_set=True,
            lifespan=config.jwks_cache_ttl,
        )

    def validate(self, token: str) -> dict:
        """
        Validate a Bearer token. Returns claims if valid.
        Raises TokenValidationError with a descriptive message if invalid.
        """

        # ── Step 2-3: Decode header and reject alg:none ──────────
        try:
            unverified_header = jwt.get_unverified_header(token)
        except Exception as e:
            raise TokenValidationError(
                "invalid_token",
                "Malformed JWT header",
                status_code=401
            ) from e

        if unverified_header.get("alg", "").lower() == "none":
            raise TokenValidationError(
                "invalid_token",
                "Unsigned tokens (alg:none) are not accepted",
                status_code=401
            )

        # ── Steps 4-5: Fetch signing key and verify signature ────
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
        except jwt.exceptions.PyJWKClientError as e:
            raise TokenValidationError(
                "invalid_token",
                f"Could not find signing key: {e}",
                status_code=401
            ) from e

        # ── Steps 6-10: Decode and verify all standard claims ────
        try:
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=self.config.algorithms,
                audience=self.config.audience,       # Validates aud
                issuer=self.config.issuer,           # Validates iss
                options={
                    "require": ["exp", "iat", "sub", "iss", "aud"],
                    "verify_exp": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_nbf": True,
                    "leeway": self.config.leeway_seconds,
                }
            )
        except jwt.ExpiredSignatureError:
            raise TokenValidationError(
                "invalid_token",
                "Token has expired",
                status_code=401
            )
        except jwt.InvalidAudienceError:
            raise TokenValidationError(
                "invalid_token",
                f"Token audience does not include {self.config.audience}",
                status_code=401
            )
        except jwt.InvalidIssuerError:
            raise TokenValidationError(
                "invalid_token",
                f"Token issuer is not {self.config.issuer}",
                status_code=401
            )
        except jwt.ImmatureSignatureError:
            raise TokenValidationError(
                "invalid_token",
                "Token is not yet valid (nbf)",
                status_code=401
            )
        except InvalidTokenError as e:
            raise TokenValidationError(
                "invalid_token",
                str(e),
                status_code=401
            ) from e

        return claims

    def validate_scope(self, claims: dict, required_scope: str) -> None:
        """
        Check that the token contains a required scope.
        Raises TokenValidationError with insufficient_scope if missing.
        """
        granted = set(claims.get("scope", "").split())
        if required_scope not in granted:
            raise TokenValidationError(
                "insufficient_scope",
                f"Token scope '{claims.get('scope', '')}' "
                f"does not include required scope '{required_scope}'",
                status_code=403
            )


class TokenValidationError(Exception):
    def __init__(self, error: str, description: str, status_code: int):
        self.error = error
        self.description = description
        self.status_code = status_code
        super().__init__(description)


# ── Flask middleware decorator ────────────────────────────────────────

def require_auth(required_scope: str | None = None):
    """
    Flask decorator: validate Bearer token on the request.
    Sets g.claims with the validated token claims.
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Step 1: Extract token from header
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({
                    "error": "invalid_request",
                    "error_description": "Missing or invalid Authorization header"
                }), 401, {
                    "WWW-Authenticate": (
                        f'Bearer realm="{validator.config.issuer}", '
                        f'error="invalid_request"'
                    )
                }

            token = auth_header[7:]  # Strip "Bearer "

            # Validate the token
            try:
                claims = validator.validate(token)

                # Step 11: Scope check
                if required_scope:
                    validator.validate_scope(claims, required_scope)

            except TokenValidationError as e:
                return jsonify({
                    "error": e.error,
                    "error_description": e.description
                }), e.status_code, {
                    "WWW-Authenticate": (
                        f'Bearer realm="{validator.config.issuer}", '
                        f'error="{e.error}", '
                        f'error_description="{e.description}"'
                    )
                }

            # Attach claims to Flask request context
            g.claims = claims
            g.subject = claims["sub"]
            logger.info(
                "Authorized: sub=%s scope=%s",
                claims["sub"],
                claims.get("scope", "")
            )

            return f(*args, **kwargs)
        return wrapper
    return decorator


# ── Usage in Flask routes ─────────────────────────────────────────────

from flask import Flask

app = Flask(__name__)

validator = TokenValidator(OAuth2Config(
    issuer="https://auth.acme.com",
    audience="https://api.acme.com",
    jwks_uri="https://auth.acme.com/.well-known/jwks.json",
    algorithms=["RS256", "ES256"],
))

@app.route("/api/profile", methods=["GET"])
@require_auth(required_scope="read:profile")
def get_profile():
    # g.claims is populated by the decorator
    return jsonify({
        "sub": g.claims["sub"],
        "message": f"Hello, {g.claims.get('name', g.claims['sub'])}"
    })

@app.route("/api/data", methods=["POST"])
@require_auth(required_scope="write:data")
def write_data():
    return jsonify({"status": "written", "by": g.subject})

@app.route("/api/admin/users", methods=["DELETE"])
@require_auth(required_scope="admin")
def admin_delete():
    return jsonify({"status": "deleted", "by": g.subject})
```

-----

## Node.js: Resource Server Middleware 🟨

```javascript
// oauth2-middleware.js — Express.js Resource Server middleware

const jwt = require('jsonwebtoken');
const jwksRsa = require('jwks-rsa');

// Configure the JWKS client
const jwksClient = jwksRsa({
  jwksUri: 'https://auth.acme.com/.well-known/jwks.json',
  cache: true,
  cacheMaxEntries: 5,
  cacheMaxAge: 3600 * 1000,  // 1 hour in ms
  rateLimit: true,
  jwksRequestsPerMinute: 5,
});

// Fetch signing key by kid
function getKey(header, callback) {
  jwksClient.getSigningKey(header.kid, (err, key) => {
    if (err) return callback(err);
    const signingKey = key.publicKey || key.rsaPublicKey;
    callback(null, signingKey);
  });
}

/**
 * Express middleware: validate OAuth2 Bearer token.
 * @param {string} requiredScope - Scope that must be present in the token
 */
function requireAuth(requiredScope) {
  return (req, res, next) => {

    // Step 1: Extract token
    const authHeader = req.headers.authorization || '';
    if (!authHeader.startsWith('Bearer ')) {
      return res.status(401)
        .set('WWW-Authenticate', 'Bearer realm="https://auth.acme.com"')
        .json({ error: 'invalid_request', error_description: 'Missing Bearer token' });
    }
    const token = authHeader.slice(7);

    // Step 2-3: Decode header and reject alg:none
    let header;
    try {
      const [headerB64] = token.split('.');
      header = JSON.parse(Buffer.from(headerB64, 'base64url').toString());
    } catch (e) {
      return res.status(401).json({ error: 'invalid_token', error_description: 'Malformed JWT' });
    }
    if (!header.alg || header.alg.toLowerCase() === 'none') {
      return res.status(401).json({ error: 'invalid_token', error_description: 'Unsigned tokens rejected' });
    }

    // Steps 4-10: Verify signature and validate claims
    jwt.verify(
      token,
      getKey,
      {
        issuer: 'https://auth.acme.com',          // iss check
        audience: 'https://api.acme.com',          // aud check
        algorithms: ['RS256', 'ES256', 'PS256'],   // Never 'none'
        clockTolerance: 60,                        // 60s leeway
      },
      (err, claims) => {
        if (err) {
          const status = err.name === 'TokenExpiredError' ? 401 : 401;
          const errorCode =
            err.name === 'TokenExpiredError' ? 'invalid_token' :
            err.name === 'JsonWebTokenError'  ? 'invalid_token' :
            'invalid_token';

          return res.status(status)
            .set('WWW-Authenticate', `Bearer error="${errorCode}"`)
            .json({ error: errorCode, error_description: err.message });
        }

        // Step 11: Scope check
        if (requiredScope) {
          const grantedScopes = (claims.scope || '').split(' ');
          if (!grantedScopes.includes(requiredScope)) {
            return res.status(403)
              .set('WWW-Authenticate', `Bearer error="insufficient_scope", scope="${requiredScope}"`)
              .json({
                error: 'insufficient_scope',
                error_description: `Required scope: ${requiredScope}`
              });
          }
        }

        // Attach claims to request
        req.auth = claims;
        req.user = { sub: claims.sub, scope: claims.scope };
        next();
      }
    );
  };
}

// Usage in Express routes
const express = require('express');
const app = express();

app.get('/api/profile', requireAuth('read:profile'), (req, res) => {
  res.json({ sub: req.auth.sub, name: req.auth.name });
});

app.post('/api/data', requireAuth('write:data'), (req, res) => {
  res.json({ status: 'written', by: req.user.sub });
});
```

-----

## Token Introspection: Calling the Lab for Confirmation 📞

For opaque tokens — or when you need the most current revocation status — call the introspection endpoint:

```python
# RFC 7662 Token Introspection
async def introspect_token(
    introspection_endpoint: str,
    token: str,
    client_id: str,
    client_secret: str,
) -> dict:
    """
    Check token validity via the AS introspection endpoint.
    More expensive than local JWT validation but handles revocation.
    """
    response = await httpx.AsyncClient().post(
        introspection_endpoint,
        data={"token": token, "token_type_hint": "access_token"},
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=3.0,
    )
    response.raise_for_status()
    result = response.json()

    # Check if the token is active
    if not result.get("active", False):
        raise TokenValidationError("invalid_token", "Token is not active", 401)

    return result

# Introspection response:
# {
#   "active": true,
#   "sub": "user_42",
#   "scope": "read:profile read:data",
#   "client_id": "my-webapp",
#   "exp": 1749643200,
#   "iat": 1749639600,
#   "iss": "https://auth.acme.com",
#   "aud": "https://api.acme.com",
#   "token_type": "Bearer"
# }
#
# Or for a revoked/expired token:
# { "active": false }
```

-----

## The HTTP Error Response Standard: RFC 6750 📜

When token validation fails, the RS must return the correct HTTP error with a `WWW-Authenticate` header:

```python
# RFC 6750 compliant error responses

# 401 Unauthorized: no token, invalid token, expired token
# Header: WWW-Authenticate: Bearer realm="...", error="...", error_description="..."

# 403 Forbidden: token is valid but scope is insufficient
# Header: WWW-Authenticate: Bearer error="insufficient_scope", scope="required:scope"

# Complete error catalogue:
error_codes = {
    "invalid_request":    (401, "Malformed request — missing or duplicate parameters"),
    "invalid_token":      (401, "Token is expired, revoked, malformed, or not valid"),
    "insufficient_scope": (403, "Token lacks required scope"),
}

def make_bearer_error(error: str, description: str, required_scope: str = None) -> tuple:
    status = 403 if error == "insufficient_scope" else 401
    www_auth = f'Bearer realm="https://api.acme.com", error="{error}", error_description="{description}"'
    if required_scope:
        www_auth += f', scope="{required_scope}"'
    return {"error": error, "error_description": description}, status, {"WWW-Authenticate": www_auth}
```

-----

## What’s Next: Cold Cases 🧊

*Grissom puts down the validation playbook.*

**GRISSOM:** “We know how to validate. We know the correct path. But what about the cases where someone tries to subvert the validation? Episode 6: cold cases. Token theft. The `alg:none` attack. The `aud` bypass. CSRF via missing state. Open redirect abuse. Authorization code injection. The full OAuth2 threat catalogue — and how each one is detected and closed.”

-----

**🔗 Resources**

- **RFC 7662 — Token Introspection**: [rfc-editor.org/rfc/rfc7662](https://www.rfc-editor.org/rfc/rfc7662)
- **RFC 6750 — Bearer Token Usage**: [rfc-editor.org/rfc/rfc6750](https://www.rfc-editor.org/rfc/rfc6750)
- **PyJWT library**: [pyjwt.readthedocs.io](https://pyjwt.readthedocs.io)
- **jwks-rsa (Node.js)**: [github.com/auth0/node-jwks-rsa](https://github.com/auth0/node-jwks-rsa)

-----

*🔬 What May You OAuth2? — a CSI-style investigation into authorization. The evidence is in the token. The verdict is in the scope.*
