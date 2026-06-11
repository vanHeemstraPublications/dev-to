---
title: "What Are You LDAP? 🔬 Ep.2"
published: false
description: "Episode 2: Every LDAP entry is a dossier. The Distinguished Name is the fingerprint — globally unique. The objectClass chain is the DNA profile — inherited types stacking from top to inetOrgPerson. The attributes are the evidence: cn, sn, uid, mail, every property of the subject. The operational attributes are the chain of custody: who created this, when, by whom. The dossier is complete. What are you?"
tags: [ldap, security, directory, authentication]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-are-you-ldap-episode-02.png"
series: "What Are You LDAP?"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

## Episode 2: The Subject’s Dossier

*🎵 What are you? What what, what what? 🎵*

-----

## “Every Attribute Tells a Story” 📁

*The LDAP lab. Sara Sidle opens a manila folder on the analysis table. Inside: an LDIF printout, every attribute visible.*

**SARA:** “This is the dossier. Not a username and password — a complete classification of the subject. objectClass, attributes, operational metadata. The question ‘what are you?’ is answered here, in every line.”

*She points to the top.*

**SARA:** “Start with the DN. The Distinguished Name. It is not just an address — it is a globally unique forensic fingerprint.”

-----

## 🗂️ SIPOC — The Dossier Build

|**Suppliers**          |**Inputs**                                               |**Process**                                                            |**Outputs**                                                                      |**Customers**                                                                   |
|-----------------------|---------------------------------------------------------|-----------------------------------------------------------------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
|Directory administrator|User data: name, email, uid, department, password        |LDAP Add operation with LDIF source                                    |A complete LDAP entry with DN, objectClasses, and all attributes                 |Every application, service, and policy that asks “what are you?” about this user|
|Object class hierarchy |`top → person → organizationalPerson → inetOrgPerson`    |Schema validation: each objectClass contributes MUST and MAY attributes|An entry that satisfies all required attributes from all declared objectClasses  |The LDAP server — which rejects entries that violate schema                     |
|Operational attributes |Server-generated metadata: timestamps, UUID, creatorsName|LDAP server auto-populates at create/modify time                       |Chain-of-custody metadata invisible to normal clients unless explicitly requested|Audit systems, replication engines, forensic investigations                     |

-----

## Evidence Item 1: The Distinguished Name — The Fingerprint 🖐️

The **Distinguished Name (DN)** is the unique identifier for every entry in the directory. Unlike a username (which might be duplicated across systems), the DN is globally unique within the DIT.

```
dn: cn=Alice Smith,ou=Users,dc=acme,dc=com
│     │              │           │
│     │              │           └─── dc=com     Domain component
│     │              │                dc=acme    Domain component
│     │              └─────────────── ou=Users   Organisational Unit
│     └────────────────────────────── cn=Alice Smith  Common Name (this entry)
└──── "dn:" — the Distinguished Name attribute label
```

**Anatomy of the DN:**

|Component       |Type            |Value      |Meaning                                                            |
|----------------|----------------|-----------|-------------------------------------------------------------------|
|`cn=Alice Smith`|RDN             |Alice Smith|The Relative Distinguished Name — uniquely identifies within parent|
|`ou=Users`      |Parent component|Users      |The immediate parent container                                     |
|`dc=acme`       |Domain component|acme       |First part of the domain                                           |
|`dc=com`        |Domain component|com        |Top-level domain                                                   |

**NICK:** “The DN is read right-to-left from the root. `dc=com` is the universe. `dc=acme` is the organisation. `ou=Users` is the department filing cabinet. `cn=Alice Smith` is the specific document. Change any component and you have a different entry entirely.”

### The Relative Distinguished Name (RDN)

The **RDN** is just the left-most component — the part that makes this entry unique within its parent container:

```
Full DN:  cn=Alice Smith,ou=Users,dc=acme,dc=com
RDN:      cn=Alice Smith                          ← Only this part
Parent:              ou=Users,dc=acme,dc=com      ← The containing entry
```

Multi-valued RDNs (rare but valid):

