---
title: "Globetrotters go EAB 😱 Ep.8"
series: "Globetrotters go EAB"
part: 8
organization: "the-software-s-journey"
tags: [certbot, troubleshooting, eab, acme, errors]
---

## Episode 8: When the Sponsor Letter Goes Missing

Every globetrotter has a horror story, and this is the EAB chapter's designated one: your `idem-certbot` container's `/etc/letsencrypt` volume — the one mounted from `<YOUR-DESTINATION-FOLDER-ON-VM>` in Episode 4's compose file, or `certbot_data_volume` if Ansible set it up — gets wiped. A rebuild without the volume flag, an over-enthusiastic cleanup, a restore that skipped a directory. The bound account key is gone. No matter, you think — you still have the sponsor letter, the same `KEY_ID` and `HMAC_KEY` as before. Surely `start.sh` just registers again on next boot?

It will certainly *try*, because as Episode 5 showed, it attempts registration on every single startup regardless. But try presenting an already-consumed `KEY_ID`/`HMAC_KEY` pair to *create a brand new account*, and depending on your CA's own policy, you may get a rejection that sounds far more dramatic than it needs to:

```
An unexpected error occurred:
The request message was malformed :: [External Account Binding]
The account is not awaiting external account binding
```

Many CAs treat a given EAB pair as tied to *one specific binding event*, not as a reusable "log back in with this" credential. Once it's bound an account, presenting it again to create a *different* account can be refused outright — the CA sees a sponsor letter that's already been stamped and used. `idem-certbot`'s own script has no special handling for this scenario either; it will simply log whatever Certbot printed and move on to attempting certificate creation with whatever account state actually exists.

The practical response, in order of preference: first, if the account key exists anywhere else — an old backup of the same volume, a snapshot — restore it into that mounted `/etc/letsencrypt/accounts/` path and skip registration entirely; the renewal loop from Episode 7 doesn't need the sponsor letter again, it needs the *key*. Second, contact whoever issued your `KEY_ID`/`HMAC_KEY` — for GARR members, that's GARR itself — and ask for a fresh, unconsumed pair; sponsors generally expect this to happen occasionally. Third: check whether your specific CA's ACME implementation supports account recovery via EAB at all before assuming Certbot's behavior is universal — not every CA treats a repeated binding attempt identically.

The lesson every globetrotter eventually tattoos on their memory: that mounted volume *is* the passport. The sponsor letter only ever gets you a fresh one once.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The mounted `/etc/letsencrypt` volume | An accidental deletion, failed restore, or volume-less rebuild | Remove the previously bound account key | A broken renewal loop with no account to renew | The sysadmin discovering the error at the worst time |
| Certbot | A repeated `register` attempt using already-consumed EAB credentials | Reject the request per the CA's own EAB reuse policy | The "not awaiting external account binding" error | The sysadmin, now reading container logs at 2am |
| Sponsor (e.g. GARR) | A request for a fresh `KEY_ID`/`HMAC_KEY` pair | Issue a new, unconsumed sponsor letter | A usable credential for re-registering the account | The affected member, back in business |

Next stop: the repo's actual answer to "one node or many" — Standalone versus Centralized mode, and how a fleet of servers ends up sharing the same certificate.
