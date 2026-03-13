---
title: "To The Moon Terraform Ep.10"
part: 10
published: false
description: "Episode 10 — Docking Procedure"
tags: [terraform, import, drift, iac]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-10.webp"
canonical_url: ""
organization: "the-software-s-journey"
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