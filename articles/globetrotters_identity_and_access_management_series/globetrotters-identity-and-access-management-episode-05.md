---
title: "Globetrotters Identity and Access Management 🌍 Ep.5"
part: 5
published: false
description: "Episode 5: The border officer cross-checks your stamp against the filing cabinet — but what is in that cabinet? LDAP directories are the physical record store of every identity, group membership, and authentication credential. This episode opens the drawer: directory structure, user objects, groups, LDAPS encryption, and ACME’s dual-DC design."
tags: [iam, ldap, security, directories]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters_identity_and_access_management_series/globetrotters-identity-and-access-management-episode-05.png"
series: "Globetrotters Identity and Access Management Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 5: The Ministry’s Filing Cabinet

> *“The border officer consulted a terminal. That terminal queried a database. That database was populated from a filing cabinet that has been growing, record by record, since the first identity was enrolled.”*

-----

## The Cabinet at the Core of Everything 🗄️

Every other component in ACME’s IAM stack is, ultimately, a query against the LDAP directory. SailPoint provisions changes into it. RWT sources identity claims from data synchronised from it. IDV validates tokens by looking up live records in it. The LDAP LB-T routes queries to it.

LDAP — the Lightweight Directory Access Protocol — is one of the oldest protocols in enterprise IT and one of the most durable. It was designed to answer one question efficiently: “Does this identity have this attribute or group membership?” In a well-designed LDAP deployment, that answer comes back in milliseconds, at scale, from a replicated directory that spans multiple data centres.

ACME runs three LDAP servers in its IAM topology. Two hold production identities for the General Manufacturing (GMF) domain, one in CITY-A and one in CITY-B. One holds acceptance-environment identities. This episode explains what is inside them, how they are structured, and why the dual-DC design exists.

-----

## 🗂️ SIPOC — The Filing Cabinet

|**Suppliers**        |**Inputs**                                                                        |**Process**                                                                                   |**Outputs**                                                                      |**Customers**                                                                         |
|---------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
|SailPoint PRD        |Provisioning events: create user, add to group, remove from group, disable account|LDAP write operations: `ldapadd`, `ldapmodify`, `ldapdelete`                                  |Updated directory objects reflecting the current authorised state                |Every component that reads LDAP: IDV PRD, LDAP LB-T, direct-binding services          |
|Client / service     |LDAP bind request with DN + password                                              |Directory authentication: verify the credential against the stored password hash              |Bind success or failure                                                          |The bound session — authenticated, authorised to query within the bind account’s scope|
|IDV / any LDAP client|LDAP search request: `(uid=svc-testfactory-prod)`                                 |Directory search: traverse the DIT from the search base, apply filter, return matching objects|LDAP entries with requested attributes: `memberOf`, `accountStatus`, `department`|IDV, LDAP LB-T clients, Test Factory service — resolved identity context              |

-----

## LDAP Directory Structure: The Directory Information Tree 🌳

LDAP organises records in a hierarchical tree called the **Directory Information Tree (DIT)**. The structure mirrors an address — you navigate from the widest scope (the country) down to the specific record (the individual person or service account).

ACME’s GMF domain tree:

```
dc=acme,dc=com                    ← Root: the domain
│
└── dc=gmf,dc=acme,dc=com         ← GMF subtree (General Manufacturing)
    │
    ├── ou=people,dc=gmf,...       ← Organisational unit: human identities
    │   ├── uid=jane.smith,...     ← Individual user object
    │   └── uid=john.doe,...
    │
    ├── ou=services,dc=gmf,...     ← Organisational unit: service accounts
    │   ├── uid=svc-testfactory-prod,...  ← Test Factory service account
    │   └── uid=svc-idv-prd,...           ← IDV service account
    │
    └── ou=groups,dc=gmf,...       ← Organisational unit: groups
        ├── cn=grp-testfactory,...
        ├── cn=grp-ldap-bind-t,...
        ├── cn=grp-platform-eng,...
        └── cn=grp-audit-read,...
```

Every record has a **Distinguished Name (DN)** — the full path from root to the specific record:

```
uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
```

This DN is the address of the Test Factory service account. Any LDAP bind or search that references this account uses this exact string.

-----

## LDAP Objects: What Is in Each Record 📋

