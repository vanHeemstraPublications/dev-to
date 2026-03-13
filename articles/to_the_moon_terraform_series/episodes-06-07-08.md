---
title: "To The Moon 🌕 Ep.6 — The Modular Rocket (Terraform Modules)"
series: To The Moon — Terraform by HashiCorp
part: 6
tags: terraform, modules, iac, reusability
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

---
---
title: "To The Moon 🌕 Ep.7 — Mission Control Systems (Remote State & Backends)"
series: To The Moon — Terraform by HashiCorp
part: 7
tags: terraform, state, remote, collaboration
---

> *"The Apollo missions were not controlled from the rocket. They were not controlled from the astronauts' laptops. They were controlled from a building in Houston — a centralised, redundant, always-available facility where the state of every system was known, recorded, and accessible to the entire team. This was not a convenience. It was a necessity."*

---

# 🌕 Episode 7 — Mission Control Systems

Picture, if you will, three engineers.

Each has their own laptop. Each has their own local `terraform.tfstate` file. Each applies changes to the same AWS account — occasionally simultaneously, occasionally while the others are unaware.

The state files diverge. Resources appear in two people's state. Resources appear in neither. An apply destroys infrastructure that a second engineer created but whose creation was not recorded in the first engineer's state.

This is the `local` backend. And it is, for team-based work, an unmitigated disaster.

**The solution is Remote State** — and it is not optional for any serious mission.

---

## 🏛️ Remote State: The Houston Flight Controller

A backend is where Terraform stores state. The default is `local` — a file on your disk. For team environments, you need a **remote backend** — a central, shared, locked location.

The most common combination for AWS is **S3 + DynamoDB**:
- **S3**: Stores the state file (durable, versioned, encrypted)
- **DynamoDB**: Provides state locking (prevents simultaneous applies)

```hcl
# terraform.tf — Configure the Remote Backend (Mission Control)

terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    # Where the state file lives
    bucket = "apollo-terraform-state"
    key    = "missions/apollo-terraform/production/terraform.tfstate"
    region = "us-east-1"

    # Encryption at rest
    encrypt = true

    # DynamoDB table for state locking
    dynamodb_table = "apollo-terraform-state-lock"

    # KMS key for additional encryption (optional but recommended)
    kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.31"
    }
  }
}
```

The S3 bucket and DynamoDB table must be created *before* you configure this backend. This is the bootstrapping problem — and it is solved with a one-time setup:

```hcl
# bootstrap/main.tf — Create the state infrastructure first
# Apply this ONCE before configuring the backend above

resource "aws_s3_bucket" "terraform_state" {
  bucket = "apollo-terraform-state"
  lifecycle {
    prevent_destroy = true   # NEVER accidentally delete the state store
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"   # Every state version preserved — time travel for your state
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name         = "apollo-terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  lifecycle {
    prevent_destroy = true
  }
}
```

---

## 🔐 State Locking: The Flight Director Mutex

When engineer A runs `terraform apply`, Terraform writes a **lock record** to DynamoDB:

```json
{
  "LockID": "apollo-terraform-state/missions/apollo/production/terraform.tfstate",
  "Info": "{\"ID\":\"8a7b6c5d\",\"Operation\":\"OperationTypeApply\",\"Who\":\"armstrong@houston.nasa.gov\",\"Created\":\"2026-03-12T09:00:00Z\"}"
}
```

If engineer B tries to apply at the same time, Terraform sees the lock and refuses:

```
Error: Error locking state: Error acquiring the state lock: ConditionalCheckFailedException
Lock Info:
  ID:        8a7b6c5d
  Path:      apollo-terraform-state/missions/apollo/production/terraform.tfstate
  Operation: OperationTypeApply
  Who:       armstrong@houston.nasa.gov
  Created:   2026-03-12 09:00:00 +0000 UTC
  Info:
```

Only one mission control can be in command at a time. The Flight Director has the floor.

---

## 🔗 Remote State as a Data Source

Remote state enables something even more powerful than sharing: **referencing another project's state**. If your network infrastructure is managed by one team and your compute by another, the compute team can read the network team's outputs:

```hcl
# In the compute team's configuration:

data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "apollo-terraform-state"
    key    = "missions/apollo-terraform/production/network/terraform.tfstate"
    region = "us-east-1"
  }
}

# Use the network team's VPC outputs:
resource "aws_instance" "lunar_module" {
  ami       = data.aws_ami.lunar.id
  subnet_id = data.terraform_remote_state.network.outputs.public_subnet_ids[0]
}
```

The teams remain independent. The states remain separate. The interfaces are explicit.

---

## 📊 The SIPOC of Episode 7

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| S3 bucket | Serialised state JSON | S3 PutObject / GetObject | Stored/retrieved state file | Terraform state engine |
| DynamoDB table | Lock record write request | Conditional write (fails if lock exists) | Lock acquired or error | Engineer attempting apply |
| Remote state data source | `data.terraform_remote_state` block | S3 read of another project's state | Referenced outputs from other project | Current project's resource configurations |
| AWS IAM | Credentials with S3 + DynamoDB permissions | Authentication + authorisation check | Authorised API access | Backend S3/DynamoDB operations |

---

*🌕 Next episode: **The Crew Manifest** — Workspaces & Environments. Because the Moon doesn't care if you're in staging.*

---
---
title: "To The Moon 🌕 Ep.8 — The Crew Manifest (Workspaces & Environments)"
series: To The Moon — Terraform by HashiCorp
part: 8
tags: terraform, workspaces, environments, iac
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
