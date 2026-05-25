---
title: "The King of the Self-signed Certificates - Ep. 02"
description: "Before the king can dress himself in a self-signed certificate, the tailors must cut the invisible cloth – a 2048-bit RSA private key. Here is how they do it in Python."
tags: [python, security, cryptography, tls]
cover_image: <https://raw.githubusercontent.com/vanHeemstraPublications/covers/main/king-self-signed-episode-02.png>
canonical_url: ""
series: "The King of the Self-signed Certificates"
part: 2
published: false
organization: "the-software-s-journey"
---

# The Royal Wardrobe

> *The tailors arrived at the palace carrying nothing at all. “We work with a very special thread,” they announced. “It is invisible to fools. Only the wise can see it.” The king nodded gravely. “Then begin at once.”*

Before the king can parade in his magnificent certificate, the tailors must produce the raw material: a **private key**. This is the foundational secret that everything else rests on. It is the loom on which the invisible cloth is woven.

In Python, the `cryptography` library generates an RSA private key in a single call. The key is born immediately, entirely on your machine, with no CA, no registry, no ceremony.

-----

## SIPOC

|Suppliers                                                                      |Inputs                                      |Process                                                       |Outputs                             |Customers                                    |
|-------------------------------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------|------------------------------------|---------------------------------------------|
|Python `cryptography` library (`cryptography.hazmat.primitives.asymmetric.rsa`)|`public_exponent` (65537), `key_size` (2048)|`rsa.generate_private_key()`                                  |`RSAPrivateKey` object in memory    |Certificate builder in Episode 03            |
|Operating system entropy source                                                |System randomness                           |OS PRNG feeds key generation                                  |PEM-encoded private key file on disk|Any TLS-capable server (Flask, FastAPI, etc.)|
|Developer                                                                      |Decision: passphrase or no passphrase       |Serialisation with `BestAvailableEncryption` or `NoEncryption`|`key.pem`                           |Deployment pipeline                          |

-----

## Generating the Key

```python
# episode_02_royal_wardrobe.py
# The tailors cut the invisible cloth: generating an RSA private key.

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_private_key(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """
    Generate an RSA private key.

    The king orders his tailors to begin. The cloth is cut from
    pure mathematical entropy -- invisible, weightless, and completely
    without external validation.

    Args:
        key_size: Bit length of the key. 2048 is the accepted minimum
                  for development purposes. The key never leaves the
                  machine that generates it.

    Returns:
        An RSAPrivateKey object. The raw cloth, not yet cut into robes.
    """
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    return key


def persist_key(
    key: rsa.RSAPrivateKey,
    path: str,
    passphrase: bytes | None = None,
) -> None:
    """
    Write the private key to disk in PEM format.

    The king's most prized possession is locked in the royal vault.
    If a passphrase is provided, the key is encrypted at rest.
    Without one, the vault door is open -- fine for local testing,
    dangerous anywhere else.

    Args:
        key:        The RSAPrivateKey to serialise.
        path:       File path for the .pem output.
        passphrase: Optional bytes passphrase. None means no encryption.
    """
    if passphrase:
        encryption = serialization.BestAvailableEncryption(passphrase)
    else:
        # NoEncryption: the vault door stands open.
        # Acceptable in development. Catastrophic in production.
        encryption = serialization.NoEncryption()

    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=encryption,
    )

    with open(path, "wb") as f:
        f.write(key_pem)

    print(f"Private key written to: {path}")


# -------------------------------------------------------------------
# Main: run the wardrobe sequence
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("The tailors arrive at the palace...")

    key = generate_private_key(key_size=2048)
    print(f"Key generated. Public exponent: {key.public_key().public_numbers().e}")
    print(f"Key size: {key.key_size} bits")

    persist_key(key, "key.pem")
    print("The cloth is woven. The king is almost dressed.")
```

-----

## What Just Happened

Two mathematical objects were created in memory:

**Private key** – a large secret integer. Only this machine knows it. It will be used to sign the certificate and to decrypt data sent to this server. If it leaks, the entire kingdom falls.

**Public key** – derived from the private key via modular arithmetic. It can be shared freely. Anyone can use it to verify a signature made by the private key, or to encrypt a message only the private key can decrypt.

The `public_exponent=65537` is a standard choice: a Fermat prime (2^16 + 1) that balances computation speed with security. It is not a magic number the tailors invented – it is the result of decades of cryptographic practice.

-----

## The Wardrobe Warning

The original gist carries a comment that deserves to be read aloud in the throne room:

```
# WARNING: the code in the gist generates self-signed certs,
# for the purposes of testing in development.
# Do not use these certs in production, or You Will Have A Bad Time.
```

The king may believe his robes are magnificent. The browser does not.

-----

## What the Key Is Not

The key alone is not a certificate. It is not a claim of identity. It is not trusted by anyone. It is pure mathematical potential – the loom, the thread, the invisible cloth. The robes still need to be sewn, fitted, and declared royal by someone. In a self-signed world, the king declares it himself.

That declaration happens in Episode 03: The King’s Portrait.

-----

## References

- [bloodearnest/selfsigned.py](https://gist.github.com/bloodearnest/9017111a313777b9cce5)
- [cryptography.io: Creating a self-signed certificate](https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate)
- [cryptography.io: RSA key generation](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
