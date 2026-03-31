---
title: "Satellite Tailscale — Ep. 9"
part: 9
published: false
description: "Your Home Assistant instance controls every light, thermostat, and camera in your home. With the Tailscale add-on installed, it joins your satellite network — accessible from your iPad Mini in any coffeeshop, anywhere on Earth."
tags: [tailscale, homeassistant, smarthome, homelab]
series: "Satellite Tailscale Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/satellite_tailscale_series/satellite-tailscale-episode-09.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛰️ Episode 9: The Smart Home Ground Station (Tailscale in Home Assistant)

> *“Get away from her, you witch!”*
> — Ellen Ripley, Aliens (a Schwarzenegger contemporary production).
> *“Get away from it, you open port!”*
> — You, discovering your Home Assistant instance has been exposed to the public internet.

-----

## 🏠 The Problem with Smart Home Remote Access

You have spent weeks setting up Home Assistant. Your lights respond to voice commands. Your thermostat knows when you leave the house. Your security cameras upload snapshots when motion is detected at 02:00. The fish feeder fires at 08:00 and 18:00, reliably, every day, without human intervention.

And then you leave for a long weekend and realise: you cannot check any of it from outside your home network.

The conventional solutions to this problem range from *mildly inconvenient* to *actively dangerous*:

- **Open a port on your router and expose Home Assistant to the internet** — technically works; also technically invites every port-scanner on the planet to your front door.
- **Use a dynamic DNS service + Let’s Encrypt + a reverse proxy** — works well, but requires maintenance, certificate renewal, and a patience for YAML that not everyone possesses.
- **Subscribe to Home Assistant Cloud (Nabu Casa)** — excellent service, worth supporting, costs money monthly, and routes your traffic through a third-party server.
- **Install the Tailscale add-on** — takes seven minutes, costs nothing extra, routes traffic directly between your devices, and works through any NAT.

We are going with the last option. Obviously.

-----

## 📋 SIPOC — The Smart Home Satellite

|**Suppliers**                               |**Inputs**                                  |**Process**                                                |**Outputs**                                                           |**Customers**                                 |
|--------------------------------------------|--------------------------------------------|-----------------------------------------------------------|----------------------------------------------------------------------|----------------------------------------------|
|Home Assistant Add-on Store                 |Home Assistant OS or Supervised installation|Install Tailscale add-on → Start → Authenticate            |Home Assistant joins your tailnet as a named node                     |You, checking the thermostat from a coffeeshop|
|Tailscale Inc. (unofficial add-on by Frenck)|Your existing tailnet (Episodes 2–8)        |Enable userspace networking → Optional: proxy + Funnel     |`homeassistant.your-tailnet.ts.net` reachable from all tailnet devices|Your iPad Mini, anywhere in the world         |
|Home Assistant Community                    |Tailscale account (free tier sufficient)    |Update ACL policy → Tag Home Assistant as `tag:home-base`  |HTTPS access to HA dashboard via MagicDNS                             |Family members you invite to your tailnet     |
|Your home hardware (Pi, NUC, etc.)          |Tailscale installed on iPad Mini, Mac Mini  |Optional: HTTPS via Tailscale Funnel for non-tailnet access|Smart home fully remotely operable                                    |Your peace of mind, on the road               |

-----

## 🤖 Two Ways to Connect Home Assistant to Tailscale

Before we start, a small clarification that has caused confusion in many a forum post:

There are **two different Tailscale things** in the Home Assistant ecosystem:

1. **The Tailscale Add-on** — installs Tailscale *inside* Home Assistant OS, making the HA instance itself a node in your tailnet. This is what we want.
1. **The Tailscale Integration** — connects to the Tailscale API to *monitor* your tailnet from within Home Assistant (tracking which devices are online). This is useful but separate — it does not provide VPN access.

We will install the **add-on** first (network access), and then optionally configure the **integration** afterwards (monitoring). Think of the add-on as the satellite dish, and the integration as the telemetry readout.

