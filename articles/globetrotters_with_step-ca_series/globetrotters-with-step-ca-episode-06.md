---
title: "Globetrotters with step-ca 🌍 Ep.6"
published: false
description: "Episode 6: The passport office that everyone in the world already trusts is great for crossing public borders. It is the wrong office to call when you just need to badge employees into your own building. This episode covers Web PKI versus Internal PKI, and the concrete reasons -- rate limits, naming restrictions, and lost control -- that push serious operators toward running their own."
tags: [security, pki, webpki, infrastructure]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-06.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 6
---

## Episode 6: Public Roads Versus Private Estates

The passport you carry across an international border is issued by a national government and recognized by essentially every other government on Earth. That's enormously convenient -- and entirely the wrong tool for getting your employees through your own office's front door. For that, you don't need a passport. You need an employee badge, issued by your own security office, recognized only by your own door scanners, governed entirely by your own rules about who gets one and for how long.

This is, almost exactly, the distinction between **Web PKI** and **Internal PKI**, and the source article is unambiguous about when to reach for each.

---

### SIPOC -- Choosing a PKI

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| Web PKI (RFC 5280 + CA/Browser Forum) | A public domain name, proof of control over it | Issue a certificate trusted by browsers and most TLS clients by default | A certificate that works out of the box for public-facing HTTPS | Anyone on the public internet visiting your site |
| Internal PKI (e.g., step-ca) | Whatever naming scheme, lifetime policy, and key types you want | Issue certificates under rules YOU define entirely | A certificate tailored to your infrastructure's actual needs | Your own services, containers, VMs, laptops, and devices |
| The CA/Browser Forum's Baseline Requirements | Public CA issuance practices | Constrain what public CAs are even ALLOWED to bind into a certificate | A flat prohibition on binding internal IPs or non-public DNS names | Anyone tempted to use Web PKI for purely internal infrastructure |

---

### Web PKI: The Passport Everyone Already Recognizes

You interact with **Web PKI** every time you load an HTTPS site -- this is the only PKI most people are even vaguely aware of. It's mostly defined by RFC 5280, refined by the CA/Browser Forum (often shortened to CA/B or CAB Forum), and sometimes called "Internet PKI" or PKIX, after the working group that built it. It defines the certificate varieties we covered in earlier episodes, what counts as a valid name and where it goes in a certificate, which signature algorithms are acceptable, how revocation and path validation work, and a long list of other rules.

Web PKI is important precisely because it works by default with browsers and nearly everything else speaking TLS. You should use it everywhere your system talks to the outside world over the public internet.

### Internal PKI: The Badge for Your Own Building

**Internal PKI** is PKI you run and operate yourself, for your own infrastructure: production services, containers, VMs, enterprise IT applications, corporate laptops and phones, and any other code or device you want to identify. It lets your stuff authenticate and establish secure channels regardless of where it physically runs -- including across the public internet -- without depending on a public CA's rules.

```
THE TRAVEL ANALOGY, MADE LITERAL

  Web PKI:
    A national passport. Universally recognized.
    Issued under rules YOU don't control.
    Rate limits exist (try applying for ten passports
    in one afternoon).
    Cannot legally certify "this badge gets you into
    Conference Room 4B" -- that's not what passports are for.

  Internal PKI:
    An employee access badge.
    Recognized only by YOUR door scanners.
    Issued under rules YOUR security office sets.
    Can be scoped to exactly what you need: "this badge
    works on floors 1-3, expires in 8 hours, full stop."
```

---

### Why Not Just Use Web PKI for Everything?

It's a fair question, and the source material answers it with three concrete, specific reasons rather than vague hand-waving.

**Reason one: rate limits and availability.** Even a free, automated CA like Let's Encrypt comes with rate limits and its own uptime dependencies. That's a real problem if you're deploying lots of services constantly and need certificates issued on demand, at volume, without waiting in line behind every other website on the internet.

**Reason two: you lose control over the details that matter.** With Web PKI you have little to no say over certificate lifetime, revocation mechanisms, renewal processes, key types, or algorithms. Every one of these is something a serious internal PKI deployment wants to tune deliberately -- and Episodes 10 through 12 of this series are entirely devoted to exactly that tuning.

**Reason three -- and this one is a flat, structural prohibition, not just an inconvenience:** the CA/Browser Forum's Baseline Requirements actively PROHIBIT Web PKI CAs from binding internal IP addresses (anything in `10.0.0.0/8`, for instance) or internal DNS names that aren't fully-qualified and resolvable in public global DNS.

```
A NAME WEB PKI WILL FLATLY REFUSE TO ISSUE FOR

  foo.ns.svc.cluster.local

  This is a perfectly normal Kubernetes cluster-internal DNS
  name. It is NOT resolvable on the public internet. The CAB
  Forum's Baseline Requirements forbid public CAs from binding
  it into a certificate, full stop, no exceptions, no appeals.

  If you want to identify THIS kind of name with a certificate
  -- and you very often will, the moment you're running
  anything containerized -- you need your own internal PKI.
```

If you want to bind internal names like this, issue large volumes of certificates, or control the fine details of how those certificates behave, Web PKI simply isn't an option. You need your own internal PKI. Period.

---

### The Practical Takeaway, Stated Plainly

The source material's own summary deserves to be quoted close to verbatim, because it's hard to improve on: use Web PKI for your public website and APIs. Use your own internal PKI for everything else.

```
USE WEB PKI FOR:
  Your public website
  Your public-facing API endpoints
  Anything a stranger's browser needs to trust by default,
  with zero prior configuration

USE YOUR OWN INTERNAL PKI FOR:
  Microservices talking to each other
  Containers, VMs, Kubernetes pods
  Corporate laptops and phones
  IoT devices
  Anything where you control both ends of the conversation
  and want full say over names, lifetimes, and key types
```

This is, not coincidentally, exactly the gap `step-ca` is built to fill. It's a private certificate authority designed specifically for the right-hand column above -- and from Episode 7 onward, we're going to start actually building one.

---

### What's Next: The Border Officer's Little Black Book

We've decided when to use your own internal PKI instead of the world's shared one. But the moment you run your own CA, a new question appears: how does anything ever come to TRUST your CA in the first place? **Episode 7** opens trust stores -- the literal little black book every border officer carries, listing exactly which passport offices they're willing to take at their word.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- CA/Browser Forum Baseline Requirements: cabforum.org/baseline-requirements-documents
- Let's Encrypt rate limits: letsencrypt.org/docs/rate-limits

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

