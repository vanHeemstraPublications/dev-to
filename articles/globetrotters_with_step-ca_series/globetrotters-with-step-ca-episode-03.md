---
title: "Globetrotters with step-ca 👁️ Ep.3"
published: false
description: "Episode 3: Public key cryptography lets one computer prove it knows something to another computer without ever revealing what it knows. This episode covers key pairs, what you can actually do with them, and why Smallstep calls this superpower a kind of vision -- the ability to recognize someone across a network the way you'd recognize a face."
tags: [security, pki, cryptography, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-03.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 3
---

## Episode 3: The Power to See Without Touching

To prove you know a password, you have to share it. The moment you do, whoever you shared it with can use that password themselves, indistinguishably from you. Passwords are a one-way ticket: once shared, the secret stops being exclusively yours.

Now imagine a different kind of proof. Imagine you could prove you know something WITHOUT ever revealing it. That sounds like a magic trick. It is, in a sense -- a gift from mathematics that computer science gladly accepted without fully deserving it. This is what **public key cryptography** does, and Smallstep's own framing of it is the best one-line summary you'll find anywhere: public key cryptography lets computers see.

---

### SIPOC -- What a Key Pair Actually Does

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| A key generation algorithm | Mathematical parameters (curve, modulus, whatever the algorithm needs) | Generate a mathematically linked pair of values | A public key (shareable) and a private key (must stay confidential) | The owner of the key pair, and anyone they ever want to prove their identity to |
| The private key | Any piece of data | Sign the data | A signature that can ONLY have come from this private key | Anyone holding the matching public key, who can verify the signature |
| The public key | Encrypted data, or a signature to check | Decrypt data signed/encrypted for this key pair, or verify a signature | Confirmation of authenticity, or recovered plaintext | The original sender, who gets a working channel; or anyone confirming who really sent something |

---

### Key Pairs: Two Halves, One Whole

Public key cryptography (also called **asymmetric cryptography**) is built on **key pairs**: a **public key** that can be freely distributed to the entire world, and a corresponding **private key** that must be kept confidential by its owner. Worth repeating exactly as bluntly as the source material does: the security of the whole system depends entirely on keeping private keys private. There is no clever workaround for this. If the private key leaks, the system has failed, full stop.

There are exactly two things you can do with a key pair, and it's worth memorizing both because they map onto two completely different use cases:

```
ENCRYPT with the PUBLIC key
  -> Only the corresponding PRIVATE key can decrypt it.
  -> Use case: send someone a secret only they can read.

SIGN with the PRIVATE key
  -> Anyone with the corresponding PUBLIC key can verify it.
  -> Use case: prove a message came from you, without revealing
     your private key to anyone.
```

Certificates and PKI lean almost entirely on the second capability -- signing -- which is exactly why Episode 2 spent so long on signatures before we even got here.

---

### Vision, Not Magic

Here's the part worth sitting with. Public key cryptography lets one computer prove to another that it knows something, without sharing that knowledge directly. The source material's own analogy: it's like vision. If you know what someone looks like, you can recognize them by sight. You cannot shape-shift into them just because someone else knows what they look like too.

Translate that into a network exchange:

```
A WANTS TO VERIFY B'S IDENTITY

  1. A already knows B's PUBLIC key (what B "looks like")
  2. A sends B a big random number ("prove you're you")
  3. B signs that number with B's PRIVATE key
  4. B sends the signature back to A
  5. A verifies the signature using B's PUBLIC key
  6. If it checks out: A has strong evidence it's really
     talking to B -- because only B's private key could
     have produced a valid signature over A's random number
```

This is, almost word for word, how the original article describes the trick: you send a big random number, the other party signs it, and verifying that signature is good evidence you're actually talking to them. It works at internet scale, between machines that have never been within a thousand miles of each other, and that's precisely why the source material calls this "straight magic" while also insisting it's just math doing its job quietly in the background.

---

### Why a Photograph Beats a Password at the Border

Back to the airport one more time, because the metaphor earns its keep here. A password is like memorizing a secret phrase to whisper at the border -- anyone who overhears it, or who you told it to once, can now whisper the same phrase and get through. A face, by contrast, is something you can verify by LOOKING at it without the looker gaining the ability to become that face themselves. The border officer checks your face against your passport photo. They walk away knowing what you look like. They cannot use that knowledge to impersonate you at the NEXT border crossing.

Public keys behave like faces. Private keys behave like the unique, hard-to-fake biological reality behind that face. The entire reason certificates exist -- which we get to properly in Episode 4 -- is to solve one specific remaining problem: what happens when you've never seen this particular traveler's face before, and have no independent way to know it's genuinely theirs?

---

### What's Next: The Passport That Binds a Face to a Name

We now understand what a key pair can do. What we haven't solved is the bootstrapping problem: how do you learn someone's public key in the first place, with enough confidence to trust it's really theirs? **Episode 4** introduces the certificate -- the document that solves exactly this, by binding a name to a public key and having that binding signed by someone you already trust.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- An Introduction to Mathematical Cryptography: math.auckland.ac.nz/~sgal018/crypto-book/crypto-book.html
- step CLI keypair generation docs: smallstep.com/docs/step-cli

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

