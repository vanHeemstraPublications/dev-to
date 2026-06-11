---
title: "What Are You LDAP? 🔬 Ep.4"
published: false
description: "Episode 4: No detective searches without a warrant. In LDAP, the search warrant is the Bind — prove who you are before you look. Then comes the search itself: base DN, scope, filter, requested attributes. The filters are the forensic query language: AND, OR, NOT, wildcard, equality, presence. Result codes tell you whether the warrant was valid. The investigation is in the search."
tags: [ldap, security, search, authentication]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-are-you-ldap-episode-04.png"
series: "What Are You LDAP?"
canonical_url: ""
organization: "the-software-s-journey"
part: 4
---

# What Are You LDAP? 🔬

## Episode 4: The Search Warrant

*🎵 What are you? What what, what what? 🎵*

-----

## “Get Me a Warrant” 🔎

*Catherine Willows sits at the terminal. She needs to find a specific entry — a service account that may have been compromised.*

**CATHERINE:** “Before I can search this directory, I need to identify myself. The Bind operation. LDAP’s version of showing your badge. Without it, the server either refuses entirely or gives you a restricted anonymous view.”

*She types the ldapsearch command.*

**CATHERINE:** “Then the warrant itself: where to search, how deep to look, what to look for, and what information to return. Get any of these wrong and you either find nothing, find too much, or crash into an access control wall.”

-----

## 🗂️ SIPOC — The Search Operation

|**Suppliers**       |**Inputs**                                                |**Process**                                                                |**Outputs**                                                   |**Customers**                                                                          |
|--------------------|----------------------------------------------------------|---------------------------------------------------------------------------|--------------------------------------------------------------|---------------------------------------------------------------------------------------|
|LDAP client         |Bind DN, credential, baseDN, scope, filter, attribute list|LDAP Bind → authenticate → LDAP Search → apply ACL filter → return results |Matching entries with permitted attributes                    |Application — which uses the result to make an authentication or authorization decision|
|Filter engine       |RFC 4515 filter expression                                |Traverses the DIT from baseDN, evaluates filter against each entry in scope|A set of matching entries (may be empty)                      |Client — which receives zero or more entries                                           |
|Access control (ACL)|Bound DN identity, target entry attributes                |Checks each attribute in each result against ACI rules for this requester  |Filtered result: some attributes may be stripped before return|Client — which only receives what it is allowed to see                                 |

-----

## Part 1: The Bind Operation — Showing Your Badge 🪪

The **Bind** operation authenticates the client to the LDAP server. It must happen before any privileged operations.

### Bind Types

```bash
# === Simple Bind (most common) ===
# Present DN + password in cleartext (use LDAPS in production!)

ldapwhoami \
  -x \
  -H ldap://localhost \
  -D "cn=Alice Smith,ou=People,dc=acme,dc=com" \
  -w "alicesecret"

# Server confirms: dn:cn=Alice Smith,ou=People,dc=acme,dc=com

# === Anonymous Bind ===
# No credentials — limited access, governed by ACL

ldapwhoami \
  -x \
  -H ldap://localhost
  # Note: no -D or -w — anonymous bind

# Server returns: dn:


# === SASL Bind (Kerberos/GSSAPI) ===
ldapwhoami \
  -Y GSSAPI \
  -H ldap://ldap.acme.com

# === SASL EXTERNAL (certificate-based) ===
ldapwhoami \
  -Y EXTERNAL \
  -H ldapi:///    # ldapi = Unix socket, client cert from TLS context
```

### Bind Result Codes

|Code|Name                    |Meaning                             |
|----|------------------------|------------------------------------|
|`0` |Success                 |Bind succeeded                      |
|`32`|noSuchObject            |The bind DN does not exist          |
|`34`|invalidDNSyntax         |The bind DN is malformed            |
|`49`|invalidCredentials      |Wrong password (most common error)  |
|`50`|insufficientAccessRights|Not permitted to bind as this DN    |
|`53`|unwillingToPerform      |Account locked, expired, or inactive|

