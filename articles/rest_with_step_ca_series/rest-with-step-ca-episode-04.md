---
title: "REST with step-ca 🔐 Ep.4"
published: false
description: "Episode 4: The JWT one-time token is the authentication mechanism for step-ca's JWK provisioner. This episode dissects the three-step token factory: fetching the JWE-encrypted provisioner key from the CA, decrypting it with the provisioner password, and signing a short-lived JWT that authorises a specific certificate request. Architecture diagrams show every transformation from encrypted blob to signed token."
tags: [python, jwt, security, certificates]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/rest-with-step-ca-episode-04.png"
series: "REST with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 4
---

## Episode 4: The Token Factory — JWK, JWE, and JWT

---

## Three Standards, One Authentication

The JWK provisioner authentication chain uses three JOSE (JSON Object Signing and Encryption) standards:

- **JWK** (JSON Web Key, RFC 7517): the format used to represent cryptographic keys as JSON objects
- **JWE** (JSON Web Encryption, RFC 7516): the format used to encrypt the JWK private key at rest inside step-ca
- **JWT** (JSON Web Token, RFC 7519): the signed token we produce to authorise a certificate signing request

The flow is: fetch JWE → decrypt to JWK → sign JWT with JWK private key → present JWT as `ott` in the sign request.

---

## 🗂️ SIPOC — The Token Factory

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| step-ca `/provisioners/{kid}/encrypted-key` | HTTPS GET (verified) | Returns the JWE compact serialisation of the provisioner's private key | A JWE string: `eyJhbGci...` | `_decrypt_provisioner_key()` |
| `jwcrypto.jwe` | JWE string + provisioner password | PBES2-HS256+A128KW decryption → returns raw JWK JSON bytes | A Python dict with the EC private key (`kty`, `crv`, `x`, `y`, `d`) | `_create_token()` |
| `python-jose` | JWK dict, JWT claims dict | Sign JWT with ES256 algorithm | A compact JWT string (`eyJ...header.payload.signature`) | `POST /1.0/sign` as the `ott` field |

---

## The Token Factory Architecture

```
TOKEN FACTORY FLOW
══════════════════════════════════════════════════════════════════════

  step-ca                        StepCAClient                 /1.0/sign
  ────────                       ────────────                 ─────────

  Provisioner config in ca.json:
  {
    "kid": "udaECquW2dYw",
    "encryptedKey": "eyJhbGciOi..."   ← JWE compact
  }
         │
         │  GET /provisioners/{kid}/encrypted-key
         │◄─────────────────────────────────────────
         │
         │  {"key": "eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLC..."}
         │──────────────────────────────────────────►
         │                            │
         │                            │  STEP 1: JWE DECRYPTION
         │                            │  ─────────────────────
         │                            │  Algorithm: PBES2-HS256+A128KW
         │                            │  Password: "provisioner-secret"
         │                            │
         │                            │  JWE → JWK JSON:
         │                            │  {
         │                            │    "use":"sig",
         │                            │    "kty":"EC",
         │                            │    "kid":"udaECquW2dYw",
         │                            │    "crv":"P-256",
         │                            │    "alg":"ES256",
         │                            │    "x":"Pn_JEpI...",
         │                            │    "y":"_x7Jjfw...",
         │                            │    "d":"u1_OZH1X..."  ← private!
         │                            │  }
         │                            │
         │                            │  STEP 2: JWT CONSTRUCTION
         │                            │  ──────────────────────
         │                            │  Header:
         │                            │  { "alg":"ES256",
         │                            │    "kid":"udaECquW2dYw" }
         │                            │
         │                            │  Claims (payload):
         │                            │  {
         │                            │    "sub": "myservice.internal",
         │                            │    "iss": "admin@example.com",
         │                            │    "aud": "https://ca:9000/1.0/sign",
         │                            │    "iat": 1720000000,
         │                            │    "exp": 1720000300,  (5 min)
         │                            │    "jti": "abc-uuid-123",
         │                            │    "sans":["myservice.internal"]
         │                            │  }
         │                            │
         │                            │  STEP 3: ES256 SIGNATURE
         │                            │  ────────────────────────
         │                            │  Sign(private_key, header+"."+payload)
         │                            │  → "eyJhbGci...header.claims.sig"
         │                            │
         │                            │  POST /1.0/sign
         │                            │  { "csr": "-----BEGIN CERT REQ...",
         │                            │    "ott": "eyJhbGci...signed_jwt" }
         │                            │──────────────────────────────────►
```

---

## The JWE Compact Serialisation

The `encryptedKey` field in the CA's provisioner config is a JWE Compact Serialisation — five Base64url-encoded segments separated by dots:

```
eyJhbGci...  .  eyJ...  .  Wm9...  .  abc...  .  XYZ...
     │              │          │          │          │
  Protected      Encrypted   Init      Cipher    Auth
  Header         CEK         Vector    Text      Tag
  (algorithm,    (Content    (IV for   (the      (integrity
   enc params)   Encryption  AES)      payload)   check)
                 Key,
                 wrapped
                 with PBES2)
```

For step-ca's JWK provisioner, the algorithm is typically:
- `alg: PBES2-HS256+A128KW` — Password-Based Encryption with SHA-256 and AES-128 key wrap
- `enc: A128CBC-HS256` — AES-128-CBC with HMAC-SHA-256 authenticated encryption

The password you provided when adding the provisioner derives the key encryption key via PBKDF2.

---

## The JWT Claims Anatomy

```
JWT CLAIMS REQUIRED BY step-ca JWK PROVISIONER
═══════════════════════════════════════════════════════════

Claim   Type     Required  Description
──────  ───────  ────────  ──────────────────────────────────
sub     string   YES       Subject being certificated
                           Must match the CN in the CSR
                           e.g. "myservice.internal"

iss     string   YES       Issuer = provisioner name
                           Must match a configured provisioner
                           e.g. "admin@example.com"

aud     string   YES       Audience = full URL of the CA endpoint
                           Must match: https://<ca_url>/1.0/sign
                           (including /1.0/sign path!)

iat     integer  YES       Issued At = Unix timestamp (now)
                           CA rejects tokens issued in the future

exp     integer  YES       Expiry = Unix timestamp (now + 5 min)
                           step-ca default: max 5 min validity
                           Token is single-use regardless

jti     string   YES       JWT ID = unique UUID per token
                           CA records it; cannot be reused
                           (prevents replay attacks)

sans    array    YES       Subject Alternative Names the cert should have
                           Must match SANs in CSR
                           e.g. ["myservice.internal", "10.0.0.42"]
```

---

## Adding the Token Factory to StepCAClient

```python
# step_ca_client.py  (additions — Token Factory)

import uuid
import time
import json as json_module
from jose import jwt as jose_jwt
from jwcrypto import jwe as jwecrypto_jwe, jwk as jwecrypto_jwk


class StepCAClient:
    # ... (existing methods from Episodes 2 & 3)

    # ── Token factory internals ───────────────────────────────────────────

    def _get_encrypted_key(self, kid: str) -> str:
        """
        GET /provisioners/{kid}/encrypted-key
        Returns the JWE-encrypted private key for the provisioner.
        """
        response = self._session.get(
            f"{self.ca_url}/provisioners/{kid}/encrypted-key"
        )
        self._raise_for_status(response)
        return response.json()["key"]

    def _decrypt_provisioner_key(self, kid: str) -> dict:
        """
        Fetch and decrypt the provisioner's JWK private key.

        1. GET /provisioners/{kid}/encrypted-key
        2. Decrypt JWE using provisioner_password
        3. Return the JWK private key as a dict

        The JWK dict contains the "d" field (private scalar for EC),
        which is used to sign JWT tokens.

        Returns:
            dict with keys: kty, crv, alg, kid, x, y, d (for EC)
        """
        encrypted_key_jwe = self._get_encrypted_key(kid)

        # Decrypt using jwcrypto
        password_key = jwecrypto_jwk.JWK(
            kty = "oct",
            k   = self._b64_encode_password(self.provisioner_password),
        )

        token = jwecrypto_jwe.JWE()
        token.deserialize(encrypted_key_jwe, key=password_key)
        decrypted_bytes = token.payload

        jwk_dict = json_module.loads(decrypted_bytes)
        logger.debug(
            "Decrypted JWK for kid=%s (kty=%s, alg=%s)",
            jwk_dict.get("kid"), jwk_dict.get("kty"), jwk_dict.get("alg")
        )
        return jwk_dict

    @staticmethod
    def _b64_encode_password(password: str) -> str:
        """Encode the provisioner password as Base64URL (as jwcrypto expects)."""
        import base64
        return base64.urlsafe_b64encode(password.encode()).rstrip(b"=").decode()

    def _create_token(
        self,
        common_name: str,
        sans:        list[str],
        provisioner: "Provisioner",
        *,
        duration_seconds: int = 300,  # 5 minutes — step-ca default max
    ) -> str:
        """
        Create and sign a one-time JWT token for the sign endpoint.

        The token (called "ott" in the step-ca API) authorises step-ca
        to sign a CSR for the specified subject and SANs.

        Args:
            common_name:      The CN / subject — must match the CSR
            sans:             The SANs list — must match the CSR
            provisioner:      The Provisioner object (provides kid, name)
            duration_seconds: Token validity in seconds (max 300 by default)

        Returns:
            A compact JWT string ("eyJhbGci...header.payload.signature")
        """
        now        = int(time.time())
        token_id   = str(uuid.uuid4())
        audience   = f"{self.ca_url}/1.0/sign"

        claims = {
            "sub":  common_name,
            "iss":  provisioner.name,          # provisioner name as issuer
            "aud":  audience,
            "iat":  now,
            "exp":  now + duration_seconds,
            "jti":  token_id,                  # unique — prevents replay
            "sans": sans,                      # must match the CSR SANs
        }

        # Decrypt the provisioner's private JWK
        jwk_private = self._decrypt_provisioner_key(provisioner.kid)

        # Sign using python-jose
        # The JWK dict format is accepted directly by python-jose
        token = jose_jwt.encode(
            claims    = claims,
            key       = jwk_private,
            algorithm = jwk_private.get("alg", "ES256"),
            headers   = {"kid": provisioner.kid},
        )

        logger.debug(
            "Created OTT for sub=%s jti=%s exp=%s",
            common_name, token_id, now + duration_seconds
        )
        return token

    def _decode_token_payload(self, token: str) -> dict:
        """
        Decode a JWT payload WITHOUT verifying the signature.
        Useful for debugging — never use for security decisions.
        """
        import base64
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Not a valid JWT")
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return json_module.loads(base64.urlsafe_b64decode(padded))
```

