---
title: "Globetrotters with Keyfactor ACME 🏛️ Ep.7"
series: "Globetrotters with Keyfactor ACME"
part: 7
organization: "the-software-s-journey"
tags: [keyfactor, acme, architecture, api, database, encryption]
---

## Episode 7: The Embassy Network

Behind every travel agency counter is a network the traveler never sees: a courier line to headquarters, a records room storing every stamped document, and a locked drawer for anything genuinely sensitive. That is the architecture of Keyfactor ACME.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Keyfactor Command | API endpoint, hostname | Route certificate request, renew, and revoke calls over the Keyfactor API | Processed certificate lifecycle actions | Keyfactor ACME server |
| Database server | Dedicated ACME schema | Store configuration and operational data, optionally shared across multiple servers | A persistent, queryable record of accounts and certificates | Keyfactor ACME server instances |
| Security engineer | SQL encryption, optional application-level encryption | Protect sensitive data such as EAB HMAC keys at rest | Encrypted, access-controlled data store | Compliance and audit stakeholders |

### The courier line to headquarters

The Keyfactor API is used to communicate between Keyfactor ACME and Keyfactor Command to perform certificate request, renewal, and revocation tasks, and the hostname of the ACME server itself is what gets used to build the URLs that ACME clients actually call. In other words, the courier line runs both ways: outbound to headquarters for processing, and inbound as the address travelers dial to reach the counter at all.

### The records room

The Keyfactor ACME database lives in its own schema and can sit on the same database server that hosts Keyfactor Command, or on a shared one, which matters because multiple Keyfactor ACME servers can point at a common database to support load balancing. By default, sensitive records such as EAB HMAC keys are already stored using SQL encryption, and for anyone who wants an extra lock on that drawer, an additional layer of application-level encryption is available on top.

### Who is allowed behind the counter

Access to the records room itself is tightly scoped. For Windows installs configured with SQL Authentication, only the current user and the application pool user can run any command-line tool commands; when Windows authentication is used instead, it is the application pool user who is granted access to the SQL Server and the ACME database. The whole office also answers to a single front door: a virtual directory created on the web server, ACME by default, though that path can be renamed during configuration.

With the plumbing understood, Episode 8 finally follows a traveler all the way through: registering, boarding, renewing, and, when it is time, being turned away at the gate.