> *“There are two kinds of people.”*
> — Arnold Schwarzenegger, probably, in some film at some point.
> *“There are two kinds of Tailscale things in Home Assistant. Know which one you need.”*
> — This episode.

-----

## 🛠️ Step 1 — Install the Tailscale Add-on

The Tailscale add-on for Home Assistant is maintained by **Frenck** (Franck Nijhof), a core Home Assistant developer. It lives in the **Home Assistant Community Add-ons** repository.

### Add the Community Add-ons Repository

If you have not already added the Community Add-ons repository to your HA instance:

1. In Home Assistant, navigate to **Settings → Add-ons → Add-on Store**.
1. Click the **three-dot menu** (⋮) in the top right.
1. Select **Repositories**.
1. Add the following URL:
   
   ```
   https://github.com/hassio-addons/repository
   ```
1. Click **Add** → **Close**.

Refresh the add-on store page. The Community Add-ons section will appear.

### Find and Install Tailscale

1. In the Add-on Store, search for **Tailscale**.
1. Click on the **Tailscale** add-on (the one by Frenck / Home Assistant Community Add-ons).
1. Click **Install**.

The installation takes a minute or two. Go make a coffee. You have earned it.

-----

## ⚙️ Step 2 — Configure the Add-on

Before starting the add-on, configure it. Click the **Configuration** tab on the Tailscale add-on page.

The minimal configuration for joining your tailnet (no Funnel, no custom domain) looks like this:

```yaml
userspace_networking: false
```

Setting `userspace_networking: false` tells Tailscale to use the kernel-level WireGuard® interface rather than a userspace implementation. This gives better performance and, crucially, allows Home Assistant to act as a **subnet router** — making your home network accessible to your tailnet, just as we configured the Mac Mini in Episode 8.

If you want to also enable the **Tailscale proxy** (which gives your HA instance an HTTPS URL on your tailnet without any certificate configuration):

```yaml
userspace_networking: false
proxy: true
```

And if you want **Tailscale Funnel** (which makes your HA instance accessible from the public internet via a Tailscale-managed URL — useful for family members who do not have Tailscale installed):

```yaml
userspace_networking: false
proxy: true
funnel: true
```

> 🛰️ **For our use case** — iPad Mini in a coffeeshop, accessing HA on your tailnet — `userspace_networking: false` is sufficient. Enable `proxy: true` if you want the convenience of `https://homeassistant.your-tailnet.ts.net`. Enable `funnel: true` only if you need non-tailnet access.

Click **Save**.

-----

## 🚀 Step 3 — Start the Add-on and Authenticate

On the **Info** tab of the Tailscale add-on:

1. Enable **Start on boot** — critical for reliability.
1. Enable **Watchdog** — restarts the add-on automatically if it crashes.
1. Enable **Auto update** — keeps Tailscale current with security patches.
1. Click **Start**.

Once running, click **Open Web UI**. This opens the Tailscale authentication page.

You may see a message about the device’s key needing renewal. Click **Reauthenticate** and follow the prompts to sign in with the same identity provider you used for your other tailnet devices.

Once authenticated, you will see a confirmation that the device has been added to your tailnet. Home Assistant is now a satellite.

> *“I’ll be back.”*
> — T-800.
> *“Start on boot: enabled. I will indeed be back.”*
> — The Tailscale add-on, silently, on every reboot.

-----

## 🔍 Step 4 — Verify Home Assistant Is in Your Tailnet

From your Mac Mini or iPad Mini, run:

```bash
tailscale status
```

You should see your Home Assistant instance listed:

```
100.x.x.x  homeassistant        youremail@  linux   -
```

With MagicDNS enabled (which it is, from Episode 5), you can now access Home Assistant from any tailnet device at:

```
http://homeassistant:8123
```

Or, with the proxy option enabled:

```
https://homeassistant.your-tailnet.ts.net
```

Open that URL from your iPad Mini in a coffeeshop. Home Assistant loads. Your living room lights are in the palm of your hand.

