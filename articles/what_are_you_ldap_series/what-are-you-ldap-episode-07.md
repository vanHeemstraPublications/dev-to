---
title: "What Are You LDAP? 🔬 Ep.7"
published: false
description: "Episode 7: One lab cannot cover the whole city. When a change is made on the provider server, the consumer needs to know — immediately, reliably, without gaps. That is syncrepl: the police radio of LDAP replication. This episode covers the provider/consumer model, delta-syncrepl for efficiency, multi-master for resilience, and cn=config (Online Configuration) — the only way to reconfigure a live LDAP server without restarting it."
tags: [ldap, replication, openldap, infrastructure]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-are-you-ldap-episode-07.png"
series: "What Are You LDAP?"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

## Episode 7: The Police Radio

*🎵 What are you? What what, what what? 🎵*

-----

## “All Units, Please Copy” 📻

*Warrick Brown stands at a whiteboard. Two rectangles: PROVIDER and CONSUMER. An arrow between them labelled SYNCREPL.*

**WARRICK:** “One lab cannot cover a city this size. Las Vegas North has its own precinct. Las Vegas South has its own. When a new suspect profile is added at North, South needs to know. When a password changes at North, South needs to reflect that before the suspect tries to authenticate there.”

*He draws the arrow.*

**WARRICK:** “The police radio. In LDAP terms: replication. The provider broadcasts every change. The consumers listen and apply. If a consumer misses a transmission, it catches up from a checkpoint. No gaps. No stale data. Every lab in the city asks the same question — and gets the same answer.”

*He caps the marker.*

**WARRICK:** “And while we are here: the online configuration system. Because in this precinct, you do not shut down the lab to reconfigure it. The lab stays open. You modify `cn=config`. The configuration changes live.”

-----

## 🗂️ SIPOC — The Police Radio Network

|**Suppliers**       |**Inputs**                                          |**Process**                                                                                         |**Outputs**                                                                    |**Customers**                                                                             |
|--------------------|----------------------------------------------------|----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
|Provider LDAP server|All write operations on the main database           |`syncprov` overlay stamps each change with a CSN (Change Sequence Number); maintains a changelog    |A replication stream of all changes, queryable by CSN                          |Consumer servers — which pull changes and apply them to their local replicas              |
|Consumer LDAP server|Provider URI, bind credentials, baseDN, starting CSN|`syncrepl` directive in consumer config; persistent connection to provider; applies received changes|An up-to-date local replica of the provider’s data                             |Applications connecting to this consumer — which receive identical answers to the provider|
|cn=config (OLC)     |LDIF modifications to `cn=config` subtree           |Live configuration changes applied without slapd restart                                            |Updated running configuration — new overlays, new ACLs, new database parameters|The running slapd — which picks up changes immediately                                    |

-----

## Part 1: How LDAP Replication Works — The Broadcast Model 📡

OpenLDAP uses **syncrepl** — defined in RFC 4533 (LDAP Content Synchronization Protocol). It is a **pull** model: the consumer asks the provider for changes.

```
Provider server (ldap1.acme.com):
  ┌─────────────────────────────────────────────┐
  │  Main database: dc=acme,dc=com              │
  │  syncprov overlay: tracks all changes       │
  │  accesslog (for delta-syncrepl): optional   │
  └─────────────────┬───────────────────────────┘
                    │ Consumer pulls changes (persistent search)
                    │ over persistent TCP connection
                    ▼
Consumer server (ldap2.acme.com):
  ┌─────────────────────────────────────────────┐
  │  Local replica: dc=acme,dc=com              │
  │  syncrepl directive: connects to provider   │
  │  Applies received changes locally           │
  └─────────────────────────────────────────────┘
```

**Two syncrepl modes:**

