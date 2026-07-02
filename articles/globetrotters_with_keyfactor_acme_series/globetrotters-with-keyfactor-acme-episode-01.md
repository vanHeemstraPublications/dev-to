---
title: "🌍 The Travel Agency Opens Ep.1"
series: "Globetrotters with Keyfactor ACME"
part: 1
organization: "the-software-s-journey"
tags: [keyfactor, acme, pki, certificates, automation, rfc8555]
---

## 🌍 Episode 1: The Travel Agency Opens

Picture a bustling travel agency counter. Travelers walk up needing one thing: a stamped, trusted document that lets them cross a border without a fuss. That document is a digital certificate. The travelers are ACME clients like Certbot. The borders are the domains they need to prove they own. And the agency, quietly making all the calls behind the counter, is the Keyfactor ACME server.

ACME, formally RFC 8555, was drawn up so that travelers would not need to fill out paperwork by hand every time. The protocol was first used by Let's Encrypt and has since become the common language spoken by CAs, PKI platforms, and browsers alike. Keyfactor ACME sits between the traveler and Keyfactor Command, the agency's back office, translating each request, renewal, and cancellation into something Keyfactor Command can process against the right embassy, in PKI terms, the right CA.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| ACME client (e.g. Certbot) | Certificate request, domain identifiers | Agency receives and translates the travel request | Forwarded request to the back office | Keyfactor Command |
| Keyfactor Command | Configured CA, certificate template | Back office processes the request against the correct embassy and paperwork rules | Issued, renewed, or revoked certificate | ACME client, end service or website |
| PKI operator | CA configuration, templates | Set up which embassies (private or public CAs) the agency can work with | Available CA options for travelers | Keyfactor ACME server |

### Two agencies, two neighborhoods

Not every traveler wants a private embassy visa. Some want a passport recognized worldwide. Keyfactor ACME serves both: private CAs such as Keyfactor EJBCA or Microsoft CA for internal travel, and public CAs such as DigiCert or Entrust for the traveler who needs to be recognized everywhere. The agency does not care which embassy the traveler eventually needs; it just knows how to route the paperwork once Keyfactor Command has been told which CA and template apply.

### Why the agency exists at all

Without an agency, every traveler would need to know the embassy's internal procedures, forms, and back rooms directly. Keyfactor ACME's whole reason for existing is to spare the traveler that pain: it is compatible with widely used ACME clients, and it lets Keyfactor Command keep its full PKI capabilities such as compliance rules and audit visibility, while travelers just speak the one ACME dialect they already know.

Next stop: before any traveler shows up at the counter, someone has to prepare the office itself. That is where Episode 2 picks up.

