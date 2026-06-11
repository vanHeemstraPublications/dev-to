---
title: "What Are You LDAP? 🔬 Ep.6"
published: false
description: "Episode 6: What are you? Not just a person entry — you are what groups you belong to. Group membership defines access. The memberOf overlay maintains that roster automatically. And when someone tries the wrong password too many times, the ppolicy overlay locks them up — account locked, no parole until an admin intervenes. Access Control Instructions complete the picture: who can see what, who can change what."
tags: [ldap, security, groups, policy]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/what-are-you-ldap-episode-06.png"
series: "What Are You LDAP?"
canonical_url: ""
organization: "the-software-s-journey"
part: 6
---

## Episode 6: Gang Memberships and Lockup

*🎵 What are you? What what, what what? 🎵*

-----

## “What You Belong To Defines What You Can Do” 🏛️

*Nick Stokes pins two documents on the board. Left: an LDAP user entry. Right: a list of groups. He draws lines between them.*

**NICK:** “Being Alice is not enough. Alice can be a person entry with perfect attributes — correct mail, correct uid, correct everything. But can Alice access the production database? Can Alice use the VPN? Can Alice read the security reports? The answer depends not on what Alice IS as an individual — it depends on what groups Alice BELONGS to.”

*He circles `memberOf: cn=admins,ou=Groups,dc=acme,dc=com`.*

**NICK:** “Membership. The gang file. And the lockup policy — if someone tries Alice’s password five times wrong, she goes into protective custody. No access. No appeal. Until an admin cuts her loose.”

-----

## 🗂️ SIPOC — Group Membership and Policy

|**Suppliers**              |**Inputs**                                                 |**Process**                                                                                                        |**Outputs**                                                                 |**Customers**                                                          |
|---------------------------|-----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------------|
|Administrator              |`ldapmodify` adding `member` DN to a group entry           |Group entry gains a `member` attribute; `memberOf` overlay adds `memberOf` to the user entry                       |Group entry with members; user entry with `memberOf` back-references        |Applications that ask “is this user in group X?” by checking `memberOf`|
|ppolicy overlay            |Failed bind attempts on a user entry                       |Count failures against `pwdMaxFailure`; update `pwdFailureTime`; set `pwdAccountLockedTime` when threshold exceeded|A locked account that returns `unwillingToPerform` (53) on all bind attempts|Security — prevents brute-force password attacks                       |
|Access Control Instructions|Bound DN identity, operation type, target DN and attributes|ACL evaluation: does this requester have permission for this operation on this target?                             |Allowed or denied; filtered attribute set in search results                 |Every LDAP operation — ACLs are the final security gate                |

-----

## Part 1: Group Types — The Gang Classifications 🏷️

LDAP supports several group objectClasses:

|objectClass         |How members are stored |Used for                                    |
|--------------------|-----------------------|--------------------------------------------|
|`groupOfNames`      |`member: full-DN`      |Standard RFC group with DN references       |
|`groupOfUniqueNames`|`uniqueMember: full-DN`|Like groupOfNames, enforces uniqueness      |
|`posixGroup`        |`memberUid: uid-string`|Unix groups (member by uid, not DN)         |
|`groupOfEntries`    |`member: full-DN`      |Newer RFC 7093 variant allowing empty groups|

```ldif
# Create a groupOfNames group
dn: cn=admins,ou=Groups,dc=acme,dc=com
objectClass: top
objectClass: groupOfNames
cn: admins
description: System administrators
member: cn=Alice Smith,ou=People,dc=acme,dc=com
member: cn=Bob Jones,ou=People,dc=acme,dc=com

# Create a posixGroup
dn: cn=developers,ou=Groups,dc=acme,dc=com
objectClass: top
objectClass: posixGroup
cn: developers
gidNumber: 10001
description: Software developers
memberUid: alice
memberUid: bjones
memberUid: cdavis
```

```bash
# Load groups
ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f groups.ldif
```

-----

## Part 2: Managing Group Membership 👥

