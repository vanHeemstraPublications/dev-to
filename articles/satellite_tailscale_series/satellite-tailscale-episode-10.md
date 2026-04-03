---
title: "Satellite Tailscale — Ep.10"
part: 10
published: false
description: "Why install Tailscale on every device in your home when your router can do it once for all of them? The UDM Pro joins the tailnet as a subnet router — and suddenly, everything on your home network is reachable from anywhere."
tags: [tailscale, unifi, networking, subnetrouter]
series: "Satellite Tailscale Series"
cover_image: “”
canonical_url: “”
organization: "the-software-s-journey"
---

# 🛰️ Ground Control (Tailscale on the UniFi Dream Machine Pro)

> *“Come with me if you want to connect.”*
> — T-800, adapted for network engineers.

## 🛰️ The Architecture Problem

Across the previous nine episodes, we built a solid personal satellite network. iPad Mini in a coffeeshop — connected. Mac Mini M4 Pro at home — connected. Home Assistant on the Parallels VM — connected. RustDesk for full remote desktop — connected. Everything that runs Tailscale is in orbit.

But your home network contains more than devices that run Tailscale. It contains:

- A **UniFi Dream Machine Pro** — the router and brain of the network
- A **UniFi Express** — the wireless access point extending coverage to every room
- Smart TVs, printers, NAS drives, smart plugs, IP cameras, the Ajax alarm hub, and every other device that connects to your LAN but will never run Tailscale

These devices are on your `192.168.x.x` network. They are behind your UDM Pro. From your iPad Mini in a coffeeshop, they are invisible — not because Tailscale cannot reach them in principle, but because nothing on your home network has told Tailscale where they live.

The solution is elegant: instead of installing Tailscale on each of these devices — which is often impossible anyway — you install it once on the **UDM Pro** and configure it as a **subnet router**. The UDM Pro tells your tailnet: *“I know where 192.168.x.x is. Send me the traffic and I will deliver it.”*

From that moment, every device on your home network is reachable from your tailnet. Not just the ones with Tailscale installed. All of them. The router becomes the gateway to your entire home.

-----

## 📋 SIPOC — Ground Control

|**Suppliers**                  |**Inputs**                                  |**Process**                                        |**Outputs**                                              |**Customers**                                                            |
|-------------------------------|--------------------------------------------|---------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------------------------|
|SierraSoftworks (tailscale-udm)|UniFi Dream Machine Pro (UniFi OS 2.x+)     |Enable SSH → Install tailscale-udm → `tailscale up`|UDM Pro in your tailnet as a named node                  |Your iPad Mini, reaching every LAN device remotely                       |
|Tailscale admin console        |Your Tailscale account (from Episodes 2–9)  |Approve subnet route in admin console              |`192.168.x.x/24` routable from any tailnet device        |Home Assistant (no longer needs its own Tailscale add-on for LAN devices)|
|UniFi OS (Debian-based, 2.x+)  |A SSH client (Terminal on Mac)              |`tailscale up --advertise-routes=192.168.x.x/24`   |UniFi dashboard reachable at its LAN IP from your tailnet|Your Mac Mini, accessing the UniFi controller remotely                   |
|Your home network              |Your home LAN subnet (e.g. `192.168.1.0/24`)|Update ACL → disable key expiry → verify           |Full home network accessible over WireGuard®, encrypted  |Everything that lives on your home LAN                                   |

-----

## 🏠 Your Home Network at a Glance

Before we start, let us map the environment. Your home network in Eersel looks like this:

```
Internet (your ISP)
        │
        ▼
UniFi Dream Machine Pro (UDM Pro)
├── WAN interface → your ISP
├── LAN interface → 192.168.1.0/24 (your home network)
│   ├── Mac Mini M4 Pro (192.168.1.x) — Tailscale installed ✅
│   ├── HAOS VM in Parallels (192.168.1.x) — Tailscale add-on ✅
│   ├── Ajax alarm hub (192.168.1.x) — no Tailscale ❌
│   ├── Smart TV (192.168.1.x) — no Tailscale ❌
│   ├── NAS (192.168.1.x) — no Tailscale ❌
│   └── Various IoT devices — no Tailscale ❌
└── WiFi → managed by UniFi Express
    ├── iPad Mini (roaming — not always on this WiFi)
    └── Phones, tablets, laptops
```

