---
title: "Air Traffic Control Scaleway Ep.8"
part: 8
published: false
description: "Episode 8 of the Air Traffic Control series: deploy managed Kubernetes on Scaleway — Kapsule for a single-cloud cluster with ingress, encrypted storage, and WordPress, then Kosmos for a multi-cloud cluster spanning four Availability Zones. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, kubernetes, kapsule]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-08.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# Fleet Command: Kubernetes Kapsule and Kosmos on Scaleway

*“A single Thunderbird can handle a single mission. But when the emergency spans continents — when you need assets in Paris, Amsterdam, Warsaw, and a node halfway between — you do not send one vehicle. You coordinate the fleet. That is what fleet command is for.”*
*— Jeff Tracy, Thunderbird Island Operations Centre*

-----

Welcome back to the **Scaleway Air Traffic Control Centre**.

Every episode so far has dealt with individual resources: one Instance, one database, one set of containers, one private network. In this final hands-on episode, we step back and manage the orchestration layer — **Kubernetes** — the system that turns a collection of individual machines into a coordinated fleet that can deploy, scale, and self-heal applications automatically.

Scaleway offers two managed Kubernetes products. **Kapsule** is a fully managed single-cloud cluster: Scaleway manages the control plane, the worker nodes, and the networking. **Kosmos** is a multi-cloud cluster: the control plane is managed by Scaleway, but worker nodes can live anywhere — across multiple Scaleway Availability Zones, other cloud providers, or on-premises infrastructure.

In this episode, we deploy both.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

**Part 1 — Kapsule:**

- Create a Kubernetes Kapsule cluster with autoscaling
- View node status via `kubectl`
- Install Traefik as an ingress controller via Easy Deploy
- Register the Load Balancer IP in a DNS record
- Create an encrypted storage class
- Deploy WordPress using the encrypted storage class and Traefik ingress
- Reboot a node and observe pod recovery
- Delete the cluster and all associated resources

**Part 2 — Kosmos:**

- Configure an IAM policy granting a Kosmos application the right to register external nodes
- Create a Kubernetes Kosmos cluster via the Scaleway CLI
- Add Scaleway pools and nodes spread across four Availability Zones
- Add a multi-cloud pool and attach an external Instance as a node
- Deploy an application with 6 replicas across the full fleet
- Apply topology spread constraints for uniform zone distribution
- Delete all resources

### Pre-Launch Checklist

