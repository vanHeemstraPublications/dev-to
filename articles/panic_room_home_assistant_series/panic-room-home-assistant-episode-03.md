---
title: "Panic Room — Ep.3"
part: 3
published: false
description: "The steel door doesn't install itself. This episode is the hands-on build: downloading the HAOS image, converting it for Parallels, creating the VM, and booting Home Assistant for the very first time."
tags: [homeassistant, parallels, macos, installation]
series: "Panic Room Home Assistant Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/panic_room_home_assistant_series/panic-room-home-assistant-episode-03.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 🔐 Building the Panic Room (Installing HAOS in Parallels)

> *"It took them three months to build this room."*
> — Burnham, Panic Room.
> *"It took us one Sunday afternoon to build ours."*
> — This episode. (Optimistically.)

---

## 🔨 Time to Build

The blueprint is approved. The materials are sourced. The Mac Mini M4 Pro is plugged in and ready. Parallels Desktop is installed and licensed.

Today we build.

This episode is the most technically dense in the series. It is also the most satisfying — because at the end of it, you will open a browser, navigate to `http://homeassistant.local:8123`, and see the Home Assistant onboarding screen for the first time. The panic room will be standing.

Take a breath. Make a coffee. Let us begin.

---

## 📋 SIPOC — Building the HAOS VM in Parallels

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Home Assistant project (GitHub releases) | Mac Mini M4 Pro running macOS Sequoia | Download HAOS aarch64 `.vmdk` image | HAOS VM running in Parallels | Every subsequent episode in this series |
| Parallels Desktop (v19+) | `prl_convert` CLI tool (ships with Parallels) | Convert `.vmdk` → `.hdd` using `prl_convert` | Parallels-compatible HAOS disk image | Your first boot of Home Assistant |
| GitHub (haos releases) | 64GB+ free disk space | Create Parallels VM → Configure networking → Boot | HAOS accessible at `homeassistant.local:8123` | You, seeing the onboarding screen |
| Your home network (with DHCP) | 30–60 minutes of your time | First boot → wait for HAOS to initialise | A running, waiting-to-be-configured smart home platform | Episode 4: Onboarding |

---

## 🔍 A Note on the Conversion Step

The Home Assistant project officially supports VirtualBox on macOS and does not mention Parallels. However, the community has long since worked out a clean path: Parallels ships with a command-line tool called `prl_convert` that converts `.vmdk` (VMware/VirtualBox format) disk images into `.hdd` format (Parallels format). One conversion command, and Parallels can use the HAOS image directly.

This is not a hack. It is a standard disk image format conversion using a tool that Parallels itself provides. The resulting VM runs the full HAOS — the same as on any other supported hypervisor.

> 🔐 **Think of it as fitting a standard security door into a non-standard frame.** A bit of extra work at installation time; a perfectly solid door thereafter.

---

## 🛠️ Step 1 — Download the HAOS Image

Navigate to the HAOS GitHub releases page:

```
https://github.com/home-assistant/operating-system/releases/latest
```

Under **Assets**, find the Apple Silicon / aarch64 image. It will be named something like:

```
haos_generic-aarch64-16.3.vmdk.zip
```

Where `16.3` is the current version number at time of download. Download this file.

> ⚠️ **Make sure you download the `generic-aarch64` variant.** This is the ARM64 image that runs natively on Apple Silicon. Do *not* download the x86-64 OVA — it would require emulation and run orders of magnitude slower.

Once downloaded, unzip the file:

```bash
cd ~/Downloads
unzip haos_generic-aarch64-*.vmdk.zip
```

You should now have a file named something like `haos_generic-aarch64-16.3.vmdk`. Note the exact filename — you will use it in the next step.

---

## 🔄 Step 2 — Convert the VMDK to Parallels HDD Format

Open **Terminal** and navigate to the folder containing the downloaded VMDK:

```bash
cd ~/Downloads
```

Run the `prl_convert` command that ships with Parallels Desktop:

```bash
prl_convert haos_generic-aarch64-16.3.vmdk \
  --dst=haos.hdd \
  --allow-no-os \
  --stand-alone-disk
```

Replace `haos_generic-aarch64-16.3.vmdk` with the exact filename you downloaded. The flags mean:

- `--dst=haos.hdd` — the output file name (you can call it anything ending in `.hdd`)
- `--allow-no-os` — HAOS does not present itself as a conventional OS, so Parallels would normally reject it; this flag overrides that check
- `--stand-alone-disk` — creates the `.hdd` as a standalone disk image rather than bundled inside a VM package

The conversion takes 30–90 seconds depending on your disk speed. When it finishes, you will see a file called `haos.hdd` in your Downloads folder. This is your panic room's steel door, ready to be hung.

> 🔍 **Where is `prl_convert`?** It lives in the Parallels application bundle. If it is not on your PATH, find it at:
> ```bash
> /Applications/Parallels\ Desktop.app/Contents/MacOS/prl_convert
> ```
> Either run it from there directly, or add the MacOS directory to your PATH.

---

## 🖥️ Step 3 — Create the Parallels VM

