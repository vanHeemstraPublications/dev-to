---
title: "Satellite Tailscale — Ep.2"
published: false
description: "Installing Tailscale on your first device is the moment your ground station goes live. Let's light the engines."
tags: tailscale, networking, installation, wireguard
series: Satellite Tailscale
cover_image: ""
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛰️ Satellite Tailscale — Episode 2: Launching the First Satellite

> *"If it bleeds, we can kill it."*
> — Arnold Schwarzenegger, Predator.
> *"If it has a network interface, we can connect it."*
> — Any Tailscale engineer, Predator (network edition).

---

## 📡 Pre-Launch Checklist

In Episode 1, we established the big picture: your devices are ground stations, Tailscale is the orbital relay system, and the coffeeshop wi-fi is the enemy. Today, we stop theorising and start launching.

Installing Tailscale is — and I cannot stress this enough — **genuinely, unreasonably easy**. It is so easy that the first time you do it, you will spend ten minutes afterwards convinced you have done something wrong and the real installation must be more complex than this.

It is not. That was it.

Let us walk through it anyway, with appropriate SIPOC rigour.

---

## 📋 SIPOC — Launching Your First Satellite

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Tailscale Inc. | A device (Mac, Linux, Windows, iOS, Android) | Download → Install → Sign in | Device joined to your tailnet | You, finally free from port forwarding |
| Your identity provider | A Tailscale account (free tier is generous) | One-click authentication via browser | A stable Tailscale IP (100.x.x.x range) | Every future device you add |
| Your package manager (brew, apt, winget, etc.) | Internet access (ironic, given the goal) | OS-level WireGuard® tunnel activated | MagicDNS hostname assigned | Your peace of mind |
| App stores (iOS, Mac App Store) | Your login credentials | Device appears in Tailscale admin console | Encrypted, authenticated mesh node | Future you, accessing this device remotely |

---

## 🚀 Step 1 — Create Your Tailscale Account

Head to [tailscale.com](https://tailscale.com) and click **Get Started**. You will be asked to sign in with one of:

- Google
- Microsoft
- GitHub
- Apple
- Or your own SSO provider (for the enterprise adventurers among us)

Tailscale uses your identity provider for authentication, which means it never stores your password. It also means that if your Google account gets compromised, you should probably deal with that first before worrying about your tailnet.

> *"Get to the chopper!"* — Arnold Schwarzenegger, Predator.
> Translation: Get to the sign-in page. Do it now. The network waits for no one.

---

## 🛠️ Step 2 — Install on Your First Device

### macOS (Mac Mini M4 Pro — your home base)

```bash
# Option A: Using Homebrew (recommended for engineers)
brew install tailscale

# Option B: Download the Mac App Store version
# Search "Tailscale" in the Mac App Store
```

After installing via Homebrew, start the service:

```bash
sudo tailscaled &
sudo tailscale up
```

A browser window opens. You sign in. You are done.

If you installed from the App Store, just launch the app. A browser window opens. You sign in. You are done.

The tailscale daemon (`tailscaled`) is now running as a background service. It will survive reboots. It will reconnect automatically. It is quietly vigilant, like a well-trained German Shepherd, or the Terminator between missions.

### Linux (for your server nodes)

```bash
# Universal one-liner — works on Ubuntu, Debian, Fedora, Arch, etc.
curl -fsSL https://tailscale.com/install.sh | sh

# Then bring Tailscale up
sudo tailscale up
```

A URL appears in your terminal. Visit it. Sign in. Your device is now a satellite.

### Windows

Download the installer from [tailscale.com/download](https://tailscale.com/download). Run it. Sign in. Done.

Windows users: yes, it really is that simple. No, this is not a trap.

---

## 🔍 Step 3 — Verify Your First Satellite Is in Orbit

After signing in, check the status of your device:

```bash
tailscale status
```

You will see something like this:

```
100.x.x.x  mac-mini-m4          youremail@  macOS   -
```

That `100.x.x.x` address is your **Tailscale IP** — a stable, private IP address that this device will always have within your tailnet. It lives in the `100.64.0.0/10` CGNAT range, which means it will never conflict with your home network's `192.168.x.x` addresses.

You can also run:

```bash
tailscale ip
```

To see your device's Tailscale IP at a glance.

And if you want the full picture:

```bash
tailscale netcheck
```

This runs a network diagnostic and tells you:
- Whether UDP connectivity is available (good for direct peer connections)
- Which DERP relay region you are closest to (your fallback satellite)
- Your NAT type (affects how easily direct connections can be made)

> 🛰️ **The DERP region closest to the Netherlands is typically Frankfurt or Amsterdam.** Your fallback relay is practically next door. Low latency. The Terminator approves.

---

## 🗺️ Step 4 — Visit Mission Control

Open [login.tailscale.com](https://login.tailscale.com) in your browser. This is your **admin console** — the Mission Control from which you manage all satellites in your tailnet.

You will see your first device listed, with:
- Its name (pulled from the device hostname)
- Its Tailscale IP
- Its last seen time
- The OS it is running
- Whether it is connected

As you add more devices over the next episodes, they will all appear here. You can rename them, apply ACL tags, set expiry, and more. We will get into that in Episode 5.

For now, admire your first satellite in orbit. It is a moment worth savouring.

---

## 🤖 What Just Happened? (Under the Hood)

When you ran `tailscale up` and signed in, here is what Tailscale did in the background:

1. **Generated a WireGuard® key pair** — a private key (stays on your device, never leaves) and a public key (shared with the coordination server).
2. **Authenticated with the coordination server** — proved your identity via your OAuth provider.
3. **Registered your device** — the coordination server now knows this device is part of your tailnet, and knows its public key.
4. **Assigned a Tailscale IP** — a stable `100.x.x.x` address.
5. **Enabled MagicDNS** (if turned on) — gave your device a hostname like `mac-mini-m4.your-tailnet.ts.net`.
6. **Started the WireGuard tunnel interface** — on macOS, this is a `utun` interface. On Linux, it is `tailscale0`. Traffic to `100.x.x.x` addresses now flows through it.

No ports opened. No firewall rules written. No router config touched. The Terminator did not even need to flex.

---

## 🛸 What's Next

In **Episode 3**, we launch the mobile ground station: installing Tailscale on your **iPad Mini** — the device you will carry into the coffeeshop, the café, the airport lounge, and anywhere else with wi-fi that makes you mildly nervous.

Two satellites. One orbit. The network is beginning to take shape.

> *"You are terminated."*
> — Arnold Schwarzenegger, The Terminator (to port forwarding).

---

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between.*
