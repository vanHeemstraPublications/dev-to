---
title: "REST with step-ca 🔐 Ep.2"
published: false
description: "Episode 2: Before any certificate can be issued, the client must establish trust with the CA. This episode builds the StepCAClient constructor — bootstrapping from a root fingerprint, downloading and pinning the root certificate, configuring an httpx session that verifies every TLS connection, and implementing the three read-only discovery endpoints: health, roots, and provisioners."
tags: [python, security, tls, certificates]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/rest-with-step-ca-episode-02.png"
series: "REST with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

## Episode 2: First Contact — Trust, Health, and Provisioners

---

## The Trust Bootstrap Problem

Every TLS connection requires the client to verify the server's certificate. For a public CA like Let's Encrypt, this is automatic — your OS ships with their root in its trust store. For a private CA like step-ca, no operating system trusts it by default. You must establish that trust explicitly.

step-ca solves this with a **root fingerprint**: a SHA-256 hash of the root certificate's DER bytes. If you know the fingerprint and the CA URL, you can securely download the root certificate and verify it before trusting anything else the CA says. The fingerprint is short enough to transmit out of band (email, Slack, a config file), but cryptographically strong enough to guarantee authenticity.

Our `StepCAClient` constructor performs this bootstrap automatically.

---

## 🗂️ SIPOC — Trust Bootstrap and Discovery

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| step-ca server | `GET /roots` response over HTTPS (unverified TLS on first call) | Download root cert PEM; compute SHA-256 of DER; compare to known fingerprint | Verified root certificate stored in memory | `httpx.Client` — which uses the root cert to verify all future connections |
| `httpx` library | Root cert PEM, CA URL | Create `httpx.Client` with `verify=root_cert_path` | An HTTPS client that verifies all step-ca connections | All subsequent API methods in `StepCAClient` |
| `GET /provisioners` endpoint | Verified HTTPS session | Fetch provisioner list; find provisioner by name; extract `kid` and `encryptedKey` | Provisioner metadata dict | Episode 4 — token factory needs `kid` and `encryptedKey` |

---

## Trust Bootstrap Architecture

```
BOOTSTRAP SEQUENCE
══════════════════════════════════════════════════════════════

  Developer/Config                StepCAClient                  step-ca
  ──────────────────              ────────────────              ────────

  Provide:                        1. GET /roots
    ca_url ─────────────────────►    (TLS unverified — one-time only)
    root_fingerprint             ◄── {"crts":["-----BEGIN CERT...-----"]}

                                  2. Verify fingerprint
                                     SHA256(DER(root_cert))
                                     == provided fingerprint?
                                     NO  → raise SecurityError
                                     YES → store root cert ✓

                                  3. Create httpx.Client
                                     verify = root_cert_path
                                     ┌─────────────────────┐
                                     │ ALL subsequent calls │
                                     │ verified against     │
                                     │ this root cert       │
                                     └─────────────────────┘

                                  4. GET /health
                                     (TLS now verified!)
                                  ◄── {"status":"ok"}

  Constructor returns             StepCAClient instance
  ready to use        ◄──────────  with verified session
```

After bootstrap, every HTTP call the client makes is protected by the verified root. The unverified first call is intentional and safe because the fingerprint check catches any tampering.

---

## The StepCAClient Skeleton

