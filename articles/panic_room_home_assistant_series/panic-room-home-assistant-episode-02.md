---
title: "Panic Room — Ep.2"
part: 2
published: false
description: "Every panic room starts with a blueprint. Before we install Home Assistant, we need to choose where it runs. The Mac Mini M4 Pro with Parallels is our steel-reinforced answer."
tags: [homeassistant, macos, parallels, virtualization]
series: "Panic Room Home Assistant Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/panic_room_home_assistant_series/panic-room-home-assistant-episode-02.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🔐 Choosing Your Panic Room Hardware

> *"You've got cameras everywhere. Every room in the house."*
> — Meg Altman, Panic Room.
> *"You've got virtualization options everywhere. Every platform on the market."*
> — This episode.

---

## 🏗️ The Blueprint

Before the contractor breaks ground on a panic room, the architect draws a blueprint. The steel door goes *here*. The independent power supply goes *there*. The surveillance feed routes to *this panel*. Every decision made on paper first saves concrete and regret later.

Before we install Home Assistant, we need to make the same deliberate choices. Home Assistant runs on many things. The wrong choice for your situation means maintenance headaches, unsupported configurations, or a setup that stops working the moment you add a USB Zigbee stick.

Let us walk through the options — and then make the case for the one that suits a Mac Mini M4 Pro user who already has Parallels.

---

## 📋 SIPOC — Choosing the Installation Platform

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Home Assistant project | Your hardware (Mac Mini M4 Pro) | Evaluate installation options → Select best fit | A supported, full-featured HAOS installation | You, running Home Assistant without maintenance regret |
| Parallels Desktop | Your use case (always-on, full add-on support, USB access) | Compare HAOS vs Supervised vs Container vs Core | An informed architecture decision | Your future self, not googling "why did my HA break" |
| Apple Silicon (M4) | Your existing software setup | Select: Parallels + HAOS aarch64 image | Clear installation path for Episode 3 | Every episode after this one |
| Time (your most finite resource) | Patience for a one-time setup | Accept that this is a Sunday afternoon, not a ten-minute job | A setup that runs for years | Rianne, who will benefit from the smart home more than she admits |

---

## 🗂️ The Four Installation Types

The Home Assistant project ships four distinct installation types. Understanding the difference is important — they have different capabilities, different levels of official support, and different maintenance burdens.

### 1. Home Assistant OS (HAOS) — Recommended ⭐

HAOS is the **full operating system** — Linux, Home Assistant Core, the Supervisor, and the Add-on Store, all bundled into a single image. You run it on bare metal (a Raspberry Pi, a dedicated NUC) or in a supported virtual machine.

**What you get:**
- The **Add-on Store** — one-click installation of Tailscale, Mosquitto, Node-RED, Whisper, and hundreds of others
- Automatic OS updates managed by the project
- Full Supervisor support (backup, restore, watchdog)
- The most straightforward upgrade path

**What you give up:**
- You cannot install arbitrary software alongside HAOS. It is a dedicated OS.
- USB passthrough requires careful VM configuration

**Verdict:** If you want the full Home Assistant experience with the least ongoing friction, this is the one. And on a Mac Mini M4 Pro with Parallels, it is achievable — with a conversion step that Episode 3 will walk through.

---

### 2. Home Assistant Supervised — For the Enthusiast

Supervised runs Home Assistant Core + Supervisor on top of an existing **Debian Linux** system. You manage the Debian layer; Home Assistant manages itself above it.

**What you get:**
- Full Supervisor and Add-on Store access (same as HAOS)
- Ability to run other services on the same machine (Docker containers, etc.)

**What you give up:**
- You are responsible for keeping Debian in a supported state
- The project is strict: specific Debian version, specific Docker version, specific `systemd` configuration — deviate and the Supervisor marks the installation as **Unsupported** with a persistent yellow warning banner
- More things that can go wrong, more things you need to maintain

**Verdict:** Interesting for homelab veterans who want full OS control. For our purposes — a clean, reliable smart home that Just Works — it adds complexity without proportionate benefit.

---

### 3. Home Assistant Container — For the Docker Native

A Docker image of Home Assistant Core. No Supervisor. No Add-on Store.

**What you get:**
- Runs alongside other Docker containers on any Linux, macOS, or Windows machine
- Simple to deploy if you already run Docker

