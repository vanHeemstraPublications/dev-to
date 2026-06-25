---
title: "Globetrotters with step-ca 🛃 Ep.7"
published: false
description: "Episode 7: Every border officer carries, in effect, a little black book listing every passport office they trust without question. This episode covers trust stores -- where they live, who maintains them, the self-signed signature at the very bottom of every chain, and how to actually bootstrap one with step-ca."
tags: [security, pki, trust, stepca]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-07.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 7
---

## Episode 7: The Border Officer's Little Black Book

We glossed over something important back in Episode 4. We said a relying party can verify a certificate's signature if they know the issuer's public key. Fine -- but how, exactly, does the relying party come to know that public key in the first place? Somebody had to tell them, at some point, to trust it.

The answer, as the source material puts it, is "simple, if not satisfying": relying parties are pre-configured with a list of trusted root certificates -- **trust anchors** -- kept in a **trust store**. It's the literal little black book a border officer keeps under the counter, listing every passport-issuing authority on Earth they've agreed, in advance, to take at their word.

---

### SIPOC -- Establishing Trust

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| Apple, Microsoft, Mozilla, and Google's root programs | Audits, policies, and applications from CAs wanting inclusion | Vet candidate root certificates against a published program policy | A curated list of trusted root certificates | Every browser, OS, and TLS-speaking program that ships with that trust store |
| A self-signed root certificate | A CA's own key pair | Sign a certificate where issuer and subject are the same entity | A root certificate -- the literal bottom of every trust chain | The trust store that decides whether to include it |
| step ca init | A chosen CA name, DNS names, a provisioner | Generate a root and intermediate key pair, sign the intermediate with the root | A working root fingerprint plus a ready-to-run CA | Every client that will ever need to bootstrap trust with this CA |

---

### Self-Signed Roots: The Bottom of Every Chain

Root certificates in trust stores are **self-signed**. The issuer and the subject are literally the same entity. Logically, it reads as a statement like: *"Mike says Mike's public key is blah blah blah."* The signature on a self-signed certificate proves the subject/issuer knows the corresponding private key -- but here's the catch worth sitting with: anyone can generate a self-signed certificate claiming ANY name they like.

```
SELF-SIGNED CERTIFICATES PROVE ONLY ONE THING

  "Whoever made this certificate knows the private key
   matching the public key inside it."

  They do NOT prove anything about whether the NAME inside
  is meaningful, honest, or worth trusting.

  PROVENANCE is everything. A self-signed certificate should
  only be trusted to the extent the PROCESS by which it
  entered your trust store is itself trustworthy.
```

This is why trust stores are managed carefully, not casually edited. On macOS, the trust store lives in the keychain. On many Linux distributions, it's simply files in `/etc` or elsewhere on disk. The source material's blunt warning here is worth repeating: if your users can modify these files, you'd better trust ALL your users, because anyone who can add a root certificate can make their own self-signed claims look exactly as legitimate as a real one.

---

### Who Actually Maintains the World's Trust Stores

For Web PKI, the most important relying parties are web browsers, and the trust stores those browsers (and nearly everything else using TLS) rely on by default are maintained by exactly four organizations:

```
APPLE'S ROOT CERTIFICATE PROGRAM
  Used by iOS and macOS

MICROSOFT'S ROOT CERTIFICATE PROGRAM
  Used by Windows

MOZILLA'S ROOT CERTIFICATE PROGRAM
  Used by Mozilla's own products -- and, because of its open
  and transparent process, used as the BASIS for many other
  trust stores too (many Linux distributions lean on it)

GOOGLE'S ROOT CERTIFICATE PROGRAM
  Used by Chrome, on every platform except iOS
```

Operating system trust stores typically ship pre-installed with the OS and get updated via regular software updates -- which, in a nice bit of recursion, are themselves usually code-signed using yet ANOTHER PKI. Firefox is the one notable exception among major browsers: it ships its own trust store, distributed using TLS from mozilla.org, which means it's bootstrapping off Web PKI using some OTHER already-trusted store. Programming languages and command-line tools like `curl` typically just defer to whatever the OS trust store says.

There are over 100 certificate authorities commonly included across these programs. You probably recognize the big names: Let's Encrypt, DigiCert, Entrust, and so on. Cloudflare's `cfssl` project maintains a public GitHub repository of trusted certificates pulled from various trust stores, useful if you ever want to inspect this landscape programmatically.

---

### The Chain of Trust Always Ends in Meatspace

