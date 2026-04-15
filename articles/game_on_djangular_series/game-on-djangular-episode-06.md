---
title: "Game on Djangular 🎮 Ep.6"
part: 6
published: false
description: "Episode 6: One-way TLS secures the XML channel. Generate a self-signed CA, issue a server certificate for the Linux server, configure Nginx to serve HTTPS, and tell Django’s requests client to verify against your CA. The complete TLS setup from scratch."
tags: [django, python, tls, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/game_on_djangular_series/game-on-djangular-episode-06.png"
series: "Game on Djangular Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 6: Encrypting the Channel

> *“Plaintext HTTP is like mailing your save file on a postcard. Anyone can read it.”*

-----

## The Postcard Problem 🃏

In Episode 5, GameLib sends XML over HTTP. The data travels in plaintext — anyone on the network path between Django and the Linux server can read it. For a game catalogue update, that is inconvenient. For a vault export containing user data, it is a compliance failure. For a future payload that includes authentication tokens, it is a security incident.

**TLS (Transport Layer Security)** encrypts the channel. The data is still XML. The protocol is still HTTP. But every byte is encrypted from the moment it leaves Django’s `requests.post()` call to the moment it arrives at the Linux server’s Nginx listener. Neither side can read the other’s data without the session keys, and those keys never travel over the network.

This episode generates a self-signed Certificate Authority, issues a server certificate for the Linux server, configures Nginx to serve HTTPS on that certificate, and tells Django’s `BridgeClient` to verify the connection against our CA. One-way TLS — the server proves its identity to Django; Django does not yet prove its identity to the server (that is Episode 7).

-----

## 🗂️ SIPOC — Encrypting the Channel

|**Suppliers**                               |**Inputs**                        |**Process**                                           |**Outputs**                                                  |**Customers**                                                                                            |
|--------------------------------------------|----------------------------------|------------------------------------------------------|-------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
|OpenSSL (on your workstation or a jump host)|CA key parameters                 |`openssl req -x509 -new -nodes ...`                   |`ca.key` (private) + `ca.crt` (self-signed root certificate) |The Linux server (trusts this CA to sign its cert) + Django backend (trusts this CA to verify the server)|
|OpenSSL                                     |Server hostname, CA key + cert    |`openssl genrsa` + `openssl req` + `openssl x509 -req`|`server.key` (private) + `server.crt` (CA-signed certificate)|Nginx on the Linux server — serves this cert on HTTPS                                                    |
|Nginx config on Linux server                |`server.key`, `server.crt`        |TLS termination on port 8443                          |HTTPS endpoint: `https://linux-srv.internal:8443/...`        |Django `BridgeClient` — connects via HTTPS                                                               |
|Django `BridgeClient`                       |`ca.crt` copied to the Django host|`requests.Session(verify="ca.crt")`                   |Verified HTTPS connection — chain validated against our CA   |The XML bridge operations from Episode 5 — now encrypted                                                 |

-----

## Understanding TLS in Two Minutes ⚡

When Django’s `requests.post("https://linux-srv.internal:8443/...")` runs:

1. TCP connection established to port 8443
1. **TLS handshake begins**: Django says “hello, here are cipher suites I support”
1. Linux server sends its **server certificate** (`server.crt`)
1. Django checks: is this certificate signed by a CA I trust?
- If `verify=True` → checks the system trust store (does not trust our self-signed CA)
- If `verify="/path/to/ca.crt"` → checks against our CA — **passes**
- If `verify=False` → skips all checking — **never do this in production**
1. Django verifies the certificate’s **Common Name / SAN** matches the hostname it connected to
1. Both sides derive session encryption keys from the handshake
1. The HTTP POST (with its XML body) travels encrypted from step 7 onwards

The server certificate is public — it is sent to every connecting client during the handshake. The private key (`server.key`) stays on the Linux server and never moves.

-----

## Step 1: Generate the Root CA 🔑

Run these commands on a secure host — your workstation during development, a dedicated PKI host in production. The CA private key must be protected; anyone who holds it can issue trusted certificates.

```bash
# Create a directory for PKI materials
mkdir -p ~/gamelib-pki/ca ~/gamelib-pki/server ~/gamelib-pki/client

# ── Generate the Root CA private key (4096-bit RSA)
openssl genrsa \
  -out ~/gamelib-pki/ca/ca.key \
  4096

# ── Self-sign the Root CA certificate (valid 10 years)
openssl req -x509 -new -nodes \
  -key  ~/gamelib-pki/ca/ca.key \
  -sha256 \
  -days 3650 \
  -out  ~/gamelib-pki/ca/ca.crt \
  -subj "/C=NL/ST=Noord-Brabant/L=Eindhoven/O=GameLib Internal/CN=GameLib Root CA"
```

Verify:

```bash
openssl x509 -in ~/gamelib-pki/ca/ca.crt -text -noout | grep -A2 "Subject:"
# Subject: C=NL, ST=Noord-Brabant, L=Eindhoven, O=GameLib Internal, CN=GameLib Root CA
```

-----

## Step 2: Generate the Server Certificate for the Linux Server 🖥️

```bash
# ── Server private key
openssl genrsa \
  -out ~/gamelib-pki/server/server.key \
  2048

# ── Certificate Signing Request (CSR)
openssl req -new \
  -key  ~/gamelib-pki/server/server.key \
  -out  ~/gamelib-pki/server/server.csr \
  -subj "/C=NL/ST=Noord-Brabant/O=GameLib Internal/CN=linux-srv.internal"

# ── Extension file: add Subject Alternative Names (SANs)
# SANs are required for modern TLS clients (Chrome, requests, etc.)
cat > /tmp/server-ext.cnf <<EOF
[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = linux-srv.internal
DNS.2 = linux-srv
IP.1  = 192.168.1.100       # replace with your server's IP
EOF

# ── Sign the CSR with the Root CA
openssl x509 -req \
  -in     ~/gamelib-pki/server/server.csr \
  -CA     ~/gamelib-pki/ca/ca.crt \
  -CAkey  ~/gamelib-pki/ca/ca.key \
  -CAcreateserial \
  -out    ~/gamelib-pki/server/server.crt \
  -days   365 \
  -sha256 \
  -extfile /tmp/server-ext.cnf \
  -extensions req_ext
```

Verify the chain:

```bash
openssl verify -CAfile ~/gamelib-pki/ca/ca.crt ~/gamelib-pki/server/server.crt
# server.crt: OK
```

-----

## Step 3: Configure Nginx on the Linux Server 🔧

Copy `server.key` and `server.crt` to the Linux server:

```bash
# On the Linux server
sudo mkdir -p /etc/gamelib/certs
# Copy files — use scp or ansible in production
sudo cp server.key /etc/gamelib/certs/
sudo cp server.crt /etc/gamelib/certs/
sudo chmod 600 /etc/gamelib/certs/server.key
sudo chmod 644 /etc/gamelib/certs/server.crt
```

Nginx configuration:

```nginx
# /etc/nginx/sites-available/gamelib-xml
server {
    listen 8080;                    # plain HTTP (default)
    server_name linux-srv.internal;

    location /catalogue/ {
        proxy_pass         http://127.0.0.1:9090;    # internal XML handler
        proxy_set_header   Host $host;
        proxy_set_header   X-GameLib-API-Key $http_x_gamelib_api_key;
    }
}

server {
    listen 8443 ssl;                 # HTTPS (optional)
    server_name linux-srv.internal;

    ssl_certificate       /etc/gamelib/certs/server.crt;
    ssl_certificate_key   /etc/gamelib/certs/server.key;

    # TLS hardening
    ssl_protocols         TLSv1.2 TLSv1.3;
    ssl_ciphers           ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;
    ssl_session_cache     shared:SSL:10m;
    ssl_session_timeout   10m;

    # No client cert required yet (Episode 7 adds mTLS here)
    # ssl_client_certificate /etc/gamelib/certs/ca.crt;
    # ssl_verify_client      off;

    location /catalogue/ {
        proxy_pass         http://127.0.0.1:9090;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-GameLib-API-Key $http_x_gamelib_api_key;
        proxy_set_header   X-Forwarded-Proto https;
    }
}
```

```bash
sudo nginx -t           # test config
sudo nginx -s reload    # apply
```

-----

## Step 4: Distribute `ca.crt` to the Django Host 📦

The CA public certificate is safe to distribute — it is public information. Copy it to the Django backend host:

```bash
# On the Django host
sudo mkdir -p /etc/gamelib/certs
sudo cp ca.crt /etc/gamelib/certs/
sudo chmod 644 /etc/gamelib/certs/ca.crt
```

-----

## Step 5: Configure Django to Use HTTPS + CA Verification ⚙️

Update `.env`:

```bash
XML_BRIDGE_USE_HTTPS=true
XML_BRIDGE_BASE_URL=https://linux-srv.internal:8443
XML_BRIDGE_CA_CERT=/etc/gamelib/certs/ca.crt
```

The `BridgeClient` from Episode 5 reads `XML_BRIDGE_CA_CERT` and sets `session.verify = ca_cert_path`. No code change needed — the toggle is already wired.

-----

## Testing the TLS Connection 🔬

From the Django host, test with `openssl s_client`:

```bash
openssl s_client \
  -connect linux-srv.internal:8443 \
  -CAfile /etc/gamelib/certs/ca.crt \
  -showcerts

# Expected output includes:
# Verify return code: 0 (ok)
```

From the Django shell:

```python
import requests

response = requests.get(
    "https://linux-srv.internal:8443/catalogue/feed",
    verify="/etc/gamelib/certs/ca.crt",
    headers={"X-GameLib-API-Key": "your-api-key"},
)
print(response.status_code)    # 200
```

If you see `SSLError: CERTIFICATE_VERIFY_FAILED`, check:

1. The CN / SAN in `server.crt` matches the hostname in `XML_BRIDGE_BASE_URL`
1. `ca.crt` is the certificate that signed `server.crt` (not a different CA)
1. The certificate has not expired (`openssl x509 -in server.crt -noout -dates`)

-----

## The TLS Architecture Diagram 🗺️

```
Django Backend                          Linux Server (Nginx)
──────────────────                      ──────────────────────
BridgeClient                            :8443 (HTTPS listener)
  session.verify = ca.crt               ssl_certificate     server.crt
  requests.post("https://...")          ssl_certificate_key server.key
        │                                         │
        │   1. TCP connect ──────────────────────►│
        │   2. TLS hello  ──────────────────────►│
        │   3. Server cert ◄──────────────────────│  (sends server.crt)
        │   4. Verify: ca.crt signs server.crt ✓  │
        │   5. Hostname check: CN = linux-srv.internal ✓
        │   6. Session keys derived
        │   7. POST /catalogue/update ──ENCRYPTED►│
        │   8. HTTP 200 response ◄──────ENCRYPTED─│
```

The channel is encrypted. Django trusts the Linux server because Django holds the CA certificate that signed the server’s certificate. The server has not yet been asked to prove the caller is Django — only that the caller knows the CA. That is Episode 7.

-----

In **Episode 7**, we add the second lock: **mTLS**. Django presents its own client certificate. The Linux server verifies it against the same CA. Both sides are cryptographically authenticated.

-----

**🔗 Resources**

- **OpenSSL commands reference**: [openssl.org/docs/manmaster/man1/openssl-req.html](https://www.openssl.org/docs/manmaster/man1/openssl-req.html)
- **Python requests SSL**: [docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification](https://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification)
- **Nginx SSL configuration**: [nginx.org/en/docs/http/ngx_http_ssl_module.html](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)

-----

*🎮 Game on Djangular Series is a series about building GameLib with Django REST Framework, Angular, XML exchange, TLS/mTLS, SailPoint IAM, and PKI management.*
