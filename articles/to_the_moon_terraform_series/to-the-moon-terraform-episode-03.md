---
title: "To The Moon Terraform 🌕 Ep.3"
part: 3
published: false
description: "Episode 3: The Blueprint (Variables & Outputs)"
tags: [terraform, variables, outputs, iac]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-03.webp"
canonical_url: ""
organization: "the-software-s-journey"
---

> *"The Saturn V flew thirteen times. Not thirteen slightly different rockets — thirteen instances of a single masterpiece, each adjusted only by the precise mission parameters it was given. The blueprint was constant. The mission was the variable."*

---

# 🌕 Episode 3 — The Blueprint (Variables & Outputs)

There is a species of creature in the engineering world that fascinates and troubles me in equal measure.

It is the **hardcoded configuration**.

You find it everywhere — lurking deep in `.tf` files, sometimes in configuration files, occasionally even in shell scripts committed to public repositories with AWS access keys in them (a horror I shall not dwell on here). This creature has one defining characteristic: it cannot adapt. It knows only one environment. One region. One instance size. One mission.

Change any parameter and the whole thing shatters.

The Saturn V engineers understood that missions would vary. The payload changes. The trajectory changes. The launch window changes. But the rocket — the *design* of the rocket — stays constant. You change the **parameters**, not the blueprint.

This is the purpose of **Terraform Variables**.

---

## 🔧 Input Variables: The Mission Parameters

An Input Variable is a parameter that makes your Terraform code reusable across missions. Instead of hardcoding `"us-east-1"` in twenty places, you declare a variable called `region` and use it everywhere.

When you want to fly to a different launch site, you change one parameter. Not twenty values scattered through three files.

```hcl
# variables.tf — The Mission Parameter Sheet

# Where are we launching from?
variable "aws_region" {
  description = "The AWS region where mission infrastructure will be deployed"
  type        = string
  default     = "us-east-1"   # Cape Canaveral is the default

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "Region must be a valid AWS region code (e.g., us-east-1, eu-west-1)."
  }
}

# What is this mission called?
variable "mission_name" {
  description = "The name of this mission. Used to tag all resources."
  type        = string

  validation {
    condition     = length(var.mission_name) >= 3 && length(var.mission_name) <= 20
    error_message = "Mission name must be between 3 and 20 characters."
  }
}

# What environment are we operating in?
variable "environment" {
  description = "The operating environment: simulation, staging, or production"
  type        = string
  default     = "simulation"

  validation {
    condition     = contains(["simulation", "staging", "production"], var.environment)
    error_message = "Environment must be 'simulation', 'staging', or 'production'."
  }
}

# What size spacecraft do we need?
variable "instance_type" {
  description = "The EC2 instance type for the lunar module compute"
  type        = string
  default     = "t3.micro"
}

# How many crew members? (How many instances to run)
variable "crew_count" {
  description = "Number of compute instances to launch"
  type        = number
  default     = 1

  validation {
    condition     = var.crew_count >= 1 && var.crew_count <= 10
    error_message = "Crew count must be between 1 and 10. We are not launching an army."
  }
}

# Mission configuration map — structured parameters as a complex type
variable "mission_config" {
  description = "Mission configuration object"
  type = object({
    enable_monitoring = bool
    backup_retention  = number
    allowed_cidrs     = list(string)
  })
  default = {
    enable_monitoring = true
    backup_retention  = 7
    allowed_cidrs     = ["10.0.0.0/8"]
  }
}
```

---

## 🔤 Variable Types: The Classification of Parameters

Variables in Terraform are typed. This is not pedantry — it is the same discipline that kept the Saturn V from exploding because someone mixed up imperial and metric units. (That particular horror belongs to a different programme.)

```hcl
# The full catalogue of Terraform variable types:

variable "example_string" {
  type    = string
  default = "Houston, we have a configuration"
}

variable "example_number" {
  type    = number
  default = 42
}

variable "example_bool" {
  type    = bool
  default = true
}

variable "example_list" {
  type    = list(string)
  default = ["Armstrong", "Aldrin", "Collins"]
}

variable "example_map" {
  type    = map(string)
  default = {
    commander = "Armstrong"
    pilot     = "Aldrin"
    module    = "Collins"
  }
}

variable "example_set" {
  type    = set(string)
  default = ["us-east-1", "eu-west-1"]
}

variable "example_object" {
  type = object({
    name        = string
    crew_size   = number
    is_crewed   = bool
    destinations = list(string)
  })
}
```

---

## 📁 Variable Values: The Mission Assignment

Declaring a variable is like designing a form with blank fields. **Providing the value** is like filling in the form for a specific mission.

There are four ways to provide values, in order of increasing precedence (later sources override earlier ones):

### Method 1: Default Values (in the variable declaration)
The fallback. Used when nothing else is specified.

### Method 2: `terraform.tfvars` file
```hcl
# terraform.tfvars — Mission Apollo-Terraform: Production Values

aws_region    = "us-east-1"
mission_name  = "apollo-terraform"
environment   = "production"
instance_type = "t3.small"
crew_count    = 3

mission_config = {
  enable_monitoring = true
  backup_retention  = 30
  allowed_cidrs     = ["10.0.0.0/8", "172.16.0.0/12"]
}
```

### Method 3: Named `.tfvars` files (for multiple missions)
```bash
# For a simulation mission
terraform apply -var-file="simulation.tfvars"

# For a production launch
terraform apply -var-file="production.tfvars"
```