```
dn: cn=Alice Smith+uid=alice,ou=Users,dc=acme,dc=com
#   ──────────────────────── ← Multi-valued RDN (two components, joined by +)
```

-----

## Evidence Item 2: objectClass — The DNA Profile 🧬

The **objectClass** attribute defines *what type of thing* this entry is. It is not a single value — it is a **chain of inheritance** from the abstract root to the specific type.

```ldif
objectClass: top                  ← Every entry has this (abstract base)
objectClass: person               ← Structural: a human being
objectClass: organizationalPerson ← Structural: a person in an organisation
objectClass: inetOrgPerson        ← Structural: a person with internet attributes
```

### The objectClass Inheritance Chain

```
top                     (abstract — all entries have this)
│
└── person              (structural — requires: cn, sn)
    │   MAY: telephoneNumber, description, seeAlso, userPassword
    │
    └── organizationalPerson    (structural — requires: nothing additional)
        │   MAY: title, ou, l, st, street, physicalDeliveryOfficeName,
        │        postalAddress, postalCode, telephoneNumber...
        │
        └── inetOrgPerson       (structural — requires: nothing additional)
            │   MAY: uid, mail, givenName, displayName, employeeNumber,
            │        departmentNumber, jpegPhoto, mobile, preferredLanguage,
            │        homePostalAddress, labeledURI, audio, video, photo...
            │
            ├── posixAccount    (auxiliary — requires: uid, uidNumber, gidNumber, homeDirectory)
            │   MAY: loginShell, gecos, userPassword
            │
            └── shadowAccount   (auxiliary — requires: uid)
                MAY: shadowLastChange, shadowMin, shadowMax, shadowExpire...
```

**GRISSOM:** “The objectClass chain is DNA evidence. Each class contributes attributes — some mandatory (MUST), some optional (MAY). The entry must satisfy every MUST attribute from every declared objectClass. You cannot add `posixAccount` to an entry without also providing `uid`, `uidNumber`, `gidNumber`, and `homeDirectory`. The schema is the forensic standard the entry must meet.”

### objectClass categories

|Category      |Description                                                 |Example                        |
|--------------|------------------------------------------------------------|-------------------------------|
|**Structural**|Defines the primary type — exactly one per entry at the core|`person`, `organizationalUnit` |
|**Auxiliary** |Adds extra capabilities — zero or more                      |`posixAccount`, `shadowAccount`|
|**Abstract**  |Base class — cannot be used alone                           |`top`                          |

-----

## Evidence Item 3: Attributes — The Full Profile 📊

Every piece of information about an entry is stored as an **attribute** — a typed name/value pair (or name/values for multi-valued attributes):

```ldif
# The complete dossier for Alice Smith

dn: cn=Alice Smith,ou=Users,dc=acme,dc=com

# ── Classification ────────────────────────────────────────────────
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
objectClass: posixAccount

# ── Required attributes (MUST from objectClass) ──────────────────
cn: Alice Smith             # commonName — MUST (person)
sn: Smith                   # surName — MUST (person)
uid: alice                  # userID — MUST (posixAccount)
uidNumber: 10042            # Unix UID — MUST (posixAccount)
gidNumber: 10000            # Primary group GID — MUST (posixAccount)
homeDirectory: /home/alice  # Home dir — MUST (posixAccount)

# ── Optional attributes (MAY from objectClass) ──────────────────
givenName: Alice            # First name
displayName: Alice Smith    # Display name (may differ from cn)
mail: alice@acme.com        # Email address
mail: alice.smith@acme.com  # MULTI-VALUED: Alice has two mail addresses!
telephoneNumber: +1 702 555 0101
mobile: +1 702 555 9999
title: Senior Software Engineer
departmentNumber: Engineering
employeeNumber: 1042
loginShell: /bin/bash
description: Senior Software Engineer, Platform Team

# ── Security ──────────────────────────────────────────────────────
userPassword: {SSHA}T5LUfNNa/WzHPEDNp8lH9rmcL7kJPHyf
# {SSHA} = Salted SHA1 hash (better: use PBKDF2 or ARGON2 in modern installs)
```

