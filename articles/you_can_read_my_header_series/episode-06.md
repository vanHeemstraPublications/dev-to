---
title: "You can read my Header 🧾 Ep.6"
series: "You can read my Header"
part: 6
organization: "the-software-s-journey"
tags: [http, headers, caching, etag, cache-control]
---

## Episode 6: The Quote That's Still Good From Last Time

A regular asks me the fare to the airport, I quote him a number, and if he calls back twenty minutes later asking the same question, I don't run the meter again from scratch to give him the same answer. I just tell him: same as before, nothing's changed, that quote's still good. Save us both the time.

HTTP does this with `ETag` and `Cache-Control`, and it's one of the more elegant tricks riding in the header block, because it lets a client skip downloading something it already has, just by asking politely. First trip through, the server hands back the resource along with a fingerprint of exactly this version of it:

```
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "a1b2c3d4"
Cache-Control: max-age=300, must-revalidate
```

`Cache-Control: max-age=300` is me telling the fare "this quote's good for five minutes, don't even bother asking again before then." After that window closes, the client doesn't necessarily assume the quote changed — it just checks, politely, showing the old fingerprint back to see if it still matches:

```
GET /trip-summary HTTP/1.1
Host: dispatch.citycab.example
If-None-Match: "a1b2c3d4"
```

And if nothing's changed since:

```
HTTP/1.1 304 Not Modified
```

No body. No re-download. Just a one-line "yep, still the same quote," and the client keeps using whatever it already had cached. That's the entire trick — the fingerprint costs almost nothing to check, and it saves the full cost of re-sending a body that would've been byte-for-byte identical anyway. Here's what checking that quote actually looks like from a client's side:

```python
import requests

headers = {}
resp = requests.get("https://dispatch.citycab.example/trip-summary", headers=headers)
etag = resp.headers.get("ETag")
data = resp.json()

# ... some time later, same client, checking if the quote's still good ...
resp2 = requests.get(
    "https://dispatch.citycab.example/trip-summary",
    headers={"If-None-Match": etag},
)

if resp2.status_code == 304:
    print("Same as before — using the cached quote.")
else:
    data = resp2.json()
    print("Quote changed — got a fresh one.")
```

Every regular fare in this city benefits from this without ever knowing it's happening — their app just feels faster, because half the time it isn't even downloading anything, just confirming the old answer still holds. That's the quiet, unglamorous magic of a well-set `ETag`: the absence of a re-fetch is the whole feature.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Server (first response) | The current state of a resource | Compute a fingerprint and attach `ETag` plus a `Cache-Control` freshness window | A cacheable response the client can trust for a while | The client's local cache |
| Client (on a later request) | A previously cached `ETag` | Send it back via `If-None-Match` instead of blindly re-requesting the full body | A conditional request that costs almost nothing if unchanged | The server, deciding whether to resend anything at all |
| Server (on the conditional check) | An `If-None-Match` value matching the current fingerprint | Reply `304 Not Modified` with no body | Bandwidth and processing saved on both ends | The client, continuing to use its cached copy |

Next stop: the relay of trip tickets passed from cab to cab — X-Forwarded-For, X-Request-ID, and tracing a fare through more garages than you'd expect.
