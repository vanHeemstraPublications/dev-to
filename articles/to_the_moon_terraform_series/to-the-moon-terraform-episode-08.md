---
title: "To The Moon Terraform Ep.8"
part: 8
published: false
description: "Episode 8 — The Crew Manifest"
tags: [terraform, modules, iac, reusability]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-08.webp"
canonical_url: ""
organization: "the-software-s-journey"
---

> *"NASA did not have one test facility and one launch pad. They had test ranges, simulation environments, and the actual launchpad at Cape Canaveral — all running the same designs, but with different stakes. A mistake in a simulation is a lesson. A mistake on the launchpad is a tragedy."*

---

# 🌕 Episode 8 — The Crew Manifest

There is a rule so fundamental to engineering that it applies equally to rocket science and cloud infrastructure:

**Never test in production.**

Yet this rule is violated, constantly, by teams who have not yet discovered a clean way to manage multiple environments with the same Terraform code. They have `dev-main.tf` and `prod-main.tf`. They copy. They paste. They diverge. And eventually — inevitably — they deploy the dev configuration to production because the files looked similar enough.

Terraform offers two primary mechanisms for environment management. We shall meet them both, assess their strengths, and know when to use each.

---

## 🔄 Workspaces: Multiple State Files, One Configuration

A **Workspace** is simply an isolated state file within the same backend. Every Terraform environment starts in the `default` workspace. You can create additional workspaces and switch between them.

```bash
# Current workspace
terraform workspace show
# default

# Create a new workspace
terraform workspace new staging
# Created and switched to workspace "staging"!

# Create production workspace
terraform workspace new production

# List all workspaces
terraform workspace list
#   default
#   production
# * staging     ← (asterisk = current)

# Switch workspaces
terraform workspace select production

# Delete a workspace (must be empty first)
terraform workspace delete staging
```

Within your configuration, you access the current workspace name:

```hcl
# main.tf — Workspace-aware configuration

locals {
  # Different instance types per environment
  instance_type = {
    default    = "t3.micro"
    staging    = "t3.small"
    production = "t3.large"
  }

  # Different replica counts per environment
  replica_count = {
    default    = 1
    staging    = 1
    production = 3
  }
}

resource "aws_instance" "lunar_module" {
  instance_type = local.instance_type[terraform.workspace]
  count         = local.replica_count[terraform.workspace]

  tags = {
    Environment = terraform.workspace
    Name        = "apollo-lunar-module-${terraform.workspace}"
  }
}
```

State is isolated per workspace. Applying in `staging` does not touch production state. Applying in `production` does not touch staging state.

---

## 📁 Directory-Per-Environment: The Alternative Pattern

For teams with significant environment differences — different provider configurations, different backend configurations, different module versions — the **directory-per-environment** pattern is often cleaner:

```
missions/
├── environments/
│   ├── simulation/
│   │   ├── terraform.tf      ← Backend key: environments/simulation/terraform.tfstate
│   │   ├── main.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── terraform.tf      ← Backend key: environments/staging/terraform.tfstate
│   │   ├── main.tf
│   │   └── terraform.tfvars
│   └── production/
│       ├── terraform.tf      ← Backend key: environments/production/terraform.tfstate
│       ├── main.tf
│       └── terraform.tfvars
└── modules/
    ├── network/
    ├── compute/
    └── security/
```

Each environment calls the same modules with different variable values:

```hcl
# environments/production/main.tf

module "network" {
  source      = "../../modules/network"
  mission_name = "apollo-terraform"
  environment  = "production"
  vpc_cidr     = "10.1.0.0/16"    # Different CIDR from staging (no overlap)
}

module "compute" {
  source        = "../../modules/compute"
  mission_name  = "apollo-terraform"
  environment   = "production"
  instance_type = "t3.large"
  replica_count = 3
  vpc_id        = module.network.vpc_id
}
```

```hcl
# environments/staging/main.tf — Identical structure, different values

module "network" {
  source       = "../../modules/network"
  mission_name = "apollo-terraform"
  environment  = "staging"
  vpc_cidr     = "10.2.0.0/16"
}

module "compute" {
  source        = "../../modules/compute"
  mission_name  = "apollo-terraform"
  environment   = "staging"
  instance_type = "t3.micro"
  replica_count = 1
  vpc_id        = module.network.vpc_id
}
```

---

## 📊 The SIPOC of Episode 8

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| `terraform workspace` CLI | Workspace name | Creates isolated state namespace in backend | Separate state file per workspace | Subsequent `terraform plan` / `apply` in that workspace |
| `terraform.workspace` value | Current workspace name | Injected into HCL evaluation context | Environment-specific config via map lookups | Resource configurations, locals, conditionals |
| Environment-specific `.tfvars` | Different variable values per environment | Variable resolution at plan time | Environment-appropriate resource configuration | All resource blocks |
| Module source | Same module, called from each environment | Module executes with environment-specific inputs | Different real resources per environment | State file, outputs |

---

*🌕 Next episode: **Mid-Course Corrections** — `terraform import` and drift detection. Because sometimes reality gets ahead of your Terraform code.*

