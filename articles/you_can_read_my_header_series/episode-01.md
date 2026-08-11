---
title: "You can read my Header 🚕 Ep.1"
series: "You can read my Header"
part: 1
organization: "the-software-s-journey"
tags: [http, headers, introduction, metadata]
---

## Episode 1: The Sign on Top Says More Than You Think

Night shift again. Rain on the windshield, steam off the grates, the city doing what it does after midnight. I drive this cab up and down the avenues and nobody ever looks up at the little box bolted to the roof. They just want to know one thing: is the light on or off. Occupied. Free. Two words, and that's supposed to be the whole story.

It isn't. My sign does more than that, if you know how to read it. Up there, above the medallion number, there's a little multilingual display — most fares never notice it, never think to ask what else a sign could possibly say. But that display carries the whole manifest of the trip. Not the passenger. Not where they're going. The stuff *around* the trip — who's paying, what language they want the receipt in, whether this is a returning customer or a first-timer, whether the fare's already been quoted and doesn't need re-metering, whether some other garage vouched for this pickup before I ever rolled up to the curb.

That's what a header is. Not the cargo. The metadata riding alongside the cargo. In HTTP, every request and every response carries this same kind of sign — a block of key-value lines sitting above the actual body of the message, saying who's asking, what they'll accept back, how they want it wrapped, and what's already been agreed on before a single byte of the real payload gets read.

```
GET /fares/pickup HTTP/1.1
Host: dispatch.citycab.example
Accept: application/json
Accept-Language: en-US, es;q=0.8
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
X-Request-ID: 8f14e45f-ceea-467e-9575-6b6c1a6c4b3d
```

Four lines up top, not one byte of the actual fare request read yet, and already I know: they want JSON back, they'll take Spanish if English isn't available, they're carrying a token that's supposed to prove who they are, and somebody handed them a ticket number to track this whole ride through however many garages it passes through before it's done. That's the sign on my roof, dressed up in HTTP's own uniform. Ride along. I'll show you every line on it, one at a time.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The requesting client (browser, app, another server) | Intent to make an HTTP request | Attach header lines describing the request before sending the body | A request carrying both metadata and payload | The receiving server |
| HTTP specification (RFC 9110 and friends) | A standardized header-line format (`Name: value`) | Define what names mean and how values should be parsed | A shared vocabulary every client and server can rely on | Every implementation of HTTP, everywhere |
| The responding server | The request's headers | Read the metadata before touching the body, decide how to respond | Response headers of its own, describing what's coming back | The original requesting client |

Next stop: the sign's language dial — Content-Type and Accept, and what happens when the passenger and the cab don't speak the same tongue.
