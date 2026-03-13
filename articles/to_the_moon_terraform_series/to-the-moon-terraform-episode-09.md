---
title: "To The Moon Terraform Ep.9"
part: 9
published: false
description: "Episode 9 — Mid-Course Corrections"
tags: [terraform, import, drift, iac]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-09.webp"
canonical_url: ""
organization: "the-software-s-journey"
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
