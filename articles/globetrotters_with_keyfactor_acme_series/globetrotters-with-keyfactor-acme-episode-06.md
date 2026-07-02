---
title: "Globetrotters with Keyfactor ACME 🎫 Ep.6"
series: "Globetrotters with Keyfactor ACME"
part: 6
organization: "the-software-s-journey"
tags: [keyfactor, acme, claims, eab, access-control, superadmin]
---

## Episode 6: Sponsorship and Visas

Some borders will not let a traveler in on a passport alone; they want a sponsor, someone who has already vouched for that person and is on record with the embassy. In Keyfactor ACME, that sponsorship comes in the form of an External Account Binding key, or EAB key, and it is the Claims command that decides who is eligible to receive one.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Access administrator | Claims command parameters, user or group identity | Create claims defining who may request EAB keys or administer the database | A set of authorized claims mapped to templates | ACME clients seeking to register |
| Identity provider (OAuth) | User authentication token | Verify the traveler's identity against the configured claim type | An authenticated, claim-matched traveler | Keyfactor ACME Key Management API |
| Keyfactor ACME server | Issued EAB key | Bind the key to the traveler's account during ACME registration | A registered ACME account tied to a specific certificate template | Certificate enrollment process |

### The sponsor's letter

Endpoints exist specifically to acquire and renew EAB keys, list and revoke accounts, and create, list, and delete claims controlling access to Keyfactor ACME. A claim does more than say yes or no to a traveler; the claims command is also used to map certificate templates to users or groups, deciding which template in Keyfactor Command applies to enrollments coming in against that traveler's EAB key. It is less a single gate and more a full customs desk that also decides which visa category the traveler falls into.

### When the sponsor system changes hands

Sponsorship used to run through Active Directory groups, letting AD users and groups be configured directly for EAB key generation. That path has closed for new registrations: the server exclusively supports OAuth for client authentication now, so AD can no longer generate new EAB keys. Existing AD-sponsored travelers already in the system were not stranded, though; on upgrade, their accounts were migrated into claims of type Active Directory User, with the claim value in the DOMAIN\\Username form, so their existing paperwork still clears the desk.

### The office's own master key

There is one more credential worth noting: SuperAdmin, a role that lets a user configure the Keyfactor ACME implementation itself and manage claims and identifiers through the API, rather than only requesting a certificate. That is less a visitor's visa and more the badge that lets someone walk behind the counter and rearrange the office. Episode 7 follows the paper trail back to headquarters to see how the whole embassy network actually talks to itself.