-----

## 🔒 Step 5 — Update Your ACL Policy

Back in the Tailscale admin console, let us tag Home Assistant and update the access policy.

### Tag Your Home Assistant Device

1. Navigate to **Machines** in the admin console.
1. Find your Home Assistant node.
1. Click `...` → **Edit ACL tags**.
1. Add `tag:home-base` (same tag as your Mac Mini — both are home base nodes).

### Update the ACL

Add Home Assistant’s specific port to your existing ACL:

```json
{
  "acls": [
    // Owner can access everything
    {
      "action": "accept",
      "src":    ["group:owner"],
      "dst":    ["*:*"]
    },
    // Mobile devices can reach home-base nodes on specific ports
    {
      "action": "accept",
      "src":    ["tag:mobile"],
      "dst":    [
        "tag:home-base:22,5900,8123,21115,21116,21117,21118,21119"
      ]
    }
  ]
}
```

Port **8123** is Home Assistant’s default HTTP port. If you enabled the proxy option and are using HTTPS via MagicDNS, traffic goes on port 443 — but for direct tailnet access, 8123 is the one to open.

-----

## 📱 Step 6 — Configure the Home Assistant Companion App

The Home Assistant mobile app (the **Companion App**) is the primary way to interact with HA from your iPad Mini. Let us configure it to use your Tailscale connection.

1. Install the **Home Assistant** app from the App Store on your iPad Mini.
1. Open the app and tap **Manual entry** (if auto-discovery does not find your instance).
1. Enter the Home Assistant URL:
- Without proxy: `http://homeassistant:8123`
- With proxy (HTTPS): `https://homeassistant.your-tailnet.ts.net`
1. Tap **Connect**.
1. Log in with your Home Assistant credentials.

The Companion App supports **multiple server URLs** — you can configure a local URL (for when you are at home on your home network) and an external URL (your Tailscale MagicDNS address for when you are away). The app switches between them automatically based on which network you are connected to.

To configure this:

1. In the Companion App: **Settings → Companion App → [your server name]**.
1. Under **Connection**, add:
- **Internal URL**: `http://homeassistant.local:8123` (for home network)
- **External URL**: `http://homeassistant:8123` (for tailnet access away from home)

When you are at home, the app talks directly to HA over your local network. When you are in a coffeeshop, it connects via Tailscale. You do not have to think about which one — the app figures it out.

> 🛰️ The satellite network is now smart enough to know when you are in its orbit and when you are not. It adjusts accordingly. Like a well-trained ground station crew.

-----

## 🌐 Bonus: Tailscale Funnel — Access for the Non-Tailscale Household

You have parents. They do not have Tailscale installed. They want to check whether you fed the cat. (You have. Twice. You are responsible.)

**Tailscale Funnel** allows you to expose your Home Assistant instance to the public internet via a Tailscale-managed subdomain (`homeassistant.your-tailnet.ts.net`), without port-forwarding, without a public IP, and with Tailscale handling TLS termination.

To enable it, update your add-on configuration to:

```yaml
userspace_networking: false
proxy: true
funnel: true
```

Restart the add-on. Check the **Logs** tab — you will see a line like:

```
INFO: Tailscale Funnel is enabled:
INFO: Your Home Assistant instance is publicly available at:
INFO: https://homeassistant.your-tailnet.ts.net
```

Share that URL with your parents. They open it in any browser, no Tailscale required, TLS certificate included, courtesy of Tailscale.

> ⚠️ **Security note:** Enabling Funnel exposes your HA instance to the public internet. Ensure your Home Assistant is on a current version, use strong passwords, enable two-factor authentication, and consider enabling the Home Assistant IP ban (`login_attempts_threshold`) as a brute-force deterrent. The Terminator checks all these boxes. So should you.

-----

## 🏠 Bonus: Home Assistant as a Subnet Router

