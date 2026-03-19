---
title: "Air Traffic Control Scaleway Ep.3"
part: 3
published: false
description: "Episode 3 of the Air Traffic Control series: choose the right Elastic Metal range for your workload — Aluminium through Titanium, matched to real-world use cases. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, elastic-metal, bare-metal]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-03.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# The Right Aircraft for the Right Mission: Elastic Metal on Scaleway

*“Every International Rescue mission begins with the same question: which Thunderbird do we send? You do not dispatch Thunderbird 4 to a mountain rescue, and you do not launch Thunderbird 2 when speed is the only variable that matters. The aircraft must match the emergency.”*
*— Jeff Tracy, Thunderbird Island Operations Centre*

-----

Welcome back to the **Scaleway Air Traffic Control Centre**.

In the previous episodes, we built the clearance architecture and launched our first virtual compute resource. Today we step into the hangar reserved for the heaviest iron in the fleet: **Elastic Metal**.

Elastic Metal is bare-metal compute — dedicated physical servers with no hypervisor layer between your workload and the hardware. No shared tenancy. No noisy neighbours. The full machine is yours.

But bare metal is not a single aircraft type. Scaleway offers five distinct Elastic Metal ranges — **Aluminium, Beryllium, Iridium, Lithium, and Titanium** — each engineered for a different class of mission. Choosing the wrong range is like sending Thunderbird 1 to lift a collapsed mine: technically present, fundamentally unsuited.

By the end of this episode, you will be able to read a workload requirement and identify the correct Elastic Metal range without hesitation.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

- Navigate the **Elastic Metal** section of the Scaleway Console
- Compare the specifications of the five Elastic Metal ranges across CPU, memory, storage, and bandwidth
- Understand the **billing model** options and their cost implications
- Map seven real-world use cases to the most appropriate server range

### Pre-Launch Checklist

- ✅ You have a Scaleway account and can access the Organisation you own

-----

## 📊 SIPOC — How Elastic Metal Selection Flows Through the System

Before we open the Console, let us map the decision process. Selecting a bare-metal range is not guesswork — it is a structured matching exercise between workload requirements and hardware capabilities.

|Stage|SIPOC Element|Elastic Metal Equivalent                                                                            |Example                                                             |
|-----|-------------|----------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway Elastic Metal catalogue + your Organisation account                                        |Five hardware ranges across multiple Availability Zones             |
|**I**|**Input**    |Use case requirements: CPU intensity, memory footprint, storage type, bandwidth needs, tenancy model|“Video processing — high CPU, large scratch storage, dedicated node”|
|**P**|**Process**  |Compare ranges → Evaluate specs → Match to use case → Identify billing model                        |All the hands-on steps in this episode                              |
|**O**|**Output**   |A reasoned range selection per use case, ready to inform a provisioning decision                    |“Big Data → Iridium; Web hosting → Aluminium”                       |
|**C**|**Consumer** |Platform engineers, architects, and cost owners who must justify infrastructure choices             |Your team, your project stakeholders, your budget review            |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway       ──▶   Use case        ──▶  Compare ranges   ──▶  Range         ──▶   Platform
Elastic Metal        requirements         Evaluate specs        selection             engineers
catalogue            CPU / memory         Match to use          per use case          Architects
                     Storage type         case                                        Cost owners