|Mode               |How it works                                                          |When to use                            |
|-------------------|----------------------------------------------------------------------|---------------------------------------|
|`refreshOnly`      |Consumer polls provider on a schedule; gets all changes since last CSN|Low-frequency sync, small directories  |
|`refreshAndPersist`|Consumer opens a persistent connection; changes pushed as they happen |Production — near-real-time replication|

-----

## Part 2: Configuring the Provider — The Broadcasting Station 📢

The provider needs the `syncprov` overlay to track and serve changes:

```ldif
# syncprov overlay on the provider's main database
dn: olcOverlay=syncprov,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: syncprov
olcSpCheckpoint: 100 10    # Checkpoint every 100 ops OR 10 minutes
olcSpSessionLog: 100       # Keep last 100 changes in memory for fast catch-up
```

```bash
ldapadd \
  -Y EXTERNAL \
  -H ldapi:/// \
  -f syncprov.ldif
```

The provider also needs a dedicated bind DN that the consumer will use to connect:

```ldif
# Create a replication service account on the provider
dn: cn=replicator,ou=Services,dc=acme,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
cn: replicator
sn: replicator
description: LDAP replication service account
userPassword: {SSHA}replsecrethashedvalue
```

```ldif
# Grant the replicator DN read access to the entire directory
# Add to the provider's ACL (olcAccess)
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcAccess
olcAccess: {0}to *
  by dn.exact="cn=replicator,ou=Services,dc=acme,dc=com" read
  by * break
```

-----

## Part 3: Configuring the Consumer — The Listening Post 🎧

The consumer uses a `syncrepl` directive in its database configuration:

```ldif
# Consumer configuration — syncrepl directive
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcSyncRepl
olcSyncRepl: rid=001
  provider=ldap://ldap1.acme.com:389
  bindmethod=simple
  binddn="cn=replicator,ou=Services,dc=acme,dc=com"
  credentials=replsecret
  searchbase="dc=acme,dc=com"
  filter="(objectClass=*)"
  scope=sub
  schemachecking=on
  type=refreshAndPersist
  retry="5 5 30 5 60 +"
  interval=00:00:05:00
  starttls=critical
  tls_reqcert=demand
  tls_cacert=/etc/ldap/ca-cert.pem
```

```ldif
# Also set the updateref — where consumers direct writes
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcUpdateRef
olcUpdateRef: ldap://ldap1.acme.com
```

**Parameter breakdown:**

|Parameter          |Value                  |Meaning                                                        |
|-------------------|-----------------------|---------------------------------------------------------------|
|`rid`              |`001`                  |Replication ID — unique per consumer per syncrepl              |
|`provider`         |`ldap://ldap1.acme.com`|Provider URI                                                   |
|`type`             |`refreshAndPersist`    |Persistent connection mode                                     |
|`retry`            |`5 5 30 5 60 +`        |Retry: 5 times every 5s, then 5 times every 30s, then every 60s|
|`starttls=critical`|—                      |Require TLS — fail if not available                            |
|`schemachecking=on`|—                      |Validate received entries against local schema                 |

```bash
# Apply consumer config
ldapmodify \
  -Y EXTERNAL \
  -H ldapi:/// \
  -f consumer-syncrepl.ldif

# Verify replication is working
ldapsearch \
  -x \
  -H ldap://ldap2.acme.com \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)" \
  cn uid
# If this returns Alice's entry, replication is working

# Check consumer sync status
ldapsearch \
  -Y EXTERNAL \
  -H ldapi:/// \
  -b "cn=config" \
  "(olcDatabase={1}mdb)" \
  olcSyncRepl
```

-----

## Part 4: Delta-syncrepl — The Efficient Radio 🎯

Standard `syncrepl` sends entire entry contents when anything changes. **Delta-syncrepl** sends only what changed — attribute by attribute. Requires the `accesslog` overlay on the provider.

```
Standard syncrepl:
  Alice's email changes → provider sends entire Alice entry (20 attributes)

Delta-syncrepl:
  Alice's email changes → provider sends only: mail: new@acme.com (1 attribute)
```

