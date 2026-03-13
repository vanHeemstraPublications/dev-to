---
title: "To The Moon Terraform Ep.11"
part: 11
published: false
description: "Episode 11 — Life Support Systems"
tags: [terraform, import, drift, iac]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-11.webp"
canonical_url: ""
organization: "the-software-s-journey"
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
