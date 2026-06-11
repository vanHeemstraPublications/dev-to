---
title: "What Are You LDAP? 🔬 Ep.8"
published: false
description: "Episode 8: The finale. Every investigation ends here — a hardened, encrypted, monitored, high-availability LDAP deployment ready for the demands of production. LDAPS and StartTLS lock down the wire. SASL EXTERNAL uses certificates for the most privileged operations. Indexes are tuned. Connection pools are calibrated. The overlays checklist is complete. The case is closed. What are you? Fully classified."
tags: [ldap, security, production, openldap]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-are-you-ldap-episode-08.png"
series: "What Are You LDAP?"
canonical_url: ""
organization: "the-software-s-journey
part: 8
---

## Episode 8: Case Closed

*🎵 What are you? What what, what what? 🎵*

-----

## “Lock the Evidence Room” 🔒

*The final briefing room. All four investigators around the table. Grissom at the whiteboard. The LDAP deployment diagram covers the wall.*

**GRISSOM:** “Eight episodes. We have built a directory from nothing. We understand what every entry is — its objectClass, its attributes, its operational metadata. We can search it, modify it, audit it, replicate it. We can lock accounts, enforce password policy, control access with ACIs.”

*He turns.*

**GRISSOM:** “But none of it means anything if the wire is unencrypted. If a simple bind sends a password in cleartext across the network, every switch between the client and the server is a crime scene. If the admin account uses a password instead of a certificate, every compromised server in the chain is a liability.”

*He picks up a certificate file.*

**GRISSOM:** “Episode 8 is not about features. It is about closing the case properly. Encrypting the evidence. Locking the room. Tuning the instruments so the lab runs at scale. And leaving a deployment that future investigators can maintain.”

-----

## 🗂️ SIPOC — The Production Hardening Operation

|**Suppliers**                            |**Inputs**                                      |**Process**                                                            |**Outputs**                                                          |**Customers**                                                                         |
|-----------------------------------------|------------------------------------------------|-----------------------------------------------------------------------|---------------------------------------------------------------------|--------------------------------------------------------------------------------------|
|TLS certificates (CA + server + client)  |CA certificate, server certificate, private key |Configure LDAPS (port 636) and/or StartTLS (port 389 + STARTTLS)       |Encrypted wire for all LDAP traffic — credentials never in cleartext |Every LDAP client — which can no longer have its bind intercepted                     |
|Client certificate (for admin operations)|CA-signed certificate tied to the admin DN      |SASL EXTERNAL auth on ldapi:// or LDAPS — certificate IS the credential|Admin operations authenticated by cryptographic proof, not a password|The most privileged operations — which should never depend on a password being correct|
|Index configuration                      |Frequently used search attributes               |`olcDbIndex` directives; `slapindex` rebuild                           |Sub-millisecond attribute lookups instead of full-table scans        |Applications — which receive fast responses at scale; the server — which uses less CPU|
|Connection pool (client-side)            |Application with many threads, each needing LDAP|Library-level connection pooling (ldap3, python-ldap, etc.)            |Reused authenticated connections — no repeated bind overhead         |High-traffic applications — which avoid repeated connect+bind per request             |

-----

## Part 1: LDAPS — The Encrypted Evidence Bag 🔐

**LDAPS** (LDAP over TLS, port 636) wraps the entire LDAP connection in TLS from the first byte. The alternative, **StartTLS**, begins as plain LDAP and upgrades to TLS via an extended operation.

```
LDAPS (port 636):
  Client → TLS handshake → TLS tunnel established → LDAP operations inside tunnel

StartTLS (port 389):
  Client → plain TCP → LDAP STARTTLS extended operation → TLS handshake → LDAP operations
```

**GRISSOM:** “StartTLS has a subtle risk: an attacker who can intercept the initial plain-text exchange can strip the STARTTLS command before the client sends it — a STARTTLS-stripping attack. LDAPS has no plain-text phase. It is the encrypted evidence bag, sealed from the first byte.”

### Generate TLS certificates

