---
title: "Globetrotters go EAB ✉️ Ep.2"
series: "Globetrotters go EAB"
part: 2
organization: "the-software-s-journey"
tags: [acme, eab, rfc8555, jws, cryptography]
---

## Episode 2: The Sponsor Letter: Key ID and HMAC Explained

Every proper sponsor letter has two things on it: a reference number identifying exactly which sponsor is vouching for you, and an unforgeable seal proving the letter really came from them. In ACME's External Account Binding, per RFC 8555 §7.3.4, those two things are the **Key ID** and the **HMAC key** — and in `idem-certbot`'s world, they travel under the refreshingly plain names `KEY_ID` and `HMAC_KEY`.

The Key ID is boring and public — your sponsor's membership number, printed right there for anyone to read. The HMAC key is the interesting bit: a shared secret, known only to you and the CA, used to *sign* your account-registration request. Your ACME account request ends up wrapped in two signatures, nested like a passport inside a diplomatic pouch:

```json
{
  "protected": "<base64url outer JWS header: alg=HS256, kid=KEY_ID, url=.../new-account>",
  "payload": "<base64url inner JWS: your account's own public key, signed by your account's own private key>",
  "signature": "<HMAC-SHA256 over protected+payload, using HMAC_KEY>"
}
```

The inner JWS proves "this is genuinely my account key." The outer HMAC proves "and my sponsor, identified by this Key ID, vouches for me." Certbot builds this double-signed envelope for you the moment you hand it two flags:

```bash
certbot register \
  --server "$SERVER_URL" \
  --eab-kid "$KEY_ID" \
  --eab-hmac-key "$HMAC_KEY" \
  --email "$EMAIL_ADMIN" \
  --non-interactive \
  --agree-tos
```

That's the exact shape of the command `idem-certbot`'s own startup script runs — we'll see it verbatim in Episode 5. Two flags, one nested JWS built entirely under the hood, and a freshly EAB-bound ACME account comes back from the CA. Everything the rest of `idem-certbot` does is really just "run that reliably, on a schedule, without a human at the keyboard."

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| EAB-gated CA | A sponsorship agreement with an organization (e.g. GARR) | Issue a Key ID and HMAC key pair for that sponsor's members | A usable "sponsor letter" (`KEY_ID` + `HMAC_KEY`) | The sponsored globetrotter about to register an ACME account |
| Certbot | `--eab-kid` and `--eab-hmac-key` flags | Construct the nested inner/outer JWS per RFC 8555 §7.3.4 | A correctly double-signed `newAccount` request | The target CA's ACME server |
| ACME server | The double-signed request | Verify the account-key signature, then the HMAC against the claimed `kid` | An EAB-bound ACME account, or a rejection | Certbot, and the certificate-issuance flow that follows |

Next stop: packing the actual suitcase — the real Dockerfile and startup script that make `idem-certbot` tick.