Organisation         Bandwidth            Identify billing
Owner account        Tenancy needs        model
```

> **Tower to crew:** This episode contains no provisioning steps — no server will be created and no cost will be incurred. This is pure mission planning: studying the aircraft before committing to a launch. International Rescue always knows which vehicle it is deploying before the hangar doors open.

-----

## 🛫 Section 1 — Enter the Hangar: Navigate to Elastic Metal

1. In the **Bare Metal** menu, select **Elastic Metal**.
1. Click **+ Create Elastic Metal server**.

> **Note:** Alternatively, open the **Create** menu and select **Elastic Metal**.

1. In the **① Availability Zone** section, choose `Paris 2`.

> **Note:** You can change the Availability Zone at any point to compare which server types are available in each location. Availability varies by region — not every range is stocked in every zone.

1. Leave the **② Billing Method** section at its default settings.

> **Note:** Switching between billing options reveals the estimated cost of your future server based on usage pattern — short-term (hourly) versus long-term (monthly commitment). The **(⑩ Order Summary)** section updates in real time with a detailed cost breakdown as you make selections.

-----

## 🏗️ Section 2 — Study the Fleet: Compare the Five Ranges

In the **③ Server** section, you will find five tabs — one per range. Work through each in turn, noting the specifications. Pay particular attention to the following dimensions for each range:

- **CPU(s):** core count, clock speed, generation
- **Memory:** total RAM, ECC support
- **Disk(s):** type (NVMe SSD, SATA SSD, HDD), capacity, configuration
- **Bandwidth:** network throughput

> **Note:** Some servers may appear greyed out. This indicates they are either temporarily out of stock or require additional quota approval. Include these in your comparison — the specifications remain valid for planning purposes even when a unit is unavailable.

> **Tip:** If the reduced contrast of greyed-out options does not meet your accessibility needs, work through this section with a partner.

The five ranges form a clear capability ladder:

|Range        |Character                    |Optimised For                                       |
|-------------|-----------------------------|----------------------------------------------------|
|**Aluminium**|Entry-level, cost-efficient  |General-purpose, web workloads, lightweight services|
|**Beryllium**|Balanced compute and memory  |Mid-tier applications, moderate data workloads      |
|**Iridium**  |High core count, large memory|Data-intensive and virtualisation workloads         |
|**Lithium**  |Storage-dense configurations |File servers, archiving, object-adjacent workloads  |
|**Titanium** |Maximum performance          |GPU-adjacent, video processing, enterprise ERP      |


> **Tower to crew:** The names are not arbitrary. Aluminium is light and abundant — affordable, everywhere. Titanium is the aerospace alloy — maximum strength, maximum cost, reserved for missions that demand it. Beryllium, Iridium, and Lithium sit between them, each with a distinct density of capability.

-----

## 🧑‍✈️ Section 3 — Mission Matching: Assign Ranges to Use Cases

With the fleet specifications studied, we now apply them. For each use case below, identify the Elastic Metal range — or combination of ranges — best suited to the task. Consider the dominant workload characteristics: is the bottleneck CPU, memory, storage throughput, network bandwidth, or isolation?

### Use Cases

**Backup & Archiving**
Large volumes of infrequently accessed data. Sequential write performance matters more than random IOPS. Cost per GB is a primary constraint. Retention periods are long.

**Virtualisation**
Multiple virtual machines running simultaneously on a single physical host. High core counts and large memory pools are the primary requirements. The hypervisor must be able to carve the machine into many independent guest environments.

**Big Data**
Distributed processing frameworks — MapReduce, Spark, Hadoop-adjacent — that ingest, transform, and aggregate large datasets. High memory and fast local storage are both required. Network throughput between nodes is significant.

**Web Hosting**
HTTP/S request handling, application server processes, database backends for moderate traffic volumes. Balanced CPU and memory. Predictable, steady-state load rather than burst. Cost efficiency is important at scale.

**File Servers**
High-capacity shared storage accessible over the network. Storage density is the primary metric. Sequential read/write performance for large files. Concurrent client connections.

**ERP Platform**
Enterprise resource planning systems — SAP, Oracle, or equivalent — that combine transactional databases, application logic, and reporting in a single environment. High memory, strong single-thread CPU performance, and low-latency storage are all required simultaneously.

**Video Processing**
Transcoding, rendering, and media pipeline workloads. CPU-intensive with large intermediate file buffers. High local storage throughput. Often bursty — long idle periods punctuated by intensive processing windows.

-----

## 🗺️ Elastic Metal Architecture — The Fleet Assignment Map

Once your analysis is complete, your range-to-use-case mapping should approximate the following:

```
┌────────────────────────────────────────────────────────────────┐
│                  ELASTIC METAL FLEET ASSIGNMENT                │
│                                                                │
│  RANGE          PRIMARY STRENGTHS        USE CASES             │
│  ──────         ─────────────────        ──────────────        │
│                                                                │
│  Aluminium  ──▶  Cost / General      ──▶  Web hosting          │
│                                                                │
│  Beryllium  ──▶  Balanced            ──▶  Web hosting (mid)    │
│                                      ──▶  File servers         │
│                                                                │
│  Iridium    ──▶  Core count /        ──▶  Virtualisation       │
│                  Large memory        ──▶  Big Data             │
│                                                                │
│  Lithium    ──▶  Storage density     ──▶  Backup & archiving   │
│                                      ──▶  File servers         │
│                                                                │
│  Titanium   ──▶  Maximum perf /      ──▶  ERP platform         │
│                  High throughput     ──▶  Video processing     │
└────────────────────────────────────────────────────────────────┘
```

> **Tower confirms:** There is no single correct answer for every organisation — hardware selection is always contextual. What the map above gives you is a defensible starting point, grounded in the specifications you have just studied. From here, benchmarking and cost modelling refine the choice further.

-----

## 📋 Episode Debrief

*“You cannot launch the right Thunderbird if you do not know what each one is capable of. Study the fleet. Know the mission. The correct choice becomes obvious.”*
*— Brains, Thunderbird Island Research Division*

In this episode, you have:

- ✅ Navigated the Elastic Metal section of the Scaleway Console
- ✅ Compared the five ranges — Aluminium, Beryllium, Iridium, Lithium, and Titanium — across CPU, memory, storage, and bandwidth
- ✅ Reviewed the billing model options and their cost implications
- ✅ Mapped seven real-world use cases to their most appropriate Elastic Metal range
- ✅ Understood why bare-metal selection is a structured matching exercise, not a default choice
- ✅ Mapped the full selection process through the SIPOC model

No server was provisioned. No cost was incurred. The mission plan is ready. In the next episode, we move to managed databases — provisioning a persistent data layer inside the zones and clearances we have already established.

-----

## 📡 Further Transmissions

- [Scaleway Elastic Metal documentation](https://www.scaleway.com/en/docs/bare-metal/elastic-metal/)
- [Elastic Metal server range comparison](https://www.scaleway.com/en/elastic-metal/)
- [Scaleway pricing calculator](https://www.scaleway.com/en/pricing/)
- [Scaleway CLI — Elastic Metal commands](https://github.com/scaleway/scaleway-cli/blob/master/docs/commands/baremetal.md)

-----

*Estimated reading time: 10 minutes. Estimated hands-on time: 20–30 minutes.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