- ✅ You have a Scaleway account and can access the Organisation you own
- ✅ You have configured an SSH key for the `default` project
- ✅ You have configured an API key for yourself (from Episode 1)
- ✅ You have [`kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl), [`kubectx`, and `kubens`](https://github.com/ahmetb/kubectx) installed on your machine
- ✅ You have cloned the [`scw-certifications`](https://github.com/scaleway/scw-certifications/) repository — the `08_kubernetes/assets/` folder contains the manifests for this episode
- ✅ The trainer has provided you with a domain and DNS zone (required for the Traefik and WordPress DNS steps)

> **Note:** For both parts of this activity, you will work in your Organisation’s `default` project.

-----

## 📊 SIPOC — How Managed Kubernetes Flows Through the System

|Stage|SIPOC Element|Kubernetes Equivalent                                                                                               |Example                                                                                                    |
|-----|-------------|--------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway Kubernetes engine (Kapsule / Kosmos) + Easy Deploy + Scaleway CLI                                          |Managed control plane, node pools, ingress, registry                                                       |
|**I**|**Input**    |Cluster config, pool specs, Helm values, DNS records, IAM policies, node-agent                                      |`hands-on-kapsule`, `PLAY2-MICRO`, Traefik YAML, encrypted storage class, Kosmos IAM                       |
|**P**|**Process**  |Create cluster → Configure kubectl → Deploy ingress → Add DNS → Encrypt storage → Deploy app → Extend to multi-cloud|All the hands-on steps in both parts                                                                       |
|**O**|**Output**   |A production-pattern Kapsule cluster running WordPress behind TLS ingress, and a Kosmos fleet spanning four zones   |`https://wordpress.training-k8s-1.<dns-zone>`, pods distributed across `fr-par-1/2`, `nl-ams-2`, `pl-waw-1`|
|**C**|**Consumer** |Platform engineers, development teams, and SREs who deploy and operate containerised workloads                      |Your kubectl session, your browser, your application teams                                                 |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway       ──▶   Cluster config  ──▶  Create cluster   ──▶  Kapsule       ──▶   Platform
Kubernetes           Pool specs            Configure kubectl     with TLS ingress      engineers
engine               Helm values           Deploy ingress        WordPress             Dev teams
(Kapsule /           DNS records           Add DNS               Encrypted storage
Kosmos)              IAM policies          Encrypt storage       Kosmos fleet          SREs
                     node-agent            Deploy app            across 4 zones
Easy Deploy          k_deployments.yml     Extend to
                                           multi-cloud
Scaleway CLI
```

> **Tower to crew:** This episode is the longest in the series. Work through Part 1 first and confirm that the Kapsule cluster is fully operational before starting Part 2. The two clusters are independent — you can delete Kapsule before starting Kosmos if resource cost is a concern.

-----

# Part 1 — Kapsule: Single-Cloud Managed Kubernetes

-----

## 🛫 Section 1 — Assemble the Fleet: Create the Kapsule Cluster

Kapsule cluster creation is a two-stage wizard: first the control plane, then the worker pool.

### 1.1 — Configure the Cluster

1. In the **Containers** section of the side menu, select **Kubernetes**, then click **Create cluster**.
1. Confirm that the following defaults are in place — leave them as is:
- Cluster type: `Kubernetes Kapsule`
- Region: `Paris`
- Control plane offer: `Free`
1. In **Choose a Kubernetes version**, select the most recent available version.
1. In **Configure a Private Network**, select `Attach to a new Private Network` and name it `hands-on-kapsule`.
1. Name the cluster `hands-on-kapsule`.
1. Click **Next**.

### 1.2 — Configure the Pool

1. For the **Availability Zone**, select `Paris 2`.
1. In the **Cost-optimized** tab, select node type `PLAY2-MICRO`.
1. In **Configure pool options**, enable `Autoscale the number of nodes`. Leave the defaults in place: minimum 3, maximum 10.
1. Review the estimated cost.
1. Click **Create cluster**.

> **Note:** You can follow the control plane deployment status in the Console. Once the cluster is available, explore the **Overview**, **Pools**, **Nodes**, **Easy Deploy**, and **Managed Logs** tabs — they give a complete picture of what Scaleway provides for day-2 cluster management.

-----

## 🏗️ Section 2 — Configure kubectl: View Node Status

1. In the **Kubernetes** page, select your cluster. The **Overview** tab displays.
1. Scroll to **Download kubeconfig** and click **Download file**.
1. In your terminal, move the file into place and set the environment variable:

```bash
mkdir -p ~/.kube
touch ~/.kube/config
mv ~/Downloads/kubeconfig-hands-on-kapsule.yaml ~/.kube/config
export KUBECONFIG=~/.kube/config
```

1. Verify that all nodes are ready:

```bash
kubectl get node
```

All nodes should show status `Ready`. If any node is still `NotReady`, wait a minute and retry — autoscaling nodes may take a moment to complete their boot sequence.

-----

## 🧑‍✈️ Section 3 — Air Traffic Control: Install Traefik via Easy Deploy

Traffic into the cluster must be controlled — every inbound HTTP/S request needs to be routed to the correct service. Traefik acts as the ingress controller: the air traffic controller of the cluster’s network layer.

1. In the **Kubernetes** page, select your cluster, then open the **Easy Deploy** tab.
1. Click **Deploy application**.
1. In **Choose an application type**, select **Application library**.
1. Search for `Traefik` and select `Traefik 2 Ingress`.
1. In **Edit default configuration**, replace the default Helm values with the following:

```yaml
deployment:
  kind: Deployment
  replicas: 3
ingressClass:
  enabled: true
  isDefaultClass: true
service:
  type: LoadBalancer
ports:
  websecure:
    tls:
      enabled: true
```

> **Tip:** YAML is whitespace-sensitive. If deployment fails with a parsing error, verify that each level of indentation uses consistent spaces — no tabs, no trailing spaces.

1. Set both the application name and namespace to `traefik-ingress-controller`.
1. Click **Deploy application**.
1. Confirm that all Traefik pods are running:

```bash
kubectl get pods -n traefik-ingress-controller
```

All pods should reach `Running` status. Three replicas means the ingress layer is resilient to a single node failure.

-----

## 🔒 Section 4 — Register the Control Tower: Add DNS Record

When Traefik deployed, Kapsule automatically provisioned a Scaleway Load Balancer to front the ingress controller. We now register its IP address in the DNS zone so that hostnames resolve to the cluster.

1. In the **Network** section of the side menu, select **Load Balancers**. Observe that a Load Balancer has been automatically created and is marked as auto-managed by Kubernetes Kapsule.
1. In your terminal, retrieve the Load Balancer’s external IP:

```bash
kubectl get services -n traefik-ingress-controller
```

1. List the current DNS records in your zone:

```bash
scw dns record list <dns-zone>
```

1. Add a wildcard A record pointing to the Load Balancer IP:

```bash
scw dns record add <dns-zone> \
  data=<load-balancer-IP-address> \
  name='*.training-k8s-1' \
  ttl=300 \
  type=A
```

1. Verify DNS resolution and ingress routing:

```bash
curl http://test.training-k8s-1.<dns-zone>.<extension>
```

Or in your browser:

```
http://test.training-k8s-1.<dns-zone>.<extension>
```

An HTTP `404` response is the expected and correct result — it confirms the request reached Traefik, which found no matching ingress rule for the test hostname. The control tower is listening.

-----

## 💾 Section 5 — Encrypt the Cargo Hold: Create an Encrypted Storage Class

Default Scaleway storage classes do not encrypt data at rest. For workloads that handle sensitive data — user credentials, configuration secrets, database volumes — encryption at rest is a baseline requirement.

1. Generate a random passphrase and encode it to Base64:

```bash
ENCRYPTION_PASSPHRASE_B64=$(openssl rand -base64 20)
```

1. Create a Kubernetes Secret containing the passphrase:

```bash
kubectl apply -f - << EOF
apiVersion: v1
kind: Secret
metadata:
  name: enc-secret
  namespace: default
type: Opaque
data:
  encryptionPassphrase: $ENCRYPTION_PASSPHRASE_B64
EOF
```

1. Navigate to the `08_kubernetes` folder of the `scw-certifications` repository and apply the encrypted storage class manifest:

```bash
kubectl apply -f assets/storage_class.yml
```

The storage class `scw-bssd-enc` is now available in the cluster. Any PersistentVolumeClaim that references this class will provision a Block Storage volume with encryption at rest enabled.

> **Tower confirms:** The passphrase never leaves the cluster — it is stored as a Kubernetes Secret and referenced by the storage class driver. The encryption is transparent to the application: data written to the volume is encrypted before it reaches the physical disk, and decrypted on read. No application code changes required.

-----

## 🌐 Section 6 — Deploy the Mission Payload: WordPress

With ingress routing, DNS, and encrypted storage in place, we deploy WordPress — a real-world application that exercises all three.

1. In the **Easy Deploy** tab, click **Deploy application**.
1. Select **Application library**, search for `Bitnami Wordpress`, and select it.
1. Replace the default Helm values with the following — substituting your actual DNS zone for `<dns-zone>`:

```yaml
global:
  storageClass: scw-bssd-enc
service:
  type: ClusterIP
ingress:
  enabled: true
  hostname: wordpress.training-k8s-1.<dns-zone>.fr
  tls: true
  selfSigned: true
```

1. Set both the application name and namespace to `wordpress`.
1. Click **Deploy application**.

> **Note:** WordPress pulls several images and provisions encrypted volumes — allow several minutes for the deployment to complete.

1. Watch the pod status until all pods reach `Running`:

```bash
kubectl get pods -n wordpress -w
```

Once running, navigate to `https://wordpress.training-k8s-1.<dns-zone>.fr` in your browser. Traefik routes the request, TLS is terminated at the ingress, and WordPress serves the page from volumes encrypted at rest.

-----

## 🔑 Section 7 — Node Recovery: Reboot a Node

The autoheal feature monitors node health and can automatically recover unhealthy nodes. In this section, we trigger a manual reboot to observe how Kubernetes redistributes workloads during a node interruption.

1. In the **Kubernetes** page, select your cluster, then open the **Nodes** tab.
1. Click the `...` menu next to any node and select **Reboot**.
1. Watch pod status during the reboot:

```bash
kubectl get pods -n wordpress -w
```

Kubernetes will evict pods from the rebooting node and reschedule them on the remaining healthy nodes. Once the node completes its reboot and rejoins the cluster as `Ready`, the scheduler will rebalance pods across all available nodes.

> **Tower confirms:** This is Kubernetes resilience in action. No human intervention was required to maintain service availability during the node reboot. The control plane observed the node state change, took corrective action, and restored the desired replica count automatically.

-----

## 🗑️ Section 8 — Stand Down the Fleet: Delete the Kapsule Cluster

1. In the **Kubernetes** page, click the `...` menu next to `hands-on-kapsule` and select **Delete**.
1. Type `DELETE`.
1. Select the checkbox to delete all volumes, empty Private Networks, and Load Balancers whose names start with the cluster ID.
1. Click **Delete cluster**.

> ⚠️ **Security Protocol — Restricted:** The deletion checkbox covers Load Balancers and Block Storage volumes provisioned by the cluster. Ensure you have not retained any data in those volumes that is needed elsewhere before confirming deletion.

-----

# Part 2 — Kosmos: Multi-Cloud Kubernetes

-----

## 🛫 Section 9 — Multi-Cloud Clearance: Configure IAM for Kosmos

Kosmos allows external nodes — Instances outside the Scaleway-managed pool — to join the cluster. This requires a dedicated IAM application and policy that grants the `node-agent` program permission to register nodes without holding Organisation-wide credentials.

### 9.1 — Create the Application

1. In the Console, open the **Organisation** drop-down and select **IAM**.
1. Open the **Applications** tab and click **Create application**.
1. Name the application `Kosmos`.
1. Click **Create application**.

### 9.2 — Create the Policy

1. Open the **Policies** tab and click **Create a policy**.
1. Name the policy `Kosmos`.
1. In **Select a principal**, choose the `Kosmos` application, then click **Add rule**.
1. In the **Scope** section, select **Access to resources**, then choose the `default` project from the drop-down. Click **Validate**.
1. In **Permission sets**, select **Containers**, then select `KubernetesExternalNodeRegister`. Click **Validate**.
1. Click **Create policy**.

### 9.3 — Generate an API Key for the Application

1. Open the **API keys** tab and click **Generate API key**.
1. In **Select API key bearer**, select `An application`, then choose `Kosmos` from the drop-down.
1. Click **Generate API key**.

> **Tip:** Copy and store the secret key immediately — it will not be shown again. This key is used exclusively by the `node-agent` program running on the external Instance. It cannot access any other resource in your Organisation.

1. Verify that your CLI profile reflects the updated configuration:

```bash
scw config dump
```

-----

## 🏗️ Section 10 — Assemble the Multi-Cloud Fleet: Create the Kosmos Cluster

### 10.1 — Create the Cluster

```bash
scw k8s cluster create \
  name=training-k8s-2 \
  cni=kilo \
  type=multicloud \
  version=1.28.0
```

### 10.2 — Verify Cluster Status

```bash
scw k8s cluster list
```

Wait for the cluster status to show `ready` before proceeding.

-----

## 🧑‍✈️ Section 11 — Spread the Fleet: Add Pools Across Four Zones

Once the cluster is ready, provision four node pools — one per Availability Zone — to distribute the fleet across multiple regions:

```bash
scw k8s pool create cluster-id=<cluster-uuid> name=fr-par-1 zone=fr-par-1 node-type=PLAY2_NANO size=1
scw k8s pool create cluster-id=<cluster-uuid> name=fr-par-2 zone=fr-par-2 node-type=PLAY2_NANO size=1
scw k8s pool create cluster-id=<cluster-uuid> name=nl-ams-2 zone=nl-ams-2 node-type=PLAY2_NANO size=2
scw k8s pool create cluster-id=<cluster-uuid> name=pl-waw-1 zone=pl-waw-1 node-type=PLAY2_NANO size=1
```

> **Note:** Replace `<cluster-uuid>` with the cluster ID returned by `scw k8s cluster list`. The `nl-ams-2` pool has 2 nodes; all others have 1 — this gives us 5 Scaleway-managed nodes across 4 zones.

-----

## 🔒 Section 12 — The External Node: Add a Multi-Cloud Pool

### 12.1 — Create the Multi-Cloud Pool

```bash
scw k8s pool create \
  cluster-id=<cluster-uuid> \
  name=pool-multi-cloud-kosmos \
  node-type=external \
  tags.0=region=paris
```

### 12.2 — Retrieve the Pool ID

```bash
scw k8s pool list cluster-id=<cluster-uuid>
```

Copy the ID for `pool-multi-cloud-kosmos` — you will need it when configuring the external node.

-----

## 💾 Section 13 — Provision and Connect the External Node

### 13.1 — Create the Instance

```bash
scw instance server create \
  name=training-k8s-kosmos \
  image=ubuntu_focal \
  type=PLAY2-NANO \
  ip=new \
  zone=fr-par-2 \
  root-volume=block:10GB
```

### 13.2 — Retrieve the Instance ID and Public IP

```bash
scw instance server list zone=fr-par-2
scw instance server get <Instance_ID> zone=fr-par-2
```

### 13.3 — Connect to the Instance

```bash
ssh root@<Public_IP_address_of_Instance>
```

-----

## 🌐 Section 14 — Attach the External Node to the Cluster

From inside the Instance:

1. Download and make executable the Kosmos node agent:

```bash
wget https://scwcontainermulticloud.s3.fr-par.scw.cloud/node-agent_linux_amd64 \
  && chmod +x node-agent_linux_amd64
```

1. Export the required environment variables — substituting your actual pool ID, pool region, and the Kosmos application secret key:

```bash
export POOL_ID=<pool_id>
export POOL_REGION=<pool_region>
export SCW_SECRET_KEY=<kosmos_app_secret_key>
```

> **Tip:** The pool ID comes from `scw k8s pool list cluster-id=<cluster-uuid>` — use the ID for `pool-multi-cloud-kosmos`. The pool region is `fr-par`.

1. Execute the node agent to register the Instance as an external node:

```bash
sudo -E ./node-agent_linux_amd64 -loglevel 0 -no-controller
```

1. In the Console, open the **Nodes** tab of your Kosmos cluster and verify that a node with type `EXTERNAL` now appears.

> **Tower confirms:** The external node is now a full member of the Kubernetes cluster. It can receive scheduled pods, participate in service routing, and be addressed by the scheduler alongside the Scaleway-managed pool nodes — despite running on a separate Instance with its own lifecycle.

-----

## 🔑 Section 15 — Deploy and Distribute: Test Multi-Zone Scheduling

### 15.1 — Deploy with 6 Replicas

```bash
kubectl create deploy first-deployment \
  --replicas=6 \
  --image=busybox \
  -- /bin/sh -c "while true; do date; sleep 10; done"
```

### 15.2 — Verify Distribution Across Nodes

```bash
kubectl get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName
```

Observe which nodes the 6 replicas landed on. Without topology constraints, the default scheduler distributes pods based on resource availability — not zone balance.

### 15.3 — Delete the Deployment

```bash
kubectl delete deploy first-deployment
```

### 15.4 — Apply Topology Spread Constraints

```bash
kubectl apply -f assets/k_deployments.yml
```

### 15.5 — Verify Uniform Zone Distribution

```bash
kubectl get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName
```

With topology spread constraints applied, pods are distributed uniformly across zones — one or two per zone rather than clustered on the nodes with the most available resources. This is zone-aware scheduling: resilience by design.

### 15.6 — Clean Up

```bash
kubectl delete deploy busy-topologyspread
```

Delete all remaining resources created during this activity — the external Instance, the Kosmos cluster (which will remove all pools and nodes), and any allocated IPs.

-----

## 🗺️ Kubernetes Architecture — The Fleet Command Map

```
┌────────────────────────────────────────────────────────────────┐
│         PART 1 — KAPSULE (hands-on-kapsule, Paris)            │
│                                                                │
│  CONTROL PLANE    Managed by Scaleway (Free tier)             │
│  POOL             PLAY2-MICRO, PAR-2, autoscale 3-10 nodes    │
│  INGRESS          Traefik 2 (3 replicas, LoadBalancer svc)    │
│  DNS              *.training-k8s-1.<zone> → LB IP             │
│  STORAGE          scw-bssd-enc (encrypted Block Storage)       │
│  APPLICATION      WordPress (ClusterIP + Traefik ingress, TLS) │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│         PART 2 — KOSMOS (training-k8s-2, multi-cloud)         │
│                                                                │
│  CONTROL PLANE    Managed by Scaleway (CNI: Kilo)             │
│  POOLS            fr-par-1 x1 / fr-par-2 x1                  │
│                   nl-ams-2 x2 / pl-waw-1 x1                   │
│  EXTERNAL POOL    pool-multi-cloud-kosmos                      │
│  EXTERNAL NODE    training-k8s-kosmos (PLAY2-NANO, fr-par-2)  │
│  APPLICATION      busy-topologyspread (zone-aware scheduling)  │
└────────────────────────────────────────────────────────────────┘
```

-----

## 📋 Episode Debrief

*“Six zones. Two clusters. One application distributed uniformly across the fleet. That is what fleet command looks like when it is working. Thunderbirds are GO.”*
*— Jeff Tracy, Thunderbird Island Operations Centre*

In this episode, you have:

- ✅ Created a Kapsule cluster with autoscaling (3–10 nodes, `PLAY2-MICRO`, PAR-2)
- ✅ Configured `kubectl` using the downloaded kubeconfig
- ✅ Deployed Traefik as a 3-replica ingress controller via Easy Deploy
- ✅ Registered a wildcard DNS record pointing to the auto-provisioned Load Balancer
- ✅ Created an encrypted storage class backed by a Kubernetes Secret
- ✅ Deployed WordPress using encrypted Block Storage and Traefik TLS ingress
- ✅ Rebooted a node and observed Kubernetes self-healing in action
- ✅ Deleted the Kapsule cluster and all associated resources
- ✅ Configured an IAM application and policy granting `KubernetesExternalNodeRegister` permission
- ✅ Created a Kosmos cluster via the Scaleway CLI with CNI type `kilo`
- ✅ Provisioned four node pools across `fr-par-1`, `fr-par-2`, `nl-ams-2`, and `pl-waw-1`
- ✅ Added a multi-cloud pool and registered an external Instance as a cluster node
- ✅ Deployed a 6-replica application and observed default scheduling behaviour
- ✅ Applied topology spread constraints and verified uniform zone distribution
- ✅ Mapped the full Kubernetes fleet lifecycle through the SIPOC model

The fleet is assembled, distributed, and operating under coordinated control. This completes the hands-on series — every major Scaleway service, from IAM to bare metal to managed Kubernetes, has been visited, exercised, and stood down in good order.

-----

## 📡 Further Transmissions

- [Scaleway Kubernetes Kapsule documentation](https://www.scaleway.com/en/docs/containers/kubernetes/)
- [Scaleway Kubernetes Kosmos documentation](https://www.scaleway.com/en/docs/containers/kubernetes/reference-content/understanding-kosmos/)
- [Scaleway Easy Deploy documentation](https://www.scaleway.com/en/docs/containers/kubernetes/how-to/use-easy-deploy/)
- [Traefik Kubernetes Ingress documentation](https://doc.traefik.io/traefik/providers/kubernetes-ingress/)
- [Kubernetes topology spread constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [Scaleway CLI — Kubernetes commands](https://github.com/scaleway/scaleway-cli/blob/master/docs/commands/k8s.md)

-----

*Estimated reading time: 18 minutes. Estimated hands-on time: 90–120 minutes.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
