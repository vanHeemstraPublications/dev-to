---
title: "To The Moon 🌕 Ep.12 — The Landing (CI/CD with Terraform)"
series: To The Moon — Terraform by HashiCorp
part: 12
tags: terraform, cicd, automation, devops
---

> *"The lunar landing was not improvised. Every step of the descent had been rehearsed hundreds of times in simulators. The software that guided the Eagle to the Moon's surface had been tested against every failure scenario imaginable. When Neil Armstrong finally took manual control in the final seconds — avoiding a boulder field the computers hadn't anticipated — he was confident because every other aspect of the landing had been automated with absolute precision."*

---

# 🌕 Episode 12 — The Landing

The most dangerous assumption in infrastructure engineering is this: *"I'll review the plan manually each time."*

You will. Until you won't. Until it's Friday afternoon. Until there are three pull requests in flight simultaneously. Until someone approves the plan without noticing the `-/+` on the database.

**Automation is not the enemy of careful thinking. It is the mechanism that enforces it every single time.**

CI/CD for Terraform means: every change to infrastructure is proposed via pull request, planned automatically, reviewed by humans, and applied only upon explicit approval. The manual steps are not removed — they are guaranteed to happen in the right sequence.

---

## 🔁 The CI/CD Pipeline for Terraform

The typical pipeline has four stages:

```
PR Opened → Plan → Review → Merge → Apply
```

```yaml
# .github/workflows/terraform.yml — GitHub Actions CI/CD Pipeline

name: "Terraform Mission Control"

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  TF_VERSION: "1.6.0"
  AWS_REGION: "us-east-1"
  WORKING_DIR: "./environments/production"

jobs:

  # ─── STAGE 1: VALIDATE ────────────────────────────────────────────────────
  validate:
    name: "Pre-Flight Validation"
    runs-on: ubuntu-latest

    steps:
      - name: "Checkout Mission Code"
        uses: actions/checkout@v4

      - name: "Setup Terraform"
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: "Configure AWS Credentials (OIDC — no stored secrets)"
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/terraform-ci-role
          aws-region: ${{ env.AWS_REGION }}

      - name: "terraform init"
        run: terraform init -input=false
        working-directory: ${{ env.WORKING_DIR }}

      - name: "terraform validate"
        run: terraform validate
        working-directory: ${{ env.WORKING_DIR }}

      - name: "terraform fmt check"
        run: terraform fmt -check -recursive
        working-directory: ${{ env.WORKING_DIR }}

  # ─── STAGE 2: PLAN (on PR) ────────────────────────────────────────────────
  plan:
    name: "Mission Plan"
    runs-on: ubuntu-latest
    needs: validate
    if: github.event_name == 'pull_request'

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/terraform-ci-role
          aws-region: ${{ env.AWS_REGION }}

      - name: "terraform init"
        run: terraform init -input=false
        working-directory: ${{ env.WORKING_DIR }}

      - name: "terraform plan"
        id: plan
        run: |
          terraform plan -no-color -input=false -out=mission.tfplan 2>&1 | tee plan.txt
          echo "exitcode=${PIPESTATUS[0]}" >> $GITHUB_OUTPUT
        working-directory: ${{ env.WORKING_DIR }}

      - name: "Post Plan to Pull Request"
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('${{ env.WORKING_DIR }}/plan.txt', 'utf8');
            const planLines = plan.split('\n').slice(-50).join('\n');  // Last 50 lines
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🌕 Terraform Mission Plan\n\`\`\`\n${planLines}\n\`\`\``
            });

  # ─── STAGE 3: APPLY (on merge to main) ────────────────────────────────────
  apply:
    name: "Launch Sequence"
    runs-on: ubuntu-latest
    needs: validate
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: production   # GitHub Environment with required reviewers

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/terraform-apply-role
          aws-region: ${{ env.AWS_REGION }}

      - name: "terraform init"
        run: terraform init -input=false
        working-directory: ${{ env.WORKING_DIR }}

      - name: "terraform apply"
        run: terraform apply -auto-approve -input=false
        working-directory: ${{ env.WORKING_DIR }}
