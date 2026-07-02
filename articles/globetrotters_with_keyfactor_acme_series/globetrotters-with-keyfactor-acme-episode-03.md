---
title: "Globetrotters with Keyfactor ACME 🛬 Ep.3"
series: "Globetrotters with Keyfactor ACME"
part: 3
organization: "the-software-s-journey"
tags: [keyfactor, acme, installation, windows, kubernetes, helm]
---

## Episode 3: Setting Up Base Camp

A travel agency can open a storefront on a quiet high street, or it can set up a modular kiosk that can be duplicated across every airport in the network. Keyfactor ACME offers the same choice: a traditional Windows installation, or a Kubernetes deployment built for cloud-native scaling.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Windows administrator | KeyfactorACME.msi installer | Run the installer on the chosen server, confirm the install location | Installed Keyfactor ACME application files | KeyfactorACMEConfig.exe configuration tool |
| Kubernetes platform team | Helm chart, cluster resources | Create the required Kubernetes resources and start the customized container | Running Keyfactor ACME container in the cluster | ACME clients, load balancer |
| Both paths | Configuration parameters | Hand off to configuration (Configure, Identifiers, Claims commands) | A fully configured ACME server ready to serve travelers | Preparing/Configuration episodes |

### The high-street storefront

On Windows, the storefront does not need to share a building with headquarters. Running the Windows installer package on the server chosen for deployment does not require that server to also host Keyfactor Command. Once installed, there is deliberately no configuration wizard waiting at the end, unlike some other Keyfactor products. Instead, staff use a command-line tool, KeyfactorACMEConfig.exe, to actually open for business.

### The modular kiosk

The Kubernetes route treats the agency as something that can be spun up, scaled, and torn down as demand changes. Using Helm to deploy in a Kubernetes environment simplifies orchestration and scaling in cloud-native environments, which matters when the agency needs to handle a sudden spike of travelers hitting the counter at once, say, during a mass certificate renewal window.

### Same office, two floor plans

Whichever base camp is chosen, the destination is identical: a running Keyfactor ACME server waiting for its configuration to be dialed in. Windows installs still lean on the command-line configuration tool for everything from authentication to identifiers and claims; Kubernetes installs apply that same configuration through the resources set up alongside the container. Episode 4 walks into the newly built office and starts filling out the actual configuration forms.