```bash
# Add Alice to the 'security-team' group
ldapmodify \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret << 'EOF'
dn: cn=security-team,ou=Groups,dc=acme,dc=com
changetype: modify
add: member
member: cn=Alice Smith,ou=People,dc=acme,dc=com
EOF

# Add multiple members at once
ldapmodify \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret << 'EOF'
dn: cn=vpn-users,ou=Groups,dc=acme,dc=com
changetype: modify
add: member
member: cn=Alice Smith,ou=People,dc=acme,dc=com
member: cn=Bob Jones,ou=People,dc=acme,dc=com
member: cn=Carol Davis,ou=People,dc=acme,dc=com
EOF

# Remove a member from a group
ldapmodify \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret << 'EOF'
dn: cn=admins,ou=Groups,dc=acme,dc=com
changetype: modify
delete: member
member: cn=Bob Jones,ou=People,dc=acme,dc=com
EOF

# List all members of a group
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=Groups,dc=acme,dc=com" \
  "(cn=admins)" \
  member
```

-----

## Part 3: The memberOf Overlay — The Auto-Updating Gang Roster 🔄

Without the `memberOf` overlay, you can see who is in a group by querying the group entry. But you cannot ask “what groups does Alice belong to?” by querying Alice’s entry — Alice’s entry has no `memberOf` attribute.

The `memberOf` overlay adds `memberOf` back-references to user entries automatically when they are added to or removed from groups.

### Configuring the memberOf overlay

```ldif
dn: olcOverlay=memberof,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcMemberOf
olcOverlay: memberof
olcMemberOfDangling: ignore       # ignore if member DN doesn't exist
olcMemberOfRefInt: TRUE           # enable referential integrity
olcMemberOfGroupOC: groupOfNames  # which objectClass is a group
olcMemberOfMemberAD: member       # group's member attribute name
olcMemberOfMemberOfAD: memberOf   # user's back-reference attribute name
```

```bash
ldapadd \
  -Y EXTERNAL \
  -H ldapi:/// \
  -f memberof-overlay.ldif
```

### After enabling memberOf

```bash
# Now Alice's entry automatically shows her group memberships
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)" \
  memberOf

# dn: cn=Alice Smith,ou=People,dc=acme,dc=com
# memberOf: cn=admins,ou=Groups,dc=acme,dc=com
# memberOf: cn=security-team,ou=Groups,dc=acme,dc=com
# memberOf: cn=vpn-users,ou=Groups,dc=acme,dc=com

# Find all members of the admins group (via user entries, not group entry)
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(memberOf=cn=admins,ou=Groups,dc=acme,dc=com)" \
  uid cn

# Find everyone with VPN access who is in Engineering
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(&(memberOf=cn=vpn-users,ou=Groups,dc=acme,dc=com)(departmentNumber=Engineering))" \
  uid cn mail
```

**SARA:** “The `memberOf` attribute turns the group membership question upside down — from the group’s perspective to the user’s perspective. The application can ask ‘what groups is this user in?’ in a single search of the user’s entry. That is what the question ‘what are you?’ means at the access control level.”

-----

## Part 4: Referential Integrity — Clean Evidence 🔒

When an entry is deleted, the `refint` overlay automatically removes that entry’s DN from any group `member` attributes:

```ldif
dn: olcOverlay=refint,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcRefintConfig
olcOverlay: refint
olcRefintAttribute: member memberOf   # clean these attributes
olcRefintNothing: cn=admin,dc=acme,dc=com  # assign if last member deleted
```

Without `refint`, deleting Alice leaves dangling `member: cn=Alice Smith,...` references in group entries pointing to a non-existent DN. With `refint`, deleting Alice automatically removes her from all groups.

-----

## Part 5: ppolicy Overlay — The Lockup System 🚔

The **ppolicy** (Password Policy) overlay enforces password rules: lockout after failures, expiry, history, and complexity.

### Setting up ppolicy