**CATHERINE:** “Result code 49 is the bouncer’s polite way of saying ‘you are not on the list.’ The DN was found — it exists — but the password did not match. Code 32 means the DN does not even exist. The distinction matters: 49 is an authentication failure, 32 is a typo in the username. Different investigations.”

-----

## Part 2: The Search Operation — Executing the Warrant 🔍

A search operation has six parameters:

```
1. baseDN    — Where to start searching in the DIT
2. scope     — How deep to search (base, one, sub)
3. filter    — What to match (RFC 4515 filter expression)
4. attributes — Which attributes to return
5. sizeLimit — Maximum number of results
6. timeLimit — Maximum seconds to spend searching
```

### The ldapsearch Command Anatomy

```bash
ldapsearch \
  -x \                                  # Simple auth (not SASL)
  -H ldap://localhost \                 # Server URI
  -D "cn=admin,dc=acme,dc=com" \        # Bind DN (authenticate as)
  -w secret \                           # Bind password
  -b "ou=People,dc=acme,dc=com" \       # Base DN (where to start)
  -s sub \                              # Scope: sub (entire subtree)
  -z 100 \                              # Size limit: 100 results max
  -l 10 \                               # Time limit: 10 seconds
  "(uid=alice)" \                       # Filter
  cn uid mail departmentNumber          # Attributes to return (omit = return all)
```

-----

## Part 3: Scope — How Deep to Look 🏚️

```
DIT:
  dc=acme,dc=com              ← baseDN in examples below
  ├── ou=People
  │   ├── cn=Alice            ← direct child of People
  │   ├── cn=Bob              ← direct child of People
  │   └── ou=External
  │       └── cn=Contractor   ← nested deeper
  └── ou=Groups
      └── cn=admins
```

|Scope |Flag     |What is searched                     |Example result                  |
|------|---------|-------------------------------------|--------------------------------|
|`base`|`-s base`|ONLY the baseDN entry itself         |Only `dc=acme,dc=com` entry     |
|`one` |`-s one` |Direct children only (one level down)|`ou=People` and `ou=Groups` only|
|`sub` |`-s sub` |Everything in the subtree (default)  |Everything in the tree          |

```bash
# base scope: examine just the base entry
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "dc=acme,dc=com" -s base "(objectClass=*)"
# Returns: only dc=acme,dc=com

# one scope: look at direct children
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "dc=acme,dc=com" -s one "(objectClass=*)"
# Returns: ou=People, ou=Groups, ou=Services, ou=Policies

# sub scope: search entire subtree
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" -s sub "(objectClass=inetOrgPerson)"
# Returns: all person entries anywhere under ou=People
```

-----

## Part 4: LDAP Filters — The Forensic Query Language 🔬

LDAP filters (RFC 4515) are the search terms in the warrant. They are evaluated against each entry in scope.

### Filter Types

```
Type          Syntax              Example                    Meaning
──────────    ──────────          ──────────────────────     ──────────────────
Equality      (attr=value)        (uid=alice)                uid equals "alice"
Presence      (attr=*)            (mail=*)                   mail attribute exists
Substring     (attr=*val*)        (cn=*Smith*)               cn contains "Smith"
Approx        (attr~=value)       (cn~=Smyth)                cn approximately "Smyth"
Greater/Equal (attr>=value)       (uidNumber>=10000)         uidNumber >= 10000
Less/Equal    (attr<=value)       (uidNumber<=10999)         uidNumber <= 10999
AND           (&(f1)(f2)...)      (&(uid=a)(mail=a@x.com))  uid=a AND mail=a@x.com
OR            (|(f1)(f2)...)      (|(uid=a)(uid=b))          uid=a OR uid=b
NOT           (!(filter))         (!(uid=guest))             uid is NOT "guest"
Extensible    (attr:rule:=value)  (cn:caseExactMatch:=Alice) case-sensitive cn
```

### Practical Filter Examples