### Multi-valued attributes

LDAP attributes can hold **multiple values** of the same type. The same attribute name appears on multiple lines:

```ldif
mail: alice@acme.com
mail: alice.smith@acme.com
telephoneNumber: +1 702 555 0101
telephoneNumber: +1 702 555 0202
```

**CATHERINE:** “Multi-valued attributes are where LDAP diverges completely from relational databases. There is no secondary table, no join, no foreign key. Multiple values of the same attribute on the same entry, each a first-class member of the set. Query for `(mail=alice@acme.com)` and Alice matches. Query for `(mail=alice.smith@acme.com)` and Alice also matches. Both are true simultaneously.”

-----

## Evidence Item 4: LDIF — The Case File Text Format 📄

**LDIF** (LDAP Data Interchange Format, RFC 2849) is the standard text representation of directory data. All LDAP tools read and write it:

### LDIF Rules

```ldif
# Lines starting with # are comments

# An entry begins with its DN:
dn: cn=Alice Smith,ou=Users,dc=acme,dc=com

# Attributes: value pairs (attribute: value)
cn: Alice Smith
sn: Smith

# A BLANK LINE separates entries:
                              ← blank line ends this entry

# Next entry:
dn: cn=Bob Jones,ou=Users,dc=acme,dc=com
cn: Bob Jones
sn: Jones
```

### Base64 encoding in LDIF

Values containing non-ASCII characters or binary data use double-colon `::` and Base64 encoding:

```ldif
# String with special characters: use ::
description:: U2VuaW9yIEVuZ2luZWVyIC0gUGxhdGZvcm0gVGVhbQ==
#  ^^  double colon = base64 encoded value
#  Decoded: "Senior Engineer - Platform Team"

# Binary data (like jpegPhoto) is always base64
jpegPhoto:: /9j/4AAQSkZJRgABAQAAAQABAAD...
```

### Line continuation (folding)

Long lines are folded with a leading space on continuation lines:

```ldif
description: This is a very long description that would exceed the line
 length limit in LDIF and therefore must be folded by placing a leading
 space on each continuation line to indicate it is a continuation.
```

-----

## Evidence Item 5: Operational Attributes — The Chain of Custody 🔗

Operational attributes are managed by the server itself — they record metadata about the entry’s lifecycle. They are not returned by default searches; you must request them explicitly.

```bash
# Request operational attributes with "+" in the attribute list
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=Users,dc=acme,dc=com" \
  "(uid=alice)" \
  "+" "*"   # "+" = all operational, "*" = all regular attributes

# Output includes:
# entryUUID: 550e8400-e29b-41d4-a716-446655440000   ← Server-assigned UUID
# entryDN: cn=Alice Smith,ou=Users,dc=acme,dc=com   ← The DN itself
# createTimestamp: 20260101143022Z                   ← When created (UTC)
# modifyTimestamp: 20260611100000Z                   ← Last modified (UTC)
# creatorsName: cn=admin,dc=acme,dc=com             ← Who created it
# modifiersName: cn=admin,dc=acme,dc=com            ← Who last modified it
# entryCSN: 20260611100000.000000Z#000000#000#000000 ← Replication sequence number
# subschemaSubentry: cn=subschema                   ← Where schema is defined
# structuralObjectClass: inetOrgPerson              ← The primary structural class
```

**WARRICK:** “The chain of custody. `createTimestamp` tells you when the entry was born. `creatorsName` tells you who brought it into the world. `modifyTimestamp` tells you when it was last changed. `modifiersName` tells you who changed it. Any discrepancy between the expected modifier and the actual one is grounds for suspicion.”

