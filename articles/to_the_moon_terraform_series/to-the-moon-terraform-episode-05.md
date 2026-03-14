---
title: "To The Moon Terraform Ep.5"
part: 5
published: false
description: "Episode 5: Launch Sequence (terraform apply & the State File)"
tags: [terraform, state, apply, iac]
series: "To The Moon Terraform Series"
canonical_url: ""
organization: "the-software-s-journey"
---

> *"T-minus 10. Nine. Eight. Ignition sequence start. Six. Five. Four. Three. Two. One. Zero. All engines running. Liftoff. We have a liftoff."*

> *"In that moment — that single, irreversible moment — the mission ceased to be a plan and became a fact."*

---

# 🌕 Episode 5 — Launch Sequence (terraform apply & the State File)

There is a moment in every mission from which there is no return.

For the Saturn V, it was the ignition of the F-1 engines — 7.5 million pounds of thrust, fire and fury, the rocket committing itself to the sky. There was no pause button. No undo command. Once the engines lit, the mission was underway.

`terraform apply` is that moment.

Not because it is dangerous — when preceded by a careful `terraform plan`, it is as safe as engineering can make it. But because it is the moment when your declarations become real. When text files become servers. When code becomes cloud.

Let us understand exactly what happens in those seconds.

---

## 🔥 What terraform apply Does

When you run `terraform apply`, Terraform:

1. Generates a fresh plan (or uses a saved plan)
2. Asks for confirmation: *"Do you want to perform these actions?"*
3. Executes the changes in the correct dependency order
4. Updates the **state file** after each resource is created/modified/destroyed
5. Displays outputs upon completion

```bash
# Standard apply — generates plan, asks for confirmation
terraform apply

# Apply a previously saved plan — no confirmation needed
terraform apply mission-apollo.tfplan

# Skip confirmation (for CI/CD pipelines — use with discipline)
terraform apply -auto-approve

# Target a single resource (use only in emergencies)
terraform apply -target=aws_instance.lunar_module
```

---

## 🌌 The Apply in Motion

Here is what the terminal looks like when a Moon mission launches:

```bash
$ terraform apply mission-apollo.tfplan

aws_vpc.launch_pad: Creating...
aws_vpc.launch_pad: Creation complete after 2s [id=vpc-0a1b2c3d4e5f67890]

aws_internet_gateway.comms_tower: Creating...
aws_subnet.runway: Creating...
aws_internet_gateway.comms_tower: Creation complete after 1s [id=igw-0a1b2c3d]
aws_subnet.runway: Creation complete after 1s [id=subnet-0a1b2c3d]

aws_security_group.crew_capsule: Creating...
aws_security_group.crew_capsule: Creation complete after 2s [id=sg-0a1b2c3d4e5f]

aws_instance.lunar_module: Creating...
aws_instance.lunar_module: Still creating... [10s elapsed]
aws_instance.lunar_module: Still creating... [20s elapsed]
aws_instance.lunar_module: Creation complete after 23s [id=i-0a1b2c3d4e5f67890]

Apply complete! Resources: 5 added, 0 changed, 0 destroyed.

Outputs:
lunar_module_public_ip = "54.123.45.67"
launch_pad_vpc_id      = "vpc-0a1b2c3d4e5f67890"
```

Notice the sequence. The VPC creates first — because the subnet and gateway reference it. The security group creates after the VPC. The instance creates last — because it references both the subnet and the security group.

Terraform's dependency graph ensures this order automatically. You declared the relationships. Terraform resolved the order. This is the division of labour between engineer and tool.

---

## 📦 The State File: Mission Flight Recorder

After every successful `terraform apply`, Terraform writes to a file called `terraform.tfstate`.

This file is the **flight recorder** — the precise record of what Terraform created, with every attribute, every ID, every generated value.

```json
// terraform.tfstate (simplified — real files are much larger)
{
  "version": 4,
  "terraform_version": "1.6.0",
  "serial": 12,
  "lineage": "8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d",
  "outputs": {
    "lunar_module_public_ip": {
      "value": "54.123.45.67",
      "type": "string"
    }
  },
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "lunar_module",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 1,
          "attributes": {
            "ami": "ami-0c55b159cbfafe1f0",
            "id": "i-0a1b2c3d4e5f67890",
            "instance_type": "t3.micro",
            "public_ip": "54.123.45.67",
            "private_ip": "10.0.1.42",
            "subnet_id": "subnet-0a1b2c3d",
            "vpc_security_group_ids": ["sg-0a1b2c3d4e5f"],
            "tags": {
              "Name": "apollo-lunar-module",
              "Mission": "apollo-terraform",
              "ManagedBy": "terraform"
            }
          }
        }
      ]
    }
  ]
}
```

