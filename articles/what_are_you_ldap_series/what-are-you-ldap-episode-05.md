---
title: "What Are You LDAP? 🔬 Ep.5"
published: false
description: "Episode 5: The entry was created. Then it was modified — a new attribute added, a password changed, a group membership updated. Then it was renamed. Every one of these actions leaves a mark: LDIF modification records, modifyTimestamp, modifiersName, and the accesslog overlay that captures every LDAP operation in a second directory. The chain of custody is unbroken."
tags: [ldap, audit, security, directory]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-are-you-ldap-episode-05.png"
series: "What Are You LDAP?"
canonical_url: ""
organization: "the-software-s-journey"
part: 5
---

## Episode 5: The Evidence Log

*🎵 What are you? What what, what what? 🎵*

-----

## “The Evidence Never Lies — If You Keep the Log” 📋

*3:00am. Warrick Brown is reviewing the accesslog. An entry was modified. Time: 02:47am. The modifier: `cn=admin,dc=acme,dc=com`. The attribute changed: `userPassword`.*

**WARRICK:** “Someone changed Alice’s password in the middle of the night. Using the admin account. The operational attributes show modifyTimestamp `20260611024712Z` — 2:47am. The accesslog shows exactly what attribute was changed and by whom.”

*He leans forward.*

**WARRICK:** “Without the accesslog overlay, I would only see that the password is different from before. With it, I have a complete forensic record: who performed the operation, when, what the operation was, what changed. That is the difference between knowing something happened and knowing what happened.”

-----

## 🗂️ SIPOC — The Evidence Log System

|**Suppliers**           |**Inputs**                                              |**Process**                                                                 |**Outputs**                                                 |**Customers**                                                                 |
|------------------------|--------------------------------------------------------|----------------------------------------------------------------------------|------------------------------------------------------------|------------------------------------------------------------------------------|
|LDAP clients and admins |Add, Modify, Delete, ModifyDN operations                |LDAP server processes operation → validates → executes → writes to accesslog|Updated directory state + accesslog record of the change    |Future searches against the updated data; audit systems querying the accesslog|
|`accesslog` overlay     |Every LDAP operation (bind, search, modify, add, delete)|Writes a structured record for each operation to a separate LDAP database   |A queryable audit log with who, what, when, and what changed|Compliance tools, SIEM systems, security investigations                       |
|LDIF modification format|Attribute change instructions                           |Add attribute values, replace attribute values, delete attribute values     |Precise, reversible change records                          |The server — which applies the change; admins — who can replay or revert      |

-----

## Part 1: The Add Operation — New Subject Enters the Lab 🆕

```bash
cat > new-user.ldif << 'EOF'
dn: cn=Carol Davis,ou=People,dc=acme,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
objectClass: posixAccount
cn: Carol Davis
sn: Davis
givenName: Carol
uid: cdavis
uidNumber: 10044
gidNumber: 10000
homeDirectory: /home/cdavis
loginShell: /bin/bash
mail: cdavis@acme.com
telephoneNumber: +1 702 555 0303
title: Security Engineer
departmentNumber: Security
employeeNumber: 1044
userPassword: carolsecret
EOF

ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f new-user.ldif

# Result: adding new entry "cn=Carol Davis,ou=People,dc=acme,dc=com"
```

After the add, the server automatically populates operational attributes:

```
createTimestamp: 20260611100001Z
creatorsName:    cn=admin,dc=acme,dc=com
entryUUID:       a1b2c3d4-e5f6-7890-abcd-ef1234567890
modifyTimestamp: 20260611100001Z    ← Same as createTimestamp initially
modifiersName:   cn=admin,dc=acme,dc=com
```

-----

## Part 2: The Modify Operation — Changing the Evidence 🔧

The **Modify** operation changes attribute values in an existing entry. LDIF modification format uses `changetype: modify`:

```ldif
# LDIF modification format
# changetype: modify must be declared
# Then each change block: operation, attribute name, colon, values, dash

dn: cn=Carol Davis,ou=People,dc=acme,dc=com
changetype: modify
add: telephoneNumber               ← ADD: add new value to attribute
telephoneNumber: +1 702 555 0404   ← The new value
-                                  ← Dash separates change blocks
add: mobile
mobile: +1 702 555 9000
-
replace: title                     ← REPLACE: replace all values
title: Senior Security Engineer    ← The new value (old values gone)
-
delete: loginShell                 ← DELETE: remove the attribute entirely
-
```

```bash
ldapmodify \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f modify-carol.ldif

# modifying entry "cn=Carol Davis,ou=People,dc=acme,dc=com"
```

