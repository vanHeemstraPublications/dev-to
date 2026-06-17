---
title: "REST with step-ca 🔐 Ep.7"
published: false
description: "Episode 7: Sometimes a certificate must be cancelled before it expires — a compromised key, a decommissioned service, a security incident. This episode implements revoke() covering both revocation methods: JWT-based (with a one-time token) and mTLS-based (presenting the cert to be revoked). A certificate lifecycle state machine diagram shows where revocation fits in the full picture."
tags: [python, security, certificates, tls]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/rest-with-step-ca-episode-07.png"
series: "REST with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

## Episode 7: Taking Back the Key — Revocation

---

## When a Certificate Must Die Early

Short-lived certificates are step-ca's primary defence against long-term credential misuse — a 24-hour cert that expires naturally is safer than a 2-year cert that needs active revocation infrastructure. But "passive revocation" (just wait for it to expire) is not always acceptable:

- A private key is compromised or stolen
- A service is decommissioned mid-lifecycle
- A security incident requires immediate invalidation
- A certificate was issued in error

For these cases, step-ca supports active revocation via `POST /1.0/revoke`. The endpoint accepts two authentication modes: a JWT token (same provisioner flow as signing) or mTLS (presenting the certificate itself).

---

## 🗂️ SIPOC — Certificate Revocation

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| `POST /1.0/revoke` | `{serial, reasonCode, reason, ott}` OR mTLS client cert | CA validates auth; marks cert as revoked in database | `{"status":"ok"}` | The audit trail; any future renew or sign attempt for this cert |
| JWT method | Serial number, reason code, provisioner token | Same token flow as signing, but different payload | A JWT authorising the revocation of a specific serial | `/1.0/revoke` endpoint |
| mTLS method | The certificate to be revoked + its private key | Present cert as TLS client cert; no body needed | Authenticated revocation without needing the provisioner key | Useful when the cert holder wants to revoke its own cert |

---

## Certificate Lifecycle State Machine

```
X.509 CERTIFICATE LIFECYCLE IN step-ca
═══════════════════════════════════════════════════════════════════════

         ┌─────────────────────────────────────┐
         │             REQUESTED               │
         │  Key + CSR generated locally        │
         │  JWT token created                  │
         │  POST /1.0/sign pending             │
         └─────────────────┬───────────────────┘
                           │  POST /1.0/sign → 200 OK
                           ▼
         ┌─────────────────────────────────────┐
         │               ACTIVE                │◄──────────────────┐
         │  Certificate issued and in use      │                   │
         │  Presented to TLS clients           │                   │
         │  Daemon monitors expiry             │                   │
         └─────────────┬──────────────┬────────┘                   │
                       │              │                            │
           2/3 lifetime│              │ Key compromise,            │
           elapsed     │              │ decommission,              │
                       │              │ security incident          │
                       ▼              ▼                            │
         ┌─────────────────┐  ┌───────────────────────────┐       │
         │   RENEWING      │  │       REVOKED              │       │
         │                 │  │                            │       │
         │ POST /1.0/renew │  │ POST /1.0/revoke           │       │
         │ (mTLS)          │  │ (JWT or mTLS)              │       │
         │                 │  │                            │       │
         │ Returns fresh   │  │ step-ca records serial     │       │
         │ certificate     │  │ in revocation database     │       │
         └────────┬────────┘  │                            │       │
                  │           │ Future renewals fail        │       │
                  │           │ Introspection returns       │       │
                  │           │ "revoked"                  │       │
                  │           └───────────────────────────┘        │
                  │                                                 │
                  └─────────────────────────────────────────────────┘
                                  (back to ACTIVE with new cert)

         ┌─────────────────────────────────────┐
         │              EXPIRED                │
         │  not_after timestamp has passed     │
         │  Certificate no longer accepted     │
         │  by TLS clients                     │
         │  (passive revocation for 24h certs) │
         └─────────────────────────────────────┘
```

---

## Revocation Reason Codes

RFC 5280 defines these reason codes for X.509 certificate revocation:

```
REVOCATION REASON CODES (RFC 5280 Section 5.3.1)

  Code   Name                     When to use
  ────   ──────────────────────   ─────────────────────────────────────────
  0      unspecified              General revocation; no specific reason given
  1      keyCompromise            Private key was or is suspected to be stolen
  2      cACompromise             The CA's key was compromised (use with caution)
  3      affiliationChanged       Subject changed org/department/name
  4      superseded               A new certificate replaces this one
  5      cessationOfOperation     Service or entity no longer needs the cert
  6      certificateHold          Temporarily suspended (not permanent revocation)
  8      removeFromCRL            Used only with hold: unhold the certificate
  9      privilegeWithdrawn       Subject lost the privilege that warranted the cert
  10     aACompromise             Attribute Authority compromise

  Most common in practice:
    1 (keyCompromise)    ← key was stolen or leaked
    4 (superseded)       ← rotation: new cert replaces old
    5 (cessationOfOperation) ← service decommissioned
```

---