Every LDAP object has a **schema** — a defined set of attributes it may or must carry. Different object classes carry different attributes.

### User object (inetOrgPerson + custom ACME attributes)

```
dn: uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
objectClass: inetOrgPerson
objectClass: acmeServiceAccount
uid: svc-testfactory-prod
cn: Test Factory Production Service Account
sn: Service
mail: testfactory-svc@acme.com
userPassword: {SSHA}...            ← Hashed — never stored plaintext
accountStatus: active
department: Test Factory
l: city-a
memberOf: cn=grp-testfactory,ou=groups,dc=gmf,dc=acme,dc=com
memberOf: cn=grp-ldap-bind-t,ou=groups,dc=gmf,dc=acme,dc=com
acmeCreatedBy: sailpoint-provisioner
acmeLastCertified: 2026-03-01
```

Key attributes for the Test Factory:

|Attribute          |Purpose                                   |IAM relevance                                                 |
|-------------------|------------------------------------------|--------------------------------------------------------------|
|`uid`              |Unique identifier within the directory    |Used as the bind DN component                                 |
|`userPassword`     |Hashed credential for LDAP bind           |Never stored plaintext; verified at bind time                 |
|`accountStatus`    |`active` / `disabled`                     |IDV and direct binders check this                             |
|`memberOf`         |Group memberships                         |Authorisation decisions — which groups this account belongs to|
|`acmeLastCertified`|When SailPoint last certified this account|Compliance tracking                                           |

### Group object (groupOfNames)

```
dn: cn=grp-testfactory,ou=groups,dc=gmf,dc=acme,dc=com
objectClass: groupOfNames
cn: grp-testfactory
description: Test Factory operator access group
member: uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
member: uid=jane.smith,ou=people,dc=gmf,dc=acme,dc=com
```

Groups contain `member` attributes listing the DNs of every account in the group. The `memberOf` attribute on user objects is the inverse view — maintained as an operational attribute by the directory server.

-----

## Authentication via LDAP: The Bind Operation 🔑

When a service binds to LDAP, it performs a **simple bind** (or SASL bind for stronger security) by presenting:

1. Its distinguished name (the full DN of its account)
1. Its password (matched against the `userPassword` hash in the directory)

The bind is the authentication event — the filing cabinet checking whether the key fits the lock:

```
LDAP Bind Request:
  DN:       uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
  Password: [plaintext credential, sent over LDAPS-encrypted channel]

Directory processes:
  1. Find the object at the specified DN
  2. Hash the presented password using the stored hash algorithm
  3. Compare: does the hash of the presented password match the stored hash?
  4a. Match → bind success; session authenticated as this DN
  4b. No match → bind failure; log the attempt; return LDAP ResultCode 49 (invalidCredentials)
```

After a successful bind, the session is authorised to perform LDAP operations within the scope the bound account’s ACLs permit.

-----

## LDAP vs LDAPS: Postcard vs Sealed Pouch 📬

**LDAP on port 389** is unencrypted. Every bind operation — including the password — travels in plaintext across the network. Any device on the path between the client and the LDAP server can read the password. On a well-controlled internal network this may be tolerable; on any shared or untrusted segment it is a critical security risk.

**LDAPS on port 636** wraps the LDAP session in TLS. The connection is encrypted from the first byte. The client must trust the server’s certificate (issued by ACME Root CA), and the server validates that the certificate chain is intact before completing the TLS handshake.

```
LDAP  (port 389):  Client ──PLAINTEXT──► LDAP Server
                   Anyone on the wire can read: bind DN, password, search results

LDAPS (port 636):  Client ──TLS─────────────────────────────► LDAP Server
                   TLS handshake validates server cert
                   All LDAP traffic encrypted end-to-end
```

**ACME’s requirement**: the Test Factory solution connects to LDAP LB-T on port 636 (LDAPS). No plaintext LDAP connections are permitted for service account authentication. The TLS certificate presented by LDAP LB-T must chain to ACME Root CA — our trust anchor (Episode 7).

-----

## ACME’s Three LDAP Servers 🗂️

From ACME’s topology:

|Server                 |Location          |Environment|GDS instance |Role                                      |
|-----------------------|------------------|-----------|-------------|------------------------------------------|
|**AUTH GMF PRD city-a**|CITY-A Data Centre|Production |gds-city-a   |Primary PRD directory, served by CITY-A DC|
|**AUTH GMF PRD city-b**|CITY-B Data Centre|Production |gds-city-b   |Replica PRD directory, served by CITY-B DC|
|**AUTH GMF ACC**       |Not specified     |Acceptance |Not specified|Acceptance-environment directory          |

### Replication between city-a and city-b

The two production LDAP servers are **replicas** of each other — they hold identical copies of the GMF PRD directory, kept synchronised by the LDAP replication protocol. When SailPoint provisions a new account or modifies a group membership, the change is written to one server and replicated to the other within seconds.

From the client’s perspective (routed through LDAP LB-T), the two servers appear as a single directory. The load balancer routes each query to whichever server is healthy and available:

```
GMF PRD LDAP LB-T
  │
  ├──► AUTH GMF PRD city-a (gds-city-a, CITY-A DC)    ← Active
  └──► AUTH GMF PRD city-b (gds-city-b, CITY-B DC)    ← Active (replica)

If city-a is unavailable:
GMF PRD LDAP LB-T
  │
  ├──► AUTH GMF PRD city-a    ← Health check: FAIL → route away
  └──► AUTH GMF PRD city-b    ← All queries routed here until city-a recovers
```

### ACC isolation

AUTH GMF ACC is completely separate from the production directory. It holds acceptance-environment identity records — test accounts, test service accounts, and test group memberships. Changes to AUTH GMF ACC do not affect the production directory and vice versa.

IDV ACC queries AUTH GMF ACC. IDV PRD queries AUTH GMF PRD. There is no cross-environment LDAP resolution.

-----

## LDAP Search Operations: What IDV Actually Asks 🔍

When IDV resolves a token’s identity claims against LDAP, it performs a **search operation**:

```
LDAP Search:
  BaseDN:    dc=gmf,dc=acme,dc=com
  Scope:     SUBTREE
  Filter:    (uid=svc-testfactory-prod)
  Attributes: memberOf, accountStatus, department, l

Response:
  dn: uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
  memberOf: cn=grp-testfactory,ou=groups,dc=gmf,dc=acme,dc=com
  memberOf: cn=grp-ldap-bind-t,ou=groups,dc=gmf,dc=acme,dc=com
  accountStatus: active
  department: Test Factory
  l: city-a
```

The filter `(uid=svc-testfactory-prod)` is an LDAP search filter — equivalent to `WHERE uid = 'svc-testfactory-prod'` in SQL terms. The directory returns all matching objects with the requested attributes.

-----

## Practical LDAP Concepts for the Test Factory 🔧

**Our bind account:** `uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com`
This is the DN our Test Factory solution presents when binding to LDAP LB-T. Its password must be stored in a secrets vault — never in configuration files or source code.

**Group verification:** After binding, our solution can search for its own `memberOf` attributes to confirm it has been correctly provisioned into the groups SailPoint should have created.

**Account status check:** If `accountStatus: disabled` is returned for our service account, the bind will succeed (if the password is correct) but downstream authorisation decisions will reject it. Monitoring for account status is an operational concern.

**Replication lag awareness:** In rare cases during SailPoint provisioning operations, city-a and city-b may be briefly out of sync (seconds to minutes). If our bind returns a group that was just added, and IDV’s query routes to city-b before replication completes, IDV may return stale data. This is an edge case but worth understanding for debugging intermittent authorisation failures.

-----

In **Episode 6**, we arrive at the checkpoint dispatcher — LDAP LB-T. Why it exists, what it does, how it achieves high availability across city-a and city-b, and why it is specifically designated as the test lane for our solution.

-----

**🔗 Resources**

- **LDAP RFC 4511**: [rfc-editor.org/rfc/rfc4511](https://www.rfc-editor.org/rfc/rfc4511)
- **LDAP data interchange format (LDIF)**: [rfc-editor.org/rfc/rfc2849](https://www.rfc-editor.org/rfc/rfc2849)
- **Understanding LDAP search filters**: [ldap.com/ldap-filters](https://ldap.com/ldap-filters/)
- **LDAPS (LDAP over TLS)**: [rfc-editor.org/rfc/rfc4513](https://www.rfc-editor.org/rfc/rfc4513)

-----

*🌍 Globetrotters Identity and Access Management Series — crossing the IAM border one checkpoint at a time.*