```bash
# Generate a self-signed CA (for testing/internal use)
# For production: use your enterprise CA or Let's Encrypt

# CA private key and certificate
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/C=US/ST=Nevada/L=LasVegas/O=ACME Corporation/CN=ACME LDAP CA"

# Server private key and CSR
openssl genrsa -out ldap-server.key 2048
openssl req -new -key ldap-server.key -out ldap-server.csr \
  -subj "/C=US/ST=Nevada/L=LasVegas/O=ACME Corporation/CN=ldap1.acme.com"

# Sign the server certificate with the CA
openssl x509 -req -days 365 \
  -in ldap-server.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out ldap-server.crt \
  -extfile <(echo "subjectAltName=DNS:ldap1.acme.com,DNS:ldap.acme.com,IP:192.168.1.10")

# Copy certificates to LDAP config directory
install -m 640 -o openldap -g openldap ca.crt          /etc/ldap/ca.crt
install -m 640 -o openldap -g openldap ldap-server.crt  /etc/ldap/server.crt
install -m 640 -o openldap -g openldap ldap-server.key  /etc/ldap/server.key
```

### Configure TLS in cn=config

```ldif
# Apply TLS configuration via cn=config (live — no restart)
dn: cn=config
changetype: modify
add: olcTLSCACertificateFile
olcTLSCACertificateFile: /etc/ldap/ca.crt
-
add: olcTLSCertificateFile
olcTLSCertificateFile: /etc/ldap/server.crt
-
add: olcTLSCertificateKeyFile
olcTLSCertificateKeyFile: /etc/ldap/server.key
-
add: olcTLSCipherSuite
olcTLSCipherSuite: HIGH:!aNULL:!MD5:!RC4
-
add: olcTLSProtocolMin
olcTLSProtocolMin: 3.3
# 3.3 = TLS 1.2 minimum; use 3.4 for TLS 1.3 minimum
-
add: olcTLSVerifyClient
olcTLSVerifyClient: demand
# demand = require and verify client certificate
# allow  = accept client certificate if presented, verify it
# never  = do not request client certificate (standard for user auth)
# try    = request but don't require
```

```bash
ldapmodify \
  -Y EXTERNAL \
  -H ldapi:/// \
  -f tls-config.ldif

# Enable LDAPS listener in slapd.conf or command-line
# Edit /etc/default/slapd (Debian/Ubuntu):
SLAPD_SERVICES="ldap:/// ldaps:/// ldapi:///"
# Then restart slapd (this is the one time a restart is warranted)
sudo systemctl restart slapd

# Verify LDAPS is listening
ss -tlnp | grep 636
# LISTEN 0  128  0.0.0.0:636  0.0.0.0:*  users:(("slapd",pid=1234,fd=9))

# Test LDAPS connection
ldapsearch \
  -x \
  -H ldaps://ldap1.acme.com:636 \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)" \
  cn
# TLS: certificate verified. Connection encrypted.

# Test StartTLS (still on port 389)
ldapsearch \
  -x \
  -H ldap://ldap1.acme.com:389 \
  -ZZ \                          # -ZZ = require StartTLS, fail if unavailable
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)" \
  cn
```

-----

## Part 2: SASL EXTERNAL — Certificate Authentication for the Most Privileged 🪪

SASL EXTERNAL uses the TLS client certificate as the credential. No password. The certificate IS the identity proof.

Used for:

- Admin operations via `ldapi:///` (Unix socket — OS user is the credential)
- Privileged operations via LDAPS with a client certificate

```bash
# Generate admin client certificate
openssl genrsa -out admin-client.key 2048
openssl req -new -key admin-client.key -out admin-client.csr \
  -subj "/C=US/O=ACME/CN=cn=admin,dc=acme,dc=com"
# Note: the CN in the subject becomes the authzDN

openssl x509 -req -days 365 \
  -in admin-client.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out admin-client.crt

# Use the client certificate for admin operations
ldapsearch \
  -H ldaps://ldap1.acme.com:636 \
  -Y EXTERNAL \
  -tls_cert admin-client.crt \
  -tls_key admin-client.key \
  -tls_cacert ca.crt \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)"
# Authenticated as: cn=admin,dc=acme,dc=com (via certificate)
# No password transmitted or required

# Via ldapi:// (Unix socket — root gets full access automatically)
sudo ldapsearch \
  -Y EXTERNAL \
  -H ldapi:/// \
  -b "cn=config" \
  "(objectClass=*)"
# Authenticated as: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
# Mapped to: cn=admin,cn=config (full config access)
```

