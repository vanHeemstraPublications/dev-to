---
title: "Game on Djangular 🎮 Ep.7"
part: 7
published: false
description: "Episode 7: Mutual TLS (mTLS) — both Django and the Linux server present certificates signed by the same CA. Generate a client certificate, configure requests with cert=(crt, key), update Nginx to require and verify client certs. The complete two-way handshake."
tags: [django, python, mtls, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/game_on_djangular_series/game-on-djangular-episode-07.png"
series: "Game on Djangular Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: Both Sides of the Lock

> *“In Episode 6, the vault door checked your face. In Episode 7, you also check its face.”*

-----

## The One-Sided Lock Problem 🔐

Episode 6 gave us TLS. Django trusts the Linux server because the server presents a certificate signed by our CA. Encrypted channel. Server authenticated.

But the Linux server does not know who is calling. Any client that holds a copy of `ca.crt` can connect. A developer’s laptop. A curl command. A different service in the same organisation. The `/catalogue/update` endpoint accepts any caller that can establish a TLS connection.

**mTLS — Mutual TLS** closes this gap. In mutual authentication, the server also requires the client to present a certificate. The Linux server now has two conditions for accepting a connection: the client must establish TLS (already done), and the client must present a certificate signed by the trusted CA. No certificate, no connection — at the TLS layer, before any HTTP request is processed.

Both sides of the lock. The vault door checks your face. You check the vault door’s face.

-----

## 🗂️ SIPOC — Both Sides of the Lock

|**Suppliers**        |**Inputs**                            |**Process**                                                           |**Outputs**                                                                           |**Customers**                                                            |
|---------------------|--------------------------------------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
|OpenSSL (PKI host)   |CA key + cert from Episode 6          |`openssl genrsa` + `openssl req` + `openssl x509 -req`                |`client.key` (private) + `client.crt` (CA-signed)                                     |Django backend — holds both files; presents them on every HTTPS call     |
|Django `BridgeClient`|`client.crt` + `client.key` file paths|`requests.Session(cert=("client.crt", "client.key"))`                 |An mTLS-capable session                                                               |`post_xml()` and `get_xml()` — both present the client cert automatically|
|Nginx (Linux server) |`ca.crt` + `ssl_verify_client on`     |At TLS handshake: request + verify client certificate against `ca.crt`|Connections authenticated at transport layer; `$ssl_client_s_dn` available to upstream|Upstream XML handler — knows the caller is the GameLib backend           |

-----

## The mTLS Handshake: Step by Step 🤝

```
Django (BridgeClient)                   Linux Server (Nginx + mTLS)
──────────────────                      ──────────────────────────
1. TCP SYN ─────────────────────────────────────────────────────►
2. TLS ClientHello ──────────────────────────────────────────────►
3.                 ◄────────────────── ServerHello + server.crt
4. Verify: ca.crt signed server.crt? ✓
5. Hostname: CN = linux-srv.internal? ✓
6.                 ◄────────────────── CertificateRequest
7. Send client.crt ──────────────────────────────────────────────►
8.                                      Verify: ca.crt signed client.crt? ✓
9.                                      CN = gamelib-backend? ✓
10. Session keys derived (both sides)
11. POST /catalogue/update ──── ENCRYPTED ───────────────────────►
12.                 ◄──────────────────────────── HTTP 200 OK ────
```

Steps 3–5 are Episode 6 (server proves itself). Steps 6–9 are new — the server challenges the client to prove itself. If Django does not present a valid certificate at step 7, Nginx closes the connection with `tlsv1 alert certificate unknown` before any HTTP traffic flows.

-----

## Step 1: Generate the Client Certificate for Django 🔑

Using the same CA from Episode 6:

```bash
# ── Client private key (stays on the Django host)
openssl genrsa \
  -out ~/gamelib-pki/client/client.key \
  2048

# ── Certificate Signing Request
openssl req -new \
  -key  ~/gamelib-pki/client/client.key \
  -out  ~/gamelib-pki/client/client.csr \
  -subj "/C=NL/ST=Noord-Brabant/O=GameLib Internal/CN=gamelib-backend"

# ── Extension file for client certificate
# extendedKeyUsage = clientAuth identifies this as a client cert
cat > /tmp/client-ext.cnf <<EOF
[client_ext]
basicConstraints      = CA:FALSE
keyUsage              = digitalSignature, keyEncipherment
extendedKeyUsage      = clientAuth
subjectKeyIdentifier  = hash
authorityKeyIdentifier = keyid,issuer
EOF

# ── Sign with the Root CA
openssl x509 -req \
  -in     ~/gamelib-pki/client/client.csr \
  -CA     ~/gamelib-pki/ca/ca.crt \
  -CAkey  ~/gamelib-pki/ca/ca.key \
  -CAcreateserial \
  -out    ~/gamelib-pki/client/client.crt \
  -days   365 \
  -sha256 \
  -extfile /tmp/client-ext.cnf \
  -extensions client_ext
```

Verify:

```bash
openssl verify -CAfile ~/gamelib-pki/ca/ca.crt ~/gamelib-pki/client/client.crt
# client.crt: OK

openssl x509 -in ~/gamelib-pki/client/client.crt -text -noout | grep "Extended Key"
# Extended Key Usage: TLS Web Client Authentication
```

-----

## Step 2: Deploy Client Cert to the Django Host 📦

```bash
# On the Django host
sudo cp ~/gamelib-pki/client/client.crt /etc/gamelib/certs/client.crt
sudo cp ~/gamelib-pki/client/client.key /etc/gamelib/certs/client.key
sudo chmod 600 /etc/gamelib/certs/client.key    # private key — restrict access
sudo chmod 644 /etc/gamelib/certs/client.crt
sudo chown www-data:www-data /etc/gamelib/certs/client.key  # Django/Gunicorn user
```

The client private key must never leave the Django host. It is not shared with the Linux server. The Linux server only needs `ca.crt` to verify client certificates.

-----

## Step 3: Update Django Settings ⚙️

```bash
# .env additions
XML_BRIDGE_CLIENT_CERT_CRT=/etc/gamelib/certs/client.crt
XML_BRIDGE_CLIENT_CERT_KEY=/etc/gamelib/certs/client.key
```

```python
# gamelib/settings.py
import os

# mTLS client cert — tuple(cert_path, key_path) or None for plain TLS
_client_crt = os.environ.get("XML_BRIDGE_CLIENT_CERT_CRT")
_client_key = os.environ.get("XML_BRIDGE_CLIENT_CERT_KEY")
XML_BRIDGE_CLIENT_CERT = (_client_crt, _client_key) if _client_crt and _client_key else None
```

The `BridgeClient._build_session()` from Episode 5 already reads `XML_BRIDGE_CLIENT_CERT`:

```python
if self.client_cert:
    session.cert = self.client_cert    # (crt_path, key_path)
```

`requests` sends the client certificate during the TLS handshake. No further code change.

-----

## Step 4: Update Nginx to Require Client Certificates 🔒

On the Linux server, update the HTTPS server block:

```nginx
# /etc/nginx/sites-available/gamelib-xml (updated HTTPS block)
server {
    listen 8443 ssl;
    server_name linux-srv.internal;

    ssl_certificate       /etc/gamelib/certs/server.crt;
    ssl_certificate_key   /etc/gamelib/certs/server.key;

    ssl_protocols         TLSv1.2 TLSv1.3;
    ssl_ciphers           ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;

    # ── mTLS: require and verify client certificate ──────────────
    ssl_client_certificate /etc/gamelib/certs/ca.crt;   # the CA that signs client certs
    ssl_verify_client      on;                           # reject connections without a valid cert
    ssl_verify_depth       2;                            # allow intermediate CAs (depth 1 = direct CA)

    location /catalogue/ {
        # Forward client cert info to the upstream handler
        proxy_pass              http://127.0.0.1:9090;
        proxy_set_header        X-SSL-Client-CN   $ssl_client_s_dn;
        proxy_set_header        X-SSL-Client-Cert $ssl_client_cert;
        proxy_set_header        X-SSL-Verify      $ssl_client_verify;
        proxy_set_header        Host              $host;
        proxy_set_header        X-Forwarded-Proto https;

        # Only allow verified clients
        if ($ssl_client_verify != SUCCESS) {
            return 403 "Client certificate required or invalid.";
        }
    }
}
```

```bash
sudo nginx -t && sudo nginx -s reload
```

The `$ssl_client_s_dn` variable contains the Distinguished Name from the client certificate — e.g. `CN=gamelib-backend,O=GameLib Internal,ST=Noord-Brabant,C=NL`. The upstream handler can read this from the `X-SSL-Client-CN` header and log it, verify it, or make authorisation decisions based on it.

-----

## Step 5: Testing mTLS 🔬

Test from the command line:

```bash
# Test without client cert — should fail at TLS layer
openssl s_client \
  -connect linux-srv.internal:8443 \
  -CAfile /etc/gamelib/certs/ca.crt
# Output: alert handshake failure (no client cert presented)

# Test with client cert — should succeed
openssl s_client \
  -connect linux-srv.internal:8443 \
  -CAfile  /etc/gamelib/certs/ca.crt \
  -cert    /etc/gamelib/certs/client.crt \
  -key     /etc/gamelib/certs/client.key
# Output: Verify return code: 0 (ok)
```

Test from Django shell:

```python
import requests

response = requests.post(
    "https://linux-srv.internal:8443/catalogue/update",
    data=b"<GameCatalogue/>",
    headers={"Content-Type": "application/xml"},
    verify="/etc/gamelib/certs/ca.crt",
    cert=("/etc/gamelib/certs/client.crt", "/etc/gamelib/certs/client.key"),
)
print(response.status_code)    # 200
```

Test with Django management command:

```bash
python manage.py push_catalogue
# Uses BridgeClient which reads XML_BRIDGE_CLIENT_CERT from settings
```

-----

## Security Properties After mTLS 🔒

With both TLS and mTLS configured:

|Property                                     |Before (HTTP)|After TLS only|After mTLS          |
|---------------------------------------------|-------------|--------------|--------------------|
|Data encrypted in transit                    |❌            |✅             |✅                   |
|Server identity verified                     |❌            |✅             |✅                   |
|Client identity verified                     |❌            |❌             |✅                   |
|Replay attacks prevented                     |❌            |✅             |✅                   |
|Man-in-the-middle blocked                    |❌            |✅             |✅                   |
|Attacker with stolen CA cert can forge client|N/A          |N/A           |⚠️ (but needs CA key)|

The remaining risk is the CA private key. If `ca.key` is stolen, an attacker can issue new certificates that our infrastructure will trust. This is why the CA key must be offline (HSM or air-gapped system) in production, and why Episode 9 covers certificate revocation — revoking a certificate that should no longer be trusted even if it was legitimately issued.

-----

## Troubleshooting Common mTLS Errors ⚠️

|Error                                 |Cause                                                               |Fix                                                                            |
|--------------------------------------|--------------------------------------------------------------------|-------------------------------------------------------------------------------|
|`SSL: TLSV1_ALERT_UNKNOWN_CA`         |CA cert on the server does not match the CA that signed `client.crt`|Ensure `ssl_client_certificate` points to the same CA used to sign `client.crt`|
|`SSL: SSLV3_ALERT_HANDSHAKE_FAILURE`  |No client certificate presented                                     |Set `XML_BRIDGE_CLIENT_CERT` in settings                                       |
|`403 Client certificate required`     |`ssl_verify_client = on` but `$ssl_client_verify != SUCCESS`        |Check Nginx reachable, cert chain correct, not expired                         |
|`KeyError` when reading `session.cert`|Cert tuple in wrong order                                           |Must be `(cert_path, key_path)`, not `(key_path, cert_path)`                   |
|`certificate has expired`             |Client or server cert past `notAfter` date                          |Regenerate and rotate (Episode 9)                                              |

-----

In **Episode 8**, we add the guild registry layer: **SailPoint IAM**. Before Django initiates an XML transfer, it asks SailPoint whether the Linux server’s identity has the access entitlement for the `catalogue_update` operation. Zero-trust, identity-governed data exchange.

-----

**🔗 Resources**

- **Mutual TLS deep dive**: [smallstep.com/hello-mtls/doc/client/requests](https://smallstep.com/hello-mtls/doc/client/requests)
- **Nginx `ssl_verify_client` directive**: [nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_verify_client](https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_verify_client)
- **Python requests mTLS**: [docs.python-requests.org/en/latest/user/advanced/#client-side-certificates](https://docs.python-requests.org/en/latest/user/advanced/#client-side-certificates)

-----

*🎮 Game on Djangular Series is a series about building GameLib with Django REST Framework, Angular, XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
