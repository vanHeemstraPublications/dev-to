---
title: "Panic Room — Ep.6"
published: false
description: "Meg Altman controlled the panic room from inside it. You control your smart home from your iPad Mini — in the coffeeshop, the airport, the train. The Home Assistant Companion App is your handheld control panel."
tags: [homeassistant, companionapp, ipad, remoteaccess]
series: "Panic Room Home Assistant Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/panic_room_home_assistant_series/panic-room-home-assistant-episode-06.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🔐 The Mobile Command Post (Companion App on iPad Mini)

> *"We're in here. We can see everything."*
> — Meg Altman, Panic Room, watching the surveillance feeds from inside the safe room.
> *"We're out here. We can see everything."*
> — You, watching your home's dashboards from a coffeeshop in Amsterdam.

---

## 📱 The Handheld Control Panel

In the film, the panic room's greatest asset — beyond the steel walls — is the surveillance panel. Meg can see every room, every corridor, every entrance from inside the room. She has more situational awareness than the intruders who are physically walking through the house.

The Home Assistant Companion App is your handheld equivalent of that surveillance panel. It is not just a remote dashboard — it is a two-way communication channel between you and your home:

- You see what the house sees (cameras, sensors, device states)
- The house sees where you are (GPS presence detection)
- You can command the house (turn on lights, arm alarms, trigger automations)
- The house can alert you (push notifications for motion, door sensors, anomalies)

And with Tailscale providing the secure connection (Episode 5), this works from anywhere on Earth — not just your home network.

---

## 📋 SIPOC — The Mobile Command Post

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Apple App Store | iPad Mini (any recent model) | Install Companion App → Connect to HA instance | Full Home Assistant dashboard on iPad Mini | You, from anywhere in the world |
| Home Assistant (mobile_app integration) | Running HAOS with Tailscale (Episodes 3–5) | Configure internal + external URL → Grant permissions | Presence detection, push notifications, remote control | Rianne, on her phone (add her separately) |
| Tailscale (Episodes 4–5 of Satellite series) | Your Tailscale-connected iPad Mini | Enable location tracking → Configure home zone | GPS-based presence detection (home/away) | Automations that respond to your physical presence |
| iOS notification system | Your HA account credentials | Set up notification actions → Test alerts | Actionable push notifications from Home Assistant | Your nervous system, alerted only for things that matter |

---

## 📲 Step 1 — Install the Companion App

Open the **App Store** on your iPad Mini. Search for **Home Assistant**.

The app is published by **Nabu Casa** — the company that funds Home Assistant development through its cloud subscription service (which we are not using, but they deserve credit for the excellent free app). It is free.

Install and open it.

---

## 🔗 Step 2 — Connect to Your Home Assistant Instance

When the app opens, it will scan your local network for a Home Assistant instance. If you are on your home Wi-Fi, it will likely find `homeassistant.local` automatically and display it for selection.

If you are on mobile data or a different network (which is precisely the point of this setup), tap **Manual entry** and enter:

**For Tailscale connection (external URL):**
```
http://homeassistant:8123
```
or, if you enabled `proxy: true` in the Tailscale add-on:
```
https://homeassistant.your-tailnet.ts.net
```

