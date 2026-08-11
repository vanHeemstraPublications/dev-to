---
title: "You can read my Header 🪧 Ep.4"
series: "You can read my Header"
part: 4
organization: "the-software-s-journey"
tags: [http, headers, www-authenticate, 401, eab]
---

## Episode 4: The Medallion Check: WWW-Authenticate

You don't just decide to pick up fares in this city. Somebody official has to say you're allowed — a medallion, a number bolted to the hood, a piece of paper the Taxi and Limousine Commission signed off on before you ever turned the key. Show up without one, and it doesn't matter how good your voucher looks. The dispatcher turns you away and tells you exactly what you're missing.

That's what the `WWW-Authenticate` header does. It doesn't show up on a request — it shows up on a *rejection*, riding along with a `401 Unauthorized`, and it's the server's way of saying "not so fast, and here's precisely what I need before I'll let you back in":

```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="dispatch.citycab.example", error="invalid_token", error_description="The access token expired"
```

Notice it doesn't just say no. It names the scheme (`Bearer`), the realm you're trying to enter, and exactly what went wrong — an expired token, in this case, not a forged one, not a missing one. That specificity is the whole point: a client reading this response knows exactly what to fix, the way a driver turned away at the garage knows exactly which paperwork to go get before coming back.

This is where the medallion and the sponsor letter turn out to be the same idea wearing different uniforms. Remember External Account Binding from a few trips back — the `KEY_ID` and `HMAC_KEY` a sponsor hands you before an ACME CA will even register your account? That's the medallion office, checked once, at registration time, before you're allowed onto the road at all. `WWW-Authenticate` is the beat cop checking your medallion every time you roll up somewhere new — not re-issuing it, just confirming it's still valid, and telling you plainly if it isn't:

```bash
curl -i https://dispatch.citycab.example/account/receipts
# HTTP/1.1 401 Unauthorized
# WWW-Authenticate: Bearer realm="dispatch.citycab.example"

curl -i https://dispatch.citycab.example/account/receipts \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
# HTTP/1.1 200 OK
```

First call, no voucher shown, no medallion visible — the server tells you exactly what scheme it wants (`Bearer`) and where (`realm`). Second call, voucher presented, and you're through. One header, doing the job of a very polite bouncer who always tells you exactly why you're not on the list yet.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| API server | An unauthenticated or improperly authenticated request | Reject with `401` and specify the required scheme via `WWW-Authenticate` | A precise, actionable rejection | The client, now knowing exactly what credential to supply |
| EAB-issued sponsor credentials (from account registration) | A `KEY_ID`/`HMAC_KEY` bound once at account setup | Establish the underlying account's trustworthiness | An account capable of obtaining Bearer tokens later | The token-issuing auth server |
| Client | The `WWW-Authenticate` header's stated scheme and realm | Retry the request with the correct `Authorization` header | A successful, authenticated request | The API server, now willing to respond |

Next stop: the chalk mark left on a returning fare's sleeve — Cookies, and how a server remembers you between rides.