## Revocation Method Comparison

```
METHOD COMPARISON: JWT vs mTLS REVOCATION
═══════════════════════════════════════════════════════════════

JWT Method:                           mTLS Method:
───────────────────────────────────   ───────────────────────────────────
Authentication: JWT signed with       Authentication: the cert+key
provisioner private key               presented as TLS client cert

Needs: provisioner password           Needs: the cert to revoke + its key
       + serial number of cert                (no provisioner password)

When to use:                          When to use:
• Revoking from an admin service      • Self-revocation by cert holder
• Revoking a cert whose key is        • The cert holder initiates revocation
  not available                       • More granular access control
• Batch revocation operations         • The service revokes on shutdown

Security note:                        Security note:
• Anyone with provisioner key can     • Only the cert holder can revoke
  revoke any cert from that CA        • No provisioner key access needed
• Requires careful key management     • Requires holding the private key

Endpoint body:                        Endpoint body:
{                                     (empty body)
  "serial": "1234abc...",
  "reasonCode": 1,
  "reason": "Key compromised",
  "ott": "eyJhbGci..."
}
```

---

## Adding revoke() to StepCAClient

```python
# step_ca_client.py  (additions — revocation)

from cryptography.x509 import load_pem_x509_certificate


class StepCAClient:
    # ... (existing methods from Episodes 2–6)

    # ── Revocation ────────────────────────────────────────────────────────

    REASON_UNSPECIFIED              = 0
    REASON_KEY_COMPROMISE           = 1
    REASON_CA_COMPROMISE            = 2
    REASON_AFFILIATION_CHANGED      = 3
    REASON_SUPERSEDED               = 4
    REASON_CESSATION_OF_OPERATION   = 5
    REASON_CERTIFICATE_HOLD         = 6
    REASON_REMOVE_FROM_CRL          = 8
    REASON_PRIVILEGE_WITHDRAWN      = 9
    REASON_AA_COMPROMISE            = 10

    def revoke(
        self,
        cert_pem:    str,
        *,
        reason_code: int  = 0,
        reason:      str  = "",
        use_mtls:    bool = False,
        key_pem:     str | None = None,
    ) -> None:
        """
        Revoke a certificate.

        Two modes:
          JWT mode (use_mtls=False, default):
            Authenticates with a provisioner JWT token.
            Requires the provisioner password (set at construction).
            Only needs the cert_pem (to extract the serial number).

          mTLS mode (use_mtls=True):
            Authenticates by presenting the cert+key as TLS client cert.
            Does not require the provisioner password.
            Requires both cert_pem AND key_pem.

        Args:
            cert_pem:    PEM of the certificate to revoke
            reason_code: RFC 5280 reason code (0–10; see class constants)
            reason:      Human-readable reason string (for audit logs)
            use_mtls:    If True, use mTLS authentication (key_pem required)
            key_pem:     Private key PEM — required only for mTLS mode

        Raises:
            StepCAError: if revocation fails (e.g. cert already revoked)
            ValueError:  if mTLS mode requested but key_pem is missing
        """
        # Extract the serial number from the certificate
        cert   = load_pem_x509_certificate(cert_pem.encode())
        serial = format(cert.serial_number, "x")   # hex string, no leading 0x

        if use_mtls:
            self._revoke_mtls(
                cert_pem    = cert_pem,
                key_pem     = key_pem,
                serial      = serial,
                reason_code = reason_code,
                reason      = reason,
            )
        else:
            self._revoke_jwt(
                cert_pem    = cert_pem,
                serial      = serial,
                reason_code = reason_code,
                reason      = reason,
            )

        logger.info(
            "Revoked certificate serial=%s reason=%s (%d)",
            serial, reason or "unspecified", reason_code
        )

    def _revoke_jwt(
        self,
        cert_pem:    str,
        serial:      str,
        reason_code: int,
        reason:      str,
    ) -> None:
        """Revoke using a provisioner JWT token."""
        provisioner = self.get_provisioner()

        # The revocation token uses the same mechanism as the sign token
        # but with the aud set to /1.0/revoke and sub set to the serial
        now        = int(time.time())
        token_id   = str(uuid.uuid4())
        audience   = f"{self.ca_url}/1.0/revoke"
        jwk_private = self._decrypt_provisioner_key(provisioner.kid)

        revoke_claims = {
            "sub":    serial,               # serial number as subject
            "iss":    provisioner.name,
            "aud":    audience,
            "iat":    now,
            "exp":    now + 300,
            "jti":    token_id,
            "sha2":   hashlib.sha256(
                load_pem_x509_certificate(cert_pem.encode())
                .public_bytes(serialization.Encoding.DER)
            ).hexdigest(),
        }

        token = jose_jwt.encode(
            claims    = revoke_claims,
            key       = jwk_private,
            algorithm = jwk_private.get("alg", "ES256"),
            headers   = {"kid": provisioner.kid},
        )

        body = {
            "serial":     serial,
            "reasonCode": reason_code,
            "reason":     reason or "",
            "ott":        token,
        }

        response = self._session.post(
            f"{self.ca_url}/1.0/revoke",
            json = body,
        )
        self._raise_for_status(response)

    def _revoke_mtls(
        self,
        cert_pem:    str,
        key_pem:     str | None,
        serial:      str,
        reason_code: int,
        reason:      str,
    ) -> None:
        """Revoke using mTLS — the cert holder authenticates with its own cert."""
        if not key_pem:
            raise ValueError(
                "key_pem is required for mTLS revocation. "
                "Use use_mtls=False to revoke via JWT instead."
            )

        # Write cert/key to temp files for mTLS
        import os
        with (
            tempfile.NamedTemporaryFile(suffix=".crt", delete=False, mode="w") as cf,
            tempfile.NamedTemporaryFile(suffix=".key", delete=False, mode="w") as kf,
        ):
            cf.write(cert_pem)
            kf.write(key_pem)
            cert_path = cf.name
            key_path  = kf.name

        try:
            mtls_session = httpx.Client(
                verify  = self._root_cert_file.name,
                cert    = (cert_path, key_path),
                timeout = self.timeout,
            )

            # mTLS revocation accepts an empty body or reason fields
            body: dict = {}
            if reason_code:
                body["reasonCode"] = reason_code
            if reason:
                body["reason"] = reason

            response = mtls_session.post(
                f"{self.ca_url}/1.0/revoke",
                json = body or None,
            )
            mtls_session.close()
            self._raise_for_status(response)

        finally:
            os.unlink(cert_path)
            os.unlink(key_path)

    def get_certificate_serial(self, cert_pem: str) -> str:
        """Extract the serial number from a certificate PEM."""
        cert = load_pem_x509_certificate(cert_pem.encode())
        return format(cert.serial_number, "x")
```

