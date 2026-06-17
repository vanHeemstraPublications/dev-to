---
title: "REST with step-ca 🔐 Ep.1"
published: false
description: "Episode 1: step-ca is a private Certificate Authority that speaks plain HTTPS. You can curl it, script it, and wrap it in a Python class. This episode introduces step-ca, explains why a REST interface beats shelling out to the CLI, surveys the full HTTP API surface with architecture diagrams, and spins up a local CA in Docker — ready for the eight-episode Python integration journey ahead."
tags: [python, security, certificates, devops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/rest-with-step-ca-episode-01.png"
series: "REST with step-ca
canonical_url: ""
organization: "the-software-s-journey
part: 1
---

## Episode 1: The CA That Answers HTTP Calls

-----

## A Certificate Authority That Speaks HTTP

Most internal Certificate Authorities are opaque black boxes. You install them once, configure them by hand, and interact through a vendor-specific GUI or a CLI tool that only works on the same machine the CA runs on. Integrating them into automation means shelling out, parsing text output, and hoping the CLI flags do not change between versions.

**step-ca** is different. From Smallstep (`github.com/smallstep/certificates`), step-ca is an open-source, online Certificate Authority that exposes a clean HTTPS REST API. Every certificate operation — health checks, listing provisioners, signing CSRs, renewing, revoking — is an HTTP call. It runs in Docker, works with the `step` CLI, and works equally well with `curl`, `requests`, `httpx`, or any HTTP library in any language.

This series builds `StepCAClient` — a Python class that wraps that REST API completely. No subprocess calls. No `shell=True`. No fragile text parsing. Pure HTTP against a well-defined JSON API.

Eight episodes. One class. Complete certificate lifecycle management in Python.

-----

## 🗂️ SIPOC — The Series at a Glance

|**Suppliers**            |**Inputs**                                           |**Process**                                                                |**Outputs**                                               |**Customers**                                         |
|-------------------------|-----------------------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------|------------------------------------------------------|
|step-ca server           |Running CA on HTTPS, JWK provisioner configured      |Python `httpx` calls; JSON request/response bodies                         |X.509 certificates, renewal confirmations, revocation acks|Any Python application needing private CA certificates|
|`cryptography` library   |Key type, subject name, SANs                         |Generate EC/RSA private key; build and sign a PKCS#10 CSR                  |PEM-encoded CSR ready for `/1.0/sign`                     |Signing step — submitted to step-ca                   |
|`python-jose` JWT library|JWK private key, provisioner name, subject           |Build JWT payload; sign with EC JWK key                                    |One-time-use signed JWT (the `ott` field)                 |`/1.0/sign` endpoint — validates before signing CSR   |
|`StepCAClient`           |CA URL, root fingerprint, provisioner name + password|Orchestrate: get key → decrypt → sign JWT → generate CSR → POST → save cert|Signed X.509 certificate ready for TLS                    |Web servers, gRPC services, mTLS clients              |

-----

## System Architecture: The Three-Layer Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      YOUR INFRASTRUCTURE                            │
│                                                                     │
│  ┌──────────────────────┐        ┌──────────────────────────────┐  │
│  │   Python Application │        │   step-ca Server             │  │
│  │                      │        │   (Docker / bare metal)      │  │
│  │  ┌────────────────┐  │        │                              │  │
│  │  │ StepCAClient   │  │ HTTPS  │  ┌────────────────────────┐ │  │
│  │  │                │◄─┼────────┼─►│  REST API  :9000       │ │  │
│  │  │  health()      │  │  JSON  │  │  /health               │ │  │
│  │  │  get_roots()   │  │        │  │  /roots                │ │  │
│  │  │  list_prov()   │  │        │  │  /provisioners         │ │  │
│  │  │  sign()        │  │        │  │  /provisioners/{kid}/  │ │  │
│  │  │  renew()       │  │        │  │    encrypted-key       │ │  │
│  │  │  revoke()      │  │        │  │  /1.0/sign             │ │  │
│  │  └────────────────┘  │        │  │  /1.0/renew            │ │  │
│  │                      │        │  │  /1.0/revoke           │ │  │
│  │  Libraries used:     │        │  └───────────┬────────────┘ │  │
│  │  - httpx (HTTP)      │        │              │              │  │
│  │  - cryptography(CSR) │        │  ┌───────────▼────────────┐ │  │
│  │  - python-jose (JWT) │        │  │  Authority (Go)        │ │  │
│  │  - jwcrypto (JWE)    │        │  │  Intermediate CA Key   │ │  │
│  └──────────────────────┘        │  │  JWK Provisioner       │ │  │
│                                   │  │  BadgerDB / MySQL      │ │  │
│  ┌──────────────────────┐        │  └────────────────────────┘ │  │
│  │   Root CA Trust      │        │                              │  │
│  │   root_ca.crt        │        │  ┌────────────────────────┐ │  │
│  │   (PEM on disk)      │        │  │  Root CA (offline)     │ │  │
│  │   Used by httpx to   │        │  │  root_ca.crt           │ │  │
│  │   verify CA's TLS    │        │  │  intermediate_ca.crt   │ │  │
│  └──────────────────────┘        │  └────────────────────────┘ │  │
│                                   └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

The Python client and step-ca server communicate over HTTPS. The client verifies the server’s certificate using the root CA certificate it bootstrapped at startup. Every request after bootstrapping is mutually authenticated through the root of trust.

-----

## The HTTP API Endpoint Map

```
step-ca REST API
Base URL: https://ca.internal:9000

READ OPERATIONS (no auth required beyond root trust)
─────────────────────────────────────────────────────
  GET  /health                      → {"status":"ok"}
  GET  /roots                       → {"crts":["-----BEGIN CERT..."]}
  GET  /provisioners                → {"provisioners":[...]}
  GET  /provisioners/{kid}/         → {"key":"<JWE compact>"}
       encrypted-key

WRITE OPERATIONS (require signed JWT "ott")
─────────────────────────────────────────────────────
  POST /1.0/sign                    body: {csr, ott}
       → {crt, ca, certChain}       Requires: valid one-time JWT

  POST /1.0/revoke                  body: {serial, reasonCode,
       → {"status":"ok"}                   reason, ott}
                                    OR: present cert via mTLS

mTLS OPERATIONS (require presenting a valid cert as client cert)
─────────────────────────────────────────────────────
  POST /1.0/renew                   No body
       → {crt, ca, certChain}       Auth: existing cert as TLS client cert

ACME (for ACME provisioner)
─────────────────────────────────────────────────────
  GET  /acme/{provisioner}/directory → ACME directory JSON
  (Full ACMEv2 RFC 8555 protocol from there)
```

-----

## What step-ca Is — and Is Not

```
IS:                                    IS NOT:
────────────────────────────────────  ────────────────────────────────────
✓ An online intermediate CA           ✗ A full enterprise PKI platform
✓ Clean REST API with JSON            ✗ A certificate history/audit UI
✓ JWK, ACME, OIDC, cloud providers   ✗ Full CRL / OCSP support (limited)
✓ Short-lived cert automation         ✗ Certificate Transparency log support
✓ Runs in Docker, single binary       ✗ Dynamic SCEP (Intune/Jamf)
✓ SSH cert support (bonus)            ✗ Multi-issuing-CA topology
✓ mTLS renewal without re-auth        ✗ Certificate issuance history
```

-----

## Setting Up step-ca with Docker

```bash
# Pull the image
docker pull smallstep/step-ca

# Create a persistent volume for CA data
docker volume create step-ca-data

# Run with auto-init via environment variables
docker run -d \
  --name step-ca \
  -p 9000:9000 \
  -v step-ca-data:/home/step \
  -e DOCKER_STEPCA_INIT_NAME="My Internal CA" \
  -e DOCKER_STEPCA_INIT_DNS_NAMES="localhost,127.0.0.1" \
  -e DOCKER_STEPCA_INIT_ADDRESS=":9000" \
  -e DOCKER_STEPCA_INIT_PROVISIONER_NAME="admin@example.com" \
  -e DOCKER_STEPCA_INIT_PASSWORD="supersecret" \
  -e DOCKER_STEPCA_INIT_PROVISIONER_PASSWORD="provisioner-secret" \
  smallstep/step-ca

# Wait for startup then verify
sleep 3
curl -k https://localhost:9000/health
# {"status":"ok"}
```

**Save the root fingerprint from the logs:**

```bash
docker logs step-ca 2>&1 | grep "Root fingerprint"
# Root fingerprint: 702a094e239c9eec6f0dcd0a5f65e595...
```

**Bootstrap the root certificate:**

```bash
# Download the root cert (the -k is a one-time bootstrap exception)
curl -sk https://localhost:9000/roots \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['crts'][0])" \
  > root_ca.crt

# All future calls use this cert instead of -k
curl --cacert root_ca.crt https://localhost:9000/health
# {"status":"ok"}
```

-----

## What the ca.json Looks Like

After init, step-ca writes a configuration file. The provisioner section is what our Python client needs:

```json
{
  "authority": {
    "provisioners": [
      {
        "type": "JWK",
        "name": "admin@example.com",
        "key": {
          "use":  "sig",
          "kty":  "EC",
          "kid":  "udaECquW2dYw-abc123",
          "crv":  "P-256",
          "alg":  "ES256",
          "x":    "Pn_JEpIByDJA...",
          "y":    "_x7JjfwqKEhBp7..."
        },
        "encryptedKey": "eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLC...",
        "claims": {
          "minTLSCertDuration":  "5m",
          "maxTLSCertDuration":  "24h",
          "defaultTLSCertDuration": "24h"
        }
      }
    ]
  }
}
```

The `key` field is the **public** JWK — used by step-ca to verify JWTs we sign.
The `encryptedKey` is the **encrypted private** JWK — we decrypt it locally to sign those JWTs.
The `kid` is the key identifier — used in the `GET /provisioners/{kid}/encrypted-key` endpoint.

-----

## Why a Python Class Rather Than Shelling Out?

```python
# ── Shelling out — what we are NOT building ──────────────────────────
import subprocess, tempfile

with tempfile.NamedTemporaryFile(suffix=".crt") as cert_f, \
     tempfile.NamedTemporaryFile(suffix=".key") as key_f:

    result = subprocess.run([
        "step", "ca", "certificate", "myservice.internal",
        cert_f.name, key_f.name,
        "--provisioner", "admin@example.com",
        "--provisioner-password-file", "/run/secrets/pass",
        "--ca-url", "https://ca.internal:9000",
        "--root", "/etc/step/root_ca.crt",
        "--not-after", "24h",
    ], capture_output=True, text=True, check=True)

    cert = cert_f.read().decode()
    key  = key_f.read().decode()

# Problems:
#  - step binary must be installed and on PATH
#  - Temp files with private key on disk
#  - Hard to mock in tests
#  - Output format can change between step versions
#  - No direct control over CSR contents
```

```python
# ── Direct HTTP — what we ARE building ──────────────────────────────
from step_ca_client import StepCAClient

ca = StepCAClient(
    ca_url             = "https://localhost:9000",
    root_fingerprint   = "702a094e239c9eec...",
    provisioner_name   = "admin@example.com",
    provisioner_password = "provisioner-secret",
)

cert_pem, key_pem = ca.sign(
    common_name = "myservice.internal",
    sans        = ["myservice.internal", "127.0.0.1"],
    duration    = "24h",
)

# Benefits:
#  - No step binary required
#  - Keys never touch disk unless you choose to write them
#  - Fully mockable: mock httpx and test every branch
#  - Direct control over every CSR field and JWT claim
#  - Works in any environment: container, Lambda, GitHub Actions
```

-----

## The Series Roadmap

|#|Episode                                    |What We Build                            |Endpoints Used                          |
|-|-------------------------------------------|-----------------------------------------|----------------------------------------|
|1|*This one* — The CA That Answers HTTP Calls|Foundation + Docker                      |Overview                                |
|2|First Contact                              |`__init__`, trust bootstrap, read methods|`GET /health`, `/roots`, `/provisioners`|
|3|Generating the CSR                         |Key + CSR factory                        |(local crypto only)                     |
|4|The Token Factory                          |JWE decrypt + JWT sign                   |`GET /provisioners/{kid}/encrypted-key` |
|5|Sign Here                                  |Full certificate issuance                |`POST /1.0/sign`                        |
|6|Still Breathing                            |mTLS renewal + daemon thread             |`POST /1.0/renew`                       |
|7|Taking Back the Key                        |Revocation                               |`POST /1.0/revoke`                      |
|8|The Complete Picture                       |Full class + Flask mTLS + ACME           |All endpoints                           |

In **Episode 2**, we build `StepCAClient.__init__`: trust bootstrap from a root fingerprint, an `httpx` session configured to verify the CA, and the three read-only discovery methods.

-----

**🔗 Resources**

- **step-ca GitHub**: [github.com/smallstep/certificates](https://github.com/smallstep/certificates)
- **step-ca docs**: [smallstep.com/docs/step-ca](https://smallstep.com/docs/step-ca/)
- **step-ca Docker**: [hub.docker.com/r/smallstep/step-ca](https://hub.docker.com/r/smallstep/step-ca)
- **Smallstep client examples**: [github.com/smallstep/clients](https://github.com/smallstep/clients)

-----

*🔐 REST with step-ca — automating certificate lifecycle one HTTP call at a time.*
