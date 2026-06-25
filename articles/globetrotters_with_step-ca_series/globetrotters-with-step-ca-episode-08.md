---
title: "Globetrotters with step-ca 🧷 Ep.8"
published: false
description: "Episode 8: Your passport alone is rarely enough at certain borders -- sometimes you need the accompanying visa, the supporting letter, the whole stapled folder that traces back to an authority the officer actually trusts. This episode covers certificate chains: why intermediates exist, why roots stay offline, and how relying parties walk the whole chain back to a trust anchor."
tags: [security, pki, certificates, stepca]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-08.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 8
---

## Episode 8: The Folder of Stamps Back to the Homeland

A passport on its own usually does the job. But sometimes -- crossing into a country with stricter requirements, traveling on a diplomatic mission, carrying documents on behalf of an organization -- a single passport isn't enough. You need the supporting visa stapled in, maybe a letter of introduction from your embassy, a whole small folder of documents that together trace an unbroken line of authority back to a government the border officer actually recognizes.

That folder is exactly what a certificate chain is, and understanding why it exists, rather than just having every certificate signed directly by a root, is one of the more genuinely clever design decisions in all of PKI.

---

### SIPOC -- Building and Validating a Chain

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| The root CA, kept offline | An intermediate CA's CSR | Sign the intermediate certificate, infrequently, by design | A signed intermediate certificate, ready to do the CA's day-to-day work | The intermediate CA, which now does all routine signing |
| The intermediate CA, kept online | A subscriber's CSR | Sign leaf certificates routinely, automated, at scale | Leaf certificates, issued continuously without ever touching the root key | Subscribers needing certificates, and the relying parties who'll eventually validate them |
| A relying party | A leaf certificate plus its accompanying intermediate(s) | Walk the chain: verify leaf was signed by intermediate, intermediate by root, root is self-signed and already trusted | A pass or fail verdict via certificate path validation | Whatever secure connection the relying party is trying to establish |

---

### Why the Root Almost Never Signs Anything Directly

Here's the practical problem certificate chains solve. People tend to obsess enormously over root private key management for internal PKIs, often to the point of delaying or outright preventing deployment. The source material pushes back on this anxiety with a sharp comparison: your AWS root account credentials are at least as sensitive as a PKI root key, if not more so. How do you manage THOSE credentials? Presumably with some combination of careful storage, limited access, and not using them for routine daily operations. The same logic applies here.

To make certificate issuance scalable, which is to say, to make automation actually possible, the root private key is used only infrequently, to sign a small number of intermediate certificates. Those intermediate CAs, also called subordinate CAs, then use their own private keys to sign and issue leaf certificates to subscribers, routinely and automatically.

```
THE DIVISION OF LABOUR

  Root CA
    Signs intermediates. Rarely. Can be kept fully offline.
    The diplomatic seal that's almost never actually applied
    in person.

  Intermediate CA
    Signs leaf certificates. Constantly. Stays online and
    automated. The consulate that handles routine, everyday
    document processing.

  Leaf certificate
    Belongs to a subscriber. The actual passport in your hand.
```

A crucial bonus: intermediates generally are NOT included in trust stores, which makes them considerably easier to revoke and rotate than a root would be. If an intermediate is ever compromised, you can retire it and issue a new one without needing every relying party on Earth to update their trust store. Only the chains that referenced the old intermediate need to change.

This bundle -- leaf, intermediate, root -- forms a certificate chain.

---

### The Chain, Drawn Out

```
                  ROOT CA
                  (self-signed, offline, almost never touched)
                     |
                     | signs (rarely)
                     v
              INTERMEDIATE CA
              (online, automated, does the routine signing)
                     |
                     | signs (constantly)
                     v
            LEAF CERTIFICATE
            (yours, mine, the web server's --
             the actual end-entity certificate)
```

