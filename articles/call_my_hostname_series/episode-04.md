---
title: "Call My Hostname 🔌 Ep.4"
published: false
description: "Configuring DHCP static reservations so a virtual machine always receives the same IP address, and passing its hostname along as DHCP Option 12."
tags: dhcp, networking, infrastructure, linux
series: Call My Hostname
part: 4
organization: "the-software-s-journey"
---

# Episode 4: Wiring MAC to Name

## Why the IP address needs to be stable before DNS can help

DNS maps a name to an IP address. If the IP address changes every time the VM reboots, whatever created that DNS record has to run again every time, which is fragile and delays resolution. The cleaner approach is to make the DHCP server always hand out the *same* IP to the *same* MAC address, so the DNS record, once created, stays valid for the life of the machine.

This is a **static reservation**, not a static IP configured inside the VM's network settings. The VM still uses DHCP; the DHCP server is simply told "if you see this MAC address, always offer this exact address," which keeps IP management centralized instead of scattered across every VM's own configuration.

## Choosing Kea over ISC dhcpd

ISC dhcpd, the traditional Unix DHCP server, is now in maintenance mode upstream; **Kea**, from the same project (ISC), is its actively developed replacement, configured in JSON rather than dhcpd's own syntax, and has first-class support for the dynamic DNS updates covered in Part 5. This episode uses Kea.

## A minimal Kea configuration with a static reservation

```json
{
  "Dhcp4": {
    "interfaces-config": {
      "interfaces": ["eth0"]
    },
    "lease-database": {
      "type": "memfile",
      "persist": true,
      "name": "/var/lib/kea/kea-leases4.csv"
    },
    "subnet4": [
      {
        "id": 1,
        "subnet": "10.20.30.0/24",
        "pools": [
          { "pool": "10.20.30.100 - 10.20.30.200" }
        ],
        "option-data": [
          { "name": "routers", "data": "10.20.30.1" },
          { "name": "domain-name-servers", "data": "10.20.30.10" },
          { "name": "domain-name", "data": "vms.company.internal" }
        ],
        "reservations": [
          {
            "hw-address": "aa:bb:cc:dd:ee:ff",
            "ip-address": "10.20.30.150",
            "hostname": "vm1234"
          }
        ]
      }
    ]
  }
}
```

Three things worth explaining carefully to an apprentice:

- **`pools` vs `reservations`.** The `pools` range is for dynamic, unreserved leases — anything without a matching reservation gets a temporary address from that range. `reservations` sit outside that logic entirely: Kea checks reservations first, and a reserved address does not need to fall inside the dynamic pool range at all (in this example it deliberately does not).
- **The `hostname` field inside the reservation** is what Kea will both offer to the client via DHCP Option 12, and — critically for Part 5 — use as the name it registers in DNS. This must match, exactly, the hostname you injected via cloud-init in Part 3. If these two do not match, the machine will believe it is called one thing while DNS says another.
- **`hw-address`** is the MAC address, the same one used as the key in the hostname ledger from Part 2. This is the thread that ties all three episodes together: one MAC address, one ledger entry, one cloud-init seed, one DHCP reservation.

## Automating reservation creation

Since reservations should be generated from the same ledger as the hostname, not typed by hand, extend the allocation script from Part 2 to also emit a Kea reservation fragment:

```python
#!/usr/bin/env python3
"""kea_reservation.py — emit a Kea DHCPv4 reservation block for an allocated host."""

import json
import sys

def build_reservation(mac_address: str, ip_address: str, hostname_short: str) -> dict:
    return {
        "hw-address": mac_address,
        "ip-address": ip_address,
        "hostname": hostname_short,
    }

if __name__ == "__main__":
    mac, ip, hostname_short = sys.argv[1], sys.argv[2], sys.argv[3]
    print(json.dumps(build_reservation(mac, ip, hostname_short), indent=2))
```

In practice, the IP address itself can come from a small IP pool ledger identical in structure to the hostname ledger in Part 2 (a table of `ip_address`, `mac_address`, `allocated_at`), so that IP allocation and hostname allocation both draw from tracked, non-overlapping pools rather than "the next free-looking address."

## Applying the change

Kea reloads its configuration without dropping active leases:

```bash
kea-dhcp4 -t /etc/kea/kea-dhcp4.conf   # syntax-check first
systemctl reload kea-dhcp4-server
```

## Verifying the reservation is honored

From the DHCP server, watch the lease get issued:

```bash
tail -f /var/log/kea/kea-dhcp4.log
```

From the VM itself, after a reboot or a manual DHCP renew:

```bash
ip -4 addr show eth0
hostname -f
```

The IP shown should match the reservation, and `hostname -f` should still show the FQDN set by cloud-init in Part 3 — these are two independent confirmations that both halves of the pipeline agree with each other.

## SIPOC for this episode

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Hostname + IP ledgers (Part 2) | MAC address, allocated IP, allocated hostname | Create a Kea static reservation | A VM that always receives the same IP and advertises the correct hostname via DHCP | Dynamic DNS update (Part 5) |

## Coming up in Part 5

DHCP now knows the hostname and IP address together, but knowing is not the same as telling DNS. Part 5 wires Kea to push that information into BIND automatically, using RFC 2136 dynamic updates.

