---
title: "Globetrotters go EAB 🔁 Ep.7"
series: "Globetrotters go EAB"
part: 7
organization: "the-software-s-journey"
tags: [certbot, renewal, docker, automation, check-freq]
---

## Episode 7: The Recurring Visa Renewal Nobody Has to Remember

Every visa has an expiry date, and every globetrotter has, at least once, discovered that date the hard way. The entire reason `idem-certbot` is a long-running container rather than a one-shot script is this exact closing block of `start.sh`:

```bash
# Renew loop
# Default to 12 hours if not set
CHECK_FREQ="${CHECK_FREQ:-12}"

# Validate CHECK_FREQ (must be a positive integer)
if ! [[ "$CHECK_FREQ" =~ ^[0-9]+$ ]]; then
  echo "[renew] Error: CHECK_FREQ must be a positive integer (hours). Current value: '$CHECK_FREQ'"
  exit 1
fi

echo "[renew] Check frequency set to $CHECK_FREQ hours."
echo -e "\n* [renew] Starting renew loop."
sleep "${CHECK_FREQ}h"

while true; do
  echo -e "\n* [renew] Running renew loop at $(date '+%Y-%m-%d %H:%M:%S')..."

  if certbot renew -q; then
    echo "* [renew] Certificate renew process finished."
  else
    echo "* [renew] Error: Failed to execute the renew command!" >&2
  fi

  echo "* [renew] Next check in $CHECK_FREQ hours"
  sleep "${CHECK_FREQ}h"
done
```

A few honest details worth flagging, since they're easy to get wrong if you're just guessing at how a renewal loop like this "probably" works. `CHECK_FREQ` is measured in **hours**, not days, and defaults to **12** — twice a day, not once every couple of months. And notice the very first `sleep "${CHECK_FREQ}h"` happens *before* the loop's first renewal attempt, not after — sensible enough, since the certificates were just freshly issued moments earlier in the script; there's nothing to renew yet, so there's no reason to check immediately.

`certbot renew -q` itself is the same well-mannered command every Certbot deployment relies on: it doesn't blindly re-request every certificate on every pass, it checks each one's actual expiry and only bothers the CA when a renewal is genuinely due. And — same as registration in Episode 5 — **the EAB flags never appear on `renew` at all**. They did their job once, binding the account back in Episode 2; from here on, Certbot renews using the account key it already has, sitting in whichever volume you mounted at `/etc/letsencrypt`. Lose that volume, and you haven't just lost certificates — you've lost the bound identity they were issued under, which is exactly the horror story waiting in the next episode.

One more quietly important thing about this loop: it's genuinely infinite, and it's the very last thing `start.sh` does. As long as the container is running — restart policy `unless-stopped` in the compose files we saw in Episode 4 — this loop just keeps going, checking in every `CHECK_FREQ` hours, forever, until someone stops the container on purpose.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `CHECK_FREQ` environment variable | An hour count, or nothing (defaults to 12) | Validate it's a positive integer, then drive the sleep interval | A predictable, configurable renewal cadence | The infinite renew loop |
| `certbot renew -q` | The account key and certificate store under `/etc/letsencrypt` | Check each certificate's real expiry; renew only what's due | Refreshed certificates, with no EAB flags needed | The domain's server, kept perpetually valid |
| The container's restart policy (`unless-stopped`) | A running or restarted container | Keep the infinite renew loop alive indefinitely | Continuous certificate freshness with zero manual intervention | Whoever would otherwise have to remember to renew by hand |

Next stop: what happens when the mounted `/etc/letsencrypt` volume itself goes missing, and the sponsor letter that got you in once doesn't automatically get you back in twice.
