---
title: "Panic Room — Ep.4"
part: 4
published: false
description: "The panic room is built. Now Meg moves in — creates her account, maps the house, connects the cameras. Home Assistant onboarding, areas, and your first integrations."
tags: [homeassistant, onboarding, integrations, smarthome]
series: "Panic Room Home Assistant Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/panic_room_home_assistant_series/panic-room-home-assistant-episode-04.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🔐 Moving In (Onboarding, Areas & First Integrations)

> *"It's a great house."*
> — Real estate agent, Panic Room.
> *"It's a great smart home platform."*
> — Also this episode.

---

## 📦 The First Day in a New House

When Meg and her daughter move into the New York brownstone, they do not immediately retreat to the panic room. First they walk through the house — room by room, floor by floor. They learn where things are. They note the light switches, the locks, the cameras. They start to understand the system.

This episode is that walk-through. Home Assistant is installed and running. Now we configure it properly: create your user account, set your home location, define the areas of your home, and connect your first devices.

At the end of this episode, your Home Assistant dashboard will show real data from your real home. The cameras will have feeds. The lights will have switches. The house will have begun to think.

---

## 📋 SIPOC — Onboarding and First Integration

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Home Assistant Core (onboarding wizard) | Running HAOS VM (from Episode 3) | Create admin account → Set home location → Configure units | A configured Home Assistant instance with admin access | You, and anyone else in your household |
| Your smart home devices | Your home address (Eersel, Netherlands) | Add integrations → Assign devices to areas | Devices visible and controllable in HA | Rianne, Beau, Elvis (the latter two not operating dashboards) |
| Home Assistant integration ecosystem | Your device brands (Philips Hue, IKEA, Shelly, etc.) | Create areas → Auto-discovery → Manual integration | Unified device control from a single interface | Your dashboards (Episode 6) |
| Your home network (LAN) | 30 minutes of your time | First automation test | A home that already does something clever | Your future self, who will keep adding integrations |

---

## 👤 Step 1 — Create Your Admin Account

Navigate to `http://homeassistant.local:8123` (or the IP address if mDNS does not resolve).

You will see the Home Assistant welcome screen. Click **"Create my smart home"**.

The first screen asks for your **name**, **username**, and **password**. A few notes:

- The **username** must be lowercase and contain no spaces. If you type a Name with capitals, Home Assistant will suggest a lowercase version. Use it.
- This is your **owner/admin account** — it has full access to everything. Store the password in a password manager.
- You can add more users (family members, with limited permissions) later under Settings → People.

Click **Create account**.

