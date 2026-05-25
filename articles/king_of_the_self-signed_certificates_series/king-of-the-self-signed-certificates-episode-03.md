---
title: "The King of the Self-signed Certificates - Ep. 03"
description: "The king commissions his own portrait. In X.509 terms, this means defining the subject name and the issuer name – and in a self-signed certificate, they are the same person."
tags: [python, security, cryptography, x509]
cover_image: <https://raw.githubusercontent.com/vanHeemstraPublications/covers/main/king-self-signed-episode-03.png>
canonical_url: ""
series: "The King of the Self-signed Certificates"
part: 3
published: false
organization: "the-software-s-journey"
---

# The King’s Portrait

> *The court painter was summoned. “Paint me,” said the king, “in the finest robes ever seen. And when you are done, sign it with my seal. I will declare the portrait authentic myself.”*
> 
> *The painter raised an eyebrow. “You wish me to paint you, and then you will authenticate the painting yourself?”*
> 
> *“That is correct,” said the king. “I am, after all, the only authority I trust.”*

This is the precise logical structure of a self-signed certificate.

In standard X.509 architecture, a certificate has two distinct parties:

- The **subject** – the entity being described (“this is the key for `mysite.com`”)
- The **issuer** – the entity that vouches for the subject (“and we, Let’s Encrypt, confirm it”)

In a self-signed certificate, subject and issuer are the same. The king paints his own portrait and stamps it with his own seal.

-----

## SIPOC

|Suppliers                         |Inputs                                                                                       |Process                         |Outputs                               |Customers                                               |
|----------------------------------|---------------------------------------------------------------------------------------------|--------------------------------|--------------------------------------|--------------------------------------------------------|
|`cryptography.x509` and `NameOID` |`COUNTRY_NAME`, `STATE_OR_PROVINCE_NAME`, `LOCALITY_NAME`, `ORGANIZATION_NAME`, `COMMON_NAME`|`x509.Name([...])`              |`x509.Name` object (subject = issuer) |`CertificateBuilder` in Episode 04                      |
|Developer                         |Hostname or domain string                                                                    |Set `COMMON_NAME` to hostname   |Named identity embedded in certificate|TLS handshake validation                                |
|`SubjectAlternativeName` extension|DNS names, IP addresses                                                                      |`x509.DNSName`, `x509.IPAddress`|SAN extension attached to cert        |Modern browsers and TLS clients (they check SAN, not CN)|

-----

## Building the Identity