```

---

## 🔐 OIDC: No Stored AWS Credentials

Notice the credential configuration: `role-to-assume`. This uses **OpenID Connect (OIDC)** — GitHub Actions obtains a temporary token from AWS IAM directly, with no long-lived access keys stored as secrets.

```hcl
# iam.tf — Create the CI/CD role that GitHub Actions assumes

data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "terraform_ci" {
  name = "terraform-ci-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = data.aws_iam_openid_connect_provider.github.arn }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          # Only your repo can assume this role
          "token.actions.githubusercontent.com:sub" = "repo:your-org/mission-apollo:*"
        }
      }
    }]
  })
}
```

No secrets. No rotation. No risk of key leakage. The role exists. GitHub proves its identity. AWS grants temporary access. The mission proceeds.

---

## 📊 The SIPOC of Episode 12

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| Developer | Pull request with `.tf` changes | GitHub Actions triggers pipeline | Automated validate + plan | Reviewer (sees plan in PR comment) |
| Reviewer | Plan output in PR comment | Human review → Approve / Request Changes | PR approval or rejection | Merge gate |
| Merged PR | `main` branch push event | Apply job triggered (with environment protection) | `terraform apply` execution | Production infrastructure |
| OIDC provider | GitHub Actions identity token | AWS IAM validates token, issues temp credentials | Temporary AWS credentials | Terraform provider authentication |

---

*🌕 Next episode: **Moon Surface Operations** — Provisioners and local-exec. For when the cloud is not quite enough.*

---
---
title: "To The Moon 🌕 Ep.13 — Moon Surface Operations (Provisioners & local-exec)"
series: To The Moon — Terraform by HashiCorp
part: 13
tags: terraform, provisioners, localexec, advanced
---

> *"Arriving on the Moon is not the end of the mission. It is, in many ways, the beginning. The astronauts must exit the vehicle, set up equipment, collect samples, deploy experiments. The landing craft brought them here. But the surface operations require additional tools — tools that the rocket itself could not perform."*

---

# 🌕 Episode 13 — Moon Surface Operations

Terraform's primary purpose is **infrastructure provisioning**: creating, modifying, and destroying cloud resources. It is extraordinarily good at this.

But occasionally — only occasionally — you need to do something *after* the infrastructure exists. Run a bootstrap script. Call an external API. Copy a file. Register a resource with an external system that has no Terraform provider.

For these moments, Terraform provides **provisioners**. They are powerful. They are necessary in rare circumstances. And they are, I must caution you, the tool that the experienced Terraform engineer uses *last* — after all other options have been exhausted.

---

## ⚠️ The Provisioner Warning Label

HashiCorp themselves describe provisioners as a *"last resort"*. This is not modesty. It reflects a genuine design philosophy.

Provisioners:
- Break the declarative model (they are imperative — they *do* things)
- Cannot be planned (Terraform cannot preview their effects)
- Are not tracked in state (Terraform doesn't know if they succeeded or what they did)
- Are difficult to retry cleanly

If you can use a `user_data` script on an EC2 instance, use that. If you can use an `aws_ssm_association` for configuration management, use that. If you can find a Terraform provider that wraps the API you need, use that.

If none of these exist: provisioners.

---

## 🔧 local-exec: Running Commands on Your Machine

`local-exec` runs a command on the machine running Terraform — your laptop, or your CI/CD runner:

```hcl
resource "aws_instance" "lunar_module" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  # After the instance is created, register it with our mission inventory API
  provisioner "local-exec" {
    command = <<-EOT
      curl -X POST https://mission-inventory.apollo.internal/register \
        -H "Content-Type: application/json" \
        -d '{"instance_id": "${self.id}", "ip": "${self.public_ip}", "role": "lunar-module"}'
    EOT

    # Run this on destroy instead of create
    # when = destroy
  }

  # Run a script to add to monitoring
  provisioner "local-exec" {
    command     = "python3 scripts/register_monitoring.py --host ${self.public_ip} --name ${self.tags.Name}"
    interpreter = ["python3", "-c"]
    working_dir = path.module
  }
}
```

---

## 📡 remote-exec: Running Commands on the New Resource

`remote-exec` connects to the newly created resource (via SSH or WinRM) and runs commands on it:

```hcl
resource "aws_instance" "lunar_module" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  key_name      = aws_key_pair.mission_key.key_name

  # SSH connection details
  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = tls_private_key.mission_key.private_key_pem
    host        = self.public_ip
  }

  # Bootstrap the lunar module's software after launch
  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo yum install -y docker",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "sudo usermod -a -G docker ec2-user",
      "docker pull mission-control/lunar-module-app:latest",
      "docker run -d -p 8080:8080 mission-control/lunar-module-app:latest",
    ]
  }
}
```

---

## 📄 file: Copying Files to a New Resource

```hcl
resource "aws_instance" "lunar_module" {
  # ... instance config ...

  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = tls_private_key.mission_key.private_key_pem
    host        = self.public_ip
  }

  # Copy a configuration file to the new server
  provisioner "file" {
    source      = "${path.module}/configs/mission-parameters.json"
    destination = "/etc/mission/parameters.json"
  }
}
```

---

## 📊 The SIPOC of Episode 13

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| Terraform apply engine | `creation_complete` event for resource | Triggers provisioner execution | Provisioner runs (local or remote) | External system or remote host |
| `local-exec` provisioner | Shell command string + interpreter | Shell executes command on CI/CD runner / local machine | Exit code (0 = success, non-0 = failure) | Terraform — marks resource as tainted on failure |
| `remote-exec` provisioner | SSH/WinRM commands + connection config | SSH connection to resource, command execution | Exit codes on remote host | Terraform — marks resource as tainted on failure |
| `file` provisioner | Local file path + remote destination + connection | SCP/SFTP transfer to remote host | File present at destination | Remote server filesystem |

---

*🌕 Final episode: **Return to Earth** — `terraform destroy` and the end of the mission. Every astronaut must come home.*

---
---
title: "To The Moon 🌕 Ep.14 — Return to Earth (terraform destroy & Mission Completion)"
series: To The Moon — Terraform by HashiCorp
part: 14
tags: terraform, destroy, iac, conclusion
---

> *"On July 24, 1969, at 12:50pm EDT, the Columbia capsule splashed down in the Pacific Ocean. The mission was complete. The infrastructure — the Saturn V, the service module, the lunar module — had served its purpose and would never be used again. Some of it burned up in the atmosphere. Some of it rests, still, on the lunar surface. The mission was finite. The achievement was permanent."*

---

# 🌕 Episode 14 — Return to Earth

There is a kind of poetry in the fact that the same tool that creates your infrastructure can unmake it.

`terraform destroy`. Two words. Nine syllables. And in its execution: the orderly, dignified, complete removal of everything you built.

This is not failure. This is the conclusion of the mission.

---

## 💥 terraform destroy: The Controlled Descent

```bash
# Full destroy — removes all resources in state
terraform destroy