1. Open **Parallels Desktop**.
2. Click the **+** button (New VM) or go to **File → New**.
3. Select **"Install Windows or another OS from a DVD or image file"** — then on the next screen, choose **"Continue without a source"** or locate the option to create a VM manually.
   - In newer Parallels versions: select **"Create a custom virtual machine"** or equivalent.
4. When asked to choose an operating system: select **Linux → Other Linux**.
5. When asked about the hard disk: choose **"Use an existing virtual disk"** (or equivalent) and select the `haos.hdd` file you created in Step 2.
6. Name the VM something meaningful: `Home Assistant OS`.
7. **Before finishing**, click **"Customize Settings"** (or equivalent) — do not start the VM yet.

---

## ⚙️ Step 4 — Configure the VM Settings

In the VM settings window:

### CPU & Memory
- **CPUs**: 2 (minimum), 4 if you have them to spare
- **Memory**: 4096 MB (4 GB) — generous but not extravagant on a 24GB system

### Network
This is the most important setting. Change the network adapter from the default (usually **Shared Network / NAT**) to **Bridged Ethernet**.

- Navigate to **Hardware → Network 1**.
- Change **Source** from `Shared Network` to **Bridged Network**.
- Set **Bridged to**: your active network adapter (typically `en0` for the built-in Ethernet or Wi-Fi).

**Why bridged?** With NAT networking, the HAOS VM gets an IP address from Parallels' internal virtual network — something like `10.211.55.x`. Other devices on your home network cannot reach this address. With bridged networking, the HAOS VM gets an IP address directly from your home router's DHCP server — a real address like `192.168.1.x` — and is reachable from every device on your network.

This matters for:
- Discovering HAOS at `homeassistant.local:8123` from any device
- Integrating with smart home devices on your local network
- Tailscale reaching the HAOS instance (Episode 5)

> 🔐 **Bridged networking is the panic room's connection to the house's camera system.** Without it, the surveillance feeds would be cut off from the control panel. Connect them properly.

### Boot Order
- Under **Boot Order**, ensure the hard disk is set as the primary boot device.

### EFI / UEFI
- Ensure **EFI boot** is enabled (not BIOS). HAOS requires UEFI.

---

## 🚀 Step 5 — First Boot

Close the settings window. Click **Start** (or the play button) on your Home Assistant OS VM.

A terminal window opens. You will see:

```
Loading Home Assistant OS...
```

Followed by a stream of Linux boot messages. Do not panic. (Panic later, if at all.) The first boot takes longer than subsequent ones — HAOS is initialising itself, resizing the filesystem to fill the allocated disk space, downloading the current version of Home Assistant Core, and configuring all its internal services.

This process typically takes **5–10 minutes** on the first boot. During this time, you will see output like:

```
[  OK  ] Started Home Assistant Supervisor.
[  OK  ] Started Home Assistant.
```

When HAOS has finished initialising, the console will show a status screen something like:

```
Home Assistant
Home Assistant Core: 2026.1.0
Home Assistant Supervisor: 2025.12.0

System information
  IPv4 address (eth0): 192.168.1.XX
  
Home Assistant URL: http://homeassistant.local:8123
```

Note the IPv4 address. Note the URL. The panic room is standing.

---

## 🌐 Step 6 — Open Home Assistant for the First Time

On your Mac Mini (or any device on your home network), open a browser and navigate to:

```
http://homeassistant.local:8123
```

If mDNS is working correctly on your network, this will resolve to your HAOS VM's IP address. If it does not resolve (some networks disable mDNS), use the IP address directly:

```
http://192.168.1.XX:8123
```

(Replace `XX` with the last octet shown in the HAOS console.)

You will see the Home Assistant **onboarding screen** — a clean, calm interface asking you to prepare for setup.

The panic room is built. The door is solid. The cameras are ready. All that remains is to turn on the lights, configure the system, and move in.

That is Episode 4's job.

---

## 🔁 Configuring Autostart (Run HAOS at Login)

Before we move on: configure Parallels to start the HAOS VM automatically when your Mac Mini boots.

In Parallels Desktop:
1. Right-click on the **Home Assistant OS** VM.
2. Select **Configure**.
3. Under **General → Start automatically**, enable **"Start VM on login"** or **"Start VM when Parallels Desktop starts"**.

Also ensure Parallels Desktop itself is set to **Open at Login** in macOS:
- System Settings → General → Login Items → add **Parallels Desktop**.

Now, if your Mac Mini reboots (after a power cut, a macOS update), it will reboot, Parallels will launch, and HAOS will start automatically. The panic room is always on.

---

## 🛸 What's Next

In **Episode 4**, we walk through the Home Assistant onboarding process — creating your user account, setting your home location, configuring the first areas, and adding your first integrations.

The building is built. Now we furnish it.

> *"We own this house now."*
> — Meg Altman, Panic Room.
> *"We own this smart home platform now."*
> — You, having completed Episode 3.

---

*🔐 Panic Room is a series about building a secure, local-first smart home using Home Assistant — installed on a Mac Mini M4 Pro via Parallels, connected via Tailscale, and controlled from an iPad Mini anywhere in the world.*