### Configuring delta-syncrepl on the provider

```ldif
# Step 1: Enable accesslog overlay (Episode 5 covered this)
# The accesslog database must be at cn=accesslog

# Step 2: Configure syncprov on the ACCESSLOG database too
dn: olcOverlay=syncprov,olcDatabase={2}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: syncprov
olcSpNoPresent: TRUE    # Skip present phase — accesslog doesn't need it
olcSpReloadHint: TRUE   # Allow reload hint for startup sync
```

### Configuring delta-syncrepl on the consumer

```ldif
dn: olcDatabase={1}mdb,cn=config
changetype: modify
replace: olcSyncRepl
olcSyncRepl: rid=001
  provider=ldap://ldap1.acme.com:389
  bindmethod=simple
  binddn="cn=replicator,ou=Services,dc=acme,dc=com"
  credentials=replsecret
  searchbase="dc=acme,dc=com"
  scope=sub
  type=refreshAndPersist
  retry="5 5 30 5 60 +"
  syncdata=accesslog          # ← KEY: use accesslog for delta sync
  logbase="cn=accesslog"      # ← Where the accesslog lives
  logfilter="(&(objectClass=auditWriteObject)(reqResult=0))"
  schemachecking=off
  starttls=critical
```

-----

## Part 5: Multi-Master — Two Labs, Equal Authority 🏛️🏛️

In standard replication, the provider is authoritative — all writes go to the provider. **MirrorMode** (OpenLDAP’s multi-master) allows two servers to both accept writes and replicate to each other.

```
  ldap1.acme.com ←──────────────── ldap2.acme.com
       │         syncrepl (both ways)      │
       │                                   │
  Writes go here                    Writes also go here
  (primary data centre)             (secondary data centre)
```

### Configure MirrorMode (on both servers)

```ldif
# On BOTH servers: set serverID (must be unique per server)
# Server 1:
dn: cn=config
changetype: modify
replace: olcServerID
olcServerID: 1 ldap://ldap1.acme.com
olcServerID: 2 ldap://ldap2.acme.com

# Server 2:
dn: cn=config
changetype: modify
replace: olcServerID
olcServerID: 2 ldap://ldap2.acme.com
olcServerID: 1 ldap://ldap1.acme.com
```

```ldif
# On BOTH servers: enable MirrorMode on the database
dn: olcDatabase={1}mdb,cn=config
changetype: modify
replace: olcMirrorMode
olcMirrorMode: TRUE
```

```ldif
# On Server 1: replicate FROM Server 2
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcSyncRepl
olcSyncRepl: rid=002
  provider=ldap://ldap2.acme.com:389
  binddn="cn=replicator,ou=Services,dc=acme,dc=com"
  credentials=replsecret
  searchbase="dc=acme,dc=com"
  type=refreshAndPersist
  retry="5 5 30 5 60 +"
  starttls=critical

# On Server 2: replicate FROM Server 1
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcSyncRepl
olcSyncRepl: rid=001
  provider=ldap://ldap1.acme.com:389
  binddn="cn=replicator,ou=Services,dc=acme,dc=com"
  credentials=replsecret
  searchbase="dc=acme,dc=com"
  type=refreshAndPersist
  retry="5 5 30 5 60 +"
  starttls=critical
```

**GRISSOM:** “MirrorMode is not true multi-master in the LDAP sense — simultaneous conflicting writes can still occur. OpenLDAP resolves conflicts by CSN ordering: the change with the later CSN wins. For most workloads — authentication lookups, occasional user updates — this is acceptable. The key benefit is write availability: if one server is down, the other still accepts all operations.”

-----

## Part 6: Monitoring Replication — Is the Radio Working? 📊

