---
title: "What May You OAuth2? 🔬 Ep.4"
published: false
description: "Episode 4: Every warrant comes from somewhere. The Authorization Server is the crime lab — the institution that authenticates users, records consent, issues tokens, publishes public keys, and maintains the registry of registered clients. This episode tours the lab: the OIDC discovery document, the JWKS endpoint, client registration, scope and claims design, and running Keycloak and ORY Hydra as real Authorization Servers."
tags: [oauth2, keycloak, openidconnect, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-may-you-oauth2-episode-04.png"
series: "What May You OAuth2?"
canonical_url: ""
organization: "the-software-s-journey"
part: 4
---

## Episode 4: The Crime Lab

*🎵 What may you? What what, what what? 🎵*

-----

## “The Lab Is Where Warrants Are Made” 🏛️

*Nick Stokes walks through the Authorization Server’s interface. Endpoints, registered clients, active sessions, token policies.*

**NICK:** “In the field, we carry the warrant. But someone has to make it. Sign it. Record it. Maintain the keys. Revoke it when it expires or gets stolen. That is the crime lab’s job. In OAuth2, that is the Authorization Server.”

*He opens the OIDC discovery document.*

**NICK:** “Every compliant Authorization Server publishes its entire capability profile at a single URL. Token endpoint, authorization endpoint, JWKS, supported scopes, supported algorithms. Everything a client or Resource Server needs to interoperate — in one JSON document.”

-----

## 🗂️ SIPOC — The Crime Lab Operations

|**Suppliers**          |**Inputs**                                                                   |**Process**                                                            |**Outputs**                                                            |**Customers**                                                               |
|-----------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------------|
|The AS operator        |Client registration data, scope definitions, user store, policy configuration|Configure and run the Authorization Server                             |A functioning OAuth2/OIDC provider at a stable issuer URL              |All clients (requesting tokens) and all Resource Servers (validating tokens)|
|JWKS endpoint          |The AS’s current signing key(s)                                              |Serve the public key set as JSON at a well-known URL                   |A JWK Set — public keys for verifying JWT signatures                   |Resource Servers — which fetch and cache these keys to verify tokens locally|
|OIDC discovery document|The AS’s configuration                                                       |Serve metadata at `/.well-known/openid-configuration`                  |A JSON document describing every endpoint, capability, and policy      |Clients and Resource Servers — which auto-configure from a single URL       |
|Client registration    |Client name, redirect URIs, scopes, authentication method                    |AS stores registration; issues client_id (and optionally client_secret)|A client_id that clients use to identify themselves in all OAuth2 flows|The registered client application                                           |

-----

## Part 1: The OIDC Discovery Document — The Lab’s Yellow Pages 📖

Every compliant AS publishes a discovery document at:

```
https://[issuer]/.well-known/openid-configuration
```

```bash
curl https://auth.acme.com/.well-known/openid-configuration | python3 -m json.tool
```

```json
{
  "issuer": "https://auth.acme.com",
  "authorization_endpoint": "https://auth.acme.com/oauth2/authorize",
  "token_endpoint": "https://auth.acme.com/oauth2/token",
  "userinfo_endpoint": "https://auth.acme.com/oauth2/userinfo",
  "jwks_uri": "https://auth.acme.com/.well-known/jwks.json",
  "registration_endpoint": "https://auth.acme.com/clients",
  "introspection_endpoint": "https://auth.acme.com/oauth2/introspect",
  "revocation_endpoint": "https://auth.acme.com/oauth2/revoke",
  "end_session_endpoint": "https://auth.acme.com/logout",
  "scopes_supported": [
    "openid", "profile", "email", "offline_access",
    "read:data", "write:data", "admin"
  ],
  "response_types_supported": ["code"],
  "grant_types_supported": [
    "authorization_code",
    "refresh_token",
    "client_credentials",
    "urn:ietf:params:oauth:grant-type:device_code"
  ],
  "subject_types_supported": ["public"],
  "id_token_signing_alg_values_supported": ["RS256", "ES256"],
  "token_endpoint_auth_methods_supported": [
    "client_secret_basic",
    "client_secret_post",
    "private_key_jwt",
    "tls_client_auth",
    "none"
  ],
  "claims_supported": [
    "sub", "iss", "aud", "exp", "iat", "jti",
    "name", "given_name", "family_name", "email",
    "email_verified", "phone_number", "address"
  ],
  "code_challenge_methods_supported": ["S256"],
  "request_parameter_supported": true,
  "pushed_authorization_request_endpoint": "https://auth.acme.com/oauth2/par"
}
```

-----

## Part 2: The JWKS Endpoint — The Fingerprint Database 🔑

```bash
curl https://auth.acme.com/.well-known/jwks.json | python3 -m json.tool
```

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "kid": "key-1",
      "alg": "RS256",
      "n": "pjdss8ZaDfEH6K6U7GeW2nxDqR4IP049fk1fK0lndimbMMVBdPv_hSpm8T8EtBDxrUdi1OHZfMhUixGyw...",
      "e": "AQAB"
    },
    {
      "kty": "EC",
      "use": "sig",
      "kid": "key-2",
      "alg": "ES256",
      "crv": "P-256",
      "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
      "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0"
    }
  ]
}
```

**JWKS field reference:**

|Field          |Meaning                                      |Notes                                 |
|---------------|---------------------------------------------|--------------------------------------|
|`kty`          |Key type: `RSA` or `EC`                      |Determines which fields are present   |
|`use`          |Usage: `sig` (signing) or `enc` (encryption) |We want `sig` for JWT verification    |
|`kid`          |Key ID                                       |Must match the `kid` in the JWT header|
|`alg`          |Algorithm: `RS256`, `ES256`…                 |The algorithm this key is used with   |
|`n`, `e`       |RSA public key components (modulus, exponent)|Reconstituted as the public key       |
|`crv`, `x`, `y`|EC key components                            |Used for ES256/ES384                  |

**Fetching and caching JWKS in a Resource Server:**

```python
import httpx
import time
from functools import lru_cache
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

