---
title: "To The Moon Terraform Ep.1"
part: 1
published: false
description: "Episode 1: The Audacity of Going to the Moon"
tags: [terraform, iac, devops, beginners]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-01.webp"
canonical_url: ""
organization: "the-software-s-journey"
---
 
> *"Here, in the vast, indifferent blackness of space, something extraordinary is about to happen. Something that has never happened before in the four-billion-year history of this planet. A creature — small, fragile, made mostly of water — has decided to leave it."*

---

# 🌕 Episode 1 — The Audacity of Going to the Moon

Observe, if you will, the modern infrastructure engineer.

They sit before a glowing screen. Around them: three empty coffee cups, a sticky note reading *"why is prod different from staging AGAIN"*, and the quiet, creeping horror of a cloud environment that has drifted — silently, inexorably — away from what it was supposed to be.

Someone, at some point, clicked something. In a console. Without telling anyone.

And now the infrastructure — the very foundation upon which their applications run — is a mystery. Not a beautiful mystery, like the bioluminescent creatures of the Mariana Trench. No. This is the mystery of: *"I have absolutely no idea what is actually deployed right now."*

This, dear reader, is the problem that Terraform was born to solve.

---

## 🚀 The Mission Briefing

In 1961, President Kennedy made one of the most audacious declarations in human history:

> *"We choose to go to the Moon. We choose to go to the Moon in this decade and do the other things, not because they are easy, but because they are hard."*

He did not say: *"Let's just spin up some servers and see what happens."*

He did not say: *"Dave from ops knows the password."*

He said: **we will declare the mission. We will plan every component. We will know exactly what we are building before we build it.** And we will do it reproducibly — because we may need to do it again.

This is the philosophy of **Terraform**.

---

## 🔭 What Is Terraform?

Terraform is an **Infrastructure as Code (IaC)** tool created by HashiCorp. It allows you to describe your infrastructure — servers, networks, databases, DNS records, Kubernetes clusters, anything — as **code in text files**.

Instead of clicking through the AWS console and hoping for the best, you write a declaration:

> *"I want three servers. This size. In this region. With this network. With this firewall rule."*

Terraform reads your declaration and makes it real. And — crucially — if you change your declaration and run Terraform again, it figures out precisely what needs to change. Not everything. Not nothing. Exactly what changed.

This is called **declarative infrastructure**. You describe the *desired state*. Terraform figures out how to get there.

---

## 🌍 Your First Line of Terraform

Here is the beginning. The first heartbeat.

```hcl
# main.tf — Mission Control, this is Houston. We are go for launch.

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "lunar_module" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  tags = {
    Name        = "lunar-module-1"
    Mission     = "apollo-terraform"
    Environment = "launch"
  }
}
```

This small declaration — 20 lines — will, when executed, provision a real server in Amazon Web Services. It will be the right size, in the right region, with the right name. And if you delete the file and run Terraform again, the server will be destroyed. The infrastructure follows the code. Always.

---

## 📊 The SIPOC of Episode 1

Every moon mission — and every Terraform operation — follows the SIPOC pattern. It tells us exactly who provides what, what happens, and who receives the result. We will use this in every episode.

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| You, the engineer | `main.tf` declaration file | `terraform init` + `terraform apply` | A real AWS EC2 instance | Your application / your team |
| HashiCorp Registry | AWS Provider plugin | Terraform downloads & installs provider | Local `.terraform/` directory | Terraform itself |
| AWS IAM | Access credentials | Authentication to AWS API | Authorised API session | Terraform AWS provider |

Read the SIPOC like a mission briefing: *"Who gives us what, what do we do with it, what comes out, and who benefits?"* Every Terraform operation — from the simplest resource to the most complex module — follows this chain.

---

## 🧭 The Four Commands You Must Know

Like the four stages of a Moon mission — launch, transit, landing, return — Terraform has four essential commands:

```bash
# 1. LAUNCH PREP — Download providers, initialise the workspace
terraform init

# 2. MISSION SIMULATION — Show what will change, before it changes
terraform plan

# 3. LAUNCH — Make the infrastructure real
terraform apply

# 4. CONTROLLED DESCENT — Destroy everything cleanly
terraform destroy
```

We will dedicate an entire episode to each of these. For now, know their names like you know the names of the Apollo 11 crew: Armstrong, Aldrin, Collins. `init`, `plan`, `apply`. These are your astronauts.

---

## 🌑 Why Does This Matter?

Consider the alternative. Without Terraform:

- Infrastructure exists only in someone's memory
- Environments drift: staging becomes different from production, nobody knows why
- Disaster recovery means *"remember what you built and rebuild it from scratch"*
- New team members inherit a maze with no map

With Terraform:

- Infrastructure is **versioned** in Git — every change is tracked
- Environments are **reproducible** — staging and production are identical by declaration
- Disaster recovery means `terraform apply` — the entire infrastructure rebuilds in minutes
- New team members read the code and *understand what exists*

---

## 🔭 The Series Ahead

Over the coming episodes, we will plan and execute a complete Moon mission — using Terraform to build the infrastructure that will carry us there. Each episode maps a mission phase to a Terraform concept.

| Episode | Mission Phase | Terraform Concept |
|---|---|---|
| **Ep.1** *(here)* | The Audacity | What is Terraform? |
| Ep.2 | Mission Architecture | Providers & Resources |
| Ep.3 | The Blueprint | Variables & Outputs |
| Ep.4 | The Pre-Flight Checklist | `terraform plan` in depth |
| Ep.5 | Launch Sequence | `terraform apply` & state |
| Ep.6 | The Modular Rocket | Terraform Modules |
| Ep.7 | Mission Control Systems | Remote State & Backends |
| Ep.8 | The Crew Manifest | Workspaces & Environments |
| Ep.9 | Mid-Course Corrections | `terraform import` & drift detection |
| Ep.10 | Docking Procedure | Dependencies & `depends_on` |
| Ep.11 | Life Support Systems | `for_each`, `count` & dynamic blocks |
| Ep.12 | The Landing | CI/CD with Terraform |
| Ep.13 | Moon Surface Operations | Provisioners & local-exec |
| Ep.14 | Return to Earth | `terraform destroy` & teardown |

---

## 🌟 Before We Leave the Launchpad

There is something quietly magnificent about what you are about to learn.

Fifty years ago, getting to the Moon required ten thousand engineers, four years, and the entire industrial capacity of a superpower. The knowledge lived in paper blueprints, in people's heads, in filing cabinets in Houston.

Today, with Terraform, you can describe an infrastructure of hundreds of services — networks, databases, load balancers, CDNs, monitoring systems, DNS records — in a few hundred lines of text. You can destroy it, recreate it, hand it to a colleague across the world, and they can run `terraform apply` and have an identical environment running in minutes.

The audacity hasn't changed. Only the tools.

---

*🌕 Next episode: **Mission Architecture** — we meet the Providers and Resources that form the components of our rocket.*

*Follow the series so you don't miss the launch.*

