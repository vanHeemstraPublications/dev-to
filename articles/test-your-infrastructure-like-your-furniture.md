---
title: "Testing Your Cloud Infrastructure Like IKEA Furniture: A Guide to Crossplane v2 End-to-End Testing"
published: false
description: "Learn how to test Crossplane v2 compositions with end-to-end testing, explained through the surprisingly apt metaphor of assembling IKEA furniture"
tags: [kubernetes, crossplane, testing, devops]
series: ""
canonical_url: ""
cover_image: https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/test-your-infrastructure-like-your-furniture.png
organization: "the-software-s-journey"
---

# Testing Your Cloud Infrastructure Like IKEA Furniture: A Guide to Crossplane v2 End-to-End Testing

Ever bought an IKEA BILLY bookshelf? You know the drill: open the box, check all the pieces are there, follow the instructions, tighten the screws, and give it a good shake to make sure it won't collapse when you load it with your collection of unread programming books.

Testing Crossplane v2 infrastructure is remarkably similar. Except instead of a wobbly bookshelf, you're building cloud resources. And instead of an Allen key, you're using YAML. (Arguably, both can be equally frustrating at times.)

In this guide, I'll walk you through setting up end-to-end (E2E) testing for Crossplane v2, using our IKEA metaphor to make the concepts stick like... well, like properly applied IKEA wood glue.

## Why Test Your Infrastructure? (Or: Why You Shouldn't Skip the Assembly Instructions)

Remember that time you *thought* you could assemble IKEA furniture without reading the instructions? And then you had leftover screws? And the drawer didn't quite close right?

That's what running Crossplane compositions in production without E2E testing feels like.

**E2E testing for Crossplane validates that:**
- All the pieces (resources) are actually created ✅
- They're assembled correctly (configured properly) ✅
- They work together (networking, permissions, dependencies) ✅
- They can be disassembled cleanly (deletion works) ✅

## The IKEA Furniture Assembly Metaphor

Let's break down our metaphor:

| IKEA Furniture | Crossplane v2 |
|----------------|---------------|
| **Instruction manual** | XRD (CompositeResourceDefinition) |
| **Assembly steps** | Composition with pipeline functions |
| **Individual pieces** | Managed Resources (Storage Account, VNet, etc.) |
| **Assembled furniture** | Composite Resource (XR) |
| **Quality check** | E2E Test Suite |
| **Allen key** | kubectl (both mysterious and essential) |

## Prerequisites: What's in Your Toolbox?

Before we start assembling (testing), let's make sure you have all the tools. Unlike IKEA, these tools aren't included in the box:

```bash
# The essentials (your "Allen keys")
brew install azure-cli kubectl helm jq
brew install fluxcd/tap/flux
brew install crossplane

# The nice-to-haves (your "electric screwdriver")
brew install k9s  # Visual cluster exploration
brew install tree # Directory visualization
```

Verify everything works:

```bash
az version
kubectl version --client
helm version
flux --version
crossplane version
```

> **Pro tip**: If any of these fail, don't panic! Check the error messages. They're usually more helpful than IKEA's pictographic instructions.

## Step 1: Building Your Workshop (Setting Up AKS)

First, we need a place to assemble our furniture. Let's create an AKS cluster:

```bash
# Set up your environment variables
export RESOURCE_GROUP="crossplane-e2e-rg"
export LOCATION="westeurope"
export CLUSTER_NAME="crossplane-e2e-aks"
export CROSSPLANE_VERSION="2.1.0"

# Log into Azure
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create your workshop (resource group)
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --tags environment=development managedBy=crossplane

# Build the workbench (AKS cluster)
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-managed-identity \
  --network-plugin azure \
  --generate-ssh-keys
```

This takes about 5-10 minutes. Perfect time for a Swedish meatball break! 🍝

```bash
# Connect your tools to the workbench
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME

# Verify you're connected
kubectl get nodes
```

## Step 2: Installing Crossplane (Getting Your Assembly Instructions Ready)

Now let's install Crossplane v2. Think of this as opening the IKEA box and laying out all the instruction sheets:

```bash
# Add the Crossplane repository
helm repo add crossplane-stable https://charts.crossplane.io/stable
helm repo update

# Install Crossplane v2
helm install crossplane \
  --namespace crossplane-system \
  --create-namespace \
  crossplane-stable/crossplane \
  --version $CROSSPLANE_VERSION \
  --wait

# Check that Crossplane is running
kubectl get pods -n crossplane-system
```

You should see something like:

```
NAME                                      READY   STATUS    RESTARTS   AGE
crossplane-xxx                            1/1     Running   0          1m
crossplane-rbac-manager-xxx               1/1     Running   0          1m
```