```python
# episode_03_kings_portrait.py
# The court painter works: defining subject, issuer, and extensions.

import ipaddress
import datetime

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa


def build_name(
    hostname: str,
    country: str = "NL",
    state: str = "Noord-Brabant",
    locality: str = "Eersel",
    organisation: str = "The Kingdom of Localhost",
) -> x509.Name:
    """
    Build an X.509 Distinguished Name.

    The court painter captures the king's likeness. Every attribute
    is a brushstroke: country, state, city, organisation, and finally
    the COMMON_NAME -- the most important detail, the face on the portrait.

    For a self-signed certificate, this same Name is used as *both*
    the subject (who this cert describes) and the issuer (who signed it).
    The king commissions and authenticates his own portrait.

    Args:
        hostname:     The CN -- typically the domain or IP this cert serves.
        country:      Two-letter ISO country code.
        state:        Full state or province name.
        locality:     City or locality.
        organisation: Org name embedded in the cert.

    Returns:
        An x509.Name object ready for use as subject and issuer.
    """
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organisation),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])


def build_san(
    hostname: str,
    ip_addresses: list[str] | None = None,
) -> x509.SubjectAlternativeName:
    """
    Build a SubjectAlternativeName (SAN) extension.

    Modern browsers do not trust COMMON_NAME alone. They require
    the SAN extension to list the valid hostnames and IPs.
    This is the detail the original court painter forgot --
    the browsers noticed, even if the court did not.

    Best practice: always include the hostname in the SAN.
    The COMMON_NAME is then redundant but harmless.

    Args:
        hostname:     Primary DNS name for the certificate.
        ip_addresses: Optional list of IP address strings to include.

    Returns:
        An x509.SubjectAlternativeName extension value.
    """
    alt_names: list[x509.GeneralName] = [x509.DNSName(hostname)]

    if ip_addresses:
        for addr in ip_addresses:
            # DNSName form: for older OpenSSL compatibility
            alt_names.append(x509.DNSName(addr))
            # IPAddress form: required by Go's crypto/tls and modern clients
            alt_names.append(x509.IPAddress(ipaddress.ip_address(addr)))

    return x509.SubjectAlternativeName(alt_names)


def build_basic_constraints(is_ca: bool = True) -> x509.BasicConstraints:
    """
    Build the BasicConstraints extension.

    path_length=0 means this certificate may sign only itself,
    not intermediate or leaf certificates. The king rules his
    own kingdom, but cannot appoint sub-kings with signing authority.

    Args:
        is_ca: Whether to mark this cert as a CA certificate.

    Returns:
        An x509.BasicConstraints extension value.
    """
    return x509.BasicConstraints(ca=is_ca, path_length=0)


# -------------------------------------------------------------------
# Main: compose the portrait
# -------------------------------------------------------------------
if __name__ == "__main__":
    hostname = "localhost"
    ip_addresses = ["127.0.0.1"]

    name = build_name(hostname)
    san = build_san(hostname, ip_addresses)
    basic_constraints = build_basic_constraints()

    print("The portrait is composed.")
    print(f"Subject / Issuer CN: {hostname}")
    print(f"SAN DNS names:  {[entry.value for entry in san if isinstance(entry, x509.DNSName)]}")
    print(f"SAN IP addresses: {ip_addresses}")
    print(f"BasicConstraints CA: {basic_constraints.ca}, path_length: {basic_constraints.path_length}")
    print()
    print("Note: in a self-signed certificate, subject == issuer.")
    print("The king commissions and authenticates his own portrait.")
```

-----

## The Subject-Issuer Paradox

In the code above, the same `name` object will be passed to both `.subject_name(name)` and `.issuer_name(name)` in the certificate builder. This is the naked truth of a self-signed certificate, expressed without ceremony:

```python
# The self-signed tautology:
subject = issuer = build_name("localhost")
```

A CA-signed certificate would have `issuer` pointing to the CA’s distinguished name – Let’s Encrypt, DigiCert, or your corporate PKI root. That CA’s name is in the trust store of every client. The chain is external and verifiable.

Here, the chain loops back to the king himself. He wrote the letter, sealed the letter, and also wrote the letter of reference confirming his letter is trustworthy.

-----

## Why SAN Matters More Than You Think

The `COMMON_NAME` field was once the field browsers used to validate the hostname. That era ended. Modern TLS clients – all browsers, Go’s `crypto/tls`, Python’s `ssl` module – require the **SubjectAlternativeName** extension to contain the hostname or IP. The `COMMON_NAME` is now largely decorative, like the flourish on a royal monogram.

The original gist captured this nuance in a comment:

```
# best practice seem to be to include the hostname in the SAN,
# which *SHOULD* mean COMMON_NAME is ignored.
```

If you omit the SAN, modern clients will reject the certificate – not because the king is naked, but because he forgot to include his address on the invitation.

-----

## Next: The Grand Parade

The portrait is painted. The name is set. Subject and issuer are one. Now comes the spectacle: building, signing, and writing the certificate to disk. The court lines the streets. The parade begins in Episode 04.

-----

## References

- [bloodearnest/selfsigned.py](https://gist.github.com/bloodearnest/9017111a313777b9cce5)
- [cryptography.io: X.509 Tutorial](https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate)
- [RFC 5280: Internet X.509 PKI Certificate Profile](https://datatracker.ietf.org/doc/html/rfc5280)