```bash
# Find all users with uid attribute (presence filter)
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=*)"

# Find Alice specifically
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)"

# Find all engineers (departmentNumber contains "Engineering")
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(departmentNumber=Engineering)"

# AND: find engineers with a mail address (both conditions must be true)
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(&(departmentNumber=Engineering)(mail=*))"

# AND with 3 conditions: engineer, has mail, uid starts with 'a'
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(&(objectClass=inetOrgPerson)(departmentNumber=Engineering)(uid=a*))"

# OR: find either Alice or Bob
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(|(uid=alice)(uid=bjones))"

# NOT: find all users who are NOT in the Guest department
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(&(objectClass=inetOrgPerson)(!(departmentNumber=Guests)))"

# Compound: active engineers with VPN access
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(&(objectClass=acmeEmployee)(departmentNumber=Engineering)(acmeVpnEnabled=TRUE))"
```

### Substring Filter Variations

```
(cn=Alice*)         — starts with Alice
(cn=*Smith)         — ends with Smith
(cn=*li*)           — contains "li"
(cn=A*e*Smith)      — starts with A, contains e, ends with Smith
(cn=*)              — the value exists at all (presence filter)
```

-----

## Part 5: Attribute Selection — What to Return 📋

```bash
# Return only specific attributes (space-separated list)
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)" \
  uid cn mail departmentNumber   # ← only these 4 attributes returned

# Return NO attributes — just the DNs (use 1.1 as attribute)
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(objectClass=inetOrgPerson)" \
  1.1   # ← the OID "1.1" means: return DN only, no attributes
# Useful for: "does this entry exist?" checks

# Return all regular + all operational attributes
ldapsearch ... "(uid=alice)" "*" "+"
```

-----

## Part 6: Result Codes — The Verdict 📜

|Code|Name                        |Meaning                          |Common cause                                 |
|----|----------------------------|---------------------------------|---------------------------------------------|
|`0` |success                     |Request completed successfully   |—                                            |
|`1` |operationsError             |Internal error                   |Server bug or misconfiguration               |
|`2` |protocolError               |Client sent invalid LDAP         |Client library bug                           |
|`4` |sizeLimitExceeded           |Too many results                 |sizeLimit too low or filter too broad        |
|`10`|referral                    |Try this other server            |Entry lives in a replicated subtree elsewhere|
|`11`|adminLimitExceeded          |Server’s own limit hit           |Server-side size/time limit                  |
|`12`|unavailableCriticalExtension|Required control not supported   |Client sent unsupported control              |
|`16`|noSuchAttribute             |Attribute does not exist in entry|Modifying nonexistent attribute              |
|`17`|undefinedAttributeType      |Attribute not in schema          |Trying to use undefined attribute            |
|`20`|attributeOrValueExists      |Value already present            |Adding duplicate attribute value             |
|`21`|invalidAttributeSyntax      |Value violates attribute syntax  |Integer field with text value                |
|`32`|noSuchObject                |Entry does not exist             |Wrong baseDN or target entry deleted         |
|`33`|aliasDereferencingProblem   |Cannot follow alias              |Alias points to nonexistent entry            |
|`34`|invalidDNSyntax             |DN is malformed                  |Typo in DN                                   |
|`49`|invalidCredentials          |Wrong password                   |Failed authentication                        |
|`50`|insufficientAccessRights    |Access denied by ACL             |No permission for this operation             |
|`53`|unwillingToPerform          |Server refuses operation         |Account locked, schema violation             |
|`65`|objectClassViolation        |Entry violates objectClass rules |Missing MUST attribute                       |
|`68`|entryAlreadyExists          |DN already taken                 |Duplicate DN                                 |

-----

## Part 7: The LDAP URI — The Complete Warrant Form 📝

An LDAP URI encodes the entire search in a single string (RFC 4516):

```
ldap://host:port/baseDN?attributes?scope?filter?extensions
```

```bash
# Full LDAP URI examples
ldapsearch "ldap://localhost/ou=People,dc=acme,dc=com?cn,mail?sub?(uid=alice)"

# Breakdown:
# ldap://localhost         ← server
# /ou=People,dc=acme,dc=com ← baseDN
# ?cn,mail                 ← attributes (cn and mail only)
# ?sub                     ← scope: subtree
# ?(uid=alice)             ← filter

# LDAPS URI (TLS)
ldapsearch "ldaps://ldap.acme.com:636/ou=People,dc=acme,dc=com?uid?sub?(mail=*@acme.com)"
```

