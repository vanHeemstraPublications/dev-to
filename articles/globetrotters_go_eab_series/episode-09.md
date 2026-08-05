---
title: "Globetrotters go EAB 👥 Ep.9"
series: "Globetrotters go EAB"
part: 9
organization: "the-software-s-journey"
tags: [rsync, ansible, centralized, standalone, certbot]
---

## Episode 9: Solo Travel or the Group Tour: Standalone vs Centralized

Here's a question every fleet with more than one server eventually asks: does every machine need its own sponsor letter and its own border crossing, or can the whole group travel on one set of papers? `idem-certbot` bakes the answer into a single Ansible variable, `certbot_mode`, and it's worth seeing exactly how the group-tour option actually works, because it's considerably more hands-on than "just copy the files somewhere."

**Standalone** is solo travel: every host in `certbot_nodes` runs its own `idem-certbot` container, registers its own account, and requests its own certificates, entirely independently. This is the default, and it's the option with the smallest blast radius — a compromised or broken node affects exactly that node.

**Centralized** is the group tour, and it works like this: one node in `certbot_nodes` — the one actually reachable on port 80 for the standalone HTTP-01 challenge from Episode 6 — does the real border crossing and ends up holding the genuine, freshly-issued certificates under its own `certbot_data_volume`. Every other machine, listed under `rsync_targets` in the inventory, receives a courier delivery of those exact same certificate files on a schedule, via a cron job installed by Ansible:

```
*/15 * * * *	root	/usr/local/bin/rsync_certbot.sh
```

Every fifteen minutes, the certificate-holding node runs this:

```bash
#!/bin/bash
set -euo pipefail

ip_addresses=("xxx.xxx.xxx.xxx" "yyy.yyy.yyy.yyy" "zzz.zzz.zzz.zzz")
SRC_DIR="/srv/certbot"
SSH_KEY="/home/certbot/.ssh/id_ed25519_certbot"
USER="certbot"

chown -R "$USER":"$USER" "$SRC_DIR"

if [ -d "$SRC_DIR" ]; then
    tar -cf - --exclude last_update -C "$SRC_DIR" . | sha1sum > "$SRC_DIR/last_update"

    for HOST_IP in "${ip_addresses[@]}"; do
        if rsync -a -s -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" "$SRC_DIR/" "$USER@$HOST_IP:$SRC_DIR/"; then
            echo "$(date) [sync] Rsync della cartella $SRC_DIR correttamente effettuato! - Host: $HOST_IP" >> /var/log/rsync-certbot.log
        else
            echo "$(date) [sync] ERRORE Rsync fallito per Host: $HOST_IP" >> /var/log/rsync-certbot.log
        fi
    done
fi
```

A dedicated `certbot` system user does the couriering, authenticating over SSH with a dedicated key pair (`ssh-keygen -t ed25519 -f .../id_ed25519_certbot`) that Ansible provisions and installs as an authorized key on every `rsync_targets` host — you'll notice from the inventory that `certbot_nodes` and `rsync_targets` are deliberately separate groups: the issuing node runs the container and the cron job; the target nodes just need the `certbot` user and its authorized key waiting, ready to receive a delivery. Before every courier run, the script also tars up the whole certificate directory (minus its own tracking file) and writes a SHA-1 hash to `last_update` — a paper trail proving exactly what state was shipped out on each round, even though `rsync -a` is what actually decides what needs copying.

The one thing centralized mode does *not* do is make the receiving nodes run Certbot at all. They never talk to the ACME server, never see the `KEY_ID` or `HMAC_KEY`, and never make an EAB decision of their own — they simply end up, every fifteen minutes, with an exact copy of whatever the one designated traveler brought back from the border. One sponsor letter, one border crossing, and a courier route doing the rest.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `certbot_nodes` group (the issuing node) | Its own `idem-certbot` container's freshly issued/renewed certificates | Tar, hash, and rsync the certificate directory to every `rsync_targets` host | An up-to-date certificate copy on every target, every 15 minutes | `rsync_targets` hosts serving the same certificate |
| Ansible (`rsync_sender.yml` / `rsync_receiver.yml`) | An SSH key pair and the `certbot_mode: centralized` setting | Provision the sender's key, the cron job, and the receiver's authorized key | A working, unattended courier route between nodes | The `certbot` system user on both ends |
| `cron` (`*/15 * * * *`) | The scheduled trigger | Run `rsync_certbot.sh` on a fixed interval | Regular, automatic redelivery regardless of when a renewal happens | Every `rsync_targets` host |

Next stop: the Ansible deploy step itself — and the deliberately paranoid thing it does to the secrets file the moment the container is safely up and running.
