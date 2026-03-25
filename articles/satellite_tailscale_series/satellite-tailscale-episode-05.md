---
title: "Satellite Tailscale — Ep.5"
part: 5
published: false
description: "Mission Control is where your satellite network gets names, rules, and governance. MagicDNS gives your devices human-readable names. ACLs decide who can talk to whom. Let's run the control room."
tags: [tailscale, dns, acl, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/satellite_tailscale_series/satellite-tailscale-episode-05.png"
series: "Satellite Tailscale Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🛰️ Episode 5: Mission Control (MagicDNS & ACLs)

> *"I know now why you cry. But it is something I can never do."*
> — T-800, Terminator 2.
> *"I know now why you use IP addresses. But it is something you should never have to do."*
> — MagicDNS, gently.

---

## 🎛️ The Control Room

Up to now, your tailnet has been a beautifully functional but somewhat unstructured collection of satellites. They are connected. They can reach each other. But there are no nameplates on the doors, and no rules about who is allowed in which room.

This episode fixes both of those things.

We are visiting **Mission Control** — the Tailscale admin console at [login.tailscale.com](https://login.tailscale.com) — to configure:

1. **MagicDNS** — Human-readable hostnames for all your devices
2. **ACLs (Access Control Lists)** — Rules governing which devices can talk to which other devices

Together, these two features transform your tailnet from a cosy web of connected devices into a properly governed private network. The kind that makes security engineers nod approvingly.

---

## 📋 SIPOC — Mission Control Configuration

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Tailscale admin console | Your tailnet (from Episodes 2–4) | Enable MagicDNS → Set nameservers → Write ACL policy | Human-readable hostnames for all devices | You, never typing a 100.x.x.x IP again |
| Tailscale coordination server | Your device hostnames | ACL HuJSON policy defining access rules | Enforced network access policy | Every device in your tailnet |
| Your devices' system hostnames | Your identity/email | Tag devices by role | Tag-based firewall rules | Future devices (auto-enrolled via policy) |
| Your preferences | Security requirements | Test access with `tailscale ping` | Verified, policy-compliant connectivity | Your inner security engineer |

---

## 🔤 Part 1: MagicDNS

### What Is MagicDNS?

MagicDNS is Tailscale's built-in DNS system. When enabled, it assigns each device in your tailnet a **stable, human-readable hostname** that resolves to its Tailscale IP — automatically, without any DNS server configuration on your part.

Instead of:
```
ssh yourusername@100.87.123.45
```

You can write:
```
ssh yourusername@mac-mini-m4
```

Or with the full MagicDNS domain:
```
ssh yourusername@mac-mini-m4.tail1234.ts.net
```

These hostnames are valid from any device in your tailnet, regardless of which physical network that device is connected to.

This is what Mission Control feels like. Every satellite has a callsign. No more squinting at IP addresses at 23:00 from a hotel in Edinburgh.

### Enabling MagicDNS

1. Open [login.tailscale.com](https://login.tailscale.com)
2. Navigate to **DNS** in the left sidebar
3. Under **Nameservers**, click **Enable MagicDNS**
4. That's it

Tailscale will now resolve `device-name` to the correct `100.x.x.x` address on all your tailnet devices. The name it uses comes from the device's hostname (which you set correctly in Episode 4).

### Verifying MagicDNS

From any tailnet device:

```bash
# Ping by hostname (no IP needed)
tailscale ping mac-mini-m4

# Or test DNS resolution directly
nslookup mac-mini-m4
```

You should get the device's `100.x.x.x` Tailscale IP back. If you do: MagicDNS is working. Arnold would say:

> *"It's not a problem."*
> — Arnold Schwarzenegger, Kindergarten Cop. (The line is actually different, but this one is better.)

### Adding Custom DNS Resolvers (Optional)

You can also configure MagicDNS to use your preferred DNS resolvers for general internet traffic (e.g., Cloudflare's 1.1.1.1, or a Pi-hole on your home network). This is done in the same **DNS** tab in the admin console.

If you have a Pi-hole or AdGuard Home running as a subnet router on your tailnet, you can point all your tailnet devices' DNS queries at it — effectively getting network-wide ad blocking on your iPad Mini, even in the coffeeshop.

The Terminator does not see ads. Now neither do you.

---

## 🔒 Part 2: ACLs (Access Control Lists)

### What Are ACLs?

ACLs are the rules that govern which devices in your tailnet can communicate with which other devices — and on which ports. By default, Tailscale gives every device in your tailnet full access to every other device. This is fine when you are the only user, but it is good hygiene to make your policy explicit.

Tailscale ACLs are written in **HuJSON** — Human JSON, a superset of JSON that allows comments. The policy lives in the **Access Controls** tab of your admin console.

### A Practical ACL Policy for Your Personal Tailnet

Here is a policy that covers the scenarios in this series:

```json
{
  // Define tags for device roles
  "tagOwners": {
    "tag:home-base":  ["youremail@example.com"],
    "tag:mobile":     ["youremail@example.com"],
    "tag:server":     ["youremail@example.com"]
  },

  // Define groups
  "groups": {
    "group:owner": ["youremail@example.com"]
  },

  // Access control rules
  "acls": [
    // Owner can access everything
    {
      "action": "accept",
      "src":    ["group:owner"],
      "dst":    ["*:*"]
    },
    // Home base can be reached by mobile devices on SSH, VNC, RustDesk ports
    {
      "action": "accept",
      "src":    ["tag:mobile"],
      "dst":    ["tag:home-base:22,5900,21115,21116,21117,21118,21119"]
    }
  ],

  // SSH policy — managed SSH access
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

Let us decode this:

- **tagOwners** — defines who can tag devices with each role tag. Only you can apply `tag:home-base`, `tag:mobile`, and `tag:server`.
- **groups** — collects your email into `group:owner` for convenient rule authoring.
- **acls** — the actual rules:
  - As `group:owner`, you can reach anything on any port. You are the administrator of this satellite network.
  - Devices tagged `tag:mobile` (your iPad Mini) can reach devices tagged `tag:home-base` (your Mac Mini) on specific ports: SSH (22), VNC (5900), and RustDesk ports (21115–21119).
- **ssh** — Tailscale's managed SSH policy. The `group:owner` can SSH into `tag:home-base` devices as any non-root user.

### Applying Tags to Your Devices

In the admin console:

1. Navigate to **Machines**.
2. Click the `...` menu next to your Mac Mini.
3. Select **Edit ACL tags**.
4. Add `tag:home-base`.
5. Repeat for your iPad Mini: add `tag:mobile`.

The ACL policy is now active and enforced across your tailnet.

> 🛰️ **Note:** The RustDesk ports (21115–21119) are UDP and TCP. We will configure RustDesk properly in Episode 7 — but including those ports in the ACL now means zero friction when we get there.

---

## 🧪 Testing Your ACL Policy

From your iPad Mini (tagged `tag:mobile`), verify you can reach the Mac Mini (tagged `tag:home-base`):

```bash
tailscale ping mac-mini-m4
```

Then verify the policy is working as intended by checking the admin console → **Logs** → **Network Flow Logs**. You can see which connections are being accepted or rejected by your ACL rules.

---

## 🤖 Mission Control: Operational

Your tailnet now has:

| Feature | Status |
|---|---|
| MagicDNS | ✅ Enabled — devices reachable by name |
| ACLs | ✅ Configured — access is explicit and minimal |
| Device tags | ✅ Applied — `home-base` and `mobile` |
| SSH policy | ✅ Defined — managed SSH for group:owner |

This is what a well-governed satellite network looks like. Not paranoid. Not permissive. Just intentional.

In **Episode 6**, we beam commands across hemispheres using **Tailscale SSH** — connecting from your iPad Mini to your Mac Mini with a single command, no keys to manage, no passwords to remember.

> *"Your clothes. Give them to me. Now."*
> — T-800, Terminator 2.
> *"Your SSH key. Give it to me. Never — Tailscale SSH handles it."*
> — Tailscale, Episode 6.

---

*📡 Satellite Tailscale is a series about building your personal mesh network using Tailscale — from a coffeeshop iPad Mini to a home Mac Mini M4 Pro, and everything in between.*
