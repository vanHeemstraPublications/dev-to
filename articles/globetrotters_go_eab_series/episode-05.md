---
title: "Globetrotters go EAB 🗣️ Ep.5"
series: "Globetrotters go EAB"
part: 5
organization: "the-software-s-journey"
tags: [certbot, acme, register, eab, start-sh]
---

## Episode 5: The Consulate Interview: Registering the Account

Container started, environment variables read, our globetrotter now steps up to the consulate counter. Here is that moment exactly as `start.sh` performs it — no paraphrasing this time, this is the real thing:

```bash
# Check if EAB variables are set, if not, we will use standard Let's Encrypt registration
USE_EAB=true
for VAR in SERVER_URL KEY_ID HMAC_KEY; do
  if [ -z "${!VAR:-}" ]; then
    USE_EAB=false
    break
  fi
done
echo "[setup] USE_EAB=$USE_EAB"

echo "[registration] Register ACME account."

if $USE_EAB; then
    echo "[registration] Using ACME EAB."
    if ! certbot register \
            --email "$EMAIL_ADMIN" \
            --server "$SERVER_URL" \
            --eab-kid "$KEY_ID" \
            --eab-hmac-key "$HMAC_KEY" \
            --non-interactive \
            --agree-tos 2>&1 | grep -q "There is an existing account"; then
        echo "[registration] ACME account registration done!"
    else
        echo "[registration] ACME account already exists, skipping registration."
    fi
else
    echo "[registration] Using Let's Encrypt standard."
    if ! certbot register \
            --email "$EMAIL_ADMIN" \
            --agree-tos \
            --non-interactive 2>&1 | grep -q "There is an existing account"; then
        echo "[registration] ACME account registration done!"
    else
        echo "[registration] ACME account already exists, skipping registration."
    fi
fi
```

Two things worth savouring here as a fellow appreciator of tidy travel logistics. First, the "which border is this" decision is refreshingly binary: loop over `SERVER_URL`, `KEY_ID`, and `HMAC_KEY`, and the moment even one is empty, `USE_EAB` flips to false and the whole trip becomes a standard Let's Encrypt crossing — exactly the strict all-or-nothing behaviour Episode 4 warned about. Second, notice that the script doesn't pre-check whether an account already exists before trying — it just *attempts* registration every single time the container starts, and then reads the tea leaves afterward. Certbot itself refuses to double-register an already-bound account and prints "There is an existing account" when that happens; the script simply greps for that exact phrase in the command's own output to decide which log line to print. It's not checking a file on disk to see if you've been here before — it's asking the consulate directly, every time, and listening carefully to the answer.

This also means restarting the container is entirely safe from a registration standpoint. Whether this is your globetrotter's first visit or their fiftieth, `start.sh` runs the same interview, and Certbot itself is the one keeping score of who's already bound and who isn't.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `start.sh`'s `USE_EAB` check | `SERVER_URL`, `KEY_ID`, `HMAC_KEY` | Flip to EAB mode only if all three are non-empty | A binary EAB/standard decision for this run | The `certbot register` call that follows |
| Certbot (`certbot register`) | `$EMAIL_ADMIN` and, if EAB, `$SERVER_URL`/`$KEY_ID`/`$HMAC_KEY` | Attempt account registration, succeeding or reporting an existing account | Either a fresh registration or an "already exists" response | The container's own log output |
| `grep -q "There is an existing account"` | Certbot's registration output | Decide which log line to print, without blocking cert creation either way | A human-readable status message | Whoever is watching `docker logs` |

Next stop: having a bound account doesn't mean you're through — customs still wants to physically inspect the domain, and `idem-certbot` does this a little differently than you might expect.
