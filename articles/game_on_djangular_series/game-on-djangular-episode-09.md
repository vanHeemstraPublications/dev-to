---
title: "Game on Djangular 🎮 Ep.9"
part: 9
published: false
description: "Episode 9: PKI management with django-ca — the Certificate Authority that signs everything. Root CA, intermediate CA, certificate lifecycle, CRL publication, OCSP responder, rotation automation, and the complete PKI architecture for GameLib. Where all locks are made."
tags: [django, python, pki, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/game_on_djangular_series/game-on-djangular-episode-09.png"
series: "Game on Djangular Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 9: The Key Factory

> *“Every lock in the game was made in the same factory. The factory keeps the master key.”*

-----

## The Factory Behind the Locks 🏭

Episodes 6 and 7 generated certificates with raw `openssl` commands. That works for initial setup. It does not scale. Three months from now, a certificate expires. Six months from now, a server is decommissioned and its certificate needs to be revoked. A year from now, someone needs to know which certificates are currently valid and which have been revoked.

Without a managed PKI, these questions have no good answers. Certificate files are scattered across servers. Expiry dates are tracked (or not) in a spreadsheet. Revocation means regenerating every certificate because nobody set up a CRL.

**PKI — Public Key Infrastructure** is the systematic management of every certificate in your system: issuing them, tracking them, rotating them, revoking them, and publishing the revocation status so that every relying party (Django, Nginx, SailPoint) knows which certificates to trust.

**`django-ca`** is a mature, open-source Django application that turns a Django deployment into a fully functional Certificate Authority with a web UI, CLI management commands, CRL endpoints, and an OCSP responder.

-----

## 🗂️ SIPOC — The Key Factory

|**Suppliers**           |**Inputs**                                               |**Process**                                                           |**Outputs**                                                       |**Customers**                                                        |
|------------------------|---------------------------------------------------------|----------------------------------------------------------------------|------------------------------------------------------------------|---------------------------------------------------------------------|
|`django-ca` application |CA configuration: key type, size, validity, CRL/OCSP URLs|`manage.py init_ca` — generates Root CA and optionally Intermediate CA|CA key (stored in database or HSM), CA certificate (distributable)|All certificate consumers: Django, Nginx, SailPoint, external clients|
|`django-ca` sign command|CSR (Certificate Signing Request) from server or client  |`manage.py sign_cert` — validates CSR, issues certificate             |Signed certificate (PEM), stored in database + on filesystem      |The certificate holder: Linux server, Django backend, etc.           |
|CRL endpoint            |Revocation events in `django-ca` database                |Periodic regeneration of CRL; Nginx serves it at a known URL          |`https://pki.gamelib.internal/crl/` — downloadable CRL            |Any TLS client that checks revocation status                         |
|OCSP responder          |Certificate serial number query                          |`django-ca` OCSP view responds to stapling or direct queries          |`good` / `revoked` / `unknown` status for a given cert serial     |Nginx OCSP stapling; any client performing OCSP validation           |
|Rotation scheduler      |Certificate expiry notifications from `django-ca`        |Email alert 30 days before expiry; automated reissue via CLI          |New certificates replacing expiring ones; zero-downtime rotation  |Operations team; CI/CD pipeline that pushes new certs                |

-----

## Installing `django-ca` 🔧

```bash
pip install django-ca

# Optional: for HSM support (PKCS#11)
pip install "django-ca[hsm]"
```

Add to `INSTALLED_APPS` in the GameLib PKI Django project (this is a separate Django project dedicated to PKI management, not the same as the main GameLib backend):

```python
# pki/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_ca",    # django-ca PKI management
]

# django-ca: where to store private keys on disk (outside the database)
CA_DEFAULT_KEY_SIZE = 4096
CA_DEFAULT_HOSTNAME = "pki.gamelib.internal"  # used in CRL and OCSP URLs

# Storage for CA private keys — can be file system, database, or HSM
# For production, use HSM (PKCS#11) or a dedicated secrets vault
CA_DEFAULT_STORAGE_BACKEND = "django_ca.key_backends.storages.StoragesUsePrivateKeyBackend"
```

```bash
python manage.py migrate
```

-----

## The CA Hierarchy: Root → Intermediate → End-Entity 🌲

A flat CA (one CA signs all certificates) is simpler but riskier. If the CA key is compromised, all issued certificates must be reissued. A hierarchy isolates the blast radius:

```
GameLib Root CA  (offline / air-gapped)
    │
    └── GameLib Infrastructure CA  (online / django-ca)
            │
            ├── linux-srv.internal (server cert)
            ├── gamelib-backend    (client cert)
            └── gamelib-analytics  (client cert)
```

The Root CA is self-signed and kept offline. It only signs the Intermediate CA certificate. The Intermediate CA (managed by `django-ca`) issues all operational certificates. If the Intermediate CA key is compromised, the Root CA can revoke it and a new Intermediate CA can be created without touching the Root.

-----

## Step 1: Create the Root CA (Offline) 🔒

The Root CA is created with OpenSSL on an air-gapped workstation, then imported into `django-ca` as read-only:

```bash
# On the air-gapped workstation
openssl genrsa -aes256 \
  -passout pass:"STRONG_PASSPHRASE" \
  -out root-ca.key \
  4096

openssl req -x509 -new -nodes \
  -key  root-ca.key \
  -passin pass:"STRONG_PASSPHRASE" \
  -sha256 \
  -days 3650 \
  -out  root-ca.crt \
  -subj "/C=NL/O=GameLib Internal/CN=GameLib Root CA"
```

Import into `django-ca` (marks it as offline — only used to sign the intermediate):

```bash
python manage.py import_ca \
  --name "GameLib Root CA" \
  root-ca.crt
```

-----

## Step 2: Create the Intermediate CA (Online) ⚙️

```bash
# django-ca creates the intermediate CA, then signs it with the Root CA
python manage.py init_ca \
  --name "GameLib Infrastructure CA" \
  --parent "GameLib Root CA" \
  --key-type RSA \
  --key-size 4096 \
  --expires 1825 \
  --path-length 0 \
  "GameLib Infrastructure CA"
```

The `--path-length 0` means this CA cannot sign other CAs — it can only sign end-entity certificates (server and client certs). This limits damage if the Intermediate CA key is stolen.

List CAs:

```bash
python manage.py list_cas
# GameLib Root CA — expires 2035-04-15
# GameLib Infrastructure CA — expires 2030-04-15 (signed by Root CA)
```

-----

## Step 3: Issue the Server Certificate 🖥️

```bash
# Issue a server certificate for the Linux XML server
python manage.py sign_cert \
  --ca "GameLib Infrastructure CA" \
  --subject "/CN=linux-srv.internal/O=GameLib Internal/C=NL" \
  --profile server \
  --alt-name "DNS:linux-srv.internal" \
  --alt-name "DNS:linux-srv" \
  --alt-name "IP:192.168.1.100" \
  --expires 365 \
  --out linux-srv-internal.crt
```

`django-ca` uses **profiles** to set appropriate X.509 extensions:

- `server` profile: `extendedKeyUsage = serverAuth`, `keyUsage = digitalSignature, keyEncipherment`
- `client` profile: `extendedKeyUsage = clientAuth`
- `ocsp` profile: for OCSP responder certificates

-----

## Step 4: Issue the Client Certificate for Django 🔑

```bash
python manage.py sign_cert \
  --ca "GameLib Infrastructure CA" \
  --subject "/CN=gamelib-backend/O=GameLib Internal/C=NL" \
  --profile client \
  --expires 365 \
  --out gamelib-backend.crt
```

`django-ca` stores every certificate it issues in the database. This creates the inventory needed for lifecycle management.

-----

## Step 5: Certificate Revocation Lists (CRL) 📋

A CRL is a list of certificate serial numbers that have been revoked. Clients download the CRL (at the URL embedded in each certificate) and reject connections from revoked certificates.

Configure `django-ca` to publish a CRL:

```python
# pki/urls.py
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",       include("django_ca.urls")),   # exposes /crl/ and /ocsp/ endpoints
]
```

`django-ca` generates the CRL URL and embeds it in every certificate it signs (via the CRL Distribution Points extension). Clients retrieve the CRL before verifying a certificate.

### Revoking a Certificate

When the Linux server is decommissioned, or the `gamelib-backend` service account is compromised:

```bash
# List all certificates signed by the Infrastructure CA
python manage.py list_certs
# Serial                                   | Common Name           | Expires
# ─────────────────────────────────────────┼───────────────────────┼──────────
# 4A:BC:12:...                             | linux-srv.internal    | 2026-04-15
# 5C:DE:34:...                             | gamelib-backend       | 2026-04-15

# Revoke by serial or Common Name
python manage.py revoke_cert 5C:DE:34:... \
  --reason keyCompromise
# Certificate 5C:DE:34:... revoked. CRL will be updated on next generation.

# Force CRL regeneration immediately
python manage.py regenerate_crls
```

From this point, any TLS client that downloads the CRL will reject connections using the revoked certificate.

-----

## Step 6: OCSP Responder 🔍

CRLs have a latency problem: they are generated periodically (often daily), so a revoked certificate can still be used for up to 24 hours. **OCSP (Online Certificate Status Protocol)** provides real-time revocation status.

`django-ca` includes a built-in OCSP responder. Enable it:

```bash
# Create an OCSP responder certificate for the Infrastructure CA
python manage.py sign_cert \
  --ca "GameLib Infrastructure CA" \
  --profile ocsp \
  --subject "/CN=GameLib OCSP/O=GameLib Internal/C=NL" \
  --expires 7 \      # OCSP responder certs are short-lived
  --out ocsp-responder.crt
```

The OCSP endpoint is at `https://pki.gamelib.internal/ocsp/{ca-serial}/`. Nginx on the Linux server uses OCSP stapling to embed the revocation status in the TLS handshake, eliminating the need for clients to make a separate OCSP request:

```nginx
# Nginx OCSP stapling configuration on Linux server
ssl_stapling             on;
ssl_stapling_verify      on;
ssl_trusted_certificate  /etc/gamelib/certs/ca-chain.crt;   # full chain: intermediate + root
resolver                 8.8.8.8 valid=300s;
resolver_timeout         5s;
```

-----

## Step 7: Expiry Notifications and Rotation 🔄

`django-ca` sends email notifications before certificates expire. Configure:

```python
# pki/settings.py
CA_DEFAULT_PROFILE = "server"

# Email notification settings (standard Django email)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST    = "smtp.company.com"
# ...

# Add watchers to receive expiry notifications
# (via manage.py sign_cert --watch ops@company.com)
```

Automate rotation with a cron job or Celery task:

```bash
# crontab on the PKI server — daily at 02:00
0 2 * * * /path/to/venv/bin/python /path/to/pki/manage.py notify_expiring --days 30
```

The notification lists every certificate expiring in the next 30 days. Operations re-issues the cert, copies it to the target host, and reloads the service. Zero downtime if the new cert is in place before the old one expires.

-----

## The Full GameLib PKI Architecture 🗺️

```
┌─────────────────────────────────────────────────────────────┐
│                  GameLib PKI (Air-Gapped Layer)             │
│                                                             │
│   GameLib Root CA (offline workstation)                     │
│   ca.key — 4096-bit RSA, passphrase-protected               │
│   ca.crt — self-signed, valid 10 years                      │
│   Signs only: GameLib Infrastructure CA                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ signs
┌──────────────────────▼──────────────────────────────────────┐
│              GameLib Infrastructure CA (django-ca)          │
│                                                             │
│   Managed by django-ca on pki.gamelib.internal              │
│   Exposes: /crl/, /ocsp/                                    │
│                                                             │
│   Issues:                                                   │
│   ┌───────────────────┐  ┌────────────────────────────┐     │
│   │ linux-srv.internal│  │ gamelib-backend (client)   │     │
│   │ server cert       │  │ client cert                │     │
│   │ Nginx mTLS        │  │ BridgeClient (Episode 5–7) │     │
│   │ Expires: 365 days │  │ Expires: 365 days          │     │
│   └───────────────────┘  └────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                       │
                  ca.crt distributed to:
                  ┌────┴────────────────┐
                  │                     │
           Django backend          Linux server
           verify=ca.crt           ssl_client_certificate=ca.crt
           ssl.verify_client=on
```

-----

## The Complete Security Stack: All Nine Episodes 🔒

|Layer                 |Component                       |Episode|
|----------------------|--------------------------------|-------|
|Application auth      |JWT (simplejwt)                 |3      |
|Data layer            |Django ORM + PostgreSQL         |2      |
|REST API              |DRF + ViewSets                  |2      |
|Frontend              |Angular + HttpInterceptor       |3–4    |
|Transport (plain)     |HTTP, `requests`                |5      |
|Transport (encrypted) |TLS, self-signed server cert    |6      |
|Mutual authentication |mTLS, client cert               |7      |
|Identity authorisation|SailPoint IAM, SCIM 2.0         |8      |
|Certificate lifecycle |`django-ca`, CRL, OCSP, rotation|9      |

Every layer addresses a different threat. Remove any one layer and a threat remains. Together, they form a defence-in-depth architecture: GameLib communicates with the Linux server over an encrypted, mutually authenticated channel, governed by a managed PKI, with identity authorisation enforced by SailPoint before any data moves.

Your vault is locked. Both sides of the lock are verified. The key factory keeps records of every key it has ever made. The guild registry confirms your membership before you enter.

Game on.

-----

**🔗 Resources**

- **django-ca documentation**: [django-ca.readthedocs.io](https://django-ca.readthedocs.io)
- **django-ca GitHub**: [github.com/mathiasertl/django-ca](https://github.com/mathiasertl/django-ca)
- **PKI fundamentals (GoLinuxCloud)**: [golinuxcloud.com/tutorial-pki-certificates-authority-ocsp](https://www.golinuxcloud.com/tutorial-pki-certificates-authority-ocsp/)
- **RFC 5280 (X.509)**: [rfc-editor.org/rfc/rfc5280](https://www.rfc-editor.org/rfc/rfc5280)
- **OCSP RFC 6960**: [rfc-editor.org/rfc/rfc6960](https://www.rfc-editor.org/rfc/rfc6960)

-----

*🎮 Game on Djangular Series is a series about building GameLib with Django REST Framework, Angular, XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
