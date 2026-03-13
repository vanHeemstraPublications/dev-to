---
title: "To The Moon 🌕 Ep.9 — Mid-Course Corrections (terraform import & Drift)"
series: To The Moon — Terraform by HashiCorp
part: 9
tags: terraform, import, drift, iac
---

> *"On the journey to the Moon, the spacecraft's trajectory was never perfect. Gravity, solar wind, tiny imprecisions in the launch — all conspired to push the vehicle off course. Mission Control made over a dozen mid-course corrections on every flight. Not because the original plan was wrong. Because reality has a habit of drifting from plans."*

---

# 🌕 Episode 9 — Mid-Course Corrections

Every infrastructure team eventually encounters the same discovery.

There are resources in the cloud that Terraform does not know about. They were created before Terraform was adopted. They were created by a colleague who was in a hurry. They were created by an automated process that didn't write state. They simply *exist* — running, billing, and serving traffic — while Terraform looks away, unaware.

Bringing these orphaned resources under Terraform's management is called **importing**. And it is, in the parlance of spaceflight, a mid-course correction.

---

## 🛸 terraform import: Adopting Orphaned Infrastructure

`terraform import` takes a real cloud resource and brings it into Terraform state, associated with a specific resource block in your configuration.

**The process has two steps:**

### Step 1: Write the resource configuration
First, write the Terraform resource block that will represent the existing resource:

```hcl
# main.tf — Add the resource block for the existing infrastructure
resource "aws_instance" "orphaned_lunar_module" {
  # You don't need to know all attributes yet —
  # Terraform will fill them in after import.
  # But you MUST have the resource block declared.
  ami           = "ami-0c55b159cbfafe1f0"   # You'll need to match existing values
  instance_type = "t3.micro"
}
```

### Step 2: Run terraform import
```bash
# Import the existing resource into state
# Syntax: terraform import <resource_address> <cloud_resource_id>
terraform import aws_instance.orphaned_lunar_module i-0a1b2c3d4e5f67890

# After import, run plan to see what configuration mismatches exist
terraform plan
# This will show any differences between your resource block and the actual resource
# Update your resource block to match, then re-run plan until it shows no changes
```

---

## 🆕 The import Block: Declarative Importing (Terraform 1.5+)

Terraform 1.5 introduced **declarative imports** — you declare what to import in your code, rather than running an imperative CLI command:

```hcl
# import.tf — Declarative import blocks

import {
  id = "i-0a1b2c3d4e5f67890"
  to = aws_instance.orphaned_lunar_module
}

import {
  id = "vpc-0a1b2c3d4e5f"
  to = aws_vpc.legacy_launch_pad
}
```

```bash
# Terraform 1.5+: Generate configuration automatically from existing resource
terraform plan -generate-config-out=generated.tf

# This creates a generated.tf with the full resource block, populated from the real resource
# Review it, adjust it, and move the blocks to your main configuration files
```

---

## 📊 The SIPOC of Episode 9

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| AWS cloud (live) | Existing resource ID | Provider reads all resource attributes from cloud | Resource attribute map | State file writer |
| Resource block in `.tf` | Declared resource address | Terraform maps real resource to code | State entry linking ID to code address | Subsequent plan/apply operations |
| `terraform plan` (post-import) | State + config | Diff between imported state and declared config | List of required configuration updates | Engineer reviewing and fixing config to match reality |

---

*🌕 Next episode: **Docking Procedure** — Dependencies and `depends_on`. Because in space, sequence is survival.*

---
---
title: "To The Moon 🌕 Ep.10 — Docking Procedure (Dependencies & depends_on)"
series: To The Moon — Terraform by HashiCorp
part: 10
tags: terraform, dependencies, iac, advanced
---

> *"The docking of Apollo with the Lunar Module required absolute sequencing. The Command Module had to be in position before the docking adapter could engage. The adapter had to engage before the hatches could open. The hatches had to open before the astronauts could transfer. No step could be skipped. No step could be reversed."*

---

# 🌕 Episode 10 — Docking Procedure

Terraform, as we have established, builds a **dependency graph**. It examines every reference between resources and constructs an ordered execution plan.

