---
title: "Globetrotters with step-ca ⏳ Ep. 12"
published: false
description: "Episode 12: The finale. Cancelling a passport at every border crossing point in the world, in real time, is genuinely hard. Letting it simply expire on schedule is genuinely easy. This last episode covers active versus passive revocation, why step-ca leans hard into the second option, and closes the whole series with the one sentence that was true on page one and remains true here: certificates and PKI bind names to public keys."
tags: [security, pki, stepca, revocation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-12.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 12
---

## Episode 12: Letting Old Passports Quietly Expire

Imagine trying to cancel a stolen passport everywhere, instantly, the moment you realize it is missing. Every border post on Earth would need to receive the cancellation notice before that passport next gets presented anywhere. That is an enormous, genuinely hard coordination problem. Now imagine a different approach entirely: issue passports that are only valid for twenty four hours in the first place. Lose one, and the window during which it is dangerous closes on its own, quickly, without a single phone call to a single border post anywhere.

This is the entire philosophical heart of how step-ca approaches revocation, and it closes out this series exactly where the source material closes out its own explanation.

---

### SIPOC for Certificate Revocation

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| Active revocation infrastructure, CRL and OCSP | A revoked certificate's serial number | Publish that serial on a list, or answer queries about its status, in real time | A revocation signal relying parties must actively go check | Relying parties willing to pay the cost of an extra network round trip per connection |
| Passive revocation | A short certificate lifetime, plus a CA that simply refuses to renew | Let expiration do the work that active revocation would otherwise need infrastructure for | A certificate that quietly stops being valid on schedule | Relying parties, who get the same protection for free, just slightly delayed |
| step-ca renewal and revoke commands | A certificate you want to stop trusting | Disable future renewal for that certificate | A certificate that is still valid until expiry, but will never be renewed again | Whoever is managing the fleet, watching the clock count down safely |

---

### Active Revocation, Cancelling Every Copy Everywhere Right Now

If a private key is compromised, or a certificate is simply no longer needed, you might want to mark it invalid immediately, before its natural expiry, so it stops being trusted right away. This is active revocation, and the source material does not sugarcoat how messy it gets in practice. Revoking X.509 certificates is, in its own words, a big mess. Unlike expiration, revocation status cannot be encoded inside the certificate itself, since the certificate was already signed before anyone decided to revoke it. The relying party has to determine revocation status through some separate, out of band process.

```
TWO ACTIVE REVOCATION MECHANISMS

CRL, Certificate Revocation List
  A published list of revoked serial numbers.
  Relying parties download and check it.
  Only needs to include serials for certificates that are
  revoked and not yet expired naturally, so shorter cert
  lifetimes keep CRLs smaller automatically.

OCSP, Online Certificate Status Protocol
  Relying parties query an OCSP responder with a specific
  serial number and get back a live answer.
  Sounds great, has real problems.
  Privacy: the responder can see every site you are
  visiting, inferred from which certificates you ask about.
  Overhead: an extra network round trip on every single
  TLS connection.
```

Both mechanisms require building and operating highly available infrastructure, and both suffer from inconsistent support across the broader PKI ecosystem. This operational burden, combined with patchy real-world adoption, is exactly what makes reliable active revocation extremely difficult to deliver in practice, even when you genuinely want it.

---

### Passive Revocation, Just Let It Expire

For internal PKI specifically, the trend has moved decisively toward accepting this reality and embracing passive revocation instead: issue certificates that expire quickly enough that active revocation is not even necessary. If you want to revoke a certificate, you simply disallow its renewal and let it expire naturally on schedule.

```
TO PASSIVELY REVOKE A CERTIFICATE

  Block its renewal at the CA.
  Wait.
  It expires. It is no longer trusted. Done.

  No CRL to publish. No OCSP responder to query.
  No extra network round trip for anyone, ever.
```

This is, almost word for word, the framing step-ca's own documentation uses elsewhere: good certificates die young. Once a certificate is issued, a CA genuinely cannot un-issue it. A compromised private key remains dangerous until its certificate either gets actively revoked or simply expires. Passive revocation accepts this and designs around it by making the simply expires path fast enough to matter.

For this to actually work as a security control, you need short lived certificates. How short depends entirely on your threat model, which is, as the source material wryly notes, how security professionals say shrug. Twenty four hours is a common default. Some deployments go far shorter, down to five minutes. There are real tradeoffs the shorter you go: every renewal now requires contacting an online CA, so your CA infrastructure needs to be genuinely scalable and highly available. And as you push certificate lifetimes shorter and shorter, clock synchronization across your fleet stops being a nice to have and starts being load bearing. Keep your clocks in sync, or you are going to have a very confusing afternoon.

Even teams that do use CRLs benefit from this approach as a complement, not a replacement: shorter lived certificates naturally keep CRLs smaller, since a CRL only needs to list serials for certificates that are revoked and have not yet expired on their own. Shorter lifetimes shrink that list for free.

---

### Revoking a Certificate With step-ca

```bash
step ca revoke --cert svc.crt --key svc.key
```

This instructs the CA to block future renewal of the named certificate. The certificate remains technically valid, cryptographically, until its existing expiry, exactly as passive revocation implies, but no further renewal will ever be granted for it. The clock that was always going to run out keeps running, and once it does, the certificate is functionally as dead as if it had been actively revoked the moment you ran this command.

```
A REVOKED CERTIFICATE'S REMAINING LIFE

  Issued at:      hour 0
  Revoked at:     hour 10, renewal now blocked
  Still valid:    hours 10 through 24, the remaining window
  Truly dead at:  hour 24, natural expiry, same as always

  The window between revocation and expiry is the residual
  risk passive revocation accepts as a tradeoff for avoiding
  CRL and OCSP infrastructure entirely. Shorter lifetimes
  shrink this window automatically.
```

---

### When Passive Revocation Is the Wrong Tool

The source material is careful not to oversell this. For the web, and for other scenarios where passive revocation genuinely will not work, its own advice is blunt: stop, and reconsider whether passive revocation is even the right model for this particular case. Some certificates need to be killable instantly, with zero residual window, and for those cases, active revocation's mess is a price worth paying. The honest takeaway is not that passive revocation always wins. It is that passive revocation is the right default for most internal PKI, and you should know exactly why before reaching for the more complicated alternative.

---

### The Whole Series, Brought Back to One Sentence

We opened Episode 1 in an arrivals hall, with a border officer waving through a traveler they had never met. Twelve episodes later, here is everything that happened in between, compressed back down to where we started.

```
ENTITIES make CLAIMS about their NAMES.

SIGNATURES let those claims be authenticated without ever
  sharing a secret.

CERTIFICATES bind a NAME to a PUBLIC KEY, signed by an
  ISSUER you have agreed, in advance, to trust.

TRUST STORES are where that agreed in advance actually
  lives, on every device, maintained by a small number of
  organizations the whole internet quietly depends on.

CHAINS let a ROOT stay safely offline while an INTERMEDIATE
  does the everyday work of signing LEAVES.

SANS say exactly what kind of thing is being named.

KEY TYPES matter far less than people assume, as long as
  the private half never leaves the subscriber's hands.

CSRS and PROVISIONERS are the application process, the
  proof of identity, and the embassy stamp.

REVOCATION, done passively through short lifetimes, lets
  expiration do the hard work that active infrastructure
  would otherwise need to do in real time.
```

And underneath every single one of those twelve ideas, the same single sentence the source article opened with, and which deserves to be the very last word of this series too:

```
THE GOAL OF CERTIFICATES AND PKI IS TO BIND NAMES TO
PUBLIC KEYS.

That is it. Everything else is just implementation detail.
```

The border officer in Episode 1 never needed to know about ASN.1, OIDs, or OCSP responders to do their job in four seconds flat. Neither, in the end, do you. You just needed the vocabulary, the metaphor, and twelve episodes of patience. Pack light. The next border crossing should feel a lot less intimidating.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- Good certificates die young, what is passive revocation: smallstep.com/blog/passive-revocation
- Certificate Revocation Management in step-ca: smallstep.com/docs/step-ca/revocation
- step-ca on GitHub: github.com/smallstep/certificates
- step CLI on GitHub: github.com/smallstep/cli

---

*Globetrotters with step-ca, every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds. Safe travels.*

