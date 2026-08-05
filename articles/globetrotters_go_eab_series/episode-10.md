---
title: "Globetrotters go EAB 🕵️ Ep.10"
series: "Globetrotters go EAB"
part: 10
organization: "the-software-s-journey"
tags: [ansible, secrets, healthcheck, deployment, security]
---

## Episode 10: The Courier Who Shreds the Note After Delivering It

Every well-trained courier in a spy film does the same thing after handing over the sealed envelope: they burn the note. `idem-certbot`'s Ansible role does exactly this, and it's my favourite small detail in the entire repository. Look closely at `deploy.yml`, and you'll find it deliberately writes your sponsor letter to disk in plain text, uses it, and then deletes the evidence:

```yaml
- name: Create Certbot folder
  ansible.builtin.file:
    path: "/opt/certbot-deploy"
    state: directory

- name: Copy files from template
  ansible.builtin.template:
    src: "{{ item }}"
    dest: "/opt/certbot-deploy/{{ item }}"
  loop:
    - "docker-compose.yml"
    - ".certbot.env"

- name: Ensure Certbot container is defined and pulled
  community.docker.docker_compose_v2:
    project_src: "/opt/certbot-deploy"
    pull: missing
    state: present

# ... start or restart the container, wait for healthy ...

- name: Delete Certbot deployment folder to preserve security
  ansible.builtin.file:
    path: "/opt/certbot-deploy"
    state: absent
```

`.certbot.env` — the templated file actually holding your real `KEY_ID` and `HMAC_KEY`, rendered from Jinja placeholders into your genuine sponsor letter — gets written into `/opt/certbot-deploy`, handed to `docker compose` via `env_file`, read once by the container at startup... and then the entire folder is deleted. Not the certificates, not the account — just the staging folder that briefly held your plaintext secrets on the host filesystem. Docker Compose has already copied what it needs into the container's environment; the note has been delivered, so the courier burns it rather than leaving it lying around for the next person who happens to `ls /opt`.

Getting from a freshly-templated compose file to a genuinely healthy container involves one more nicely paranoid touch — Ansible doesn't just start the container and walk away, it *waits*:

```yaml
- name: Wait for Docker container to be healthy
  ansible.builtin.shell: docker inspect --format '{{ '{{.State.Health.Status}}' }}' "{{ container_name }}"
  register: docker_health
  until: docker_health.stdout | trim == 'healthy'
  retries: 30
  delay: 5
  changed_when: false
```

That's the exact same `healthcheck` block from Episode 4's compose file (`certbot certificates > /dev/null 2>&1`, checked every minute) being polled here every five seconds, up to thirty times, before Ansible considers the job done. And there's one more detail worth savouring: if the container was *already* running from a previous deployment, Ansible doesn't just leave it be — it explicitly restarts it:

```yaml
- name: Restart the container if already running - needed to request certificates after the first deployment
  community.docker.docker_container:
    name: "{{ container_name }}"
    state: restarted
  when: certbot_info.containers is defined
```

Because `start.sh`'s entire certificate-request logic runs once, at container startup, updating `DOMAINS_LIST` and re-running the playbook against an already-running container would otherwise do nothing at all for any newly-added domain — the running process is happily sitting in its renewal loop from Episode 7, not watching for new instructions. A deliberate restart is what actually re-triggers the registration-and-issuance dance for anything new on the itinerary.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Ansible `template` task | Jinja-rendered `docker-compose.yml` and `.certbot.env` (with real secrets) | Write both files to a temporary `/opt/certbot-deploy` staging folder | A short-lived, plaintext-secret-bearing deployment folder | `docker compose`, reading `env_file` at container start |
| Ansible `file: state: absent` task | The staging folder, no longer needed once the container has started | Delete it entirely from the host filesystem | No lingering plaintext `KEY_ID`/`HMAC_KEY` on disk | Anyone who might otherwise stumble across it later |
| Ansible's healthcheck-wait and restart logic | The container's own `HEALTHCHECK` status, and its prior running state | Poll until healthy; force a restart if the container already existed | A confirmed-healthy container that has actually re-run its startup logic | Whoever is watching the playbook finish |

Next stop: closing the passport — the full trip, start to finish, and where the wider GARR toolbox picks up from here.