# Terraform will show you the plan for destruction:
# Plan: 0 to add, 0 to change, 5 to destroy.

# Destroy with auto-approval (CI/CD cleanup jobs)
terraform destroy -auto-approve

# Destroy a single resource (surgical)
terraform destroy -target=aws_instance.lunar_module

# Preview what would be destroyed without destroying it
terraform plan -destroy
```

The destroy operation runs in **reverse dependency order**. The instance is destroyed before the security group. The security group is destroyed before the VPC. The internet gateway is detached before the VPC is removed.

Terraform knows the sequence. It built the same graph in reverse.

---

## 🔬 The Anatomy of a Destroy

```bash
$ terraform destroy

aws_instance.lunar_module: Destroying... [id=i-0a1b2c3d4e5f67890]
aws_instance.lunar_module: Still destroying... [10s elapsed]
aws_instance.lunar_module: Destruction complete after 32s

aws_security_group.crew_capsule: Destroying... [id=sg-0a1b2c3d4e5f]
aws_security_group.crew_capsule: Destruction complete after 2s

aws_subnet.runway: Destroying... [id=subnet-0a1b2c3d]
aws_subnet.runway: Destruction complete after 1s

aws_internet_gateway.comms_tower: Destroying... [id=igw-0a1b2c3d]
aws_internet_gateway.comms_tower: Destruction complete after 1s

aws_vpc.launch_pad: Destroying... [id=vpc-0a1b2c3d4e5f67890]
aws_vpc.launch_pad: Destruction complete after 1s