```hcl
# simulation.tfvars — Simulation parameters (cheaper, lower stakes)
environment   = "simulation"
instance_type = "t3.micro"
crew_count    = 1

mission_config = {
  enable_monitoring = false
  backup_retention  = 1
  allowed_cidrs     = ["0.0.0.0/0"]
}
```

### Method 4: Environment Variables and CLI flags (for automation)
```bash
# Environment variables prefix with TF_VAR_
export TF_VAR_mission_name="apollo-terraform"
export TF_VAR_environment="production"

# Or pass directly at the command line
terraform apply -var="crew_count=5" -var="environment=staging"
```

---

## 📤 Outputs: The Mission Report

If Variables are the inputs to the mission, **Outputs** are the mission report — the telemetry sent back from space that tells you what was created, where it is, and how to reach it.

After `terraform apply`, you want to know: *What is the IP address of my server? What is the name of the S3 bucket? What is the ARN of the IAM role?*

Outputs answer these questions.

```hcl
# outputs.tf — The Mission Telemetry Report

output "lunar_module_public_ip" {
  description = "Public IP address of the Lunar Module (for SSH access)"
  value       = aws_instance.lunar_module.public_ip
}

output "lunar_module_id" {
  description = "AWS instance ID of the Lunar Module"
  value       = aws_instance.lunar_module.id
}

output "launch_pad_vpc_id" {
  description = "VPC ID of the Launch Pad network"
  value       = aws_vpc.launch_pad.id
}

output "mission_summary" {
  description = "Complete mission deployment summary"
  value = {
    mission     = var.mission_name
    environment = var.environment
    region      = var.aws_region
    server_ip   = aws_instance.lunar_module.public_ip
    server_id   = aws_instance.lunar_module.id
    vpc_id      = aws_vpc.launch_pad.id
  }
}

# Sensitive outputs — marked, so Terraform won't display them in logs
output "database_password" {
  description = "The database password (sensitive — not displayed in logs)"
  value       = random_password.db_password.result
  sensitive   = true   # Redacted in terminal output; still stored in state
}
```

After `terraform apply`, you retrieve outputs:

```bash
# See all outputs
terraform output

# See one specific output
terraform output lunar_module_public_ip

# Output as JSON (for scripts and pipelines)
terraform output -json

# Example output:
# lunar_module_public_ip = "54.123.45.67"
# launch_pad_vpc_id = "vpc-0a1b2c3d4e5f"
```

---

## 📊 The SIPOC of Episode 3

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| You, the engineer | `variables.tf` type declarations | Terraform validates types & constraints | Type-safe variable schema | All `.tf` files using `var.*` references |
| `terraform.tfvars` / env vars | Concrete variable values | Terraform populates `var.*` namespace | Resolved variable values | Resource configurations at apply time |
| Cloud provider (AWS) | Applied resource configuration | Resource creation in cloud | Real resources with IDs, IPs, ARNs | `outputs.tf` value references |
| Terraform state | Resource attribute values post-apply | Output value resolution | Named outputs in state | CI/CD pipelines, other Terraform modules, your terminal |

---

## 🔄 Locals: The Derived Calculations

Between inputs and outputs, there is a third category: **locals**. These are computed values derived from variables and resource attributes — the mission's internal calculations that don't need to be exposed as parameters.

```hcl
# locals.tf — Internal Mission Calculations

locals {
  # Derived naming convention — consistent across all resources
  name_prefix = "${var.mission_name}-${var.environment}"

  # Common tags — applied to everything, computed once
  common_tags = {
    Mission     = var.mission_name
    Environment = var.environment
    ManagedBy   = "terraform"
    LaunchDate  = formatdate("YYYY-MM-DD", timestamp())
  }

  # Conditional logic — which AMI for which environment?
  ami_id = var.environment == "production" ? "ami-prod-0abc123" : "ami-dev-0def456"

  # Computed CIDR blocks
  public_subnet_cidrs  = [for i in range(3) : cidrsubnet(var.vpc_cidr, 8, i)]
  private_subnet_cidrs = [for i in range(3) : cidrsubnet(var.vpc_cidr, 8, i + 10)]
}

# Use in resources:
resource "aws_instance" "lunar_module" {
  ami           = local.ami_id
  instance_type = var.instance_type
  tags          = merge(local.common_tags, { Name = "${local.name_prefix}-lunar-module" })
}
```

Locals are the mission engineer's scratch pad. They transform raw parameters into usable values without exposing the intermediate calculations to the outside world.

---

## 🌟 The Blueprint Complete

We now have a Terraform configuration that:

- Accepts **parameters** — mission name, environment, region, instance type
- **Validates** those parameters before any infrastructure is created
- **Computes** derived values using locals
- **Creates** real infrastructure using the parameterised values
- **Reports back** the critical attributes through outputs

This same blueprint can now be used to deploy:
- A `simulation` mission in `us-east-1` with `t3.micro`
- A `staging` mission in `eu-west-1` with `t3.small`
- A `production` mission in `us-east-1` with `t3.large` and 3 instances

One blueprint. Multiple missions. Exactly as NASA intended.

---

*🌕 Next episode: **The Pre-Flight Checklist** — we go deep on `terraform plan` and learn why you should never, ever apply without planning first.*

*It is the same reason you do not fire a rocket engine without checking all 400,000 components first.*
