---
title: "To The Moon Terraform Ep.12"
part: 12
published: false
description: "Episode 12 — The Landing"
tags: [terraform, cicd, automation, devops]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-12.webp"
canonical_url: ""
organization: "the-software-s-journey"
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