The UDM Pro sits at the top of this hierarchy. It sees everything. It routes everything. If we get Tailscale running on the UDM Pro and configure it as a subnet router, it bridges the home LAN (`192.168.1.0/24`) into your tailnet — and every device on that LAN becomes addressable from anywhere in the world.

-----

## ⚠️ A Word on the UniFi Express

The **UniFi Express** (UX) is a compact mesh Wi-Fi device that combines an access point and a basic router. It runs UniFi OS but with a considerably more locked-down configuration than the UDM Pro. Community research has confirmed that the UniFi Express has restrictions that prevent straightforward `tailscale-udm` installation via the standard script.

> 🛰️ **The rule of thumb:** Install Tailscale on the **UDM Pro** — the primary gateway device. Leave the UniFi Express alone. The Express plays the role of Wi-Fi satellite dish: it extends your wireless coverage, adopts your HAOS VM’s MagicDNS names over Wi-Fi, and routes traffic to the UDM Pro as usual. It does not need to be in your tailnet independently. The UDM Pro’s subnet routing covers the entire LAN — including devices connected via the Express’s Wi-Fi.

This is the correct architecture for your setup: one tailnet node on the UDM Pro, covering the whole LAN. The Express stays as a managed access point, as Ubiquiti intended it.

-----

## ⚠️ The Warranty Warning — Read This First

When you SSH into a UniFi device and modify it outside normal operation, Ubiquiti’s firmware presents this message:

> *“You acknowledge that the use of CLI to modify device(s) outside of their normal operational scope, or in any manner inconsistent with the ToS or EULA, will permanently and irrevocably void any applicable warranty.”*

This is real. Ubiquiti does not officially support Tailscale. The `tailscale-udm` community script is maintained independently of both Ubiquiti and Tailscale Inc. It works reliably for thousands of users, but UniFi firmware updates can occasionally require a reinstall.

With that clearly stated: proceed if you are comfortable with CLI-level access to your router. The community has validated this approach thoroughly, the install script is widely used with 1,400+ GitHub stars, and the risk is well understood.

-----

## 🛠️ Step 1 — Enable SSH on the UDM Pro

SSH is disabled on UniFi devices by default. Enable it in the UniFi console:

1. Log in to your **UniFi Network** controller (at `https://192.168.1.1` or your UniFi console IP).
1. Navigate to **Settings → System → Advanced**.
1. Find **Device SSH Authentication**.
1. Enable it and set a **username** and **strong password** (or upload an SSH public key — preferred).
1. Click **Apply Changes**.

From your Mac Mini M4 Pro, SSH in:

```bash
ssh admin@192.168.1.1
```

Substitute `admin` with the username you set, and `192.168.1.1` with your UDM Pro’s LAN IP. Accept the host fingerprint when prompted.

If you land at a prompt that looks like a Unix shell — congratulations. You are backstage at the UDM Pro. Do not touch anything you do not recognise.

-----

## 🔍 Step 2 — Verify Your UniFi OS Version

Before installing anything, confirm which version of UniFi OS your UDM Pro is running. The `tailscale-udm` script requires **UniFi OS 2.x or later**:

```bash
/usr/bin/ubnt-device-info firmware_detail
```

Sample output:

```
UniFi Dream Machine Pro
UniFiOS 3.2.17
...
```

Anything `2.x` or `3.x` is compatible. If you somehow have `1.x` — update your firmware via the UniFi console first. `1.x` support was dropped from the script in 2025 and the legacy branch is unmaintained.

-----

## 📦 Step 3 — Install the Tailscale-UDM Script

The `tailscale-udm` script by SierraSoftworks is the community-standard approach. It:

- Downloads the latest Tailscale binary for your device’s architecture
- Installs it into `/data/tailscale/`
- Registers a `systemd` service (`tailscaled`) that survives reboots
- Sets up an `on_boot.d` script so Tailscale restarts correctly after firmware updates

While still SSH’d into the UDM Pro, run:

```bash
curl -sSLq https://raw.github.com/SierraSoftworks/tailscale-udm/main/install.sh | sh
```

> 🛸 **Inspect before you execute:** If you prefer to review the script before running it (a good habit), first download it and read it:
> 
> ```bash
> curl -sSLq https://raw.github.com/SierraSoftworks/tailscale-udm/main/install.sh -o /tmp/install.sh
> cat /tmp/install.sh
> sh /tmp/install.sh
> ```

The script runs for 30–60 seconds. When it finishes, Tailscale is installed and `tailscaled` is running.

Confirm:

```bash
tailscale status
```

You should see output indicating Tailscale is running but not yet authenticated:

```
# Health check:
#     - not logged in
```

-----

## 🔑 Step 4 — Authenticate the UDM Pro to Your Tailnet

Run `tailscale up` with the routes you want to advertise. Your home LAN is `192.168.1.0/24` (adjust if your subnet differs):

```bash
tailscale up \
  --advertise-routes=192.168.1.0/24 \
  --advertise-exit-node \
  --hostname=udm-pro
```

The flags:

|Flag                               |Purpose                                                                |
|-----------------------------------|-----------------------------------------------------------------------|
|`--advertise-routes=192.168.1.0/24`|Tells your tailnet: “I can route to this subnet”                       |
|`--advertise-exit-node`            |Makes the UDM Pro available as a Tailscale Exit Node                   |
|`--hostname=udm-pro`               |Clean, readable name in your tailnet (instead of the default device ID)|

After running this command, Tailscale prints a URL:

```
To authenticate, visit:
https://login.tailscale.com/a/xxxxxxxxxxxxxxxx
```

Open this URL on any device — your Mac Mini, your iPad Mini, your phone. Sign in with the same identity provider you use for your tailnet. The UDM Pro is now authenticated and joins your constellation.

> 📌 **IP forwarding note:** Unlike standard Linux machines, you do NOT need to manually enable `net.ipv4.ip_forward` on UniFi OS. It is already enabled by default. The `tailscale-udm` documentation confirms this. One less thing to worry about.

-----

## ✅ Step 5 — Approve the Subnet Route in the Admin Console

Adding `--advertise-routes` tells Tailscale the UDM Pro *wants* to advertise the route. But it does not take effect until an admin explicitly approves it in the admin console. This two-step approval is intentional — it prevents rogue devices from accidentally (or maliciously) advertising routes without explicit authorisation.

