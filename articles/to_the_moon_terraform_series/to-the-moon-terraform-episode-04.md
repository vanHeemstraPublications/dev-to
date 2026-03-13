---
title: "To The Moon 🌕 Ep.4"
part: 4
published: false
description: "Episode 4: The Pre-Flight Checklist (terraform plan)"
tags: [terraform, plan, iac, devops]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-04.webp"
canonical_url: ""
organization: "the-software-s-journey"
---

> *"On the morning of July 16, 1969, launch controllers ran through a checklist of 363,000 items. Three hundred and sixty-three thousand. Every one of them had to be confirmed 'GO' before a single gram of propellant was ignited. This was not caution. This was the highest form of engineering confidence: the certainty that comes only from having checked everything."*

---

# 🌕 Episode 4 — The Pre-Flight Checklist (terraform plan)

There exists a particular kind of recklessness that wears the costume of confidence.

You have seen it. Perhaps you have *been* it — fingers hovering over the keyboard, infrastructure code freshly written, and the irresistible urge to simply *run it and see what happens*.

This is how databases are accidentally deleted. This is how production environments are brought to their knees at 2pm on a Tuesday. This is how a senior engineer discovers, with cold clarity, that `terraform destroy` without a `-target` flag is not selective.

`terraform plan` exists to save you from yourself.

---

## 🔭 What terraform plan Actually Does

`terraform plan` is a **dry run** — a complete simulation of what would happen if you ran `terraform apply`. It does not change anything. It examines three things:

1. **Your desired state** — what your `.tf` files declare should exist
2. **Your current state** — what Terraform last recorded as actually existing (in `terraform.tfstate`)
3. **Reality** — what the cloud provider says actually exists right now

It computes the **diff** between where you are and where you want to be, and presents it to you as a precise, human-readable plan.

```bash
# Run the pre-flight checklist
terraform plan

# Save the plan to a file (for guaranteed identical apply)
terraform plan -out=mission-apollo.tfplan

# Apply ONLY what was in the saved plan — no surprises
terraform apply mission-apollo.tfplan
```

---

## 📋 Reading the Plan Output

The plan output uses a simple symbology — three symbols that carry enormous weight:

```
+ create     ← This resource will be CREATED (new)
- destroy    ← This resource will be DESTROYED (removed)
~ update     ← This resource will be UPDATED in-place (changed)
-/+ replace  ← This resource will be DESTROYED and RECREATED (breaking change)
```

That last one — `-/+` — is the one that stops your heart. It means the change you made requires the resource to be destroyed and rebuilt. For a database, that means data loss. For a server, that means downtime. For an S3 bucket with versioning disabled, that means gone.

Let us see a real plan output:

```hcl
# Before: We have a t3.micro lunar module
resource "aws_instance" "lunar_module" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"   # We are changing this to t3.small
  ...
}
```

```bash
$ terraform plan

Terraform will perform the following actions:

  # aws_instance.lunar_module will be updated in-place
  ~ resource "aws_instance" "lunar_module" {
        id                    = "i-0a1b2c3d4e5f67890"
      ~ instance_type         = "t3.micro" -> "t3.small"
        # (All other attributes unchanged)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

Good. The instance type changes in-place. No destruction. No data loss.

Now watch what happens when we change something that *forces replacement*:

```hcl
# Changing the AMI of a running instance requires destroy + recreate
resource "aws_instance" "lunar_module" {
  ami           = "ami-0c55b159cbfafe1f0"   # Changing this value
  instance_type = "t3.micro"
}
```

```bash
$ terraform plan

Terraform will perform the following actions:

  # aws_instance.lunar_module must be replaced
-/+ resource "aws_instance" "lunar_module" {
      ~ ami           = "ami-0c55b159cbfafe1f0" -> "ami-0987654321abcdef0" # forces replacement
        id            = "i-0a1b2c3d4e5f67890"
        instance_type = "t3.micro"
        # (All other attributes unchanged)
    }

Plan: 1 to add, 0 to change, 1 to destroy.
```

The `-/+` tells you: the old server will be destroyed, and a new one created. This is your warning. This is the pre-flight checklist catching a potentially catastrophic consequence *before* any propellant is ignited.

---

## 📊 The SIPOC of Episode 4

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| Your `.tf` files | Desired infrastructure state | Terraform parses HCL configuration | Internal desired-state model | Diff engine |
| `terraform.tfstate` | Last known real state | State file is read and loaded | Current state model | Diff engine |
| Cloud provider API | Real-time resource query (refresh) | Provider queries live cloud resources | Refreshed actual state | Diff engine |
| Diff engine | Desired vs actual state | Three-way comparison | Ordered list of changes | Human reviewer + `terraform apply` |
| You, the reviewer | Plan output | Human review of changes | GO / NO-GO decision | Launch (apply) or abort |

Read this SIPOC carefully. Notice that **you** are in the chain — between the plan output and the apply decision. This is intentional. Terraform plans are not automated approvals. They are requests for human sign-off. The checklist requires a human controller to say *GO*.

---

## 🚨 The -/+ Destroyer: Forces Replacement

Learning which changes force replacement is one of the most valuable skills in Terraform mastery. Here is the field guide:

```hcl
# Changes that UPDATE IN-PLACE (safe, no disruption):
# - Tags (on most resources)
# - Instance type (on EC2 — requires stop/start but no replacement)
# - Security group associations
# - IAM policy document content