-----

## Part 8: Authentication via LDAP — The Application Pattern 🔐

The most common use of LDAP is application authentication. The pattern is: bind as a service account, search for the user, then re-bind as the found user to verify their password.

```python
# Python: LDAP authentication pattern
import ldap3

def authenticate_user(username: str, password: str) -> dict | None:
    """
    Authenticate a user against LDAP.
    Returns the user's entry dict if successful, None if not.
    """
    server = ldap3.Server(
        'ldap.acme.com',
        port=636,
        use_ssl=True,
        get_info=ldap3.ALL
    )

    # Step 1: Bind as service account to search for the user
    conn = ldap3.Connection(
        server,
        user='cn=webapp-reader,ou=Services,dc=acme,dc=com',
        password='service-account-secret',
        authentication=ldap3.SIMPLE
    )

    if not conn.bind():
        raise RuntimeError(f"Service account bind failed: {conn.result}")

    # Step 2: Search for the user by uid
    conn.search(
        search_base='ou=People,dc=acme,dc=com',
        search_filter=f'(uid={ldap3.utils.conv.escape_filter_chars(username)})',
        search_scope=ldap3.SUBTREE,
        attributes=['cn', 'mail', 'uid', 'departmentNumber',
                    'memberOf', 'acmeClearanceLevel']
    )

    if not conn.entries:
        return None  # User not found

    user_dn = conn.entries[0].entry_dn
    user_attrs = {
        attr: conn.entries[0][attr].value
        for attr in ['cn', 'mail', 'uid', 'departmentNumber']
        if attr in conn.entries[0]
    }

    # Step 3: Attempt bind as the user with their password
    user_conn = ldap3.Connection(
        server,
        user=user_dn,
        password=password,
        authentication=ldap3.SIMPLE
    )

    if not user_conn.bind():
        # Result code 49 = invalid credentials
        return None  # Wrong password

    user_conn.unbind()
    return user_attrs


# Usage
result = authenticate_user('alice', 'alicesecret')
if result:
    print(f"Authenticated: {result['cn']} ({result['departmentNumber']})")
else:
    print("Authentication failed")
```

**WARRICK:** “Note the `escape_filter_chars` call. LDAP injection is real. If an attacker sends `username=*)(|(uid=*)` as their username, an unescaped filter becomes `(uid=*)(|(uid=*)` — which matches everyone. Always escape user input before embedding it in a filter.”

### LDAP Injection Example

```bash
# Malicious username: *)(|(uid=*)
# Unescaped filter: (uid=*)(|(uid=*))
# This matches EVERY entry — authentication bypass!

# Safe: always escape special characters in filters
# Special chars: ( ) * \ NUL — must be escaped as \HEX
# ( → \28
# ) → \29
# * → \2a
# \ → \5c

# Safe filter: (uid=\2a\29\28\7c\28uid=\2a\29)
# Which returns NXDOMAIN (no match)
```

-----

## What’s Next: The Evidence Log 📋

*Warrick Brown holds up an accesslog entry.*

**WARRICK:** “We can search. But searches are only part of what happens to an entry. It gets created, modified, deleted, renamed. Episode 5: the evidence log. Every modification tracked. The accesslog overlay. LDIF modification format. Chain of custody from creation to destruction.”

-----

**🔗 Resources**

- **RFC 4515 — LDAP Filters**: [rfc-editor.org/rfc/rfc4515](https://www.rfc-editor.org/rfc/rfc4515)
- **RFC 4516 — LDAP URI**: [rfc-editor.org/rfc/rfc4516](https://www.rfc-editor.org/rfc/rfc4516)
- **ldap3 Python library**: [ldap3.readthedocs.io](https://ldap3.readthedocs.io)
- **LDAP result codes**: [ldap.com/ldap-result-code-reference](https://ldap.com/ldap-result-code-reference/)

-----

*🔬 What Are You LDAP? — a CSI-style investigation into the directory service that classifies every identity. The evidence is in the entry. The answers are in the attributes.*
