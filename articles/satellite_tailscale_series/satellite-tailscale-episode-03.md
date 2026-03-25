---
title: "Satellite Tailscale — Ep. 3"
published: false
description: "Your iPad Mini is the roaming satellite dish — connecting from coffeeshops, airports, and hotel lobbies back to your Mac Mini at home. Let's get it into orbit."
tags: [tailscale, ipad, ios, mobile]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/satellite_tailscale_series/satellite-tailscale-episode-03.png"
series: "Satellite Tailscale Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛰️ Satellite Tailscale — Episode 3: The Mobile Ground Station (iPad Mini)

> *"I need your clothes, your boots, and your motorcycle."*
> — Arnold Schwarzenegger, Terminator 2: Judgment Day.
> *"I need your Wi-Fi password, your SSID, and your NAT type."*
> — Your iPad Mini, every time you walk into a new coffeeshop.

---

## ☕ The Coffeeshop Problem

Here is the scenario we are solving. You are in a coffeeshop somewhere — let's say it is a Tuesday, the flat white is excellent, and you need to access something on your Mac Mini M4 Pro sitting at home.

Maybe it is a file. Maybe it is a development server. Maybe you just want to check that your beloved Mac Mini is still alive and not being used as a cat bed by someone who shall not be named.

Your iPad Mini is your tool. The coffeeshop wi-fi is a hostile environment. But with Tailscale installed, your iPad and your Mac Mini are on the same private network — regardless of which café, airport, hotel, or train station you find yourself in.

Today, we get the iPad Mini into orbit.

---

## 📋 SIPOC — The Mobile Ground Station

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Apple App Store | iPad Mini (any model with iOS 16+) | Install Tailscale app → Sign in | iPad joined to your tailnet | You, ordering a second flat white |
| Tailscale Inc. | Your Tailscale account | iOS VPN profile installed automatically | Stable Tailscale IP for iPad | All your other tailnet devices |
| Your identity provider | Coffeeshop / mobile / home wi-fi | Tailscale routes traffic through WireGuard® tunnel | Encrypted connection to all tailnet nodes | Future you, accessing the Mac Mini remotely |
| iOS VPN framework | Permission to add VPN configuration | Device appears in admin console | Persistent connection across networks | Your productivity, restored |

---

## 📲 Installing Tailscale on iPad Mini

This is the easiest step in the entire series. Possibly the easiest step in networking history.

1. Open the **App Store** on your iPad Mini.
2. Search for **Tailscale**.
3. Tap **Get** (it is free).
4. Open the app.
5. Tap **Sign in**.
6. Authenticate with the same identity provider you used for your first device.
7. When prompted, tap **Allow** to add the VPN configuration.

That is it. You are in orbit.

iOS will ask you to confirm adding a VPN profile. This is normal. Tailscale uses the iOS VPN framework to create the WireGuard® tunnel. It does not reroute your traffic through some mysterious third-party server — it creates an encrypted tunnel directly to your other tailnet devices. The VPN profile is the mechanism; your tailnet is the destination.

> *"It's in your nature to destroy yourselves."*
> — The Terminator (T-800), Terminator 2.
> *"It's in your nature to expose your home network to the public internet."*
> — Tailscale, looking at your old port forwarding setup.
> *"Not anymore."*
> — Tailscale, installing a VPN profile.

---

## 🔋 The Battery Question

You are probably thinking: *"Won't a persistent VPN kill my battery?"*

Reasonable concern. Here is the good news: Tailscale on iOS is impressively power-efficient. It uses the system VPN framework intelligently, keeping the tunnel alive with minimal wake-ups. In practice, most users report **negligible battery impact** compared to always-on apps like email, push notifications, or, frankly, the screen itself.

A few tips to keep things tidy:

- **Allow Tailscale to run in background**: Settings → Tailscale → toggle on "Allow Background App Refresh" if needed.
- **Use the Tailscale widget**: Add the Tailscale status widget to your home screen or lock screen to see at a glance whether you are connected.
- **Check the status indicator**: The VPN icon in the iOS status bar tells you the tunnel is active.

---

## 🌐 Switching Networks Like a Satellite

Here is where Tailscale's elegance becomes apparent. Your iPad Mini will, during its life, connect to:

- Your home Wi-Fi (the safe harbour)
- Coffeeshop Wi-Fi (the wild west)
- 4G/5G mobile data (the open sky)
- Hotel Wi-Fi (the labyrinth — always with a captive portal)
- Airport lounges (surprisingly decent, usually)

Every time your iPad Mini switches networks, Tailscale **automatically reconnects**. It detects the network change, re-establishes the WireGuard® tunnel, and your tailnet connection is live again — usually within a second or two.

You do not need to tap anything. You do not need to reconnect manually. The satellite just... keeps orbiting.

This is the part that feels like magic and is actually cryptography.

---

## 🔍 Verifying the iPad Mini Is in Your Tailnet

On your iPad Mini, open the Tailscale app. You will see:

- **Your tailnet name** at the top
- **Your iPad's Tailscale IP** (100.x.x.x)
- **A list of all other devices in your tailnet** — including your Mac Mini M4

Tap on your Mac Mini's name. You will see its Tailscale IP and options to open a connection. We will use those in later episodes.

Meanwhile, on your Mac Mini (or any other device already in your tailnet), run:

```bash
tailscale status
```

Your iPad Mini should now appear in the list:

```
100.x.x.x  ipad-mini-willem     youremail@  iOS     -
```

Two satellites. Two ground stations. One tailnet. The constellation is forming.

---

## 📶 A Note on Captive Portals (Hotel Wi-Fi Traps)

Captive portals — those interstitial pages that hotel and airport wi-fi shows you before letting you onto the internet — can sometimes interfere with Tailscale.

The fix is simple:

1. Connect to the hotel Wi-Fi.
2. **Disable Tailscale** temporarily (toggle it off in the app).
3. Open Safari, which should redirect you to the captive portal.
4. Accept the terms / enter the room number / solve the puzzle / sacrifice a goat (hotel-dependent).
5. **Re-enable Tailscale**.

Tailscale will reconnect and you are back in orbit. The captive portal is handled. The goat situation is between you and the hotel.

> 🛰️ **Pro tip**: If the captive portal does not appear automatically, try navigating to `http://captive.apple.com` in Safari. This forces iOS to detect and display the captive portal page.

---

## 🤖 Two Satellites in Orbit

Let us take stock of where we are:

| Device | Role | Tailscale IP | Status |
|---|---|---|---|
| Mac Mini M4 Pro | Home Base | 100.x.x.x | ✅ In orbit |
| iPad Mini | Mobile Ground Station | 100.x.x.x | ✅ In orbit |

These two devices can now reach each other, encrypted and authenticated, regardless of what network either of them is connected to.

In **Episode 4**, we zoom in on the Mac Mini M4 Pro — configuring it properly as the home base, ensuring it is always available, and setting it up to receive incoming connections gracefully.

The home base needs to be ready. When the iPad Mini calls from the coffeeshop, someone has to pick up.

> *"Come with me if you want to live."*
> — Arnold Schwarzenegger, The Terminator.
> Also: Tailscale, inviting your iPad Mini into the tailnet.

---

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between.*