```python
# step_ca_client.py
"""
StepCAClient — a Python REST client for step-ca.

Covers the full X.509 certificate lifecycle:
  sign → renew → revoke

Built episode by episode across this series.
Each episode adds methods; the class is cumulative.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import ssl
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

logger = logging.getLogger(__name__)


class StepCAError(Exception):
    """Raised when step-ca returns an error response."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class FingerprintMismatchError(StepCAError):
    """Raised when the downloaded root cert does not match the expected fingerprint."""


@dataclass
class Provisioner:
    """Metadata for a single step-ca provisioner."""
    name:          str
    type:          str
    kid:           str
    public_key:    dict         # JWK public key (for JWT verification by the CA)
    encrypted_key: str | None   # JWE-encrypted private key (for us to decrypt)
    claims:        dict = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict) -> "Provisioner":
        key_data = data.get("key", {})
        return cls(
            name          = data["name"],
            type          = data["type"],
            kid           = key_data.get("kid", ""),
            public_key    = key_data,
            encrypted_key = data.get("encryptedKey"),
            claims        = data.get("claims", {}),
        )


class StepCAClient:
    """
    REST client for step-ca certificate operations.

    Usage:
        ca = StepCAClient(
            ca_url              = "https://localhost:9000",
            root_fingerprint    = "702a094e239c...",
            provisioner_name    = "admin@example.com",
            provisioner_password= "provisioner-secret",
        )
        cert_pem, key_pem = ca.sign("myservice.internal",
                                     sans=["myservice.internal"])
    """

    def __init__(
        self,
        ca_url:               str,
        root_fingerprint:     str,
        provisioner_name:     str,
        provisioner_password: str,
        *,
        timeout:              float = 30.0,
        root_cert_path:       str | None = None,
    ) -> None:
        """
        Bootstrap trust and create a verified HTTPS session.

        Args:
            ca_url:               Full URL of the CA, e.g. "https://localhost:9000"
            root_fingerprint:     SHA-256 hex fingerprint of the root CA certificate
            provisioner_name:     Name of the JWK provisioner (e.g. "admin@example.com")
            provisioner_password: Password to decrypt the provisioner's JWK private key
            timeout:              Request timeout in seconds
            root_cert_path:       Optional: path to an already-downloaded root cert
                                  (skips the bootstrap GET /roots call)
        """
        self.ca_url              = ca_url.rstrip("/")
        self.root_fingerprint    = root_fingerprint.lower().replace(":", "")
        self.provisioner_name    = provisioner_name
        self.provisioner_password = provisioner_password
        self.timeout             = timeout

        # Step 1: Get and verify the root certificate
        self._root_cert_pem: str = self._bootstrap_root(root_cert_path)

        # Step 2: Write root cert to a temp file for httpx
        self._root_cert_file = tempfile.NamedTemporaryFile(
            suffix=".crt", delete=False, mode="w"
        )
        self._root_cert_file.write(self._root_cert_pem)
        self._root_cert_file.flush()

        # Step 3: Create verified HTTPS session
        self._session: httpx.Client = httpx.Client(
            verify  = self._root_cert_file.name,
            timeout = self.timeout,
        )

        # Step 4: Verify the CA is reachable
        self._provisioner_cache: dict[str, Provisioner] | None = None
        status = self.health()
        if status != "ok":
            raise StepCAError(f"CA health check returned unexpected status: {status!r}")

        logger.info("StepCAClient initialised; CA at %s is healthy", self.ca_url)

    # ── Trust bootstrap ───────────────────────────────────────────────────

    def _bootstrap_root(self, root_cert_path: str | None) -> str:
        """
        Download the root certificate and verify its fingerprint.
        If root_cert_path is provided and exists, load from disk instead.
        """
        if root_cert_path and Path(root_cert_path).exists():
            logger.debug("Loading root cert from %s", root_cert_path)
            root_pem = Path(root_cert_path).read_text()
            self._verify_fingerprint(root_pem)
            return root_pem

        logger.debug("Bootstrapping root cert from %s/roots", self.ca_url)

        # This one request uses verify=False — intentional bootstrap exception
        # Safety: the fingerprint check immediately after catches any tampering
        with httpx.Client(verify=False, timeout=self.timeout) as unverified:
            response = unverified.get(f"{self.ca_url}/roots")
            response.raise_for_status()

        data = response.json()
        # The API returns a list; we use the first (usually the only) root
        root_pem: str = data["crts"][0]

        self._verify_fingerprint(root_pem)
        return root_pem

    def _verify_fingerprint(self, root_pem: str) -> None:
        """
        Verify that the root certificate's SHA-256 fingerprint matches
        the expected fingerprint provided at construction time.

        Raises:
            FingerprintMismatchError: if the fingerprints do not match
        """
        cert = x509.load_pem_x509_certificate(root_pem.encode())
        der  = cert.public_bytes(serialization.Encoding.DER)
        actual_fingerprint = hashlib.sha256(der).hexdigest()

        if actual_fingerprint != self.root_fingerprint:
            raise FingerprintMismatchError(
                f"Root certificate fingerprint mismatch!\n"
                f"  Expected: {self.root_fingerprint}\n"
                f"  Actual:   {actual_fingerprint}\n"
                f"The CA may have been tampered with, or the fingerprint is wrong."
            )

        logger.debug("Root fingerprint verified: %s", actual_fingerprint)

    # ── Discovery endpoints ───────────────────────────────────────────────

    def health(self) -> str:
        """
        GET /health
        Returns the CA status string ("ok" if healthy).
        """
        response = self._session.get(f"{self.ca_url}/health")
        self._raise_for_status(response)
        return response.json().get("status", "unknown")

    def get_roots(self) -> list[str]:
        """
        GET /roots
        Returns a list of root CA certificates in PEM format.
        """
        response = self._session.get(f"{self.ca_url}/roots")
        self._raise_for_status(response)
        return response.json().get("crts", [])

    def list_provisioners(self, *, limit: int = 100) -> list[Provisioner]:
        """
        GET /provisioners
        Returns all provisioners configured in the CA.
        Results are cached for the lifetime of the client.
        """
        if self._provisioner_cache is not None:
            return list(self._provisioner_cache.values())

        provisioners: list[Provisioner] = []
        cursor = ""

        while True:
            params: dict = {"limit": limit}
            if cursor:
                params["cursor"] = cursor

            response = self._session.get(
                f"{self.ca_url}/provisioners", params=params
            )
            self._raise_for_status(response)
            data = response.json()

            provisioners.extend(
                Provisioner.from_api(p)
                for p in data.get("provisioners", [])
            )

            cursor = data.get("nextCursor", "")
            if not cursor:
                break

        self._provisioner_cache = {p.name: p for p in provisioners}
        logger.debug("Loaded %d provisioner(s)", len(provisioners))
        return provisioners

    def get_provisioner(self, name: str | None = None) -> Provisioner:
        """
        Find a specific provisioner by name.
        Defaults to the provisioner_name provided at construction.
        """
        target = name or self.provisioner_name
        self.list_provisioners()   # populates cache

        provisioner = self._provisioner_cache.get(target)  # type: ignore[union-attr]
        if not provisioner:
            available = ", ".join(self._provisioner_cache.keys())  # type: ignore
            raise StepCAError(
                f"Provisioner {target!r} not found. "
                f"Available: {available}"
            )
        return provisioner

    # ── Internal helpers ──────────────────────────────────────────────────

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Raise StepCAError if the response indicates an error."""
        if response.is_error:
            try:
                detail = response.json()
                message = detail.get("message", response.text)
            except Exception:
                message = response.text
            raise StepCAError(
                f"step-ca error {response.status_code}: {message}",
                status_code=response.status_code,
            )

    def __del__(self) -> None:
        """Clean up the temporary root cert file on GC."""
        try:
            self._session.close()
            if hasattr(self, "_root_cert_file"):
                os.unlink(self._root_cert_file.name)
        except Exception:
            pass
```

