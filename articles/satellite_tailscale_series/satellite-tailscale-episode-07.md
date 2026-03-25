---
title: "Satellite Tailscale — Ep.7"
part: 7
published: false
description: "SSH is powerful, but sometimes you need to see the whole desktop. Combining Tailscale with RustDesk gives you full, fast, encrypted remote desktop access — no servers, no keys, no compromises."
tags: [tailscale, rustdesk, remotedesktop, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/satellite_tailscale_series/satellite-tailscale-episode-07.png"
series: "Satellite Tailscale Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛰️ Satellite Tailscale — Episode 7: Full Remote Desktop Across Hemispheres (Tailscale + RustDesk)

> *"Remember me? I'm back."*
> — Douglas Quaid (Arnold Schwarzenegger), Total Recall.
> Also: your Mac Mini M4 Pro desktop, appearing on your iPad Mini screen from 1,200 kilometres away.

---

## 🖥️ When SSH Is Not Enough

SSH is magnificent. In Episode 6, we used it to command our Mac Mini from a coffeeshop with nothing but a terminal and a Tailscale identity. For many tasks — pulling git repos, running scripts, inspecting logs — it is perfectly sufficient.

But sometimes you need the **full desktop experience**. You need to:

- Use a GUI application that has no CLI equivalent
- Navigate a file system in Finder rather than in `ls`
- See what is actually on the screen (perhaps a running presentation, a rendering job, a slow build)
- Explain something to someone by sharing your screen remotely
- Simply *be* at your Mac Mini, cursor and all, from the other side of the country

For all of this, you need a **remote desktop client**. And the best one, in our considered opinion, is **RustDesk** — combined with Tailscale to skip all the fiddly server infrastructure.

---

## 📋 SIPOC — Tailscale + RustDesk Setup

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| RustDesk (open source) | Your tailnet (Episodes 2–6) | Install RustDesk on all devices → Enable direct IP access → Connect by Tailscale IP | Full remote desktop session, peer-to-peer encrypted | You, moving the Mac Mini cursor from your iPad Mini |
| Tailscale Inc. | Mac Mini M4 Pro (host) + iPad Mini (client) | Skip RustDesk server setup entirely — Tailscale provides all coordination | Direct, encrypted desktop streaming | Your inner designer/developer who needs GUI apps remotely |
| GitHub (RustDesk releases) | RustDesk installed on both devices | Set permanent password → Configure display settings | Persistent, password-protected remote access | Anyone you invite (deliberately) to your tailnet |
| Apple App Store (iOS client) | Tailscale running on all devices | Test connection via Tailscale IP / MagicDNS name | Latency-optimised remote desktop using modern codecs | Future episodes, future use cases |

---

## 🦀 What Is RustDesk?

RustDesk is a **free, open-source remote desktop application** written in Rust (hence the name — Rust, as in the programming language; Desk, as in desktop; RustDesk, as in a desk made of Rust, which is actually quite sturdy). It supports:

- **Windows** (host and client)
- **macOS** (host and client)
- **Linux** (host and client)
- **iOS** (client)
- **Android** (client)
- **Browser** (experimental web client)

It supports file transfers, clipboard sharing, audio, multiple monitors, and more. It uses modern streaming codecs to feel responsive even on slower connections.

Normally, RustDesk suggests running your own relay server (actually two: an `hbbs` ID server and an `hbbr` relay server) for peer-to-peer connections outside your local network. This is not hard — Docker makes it manageable — but it requires:

- A server with a public IP
- Six open TCP/UDP ports
- A public key copied to every client
- Ongoing maintenance

With Tailscale, you need **none of this**. Tailscale already provides everything a RustDesk server does: device identity, IP address coordination, hole-punching, and encrypted relay as a fallback. By telling RustDesk to connect directly by IP, you bypass the relay infrastructure entirely and use Tailscale's as the transport layer.

One setting. That is the entire integration.

---

## 🛠️ Step 1 — Install RustDesk on the Mac Mini M4 Pro (Host)

Download the latest macOS release from:

```
https://github.com/rustdesk/rustdesk/releases/latest
```

Look for the `.dmg` file for Apple Silicon (`aarch64` or `arm64`). The Mac Mini M4 Pro runs Apple Silicon — make sure you grab the right architecture.

Install it:
1. Open the `.dmg`
2. Drag RustDesk to **Applications**
3. Launch RustDesk
4. Grant the permissions it requests:
   - **Screen Recording** — required for the host to share its screen
   - **Accessibility** — required for mouse and keyboard control
   - **Microphone** (optional — for audio)

These permissions can be granted in **System Settings → Privacy & Security**.

> ⚠️ On macOS, RustDesk will ask you to add it to Screen Recording permissions. If you skip this, the remote session will show a black screen. This is macOS doing its job. Give RustDesk what it needs.

---

## ⚙️ Step 2 — Configure RustDesk for Direct IP Access (The One Setting)

This is the magic step. Open RustDesk on your Mac Mini.

1. Click the **three-dot menu** (⋯) next to the ID number on the left side of the RustDesk window.
2. Select **Settings**.
3. Click on the **Security** section header to unlock it.
4. Under **Security** (the sub-section), find **"Enable direct IP access"**.
5. **Check the box**.

That is the entire Tailscale integration. One checkbox.

By enabling direct IP access, RustDesk can accept incoming connections by IP address directly — without needing to go through a relay server. Tailscale provides the IP (`100.x.x.x`), the encryption (WireGuard®), and the authentication. RustDesk provides the screen streaming and input handling.

The combination is: **Tailscale does the networking; RustDesk does the desktop.**

---

## 🔒 Step 3 — Set a Permanent Password

By default, RustDesk generates a new random temporary password each time it starts. This is inconvenient for our use case — you want to connect to your Mac Mini from a coffeeshop without needing to know the current temporary password (which changes every session and is only visible on the Mac Mini's screen).

Set a permanent password:

1. In RustDesk Settings → **Security**.
2. Under **Password**, toggle **"Use permanent password"**.
3. Set a strong password.

Store this in your password manager. You will use it every time you connect from your iPad Mini.

> *"You could leave. I'd find you."*
> — The Terminator.
> *"You could lock your Mac. I'd unlock it. With the permanent password I set in RustDesk."*
> — You, less menacingly.

---

## 📲 Step 4 — Install RustDesk on Your iPad Mini (Client)

Open the **App Store** on your iPad Mini and search for **RustDesk**. Install it. It is free.

Open RustDesk on your iPad Mini. You will see a text field that says **"Enter ID or IP address"**.

Here is where Tailscale enters the picture: instead of entering the Mac Mini's RustDesk-generated ID (which requires a relay server), you enter its **Tailscale IP** or **MagicDNS hostname**:

- `100.x.x.x` (the Mac Mini's Tailscale IP)
- or `mac-mini-m4` (if MagicDNS is set up — and it is, from Episode 5)

Tap **Connect**. Enter the permanent password you set in Step 3.

Your Mac Mini's desktop appears on your iPad Mini screen.

You are there. From a coffeeshop. From an iPad Mini. Across however many kilometres separate you from your home.

---

## 🎨 Step 5 — Optimise the RustDesk Experience

### Display Settings

On the iPad Mini client, once connected, tap the **toolbar** at the top of the screen to access session settings:

- **Quality**: Adjust between "Smooth" (lower bandwidth) and "Best" (higher quality). On a good coffeeshop Wi-Fi connection, "Best" is achievable.
- **Resolution**: RustDesk will match your Mac Mini's native resolution by default. You can scale this down for better performance.
- **Frame rate**: Higher frame rates feel smoother for cursor movement; lower frame rates save bandwidth.

### Input Settings

On the iPad Mini, you can control the Mac Mini using:

- **Touch**: tap to click, drag to move, pinch to scroll
- **External keyboard** (via Bluetooth): full keyboard input works
- **Apple Pencil**: surprisingly good for precise cursor control

### Multiple Monitors

If your Mac Mini M4 Pro is connected to multiple displays (it supports two 4K displays simultaneously), RustDesk handles multi-monitor setups gracefully — you can switch between monitors within the session.

---

## 🌐 The Full Picture — What Happens When You Connect

Let us trace the connection path from your iPad Mini in a coffeeshop to your Mac Mini M4 Pro at home:

```
iPad Mini (iOS, RustDesk client)
    │
    ▼
Tailscale (WireGuard® tunnel, encrypted, via coffeeshop NAT)
    │
    ▼
Internet (CGNAT traversal handled by Tailscale)
    │
    ▼
Tailscale (WireGuard® tunnel, decrypted on Mac Mini)
    │
    ▼
Mac Mini M4 Pro (RustDesk host, direct IP connection)
    │
    ▼
Your Mac Mini desktop, streamed back to your iPad Mini
```

No relay server. No RustDesk ID server. No open ports on your home router. No public IP needed. Tailscale handles the entire networking layer; RustDesk handles the desktop streaming.

The security story is also clean:
- **Encryption**: WireGuard® (Tailscale) for the network layer + RustDesk's own encryption for the desktop stream
- **Authentication**: Tailscale identity (for network access) + RustDesk password (for session access)
- **Access control**: Your ACL policy from Episode 5 (ports 21115–21119 open for `tag:mobile` → `tag:home-base`)

Two layers of authentication. Two layers of encryption. The Terminator would not get in without both.

---

## 🧰 Bonus: RustDesk Features Worth Knowing

| Feature | How to Access | Use Case |
|---|---|---|
| **File Transfer** | Toolbar → Files icon | Move files between iPad Mini and Mac Mini |
| **Clipboard Sync** | Automatic when connected | Copy on Mac Mini, paste on iPad (or vice versa) |
| **Remote Restart** | Toolbar → Power icon | Restart the Mac Mini without losing the tailnet |
| **Audio** | Toolbar → Audio icon | Hear system sounds from the Mac Mini |
| **Chat** | Toolbar → Chat icon | Text chat during a session (useful when helping others) |
| **Screenshot** | Toolbar → Camera icon | Capture the current remote screen |
| **Touchpad Mode** | Tap mode toggle | Use iPad as a trackpad rather than direct touch |

---

## 🤖 The Ultimate Coffeeshop Scenario

You are in a coffeeshop. The flat white is excellent. You open RustDesk on your iPad Mini. You type `mac-mini-m4`. You enter your password.

Your Mac Mini M4 Pro desktop appears on your iPad Mini screen. You can:

- Open Visual Studio Code and edit code
- Run Docker commands in the Terminal
- Open Finder and manage files
- Use applications that require a full desktop GUI
- Present something running on the Mac Mini to a colleague via screen share
- Check on a long-running build
- Basically: be at your Mac Mini, from anywhere, with your iPad Mini

This is the satellite network, fully operational. iPad Mini and Mac Mini M4 Pro — two hemispheres, one desktop, zero compromises.

> *"You've been targeted for termination."*
> — The Terminator (to traditional remote access solutions).
> *"Port forwarding: terminated. VPN servers: terminated. RustDesk relay servers: terminated. Complexity: terminated."*
> — Tailscale + RustDesk, methodically.

---

## 🛸 What's Next

In **Episode 8**, we explore the final frontier: **Exit Nodes and Subnet Routing** — Tailscale's most powerful features for making your home network truly global. Your Mac Mini becomes not just a remote desktop, but a gateway to your entire home network.

> *"I'll be back."*
> — T-800, Episode 8.

---

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between.*
