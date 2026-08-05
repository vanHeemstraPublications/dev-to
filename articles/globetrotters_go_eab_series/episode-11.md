---
title: "Globetrotters go EAB 🧷 Ep.11"
series: "Globetrotters go EAB"
part: 11
organization: "the-software-s-journey"
tags: [acme, eab, certbot, garr, wrapup, ansible]
---

## Episode 11: Closing the Passport, Stamps and All

And here we are, back home, unpacking the suitcase one last time. Let's lay every souvenir out on the table, and this time every single one of them is genuine.

Some borders — EAB-gated CAs — want a sponsor letter before they'll even talk to you: a `KEY_ID` and an `HMAC_KEY`, nested into a double-signed JWS that Certbot builds the instant you hand it `--eab-kid` and `--eab-hmac-key`. `idem-certbot` packs the whole itinerary into one small Alpine image built on `certbot/certbot:v5.1.0`, with a single `start.sh` entrypoint that decides EAB-or-not by checking whether `SERVER_URL`, `KEY_ID`, and `HMAC_KEY` are *all* present, registers the account (re-attempting harmlessly on every restart, reading Certbot's own "There is an existing account" response to know which log line to print), parses a genuinely clever `DOMAINS_LIST` syntax into one certificate request per semicolon-separated group, crosses customs using Certbot's own `--standalone` HTTP-01 challenge rather than depending on an external web server, forces every key to RSA 3072 regardless of which border was crossed, and finally settles into an infinite renewal loop checked every `CHECK_FREQ` hours (twelve, by default) — never needing the sponsor letter again, because the binding lives with the account key sitting in your mounted `/etc/letsencrypt` volume.

Lose that volume without a backup, and Episode 8's horror story becomes yours. And if your fleet is bigger than one machine, the real choice isn't "share credentials or don't" — it's Standalone (everyone crosses the border themselves) versus Centralized (one node crosses it, and an rsync courier on a fifteen-minute cron delivers identical certificate files to everyone else, over SSH, with a SHA-1 hash written alongside each delivery as a paper trail). Deploying any of this through Ansible adds one more layer of care worth genuinely admiring: your plaintext sponsor letter gets templated to disk just long enough for `docker compose` to read it, and then the staging folder is deleted outright — and if the container was already running, Ansible restarts it on purpose, because `start.sh`'s registration-and-issuance logic only ever runs once, at startup, and a live renewal loop won't notice a newly added domain on its own.

The full round trip, start to finish, looks like this:

```bash
# 1. Build the suitcase
docker build -f docker/Dockerfile -t idem-certbot:latest .

# 2a. Local deployment: write a docker-compose.yml (Episode 4), then
docker compose up -d

# 2b. Fleet deployment: copy the example inventory, generate an SSH
#     key pair for rsync, fill in group_vars/all.yml (Episode 4 & 9),
#     then let Ansible do the rest
ansible-playbook ansible/playbook.yml \
  -u <remote-user> \
  -i ansible/inventories/<your-folder>/inventory.ini \
  --ask-vault-pass
```

Passport closed, stamps genuine, suitcase back in the closet until the renewal loop quietly handles the next border crossing entirely on its own. Safe travels.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Consortium GARR (`idem-certbot`) | The full lifecycle of ACME registration, EAB or not, issuance, and renewal | Package it into one Docker image and one Ansible role, for solo or fleet deployment | Continuously valid TLS certificates, standalone or centralized | GARR members and any operator with the same border to cross |
| This series | Eleven episodes, now checked directly against the repository's real README, Dockerfile, `start.sh`, and Ansible role | Explain the full lifecycle accurately, from sponsor letter to courier route | A reader who understands both *why* EAB exists and exactly *how* `idem-certbot` operates it | Sysadmins setting up or troubleshooting `idem-certbot` for the first time |
| The reader | Everything covered across this series | Apply it to their own EAB-gated or standard ACME certificate needs, standalone or fleet-wide | A correctly configured, reliably renewing certificate setup | Their own organization's users, relying on a certificate that just works |
