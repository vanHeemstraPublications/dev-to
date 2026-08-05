---
title: "Globetrotters go EAB 🛃 Ep.6"
series: "Globetrotters go EAB"
part: 6
organization: "the-software-s-journey"
tags: [acme, http-01, standalone, certbot, rsa]
---

## Episode 6: Customs Wants to Inspect the Luggage Itself

Here's the twist that catches every first-time globetrotter off guard: a bound account does not wave you straight through to baggage claim. Customs still wants to inspect the actual luggage — proof that you, right now, control the domain you're claiming — and EAB changes nothing about that second, entirely separate check. What's worth noting is *how* `idem-certbot` handles this inspection, because it's a more hands-on approach than you might expect from a container that otherwise runs quietly in the background:

```bash
if $USE_EAB; then
    certbot certonly \
        --standalone \
        --email "$EMAIL_ADMIN" \
        --server "$SERVER_URL" \
        --eab-kid "$KEY_ID" \
        --eab-hmac-key "$HMAC_KEY" \
        "${domain_args[@]}" \
        --key-type rsa \
        --rsa-key-size 3072 \
        --quiet --non-interactive --agree-tos 2>&1
else
    certbot certonly \
        --standalone \
        --email "$EMAIL_ADMIN" \
        "${domain_args[@]}" \
        --key-type rsa \
        --rsa-key-size 3072 \
        --quiet --non-interactive --agree-tos 2>&1
fi
```

`--standalone` is the detail worth pausing on. Rather than expecting an nginx or Apache already running on the host to serve a challenge file from some shared webroot, Certbot's standalone plugin briefly spins up its *own* tiny temporary web server, directly inside the container, purely to answer the HTTP-01 challenge, then tears it back down the moment validation completes. It's the customs equivalent of the officer briefly opening your suitcase themselves rather than asking a nearby porter to hold it open — no dependency on some other web server already running correctly on port 80, just Certbot, briefly, doing the whole inspection itself. The practical consequence for anyone deploying this: port 80 on the host needs to be free and reachable for that brief window, since nothing else is serving the challenge.

Before we move off this block, notice the identical `--key-type rsa --rsa-key-size 3072` on both branches, EAB or not. That's not the CA's demand — Certbot defaults to ECDSA on modern versions — it's `idem-certbot` making a deliberate, house-style choice: every certificate this container ever requests carries an RSA key, sized 3072 bits, full stop, regardless of which border it crossed to get there. Consistent passport photo specifications, no matter which consulate took the picture.

And notice, too, the check guarding the whole `create_cert` function before any of this runs: `if [ ! -f "/etc/letsencrypt/live/$domain/cert.pem" ]`. Unlike registration's grep-and-hope approach from the last episode, certificate creation checks the actual filesystem first — if a cert already exists for this domain, the container skips straight past it, no re-inspection needed.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Certbot's standalone plugin | An HTTP-01 challenge from the ACME server | Spin up a temporary web server on port 80, answer the challenge, tear it down | Proven domain control, no external web server required | The ACME server's validation step |
| `start.sh`'s `create_cert` function | `$domain` and its parsed alias list | Check `/etc/letsencrypt/live/$domain/cert.pem`; request only if missing | An idempotent, restart-safe certificate request | The container's certificate store |
| `--key-type rsa --rsa-key-size 3072` (hardcoded) | Every certificate request, EAB or standard | Force RSA 3072-bit keys regardless of border crossed | Consistent key material across the whole fleet | Whatever service ultimately presents this certificate |

Next stop: certificates don't last forever — how the renewal loop keeps the visa fresh, on a schedule measured in hours, not days.