Tap **Connect**. Enter your Home Assistant username and password (and the TOTP code if you enabled 2FA in Episode 4 — you did, didn't you).

The app connects. Your Home Assistant dashboard appears on your iPad Mini screen.

> 🔐 **You are now looking at your home, from outside your home.** The surveillance panel is in your hand.

---

## ⚙️ Step 3 — Configure Internal and External URLs

The Companion App can automatically switch between a **local URL** (when you are at home) and an **external URL** (when you are away). This gives you the fastest possible connection when local and a reliable connection when remote.

In the Companion App:

1. Tap the **three-line menu** (☰) → **Settings** → **[your HA instance name]** → **Connection**.
2. Set **Internal URL**: `http://homeassistant.local:8123`
   - This is used when you are connected to your home Wi-Fi
3. Set **External URL**: `http://homeassistant:8123` (or `https://homeassistant.your-tailnet.ts.net` with proxy)
   - This is used when you are away — via Tailscale

The app determines which URL to use based on your network — it tries the internal URL first, falls back to external. You never have to think about it.

---

## 📍 Step 4 — Grant Location Permissions (Presence Detection)

This is the step that turns your iPad Mini from a remote control into an active participant in your smart home.

When prompted, allow Home Assistant to access your **location** — select **"Always Allow"** (not just "While Using the App"). This enables background location updates, which is how the app tells Home Assistant where you are even when the app is not open.

In the Companion App:

1. Go to **Settings → [your HA instance] → Sensors**.
2. Locate **Location** sensors and ensure they are enabled.
3. You will see sensors like:
   - `sensor.ipad_mini_geocoded_location` — your current address, in text
   - `device_tracker.ipad_mini` — your location as a GPS coordinate, tracked by HA zone
   - `sensor.ipad_mini_distance_from_home` — how far you are from the home zone
   - `binary_sensor.ipad_mini_is_home` — are you in the home zone? True/False

The `device_tracker.ipad_mini` entity is what the home zone automation system uses. When your iPad Mini enters the zone defined during onboarding (Eersel, 100m radius), Home Assistant marks you as "home". When you leave, you are "away".

> 🔐 This is the equivalent of the panic room knowing when Meg is inside it versus when she is not. The system adjusts its behaviour based on her presence. So does yours.

---

## 🔔 Step 5 — Enable Push Notifications

Push notifications are how your home talks back to you. Configure them:

1. In the Companion App, go to **Settings → [instance] → Notifications**.
2. Allow notifications when prompted by iOS.
3. In Home Assistant (web UI or app), navigate to **Settings → Devices & Services → Devices** and find your iPad Mini. You will see it registered as a device with a **Notifications** service: `notify.mobile_app_ipad_mini`.

Test it from the HA web UI:

1. Go to **Developer Tools → Services**.
2. Call service: `notify.mobile_app_ipad_mini`
3. Data:
   ```yaml
   message: "The panic room is operational."
   title: "Home Assistant"
   ```
4. Click **Call Service**.

Your iPad Mini will receive a push notification — from your Home Assistant instance, running in a Parallels VM, on your Mac Mini M4 Pro, in your house in Eersel. Over Tailscale. End-to-end encrypted.

---

## 📊 Step 6 — Create a Dashboard for the iPad Mini

The default Home Assistant dashboard is designed for desktop browsers. On an iPad Mini, it may feel cramped or not take advantage of the screen's size and touch capabilities.

Create a dedicated iPad Mini dashboard:

1. In the HA web UI, go to **Overview** → click the three-dot menu → **Edit Dashboard**.
2. Click **+ Create new dashboard** (or duplicate the existing one).
3. Name it `iPad Mini`.
4. Set it as the **default dashboard** for your user (under your profile settings).

In the Companion App, you can switch between dashboards by tapping the menu icon and selecting the dashboard name.

Design the iPad Mini dashboard with touch in mind:

- **Larger buttons** for lights and switches (easier to tap)
- **Camera feeds** in a grid view for a quick visual overview
- **Person entities** showing who is home
- **Area-based cards** — one card per room, expandable
- **Quick action buttons** — "I'm leaving", "Goodnight", "Movie Mode" (these trigger scripts/scenes)

Home Assistant's **Tile cards** work particularly well on touch screens — they are large, tappable, and show state clearly at a glance.

---

## 📡 Step 7 — Configure Actionable Notifications

Standard push notifications tell you something happened. **Actionable notifications** let you respond without opening the app.

Example: when the front door sensor opens after 22:00, send a notification with two actions: **"That's me"** (dismiss) and **"Alert me"** (trigger an alarm sound).

In HA configuration (via the YAML editor or automation UI):

```yaml
automation:
  - alias: "Late night front door alert"
    triggers:
      - trigger: state
        entity_id: binary_sensor.front_door
        to: "on"
    conditions:
      - condition: time
        after: "22:00:00"
    actions:
      - action: notify.mobile_app_ipad_mini
        data:
          title: "🚪 Front door opened"
          message: "The front door opened at {{ now().strftime('%H:%M') }}."
          data:
            actions:
              - action: "DISMISS"
                title: "That's me"
              - action: "ALERT"
                title: "Alert me"
```

In the Companion App, responding to "Alert me" can trigger another automation via the `mobile_app_notification_action` event — for example, flashing all lights red, triggering a siren, or sending a second notification to another household member.

> 🔐 The panic room did not just show feeds. It let Meg make decisions and take action. Your notification system does the same — from anywhere in the world.

---

## 👥 Step 8 — Add Rianne's Phone to the System

The household presence detection works best when every person's device is tracked. Add Rianne's phone:

1. In HA: **Settings → People → Add Person → Add**.
2. Create a person: `Rianne`.
3. Create a Home Assistant user for her: **Settings → People → Users → Add User** (limit-access user, not admin).
4. On Rianne's phone: install the Home Assistant Companion App, connect with her credentials.
5. In the app, grant location permissions (always allow).
6. Back in HA, link her phone's `device_tracker` entity to her person.

Now automations can use conditions like:
- `person.willem == home` — Willem is home
- `person.rianne == home` — Rianne is home
- Both home, neither home, one home and not the other — all expressible as presence-based automation conditions.

Beau and Elvis do not have phones. But their behaviour is trackable via motion sensors in the rooms they inhabit — useful for "are the dogs still on the sofa" automations, which is to say, all automations.

---

## 🎛️ The Control Panel Is Live

Your mobile command post is now operational:

| Capability | Status |
|---|---|
| Remote dashboard access via Tailscale | ✅ Any network, anywhere |
| Auto-switch between local and external URL | ✅ Seamless |
| GPS presence detection | ✅ Home/away state tracked |
| Push notifications | ✅ House alerts you when it matters |
| Actionable notifications | ✅ Respond without opening the app |
| Rianne's presence tracked | ✅ Household-level presence detection |

In **Episode 7**, we put it all together: building automations that use everything we have configured — presence, time, sensors, notifications — to make the house truly think for itself.

> *"We can see everything they're doing. And they don't know it."*
> — Meg Altman, Panic Room.
> *"We can see everything the house is doing. And act on it, from anywhere."*
> — You, Episode 7.

---

*🔐 Panic Room is a series about building a secure, local-first smart home using Home Assistant — installed on a Mac Mini M4 Pro via Parallels, connected via Tailscale, and controlled from an iPad Mini anywhere in the world.*