### The Three Modify Operations

```ldif
# ADD: add a new value (does NOT remove existing values)
changetype: modify
add: mail
mail: carol.davis@acme.com    ← adds this alongside existing carol@acme.com
-

# REPLACE: replace ALL existing values with new value(s)
changetype: modify
replace: title
title: Principal Security Engineer  ← replaces whatever was there
-

# REPLACE with no value: DELETE the entire attribute
changetype: modify
replace: description
-                                  ← no value = delete the attribute

# DELETE specific value
changetype: modify
delete: telephoneNumber
telephoneNumber: +1 702 555 0303  ← delete only this specific value
-                                  ← (other phone numbers remain)

# DELETE entire attribute (all values)
changetype: modify
delete: mobile
-                                  ← no value = delete all mobile values
```

-----

## Part 3: Modify in a Single Command (inline) 🔧

```bash
# Change password directly via ldappasswd
ldappasswd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -S \
  "cn=Carol Davis,ou=People,dc=acme,dc=com"
# Prompts for new password twice

# Or: specify new password on command line
ldappasswd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -s "new_password_here" \
  "cn=Carol Davis,ou=People,dc=acme,dc=com"

# Self-service password change (user changes their own password):
ldappasswd \
  -x \
  -H ldap://localhost \
  -D "cn=Carol Davis,ou=People,dc=acme,dc=com" \
  -w carolsecret \           # Old password (authentication)
  -a carolsecret \           # Old password again (old value)
  -s "newcarolsecret"        # New password
```

-----

## Part 4: ModifyDN — The Rename Operation 📝

Rename an entry or move it within the DIT:

```bash
# Rename the entry's RDN (same parent container)
ldapmodrdn \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  "cn=Carol Davis,ou=People,dc=acme,dc=com" \
  "cn=Carol Johnson"    ← New RDN (she got married, changed name)
# deleteoldrdn=1 by default (remove cn=Carol Davis from entry)

# Move entry to a different container (requires Superior DN)
ldapmodrdn \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -r \                   # Remove old RDN value
  -s "ou=Alumni,dc=acme,dc=com" \   # New superior (parent)
  "cn=Carol Davis,ou=People,dc=acme,dc=com" \
  "cn=Carol Davis"       # RDN (same)
# Result: entry is now at cn=Carol Davis,ou=Alumni,dc=acme,dc=com
```

-----

## Part 5: The Delete Operation — Removing the Evidence ❌

```bash
# Delete a single entry
ldapdelete \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  "cn=Carol Davis,ou=People,dc=acme,dc=com"

# Delete all entries under a container (with -r recursive flag)
ldapdelete \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -r \
  "ou=Temp,dc=acme,dc=com"
```

**CATHERINE:** “You cannot delete a container entry if it has children. The server returns `notAllowedOnNonLeaf` (code 66). Either delete children first (recursively) or use the `-r` flag with tools that support it. The directory protects against orphaned subtrees.”

-----

## Part 6: The accesslog Overlay — The Wiretap 🎙️

The `accesslog` overlay records every LDAP operation — bind, search, modify, add, delete — to a second LDAP database. It is the forensic wiretap.

### Configuring the accesslog overlay

```ldif
# Step 1: Create the accesslog database
dn: olcDatabase={2}mdb,cn=config
objectClass: olcDatabaseConfig
objectClass: olcMdbConfig
olcDatabase: {2}mdb
olcDbDirectory: /var/lib/ldap/accesslog
olcSuffix: cn=accesslog
olcRootDN: cn=admin,cn=accesslog
olcRootPW: {SSHA}accesslog_admin_hash
olcAccess: to * by dn.exact="cn=admin,dc=acme,dc=com" read
           by * none
olcDbIndex: default eq
olcDbIndex: entryCSN,objectClass,reqEnd,reqResult,reqStart eq

# Step 2: Load the accesslog overlay on the main database
dn: olcOverlay=accesslog,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcAccessLogConfig
olcOverlay: accesslog
olcAccessLogDB: cn=accesslog         # Where to write logs
olcAccessLogOps: writes              # Log: writes (add,modify,delete,modrdn)
# Other options: reads, binds, all
olcAccessLogSuccess: TRUE            # Log successful operations
olcAccessLogOld: reqMod              # Record old values when modifying
olcAccessLogPurge: 7+00:00 1+00:00  # Purge logs older than 7 days
```

```bash
ldapadd \
  -Y EXTERNAL \
  -H ldapi:/// \
  -f accesslog-config.ldif
```

### Querying the accesslog

