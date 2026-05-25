---
title: "The King of the Self-signed Certificates - Ep. 05"
description: "A child in the crowd says what the entire court refused to say. Browsers have been that child since 2017. Learn why self-signed certs fail in production and how a proper CA hierarchy restores trust."
tags: [python, security, cryptography, pki]
cover_image: <https://raw.githubusercontent.com/vanHeemstraPublications/covers/main/king-self-signed-episode-05.png>
canonical_url: ""
series: "The King of the Self-signed Certificates"
part: 5
published: false
organization: "the-software-s-journey"
---

# The Child Speaks

> *As the carriage rolled past, a small child tugged at her father’s sleeve.*
> 
> *“But he has no clothes on,” she said.*
> 
> *The crowd fell silent. The king’s carriage rolled on. And from that day forward, every browser, every TLS client, every operating system trust store repeated exactly what the child had said – loudly, in red, with a warning triangle.*

This is what happens when you deploy a self-signed certificate outside your development machine.

The browser does not care about the distinguished name. It does not care about the validity period, the SHA-256 signature, or the elegant Python code that produced the certificate. It asks one question only: **is the issuer in my trust store?**

For a self-signed certificate, the issuer is the certificate itself. And the certificate is not in any trust store on earth except the ones you explicitly configured yourself.

The child speaks. The warning appears. The parade is over.

-----

## SIPOC

|Suppliers                       |Inputs                                                                           |Process                                   |Outputs                                |Customers                                                          |
|--------------------------------|---------------------------------------------------------------------------------|------------------------------------------|---------------------------------------|-------------------------------------------------------------------|
|`cryptography` EC key generation|`ec.SECP256R1()` private keys                                                    |`ec.generate_private_key()`               |Root CA key, intermediate key, leaf key|CA hierarchy builder                                               |
|Root CA cert builder            |`BasicConstraints(ca=True, path_length=None)`, `KeyUsage`, `SubjectKeyIdentifier`|`CertificateBuilder().sign(root_key, ...)`|Root CA certificate                    |Browser / OS trust store (after manual import)                     |
|Intermediate CA cert builder    |Root CA cert as issuer, `path_length=0`, `AuthorityKeyIdentifier`                |`CertificateBuilder().sign(root_key, ...)`|Intermediate CA certificate            |Leaf certificate issuer                                            |
|Leaf cert builder               |Intermediate as issuer, `SubjectAlternativeName`, `ExtendedKeyUsage`             |`CertificateBuilder().sign(int_key, ...)` |Leaf certificate for `cryptography.io` |`PolicyBuilder().store(Store([root_cert])).build_server_verifier()`|
|`PolicyBuilder` + `Store`       |Root cert in store, leaf + intermediates                                         |`verifier.verify(ee_cert, [int_cert])`    |Verified chain of length 3             |Confirmed: the king is now dressed                                 |

-----

## Why Browsers Reject Self-signed Certificates

Every major operating system ships with a **root certificate store** – a list of public keys belonging to trusted Certificate Authorities. When a browser validates a certificate, it walks a chain:

```
leaf cert  --> signed by --> intermediate CA  --> signed by --> root CA
```

If the root CA at the top of that chain is in the trust store, the entire chain is valid. The king’s identity is confirmed by an external authority.

A self-signed certificate has no chain. It is its own root. The browser reaches the top and finds a name it has never heard of: `The Kingdom of Localhost`. It is not in the store. The child speaks.

```
NET::ERR_CERT_AUTHORITY_INVALID
Your connection is not private.
```

-----

## The Solution: Build Your Own CA Hierarchy

For development environments where you need browsers to trust your local certs, the answer is to build a minimal CA hierarchy and import only the root CA into your trust store. You never import the leaf certificate directly – you import the root, and let the chain do the work.