### Map external identity to directory DN

```ldif
# Map the SASL EXTERNAL identity to the admin DN
dn: cn=config
changetype: modify
add: olcAuthzRegexp
olcAuthzRegexp: "gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth"
  "cn=admin,dc=acme,dc=com"
```

-----

## Part 3: Client-Side TLS Configuration 🔧

Application clients need to know how to verify the server certificate:

```bash
# /etc/ldap/ldap.conf — system-wide LDAP client defaults
TLS_CACERT    /etc/ldap/ca.crt
TLS_REQCERT   demand          # Require and verify server certificate
TLS_PROTOCOL_MIN 3.3         # Minimum TLS 1.2
URI           ldaps://ldap1.acme.com ldaps://ldap2.acme.com
BASE          dc=acme,dc=com
```

```python
# Python ldap3 with TLS verification
import ldap3

tls_config = ldap3.Tls(
    ca_certs_file='/etc/ldap/ca.crt',
    validate=ssl.CERT_REQUIRED,
    version=ssl.PROTOCOL_TLS,
    ciphers='HIGH:!aNULL:!MD5'
)

server = ldap3.Server(
    'ldap1.acme.com',
    port=636,
    use_ssl=True,
    tls=tls_config,
    get_info=ldap3.ALL
)

conn = ldap3.Connection(
    server,
    user='cn=webapp-reader,ou=Services,dc=acme,dc=com',
    password='webappsecret',
    authentication=ldap3.SIMPLE,
    auto_bind=True
)
# Connection is TLS-encrypted and certificate-verified
```

-----

## Part 4: Index Configuration — The Forensic Filing Speed 📂

Without indexes, every search is a full scan of the entire database. With indexes, lookups are sub-millisecond even with millions of entries.

```ldif
# Add production indexes via cn=config (live — no restart)
dn: olcDatabase={1}mdb,cn=config
changetype: modify
replace: olcDbIndex
olcDbIndex: objectClass eq
olcDbIndex: entryUUID eq
olcDbIndex: entryCSN eq
olcDbIndex: uid eq,sub
olcDbIndex: cn eq,sub,pres
olcDbIndex: sn eq,sub,pres
olcDbIndex: givenName eq,sub
olcDbIndex: mail eq,sub
olcDbIndex: memberOf eq
olcDbIndex: member eq
olcDbIndex: uniqueMember eq
olcDbIndex: departmentNumber eq
olcDbIndex: employeeNumber eq
olcDbIndex: telephoneNumber eq
olcDbIndex: uidNumber eq
olcDbIndex: gidNumber eq
```

```bash
# Apply index configuration
ldapmodify -Y EXTERNAL -H ldapi:/// -f indexes.ldif

# Rebuild all indexes (needed after adding new indexes to existing data)
# Stop slapd first OR use slapindex with slapd running (since OpenLDAP 2.6)
slapindex -n 1
# For large databases: run during a maintenance window

# Verify indexes were created
ls -la /var/lib/ldap/
# Should show .bdb files for each indexed attribute
```

**Index type reference:**

|Type       |Keyword                                  |When to use                            |
|-----------|-----------------------------------------|---------------------------------------|
|Equality   |`eq`                                     |`(uid=alice)` — exact match queries    |
|Substring  |`sub`                                    |`(cn=*smith*)` — wildcard searches     |
|Presence   |`pres`                                   |`(mail=*)` — “attribute exists” queries|
|Approximate|`approx`                                 |`(cn~=Smyth)` — phonetic matching      |
|Ordering   |`ordering` (implied with eq for integers)|`(uidNumber>=10000)`                   |

-----

## Part 5: MDB Database Tuning — The Lab’s Storage System 💾

OpenLDAP uses LMDB (Lightning Memory-Mapped Database) as its storage engine. Key tuning parameters:

```ldif
# Tune the MDB database for production workloads
dn: olcDatabase={1}mdb,cn=config
changetype: modify
replace: olcDbMaxSize
olcDbMaxSize: 10737418240
# 10 GB maximum database size
# Set this LARGER than your actual data — LMDB pre-allocates the address space
# Actual disk usage grows as needed; this is just the upper bound

-
replace: olcDbMaxReaders
olcDbMaxReaders: 126
# Maximum concurrent read transactions
# Default 126 is usually sufficient; increase if you have many replicas

-
add: olcDbCheckpoint
olcDbCheckpoint: 512 30
# Checkpoint every 512 KB of transaction log OR every 30 minutes
# Faster checkpoints = faster recovery after crash, slightly more I/O
```

