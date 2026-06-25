---
title: "Globetrotters with step-ca 🧳 Ep.1"
published: false
description: "Episode 1: Before any passport is stamped or any border is crossed, we need a shared vocabulary. This episode lays out the cast of characters in every PKI story -- entities, identities, claims, subscribers, certificate authorities, and relying parties -- using the oldest trick in human travel: trusting a stranger because someone else vouched for them."
tags: [security, pki, stepca, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-01.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## 🧳 The Traveler Who Has Never Met You

Picture an arrivals hall. A traveler steps up to the booth. The border officer has never met this person in their life. Has no idea what kind of music they like, whether they remembered to water their plants before leaving, or what they had for breakfast. And yet, within about four seconds, the officer waves them through.

This small daily miracle is the entire plot of public key infrastructure (PKI), and it's worth slowing down on before we touch a single line of `step-ca` configuration. Smallstep's own missing manual on this topic opens with a confession: certificates and PKI are hard, and a lot of smart people avoid the subject out of quiet embarrassment. The fix isn't more shame. It's vocabulary. So let's build the cast of characters first, the way you'd learn the difference between a passport, a visa, and a boarding pass before your first international trip.

---

### SIPOC -- Setting the Vocabulary

| Suppliers | Inputs | Process | Outputs | Customers |
|---|---|---|---|---|
| The PKI glossary (RFC 4949 and friends) | Raw concepts: existence, attributes, claims | Define entity, identity, identifier/name, and claim precisely enough to build on | A shared vocabulary that doesn't wobble later when the math shows up | Every later episode in this series, which leans on these words without redefining them |
| An entity participating in a PKI | A name it wants to use, a claim it wants to make | Become a subscriber (or end entity) capable of holding a certificate | A named participant the rest of the system can reason about | The certificate authority, which will need someone to issue a certificate to |
| A certificate authority | A subscriber's claimed name and public key | Decide whether and how to vouch for that claim | An issued certificate, or a refusal | A relying party, who will eventually decide whether to trust that vouching |

---

### Entities: Anything That Exists, Even Loosely

An **entity** is anything that exists, even if only conceptually. Your laptop is an entity. The microservice you deployed last Tuesday is an entity. You, reading this, are an entity. The article that inspired this whole series put it more colorfully: even the burrito you ate for lunch counts, and so does the ghost you swore you saw as a kid, even if your mother was right and it was just a coat rack in bad lighting.

Every entity has an **identity** -- the genuinely hard-to-pin-down "what makes you you" quality, usually represented on computers as a bag of attributes: group membership, location, age, whatever matters in context. An **identifier**, or **name**, is different from an identity. It's just a unique reference to an entity that has one. You might be "Mike," but "Mike" isn't your identity any more than your passport number is your personality.

### Claims and Authentication

Entities can **claim** they have a particular name. They can also claim almost anything else -- their age, their access rights, their opinion on the meaning of life. **Authentication**, broadly, is the process of confirming whether a claim is true.

This is the whole job of the border officer. The traveler claims a name. The officer authenticates that claim by checking a document. Nobody at the booth is debating the traveler's hopes and dreams. They're checking one specific, narrow claim: does this face match this name on this document, issued by an authority the officer's government trusts?

### The Cast: Subscriber, CA, Relying Party

A few more terms, and then we can start building things:

```
SUBSCRIBER (also called END ENTITY)
  An entity participating in a PKI that can be the SUBJECT of a
  certificate. The traveler. The web server. Your laptop.

CERTIFICATE AUTHORITY (CA)
  An entity that issues certificates to subscribers.
  Also called the ISSUER. The passport office.

LEAF CERTIFICATE
  A certificate belonging to a subscriber (an "end entity"
  certificate). Why "leaf"? Because of how certificate chains
  branch -- more on that in Episode 8.

ROOT CERTIFICATE / INTERMEDIATE CERTIFICATE
  Certificates belonging to CAs, depending on their role in the
  chain. We'll meet both properly in Episode 8 as well.

RELYING PARTY (RP)
  A certificate USER that verifies and trusts certificates issued
  by a CA. The border officer.
```

One wrinkle worth flagging early, because it trips people up constantly: a single entity can be BOTH a subscriber and a relying party. Your laptop might hold its own certificate (subscriber) while also checking the certificate presented by a server it's connecting to (relying party). This dual role is exactly what happens during mutual TLS, which we'll get to much later in this series. For now, just notice that "traveler" and "border officer" aren't permanently assigned roles -- the same entity can wear either hat depending on which direction the conversation is going.

---

### Why This Matters Before We Touch step-ca

It would be tempting to skip straight to `step ca init` and start generating certificates. But every confusing PKI error message you will ever encounter -- "unknown authority," "certificate signed by unknown CA," "x509: certificate is valid for X, not Y" -- is really just one of these vocabulary terms misbehaving. A relying party that doesn't trust the issuer. A subscriber whose claimed name doesn't match what's on the certificate. Getting the cast of characters straight now means every later episode's error messages will make immediate, almost boring sense.

---

### What's Next: A Letter Only One Hand Can Sign

We've met the travelers, the passport offices, and the border officers. What we haven't covered is the actual mechanism that lets a claim be authenticated at a distance, across a network, between entities that have never been in the same room. In **Episode 2**, we look at message authentication codes and signatures -- the cryptographic equivalent of a signature that nobody else can forge.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- RFC 4949, Internet Security Glossary: tools.ietf.org/html/rfc4949
- step-ca on GitHub: github.com/smallstep/certificates

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*
