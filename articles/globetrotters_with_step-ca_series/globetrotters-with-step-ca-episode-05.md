---
title: "Globetrotters with step-ca 📜 Ep.5"
published: false
description: "Episode 5: A passport's idea is simple. A passport's printing standard, watermark placement, and machine-readable zone are anything but. This episode covers X.509, ASN.1, OIDs, DER, PEM, and the PKCS envelope formats -- the genuinely annoying part of PKI, explained as honestly as the source material explains it: this stuff is dumb, and that's not your fault."
tags: [security, pki, x509, encoding]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-05.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 5
---

## The Paperwork Behind Every Passport

Every passport in the world follows the same idea -- a name, a photo, an issuing authority's seal. But the actual PRINTING of a passport is governed by an international standard most travelers have never heard of (ICAO Document 9303, since you asked), specifying everything from page layout to the machine-readable zone at the bottom to the exact placement of security threads.

Certificates have an almost identical split, and the source material is candid about which half is the hard part: "Let's look at how certificates are represented as bits and bytes. This part actually is annoyingly complicated... I suspect that the esoteric and poorly defined manner in which certificates and keys are encoded is the source of most confusion and frustration around PKI in general. This stuff is dumb. Sorry." We're going to walk through it anyway, because you will eventually need to recognize these formats by sight.

---

### SIPOC -- Encoding a Certificate

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| RFC 5280 (PKIX) | A certificate's logical content: name, key, signature, extensions | Define the structure using ASN.1 | An abstract, language-agnostic description of what a certificate contains | DER, the encoding rule that turns this abstraction into actual bytes |
| DER (Distinguished Encoding Rules) | An ASN.1-defined structure | Apply type-length-value binary encoding | Raw binary bytes -- a `.der` file | PEM, which wraps this binary for easier handling |
| PEM | DER bytes, a descriptive header label | Base64-encode the bytes, sandwich them between header and footer | A `-----BEGIN CERTIFICATE-----` block you can copy-paste | Humans, version control systems, and config files everywhere |

---

### X.509: Designed for a Phone Book, Not the Web

When people say "certificate" without qualification, they almost always mean an **X.509 v3 certificate** -- specifically the PKIX variant from RFC 5280, further refined by the CA/Browser Forum's Baseline Requirements. These are the certificates browsers understand for HTTPS.

Here's the history that explains a lot of X.509's weirdness: it was first standardized in 1988, as part of the broader X.500 project, under the ITU-T -- the International Telecommunications Union's standards body. X.500 was the telecom industry's attempt to build a **global telephone book**. That global phone book never actually happened, but the vestiges are baked permanently into every certificate you'll ever inspect.

```
WHY YOUR CERTIFICATE HAS A "LOCALITY" AND "COUNTRY" FIELD

  X.509 wasn't designed for the web.
  It was designed thirty years ago to build a phone book.

  That's why a certificate's Distinguished Name (DN) can include
  locality, state, organization, and country -- fields that make
  almost no sense for "is this the right website" but made
  perfect sense for "which Mike Malone, in which city, in which
  country, are we listing in this directory."
```

### ASN.1: The Notation Underneath

X.509 is built on **ASN.1** (Abstract Syntax Notation One), another ITU-T standard. Think of it as a notation for defining data types -- somewhat like JSON for X.509, though it's really closer in spirit to protobuf, Thrift, or SQL's data definition language. RFC 5280 uses ASN.1 to define an X.509 certificate as an object containing a name, a key, a signature, and various other fields.

ASN.1 has the usual data types -- integers, strings, sets, sequences -- plus one unusual one worth knowing by name: the **object identifier (OID)**. An OID is like a URI, but more annoying. It's a hierarchical sequence of integers meant to be a universally unique tag for a type of data.

```
A STRING IS JUST A STRING...

  "Bob"

...UNTIL YOU TAG IT WITH AN OID

  OID 2.5.4.3 + "Bob"  =  an X.509 COMMON NAME, specifically
```

OIDs are how a certificate's parser knows that one particular string is the subject's common name, another is the organization, and another is something else entirely -- all without any of them being labeled in plain English anywhere in the actual bytes.

### DER: Turning the Abstract Into Bytes

ASN.1 is deliberately *abstract* -- the standard says nothing about how data should actually be represented as bits and bytes. That's the job of **encoding rules**. There are several, but for X.509 and most crypto material, only one matters in practice: **DER**, Distinguished Encoding Rules (the related but non-canonical BER also turns up occasionally). DER is a fairly simple type-length-value binary encoding. You rarely need to hand-encode or hand-decode it yourself -- libraries handle the heavy lifting -- but you absolutely need to recognize WHEN you're looking at it versus something fancier.

---

### PEM: Making Binary Copy-Pasteable

DER is straight binary, and binary is miserable to copy-paste, email, or paste into a YAML file. So most certificates travel as **PEM** -- which, in one of the field's many small historical jokes, stands for *Privacy Enhanced Mail*, a 1990s email security standard whose only surviving legacy is this file format. PEM base64-encodes the DER payload and wraps it between a labeled header and footer, similar in spirit to MIME.