## Step 3: Setting Up Azure Authentication (The Security Sticker)

Just like IKEA furniture has those "quality checked" stickers, we need to authenticate Crossplane with Azure:

```bash
# Get your subscription ID
export SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create a service principal (think of it as the QA inspector's badge)
SP_OUTPUT=$(az ad sp create-for-rbac \
  --name "crossplane-e2e-${CLUSTER_NAME}" \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --output json)

# Extract and save the credentials
export AZURE_CLIENT_ID=$(echo $SP_OUTPUT | jq -r '.appId')
export AZURE_CLIENT_SECRET=$(echo $SP_OUTPUT | jq -r '.password')
export AZURE_TENANT_ID=$(echo $SP_OUTPUT | jq -r '.tenant')

# Create a Kubernetes secret
kubectl create secret generic azure-secret \
  --namespace crossplane-system \
  --from-literal=creds="[default]
client_id = $AZURE_CLIENT_ID
client_secret = $AZURE_CLIENT_SECRET
tenant_id = $AZURE_TENANT_ID
subscription_id = $SUBSCRIPTION_ID"
```

> **Important**: Save these credentials! You'll need them later, and unlike that bag of extra IKEA screws, you can't just shrug and throw them in a drawer.

## Step 4: Installing Azure Providers (Getting the Right Pieces)

Crossplane v2 uses modular providers. It's like ordering specific IKEA departments: kitchen, bedroom, storage. We need to install the Azure providers we'll use:

```bash
# Install the providers we need
cat <<EOF | kubectl apply -f -
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-storage
spec:
  package: xpkg.upbound.io/upbound/provider-azure-storage:v1.3.0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-network
spec:
  package: xpkg.upbound.io/upbound/provider-azure-network:v1.3.0
EOF

# Wait for providers to install (grab another coffee ☕)
kubectl wait provider --all \
  --for=condition=Healthy \
  --timeout=600s
```

Now configure the providers to use our Azure credentials:

```bash
cat <<EOF | kubectl apply -f -
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
```

## Step 5: Creating Your First "Furniture" (XRD and Composition)

Here's where it gets fun! We're going to create an XRD (the instruction manual) and a Composition (the assembly steps) for a Storage Account.

**The XRD (Instruction Manual):**

```yaml
# config/xrds/xstorage-account.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xstorageaccounts.storage.example.io
spec:
  group: storage.example.io
  names:
    kind: XStorageAccount
    plural: xstorageaccounts
  scope: Namespaced
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
              parameters:
                type: object
                properties:
                  location:
                    type: string
                    default: westeurope
                  accountTier:
                    type: string
                    enum: [Standard, Premium]
                    default: Standard
                  replicationType:
                    type: string
                    enum: [LRS, GRS, RAGRS, ZRS]
                    default: LRS
                  resourceGroupName:
                    type: string
                required:
                - resourceGroupName
```

**The Composition (Assembly Steps):**

In Crossplane v2, we use **pipeline mode** with composition functions. It's like having step-by-step assembly instructions instead of just a picture:

```yaml
# config/compositions/storage-account.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xstorageaccounts.storage.example.io
  labels:
    provider: azure
    type: standard
spec:
  compositeTypeRef:
    apiVersion: storage.example.io/v1alpha1
    kind: XStorageAccount
  
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      # First piece: The resource group (the room)
      - name: resourcegroup
        base:
          apiVersion: azure.m.upbound.io/v1beta1
          kind: ResourceGroup
          spec:
            forProvider:
              location: westeurope
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.location
          toFieldPath: spec.forProvider.location
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.resourceGroupName
          toFieldPath: metadata.name

      # Second piece: The storage account (the furniture)
      - name: storageaccount
        base:
          apiVersion: storage.azure.m.upbound.io/v1beta2
          kind: Account
          spec:
            forProvider:
              accountReplicationType: LRS
              accountTier: Standard
              resourceGroupNameSelector:
                matchControllerRef: true
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.accountTier
          toFieldPath: spec.forProvider.accountTier
        - type: ToCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: status.storageAccountName
        readinessChecks:
        - type: MatchString
          fieldPath: status.atProvider.provisioningState
          matchString: Succeeded
  
  - step: auto-ready
    functionRef:
      name: function-auto-ready
```

Install the composition functions first:

```bash
cat <<EOF | kubectl apply -f -
---
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.2.1
---
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-auto-ready
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-auto-ready:v0.2.1
EOF

# Wait for functions to be ready
kubectl wait function --all --for=condition=Healthy --timeout=300s
```

Now apply your XRD and Composition:

```bash
kubectl apply -f config/xrds/xstorage-account.yaml
kubectl apply -f config/compositions/storage-account.yaml
```

## Step 6: The Quality Check (Setting Up E2E Tests)

Now comes the crucial part: testing! We'll use **kuttl** (Kubernetes Test Tool) - think of it as your IKEA quality inspector.

Install kuttl:

```bash
KUTTL_VERSION=0.15.0
wget -q https://github.com/kudobuilder/kuttl/releases/download/v${KUTTL_VERSION}/kubectl-kuttl_${KUTTL_VERSION}_linux_x86_64
chmod +x kubectl-kuttl_${KUTTL_VERSION}_linux_x86_64
sudo mv kubectl-kuttl_${KUTTL_VERSION}_linux_x86_64 /usr/local/bin/kubectl-kuttl
```

Create your test structure:

```bash
mkdir -p tests/e2e/01-storage-account/{00-setup,01-verify,02-cleanup}
```

**Test Step 1: Create the furniture (00-setup)**

```yaml
# tests/e2e/01-storage-account/00-setup/00-xr-storage.yaml
apiVersion: storage.example.io/v1alpha1
kind: XStorageAccount
metadata:
  name: test-storage-e2e-001
  namespace: default
spec:
  parameters:
    location: westeurope
    accountTier: Standard
    replicationType: LRS
    resourceGroupName: crossplane-e2e-test-rg
  compositionSelector:
    matchLabels:
      provider: azure
      type: standard
```

```yaml
# tests/e2e/01-storage-account/00-setup/00-assert.yaml
apiVersion: storage.example.io/v1alpha1
kind: XStorageAccount
metadata:
  name: test-storage-e2e-001
  namespace: default
status:
  conditions:
  - type: Ready
    status: "True"
  - type: Synced
    status: "True"
```

**Test Step 2: Verify it's sturdy (01-verify)**

```yaml
# tests/e2e/01-storage-account/01-verify/00-assert-storage.yaml
apiVersion: storage.azure.m.upbound.io/v1beta2
kind: Account
metadata:
  namespace: default
  ownerReferences:
  - apiVersion: storage.example.io/v1alpha1
    kind: XStorageAccount
    name: test-storage-e2e-001
status:
  conditions:
  - type: Ready
    status: "True"
```

**Test Step 3: Check in the real world (Azure)**

```yaml
# tests/e2e/01-storage-account/01-verify/01-verify-azure.yaml
apiVersion: kuttl.dev/v1beta1
kind: TestAssert
commands:
- script: |
    # Get the storage account name
    STORAGE_NAME=$(kubectl get xstorageaccount test-storage-e2e-001 \
      -n default \
      -o jsonpath='{.status.storageAccountName}')
    
    # Verify it exists in Azure (give it a shake!)
    az storage account show \
      --name $STORAGE_NAME \
      --resource-group crossplane-e2e-test-rg \
      --query "provisioningState" \
      --output tsv | grep -q "Succeeded"
```

**Test Step 4: Disassemble (02-cleanup)**

```yaml
# tests/e2e/01-storage-account/02-cleanup/00-delete.yaml
apiVersion: storage.example.io/v1alpha1
kind: XStorageAccount
metadata:
  name: test-storage-e2e-001
  namespace: default
$patch: delete
```

Create the test configuration:

```yaml
# tests/e2e/01-storage-account/kuttl-test.yaml
apiVersion: kuttl.dev/v1beta1
kind: TestSuite
metadata:
  name: storage-account-e2e
timeout: 600
parallel: 1
testDirs:
- .
```

## Step 7: Running Your Tests (The Moment of Truth)

Time to run the quality check! This is like that satisfying moment when you tighten the last screw and give the furniture a shake to make sure it's stable:

```bash
# Run the E2E tests
kubectl kuttl test tests/e2e/01-storage-account/

# In another terminal, watch the magic happen
watch kubectl get xstorageaccount,account,resourcegroup
```

You should see output like:

```
=== RUN   kuttl
    harness.go:462: starting setup
    harness.go:252: running tests using configured kubeconfig.
    harness.go:285: Successful connection to cluster at: https://crossplane-e2e-aks-xxx.hcp.westeurope.azmk8s.io:443
=== RUN   kuttl/harness
=== RUN   kuttl/harness/storage-account-e2e
=== PAUSE kuttl/harness/storage-account-e2e
=== CONT  kuttl/harness/storage-account-e2e
    logger.go:42: 12:34:56 | storage-account-e2e | Creating namespace: kuttl-test-xxx
    logger.go:42: 12:34:57 | storage-account-e2e/0-setup | starting test step 0-setup
    logger.go:42: 12:35:30 | storage-account-e2e/0-setup | test step completed 0-setup
    logger.go:42: 12:35:30 | storage-account-e2e/1-verify | starting test step 1-verify
    logger.go:42: 12:35:45 | storage-account-e2e/1-verify | test step completed 1-verify
    logger.go:42: 12:35:45 | storage-account-e2e/2-cleanup | starting test step 2-cleanup
    logger.go:42: 12:36:00 | storage-account-e2e/2-cleanup | test step completed 2-cleanup
=== CONT  kuttl
    harness.go:405: run tests finished
    harness.go:513: cleaning up
    harness.go:570: removing temp folder: ""
--- PASS: kuttl (65.23s)
    --- PASS: kuttl/harness (0.00s)
        --- PASS: kuttl/harness/storage-account-e2e (65.12s)
PASS
```

✨ **If you see PASS, congratulations!** Your infrastructure furniture is assembled correctly!

## Troubleshooting (When Your Drawer Won't Close)

### Problem: Provider not becoming healthy

```bash
# Check provider logs
kubectl logs -n crossplane-system -l pkg.crossplane.io/provider=provider-azure-storage

# Usually it's authentication - double-check your secret
kubectl get secret azure-secret -n crossplane-system
```

### Problem: XR stuck in "not ready"

```bash
# Check what's wrong
kubectl describe xstorageaccount test-storage-e2e-001

# Check the managed resources
kubectl get managed

# Check Crossplane logs
kubectl logs -n crossplane-system deployment/crossplane -f
```

### Problem: Test timeout

This usually means Azure is taking longer than expected. You can increase the timeout in your `kuttl-test.yaml`:

```yaml
timeout: 900  # Increase from 600 to 900 seconds
```

## Bonus: GitOps with Flux (Assembly Instructions on Demand)

Want to make this even more automated? Add Flux for GitOps! It's like having IKEA deliver your furniture AND the assembly instructions automatically update when they improve them:

```bash
# Install Flux
flux bootstrap github \
  --owner=YOUR_GITHUB_USER \
  --repository=crossplane-e2e-fleet \
  --branch=main \
  --path=./clusters/dev \
  --personal

# Create GitRepository
cat <<EOF | kubectl apply -f -
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: crossplane-configs
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/YOUR_USER/YOUR_REPO
  ref:
    branch: main
EOF

# Create Kustomization
cat <<EOF | kubectl apply -f -
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: crossplane-xrds
  namespace: flux-system
spec:
  interval: 5m
  path: ./config/xrds
  prune: true
  sourceRef:
    kind: GitRepository
    name: crossplane-configs
EOF
```

Now whenever you push changes to your Git repo, Flux automatically applies them to your cluster!

## Cleaning Up (Because Storage Costs Money)

When you're done testing:

```bash
# Delete test resources
kubectl delete xstorageaccount --all

# Or delete everything
az group delete --name crossplane-e2e-rg --yes --no-wait
```

## The Complete Picture (Full Source Code)

All the code from this tutorial is available in my GitHub repository:

🔗 **[github.com/vanHeemstraSystems/learning-crossplane-e2e-testing](https://github.com/vanHeemstraSystems/learning-crossplane-e2e-testing)**

The repo includes:
- Complete setup script for automation
- Additional test examples (VNets, PostgreSQL)
- Helper scripts for running and cleaning up tests
- Flux GitOps configurations
- Troubleshooting guides

## Key Takeaways (Your Assembly Summary Sheet)

1. **E2E testing validates your entire Crossplane setup** - from XRD to actual Azure resources
2. **Crossplane v2 uses pipeline mode** - more powerful and flexible than v1
3. **Test in layers**: Create → Verify → Cleanup (just like assembling furniture)
4. **Automate with tools**: kuttl for testing, Flux for GitOps
5. **Always clean up test resources** - Azure charges are real!

## What's Next?

Now that you know how to test your "IKEA furniture," you can:

- Create more complex compositions (networks, databases, full applications)
- Integrate E2E tests into your CI/CD pipeline
- Build a platform with Backstage for self-service infrastructure
- Add cost tracking and governance policies

Remember: just like IKEA furniture, Crossplane infrastructure is much better when you follow the instructions and test that everything fits together properly. Happy building! 🔧

---

*Got questions? Drop them in the comments! I'd love to hear about your Crossplane testing experiences.*

*If you found this helpful, give it a ❤️ and share it with someone who's also wrangling cloud infrastructure!*

---

**About the Author**: I'm Willem, a Cloud Engineer transitioning to platform engineering. I believe complex infrastructure concepts should be accessible to everyone - even if it means comparing them to Swedish furniture. Follow me for more cloud-native content!