```ldif
# First: load the ppolicy schema (if not already loaded)
dn: cn=module,cn=config
objectClass: olcModuleList
cn: module
olcModulePath: /usr/lib/ldap
olcModuleLoad: ppolicy.la

# Create a default policy entry
dn: cn=default,ou=Policies,dc=acme,dc=com
objectClass: top
objectClass: device
objectClass: pwdPolicy
pwdAttribute: userPassword         # Which attribute holds the password
pwdMinAge: 0                       # Minimum days between password changes
pwdMaxAge: 7776000                 # Maximum age: 90 days (in seconds)
pwdInHistory: 5                    # Remember last 5 passwords
pwdCheckQuality: 1                 # Check quality (1=if possible, 2=always)
pwdMinLength: 8                    # Minimum password length
pwdMaxFailure: 5                   # Lock after 5 failed attempts
pwdLockout: TRUE                   # Enable lockout
pwdLockoutDuration: 0              # Lock indefinitely (0 = until admin unlocks)
pwdExpireWarning: 604800           # Warn 7 days before expiry
pwdGraceAuthNLimit: 5              # 5 more logins after expiry before hard lock
pwdMustChange: FALSE               # Don't require change after admin reset
pwdAllowUserChange: TRUE           # Allow users to change their own password
```

```bash
ldapadd \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -f ppolicy.ldif

# Enable the overlay
ldapadd \
  -Y EXTERNAL \
  -H ldapi:/// << 'EOF'
dn: olcOverlay=ppolicy,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcPPolicyConfig
olcOverlay: ppolicy
olcPPolicyDefault: cn=default,ou=Policies,dc=acme,dc=com
olcPPolicyHashCleartext: TRUE       # Hash plaintext passwords on input
olcPPolicyUseLockout: TRUE          # Return lockout-specific error codes
EOF
```

### ppolicy Operational Attributes

After the overlay is active, each user entry gets password management attributes:

```bash
# Query password state for Alice
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" \
  -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)" \
  pwdChangedTime pwdAccountLockedTime pwdFailureTime \
  pwdHistory pwdReset pwdPolicySubentry

# dn: cn=Alice Smith,ou=People,dc=acme,dc=com
# pwdChangedTime: 20260601100000Z       ← When password was last changed
# pwdFailureTime: 20260611024700Z       ← Last failed attempt time
# pwdFailureTime: 20260611024702Z       ← Multiple failures stored
# pwdFailureTime: 20260611024703Z
```

### Checking and Clearing a Lockout

```bash
# Simulate 5 failed bind attempts
for i in 1 2 3 4 5; do
  ldapwhoami \
    -x \
    -H ldap://localhost \
    -D "cn=Alice Smith,ou=People,dc=acme,dc=com" \
    -w wrongpassword 2>&1
done
# Each returns: ldap_bind: Invalid credentials (49)
# After 5th: ldap_bind: Invalid credentials (49)
#             additional info: Account locked

# Now check the lock
ldapsearch -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)" \
  pwdAccountLockedTime
# pwdAccountLockedTime: 20260611024712Z  ← The exact lockout time

# Unlock: delete the lockout attribute
ldapmodify -x -H ldap://localhost \
  -D "cn=admin,dc=acme,dc=com" -w secret << 'EOF'
dn: cn=Alice Smith,ou=People,dc=acme,dc=com
changetype: modify
delete: pwdAccountLockedTime
-
delete: pwdFailureTime
EOF

# Now Alice can bind again
```

-----

## Part 6: Access Control Instructions — The Lab’s Security Policy 🔐

**ACI** (Access Control Instructions) — called `olcAccess` in OpenLDAP — define who can see and do what in the directory.

### ACI Syntax

```
olcAccess: to <what> by <who> <access-level> [<control>]

where:
  <what>:   * (everything), dn=..., attrs=..., filter=...
  <who>:    * (everyone), anonymous, users, self, dn=..., group=...
  <access>: none, disclose, auth, compare, search, read, write, manage
  <control>: stop, continue, break
```

### The Default Access Rules

```ldif
# These are the default OpenLDAP ACLs — always present
# Last rule always applies: access to everything is denied

# 1. Admin gets full access
olcAccess: to *
  by dn.exact="cn=admin,dc=acme,dc=com" manage
  by * break

# 2. Users can change their own password
olcAccess: to attrs=userPassword
  by self write
  by anonymous auth
  by * none

# 3. Users can read most attributes of other users
olcAccess: to attrs=shadowExpire,shadowFlag,shadowInactive,shadowLastChange,
               shadowMax,shadowMin,shadowWarning
  by self write
  by * none

# 4. Everyone can read everything else (often too permissive!)
olcAccess: to *
  by * read
```

### Production ACL Configuration