Destroy complete! Resources: 5 destroyed.
```

Nothing remains. No billing. No orphaned resources. No forgotten security groups charging you five cents a month for seven years. A clean slate.

This is the extraordinary gift of Terraform: what it creates, it can also unmake. Completely. Verifiably. Without manual clicking through console pages hunting for resources you might have forgotten.

---

## 🛡️ Protecting Critical Resources from Accidental Destroy

Not everything should be destroyable by `terraform destroy`. Databases. State buckets. Production VPCs. These get the `prevent_destroy` lifecycle guard:

```hcl
resource "aws_db_instance" "mission_database" {
  identifier     = "apollo-mission-db"
  instance_class = "db.t3.micro"
  engine         = "postgres"

  lifecycle {
    prevent_destroy = true
  }
}

# terraform destroy will now error:
# Error: Instance cannot be destroyed
# Resource aws_db_instance.mission_database has lifecycle.prevent_destroy
# set, but the plan calls for this resource to be destroyed.
```

The resource can still be destroyed — but only by removing the `prevent_destroy = true` line, committing that change to Git, and applying it. This creates an audit trail. Someone made a deliberate decision to allow destruction. And that decision is recorded.

---

## 📊 The SIPOC of Episode 14

| 🔵 Supplier | 🟡 Input | 🟢 Process | 🟠 Output | 🔴 Consumer |
|---|---|---|---|---|
| Terraform state | All managed resources | Generate reverse-dependency ordered destroy plan | Ordered list of resources to destroy | Human reviewer (confirm) |
| Human reviewer | Destroy plan | Confirm or abort | GO / NO-GO decision | Terraform destroy execution |
| Cloud provider API | Destroy requests for each resource | Resource deletion in reverse dependency order | Deleted resources, freed capacity | Billing system (costs stop) |
| State writer | Completion of each resource deletion | Remove resource from state file | Empty (or partially empty) state file | Future terraform commands (empty state = no resources) |

---

## 🌟 The Complete Mission: Everything We Learned

Over fourteen episodes, we planned and executed a complete Moon mission — and in doing so, learned the complete arc of Terraform:

| Episode | Mission Phase | Terraform Concept |
|---|---|---|
| 1 | The Audacity | What is Terraform? Declarative IaC. |
| 2 | Mission Architecture | Providers and Resources |
| 3 | The Blueprint | Variables, Outputs, and Locals |
| 4 | Pre-Flight Checklist | `terraform plan` in depth |
| 5 | Launch Sequence | `terraform apply` and the State File |
| 6 | The Modular Rocket | Terraform Modules |
| 7 | Mission Control Systems | Remote State and Backends |
| 8 | The Crew Manifest | Workspaces and Environments |
| 9 | Mid-Course Corrections | `terraform import` and Drift |
| 10 | Docking Procedure | Dependencies and `depends_on` |
| 11 | Life Support Systems | `count`, `for_each`, Dynamic Blocks |
| 12 | The Landing | CI/CD with Terraform |
| 13 | Moon Surface Operations | Provisioners and `local-exec` |
| 14 | Return to Earth | `terraform destroy` and completion |

---

## 🌍 One Final Observation

Somewhere in the world right now, an engineer is sitting before a screen, contemplating infrastructure. They might be in Sydney. In Amsterdam. In Riyadh. In Nairobi. And they are asking the same question that every engineer before them has asked:

*"How do I build this in a way I can understand, maintain, and trust?"*

Terraform is not the only answer. But it is, for millions of engineers, a very good one.

Because the code is the blueprint. The plan is the checklist. The apply is the launch. And the destroy is the return — complete, clean, and leaving nothing behind but the knowledge of what was built, and the confidence that it can be built again.

The Moon is 384,400 kilometres away. Your infrastructure can be anywhere. And with Terraform, you can describe it, plan it, build it, change it, and dismantle it — in text files, in version control, in a pipeline that runs the same way every time.

This is not just infrastructure management.

*This is engineering.*

---

*🌕 Thank you for flying the To The Moon series. The repository for all code examples is at the series companion repo. Comments, corrections, and mission reports are always welcome.*

*Ad astra.*
