---
title: "Globetrotters go EAB 📋 Ep.4"
series: "Globetrotters go EAB"
part: 4
organization: "the-software-s-journey"
tags: [docker-compose, environment-variables, acme, eab, certbot]
---

## Episode 4: Filling Out the Visa Form Before You Fly

No globetrotter enjoys the visa application form, but everyone agrees it beats being turned away at the gate. Here's `idem-certbot`'s actual form, straight from the README's table of environment variables:

| Variable | Description | Required? |
|---|---|---|
| `EMAIL_ADMIN` | Admin email for ACME registration | Yes |
| `DOMAINS_LIST` | Domains to certificate, separated by `;`, with optional aliases after `:` | Yes |
| `SERVER_URL` | ACME server URL | Only for EAB |
| `KEY_ID` | EAB key identifier | Only for EAB |
| `HMAC_KEY` | HMAC key for EAB | Only for EAB |
| `CHECK_FREQ` | Hours between certificate checks and renewal | No — default 12 |

`DOMAINS_LIST` deserves a proper look before we move on, because it's doing more work than it looks like: semicolons separate independent certificate requests, and a colon after a domain introduces a comma-separated list of aliases that ride along on the *same* certificate as Subject Alternative Names:

```
DOMAINS_LIST=domain1:alias1,alias2;domain2;domain3:alias1
```

Read that as three separate trips: a certificate for `domain1` that also covers `alias1` and `alias2`, a plain single-domain certificate for `domain2`, and a certificate for `domain3` plus `alias1`. One environment variable, an entire multi-stop itinerary.

Here's the actual visa form for a border requiring a sponsor letter — the README's own local, no-Ansible `docker-compose.yml`:

```yaml
services:
    idem-certbot:
        image: "<DOCKER-IMAGE-NAME>:<TAG>"
        container_name: "custom-certbot"
        hostname: certbot
        environment:
            - EMAIL_ADMIN=<MAIL-UTENTE>
            - KEY_ID=<KEY-ID-VALUE>
            - HMAC_KEY=<HMAC_KEY_VALUE>
            - SERVER_URL=<ACME-SERVER-URL>
            - CHECK_FREQ=<CHECK-FREQ>
            - DOMAINS_LIST=domain1:alias1,alias2;domain2;domain3:alias1
        volumes:
            - <YOUR-DESTINATION-FOLDER-ON-VM>:/etc/letsencrypt
        restart: unless-stopped
        healthcheck:
            test: ["CMD-SHELL", "certbot certificates > /dev/null 2>&1"]
            interval: 1m
            timeout: 10s
            retries: 3
            start_period: 20s
```

And here's the important warning, printed in the README in the loudest formatting a Markdown file has available: if you're heading to the easygoing Let's-Encrypt-Land border instead, you must leave `KEY_ID`, `HMAC_KEY`, and `SERVER_URL` **completely empty**. Not omitted casually, not commented out — genuinely empty. That's because `start.sh` doesn't check "did the user say EAB or not"; it checks whether all three variables actually have values, and treats their presence or absence as the entire decision. Half-fill the form — say, an EAB server URL with no key ID — and the container won't guess what you meant. We'll watch exactly how it decides in the next episode.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Domain owner / sysadmin | `EMAIL_ADMIN`, `DOMAINS_LIST`, and (if required) `SERVER_URL`/`KEY_ID`/`HMAC_KEY` | Populate the `docker-compose.yml` environment block | A filled-out, ready-to-run visa form | The `idem-certbot` container about to start |
| `DOMAINS_LIST` parser (inside `start.sh`) | The `;`- and `:`-delimited domain/alias string | Split into individual certificate requests, each with its own SAN list | One `create_cert` call per domain group | Certbot's `certonly` invocation |
| `docker compose up -d` | The completed compose file | Start the container with the given environment | A running certificate-automation process | The domain's server, waiting for its certificate |

Next stop: what actually happens at the consulate counter once the container starts — the account registration itself, verbatim from `start.sh`.
