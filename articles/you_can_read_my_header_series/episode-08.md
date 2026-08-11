---
title: "You can read my Header 🚧 Ep.8"
series: "You can read my Header"
part: 8
organization: "the-software-s-journey"
tags: [http, headers, cors, preflight, security]
---

## Episode 8: Which Garages Are Even Allowed to Dispatch to This Cab

I don't take a fare just because somebody waves from across the street claiming to be dispatch. Different garages, different rules, and before I'll even roll toward a pickup called in by an app running out of some other outfit's territory, I want to know: is this garage actually on my approved list? That check happens before the ride, quietly, and most passengers never even know it occurred.

That's Cross-Origin Resource Sharing — CORS — and the interesting part is that for anything beyond the simplest request, the browser sends a whole separate check first, called a preflight, before the real request ever goes out:

```
OPTIONS /fares/pickup HTTP/1.1
Host: dispatch.citycab.example
Origin: https://rival-garage-app.example
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Authorization, Content-Type
```

That's the browser, on the app's behalf, asking dispatch: "a script running on `rival-garage-app.example` wants to send you a POST with these headers attached — is that even allowed?" And dispatch answers, before any real fare data is exchanged at all:

```
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://rival-garage-app.example
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 600
```

Get a "no" instead — either no `Access-Control-Allow-Origin` header at all, or one naming a different origin — and the browser never even sends the real request. Not because the server would have refused it necessarily, but because the browser itself refuses to let the script read the response, on the script's own behalf, as a security boundary. This is worth sitting with for a second: CORS isn't the server protecting itself from a malicious script — it's the *browser* protecting the *user* from a script quietly using their already-logged-in session to talk to some other garage's dispatch without asking.

```javascript
// Running on https://rival-garage-app.example
fetch("https://dispatch.citycab.example/fares/pickup", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include",  // send cookies along too
  body: JSON.stringify({ pickup: "42nd St" }),
})
  .then(r => r.json())
  .catch(err => console.error("Blocked by CORS:", err));
```

That `Access-Control-Max-Age: 600` line is dispatch saying "you don't need to ask me this same preflight question again for the next ten minutes — I'll remember my own answer." Every subsequent request from that same origin, for that same method and headers, skips straight to the real thing, no repeated preflight required. One approval, cached, and the garage stops re-litigating a decision it already made.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Browser (on behalf of a cross-origin script) | An intended request to a different origin | Send an `OPTIONS` preflight before the real request, when required | A yes/no answer about whether the real request may proceed | The script attempting the cross-origin call |
| Server | An incoming preflight's `Origin`, method, and headers | Decide whether to allow it, and for how long to cache that answer | `Access-Control-Allow-*` headers, or a silent refusal | The browser enforcing the decision |
| Browser (enforcement) | The server's CORS response | Permit or block the script from reading the real response | Either a successful cross-origin call or a blocked one | The end user, protected from unapproved cross-origin access to their session |

Next stop: the placard warning off impersonator cabs entirely — HSTS, Content-Security-Policy, and the headers that keep this ride from getting hijacked.
