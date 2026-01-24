---
title: "Protecting Your Prize-Winning Cyber-Carrots: A Defense-in-Depth Guide to Azure AKS with Crossplane v2"
published: false
description: "Learn how to apply layered security controls to your Azure AKS deployments using Crossplane v2 - because cyber-rabbits are always hungry for your data!"
tags: crossplane, kubernetes, azure, security
series: Crossplane Adventures
cover_image: https://raw.githubusercontent.com/software-journey/defense-in-depth-of-cyber-carrots/main/images/cyber-carrots-cover.png
canonical_url: 
organization: the-software-s-journey
---

# Protecting Your Prize-Winning Cyber-Carrots: A Defense-in-Depth Guide to Azure AKS with Crossplane v2

*Inspired by [Google's Defense-in-Depth Security module](https://www.skills.google/paths/419/course_templates/1300/video/579179) - because even Google knows you need more than one fence to keep the rabbits out!*

## 🥕 Introduction: The Garden of Cloud Resources

Picture this: You've spent months cultivating the most beautiful cyber-carrots (your precious application data) in your Azure Kubernetes Service garden. They're orange, they're crunchy, and they're absolutely irresistible to cyber-rabbits (malicious actors) who would love nothing more than to munch on your sensitive customer data.

Now, you could just plant your carrots and hope for the best. But that's like leaving a "FREE CARROTS" sign on your garden gate. Instead, we're going to build a proper defense-in-depth security strategy using Crossplane v2 - think of it as building the Fort Knox of vegetable gardens.

In this article, we'll deploy a production-ready Azure AKS cluster with multiple layers of security controls. Because in cybersecurity, as in gardening, one fence is never enough when rabbits are this motivated.

## 🐰 Understanding Defense-in-Depth (Or: Why Cyber-Rabbits Are Persistent)

Before we dive into code, let's understand what defense-in-depth actually means. According to Google's Cloud Security course, it's like protecting a community garden with multiple security layers:

1. **Identity Controls** - Who gets a key to the garden gate?
2. **Protective Controls** - The fence around your carrots
3. **Network Controls** - Which paths lead to which carrot beds?
4. **Detective Controls** - Cameras to spot sneaky rabbits
5. **Responsive Controls** - Automatic sprinklers when intruders detected
6. **Recovery Controls** - Replanting carrots after an attack

Each layer works together. If a particularly clever cyber-rabbit gets past the fence, the cameras spot it, the sprinklers activate, and you can restore from your backup seed vault.

## 🎯 What We're Building

We're going to deploy a secure Azure AKS cluster with Crossplane v2 that includes:

- **Identity Layer**: Azure AD integration and RBAC
- **Protective Layer**: Network policies and pod security standards
- **Network Layer**: Private clusters and firewall rules
- **Detective Layer**: Azure Monitor and Container Insights
- **Responsive Layer**: Azure Policy auto-remediation
- **Recovery Layer**: Backup and disaster recovery

All of this will be declared as code, version-controlled, and reproducible. Because infrastructure-as-code is like having a detailed garden plan - you can rebuild your garden exactly the same way every time.

## 🛠️ Prerequisites

Before we start planting our cyber-carrots, make sure you have:

```bash
# Crossplane v2 (the important bit!)
kubectl crossplane --version
# Should show v2.x.x

# Azure CLI
az --version

# kubectl
kubectl version --client

# Helm (for Crossplane installation)
helm version
```

**Full source code available at**: [github.com/software-journey/defense-in-depth-of-cyber-carrots](https://github.com/software-journey/defense-in-depth-of-cyber-carrots)

## 📦 Layer 1: Identity Controls (Garden Gate Keys)

First, let's set up who can access our garden. We'll create a Crossplane composition that includes Azure AD integration:

```yaml
# compositions/aks-with-identity.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: secure-aks-cluster
  labels:
    provider: azure
    security-level: defense-in-depth
spec:
  compositeTypeRef:
    apiVersion: platform.example.com/v1alpha1
    kind: SecureAKSCluster
  
  mode: Pipeline
  pipeline:
  - step: render-aks-cluster
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      # Identity Control: Azure AD Integration
      - name: aks-cluster
        base:
          apiVersion: containerservice.azure.upbound.io/v1beta1
          kind: KubernetesCluster
          spec:
            forProvider:
              # Enable Azure AD integration - our first layer of defense!
              azureActiveDirectoryRoleBasedAccessControl:
              - managed: true
                azureRbacEnabled: true
                adminGroupObjectIds:
                - $(admin_group_id)
              
              # Enable managed identity (like giving the cluster its own key)
              identity:
              - type: SystemAssigned
              
              resourceGroupName: $(resource_group)
              location: westeurope
              dnsPrefix: secure-carrots
              
              defaultNodePool:
              - name: system
                nodeCount: 3
                vmSize: Standard_D2s_v3
                # Enable auto-scaling (garden grows with your carrots!)
                enableAutoScaling: true
                minCount: 3
                maxCount: 6
                
              networkProfile:
              - networkPlugin: azure
                networkPolicy: calico  # More on this in Layer 3!
                
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.resourceGroup
          toFieldPath: spec.forProvider.resourceGroupName
        - type: FromCompositeFieldPath
          fromFieldPath: spec.adminGroupId
          toFieldPath: spec.forProvider.azureActiveDirectoryRoleBasedAccessControl[0].adminGroupObjectIds[0]
```

**Why this matters**: Without Azure AD integration, anyone with cluster credentials can waltz into your garden. With it, you control exactly who gets which keys - some people can only water the carrots, others can harvest them.

## 🔒 Layer 2: Protective Controls (The Fence)

Now let's build our fence - pod security standards that prevent mischievous containers from doing things they shouldn't:

```yaml
# compositions/pod-security-standards.yaml
- name: pod-security-policy
  base:
    apiVersion: kubernetes.crossplane.io/v1alpha2
    kind: Object
    spec:
      forProvider:
        manifest:
          apiVersion: v1
          kind: Namespace
          metadata:
            name: carrot-storage
            labels:
              # Enforce restricted pod security standard
              pod-security.kubernetes.io/enforce: restricted
              pod-security.kubernetes.io/audit: restricted
              pod-security.kubernetes.io/warn: restricted
          
  - name: network-policy-default-deny
    base:
      apiVersion: kubernetes.crossplane.io/v1alpha2
      kind: Object
      spec:
        forProvider:
          manifest:
            apiVersion: networking.k8s.io/v1
            kind: NetworkPolicy
            metadata:
              name: default-deny-all
              namespace: carrot-storage
            spec:
              # Default: Trust no one! 🥕
              podSelector: {}
              policyTypes:
              - Ingress
              - Egress
```

This is like putting up a "NO UNAUTHORIZED VEGETABLES" sign. Pods can't run as root, can't mount sensitive host paths, and can't do other risky things that cyber-rabbits love.

## 🌐 Layer 3: Network Controls (Controlled Pathways)

Let's ensure only the right paths lead to our carrots:

```yaml
# compositions/network-security.yaml
- name: allow-frontend-to-backend
  base:
    apiVersion: kubernetes.crossplane.io/v1alpha2
    kind: Object
    spec:
      forProvider:
        manifest:
          apiVersion: networking.k8s.io/v1
          kind: NetworkPolicy
          metadata:
            name: allow-frontend-to-carrot-api
            namespace: carrot-storage
          spec:
            podSelector:
              matchLabels:
                app: carrot-api
            policyTypes:
            - Ingress
            ingress:
            - from:
              - namespaceSelector:
                  matchLabels:
                    name: frontend
              ports:
              - protocol: TCP
                port: 8080

# Also create an Azure Firewall for cluster egress
- name: azure-firewall
  base:
    apiVersion: network.azure.upbound.io/v1beta1
    kind: Firewall
    spec:
      forProvider:
        location: westeurope
        resourceGroupName: $(resource_group)
        sku:
        - name: AZFW_VNet
          tier: Standard
        ipConfiguration:
        - name: configuration
          subnetIdSelector:
            matchLabels:
              subnet: firewall
        
- name: firewall-rules
  base:
    apiVersion: network.azure.upbound.io/v1beta1
    kind: FirewallNetworkRuleCollection
    spec:
      forProvider:
        # Only allow outbound to approved vegetable suppliers
        rule:
        - name: allow-approved-egress
          protocols:
          - TCP
          destinationAddresses:
          - "20.20.20.0/24"  # Approved package repositories
          destinationPorts:
          - "443"
          sourceAddresses:
          - "10.0.0.0/16"  # Our AKS subnet
```

**The garden path analogy**: You wouldn't let people walk through your prize tomatoes to get to the carrots. Same with network traffic - everything follows designated paths.

## 📹 Layer 4: Detective Controls (Security Cameras)

Time to install cameras to watch for suspicious behavior:

```yaml
# compositions/monitoring.yaml
- name: container-insights
  base:
    apiVersion: operationsmanagement.azure.upbound.io/v1beta1
    kind: SolutionsPlan
    spec:
      forProvider:
        location: westeurope
        resourceGroupName: $(resource_group)
        plan:
        - product: OMSGallery/ContainerInsights
          publisher: Microsoft
          
- name: log-analytics-workspace
  base:
    apiVersion: operationalinsights.azure.upbound.io/v1beta1
    kind: Workspace
    spec:
      forProvider:
        location: westeurope
        resourceGroupName: $(resource_group)
        sku: PerGB2018
        retentionInDays: 30

- name: diagnostic-settings
  base:
    apiVersion: insights.azure.upbound.io/v1beta1
    kind: MonitorDiagnosticSetting
    spec:
      forProvider:
        targetResourceIdSelector:
          matchLabels:
            resource: aks-cluster
        logAnalyticsWorkspaceIdSelector:
          matchLabels:
            resource: log-analytics
        
        # Watch everything suspicious
        log:
        - category: kube-audit
          enabled: true
        - category: kube-apiserver
          enabled: true
        - category: cluster-autoscaler
          enabled: true
        
        metric:
        - category: AllMetrics
          enabled: true
```

These logs will alert you when:
- Someone tries to access carrots they shouldn't (failed auth attempts)
- Unusual API calls happen (suspicious pod creations)
- Resource usage spikes (possible crypto-mining rabbits!)

## 🚨 Layer 5: Responsive Controls (Automatic Sprinklers)

When the cameras spot trouble, we respond automatically:

```yaml
# compositions/auto-response.yaml
- name: azure-policy-assignment
  base:
    apiVersion: authorization.azure.upbound.io/v1beta1
    kind: PolicyAssignment
    spec:
      forProvider:
        policyDefinitionId: /providers/Microsoft.Authorization/policyDefinitions/
          e3576e28-8b17-4677-84c3-db2990658d64  # Kubernetes cluster containers CPU and memory limits
        resourceGroupName: $(resource_group)
        
        # Auto-remediate non-compliant resources
        remediation:
        - enabled: true

# Create alerting rules
- name: high-privilege-pod-alert
  base:
    apiVersion: insights.azure.upbound.io/v1beta1
    kind: MonitorMetricAlert
    spec:
      forProvider:
        resourceGroupName: $(resource_group)
        scopes:
        - $(aks_resource_id)
        
        criteria:
        - aggregation: Total
          metricName: pod_created_with_privileged
          operator: GreaterThan
          threshold: 0
        
        # Send immediate alerts
        action:
        - actionGroupId: $(security_team_action_group)
```

**Translation**: If a cyber-rabbit tries to create a privileged pod (running as root), Azure Policy blocks it, and your security team gets a text message faster than you can say "organic vegetables."

## 🔄 Layer 6: Recovery Controls (Seed Vault)

Finally, our backup plan for when despite all defenses, some rabbits still get through:

```yaml
# compositions/backup-recovery.yaml
- name: velero-backup
  base:
    apiVersion: kubernetes.crossplane.io/v1alpha2
    kind: Object
    spec:
      forProvider:
        manifest:
          apiVersion: v1
          kind: Namespace
          metadata:
            name: velero

- name: backup-storage-account
  base:
    apiVersion: storage.azure.upbound.io/v1beta1
    kind: Account
    spec:
      forProvider:
        resourceGroupName: $(resource_group)
        location: westeurope
        accountTier: Standard
        accountReplicationType: GRS  # Geo-redundant - seeds in multiple locations!
        
- name: backup-schedule
  base:
    apiVersion: kubernetes.crossplane.io/v1alpha2
    kind: Object
    spec:
      forProvider:
        manifest:
          apiVersion: velero.io/v1
          kind: Schedule
          metadata:
            name: daily-carrot-backup
            namespace: velero
          spec:
            schedule: "0 2 * * *"  # 2 AM daily
            template:
              includedNamespaces:
              - carrot-storage
              - carrot-api
              storageLocation: azure-backup
```

Now if cyber-rabbits eat all your carrots, you can restore from last night's backup. It's like having a seed vault in Svalbard, but for your data.

## 🎨 Putting It All Together: The Complete Garden Plan

Here's our XRD (the blueprint for our secure garden):

```yaml
# apis/secure-aks-cluster.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: secureaksclusters.platform.example.com
spec:
  group: platform.example.com
  names:
    kind: SecureAKSCluster
    plural: secureaksclusters
  claimNames:
    kind: SecureAKSClusterClaim
    plural: secureaksclusterclaims
  
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              # Garden parameters
              resourceGroup:
                type: string
                description: "Which plot of land (resource group)"
              adminGroupId:
                type: string
                description: "Who gets the master key (admin Azure AD group)"
              environment:
                type: string
                enum: [dev, staging, prod]
                description: "Type of garden (affects security levels)"
              carrotSensitivity:
                type: string
                enum: [public, internal, confidential, top-secret]
                default: confidential
                description: "How valuable are your cyber-carrots?"
            required:
            - resourceGroup
            - adminGroupId
            - environment
```

## 🚀 Deploying Your Secure Garden

Now let's plant this garden:

```bash
# 1. Install Crossplane v2
helm repo add crossplane-stable https://charts.crossplane.io/stable
helm repo update

helm install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --version v2.0.0

# 2. Install Azure provider
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-containerservice
spec:
  package: xpkg.upbound.io/upbound/provider-azure-containerservice:v1.0.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-network
spec:
  package: xpkg.upbound.io/upbound/provider-azure-network:v1.0.0
EOF

# 3. Configure Azure credentials
az ad sp create-for-rbac --sdk-auth --role Contributor \
  --scopes /subscriptions/YOUR-SUBSCRIPTION-ID > azure-credentials.json

kubectl create secret generic azure-secret \
  -n crossplane-system \
  --from-file=creds=./azure-credentials.json

kubectl apply -f - <<EOF
apiVersion: azure.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: azure-secret
      key: creds
EOF

# 4. Install our composition
kubectl apply -f compositions/

# 5. Claim your secure garden!
kubectl apply -f - <<EOF
apiVersion: platform.example.com/v1alpha1
kind: SecureAKSClusterClaim
metadata:
  name: production-carrot-garden
  namespace: default
spec:
  resourceGroup: rg-secure-carrots-prod
  adminGroupId: "YOUR-AZURE-AD-GROUP-ID"
  environment: prod
  carrotSensitivity: top-secret
EOF
```

## 🔍 Verifying Your Defenses

Let's make sure all our layers are working:

```bash
# Check identity layer
kubectl get managedclusters -o jsonpath='{.items[0].spec.forProvider.azureActiveDirectoryRoleBasedAccessControl}'

# Verify network policies are in place
kubectl get networkpolicies -n carrot-storage

# Check monitoring is active
az monitor log-analytics workspace show \
  --resource-group rg-secure-carrots-prod \
  --workspace-name YOUR-WORKSPACE

# Test responsive controls (try to create a privileged pod)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: sneaky-rabbit
spec:
  containers:
  - name: bad-container
    image: nginx
    securityContext:
      privileged: true  # This should be blocked!
EOF

# Should see: Error from server (Forbidden): admission webhook denied

# Verify backups are running
kubectl get schedules -n velero
```

## 🎓 Lessons from the Garden

What we've learned about defense-in-depth:

### 1. **No Single Layer is Perfect**
Just like a fence won't stop a determined rabbit, no single security control is foolproof. Cyber-rabbits are clever - they'll find ways around your identity controls, they'll try to tunnel under your network policies, and they'll attempt to disguise themselves to avoid your cameras.

### 2. **Layers Work Together**
When your identity layer catches 80% of attacks, your network layer catches 80% of what gets through, and so on - you end up with 99.9%+ protection. Math!

### 3. **Automate the Boring Stuff**
Crossplane v2's composition pipelines let you codify this entire garden plan. No more manual clicking in Azure Portal at 2 AM because a cyber-rabbit showed up.

### 4. **Defense is Ongoing**
Gardens need weeding, fences need mending, and security needs updating. Your Crossplane compositions should evolve as new threats emerge.

## 🐛 Common Pitfalls (Or: How Rabbits Actually Get In)

### Mistake 1: "It's Just Dev, We Don't Need Security"
```yaml
# ❌ DON'T DO THIS
environment: dev
carrotSensitivity: public  # "It's fine, it's just test data"
```

Cyber-rabbits don't care if it's production or dev. They'll happily eat test carrots while learning your garden layout for the real heist later.

### Mistake 2: "Too Many Policies Will Slow Us Down"
```yaml
# ❌ DANGER ZONE
networkPolicy: none  # "Network policies are hard, let's skip them"
podSecurityStandards: privileged  # "Developers need root everywhere"
```

You know what's slower than implementing security? Recovering from a breach. And explaining to your CEO why all the customer carrots are gone.

### Mistake 3: "I'll Add Security Later"
Later never comes. Cyber-rabbits don't wait for your next sprint.

## 📊 Measuring Success

How do you know your defense-in-depth is working?

```bash
# Check blocked attempts (rabbits turned away at the gate)
kubectl logs -n kube-system -l component=kube-apiserver | \
  grep "Forbidden"

# Review audit logs for suspicious patterns
az monitor log-analytics query \
  --workspace YOUR-WORKSPACE \
  --analytics-query 'KubeAuditLogs | where ResponseStatus == 403'

# Count backup success rate (seed vault health)
kubectl get backups -n velero \
  -o jsonpath='{.items[?(@.status.phase=="Completed")].metadata.name}' | \
  wc -l
```

Success metrics:
- **Identity Layer**: 99%+ authentication success rate for legitimate users
- **Network Layer**: Zero unauthorized cross-namespace communication
- **Detective Layer**: < 5 minutes to detect anomalies
- **Responsive Layer**: Automatic remediation of 80%+ policy violations
- **Recovery Layer**: < 15 minutes to restore from backup

## 🚀 Next Steps

Want to take your garden security further?

1. **Add Service Mesh**: Istio or Linkerd for even more granular network control
2. **Implement GitOps**: Flux or ArgoCD to ensure only approved changes reach your garden
3. **Add Runtime Security**: Falco for detecting suspicious behavior at runtime
4. **Implement Secrets Management**: Azure Key Vault integration for your most sensitive seeds

## 🎬 Conclusion

We've built a production-ready, defense-in-depth secured Azure AKS cluster using Crossplane v2. Your cyber-carrots are now protected by:

✅ Identity controls (Azure AD + RBAC)
✅ Protective controls (Pod Security Standards)  
✅ Network controls (Network Policies + Firewall)
✅ Detective controls (Azure Monitor + Insights)
✅ Responsive controls (Azure Policy auto-remediation)
✅ Recovery controls (Velero backups)

Are cyber-rabbits going to try to eat your carrots anyway? Absolutely. Will they succeed? Not if you maintain your garden properly!

Remember: Security isn't a one-time task - it's a continuous practice, just like gardening. Water your defenses, weed out vulnerabilities, and keep those cyber-rabbits at bay.

Now go forth and protect those prize-winning cyber-carrots! 🥕🔒

---

**Full source code and examples**: [github.com/software-journey/defense-in-depth-of-cyber-carrots](https://github.com/software-journey/defense-in-depth-of-cyber-carrots)

**Questions? Found a hole in the fence?** Drop a comment below!

*Special thanks to the Google Cloud Security course for the garden metaphor that made this article possible. If you're interested in diving deeper into cloud security fundamentals, check out their excellent [Defense-in-Depth module](https://www.skills.google/paths/419/course_templates/1300/video/579179).*

---

*This article is part of our Crossplane Adventures series. Previously: [Testing Your Cloud Infrastructure Like IKEA Furniture: A Guide to Crossplane v2 End-to-End Testing](#)*

---

### Tags
#crossplane #kubernetes #azure #security #devops #infrastructure-as-code #defense-in-depth #cloudsecurity #aks #devsecops