```python
# episode_05_child_speaks.py
# The court finally listens. A proper CA hierarchy is built.
# Based on the cryptography.io tutorial CA hierarchy example.

import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from cryptography.x509.verification import PolicyBuilder, Store


# -------------------------------------------------------------------
# Helper: build a Name
# -------------------------------------------------------------------

def make_name(common_name: str, organisation: str = "The Kingdom of Localhost") -> x509.Name:
    """
    Build an X.509 Name for use as subject or issuer.

    Args:
        common_name:  The CN field -- identifies the role in the hierarchy.
        organisation: Shared organisation name across the hierarchy.

    Returns:
        An x509.Name object.
    """
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "NL"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Noord-Brabant"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Eersel"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organisation),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])


# -------------------------------------------------------------------
# Step 1: Root CA
# The child's father, at last, speaks the truth.
# This is the certificate you import once into the OS trust store.
# -------------------------------------------------------------------

def build_root_ca() -> tuple[ec.EllipticCurvePrivateKey, x509.Certificate]:
    """
    Generate the root CA key and certificate.

    The root CA is the single external authority that grants legitimacy
    to the entire hierarchy. Unlike the self-signed king, the root CA
    is a known, imported, explicitly trusted entity. You place it in
    the trust store yourself -- which is a conscious, verifiable act
    of trust, not a royal proclamation.

    Returns:
        Tuple of (root_private_key, root_ca_certificate).
    """
    root_key = ec.generate_private_key(ec.SECP256R1())
    subject = issuer = make_name("Kingdom Root CA")
    now = datetime.datetime.now(datetime.timezone.utc)

    root_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365 * 10))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()),
            critical=False,
        )
        .sign(root_key, hashes.SHA256())
    )

    return root_key, root_cert


# -------------------------------------------------------------------
# Step 2: Intermediate CA
# The court chamberlain, delegated authority from the king's father.
# -------------------------------------------------------------------

def build_intermediate_ca(
    root_key: ec.EllipticCurvePrivateKey,
    root_cert: x509.Certificate,
) -> tuple[ec.EllipticCurvePrivateKey, x509.Certificate]:
    """
    Generate an intermediate CA, signed by the root CA.

    The intermediate CA is issued by the root and can issue leaf
    certificates. path_length=0 means it cannot delegate further.
    The chamberlain may appoint servants, but not lords.

    Args:
        root_key:  Root CA private key (used to sign this cert).
        root_cert: Root CA certificate (used as the issuer name).

    Returns:
        Tuple of (intermediate_private_key, intermediate_ca_certificate).
    """
    int_key = ec.generate_private_key(ec.SECP256R1())
    subject = make_name("Kingdom Intermediate CA")
    now = datetime.datetime.now(datetime.timezone.utc)

    int_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(root_cert.subject)             # issued by root, not self
        .public_key(int_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365 * 3))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=0),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(int_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
                root_cert.extensions.get_extension_for_class(
                    x509.SubjectKeyIdentifier
                ).value
            ),
            critical=False,
        )
        .sign(root_key, hashes.SHA256())            # signed by root key
    )

    return int_key, int_cert


# -------------------------------------------------------------------
# Step 3: Leaf (end-entity) certificate
# The servant with a name badge. Trusted because the chamberlain said so.
# -------------------------------------------------------------------

def build_leaf_cert(
    hostname: str,
    int_key: ec.EllipticCurvePrivateKey,
    int_cert: x509.Certificate,
) -> tuple[ec.EllipticCurvePrivateKey, x509.Certificate]:
    """
    Generate a leaf (end-entity) certificate signed by the intermediate CA.

    This is the certificate your server presents during the TLS handshake.
    It is not self-signed. Its issuer is the intermediate CA, whose issuer
    is the root CA, which is in the trust store. The chain is complete.
    The child is silent. The king is dressed.

    Args:
        hostname: The domain or hostname this certificate serves.
        int_key:  Intermediate CA private key (used to sign this cert).
        int_cert: Intermediate CA certificate (used as issuer name).

    Returns:
        Tuple of (leaf_private_key, leaf_certificate).
    """
    ee_key = ec.generate_private_key(ec.SECP256R1())
    subject = make_name(hostname)
    now = datetime.datetime.now(datetime.timezone.utc)

    ee_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(int_cert.subject)              # issued by intermediate
        .public_key(ee_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=10))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(hostname),
                x509.DNSName(f"www.{hostname}"),
            ]),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([
                x509.ExtendedKeyUsageOID.CLIENT_AUTH,
                x509.ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=False,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ee_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
                int_cert.extensions.get_extension_for_class(
                    x509.SubjectKeyIdentifier
                ).value
            ),
            critical=False,
        )
        .sign(int_key, hashes.SHA256())             # signed by intermediate key
    )

    return ee_key, ee_cert


# -------------------------------------------------------------------
# Step 4: Verify the chain
# The child checks. The chain is valid.
# -------------------------------------------------------------------

def verify_chain(
    root_cert: x509.Certificate,
    int_cert: x509.Certificate,
    ee_cert: x509.Certificate,
    hostname: str,
) -> None:
    """
    Verify the certificate chain using cryptography's PolicyBuilder.

    This is the moment the child looks at the king and sees real clothes.
    The root is in the store. The chain resolves. Verification passes.

    Args:
        root_cert: The trust anchor (root CA certificate).
        int_cert:  The intermediate CA certificate.
        ee_cert:   The leaf/end-entity certificate.
        hostname:  The DNS name to verify against.
    """
    from cryptography.x509 import DNSName

    store = Store([root_cert])
    builder = PolicyBuilder().store(store)
    verifier = builder.build_server_verifier(DNSName(hostname))
    chain = verifier.verify(ee_cert, [int_cert])

    print(f"Chain verified successfully. Length: {len(chain)}")
    for i, cert in enumerate(chain):
        print(f"  [{i}] {cert.subject.rfc4514_string()}")


# -------------------------------------------------------------------
# Main: the child finally sees the truth
# -------------------------------------------------------------------
if __name__ == "__main__":
    hostname = "localhost"

    print("Building root CA...")
    root_key, root_cert = build_root_ca()

    print("Building intermediate CA...")
    int_key, int_cert = build_intermediate_ca(root_key, root_cert)

    print(f"Building leaf certificate for: {hostname}")
    ee_key, ee_cert = build_leaf_cert(hostname, int_key, int_cert)

    print()
    verify_chain(root_cert, int_cert, ee_cert, hostname)

    print()
    print("The child looked at the king.")
    print("The king was dressed.")
    print("The root CA was in the trust store.")
    print("The chain resolved.")
    print("Everyone, at last, agreed.")
```

