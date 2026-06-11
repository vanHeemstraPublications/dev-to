---
title: "What Are You LDAP? 🔬 Ep.1"
published: false
description: "Episode 1: *ba-ba-baaaa, ba-ba-baaaaa* — Who are you? No — What ARE you? A user walks into an authentication system. The system asks not just ‘who are you?’ but ‘what are you?’ — what objectClass, what attributes, what group memberships, what policies apply? The LDAP directory holds every answer. Welcome to the lab."
tags: [ldap, security, authentication, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-are-you-ldap-episode-01.png"
series: "What Are You LDAP?"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: The Opening Credits

*🎵 ba-ba-baaaa, ba-ba-baaaaa… Who are you? Who who, who who? 🎵*

*Wait.*

*Not quite right.*

*The question is different here.*

*🎵 What are you? What what, what what? 🎵*

-----

## The Distinction That Changes Everything 🚨

*Las Vegas. 10:14pm. An application fires an authentication error. User `alice` cannot log in. The access logs show a bind failure — LDAP result code 49, invalidCredentials.*

*Gil Grissom steps into the server room. He looks at the LDAP log. Then looks again.*

**GRISSOM:** “Most systems ask: *who* are you? Name, password, done. But LDAP asks something more interesting. It asks: *what* are you? And the answer is an entire dossier. Your type — your objectClass. Your properties — every attribute in your entry. Your affiliations — every group you belong to. Your history — timestamps, last modifier, UUID. All of it, in a single LDAP entry.”

*He turns.*

**GRISSOM:** “The question ‘who are you?’ has a binary answer: yes or no, authenticated or not. The question ‘what are you?’ has as many answers as you have attributes. And every one of those attributes can be evaluated by a policy, an access control rule, an application decision.”

*He picks up an LDIF file. Scans it.*

**GRISSOM:** “The LDAP directory is not a password checker. It is a classification system. What are you — that is the real question. And the real crime is when the classification is wrong.”

-----

## 🗂️ SIPOC — The Directory Opens Its Doors

|**Suppliers**           |**Inputs**                                                  |**Process**                                                                              |**Outputs**                                                       |**Customers**                                                                          |
|------------------------|------------------------------------------------------------|-----------------------------------------------------------------------------------------|------------------------------------------------------------------|---------------------------------------------------------------------------------------|
|Directory administrators|User records, organizational structure, group assignments   |LDAP operations: add entries, define schema, configure access controls                   |A populated Directory Information Tree with entries at every level|Every application that needs authentication, authorisation, or directory lookup        |
|Applications (clients)  |Bind request (DN + credential), search filter, target baseDN|LDAP server processes bind → validates → processes search → applies ACL → returns results|Authenticated session; matching entries with requested attributes |The user being authenticated; the application making the lookup                        |
|The schema              |Object class definitions, attribute type definitions        |Every entry validated against the schema at write time                                   |Consistent, typed, query-able directory data                      |All consumers — they can trust that `mail` is always an email, `uid` is always a string|
|Policy engine (ACI/ACL) |Requester identity, operation type, target entry            |Access control evaluation: is this bind DN allowed to see these attributes?              |Filtered response — only what the requester is permitted to see   |Applications — they only receive what they are authorized to access                    |

-----

## The CSI/LDAP Metaphor Table: Every Concept, One Place 🔬

|CSI / criminal investigation        |LDAP concept                                                                 |
|------------------------------------|-----------------------------------------------------------------------------|
|*“What are you?”* — the series theme|LDAP answers what an entry IS: objectClass, attributes, memberships, policies|
|The crime scene                     |An authentication failure, bind error, or attribute mismatch                 |
|The victim                          |The user or application that cannot authenticate or access a resource        |
|The lab                             |The LDAP directory server (slapd, 389-DS, Active Directory)                  |
|The subject’s dossier               |An LDAP entry — all its attributes and values                                |
|DNA evidence                        |The objectClass inheritance chain (`top → person → inetOrgPerson`)           |
|Fingerprints (unique ID)            |The Distinguished Name (DN) — globally unique path to the entry              |
|The filing cabinet                  |The Directory Information Tree (DIT)                                         |
|The filing system dividers          |`dc=`, `ou=`, `cn=` — the naming hierarchy                                   |
|The identity card                   |`uid`, `cn`, `sn` — the primary identifying attributes                       |
|The full criminal profile           |All attributes of an LDAP entry combined                                     |
|The warrant to search               |The Bind operation — authenticate before you search                          |
|The search warrant details          |Search parameters: baseDN, scope, filter, attributes                         |
|The search scope                    |`base` (one entry) / `one` (direct children) / `sub` (entire subtree)        |
|The search terms                    |LDAP filters: `(&(objectClass=user)(uid=alice))`                             |
|The evidence log                    |`accesslog` overlay — records every LDAP operation                           |
|Police radio / broadcast            |syncrepl replication — changes broadcast to consumers                        |
|Chain of custody                    |`createTimestamp`, `modifyTimestamp`, `creatorsName`, `modifiersName`        |
|Gang membership file                |`groupOfNames` / `memberOf` attribute                                        |
|Auto-updated gang roster            |`memberOf` overlay — maintains membership automatically                      |
|Protective custody (account locked) |ppolicy `pwdAccountLockedTime` — locked after failed binds                   |
|The lab’s access policy             |ACI/ACL rules — `olcAccess` in OpenLDAP                                      |
|The bouncer at the door             |Bind operation — rejects invalid credentials (code 49)                       |
|Person not found                    |LDAP result code 32 — `noSuchObject`                                         |
|Schema tampering                    |Attempting to add invalid attribute or violate objectClass                   |
|Witness protection / referral       |LDAP referral — “this entry is at another server”                            |
|The encrypted evidence bag          |LDAPS (port 636) / StartTLS (port 389)                                       |
|DNA database (types and rules)      |The schema — all defined object classes and attribute types                  |
|The morgue’s master register        |Root DSE (empty DN) — the directory’s information kiosk                      |
|Case file text format               |LDIF — LDAP Data Interchange Format                                          |

-----

## What Is LDAP? The Lab’s Mission Statement 🏛️

**L**ightweight **D**irectory **A**ccess **P**rotocol. Defined in RFC 4511. A client/server protocol for reading from and writing to a **directory service** — a specialised database optimised for:

- Very fast **reads** (far more reads than writes in practice)
- **Hierarchical** data organisation
- **Rich attribute typing** — every value has a defined type and matching rule
- **Distributed** architecture with replication and referrals

LDAP is not a general-purpose database. It is a classification system. You store **entries** — records describing objects in the real world — and each entry is defined by what **it is** (objectClass) and what **properties it has** (attributes).

**SARA:** “The key insight is the objectClass. When you ask a relational database ‘who is in the users table?’, everyone in the table is just a row — they are all the same shape. When you ask LDAP ‘what is cn=Alice,ou=Users,dc=acme,dc=com?’, the answer might be: an inetOrgPerson (a type of person), with posixAccount (a Unix account), with shadowAccount (password aging). Three types. Dozens of attributes from each type. All applied to a single entry.”

-----

## The Directory Information Tree: The Filing Cabinet 🗂️

LDAP data is organised in a tree — the **Directory Information Tree (DIT)**. Like a filing cabinet: drawers → folders → documents. Each node in the tree is an **entry**.

```
dc=acme,dc=com                          ← Root entry (the organisation)
│
├── ou=Users,dc=acme,dc=com             ← Organisational Unit (a drawer)
│   ├── cn=Alice,ou=Users,...           ← A user entry (a document)
│   └── cn=Bob,ou=Users,...
│
├── ou=Groups,dc=acme,dc=com            ← Another drawer
│   ├── cn=admins,ou=Groups,...         ← A group entry
│   └── cn=developers,ou=Groups,...
│
├── ou=Services,dc=acme,dc=com          ← Service accounts drawer
│   └── cn=webapp,ou=Services,...
│
└── ou=Policies,dc=acme,dc=com          ← Policies drawer
```

**NICK:** “The tree makes the location meaningful. An entry at `cn=Alice,ou=Users,dc=acme,dc=com` tells you immediately: this is Alice, in the Users container, in the acme.com organisation. The path IS the identity.”

-----

## Your First LDAP Entry: The Subject’s Dossier 📋

An LDAP entry in **LDIF format** — the case file text format:

```ldif
# An LDAP entry for Alice
# LDIF: LDAP Data Interchange Format
# Each attribute: value pair on its own line
# Blank line separates entries

dn: cn=Alice Smith,ou=Users,dc=acme,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Alice Smith
sn: Smith
givenName: Alice
uid: alice
mail: alice@acme.com
telephoneNumber: +1 702 555 0101
userPassword: {SSHA}hashed_password_here
departmentNumber: Engineering
employeeNumber: 1042
description: Senior Software Engineer
```

**GRISSOM:** “Every attribute line answers ‘what are you?’ — not just ‘who are you?’ Alice is not simply a username. She is a `person`, an `organizationalPerson`, an `inetOrgPerson` — three objectClasses, each contributing a set of permitted and required attributes. She has a department number, an employee number, a phone number. Any policy that evaluates her entry can see all of this. ‘Is Alice in Engineering? Check. Does Alice have a phone number? Check. Is Alice’s mail domain acme.com? Check.’ All from one entry.”

-----

## Installing and Starting the Lab: OpenLDAP 🔧

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y slapd ldap-utils

# CentOS/RHEL/Rocky
sudo dnf install -y openldap-servers openldap-clients

# macOS (Homebrew)
brew install openldap

# Docker (for quick testing)
docker run \
  --name ldap-lab \
  -p 389:1389 \
  -e LDAP_ADMIN_USERNAME=admin \
  -e LDAP_ADMIN_PASSWORD=secret \
  -e LDAP_ROOT=dc=acme,dc=com \
  -d bitnami/openldap:latest
```

### Initial configuration (reconfigure if needed)

```bash
# Ubuntu: reconfigure the admin password and base DN
sudo dpkg-reconfigure slapd
# Follow prompts:
#   Omit OpenLDAP server configuration? No
#   DNS domain name: acme.com
#   Organization name: ACME Corporation
#   Administrator password: [secure password]
#   Confirm password: [same password]
#   Remove db when slapd is purged? No
#   Move old database? Yes
```

### Test the lab is running

```bash
# Query the Root DSE (the directory's master register)
ldapsearch \
  -x \
  -H ldap://localhost \
  -b "" \
  -s base \
  "(objectClass=*)"

# Expected output:
# dn:
# objectClass: top
# objectClass: OpenLDAProotDSE
# structuralObjectClass: OpenLDAProotDSE
# configContext: cn=config
# namingContexts: dc=acme,dc=com
# defaultNamingContext: dc=acme,dc=com
# supportedLDAPVersion: 3
```

**WARRICK:** “The Root DSE is the morgue’s master register. Query the empty DN and the server tells you everything about itself — what naming contexts it manages, what LDAP version it speaks, what controls and extensions it supports. Always start here when you enter a new lab.”

-----

## Adding the First Entry: Loading the Case File 📂

```bash
# Create a base LDIF file with the root entry and first OU
cat > base.ldif << 'EOF'
# Root entry for acme.com
dn: dc=acme,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
dc: acme
o: ACME Corporation
description: ACME Corporation LDAP Directory

# Users container
dn: ou=Users,dc=acme,dc=com
objectClass: top
objectClass: organizationalUnit
ou: Users
description: All user accounts

# Groups container
dn: ou=Groups,dc=acme,dc=com
objectClass: top
objectClass: organizationalUnit
ou: Groups
description: All groups

EOF

# Load the base structure
ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f base.ldif

# adding new entry "dc=acme,dc=com"
# adding new entry "ou=Users,dc=acme,dc=com"
# adding new entry "ou=Groups,dc=acme,dc=com"
```

```bash
# Add Alice's entry
cat > alice.ldif << 'EOF'
dn: cn=Alice Smith,ou=Users,dc=acme,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
cn: Alice Smith
sn: Smith
givenName: Alice
uid: alice
mail: alice@acme.com
telephoneNumber: +1 702 555 0101
departmentNumber: Engineering
description: Senior Software Engineer
userPassword: alicesecret

EOF

ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f alice.ldif

# adding new entry "cn=Alice Smith,ou=Users,dc=acme,dc=com"
```

-----

## The First Search: Running the Investigation 🔍

```bash
# Search for Alice — what ARE you?
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=Users,dc=acme,dc=com" \
  "(uid=alice)"

# Output — the complete dossier:
# dn: cn=Alice Smith,ou=Users,dc=acme,dc=com
# objectClass: top
# objectClass: person
# objectClass: organizationalPerson
# objectClass: inetOrgPerson
# cn: Alice Smith
# sn: Smith
# givenName: Alice
# uid: alice
# mail: alice@acme.com
# telephoneNumber: +1 702 555 0101
# departmentNumber: Engineering
# description: Senior Software Engineer
```

**SARA:** “One query. Every attribute about this entry. The answer to ‘what are you?’ in seventeen lines. This is the power of LDAP — not just identity, but full classification.”

-----

## The Series: Eight Cases for “What Are You?” 📚

|#|Episode                         |The Case               |What We Investigate                                |
|-|--------------------------------|-----------------------|---------------------------------------------------|
|1|*This one* — The Opening Credits|Introduction           |LDAP philosophy, DIT, first entry, ldapsearch      |
|2|The Subject’s Dossier           |Entry anatomy          |DN, RDN, attributes, LDIF, objectClass hierarchy   |
|3|The Filing Cabinet              |DIT and Schema         |DIT design, schema, attribute types, object classes|
|4|The Search Warrant              |Bind and Search        |Bind operation, filters, scope, result codes       |
|5|The Evidence Log                |Modifications and audit|Add/modify/delete, accesslog overlay, LDIF changes |
|6|Gang Memberships and Lockup     |Groups and policy      |groupOfNames, memberOf, ppolicy, ACIs              |
|7|The Police Radio                |Replication and config |syncrepl, cn=config (OLC), referrals               |
|8|Case Closed                     |Production hardening   |TLS, SASL, performance, complete deployment        |

**GRISSOM:** “Every entry in the directory is a case file waiting to be read. Every attribute is evidence. Every objectClass is a classification. The question is never just ‘who are you?’”

*He closes the LDIF file.*

**GRISSOM:** “The question is always: *what* are you?”

-----

**🔗 Resources**

- **OpenLDAP documentation**: [openldap.org/doc](https://openldap.org/doc/)
- **RFC 4511 — LDAP Protocol**: [rfc-editor.org/rfc/rfc4511](https://www.rfc-editor.org/rfc/rfc4511)
- **RFC 4512 — LDAP Models**: [rfc-editor.org/rfc/rfc4512](https://www.rfc-editor.org/rfc/rfc4512)
- **Bitnami OpenLDAP Docker image**: [hub.docker.com/r/bitnami/openldap](https://hub.docker.com/r/bitnami/openldap)

-----

*🔬 What Are You LDAP? — a CSI-style investigation into the directory service that classifies every identity. The evidence is in the entry. The answers are in the attributes.*
