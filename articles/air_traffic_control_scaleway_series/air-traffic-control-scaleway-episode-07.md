---
title: "Air Traffic Control Scaleway Ep.7"
part: 7
published: false
description: "Episode 7 of the Air Traffic Control series: build a private network on Scaleway — create a VPC, attach a Public Gateway, connect two Instances via a Private Network, and reach them through an SSH bastion. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, networking, vpc]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-07.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Secure Corridors: Private Networks on Scaleway

*“International Rescue does not broadcast on open frequencies. Every transmission between Thunderbird Island and a mission vehicle travels through a secured, private channel — known to the crew, invisible to everyone else. The network is the mission.”*
*— Lady Penelope Creighton-Ward, London Agent*

-----

Welcome back to the **Scaleway Air Traffic Control Centre**.

Everything we have built so far has operated over the public internet — Instances with public IPs, containers with public endpoints, databases with public network access. That is appropriate for a training environment. It is not appropriate for production.

In this episode, we build the private corridor: a **Virtual Private Cloud (VPC)** containing a **Private Network** that connects resources to each other without exposing them to the public internet. A **Public Gateway** sits at the perimeter — the single controlled entry and exit point, with an **SSH bastion** that lets authorised operators reach private Instances without granting them a public IP address.

This is network discipline. This is how International Rescue operates.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

- Create a **Private Network** inside a Scaleway VPC
- Create a **Public Gateway** and attach it to the Private Network
- Create two **Instances** using Cloud-init for automated configuration
- Attach both Instances to the Private Network
- Activate the **SSH bastion** on the Public Gateway
- Connect to an Instance via its **private IP address** through the bastion
- Delete all resources cleanly

### Pre-Launch Checklist

