---
title: "Globetrotters with step-ca 🛂 Ep.4"
published: false
description: "Episode 4: What if you've never seen this traveler's face before? That's what certificates solve. This episode covers the fundamental, almost embarrassingly simple structure of a certificate -- a public key and a name, signed by someone you trust -- and why a passport is the cleanest real-world analogy you'll ever find for it."
tags: [security, pki, x509, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-04.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 4
---

## Episode 4: The Passport That Binds a Face to a Name

Episode 3 ended on an unresolved problem: vision only helps you recognize a face you've already seen. What does a border officer do with a traveler whose face they have genuinely never encountered before?

The answer, in the physical world, is a passport. The officer hasn't met you, but they trust the government that issued your document. The document carries your name and your photo, sealed together by an authority the officer's own government has agreed to trust. In the digital world, the answer is a **certificate**, and it works on the exact same principle, just with signatures standing in for ink and security holograms.

---

### SIPOC -- Issuing a Certificate

| Suppliers | Inputs | Process | Outputs | Customers |
|---|---|---|---|---|
| A subscriber (the subject) | A name, a public key | Submit both to a certificate authority for binding | A claim ready to be vouched for | The certificate authority, which decides whether to sign it |
| A certificate authority (the issuer) | The subscriber's name and public key | Build the data structure, sign it with the CA's own private key | A signed certificate -- a claim with a cryptographic seal | The relying party, who will eventually need to trust this claim |
| The relying party | A certificate, the issuer's already-known public key | Verify the signature, then trust the bound name-to-key relationship if the issuer is trusted | A confirmed, usable public key for the named subject | Whatever secure channel the relying party is trying to establish with the subject |

---

### The Whole Idea, In One Sentence

Strip away every diagram, every acronym, every encoding format we're going to cover in later episodes, and you're left with the single sentence the source article anchors its entire explanation around:

```
THE GOAL OF CERTIFICATES AND PKI IS TO BIND NAMES TO PUBLIC KEYS.

That's it. Everything else is implementation detail.
```

A certificate is a data structure containing a public key and a name. That structure is then signed. The signature **binds** the public key to the name. The entity that signs is the **issuer** (or certificate authority). The entity named inside is the **subject**.

If *Some Issuer* signs a certificate for *Bob*, you can read that certificate as a plain-language claim: *"Some Issuer says Bob's public key is 01:23:42..."* It's a claim, made by Some Issuer, about Bob. The claim is signed, so anyone who knows Some Issuer's public key can verify it really came from Some Issuer (Episode 2's signature property, doing its job). And if you trust Some Issuer, you can trust the claim itself -- which means you now know Bob's public key, even though Bob never told you directly.

```
THE CERTIFICATE, AS A SENTENCE

  "[ISSUER] says [SUBJECT]'s public key is [PUBLIC KEY VALUE]."

  Signed by:  [ISSUER]'s private key
  Verified using:  [ISSUER]'s public key (which YOU already trust)
```

---

### Driver's Licenses and Passports, Side by Side

The source article reaches for exactly this analogy, and it holds up remarkably well under scrutiny. If you've never met someone before, but you trust the DMV (or the passport office), you can use their license or passport for authentication: check that the document is genuine (hologram, security thread, whatever your jurisdiction uses), look at the photo, look at the person standing in front of you, read the name.

```
THE DRIVER'S LICENSE / CERTIFICATE PARALLEL

  Human world:                          Computer world:
  ───────────────────────────           ───────────────────────────
  Check the license is genuine          Verify the signature
  (hologram, security features)         (using the issuer's public key)

  Look at the photo                     Look at the public key

  Look at the person in front of you    "Look at" the private key
                                         across the network (Episode 3's
                                         random-number-signing trick)

  Read the name                         Read the subject name
```

There's other stuff stuffed into both documents too. A driver's license says whether you're an organ donor and whether you're cleared to drive a commercial vehicle. A certificate says whether its holder is itself allowed to act as a CA, and whether the public key inside is meant for signing or encryption. Both carry expiration dates. None of this extra detail changes the core sentence above -- it's all just additional clauses tacked onto the same fundamental claim.

---

### A Real Certificate, Briefly Inspected

Using the `step` CLI, you can inspect any certificate and see this structure laid bare:

```bash
step certificate inspect svc.crt --short
```

```
X.509v3 TLS Certificate (ECDSA P-256) [Serial: 7720...1576]
Subject: svc.example.com
Issuer: Smallstep Intermediate CA
Provisioner: carl@smallstep.com [ID: JxCv...IjUg]
Valid from: 2020-09-22T00:59:37Z
        to: 2020-09-23T01:00:37Z
```

Subject. Issuer. A validity window. Strip away the formatting and you've got the exact sentence from earlier: the Smallstep Intermediate CA says svc.example.com's public key is whatever's embedded in this file, valid for roughly 24 hours. That 24-hour window is not an accident -- step-ca's default leans hard into short lifetimes, and Episode 12 explains exactly why.

---

### Why "Simple" Doesn't Mean "Easy"

It's worth being honest here, the way the source material is honest about its own subject: the CORE IDEA of a certificate is genuinely simple. A name. A public key. A signature binding them together. What makes PKI feel hard in practice isn't this core idea -- it's everything bolted onto the edges of it. How do you encode that data structure as actual bytes? What format do different tools expect? How do you know if a certificate is meant for a server, a person, or another CA? Those questions are real, and they deserve real episodes. But none of them change the sentence at the center of this one.

---

### What's Next: The Paperwork Behind Every Passport

A passport's CONTENT is simple -- name, photo, signature. A passport's PRINTING STANDARD, on the other hand, is governed by international document standards most travelers never think about. Certificates have the exact same split. **Episode 5** dives into X.509, ASN.1, OIDs, DER, PEM, and the PKCS family -- the paperwork standards behind every certificate you'll ever inspect.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- step certificate inspect documentation: smallstep.com/docs/step-cli/reference/certificate/inspect
- RFC 5280, Internet X.509 Public Key Infrastructure Certificate and CRL Profile: tools.ietf.org/html/rfc5280

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

