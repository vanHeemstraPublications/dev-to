---
title: "Call My Hostname 🔁 Ep.5"
published: false
description: "Configuring RFC 2136 dynamic DNS updates so that Kea automatically creates and removes DNS records in BIND as leases are granted and released."
tags: dns, dhcp, bind, infrastructure
series: Call My Hostname
part: 5
organization: "the-software-s-journey"
---

# Episode 5: Teaching DHCP to Talk to DNS

## What "dynamic update" actually means

Ordinarily, a DNS zone file is edited by a human or a configuration management tool, and the DNS server is told to reload. **Dynamic update**, defined in RFC 2136, is a protocol that lets another system — in this case, the DHCP server — add or remove individual records in a running zone over the network, without editing the zone file directly and without a reload. Kea supports this natively through its `dhcp-ddns` component, `kea-dhcp-ddns`.

This is the step that finally makes `vm1234.vms.company.internal` resolve to `10.20.30.150` without anyone hand-editing a zone file.

## Security: TSIG

Any server accepting unauthenticated updates to its zone data is a serious problem — anyone on the network could claim any name. RFC 2136 updates are therefore authenticated with a **TSIG key**, a shared secret that both BIND and Kea know, sent as part of each update request.

Generate the key with BIND's own tooling:

```bash
tsig-keygen -a hmac-sha256 kea-ddns-key
```

This prints a `key` block. Save it; you will place a copy in both BIND's and Kea's configuration.

```
key "kea-ddns-key" {
    algorithm hmac-sha256;
    secret "base64-secret-value-here==";
};
```

## Configuring BIND to accept updates

In `named.conf`, reference the key and allow it to update the relevant zone:

```
include "/etc/bind/kea-ddns-key.conf";

zone "vms.company.internal" {
    type master;
    file "/var/lib/bind/db.vms.company.internal";
    allow-update { key "kea-ddns-key"; };
};

zone "30.20.10.in-addr.arpa" {
    type master;
    file "/var/lib/bind/db.30.20.10";
    allow-update { key "kea-ddns-key"; };
};
```

Note the second zone: reverse DNS (the `in-addr.arpa` zone) needs `allow-update` too, or you will get forward resolution (`vm1234... → 10.20.30.150`) without reverse resolution (`10.20.30.150 → vm1234...`) — a common half-working state that breaks tools relying on PTR lookups, such as some logging and SSH `known_hosts` checks.

## Configuring Kea's DDNS component

Kea splits this into two pieces: `kea-dhcp4` needs to know it should *ask* for updates, and `kea-dhcp-ddns` needs to know *how* to actually send them to BIND.

In `kea-dhcp4.conf`, add:

```json
{
  "Dhcp4": {
    "dhcp-ddns": {
      "enable-updates": true
    }
  }
}
```

In `kea-dhcp-ddns.conf`:

```json
{
  "DhcpDdns": {
    "ip-address": "127.0.0.1",
    "port": 53001,
    "tsig-keys": [
      {
        "name": "kea-ddns-key",
        "algorithm": "HMAC-SHA256",
        "secret": "base64-secret-value-here=="
      }
    ],
    "forward-ddns": {
      "ddns-domains": [
        {
          "name": "vms.company.internal.",
          "key-name": "kea-ddns-key",
          "dns-servers": [
            { "ip-address": "10.20.30.10", "port": 53 }
          ]
        }
      ]
    },
    "reverse-ddns": {
      "ddns-domains": [
        {
          "name": "30.20.10.in-addr.arpa.",
          "key-name": "kea-ddns-key",
          "dns-servers": [
            { "ip-address": "10.20.30.10", "port": 53 }
          ]
        }
      ]
    }
  }
}
```

Both configuration files reference the same key name, `kea-ddns-key`, and the secret must be byte-for-byte identical to the one BIND was given — a copy-paste mismatch here is the single most common cause of updates silently failing.

## Starting the DDNS component

```bash
systemctl enable --now kea-dhcp-ddns
systemctl restart kea-dhcp4-server
```

## What happens on a lease event

When Kea's DHCP4 process grants (or releases) the reservation created in Part 4, it now sends an internal message to `kea-dhcp-ddns`, which in turn sends a signed RFC 2136 update to BIND, adding (or removing) both the forward A record and the reverse PTR record. No zone file is edited by a human, and no reload of BIND is required — the update happens live, against the running zone.

## Verifying the record actually landed

From any machine that can query the DNS server:

```bash
dig vm1234.vms.company.internal @10.20.30.10 A
dig -x 10.20.30.150 @10.20.30.10
```

The first should return `10.20.30.150`; the second should return `vm1234.vms.company.internal`. If either is empty, check `kea-dhcp-ddns`'s logs first, since a rejected TSIG signature is logged there, not in BIND's general log:

```bash
journalctl -u kea-dhcp-ddns -f
```

## SIPOC for this episode

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Kea DHCP4 (Part 4) | Lease grant/release event, hostname, IP address | Signed RFC 2136 update via kea-dhcp-ddns to BIND | Forward (A) and reverse (PTR) DNS records | Anyone resolving the VM by name (Part 6 verifies this) |

## Coming up in Part 6

Every piece of the pipeline has now been built: allocation, hostname injection, IP reservation, and DNS update. Part 6 walks through verifying the entire chain end to end, and what to check first when one link in it breaks.