class JWKSCache:
    """Thread-safe JWKS cache with TTL and kid-based lookup."""

    def __init__(self, jwks_uri: str, ttl_seconds: int = 3600):
        self.jwks_uri = jwks_uri
        self.ttl_seconds = ttl_seconds
        self._cache: dict = {}
        self._fetched_at: float = 0

    def get_key(self, kid: str):
        """Get the public key for a given kid. Refreshes cache if stale."""
        # Refresh if cache is stale OR kid is not found
        if time.time() - self._fetched_at > self.ttl_seconds or kid not in self._cache:
            self._refresh()

        # After refresh, check again (handles key rotation)
        if kid not in self._cache:
            raise KeyError(f"Unknown kid: {kid}")

        return self._cache[kid]

    def _refresh(self):
        import jwt
        jwks_client = jwt.PyJWKClient(self.jwks_uri, cache_jwk_set=True, lifespan=360)
        self._fetched_at = time.time()
        # PyJWKClient handles fetching and caching internally
        self._client = jwks_client
```

-----

## Part 3: The AS in Docker — Running the Lab 🐳

### Option A: Keycloak (full-featured, enterprise-ready)

```yaml
# docker-compose.yml for Keycloak
services:
  keycloak:
    image: quay.io/keycloak/keycloak:25.0
    command: start-dev
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
      KC_HOSTNAME: localhost
    ports:
      - "8080:8080"
    volumes:
      - keycloak_data:/opt/keycloak/data

volumes:
  keycloak_data:
```

```bash
docker compose up -d

# Access admin UI at http://localhost:8080
# Realm: master (default)
# Discovery: http://localhost:8080/realms/master/.well-known/openid-configuration
```

**Create a realm via Keycloak REST API:**

```bash
# Get admin access token
ADMIN_TOKEN=$(curl -s \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" \
  http://localhost:8080/realms/master/protocol/openid-connect/token \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Create a new realm
curl -s \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "realm": "acme",
    "enabled": true,
    "displayName": "ACME Corporation",
    "sslRequired": "external",
    "registrationAllowed": false,
    "loginWithEmailAllowed": true,
    "accessTokenLifespan": 3600,
    "refreshTokenMaxReuse": 0,
    "revokeRefreshToken": true
  }' \
  http://localhost:8080/admin/realms

# Realm discovery document
curl http://localhost:8080/realms/acme/.well-known/openid-configuration
```

### Option B: ORY Hydra (OAuth2-only, minimal, production-focused)

```yaml
services:
  hydra:
    image: oryd/hydra:v2.2
    command: serve all --dev
    environment:
      DSN: memory
      URLS_SELF_ISSUER: http://localhost:4444
      URLS_CONSENT: http://localhost:3000/consent
      URLS_LOGIN: http://localhost:3000/login
      SECRETS_SYSTEM: "this-is-a-dev-secret-change-in-prod"
    ports:
      - "4444:4444"   # Public OAuth2 endpoints
      - "4445:4445"   # Admin API
```

-----

## Part 4: Client Registration — Registering with the Lab 📝

Every application that wants to use OAuth2 must be registered with the AS. The registration records:

- What grant types it may use
- Which redirect URIs are valid
- What scopes it may request
- How it authenticates to the token endpoint
- Token lifetimes

```bash
# Register a confidential web application via Keycloak Admin API
curl -s \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "my-webapp",
    "name": "ACME Web Application",
    "enabled": true,
    "protocol": "openid-connect",
    "publicClient": false,
    "standardFlowEnabled": true,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": false,
    "serviceAccountsEnabled": false,
    "redirectUris": [
      "https://app.acme.com/oauth/callback"
    ],
    "webOrigins": ["https://app.acme.com"],
    "defaultClientScopes": ["openid", "profile", "email"],
    "optionalClientScopes": ["read:data", "write:data"],
    "attributes": {
      "access.token.lifespan": "3600",
      "client.session.max.lifespan": "86400",
      "pkce.code.challenge.method": "S256"
    }
  }' \
  http://localhost:8080/admin/realms/acme/clients

