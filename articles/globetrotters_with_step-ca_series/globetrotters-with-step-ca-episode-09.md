---
title: "Globetrotters with cert-ca 🏷️ Ep.9"
published: false
description: "Episode 9: A passport's cover only ever needs one name. Modern certificates faced a similar question and arrived at a better answer than the original design: stop overloading one crowded field, and use a dedicated extension built for exactly this. This episode covers Subject Alternative Names, why the old Distinguished Name fields fell out of favor, and how to pick the right SAN type for people, machines, and code."
tags: [security, pki, x509, dns]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-09.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 9
---

## Choosing What Name Goes on the Cover

Imagine a passport whose cover tried to cram in your name, your hometown, your employer, your favorite color, and a few other fields nobody asked for, all squeezed into one crowded line. That's roughly what the original X.509 naming scheme looked like, and the modern world has quietly moved past it in favor of something cleaner.

---

### SIPOC -- Naming a Certificate's Subject

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| PKIX (original design) | A subject's locality, state, country, organization, common name | Pack all of it into a Distinguished Name (DN) | A crowded, phone-book-style name field, now deprecated by the CAB Forum | Legacy tooling that still expects a DN, and not much else |
| The CAB Forum (modern guidance) | The same naming need, simplified | Define the Subject Alternative Name (SAN) X.509 extension | A clean, purpose-built name binding, separate from the DN entirely | Every modern certificate consumer -- browsers, TLS libraries, step-ca itself |
| A subscriber requesting a certificate | The kind of entity they are: person, machine, code | Choose the matching SAN type | A SAN entry that correctly identifies what's actually being certified | Relying parties, who can now check the right kind of name for the right kind of subject |

---

### The Old Way: Distinguished Names

PKIX originally specified that a website's DNS hostname should be bound in the certificate's **Distinguished Name (DN) common name** field. The DN itself traces back to X.500's phone-book ambitions from Episode 5 -- it can include a common name, locality, state, country, organization, organizational unit, and a fair amount of what the source material calls "other irrelevant crap," because, again, this stuff was designed thirty years ago to build a digital phone directory, not to identify a website.

The CAB Forum has since deprecated this practice and made the entire DN field optional in its Baseline Requirements (see section 7.1.4.2, if you enjoy reading standards documents for fun). Nobody fully understands distinguished names, they don't map cleanly onto how the web actually works, and the source material's advice is to avoid them. If you must use one, keep it simple -- a common name is probably all you need, and maybe an organization name if you're feeling adventurous.

---

### The Modern Way: Subject Alternative Names

Instead, modern best practice leverages the **Subject Alternative Name (SAN)** X.509 extension to bind a name into a certificate. There are four kinds of SANs in common use, and each maps cleanly onto a different category of "thing being identified":

```
DNS SAN
  A domain name. Use for: machines, services, code.
  Example: api.example.com

EMAIL SAN
  An email address. Use for: people.
  Example: alice@example.com

IP SAN
  An IP address. Use for: machines and code, when a stable
  name isn't available or appropriate.
  Example: 10.0.4.12

URI SAN
  A Uniform Resource Identifier. Use for: getting fancy, or
  whenever the first three don't fit cleanly.
  Example: spiffe://example.com/service/billing
```

The reasoning behind this list is pragmatic, not arbitrary: these four identifier types are already supposed to be unique in the contexts that matter, and they map well onto the things we actually want to identify. Email addresses already uniquely identify people in most systems. Domain names and IP addresses already uniquely identify machines and code. URIs are there if you want maximum flexibility -- and, in the SPIFFE ecosystem and similar frameworks, URI SANs have become the backbone of entire workload-identity systems.

```
THE SOURCE MATERIAL'S OWN GUIDANCE, COMPRESSED

  Use SANs for names.
  DNS SANs for code and machines.
  EMAIL SANs for people.
  Use URI SANs if these don't fit.
```

---

### Multiple Names, and the Wildcard Trick

Web PKI allows multiple names to be bound into a single certificate, and allows wildcards within those names. A certificate can list several SANs at once and can include entries like `*.smallstep.com` -- genuinely useful for a site that needs to respond to both `smallstep.com` and `www.smallstep.com` under the same certificate, rather than juggling two separate ones.

```
A CERTIFICATE WITH MULTIPLE SANS

  DNS:  smallstep.com
  DNS:  www.smallstep.com
  DNS:  *.api.smallstep.com

  One certificate. One private key. Three valid names a
  relying party will accept when connecting.
```

---

### Naming in Practice, With step-ca

```bash
# A leaf certificate for a service, named by DNS SAN
step ca certificate api.internal.example.com api.crt api.key

# A certificate covering multiple names at once
step ca certificate api.internal.example.com api.crt api.key \
  --san api.internal.example.com \
  --san 10.0.4.12 \
  --san api-backup.internal.example.com
```

`step-ca` also supports certificate issuance **policies**, letting administrators configure exactly which Subjects, SANs, and Principals a given CA or provisioner is allowed to sign for. A typical policy might restrict issuance to strict subdomains of an internal zone, encoded as `*.internal.example.com` -- meaning the CA itself enforces the naming discipline this episode is describing, rather than relying on every requester to behave correctly.

---

### Naming the Traveler Versus Naming the Vehicle

Back to the airport one final time for this episode: a passport names a PERSON. A vehicle registration names a CAR. You wouldn't try to cram both naming schemes into the same physical document, because they identify fundamentally different kinds of things. SANs formalize this same intuition for certificates -- an EMAIL SAN names a person, a DNS SAN names a service, and choosing the right one for the right subject is most of what "good naming practice" actually means in PKI.

---

### What's Next: Packing the Right Kind of Lock

We've decided what name goes on the cover. The next decision is what kind of lock secures the document -- and, reassuringly, the source material's own verdict here is that this decision matters far less than people assume. **Episode 10** covers key types and algorithms: RSA, ECDSA, and EdDSA, and why none of them is likely to be the weakest link in your PKI.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- CA/Browser Forum Baseline Requirements section 7.1.4.2: cabforum.org/baseline-requirements-documents
- step-ca policy documentation: smallstep.com/docs/step-ca/policies

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