-----

## Part 6: Connection Pooling — The High-Traffic Lab 🚦

Simple authentication in production applications is expensive without connection pooling:

```
Without pool: each request → connect → bind → search → unbind → disconnect
With pool:    each request → get connection from pool → search → return to pool
```

```python
# Production connection pool with ldap3
import ldap3
from ldap3.utils.conv import escape_filter_chars

# Create a server pool with failover
server_pool = ldap3.ServerPool(
    [
        ldap3.Server('ldap1.acme.com', port=636, use_ssl=True,
                     tls=tls_config, get_info=ldap3.ALL),
        ldap3.Server('ldap2.acme.com', port=636, use_ssl=True,
                     tls=tls_config, get_info=ldap3.ALL),
    ],
    ldap3.ROUND_ROBIN,       # Load balance across servers
    active=True,             # Check server availability
    exhaust=True             # Use next server if current fails
)

# Create a reusable connection pool
pool = ldap3.Connection(
    server_pool,
    user='cn=webapp-reader,ou=Services,dc=acme,dc=com',
    password='webappsecret',
    client_strategy=ldap3.REUSABLE,   # Connection pool strategy
    pool_size=10,                      # 10 persistent connections
    pool_lifetime=3600,                # Recreate connections after 1 hour
    pool_keepalive=60,                 # Send keepalive every 60 seconds
    auto_bind=True
)

def lookup_user(uid: str) -> dict | None:
    safe_uid = escape_filter_chars(uid)
    with pool.connection() as conn:
        conn.search(
            search_base='ou=People,dc=acme,dc=com',
            search_filter=f'(uid={safe_uid})',
            search_scope=ldap3.SUBTREE,
            attributes=['cn', 'mail', 'memberOf', 'departmentNumber',
                        'acmeClearanceLevel', 'pwdAccountLockedTime']
        )
        if not conn.entries:
            return None
        entry = conn.entries[0]
        return {
            'cn': entry.cn.value,
            'mail': entry.mail.value,
            'memberOf': list(entry.memberOf) if entry.memberOf else [],
            'department': entry.departmentNumber.value,
            'locked': bool(getattr(entry, 'pwdAccountLockedTime', None))
        }
```

-----

## Part 7: The Complete Overlays Checklist 📋

A production OpenLDAP deployment should evaluate each overlay:

|Overlay     |Purpose                                   |Production recommendation                            |
|------------|------------------------------------------|-----------------------------------------------------|
|`syncprov`  |Replication provider                      |**Required** if you have consumers                   |
|`memberof`  |Back-reference group membership           |**Recommended** — enables fast “what groups is X in?”|
|`refint`    |Referential integrity on delete           |**Recommended** — prevents dangling group member DNs |
|`ppolicy`   |Password policy (lockout, expiry, history)|**Required** — never run production without lockout  |
|`accesslog` |Full LDAP operation audit log             |**Required** — compliance, forensics, delta-syncrepl |
|`unique`    |Enforce uniqueness across attributes      |**Recommended** — prevent duplicate uid/mail values  |
|`constraint`|Validate attribute value format           |**Recommended** — enforce mail syntax, UID ranges    |
|`dynlist`   |Dynamic group membership from search      |**Optional** — useful for role-based groups          |
|`rwm`       |Rewrite/remap attribute names             |**Optional** — legacy compatibility                  |
|`auditlog`  |Flat-file audit trail                     |**Optional** — simpler than accesslog, less queryable|

### The `unique` overlay — prevent duplicate UIDs

```ldif
dn: olcOverlay=unique,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcUniqueConfig
olcOverlay: unique
olcUniqueUri: ldap:///ou=People,dc=acme,dc=com?uid?sub
olcUniqueUri: ldap:///ou=People,dc=acme,dc=com?mail?sub
olcUniqueUri: ldap:///ou=People,dc=acme,dc=com?uidNumber?sub
olcUniqueUri: ldap:///ou=People,dc=acme,dc=com?employeeNumber?sub
```