**What you give up:**
- **No Add-on Store.** Want Tailscale integration? Install it manually as a separate container and wire it up yourself. Want Mosquitto MQTT broker? Same. Want automatic backups? Write your own solution.
- No Supervisor means no one-click restore from the HA UI

**Verdict:** Powerful for experienced users who are comfortable with Docker Compose and want Home Assistant as one container among many. Not the right choice if you want the integrated experience this series describes.

---

### 4. Home Assistant Core — For the Python Developer

Raw Python application, installed in a virtual environment. Maximum control; maximum manual labour.

**Verdict:** No.

---

## 🍎 Why Parallels on Mac Mini M4 Pro?

The Mac Mini M4 Pro is an excellent Home Assistant host:

- **Always on**: desktop-class machine designed to stay plugged in
- **Powerful**: M4 Pro chip with 24GB unified memory — running a HAOS VM alongside your normal workload is trivial
- **Silent**: the M4 Pro's thermal design means it runs cool and quiet under light VM loads
- **Economical**: you already own it

The natural path for HAOS on a Mac is via a virtual machine. The official documentation recommends **VirtualBox** for macOS. VirtualBox on Apple Silicon is available (since June 2025) but still described as early days. An older, more battle-tested community path uses **UTM** (free, QEMU-based).

If you already have **Parallels Desktop** installed — for Windows, for Linux development, for anything — then using Parallels for HAOS is an attractive option. It runs the same ARM HAOS image, benefits from Parallels' polished VM management, and integrates with macOS's autostart-at-login feature.

The catch: Parallels does not natively import the `.vmdk` format that the HAOS project ships for Apple Silicon. It requires a one-time conversion using a command-line tool that ships with Parallels. Slightly fiddly. Entirely doable. Documented in full in Episode 3.

> 🏗️ **The alternatives for reference:**
>
> - **VirtualBox (Apple Silicon)**: Free. Official path per HA docs. Newer on Apple Silicon than UTM.
> - **UTM**: Free, QEMU-based. Excellent community guides for HAOS on Apple Silicon. Slightly less polished UI than Parallels.
> - **VMware Fusion**: Now free (as of 2024). Strong community guide for HAOS on Apple Silicon. Well-regarded.
>
> Any of these will produce a working HAOS installation. This series uses Parallels because you likely already have it.

---

## 💾 Minimum VM Specifications for HAOS

Whatever VM host you choose, the Home Assistant project recommends these minimums:

| Resource | Minimum | Recommended for Add-ons |
|---|---|---|
| RAM | 2 GB | 4 GB |
| Storage | 32 GB | 64 GB |
| vCPU | 2 cores | 2–4 cores |

On the Mac Mini M4 Pro with 24GB unified memory, allocating 4GB RAM and 2 vCPUs to the HAOS VM leaves abundant headroom for everything else you run. Home Assistant is not a heavy workload — most installations use under 1GB RAM under normal operation. The extra allocation is buffer for add-ons like Whisper (local speech-to-text), Frigate (local camera AI), or any ML-based tools you add later.

---

## 🔐 The Architecture Decision

Here is what we are building:

```
Mac Mini M4 Pro (macOS Sequoia)
└── Parallels Desktop
    └── HAOS VM (aarch64, ARM native)
        ├── Home Assistant Core
        ├── Home Assistant Supervisor
        └── Add-on Store
            ├── Tailscale (Episode 5)
            ├── [future add-ons]
            └── ...
```

The HAOS VM runs 24/7 alongside macOS. Parallels manages the VM lifecycle. The Mac Mini M4 Pro handles power management — set it to never sleep (as we configured in the Satellite Tailscale series), and the panic room is always on.

---

## 🛸 What's Next

In **Episode 3**, we break ground. We download the HAOS image, run the `prl_convert` conversion, create the Parallels VM, configure networking, and boot into Home Assistant for the first time.

The panic room is about to be built.

> *"They built it to be hidden."*
> — Lydia, Panic Room.
> *"They built it to be local-first."*
> — The Home Assistant project, essentially.

---

*🔐 Panic Room is a series about building a secure, local-first smart home using Home Assistant — installed on a Mac Mini M4 Pro via Parallels, connected via Tailscale, and controlled from an iPad Mini anywhere in the world.*
