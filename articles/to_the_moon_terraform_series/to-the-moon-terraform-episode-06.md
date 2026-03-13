---
title: "To The Moon Terraform Ep.6"
part: 6
published: false
description: "Episode 6 — The Modular Rocket"
tags: [terraform, modules, iac, reusability]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-06.webp"
canonical_url: ""
organization: "the-software-s-journey"
---

> *"The Saturn V was not one thing. It was three stages, a command module, a service module, and a lunar module — each designed independently, each tested independently, each capable of being replaced independently. The genius was not in any single component. The genius was in the interface between them."*

---

# 🌕 Episode 6 — The Modular Rocket

Let us consider, briefly, the engineering absurdity of building everything from scratch every time.

Imagine if NASA, having built the first Saturn V rocket, responded to the second Moon mission by saying: *"Right. Let's design a new rocket from first principles."* The fuel tank: reinvented. The guidance system: rewritten. The escape tower: reconsidered.

No organisation on Earth would do this. And yet, without Terraform Modules, this is precisely what infrastructure engineers do.

They write the same VPC configuration in every project. They copy-paste security group rules. They duplicate S3 bucket configurations with subtle differences that introduce subtle bugs. They re-invent, again and again, components that were already correct the first time.

Modules are how you build a rocket once and fly it many times.

---

## 🧱 What Is a Module?

A Terraform Module is simply a **directory of `.tf` files**. Any directory of Terraform configuration *is* a module — including the directory you have been working in, which is called the **root module**.

What makes modules powerful is **calling one module from another** — passing inputs in, receiving outputs back, hiding the internal complexity.

```
mission-apollo/                      ← Root module (your project)
├── main.tf                          ← Calls child modules
├── variables.tf
├── outputs.tf
│
└── modules/                         ← Child modules (reusable components)
    ├── network/                     ← VPC, subnets, gateways
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── compute/                     ← EC2 instances, launch templates
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── security/                    ← Security groups, IAM roles
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

Each module is a **stage of the rocket**: designed independently, tested independently, assembled into the complete vehicle.

---

## 🔧 Writing a Module: The Network Stage

```hcl
# modules/network/variables.tf

variable "mission_name" {
  description = "Mission name prefix for all resources"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_count" {
  description = "Number of public subnets"
  type        = number
  default     = 2
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}
```

```hcl
# modules/network/main.tf

locals {
  name_prefix = "${var.mission_name}-${var.environment}"
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "${local.name_prefix}-vpc" }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags   = { Name = "${local.name_prefix}-igw" }
}

resource "aws_subnet" "public" {
  count             = var.public_subnet_count
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${local.name_prefix}-public-${count.index + 1}" }
}

data "aws_availability_zones" "available" {
  state = "available"
}
```

```hcl
# modules/network/outputs.tf

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "internet_gateway_id" {
  description = "The ID of the Internet Gateway"
  value       = aws_internet_gateway.this.id
}
```

---

## 🚀 Calling a Module: The Assembly

```hcl
# main.tf — Root module: assembly of the rocket stages

# Stage 1: The Network (VPC and subnets)
module "network" {
  source = "./modules/network"   # Local path to the module

  mission_name        = var.mission_name
  environment         = var.environment
  vpc_cidr            = "10.0.0.0/16"
  public_subnet_count = 3
}

# Stage 2: The Compute (using network outputs as inputs)
module "compute" {
  source = "./modules/compute"

  mission_name   = var.mission_name
  environment    = var.environment
  vpc_id         = module.network.vpc_id              # Output from network → input to compute
  subnet_ids     = module.network.public_subnet_ids   # Output from network → input to compute
  instance_type  = var.instance_type
}

# Stage 3: The Security (IAM roles and policies)
module "security" {
  source = "./modules/security"

  mission_name = var.mission_name
  environment  = var.environment
}
```

The elegance: `module.network.vpc_id` — the output of one stage feeds directly into the input of the next. The interfaces between stages are explicit, typed, and documented.

---

## 🌐 Public Modules: The Supplier Network

You do not need to write every module yourself. The **Terraform Registry** (`registry.terraform.io`) hosts thousands of community and verified modules — pre-built rocket stages from trusted suppliers.

```hcl
# Using official AWS VPC module from the Terraform Registry
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"   # Pin the version — always

  name = "${var.mission_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Mission     = var.mission_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

This single module call replaces hundreds of lines of VPC configuration — and it has been tested by thousands of teams worldwide.

---

## 📊 The SIPOC of Episode 6

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| Root module | `module {}` block with `source` + input variables | Terraform resolves module source path or downloads from Registry | Module resource definitions merged into plan | Terraform planning and apply engine |
| Module's `variables.tf` | Values passed in `module {}` block | Input validation and type checking | Populated `var.*` namespace within module | Module's internal `main.tf` resources |
| Module's `main.tf` | Provider configuration (inherited from root) | Resources planned and applied | Real cloud resources | Module's `outputs.tf` value resolution |
| Module's `outputs.tf` | Attributes of resources created within module | Value extraction and exposure | Named outputs (`module.<name>.<output>`) | Root module and other modules referencing them |

---

*🌕 Next episode: **Mission Control Systems** — Remote State and Backends. Because a flight recorder that exists on only one engineer's laptop is not a flight recorder.*
