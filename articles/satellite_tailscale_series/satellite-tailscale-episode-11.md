---
title: "Satellite Tailscale — Ep.11"
part: 11
published: false
description: "The Google Nest Hub Chalk is a 7-inch touchscreen permanently mounted in your home. It cannot run Tailscale — but it doesn’t need to. Your UDM Pro’s subnet routing already covers it, and Tailscale’s proxy gives it the HTTPS it needs to cast a live Home Assistant dashboard."
tags: [tailscale, homeassistant, googlenest, smarthome]
series: "Satellite Tailscale Series"
cover_image: ""
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛰️ The Home Screen (Google Nest Hub, Home Assistant & the Subnet That Makes It All Work)

> *“Come with me if you want to live.”*
> — T-800, The Terminator.
> *“Come with me if you want a persistent, always-on smart home dashboard permanently glowing on your kitchen worktop.”*
> — Tailscale subnet routing, Episode 11.

## 🖥️ The Permanent Ground Station

Your satellite network now has three active nodes: iPad Mini in your pocket, Mac Mini M4 Pro on the desk, and HAOS in a Parallels VM behind them both. The UDM Pro acts as subnet router for the whole LAN. Everything is connected. Everything is reachable.

But there is one device that does not move. Does not go to coffeeshops. Does not leave for Guernsey in September. It sits — permanently, quietly, glowing — in your home, waiting to be useful.

The **Google Nest Hub 7” (Chalk)**.

A 7-inch touchscreen with Google Assistant built in, connected to your home Wi-Fi via the UniFi Express, showing the time and weather and waiting for you to say “Hey Google” or reach out and tap it. It is, by every reasonable measure, a perfect candidate for a permanent Home Assistant dashboard — your home’s status panel, always on, always visible, always a few centimetres from wherever you happen to be standing in the house.

The challenge: the Nest Hub is a locked Google appliance. You cannot install Home Assistant’s Companion App on it. You cannot install Tailscale on it. You cannot install anything on it. What you *can* do is get it to display a live, interactive Home Assistant dashboard via Google’s built-in **Cast** capability.

That is what this episode is about.

-----

## 📋 SIPOC — The Home Screen

|**Suppliers**                        |**Inputs**                                         |**Process**                                                                |**Outputs**                                                  |**Customers**                                                                         |
|-------------------------------------|---------------------------------------------------|---------------------------------------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------------|
|Google (Nest Hub hardware)           |Nest Hub 7” Chalk on home Wi-Fi (via UniFi Express)|Google Cast integration → trusted_networks auth bypass → cast dashboard URL|Live HA dashboard displayed on Nest Hub touchscreen          |Everyone in the house — a permanently visible smart home control panel                |
|HA Google Cast integration (built-in)|HAOS on Parallels VM with Tailscale proxy enabled  |Tailscale proxy provides HTTPS → satisfies Cast’s HTTPS requirement        |Touch-interactive dashboard — lights, alarm, climate, cameras|Rianne, who can tap the lights off without picking up the iPad                        |
|Tailscale (proxy: true in add-on)    |UDM Pro as subnet router (Episode 10)              |HACS Continuously Casting Dashboards integration → auto-recast             |Persistent, auto-resuming dashboard cast                     |Beau and Elvis, who are indifferent but aesthetically complemented by the ambient glow|
|HACS (Home Assistant Community Store)|The Nest Hub’s LAN IP address (from UniFi console) |trusted_networks + allow_bypass_login in configuration.yaml                |Password-free login for the Nest Hub                         |Your home, operating as intended                                                      |

-----

## 🔍 Understanding the Nest Hub’s Role in the Constellation

Let us be precise about what the Nest Hub is and is not, in the context of your satellite network.

**What the Nest Hub IS:**

- A Cast-capable Chromecast device, visible to Home Assistant via mDNS on your local network
- A Google Assistant voice interface for controlling devices in your Google Home
- A touchscreen that can display any web page cast to it via the Cast protocol
- A device on your `192.168.1.0/24` LAN, reachable via the UDM Pro’s subnet routing

