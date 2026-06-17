---
title: "REST with step-ca 🔐 Ep.6"
published: false
description: "Episode 6: Certificates expire. A service that goes dark when its certificate hits midnight is not a service — it is a liability. This episode adds renew() using mTLS authentication against /1.0/renew, and a start_renewal_daemon() background thread that monitors the certificate lifetime and renews automatically at two-thirds of the remaining validity window. Architecture diagrams show the renewal timing strategy."
tags: [python, tls, certificates, automation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/rest-with-step-ca-episode-06.png"
series: "REST with step-ca"
canonical_url: ""
organization: "the-software-s-journey"
part: 6
---

## Episode 6: Still Breathing — mTLS Renewal and the Daemon

---

## Certificates Have an Expiry Problem

A 24-hour certificate issued by step-ca expires in 24 hours. That is the point — short-lived certificates are a security feature, not a bug. Passive revocation: if a certificate is stolen, it becomes useless quickly without any revocation infrastructure needed.

But "useful for 24 hours" does not mean "renew it manually every morning." That defeats the purpose of automation. The solution is a **renewal daemon**: a background thread that watches the certificate's expiry and renews it automatically before it expires, using **mTLS** — mutual TLS — so no JWT is required.

---

## 🗂️ SIPOC — Certificate Renewal

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| The current certificate | `cert_pem`, `key_pem` (from the last sign or renew) | Configure an `httpx.Client` with the cert+key as mTLS client credentials | An mTLS-capable session for the renewal request | `POST /1.0/renew` — authenticates via the presented cert |
| `POST /1.0/renew` endpoint | mTLS connection presenting current cert | CA verifies cert: provisioner still active? Not expired beyond grace? Clone cert with fresh expiry | `{crt, ca, certChain}` — same structure as `/1.0/sign` | `renew()` — extracts the new cert/chain |
| Renewal daemon thread | Cert `not_after` timestamp; renewal fraction (default 2/3) | Sleep until 2/3 of lifetime has elapsed; call `renew()`; repeat | Continuously fresh certificate in memory (and optionally on disk) | Any code holding a reference to the `IssuedCertificate` object |

---

## The Renewal Timing Strategy

```
CERTIFICATE LIFETIME AND RENEWAL WINDOW
═══════════════════════════════════════════════════════════════════════

  Certificate issued          Renewal window opens      Expires
       │                             │                    │
       ▼                             ▼                    ▼
  ─────┬────────────────────────────┬────────────────────┬─────
       │◄──────── 24h lifetime ────►│◄──── 8h safe ─────►│
       │                            │       renewal       │
       │◄─ first 16h: not renewed ─►│        zone         │
       │                            │                     │
       │         "2/3 rule":        │ Daemon checks every │
       │         wait until 2/3     │ few minutes; renews │
       │         of lifetime        │ if in this window   │
       │         has elapsed        │                     │

  Why 2/3?
  ────────
  step-ca's recommendation: renew when ≥ 2/3 of the cert's lifetime
  has elapsed. For a 24h cert: renew after 16h.

  Benefits:
  • Renewable even if the CA is briefly down (8h margin to retry)
  • Not renewing too early (wastes entropy, keeps logs clean)
  • Aligns with step's built-in daemon behaviour

  Jitter: add ±10% random delay to prevent thundering-herd renewals
  when many services are provisioned simultaneously.


  RENEWAL DAEMON FLOW
  ───────────────────

  start_renewal_daemon()
       │
       ▼
  ┌──────────────────────────────────────────────────────────┐
  │  Background thread (daemon=True — exits with main)        │
  │                                                           │
  │  Loop:                                                    │
  │    1. Read cert not_after                                 │
  │    2. Compute seconds_remaining = not_after - now()       │
  │    3. lifetime = not_after - not_before                   │
  │    4. renewal_fraction (default 2/3)                      │
  │    5. sleep_until = not_before + lifetime * 2/3           │
  │    6. sleep_seconds = sleep_until - now() + jitter        │
  │    7. if sleep_seconds > 0: time.sleep(sleep_seconds)     │
  │    8. Attempt renew()                                     │
  │       On success: update cert reference; log              │
  │       On failure: retry with exponential backoff          │
  │    9. goto 1 (now cert has fresh not_before/not_after)    │
  └──────────────────────────────────────────────────────────┘
```

---

## mTLS Renewal Architecture

```
mTLS RENEWAL — HOW AUTHENTICATION WORKS
═══════════════════════════════════════════════════════════════

WITHOUT mTLS (regular HTTPS):
  Client ──TLS handshake──► Server
  Server presents its cert; client verifies it.
  Client is anonymous to the server.

WITH mTLS (mutual TLS for renewal):
  Client ──TLS handshake──► Server
  Server presents its cert; client verifies it. (as before)
  Client also presents ITS cert; server verifies it.

  For step-ca /1.0/renew:
    Client cert:  the certificate to be renewed
    CA verifies:  Is this cert signed by our CA?
                  Is the provisioner that signed it still active?
                  Is the cert not expired beyond the grace window?
    If all OK:    Issue a new cert cloning the subject/SANs/key
                  (The key itself is NOT reused — a fresh key
                   can be generated, or the same key is embedded
                   from the renewed CSR)

  step-ca behaviour on /1.0/renew:
    - No body required in the POST
    - Authentication = the TLS client certificate
    - The CA "clones" the expiring cert with a new validity window
    - The response certChain has the same subject/SANs as the original
```

---

## Adding renew() and the Renewal Daemon

```python
# step_ca_client.py  (additions — renewal)

import threading
import random
import datetime
import ssl
import tempfile

from cryptography.hazmat.primitives import serialization


class StepCAClient:
    # ... (existing methods from Episodes 2–5)

    # ── Renewal ───────────────────────────────────────────────────────────

    def renew(
        self,
        cert_pem: str,
        key_pem:  str,
    ) -> IssuedCertificate:
        """
        Renew a certificate using mTLS authentication.

        The current certificate and its private key are presented as the
        TLS client certificate to /1.0/renew. No JWT required.
        step-ca clones the certificate with a fresh validity window.

        Args:
            cert_pem: Current certificate PEM (leaf only, or full chain)
            key_pem:  Private key PEM (unencrypted)

        Returns:
            IssuedCertificate with fresh cert_pem, chain_pem, key_pem
        """
        # Write the cert and key to temp files for the mTLS session
        # (httpx requires paths for client certificate auth)
        with (
            tempfile.NamedTemporaryFile(suffix=".crt", delete=False, mode="w") as cf,
            tempfile.NamedTemporaryFile(suffix=".key", delete=False, mode="w") as kf,
        ):
            cf.write(cert_pem)
            kf.write(key_pem)
            cert_path = cf.name
            key_path  = kf.name

        try:
            # Build a dedicated mTLS session that presents the cert
            mtls_session = httpx.Client(
                verify  = self._root_cert_file.name,   # trust our CA root
                cert    = (cert_path, key_path),        # present as client cert
                timeout = self.timeout,
            )

            response = mtls_session.post(f"{self.ca_url}/1.0/renew")
            mtls_session.close()

            self._raise_for_status(response)

        finally:
            import os
            os.unlink(cert_path)
            os.unlink(key_path)

        data      = response.json()
        cert_chain = data.get("certChain", [data.get("crt", ""), data.get("ca", "")])
        leaf_pem  = cert_chain[0]
        ca_pem    = cert_chain[1] if len(cert_chain) > 1 else ""
        chain_pem = "".join(cert_chain)

        issued = IssuedCertificate(
            cert_pem  = leaf_pem,
            chain_pem = chain_pem,
            ca_pem    = ca_pem,
            key_pem   = key_pem,   # Renew keeps the same key by default
        )

        info = issued.inspect()
        logger.info(
            "Certificate renewed: CN=%s not_after=%s",
            info["subject"], info["not_after"]
        )
        return issued

    def start_renewal_daemon(
        self,
        initial_cert: "IssuedCertificate",
        *,
        renewal_fraction: float = 2 / 3,
        on_renewal:       "Callable[[IssuedCertificate], None] | None" = None,
        on_error:         "Callable[[Exception], None] | None" = None,
        max_retries:      int   = 5,
        retry_base_delay: float = 60.0,   # seconds for first retry
    ) -> "RenewalDaemon":
        """
        Start a background thread that automatically renews the certificate.

        The daemon sleeps until renewal_fraction of the certificate's
        lifetime has elapsed, then renews. It continues indefinitely,
        updating the cert reference after each renewal.

        Args:
            initial_cert:     The certificate to renew (will be mutated on renewal)
            renewal_fraction: When to renew — 2/3 of lifetime by default
            on_renewal:       Optional callback invoked after each renewal
                              with the new IssuedCertificate
            on_error:         Optional callback invoked on renewal failure
            max_retries:      Retry attempts before giving up on a renewal cycle
            retry_base_delay: Base delay (seconds) for exponential backoff

        Returns:
            RenewalDaemon — call .stop() to terminate the thread
        """
        daemon = RenewalDaemon(
            ca               = self,
            cert             = initial_cert,
            renewal_fraction = renewal_fraction,
            on_renewal       = on_renewal,
            on_error         = on_error,
            max_retries      = max_retries,
            retry_base_delay = retry_base_delay,
        )
        daemon.start()
        logger.info(
            "Renewal daemon started (fraction=%.2f, max_retries=%d)",
            renewal_fraction, max_retries
        )
        return daemon


class RenewalDaemon:
    """
    Background thread that renews a certificate automatically.

    Create via StepCAClient.start_renewal_daemon().
    """

    def __init__(
        self,
        ca:               StepCAClient,
        cert:             IssuedCertificate,
        renewal_fraction: float,
        on_renewal:       "Callable | None",
        on_error:         "Callable | None",
        max_retries:      int,
        retry_base_delay: float,
    ) -> None:
        self._ca               = ca
        self._cert             = cert
        self._fraction         = renewal_fraction
        self._on_renewal       = on_renewal
        self._on_error         = on_error
        self._max_retries      = max_retries
        self._retry_base_delay = retry_base_delay
        self._stop_event       = threading.Event()
        self._thread           = threading.Thread(
            target = self._run,
            daemon = True,   # exits when the main thread exits
            name   = "step-ca-renewal",
        )

    @property
    def current_cert(self) -> IssuedCertificate:
        """The most recently issued (or renewed) certificate."""
        return self._cert

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        """Signal the daemon to stop. Blocks until the thread exits."""
        self._stop_event.set()
        self._thread.join(timeout=5.0)

    def _sleep_until_renewal(self) -> None:
        """Sleep until it is time to renew based on the renewal fraction."""
        leaf_cert  = x509.load_pem_x509_certificate(
            self._cert.cert_pem.encode()
        )
        not_before = leaf_cert.not_valid_before_utc
        not_after  = leaf_cert.not_valid_after_utc
        lifetime   = (not_after - not_before).total_seconds()
        renewal_at = not_before.timestamp() + lifetime * self._fraction

        now        = time.time()
        sleep_secs = renewal_at - now

        # Add ±10% jitter to prevent thundering herd
        jitter = sleep_secs * 0.10 * (random.random() * 2 - 1)
        sleep_secs = max(0.0, sleep_secs + jitter)

        if sleep_secs > 0:
            logger.debug(
                "Renewal daemon sleeping %.0fs (renews at %s)",
                sleep_secs,
                datetime.datetime.fromtimestamp(renewal_at).isoformat()
            )
            self._stop_event.wait(timeout=sleep_secs)

    def _run(self) -> None:
        """Main loop: sleep → renew → update cert → repeat."""
        while not self._stop_event.is_set():
            self._sleep_until_renewal()

            if self._stop_event.is_set():
                break

            # Attempt renewal with exponential backoff
            for attempt in range(1, self._max_retries + 1):
                try:
                    new_cert = self._ca.renew(
                        self._cert.cert_pem,
                        self._cert.key_pem,
                    )
                    self._cert = new_cert

                    if self._on_renewal:
                        try:
                            self._on_renewal(new_cert)
                        except Exception:
                            logger.warning(
                                "on_renewal callback raised an exception",
                                exc_info=True
                            )

                    logger.info("Certificate renewed successfully (attempt %d)", attempt)
                    break

                except Exception as exc:
                    logger.warning(
                        "Renewal attempt %d/%d failed: %s",
                        attempt, self._max_retries, exc
                    )
                    if self._on_error:
                        try:
                            self._on_error(exc)
                        except Exception:
                            pass

                    if attempt < self._max_retries:
                        backoff = self._retry_base_delay * (2 ** (attempt - 1))
                        logger.debug("Retrying in %.0fs", backoff)
                        self._stop_event.wait(timeout=backoff)
                    else:
                        logger.error(
                            "Renewal failed after %d attempts; "
                            "certificate will expire at %s",
                            self._max_retries,
                            x509.load_pem_x509_certificate(
                                self._cert.cert_pem.encode()
                            ).not_valid_after_utc.isoformat()
                        )
```

---

## Using the Renewal Daemon

```python
# demo_renewal.py

from step_ca_client import StepCAClient
import time, logging

logging.basicConfig(level=logging.INFO)

ca = StepCAClient(
    ca_url               = "https://localhost:9000",
    root_fingerprint     = "702a094e...",
    provisioner_name     = "admin@example.com",
    provisioner_password = "provisioner-secret",
)

# Issue the initial certificate
cert = ca.sign("myservice.internal", sans=["myservice.internal"])
cert.save("myservice.crt", "myservice.key")

# Track what cert file is in use
current_cert_path = "myservice.crt"

def on_renewal(new_cert):
    """Called after each successful renewal."""
    new_cert.save("myservice.crt", "myservice.key")
    info = new_cert.inspect()
    print(f"Renewed: now expires {info['not_after']}")
    # Your service can also be notified here to reload the cert
    # e.g. os.kill(os.getpid(), signal.SIGHUP)

def on_error(exc):
    """Called on each failed renewal attempt."""
    print(f"Renewal error (will retry): {exc}")

# Start the daemon
daemon = ca.start_renewal_daemon(
    initial_cert     = cert,
    renewal_fraction = 2/3,    # renew at 2/3 of cert lifetime
    on_renewal       = on_renewal,
    on_error         = on_error,
)

# Your main service logic runs here
try:
    print("Service running. Press Ctrl+C to stop.")
    while True:
        # The daemon transparently keeps the cert fresh
        # daemon.current_cert always has the latest issued cert
        time.sleep(60)
except KeyboardInterrupt:
    pass
finally:
    daemon.stop()
    print("Daemon stopped.")
```

---

## What's Next: Taking Back the Key

In **Episode 7**, we add `revoke()` — the ability to cancel a certificate before its expiry. Revocation uses either a JWT token (similar to signing) or an mTLS connection presenting the certificate to be revoked. We cover both paths, all reason codes, and what "passive revocation" means for short-lived cert strategies.

---

**🔗 Resources**
- **step-ca renewal documentation**: [smallstep.com/docs/step-ca/renewal](https://smallstep.com/docs/step-ca/renewal/)
- **Passive revocation (short-lived certs)**: [smallstep.com/blog/passive-revocation](https://smallstep.com/blog/passive-revocation.html)
- **mTLS with Python**: [python-httpx.org/advanced/client-credentials](https://www.python-httpx.org/advanced/)

---

*🔐 REST with step-ca — automating certificate lifecycle one HTTP call at a time.*