### The `constraint` overlay — enforce valid values

```ldif
dn: olcOverlay=constraint,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcConstraintConfig
olcOverlay: constraint
# Email must match a valid format
olcConstraintAttribute: mail regex ^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$
# uidNumber must be between 10000 and 99999
olcConstraintAttribute: uidNumber count 1 urldomain:///ou=People,dc=acme,dc=com??sub?(uidNumber=*)
```

-----

## Part 8: The Complete Production Deployment 🏛️

```bash
#!/bin/bash
# ldap-production-verify.sh — verify a production LDAP deployment

LDAP_URI="ldaps://ldap1.acme.com:636"
BASE_DN="dc=acme,dc=com"
ADMIN_DN="cn=admin,dc=acme,dc=com"
ADMIN_PW="$LDAP_ADMIN_PASSWORD"  # from environment

echo "=== ACME LDAP Production Verification ==="

# 1. TLS check
echo ""
echo "1. TLS Certificate:"
openssl s_client \
  -connect ldap1.acme.com:636 \
  -CAfile /etc/ldap/ca.crt \
  -showcerts < /dev/null 2>&1 \
  | grep -E "(subject|issuer|notAfter)"

# 2. Connectivity
echo ""
echo "2. Connectivity:"
ldapwhoami -x -H "$LDAP_URI" \
  -D "$ADMIN_DN" -w "$ADMIN_PW" && echo "  Admin bind: OK" || echo "  Admin bind: FAILED"

# 3. Entry count
echo ""
echo "3. Entry counts:"
for OU in People Groups Services Policies; do
  COUNT=$(ldapsearch -x -H "$LDAP_URI" \
    -D "$ADMIN_DN" -w "$ADMIN_PW" \
    -b "ou=$OU,$BASE_DN" \
    "(objectClass=*)" 1.1 2>/dev/null \
    | grep "^dn:" | wc -l)
  echo "  ou=$OU: $COUNT entries"
done

# 4. Replication check
echo ""
echo "4. Replication (contextCSN):"
for HOST in ldap1.acme.com ldap2.acme.com; do
  CSN=$(ldapsearch -x -H "ldaps://$HOST:636" \
    -D "$ADMIN_DN" -w "$ADMIN_PW" \
    -b "$BASE_DN" -s base "(objectClass=*)" contextCSN 2>/dev/null \
    | grep contextCSN | head -1)
  echo "  $HOST: ${CSN:-NOT REACHABLE}"
done

# 5. Key overlay verification
echo ""
echo "5. Active overlays:"
ldapsearch -Y EXTERNAL -H ldapi:/// \
  -b "olcDatabase={1}mdb,cn=config" -s one \
  "(objectClass=olcOverlayConfig)" \
  olcOverlay 2>/dev/null \
  | grep "^olcOverlay:" | sort

# 6. Index verification
echo ""
echo "6. Indexes:"
ldapsearch -Y EXTERNAL -H ldapi:/// \
  -b "olcDatabase={1}mdb,cn=config" -s base \
  "(objectClass=*)" olcDbIndex 2>/dev/null \
  | grep "^olcDbIndex:"

# 7. ppolicy test
echo ""
echo "7. Password policy (default):"
ldapsearch -x -H "$LDAP_URI" \
  -D "$ADMIN_DN" -w "$ADMIN_PW" \
  -b "cn=default,ou=Policies,$BASE_DN" \
  "(objectClass=pwdPolicy)" \
  pwdMaxFailure pwdLockout pwdMaxAge 2>/dev/null \
  | grep "^pwd"

echo ""
echo "=== Verification Complete ==="
```

-----

## The Production Deployment Manifest 📋

A reference architecture for a hardened LDAP deployment:

