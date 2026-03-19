---
title: "Air Traffic Control Scaleway Ep.2"
part: 2
published: false
description: "Episode 2 of the Air Traffic Control series: spin up your first Compute Instance on Scaleway — configure security groups, attach Block Storage, and power down via CLI. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, compute, instances]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-02.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Cleared for Takeoff: Compute Instances on Scaleway

*“Thunderbird 1 is go. Paris runway confirmed. But before Scott reaches maximum velocity, every system check must be complete — engines, fuel, clearance, and the ground crew who will guide him home.”*
*— Jeff Tracy, Thunderbird Island Operations Centre*

-----

Welcome back to the **Scaleway Air Traffic Control Centre**.

In Episode 1, we built the clearance architecture — the IAM framework that determines who is authorised to do what. Now it is time to put metal on the runway. In this episode, we launch our first **Compute Instance**: a live, running machine in the cloud that your cleared crew can access, configure, and command.

Think of a Compute Instance as Thunderbird 1 itself. It does not appear by magic — it requires a designated hangar (Availability Zone), a mission profile (Instance type and image), a pilot’s access code (SSH key), and a perimeter defence system (security group) that decides which signals reach it and which are dropped into silence.

By the end of this episode, the aircraft will have taken off, completed its mission, and been stood down — all under your precise control.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

- Create a standard **Instance** in the Scaleway Console
- Create a **custom security group** and attach it to your Instance
- Connect to your Instance via **SSH**
- Configure the security group to **block and selectively permit** network connections
- Attach an additional **Block Storage volume** to your Instance
- **Format and mount** the Block Storage volume from inside the Instance
- **Power off** your Instance using the Scaleway CLI
- **Delete** your Instance and its associated resources

### Pre-Launch Checklist