```bash
# Search the accesslog for all operations on Alice's entry
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "cn=accesslog" \
  "(reqDN=cn=Alice Smith,ou=People,dc=acme,dc=com)"

# Search for all failed bind attempts (result code 49)
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "cn=accesslog" \
  "(&(objectClass=auditBind)(reqResult=49))" \
  reqDN reqStart reqResult reqAuthzID

# Search for password changes in the last 24 hours
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "cn=accesslog" \
  "(&(objectClass=auditModify)(reqMod=userPassword:*))" \
  reqDN reqStart reqAuthzID reqMod
```

### accesslog Entry Structure

```ldif
# A sample accesslog entry — password modification
dn: reqStart=20260611024712.000000Z,cn=accesslog
objectClass: auditObject
objectClass: auditModify
reqDN: cn=Alice Smith,ou=People,dc=acme,dc=com
reqStart: 20260611024712.000000Z    ← When the operation started
reqEnd: 20260611024712.003219Z      ← When it finished
reqType: modify                     ← Operation type
reqResult: 0                        ← Result code (0 = success)
reqAuthzID: cn=admin,dc=acme,dc=com ← Who performed the operation
reqMod: userPassword:= {SSHA}...   ← The change (new password hash)
reqOld: userPassword:= {SSHA}...   ← The old value (if olcAccessLogOld set)
reqSession: 000000b3                ← Session identifier
```

**WARRICK:** “The `reqOld` attribute is the forensic key. With `olcAccessLogOld: reqMod`, the log records not only what the new value is, but what the old value was. I can see that the password was changed at 2:47am, by the admin account, and I can see what the previous hash was. Complete chain of custody.”

-----

## Part 7: Bulk Operations — Processing Multiple Records 📦

```bash
# Load multiple entries from a file
ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f users-bulk.ldif \
  -c   # -c: continue on error (don't stop on first failure)

# Apply multiple modifications
ldapmodify \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f modifications.ldif \
  -c

# Backup: dump entire directory to LDIF (offline)
# Stop slapd first or use slapcat for consistency
slapcat \
  -n 1 \              # Database number (1 = main db)
  -l /backup/acme-backup-$(date +%Y%m%d).ldif

# Restore from backup (offline — slapd must be stopped)
slapadd \
  -n 1 \
  -F /etc/ldap/slapd.d \
  -l /backup/acme-backup-20260101.ldif
```

-----

## Part 8: The auditlog Overlay — The Written Record 📄

The `auditlog` overlay (different from `accesslog`) writes a plain LDIF file to disk — a text-based audit trail:

```ldif
# Enable the auditlog overlay
dn: olcOverlay=auditlog,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcAuditLogConfig
olcOverlay: auditlog
olcAuditLogFile: /var/log/ldap/audit.ldif  # Write to this file
```

```bash
# The audit log file contains change records:
cat /var/log/ldap/audit.ldif

# # add 1749639600 cn=Carol Davis,ou=People,dc=acme,dc=com
# # by cn=admin,dc=acme,dc=com
# dn: cn=Carol Davis,ou=People,dc=acme,dc=com
# changetype: add
# objectClass: inetOrgPerson
# cn: Carol Davis
# sn: Davis
# uid: cdavis
# ...
#
# # modify 1749643200 cn=Carol Davis,ou=People,dc=acme,dc=com
# # by cn=admin,dc=acme,dc=com
# dn: cn=Carol Davis,ou=People,dc=acme,dc=com
# changetype: modify
# replace: title
# title: Senior Security Engineer
# -
```

-----

## What’s Next: Gang Memberships and Lockup 🔒

*Nick Stokes pins a group membership diagram to the board.*

**NICK:** “We can create, modify, delete. The audit trail is running. Now Episode 6: the two things that define what an entry is allowed to do — group memberships and password policy. groupOfNames, memberOf overlay, ppolicy lockout, and Access Control Instructions. What you belong to defines what you can access. What your password policy is defines how long before you get locked up.”

-----

**🔗 Resources**

- **OpenLDAP accesslog overlay**: [openldap.org/doc/admin26/overlays.html#Access Logging](https://openldap.org/doc/admin26/overlays.html)
- **ldapmodify / ldapadd**: [ldap.com/ldap-operation-types](https://ldap.com/ldap-operation-types/)
- **RFC 4511 — LDAP Modify operation**: [rfc-editor.org/rfc/rfc4511#section-4.6](https://www.rfc-editor.org/rfc/rfc4511#section-4.6)

-----

*🔬 What Are You LDAP? — a CSI-style investigation into the directory service that classifies every identity. The evidence is in the entry. The answers are in the attributes.*
