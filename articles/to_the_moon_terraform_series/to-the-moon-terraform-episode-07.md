---
title: "To The Moon Terraform Ep.7"
part: 7
published: false
description: "Episode 7 — Mission Control Systems"
tags: [terraform, modules, iac, reusability]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-07.webp"
canonical_url: ""
organization: "the-software-s-journey"
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
