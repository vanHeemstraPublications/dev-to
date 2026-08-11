---
title: "You can read my Header ⏳ Ep.10"
series: "You can read my Header"
part: 10
organization: "the-software-s-journey"
tags: [http, headers, rate-limiting, retry-after, 429]
---

## Episode 10: When Dispatch Tells You to Wait

There's a stand outside the terminal, and I don't get to just sit there all night calling in for fares every ten seconds hoping something sticks. Dispatch has a rhythm, a capacity, a number of calls it can actually field before the whole system chokes. Push too hard, too fast, and dispatch doesn't just ignore you — it tells you, plainly, to circle the block and try again in a few minutes.

HTTP's version of that instruction is a `429 Too Many Requests`, and the header riding along with it is the part that actually makes it useful rather than just annoying:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
Content-Type: application/json

{"error": "rate_limited", "message": "Too many pickup requests. Slow down."}
```

`Retry-After: 30` isn't a vague "try later." It's dispatch telling you, precisely, how many seconds to wait before calling back in — and a well-behaved client honors that number exactly rather than guessing, or worse, hammering the same endpoint again immediately out of impatience:

```python
import time
import requests

def request_with_backoff(url: str, headers: dict) -> requests.Response:
    resp = requests.get(url, headers=headers)
    if resp.status_code == 429:
        wait = int(resp.headers.get("Retry-After", "5"))
        print(f"Dispatch says wait {wait}s before calling back in.")
        time.sleep(wait)
        return requests.get(url, headers=headers)
    return resp
```

Some dispatchers are even more forthcoming than that, telling you your standing *before* you ever get rejected, so you can pace yourself and never hit the wall at all:

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1720003600
```

Read that as dispatch saying, quietly, on every single successful call: "you get a hundred calls in this window, you've got four left, and the window resets at this exact timestamp." A considerate client watches that number tick down and slows itself down voluntarily, long before dispatch ever has to raise its voice with a 429. That's the real point of a rate-limiting header — it's not a punishment mechanism bolted on after the fact, it's dispatch and driver negotiating pace together, out loud, in a language both sides already understand, so nobody has to find the limit the hard way.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Server (rate limiter) | The client's request rate against a defined budget | Track usage and decide whether to allow, warn, or reject | `X-RateLimit-*` headers on success, or `429` with `Retry-After` when exceeded | The requesting client |
| Well-behaved client | A `Retry-After` value on a `429` response | Wait exactly that long before retrying | A request that succeeds on retry instead of compounding the problem | The server, no longer under unnecessary pressure |
| Client (proactive pacing) | `X-RateLimit-Remaining` and `X-RateLimit-Reset` on successful responses | Slow its own request rate before ever being rejected | A relationship with the server that never needs a 429 at all | Both sides, avoiding the rejection entirely |

Next stop: the whole dashboard, every sign lit up at once — closing out the trip and looking back at everything riding above the fare this whole time.
