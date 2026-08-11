---
title: "You can read my Header 🩹 Ep.5"
series: "You can read my Header"
part: 5
organization: "the-software-s-journey"
tags: [http, headers, cookies, sessions, state]
---

## Episode 5: The Chalk Mark on a Returning Fare's Sleeve

Some nights the same fare gets in twice. Once around midnight, once again near closing time, and the second time, I already know their stop, already know they tip in cash, already know not to take the bridge because they mentioned last time they get carsick on it. I didn't memorize their whole life story. I just marked them — a little chalk tick I keep track of on my own side, so the next ride starts smarter than the last one ended.

That's a cookie. The server hands one out on a response, the client carries it back on every request after that, and neither side has to reintroduce themselves from scratch:

```
HTTP/1.1 200 OK
Set-Cookie: session_id=8f14e45f-ceea; HttpOnly; Secure; SameSite=Strict; Max-Age=3600
```

Read that line the way I'd read my own chalk marks. `session_id` is the tick itself — meaningless to anyone but the dispatcher who wrote it. `HttpOnly` means don't let some pickpocket script running in the passenger's own browser read this off their sleeve; only the server that wrote it gets to read it back. `Secure` means don't even whisper this mark out loud unless the whole conversation's happening over HTTPS. `SameSite=Strict` means don't honor this mark if it's some other garage's request trying to pass it off as theirs. `Max-Age=3600` means the chalk washes off in an hour whether anyone remembers to erase it or not.

On the next ride, the client just shows the mark back, no questions asked:

```
GET /account/receipts HTTP/1.1
Host: dispatch.citycab.example
Cookie: session_id=8f14e45f-ceea
```

And in code, this whole exchange is invisible if you let your HTTP client handle it for you — which, for a browser, it always does automatically:

```python
import requests

session = requests.Session()  # keeps cookies between calls, like a driver who remembers a fare

session.post("https://dispatch.citycab.example/login", data={"user": "travis", "pass": "..."})
# Set-Cookie arrives, gets stored in `session`

resp = session.get("https://dispatch.citycab.example/account/receipts")
# Cookie gets sent back automatically — no manual chalk-checking required
```

The thing worth remembering about a cookie, though, is that it's not proof of anything on its own — it's a reference to state the *server* is holding, or, if it's a signed cookie, a claim the server can verify came from itself. Anyone can write "8f14e45f-ceea" on a piece of paper and hand it to me. What makes the mark trustworthy is that I'm the one who wrote it in the first place, and I know how to tell my own handwriting from a forgery.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Server (on login or first response) | A session identifier and security flags | Emit a `Set-Cookie` header | A chalk mark the client will carry forward | The client's cookie jar |
| Client's HTTP stack (browser or `requests.Session`) | A stored cookie matching the request's domain/path | Automatically attach it as a `Cookie` header on future requests | Continuity between requests without re-authenticating each time | The server, recognizing a returning fare |
| Server (on each subsequent request) | An incoming `Cookie` header | Look up the referenced session state | A response tailored to the recognized session | The client, served without re-introducing itself |

Next stop: the quote that's still good from last time — ETag, Cache-Control, and not re-metering a fare who already paid for this exact ride.