Here's a detail from the source material worth sitting with for a moment, because it's genuinely a little philosophically satisfying: however you bootstrap trust, if you trace the chain far enough back, you always end up at PEOPLE. Maybe an automation tool used SSH to copy a root certificate onto a new machine -- but that SSH access was itself bootstrapped off some other PKI, which was bootstrapped off whatever authentication your cloud provider did when you handed them a credit card and created an account.

```
EVERY TRUST CHAIN, FOLLOWED FAR ENOUGH BACK

  Your service trusts a CA
       ↓ (bootstrapped via)
  SSH access copied a root cert
       ↓ (bootstrapped via)
  Your cloud provider's Web PKI + account creation
       ↓ (bootstrapped via)
  A human typing a credit card number into a form

  Every trust chain ends in meatspace.
```

---

### Bootstrapping Your Own Little Black Book With step-ca

This is where theory turns into a working CA. Initializing a new `step-ca` instance generates exactly the root/intermediate pair this episode has been describing:

```bash
step ca init
```

```
✔ What would you like to name your new PKI? (e.g. Smallstep): Example Inc.
✔ What DNS names or IP addresses would you like to add to your new CA? (e.g. ca.smallstep.com[,1.1.1.1,etc.]): localhost
✔ What address will your new CA listen at? (e.g. :443): 127.0.0.1:8443
✔ What would you like to name the first provisioner for your new CA? (e.g. you@smallstep.com): bob@example.com
✔ What do you want your password to be? [leave empty and we will generate one]: abc123

Generating root certificate... all done!
Generating intermediate certificate... all done!

✔ Root certificate: /Users/bob/.step/certs/root_ca.crt
✔ Root private key: /Users/bob/.step/secrets/root_ca_key
✔ Root fingerprint: 702a094e239c9eec6f0dcd0a5f65e595bf7ed6614012825c5fe3d1ae1b2fd6ee
✔ Intermediate certificate: /Users/bob/.step/certs/intermediate_ca.crt
✔ Intermediate private key: /Users/bob/.step/secrets/intermediate_ca_key
✔ Default configuration: /Users/bob/.step/config/defaults.json
✔ Certificate Authority configuration: /Users/bob/.step/config/ca.json

Your PKI is ready to go. Make a note of the root fingerprint!
You'll need it in future steps to establish trust with your
CA from other environments or hosts.
```

That **root fingerprint** is the modern, compact equivalent of a passport office publishing its master seal somewhere everyone can verify it against -- a short, copy-pasteable value you can use to bootstrap trust from any other host or environment without transmitting the entire root certificate insecurely.

Start the CA, pointing it at the configuration file just generated:

```bash
step-ca $(step path)/config/ca.json
```

```
Please enter the password to decrypt /Users/bob/.step/secrets/intermediate_ca_key: abc123
2019/02/18 13:28:58 Serving HTTPS on 127.0.0.1:8443
```

And from any client machine that needs to start trusting this CA, bootstrap using nothing more than the fingerprint and the CA's address:

```bash
step ca bootstrap --ca-url https://localhost:8443 --fingerprint 702a094e239c9eec6f0dcd0a5f65e595bf7ed6614012825c5fe3d1ae1b2fd6ee
```

This downloads the root certificate and writes the connection details locally, so the `step` command on that machine now genuinely trusts your CA. If you'd also like system-wide trust -- so tools like `curl` pick it up automatically -- install it into the OS trust store directly:

```bash
step certificate install $(step path)/certs/root_ca.crt
```

```
Certificate /home/alice/.step/certs/root_ca.crt has been installed.

X.509v3 Root CA Certificate (ECDSA P-256) [Serial: 2282...6360]
Subject: Example Inc. Root CA
Issuer: Example Inc. Root CA
Valid from: 2021-05-11T21:40:19Z
        to: 2031-05-09T21:40:19Z
```

Notice the Subject and Issuer fields are identical -- exactly the self-signed structure this episode opened with, now sitting on your own disk, under your own control.

---

### What's Next: The Folder of Stamps Back to the Homeland

We've established the root of trust. But step-ca deliberately never SIGNS your everyday certificates directly with that root -- it uses an intermediate instead, and the resulting chain has to be carried along and verified every single time. **Episode 8** covers certificate chains: why intermediates exist, why roots stay offline, and how a relying party actually walks the whole chain back to a trust anchor.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- Getting Started with step-ca: smallstep.com/docs/step-ca/getting-started
- Mozilla's root certificate policy: mozilla.org/en-US/about/governance/policies/security-group/certs

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

