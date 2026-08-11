---
title: "You can read my Header 🛑 Ep.9"
series: "You can read my Header"
part: 9
organization: "the-software-s-journey"
tags: [http, headers, hsts, csp, security]
---

## Episode 9: The Placard Warning Off Impersonator Cabs

There are cabs out there that aren't really cabs. Wrong medallion, painted up to look official, waiting outside the terminal for somebody too tired to check the door before getting in. The city can't stop every one of them, but a good dispatcher can at least post a placard that says, plainly, "our real cabs always look like this, always take this route, never do that other thing — if a cab claiming to be ours does otherwise, it isn't ours."

That's what a handful of security-focused headers do for a browser, and they're worth knowing by name because each one closes off a specific, well-worn trick. `Strict-Transport-Security` is the placard that says "we never, ever run unencrypted — if you ever reach us over plain HTTP again, don't even try, go straight to HTTPS":

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Once a browser's seen that header, it remembers for a full year (`max-age` in seconds) and refuses to even attempt an HTTP connection to that domain again, upgrading automatically — closing off the classic trick where an attacker on the same network quietly downgrades a connection to unencrypted before anyone notices.

`Content-Security-Policy` is the placard listing exactly which garages are allowed to load anything into this page at all — scripts, styles, images, the works:

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.example; object-src 'none'
```

Read plainly: only load resources from our own origin by default, allow scripts specifically from one trusted CDN and nowhere else, and never, under any circumstances, load a plugin object. An attacker who manages to sneak a rogue `<script>` tag into a page via some injection flaw finds that script simply refuses to run — the browser checked the placard first and the script's origin wasn't on the approved list.

`X-Frame-Options` (and its more flexible modern replacement, `frame-ancestors` inside CSP) stops a very specific con: a fraudulent page loading the real dispatch site inside an invisible frame, laying its own fake buttons on top, and tricking a passenger into clicking what looks like "confirm pickup" while actually clicking something on the hidden real site underneath — a trick called clickjacking:

```
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'
```

`DENY` means this page refuses to be embedded in *any* frame, on any site, ever. And here's the one that ties every header in this whole series together: none of these placards work if a passenger can't trust that the placard itself came from the real dispatcher and wasn't forged along the way. That trust is exactly what HTTPS and a properly issued certificate provide — which is why the EAB series a few trips back, and this whole series about headers, are really two chapters of the same story: certificates prove who's talking, headers describe what's being said and under what rules, and neither one means much without the other standing guard.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Server operator | A decision to enforce HTTPS-only, restrict resource origins, and forbid framing | Set `Strict-Transport-Security`, `Content-Security-Policy`, and `X-Frame-Options` | A browser-enforced security posture for the whole origin | Every browser visiting the site |
| Browser | The security headers above, remembered per origin | Refuse downgraded connections, block unapproved script/resource origins, refuse framing | A hardened session resistant to downgrade, injection, and clickjacking attacks | The end user |
| TLS/certificate layer (from the EAB series) | A valid, trusted certificate for the origin | Establish that the security headers themselves are genuinely from the claimed origin | A trustworthy channel for the placards to travel over in the first place | Every header discussed in this whole series |

Next stop: what happens when you show up to the stand and dispatch tells you to wait — Retry-After, rate limiting, and knowing when to circle the block instead of hailing again immediately.