# Register a public SPA client
curl -s \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "acme-spa",
    "publicClient": true,
    "standardFlowEnabled": true,
    "redirectUris": ["https://spa.acme.com/*"],
    "webOrigins": ["https://spa.acme.com"],
    "attributes": {
      "pkce.code.challenge.method": "S256"
    }
  }' \
  http://localhost:8080/admin/realms/acme/clients

# Register a machine-to-machine service client
curl -s \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "backend-service",
    "publicClient": false,
    "standardFlowEnabled": false,
    "serviceAccountsEnabled": true,
    "defaultClientScopes": ["read:internal-data"]
  }' \
  http://localhost:8080/admin/realms/acme/clients
```

-----

## Part 5: Scope and Claims Design — The Warrant Template Library 🗂️

Good scope design is the difference between a useful authorization system and an unmaintainable mess.

### Scope Design Principles

```
Principle 1: Verb-Noun pattern
  read:users      — read operations on the users resource
  write:users     — write operations on the users resource
  delete:users    — delete operations on the users resource
  admin:billing   — administrative access to billing

Principle 2: Don't mix fine and coarse
  BAD:  read:profile  AND  api  (one is fine, one is "everything")
  GOOD: read:profile  AND  read:data  AND  write:data

Principle 3: Scope = capability, not role
  BAD:  scope=admin      (role-based — what defines "admin"?)
  GOOD: scope=read:users write:users delete:users

Principle 4: Audience-specific scopes
  api1:read:data   — read from API 1
  api2:read:data   — read from API 2
  (Prevents a token for API1 from working at API2)
```

### Adding Custom Scopes in Keycloak

```bash
# Create a custom scope
curl -s \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "read:data",
    "description": "Read access to user data",
    "protocol": "openid-connect",
    "attributes": {
      "include.in.token.scope": "true",
      "display.on.consent.screen": "true",
      "consent.screen.text": "Read your data"
    }
  }' \
  http://localhost:8080/admin/realms/acme/client-scopes
```

### Adding Custom Claims — Extending the Warrant Template

```bash
# Add a protocol mapper that includes "department" in the access token
# First get the scope ID
SCOPE_ID=$(curl -s \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8080/admin/realms/acme/client-scopes \
  | python3 -c "
import sys, json
scopes = json.load(sys.stdin)
print([s['id'] for s in scopes if s['name']=='read:data'][0])
")

# Add a mapper for the department attribute
curl -s \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "department-claim",
    "protocol": "openid-connect",
    "protocolMapper": "oidc-user-attribute-mapper",
    "config": {
      "claim.name": "department",
      "user.attribute": "department",
      "id.token.claim": "false",
      "access.token.claim": "true",
      "userinfo.token.claim": "true",
      "jsonType.label": "String"
    }
  }' \
  "http://localhost:8080/admin/realms/acme/client-scopes/$SCOPE_ID/protocol-mappers/models"
```

-----

## Part 6: The /userinfo Endpoint — The Crime Lab Report 📊

The `/userinfo` endpoint returns the authenticated user’s attributes. It requires a valid access token with the `openid` scope.

```bash
# Request user information
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  https://auth.acme.com/oauth2/userinfo

# Response:
# {
#   "sub": "user_42",
#   "name": "Alice Smith",
#   "given_name": "Alice",
#   "family_name": "Smith",
#   "email": "alice@acme.com",
#   "email_verified": true,
#   "phone_number": "+1 702 555 0101",
#   "department": "Engineering",
#   "locale": "en-US"
# }
```

```python
def get_user_info(userinfo_endpoint: str, access_token: str) -> dict:
    """Fetch user attributes from the /userinfo endpoint."""
    response = httpx.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=5.0,
    )
    if response.status_code == 401:
        raise TokenInvalidError("Access token is invalid or expired")
    if response.status_code == 403:
        raise InsufficientScopeError("Token lacks 'openid' scope")
    response.raise_for_status()
    return response.json()
```

-----

## What’s Next: Running the Prints 🖐️

*Warrick Brown looks at the Resource Server code on his monitor.*

**WARRICK:** “The token is issued. The client has it. Now it walks up to the API and presents it. Episode 5: running the prints. The complete Resource Server validation pipeline — extract from header, verify signature via JWKS, check every claim, verify scope, optionally call introspect. Every step. Every failure mode. In Python and Node.js.”

-----

**🔗 Resources**

- **Keycloak documentation**: [keycloak.org/documentation](https://www.keycloak.org/documentation)
- **ORY Hydra**: [ory.sh/hydra](https://www.ory.sh/hydra/)
- **RFC 7591 — Dynamic Client Registration**: [rfc-editor.org/rfc/rfc7591](https://www.rfc-editor.org/rfc/rfc7591)
- **OpenID Connect Discovery**: [openid.net/specs/openid-connect-discovery-1_0.html](https://openid.net/specs/openid-connect-discovery-1_0.html)

-----

*🔬 What May You OAuth2? — a CSI-style investigation into authorization. The evidence is in the token. The verdict is in the scope.*
