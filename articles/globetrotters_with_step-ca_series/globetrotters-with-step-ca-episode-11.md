---
title: "Globetrotters with step-ca 🛄 Ep. 11"
published: false
description: "Episode 11: Getting a passport, or a certificate, is a two-part deal: you have to prove who you say you are, and someone trustworthy has to sign off on it. This episode covers certificate signing requests, the spectrum of identity proofing from domain validation to your own internal rules, and the practical mechanics of renewing a certificate with step-ca before it expires."
tags: [security, pki, stepca, automation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters-with-step-ca-episode-11.png"
series: "Globetrotters with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 11
---

## Episode 11: Applying at the Embassy

You do not get a passport simply by asking nicely. You fill in a form, you provide a photo that is unmistakably your own face, and the issuing office does some amount of work to confirm you actually are who you claim to be before they staple their seal onto your document. Certificates follow the identical two-part ceremony: submit a request, prove your identity, receive a signed document.

---

### SIPOC for Requesting and Renewing a Certificate

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| A subscriber | A name from Episode 9, a freshly generated key pair from Episode 10 | Build and sign a Certificate Signing Request with the private key | A CSR, ready to submit to a CA | The CA, which still needs to verify the requester's identity |
| The CA's identity-proofing process | The CSR, plus whatever authentication mechanism the CA requires | Confirm the requester actually controls the name being claimed | A decision: issue, or refuse | The subscriber, who either gets a certificate or does not |
| Automated renewal via step ca renew | An existing, still-valid client certificate | Authenticate via mutual TLS, request a fresh certificate before expiry | A renewed certificate with a fresh validity window | The subscriber's own runtime, which keeps working without manual intervention |

---

### The CSR: Filling In the Application Form

Once a subscriber has a name and a key pair, the next step toward obtaining a leaf certificate is generating a Certificate Signing Request, or CSR. A CSR bundles the requested name and public key together, signed by the corresponding private key, proving right from the start that the requester genuinely controls that key, the same property signatures gave us back in Episode 2.

```bash
step certificate create --csr foo.example.com foo.csr foo.key
```

```
Please enter the password to encrypt the private key:
Your certificate signing request has been saved in foo.csr.
Your private key has been saved in foo.key.
```

If you already have a CSR and just need it signed:

```bash
step ca sign foo.csr foo.crt
```

```
Provisioner: carl@smallstep.com (JWK) [kid: yWa7WGfoSt9yJ0OZCndrvR_m65jzDriY7mhPz094fdw]
Please enter the password to decrypt the provisioner key: ...
CA: https://127.0.0.1:4337
Certificate: foo.crt
```

---

### Provisioners as the Embassy Staff Checking Your Documents

A CA receiving a CSR has signature verification covered already, since Episode 2's properties handle that automatically, but it still faces a harder question: is the name being requested actually the correct name for this requester? step-ca answers this through provisioners, the embassy staff at the front desk whose entire job is verifying identity before any document gets signed.

Several provisioner types accept a JSON Web Token alongside the CSR to authenticate the request:

```
JWK PROVISIONER
  Accepts JWTs signed using a JavaScript Web Key whose public
  key is already configured in the CA. Good for custom
  integrations, easy to generate programmatically.

OIDC PROVISIONER
  Accepts JWTs signed by an identity provider via a normal
  single sign-on flow. Good for issuing certificates to humans.

X5C PROVISIONER
  Accepts JWTs signed using an existing X.509 certificate's
  private key, where that certificate's root is configured in
  the CA. Lets you bootstrap trust from a different existing PKI.
```

A typical JWK-provisioner flow, separated into its component steps:

```bash
TOKEN=$(step ca token localhost)
```

```
Provisioner: carl@smallstep.com (JWK) [kid: kvPj79hrAnrQywrVy-oFmye4foHq1rdUg55nxsuCvkI]
Please enter the password to decrypt the provisioner key:
```

Inspecting that token reveals exactly what is being claimed and for how long:

```bash
echo $TOKEN | step crypto jwt inspect --insecure
```

```json
{
  "header": { "alg": "ES256", "kid": "kvPj79hrAnrQywrVy-oFmye4foHq1rdUg55nxsuCvkI", "typ": "JWT" },
  "payload": {
    "aud": "https://localhost:8443/1.0/sign",
    "exp": 1634667515,
    "iat": 1634667215,
    "iss": "carl@smallstep.com",
    "jti": "ffa63c06b0f3ccb0de554711836042a877e32a0322df42d617c6da59af65ec7d",
    "nbf": 1634667215,
    "sans": ["localhost"],
    "sub": "localhost"
  },
  "signature": "g8S-1Mrb9U3l3CbTRE-Mvcy2m2I-M2b_9KXj04SnqSxyMVDRzvnpoW3XYtlGgCcIexo5gQpOpe0QrkdZuKwhUQ"
}
```

That token expires in five minutes. The CSR and the token can be generated separately, in different contexts, which is useful if you want to generate a CA token on a host and inject it into a Docker container, so the container can build its own private key and request a certificate without ever holding any long-lived CA credentials itself.

---

### Identity Proofing and How Much You Actually Trust This Claim

Once a CA has a verified CSR, it still has to decide whether the name inside is legitimately the requester's to claim. For Web PKI, there are three tiers, distinguished mainly by how rigorously identity gets proofed:

```
DOMAIN VALIDATION (DV)
  Binds a DNS name, issued based on proof of control over that
  domain. Typically a simple ceremony: confirmation email sent
  to the administrative contact on file in WHOIS records.

ORGANIZATION VALIDATION (OV)
  Adds verification of the requesting organization's identity.

EXTENDED VALIDATION (EV)
  The most rigorous tier, with the most thorough vetting.
```

The source material is candid about what DV actually proves, which is less than it sounds like: it is supposed to prove the requester owns the relevant domain. What it actually proves is that, at some point, the requester was able to read an email, configure DNS, or serve a secret over HTTP. The underlying security of DNS, email, and BGP that these processes lean on is not great, and there have been real attacks against this infrastructure aimed specifically at obtaining fraudulent certificates.

For internal PKI, you are freed from this constraint entirely: you can use any identity-proofing process you want, and you can very plausibly do better than DV's reliance on DNS or email. The trick is leveraging infrastructure you already trust: whatever you use to provision your services in the first place should also be able to measure and attest to the identity of whatever is being provisioned, such as a cloud instance identity document, a Kubernetes service account token, or an existing corporate SSO session. This is not actually hard once you frame it this way, it is just unfamiliar the first time.

---

### Renewal and Not Waiting Until the Embassy Closes

Certificates expire, by design, and Episode 12 explains exactly why this is a feature. When it comes time to renew, do not dawdle: once a certificate has actually expired, step-ca will not renew it. You will need to replace it entirely instead, via the full issuance process. To avoid this, set up automated renewal for any certificate that always needs to stay valid.

```bash
step ca renew svc.crt svc.key
```

step-ca's automation tooling targets renewal at roughly two-thirds of a certificate's total lifetime, not the very end of its window, leaving comfortable margin for retries if something goes briefly wrong.

```
RENEWAL TIMING, ILLUSTRATED

  Certificate issued at:  hour 0
  Certificate expires at: hour 24
  Automated renewal fires at: hour 16 (two-thirds of the way)

  This leaves a third of the certificate's life as a safety
  margin, room to retry if the CA is briefly unreachable,
  without ever brushing up against actual expiry.
```

One important mechanical limitation: because step ca renew authenticates using mutual TLS, it can only renew client certificates, ones marked with the Client Authentication key usage. Anything else has to be replaced before expiry through the full issuance flow instead.

Default lifetimes are deliberately short, and deliberately adjustable: the 24-hour default TLS certificate lifetime is, in the source material's own words, rather arbitrary. Depending on your threat model, you will often want something different:

```
SERVER AND SERVICE ACCOUNT CERTIFICATES
  Typically longer-lived: 1 to 90 days

CLIENT CERTIFICATES FOR HUMANS
  Typically shorter-lived: a few minutes up to a month
```

The general principle, stated plainly: a shorter validity period limits the downside risk if a private key is ever stolen. And since every certificate needs renewing eventually anyway, you may as well automate that process thoroughly and renew often. Episode 12 picks this exact thread up and runs with it all the way to revocation.

---

### What's Next: Letting Old Passports Quietly Expire

We have covered how to get a certificate. The final piece of the lifecycle is what happens when one needs to stop being valid before its time, or, in the increasingly common case, simply by aging out gracefully on its own. Episode 12, the close of this series, covers active versus passive revocation, and the summary that ties the entire journey together.

---

**Resources**
- Everything you should know about certificates and PKI but are too afraid to ask: smallstep.com/blog/everything-pki
- Basic Certificate Authority Operations: smallstep.com/docs/step-ca/basic-certificate-authority-operations
- step-ca Provisioners documentation: smallstep.com/docs/step-ca/provisioners

---

*Globetrotters with step-ca, every certificate is a passport, every CA is a passport office, and every relying party is a border officer doing their job in milliseconds.*