Most of the time, this happens automatically. When `aws_instance.lunar_module` references `aws_subnet.runway.id`, Terraform knows the subnet must exist first. The reference *is* the dependency declaration.

But sometimes, dependencies exist that Terraform cannot see through references alone. And for those, we have `depends_on`.

---

## 🔗 Implicit Dependencies: The Automatic Docking

When you reference one resource's attribute in another, Terraform automatically creates a dependency:

```hcl
resource "aws_vpc" "launch_pad" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "runway" {
  vpc_id     = aws_vpc.launch_pad.id   # <- This reference IS the dependency
  cidr_block = "10.0.1.0/24"
}
# Terraform knows: launch_pad must exist before runway
```

---

## 🤝 explicit `depends_on`: The Manual Docking Procedure

When a dependency exists but no reference is visible in the code, you declare it explicitly:

```hcl
# The IAM role must be fully propagated before the instance can use it
# But the instance doesn't reference the role directly — it uses the instance profile
resource "aws_iam_role" "mission_role" {
  name               = "apollo-mission-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "mission_policy" {
  role       = aws_iam_role.mission_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "mission_profile" {
  name = "apollo-mission-profile"
  role = aws_iam_role.mission_role.name
}

resource "aws_instance" "lunar_module" {
  ami                  = "ami-0c55b159cbfafe1f0"
  instance_type        = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.mission_profile.name

  # IAM propagation delay — the policy attachment must complete before the instance launches
  # Terraform can't see this dependency from the code references alone
  depends_on = [
    aws_iam_role_policy_attachment.mission_policy
  ]
}
```

---

## 🔀 Resource Replacement Order: `create_before_destroy`

By default, Terraform destroys a resource before creating its replacement. This causes downtime. The `create_before_destroy` lifecycle argument reverses this:

```hcl
resource "aws_instance" "lunar_module" {
  ami           = var.ami_id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true
    # New instance created, traffic shifts, then old instance destroyed
    # Zero-downtime replacement — like docking the new module before releasing the old one
  }
}
```

---

## 📊 The SIPOC of Episode 10

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| Resource attribute references | Cross-resource `resource_type.name.attribute` references | Graph edge construction (implicit) | Directed dependency graph | Terraform execution engine |
| `depends_on` blocks | Explicit dependency list | Graph edge construction (explicit) | Additional edges in dependency graph | Terraform execution engine |
| Dependency graph | All edges (implicit + explicit) | Topological sort | Ordered execution sequence | Terraform apply parallelism engine |
| `lifecycle` block | `create_before_destroy`, `prevent_destroy` | Modified resource replacement behaviour | Changed resource lifecycle events | Terraform apply engine |

---

*🌕 Next episode: **Life Support Systems** — `count`, `for_each`, and dynamic blocks. For when one lunar module is simply not enough.*

---
---
title: "To The Moon 🌕 Ep.11 — Life Support Systems (count, for_each & Dynamic Blocks)"
series: To The Moon — Terraform by HashiCorp
part: 11
tags: terraform, foreach, count, advanced
---

> *"The life support systems of the Apollo spacecraft did not exist as a single unit. They were arrays — redundant, parallel systems, each capable of taking over from the others. Oxygen management. CO2 scrubbing. Thermal control. Each duplicated, each addressable individually, each part of a coordinated ensemble. One failure would not end the mission."*

---

# 🌕 Episode 11 — Life Support Systems

A single lunar module is magnificent. But missions of real scale require infrastructure that scales with requirements. You do not write one resource block for each server in a hundred-server cluster. You do not write one security group rule for each of thirty-seven allowed IP ranges.

You use iteration.

Terraform provides two iteration mechanisms — `count` and `for_each` — plus `dynamic` blocks for nested configuration. Together they allow you to build armies of resources from a single declaration.

---

## 🔢 count: The Simple Multiplier

`count` creates N copies of a resource. It is the bluntest of the tools — powerful for simple cases, limited for complex ones.