```
ldap1.acme.com (Primary — provider)
├── slapd with LDAPS on :636 + ldapi:///
├── Overlays: syncprov, memberof, refint, ppolicy, accesslog, unique
├── cn=config: all configuration via OLC (no slapd.conf)
├── LMDB: 10GB max, checkpoint 512/30
├── Indexes: uid, cn, sn, mail, memberOf, member, uidNumber, gidNumber, objectClass
├── TLS 1.2+ minimum, cipher suite HIGH:!aNULL:!MD5
├── ACLs: admin=manage, self=write (safe attrs), service=read, anon=auth only
└── Monitoring: cn=monitor database, Prometheus LDAP exporter

ldap2.acme.com (Secondary — consumer/MirrorMode)
├── Identical configuration to primary
├── olcMirrorMode: TRUE
├── syncrepl from ldap1 (rid=001)
└── ldap1 syncrepl from ldap2 (rid=002)

Clients:
├── Applications bind to server pool [ldap1, ldap2], round-robin
├── ldap3 REUSABLE pool, 10 connections, 3600s lifetime
├── All binds over LDAPS (port 636)
├── Service account: cn=webapp-reader (read-only, specific attributes only)
└── LDAP injection prevention: escape_filter_chars on all user input
```

-----

## The Series: Eight Cases Closed 🏁

*Grissom walks the length of the investigation board. Every case file: CLOSED.*

**GRISSOM:** “Eight episodes. Eight case files.”

*He reads each one.*

**GRISSOM:** “Episode 1: The question. Not ‘who are you?’ but ‘what are you?’ We met LDAP — a classification system, not a password checker. An entry is a complete dossier: type, attributes, relationships, history.”

**GRISSOM:** “Episode 2: The dossier. The Distinguished Name — a fingerprint. The objectClass chain — DNA evidence. The operational attributes — chain of custody. The Root DSE — the morgue’s master register.”

**GRISSOM:** “Episode 3: The filing cabinet. DIT design — three patterns, each a commitment. The schema — the forensic standard every entry must meet. Custom schema — extending the classification vocabulary.”

**GRISSOM:** “Episode 4: The search warrant. Bind first — show your badge. Then the search: baseDN, scope, filter. The RFC 4515 filter language: AND, OR, NOT, wildcard, presence, substring. LDAP injection — always escape user input.”

**GRISSOM:** “Episode 5: The evidence log. Add, modify, delete, modifyDN. The LDIF modification format. The accesslog overlay — the wiretap that records everything. The auditlog — the written record.”

**GRISSOM:** “Episode 6: Gang memberships and lockup. groupOfNames, posixGroup. The memberOf overlay — the auto-updating roster. The ppolicy overlay — lockout, expiry, history. Access Control Instructions — the final policy gate.”

**GRISSOM:** “Episode 7: The police radio. syncrepl — provider and consumer. Delta-syncrepl for efficiency. MirrorMode for high availability. cn=config — the live configuration system that never needs a restart. Referrals — the precinct transfer.”

**GRISSOM:** “Episode 8: This one. LDAPS, StartTLS. SASL EXTERNAL — certificate authentication for the most privileged operations. Indexes for performance. MDB tuning. The overlays checklist. Connection pooling. The complete production deployment.”

*He turns to face the team.*

**GRISSOM:** “The question was always: what are you? Not who — what. What objectClass, what attributes, what groups, what policies apply. The LDAP directory answers that question for every entry, every time, consistently. The crime is when the answer is wrong. Our job is to make sure it never is.”

*He closes the last case file.*

**GRISSOM:** “Case closed.”

*🎵 What are you? What what, what what? 🎵*

*The lab hums. An authentication request arrives. The directory processes it in 0.4 milliseconds. The entry is returned. The attributes are correct. The answer is complete.*

*What are you?*

*Fully classified.*

-----

**🔗 Resources**

- **OpenLDAP TLS configuration**: [openldap.org/doc/admin26/tls.html](https://openldap.org/doc/admin26/tls.html)
- **OpenLDAP SASL**: [openldap.org/doc/admin26/sasl.html](https://openldap.org/doc/admin26/sasl.html)
- **LMDB (MDB) tuning**: [openldap.org/doc/admin26/backends.html](https://openldap.org/doc/admin26/backends.html)
- **ldap3 Python library (connection pool)**: [ldap3.readthedocs.io](https://ldap3.readthedocs.io)
- **RFC 4513 — LDAP Authentication Methods**: [rfc-editor.org/rfc/rfc4513](https://www.rfc-editor.org/rfc/rfc4513)

-----

*🔬 What Are You LDAP? — eight cases, one directory, zero unclassified entries. The investigation is complete.*