|Operational attribute  |Meaning                        |Forensic value                                      |
|-----------------------|-------------------------------|----------------------------------------------------|
|`entryUUID`            |Globally unique identifier     |Cannot be faked; stable across renames              |
|`entryDN`              |Reflected DN                   |Confirms the entry is where it claims to be         |
|`createTimestamp`      |UTC creation time              |Establishes timeline of when account was provisioned|
|`modifyTimestamp`      |UTC last-modified time         |Detects unauthorised changes                        |
|`creatorsName`         |DN that created the entry      |Identifies provisioning source                      |
|`modifiersName`        |DN that last modified the entry|Detects unexpected modifiers                        |
|`structuralObjectClass`|The primary structural class   |Confirms the entry’s core type                      |
|`entryCSN`             |Change Sequence Number         |Replication state tracking                          |

-----

## Evidence Item 6: The Root DSE — The Morgue’s Master Register 🗃️

The **Root DSE** (DSA-Specific Entry) is a special entry with an empty DN (`""`). Query it to learn everything about the server’s capabilities:

```bash
ldapsearch \
  -x \
  -H ldap://localhost \
  -b "" \
  -s base \
  "(objectClass=*)" \
  "+" "*"
```

```ldif
# dn: (empty — the Root DSE)
structuralObjectClass: OpenLDAProotDSE
configContext: cn=config              ← Where online configuration lives
namingContexts: dc=acme,dc=com       ← Data partitions this server manages
defaultNamingContext: dc=acme,dc=com
rootDomainNamingContext: dc=acme,dc=com
supportedLDAPVersion: 3              ← LDAP protocol version
supportedControl: 1.2.840.113556.1.4.319   ← Paged results
supportedControl: 2.16.840.1.113730.3.4.2  ← ManageDsaIT
supportedExtension: 1.3.6.1.4.1.1466.20037  ← StartTLS
supportedExtension: 1.3.6.1.4.1.4203.1.11.1 ← Password modify
supportedSASLMechanisms: GSSAPI
supportedSASLMechanisms: DIGEST-MD5
supportedSASLMechanisms: PLAIN
```

-----

## Complete Entry Example: The Full Dossier 📋

```bash
# Create a comprehensive test user
cat > complete-user.ldif << 'EOF'
dn: cn=Bob Jones,ou=Users,dc=acme,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
cn: Bob Jones
sn: Jones
givenName: Bob
displayName: Bob Jones
uid: bjones
uidNumber: 10043
gidNumber: 10000
homeDirectory: /home/bjones
loginShell: /bin/bash
mail: bjones@acme.com
telephoneNumber: +1 702 555 0202
mobile: +1 702 555 8888
title: DevOps Engineer
departmentNumber: Platform
employeeNumber: 1043
description: DevOps Engineer - Security Focus
preferredLanguage: en
shadowLastChange: 19520
shadowMin: 0
shadowMax: 90
shadowWarning: 14
userPassword: {SSHA}Tr2vN8kLmQpX4bDc9wFyRhJaKe7sVuIz
EOF

ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f complete-user.ldif

# Now query the full dossier
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=Users,dc=acme,dc=com" \
  "(uid=bjones)" \
  "+" "*"
```

-----

## What’s Next: The Filing Cabinet 🗂️

*Nick Stokes taps the DIT diagram on the wall.*

**NICK:** “We know what an entry looks like — the dossier is complete. But where do these entries live? How is the filing cabinet organised? Episode 3: the DIT structure, naming strategy, and the schema — the DNA database that defines what every entry can and must contain.”

-----

**🔗 Resources**

- **RFC 4512 — LDAP Models (objectClass, attributes)**: [rfc-editor.org/rfc/rfc4512](https://www.rfc-editor.org/rfc/rfc4512)
- **RFC 2849 — LDIF format**: [rfc-editor.org/rfc/rfc2849](https://www.rfc-editor.org/rfc/rfc2849)
- **inetOrgPerson schema (RFC 2798)**: [rfc-editor.org/rfc/rfc2798](https://www.rfc-editor.org/rfc/rfc2798)
- **OpenLDAP Software 2.6 Administrator’s Guide**: [openldap.org/doc/admin26](https://openldap.org/doc/admin26/)

-----

*🔬 What Are You LDAP? — a CSI-style investigation into the directory service that classifies every identity. The evidence is in the entry. The answers are in the attributes.*
