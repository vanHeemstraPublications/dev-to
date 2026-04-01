---
title: "Panic Room — Ep.5"
part: 5
published: false
description: "In Panic Room, the safe room has its own phone line — independent, secure, unreachable by anyone who has cut the main lines. Tailscale is Home Assistant's independent communication line."
tags: [homeassistant, tailscale, remoteaccess, security]
series: "Panic Room Home Assistant Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/panic_room_home_assistant_series/panic-room-home-assistant-episode-05.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🔐 The Independent Phone Line (Tailscale Integration)

> *"The phones are dead. But that room has its own phone line. It goes straight to the street."*
> — Burnham, Panic Room.
> *"The public internet is hostile. But Home Assistant has its own encrypted tunnel. It goes straight to your iPad Mini."*
> — Tailscale, Panic Room (smart home edition).

---

## 📞 The Independent Line

In *Panic Room*, one of the panic room's critical features is its independent phone line. It bypasses the house's main communications — which the intruders have cut — and connects directly to the outside world. It is the one line the intruders cannot control.

Your Home Assistant installation has an equivalent vulnerability without Tailscale: it is accessible only from within your home network. Step outside — into the coffeeshop, the airport, the hotel lobby — and the line goes dead. You cannot check the cameras. You cannot turn off the lights you left on. You cannot see whether the door sensor registered anything while you were away.

Tailscale is the independent phone line. It connects your Home Assistant instance to your iPad Mini — and to any other device in your tailnet — through an encrypted WireGuard® tunnel that bypasses NAT, requires no port-forwarding, and exposes nothing to the public internet.

The intruders (hostile network conditions, port-scanners, nosy ISPs) cannot touch it.

---