-----

## The Difference in One Table

|Property                  |Self-signed (Episodes 01-04)   |CA Hierarchy (Episode 05)   |
|--------------------------|-------------------------------|----------------------------|
|Subject == Issuer         |Yes                            |No (except root CA)         |
|Trust store entry required|Yes, the cert itself           |Only the root CA            |
|Browser accepts by default|No                             |Yes (once root is imported) |
|Revocable                 |Only by removing from whitelist|Via CRL or OCSP             |
|Appropriate for production|No                             |Yes (if root is external CA)|
|What the child says       |“He has no clothes”            |“He is properly dressed”    |

-----

## Importing Your Root CA for Local Development

If you want a browser to trust your local development hierarchy, import only `root_cert.pem` into the OS or browser trust store. On macOS: Keychain Access. On Windows: Certificate Manager (`certmgr.msc`). On Linux: `update-ca-certificates`. The leaf certificate is never imported directly.

Tools like [mkcert](https://github.com/FiloSottile/mkcert) automate exactly this workflow for development teams.

-----

## Series Complete

|Episode|Title                  |Lesson                                                  |
|-------|-----------------------|--------------------------------------------------------|
|01     |The King’s Proclamation|Self-signed means the subject is also the issuer        |
|02     |The Royal Wardrobe     |The RSA private key is the invisible cloth              |
|03     |The King’s Portrait    |Subject, issuer, SAN, and BasicConstraints              |
|04     |The Grand Parade       |Complete assembly, signing, and serialisation           |
|05     |The Child Speaks       |Why browsers reject and how CA hierarchies restore trust|

The king was naked all along. That was fine – in his private chambers, for development purposes only. The moment he rode into production, the child spoke. Now you know what she was saying, and how to give the king some actual clothes.

-----

## References

- [bloodearnest/selfsigned.py](https://gist.github.com/bloodearnest/9017111a313777b9cce5)
- [cryptography.io: Creating a CA hierarchy](https://cryptography.io/en/latest/x509/tutorial/#creating-a-ca-hierarchy)
- [cryptography.io: X.509 Verification](https://cryptography.io/en/latest/x509/verification/)
- [mkcert: locally trusted development certificates](https://github.com/FiloSottile/mkcert)