**What the Nest Hub IS NOT:**

- A Tailscale node (cannot run Tailscale; Google manages the OS)
- A Home Assistant Companion App device (no third-party app installs)
- Directly reachable from the tailnet via Tailscale (it has no Tailscale client)

The Nest Hub is, from Tailscale’s perspective, just another device on your home LAN. Your iPad Mini can reach it by its LAN IP (`192.168.1.x`) via the UDM Pro’s subnet routing — the work done in Episode 10. Home Assistant can discover and control it via the Google Cast integration over the LAN.

The integration happens entirely on the LAN side, facilitated by Tailscale making the LAN accessible from anywhere — not by putting Tailscale *on* the Nest Hub.

> 🛰️ **The satellite analogy:** The Nest Hub is like a fixed ground antenna — it does not orbit, it does not roam. It sits in your home and receives signals from your satellites. Your job is to ensure your satellites (HAOS) can reach it (they can — via LAN) and can send it the right signal (the Home Assistant dashboard URL over HTTPS).

-----

## 🌐 The HTTPS Problem — And Why Tailscale Already Solved It

Here is the complication that trips up most people trying to cast a dashboard to a Nest Hub: **Home Assistant Cast requires HTTPS**.

The Cast protocol works by telling the Nest Hub to open a URL in its built-in browser. For the Home Assistant dashboard to connect properly — authenticating, opening a WebSocket connection, receiving live updates — the URL must be served over HTTPS with a valid certificate. Plain `http://192.168.1.x:8123` does not work. The WebSocket handshake fails.

The three conventional solutions to this are:

1. **Nabu Casa subscription** — provides an HTTPS external URL automatically
1. **Let’s Encrypt + DuckDNS** — complex certificate management, requires a public domain
1. **Tailscale proxy** — provides HTTPS via a `*.ts.net` certificate automatically

Option 3 is the one you already have.

In the Satellite Tailscale series (Episode 9 of the Panic Room series, mirroring Episode 5 of the Satellite series), you configured the Tailscale add-on in HAOS with:

```yaml
userspace_networking: false
proxy: true
```

The `proxy: true` setting tells Tailscale to:

1. Obtain a Let’s Encrypt certificate for `homeassistant.your-tailnet.ts.net`
1. Serve HTTPS on port 443 at that address
1. Proxy requests to the HAOS instance running on port 8123

This gives you a valid HTTPS URL — `https://homeassistant.your-tailnet.ts.net` — that is reachable from anywhere in your tailnet and from devices on the LAN that can resolve the `*.ts.net` DNS name.

The Nest Hub, on your LAN, going through the UDM Pro, can reach this HTTPS URL. The certificate is valid. The WebSocket connection succeeds. The dashboard loads.

> 🔐 The Tailscale proxy is the missing HTTPS piece. No DuckDNS. No Let’s Encrypt configuration. No Nabu Casa subscription. Just `proxy: true` in the Tailscale add-on config — which you likely already have.

If you have not yet enabled proxy mode, do it now in the Tailscale add-on (Episode 9 of the Panic Room series / Episode 5 of the Satellite series):

1. In HA → **Settings → Add-ons → Tailscale → Configuration**.
1. Set:
   
   ```yaml
   userspace_networking: false
   proxy: true
   ```
1. Restart the add-on.
1. Your HA instance is now available at `https://homeassistant.your-tailnet.ts.net`.

Verify: open that URL in a browser on your Mac Mini or iPad Mini. It should load the HA UI over HTTPS with a valid certificate.

-----

## 📡 Part 1 — Google Cast Integration

Home Assistant ships with a built-in **Google Cast** integration that auto-discovers Chromecast and Cast-compatible devices on your LAN via mDNS. The Nest Hub is Cast-compatible — Google built it that way.

### Step 1 — Enable the Google Cast Integration

In most HA installations, Google Cast is already configured automatically via mDNS discovery. Check:

1. Go to **Settings → Devices & Services**.
1. Look for **Google Cast** in the integrations list.

If it is not there:

1. Click **+ Add Integration**.
1. Search for **Google Cast**.
1. Click **Configure** — HA will discover Cast devices on your network.
1. Your Nest Hub (named something like “Nest Hub” in Google Home) appears as a discovered device.
1. Click **Submit** to add it.

Once added, your Nest Hub appears as a `media_player` entity in Home Assistant:

```
media_player.nest_hub_chalk
```

(The exact entity name depends on the device name you set in the Google Home app.)

> 📌 **mDNS is required for auto-discovery.** UniFi OS on the UDM Pro supports mDNS forwarding by default — your devices on the LAN should be discoverable without any additional configuration. If the Nest Hub does not appear automatically, add its LAN IP manually in the Google Cast integration options: **Settings → Devices & Services → Google Cast → Configure → Known hosts**.

### Step 2 — Verify the Media Player Entity

In **Developer Tools → States**, filter for `media_player`. You should see your Nest Hub listed with a state like `standby` or `idle`. This confirms Home Assistant can see and communicate with it.

From the HA interface, you can now:

- Send media (audio, video) to the Nest Hub via **Media → Play Media**
- Cast a Home Assistant dashboard to it (the main goal)
- Use it in automations (e.g., announce a voice notification via TTS, or switch to a camera feed when the doorbell rings)

-----

## 🔐 Part 2 — Trusted Networks: Password-Free Login for the Nest Hub

The Nest Hub does not have a keyboard. When it opens a Home Assistant URL and hits the login screen, it cannot type a username and password. It will sit there, with a login form, indefinitely — useful to no one.

The solution is **trusted networks** — a Home Assistant authentication provider that allows specific IP addresses to log in without a password, automatically using a designated user account.

### Step 1 — Create a Dedicated Dashboard User

First, create a Home Assistant user specifically for the Nest Hub. This user will have limited access — no admin rights, just enough to view the dashboard.

1. Go to **Settings → People → Users → Add User**.
1. Set:
- **Display Name**: `Nest Hub`
- **Username**: `nest-hub`
- **Password**: something long and random (it will not be used for login, but HA requires it)
- **Administrator**: Off
1. Save the user.
1. Note the **User ID**: go to **Settings → People → Users**, click the Nest Hub user, and look at the URL. The ID is the long string after `/profile/`.

### Step 2 — Find the Nest Hub’s LAN IP

In the Google Home app, or on the Nest Hub itself:

1. On the Nest Hub: swipe up from the bottom → **Settings** → **Device Information** → **Technical Information** → note the **IP Address**.
1. Alternatively, in the UniFi console: **Clients** → find the Nest Hub by name or MAC address → its assigned IP.

Reserve a static DHCP lease for this IP in the UniFi console so it never changes. A changing IP would break the trusted network configuration.

**In UniFi:**

1. **Settings → Networks** → your LAN network → **DHCP Name Mapping** or **Fixed IP Assignment**.
1. Find the Nest Hub’s MAC address → assign a fixed IP (e.g., `192.168.1.200`).

### Step 3 — Configure `configuration.yaml`

Edit your HA `configuration.yaml` to add the trusted networks authentication provider. In the HA file editor (or Studio Code Server add-on):

```yaml
homeassistant:
  auth_providers:
    - type: trusted_networks
      trusted_networks:
        - 192.168.1.200/32   # Nest Hub Chalk — fixed IP from DHCP reservation
      trusted_users:
        192.168.1.200:
          - USER_ID_OF_NEST_HUB_USER   # The ID from Step 1
      allow_bypass_login: true
    - type: homeassistant    # Keep normal login for all other devices
```

> ⚠️ **Order matters.** The `trusted_networks` provider must come **before** `homeassistant` in the list. If reversed, the Nest Hub still gets prompted to log in.

> ⚠️ **`allow_bypass_login: true` only works when exactly one user is mapped to the device’s IP.** If you map multiple users, the Nest Hub will see a user selection screen rather than logging in automatically. Stick to one user per device.

Restart Home Assistant:

```
Settings → System → Restart
```

