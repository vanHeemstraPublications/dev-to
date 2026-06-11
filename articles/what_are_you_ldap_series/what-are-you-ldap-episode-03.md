---
title: "What Are You LDAP? 🔬 Ep.3"
published: false
description: "Episode 3: Every great investigation depends on a well-organised filing cabinet. The DIT is that cabinet — dc= drawers, ou= folders, cn= documents. But the filing system is only as good as the classification rules that govern it: the schema. Attribute types, object class definitions, syntax rules, matching rules — the DNA database that defines what every entry can and must be."
tags: [ldap, schema, directory, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-are-you-ldap-episode-03.png"
series: "What Are You LDAP?"
canonical_url: ""
organization: "the-software-s-journey"
part: 3
---

## Episode 3: The Filing Cabinet

*🎵 What are you? What what, what what? 🎵*

-----

## “A Lab Without a Filing System Is Just a Room Full of Evidence” 🗂️

*Nick Stokes stands in front of the DIT diagram. He draws three columns: dc=, ou=, cn=.*

**NICK:** “Every investigation needs a filing system. Not just ‘put it in a drawer’ — a structured system where you know exactly where everything is and what it means. The DIT — the Directory Information Tree — is that filing system for LDAP. And the schema is the set of rules that governs what goes in each drawer.”

*He taps the diagram.*

**NICK:** “The DIT is the cabinet. The schema is the filing standard. Get either one wrong and your investigation collapses.”

-----

## 🗂️ SIPOC — The Filing System Build

|**Suppliers**                   |**Inputs**                                                                |**Process**                                                                |**Outputs**                                                                 |**Customers**                                                                             |
|--------------------------------|--------------------------------------------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
|Directory architect             |Organisational structure, naming conventions, required data types         |Design DIT hierarchy, define custom schema if needed, load standard schemas|A well-structured DIT with consistent naming and complete attribute coverage|Applications — which can search predictably; admins — who can find any entry              |
|LDAP schema files               |Object class and attribute type definitions in `.schema` or `.ldif` format|Schema loading: `cn=config` or `schema.conf` include directives            |A validated schema that every subsequent entry must satisfy                 |The server — which rejects malformed entries; clients — which trust the data is consistent|
|Subschema entry (`cn=subschema`)|Runtime schema discovery                                                  |Query the subschema entry to introspect object classes and attribute types |Live schema documentation accessible via LDAP itself                        |Applications, tools, and administrators discovering what is possible                      |

-----

## Part 1: DIT Design — The Filing Cabinet Architecture 🏛️

### The Three Naming Components

```
dc=acme,dc=com          ← Domain component: derived from DNS name
ou=Engineering          ← Organisational unit: a logical grouping
cn=Alice Smith          ← Common name: typically identifies a leaf entry
```

But these are conventions, not hard rules. LDAP also supports:

```
uid=alice               ← uid-named entries (common for users in some schemas)
o=ACME Corporation      ← organization attribute (older style)
l=Las Vegas             ← locality (rare as a naming component)
```

### Three Common DIT Design Patterns

**Pattern 1: Domain-based (most common for internet-facing directories)**

```
dc=acme,dc=com
├── ou=People
│   ├── cn=Alice Smith
│   └── cn=Bob Jones
├── ou=Groups
│   ├── cn=admins
│   └── cn=developers
├── ou=Services
│   └── cn=webapp-reader
└── ou=Policies
    └── cn=default-ppolicy
```

**Pattern 2: Department-based (mirrors org chart)**

```
dc=acme,dc=com
├── ou=Engineering
│   ├── ou=Platform
│   │   └── cn=Alice Smith
│   └── ou=Security
│       └── cn=Bob Jones
├── ou=Finance
│   └── cn=Carol Davis
└── ou=HR
    └── cn=Dave Wilson
```

**Pattern 3: Location-based (multi-site organisations)**

```
dc=acme,dc=com
├── l=LasVegas
│   ├── ou=People
│   └── ou=Groups
├── l=NewYork
│   ├── ou=People
│   └── ou=Groups
└── l=London
    ├── ou=People
    └── ou=Groups
```

**GRISSOM:** “The DIT design is a crime scene choice. Choose Pattern 1 and searching for all users is simple: `ldapsearch -b ou=People`. Choose Pattern 2 and searching for all users across departments requires either a subtree search from the root or knowledge of every department. Pattern 2 mirrors the org chart faithfully, but makes universal queries harder. Pattern 1 separates ‘type of entry’ from ‘organisational affiliation.’ Neither is wrong — both are committed to.”

-----

## Part 2: Loading a Complete DIT Structure 🏗️

```bash
cat > dit-structure.ldif << 'EOF'
# Root
dn: dc=acme,dc=com
objectClass: top
objectClass: dcObject
objectClass: organization
dc: acme
o: ACME Corporation

# People
dn: ou=People,dc=acme,dc=com
objectClass: top
objectClass: organizationalUnit
ou: People
description: All person entries

# Groups
dn: ou=Groups,dc=acme,dc=com
objectClass: top
objectClass: organizationalUnit
ou: Groups

# Services
dn: ou=Services,dc=acme,dc=com
objectClass: top
objectClass: organizationalUnit
ou: Services
description: Service accounts (non-human)

# Policies
dn: ou=Policies,dc=acme,dc=com
objectClass: top
objectClass: organizationalUnit
ou: Policies

# Hosts
dn: ou=Hosts,dc=acme,dc=com
objectClass: top
objectClass: organizationalUnit
ou: Hosts
description: Machine entries

EOF

ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f dit-structure.ldif
```

-----

## Part 3: The Schema — The DNA Database 🧬

The **schema** defines the vocabulary of the directory: what attribute types exist, what syntax they use, how they match, what object classes exist, and what attributes each class requires or permits.

### Querying the Subschema: The Live Schema Catalog

```bash
# Query the subschema entry — the directory's own documentation
ldapsearch \
  -x \
  -H ldap://localhost \
  -b "cn=subschema" \
  -s base \
  "(objectClass=subschema)" \
  attributeTypes \
  objectClasses

# Returns all defined attribute types and object classes
```

### Attribute Types: What Can Be Stored

An attribute type definition specifies:

```
# From the schema (OID-based definition)
attributetype ( 2.5.4.3                   ← OID: unique identifier
  NAME 'cn'                               ← Human-readable name(s)
  DESC 'RFC4519: common name'             ← Description
  SUP name                                ← Inherits from 'name' type
  EQUALITY caseIgnoreMatch                ← How equality is tested
  SUBSTR caseIgnoreSubstringsMatch        ← How substring matching works
  SYNTAX 1.3.6.1.4.1.1466.115.121.1.15   ← Syntax: Directory String
  SINGLE-VALUE                            ← (absent here means multi-valued)
)
```

**Key attribute type properties:**

|Property              |Values                                                  |Meaning                                       |
|----------------------|--------------------------------------------------------|----------------------------------------------|
|`EQUALITY`            |caseIgnoreMatch, caseExactMatch, integerMatch…          |How `(attr=value)` filters work               |
|`ORDERING`            |integerOrderingMatch, generalizedTimeOrderingMatch      |How `>=` and `<=` filters work                |
|`SUBSTR`              |caseIgnoreSubstringsMatch                               |How `(attr=*wild*card*)` filters work         |
|`SYNTAX`              |Directory String, Integer, Boolean, DN, GeneralizedTime…|What values are valid                         |
|`SINGLE-VALUE`        |(flag)                                                  |Only one value allowed (absent = multi-valued)|
|`NO-USER-MODIFICATION`|(flag)                                                  |Server-managed, clients cannot write          |

### Common Attribute Syntaxes

|Syntax OID alias|Meaning           |Example value                     |
|----------------|------------------|----------------------------------|
|DirectoryString |UTF-8 text        |`Alice Smith`                     |
|Integer         |Whole number      |`10042`                           |
|Boolean         |TRUE or FALSE     |`TRUE`                            |
|DN              |Distinguished Name|`cn=Alice,ou=Users,dc=acme,dc=com`|
|GeneralizedTime |UTC timestamp     |`20260611143022Z`                 |
|OctetString     |Binary data       |(jpeg photo bytes)                |

-----

### Object Class Definitions: The Classification Rules

```
# From the schema
objectclass ( 2.16.840.1.113730.3.2.2    ← OID
  NAME 'inetOrgPerson'                   ← Name
  DESC 'RFC2798: Internet Organizational Person'
  SUP organizationalPerson               ← Inherits from this class
  STRUCTURAL                             ← Type: structural
  MAY (                                  ← Optional attributes
    audio $
    businessCategory $
    carLicense $
    departmentNumber $
    displayName $
    employeeNumber $
    employeeType $
    givenName $
    homePhone $
    homePostalAddress $
    initials $
    jpegPhoto $
    labeledURI $
    mail $                               ← Email
    manager $
    mobile $
    o $
    pager $
    photo $
    roomNumber $
    secretary $
    uid $                               ← User ID
    userCertificate $
    x500uniqueIdentifier $
    preferredLanguage $
    userSMIMECertificate $
    userPKCS12
  )
)
```

-----

## Part 4: Custom Schema — Extending the Database 🔬

Standard schemas cover most needs. Sometimes you need custom attribute types for organisation-specific data:

```ldif
# Add a custom schema via cn=config (online configuration)
dn: cn={4}acme,cn=schema,cn=config
objectClass: olcSchemaConfig
cn: {4}acme

# Custom attribute type: employee badge number
olcAttributeTypes: ( 1.3.6.1.4.1.99999.1.1
  NAME 'acmeBadgeNumber'
  DESC 'ACME Corporation physical badge number'
  EQUALITY caseIgnoreMatch
  SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
  SINGLE-VALUE )

# Custom attribute type: clearance level
olcAttributeTypes: ( 1.3.6.1.4.1.99999.1.2
  NAME 'acmeClearanceLevel'
  DESC 'ACME security clearance level: none, basic, elevated, admin'
  EQUALITY caseIgnoreMatch
  SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
  SINGLE-VALUE )

# Custom attribute type: VPN group membership flag
olcAttributeTypes: ( 1.3.6.1.4.1.99999.1.3
  NAME 'acmeVpnEnabled'
  DESC 'Whether this account can use the corporate VPN'
  EQUALITY booleanMatch
  SYNTAX 1.3.6.1.4.1.1466.115.121.1.7
  SINGLE-VALUE )

# Custom object class that includes the custom attributes
olcObjectClasses: ( 1.3.6.1.4.1.99999.2.1
  NAME 'acmeEmployee'
  DESC 'ACME Corporation employee auxiliary class'
  SUP top
  AUXILIARY
  MAY ( acmeBadgeNumber $ acmeClearanceLevel $ acmeVpnEnabled )
)
```

```bash
# Add the custom schema
ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,cn=config" \
  -w config_secret \
  -f acme-schema.ldif
```

```ldif
# Now use the custom attributes in an entry
dn: cn=Alice Smith,ou=People,dc=acme,dc=com
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: acmeEmployee     ← our custom auxiliary class
cn: Alice Smith
sn: Smith
uid: alice
uidNumber: 10042
gidNumber: 10000
homeDirectory: /home/alice
mail: alice@acme.com
acmeBadgeNumber: B-10042       ← custom attribute
acmeClearanceLevel: elevated   ← custom attribute
acmeVpnEnabled: TRUE           ← custom attribute
```

**SARA:** “Now every policy that asks ‘what are you?’ about Alice gets the full picture: not just her standard attributes, but her clearance level and VPN access status. The custom schema extends the vocabulary. The entry extends the knowledge.”

-----

## Part 5: Schema Violations — Evidence Tampering 🚨

Attempting to add an entry that violates the schema produces an error. The server protects the evidence:

```bash
# Attempt to add an entry missing required attribute (sn is MUST for person)
ldapadd -x -H ldap://localhost -D "cn=admin,dc=acme,dc=com" -w secret << 'EOF'
dn: cn=NoSurname,ou=People,dc=acme,dc=com
objectClass: inetOrgPerson
cn: NoSurname
uid: nosurname
EOF

# Server response:
# ldap_add: Object class violation (65)
#         additional info: object class 'person' requires attribute 'sn'
```

```bash
# Attempt to add unknown attribute
ldapadd -x -H ldap://localhost -D "cn=admin,dc=acme,dc=com" -w secret << 'EOF'
dn: cn=Alice Smith,ou=People,dc=acme,dc=com
objectClass: inetOrgPerson
cn: Alice Smith
sn: Smith
favoriteColor: blue          ← not in any schema
EOF

# Server response:
# ldap_add: Undefined attribute type (17)
#         additional info: favoriteColor: AttributeDescription not recognized
```

**CATHERINE:** “Schema violations are evidence tampering. The server does not guess. It does not accept ‘probably valid.’ Every attribute must be defined. Every required attribute must be present. Every value must match its syntax. The schema is the standard the evidence must meet.”

-----

## Part 6: Querying the Schema Itself 🔍

```bash
# Find the definition of the 'mail' attribute type
ldapsearch \
  -x \
  -H ldap://localhost \
  -b "cn=subschema" \
  -s base \
  "(objectClass=subschema)" \
  attributeTypes \
  | grep -A 10 "NAME 'mail'"

# Find which objectClasses permit the 'uid' attribute
ldapsearch \
  -x \
  -H ldap://localhost \
  -b "cn=subschema" \
  -s base \
  "(objectClass=subschema)" \
  objectClasses \
  | grep "uid"

# Get the OID for a specific attribute
ldapsearch \
  -x \
  -H ldap://localhost \
  -b "cn=subschema" \
  -s base \
  "(objectClass=subschema)" \
  attributeTypes \
  | grep -B 1 "NAME 'cn'"
```

-----

## The Schema Standard Library 📚

Standard schemas shipped with most LDAP implementations:

|Schema                |OID prefix               |Contains                                        |Common use             |
|----------------------|-------------------------|------------------------------------------------|-----------------------|
|`core.schema`         |2.5.4.x                  |cn, sn, ou, o, dc, description, telephoneNumber…|Core X.500 attributes  |
|`cosine.schema`       |0.9.2342.x               |uid, mail, documentTitle, documentAuthor…       |Internet schemas       |
|`inetorgperson.schema`|2.16.840.1.113730.3.2.2  |inetOrgPerson objectClass                       |Internet person entries|
|`nis.schema`          |1.3.6.1.1.1.x            |posixAccount, shadowAccount, posixGroup         |Unix integration       |
|`ppolicy.schema`      |1.3.6.1.4.1.42.2.27.8.2.x|pwdPolicy, password policy attributes           |Password policies      |
|`collective.schema`   |2.5.17.x                 |Collective attributes (distributed inheritance) |Advanced DIT           |

-----

## What’s Next: The Search Warrant 🔎

*Sara Sidle holds up an LDAP search filter on a sticky note.*

**SARA:** “The filing cabinet is built. The schema is loaded. The entries are filed. Now we need to search. Episode 4: the search warrant. Bind operation, LDAP search filters, scope, result codes. How to ask the directory exactly what you need — and how to make sure the warrant is valid before the search begins.”

-----

**🔗 Resources**

- **RFC 4517 — LDAP Syntaxes and Matching Rules**: [rfc-editor.org/rfc/rfc4517](https://www.rfc-editor.org/rfc/rfc4517)
- **OpenLDAP Schema**: [openldap.org/doc/admin26/schema.html](https://openldap.org/doc/admin26/schema.html)
- **Internet core schema RFC 4519**: [rfc-editor.org/rfc/rfc4519](https://www.rfc-editor.org/rfc/rfc4519)

-----

*🔬 What Are You LDAP? — a CSI-style investigation into the directory service that classifies every identity. The evidence is in the entry. The answers are in the attributes.*