```ldif
# Realistic production ACLs

# ACL 1: Admin has full control
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcAccess
olcAccess: {0}to *
  by dn.exact="cn=admin,dc=acme,dc=com" manage
  by * break

# ACL 2: Passwords — self-write and anonymous auth only
olcAccess: {1}to attrs=userPassword
  by self write
  by anonymous auth
  by * none

# ACL 3: Each user can modify their own non-sensitive attributes
olcAccess: {2}to dn.regex="cn=[^,]+,ou=People,dc=acme,dc=com"
  attrs=telephoneNumber,mobile,homePostalAddress
  by self write
  by * read

# ACL 4: Service accounts can read user data for authentication
olcAccess: {3}to dn.subtree="ou=People,dc=acme,dc=com"
  attrs=cn,uid,mail,memberOf,departmentNumber
  by dn.exact="cn=webapp-reader,ou=Services,dc=acme,dc=com" read
  by users read
  by anonymous auth

# ACL 5: Groups — only admins and group admins can modify membership
olcAccess: {4}to dn.subtree="ou=Groups,dc=acme,dc=com"
  by dn.exact="cn=admin,dc=acme,dc=com" write
  by group/groupOfNames/member="cn=group-admins,ou=Groups,dc=acme,dc=com" write
  by users read
  by * none

# ACL 6: Policies — read-only for all, write for admin
olcAccess: {5}to dn.subtree="ou=Policies,dc=acme,dc=com"
  by dn.exact="cn=admin,dc=acme,dc=com" manage
  by * read

# ACL 7: Default — authenticated users can read the directory
olcAccess: {6}to *
  by users read
  by anonymous none
```

**GRISSOM:** “Access control is the final answer to ‘what are you?’ in a policy context. You might BE an inetOrgPerson with all the right attributes. But if the ACL says `by * none` for the attribute an application needs to read, it cannot see it. Being the right thing is not enough — the policy must confirm what you are allowed to be.”

-----

## Part 7: Testing Access Controls 🧪

```bash
# Test what Alice can see about herself
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=Alice Smith,ou=People,dc=acme,dc=com" \
  -w alicesecret \
  -b "cn=Alice Smith,ou=People,dc=acme,dc=com" \
  "(objectClass=*)"

# Test what the webapp service account can see
ldapsearch \
  -x \
  -H ldap://localhost \
  -D "cn=webapp-reader,ou=Services,dc=acme,dc=com" \
  -w webappsecret \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)" \
  "*" "+"

# Test anonymous access (should be very limited)
ldapsearch \
  -x \
  -H ldap://localhost \
  -b "ou=People,dc=acme,dc=com" \
  "(uid=alice)"

# Use slapacl tool to test ACLs without actually performing operations
slapacl \
  -F /etc/ldap/slapd.d \
  -b "cn=Alice Smith,ou=People,dc=acme,dc=com" \
  -D "cn=webapp-reader,ou=Services,dc=acme,dc=com" \
  "attrs=userPassword/auth"
# authcDN: "cn=webapp-reader,ou=Services,dc=acme,dc=com"
# read access to userPassword: ALLOWED (due to "by anonymous auth" rule)
```

-----

## What’s Next: The Police Radio 📻

*Warrick Brown holds up a syncrepl configuration.*

**WARRICK:** “The directory is populated. The policies are set. The access controls are running. But what happens when you need two directors? Two labs? One server gets updates, another server needs to know about them. Episode 7: replication. The police radio — how changes broadcast from provider to consumer, and how the online configuration (cn=config) manages it all without restarting.”

-----

**🔗 Resources**

- **OpenLDAP ppolicy overlay**: [openldap.org/doc/admin26/overlays.html#Password Policies](https://openldap.org/doc/admin26/overlays.html)
- **OpenLDAP Access Control**: [openldap.org/doc/admin26/access-control.html](https://openldap.org/doc/admin26/access-control.html)
- **RFC 3671 — Collective Attributes**: [rfc-editor.org/rfc/rfc3671](https://www.rfc-editor.org/rfc/rfc3671)

-----

*🔬 What Are You LDAP? — a CSI-style investigation into the directory service that classifies every identity. The evidence is in the entry. The answers are in the attributes.*