---

## Using the Client: First Contact

```python
# first_contact.py
from step_ca_client import StepCAClient, FingerprintMismatchError

# Construct — this bootstraps trust and checks health automatically
try:
    ca = StepCAClient(
        ca_url               = "https://localhost:9000",
        root_fingerprint     = "702a094e239c9eec6f0dcd0a5f65e595bf7ed6614012825c5fe3d1ae1b2fd6ee",
        provisioner_name     = "admin@example.com",
        provisioner_password = "provisioner-secret",
    )
except FingerprintMismatchError as e:
    print(f"Security alert: {e}")
    raise SystemExit(1)

# Health check
status = ca.health()
print(f"CA status: {status}")   # "ok"

# List provisioners
provisioners = ca.list_provisioners()
for p in provisioners:
    print(f"  {p.type:6s}  {p.name:40s}  kid={p.kid[:12]}...")

# Example output:
#   JWK    admin@example.com                         kid=udaECquW2dYw...

# Fetch just our provisioner
prov = ca.get_provisioner()
print(f"\nUsing provisioner: {prov.name}")
print(f"  kid:          {prov.kid}")
print(f"  has key:      {prov.encrypted_key is not None}")
print(f"  cert max dur: {prov.claims.get('maxTLSCertDuration', 'default')}")
```

---

## The Provisioner Response Anatomy

