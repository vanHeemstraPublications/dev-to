---
title: "Call My Hostname 🗂️ Ep.2"
published: false
description: "Designing a simple, file-based hostname pool that guarantees every virtual machine gets a unique name before it is ever provisioned."
tags: networking, infrastructure, python, dns
series: Call My Hostname
part: 2
organization: "the-software-s-journey"
---

# Episode 2: The Allocation Ledger

## The problem with naming a VM when you create it

The natural instinct is to name the VM at the moment you create it: "this is for the finance team, call it fin-app-01." That works until someone else, weeks later, also needs a machine for finance and also types `fin-app-01`. Naming at creation time invites collisions because there is no shared state being checked.

The fix is to separate two decisions that feel like one:

1. **What is this machine for** (a label humans use in tickets, inventories, tags)
2. **What is its hostname** (a machine-generated, guaranteed-unique identifier used by DNS and the operating system)

This episode only deals with decision 2.

## Designing the naming scheme

A pattern like `vm1234.vms.company.internal` has three parts:

- `vm` — a fixed prefix so anyone reading a hostname immediately knows it is a virtual machine, not a switch, printer, or physical server
- `1234` — a number drawn from a pool, never reused while the machine exists
- `.vms.company.internal` — a DNS zone dedicated to VMs, kept separate from your public or general-purpose internal zone

Using a numeric suffix instead of a descriptive name is what actually prevents collisions. Descriptive names are for tags and CMDB entries, not for the hostname itself.

## The ledger

The ledger is the single source of truth for which numbers are taken. It does not need a database engine for a small or medium fleet; a plain text file under version control, or a simple SQLite file, is enough, as long as only one process can write to it at a time.

Here is a minimal but correct implementation using SQLite, which gives you file locking for free and survives concurrent requests better than a flat file:

```python
#!/usr/bin/env python3
"""hostname_ledger.py — allocate and release hostnames from a numeric pool."""

import sqlite3
import sys
from contextlib import closing

DB_PATH = "/var/lib/hostname-ledger/ledger.db"
POOL_START = 1000
POOL_END = 9999
DOMAIN_SUFFIX = "vms.company.internal"


def init_db(path: str = DB_PATH) -> None:
    with closing(sqlite3.connect(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS allocations (
                number INTEGER PRIMARY KEY,
                hostname TEXT NOT NULL UNIQUE,
                mac_address TEXT,
                allocated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def allocate(mac_address: str, path: str = DB_PATH) -> str:
    """Return a free hostname and record it against a MAC address."""
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("BEGIN IMMEDIATE")  # lock the DB for this transaction
        existing = conn.execute(
            "SELECT number FROM allocations WHERE mac_address = ?", (mac_address,)
        ).fetchone()
        if existing:
            conn.rollback()
            number = existing[0]
            return f"vm{number}.{DOMAIN_SUFFIX}"

        taken = {row[0] for row in conn.execute("SELECT number FROM allocations")}
        for number in range(POOL_START, POOL_END + 1):
            if number not in taken:
                hostname = f"vm{number}.{DOMAIN_SUFFIX}"
                conn.execute(
                    "INSERT INTO allocations (number, hostname, mac_address) VALUES (?, ?, ?)",
                    (number, hostname, mac_address),
                )
                conn.commit()
                return hostname
        conn.rollback()
        raise RuntimeError("hostname pool exhausted")


def release(mac_address: str, path: str = DB_PATH) -> None:
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("DELETE FROM allocations WHERE mac_address = ?", (mac_address,))
        conn.commit()


if __name__ == "__main__":
    init_db()
    if len(sys.argv) < 3:
        print("usage: hostname_ledger.py [allocate|release] <mac_address>")
        sys.exit(1)
    action, mac = sys.argv[1], sys.argv[2].lower()
    if action == "allocate":
        print(allocate(mac))
    elif action == "release":
        release(mac)
    else:
        print(f"unknown action: {action}")
        sys.exit(1)
```

A few design points worth explaining to an apprentice:

- **Idempotency by MAC address.** If the same physical or virtual NIC asks for a hostname twice (a re-run of a provisioning script, a retry after a timeout), it gets back the *same* hostname instead of consuming a second number. This is why the MAC address is stored, not just the hostname.
- **`BEGIN IMMEDIATE`** takes a write lock on the SQLite file for the duration of the transaction, so two provisioning requests arriving at the same second cannot both grab the same number.
- **Release is explicit.** When a VM is decommissioned, its number should go back into the pool deliberately, not automatically on some timer, so a mistaken deallocation does not let a still-running machine's name be handed to someone else.

## Where this fits in the pipeline

This script is called once, at the very start of provisioning a new VM, before the VM is created and before cloud-init is asked to do anything. Its only output is a string like `vm1234.vms.company.internal`, which the next episode will inject into the machine.

## SIPOC for this episode

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Provisioning script / operator | MAC address of the new VM's NIC | Query the ledger, allocate the next free number, record the mapping | A unique hostname string | cloud-init seed generator (Part 3) |

## Coming up in Part 3

With a guaranteed-unique hostname in hand, the next step is getting that string into the virtual machine's operating system the moment it boots for the first time, using cloud-init's NoCloud datasource.
