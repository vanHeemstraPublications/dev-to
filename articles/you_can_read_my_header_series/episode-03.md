---
title: "You can read my Header 🎫 Ep.3"
series: "You can read my Header"
part: 3
organization: "the-software-s-journey"
tags: [http, headers, authorization, jwt, bearer-token]
---

## Episode 3: The Sealed Trip Voucher: Bearer Tokens and JWTs

Some fares don't pay cash. They hand me a voucher instead — company account, pre-approved, already stamped by somebody upstream who's vouching for the whole ride before I ever ask a question. I don't call the company to check every time. I just read the voucher. If the seal's intact and it hasn't expired, that's good enough for me to pull away from the curb.

That's the `Authorization` header, and the most common voucher riding inside it these days is a Bearer token — specifically, a JSON Web Token, a JWT. You'll see it sitting right there in the request, plain as day:

```
GET /account/receipts HTTP/1.1
Host: dispatch.citycab.example
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJUcmF2aXMiLCJpYXQiOjE3MjAwMDAwMDAsImV4cCI6MTcyMDAwMzYwMH0.dGhpc19pc19hX2Zha2Vfc2lnbmF0dXJl
```

Three dot-separated parts, and if you know how to unfold a voucher, none of it's a secret — a JWT's header and payload are just base64url, not encrypted, meant to be read by anyone who picks it up:

```python
import base64, json

def decode_jwt_part(part: str) -> dict:
    padded = part + "=" * (-len(part) % 4)
    return json.loads(base64.urlsafe_b64decode(padded))

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJUcmF2aXMiLCJpYXQiOjE3MjAwMDAwMDAsImV4cCI6MTcyMDAwMzYwMH0.dGhpc19pc19hX2Zha2Vfc2lnbmF0dXJl"
header_b64, payload_b64, signature_b64 = token.split(".")

print(decode_jwt_part(header_b64))   # {'alg': 'HS256', 'typ': 'JWT'}
print(decode_jwt_part(payload_b64))  # {'sub': 'Travis', 'iat': 1720000000, 'exp': 1720003600}
```

Fold that voucher back open and you get the claims — `sub`, the passenger's own name printed on the voucher; `iat`, when it was issued; `exp`, when it stops being good for a ride. What you *can't* fake, not without getting caught, is the third part: the signature. That's the seal, produced by whoever issued the voucher using a secret or a private key I trust, and it's the one part of the voucher that isn't just plain text sitting there for anyone to edit. Change one character of the `sub` claim to give yourself somebody else's name, and the signature no longer matches — the seal's broken, and any server checking it properly will toss the voucher straight back at you.

This is exactly the same trust logic from an earlier trip through this city — the sponsor letters we talked about in the External Account Binding series were doing the identical job at account-registration time, just with a different-shaped envelope. A JWT does it per-ride, every single request, riding along in one header line, checked fresh every time the cab pulls up.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Token issuer (auth server) | A verified user identity and a signing key | Encode claims (`sub`, `iat`, `exp`, and others) into a signed JWT | A portable, tamper-evident credential | The client that will present it on future requests |
| Client | The issued JWT | Attach it as `Authorization: Bearer <token>` on each request | An authenticated request, no separate login needed per call | The API server receiving the request |
| API server | An incoming Bearer token | Verify the signature and check `exp`/claims before trusting it | Either an authorized response or a rejection | The requesting client |

Next stop: the medallion plate the city itself issues before you're even allowed to pick up a fare — WWW-Authenticate, and how it ties back to External Account Binding.