## 📋 SIPOC — The Independent Phone Line

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Tailscale (Frenck's community add-on) | Running HAOS instance (from Episode 3–4) | Install Tailscale add-on → Configure → Authenticate | HAOS joins your tailnet as a named node | You, accessing HA from anywhere |
| Your existing tailnet (Satellite series) | Your Tailscale account | Enable userspace networking: false → Start → Open Web UI | `homeassistant.your-tailnet.ts.net` accessible via MagicDNS | iPad Mini Companion App (Episode 6) |
| Home Assistant Add-on Store | Tailscale admin console access | Approve device in admin console → Update ACL | HAOS reachable at port 8123 from tailnet devices | Your peace of mind, from 800 kilometres away |
| HAOS Supervisor | The YAML configuration from the Satellite series | Optional: enable proxy for HTTPS via MagicDNS | Clean, encrypted, identity-authenticated HA access | Rianne's phone, also added to the tailnet if desired |

---

## 🔗 Prerequisites

Before this episode, ensure:

1. ✅ You have a working Tailscale account (from the Satellite Tailscale series)
2. ✅ Your Mac Mini M4 Pro and iPad Mini are already in your tailnet
3. ✅ MagicDNS is enabled on your tailnet (Episode 5 of the Satellite series)
4. ✅ Your HAOS VM is running and accessible at `http://homeassistant.local:8123`

If you have not completed the Satellite Tailscale series, start there first — or at minimum create a Tailscale account and install Tailscale on at least one device. The Satellite series is the backstory; this episode is the sequel.

---

## 🛠️ Step 1 — Add the Community Add-ons Repository

The Tailscale add-on lives in the **Home Assistant Community Add-ons** repository maintained by Frenck (Franck Nijhof), a core Home Assistant developer. If you have not added this repository yet:

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
2. Click the **three-dot menu** (⋮) in the top-right.
3. Select **Repositories**.
4. Paste the following URL and click **Add**:
   ```
   https://github.com/hassio-addons/repository
   ```
5. Click **Close** and refresh the store page.

The **Home Assistant Community Add-ons** section will now appear in the store.

---

## 📦 Step 2 — Install the Tailscale Add-on

In the Add-on Store, search for **Tailscale**. Click the result under *Home Assistant Community Add-ons* (not the official integrations section, which is a different thing — see the note in Episode 9 of the Satellite series).

Click **Install**. Wait 60–90 seconds.

---

## ⚙️ Step 3 — Configure the Add-on

Click the **Configuration** tab on the Tailscale add-on page.

For our setup — direct tailnet access, no Funnel, no custom domain — the configuration is minimal:

```yaml
userspace_networking: false
```

Setting `userspace_networking: false` uses the kernel-level WireGuard® interface rather than a slower userspace implementation. This is important for two reasons:

1. **Performance**: kernel-level networking is faster and more efficient
2. **Subnet routing capability**: the HAOS node can optionally act as a subnet router, exposing your home network (`192.168.x.x`) to your tailnet — just as we configured the Mac Mini in Episode 8 of the Satellite series

If you also want the convenience of an HTTPS URL via MagicDNS (recommended — it avoids browser certificate warnings):

```yaml
userspace_networking: false
proxy: true
```

With `proxy: true`, your Home Assistant instance is accessible at:
```
https://homeassistant.your-tailnet.ts.net
```

With a valid TLS certificate managed by Tailscale. No Let's Encrypt configuration. No certificate renewal. The panic room's independent line has end-to-end encryption all the way to the surface.

Click **Save**.

---

## 🚀 Step 4 — Configure Reliability Options and Start

On the **Info** tab:

1. Enable **Start on boot** — Home Assistant restarts after any VM reboot, and the Tailscale add-on must come back with it.
2. Enable **Watchdog** — automatically restarts the add-on if it crashes.
3. Enable **Auto update** — receives Tailscale security patches automatically.
4. Click **Start**.

Watch the **Log** tab as the add-on starts. You will see Tailscale initialising, and then a line like:

```
To authenticate, visit:
https://login.tailscale.com/a/xxxxxxxxxxxxxxx
```

---

## 🔑 Step 5 — Authenticate with Tailscale

Click **Open Web UI** on the add-on page. This opens the Tailscale authentication page (or click the URL from the logs).

Sign in with the same identity provider you used for your other tailnet devices. You will be asked to confirm adding a new device called something like `homeassistant`.

Confirm. The add-on's log will show:

```
Tailscale is running
```

Your Home Assistant instance is now a node in your tailnet.

---

## 🔍 Step 6 — Verify HAOS Is in Your Tailnet

From any other tailnet device (your Mac Mini terminal or iPad Mini terminal), run:

```bash
tailscale status
```

You should see:

```
100.x.x.x  homeassistant        youremail@  linux   -
```

With MagicDNS enabled, you can now access Home Assistant from any tailnet device:

```
http://homeassistant:8123
```

Or, with `proxy: true`:

```
https://homeassistant.your-tailnet.ts.net
```

Open that URL from your **iPad Mini**, connected to mobile data (not your home Wi-Fi). Home Assistant loads. The independent phone line is live.

> 🔐 This is the moment. Home Assistant, running in a Parallels VM on your Mac Mini M4 Pro in Eersel, accessible from your iPad Mini in a coffeeshop in Amsterdam. Encrypted. Authenticated. No port forwarding. No public IP exposed.

---

## 🔒 Step 7 — Update Your Tailscale ACL Policy

In the Tailscale admin console, tag your Home Assistant device and update your ACL:

### Tag the Device

1. Navigate to **Machines** in the admin console.
2. Find `homeassistant`.
3. Click `...` → **Edit ACL tags** → add `tag:home-base`.

### Update the ACL

Add Home Assistant's port to your existing policy:

```json
{
  "acls": [
    {
      "action": "accept",
      "src":    ["group:owner"],
      "dst":    ["*:*"]
    },
    {
      "action": "accept",
      "src":    ["tag:mobile"],
      "dst":    ["tag:home-base:22,5900,8123,21115,21116,21117,21118,21119"]
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

Port **8123** is Home Assistant's HTTP port. If you enabled `proxy: true`, Tailscale serves HTTPS on port 443 — already covered by the `group:owner` → `*:*` rule.

---

## 📊 Step 8 (Optional) — Add the Tailscale Monitoring Integration

Once the add-on is running, you can optionally install the **Tailscale integration** (the API-based monitoring integration, distinct from the add-on). This brings your tailnet's device states into Home Assistant as sensors and binary sensors.

1. Go to **Settings → Devices & Services → + Add Integration**.
2. Search for **Tailscale**.
3. Follow the prompts — you need an **API key** from [login.tailscale.com](https://login.tailscale.com) → Settings → Keys → Generate API key.
4. Enter your **tailnet name** (your email or organisation slug).

The integration creates entities like:
- `binary_sensor.mac_mini_m4_tailscale` — is the Mac Mini connected to the tailnet?
- `binary_sensor.ipad_mini_tailscale` — is the iPad Mini connected?
- `sensor.tailscale_devices` — total device count

This enables automations like:

```yaml
automation:
  - alias: "Alert when Mac Mini drops off tailnet"
    triggers:
      - trigger: state
        entity_id: binary_sensor.mac_mini_m4_tailscale
        from: "on"
        to: "off"
        for: "00:02:00"   # Only alert if offline for 2+ minutes (ignore brief reconnects)
    actions:
      - action: notify.mobile_app_ipad_mini
        data:
          message: >
            ⚠️ Mac Mini has been offline on Tailscale for 2 minutes.
            Check the Parallels VM — did it pause?
```

The panic room's communication system is now self-monitoring. If the line goes down, the system alerts you immediately.

---

## 🏠 The Constellation — Home Assistant Edition

| Device | Role in Tailnet | Status |
|---|---|---|
| Mac Mini M4 Pro | Home Base | ✅ In tailnet |
| HAOS VM (Parallels) | Smart Home Ground Station | ✅ In tailnet |
| iPad Mini | Mobile Command Post | ✅ In tailnet |

Three nodes. One encrypted mesh. Full smart home remote access.

In **Episode 6**, we configure the **Home Assistant Companion App** on the iPad Mini — the mobile command post from which you control the entire house.

> *"We're not leaving this room."*
> — Meg Altman, Panic Room.
> *"We're not losing connection to this room."*
> — Tailscale, ensuring persistent access.

---

*🔐 Panic Room is a series about building a secure, local-first smart home using Home Assistant — installed on a Mac Mini M4 Pro via Parallels, connected via Tailscale, and controlled from an iPad Mini anywhere in the world.*