- ✅ You have a Scaleway account and can access the Organisation you own
- ✅ You have configured an SSH key for the `default` project
- ✅ You have [cURL](https://everything.curl.dev/get) installed on your machine
- ✅ You have cloned the [`scw-certifications`](https://github.com/scaleway/scw-certifications/) repository — the `07_network/assets/` folder contains the Cloud-init files for this episode

> **Note:** For this activity, you will work in your Organisation’s `default` project.

-----

## 📊 SIPOC — How Private Networking Flows Through the System

|Stage|SIPOC Element|Networking Equivalent                                                                                                                                     |Example                                                                      |
|-----|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway VPC engine + Public Gateway service + Compute                                                                                                    |The network layer and the instances it connects                              |
|**I**|**Input**    |VPC region, Private Network name, Gateway type, Instance specs, Cloud-init configs                                                                        |`Paris`, `hands-on-private-network`, `VPC-GW-S`, `server1.yml`, `server2.yml`|
|**P**|**Process**  |Create Instance → Connect via SSH → Create VPC + Private Network → Create Gateway → Attach Gateway → Attach Instances → Enable bastion → Connect privately|All the hands-on steps in this episode                                       |
|**O**|**Output**   |Two Instances reachable via private IP only, accessed through a single bastion entry point                                                                |`ssh root@<private-ip> -J bastion@<gateway-ip>:<port>`                       |
|**C**|**Consumer** |Operators, CI/CD pipelines, and internal services that must reach resources without public IP exposure                                                    |Your terminal, your internal automation, your secured application tier       |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway       ──▶   VPC region      ──▶  Create Instance  ──▶  Private       ──▶   Operators
VPC engine           Private Network       Create VPC            corridor              CI/CD
                     name                  Create Gateway        SSH bastion           pipelines
Public               Gateway type          Attach Gateway        entry point           Internal
Gateway              Instance specs        Attach Instances      No public IPs         services
service              Cloud-init            Enable bastion        on resources
                     configs               Connect privately
Compute
```

> **Tower to crew:** By the end of this episode, neither Instance will require a public IP to be reachable. The Public Gateway is the sole entry point. The SSH bastion is the sole operator channel. This is the minimum viable network perimeter for any workload that should not be directly addressable from the internet.

-----

## 🛫 Section 1 — First Aircraft on the Runway: Create and Connect to an Instance

Before we build the network, we need something to connect to it. We start with a single Instance, configured automatically via Cloud-init.

### 1.1 — Create the Instance

1. In the **Compute** section of the side menu, select **Instances**, then click **Create Instance**.
1. For the **Availability Zone**, select `Paris 2`.
1. In the **Select an Instance** section, open the **Workload-Optimized** tab and select `POP2-HM-2C-16G`.
1. For the image, select **Debian Bullseye**.
1. Verify that your SSH key appears in the **SSH keys** section.
1. Set the Instance name to `hands-on-network`.
1. Open **Advanced options** and enable the **Cloud-init** toggle.
1. Paste the contents of the `assets/server1.yml` file into the text box.
1. Click **Create Instance**.
1. Wait for the Instance status to change from `Starting` to `Running` in the **Instance Information** section of the **Overview** tab.

> **Note:** Cloud-init runs at first boot and applies the configuration in `server1.yml` automatically — packages, users, services, and any startup scripts defined in the file are applied without manual intervention. This is Infrastructure as Configuration: the machine knows what it is before a human touches it.

### 1.2 — Connect via SSH and Verify

1. In the **Instance Information** section of the **Overview** tab, copy the SSH command.
1. Run it in your terminal.
1. If prompted with `Are you sure you want to continue connecting`, type `yes` and press Enter.
1. Enter your passphrase if required.
1. Confirm connectivity and public IP:

```bash
curl https://ifconfig.co -4
```

You should receive a response showing the Instance’s public IP address. The aircraft is on the runway and responding.

-----

## 🏗️ Section 2 — Establish the Corridor: Create a VPC and Private Network

With the first Instance running, we build the private corridor it will move into.

1. In the **Network** section of the side menu, select **VPC**. The VPC page displays.
1. Click **Create VPC**. The VPC creation wizard displays.
1. For the region, select `Paris`.
1. For the VPC name, enter `hands-on-vpc`.
1. For the Private Network name, enter `hands-on-private-network`.
1. Click **Create VPC**.

> **Tower to crew:** A VPC is a logically isolated section of Scaleway’s network — your own address space, your own routing rules. A Private Network lives inside a VPC and provides the actual Layer 2 segment that resources connect to. Think of the VPC as the controlled airspace; the Private Network is the private runway within it.

-----

## 🔒 Section 3 — The Perimeter Gate: Create a Public Gateway

The Public Gateway is the single, controlled point of contact between the Private Network and the public internet. Nothing enters or leaves the private corridor without passing through it.

1. In the **Network** section of the side menu, select **Public Gateways**.
1. Click **Create Public Gateway**.
1. For the **Availability Zone**, select `Paris 2`.
1. Select the gateway type `VPC-GW-S` with 100 Mbps of bandwidth.
1. In the **Select an IP** section, leave `Allocate a new IP` selected.
1. Set the gateway name to `hands-on-public-gateway`.
1. Click **Create Public Gateway**.

-----

## 🧑‍✈️ Section 4 — Connect Gate to Corridor: Attach the Gateway to the Private Network

1. In the **Public Gateways** tab, select the gateway you just created.
1. Open the **Private Networks** tab and click **Attach to a Private Network**.
1. Select `hands-on-private-network` from the list.
1. Clear the **Advertise default route** toggle.
1. Click **Attach to Private Network**.

> **Note:** Clearing **Advertise default route** keeps the Instance’s public IP accessible via its existing route. Enabling it would force all outbound traffic through the Gateway — useful for NAT-only architectures, but not required here. We are preserving dual access during the hands-on activity to make the bastion test easier to verify.

-----

## 💾 Section 5 — Move the Aircraft Inside: Attach Instances to the Private Network

### 5.1 — Attach the First Instance

1. In the **Network** section of the side menu, select **VPC**, then select the `hands-on-vpc` VPC.
1. Open the **Private Networks** tab and select `hands-on-private-network`.
1. Click **Attach resource**.
1. In the **Resource** drop-down, select the `hands-on-network` Instance.
1. Click **Attach resource**.

### 5.2 — Create and Attach a Second Instance

Create a second Instance with the following specifications:

|Field                |Value                                     |
|---------------------|------------------------------------------|
|**Availability Zone**|`Paris 2`                                 |
|**Type**             |Cost-Optimized → `PLAY2-PICO`             |
|**Image**            |Debian Bullseye                           |
|**Name**             |`hands-on-network-2`                      |
|**Cloud-init**       |Paste the contents of `assets/server2.yml`|
|**Private Network**  |`hands-on-private-network`                |


> **Note:** You can attach the Instance to the Private Network directly during creation by selecting it in the **Network** section of the Instance creation wizard — no need to navigate back to the VPC page afterwards.

-----

## 🗺️ Network Architecture — The Secure Corridor Map

Before activating the bastion, verify that the architecture matches the following layout:

```
┌────────────────────────────────────────────────────────────────┐
│              ORGANISATION — default project                    │
│                                                                │
│  VPC: hands-on-vpc (Paris)                                     │
│  ─────────────────────────────────────────────────────────    │
│                                                                │
│  PRIVATE NETWORK: hands-on-private-network                     │
│                                                                │
│  hands-on-network    (POP2-HM-2C-16G)  ──▶ private IP         │
│  hands-on-network-2  (PLAY2-PICO)      ──▶ private IP         │
│                                                                │
│  PUBLIC GATEWAY: hands-on-public-gateway (VPC-GW-S, PAR-2)    │
│  Public IP: <allocated>                                        │
│  Attached to: hands-on-private-network                         │
│  Advertise default route: OFF                                  │
│                                                                │
│  OPERATOR ACCESS                                               │
│  ssh root@<private-ip> -J bastion@<gateway-ip>:<port>         │
└────────────────────────────────────────────────────────────────┘
```

-----

## 🔑 Section 6 — Open the Secure Channel: SSH Bastion

The SSH bastion turns the Public Gateway into a jump host. An operator connects to the bastion first; the bastion then proxies the connection inward to the private Instance. The Instance never needs a public IP.

### 6.1 — Verify Private IP Addresses

1. In the **Private Networks** tab of the VPC, open the **Attached resources** tab.
1. Confirm that both Instances have been assigned private IP addresses within the Private Network.

### 6.2 — Activate the SSH Bastion

1. In the **Network** section of the side menu, select **Public Gateways**.
1. Select `hands-on-public-gateway`, then open the **Overview** tab.
1. Activate the **SSH bastion** option.

> **Note:** Once enabled, the bastion port is displayed in the Gateway Overview. Copy it — you will need it in the next step.

### 6.3 — Connect to an Instance via the Bastion

In your terminal, run the following command — substituting the private IP of either Instance, the public IP of the Gateway, and the bastion port:

```bash
ssh root@<Private IP of the Instance> \
  -J bastion@<Public IP of the Public Gateway>:<ssh bastion port>
```

> **Tower confirms:** The `-J` flag instructs your SSH client to use the bastion as a jump host — it establishes a connection to the bastion first, then proxies the session through to the private Instance. From the Instance’s perspective, the connection arrives from inside the Private Network. No public exposure. No inbound firewall rule on the Instance. The corridor is working exactly as designed.

-----

## 🗑️ Section 7 — Clear the Airspace: Delete All Resources

Delete resources in the following order to avoid dependency conflicts:

1. **Detach Instances** from `hands-on-private-network`
1. **Delete Instances** — `hands-on-network` and `hands-on-network-2`
1. **Detach the Public Gateway** from the Private Network
1. **Delete the Public Gateway** — `hands-on-public-gateway` (this also releases the allocated IP)
1. **Delete the Private Network** — `hands-on-private-network`
1. **Delete the VPC** — `hands-on-vpc`

> ⚠️ **Security Protocol — Restricted:** Deleting the Public Gateway releases its allocated IP. If you need to retain the IP for future use, detach it from the Gateway before deletion and keep it as an unattached flexible IP in your account.

-----

## 📋 Episode Debrief

*“Secure channel confirmed. Both Instances are reachable. No public exposure. The corridor holds. Thunderbirds are GO.”*
*— Lady Penelope Creighton-Ward, London Agent*

In this episode, you have:

- ✅ Created a `POP2-HM-2C-16G` Instance configured via Cloud-init from `server1.yml`
- ✅ Connected to the Instance via SSH and verified public IP connectivity
- ✅ Created a VPC (`hands-on-vpc`) and Private Network (`hands-on-private-network`) in the Paris region
- ✅ Created a `VPC-GW-S` Public Gateway (`hands-on-public-gateway`) in Paris 2
- ✅ Attached the Gateway to the Private Network with **Advertise default route** disabled
- ✅ Attached the first Instance to the Private Network
- ✅ Created a second Instance (`PLAY2-PICO`) configured via `server2.yml` and attached to the same Private Network
- ✅ Verified that both Instances received private IP addresses
- ✅ Activated the SSH bastion on the Public Gateway
- ✅ Connected to a private Instance via its private IP using the bastion as a jump host
- ✅ Deleted all resources in the correct dependency order
- ✅ Mapped the full private networking pipeline through the SIPOC model

The secure corridor is proven. In the next episode, we close out the series with a full architecture review — bringing together everything built across all seven episodes into a single coherent picture.

-----

## 📡 Further Transmissions

- [Scaleway VPC documentation](https://www.scaleway.com/en/docs/network/vpc/)
- [Scaleway Private Networks documentation](https://www.scaleway.com/en/docs/network/vpc/how-to/create-private-network/)
- [Scaleway Public Gateways documentation](https://www.scaleway.com/en/docs/network/public-gateways/)
- [Scaleway Public Gateway — SSH bastion](https://www.scaleway.com/en/docs/network/public-gateways/how-to/use-ssh-bastion/)
- [Cloud-init documentation](https://cloudinit.readthedocs.io/en/latest/)

-----

*Estimated reading time: 12 minutes. Estimated hands-on time: 45–60 minutes.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
