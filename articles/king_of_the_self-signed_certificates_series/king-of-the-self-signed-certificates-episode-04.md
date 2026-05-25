---
title: "The King of the Self-signed Certificates - Ep. 04"
description: "The certificate is assembled, signed, and written to disk. The king dresses himself, steps into his carriage, and rides through the streets. Here is the complete Python implementation."
tags: [python, security, cryptography, tls]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/covers/main/king-self-signed-episode-04.png"
canonical_url: ""
series: "The King of the Self-signed Certificates"
part: 4
published: false
organization: "the-software-s-journey"
---

# The Grand Parade

> *At last the king was ready. The invisible robes had been woven, the portrait painted, the seal prepared. The royal herald announced the procession. The court lined both sides of the boulevard. The king stepped into his carriage and rode forward, magnificently and unmistakably naked, while all the courtiers applauded.*

This is the episode where we assemble everything and run the full parade: key generation, certificate construction, signing, and disk serialisation in one complete, working Python module.

-----

## SIPOC

|Suppliers                             |Inputs                                                             |Process                                                |Outputs                          |Customers                       |
|--------------------------------------|-------------------------------------------------------------------|-------------------------------------------------------|---------------------------------|--------------------------------|
|Episode 02 (`generate_private_key`)   |`RSAPrivateKey` object                                             |`CertificateBuilder()` chain                           |Signed `Certificate` object      |PEM encoder                     |
|Episode 03 (`build_name`, `build_san`)|`x509.Name`, `x509.SubjectAlternativeName`, `x509.BasicConstraints`|`.subject_name()`, `.issuer_name()`, `.add_extension()`|Builder with all fields populated|`.sign(key, hashes.SHA256())`   |
|`x509.random_serial_number()`         |OS entropy                                                         |Serial assignment                                      |Unique serial per cert           |CRL and OCSP revocation tracking|
|`datetime.timezone.utc`               |Current UTC time + validity window                                 |`.not_valid_before()`, `.not_valid_after()`            |Validity period embedded in cert |TLS handshake clock validation  |
|`.sign(key, hashes.SHA256())`         |Private key + SHA-256 digest                                       |Cryptographic signature over all fields                |Immutable, signed certificate    |File system (`cert.pem`)        |

-----

## The Complete Implementation

