---
title: "To The Moon Terraform Ep.2"
part: 2
published: false
description: "Episode 2: Mission Architecture (Providers & Resources)"
tags: [terraform, iac, providers, resources]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-02.webp"
canonical_url: ""
organization: "the-software-s-journey"
---

> *"Before a single component can be manufactured, before a single bolt is tightened, the engineers must agree on something fundamental: what, precisely, are we building? And who, precisely, will supply each part?"*

---

# 🌕 Episode 2 — Mission Architecture (Providers & Resources)

Watch, for a moment, the engineers of the Saturn V rocket.

They did not sit down one morning and simply *start welding*. What they produced first — before any physical work began — was a document of breathtaking specificity. Every stage. Every engine. Every fuel line. Every guidance system. Thousands of components, each with a defined supplier, defined inputs, defined outputs, and a defined interface with every adjacent component.

They called this **systems engineering**.

Terraform calls it **providers and resources**.

---

## 🏭 The Rocket's Bill of Materials

A Moon rocket is not one thing. It is thousands of things, assembled from dozens of suppliers, each responsible for a specific domain.

- **Rocketdyne** supplies the F-1 engines
- **IBM** supplies the guidance computer
- **North American Aviation** supplies the Command Module
- **Grumman** supplies the Lunar Module

Each supplier speaks their own technical language. Each delivers a specific component. Each has a precise interface.

In Terraform, **Providers** are your suppliers. And **Resources** are the components they deliver.

---

## 🔌 Providers: The Component Suppliers

A Provider is a plugin that teaches Terraform how to talk to a specific system. AWS. Azure. Google Cloud. Kubernetes. GitHub. Cloudflare. Datadog. There are over 3,000 providers in the HashiCorp Registry.

Each provider is a bridge between Terraform's language and a remote API.

```hcl
# terraform.tf — The Mission Supplier Manifest

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    # Supplier 1: Amazon Web Services — rocket fuel and launch infrastructure
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.31"
    }

    # Supplier 2: Random — for generating unique identifiers (mission codes)
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }

    # Supplier 3: TLS — for generating cryptographic keys (astronaut badges)
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

# Configure the AWS supplier: which launch site (region)?
provider "aws" {
  region = "us-east-1"   # Cape Canaveral

  default_tags {
    tags = {
      Mission    = "apollo-terraform"
      ManagedBy  = "terraform"
      Series     = "to-the-moon"
    }
  }
}
```

When you run `terraform init`, Terraform downloads each provider plugin — like calling your suppliers and saying: *"We are go. Begin shipping components."*

---

## 🧱 Resources: The Mission Components

A Resource is a single piece of infrastructure managed by Terraform. A server. A network. A database. A DNS record. A firewall rule. Each resource has a **type** (what it is) and a **name** (what you call it).

```hcl
# Resources follow the pattern:
# resource "<provider>_<type>" "<local_name>" { ... }
```

Observe now the bill of materials for our lunar mission infrastructure:

```hcl
# network.tf — The Launch Site Infrastructure

# Component 1: The Launch Pad (Virtual Private Cloud — our isolated network)
resource "aws_vpc" "launch_pad" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "apollo-launch-pad"
    Role = "mission-network"
  }
}

# Component 2: The Runway (Public Subnet — where traffic lands and takes off)
resource "aws_subnet" "runway" {
  vpc_id            = aws_vpc.launch_pad.id   # <- References the VPC above
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  map_public_ip_on_launch = true

  tags = {
    Name = "apollo-runway"
    Role = "public-access"
  }
}

# Component 3: The Mission Comms Tower (Internet Gateway — connects us to the outside world)
resource "aws_internet_gateway" "comms_tower" {
  vpc_id = aws_vpc.launch_pad.id

  tags = {
    Name = "apollo-comms-tower"
  }
}
```

Notice something extraordinary here. `aws_subnet.runway` references `aws_vpc.launch_pad.id`. This is not an accident. This is Terraform's **dependency graph** — the subnet knows it cannot exist without the VPC, and Terraform ensures the VPC is created first. The rocket stages fire in sequence. Always.

---

## 📊 The SIPOC of Episode 2

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| HashiCorp Registry | Provider source + version in `terraform {}` block | `terraform init` downloads plugins | Provider binary in `.terraform/` | All resource blocks in your config |
| AWS API | Resource block configuration (CIDR, region, tags) | AWS creates the actual network resource | Real VPC with an ID (`vpc-0abc1234`) | Other resources that reference `aws_vpc.launch_pad.id` |
| Terraform state engine | Current desired state + last known real state | Diff calculation | Change plan (create/update/destroy) | `terraform apply` execution engine |
| You, the engineer | `.tf` files checked into Git | `terraform plan` | Human-readable preview of changes | Your team's review process |

