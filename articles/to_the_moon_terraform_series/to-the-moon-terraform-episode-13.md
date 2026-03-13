---
title: "To The Moon Terraform Ep.13"
part: 13
published: false
description: "Episode 13 — Moon Surface Operations"
tags: [erraform, cicd, automation, devops]
series: "To The Moon Terraform Series"
cover_image: "https://raw.githubusercontent.com/software-journey/terraform/main/images/to_the_moon_terraform_series/episode-13.webp"
canonical_url: ""
organization: "the-software-s-journey"
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
