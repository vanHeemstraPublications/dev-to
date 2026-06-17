---
title: "REST with step-ca 🔐 Ep.8"
published: false
description: "Episode 8: The finale. All seven episodes assemble into the complete StepCAClient class. Then we go further: a Flask server protected by mTLS using step-ca certificates, the ACME provisioner as a simpler alternative to JWK, and the full production hardening checklist. A complete architecture diagram shows how every component fits together in a real deployment."
tags: [python, tls, flask, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/rest-with-step-ca-episode-08.png"
series: "REST with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 8
---

## Episode 8: The Complete Picture — Production Patterns

---

## Eight Episodes, One Class

This is the episode where everything connects. We have built `StepCAClient` piece by piece across seven episodes. Now we review the complete class, demonstrate a Flask server using step-ca certificates with mutual TLS, introduce the ACME provisioner as a simpler alternative for certain use cases, and close with a production hardening checklist.

---

## 🗂️ SIPOC — The Production System

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| `StepCAClient` | CA URL, fingerprint, provisioner config | Orchestrate all cert lifecycle operations via REST | X.509 certificates, renewal, revocation | Flask server — loads cert+key; renewal daemon refreshes them |
| Flask + `ssl` module | `cert_pem`, `key_pem` from `StepCAClient` | Configure SSLContext with step-ca-issued cert + CA as client CA | An mTLS HTTPS server that only accepts clients with valid step-ca certs | Curl, httpx clients presenting their own step-ca certs |
| ACME provisioner | An ACME client (certbot, acme.sh, Caddy, httpx-acme) | Standard ACMEv2 protocol against step-ca's ACME directory | Certificates issued through ACME without custom JWT code | Any ACME-compatible client or library |

---

## Complete System Architecture

```
PRODUCTION DEPLOYMENT WITH step-ca + StepCAClient
═══════════════════════════════════════════════════════════════════════════

   ┌──────────────────────────────────────────────────────────────────┐
   │                      PRIVATE NETWORK                            │
   │                                                                  │
   │  ┌─────────────────┐         ┌──────────────────────────────┐  │
   │  │  step-ca Server │         │   Python Services            │  │
   │  │                 │         │                              │  │
   │  │  Root CA        │         │  ┌───────────────────────┐  │  │
   │  │  (offline key   │         │  │  service-a             │  │  │
   │  │   on disk)      │         │  │                        │  │  │
   │  │                 │         │  │  StepCAClient          │  │  │
   │  │  Intermediate   │         │  │  ┌─────────────────┐  │  │  │
   │  │  CA (signs      │◄────────┼──┼──│  sign()         │  │  │  │
   │  │  end-entity     │  HTTPS  │  │  │  renew()        │  │  │  │
   │  │  certs)         │  :9000  │  │  │  revoke()       │  │  │  │
   │  │                 │         │  │  └────────┬────────┘  │  │  │
   │  │  REST API:      │         │  │           │cert       │  │  │
   │  │  /health        │         │  │  ┌────────▼────────┐  │  │  │
   │  │  /roots         │         │  │  │  Flask mTLS     │  │  │  │
   │  │  /provisioners  │         │  │  │  Server  :8443  │  │  │  │
   │  │  /1.0/sign      │         │  │  │                 │  │  │  │
   │  │  /1.0/renew     │         │  │  │  RenewalDaemon  │  │  │  │
   │  │  /1.0/revoke    │         │  │  └────────┬────────┘  │  │  │
   │  │                 │         │  └───────────┼───────────┘  │  │
   │  │  ACME endpoint: │         │              │ mTLS          │  │
   │  │  /acme/acme/    │         │  ┌───────────▼───────────┐  │  │
   │  │  directory      │         │  │  service-b client     │  │  │
   │  │                 │         │  │  (its own step-ca     │  │  │
   │  └─────────────────┘         │  │   cert as client      │  │  │
   │                               │  │   cert for mTLS)      │  │  │
   │                               │  └───────────────────────┘  │  │
   │                               └──────────────────────────────┘  │
   │                                                                  │
   │  Root CA trust:                                                  │
   │  root_ca.crt  (bootstrapped via fingerprint by every client)    │
   └──────────────────────────────────────────────────────────────────┘

   Data flow for mTLS call from service-b → service-a:
   ┌─────────────────────────────────────────────────────────────┐
   │  service-b                                  service-a       │
   │  (client)                                   (server)        │
   │  presents: its step-ca cert ─────────────►  verifies:       │
   │  verifies: service-a's step-ca cert ◄─────  presents: its   │
   │                                             step-ca cert    │
   │  Both certs signed by same CA root → mutual trust           │
   └─────────────────────────────────────────────────────────────┘
```

---

## The Complete StepCAClient — All Episodes Combined

```python
# step_ca_client.py  — complete module (all episodes assembled)
"""
StepCAClient: Python REST client for step-ca certificate authority.

Implements the full X.509 certificate lifecycle:
  sign() → renew() → revoke()

Also provides:
  health(), get_roots(), list_provisioners()
  create_key_and_csr()
  start_renewal_daemon()
"""

from __future__ import annotations

import datetime
import hashlib
import ipaddress
import json as json_module
import logging
import os
import random
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from jose import jwt as jose_jwt
from jwcrypto import jwe as jwecrypto_jwe, jwk as jwecrypto_jwk

logger = logging.getLogger(__name__)


# ── Exceptions ────────────────────────────────────────────────────────────────

class StepCAError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

class FingerprintMismatchError(StepCAError):
    pass


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Provisioner:
    name: str
    type: str
    kid:  str
    public_key:    dict
    encrypted_key: str | None
    claims:        dict = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict) -> "Provisioner":
        key = data.get("key", {})
        return cls(
            name          = data["name"],
            type          = data["type"],
            kid           = key.get("kid", ""),
            public_key    = key,
            encrypted_key = data.get("encryptedKey"),
            claims        = data.get("claims", {}),
        )


@dataclass
class IssuedCertificate:
    cert_pem:  str
    chain_pem: str
    ca_pem:    str
    key_pem:   str

    def save(self, cert_path: str, key_path: str, *, chain: bool = True,
             password: bytes | None = None) -> None:
        Path(cert_path).write_text(self.chain_pem if chain else self.cert_pem)
        if password:
            from cryptography.hazmat.primitives.serialization import (
                load_pem_private_key, Encoding, PrivateFormat, BestAvailableEncryption)
            key_obj = load_pem_private_key(self.key_pem.encode(), password=None)
            Path(key_path).write_text(
                key_obj.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL,
                                      BestAvailableEncryption(password)).decode())
        else:
            Path(key_path).write_text(self.key_pem)

    def inspect(self) -> dict:
        cert  = x509.load_pem_x509_certificate(self.cert_pem.encode())
        sans: list[str] = []
        try:
            san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            for n in san.value:
                if isinstance(n, x509.DNSName):   sans.append(f"DNS:{n.value}")
                elif isinstance(n, x509.IPAddress): sans.append(f"IP:{n.value}")
        except x509.ExtensionNotFound:
            pass
        return {
            "subject":    cert.subject.rfc4514_string(),
            "issuer":     cert.issuer.rfc4514_string(),
            "serial":     format(cert.serial_number, "x"),
            "not_before": cert.not_valid_before_utc.isoformat(),
            "not_after":  cert.not_valid_after_utc.isoformat(),
            "sans":       sans,
        }


# ── Main class ────────────────────────────────────────────────────────────────

class StepCAClient:

    REASON_UNSPECIFIED            = 0
    REASON_KEY_COMPROMISE         = 1
    REASON_CA_COMPROMISE          = 2
    REASON_AFFILIATION_CHANGED    = 3
    REASON_SUPERSEDED             = 4
    REASON_CESSATION_OF_OPERATION = 5
    REASON_CERTIFICATE_HOLD       = 6
    REASON_REMOVE_FROM_CRL        = 8
    REASON_PRIVILEGE_WITHDRAWN    = 9
    REASON_AA_COMPROMISE          = 10

    def __init__(self, ca_url: str, root_fingerprint: str,
                 provisioner_name: str, provisioner_password: str,
                 *, timeout: float = 30.0,
                 root_cert_path: str | None = None) -> None:
        self.ca_url               = ca_url.rstrip("/")
        self.root_fingerprint     = root_fingerprint.lower().replace(":", "")
        self.provisioner_name     = provisioner_name
        self.provisioner_password = provisioner_password
        self.timeout              = timeout
        self._root_cert_pem       = self._bootstrap_root(root_cert_path)
        self._root_cert_file      = tempfile.NamedTemporaryFile(
            suffix=".crt", delete=False, mode="w")
        self._root_cert_file.write(self._root_cert_pem)
        self._root_cert_file.flush()
        self._session             = httpx.Client(
            verify=self._root_cert_file.name, timeout=self.timeout)
        self._provisioner_cache:  dict | None = None
        if self.health() != "ok":
            raise StepCAError("CA health check failed")

    def _bootstrap_root(self, root_cert_path: str | None) -> str:
        if root_cert_path and Path(root_cert_path).exists():
            pem = Path(root_cert_path).read_text()
            self._verify_fingerprint(pem); return pem
        with httpx.Client(verify=False, timeout=self.timeout) as c:
            pem = c.get(f"{self.ca_url}/roots").json()["crts"][0]
        self._verify_fingerprint(pem); return pem

    def _verify_fingerprint(self, root_pem: str) -> None:
        cert = x509.load_pem_x509_certificate(root_pem.encode())
        actual = hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()
        if actual != self.root_fingerprint:
            raise FingerprintMismatchError(
                f"Fingerprint mismatch\n  Expected: {self.root_fingerprint}\n  Actual:   {actual}")

    def _raise_for_status(self, r: httpx.Response) -> None:
        if r.is_error:
            try: msg = r.json().get("message", r.text)
            except Exception: msg = r.text
            raise StepCAError(f"step-ca {r.status_code}: {msg}", r.status_code)

    # Discovery
    def health(self) -> str:
        r = self._session.get(f"{self.ca_url}/health"); self._raise_for_status(r)
        return r.json().get("status", "unknown")

    def get_roots(self) -> list[str]:
        r = self._session.get(f"{self.ca_url}/roots"); self._raise_for_status(r)
        return r.json().get("crts", [])

    def list_provisioners(self) -> list[Provisioner]:
        if self._provisioner_cache is not None:
            return list(self._provisioner_cache.values())
        provs, cursor = [], ""
        while True:
            params: dict = {"limit": 100}
            if cursor: params["cursor"] = cursor
            r = self._session.get(f"{self.ca_url}/provisioners", params=params)
            self._raise_for_status(r); data = r.json()
            provs.extend(Provisioner.from_api(p) for p in data.get("provisioners", []))
            cursor = data.get("nextCursor", "")
            if not cursor: break
        self._provisioner_cache = {p.name: p for p in provs}
        return provs

    def get_provisioner(self, name: str | None = None) -> Provisioner:
        self.list_provisioners()
        target = name or self.provisioner_name
        if target not in self._provisioner_cache:  # type: ignore
            raise StepCAError(f"Provisioner {target!r} not found")
        return self._provisioner_cache[target]  # type: ignore

    # CSR factory
    def create_key_and_csr(self, common_name: str, sans: list[str], *,
                           key_type: str = "EC", key_size: int = 2048,
                           organization: str = "", country: str = "") -> tuple:
        key = ec.generate_private_key(ec.SECP256R1()) if key_type.upper() == "EC" \
              else rsa.generate_private_key(65537, key_size)
        attrs = [x509.NameAttribute(NameOID.COMMON_NAME, common_name)]
        if organization: attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization))
        if country:      attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, country))
        san_entries = []
        for s in sans:
            try: san_entries.append(x509.IPAddress(ipaddress.ip_address(s)))
            except ValueError: san_entries.append(x509.DNSName(s))
        builder = (x509.CertificateSigningRequestBuilder()
                   .subject_name(x509.Name(attrs)))
        if san_entries:
            builder = builder.add_extension(x509.SubjectAlternativeName(san_entries), critical=False)
        builder = builder.add_extension(x509.ExtendedKeyUsage(
            [ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False)
        csr = builder.sign(key, hashes.SHA256())
        return key, csr.public_bytes(serialization.Encoding.PEM).decode()

    @staticmethod
    def private_key_to_pem(key, password: bytes | None = None) -> str:
        enc = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
        return key.private_bytes(serialization.Encoding.PEM,
                                 serialization.PrivateFormat.TraditionalOpenSSL, enc).decode()

    # Token factory
    def _get_encrypted_key(self, kid: str) -> str:
        r = self._session.get(f"{self.ca_url}/provisioners/{kid}/encrypted-key")
        self._raise_for_status(r); return r.json()["key"]

    def _decrypt_provisioner_key(self, kid: str) -> dict:
        jwe_str = self._get_encrypted_key(kid)
        import base64
        pw_b64  = base64.urlsafe_b64encode(
            self.provisioner_password.encode()).rstrip(b"=").decode()
        pw_key  = jwecrypto_jwk.JWK(kty="oct", k=pw_b64)
        token   = jwecrypto_jwe.JWE()
        token.deserialize(jwe_str, key=pw_key)
        return json_module.loads(token.payload)

    def _create_token(self, common_name: str, sans: list[str],
                      provisioner: Provisioner, *, duration_seconds: int = 300) -> str:
        now, jti = int(time.time()), str(uuid.uuid4())
        jwk      = self._decrypt_provisioner_key(provisioner.kid)
        return jose_jwt.encode(
            {"sub": common_name, "iss": provisioner.name,
             "aud": f"{self.ca_url}/1.0/sign", "iat": now,
             "exp": now + duration_seconds, "jti": jti, "sans": sans},
            jwk, algorithm=jwk.get("alg", "ES256"), headers={"kid": provisioner.kid})

    # Certificate operations
    def sign(self, common_name: str, sans: list[str], *,
             key_type: str = "EC", key_size: int = 2048,
             organization: str = "", country: str = "") -> IssuedCertificate:
        eff_sans = list(dict.fromkeys([common_name] + sans))
        prov     = self.get_provisioner()
        key, csr = self.create_key_and_csr(common_name, eff_sans, key_type=key_type,
                                            key_size=key_size, organization=organization,
                                            country=country)
        token    = self._create_token(common_name, eff_sans, prov)
        r        = self._session.post(f"{self.ca_url}/1.0/sign",
                                      json={"csr": csr, "ott": token})
        self._raise_for_status(r); data = r.json()
        chain    = data.get("certChain", [data.get("crt",""), data.get("ca","")])
        return IssuedCertificate(cert_pem=chain[0],
                                 chain_pem="".join(chain),
                                 ca_pem=chain[1] if len(chain)>1 else "",
                                 key_pem=self.private_key_to_pem(key))

    def renew(self, cert_pem: str, key_pem: str) -> IssuedCertificate:
        with (tempfile.NamedTemporaryFile(suffix=".crt", delete=False, mode="w") as cf,
              tempfile.NamedTemporaryFile(suffix=".key", delete=False, mode="w") as kf):
            cf.write(cert_pem); kf.write(key_pem)
            cp, kp = cf.name, kf.name
        try:
            s = httpx.Client(verify=self._root_cert_file.name, cert=(cp, kp), timeout=self.timeout)
            r = s.post(f"{self.ca_url}/1.0/renew"); s.close()
            self._raise_for_status(r)
        finally:
            os.unlink(cp); os.unlink(kp)
        data  = r.json()
        chain = data.get("certChain", [data.get("crt",""), data.get("ca","")])
        return IssuedCertificate(cert_pem=chain[0], chain_pem="".join(chain),
                                 ca_pem=chain[1] if len(chain)>1 else "", key_pem=key_pem)

    def revoke(self, cert_pem: str, *, reason_code: int = 0, reason: str = "",
               use_mtls: bool = False, key_pem: str | None = None) -> None:
        cert   = x509.load_pem_x509_certificate(cert_pem.encode())
        serial = format(cert.serial_number, "x")
        if use_mtls:
            if not key_pem: raise ValueError("key_pem required for mTLS revocation")
            with (tempfile.NamedTemporaryFile(suffix=".crt",delete=False,mode="w") as cf,
                  tempfile.NamedTemporaryFile(suffix=".key",delete=False,mode="w") as kf):
                cf.write(cert_pem); kf.write(key_pem); cp, kp = cf.name, kf.name
            try:
                s = httpx.Client(verify=self._root_cert_file.name,cert=(cp,kp),timeout=self.timeout)
                r = s.post(f"{self.ca_url}/1.0/revoke",
                           json={"reasonCode":reason_code,"reason":reason} or None)
                s.close(); self._raise_for_status(r)
            finally: os.unlink(cp); os.unlink(kp)
        else:
            prov = self.get_provisioner()
            jwk  = self._decrypt_provisioner_key(prov.kid)
            now  = int(time.time())
            token = jose_jwt.encode(
                {"sub":serial,"iss":prov.name,"aud":f"{self.ca_url}/1.0/revoke",
                 "iat":now,"exp":now+300,"jti":str(uuid.uuid4())},
                jwk, algorithm=jwk.get("alg","ES256"), headers={"kid":prov.kid})
            r = self._session.post(f"{self.ca_url}/1.0/revoke",
                                   json={"serial":serial,"reasonCode":reason_code,
                                         "reason":reason,"ott":token})
            self._raise_for_status(r)

    def start_renewal_daemon(self, initial_cert: IssuedCertificate, *,
                             renewal_fraction: float = 2/3,
                             on_renewal: Callable | None = None,
                             on_error: Callable | None = None) -> "RenewalDaemon":
        d = RenewalDaemon(self, initial_cert, renewal_fraction, on_renewal, on_error)
        d.start(); return d

    def get_certificate_serial(self, cert_pem: str) -> str:
        return format(x509.load_pem_x509_certificate(cert_pem.encode()).serial_number, "x")

    def __del__(self) -> None:
        try:
            self._session.close()
            os.unlink(self._root_cert_file.name)
        except Exception: pass


class RenewalDaemon:
    def __init__(self, ca, cert, fraction, on_renewal, on_error):
        self._ca=ca; self._cert=cert; self._fraction=fraction
        self._on_renewal=on_renewal; self._on_error=on_error
        self._stop=threading.Event()
        self._thread=threading.Thread(target=self._run,daemon=True,name="step-ca-renewal")
    @property
    def current_cert(self): return self._cert
    def start(self): self._thread.start()
    def stop(self): self._stop.set(); self._thread.join(timeout=5.0)
    def _run(self):
        while not self._stop.is_set():
            leaf = x509.load_pem_x509_certificate(self._cert.cert_pem.encode())
            lifetime = (leaf.not_valid_after_utc - leaf.not_valid_before_utc).total_seconds()
            renew_at = leaf.not_valid_before_utc.timestamp() + lifetime * self._fraction
            sleep    = max(0, renew_at - time.time()) * (1 + 0.1*(random.random()*2-1))
            self._stop.wait(timeout=sleep)
            if self._stop.is_set(): break
            for attempt in range(1, 6):
                try:
                    self._cert = self._ca.renew(self._cert.cert_pem, self._cert.key_pem)
                    if self._on_renewal:
                        try: self._on_renewal(self._cert)
                        except Exception: pass
                    break
                except Exception as exc:
                    if self._on_error:
                        try: self._on_error(exc)
                        except Exception: pass
                    self._stop.wait(timeout=60*(2**(attempt-1)))
```

---

## Flask Server with mTLS Using step-ca Certificates

```python
# flask_mtls_server.py

import ssl
import tempfile
import threading
import os
from flask import Flask, request, jsonify
from step_ca_client import StepCAClient

app = Flask(__name__)
_cert: "IssuedCertificate" = None  # type: ignore
_daemon = None

@app.route("/api/hello")
def hello():
    # In mTLS mode: the client cert subject is available via the SSL context
    # (requires a custom request handler or middleware to extract it)
    return jsonify({"message": "Hello from mTLS-protected service!",
                    "server": "myservice.internal"})

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


def start_mtls_server(ca: StepCAClient) -> None:
    global _cert, _daemon

    # Get a certificate for this server
    _cert = ca.sign(
        "myservice.internal",
        sans=["myservice.internal", "127.0.0.1"],
    )

    # Start renewal daemon — keeps cert fresh automatically
    def on_renewal(new_cert):
        global _cert
        _cert = new_cert
        # In production: reload the SSL context or restart the listener
        # For simplicity here we just update the reference
        _cert.save("/tmp/server.crt", "/tmp/server.key")

    _daemon = ca.start_renewal_daemon(_cert, on_renewal=on_renewal)
    _cert.save("/tmp/server.crt", "/tmp/server.key")

    # Build the SSL context
    # SSLContext.PROTOCOL_TLS_SERVER sets up a TLS server
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("/tmp/server.crt", "/tmp/server.key")

    # For mTLS: require client certificates verified against the root CA
    context.verify_mode = ssl.CERT_REQUIRED
    # Write root CA to a temp file for the SSL context
    root_pem = ca._root_cert_pem  # the verified root from bootstrap
    with tempfile.NamedTemporaryFile(suffix=".crt", delete=False, mode="w") as f:
        f.write(root_pem)
        root_path = f.name
    context.load_verify_locations(root_path)
    os.unlink(root_path)

    print("Starting mTLS server on https://127.0.0.1:8443")
    app.run(
        host    = "127.0.0.1",
        port    = 8443,
        ssl_context = context,
        debug   = False,
    )


# ── Making an mTLS request with httpx ────────────────────────────────────────

def call_with_mtls(ca: StepCAClient, server_url: str) -> dict:
    """Call the mTLS server using a client certificate from step-ca."""
    # Get a client certificate
    client_cert = ca.sign(
        "client.internal",
        sans=["client.internal"],
    )

    with tempfile.NamedTemporaryFile(suffix=".crt",delete=False,mode="w") as cf, \
         tempfile.NamedTemporaryFile(suffix=".key",delete=False,mode="w") as kf:
        cf.write(client_cert.chain_pem)
        kf.write(client_cert.key_pem)
        cp, kp = cf.name, kf.name

    try:
        # Write root CA for server verification
        with tempfile.NamedTemporaryFile(suffix=".crt",delete=False,mode="w") as rf:
            rf.write(ca._root_cert_pem); rp = rf.name

        r = httpx.get(
            f"{server_url}/api/hello",
            verify = rp,     # trust only our CA root
            cert   = (cp, kp),  # present our client cert
        )
        return r.json()
    finally:
        for p in [cp, kp, rp]: os.unlink(p)
```

---

## The ACME Alternative

For services that use standard ACME clients (certbot, Caddy, cert-manager), step-ca's ACME provisioner is often simpler than the JWK flow — no custom JWT code needed.

```bash
# Add an ACME provisioner to step-ca
step ca provisioner add acme --type ACME

# Verify the ACME directory is live
curl https://localhost:9000/acme/acme/directory

# Use certbot against your step-ca ACME endpoint
certbot certonly \
  --standalone \
  --server https://localhost:9000/acme/acme/directory \
  --no-verify-ssl \
  -d myservice.internal
```

```python
# Python ACME client against step-ca (using the acme library)
# pip install acme

from acme import client, challenges, crypto_util, messages
from cryptography.hazmat.primitives.asymmetric import ec
import josepy

# Generate an ACME account key
account_key = ec.generate_private_key(ec.SECP256R1())
account_jwk = josepy.JWKEC(key=account_key)

# Connect to the step-ca ACME directory
# Note: verify=False only for dev — in prod use the root_ca.crt
acme_client = client.ClientV2(
    directory = client.ClientNetwork.from_directory(
        "https://localhost:9000/acme/acme/directory",
        account_key = account_jwk,
        verify_ssl  = False,  # dev only
    ),
    net = client.ClientNetwork(account_jwk, verify_ssl=False),
)

# For production: point your ACME client at your step-ca;
# the ACME protocol handles auth automatically via http-01/dns-01
```

---

## Production Hardening Checklist

```
STEP-CA + STEPCA CLIENT PRODUCTION CHECKLIST
═════════════════════════════════════════════════════════════════

step-ca Server:
  [✓] Run as non-root user with minimal filesystem access
  [✓] Root CA key in HSM or KMS (not on-disk in production)
  [✓] Use POSTGRES or MySQL backend (not BadgerDB) for HA
  [✓] Enable TLS 1.2+ only; disable old cipher suites
  [✓] Set short default cert lifetime (24h or less)
  [✓] Set maxTLSCertDuration per provisioner to limit exposure
  [✓] Enable audit logging; ship logs to SIEM
  [✓] Network-isolate: only CA-authorised services can reach :9000
  [✓] Monitor: alert on cert issuance anomalies, failed renewals

StepCAClient in your application:
  [✓] Store provisioner_password in a secrets manager (Vault, AWS SSM)
      Never hardcode or commit to version control
  [✓] Store root_fingerprint in config (not from an untrusted source)
  [✓] Use a dedicated JWK provisioner per application/environment
      (not the default admin@ provisioner)
  [✓] Set maxTLSCertDuration for each provisioner to match your renewal daemon
  [✓] Start renewal daemon on application startup; log renewal events
  [✓] Handle RenewalDaemon errors: alert + page on repeated failure
  [✓] Revoke certs on service shutdown or key rotation
  [✓] Never log key_pem — treat it like a password
  [✓] Use PKCS#11 or cloud KMS for key generation in high-security contexts
  [✓] Test: mock the CA endpoints in unit tests; integration-test with a real CA

For mTLS:
  [✓] Validate client cert's CN/SANs in your application logic
  [✓] Do not rely solely on TLS-layer mTLS for access control
      Add application-level authz (JWT, OPA, etc.) for fine-grained control
```

---

## The Series: Eight Episodes, Complete

| # | Episode | What We Built | Key Methods |
|---|---|---|---|
| 1 | The CA That Answers HTTP Calls | Foundation, Docker, API overview | Docker setup |
| 2 | First Contact | Trust bootstrap, verified session | `__init__`, `health()`, `get_roots()`, `list_provisioners()` |
| 3 | Generating the CSR | Key + CSR factory | `create_key_and_csr()`, `inspect_csr()` |
| 4 | The Token Factory | JWE decrypt + JWT signing | `_decrypt_provisioner_key()`, `_create_token()` |
| 5 | Sign Here | Full certificate issuance | `sign()`, `IssuedCertificate` |
| 6 | Still Breathing | mTLS renewal + daemon | `renew()`, `start_renewal_daemon()`, `RenewalDaemon` |
| 7 | Taking Back the Key | Both revocation methods | `revoke()` (JWT + mTLS) |
| 8 | *This one* — The Complete Picture | Assembly + Flask mTLS + ACME + production | Full class listing |

The complete `StepCAClient` class is the thread running through the entire series. Each episode added one layer. The final class is straightforward: bootstrap trust, discover provisioners, generate keys, sign JWTs, POST to the CA, manage the lifecycle.

REST with step-ca. No CLI required.

---

**🔗 Resources**
- **step-ca GitHub**: [github.com/smallstep/certificates](https://github.com/smallstep/certificates)
- **step-ca documentation**: [smallstep.com/docs/step-ca](https://smallstep.com/docs/step-ca/)
- **Smallstep client examples**: [github.com/smallstep/clients](https://github.com/smallstep/clients)
- **Practical Zero Trust (Smallstep book)**: [smallstep.com/docs/practical-zero-trust](https://smallstep.com/docs/practical-zero-trust/)
- **mTLS with Python**: [smallstep.com/docs/mtls](https://smallstep.com/docs/mtls/)

---

*🔐 REST with step-ca — eight episodes, one Python class, complete certificate lifecycle.*