The leaf is signed by the intermediate. The intermediate is signed by the root. The root signs itself. Technically, even this is a slight simplification -- nothing stops you from building longer chains with multiple intermediates, or more complex graphs via cross-certification. This is generally discouraged, though, because it gets complicated fast for limited benefit. In every normal case, end-entity certificates are leaf nodes in this small tree, which is exactly where the name "leaf certificate" comes from.

---

### Why You Have to Carry the Whole Folder

Since intermediates aren't in trust stores, they need to be distributed and verified just like leaf certificates -- you can't assume a relying party already has a copy sitting around. This is why, when you configure a subscriber such as a web server like nginx, Envoy, or Linkerd, you typically provide not just the leaf certificate but a certificate bundle including the necessary intermediate or intermediates.

With TLS, this bundle delivery happens automatically as part of the handshake that establishes a connection. When a subscriber sends its certificate to a relying party, it includes whatever intermediates are necessary to chain back up to a trusted root. The relying party then verifies the ENTIRE chain in a process called certificate path validation.

```
WHAT HAPPENS WHEN A SUBSCRIBER CONNECTS

  Subscriber sends:
    [leaf certificate] + [intermediate certificate(s)]

  Relying party already has, in its trust store:
    [root certificate]   (NOT sent over the wire -- pre-installed)

  Relying party performs CERTIFICATE PATH VALIDATION:
    1. Is the leaf signed by the intermediate?
    2. Is the intermediate signed by a root I already trust?
    3. Has anything in the chain expired?
    4. Has anything in the chain been revoked?
    5. Do certificate policies and key-use restrictions check out?

  If all checks pass: the connection proceeds.
```

The source material is emphatic about how much rides on this step: the complete path validation algorithm is genuinely complicated, covering expirations, revocation status, certificate policies, key-use restrictions, and more. Proper implementation of this algorithm by relying parties is, in its own words, absolutely critical. A relying party that skips or botches path validation has effectively thrown away most of the security PKI was supposed to provide, which is exactly why disabling certificate validation in a TLS client, even just for testing, is one of the most dangerous shortcuts in all of software engineering.

---

### Packaging the Folder: Order Matters, and Nobody Agrees

When certificate chains travel as files rather than over an active TLS handshake, PKCS#7 and PKCS#12 from Episode 5 sometimes get used because they can bundle a full chain. More often, in practice, chains are simply encoded as a sequence of line-separated PEM blocks concatenated together. The source material's honest warning here: some tools expect the certificates ordered leaf-to-root, others expect root-to-leaf, and some genuinely don't care. There is no universal convention. Check your specific tool's documentation, every time, without assuming the last tool's ordering carries over.

---

### Building a Chain With step-ca

The step CLI exposes exactly this leaf-intermediate-root structure directly:

```bash
# Create a root certificate and private key (EC P-256 by default)
step certificate create "Example Root CA" \
  root_ca.crt root_ca_key --profile root-ca

# Create an intermediate, signed BY the root
step certificate create "Example Intermediate CA" \
  intermediate_ca.crt intermediate_ca_key \
  --ca root_ca.crt --ca-key root_ca_key

# Create a leaf certificate, signed BY the intermediate
step certificate create svc.example.com \
  svc.crt svc.key \
  --ca intermediate_ca.crt --ca-key intermediate_ca_key
```

Inspecting the resulting leaf shows the Issuer field pointing at the intermediate, never the root directly -- the structural proof that the chain we just described is exactly what got built.

---

### What's Next: Choosing What Name Goes on the Cover

We've spent two episodes on signatures and chains without dwelling on the most basic decision of all: what name actually goes inside the certificate, and where. Episode 9 covers Subject Alternative Names, the modern, correct answer to how you name the thing a certificate identifies.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- Deploy an Intermediate CA with an Existing Root: smallstep.com/docs/tutorials/intermediate-ca-new-ca
- step certificate create reference: smallstep.com/docs/step-cli/reference/certificate/create

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