This state file is the answer to: *"What does Terraform currently know about the real world?"*

Without it, Terraform cannot compute diffs. Without it, Terraform cannot know that `i-0a1b2c3d4e5f67890` is `aws_instance.lunar_module`. Without it, every apply would try to create everything from scratch.

**The state file is not a log. It is memory. And like all memory, it must be protected.**

---

## 📊 The SIPOC of Episode 5

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| Saved plan file | Ordered change set | Terraform executes changes via provider API | Real cloud resources (IDs, IPs, ARNs) | State file, outputs |
| Cloud provider API | Resource creation/update requests | AWS creates/modifies resources | Resource attributes (id, public_ip, etc.) | Terraform state writer |
| State writer | Resource attributes from provider | JSON serialisation | Updated `terraform.tfstate` | Next `terraform plan` or `terraform apply` |
| State file | Previous known state | Read on every plan/apply | Baseline for diff calculation | Terraform planning engine |
| Output definitions | Resource attribute references | Value resolution post-apply | Output values displayed + stored in state | Engineers, CI/CD pipelines, downstream modules |

---

## ⚠️ State File Rules: The Non-Negotiables

The state file has properties that every Terraform engineer must understand and respect:

### 1. Never commit it to Git (if it contains secrets)
The state file may contain sensitive values — database passwords, private keys, API tokens. If your state file contains secrets, it should never live in a Git repository.

```gitignore
# .gitignore — Always add these
*.tfstate
*.tfstate.backup
.terraform/
*.tfplan
```

### 2. Never edit it by hand
The state file is Terraform's internal database. Editing it by hand is like performing surgery on a flight recorder with a chisel. It can be done. It should almost never be done. When it must be done, use `terraform state` commands.

```bash
# State manipulation commands (use with extreme care)
terraform state list                           # List all resources in state
terraform state show aws_instance.lunar_module # Show full state for one resource
terraform state rm aws_instance.lunar_module   # Remove from state (doesn't destroy cloud resource)
terraform state mv source destination          # Rename a resource in state
```

### 3. Never let two people apply at the same time
If two engineers run `terraform apply` simultaneously against the same state, they will produce **state corruption** — the flight recorder will contain conflicting information. This is why remote state with locking exists (Episode 7).

---

## 🔄 Drift: When Reality Departs from the Plan

A fascinating and troubling phenomenon occurs when someone modifies infrastructure *outside* of Terraform — directly in the AWS console, via CLI, via another tool. The cloud changes. The state file doesn't. Reality diverges from the record.

This is called **drift**.

```bash
# Detect drift: refresh state from cloud reality
terraform refresh     # Updates state to match cloud reality
terraform plan        # Will now show drift as proposed changes

# Or use plan with refresh (same effect, combined)
terraform plan -refresh=true
```

```bash
# Example: Someone manually changed the instance type in the AWS console
# Terraform plan will detect this:

  # aws_instance.lunar_module will be updated in-place
  ~ resource "aws_instance" "lunar_module" {
        id            = "i-0a1b2c3d4e5f67890"
      ~ instance_type = "t3.small" -> "t3.micro"   # Drift detected! Cloud has t3.small, code says t3.micro
    }
```

Terraform will propose reverting the change — because the code is the source of truth. If the manual change was intentional and correct, update the code to match. If it was accidental, apply Terraform to restore the intended state.

The state file is not just memory. It is the mission's **single source of truth**. Drift is not a mystery to be accepted. It is a discrepancy to be resolved.

---

## 🌟 The First Apply: A Moment Worth Noting

There is something genuinely remarkable about the first `terraform apply` on a new project.

You have written text files. Plain text. HCL syntax. And now, in the span of seconds to minutes, real infrastructure springs into existence in a data centre thousands of miles away. Servers. Networks. Databases. Load balancers. All conjured from declarations.

In the four billion years this planet has existed, no organism has ever done this before. No creature has ever looked at text and said: *"Make that real."* And then watched it happen.

We have built something extraordinary. And we have barely started.

---

*🌕 Next episode: **The Modular Rocket** — Terraform Modules. Because the Saturn V was not built as one piece, and neither should your infrastructure.*
