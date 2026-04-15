---
title: "Game on Djangular 🎮 Ep.8"
published: false
description: "Episode 8: SailPoint IAM is the guild registry — the authoritative record of every identity and what they are permitted to do. Before GameLib’s Django backend exchanges XML with the Linux server, it asks SailPoint: does this identity have the catalogue_update entitlement? SCIM 2.0, access tokens, and zero-trust enforcement."
tags: [django, python, iam, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/game_on_djangular_series/game-on-djangular-episode-08.png"
series: "Game on Djangular Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: The Guild Registry

> *“Your certificate proves you are who you say. The guild registry proves you are allowed to be here.”*

-----

## Authentication vs Authorisation 🗂️

Episodes 6 and 7 gave us cryptographic identity: the mTLS handshake proves the Django backend is the entity that holds the private key for the certificate signed by our CA. That is **authentication** — proving who you are.

But authentication is not sufficient for zero-trust. Knowing who someone is does not tell you what they are permitted to do. The Linux server accepting a connection from `CN=gamelib-backend` knows the caller holds a valid certificate. It does not know whether the GameLib backend is currently authorised to perform catalogue updates, whether that entitlement was revoked after a security incident, or whether it was ever granted in the first place.

**Authorisation** — the answer to “are you allowed?” — requires a separate system. That system is **SailPoint**.

-----

## 🗂️ SIPOC — The Guild Registry

|**Suppliers**                     |**Inputs**                                                            |**Process**                                                        |**Outputs**                                     |**Customers**                                                      |
|----------------------------------|----------------------------------------------------------------------|-------------------------------------------------------------------|------------------------------------------------|-------------------------------------------------------------------|
|SailPoint IdentityIQ / IdentityNow|Service account identity (`gamelib-backend`) + entitlement definitions|Administrator grants `catalogue_update` role to the service account|An entitlement record queryable via SCIM 2.0 API|Django `IAMClient` — queries SailPoint before each bridge operation|
|Django `IAMClient`                |Service account identifier + entitlement to check                     |SCIM 2.0 `GET /v2/Users?filter=...` → check entitlements           |`True` / `False` — caller is authorised or not  |`BridgeClient` decorator — block XML exchange if not authorised    |
|Linux server (inbound direction)  |Client cert CN from mTLS handshake                                    |Query SailPoint SCIM for the caller’s CN                           |Entitlement result                              |HTTP handler — accept or reject the request based on entitlement   |

-----

## What SailPoint Does in This Context 🏛️

**SailPoint IdentityIQ** (on-premises) and **SailPoint IdentityNow / Identity Security Cloud** (cloud) are Identity Governance and Administration (IGA) platforms. For GameLib, they serve two roles:

**Role 1: Service account entitlement registry**. The `gamelib-backend` service account exists in SailPoint as a managed identity. An administrator grants it the `catalogue_update` entitlement. When that entitlement needs to be removed (incident response, service decommission), the SailPoint admin revokes it in one place. Django queries SailPoint at runtime to check the current entitlement state.

**Role 2: Inbound verification**. When the Linux server receives an XML request from a client presenting `CN=gamelib-backend`, it can query SailPoint to verify that this service account identity is still active and still has the entitlement to perform this operation. The mTLS certificate proved the cryptographic identity. SailPoint confirms the business-level authorisation.

-----

## SailPoint SCIM 2.0 API Primer 📖

SailPoint exposes identity data via **SCIM 2.0** (System for Cross-domain Identity Management). SCIM is a standardised REST protocol using JSON payloads, operated over HTTPS.

Key endpoints used in this episode:

|Endpoint                                             |Method|Description                                |
|-----------------------------------------------------|------|-------------------------------------------|
|`/scim/v2/Users?filter=userName eq "gamelib-backend"`|`GET` |Retrieve a user/service account by username|
|`/scim/v2/Users/{id}/Entitlements`                   |`GET` |List entitlements for a specific user      |
|`/scim/v2/Roles?filter=name eq "catalogue_update"`   |`GET` |Look up a role definition                  |

Authentication to SailPoint:

- **IdentityIQ** (on-premises): HTTP Basic Auth with a dedicated integration user account
- **IdentityNow / ISC** (cloud): OAuth 2.0 Client Credentials — `POST /oauth/token` → `Bearer` token on subsequent calls

-----

## The SailPoint IAM Client 🔌

```python
# xml_bridge/iam_client.py
import logging
import requests
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class IAMClient:
    """
    Client for SailPoint IdentityIQ or IdentityNow SCIM 2.0 API.

    Settings:
        SAILPOINT_BASE_URL       — e.g. https://identityiq.company.com/identityiq
                                   or   https://tenant.api.identitynow.com
        SAILPOINT_AUTH_MODE      — "basic" (IIQ) or "oauth2" (IdentityNow)
        SAILPOINT_CLIENT_ID      — OAuth2 client ID (IdentityNow)
        SAILPOINT_CLIENT_SECRET  — OAuth2 client secret (IdentityNow)
        SAILPOINT_BASIC_USER     — HTTP Basic username (IdentityIQ)
        SAILPOINT_BASIC_PASS     — HTTP Basic password (IdentityIQ)
        SAILPOINT_CA_CERT        — Path to CA cert for HTTPS (if custom CA)
    """

    def __init__(self):
        self.base_url   = settings.SAILPOINT_BASE_URL.rstrip("/")
        self.auth_mode  = getattr(settings, "SAILPOINT_AUTH_MODE", "oauth2")
        self.ca_cert    = getattr(settings, "SAILPOINT_CA_CERT", True)   # True = system store
        self._session   = requests.Session()
        self._session.verify = self.ca_cert
        self._access_token: Optional[str] = None

    def _authenticate(self) -> None:
        """Obtain a fresh access token (OAuth2) or set Basic Auth headers."""
        if self.auth_mode == "oauth2":
            token_url = f"{self.base_url}/oauth/token"
            response = requests.post(
                token_url,
                data={
                    "grant_type":    "client_credentials",
                    "client_id":     settings.SAILPOINT_CLIENT_ID,
                    "client_secret": settings.SAILPOINT_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                verify=self.ca_cert,
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]
            self._session.headers.update(
                {"Authorization": f"Bearer {self._access_token}"}
            )

        elif self.auth_mode == "basic":
            self._session.auth = (
                settings.SAILPOINT_BASIC_USER,
                settings.SAILPOINT_BASIC_PASS,
            )

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        """Authenticated GET to SailPoint SCIM API."""
        if not self._access_token and self.auth_mode == "oauth2":
            self._authenticate()
        url = f"{self.base_url}/scim/v2/{path.lstrip('/')}"
        try:
            response = self._session.get(url, params=params, timeout=10)
            if response.status_code == 401 and self.auth_mode == "oauth2":
                # Token expired — refresh and retry once
                self._authenticate()
                response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as exc:
            logger.error("SailPoint SCIM error %s: %s", exc.response.status_code, url)
            raise
        except requests.exceptions.ConnectionError:
            logger.error("Cannot reach SailPoint at %s", url)
            raise

    # ---------------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------------

    def get_identity(self, username: str) -> Optional[dict]:
        """
        Retrieve a SailPoint identity (user/service account) by username.

        Returns the SCIM User resource dict, or None if not found.
        """
        result = self._get("Users", params={
            "filter": f'userName eq "{username}"',
            "attributes": "id,userName,active,displayName",
        })
        resources = result.get("Resources", [])
        return resources[0] if resources else None

    def has_entitlement(self, username: str, entitlement_name: str) -> bool:
        """
        Check whether a SailPoint identity holds a specific entitlement.

        Args:
            username:         The service account or user username in SailPoint.
            entitlement_name: The entitlement / role name to check,
                              e.g. "catalogue_update" or "gamelib.xml.write".

        Returns:
            True if the identity is active AND holds the entitlement.
        """
        identity = self.get_identity(username)
        if not identity:
            logger.warning("Identity not found in SailPoint: %s", username)
            return False

        if not identity.get("active", False):
            logger.warning("Identity %s is inactive in SailPoint", username)
            return False

        # Fetch assigned entitlements / roles for this identity
        user_id = identity["id"]
        try:
            roles_data = self._get(
                f"Users/{user_id}",
                params={"attributes": "id,userName,roles,entitlements"},
            )
        except Exception:
            logger.error("Could not retrieve entitlements for %s", username)
            return False

        # Check roles array (IdentityNow format)
        roles = roles_data.get("roles", [])
        for role in roles:
            role_name = role.get("value") or role.get("display") or ""
            if role_name.lower() == entitlement_name.lower():
                logger.info("Identity %s has entitlement %s", username, entitlement_name)
                return True

        logger.warning("Identity %s does NOT have entitlement %s", username, entitlement_name)
        return False

    def is_service_account_authorised(
        self, cn: str, operation: str
    ) -> bool:
        """
        High-level check: given the CN from a client certificate,
        determine whether the corresponding SailPoint identity is
        authorised for the named operation.

        This is the primary entry point for the xml_bridge.

        Args:
            cn:        Common Name from the mTLS client certificate,
                       e.g. "gamelib-backend"
            operation: The operation being attempted,
                       e.g. "catalogue_update" or "vault_export"

        Returns:
            True if authorised; False otherwise.
        """
        # Map CN to SailPoint username (may be identical or require lookup)
        sailpoint_username = getattr(settings, "SAILPOINT_CN_MAP", {}).get(cn, cn)
        return self.has_entitlement(sailpoint_username, operation)


# Module-level singleton
iam_client = IAMClient()
```

-----

## Wiring IAM into the Bridge Client 🔗

```python
# xml_bridge/client.py — updated post_xml and get_xml methods

from .iam_client import iam_client

class BridgeClient:
    # ... (previous code unchanged) ...

    def _check_authorisation(self, operation: str) -> None:
        """
        Before performing an XML bridge operation, verify that the
        service account identity is authorised in SailPoint.
        """
        if not getattr(settings, "XML_BRIDGE_IAM_ENABLED", False):
            return    # IAM check disabled (dev mode)

        cn = getattr(settings, "XML_BRIDGE_IDENTITY_CN", "gamelib-backend")
        if not iam_client.is_service_account_authorised(cn, operation):
            raise PermissionError(
                f"SailPoint IAM: identity '{cn}' is not authorised "
                f"for operation '{operation}'."
            )

    def post_xml(self, path: str, xml_bytes: bytes, operation: str = "catalogue_update"):
        self._check_authorisation(operation)    # IAM gate
        # ... rest of post_xml from Episode 5 unchanged ...

    def get_xml(self, path: str, params=None, operation: str = "catalogue_read"):
        self._check_authorisation(operation)    # IAM gate
        # ... rest of get_xml from Episode 5 unchanged ...
```

Django settings additions:

```python
# gamelib/settings.py
SAILPOINT_BASE_URL     = os.environ.get("SAILPOINT_BASE_URL", "")
SAILPOINT_AUTH_MODE    = os.environ.get("SAILPOINT_AUTH_MODE", "oauth2")
SAILPOINT_CLIENT_ID    = os.environ.get("SAILPOINT_CLIENT_ID", "")
SAILPOINT_CLIENT_SECRET = os.environ.get("SAILPOINT_CLIENT_SECRET", "")
# For IIQ Basic Auth:
SAILPOINT_BASIC_USER   = os.environ.get("SAILPOINT_BASIC_USER", "")
SAILPOINT_BASIC_PASS   = os.environ.get("SAILPOINT_BASIC_PASS", "")
SAILPOINT_CA_CERT      = os.environ.get("SAILPOINT_CA_CERT", True)

# Map mTLS Common Names to SailPoint usernames
SAILPOINT_CN_MAP = {
    "gamelib-backend":   "svc_gamelib_backend",    # SailPoint service account
    "gamelib-analytics": "svc_gamelib_analytics",
}

# Enable IAM enforcement
XML_BRIDGE_IAM_ENABLED  = os.environ.get("XML_BRIDGE_IAM_ENABLED", "false").lower() == "true"
XML_BRIDGE_IDENTITY_CN  = "gamelib-backend"
```

-----

## The Linux Server Side: Verifying the Caller 🖥️

The Linux server can also call SailPoint to verify the caller’s identity. The Nginx `$ssl_client_s_dn` variable (forwarded as `X-SSL-Client-CN` header) provides the certificate CN.

Example Python handler on the Linux server side:

```python
# linux_server/xml_handler.py (simplified Flask/FastAPI handler)
import os, requests
from flask import Flask, request, abort

app = Flask(__name__)

SAILPOINT_BASE_URL = os.environ["SAILPOINT_BASE_URL"]
SAILPOINT_TOKEN_URL = f"{SAILPOINT_BASE_URL}/oauth/token"

def check_caller_identity(cn: str, required_entitlement: str) -> bool:
    """Ask SailPoint if the caller (identified by CN) is authorised."""
    # Get OAuth token
    token_resp = requests.post(
        SAILPOINT_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id":  os.environ["SAILPOINT_CLIENT_ID"],
            "client_secret": os.environ["SAILPOINT_CLIENT_SECRET"],
        }
    )
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Look up the identity
    user_resp = requests.get(
        f"{SAILPOINT_BASE_URL}/scim/v2/Users",
        params={"filter": f'userName eq "{cn}"'},
        headers=headers,
    )
    users = user_resp.json().get("Resources", [])
    if not users or not users[0].get("active", False):
        return False

    # Check entitlement (simplified — real implementation would check roles)
    user_id = users[0]["id"]
    detail = requests.get(
        f"{SAILPOINT_BASE_URL}/scim/v2/Users/{user_id}",
        params={"attributes": "roles"},
        headers=headers,
    ).json()
    role_names = [r.get("display", "") for r in detail.get("roles", [])]
    return required_entitlement in role_names


@app.post("/catalogue/update")
def receive_catalogue_update():
    # mTLS client CN is forwarded by Nginx as a header
    client_cn = request.headers.get("X-SSL-Client-CN", "")
    if not client_cn:
        abort(403, "No client certificate CN.")

    if not check_caller_identity(client_cn, "catalogue_update"):
        abort(403, f"Identity '{client_cn}' not authorised for catalogue_update.")

    xml_data = request.data
    # ... process the XML ...
    return {"status": "ok", "bytes_received": len(xml_data)}
```

-----

## The Zero-Trust Flow: End to End 🔒

```
Django BridgeClient
    │
    ├── 1. _check_authorisation("catalogue_update")
    │        └── IAMClient.is_service_account_authorised("gamelib-backend", "catalogue_update")
    │                └── SCIM GET /Users?filter=userName eq "svc_gamelib_backend"
    │                └── Check roles → "catalogue_update" present? ✓
    │
    ├── 2. requests.post("https://linux-srv.internal:8443/catalogue/update", ...)
    │        └── TLS: server cert verified against ca.crt ✓
    │        └── mTLS: client cert (client.crt) presented ✓
    │        └── mTLS: Linux Nginx verifies client.crt against ca.crt ✓
    │
    └── 3. Linux server XML handler
             ├── Read X-SSL-Client-CN = "gamelib-backend"
             ├── SCIM query to SailPoint: "gamelib-backend" has catalogue_update? ✓
             └── Process XML → return HTTP 200
```

Three independent verification layers:

1. SailPoint IAM confirms the identity is authorised (business-level)
1. TLS confirms the server is genuine (server authentication)
1. mTLS confirms the client is genuine (client authentication)

-----

In **Episode 9**, we build the full PKI infrastructure that manages all of this: the CA hierarchy, the `django-ca` application, certificate rotation, CRL publication, and OCSP responses — the key factory that makes all locks.

-----

**🔗 Resources**

- **SailPoint developer portal**: [developer.sailpoint.com](https://developer.sailpoint.com)
- **SailPoint SCIM API (IIQ)**: [developer.sailpoint.com/docs/api/iiq](https://developer.sailpoint.com/docs/api/iiq/)
- **IdentityNow v2025 API**: [developer.sailpoint.com/docs/api/v2025](https://developer.sailpoint.com/docs/api/v2025/)
- **SCIM 2.0 RFC 7644**: [rfc-editor.org/rfc/rfc7644](https://www.rfc-editor.org/rfc/rfc7644)

-----

*🎮 Game on Djangular Series is a series about building GameLib with Django REST Framework, Angular, XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
