---
title: "Satellite Tailscale — Ep.4"
part: 4
published: false
description: "Your Mac Mini M4 Pro is the mission-critical home station — always on, always reachable, always ready to receive your iPad Mini's signal from across the globe."
tags: [tailscale, macos, macmini, homelab]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/satellite_tailscale_series/satellite-tailscale-episode-04.png"
series: "Satellite Tailscale Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛰️ Satellite Tailscale — Episode 4: Home Base (Mac Mini M4 Pro)

> *"I'll be back."*
> — Arnold Schwarzenegger, The Terminator.
> Also: your Mac Mini M4 Pro, after every reboot, reconnecting to Tailscale automatically.

---

## 🏠 The Home Base Problem

A remote access setup is only as good as the device being accessed. Your iPad Mini can be the most brilliantly configured mobile ground station in the Netherlands, but if the Mac Mini at home is:

- Asleep
- Not running Tailscale
- Firewalled in a way that blocks incoming connections
- Being used as a surface for stacking unopened mail

...then none of it matters.

In this episode, we configure the Mac Mini M4 Pro as a **proper home base** — always on, always connected, always reachable. The kind of reliable, silent presence that does not need your attention until you need it. Like a very patient assistant with excellent connectivity.

---

## 📋 SIPOC — Configuring the Home Base

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Apple / macOS Sequoia+ | Mac Mini M4 Pro (24GB unified memory) | Disable sleep → Enable Tailscale autostart → Configure sharing | Always-on tailnet node | Your iPad Mini, calling from the coffeeshop |
| Tailscale Inc. | Tailscale installed (from Episode 2) | Set Mac Mini hostname → Enable SSH → Verify connectivity | Reachable home base with stable DNS name | Future episodes (SSH, RustDesk, file access) |
| macOS System Settings | Power adapter (Mac Mini is always plugged in) | Optional: configure Screen Sharing for VNC backup | Persistent Tailscale connection across reboots | Your peace of mind at 30,000 feet |
| Home router | A router that does not do anything weird with CGNAT | Test connectivity from another device | Confirmed two-way communication in tailnet | You, sipping a flat white somewhere distant |

---

## 😴 Step 1 — Prevent Your Mac Mini from Sleeping

A sleeping Mac Mini does not answer the satellite phone. Let us fix that.

**macOS Sequoia / Ventura:**

1. Open **System Settings** → **Energy**.
2. Under **Power Adapter**, set **"Prevent your Mac from automatically sleeping when the display is off"** to **On** (or drag the slider to **Never**).
3. Enable **"Wake for network access"** — this allows the Mac Mini to respond to network requests even when the display is off.

Alternatively, via Terminal:

```bash
# Prevent sleep (requires plugged-in power adapter)
sudo pmset -a sleep 0

# Enable network wake
sudo pmset -a womp 1

# Verify settings
pmset -g
```

The Mac Mini M4 Pro is a desktop machine — it is always plugged in. This means macOS is generally happy to keep it awake. Unlike a MacBook, it is not silently praying that you plug it in soon.

> *"There is no fate but what we make."*
> — Sarah Connor, Terminator 2.
> *"There is no sleep but what pmset makes."*
> — macOS power management, less poetically.

---

## 🏷️ Step 2 — Give Your Mac Mini a Proper Name

By default, your Mac Mini's hostname might be something like `Willems-Mac-Mini` — fine, but a bit casual for a mission-critical home base. Let us make it something cleaner.

**In macOS:**

```bash
# Set the ComputerName (displayed in Finder, About This Mac)
sudo scutil --set ComputerName "mac-mini-m4"

# Set the LocalHostName (used by Bonjour/mDNS, becomes Tailscale hostname)
sudo scutil --set LocalHostName "mac-mini-m4"

# Set the HostName (used by shell, terminal prompts, and Tailscale)
sudo scutil --set HostName "mac-mini-m4"
```

