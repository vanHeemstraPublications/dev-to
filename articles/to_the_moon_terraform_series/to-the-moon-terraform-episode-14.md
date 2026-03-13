---
title: "To The Moon Terraform Ep.14"
part: 14
published: false
description: "Episode 14 — Return to Earth"
tags: [erraform, cicd, automation, devops]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-14.webp"
canonical_url: ""
organization: "the-software-s-journey"
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
