---
title: "You can read my Header 🗣️ Ep.2"
series: "You can read my Header"
part: 2
organization: "the-software-s-journey"
tags: [http, headers, content-type, accept, content-negotiation]
---

## Episode 2: The Language Dial: Content-Type and Accept

Every fare that gets in the back has an idea of what they want handed back to them at the end of the trip. Some want a paper receipt. Some want it read out loud. Some, believe it or not, want it in a language I don't even speak, and my sign's got a dial for that too — a little flag icon that flips depending on who climbed in.

In HTTP, the passenger states that preference with `Accept`, and I state what I'm actually handing over with `Content-Type`. Two sides of the same conversation, and they are not the same header, no matter how many people mix them up on their first ride.

```
GET /trip-summary HTTP/1.1
Host: dispatch.citycab.example
Accept: application/json, application/xml;q=0.9, text/plain;q=0.5
Accept-Language: en-US, it;q=0.7
```

That `q=` business is the passenger ranking their preferences out loud — "JSON if you've got it, XML if you don't, plain text if that's all that's left, and by the way, English first, Italian if you're out of English." The server reads that whole ranked list before it decides what to actually print on the receipt, and it says so, right there in the response:

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Language: en-US
```

`Content-Type` on the response isn't a suggestion, it's a declaration — "here's what I'm actually handing you, formatted exactly like this." A client that ignores it and tries to parse JSON as if it were XML gets exactly the mess you'd expect from trying to read a Italian receipt as if it were printed in English. Get the request side wrong too, and you get the flip side of the mess — send a request body that's actually form data but declare it as JSON, and:

```python
import requests

resp = requests.post(
    "https://dispatch.citycab.example/fares",
    data="pickup=42nd+St&dropoff=Grand+Central",
    headers={"Content-Type": "application/json"},  # lying about the format
)
```

That request is a passenger handing me a note written in Italian while insisting, loudly, that it's in English. I'll try to read it that way because the sign told me to, and I'll get it wrong, and it won't be the note's fault. The header isn't decoration — it's the one thing standing between "this body means something specific" and "good luck guessing."

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Requesting client | A ranked list of acceptable formats and languages | Set `Accept` and `Accept-Language` on the outgoing request | A stated preference the server can honor or negotiate around | The responding server |
| Responding server | The client's stated preferences, plus its own available formats | Choose a format to actually return | A `Content-Type` (and optionally `Content-Language`) declaring what's coming | The requesting client's parser |
| Either party sending a body | Raw bytes meant to represent a specific format | Label those bytes accurately via `Content-Type` | A body the receiver can parse correctly on the first try | Whichever side has to read it |

Next stop: the sealed trip voucher every fare carries now — Authorization, Bearer tokens, and the JWT riding inside them.
