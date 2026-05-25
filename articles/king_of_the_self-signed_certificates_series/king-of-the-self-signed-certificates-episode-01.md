---
title: "The King of the Self-signed Certificates - Ep. 01"
description: "A self-signed certificate is a royal decree the king writes, seals, and signs himself. Learn what it really is and when it belongs on the throne – and when it does not."
tags: [python, security, cryptography, tls]
cover_image: <https://raw.githubusercontent.com/vanHeemstraPublications/covers/main/king-self-signed-episode-01.png>
canonical_url: ""
series: "The King of the Self-signed Certificates"
part: 1
published: false
organization: "the-software-s-journey"
---
 
# The King’s Proclamation

> *In a faraway kingdom, a king sat upon his throne and declared himself dressed in the finest garments ever woven. The tailors had promised him that only the wise and worthy could see the cloth. And so the entire court agreed: magnificent robes, Your Majesty. Magnificent robes.*

A self-signed certificate is exactly that king.

It arrives dressed in the full regalia of TLS: a subject name, an issuer name, a public key, a validity window, a digital signature. To a casual glance, it looks every bit as legitimate as a certificate signed by a trusted Certificate Authority. The court bows.

But the browser knows. The operating system’s trust store knows. And eventually – sometimes loudly, in the form of a red warning page – the child in the crowd speaks up.

-----

## SIPOC

|Suppliers                               |Inputs                         |Process                                                 |Outputs                                                 |Customers                                          |
|----------------------------------------|-------------------------------|--------------------------------------------------------|--------------------------------------------------------|---------------------------------------------------|
|Python `cryptography` library           |Hostname, optional IP addresses|Generate key pair; build certificate identity; self-sign|`.pem` certificate + private key                        |Developer testing environments, local HTTPS servers|
|Developer’s own machine                 |Validity period (days)         |Encode and persist to disk                              |Human-readable understanding of what “self-signed” means|Engineers learning TLS fundamentals                |
|Hans Christian Andersen (metaphorically)|Naked trust model              |Reveal the emperor’s new clothes                        |Informed decision to use or refuse self-signed certs    |Security reviewers, auditors                       |

-----

## What a Certificate Really Is

A certificate is a data structure that binds a public key to an identity. That identity is described using an **X.509 Distinguished Name** – a set of attributes including:

- `COUNTRY_NAME`
- `STATE_OR_PROVINCE_NAME`
- `ORGANIZATION_NAME`
- `COMMON_NAME` (the domain or hostname)

Normally, a trusted third party – a **Certificate Authority** (CA) – inspects your request, verifies you control the domain, and then signs the certificate with *their* private key. Every browser ships with a list of trusted CA public keys. When your browser sees a certificate signed by one of them, the chain is complete and the robes appear real.

A **self-signed** certificate skips the CA entirely. The subject and the issuer are the same entity. The king validates his own wardrobe.

```python
# The fundamental self-signed paradox, expressed in Python:
# subject == issuer
# The king signs his own certificate of kingship.

subject = issuer = "The Kingdom of localhost"
```

This is not fraud. It is just nakedness declared as clothing.

-----

## When the King’s Wardrobe Is Acceptable

The king’s nakedness is perfectly fine in his private chambers. Self-signed certificates are appropriate when:

- You are running **local development** servers (`localhost`, `127.0.0.1`)
- You control both ends of a connection and can distribute trust out-of-band
- You need TLS encryption but not third-party identity verification
- You are running automated tests that need HTTPS without hitting a real CA

The wardrobe fails in public. In production, where browsers and clients you do not control must trust your certificate, a CA-signed cert is required.

-----

## The Series Ahead

This series builds the complete picture, episode by episode:

|Episode|Title                  |Theme                                             |
|-------|-----------------------|--------------------------------------------------|
|01     |The King’s Proclamation|What self-signed means and when it applies        |
|02     |The Royal Wardrobe     |Generating the RSA private key                    |
|03     |The King’s Portrait    |Building the certificate identity                 |
|04     |The Grand Parade       |Signing, serialising, and writing to disk         |
|05     |The Child Speaks       |Trust chains, browser warnings, and CA hierarchies|

In the next episode, we start cutting the invisible fabric: generating the private key that makes the whole illusion possible.

-----

## References

- [bloodearnest/selfsigned.py](https://gist.github.com/bloodearnest/9017111a313777b9cce5) – the compact self-signed gist this series builds on
- [cryptography.io X.509 Tutorial](https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate) – the official modern reference