### Step 4 — First Login on the Nest Hub

After restarting, cast a dashboard to the Nest Hub (we will set this up permanently in Part 3). When it first opens the HA URL, you will see a login screen — but with the trusted network configuration, there will be a user tile for “Nest Hub” at the top. Tap it. Tap **“Remember this device”** if prompted. The Nest Hub is now logged in and will stay logged in. Subsequent casts require no login.

-----

## 📺 Part 3 — Continuously Casting Dashboards (HACS Integration)

The native Home Assistant Cast action works — but it casts the dashboard once. When the Nest Hub’s screensaver kicks in after a few minutes of inactivity, or when it plays audio, or when it reboots, the dashboard disappears. You would need to manually recast every time.

**Continuously Casting Dashboards** is a HACS integration by b0mbays that solves this: it monitors your Cast devices and automatically recasts the configured dashboard whenever the device stops displaying it. Set it once; it runs forever.

### Step 1 — Install HACS

If HACS is not yet installed, install it first. In HA:

1. Go to **Settings → Add-ons → Add-on Store**.
1. Install the **Terminal & SSH** add-on (or use Studio Code Server).
1. Open a terminal and run the HACS install script:
   
   ```bash
   wget -O - https://get.hacs.xyz | bash -
   ```
1. Restart Home Assistant.
1. Go to **Settings → Devices & Services → + Add Integration → HACS**.
1. Authenticate with your GitHub account.

### Step 2 — Install Continuously Casting Dashboards via HACS

1. Open **HACS** in the HA sidebar.
1. Click the three dots (⋮) → **Custom repositories**.
1. Add:
- **Repository**: `b0mbays/continuously_casting_dashboards`
- **Category**: Integration
1. Click **Add**, then close the dialog.
1. Find **Continuously Cast Dashboards** in the HACS Integrations list → **Download**.
1. Restart Home Assistant.

### Step 3 — Install ha-catt-fix (Frontend Resource)

This HACS frontend resource prevents the dashboard from disconnecting after 10 minutes — a known issue with cast sessions:

1. In HACS → **Frontend** tab → **Explore and download repositories**.
1. Search for **ha-catt-fix** → Download.
1. Verify: open your dashboard → three dots → **Edit** → three dots → **Manage resources** → confirm `ha-catt-fix` is listed.

### Step 4 — Design a Touch-Optimised Dashboard for the Nest Hub

The Nest Hub’s 7-inch display is excellent for ambient information, but your regular desktop HA dashboard will be too cramped and too mouse-oriented. Create a dedicated touch dashboard.

In HA:

1. **Settings → Dashboards → + Add Dashboard**.
1. Name: `Nest Hub`
1. URL: `nest-hub`
1. Icon: `mdi:tablet-dashboard`
1. Do NOT set it as default (it is for the Nest Hub, not for browsers).

Design considerations for a 7-inch touch display:

- **Large buttons** — 48px minimum tap target; use Tile cards
- **High contrast** — the Nest Hub screen in a bright room needs readable colours
- **Minimal scrolling** — everything important should be visible without swiping
- **Three views maximum** — use the top-row tabs

A sample Nest Hub dashboard layout in YAML:

```yaml
title: Nest Hub
views:
  - title: Home
    icon: mdi:home
    path: nest-hub-home
    badges: []
    cards:
      - type: custom:clock-weather-card   # Community weather card (install via HACS)
        entity: weather.eersel
        name: Eersel
        
      - type: grid
        columns: 2
        square: false
        cards:
          - type: tile
            entity: alarm_control_panel.alarmo
            name: Alarm
            icon: mdi:shield-home
            
          - type: tile
            entity: person.willem
            name: Willem
            
          - type: tile
            entity: person.rianne
            name: Rianne
            
          - type: tile
            entity: binary_sensor.front_door
            name: Front Door
            icon: mdi:door

      - type: grid
        columns: 3
        square: false
        cards:
          - type: tile
            entity: light.living_room
            name: Living Room
          - type: tile
            entity: light.kitchen
            name: Kitchen
          - type: tile
            entity: light.bedroom
            name: Bedroom

  - title: Climate
    icon: mdi:thermometer
    path: nest-hub-climate
    cards:
      - type: thermostat
        entity: climate.living_room
        
  - title: Cameras
    icon: mdi:camera
    path: nest-hub-cameras
    cards:
      - type: picture-entity
        entity: camera.front_door
        show_state: false
      - type: picture-entity
        entity: camera.garden
        show_state: false
```

