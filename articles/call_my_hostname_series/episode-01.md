---
title: "Call My Hostname 🏷️ Ep.1"
published: false
description: "Why on-premise virtual machines need a hostname allocation strategy that is separate from the machine's identity in your hypervisor, and the architecture we will build across this series."
tags: networking, dns, dhcp, infrastructure
series: Call My Hostname
organization: "the-software-s-journey"
---

# Episode 1: The Problem with Machine1

## Why this series exists

If you provision virtual machines by hand, or with a template that always names the VM object "machine1" or copies a base image without changing anything, you will eventually get two machines answering to the same name on the same network. DHCP will hand out a hostname option nobody asked for, DNS will silently overwrite one record with another, and whoever is troubleshooting at 2 AM will not know which physical box "machine1" actually is.

The fix is not "be more careful with names." The fix is to treat the hostname as a resource that is allocated, tracked, and injected into the machine at boot time, independently of whatever the hypervisor or the person provisioning it decided to call the VM object. This series builds that pipeline entirely on-premise, with no cloud metadata service and no cloud DNS auto-registration to lean on.

## What "on-premise" changes

In a cloud environment, a metadata service answers questions like "what is my hostname supposed to be" the moment the VM boots, and the cloud's own DNS quietly registers whatever hostname it is told. On-premise, none of that exists by default. You have to build each piece yourself:

- something that decides the hostname before the VM ever boots
- something that gets that hostname into the VM's operating system
- something that connects an IP address to that hostname in DNS, so other machines can actually find it by name

Three separate concerns, three separate technologies, and this series gives each one its own episode.

## The architecture, end to end

| Step | Technology | Question it answers |
|---|---|---|
| 1 | A hostname pool (a ledger) | Which name, from a pre-generated list, is still free? |
| 2 | cloud-init NoCloud datasource | How does that name get written into the VM's `/etc/hostname` at first boot? |
| 3 | DHCP static reservation (Kea or ISC dhcpd) | How does the VM's network interface (identified by MAC address) always receive the same IP? |
| 4 | Dynamic DNS update (RFC 2136) | How does DHCP tell DNS "this IP now belongs to this hostname"? |
| 5 | Verification tooling | How do you prove the whole chain worked, and fix it when it did not? |

By the end of the series, a newly created VM will boot, receive the name `vm1234.vms.company.internal` (not "machine1"), get a reserved IP address tied to its MAC address, and have that IP and name appear correctly in DNS, without a human typing any of it in by hand at boot time.

## SIPOC for this episode

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Infrastructure architect | Requirement: unique, collision-free hostnames | Define the five-step pipeline | A documented architecture and episode roadmap | Network/infra apprentice reading this series |

## What is deliberately out of scope

This series assumes Linux VMs, ISC dhcpd or Kea as the DHCP server, and BIND9 as the DNS server, because that combination is the most transparent for learning the underlying protocols. If your organization runs Windows Server with Active Directory-integrated DNS, the same five steps apply, but step 4 becomes "secure dynamic update" handled natively between the Windows DHCP and DNS roles rather than an explicit TSIG key exchange. The concepts transfer; the commands do not.

## Coming up in Episode 2

Before any VM boots, you need a source of truth for which hostnames exist and which ones are still available. Episode 2 builds that ledger.

