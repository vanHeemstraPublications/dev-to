---
title: "Call My Hostname 🔍 Ep.6"
published: false
description: "An end-to-end verification checklist for the on-premise hostname pipeline, common failure points at each layer, and a reconciliation script for environments without dynamic DNS."
tags: dns, dhcp, troubleshooting, infrastructure
series: Call My Hostname
part: 6
organization: "the-software-s-journey"
---

# Episode 6: Proving It Works

## Walking the chain in order

When something is wrong, resist the urge to jump straight to DNS, since DNS is usually the last symptom of a problem that started two layers earlier. Check each link in the order it was built across this series.

### 1. Was a hostname actually allocated

```bash
sqlite3 /var/lib/hostname-ledger/ledger.db \
  "SELECT * FROM allocations WHERE mac_address = 'aa:bb:cc:dd:ee:ff';"
```

If this returns nothing, the VM was provisioned without going through the ledger from Part 2 — nothing downstream can be correct, because there is no record of what it was supposed to be called.

### 2. Did cloud-init apply it inside the VM

From inside the VM:

```bash
cloud-init status --long
hostnamectl status
```

Look specifically for `status: done` with no errors. A common failure is the seed ISO not being attached at all, in which case cloud-init falls back to `None` datasource behavior and leaves the hypervisor-assigned name in place — the VM will boot successfully, but with the wrong hostname, which looks fine until someone tries to reach it by its intended name.

If `cloud-init status` shows an error, the detailed log is here:

```bash
less /var/log/cloud-init.log
```

### 3. Did DHCP hand out the reserved IP, not a pool IP

From the DHCP server:

```bash
grep -A2 "aa:bb:cc:dd:ee:ff" /var/lib/kea/kea-leases4.csv
```

If the leased IP does not match the reservation from Part 4, check that the reservation's `hw-address` is lowercase and colon-separated exactly as Kea expects, and that the MAC address the VM actually presents on the wire matches what was recorded in the ledger — a VM cloned from a template sometimes inherits the template's original MAC rather than getting a fresh one, which silently reassigns the template's reservation.

### 4. Did the DNS record get created

```bash
dig vm1234.vms.company.internal @10.20.30.10 A
dig -x 10.20.30.150 @10.20.30.10
```

If forward resolution works but reverse does not (or the other way around), re-check that `allow-update` is set on *both* zones in BIND's configuration, as shown in Part 5 — this is the most common half-working state.

If neither resolves, check the DDNS component's log, since a TSIG key mismatch is rejected there before it ever reaches BIND:

```bash
journalctl -u kea-dhcp-ddns -n 100 --no-pager
```

### 5. Confirm from a third machine, not the VM itself

A VM can often resolve its own name via `/etc/hosts` even when DNS is broken for everyone else, because `manage_etc_hosts: true` (Part 3) wrote a local entry. Always confirm resolution from a separate machine on the network to be sure DNS itself, not just local host file resolution, is working.

## What to do when dynamic DNS is not available

Some organizations will not permit RFC 2136 updates for security policy reasons, even with TSIG. In that case, Part 5's live update mechanism is replaced with a periodic reconciliation script that compares DHCP leases against DNS records and reports (or fixes) drift:

```python
#!/usr/bin/env python3
"""reconcile_dns.py — compare Kea leases against BIND zone records and report drift."""

import csv
import subprocess

LEASES_FILE = "/var/lib/kea/kea-leases4.csv"
DNS_SERVER = "10.20.30.10"
ZONE = "vms.company.internal"


def read_active_leases(path: str) -> dict[str, str]:
    """Return {hostname: ip_address} for currently valid leases."""
    leases = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("hostname") and row.get("address"):
                leases[row["hostname"]] = row["address"]
    return leases


def resolve(hostname: str) -> str | None:
    fqdn = f"{hostname}.{ZONE}"
    result = subprocess.run(
        ["dig", "+short", fqdn, f"@{DNS_SERVER}", "A"],
        capture_output=True, text=True, check=False,
    )
    answer = result.stdout.strip()
    return answer or None


def main() -> None:
    leases = read_active_leases(LEASES_FILE)
    drift_found = False
    for hostname, expected_ip in leases.items():
        actual_ip = resolve(hostname)
        if actual_ip != expected_ip:
            drift_found = True
            print(
                f"DRIFT: {hostname}.{ZONE} expected {expected_ip}, "
                f"DNS reports {actual_ip or 'no record'}"
            )
    if not drift_found:
        print("no drift detected")


if __name__ == "__main__":
    main()
```

Run this from cron every few minutes. It only reports drift here; extending it to call `nsupdate` and correct the record automatically is a reasonable next step once you trust the comparison logic, but keep the two responsibilities (detecting vs. fixing) in separate, individually testable functions.

## The five questions to ask, in order

| Layer | Question | Command to answer it |
|---|---|---|
| Ledger | Was a hostname allocated for this MAC? | Query the SQLite ledger |
| cloud-init | Did the VM apply the hostname at boot? | `cloud-init status --long`, `hostnamectl status` |
| DHCP | Did the VM get its reserved IP, not a pool IP? | Check the Kea lease file against the reservation |
| DNS update | Did the record get created in both zones? | `dig` forward and reverse, from another host |
| DDNS transport | If DNS is wrong, did the update even arrive? | `journalctl -u kea-dhcp-ddns` |

## Closing note for the series

Across six episodes, one MAC address flowed through five independent systems — a ledger, cloud-init, Kea, BIND, and a verification script — each with a single, narrow responsibility. None of them individually "does hostname management." The reliability comes from the fact that each layer can be checked and fixed on its own, which is the entire point of building this on-premise instead of relying on a single cloud platform to hide it all behind one API call.

## SIPOC for this episode

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| All previous episodes' systems | Ledger entries, cloud-init logs, DHCP leases, DNS zone state | Layer-by-layer verification, or periodic reconciliation | Confirmed or corrected hostname-to-IP mapping | Network/infrastructure apprentice operating the pipeline |