### Step 5 — Configure Continuously Casting Dashboards via UI

After installing the integration, go to:
**Settings → Devices & Services → Continuously Cast Dashboards → Configure**

Set up your Nest Hub:

|Field            |Value                                                                   |
|-----------------|------------------------------------------------------------------------|
|**Device name**  |`Nest Hub` (exact name as in Google Home app)                           |
|**Dashboard URL**|`https://homeassistant.your-tailnet.ts.net/nest-hub/nest-hub-home?kiosk`|
|**Cast delay**   |`45` seconds between state checks                                       |
|**Start time**   |`07:00` (when to start casting)                                         |
|**End time**     |`23:30` (when to stop — let it sleep at night)                          |
|**Volume**       |`5` (low — ambient display, not a speaker)                              |


> 📌 **The URL uses the Tailscale HTTPS address** (`homeassistant.your-tailnet.ts.net`), not the plain HTTP LAN address. This is what satisfies the Cast HTTPS requirement. The Nest Hub, on your LAN, resolves this `*.ts.net` DNS name and reaches the Tailscale proxy, which serves the dashboard over HTTPS.

> 📌 **`?kiosk` at the end of the URL** hides the HA sidebar and header, giving you a full-screen dashboard with no navigation chrome. Install the **Kiosk Mode** HACS frontend integration for this to work properly. Search HACS → Frontend → **Kiosk Mode** → Download.

-----

## 🗣️ Part 4 — Google Assistant + Home Assistant

The Nest Hub is not just a display — it is also a Google Assistant speaker. You can say “Hey Google, turn off the living room lights” and the Nest Hub executes it via Google’s cloud.

To make this work with Home Assistant devices (including those not natively in Google Home), connect the Google Nest integration:

### Home Assistant → Google Assistant (via Google Home)

1. In HA: **Settings → Devices & Services → + Add Integration → Google**.
1. Follow the OAuth flow to connect your Google account.
1. Devices you have exposed in HA will appear in Google Home and become voice-controllable from the Nest Hub.

This is cloud-dependent: commands go iPad Mini → Google Cloud → HA → device. The path is less elegant than local control, but for voice commands from a Nest Hub, the latency is acceptable and the convenience is significant.

> ⚠️ **The Google Nest SDM integration ($5 fee)** gives you camera streams, thermostat control, and sensor data from Google/Nest devices in HA. This is separate from the Google Cast integration. If you want your Nest Hub to *show* HA dashboards (Cast, covered above) and *control* HA devices by voice (Google Home, covered above), you do not need the SDM integration. The SDM integration is only needed if you want to bring Google/Nest device data *into* HA.

-----

## 📱 Part 5 — Voice Automations: “Hey Google” Triggers HA

The most satisfying integration: using the Nest Hub as a voice trigger for Home Assistant automations.

This works via the **Google Home + Home Assistant** cloud integration. Once connected, you can create Routines in the Google Home app that trigger HA scenes or scripts:

**Example routine in Google Home:**

- Trigger: “Hey Google, goodnight”
- Actions:
  - Turn off lights (Google Home)
  - Call Home Assistant webhook: `https://homeassistant.your-tailnet.ts.net/api/webhook/goodnight_routine`

In HA, create an automation triggered by that webhook:

```yaml
automation:
  - alias: "Goodnight via Google"
    triggers:
      - trigger: webhook
        webhook_id: "goodnight_routine"
        allowed_methods:
          - POST
    actions:
      - action: script.goodnight   # The Goodnight script from Episode 7
```

