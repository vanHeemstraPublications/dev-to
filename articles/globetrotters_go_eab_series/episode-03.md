---
title: "Globetrotters go EAB 🧳 Ep.3"
series: "Globetrotters go EAB"
part: 3
organization: "the-software-s-journey"
tags: [idem-certbot, docker, garr, certbot, acme]
---

## Episode 3: Packing the Suitcase: What idem-certbot Actually Is

Any seasoned globetrotter will tell you the trip isn't really about the border crossing — it's about the packing beforehand. `idem-certbot` packs remarkably light. The whole travel kit is one `Dockerfile`:

```dockerfile
FROM certbot/certbot:v5.1.0

RUN apk update && apk add --no-cache docker-cli bash

# Copy the startup script and make it executable
COPY --chmod=755 docker/start.sh /usr/local/bin/start.sh

# Set the startup command
ENTRYPOINT ["/usr/local/bin/start.sh"]
```

Alpine-based, built straight on top of the official `certbot/certbot` image, with `bash` added so the startup script has something proper to run in, and the entrypoint pointed at one script that does absolutely everything: read the packing list (environment variables), decide which kind of border this trip is crossing, register the account, request every certificate on the itinerary, and then settle into a renewal loop for as long as the container lives.

Building your own copy of the suitcase is one command, run from the repository root:

```bash
docker build -f docker/Dockerfile -t idem-certbot:latest .
```

And this is where the trip-planning genuinely branches. `idem-certbot` supports two travel styles, chosen with a single Ansible variable (`certbot_mode`) if you're deploying at scale, or simply by how many containers you run if you're doing it by hand:

- **Standalone** — every node is its own solo traveler. It registers its own account, requests its own certificates, and renews entirely on its own. Good for a single VM, or a fleet where each machine's certificate genuinely belongs to that machine alone.
- **Centralized** — one node does the actual border crossing on behalf of the whole group, and its certificates get couriered out to every other node afterward via rsync. Good for a fleet of near-identical servers that all need to present the exact same certificate.

Which style you want changes nothing about the Dockerfile or the ACME conversation itself — both styles run the identical `start.sh` inside the identical container. What changes is what happens *around* the container: whether Ansible also sets up an rsync courier route to other machines, which we'll get to properly a few episodes from now. For the moment, know this: one small Alpine image, one entrypoint script, and a choice of how many friends are coming on the trip.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `certbot/certbot:v5.1.0` (upstream base image) | Alpine + Certbot already installed | Provide the ACME client the rest of the image builds on | A base image `idem-certbot` extends | The `idem-certbot` Dockerfile |
| `docker build -f docker/Dockerfile` | The repository's Dockerfile and `start.sh` | Layer `docker-cli`, `bash`, and the startup script onto the base image | A single, self-contained `idem-certbot` image | Anyone deploying it, locally or via Ansible |
| Deployment choice (Standalone vs Centralized) | The `certbot_mode` variable (or manual choice) | Run the same container either independently per node, or as one source-of-truth node plus rsync targets | Either N independent certificate holders, or 1 issuer + N synced copies | The fleet of servers needing the certificate |

Next stop: the actual packing list — every environment variable this suitcase wants filled in before departure, straight from the README.