1. Open [login.tailscale.com](https://login.tailscale.com).
1. Navigate to **Machines**.
1. Find `udm-pro`.
1. Click the `...` menu → **Edit route settings**.
1. Enable the checkbox next to `192.168.1.0/24`.
1. If you also set `--advertise-exit-node`, enable **“Use as exit node”** on the same screen.
1. Click **Save**.

From this moment, every device in your tailnet can route traffic to `192.168.1.x` via the UDM Pro. The entire home network is reachable.

-----

## 🔑 Step 6 — Disable Key Expiry on the UDM Pro

By default, Tailscale device keys expire after 180 days. When a key expires, the device is removed from the tailnet until someone re-authenticates it. On a laptop this is a minor inconvenience. On a router sitting in a rack, it is the moment you lose access to your home network from Guernsey.

Disable key expiry for the UDM Pro:

1. In the admin console → **Machines** → find `udm-pro`.
1. Click `...` → **Disable key expiry**.

The UDM Pro will remain in your tailnet permanently without requiring re-authentication. This is appropriate for a fixed infrastructure device that you control and manage.

-----

## 🔒 Step 7 — Tag the UDM Pro and Update Your ACL

Apply the `tag:home-base` tag to the UDM Pro — consistent with how you tagged the Mac Mini and Home Assistant in the existing episodes:

1. Admin console → **Machines** → `udm-pro` → `...` → **Edit ACL tags**.
1. Add `tag:home-base`.

Update your ACL policy to explicitly permit subnet traffic from mobile devices through the UDM Pro:

```json
{
  "tagOwners": {
    "tag:home-base":  ["youremail@example.com"],
    "tag:mobile":     ["youremail@example.com"]
  },

  "groups": {
    "group:owner": ["youremail@example.com"]
  },

  "acls": [
    // Owner can reach everything
    {
      "action": "accept",
      "src":    ["group:owner"],
      "dst":    ["*:*"]
    },
    // Mobile devices can reach home-base nodes on specific ports
    {
      "action": "accept",
      "src":    ["tag:mobile"],
      "dst":    ["tag:home-base:22,443,5900,8123,21115,21116,21117,21118,21119"]
    },
    // All tailnet devices can reach the home LAN subnet via UDM Pro
    {
      "action": "accept",
      "src":    ["group:owner"],
      "dst":    ["192.168.1.0/24:*"]
    }
  ],

  "ssh": [
    {
      "action":  "accept",
      "src":     ["group:owner"],
      "dst":     ["tag:home-base"],
      "users":   ["autogroup:nonroot"]
    }
  ]
}
```

The key addition is the third ACL rule: `"dst": ["192.168.1.0/24:*"]`. This explicitly permits traffic from `group:owner` devices to the home subnet — the traffic that the UDM Pro’s subnet routing will handle.

-----

## ✅ Step 8 — Verify Everything Works

From your Mac Mini M4 Pro (or iPad Mini connected to mobile data), verify:

```bash
# Check the UDM Pro is in your tailnet
tailscale status

# Ping the UDM Pro itself via its Tailscale IP
tailscale ping udm-pro

# Ping a device on the LAN that does NOT have Tailscale installed
# (e.g., your NAS at 192.168.1.50)
ping 192.168.1.50

# Access the UniFi controller web UI via the LAN IP
# Open in browser: https://192.168.1.1
```

If the ping to `192.168.1.50` succeeds — a device with no Tailscale installed, reached from outside your home network — the subnet routing is working. Your entire home LAN is now reachable from anywhere in your tailnet.

> 🛸 **If pings succeed but the UniFi browser UI does not load:** Try connecting to the Tailscale IP of the UDM Pro directly (`https://100.x.x.x`) rather than the LAN IP. Some UniFi configurations require accessing the controller via its Tailscale address when connecting from outside the subnet.

-----

## 🌐 What You Can Now Do — The Full Picture

With the UDM Pro in your tailnet as a subnet router, your access from the coffeeshop or from Guernsey expands dramatically:

|Device                   |Access method          |Previously      |
|-------------------------|-----------------------|----------------|
|**Mac Mini M4 Pro**      |Tailscale IP / MagicDNS|✅ Already worked|
|**HAOS VM (Parallels)**  |`homeassistant:8123`   |✅ Already worked|
|**UniFi controller**     |`https://192.168.1.1`  |❌ LAN-only      |
|**UniFi Protect cameras**|Via LAN IP in browser  |❌ LAN-only      |
|**NAS**                  |Via LAN IP or SMB      |❌ LAN-only      |
|**Ajax alarm hub UI**    |`http://192.168.1.x`   |❌ LAN-only      |
|**Smart TV (AirPlay)**   |Via LAN IP             |❌ LAN-only      |
|**Any IoT device**       |Via LAN IP             |❌ LAN-only      |

Everything that was LAN-only is now tailnet-accessible. No port forwarding. No VPN server. No public IP exposure. The UDM Pro carries all of it.

-----

## 📡 The UniFi Express — Its Actual Role

Now that Tailscale is on the UDM Pro, let us be clear about what the **UniFi Express** contributes to this setup:

The UniFi Express is a **managed satellite access point** — it extends your Wi-Fi coverage, adopts devices into the UniFi network, and passes all traffic up to the UDM Pro for routing. In your home, it likely provides Wi-Fi coverage in a room or floor that the UDM Pro’s built-in radio does not reach well.

From a Tailscale perspective, the Express is transparent:

- Devices connected to the Express’s Wi-Fi are on the same `192.168.1.0/24` subnet as devices connected to the UDM Pro directly
- Traffic from those devices routes through the Express → UDM Pro → Tailscale tunnel, exactly as it should
- The Express never needs to know about Tailscale at all

This is the correct role for the Express in this architecture. It does not need Tailscale; it does not benefit from Tailscale. It is a Wi-Fi antenna, and it does its job without any modification.

-----

## 🔄 Keeping Tailscale Updated After Firmware Updates

UniFi firmware updates occasionally wipe custom installs. The `tailscale-udm` script handles this with an `on_boot.d` hook — but firmware updates sometimes require you to reinstall Tailscale manually.

After any UniFi firmware update, SSH in and check:

```bash
tailscale status
```

If Tailscale is not running, reinstall:

```bash
/data/tailscale/manage.sh update
```

Or, if you need to fully reinstall:

```bash
curl -sSLq https://raw.github.com/SierraSoftworks/tailscale-udm/main/install.sh | sh
tailscale up --advertise-routes=192.168.1.0/24 --advertise-exit-node --hostname=udm-pro
```

Because you disabled key expiry in Step 6, the UDM Pro will re-authenticate immediately without requiring a browser login. The route approval in the admin console persists — you will not need to re-approve it.

Update Tailscale via `apt` when a new version is available:

```bash
apt update && apt install -y tailscale
```

Or use the management script:

```bash
/data/tailscale/manage.sh update
```

> 💡 **Pro tip:** Set Tailscale SSH on the UDM Pro so you can recover access even if your LAN connectivity is interrupted:
> 
> ```bash
> tailscale up --advertise-routes=192.168.1.0/24 --advertise-exit-node --hostname=udm-pro --ssh
> ```
> 
> With Tailscale SSH enabled, you can SSH into the UDM Pro via its Tailscale IP even if you cannot reach it on the LAN — useful for remote troubleshooting from a coffeeshop.

-----

## 🛸 The Complete Constellation — Final Status

|Device             |Role                     |Tailscale         |Status                                  |
|-------------------|-------------------------|------------------|----------------------------------------|
|Mac Mini M4 Pro    |Home Base                |✅ Native Tailscale|Always-on, SSH, RustDesk, subnet gateway|
|HAOS VM (Parallels)|Smart Home Ground Station|✅ Tailscale add-on|HA dashboard, automations, Ajax alarm   |
|UDM Pro            |Network Gateway          |✅ tailscale-udm   |Subnet router for entire 192.168.1.0/24 |
|UniFi Express      |Wi-Fi Satellite          |➖ Not needed      |Extends coverage, routes via UDM Pro    |
|iPad Mini          |Mobile Command Post      |✅ iOS app         |Reaches everything, from anywhere       |

Your home network is fully integrated into your satellite constellation. Not just the devices with Tailscale installed — the entire `192.168.1.0/24` subnet, with every device on it, reachable from your iPad Mini wherever you are.

The coffeeshop. The train. The airport lounge in September before the Guernsey flight. Anywhere with a network connection and a tailnet, your home is exactly one hop away.

> *“I’ll be back.”*
> — T-800, Terminator.
> *“Your home network will be back — online, reachable, and fully routed via the UDM Pro.”*
> — Tailscale, on reconnection after any brief interruption.

-----

## 🔭 Further Reading

- [tailscale-udm GitHub repository (SierraSoftworks)](https://github.com/SierraSoftworks/tailscale-udm)
- [Tailscale subnet router documentation](https://tailscale.com/kb/1019/subnets)
- [Tailscale exit node documentation](https://tailscale.com/kb/1103/exit-nodes)
- [Tailscale SSH documentation](https://tailscale.com/kb/1193/tailscale-ssh)
- [UniFi SSH access guide (Ubiquiti)](https://help.ui.com/hc/en-us/articles/204909374)

-----

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between.*
