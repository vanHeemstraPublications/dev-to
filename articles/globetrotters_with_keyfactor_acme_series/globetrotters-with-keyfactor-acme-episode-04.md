---
title: "Globetrotters with Keyfactor ACME 🛂 Ep.4"
series: "Globetrotters with Keyfactor ACME"
part: 4
organization: "the-software-s-journey"
tags: [keyfactor, acme, configuration, oauth, sql, command-line-tool]
---

## Episode 4: The Passport Office

Every travel agency needs a back-office worker who fills in the ledgers: which database tracks every stamp ever issued, which headquarters system to call, and which credentials prove the office itself is legitimate. In Keyfactor ACME, that worker is the configure command of KeyfactorACMEConfig.exe.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Database administrator | SQL server name, authentication choice | Create or connect to the ACME database, choosing SQL or Integrated Authentication | A provisioned and upgraded ACME database | Keyfactor ACME server |
| Identity provider | OAuth authority URLs, client ID and secret, JWKS URL | Configure OAuth for both client-facing and Command-facing authentication | Verified authentication to Keyfactor Command | ACME clients, Keyfactor Command |
| Operations engineer | Configure command parameters | Run configure, fix any reported errors, re-run as needed | A named, working Keyfactor ACME instance bound to a hostname | Travelers (ACME clients) arriving at the counter |

### The ledger room

The configure command is run from an administrator command prompt or a regular PowerShell window, deliberately not the PowerShell ISE, since that shell lacks support the tool needs. The very first thing it does is sort out the ledger: pointing at a SQL server, choosing between SQL or Integrated Authentication, and creating the database if it does not already exist, then upgrading it to the current schema.

### Proving the office is who it says it is

Once the ledger is in place, the tool configures authentication with the Keyfactor ACME Key Management API and with Keyfactor Command itself. These can run through OAuth, and notably the identity provider used to authenticate travelers at the counter does not have to be the same one used for the office's own back-office calls to headquarters. During this step the authentication type provided is checked against what Keyfactor Command actually expects; a mismatch stops the process cold rather than limping along half-configured.

### If a form comes back stamped "rejected"

Configuration is not a one-shot ritual. If the tool reports an error, the fix is simply to correct the issue and re-run the command; there is no need to tear the office down and start again. The same command also underpins load-balanced setups, where several physical offices share one common ledger, a topic Episode 9 returns to. Next, in Episode 5, we look at how the office actually proves a traveler owns the address they claim to live at.

