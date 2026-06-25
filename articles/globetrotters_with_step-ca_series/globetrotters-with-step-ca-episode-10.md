---
title: "Globetrotters with step-ca 🔑 Ep.10"
published: false
description: "Episode 10: Of all the decisions in this series, this is the one most likely to cause needless anxiety, and the source material's own verdict is refreshingly relaxed about it. This episode covers RSA, ECDSA, and EdDSA, the practical guidance on which to choose, and why your key type is almost never going to be the weakest link in your PKI."
tags: [security, pki, cryptography, ecdsa]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-10.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 10
---

## Episode 10: Packing the Right Kind of Lock

Before generating a key pair, every traveler eventually asks some version of the same question: should I get the deluxe biometric passport, or is the standard one fine? The honest answer, in both the travel world and the cryptography world, is that the standard option is almost always fine, and agonizing over this particular decision is rarely where your actual risk lives.

---

### SIPOC -- Choosing a Key Type

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| A subscriber generating its own key pair | A chosen algorithm and parameters (RSA size, EC curve) | Generate the key pair locally, ideally never letting the private half touch disk or the network | A public key ready for a CSR, a private key that stays exactly where it was born | The CSR-building step that follows in Episode 11 |
| RSA, ECDSA, or EdDSA | Algorithm-specific parameters | Produce mathematically valid key material meeting modern size/curve guidance | A key pair appropriate for the chosen algorithm | step-ca, which can sign leaf certificates using any of these regardless of the CA's own key type |
| step crypto keypair | A `--kty` flag and curve/size options | Generate the requested key type locally via the step CLI | A `.pub` and `.prv` file pair, or in-memory key material for programmatic use | Whatever process needs the resulting key pair next |

---

### The One Invariant That Actually Matters

Before talking algorithms, the source material insists on a non-negotiable rule that has nothing to do with which algorithm you pick: the security of a PKI depends critically on a simple invariant -- that the ONLY entity that knows a given private key is the subscriber named in the corresponding certificate. To guarantee this holds, best practice is for the subscriber to generate its OWN key pair, so it is the only thing that ever knows it. Avoid transmitting a private key across a network, full stop. You can even generate and use key pairs entirely in memory, never letting the private half touch a disk at all, if your tooling supports it.

```
THE RULE THAT MATTERS MORE THAN WHICH ALGORITHM YOU PICK

  The subscriber generates its own key pair.
  The private key NEVER travels across a network.
  The private key, ideally, never touches disk either.

  Get this wrong, and it doesn't matter how strong your
  algorithm is.
```

---

### RSA, ECDSA, and EdDSA: The Quick Guidance

With that settled, here's the source material's own pragmatic, slightly weary summary -- explicitly framed "as of May 2023," because cryptographic best practice genuinely does shift over time:

```
THERE'S A SLOW BUT ONGOING TRANSITION FROM RSA TO
ELLIPTIC CURVE KEYS (ECDSA OR EdDSA).

RSA
  If you use it: at least 2048 bits. Don't bother going
  bigger than 4096 bits -- you're past the point of
  meaningful benefit. Use RSA-PSS, not RSA PKCS#1 v1.5.

ECDSA
  P-256 is probably your best default choice
  (secp256k1 / prime256v1 in OpenSSL terms).

EdDSA
  Curve25519, if you're worried about certain
  algorithm-choice concerns and want something a bit
  fancier -- though tooling support is not as universal.
```

A small but genuinely important technical detail buried in this guidance: RSA-PSS, not the older RSA PKCS#1 v1.5 padding scheme, despite PKCS#1 v1.5 dating back to 1993 and having no KNOWN security weaknesses as of late 2025. RSA-PSS has an actual security proof behind it and is, in theory, more robust. When given the choice, prefer it.

---

### Generating Keys, Two Ways

With OpenSSL:

```bash
openssl ecparam -name prime256v1 -genkey -out k.prv
openssl ec -in k.prv -pubout -out k.pub
```

With the step CLI:

```bash
step crypto keypair --kty EC --curve P-256 k.pub k.prv
```

Both produce functionally equivalent key material -- the source material's own closing line on this choice is simply "choose your poison." Neither path is wrong.

---

### Why step-ca's Default Doesn't Match Your Leaf Certificates -- and Why That's Fine

Here's a detail worth flagging because it confuses people the first time they notice it: `step ca init` creates a PKI with ECDSA P-256 keys for the root and intermediate by default. Some applications, for legacy or compliance reasons, require an RSA chain instead -- and `step-ca` supports replacing the default chain with one built on RSA keys.

But here's the genuinely reassuring part: regardless of what key type your ROOT and INTERMEDIATE use, `step-ca` can sign leaf certificates using RSA, ECDSA, or Ed25519 key types, freely, on a per-request basis. An ECDSA intermediate signing an RSA leaf is completely normal and fully supported.

```bash
# An RSA root and intermediate, built explicitly
step certificate create "Example Root CA" root_ca.crt root_ca_key \
  --kty RSA --size 3072 --not-after 87660h

step certificate create "Example Intermediate CA" \
  intermediate_ca.crt intermediate_ca_key \
  --ca root_ca.crt --ca-key root_ca_key \
  --kty RSA --size 3072 --not-after 87660h
```

Even then, step-ca will still issue its own internal TLS leaf certificate as ECDSA P-256 for its own HTTPS listener -- a detail specific to how the CA secures itself -- regardless of what your chain above it uses.

---

### The Comforting Bottom Line

This is the episode where the source material actively tells you to relax, and the framing is worth repeating close to verbatim: key type is a big topic that's mostly unimportant in PRACTICE. You can change key types, and the actual cryptography genuinely won't be the weakest link in your PKI. The weak links live elsewhere -- in how you handle the private key, in your renewal automation, in your naming policy, in your revocation strategy. Choose a sane default (EC P-256 is a perfectly fine one), move on, and spend your remaining attention budget on the parts of this series that actually determine whether your PKI is secure in practice.

---

### What's Next: Applying at the Embassy

We've named the subject and chosen a lock for the document. The next step is the actual application process: submitting a request, proving who you are, and receiving the signed document back. **Episode 11** covers certificate signing requests, identity proofing, and renewal -- the full lifecycle of actually getting and keeping a certificate.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- Configure an RSA Certificate Chain Tutorial: smallstep.com/docs/tutorials/rsa-chain
- step crypto keypair reference: smallstep.com/docs/step-cli/reference/crypto/keypair

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

