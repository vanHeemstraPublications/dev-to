---
title: "REST with step-ca 🔐 Ep.5"
published: false
description: "Episode 5: All the pieces are in place. This episode assembles the complete sign() method: generate a key and CSR, create the JWT one-time token, POST both to /1.0/sign, parse the certChain response, and return the signed certificate. A full sequence diagram shows every network hop and cryptographic step from call to certificate."
tags: [python, tls, certificates, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/rest-with-step-ca-episode-05.png"
series: "REST with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 5
---

## Episode 5: Sign Here — The Certificate Issuance Flow

---

## The Moment of Truth

Four episodes of preparation lead to this. We have a verified HTTPS session, a CSR factory, and a token factory. Now we assemble them into a single `sign()` call that returns a ready-to-use X.509 certificate — from a one-line invocation.

---

## 🗂️ SIPOC — Certificate Issuance

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Episodes 2, 3, 4 | CA session, key factory, token factory | Orchestrate: provisioner → key+CSR → token → POST /sign → parse | `(cert_pem, key_pem)` tuple | Any service that needs a TLS certificate |
| `POST /1.0/sign` endpoint | `{csr: PEM, ott: JWT}` JSON body | Validate JWT, validate CSR, sign with intermediate CA key | `{crt, ca, certChain}` JSON response | The client — which extracts and stores the certificate |
| `certChain` response array | `["<leaf cert PEM>", "<intermediate PEM>"]` | Parse and concatenate as a full chain PEM | A PEM file containing the full chain | TLS servers — which must present the full chain to clients |

---

## The Complete Issuance Sequence Diagram

```
CLIENT (StepCAClient)                    step-ca Server
══════════════════════                   ══════════════════════════════

1. ca.sign("myservice.internal", sans=[...])
   │
   ├── list_provisioners()
   │   GET /provisioners ───────────────►
   │   ◄── {"provisioners":[...]}
   │
   ├── _get_encrypted_key(kid)
   │   GET /provisioners/{kid}/encrypted-key ──►
   │   ◄── {"key":"eyJhbGci..."}  (JWE)
   │
   ├── _decrypt_provisioner_key()
   │   JWE → JWK (local, no network)
   │   EC private key extracted
   │
   ├── create_key_and_csr("myservice.internal", sans=[...])
   │   EC key generated (local)
   │   PKCS#10 CSR signed with EC key (local)
   │
   ├── _create_token("myservice.internal", sans, provisioner)
   │   JWT claims assembled (local)
   │   JWT signed with provisioner EC key (local)
   │   jti = unique UUID
   │
   └── POST /1.0/sign ─────────────────────────────────────────►
       body = {                              │
         "csr": "-----BEGIN CERT REQ..."    │ Validate JWT:
         "ott": "eyJhbGci...jwt"            │   signature? ✓
       }                                    │   exp? ✓
                                            │   aud? ✓
                                            │   jti not reused? ✓
                                            │
                                            │ Validate CSR:
                                            │   self-signature? ✓
                                            │   CN matches jwt.sub? ✓
                                            │   SANs ⊆ jwt.sans? ✓
                                            │
                                            │ Sign certificate:
                                            │   Embed CSR public key
                                            │   Set subject/SANs
                                            │   Set validity: 24h
                                            │   Sign: intermediate CA key
                                            │
       ◄── 200 OK ──────────────────────────────────────────────
       {
         "crt":       "-----BEGIN CERT...  (leaf cert)
         "ca":        "-----BEGIN CERT...  (intermediate cert)
         "certChain": ["-----BEGIN CERT... (leaf)",
                       "-----BEGIN CERT... (intermediate)"]
       }

2. Returns: (cert_pem, key_pem)
   cert_pem = leaf + intermediate (full chain)
   key_pem  = the EC private key generated in step above
```

---

## The sign() Method

```python
# step_ca_client.py  (additions — certificate issuance)

from dataclasses import dataclass


@dataclass
class IssuedCertificate:
    """Result of a certificate signing operation."""
    cert_pem:  str   # Leaf certificate PEM
    chain_pem: str   # Full chain PEM (leaf + intermediate)
    ca_pem:    str   # Intermediate CA PEM
    key_pem:   str   # Private key PEM (unencrypted — handle carefully)

    def save(
        self,
        cert_path: str,
        key_path:  str,
        *,
        chain:     bool  = True,
        password:  bytes | None = None,
    ) -> None:
        """
        Save the certificate and key to disk.

        Args:
            cert_path: Path for the certificate PEM file
            key_path:  Path for the private key PEM file
            chain:     If True (default), write full chain to cert_path
            password:  Optional password to encrypt the private key
        """
        cert_content = self.chain_pem if chain else self.cert_pem
        Path(cert_path).write_text(cert_content)

        if password:
            from cryptography.hazmat.primitives.serialization import (
                load_pem_private_key, Encoding, PrivateFormat,
                BestAvailableEncryption
            )
            key_obj = load_pem_private_key(
                self.key_pem.encode(), password=None
            )
            encrypted_pem = key_obj.private_bytes(
                Encoding.PEM,
                PrivateFormat.TraditionalOpenSSL,
                BestAvailableEncryption(password),
            ).decode()
            Path(key_path).write_text(encrypted_pem)
        else:
            Path(key_path).write_text(self.key_pem)

        logger.info("Saved cert to %s and key to %s", cert_path, key_path)

    def inspect(self) -> dict:
        """Parse the leaf certificate and return key metadata."""
        cert = x509.load_pem_x509_certificate(self.cert_pem.encode())
        sans = []
        try:
            san_ext = cert.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            )
            for name in san_ext.value:
                if isinstance(name, x509.DNSName):
                    sans.append(f"DNS:{name.value}")
                elif isinstance(name, x509.IPAddress):
                    sans.append(f"IP:{name.value}")
        except x509.ExtensionNotFound:
            pass

        return {
            "subject":     cert.subject.rfc4514_string(),
            "issuer":      cert.issuer.rfc4514_string(),
            "serial":      str(cert.serial_number),
            "not_before":  cert.not_valid_before_utc.isoformat(),
            "not_after":   cert.not_valid_after_utc.isoformat(),
            "sans":        sans,
        }


class StepCAClient:
    # ... (existing methods from Episodes 2, 3, 4)

    # ── Certificate issuance ──────────────────────────────────────────────

    def sign(
        self,
        common_name:  str,
        sans:         list[str],
        *,
        key_type:     str  = "EC",
        key_size:     int  = 2048,
        organization: str  = "",
        country:      str  = "",
        duration:     str  = "",
    ) -> IssuedCertificate:
        """
        Issue a certificate from step-ca using the JWK provisioner.

        This is the main entry point for certificate issuance.
        It orchestrates key generation, CSR creation, token creation,
        and the POST to /1.0/sign.

        Args:
            common_name:  Subject CN and primary identity
            sans:         Subject Alternative Names (DNS names and/or IPs)
            key_type:     "EC" (default) or "RSA"
            key_size:     RSA key size (default 2048, ignored for EC)
            organization: O= attribute in Subject DN
            country:      C= attribute in Subject DN (2-letter ISO code)
            duration:     Optional certificate duration override,
                          e.g. "1h", "72h". Empty = use CA default (24h).

        Returns:
            IssuedCertificate with cert_pem, chain_pem, ca_pem, key_pem
        """
        # Make sure CN is in SANs list (best practice; step-ca may require it)
        effective_sans = list(dict.fromkeys([common_name] + sans))

        # Get the provisioner we will use
        provisioner = self.get_provisioner()

        # Generate the private key and CSR
        private_key, csr_pem = self.create_key_and_csr(
            common_name  = common_name,
            sans         = effective_sans,
            key_type     = key_type,
            key_size     = key_size,
            organization = organization,
            country      = country,
        )

        # Create the one-time JWT token
        token = self._create_token(
            common_name = common_name,
            sans        = effective_sans,
            provisioner = provisioner,
        )

        # POST to /1.0/sign
        request_body: dict = {
            "csr": csr_pem,
            "ott": token,
        }
        if duration:
            request_body["notAfter"] = duration  # step-ca accepts duration strings

        logger.info(
            "Signing certificate: CN=%s SANs=%s via %s",
            common_name, effective_sans, self.ca_url
        )

        response = self._session.post(
            f"{self.ca_url}/1.0/sign",
            json = request_body,
        )
        self._raise_for_status(response)

        data = response.json()

        # Parse the response
        # certChain[0] = leaf cert, certChain[1] = intermediate cert
        cert_chain = data.get("certChain", [])
        if not cert_chain:
            # Fallback: some versions return crt + ca separately
            cert_pem_from_response = data.get("crt", "")
            ca_pem   = data.get("ca", "")
            cert_chain = [cert_pem_from_response, ca_pem]

        leaf_pem  = cert_chain[0]
        ca_pem    = cert_chain[1] if len(cert_chain) > 1 else ""
        chain_pem = "".join(cert_chain)   # full chain for servers

        key_pem = self.private_key_to_pem(private_key)

        issued = IssuedCertificate(
            cert_pem  = leaf_pem,
            chain_pem = chain_pem,
            ca_pem    = ca_pem,
            key_pem   = key_pem,
        )

        info = issued.inspect()
        logger.info(
            "Certificate issued: CN=%s not_after=%s",
            info["subject"], info["not_after"]
        )

        return issued
```

---

## Using sign() End to End

```python
# demo_sign.py

from step_ca_client import StepCAClient

ca = StepCAClient(
    ca_url               = "https://localhost:9000",
    root_fingerprint     = "702a094e...",
    provisioner_name     = "admin@example.com",
    provisioner_password = "provisioner-secret",
)

# Issue a certificate
cert = ca.sign(
    common_name  = "myservice.internal",
    sans         = ["myservice.internal", "10.96.0.10"],
    organization = "Acme Corp",
    country      = "NL",
)

# Inspect what we got
info = cert.inspect()
print(f"Subject:    {info['subject']}")
print(f"Issuer:     {info['issuer']}")
print(f"Serial:     {info['serial']}")
print(f"Not before: {info['not_before']}")
print(f"Not after:  {info['not_after']}")
print(f"SANs:       {info['sans']}")

# Subject:    CN=myservice.internal,O=Acme Corp,C=NL
# Issuer:     CN=My Internal CA Intermediate
# Serial:     123456789
# Not before: 2026-06-17T10:00:00+00:00
# Not after:  2026-06-18T10:00:00+00:00
# SANs:       ['DNS:myservice.internal', 'IP:10.96.0.10']

# Save to disk
cert.save("myservice.crt", "myservice.key")
print("Certificate and key saved.")

# Or use the PEMs directly in memory (no disk I/O)
cert_pem = cert.chain_pem   # full chain for TLS servers
key_pem  = cert.key_pem     # private key (handle carefully)
```

---

## The certChain Response Anatomy

```
POST /1.0/sign  →  200 OK

{
  "crt": "-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----\n",
         └─ Leaf certificate only (for backward compatibility)

  "ca": "-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----\n",
        └─ Intermediate CA certificate

  "certChain": [
    "-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----\n",
     └─ [0] Leaf certificate (what was signed)

    "-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----\n"
     └─ [1] Intermediate CA certificate
  ]
}

TLS Server Usage:
  - Present certChain (leaf + intermediate) to clients
  - The root cert is in clients' trust store (from bootstrap)
  - Clients build the chain: leaf → intermediate → root

Note: The `crt` and `ca` fields exist for backward compatibility.
Use `certChain` when available — it is more explicit about ordering.
```

---

## Error Handling for the Sign Request

```python
from step_ca_client import StepCAClient, StepCAError

ca = StepCAClient(...)

try:
    cert = ca.sign("myservice.internal", sans=["myservice.internal"])
except StepCAError as e:
    if e.status_code == 400:
        # JWT or CSR validation failure
        print(f"Bad request: {e}")
        # e.g. "The token is not valid: aud claim does not match"
        # e.g. "Certificate request is not authorized: check CSR SANs"
    elif e.status_code == 401:
        # Token rejected — expired, reused, or invalid signature
        print(f"Auth failure: {e}")
    elif e.status_code == 500:
        # step-ca internal error (check CA logs)
        print(f"CA server error: {e}")
    else:
        raise

# Common error messages from step-ca /1.0/sign:
# "The token is expired"              → exp claim in the past
# "token already used"                → jti already recorded (replay)
# "The token audience is invalid"     → aud doesn't match CA URL + /1.0/sign
# "certificate request is not valid"  → CSR SANs not authorised by JWT
```

---

## What's Next: Still Breathing

In **Episode 6**, we tackle renewal. Certificates expire. step-ca supports renewal via **mTLS** — no JWT needed, just present the existing certificate as a TLS client certificate in a POST to `/1.0/renew`. We add `renew()` and a background `start_renewal_daemon()` thread that automatically renews at two-thirds of the certificate's remaining lifetime.

---

**🔗 Resources**
- **step-ca `/1.0/sign` endpoint**: [smallstep.com/docs/step-ca/basic-certificate-authority-operations](https://smallstep.com/docs/step-ca/basic-certificate-authority-operations/)
- **RFC 2986 PKCS#10**: [rfc-editor.org/rfc/rfc2986](https://www.rfc-editor.org/rfc/rfc2986)

---

*🔐 REST with step-ca — automating certificate lifecycle one HTTP call at a time.*