> 🔐 **This account is the master key to the panic room.** Treat it accordingly. Long password, stored securely, two-factor authentication enabled (we'll add that shortly).

---

## 📍 Step 2 — Set Your Home Location

The next screen asks for your home location. This is used for:
- **Sunrise/sunset automations** — turn on outdoor lights at dusk; open the blinds at dawn
- **Weather integration** — local weather data for your exact location
- **Presence detection home zone** — Home Assistant knows you are "home" when your phone GPS is within this zone

Home Assistant will attempt to auto-detect your location from your IP address. For Eersel, this will get you close but likely not precise. Click the map to drag the pin to your exact address, or:

1. Click the location field.
2. Type your address.
3. Accept the suggested location.
4. The radius (default 100m) defines how close you need to be to count as "home". Adjust if your property is large.

**Set your elevation** (used for solar calculations): Eersel, Noord-Brabant is approximately 25 metres above sea level. Enter `25`.

Select your **unit system**: Home Assistant will default to metric based on the Netherlands location. Confirm: Celsius, km/h, metres. Correct.

Click **Next**.

---

## 🔒 Step 3 — Privacy Settings

Home Assistant asks what anonymised data (if any) you want to share with the project. This helps the team understand which integrations are popular and which hardware is in use. It is entirely optional and the data is aggregated.

Our recommendation: share **usage statistics** (which integrations you use, how many devices) but not crash reports if you prefer full privacy. Either choice is fine. The local-first philosophy means this data never includes your device states or home behaviour — only aggregate counts.

Click **Next**.

---

## ✅ Step 4 — Finish Onboarding

Click **Finish**. You are now on the Home Assistant default dashboard — the **Overview** page.

It will look sparse. Perhaps a weather widget. Perhaps some auto-discovered devices if you have Philips Hue or other mDNS-announcing devices on your network. Do not worry about the emptiness. We are about to fill it.

---

## 🔐 Step 5 — Enable Two-Factor Authentication

Before adding any devices, let us secure the admin account properly.

1. Click your **profile icon** (bottom left of the sidebar).
2. Scroll to **Multi-factor Authentication**.
3. Click **Enable** next to **Time-based One-Time Password (TOTP)**.
4. Scan the QR code with your authenticator app (Authy, 1Password, Google Authenticator, etc.).
5. Enter the 6-digit code to confirm.

From now on, logging into Home Assistant requires your password and the current TOTP code. Even if someone guesses your password, they cannot log in without the second factor.

> 🔐 **The panic room door has a secondary lock.** Good. The intruders in the film did not have the combination. Neither will anyone who guesses your password.

---

## 🗺️ Step 6 — Create Your Home's Areas

**Areas** in Home Assistant are logical zones — rooms, floors, outdoor spaces — that you assign devices to. They make dashboards readable, automations expressible in plain language, and the system feel like it maps to your actual house.

Navigate to **Settings → Areas & Zones → Areas**.

Click **Create Area** and add the rooms in your home. For a typical Dutch house in Eersel, this might include:

| Area | Example Devices |
|---|---|
| Living Room | Lights, TV, thermostat, motion sensor |
| Kitchen | Lights, smart plug (kettle), air quality sensor |
| Bedroom | Lights, smart socket, sleep tracker |
| Office / Study | Lights, Mac Mini display, UPS sensor |
| Garden | Outdoor lights, weather station, gate sensor |
| Hallway | Lights, door sensor, motion sensor |
| Utility Room | Washing machine smart plug, NAS sensor |

Home Assistant will suggest areas based on common room names. Add your own as needed.

Areas are visible on the dashboard and in automations. When you say "turn off all lights in the Living Room at 23:00", Home Assistant knows exactly which devices that means.

---

## 🔌 Step 7 — Add Your First Integrations

This is the moment the house starts talking. Navigate to **Settings → Devices & Services**.

Home Assistant will likely have already auto-discovered some devices on your network. You may see:

- **Philips Hue** (if your Hue Bridge is on the network)
- **IKEA Dirigera** or older IKEA hub
- **Sonos** speakers
- **Apple TV**
- **Shelly** devices
- **UniFi Network** (if you use Ubiquiti)
- Your **router** (if it supports UPnP discovery)

Click **Configure** on any auto-discovered device and follow the prompts — usually just pressing a physical button on the hub (Hue) or entering credentials.

For devices that are not auto-discovered, click **+ Add Integration** and search for your device brand. Home Assistant supports over 2,750 integrations at last count. If your device has a name, there is almost certainly an integration for it.

### Essential Integrations to Add First

1. **Weather** — search for `Buienradar` (the Dutch weather service) or `Open-Meteo` for a free, accurate local weather integration. Assign your location.

2. **Sun** — built-in, no configuration needed. Enables sunset/sunrise automations. Just enable it.

3. **Mobile App** — we will configure this fully in Episode 6, but add it now. This creates the infrastructure that the Companion App will connect to.

4. **Tailscale** (monitoring) — we will add this in Episode 5. Skip for now.

5. **Your smart lights** — Philips Hue, IKEA, Shelly, TP-Link Kasa, whatever brand you use. Get at least one set of lights working before moving on.

---

## 🏠 Step 8 — Assign Devices to Areas

Once your first integration is added and devices appear, assign them to areas:

1. Go to **Settings → Devices & Services → Devices**.
2. Click on a device.
3. Under **Area**, select the room it belongs to.

Do this for every device. It takes a few minutes and saves hours of confusion later. A dashboard card for "Living Room Lights" works correctly only if those lights are assigned to the Living Room area.

---

## 🌅 Step 9 — Your First Automation (Sunset Lights)

Let us prove the system is alive with a simple automation: turn on the living room lights at sunset.

Navigate to **Settings → Automations & Scenes → + Create Automation**.

Select **"Start with an empty automation"**.

Configure:

- **Name**: `Living Room lights at sunset`
- **Trigger**: Time → Sun → Sunset (offset: 0 minutes)
- **Condition**: None (or add "Only if someone is home" once presence detection is set up in Episode 6)
- **Action**: Call service → `light.turn_on` → Select your living room lights → Brightness: 80%

Save. In the automation list, click the three-dot menu → **Run** to test it immediately without waiting for actual sunset.

Your living room lights turn on. The house is awake.

> *"It's all connected."*
> — Burnham, Panic Room, explaining the surveillance system.
> *"It's all connected."*
> — Home Assistant, explaining the automation system, with more benevolent intent.

---

## 🛸 What's Next

In **Episode 5**, we install the **Tailscale add-on** — connecting your Home Assistant instance to your tailnet so it is accessible from your iPad Mini, from anywhere in the world, over an encrypted WireGuard® tunnel.

The panic room is furnished. Now we connect its independent communication line to the outside world.

> *"The phones are dead. But we have an independent line."*
> — Meg Altman, Panic Room.
> *"The public internet is hostile. But we have Tailscale."*
> — This series, picking up the thread.

---

*🔐 Panic Room is a series about building a secure, local-first smart home using Home Assistant — installed on a Mac Mini M4 Pro via Parallels, connected via Tailscale, and controlled from an iPad Mini anywhere in the world.*