```bash
# Check the consumer's sync state
ldapsearch \
  -Y EXTERNAL \
  -H ldapi:/// \
  -b "cn=config" \
  "(olcDatabase={1}mdb)" \
  olcSyncRepl

# Verify both servers have the same entry
# On provider:
ldapsearch -x -H ldap://ldap1.acme.com \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" "(uid=alice)" \
  entryCSN modifyTimestamp

# On consumer:
ldapsearch -x -H ldap://ldap2.acme.com \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" "(uid=alice)" \
  entryCSN modifyTimestamp

# The entryCSN should be IDENTICAL on both servers
# If provider has a later CSN, consumer is lagging

# Check replication lag via contextCSN
ldapsearch -x -H ldap://ldap1.acme.com \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "dc=acme,dc=com" -s base \
  "(objectClass=*)" contextCSN

ldapsearch -x -H ldap://ldap2.acme.com \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "dc=acme,dc=com" -s base \
  "(objectClass=*)" contextCSN

# If contextCSN differs: consumer is behind
# If same: replication is current
```

-----

## Part 7: cn=config — The Live Configuration System ⚙️

**cn=config** (OLC — Online LDAP Configuration) is a special LDAP database that holds the entire server configuration. Instead of editing `slapd.conf` and restarting, you make LDAP operations against `cn=config` and the changes take effect immediately.

```
cn=config
├── cn=module{0},cn=config          ← Loaded modules
├── cn=schema,cn=config             ← Schema
│   ├── cn={0}core,cn=schema,...    ← Core schema
│   ├── cn={1}cosine,cn=schema,...
│   ├── cn={2}inetorgperson,...
│   └── cn={4}acme,...              ← Custom schema
├── olcDatabase={-1}frontend,...    ← Global defaults
├── olcDatabase={0}config,...       ← Config database itself
└── olcDatabase={1}mdb,...          ← Main data database
    └── olcOverlay={0}syncprov,...  ← Overlays on main db
```

### Viewing the live configuration

```bash
# View entire cn=config tree
ldapsearch \
  -Y EXTERNAL \
  -H ldapi:/// \
  -b "cn=config" \
  "(objectClass=*)" \
  "*" "+"

# View just the main database configuration
ldapsearch \
  -Y EXTERNAL \
  -H ldapi:/// \
  -b "olcDatabase={1}mdb,cn=config" \
  -s base \
  "(objectClass=*)"

# View currently active access controls
ldapsearch \
  -Y EXTERNAL \
  -H ldapi:/// \
  -b "olcDatabase={1}mdb,cn=config" \
  -s base \
  "(objectClass=*)" \
  olcAccess
```

### Modifying live configuration

```bash
# Add a new index to the running database (no restart)
ldapmodify \
  -Y EXTERNAL \
  -H ldapi:/// << 'EOF'
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcDbIndex
olcDbIndex: memberOf eq
olcDbIndex: departmentNumber eq,sub
olcDbIndex: employeeNumber eq
EOF

# Then rebuild the indexes
slapindex -n 1    # Brief pause — do during low-traffic window

# Change the admin password live
ldapmodify \
  -Y EXTERNAL \
  -H ldapi:/// << 'EOF'
dn: olcDatabase={1}mdb,cn=config
changetype: modify
replace: olcRootPW
olcRootPW: {SSHA}new_hashed_password_here
EOF

# Load a new module without restart
ldapmodify \
  -Y EXTERNAL \
  -H ldapi:/// << 'EOF'
dn: cn=module{0},cn=config
changetype: modify
add: olcModuleLoad
olcModuleLoad: memberof.la
EOF
```

**NICK:** “The `ldapi:///` URI is the Unix socket connection — connects directly to the slapd process on the same machine, bypasses TCP, and authenticates using the EXTERNAL SASL mechanism based on the Unix process credentials. The root user on the server gets admin access to `cn=config` automatically. No password needed. No network required. This is how you manage LDAP without LDAP being fully functional.”

-----

## Part 8: Referrals — The Precinct Transfer 🗺️

A **referral** is LDAP’s way of saying “the entry you want is not here — try this other server.” The server returns a referral result (code 10) with a URI pointing elsewhere.