---

## Using revoke()

```python
# demo_revoke.py

from step_ca_client import StepCAClient

ca = StepCAClient(
    ca_url               = "https://localhost:9000",
    root_fingerprint     = "702a094e...",
    provisioner_name     = "admin@example.com",
    provisioner_password = "provisioner-secret",
)

# First: issue a certificate
cert = ca.sign("compromised.internal", sans=["compromised.internal"])
print(f"Issued serial: {ca.get_certificate_serial(cert.cert_pem)}")

# Scenario 1: Key compromise — use JWT revocation
# (caller has provisioner password; may not have the private key)
ca.revoke(
    cert_pem    = cert.cert_pem,
    reason_code = StepCAClient.REASON_KEY_COMPROMISE,
    reason      = "Private key found in public GitHub repository",
)
print("Certificate revoked (JWT method).")

# Scenario 2: Self-revocation on service shutdown
cert2 = ca.sign("goodbye.internal", sans=["goodbye.internal"])

ca.revoke(
    cert_pem    = cert2.cert_pem,
    reason_code = StepCAClient.REASON_CESSATION_OF_OPERATION,
    reason      = "Service decommissioned",
    use_mtls    = True,
    key_pem     = cert2.key_pem,
)
print("Certificate self-revoked (mTLS method).")

# After revocation: attempting to renew will fail
try:
    ca.renew(cert.cert_pem, cert.key_pem)
except StepCAError as e:
    print(f"Expected error: {e}")
    # step-ca error 401: certificate has been revoked
```

---

## Revocation and Short-Lived Certs

```
REVOCATION STRATEGY COMPARISON

  Strategy              Pros                    Cons
  ──────────────────    ──────────────────────  ──────────────────────
  Passive (expire)      No infrastructure       Must wait for expiry
  24h cert expires      Zero revocation cost    Max 24h window
  at midnight           Simple                  Not suitable for key
                                                compromise

  Active revocation     Immediate effect        Requires step-ca
  POST /1.0/revoke      Suitable for key        revocation database
                        compromise              step-ca limited OCSP
                        Full audit trail        (no CRL by default)

  Recommended pattern for step-ca:
  • Use 24h or shorter certs (passive revocation is usually sufficient)
  • Reserve active revocation for key compromise events
  • For high-security requirements: use 1h certs + renewal daemon
    → worst-case exposure after compromise = 1 hour
```

---

## What's Next: The Complete Picture

In **Episode 8**, we assemble all eight episodes into the complete `StepCAClient` class listing, add a Flask server that uses step-ca certificates with mTLS, walk through the ACME provisioner as an alternative to the JWK flow, and review the production hardening checklist.

---

**🔗 Resources**
- **step-ca revocation**: [smallstep.com/docs/step-ca/revocation](https://smallstep.com/docs/step-ca/revocation/)
- **RFC 5280 revocation reason codes**: [rfc-editor.org/rfc/rfc5280#section-5.3.1](https://www.rfc-editor.org/rfc/rfc5280#section-5.3.1)
- **Passive revocation explanation**: [smallstep.com/blog/passive-revocation](https://smallstep.com/blog/passive-revocation.html)

---

*🔐 REST with step-ca — automating certificate lifecycle one HTTP call at a time.*