The elegance here is in the chain. Every output becomes someone else's input. The supplier hands to the process hands to the output hands to the consumer. Nothing is orphaned. Nothing is ambiguous.

---

## 🔗 Resource References: The Assembly Line

Every resource, once created, exposes **attributes** — properties that other resources can reference. This is how complex infrastructure assembles itself, component by component, like Saturn V stages stacking in the Vehicle Assembly Building.

```hcl
# compute.tf — The Crew Capsule

# First, a security group — the spacecraft's hull (controls what enters and exits)
resource "aws_security_group" "crew_capsule" {
  name        = "apollo-crew-capsule-sg"
  description = "Mission Control approved communications only"
  vpc_id      = aws_vpc.launch_pad.id   # Knows which launch pad it lives on

  # Inbound: HTTPS only (authorised comms from Earth)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Mission comms from Earth"
  }

  # Outbound: All traffic allowed (astronauts can call home freely)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Crew comms to any destination"
  }

  tags = {
    Name = "apollo-crew-capsule-sg"
    Role = "spacecraft-hull"
  }
}

# The Lunar Module — the actual compute workload
resource "aws_instance" "lunar_module" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.runway.id             # Which runway?
  vpc_security_group_ids = [aws_security_group.crew_capsule.id]  # Which hull?

  tags = {
    Name = "apollo-lunar-module"
    Role = "primary-compute"
  }
}
```

The lunar module references the runway. The runway references the launch pad. The crew capsule references the launch pad. Terraform builds a **dependency graph** from these references and determines the correct creation order automatically.

You do not instruct it to *"create the VPC first, then the subnet, then the security group, then the instance."* You simply describe the relationships and Terraform resolves the order. Like a brilliant mission coordinator who needs only to know the dependencies — not be told, step by step, what to do next.

---

## 📁 File Organisation: The Mission Binders

Terraform does not care which `.tf` file your code is in. All `.tf` files in a directory are processed together. This gives you freedom to organise — and responsibility to do so wisely.

A mission-worthy file structure:

```
apollo-terraform/
├── terraform.tf        # Provider requirements — the supplier manifest
├── main.tf             # Primary resources — the mission core
├── network.tf          # VPC, subnets, gateways — the launch site
├── compute.tf          # Servers, clusters — the spacecraft
├── security.tf         # IAM, security groups — the mission rules
├── variables.tf        # Input declarations — the mission parameters
├── outputs.tf          # Output declarations — the mission reports
└── terraform.tfvars    # Variable values — the actual values for THIS mission
```

This is not bureaucracy. This is the same systematic organisation that allowed NASA to manage millions of components across dozens of contractors — because when something goes wrong (and something will go wrong), you need to know exactly where to look.

---

## 🌑 The Resource Lifecycle

Every Terraform resource has a lifecycle — a journey from declaration to existence to destruction.

```
Declared in .tf  →  terraform plan (proposed)  →  terraform apply (created)
     ↑                                                      ↓
Updated in .tf   ←  terraform plan (proposed change)  ←  Running in cloud
     ↓                                                      ↓
terraform apply  →  Resource updated in-place OR destroyed+recreated
     ↓
terraform destroy → Resource removed from cloud AND from state
```

In lifecycle terms, Terraform resources are mortal. They are born when you declare them, they live as long as you maintain them, and they die when you remove them from your code. There is something almost poetic in this. The infrastructure is entirely subordinate to the declaration.

The code is truth. The cloud is merely its current reflection.

---

## 🌟 What We Have Built

We now have:
- A network (VPC) — the launch site
- A subnet — the runway
- An internet gateway — the comms tower
- A security group — the spacecraft hull
- A compute instance — the lunar module

Five components. Five resources. One coherent system. And every single one of it is described in text files that can be committed to Git, reviewed by peers, and applied identically in any AWS account on the planet.

This is the power that the Moon missions lacked. Every Apollo blueprint existed in one place. If the building burned down, the knowledge burned with it.

Your Terraform code lives everywhere Git lives. The knowledge is immortal.

---

*🌕 Next episode: **The Blueprint** — we discover Variables and Outputs, and learn how to build a mission that can be re-flown with different parameters.*

*Because going to the Moon once is magnificent. Going repeatedly — with confidence — is engineering.*