```
-----BEGIN CERTIFICATE-----
MIIBwzCCAWqgAwIBAgIRAIi5QRl9kz1wb+SUP20gB1kwCgYIKoZIzj0EAwIwGzEZ
MBcGA1UEAxMQTDVkIFRlc3QgUm9vdCBDQTAeFw0xODExMDYyMjA0MDNaFw0yODEx
MDMyMjA0MDNaMCMxITAfBgNVBAMTGEw1ZCBUZXN0IEludGVybWVkaWF0ZSBDQTBZ
MBMGByqGSM49AgEGCCqGSM49AwEHA0IABAST8h+JftPkPocZyuZ5CVuPUk3vUtgo
cgRbkYk7Ong7ey/fM5fJdRNdeW6SouV5h3nF9JvYKEXuoymSNjGbKomjgYYwgYMw
DgYDVR0PAQH/BAQDAgGmMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAS
BgNVHRMBAf8ECDAGAQH/AgEAMB0GA1UdDgQWBBRc+LHppFk8sflIpm/XKpbNMwx3
SDAfBgNVHSMEGDAWgBTirEpzC7/gexnnz7ozjWKd71lz5DAKBggqhkjOPQQDAgNH
ADBEAiAejDEfua7dud78lxWe9eYxYcM93mlUMFIzbWlOJzg+rgIgcdtU9wIKmn5q
FU3iOiRP5VyLNmrsQD3/ItjUN1f1ouY=
-----END CERTIFICATE-----
```

PEM-encoded certificates usually carry a `.pem`, `.crt`, or `.cer` extension. Raw DER usually carries `.der`. As the source material warns, consistency here is more aspiration than reality -- your mileage will vary.

---

### PKCS: When a "Certificate" Is Actually a Folder of Documents

Sometimes you'll be asked for "a certificate" when what's actually wanted is a certificate wrapped in a fancier envelope alongside other material -- think of it as the difference between handing someone your passport alone versus handing them a folder containing your passport, your visa, AND your travel insurance documents stapled together.

These envelope formats belong to a suite called **PKCS** (Public Key Cryptography Standards):

```
PKCS#7 (rebranded CMS -- Cryptographic Message Syntax)
  Can contain ONE OR MORE certificates -- a full chain.
  Commonly used by Java.
  Extensions: .p7b, .p7c

PKCS#12
  Can contain a certificate chain PLUS an (encrypted) private key.
  Commonly used by Microsoft products.
  Extensions: .pfx, .p12
```

Both are, unsurprisingly, also defined using ASN.1, and both CAN technically be PEM or BER encoded -- but in practice, you'll almost always encounter them as raw DER.

### Private Keys: The Same Story, One More Layer of Confusion

Key encoding follows the identical pattern: an ASN.1 structure describes the key, DER encodes it to bytes, and PEM (hopefully with a useful label) wraps it for human handling. Figuring out exactly what kind of key you're looking at is, in the source material's words, half art and half science.

```bash
step crypto keypair --kty EC --no-password --insecure ec.pub ec.prv
cat ec.pub ec.prv
```

```
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEc73/+JOESKlqWlhf0UzcRjEe7inF
uu2z1DWxr+2YRLfTaJOm9huerJCh71z5lugg+QVLZBedKGEff5jgTssXHg==
-----END PUBLIC KEY-----
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEICjpa3i7ICHSIqZPZfkJpcRim/EAmUtMFGJg6QjkMqDMoAoGCCqGSM49
AwEHoUQDQgAEc73/+JOESKlqWlhf0UzcRjEe7inFuu2z1DWxr+2YRLfTaJOm9hue
rJCh71z5lugg+QVLZBedKGEff5jgTssXHg==
-----END EC PRIVATE KEY-----
```

Elliptic curve keys usually carry an explicit label, though even that isn't fully standardized. Other keys are simply labeled "PRIVATE KEY" -- usually a sign you're looking at a **PKCS#8** payload, an envelope format for private keys that bundles in the key type and other metadata. And yes, those can be password-encrypted too, which is when you'll see `Proc-Type` and `DEK-Info` headers announcing the encryption algorithm in use (commonly `AES-256-CBC`).

```
-----BEGIN EC PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-256-CBC,b3fd6578bf18d12a76c98bda947c4ac9

qdV5u+wrywkbO0Ai8VUuwZO1cqhwsNaDQwTiYUwohvot7Vw851rW/43poPhH07So
sdLFVCKPd9v6F9n2dkdWCeeFlI4hfx+EwzXLuaRWg6aoYOj7ucJdkofyRyd4pEt+
Mj60xqLkaRtphh9HWKgaHsdBki68LQbObLOz4c6SyxI=
-----END EC PRIVATE KEY-----
```

If the payload itself is an encrypted PKCS#8 object, the header instead reads "ENCRYPTED PRIVATE KEY," with no `Proc-Type`/`DEK-Info` lines, because that information is folded into the payload instead.

```
THE WHOLE STACK, SUMMARIZED ONE MORE TIME

  ASN.1   defines the DATA TYPES (certificates, keys)
  DER     turns ASN.1 into actual BYTES
  X.509   is a certificate, DEFINED in ASN.1
  PKCS#7/#12  are BIGGER envelopes, also ASN.1, holding
              certificates plus other stuff
  PEM     wraps raw binary (DER) in base64 + labels, for
          humans and text-based tools

  Public keys: usually .pub or .pem
  Private keys: usually .prv, .key, or .pem
  Consistency: aspirational at best
```

If this is confusing, the source material's own closing line on the subject is worth repeating verbatim: it's not you. It's the world. I tried.

---

### What's Next: Public Roads Versus Private Estates

We now know what a certificate's "paperwork" looks like. The next question is where these documents actually get used, and why you might want a passport office of your own rather than relying on the one the world already trusts. **Episode 6** covers Web PKI versus Internal PKI.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- RFC 7468, Textual Encodings of PKIX, PKCS, and CMS Structures: tools.ietf.org/html/rfc7468
- RFC 5208, PKCS#8: tools.ietf.org/html/rfc5208

---

*Globetrotters with step-ca -- every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