In Episode 8, we configured the Mac Mini M4 Pro as a subnet router, making your entire home network accessible via Tailscale. Your Home Assistant instance can do the same job — and for some setups (where HA is the always-on device, not the Mac Mini), it makes more sense for HA to carry this responsibility.

In the add-on configuration:

```yaml
userspace_networking: false
proxy: true
tags:
  - tag:home-base
```

Then, in the Tailscale admin console, approve the subnet route for your home network (e.g., `192.168.1.0/24`) on the Home Assistant node.

Now your iPad Mini can reach *every device on your home network* — smart plugs, cameras, the NAS, the Pi-hole — via the Home Assistant node acting as the gateway. One satellite to rule them all.

-----

## 📊 Bonus: The Tailscale Integration (Monitoring Your Tailnet from HA)

Once the add-on is running and HA is on your tailnet, you can optionally install the **Tailscale Integration** to bring tailnet monitoring *into* Home Assistant.

1. Navigate to **Settings → Devices & Services → Add Integration**.
1. Search for **Tailscale**.
1. Follow the prompts — you will need an **API access token** from the Tailscale admin console (Admin → Settings → API keys).
1. Enter your **tailnet name** (your email or organisation name).

The integration creates sensors for:

- Total devices in your tailnet
- Number of currently connected devices
- Number of disconnected devices
- Individual binary sensors per device (online/offline)

This unlocks automations like:

```yaml
automation:
  - alias: "Alert when Mac Mini goes offline"
    triggers:
      - trigger: state
        entity_id: binary_sensor.mac_mini_m4_tailscale
        from: "on"
        to: "off"
    actions:
      - action: notify.mobile_app_ipad_mini
        data:
          message: "⚠️ Mac Mini went offline. Did the cat unplug it?"
```

Your satellite network is now self-monitoring. If a ground station goes dark, you get an alert on your iPad Mini. The Terminator would call this situational awareness. We call it good engineering.

-----

## 🤖 The Constellation — Updated Status

|Device         |Role                     |Tailscale         |Status                              |
|---------------|-------------------------|------------------|------------------------------------|
|Mac Mini M4 Pro|Home Base / Subnet Router|✅ Always-on node  |Full desktop, SSH, subnet gateway   |
|iPad Mini      |Mobile Ground Station    |✅ Roaming node    |Connects from anywhere              |
|Home Assistant |Smart Home Ground Station|✅ Add-on installed|All automations, remotely accessible|

Three satellites. One tailnet. One flat white.

-----

## ☕ The Complete Coffeeshop Scenario

You are in the coffeeshop. The oat milk flat white is exceptional today. Your Tailscale connection is up. You open the Home Assistant Companion App on your iPad Mini.

From there, you can:

- **Check live camera feeds** from every room
- **Adjust the thermostat** before you head home
- **Turn off a light** you are now certain you left on
- **Trigger automations** manually (goodbye, morning routine — I am running it from here)
- **Check the fish feeder log** — yes, it fired at 08:00, the fish are fine
- **Arm or disarm the alarm**
- **See who is at the front door** if you have a video doorbell

All of this, secured by WireGuard®, authenticated by your Tailscale identity, governed by your ACL policy, from a coffeeshop with perfectly acceptable wi-fi.

> *“Come with me if you want to live.”*
> — T-800, Terminator 2.
> *“Come into my tailnet if you want your smart home to remain accessible.”*
> — Tailscale, Home Assistant episode.

-----

## 🔭 Further Reading

- [Tailscale blog: Remotely access Home Assistant](https://tailscale.com/blog/remotely-access-home-assistant)
- [Home Assistant Tailscale add-on (GitHub / Frenck)](https://github.com/hassio-addons/addon-tailscale)
- [Home Assistant Tailscale integration docs](https://www.home-assistant.io/integrations/tailscale/)
- [Tailscale Funnel documentation](https://tailscale.com/kb/1223/tailscale-funnel)
- [Home Assistant Companion App](https://companion.home-assistant.io/)

-----

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between.*
