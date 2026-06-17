---
title: "REST with step-ca 🔐 Ep.3"
published: false
description: "Episode 3: Before you can ask a CA to sign anything, you need a Certificate Signing Request. This episode builds create_key_and_csr() — generating EC or RSA private keys with the Python cryptography library, constructing a PKCS#10 CSR with a proper Subject DN and Subject Alternative Names, and understanding exactly what step-ca expects in the PEM it receives at /1.0/sign."
tags: [python, cryptography, x509, certificates]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/rest-with-step-ca-episode-03.png"
series: "REST with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 3
---

## Episode 3: Generating the CSR — Keys, Subjects, and SANs

---

## What the CA Actually Signs

When you ask step-ca for a certificate, you do not hand it a wishlist. You hand it a **Certificate Signing Request** (CSR, PKCS#10, RFC 2986) — a structure that contains your public key, your requested Subject, your requested Subject Alternative Names, and a signature over all of it made with your private key.

The CSR signature proves you hold the private key corresponding to the public key in the request. step-ca validates this before it will sign anything. It then issues a certificate with a subject and SANs consistent with what the provisioner token says you are allowed to have.

The private key never leaves your process. You generate it, use it to sign the CSR, and keep it. The CA sees only the public key.

---

## 🗂️ SIPOC — Key and CSR Generation

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| `cryptography.hazmat.primitives` | Key type (`ec`/`rsa`), curve or key size | Generate private key in memory | Private key object (never serialised unless explicitly requested) | CSR builder — uses the private key to sign the CSR |
| `cryptography.x509` | Common name, SANs (DNS names, IP addresses), key usage flags | Build `CertificateSigningRequestBuilder`; add extensions; sign with private key | A `CertificateSigningRequest` object | `StepCAClient.sign()` — converts to PEM and sends to `/1.0/sign` |
| The developer | Subject CN, list of SANs | Call `create_key_and_csr(cn, sans)` | `(private_key, csr_pem: str)` tuple | Subsequent sign/renew calls; disk storage if desired |

---

## X.509 CSR Anatomy

```
PKCS#10 Certificate Signing Request (CSR)
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│  CertificationRequestInfo  (the data being signed)              │
│                                                                 │
│  version:     0  (always 0 for PKCS#10 v1)                      │
│                                                                 │
│  subject:     C=NL, O=Acme Corp, CN=myservice.internal          │
│               └─ Distinguished Name — who is requesting         │
│                                                                 │
│  subjectPublicKeyInfo:                                          │
│    algorithm:  id-ecPublicKey + prime256v1                      │
│    publicKey:  04 xx xx xx ...  (65 bytes, uncompressed EC)     │
│    └─ The public key the CA will embed in the certificate       │
│                                                                 │
│  extensions (optional, via attributes):                         │
│    SubjectAltName:                                              │
│      dNSName:  myservice.internal                               │
│      dNSName:  myservice.svc.cluster.local                      │
│      iPAddress: 10.0.0.42                                       │
│    KeyUsage:                                                    │
│      digitalSignature, keyEncipherment                          │
│    ExtendedKeyUsage:                                            │
│      serverAuth (1.3.6.1.5.5.7.3.1)                             │
│      clientAuth (1.3.6.1.5.5.7.3.2)                             │
└─────────────────────────────────────────────────────────────────┘
│
│  signature:  ECDSA-with-SHA256(privateKey, CertificationRequestInfo)
│  └─ Proves the requester holds the private key for the public key above
```

step-ca reads the CSR, validates the signature, checks the subject and SANs against the JWT claims, and — if everything matches — signs a new certificate.

---

## Key Type Decision

```
KEY TYPE COMPARISON FOR step-ca CERTIFICATES

  EC P-256 (ECDSA)          RSA 2048               RSA 4096
  ──────────────────        ──────────────────      ──────────────────
  Default in step-ca        Legacy-compatible       Maximum RSA security
  Smaller key (256 bit)     2048-bit key            4096-bit key
  Fast signing/verify       Slower than EC          Slowest
  ~32-byte signature        ~256-byte signature     ~512-byte signature
  Perfect forward secrecy   PFS with ECDHE          PFS with ECDHE
  Not all legacy TLS        Universally supported   Some clients reject it
  clients support it

  RECOMMENDATION: Use EC P-256 for new services.
  Use RSA 2048 only when connecting to legacy systems that
  reject EC certificates (old Java clients, some IoT devices).
```

---

## Adding `create_key_and_csr` to StepCAClient

```python
# step_ca_client.py  (additions to the class from Episode 2)

import ipaddress
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography import x509


# ── Key generation helpers ─────────────────────────────────────────

def _generate_ec_key() -> ec.EllipticCurvePrivateKey:
    """Generate an EC P-256 private key."""
    return ec.generate_private_key(ec.SECP256R1())

def _generate_rsa_key(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """Generate an RSA private key."""
    return rsa.generate_private_key(
        public_exponent = 65537,
        key_size        = key_size,
    )


class StepCAClient:
    # ... (existing __init__, health, get_roots, list_provisioners from Ep2)

    # ── CSR generation ────────────────────────────────────────────────────

    def create_key_and_csr(
        self,
        common_name:  str,
        sans:         list[str],
        *,
        key_type:     str  = "EC",
        key_size:     int  = 2048,
        organization: str  = "",
        country:      str  = "",
        include_key_usage: bool = True,
        include_eku:       bool = True,
    ) -> tuple[object, str]:
        """
        Generate a private key and a PKCS#10 CSR.

        Args:
            common_name:   The CN for the Subject DN (e.g. "myservice.internal")
            sans:          List of SANs. DNS names and/or IPv4/IPv6 addresses.
                           e.g. ["myservice.internal", "10.0.0.42", "::1"]
            key_type:      "EC" (default) or "RSA"
            key_size:      RSA key size in bits (ignored for EC). Default: 2048
            organization:  O= field in Subject DN (optional)
            country:       C= field in Subject DN (optional, 2-letter ISO)
            include_key_usage: Add KeyUsage extension (recommended: True)
            include_eku:       Add ExtendedKeyUsage for serverAuth+clientAuth

        Returns:
            (private_key, csr_pem_string)
            The private key is a cryptography private key object.
            Call private_key_to_pem(key) to serialise it.
        """
        # Generate the private key
        if key_type.upper() == "EC":
            private_key = _generate_ec_key()
        elif key_type.upper() == "RSA":
            private_key = _generate_rsa_key(key_size)
        else:
            raise ValueError(f"key_type must be 'EC' or 'RSA', not {key_type!r}")

        # Build the Subject Distinguished Name
        subject_attrs = [
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
        if organization:
            subject_attrs.append(
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization)
            )
        if country:
            subject_attrs.append(
                x509.NameAttribute(NameOID.COUNTRY_NAME, country)
            )
        subject = x509.Name(subject_attrs)

        # Parse SANs: distinguish DNS names from IP addresses
        san_entries: list[x509.GeneralName] = []
        for san in sans:
            try:
                ip = ipaddress.ip_address(san)
                san_entries.append(x509.IPAddress(ip))
            except ValueError:
                san_entries.append(x509.DNSName(san))

        # Build the CSR
        builder = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(subject)
        )

        if san_entries:
            builder = builder.add_extension(
                x509.SubjectAlternativeName(san_entries),
                critical=False,
            )

        if include_key_usage:
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature  = True,
                    key_encipherment   = (key_type.upper() == "RSA"),
                    content_commitment = False,
                    data_encipherment  = False,
                    key_agreement      = False,
                    key_cert_sign      = False,
                    crl_sign           = False,
                    encipher_only      = False,
                    decipher_only      = False,
                ),
                critical=True,
            )

        if include_eku:
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([
                    ExtendedKeyUsageOID.SERVER_AUTH,
                    ExtendedKeyUsageOID.CLIENT_AUTH,
                ]),
                critical=False,
            )

        # Sign the CSR with the private key
        csr = builder.sign(
            private_key,
            hashes.SHA256(),
        )

        csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode()
        logger.debug(
            "Generated %s CSR for CN=%s with %d SAN(s)",
            key_type.upper(), common_name, len(san_entries)
        )
        return private_key, csr_pem

    @staticmethod
    def private_key_to_pem(
        private_key: object,
        password:    bytes | None = None,
    ) -> str:
        """
        Serialise a private key to PEM format.

        Args:
            private_key: An EC or RSA private key object
            password:    Optional encryption password for the PEM.
                         If None, the PEM is unencrypted (keep it safe!).
        Returns:
            PEM-encoded private key as a string
        """
        encryption = (
            serialization.BestAvailableEncryption(password)
            if password
            else serialization.NoEncryption()
        )
        return private_key.private_bytes(
            encoding           = serialization.Encoding.PEM,
            format             = serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm = encryption,
        ).decode()

    @staticmethod
    def inspect_csr(csr_pem: str) -> dict:
        """
        Parse a CSR PEM and return a dict describing its contents.
        Useful for debugging and logging.
        """
        csr = x509.load_pem_x509_csr(csr_pem.encode())
        result: dict = {
            "subject": csr.subject.rfc4514_string(),
            "key_type": type(csr.public_key()).__name__,
            "signature_valid": csr.is_signature_valid,
            "sans": [],
        }
        try:
            san_ext = csr.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            )
            for name in san_ext.value:
                if isinstance(name, x509.DNSName):
                    result["sans"].append(f"DNS:{name.value}")
                elif isinstance(name, x509.IPAddress):
                    result["sans"].append(f"IP:{name.value}")
        except x509.ExtensionNotFound:
            pass
        return result
```

---

## Exercising the CSR Factory

```python
# demo_csr.py

from step_ca_client import StepCAClient

ca = StepCAClient(
    ca_url               = "https://localhost:9000",
    root_fingerprint     = "702a094e...",
    provisioner_name     = "admin@example.com",
    provisioner_password = "provisioner-secret",
)

# EC key (default, recommended)
key, csr_pem = ca.create_key_and_csr(
    common_name  = "myservice.internal",
    sans         = [
        "myservice.internal",
        "myservice.svc.cluster.local",
        "10.96.0.10",
    ],
    organization = "Acme Corp",
    country      = "NL",
)

# Inspect what we built
info = ca.inspect_csr(csr_pem)
print(f"Subject:   {info['subject']}")
print(f"Key type:  {info['key_type']}")
print(f"Signature: {'valid' if info['signature_valid'] else 'INVALID'}")
print(f"SANs:      {info['sans']}")
# Subject:   CN=myservice.internal,O=Acme Corp,C=NL
# Key type:  EllipticCurvePublicKey
# Signature: valid
# SANs:      ['DNS:myservice.internal', 'DNS:myservice.svc.cluster.local', 'IP:10.96.0.10']

print("\n--- CSR PEM ---")
print(csr_pem[:120], "...")

# Optionally save the private key (encrypted)
key_pem = ca.private_key_to_pem(key, password=b"my-key-password")
print("\n--- Private Key (encrypted PEM) ---")
print(key_pem[:80], "...")
```

---

## What step-ca Does With the CSR

```
CSR VALIDATION FLOW IN STEP-CA

  Client                           step-ca /1.0/sign
  ──────                           ────────────────────────────────────
  POST {csr: PEM, ott: JWT}
                              ──► 1. Parse JWT (ott)
                                     Verify JWT signature
                                     (using provisioner's PUBLIC key)
                                     Check exp, iat, iss, aud, jti
                                     Extract: subject, sans from JWT

                                  2. Parse CSR
                                     Verify CSR self-signature
                                     Extract: subject, SANs from CSR

                                  3. Policy check
                                     JWT subject == CSR CN? ✓
                                     JWT sans ⊇ CSR SANs? ✓
                                     Duration within provisioner limits? ✓

                                  4. Sign the certificate
                                     Embed public key from CSR
                                     Set subject from JWT/CSR
                                     Set SANs from JWT/CSR
                                     Set validity (default 24h)
                                     Sign with intermediate CA key

  ◄── {crt: PEM, ca: PEM, certChain: [...]}
```

The JWT and CSR must agree on subject and SANs. If the JWT says `CN=foo.internal` but the CSR says `CN=bar.internal`, the sign request is rejected.

---

## What's Next: The Token Factory

In **Episode 4**, we build `_decrypt_provisioner_key()` and `_create_token()` — the methods that decrypt the JWE-encrypted JWK private key from the CA and use it to sign the JWT (the `ott`) that authorises the sign request. The provisioner password is the key to the kingdom, and Episode 4 opens that lock.

---

**🔗 Resources**
- **RFC 2986 — PKCS#10 CSR**: [rfc-editor.org/rfc/rfc2986](https://www.rfc-editor.org/rfc/rfc2986)
- **cryptography library CSR docs**: [cryptography.io/en/latest/x509/reference/#certificate-signing-requests](https://cryptography.io/en/latest/x509/reference/#certificate-signing-requests)
- **X.509 SAN types**: [rfc-editor.org/rfc/rfc5280#section-4.2.1.6](https://www.rfc-editor.org/rfc/rfc5280#section-4.2.1.6)

---

*🔐 REST with step-ca — automating certificate lifecycle one HTTP call at a time.*