Now “Hey Google, goodnight” from the Nest Hub runs your full HA Goodnight routine — locks the front door, dims the bedroom lights, sets the thermostat to 18°C, and sends a confirmation notification to your iPad Mini.

The Nest Hub is now a full voice interface for your home, backed by Home Assistant’s automation engine.

-----

## 🔧 Troubleshooting Common Issues

|Symptom                                      |Cause                                         |Fix                                                                                                        |
|---------------------------------------------|----------------------------------------------|-----------------------------------------------------------------------------------------------------------|
|Dashboard shows “not connected” after casting|HTTPS WebSocket fails                         |Ensure proxy: true in Tailscale add-on; verify `https://homeassistant.your-tailnet.ts.net` loads in browser|
|Nest Hub not discovered by HA                |mDNS not working                              |Enter Nest Hub’s LAN IP manually in Google Cast integration options                                        |
|Dashboard shows login screen, no bypass      |trusted_networks misconfigured                |Verify Nest Hub IP is reserved, check configuration.yaml syntax, ensure `allow_bypass_login: true` is set  |
|Dashboard disappears after 10 min            |Missing ha-catt-fix                           |Install ha-catt-fix via HACS Frontend                                                                      |
|Cast keeps reverting to weather/clock        |Continuously Casting Dashboards not running   |Check integration is configured; verify cast_delay and time window settings                                |
|“Hey Google” commands don’t reach HA         |Google Home integration not set up            |Set up HA → Google Assistant integration via **Settings → Devices & Services → Google**                    |
|Dashboard cuts off at edges                  |Not using `?kiosk` or Kiosk Mode not installed|Add `?kiosk` to URL and install Kiosk Mode via HACS                                                        |

-----

## 🛸 The Constellation — Final Expanded View

|Device             |Role                           |Tailscale       |LAN reachable via subnet?   |
|-------------------|-------------------------------|----------------|----------------------------|
|Mac Mini M4 Pro    |Home Base                      |✅ Native        |✅ Direct                    |
|HAOS VM (Parallels)|Smart Home Platform            |✅ Add-on + proxy|✅ Direct                    |
|UDM Pro            |Network Gateway + Subnet Router|✅ tailscale-udm |✅ Is the gateway            |
|UniFi Express      |Wi-Fi Satellite                |➖ Not needed    |✅ Extends LAN               |
|Nest Hub Chalk     |Permanent Home Dashboard       |❌ Not possible  |✅ Via UDM Pro subnet routing|
|iPad Mini          |Mobile Command Post            |✅ iOS app       |✅ When home                 |

The Nest Hub sits permanently in your home — no Tailscale, no Companion App, no special treatment required. The subnet routing from Episode 10 means your tailnet can reach it. Tailscale’s proxy on HAOS gives it the HTTPS it needs. The continuously casting integration keeps the dashboard alive. The trusted network authentication keeps it logged in.

Your home now has a permanent, always-on, touch-interactive control panel in Chalk white, glowing gently from the worktop.

> *“It’s in your nature to destroy yourselves.”*
> — T-800, Terminator 2: Judgment Day.
> *“It’s in your nature to need a convenient place to turn off the kitchen lights without reaching for your iPad.”*
> — Google Nest Hub, Episode 11.

-----

## 🔭 Further Reading

- [Home Assistant Google Cast integration](https://www.home-assistant.io/integrations/cast/)
- [Home Assistant Trusted Networks authentication](https://www.home-assistant.io/docs/authentication/providers/#trusted-networks)
- [Continuously Casting Dashboards (HACS)](https://github.com/b0mbays/continuously_casting_dashboards)
- [ha-catt-fix (HACS frontend resource)](https://github.com/swiergot/ha-catt-fix)
- [Kiosk Mode (HACS)](https://github.com/NemesisRE/kiosk-mode)
- [Tailscale HTTPS certificates documentation](https://tailscale.com/kb/1153/enabling-https)
- [Casting HA dashboards to Nest Hub — vNinja.net](https://vninja.net/2025/07/20/homeassistant-google-nest-hub-2nd-gen-take2/)

-----

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between.*
