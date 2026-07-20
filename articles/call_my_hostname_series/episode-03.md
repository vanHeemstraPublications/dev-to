---
title: "Call My Hostname 📦 Ep.3"
published: false
description: "Using cloud-init's NoCloud datasource to inject an allocated hostname into a virtual machine at first boot, with no cloud metadata service available."
tags: cloudinit, linux, virtualization, infrastructure
series: Call My Hostname
organization: "the-software-s-journey"
part: 3
---

# Episode 3: Building the Seed

## What cloud-init needs, and why NoCloud

cloud-init is the program, already installed in most modern Linux cloud images, that runs during first boot and configures the operating system: hostname, users, SSH keys, package installs, and more. It reads its configuration from a "datasource." In AWS, Azure, or GCP, the datasource is a metadata HTTP service reachable at a fixed IP address. On-premise, with KVM, libvirt, or Proxmox, there is no such service, so cloud-init falls back to the **NoCloud** datasource, which reads its configuration from a small virtual disk (an ISO image or raw disk) attached to the VM.

That virtual disk needs exactly two files:

- `meta-data` — identifies the instance
- `user-data` — the actual configuration, including the hostname

## meta-data

```yaml
instance-id: vm1234
local-hostname: vm1234
```

`instance-id` must be unique per VM and, importantly, must change if you ever reuse a disk image for a different VM — cloud-init uses it to decide "have I already configured this machine," and will skip configuration entirely on a matching instance-id.

## user-data

```yaml
#cloud-config
hostname: vm1234
fqdn: vm1234.vms.company.internal
manage_etc_hosts: true

# Optional but recommended: make the hostname visible immediately in the shell prompt
preserve_hostname: false
```

`manage_etc_hosts: true` tells cloud-init to also write a matching entry into `/etc/hosts`, which avoids a common symptom where `hostname -f` returns the FQDN correctly but local tools that only check `/etc/hosts` still see the old or generic name.

## Generating the seed image

The two files above need to become an ISO that gets attached to the VM as a virtual CD-ROM. `cloud-localds`, part of the `cloud-image-utils` package on Debian/Ubuntu (or `cloud-utils` on RHEL-family systems), builds this in one command:

```bash
#!/usr/bin/env bash
# generate_seed.sh — build a NoCloud seed ISO for a given hostname
set -euo pipefail

HOSTNAME_SHORT="$1"      # e.g. vm1234
FQDN="${HOSTNAME_SHORT}.vms.company.internal"
OUTPUT_DIR="/var/lib/vm-seeds"
SEED_ISO="${OUTPUT_DIR}/${HOSTNAME_SHORT}-seed.iso"

mkdir -p "${OUTPUT_DIR}"

cat > /tmp/meta-data <<EOF
instance-id: ${HOSTNAME_SHORT}
local-hostname: ${HOSTNAME_SHORT}
EOF

cat > /tmp/user-data <<EOF
#cloud-config
hostname: ${HOSTNAME_SHORT}
fqdn: ${FQDN}
manage_etc_hosts: true
preserve_hostname: false
EOF

cloud-localds "${SEED_ISO}" /tmp/user-data /tmp/meta-data

echo "seed ISO created at ${SEED_ISO}"
```

Run it with the hostname allocated in Episode 2:

```bash
HOSTNAME=$(python3 hostname_ledger.py allocate aa:bb:cc:dd:ee:ff)
SHORT_NAME="${HOSTNAME%%.*}"        # strips the domain, keeps "vm1234"
./generate_seed.sh "${SHORT_NAME}"
```

## Attaching the seed to the VM

With `virt-install` (libvirt/KVM), the seed ISO is attached as a second CD-ROM device alongside the OS disk:

```bash
virt-install \
  --name vm1234 \
  --memory 4096 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/vm1234.qcow2,size=20 \
  --disk path=/var/lib/vm-seeds/vm1234-seed.iso,device=cdrom \
  --network network=vm-bridge,mac=aa:bb:cc:dd:ee:ff \
  --os-variant ubuntu22.04 \
  --import \
  --noautoconsole
```

Note that `--name vm1234` here is only the libvirt-level object name shown in `virsh list`; it has no bearing on the guest operating system's actual hostname, which comes entirely from the seed ISO. This is the decoupling described in Part 1: the hypervisor's label for the VM and the VM's own hostname are two independent strings that happen, in this example, to look similar.

## Verifying at first boot

Once the VM finishes its first boot, confirm cloud-init actually applied the configuration:

```bash
cloud-init status --long
hostnamectl status
cat /etc/hosts
```

`hostnamectl status` should show `Static hostname: vm1234` and `Transient hostname` (if set) matching, and `/etc/hosts` should contain a line mapping `127.0.1.1` (or similar) to `vm1234.vms.company.internal vm1234`.

## SIPOC for this episode

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Hostname ledger (Episode 2) | Allocated hostname string | Generate NoCloud meta-data/user-data, build seed ISO, attach to VM | A VM whose OS hostname matches the allocated name | DHCP/DNS provisioning (Episodes 4 and 5) |

## Coming up in Episode 4

The hostname now lives correctly inside the VM. Next, that VM's network interface needs to receive the same IP address every time it boots, so that DNS can point to something stable.

