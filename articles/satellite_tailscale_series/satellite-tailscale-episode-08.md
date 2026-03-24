---
title: "Satellite Tailscale — Ep.8"
published: false
description: "Exit Nodes and Subnet Routing are Tailscale's most powerful capabilities — turning your Mac Mini M4 Pro into a gateway to your entire home network, and routing all your traffic through home when the coffeeshop Wi-Fi gets suspicious."
tags: tailscale, exitnode, subnetrouting, networking
series: Satellite Tailscale
cover_image: ""
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛰️ Satellite Tailscale — Episode 8: Orbital Maneuvers (Exit Nodes & Subnet Routing)

> *"I'm a cybernetic organism. Living tissue over a metal endoskeleton."*
> — T-800, Terminator 2.
> *"I'm a subnet router. Private network traffic over a WireGuard® mesh."*
> — Your Mac Mini M4 Pro, Episode 8.

---

## 🚀 Beyond Point-to-Point

Through Episodes 1–7, we built something excellent: a personal satellite network where your iPad Mini and Mac Mini M4 Pro are seamlessly connected across the globe. You can SSH in. You can take over the desktop. You can transfer files and run commands as if you were sitting at home.

But Tailscale has more in its orbital toolkit. Two features, in particular, dramatically extend what your tailnet can do:

1. **Exit Nodes** — Route *all* your iPad Mini's internet traffic through your home Mac Mini (or any other tailnet node), so coffeeshop Wi-Fi never sees your traffic.
2. **Subnet Routing** — Expose your entire home network (`192.168.x.x`) to your tailnet, so you can reach *any device* on your home network — not just the ones with Tailscale installed.

Together, these features transform your Mac Mini from a remote access target into a **full network gateway**. An orbital relay for your home network.

---

## 📋 SIPOC — Orbital Maneuvers

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Tailscale Inc. | Your tailnet (Episodes 2–7) | Enable Exit Node on Mac Mini → Approve in admin console → Use from iPad Mini | All iPad Mini traffic exits via Mac Mini home IP | You, browsing from the coffeeshop as if you are at home |
| macOS network stack | Your home network (192.168.x.x subnet) | Enable Subnet Routing → Advertise routes → Approve in admin console | All home network devices reachable from tailnet | Your NAS, smart home hub, printer, Raspberry Pi, etc. |
| Your home router | IP forwarding enabled on Mac Mini | Enable IP forwarding on macOS → Tailscale advertises routes | Home subnet exposed to tailnet without Tailscale on each device | Future you, accessing the home NAS from Edinburgh |
| Your ISP | Your public IP address | iPad Mini uses Mac Mini as Exit Node | Coffeeshop only sees Tailscale traffic; your home IP appears to the internet | Your privacy, significantly improved |

---

## 🌍 Part 1: Exit Nodes

### What Is an Exit Node?

Normally, your iPad Mini's internet traffic goes through whatever network it is connected to — the coffeeshop Wi-Fi, 4G, hotel Wi-Fi, and so on. Tailscale handles traffic to your other tailnet devices, but general internet traffic (websites, APIs, streaming) bypasses Tailscale entirely.

An **Exit Node** changes this. When you designate your Mac Mini as an Exit Node and select it on your iPad Mini, **all internet traffic from your iPad Mini is routed through your Mac Mini's home internet connection**. From the perspective of the wider internet, your iPad Mini appears to come from your home IP address.

This means:
- The coffeeshop Wi-Fi cannot see your traffic (it is all WireGuard®-encrypted between your iPad and Mac Mini)
- Websites see your home IP, not the coffeeshop's
- Region-restricted content that works at home works from the coffeeshop
- DNS queries are resolved at home, bypassing any dodgy coffeeshop DNS

It is not a commercial VPN. It is *better* — because you own and control the exit point.

### Enabling Your Mac Mini as an Exit Node

On the Mac Mini M4 Pro:

```bash
# Advertise this device as an Exit Node
sudo tailscale up --advertise-exit-node
```

Or, if Tailscale is already up:

```bash
sudo tailscale set --advertise-exit-node
```

Now, in the Tailscale admin console:

1. Navigate to **Machines**.
2. Find your Mac Mini.
3. Click the `...` menu → **Edit route settings**.
4. Enable **"Use as exit node"**.

> ⚠️ **This approval step is important.** Exit Nodes require explicit admin approval — so that a rogue device in your tailnet cannot spontaneously start routing all traffic through itself. You are the admin. You approve it.

### Updating the ACL to Allow Exit Node Usage

In your ACL policy, add:

```json
{
  "action": "accept",
  "src":    ["group:owner"],
  "dst":    ["autogroup:internet:*"]
}
```

This allows `group:owner` (you) to route traffic through Exit Nodes to the wider internet.

### Using the Exit Node from Your iPad Mini

On your iPad Mini, open the Tailscale app:

1. Tap on **Exit Nodes** (or the device name area at the top).
2. Select your Mac Mini from the list.
3. Confirm.

Your iPad Mini's internet traffic now flows through your home Mac Mini. The coffeeshop Wi-Fi sees only encrypted WireGuard® traffic. You are home, digitally speaking.

> *"I'll be back."*
> — T-800, every time you return to the coffeeshop and select the Exit Node again.

---

## 🏘️ Part 2: Subnet Routing

### What Is Subnet Routing?

Your home network contains more than just your Mac Mini. It probably also contains:

- A **NAS** (Synology, QNAP, or similar) storing years of photos and documents
- A **Raspberry Pi** running Pi-hole, Home Assistant, or a media server
- A **smart home hub** (Philips Hue, IKEA Dirigera, etc.)
- A **printer** (old, resentful, alive)
- Maybe a **network switch** with a web management interface