```
GET /provisioners response

{
  "provisioners": [
    {
      "type":   "JWK",             ← Provisioner type
      "name":   "admin@example.com",  ← Human-readable name / issuer
      "key": {
        "use":  "sig",             ← Usage: signature
        "kty":  "EC",              ← Key type: Elliptic Curve
        "kid":  "udaECquW2dYw",   ← Key ID (used in URL)
        "crv":  "P-256",          ← Curve: NIST P-256
        "alg":  "ES256",          ← Algorithm: ECDSA + SHA-256
        "x":    "Pn_JEpI...",     ← Public key X component
        "y":    "_x7Jjfw..."      ← Public key Y component
                                   (no "d" field — this is PUBLIC only)
      },
      "encryptedKey": "eyJhbGci...",  ← JWE-encrypted PRIVATE key
                                         (Episode 4 decrypts this)
      "claims": {
        "minTLSCertDuration":     "5m",
        "maxTLSCertDuration":     "24h",
        "defaultTLSCertDuration": "24h"
      }
    }
  ],
  "nextCursor": ""   ← Pagination cursor (empty = no more pages)
}
```

---

## Installing Dependencies

```bash
pip install httpx cryptography python-jose jwcrypto
```

```toml
# pyproject.toml
[project]
name = "step-ca-client"
requires-python = ">=3.11"

dependencies = [
    "httpx>=0.27",           # HTTP client with TLS verify support
    "cryptography>=42",      # CSR generation, cert parsing
    "python-jose[cryptography]>=3.3",  # JWT encoding with EC keys
    "jwcrypto>=1.5",         # JWE decryption for provisioner key
]
```

---

## Testing the Bootstrap

```python
# tests/test_bootstrap.py
from unittest.mock import patch, MagicMock
import hashlib
import pytest
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID
import datetime

def make_self_signed_pem() -> tuple[str, str]:
    """Generate a self-signed cert and return (pem, fingerprint)."""
    key  = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Test CA")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    pem = cert.public_bytes(serialization.Encoding.PEM).decode()
    der = cert.public_bytes(serialization.Encoding.DER)
    fingerprint = hashlib.sha256(der).hexdigest()
    return pem, fingerprint


def test_fingerprint_mismatch_raises():
    """A wrong fingerprint must be rejected immediately."""
    from step_ca_client import StepCAClient, FingerprintMismatchError

    pem, _correct = make_self_signed_pem()

    with patch("httpx.Client") as mock_client_cls:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"crts": [pem]}
        mock_resp.raise_for_status.return_value = None
        mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_resp

        with pytest.raises(FingerprintMismatchError):
            StepCAClient(
                ca_url               = "https://fake.ca:9000",
                root_fingerprint     = "deadbeef" * 8,   # wrong fingerprint
                provisioner_name     = "test@example.com",
                provisioner_password = "pass",
            )


def test_correct_fingerprint_succeeds():
    """The correct fingerprint must allow bootstrap to proceed."""
    from step_ca_client import StepCAClient

    pem, fingerprint = make_self_signed_pem()

    with patch("httpx.Client") as mock_client_cls, \
         patch("step_ca_client.StepCAClient.health", return_value="ok"):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"crts": [pem]}
        mock_resp.raise_for_status.return_value = None
        mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_resp

        # Should not raise
        ca = StepCAClient(
            ca_url               = "https://fake.ca:9000",
            root_fingerprint     = fingerprint,
            provisioner_name     = "test@example.com",
            provisioner_password = "pass",
        )
        assert ca is not None
```

---

## What's Next: Building the CSR Factory

In **Episode 3**, we add `create_key_and_csr()` — the method that generates an EC or RSA private key and a matching PKCS#10 Certificate Signing Request using the `cryptography` library. Subject DN, Subject Alternative Names, key usage extensions — all configurable, all staying in memory until you explicitly write them to disk.

---

**🔗 Resources**
- **httpx documentation**: [www.python-httpx.org](https://www.python-httpx.org)
- **cryptography library**: [cryptography.io](https://cryptography.io)
- **step-ca provisioners**: [smallstep.com/docs/step-ca/provisioners](https://smallstep.com/docs/step-ca/provisioners/)
- **JWK specification (RFC 7517)**: [rfc-editor.org/rfc/rfc7517](https://www.rfc-editor.org/rfc/rfc7517)

---

*🔐 REST with step-ca — automating certificate lifecycle one HTTP call at a time.*