# Changes that FORCE REPLACEMENT (destroy + recreate — potentially destructive):
# - AMI ID on an EC2 instance
# - Subnet ID (you can't move a resource between subnets)
# - VPC ID (you can't move a resource between VPCs)
# - Encryption settings on an EBS volume
# - The 'name' attribute on many resources (names are immutable in AWS)
# - Availability zone of a resource
```

When you see `-/+` in a plan output affecting a database, a file storage service, or anything stateful — **stop**. Read the plan. Understand what data might be lost. Consider using `lifecycle` blocks to prevent accidental destruction:

```hcl
resource "aws_db_instance" "mission_database" {
  identifier     = "apollo-mission-db"
  instance_class = "db.t3.micro"
  engine         = "postgres"
  engine_version = "15.3"

  # ... other config ...

  lifecycle {
    # Terraform will error rather than destroy this resource
    prevent_destroy = true

    # New resource created before old one destroyed (zero-downtime replacement)
    create_before_destroy = true

    # Ignore changes to these attributes (made outside Terraform — e.g., by autoscaling)
    ignore_changes = [
      engine_version,    # Allow AWS to manage minor version upgrades
      instance_class,    # Allow autoscaling to change instance size
    ]
  }
}
```

---

## 🗂️ Saved Plans: The Signed Flight Manifest

The most rigorous teams do not just run `terraform plan` for review and then `terraform apply` separately. They **save the plan** and apply *exactly that plan* — nothing more, nothing less.

```bash
# Generate and save the plan — sign the manifest
terraform plan -out=mission-apollo-2026-03-12.tfplan

# Inspect the saved plan (shows same output as initial plan)
terraform show mission-apollo-2026-03-12.tfplan

# Apply EXACTLY the saved plan — no new diff calculated
terraform apply mission-apollo-2026-03-12.tfplan
```

Why does this matter? Because between your `plan` and your `apply`, the world may have changed. A colleague may have applied a different change. AWS may have updated an attribute. Using a saved plan guarantees that what you reviewed is *exactly* what gets applied.

In the Apollo programme, this was called **configuration control**. The vehicle you reviewed on the launchpad is the vehicle that launches. No last-minute swaps. No undocumented modifications.

---

## 🔍 Plan Detail Flags: The Extended Checklist

```bash
# Show what the plan will refresh from the cloud before diffing
terraform plan -refresh=true   # Default: true

# Skip refreshing from cloud (faster, but may miss drift)
terraform plan -refresh=false

# Target only specific resources (use sparingly — can create inconsistencies)
terraform plan -target=aws_instance.lunar_module

# Show compact diff (only what changes, not unchanged attributes)
terraform plan -compact-warnings

# Detailed exit codes for CI/CD pipelines:
# 0 = no changes  |  1 = error  |  2 = changes present
terraform plan -detailed-exitcode
echo "Exit code was: $?"
```

---

## 🌑 What the Plan Doesn't Tell You

`terraform plan` is extraordinarily good at what it does. But there are things it cannot know:

- **Application-level impact**: Deleting a security group rule may not break Terraform — but it may break your application.
- **Timing effects**: Some resources take time to become active after creation. The plan doesn't show wait times.
- **External dependencies**: If another team's infrastructure depends on yours, the plan doesn't know about them.
- **Quotas and limits**: The plan may succeed syntactically but fail at apply time because your AWS account has hit a service limit.

The pre-flight checklist is not infallible. It eliminates the preventable disasters. The unforeseeable ones — those are what contingency plans are for.

---

## 🌟 The GO/NO-GO Decision

In mission control, the Flight Director polls each station: *"FIDO, go or no-go? GUIDO, go or no-go? FLIGHT, we are go for launch."*

Your `terraform plan` output is the polling of stations. You review each change. You understand each `-/+`. You confirm that the plan is consistent with your intent. And then — only then — you say GO.

```bash
# The sequence every mission should follow:
terraform init       # Prepare the launch systems
terraform validate   # Syntax check — all wiring connected?
terraform plan -out=mission.tfplan   # Run the full checklist
# [HUMAN REVIEW OF PLAN OUTPUT]
# [GO/NO-GO DECISION]
terraform apply mission.tfplan   # Launch
```

This is not bureaucracy. This is the discipline that separates the missions that land from the ones that don't.

---

*🌕 Next episode: **Launch Sequence** — `terraform apply` and the state file. The moment the infrastructure becomes real.*

*We have checked everything. We are GO for launch.*