None of these devices run Tailscale. None of them are in your tailnet. But with **Subnet Routing**, your Mac Mini can advertise your entire home network subnet to your tailnet — making every device on that subnet reachable from your iPad Mini, anywhere in the world.

### Enabling IP Forwarding on macOS

Subnet routing requires IP forwarding — your Mac Mini needs to be able to forward packets between your home network and the WireGuard® tunnel.

```bash
# Enable IP forwarding (IPv4)
sudo sysctl -w net.inet.ip.forwarding=1

# Enable IP forwarding (IPv6, if needed)
sudo sysctl -w net.inet6.ip6.forwarding=1
```

To make this persistent across reboots, add to `/etc/sysctl.conf`:

```
net.inet.ip.forwarding=1
```

### Advertising Your Home Subnet

First, identify your home network subnet. Usually this is `192.168.1.0/24` or `192.168.0.0/24`. Check:

```bash
# Show your home network interface and subnet
ifconfig | grep inet
```

Look for the `192.168.x.x` address on your `en0` or `en1` interface. The subnet is typically that address with the last octet replaced by `.0/24`.

Now advertise it to your tailnet:

```bash
sudo tailscale up --advertise-routes=192.168.1.0/24
```

Or, if Tailscale is already running:

```bash
sudo tailscale set --advertise-routes=192.168.1.0/24
```

### Approving the Subnet Route

In the Tailscale admin console:

1. Navigate to **Machines**.
2. Find your Mac Mini.
3. Click `...` → **Edit route settings**.
4. Enable **"192.168.1.0/24"** under Subnets.

Your home subnet is now accessible from your tailnet.

### Accessing Home Network Devices from Your iPad Mini

On your iPad Mini, open the Tailscale app and ensure **"Accept routes"** is enabled (it usually is by default).

Now, from any terminal or app on your iPad Mini, you can reach:

| Device | IP | Access method |
|---|---|---|
| NAS | `192.168.1.10` | Web browser or SMB/NFS client |
| Pi-hole | `192.168.1.20` | Web browser (`http://192.168.1.20/admin`) |
| Raspberry Pi | `192.168.1.30` | SSH (`ssh pi@192.168.1.30`) |
| Smart home hub | `192.168.1.40` | Web browser |
| Printer | `192.168.1.50` | Try `lpd://192.168.1.50` and pray |

All of this, from your iPad Mini, from a coffeeshop, through your Tailscale-encrypted satellite network, without those devices needing Tailscale installed.

> 🛰️ The Mac Mini M4 Pro is now functioning as a **full network gateway** — a satellite in permanent orbit over your home network, making everything below it visible to your tailnet.

---

## 🔒 Keeping It Secure

With Exit Nodes and Subnet Routing active, your ACL policy becomes more important. A few recommendations:

```json
{
  "acls": [
    // Only you can use the Exit Node
    {
      "action": "accept",
      "src":    ["group:owner"],
      "dst":    ["autogroup:internet:*"]
    },
    // Only you can reach the home subnet via the router
    {
      "action": "accept",
      "src":    ["group:owner"],
      "dst":    ["192.168.1.0/24:*"]
    }
  ]
}
```

This ensures that even if you ever share your tailnet with others (guest devices, family members), they cannot use your Mac Mini as an exit node or access your home subnet.

The Terminator applies least-privilege access control. So should you.

---

## 🌌 The Complete Constellation — Final Status

| Feature | Status | Notes |
|---|---|---|
| Mac Mini M4 Pro | ✅ In orbit | Always-on tailnet node |
| iPad Mini | ✅ In orbit | Mobile ground station |
| MagicDNS | ✅ Active | Human-readable hostnames |
| ACLs | ✅ Enforced | Least-privilege policy |
| Tailscale SSH | ✅ Enabled | Identity-aware shell access |
| RustDesk | ✅ Configured | Full remote desktop, no relay server |
| Exit Node | ✅ Available | Route all traffic via home IP |
| Subnet Routing | ✅ Active | Entire home network accessible |

This is a complete, production-quality personal satellite network. Built on free and open-source tools (WireGuard®, RustDesk), a generous free tier (Tailscale personal use), and the patient application of good engineering principles.

---

## 🎯 What We Built — The Mission Debrief

Over eight episodes, starting from first principles, we built:

1. **A mental model** — satellites, ground stations, orbital relays
2. **A tailnet** — Mac Mini and iPad Mini, permanently connected
3. **Identity-aware access** — SSH without key management
4. **Full desktop control** — RustDesk + Tailscale, no relay servers
5. **A proper network gateway** — Exit Nodes and Subnet Routing

From a coffeeshop iPad Mini to a home Mac Mini M4 Pro. Across hemispheres. Encrypted. Authenticated. Governed.

The mission is complete.

> *"It's over."*
> — Sarah Connor, Terminator 2.
> *"Your complex remote access setup: over. Your port forwarding rules: over. Your VPN server maintenance: over."*
> — You, having read this series.
> *"I'll be back."*
> — T-800, in every network disruption that Tailscale will silently recover from while you sleep.

---

## 🔭 Further Reading

- [Tailscale Documentation](https://tailscale.com/kb)
- [RustDesk GitHub](https://github.com/rustdesk/rustdesk)
- [Tailscale + RustDesk official guide](https://tailscale.com/blog/tailscale-rustdesk-remote-desktop-access)
- [WireGuard® protocol](https://www.wireguard.com/)
- [learning-tailscale repository](https://github.com/vanHeemstraSystems/learning-tailscale)

---

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between. Thank you for flying with us.*
