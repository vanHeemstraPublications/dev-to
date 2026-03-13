---
title: "Welcome to Container Harbour! 🚢 Ep.10"
published: false
description: "Episode 10: ID Badges and Security Guards — RBAC Explained. Not everyone gets cluster-admin. Especially not Dave. Especially not in production."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-10.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 10: ID Badges and Security Guards — RBAC 🪪

### The Engineer Who Gave EVERYONE cluster-admin 😭

True story. New Kubernetes cluster. Eager team lead who just wanted everyone to be productive. Solution? Give every developer `cluster-admin`.

`cluster-admin` means: **you can do anything. To anything. Anywhere. Forever.**

For three months, everything was fine. Then a developer ran the wrong `kubectl delete` command against production instead of staging. The namespaces look similar. It was a Monday morning. Coffee hadn't kicked in.

Production namespace: deleted.

ALL the Deployments: deleted.

ALL the Services: deleted.

ALL the ConfigMaps and Secrets: deleted.

They got most of it back from their GitOps repo. It took four hours. It aged the team lead five years.

**This is why RBAC exists.** Not because your developers are malicious. Because humans make mistakes and the blast radius of mistakes should be LIMITED. 🎯

---

## The SIPOC of RBAC 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who defines access policies? | Platform/security team, cluster admins |
| **Input** | What goes in? | Roles (what's allowed), RoleBindings (who gets it) |
| **Process** | What happens? | API Server checks: "Does this user have permission for this action on this resource?" |
| **Output** | What comes out? | Allowed actions proceed; forbidden ones are rejected with 403 |
| **Consumer** | Who is governed? | Developers, CI/CD pipelines, service accounts, operators |

---

## The Four RBAC Building Blocks 🏗️

```
🪪  RBAC SYSTEM:

Role / ClusterRole          RoleBinding / ClusterRoleBinding
"What actions are           "Who gets to use this Role?"
 allowed on what
 resources?"
      |                                 |
      |<---- combined by binding ------>|
      |                                 |
      v                                 v
  can: get, list pods           Subject: developer@harbour.io
  in: namespace=production      in: namespace=production
```

| Object | Scope | Purpose |
|---|---|---|
| `Role` | One namespace | Permissions for resources IN that namespace |
| `ClusterRole` | Entire cluster | Permissions across all namespaces, or cluster-wide resources |
| `RoleBinding` | One namespace | Gives a Role (or ClusterRole) to a user/group/SA in one namespace |
| `ClusterRoleBinding` | Entire cluster | Gives a ClusterRole to a user/group/SA everywhere |

---

## Your First Role: The Developer Badge 👷

```yaml
# developer-role.yaml
# "Developers can READ everything in production, but not change it"
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-readonly
  namespace: production         # Only applies in 'production' namespace
rules:
- apiGroups: [""]               # "" = core API group (pods, services, etc.)
  resources: ["pods", "pods/log", "pods/exec", "services", "endpoints", "configmaps"]
  verbs: ["get", "list", "watch"]    # READ ONLY

- apiGroups: ["apps"]
  resources: ["deployments", "replicasets", "daemonsets", "statefulsets"]
  verbs: ["get", "list", "watch"]    # READ ONLY

- apiGroups: [""]
  resources: ["pods/portforward"]
  verbs: ["create"]                  # Allow port-forwarding for debugging

# What developers CAN'T do: delete, create, update, patch anything
# What developers DEFINITELY CAN'T do: touch secrets
```

---

## Binding the Role: Handing Out the Badge 🏷️

```yaml
# developer-rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-readonly-binding
  namespace: production
subjects:
# Individual user
- kind: User
  name: "alice@harbour.io"
  apiGroup: rbac.authorization.k8s.io

# A whole group
- kind: Group
  name: "harbour-developers"
  apiGroup: rbac.authorization.k8s.io

# A service account (for CI/CD pipelines, operators)
- kind: ServiceAccount
  name: ci-pipeline
  namespace: ci-cd

roleRef:
  kind: Role
  name: developer-readonly
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f developer-role.yaml
kubectl apply -f developer-rolebinding.yaml

# Verify: Can alice list pods in production?
kubectl auth can-i list pods --namespace=production --as=alice@harbour.io
# yes

# Can alice delete a deployment?
kubectl auth can-i delete deployments --namespace=production --as=alice@harbour.io
# no

# Can alice do ANYTHING in the 'staging' namespace?
kubectl auth can-i list pods --namespace=staging --as=alice@harbour.io
# no   (the Role only applies to 'production'!)
```

---

## ClusterRoles: Harbour-Wide Badges 🌍

Some permissions span the whole cluster. Use ClusterRole + ClusterRoleBinding:

```yaml
# monitoring-clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-reader
rules:
- apiGroups: [""]
  resources: ["nodes", "pods", "services", "endpoints", "namespaces"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets", "daemonsets", "statefulsets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["metrics.k8s.io"]
  resources: ["nodes", "pods"]
  verbs: ["get", "list", "watch"]
```

```yaml
# monitoring-clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring-reader-binding
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring
roleRef:
  kind: ClusterRole
  name: monitoring-reader
  apiGroup: rbac.authorization.k8s.io
```

---

## Service Accounts: Badges for Machines 🤖

Every Pod that needs to talk to the Kubernetes API gets a **ServiceAccount**. By default, every Pod gets the `default` ServiceAccount in its namespace — which has minimal permissions.

For CI/CD, operators, and tools that need API access:

```yaml
# ci-serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ci-pipeline
  namespace: ci-cd
---
# Give it permission to deploy to staging only
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployer
  namespace: staging
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "update", "patch"]    # Can update deployments (rolling updates!)
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ci-deployer-binding
  namespace: staging
subjects:
- kind: ServiceAccount
  name: ci-pipeline
  namespace: ci-cd
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# Pod using the service account:
spec:
  serviceAccountName: ci-pipeline   # Assign the ServiceAccount to this Pod
  automountServiceAccountToken: true  # Mount the token (default: true)
  containers:
  - name: ci-runner
    image: my-ci-runner:latest
    # Inside this container, kubectl will authenticate as ci-pipeline
```

---

## Built-in ClusterRoles: The Pre-Made Badge Collection 🏆

Kubernetes ships with useful ClusterRoles you can bind directly:

```bash
kubectl get clusterroles | grep -v system

# NAME                    DESCRIPTION
# admin                   Full access to namespace resources (not cluster-level)
# edit                    Read+write most namespace resources (no RBAC, no Secrets)
# view                    Read-only access to most namespace resources
# cluster-admin           GOD MODE. Can do everything. Use sparingly.
```

```yaml
# Give a developer 'edit' access to staging (common pattern)
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-edit-staging
  namespace: staging
subjects:
- kind: Group
  name: "harbour-developers"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: edit                 # Built-in! No need to create a Role.
  apiGroup: rbac.authorization.k8s.io
```

---

## Debugging RBAC: "Why Am I Getting 403?" 🔍

```bash
# Check what a user/SA can do
kubectl auth can-i --list --namespace=production --as=bob@harbour.io

# Resources                         Non-Resource URLs   Resource Names   Verbs
# pods                              []                  []               [get list watch]
# deployments.apps                  []                  []               [get list watch]

# Check a specific action
kubectl auth can-i delete secrets --namespace=production --as=bob@harbour.io
# no

# Who has access to a resource?
kubectl get rolebindings,clusterrolebindings -A | grep developer

# See all roles in a namespace
kubectl get roles -n production
kubectl describe role developer-readonly -n production

# Full RBAC audit (what can EVERYONE do?)
kubectl get clusterrolebindings -o json | \
  jq '.items[] | {name: .metadata.name, subjects: .subjects, role: .roleRef.name}'
```

---

## The Principle of Least Privilege: Only What's Needed 🔒

The Harbourmaster's rule: **give the minimum permissions to do the job. Nothing more.**

```
🚫 Too broad:          ✅ Just right:
cluster-admin          Role: can list pods in staging
                       Role: can update deployment image in staging
                       Role: can read logs in staging
                       
                       Nothing more. If they need more: discuss, justify, add.
```

```yaml
# Common permission patterns:

# Pattern 1: Read-only developer (troubleshoot without breaking)
rules:
- apiGroups: ["", "apps"]
  resources: ["pods", "pods/log", "deployments", "services"]
  verbs: ["get", "list", "watch"]

# Pattern 2: Deployer (CI/CD pipeline)
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "update", "patch"]   # Can roll out new images
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch", "delete"]   # Can restart pods

# Pattern 3: Namespace admin (team lead for their own namespace)
# -> Use built-in 'admin' ClusterRole with a RoleBinding to their namespace

# Pattern 4: Cluster-wide viewer (SRE, monitoring)
# -> Use built-in 'view' ClusterRole with a ClusterRoleBinding
```

---

## The Harbourmaster's Log — Entry 10 📋

*Revoked cluster-admin from all developers today. Replaced with appropriately scoped Role bindings.*

*Ten minutes later: three Slack messages asking why they can't delete things in production.*

*I explained this was the point.*

*Dave asked why he needed production delete access. I asked him to recall the incident from Episode 9 — the one where he deleted the test pods that turned out to be production pods.*

*Dave went very quiet.*

*I explained that he now has read-only access to production, edit access to staging, and admin access to his personal dev namespace. This covers 100% of legitimate use cases.*

*Dave asked what would happen if he needed to restart a production pod.*

*"You ask me," I said. "And I do it."*

*Dave looked like this was the worst news he had ever received. I consider this a security success.* 🎩

---

## Your Mission 🎯

1. Create a `developer` Role in `staging` namespace: can get/list/watch pods, deployments, services. Can exec into pods. CANNOT delete or modify anything.

2. Create a `deployer` Role in `staging`: can update deployments (rolling updates only).

3. Create two ServiceAccounts: `dev-user` and `ci-runner`.

4. Bind the roles to the ServiceAccounts.

5. Test permissions:
```bash
kubectl auth can-i exec pods --namespace=staging \
  --as=system:serviceaccount:staging:dev-user
# yes

kubectl auth can-i delete deployments --namespace=staging \
  --as=system:serviceaccount:staging:dev-user
# no

kubectl auth can-i update deployments --namespace=staging \
  --as=system:serviceaccount:staging:ci-runner
# yes
```

**Bonus:** Try running a pod as the `dev-user` service account and attempt to delete something. Observe the 403 error with satisfaction.

---

## Next Time 🎬

**Episode 11**: The Health Inspector Visits — **Liveness and Readiness Probes**. Is your container actually doing anything, or just sitting there consuming CPU and lying to everyone? Time to find out. 🩺

---

*P.S. — The Kubernetes RBAC system was introduced in version 1.6 (2017). Before that, there was ABAC (Attribute-Based Access Control) which was configured via a file on the API Server that required a server restart to update. Changing access control required restarting the entire control plane. RBAC was the greatest quality-of-life improvement in Kubernetes history and nobody talks about it enough.* 🎉

---

**🎯 Key Takeaways:**

- **RBAC** = Role-Based Access Control. Who can do what, on which resources, where.
- **Role** = permissions in ONE namespace. **ClusterRole** = permissions cluster-wide.
- **RoleBinding** = assigns a Role to users/groups/SAs in ONE namespace.
- **ClusterRoleBinding** = assigns a ClusterRole everywhere.
- **ServiceAccount** = the identity for Pods and automated systems talking to the Kubernetes API.
- `kubectl auth can-i` = your RBAC debugging superpower. Use it constantly.
- **Built-in roles**: `view` (read-only), `edit` (read-write), `admin` (namespace admin), `cluster-admin` (god mode — use sparingly).
- Principle of least privilege: minimum permissions to do the job. Always. No exceptions. 🔒
