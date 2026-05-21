---
title: "Big Bad Wolf Meets Nirmata 🐺 Ep.1"
part: 1
published: false
description: "Episode 1: Once upon a time, three little piglets built their Kubernetes clusters — one in straw, one in sticks, and one in policy-as-code bricks. Then the Big Bad Wolf arrived, sniffing for misconfigurations. This is that story. Meet Nirmata, Kyverno, and the only house that doesn’t blow down."
tags: [kubernetes, security, nirmata, devops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/big-bad-wolf-nirmata-episode-01.png"
series: "Big Bad Wolf Meets Nirmata"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 1: Once Upon a Time in the Cloud

> *“I’ll huff, and I’ll puff, and I’ll BREACH your infrastructure!”*
> — The Big Bad Wolf, seconds before discovering Kyverno

-----

## Gather Round, Children of the Kubernetes Kingdom 📖

Once upon a time, in the magical land of Cloud-Native-Ville, there lived three little piglets. They were developers, and they were very busy, and they had been told — repeatedly, at conferences, in blog posts, and by their very concerned CISO — that they really ought to secure their Kubernetes clusters.

The first little piglet, whose name was **Penny the Promptless**, built her cluster out of *straw*. That is to say, she deployed workloads with no security policies whatsoever. Any container could run as root. Any image could come from any registry, including one called `totallylegit-alpine:latest-notmalware`. Privileged pods roamed freely like unsupervised children at a candy shop. It was fast to set up, which was exactly the wrong reason to feel pleased with herself.

The second little piglet, **Stanley the Slightly-Worried**, built his cluster out of *sticks*. He had RBAC. He had *some* network policies. He had a spreadsheet listing all the things he meant to enforce eventually. He ran the occasional security scan on Tuesday afternoons when nothing else was happening, which meant approximately never.

The third little piglet, **Brenda the Brick-Layer**, built her cluster out of *policy-as-code bricks*. Every brick was a Kyverno policy. Every brick was tested, versioned, peer-reviewed, and enforced in both her pipeline and her cluster. Her colleagues thought she was somewhat excessive. Her CISO thought she was a hero. She thought everyone else was living dangerously.

Then the Big Bad Wolf appeared on the horizon.

His name was **Wolfgang von Misconfiguration**, and he was *very* good at his job.

-----

## 🗂️ SIPOC — The Fairytale Begins

|**Suppliers**                           |**Inputs**                                                                |**Process**                                                                                 |**Outputs**                                                                  |**Customers**                                                                   |
|----------------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------------------------------------------------------------------|
|The Big Bad Wolf (attackers, misconfigs)|Unprotected Kubernetes clusters with no policies                          |Probe for privileged containers, unverified images, missing resource limits, open namespaces|Breached clusters, data exfiltration, resource hijacking, compliance failures|The three piglets — specifically the unhappy ones                               |
|Nirmata + Kyverno                       |Policy-as-Code rules (YAML/CEL), cluster connections                      |Validate every API call, mutate resources to meet standards, block anything the Wolf tries  |A cluster that doesn’t blow down, ever, regardless of huffing intensity      |Platform teams, security teams, compliance auditors, and the three piglets’ CISO|
|The Three Piglets                       |Kubernetes clusters: unprotected, partially protected, and fully protected|Build infrastructure with varying levels of policy governance                               |A very instructive before/after comparison                                   |You, the reader, who is hopefully more Brenda and less Penny                    |

-----

## Who Is the Big Bad Wolf? 🐺

Let us be precise about our villain. The Big Bad Wolf is not merely a mustache-twirling hacker in a hoodie. He comes in several flavours, all equally unpleasant:

**Flavour 1: The Misconfiguration Wolf 🏚️**
Privileged containers. Containers running as root (uid 0). No resource limits, so one runaway pod eats all the CPU and causes a cascade failure. Missing security contexts. Containers with `hostNetwork: true`, accidentally sharing the host’s network namespace like a guest who won’t leave a party.

**Flavour 2: The Supply Chain Wolf 🐍**
Images pulled from unverified registries. `latest` tags that could point to anything. No image signature verification. A dependency that quietly received a malicious update at 3am. He smiles innocently and says he is `nginx:latest`.

**Flavour 3: The Compliance Wolf 📋**
Not a breach — just catastrophically expensive findings at audit time. “Your clusters aren’t CIS-benchmarked.” “You have no evidence of HIPAA controls.” “Your SOC 2 auditors are asking where your policy documentation is.” *Huff. Puff.* There goes your certification.

**Flavour 4: The Drift Wolf 🌊**
Everything was fine on Monday. A well-meaning developer pushed a hotfix at 2am on Thursday that temporarily disabled a security control “just while the incident was being handled.” It is now Saturday. The control is still disabled. The Wolf moved in on Friday.

**Flavour 5: The Cost Wolf 💸**
Not technically a security wolf, but still destructive. Namespaces without resource quotas. Developers spinning up enormous test clusters and forgetting about them for three months. Orphaned volumes. The infrastructure bill arrives and it looks like someone’s mortgage.

All five wolves. One platform that handles them all. Ladies and gentlemen: **Nirmata**.

-----

## Who Is Nirmata? 🏛️

Nirmata is the company that created and maintains **Kyverno** — the Kubernetes-native policy engine that is now a CNCF (Cloud Native Computing Foundation) incubating project with over **3 billion downloads**. That is not a typo. Three billion.

Nirmata is, in the simplest possible terms, the enterprise platform that sits on top of Kyverno and makes it work at the scale, complexity, and regulatory requirements of large organisations. Where Kyverno is the individual brick, Nirmata is the brick factory, the architect, the building inspector, and the AI assistant who spots cracks before they appear.

**The Nirmata product family:**

|Product                       |What it does                                                |House analogy                                     |
|------------------------------|------------------------------------------------------------|--------------------------------------------------|
|**Kyverno OSS**               |Open-source policy engine — validates, mutates, generates   |Individual bricks, freely available               |
|**Nirmata Enterprise Kyverno**|Enterprise lifecycle, health checks, SLAs                   |Industrial-grade bricks with warranty             |
|**Nirmata Control Hub (NCH)** |Central control plane: multi-cluster, AI copilot, dashboards|The architect’s office overseeing all three houses|
|**AI Platform Assistant**     |Natural language → policies, AI remediation agents          |The architect’s AI assistant who never sleeps     |

-----

## The Village Layout: Three Clusters, Three Fates 🗺️

Throughout this series, we follow Penny, Stanley, and Brenda as Wolfgang the Wolf attempts to breach each of their homes.

```
🌾 Penny's Straw Cluster
   └── No Kyverno
   └── No admission control
   └── Privileged pods everywhere
   └── "I'll set this up properly next sprint"
   
🪵 Stanley's Stick Cluster
   └── Some RBAC
   └── Manual scanning (sometimes)
   └── No Policy-as-Code
   └── Spreadsheet titled "TODO_security.xlsx"

🧱 Brenda's Brick Cluster
   └── Kyverno OSS deployed
   └── NCH connected (multi-cluster)
   └── Policies enforced in pipeline AND cluster
   └── Audit trail, compliance reports
   └── Wolf has been trying for 18 months. Still nothing.
```

-----

## A Brief Word on Houses, Wolves, and YAML 🏗️

Kubernetes is a wonderful platform. It is also, by default, wide open. Like a house with no locks, no windows, no walls, and a sign outside saying “Free stuff, help yourself.” The power that makes Kubernetes flexible — the ability to run any container, with any configuration, doing almost anything — is also the power that makes it exploitable.

**Policy-as-Code** is the answer. Instead of a security team manually reviewing every deployment (an approach that scales approximately as well as reviewing every brick placement by hand), you write the rules *as code*, commit them to git, and let Kyverno enforce them automatically at the moment any resource tries to be created or changed.

The Wolf tries to create a privileged pod? Kyverno rejects it before it even exists.
The Wolf tries to pull an image from an untrusted registry? Rejected.
The Wolf tries to sneak in without a resource limit? Mutated automatically to include sensible defaults.
The Wolf tries to create a namespace without the required labels? Generated automatically on his behalf — or blocked, depending on mood.

The Wolf is not even in the picture anymore. He is standing outside the cluster, huffing at an API server that simply replies: `403 Forbidden: PolicyViolation: "your-pod-is-bad-and-you-should-feel-bad"`.

-----

## The Series: Eight Episodes of Wolfish Frustration 📚

|#|Episode                      |House being built       |The Wolf’s approach                 |
|-|-----------------------------|------------------------|------------------------------------|
|1|*This one* — Once Upon a Time|Scene-setting           |Wolf arrives and cracks knuckles    |
|2|Straw by Straw               |No policies at all      |Wolf walks straight through         |
|3|Sticks and Half-Measures     |Manual security         |Wolf finds the gaps                 |
|4|Bricks and Policy-as-Code    |Kyverno enforced        |Wolf starts to sweat                |
|5|The Control Tower            |Nirmata Control Hub     |Wolf tries the multi-cluster village|
|6|The AI Wolf-Spotter          |AI Platform Assistant   |Wolf writes a disguise letter       |
|7|The Boiling Pot              |Continuous compliance   |Wolf tries drifting back in at night|
|8|Happily Ever After           |The whole forest secured|Wolf writes a memoir. It is sad.    |

In **Episode 2**, we visit Penny’s straw house. The Wolf is already warming up his lungs. It does not go well for Penny.

-----

**🔗 Resources**

- **Nirmata**: [nirmata.com](https://nirmata.com)
- **Kyverno**: [kyverno.io](https://kyverno.io)
- **Kyverno GitHub** (3B+ downloads): [github.com/kyverno/kyverno](https://github.com/kyverno/kyverno)
- **Nirmata Control Hub**: [nirmata.com/nirmata-control-hub](https://nirmata.com/nirmata-control-hub/)

-----

*🐺 Big Bad Wolf Meets Nirmata — the fairytale in which Policy-as-Code proves considerably more durable than both straw and sticks.*
