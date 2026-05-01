---
title: "Globetrotters Identity and Access Management 🌍 Ep.7"
part: 7
published: false
description: "Episode 7: A visa in a plastic bag is not a visa. The seal matters. PKI — Public Key Infrastructure — is the seal system that makes every certificate in ACME’s IAM stack trustworthy. TLS encrypts the channel. mTLS verifies both sides. The ACME Root CA is the authority whose seal makes everything valid."
tags: [iam, pki, tls, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters_identity_and_access_management_series/globetrotters-identity-and-access-management-episode-07.png"
series: "Globetrotters Identity and Access Management Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: Sealed Diplomatic Pouches

> *“A diplomatic pouch is not valuable because of the bag. It is valuable because of the seal — the tamper-evident, cryptographically verifiable mark that says a trusted authority prepared this, and nobody opened it in transit.”*

-----

## The Seal That Makes Everything Real 🔏

All previous episodes have been about identity claims: who you say you are, what groups you belong to, what stamps you carry. Every one of those claims is meaningless unless the documents carrying them cannot be forged.

A passport without a holographic seal can be printed at home. A visa stamp without a verified ink pattern is just a rubber impression. The entire border control system rests, ultimately, on the assumption that the documents are genuine — that a trusted authority produced them, and that the document has not been tampered with since.

**Public Key Infrastructure (PKI)** is how digital systems solve the same problem. X.509 certificates are the digital equivalent of tamper-evident documents. The Certificate Authority (CA) is the national printing office. TLS is the sealed diplomatic pouch. mTLS is a protocol where both the courier and the recipient show their sealed documents to each other before exchanging anything.

ACME’s PKI sits underneath every secure connection in the IAM topology — LDAPS connections to LDAP LB-T, mTLS to the SUT, OAuth to RWT. Understanding PKI means understanding the foundation that every other security control depends on.

-----

## 🗂️ SIPOC — Sealed Diplomatic Pouches

|**Suppliers**                |**Inputs**                                                               |**Process**                                                                            |**Outputs**                                                        |**Customers**                                                                                            |
|-----------------------------|-------------------------------------------------------------------------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
|ACME Root CA                 |Certificate Signing Request (CSR) from Keyfactor CA                      |Root CA signs the Intermediate CA certificate                                          |Trusted Intermediate CA certificate                                |Every system that trusts the ACME Root CA automatically trusts certificates signed by the Intermediate CA|
|Keyfactor CA (Intermediate)  |CSR from a service (LDAP server, our Test Factory client)                |Intermediate CA signs the end-entity certificate                                       |X.509 certificate: subject, public key, validity, SAN, CA signature|The certificate holder — presents this cert during TLS/mTLS handshakes                                   |
|TLS client (Test Factory)    |Server’s certificate chain (LDAP LB-T cert → Keyfactor CA → ACME Root CA)|Verify: is the chain intact? Is the Root CA trusted? Is the cert valid and not revoked?|Trust decision: proceed or abort                                   |LDAP session — proceeds only if verification passes                                                      |
|mTLS participant (both sides)|Both server cert and client cert                                         |Each side verifies the other’s certificate chain against the trusted Root CA           |Mutual authentication: both parties cryptographically verified     |The protected channel — neither side proceeds without the other’s verification                           |

-----

## The Certificate Chain: Passport → Issuing Office → Ministry 📜

An X.509 certificate chain works exactly like the trail of authority on a government document:

```
ACME Root CA                           ← The national printing office
  (self-signed, highly protected)        Trusted by all ACME systems

  └── Keyfactor Intermediate CA         ← The regional issuing office
        (signed by ACME Root CA)          Issues certificates for specific purposes

      └── LDAP LB-T Server Certificate  ← The individual document
            (signed by Keyfactor CA)      Presented during TLS handshake

      └── VFab Client Certificate       ← Our Test Factory's identity document
            (signed by Keyfactor CA)      Presented during mTLS handshake
```

The verification process is a chain-of-custody check:

1. The LDAP LB-T server presents its certificate
1. Our client checks: is this cert signed by a CA it trusts?
1. It follows the chain: LDAP server cert → signed by Keyfactor CA → signed by ACME Root CA
1. Is ACME Root CA in our local trust store? If yes: chain verified
1. Is the cert valid today (not expired)? Is it revoked? Does the hostname match?
1. If all checks pass: TLS proceeds

-----

## TLS: The Sealed Pouch on Every LDAPS Connection 🔐

**Transport Layer Security (TLS)** is the protocol that encrypts the LDAP session between our solution and LDAP LB-T. It provides:

|Property       |What it means                                                                 |Border analogy                                   |
|---------------|------------------------------------------------------------------------------|-------------------------------------------------|
|Confidentiality|The LDAP traffic (bind DN, password, search results) cannot be read in transit|The pouch is sealed — nobody reads it en route   |
|Integrity      |Any modification to the data in transit is detectable                         |Tamper-evident seal — if opened, it shows        |
|Authentication |The server presents a certificate; the client verifies its identity           |The courier presents their diplomatic credentials|

### The TLS handshake for LDAPS connections

```
Test Factory client                    LDAP LB-T server

ClientHello (supported cipher suites) ─────────────────►

                                       ServerHello (chosen cipher)
                              ◄─────── Certificate (LDAP LB-T cert chain)
                                       ServerHelloDone

Verify certificate chain:
  LDAP LB-T cert → Keyfactor CA → ACME Root CA
  Is ACME Root CA in trust store? ✓
  Is cert valid today? ✓
  Does Subject Alternative Name include ldap-lb-t.gmf.acme.com? ✓

ClientKeyExchange (key material) ──────────────────────►
ChangeCipherSpec ──────────────────────────────────────►
Finished ──────────────────────────────────────────────►

                              ◄─────── ChangeCipherSpec
                              ◄─────── Finished

[ TLS session established — all subsequent LDAP traffic encrypted ]
```

If the certificate chain fails to verify — wrong CA, expired cert, hostname mismatch — the TLS handshake aborts. The LDAP session never opens. This is the first line of defence against connection to a rogue LDAP server.

-----

## mTLS: Both Sides Show Their Credentials 🤝

**Mutual TLS (mTLS)** extends TLS by requiring the *client* to also present a certificate, not just the server. Both parties authenticate cryptographically. Neither trusts the other without verifiable proof.

In the border analogy: this is not just the traveller showing their passport to the officer. The officer also shows *their* credentials to the traveller, and both verify the other’s documents are genuine before exchanging anything.

```
Test Factory client                    Protected SUT (mTLS)

ClientHello ──────────────────────────────────────────►

                                       ServerHello
                              ◄─────── Certificate (SUT cert chain)
                              ◄─────── CertificateRequest ← NEW in mTLS

Verify server certificate:
  SUT cert → Keyfactor CA → ACME Root CA ✓

Certificate (VFab client cert chain) ──────────────────►

                                       Verify client certificate:
                                       VFab cert → Keyfactor CA → ACME Root CA ✓

[ Mutual authentication complete — both parties verified ]
[ mTLS session established — encrypted, bidirectionally authenticated ]
```

### Why mTLS matters for the Test Factory

For connections to the System Under Test (SUT), mTLS provides a level of assurance that Bearer tokens alone cannot: the SUT knows not just *who* the caller claims to be (via the token) but *that the caller is cryptographically who they claim to be* (via the client certificate). A stolen token presented from an unknown client is rejected at the mTLS layer — the caller cannot present the correct client certificate.

This directly connects to ACME’s PKI design: the same Keyfactor-issued certificates that our Test Factory presents to the SUT for mTLS can authenticate our workloads to the LDAP infrastructure, provided the LDAP servers trust the Keyfactor CA chain.

-----

## The Three Certificate Use Cases in ACME’s IAM Topology 📋

|Connection        |Certificate type                              |Trust chain                                                                |Used for                                                  |
|------------------|----------------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------|
|LDAPS to LDAP LB-T|Server certificate (one-way TLS)              |ACME Root CA → LDAP LB-T server cert                                       |Encrypts the LDAP channel; client verifies server identity|
|mTLS to SUT       |Client certificate (mutual TLS)               |ACME Root CA → Keyfactor CA → VFab client cert                             |Client authenticates to SUT; SUT verifies client identity |
|HTTPS to RWT      |Server certificate (one-way TLS) + client auth|ACME Root CA → RWT server cert; client uses client_id/secret or client cert|OAuth token request; encrypts the credential exchange     |

-----

## The ACME Root CA: The Printing Office 🏛️

The ACME Root CA is the top of the trust hierarchy. Its certificate is self-signed (it vouches for itself) and is installed in the trust store of every system in ACME’s infrastructure. If you trust the ACME Root CA, you automatically trust any certificate signed by a CA it has signed.

Key properties of the Root CA:

- **Offline / highly protected**: the Root CA private key is typically stored in an HSM (Hardware Security Module) and kept offline except when signing Intermediate CA certificates
- **Long validity period**: Root CA certificates are typically valid for 10–20 years
- **Never issued directly to end entities**: the Root CA only signs Intermediate CA certificates; end-entity certificates come from the Intermediate CAs

The Root CA’s public certificate must be installed in our Test Factory solution’s trust store before any TLS connection to ACME infrastructure is possible. Without it, every LDAPS connection to LDAP LB-T will fail with a certificate verification error.

-----

## Keyfactor: The Certificate Issuing Authority 🏢

Keyfactor is ACME’s intermediate CA — the regional issuing office that handles the day-to-day issuance of certificates to servers and clients. It sits below the ACME Root CA:

```
ACME Root CA (offline, HSM-protected)
    │
    └── Keyfactor CA (online, operational)
            │
            ├── LDAP LB-T server certificate
            ├── RWT PRD server certificate
            ├── IDV PRD server certificate
            └── VFab client certificate (our Test Factory's identity)
```

The Keyfactor CA is the entity our team interacts with when obtaining certificates. The process:

1. Generate a private key (stays in our control — never sent to Keyfactor)
1. Generate a Certificate Signing Request (CSR) from the private key
1. Submit the CSR to Keyfactor (via API, web interface, or automated pipeline)
1. Keyfactor signs the CSR and returns the certificate
1. Our solution presents this certificate during mTLS handshakes

-----

## Certificate Validation at Runtime: What Our Solution Must Check 🔍

Every TLS connection our solution makes must include certificate validation. A solution that skips verification (`InsecureSkipVerify: true` in Go, or similar in other languages) is connecting to an unverified server — equivalent to accepting any visa without checking the seal.

Minimum validation our Test Factory connection code must perform:

```python
import ssl
import ldap3

# Load the ACME Root CA certificate (required)
tls_config = ldap3.Tls(
    ca_certs_file="/etc/ssl/acme/acme-root-ca.crt",
    validate=ssl.CERT_REQUIRED,            # reject invalid certs
    version=ssl.PROTOCOL_TLS_CLIENT,
    check_hostname=True,                   # hostname must match cert SAN
)

server = ldap3.Server(
    "ldap-lb-t.gmf.acme.com",
    port=636,
    use_ssl=True,
    tls=tls_config,
)
```

If `validate=ssl.CERT_NONE` is used, certificate errors are silently ignored. This means our solution cannot distinguish between the real LDAP LB-T and a malicious server presenting a self-signed certificate.

-----

## Certificate Lifecycle: Renewal Before Expiry ⏱️

Certificates have a validity period. The LDAP LB-T server certificate might be valid for one year. Our VFab client certificate might be valid for two years. When they expire:

- LDAPS connections to LDAP LB-T fail immediately (server cert expired)
- mTLS connections from our solution to the SUT fail immediately (client cert expired)

Certificate expiry is an operational concern that must be tracked and actioned before the expiry date. ACME’s Keyfactor CA typically provides notifications before expiry and supports automated renewal via ACME protocol or Keyfactor’s own API.

For the Test Factory, the certificates to monitor are:

- VFab client certificate (issued by Keyfactor, held by our solution)
- ACME Root CA certificate (in our trust store — very long validity, but must be checked)

-----

## PKI and the Full IAM Stack: The Thread That Holds It Together 🧵

Every secure connection in ACME’s IAM topology depends on PKI:

```
SailPoint PRD ──HTTPS/mTLS──► RWT PRD        (ACME CA → RWT server cert)
RWT PRD       ──HTTPS/mTLS──► IDV PRD        (ACME CA → IDV server cert)
IDV PRD       ──LDAPS───────► LDAP LB-T      (ACME CA → LDAP LB-T cert)
LDAP LB-T     ──TCP─────────► AUTH GMF PRD   (internal, may be unencrypted on private segment)
Test Factory  ──LDAPS───────► LDAP LB-T      (ACME CA → LDAP LB-T cert; our trust store)
Test Factory  ──mTLS────────► SUT            (ACME CA → Keyfactor → VFab client cert)
```

Without the ACME Root CA in every trust store, these connections cannot be established. Without Keyfactor issuing valid certificates to every server and client, every handshake fails. PKI is the prerequisite for everything else.

-----

In **Episode 8**, we bring everything together at the dedicated test lane: the complete Test Factory entry flow, the choice between direct LDAP and OAuth, the implementation details, and the operational runbook for maintaining secure LDAP LB-T connectivity.

-----

**🔗 Resources**

- **X.509 certificate standard**: [rfc-editor.org/rfc/rfc5280](https://www.rfc-editor.org/rfc/rfc5280)
- **TLS 1.3 RFC 8446**: [rfc-editor.org/rfc/rfc8446](https://www.rfc-editor.org/rfc/rfc8446)
- **Mutual TLS explained**: [cloudflare.com/learning/access-management/what-is-mutual-tls](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/)
- **Keyfactor Certificate Authority**: [keyfactor.com](https://www.keyfactor.com)

-----

*🌍 Globetrotters Identity and Access Management Series — crossing the IAM border one checkpoint at a time.*