```python
# episode_04_grand_parade.py
# The king processes through the streets.
# Full self-signed certificate generation, assembly, and persistence.

import ipaddress
import datetime
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


# -------------------------------------------------------------------
# Key generation (Episode 02 recap)
# -------------------------------------------------------------------

def generate_private_key(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """Generate an RSA private key. The invisible cloth is cut."""
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )


# -------------------------------------------------------------------
# Certificate assembly (Episode 03 recap + signing)
# -------------------------------------------------------------------

def generate_selfsigned_cert(
    hostname: str,
    ip_addresses: list[str] | None = None,
    key: rsa.RSAPrivateKey | None = None,
    validity_days: int = 10,
    country: str = "NL",
    state: str = "Noord-Brabant",
    locality: str = "Eersel",
    organisation: str = "The Kingdom of Localhost",
) -> tuple[bytes, bytes]:
    """
    Generate a self-signed X.509 certificate.

    The grand parade. The king mounts the carriage.
    Subject and issuer are one and the same.
    The certificate signs itself with its own private key.

    Args:
        hostname:      CN and primary SAN DNS entry.
        ip_addresses:  Optional IP strings to include in SAN.
        key:           Optional pre-existing RSAPrivateKey.
                       If None, a fresh 2048-bit key is generated.
        validity_days: How many days from now the cert is valid.
                       Default: 10. Ten days is enough for testing.
                       The king's parade does not last forever.
        country:       Two-letter ISO country code.
        state:         State or province name.
        locality:      City.
        organisation:  Organisation name for the cert.

    Returns:
        Tuple of (cert_pem_bytes, key_pem_bytes).
        Both are PEM-encoded and ready to write to disk.

    WARNING:
        Self-signed certificates are for development and testing only.
        They will be rejected by browsers and other TLS clients that
        enforce the CA trust store. Do not deploy these in production.
        The king is naked. The child will say so.
    """
    # Step 1: produce the key if one was not provided
    if key is None:
        key = generate_private_key()

    # Step 2: build the identity
    # Subject == Issuer: the self-signed tautology
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organisation),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])

    # Step 3: build the SubjectAlternativeName extension
    # Modern clients check SAN, not COMMON_NAME.
    alt_names: list[x509.GeneralName] = [x509.DNSName(hostname)]
    if ip_addresses:
        for addr in ip_addresses:
            # DNSName for older OpenSSL; IPAddress for Go's crypto/tls
            alt_names.append(x509.DNSName(addr))
            alt_names.append(x509.IPAddress(ipaddress.ip_address(addr)))

    san = x509.SubjectAlternativeName(alt_names)

    # path_length=0: this cert can sign only itself
    basic_constraints = x509.BasicConstraints(ca=True, path_length=0)

    # Step 4: assemble and sign
    now = datetime.datetime.now(datetime.timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)                     # same as subject
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())  # unique, random serial
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=validity_days))
        .add_extension(basic_constraints, critical=False)
        .add_extension(san, critical=False)
        .sign(key, hashes.SHA256())             # signed with own private key
    )

    # Step 5: serialise to PEM bytes
    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return cert_pem, key_pem


# -------------------------------------------------------------------
# Persistence helpers
# -------------------------------------------------------------------

def write_pem_files(
    cert_pem: bytes,
    key_pem: bytes,
    cert_path: str = "cert.pem",
    key_path: str = "key.pem",
) -> None:
    """
    Write cert and key PEM files to disk.

    The herald pins the royal proclamation to the palace door.
    Two files emerge: the certificate (public, shareable) and
    the private key (secret, guard it with your life).

    Args:
        cert_pem:  PEM-encoded certificate bytes.
        key_pem:   PEM-encoded private key bytes.
        cert_path: Output path for the certificate file.
        key_path:  Output path for the private key file.
    """
    Path(cert_path).write_bytes(cert_pem)
    Path(key_path).write_bytes(key_pem)
    print(f"Certificate written to: {cert_path}")
    print(f"Private key  written to: {key_path}")


def inspect_cert(cert_pem: bytes) -> None:
    """
    Print a brief summary of the certificate just generated.

    The courtiers admire the king's new clothes and describe them
    in glowing terms, whether they can see them or not.

    Args:
        cert_pem: PEM-encoded certificate bytes.
    """
    cert = x509.load_pem_x509_certificate(cert_pem)
    print()
    print("--- Certificate Summary ---")
    print(f"Subject:      {cert.subject.rfc4514_string()}")
    print(f"Issuer:       {cert.issuer.rfc4514_string()}")
    print(f"Serial:       {cert.serial_number}")
    print(f"Not before:   {cert.not_valid_before_utc.isoformat()}")
    print(f"Not after:    {cert.not_valid_after_utc.isoformat()}")
    print(f"Subject == Issuer: {cert.subject == cert.issuer}")
    print("---------------------------")


# -------------------------------------------------------------------
# Main: run the full parade
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("The grand parade begins...")
    print()

    cert_pem, key_pem = generate_selfsigned_cert(
        hostname="localhost",
        ip_addresses=["127.0.0.1"],
        validity_days=10,
    )

    write_pem_files(cert_pem, key_pem)
    inspect_cert(cert_pem)

    print()
    print("The king processes through the streets.")
    print("The court applauds. The certificate exists.")
    print("Whether anyone trusts it is a different matter entirely.")
```

-----

## Running the Parade

```bash
pip install cryptography
python episode_04_grand_parade.py
```

Expected output:

```
The grand parade begins...

Certificate written to: cert.pem
Private key  written to: key.pem

--- Certificate Summary ---
Subject:      CN=localhost,O=The Kingdom of Localhost,L=Eersel,...
Issuer:       CN=localhost,O=The Kingdom of Localhost,L=Eersel,...
Serial:       <random large integer>
Not before:   2026-05-25T...
Not after:    2026-06-04T...
Subject == Issuer: True
---------------------------

The king processes through the streets.
The court applauds. The certificate exists.
Whether anyone trusts it is a different matter entirely.
```

-----

## Two Files, Two Roles

`cert.pem` is public. You can hand it to your Flask or FastAPI development server. You can import it into your test client’s trust store. You can read it with `openssl x509 -in cert.pem -text -noout`. It is the king’s portrait, framed and on display.

`key.pem` is secret. It never leaves the machine. It is what makes the signature on the certificate valid. Anyone who holds this file can impersonate the king completely.

-----

## A Note on the Serial Number

The original gist used a hardcoded serial of `1000`. The modern `cryptography` tutorial uses `x509.random_serial_number()`. The random serial is the better practice: it avoids collisions in CA logs and revocation infrastructure. Even a king who signs his own documents should give each one a unique number.

-----

## What Comes Next

The parade is over. The certificate exists on disk. A browser navigating to your `localhost` server will see it – and then will show a red warning screen. The child who sees through the king’s wardrobe lives in the browser’s trust store. Episode 05 explains why, and what a real trust hierarchy looks like.

-----

## References

- [bloodearnest/selfsigned.py](https://gist.github.com/bloodearnest/9017111a313777b9cce5)
- [cryptography.io: Creating a self-signed certificate](https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate)
- [cryptography.io: Creating a CA hierarchy](https://cryptography.io/en/latest/x509/tutorial/#creating-a-ca-hierarchy)