After this, your Mac Mini will appear in your Tailscale admin console as `mac-mini-m4` and will be reachable (with MagicDNS enabled) as `mac-mini-m4.your-tailnet-name.ts.net`.

Clean, memorable, professional. The kind of hostname that says: *I know what I am doing.*

---

## 🔄 Step 3 — Ensure Tailscale Starts on Boot

If you installed Tailscale from the Mac App Store, it registers itself as a login item and starts automatically. If you installed via Homebrew, let us make sure it is set up as a service:

```bash
# Start tailscaled as a system service (survives reboots)
sudo brew services start tailscale

# Verify it is running
brew services list | grep tailscale
```

You should see `tailscale` listed as `started`.

Now test it: reboot your Mac Mini. After it comes back up, check from another device:

```bash
tailscale status
```

Your Mac Mini should appear as connected within 30–60 seconds of booting — automatically, without any manual intervention. Like a loyal ground station that never takes a day off.

---

## 🔐 Step 4 — Enable SSH on the Mac Mini

We will dedicate a full episode to Tailscale SSH, but let us lay the groundwork now. macOS ships with an SSH server; it just needs to be turned on.

**Via System Settings:**
1. Open **System Settings** → **General** → **Sharing**.
2. Enable **Remote Login**.
3. Set it to allow access for **your user** (or specific users).

**Via Terminal:**
```bash
sudo systemsetup -setremotelogin on
```

Verify it is working from within your home network:
```bash
ssh yourusername@mac-mini-m4.local
```

Once Tailscale is in place, you will be able to do this from anywhere:
```bash
ssh yourusername@mac-mini-m4
```

No IP address. No port forwarding. Just the hostname. We will explore this properly in Episode 6.

---

## 🖥️ Step 5 — Enable Screen Sharing (as a Backup)

We will be setting up RustDesk in Episode 7 for proper remote desktop access. But it is good practice to also enable macOS's built-in Screen Sharing as a fallback — accessible via VNC clients.

**Via System Settings:**
1. **System Settings** → **General** → **Sharing**.
2. Enable **Screen Sharing**.

This gives you access via:
- **Finder** → Go → Connect to Server → `vnc://mac-mini-m4` (from within your tailnet)
- Any VNC client pointed at your Mac Mini's Tailscale IP

It is not as polished as RustDesk, but it works in a pinch. Think of it as the emergency parachute — you hope you never need it, but you are glad it is there.

---

## ✅ Verification — The Connectivity Check

From your iPad Mini (connected to coffeeshop Wi-Fi or mobile data), open the Tailscale app and tap on your Mac Mini. You should see:

- **Status: Connected**
- **Tailscale IP: 100.x.x.x**
- **MagicDNS name: mac-mini-m4.your-tailnet.ts.net** (if MagicDNS is enabled)

If you have SSH enabled, you can verify with a terminal app on your iPad (such as **Prompt 3**, **SSH Files**, or **a-Shell**):

```bash
ssh yourusername@mac-mini-m4
```

If you get a shell prompt on your Mac Mini, from your iPad Mini, from a coffeeshop, across the internet: congratulations. You have established your first satellite link.

> 🛰️ This is the moment. The home base and the mobile ground station are in contact. Mission Control would be proud.

---

## 🤖 The State of the Constellation

| Device | Role | Status | Notes |
|---|---|---|---|
| Mac Mini M4 Pro | Home Base | ✅ In orbit, always-on | Sleep disabled, Tailscale autostart |
| iPad Mini | Mobile Ground Station | ✅ In orbit, roaming | Follows you everywhere |

Two satellites. Verified two-way communication. The network is operational.

In **Episode 5**, we visit Mission Control properly: MagicDNS, ACLs, and the admin console — the tools that turn a pair of connected devices into a well-governed private network.

> *"Now there's two of us."*
> — T-800, Terminator 2.
> Translation: Two tailnet nodes. The constellation grows.

---

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between.*