- ✅ You have a Scaleway account and can access the Organisation you own
- ✅ You have configured an SSH key in the `default` project (from Episode 1)
- ✅ You have [cURL](https://everything.curl.dev/get) installed on your machine

> **Note:** For this activity, you will work in your Organisation’s `personal` project.

-----

## 📊 SIPOC — How Compute Flows Through the System

Before engines ignite, let us map the pipeline. A Compute Instance is not a single object — it is the outcome of a coordinated sequence of configuration decisions. The SIPOC model shows us the full flight plan.

|Stage|SIPOC Element|Compute Equivalent                                                                          |Example                                                                                  |
|-----|-------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway Compute engine + your Organisation account                                         |The platform and the operator who configures it                                          |
|**I**|**Input**    |Instance type, image, SSH key, security group rules, Block Storage spec                     |`POP2-2C-8G`, CentOS, SSH key, `Accept TCP:22`                                           |
|**P**|**Process**  |Create Instance → Attach security group → Connect via SSH → Add storage → Power off → Delete|All the hands-on steps in this episode                                                   |
|**O**|**Output**   |A running, SSH-accessible Instance with scoped network controls and mounted Block Storage   |`my-first-scw-instance` in PAR-2, with `sdb` formatted and mounted at `/mnt/block-volume`|
|**C**|**Consumer** |Developers, CI/CD pipelines, and platform operators who need ephemeral or persistent compute|Your terminal session, your team, your automation tooling                                |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway       ──▶   Instance type   ──▶  Create Instance  ──▶  Running VM    ──▶   Developers
Compute              Image                Configure SG          SSH-accessible        CI/CD
engine               SSH key              Connect via SSH       Block Storage         pipelines
                     SG rules             Mount storage         mounted               Operators
Organisation         Block Storage        Power off             Cleaned up
Owner account        spec                 Delete
```

> **Tower to crew:** The SIPOC reminds us that compute without clearance is a runway without a control tower. The IAM policies from Episode 1 are already watching — your Instance lands inside the zone your policy permits.

-----

## 🛫 Section 1 — Aircraft Procurement: Create an Instance

Scott Tracy does not select just any vehicle for a mission. The Instance type, image, and zone are chosen with precision. Let us configure ours.

### 1.1 — Configure and Launch

1. In the **Compute** menu, select **CPU & GPU Instances**.
1. Click **+ Create CPU Instance**.

> **Note:** Alternatively, open the **Create** menu and select **CPU Instance**.

1. In the **① Availability Zone** section, choose `Paris 2`.
1. In the **② Instance** section, select the **General Purpose** tab and choose `POP2-2C-8G`.

> **Note:** Pause here and review the Instance specifications: **vCPUs**, **Memory**, **Storage**, and **Bandwidth**. This is your mission dossier — know what you are deploying before you deploy it.

1. In the **③ Image** section, select the most recent **CentOS** image.
1. In the **④ Name & Tags** section, enter a name — for example, `my-first-scw-instance`. Leave **Tags** empty.
1. Leave **⑤ Volumes** and **⑥ Public IPs** at their default settings.
1. In the **⑦ SSH Keys** section, verify that your SSH key from Episode 1 appears.
1. In the **⑧ Environmental footprint** section, note the estimated carbon impact of your Instance — International Rescue does not ignore its footprint.
1. In the **⑨ Estimated cost** section, use the drop-down to review the projected monthly cost.
1. Click **Create Instance**.

> **Note:** Wait for the Instance status to change from `Starting` to `Running` in the **Instance Information** section of the **Overview** tab before proceeding.

-----

## 🏗️ Section 2 — Perimeter Defence: Custom Security Groups

A Thunderbird vehicle on the apron without a security perimeter is a liability. By default, Scaleway places your Instance in an auto-generated **Default security group** for its Availability Zone. We will replace that with a precision-configured perimeter of our own.

### 2.1 — Create the Security Group

1. In the **Compute** menu, select **CPU & GPU Instances**, ensure the Availability Zone is set to **PAR 2**, then select the **Security groups** tab.

> **Note:** The Default security group you see was auto-generated when you created your first Instance in this zone. All Instances in the zone are assigned to it unless you specify otherwise.

1. Click **+ Create security group**.
1. In **① Name & Tags**, enter a name — for example, `hands-on-compute`.
1. In **② Availability Zone**, select `Paris 2`.
1. Leave **③ Instance link** and **④ Rules** at their defaults.
1. Click **Create security group**.

### 2.2 — Attach the Security Group to Your Instance

1. Select the security group you just created, then open the **Instances** tab.
1. From the drop-down, select your Instance. Click **Add Instance**.
1. Return to **Compute** → **CPU & GPU Instances** → **Instances** tab. Select your Instance and scroll to the **Security group** section.
1. Confirm that the security group now shows `hands-on-compute` rather than the default.

> **Tip:** The **Edit** button in the **Security group** section lets you switch an Instance to a different security group at any time — no restart required.

-----

## 🧑‍✈️ Section 3 — Pilot Ingress: Connect via SSH

The hangar doors are open. Time to step aboard.

1. In your terminal, run the following command — substituting your private key path and your Instance’s public IP:

```bash
ssh -i <your_private_key_with_path> root@<your_instance_public_ip>
```

> **Tip:** A full list of your Instances and their public IP addresses is available on the **CPU & GPU Instances** page of the Console.

1. If prompted with `Are you sure you want to continue connecting`, type `yes` and press Enter.
1. Enter your passphrase if required.
1. Run the following command to confirm you are connected and visible on the network:

```bash
curl https://ifconfig.co -4
```

You should receive a response showing your Instance’s public IP address. Connection confirmed. You are aboard.

-----

## 🔒 Section 4 — Lockdown Protocol: Configure Security Group Rules

International Rescue does not leave its hangar doors open overnight. We now configure the security group to drop all traffic by default — and admit only what we explicitly authorise.

### 4.1 — Set Default Policies to Drop

1. In the **Compute** menu, select **CPU & GPU Instances**, then open the **Security groups** tab.
1. Select `hands-on-compute`, then open the **Rules** tab.
1. In the **Default policy** section, click the **Edit** icon.
1. Set **Inbound default policy** to `Drop`.
1. Set **Outbound default policy** to `Drop`.
1. Click the **Validate** icon.

### 4.2 — Add a Selective Inbound Rule

1. In the **Rules** section, click the **Edit** icon.
1. Click **+ Add inbound rule** and configure as follows:

|Field       |Value                             |
|------------|----------------------------------|
|**Rule**    |`Accept`                          |
|**Protocol**|`TCP`                             |
|**Port**    |Clear `All ports`, then enter `22`|
|**IP range**|`All IPv4`                        |

1. Click the **Validate** icon.

### 4.3 — Verify the Lockdown

Back in your terminal (still connected via SSH), run:

```bash
curl https://ifconfig.co -4
```

This time, you should receive no response. The outbound Drop rule is working exactly as intended — your Instance can receive authorised SSH connections, but all other traffic, outbound included, is silenced.

> **Tower confirms:** Inbound SSH is open. All other channels are closed. The perimeter is live. This is precisely the discipline that separates a production-grade deployment from a poorly configured test environment left exposed on the internet.

-----

## 💾 Section 5 — Additional Cargo: Attach Block Storage

Thunderbird 2 carries its payload in a dedicated pod — separate from the vehicle itself, swappable by mission. We replicate this with an additional Block Storage volume attached to our Instance.

> **Note:** Your Instance already has a 10 GB system Block Storage volume. What follows adds a second, independent volume.

### 5.1 — Create and Attach the Volume

1. In the **Compute** menu, select **CPU & GPU Instances**.
1. Click your Instance, then open the **Storage** tab.
1. Click **+ Create volume**.
1. Complete the **Name** field — for example, `handson-my-vol`.
1. Set **Size** to `20 GB`.
1. Set **Block storage IOPS** to `5K`.
1. Review the estimated cost shown next to **Block Storage**.
1. Click **Add volume**.

### 5.2 — Format and Mount the Volume

Reconnect to your Instance via SSH, then proceed.

1. Run `lsblk` to confirm the new volume is visible to the OS:

```bash
lsblk
```

Expected output — look for `sdb`, your new unformatted volume:

```
NAME    MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda       8:0    0   9.3G  0 disk
├─sda3    8:1    0   9.2G  0 part /
├─sda2   8:14   0     4M  0 part /boot
└─sda1   8:15   0   106M  0 part /boot/efi
sdb       8:16   0  18.6G  0 disk
```

> **Note:** Scaleway uses GiB internally. Your 20 GB volume appears as 18.6 GiB — this is expected, not an error.

1. Create an `ext4` file system on the volume:

```bash
mkfs.ext4 /dev/sdb
```

> **Note:** `ext4` is the standard choice for general-purpose Linux workloads. Substitute an alternative file system if your mission profile requires it.

1. Verify the file system was created correctly:

```bash
lsblk -f
```

You should see `ext4` listed under `FSTYPE` for `sdb`, alongside a newly assigned `UUID`. The payload pod has been prepared.

1. Create a mount point and mount the volume:

```bash
mkdir /mnt/block-volume
mount -o defaults /dev/sdb /mnt/block-volume
```

> **Tip:** The `-o defaults` flag applies a standard set of mount options: `rw`, `suid`, `dev`, `exec`, `auto`, `nouser`, and `async`. Run `man mount` to review all available options.

1. Confirm the volume is mounted:

```bash
lsblk
```

`/mnt/block-volume` should now appear in the `MOUNTPOINTS` column for `sdb`. The cargo pod is loaded and secured.

-----

## 🗺️ Compute Architecture — The Flight Status Map

Your deployment should now match the following layout:

```
┌────────────────────────────────────────────────────────────────┐
│               ORGANISATION — personal project                  │
│                                                                │
│  AVAILABILITY ZONE: PAR-2                                      │
│  ──────────────────────────────────────────────────────────   │
│                                                                │
│  INSTANCE                                                      │
│  my-first-scw-instance (POP2-2C-8G, CentOS)                   │
│  Status: Running                                               │
│                                                                │
│  SECURITY GROUP                                                │
│  hands-on-compute                                              │
│  Inbound:  TCP:22 Accept | All other: Drop                     │
│  Outbound: Drop                                                │
│                                                                │
│  STORAGE                                                       │
│  sda  — 10 GB  — system volume   (/)                          │
│  sdb  — 20 GB  — ext4            (/mnt/block-volume)          │
└────────────────────────────────────────────────────────────────┘
```

-----

## 🔑 Section 6 — Mission Stand-Down: Power Off via CLI

The Scaleway CLI is your direct radio link to the platform — no Console required. We use it now to power off the Instance cleanly: OS halted, data transferred to volume store, physical node returned to the pool.

> **Note:** Powering off is not the same as deleting. The Instance’s flexible IP remains in your account. The volume data is preserved. Think of it as returning Thunderbird 1 to its launch silo — ready to fly again, but not consuming active compute resources.

> **Note:** If the Instance has significant data on its volumes, the power-off sequence may take time. It is good practice to halt the OS first: connect as `root` and run `halt` before issuing the CLI command.

### 6.1 — Install and Initialise the CLI

1. Install the [Scaleway CLI](https://github.com/scaleway/scaleway-cli) following the README instructions for your operating system.
1. Run `scw init` to initialise your configuration:

```bash
scw init
```

> **Note:** You will need your **Secret Key**, **Access Key**, and **Project ID**. The Project ID is available in the **Settings** tab of the Project Dashboard.

> **Tip:** After `scw init`, the CLI defaults to zone `fr-par-1`. Since your Instance is in `fr-par-2`, you will need to include `zone=fr-par-2` in each command. The steps below include this explicitly.

### 6.2 — List and Power Off

1. List all running Instances across all zones:

```bash
scw instance server list zone=all
```

> **Note:** Copy the Instance ID displayed — you will need it in the next command.

1. Power off your Instance:

```bash
scw instance server stop <instance-id> zone=fr-par-2
```

1. Confirm the status change:

```bash
scw instance server list zone=all
```

The status column should now read `archived`. Return to the Console and confirm the Instance shows `Powered off` on its Overview page.

> **Tower confirms:** Two independent confirmation methods — CLI output and Console status — both read `powered off`. The aircraft is in the silo.

-----

## 🗑️ Section 7 — End of Mission: Delete the Instance

Powering off preserves resources. Deleting removes them permanently. Choose deletion when the mission is genuinely complete and the resources are no longer required.

> ⚠️ **Security Protocol — Restricted:** Deletion is irreversible. All Instance data is permanently destroyed. Confirm that no data on the system volume is needed before proceeding.

1. In the **Compute** menu, select **CPU & GPU Instances**.
1. Click your Instance, open the **Actions** drop-down menu, and choose **Delete**.
1. Select the checkbox next to **Delete associated IPs**.
1. Select the checkbox next to **Delete Block Storage volumes**.
1. Type `DELETE` to confirm.
1. Click **Delete Instance**.

The aircraft has been decommissioned. The runway is clear.

-----

## 📋 Episode Debrief

*“All systems nominal. Instance destroyed on schedule. The zone is clean, the clearances are intact, and the crew is standing by for the next mission. Thunderbirds are GO.”*
*— Jeff Tracy, Thunderbird Island Operations Centre*

In this episode, you have:

- ✅ Created a `POP2-2C-8G` Instance in `Paris 2` running CentOS
- ✅ Created a custom security group `hands-on-compute` and attached it to your Instance
- ✅ Connected to the Instance via SSH using an Ed25519 key
- ✅ Configured the security group with Drop defaults and a selective `Accept TCP:22` inbound rule
- ✅ Verified that the Drop outbound rule silences all outbound traffic
- ✅ Attached a 20 GB Block Storage volume (`handson-my-vol`) to the Instance
- ✅ Formatted the volume as `ext4` and mounted it at `/mnt/block-volume`
- ✅ Powered off the Instance using the Scaleway CLI with explicit zone targeting
- ✅ Deleted the Instance along with its associated IP and Block Storage volumes
- ✅ Mapped the full compute lifecycle through the SIPOC model

The runway is clear. In the next episode, we go serverless — deploying functions and containers into zones already protected by the clearance architecture we have built.

-----

## 📡 Further Transmissions

- [Scaleway Instances documentation](https://www.scaleway.com/en/docs/compute/instances/)
- [Scaleway security groups](https://www.scaleway.com/en/docs/compute/instances/how-to/use-security-groups/)
- [Scaleway Block Storage documentation](https://www.scaleway.com/en/docs/storage/block/)
- [Scaleway CLI — instance commands](https://github.com/scaleway/scaleway-cli/blob/master/docs/commands/instance.md)
- [Linux `mount` command reference](https://man7.org/linux/man-pages/man8/mount.8.html)

-----

*Estimated reading time: 13 minutes. Estimated hands-on time: 45–60 minutes.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