```hcl
variable "crew_count" {
  type    = number
  default = 3
}

resource "aws_instance" "crew_member" {
  count         = var.crew_count   # Creates 3 instances
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  tags = {
    Name      = "apollo-crew-${count.index + 1}"   # crew-1, crew-2, crew-3
    CrewSlot  = count.index   # 0, 1, 2
  }
}

# Reference a specific instance by index
output "commander_ip" {
  value = aws_instance.crew_member[0].public_ip   # First instance
}

# Reference all instances
output "all_crew_ips" {
  value = aws_instance.crew_member[*].public_ip   # All IPs as a list
}
```

**The limitation of count**: resources are identified by *index*. Remove the first item from your list and every subsequent resource is renumbered — Terraform will destroy and recreate them all. This is the equivalent of renaming every crew member when one person leaves.

---

## 🔑 for_each: The Named Ensemble

`for_each` creates one resource per item in a map or set, addressed by **key**. Removing one item does not affect the others.

```hcl
variable "crew_manifest" {
  description = "Crew members and their roles"
  type = map(object({
    role          = string
    instance_type = string
    subnet_key    = string
  }))
  default = {
    "armstrong" = { role = "commander",    instance_type = "t3.small",  subnet_key = "public-1" }
    "aldrin"    = { role = "lunar-pilot",  instance_type = "t3.small",  subnet_key = "public-2" }
    "collins"   = { role = "cmd-module",   instance_type = "t3.micro",  subnet_key = "public-3" }
  }
}

resource "aws_instance" "crew_member" {
  for_each      = var.crew_manifest
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = each.value.instance_type
  subnet_id     = aws_subnet.public[each.value.subnet_key].id

  tags = {
    Name      = "apollo-${each.key}"
    Role      = each.value.role
    CrewMember = each.key
  }
}

# Resources are addressed by key:
# aws_instance.crew_member["armstrong"]
# aws_instance.crew_member["aldrin"]
# aws_instance.crew_member["collins"]

output "crew_ips" {
  value = { for k, v in aws_instance.crew_member : k => v.public_ip }
}
```

Remove `"collins"` from the map and only Collins's instance is destroyed. Armstrong and Aldrin continue orbiting, undisturbed.

---

## 🔁 Dynamic Blocks: The Repeated Configuration

Some resources have nested blocks that need to repeat. Security group rules. EBS volumes. Tags as blocks. `dynamic` generates these from collections:

```hcl
variable "mission_access_rules" {
  description = "Approved communication channels for the mission"
  type = list(object({
    description = string
    port        = number
    protocol    = string
    cidr        = string
  }))
  default = [
    { description = "HTTPS from Earth",  port = 443, protocol = "tcp", cidr = "0.0.0.0/0"  },
    { description = "SSH from Houston",  port = 22,  protocol = "tcp", cidr = "10.0.0.0/8" },
    { description = "Mission telemetry", port = 8080, protocol = "tcp", cidr = "10.0.0.0/8" },
  ]
}

resource "aws_security_group" "mission_comms" {
  name   = "apollo-mission-comms"
  vpc_id = aws_vpc.launch_pad.id

  # Dynamic block: generates one ingress rule per item in the list
  dynamic "ingress" {
    for_each = var.mission_access_rules
    content {
      description = ingress.value.description
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = ingress.value.protocol
      cidr_blocks = [ingress.value.cidr]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Unrestricted outbound — astronauts can call home"
  }
}
```

Add a rule to the variable. The security group gains a new ingress rule on the next apply. Remove a rule. It disappears. No manual editing of individual rule blocks.

---

## 📊 The SIPOC of Episode 11

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| `count` meta-argument | Integer N | Terraform creates N resource instances indexed 0 to N-1 | N resource instances addressed by index | Other resources, outputs using `[index]` notation |
| `for_each` meta-argument | map or set of keys | Terraform creates one instance per key | Named resource instances addressed by key | Other resources, outputs using `[key]` notation |
| `dynamic` block | List or map + `for_each` | Repeated nested block generation | Multiple identical nested blocks in resource | Cloud provider API (security rules, EBS volumes, etc.) |
| `for` expressions | Collection + transformation | Functional iteration over lists/maps | New list or map derived from input | Resource arguments, outputs, locals |

---

*🌕 Next episode: **The Landing** — CI/CD with Terraform. Because the most dangerous part of any mission is landing.*