---

## Exercising the Token Factory in Isolation

```python
# demo_token.py

from step_ca_client import StepCAClient

ca = StepCAClient(
    ca_url               = "https://localhost:9000",
    root_fingerprint     = "702a094e...",
    provisioner_name     = "admin@example.com",
    provisioner_password = "provisioner-secret",
)

# Get the provisioner
prov = ca.get_provisioner()
print(f"Provisioner: {prov.name}  kid={prov.kid}")

# Create a token
token = ca._create_token(
    common_name = "myservice.internal",
    sans        = ["myservice.internal", "10.0.0.42"],
    provisioner = prov,
)

# Decode and inspect the payload (do not use for auth decisions!)
payload = ca._decode_token_payload(token)
import json
print("\nJWT Payload:")
print(json.dumps(payload, indent=2))
# {
#   "sub":  "myservice.internal",
#   "iss":  "admin@example.com",
#   "aud":  "https://localhost:9000/1.0/sign",
#   "iat":  1720000000,
#   "exp":  1720000300,
#   "jti":  "a3b4c5d6-e7f8-...",
#   "sans": ["myservice.internal", "10.0.0.42"]
# }

print(f"\nToken valid for {payload['exp'] - payload['iat']} seconds")
print(f"jti (unique):   {payload['jti']}")
print(f"Single-use:     step-ca records jti and rejects reuse")
```

---

## Security Properties of the Token

```
SECURITY PROPERTIES OF THE OTT (ONE-TIME TOKEN)
═══════════════════════════════════════════════════

Property            How It Is Enforced
────────────────    ────────────────────────────────────────────────
Single-use          step-ca records the jti. A second request with
                    the same jti is rejected with 401.

Short-lived         exp = iat + 300 seconds (5 minutes maximum).
                    step-ca rejects tokens with exp in the past.

Bound to issuer     iss must match a known provisioner name.
                    Unknown issuers are rejected.

Bound to audience   aud must contain the exact CA sign endpoint URL.
                    Wrong audience → rejected.

Cryptographically   The token is signed with the provisioner's EC key.
authenticated       step-ca verifies with the provisioner's public key
                    (from ca.json). A forged token cannot be signed.

Subject binding     sub in the JWT must match the CN in the CSR.
                    SAN binding: jwt.sans must cover csr.sans.
                    Mismatches → rejected.
```

The token cannot be reused (jti tracking), cannot be extended (exp), cannot be forged (EC signature), and cannot authorise a different certificate than specified (sub/sans binding). This makes the JWK provisioner safe for custom integrations even though the private key is stored outside the CA.

---

## What's Next: Sign Here

In **Episode 5**, we assemble the sign call: `create_key_and_csr()` from Episode 3 + `_create_token()` from this episode → `POST /1.0/sign` → parse the `certChain` response → return `(cert_pem, key_pem)`. The first real certificate leaves the factory.

---

**🔗 Resources**
- **RFC 7519 — JSON Web Tokens**: [rfc-editor.org/rfc/rfc7519](https://www.rfc-editor.org/rfc/rfc7519)
- **RFC 7516 — JWE**: [rfc-editor.org/rfc/rfc7516](https://www.rfc-editor.org/rfc/rfc7516)
- **python-jose**: [github.com/mpdavis/python-jose](https://github.com/mpdavis/python-jose)
- **jwcrypto**: [github.com/latchset/jwcrypto](https://github.com/latchset/jwcrypto)

---

*🔐 REST with step-ca — automating certificate lifecycle one HTTP call at a time.*