```ldif
# Add a referral for a subtree managed by another server
dn: dc=subsidiary,dc=acme,dc=com
objectClass: top
objectClass: referral
objectClass: extensibleObject
dc: subsidiary
ref: ldap://ldap-subsidiary.acme.com/dc=subsidiary,dc=acme,dc=com
```

```bash
# Query for an entry under the referral subtree
ldapsearch \
  -x \
  -H ldap://ldap1.acme.com \
  -b "ou=Users,dc=subsidiary,dc=acme,dc=com" \
  "(uid=frank)"

# Server returns code 10 (referral):
# Result: Referral (10)
# Referrals:
#   ldap://ldap-subsidiary.acme.com/ou=Users,dc=subsidiary,dc=acme,dc=com

# Client follows the referral automatically with -C flag
ldapsearch \
  -x \
  -H ldap://ldap1.acme.com \
  -C \                    # ← Follow referrals automatically
  -b "ou=Users,dc=subsidiary,dc=acme,dc=com" \
  "(uid=frank)"
# Now queries ldap-subsidiary.acme.com directly
```

-----

## Replication Monitoring Script 🔍

```bash
#!/bin/bash
# check-replication.sh — verify all consumers match the provider

PROVIDER="ldap://ldap1.acme.com"
CONSUMERS=("ldap://ldap2.acme.com" "ldap://ldap3.acme.com")
BIND_DN="cn=monitor,dc=acme,dc=com"
BIND_PW="monitorsecret"
BASE_DN="dc=acme,dc=com"

# Get provider contextCSN
PROVIDER_CSN=$(ldapsearch \
  -x -H "$PROVIDER" \
  -D "$BIND_DN" -w "$BIND_PW" \
  -b "$BASE_DN" -s base \
  "(objectClass=*)" contextCSN 2>/dev/null \
  | grep contextCSN | awk '{print $2}')

echo "Provider CSN: $PROVIDER_CSN"

for CONSUMER in "${CONSUMERS[@]}"; do
  CONSUMER_CSN=$(ldapsearch \
    -x -H "$CONSUMER" \
    -D "$BIND_DN" -w "$BIND_PW" \
    -b "$BASE_DN" -s base \
    "(objectClass=*)" contextCSN 2>/dev/null \
    | grep contextCSN | awk '{print $2}')

  if [ "$PROVIDER_CSN" = "$CONSUMER_CSN" ]; then
    echo "  $CONSUMER: IN SYNC ✓"
  else
    echo "  $CONSUMER: LAGGING ✗"
    echo "    Consumer CSN: $CONSUMER_CSN"
  fi
done
```

-----

## What’s Next: Case Closed 🏁

*Catherine Willows looks at the complete investigation board. Every episode case closed. One remains.*

**CATHERINE:** “Seven episodes. We know what LDAP is. We know what an entry contains. We know how the DIT is structured, how to search, how to modify, how to audit, how groups and policies work, how replication keeps everything synchronized.”

*She points to the final case file.*

**CATHERINE:** “Episode 8. The hardening. The production lab. LDAPS — the encrypted evidence bag. SASL EXTERNAL — certificate authentication for the most sensitive operations. Performance tuning: indexes, connection pools, MDB tuning. The complete production checklist. Case closed.”

-----

**🔗 Resources**

- **OpenLDAP Replication**: [openldap.org/doc/admin26/replication.html](https://openldap.org/doc/admin26/replication.html)
- **RFC 4533 — LDAP Content Sync**: [rfc-editor.org/rfc/rfc4533](https://www.rfc-editor.org/rfc/rfc4533)
- **cn=config (OLC)**: [openldap.org/doc/admin26/slapdconf2.html](https://openldap.org/doc/admin26/slapdconf2.html)

-----

*🔬 What Are You LDAP? — a CSI-style investigation into the directory service that classifies every identity. The evidence is in the entry. The answers are in the attributes.*
