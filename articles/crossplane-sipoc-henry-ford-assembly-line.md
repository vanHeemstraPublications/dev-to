---
title: "Any Customer Can Have Any Cloud Resource, Provided It Comes Off the Assembly Line: Crossplane v2 and the SIPOC Factory Floor"
published: true
description: "Henry Ford revolutionised manufacturing with the assembly line. Crossplane v2 does the same for cloud infrastructure. Join us as old Henry walks us through Supplier, Input, Process, Output, Consumer — and explains why your platform team is basically running a factory floor, minus the child labour and questionable labour relations."
tags: [crossplane, kubernetes, platformengineering, devops]
series: "Infrastructure-as-Code Adventures"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/crossplane-sipoc-assembly-line.png"
organization: "the-software-s-journey"
---

*How Crossplane v2 orchestrates your cloud infrastructure like Henry Ford orchestrated the Model T — with stunning efficiency, total standardisation, and a philosophy that any customer can have any colour, as long as it’s black. Or in our case: any resource, as long as it’s defined in a Composition.*

## Introduction

It’s 1913. Highland Park, Michigan. Henry Ford is pacing the factory floor, twirling his moustache, and muttering something darkly about chassis frames not moving fast enough. Then, in a moment of industrial genius that would define the twentieth century, he invents the moving assembly line. Workers stay put. The work comes to them. Every step is standardised. Every output is predictable. Every Model T rolls off the end looking exactly like the last one.

The output was so standardised, in fact, that Ford famously told customers they could have any colour they liked — as long as it was black. Not because he lacked imagination. Because standardisation was *the point*.

Fast-forward 111 years. You’re on a platform engineering team. Application developers are pinging you on Slack at 2pm (and 2am, and on a Friday afternoon when you were *this close* to starting the weekend). “Can I have an Azure Resource Group?” “Can I have an AKS cluster?” “Can I have an Azure Subscription?” You’re the factory. They’re the customers. And right now, your production line is a shared Google Doc, a Jira ticket nobody reads, and a mild sense of existential dread.

Enter **Crossplane v2**.

And Henry Ford, back from the dead and extremely opinionated about YAML.

-----

## The SIPOC Mental Model (Straight Off the Factory Floor)

Before we look at a single line of YAML, let’s borrow a concept from the world of Lean process improvement: **SIPOC**.

**S**upplier → **I**nput → **P**rocess → **O**utput → **C**onsumer

Ford used this pattern at Highland Park — he just didn’t call it that. He was too busy being revolutionary and paying his workers five dollars a day, which was either enlightened capitalism or a clever scheme to ensure they could afford to buy the cars they built. Possibly both.

Here’s how his factory maps to Crossplane v2:

|SIPOC Stage |Ford’s Factory (1913)                            |Crossplane v2 (Now)                         |
|------------|-------------------------------------------------|--------------------------------------------|
|**Supplier**|Steel mills, rubber plantations, glass factories |Providers, Composition Functions            |
|**Input**   |Raw materials: steel, rubber, glass, dreams      |XRD schema + XR instance                    |
|**Process** |The moving assembly line itself                  |Composition (Pipeline mode)                 |
|**Output**  |A gleaming Model T in any colour you like (black)|A managed cloud resource in Azure           |
|**Consumer**|A proud American buying their first automobile   |Your app team, self-serving infra via GitOps|

“Gentlemen,” Ford announces to the assembled platform engineers, most of whom are wearing hoodies and looking slightly alarmed, “you have been hand-crafting automobiles. One. At. A. Time. Bespoke. Artisanal. *Slow.*”

He gestures at the chaos of tickets, Slack messages, and manually-clicked Azure portals.

“I see your problem. You have no assembly line.”

He’s right. And Crossplane v2 is about to fix that.

-----

## The Supplier: Raw Materials Come From Somewhere

Ford didn’t grow his own rubber or smelt his own steel. He had *suppliers* — raw material producers who fed the factory with exactly what it needed to build cars. Without them, the assembly line grinds to a halt and everyone goes home disappointed.

In Crossplane v2, your **Suppliers** are:

1. **Providers** — the connections to cloud APIs (Azure, AWS, GCP). They’re your steel mills: they provide the raw managed resource types your platform will compose.
1. **Composition Functions** — the specialised tools that know *how* to shape those raw materials. They’re your rubber vulcanisers and glass cutters.

Let’s install ours. Ford would call this “building the supply chain.” We call it “applying some YAML.”

### Installing the Azure Provider (Your Steel Mill)

```yaml
# provider-azure.yaml
# The steel mill — provides every Azure resource type we could want
# (and several we definitely don't, but they come along for the ride)
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-resources
spec:
  package: xpkg.upbound.io/upbound/provider-azure-resources:v1
  # Ford didn't question where the steel came from. We don't question the package registry.
  runtimeConfigRef:
    name: provider-azure-runtime
```

```yaml
# provider-config.yaml
# The supplier contract — credentials and which Azure subscription to use
# Ford had to sign contracts with Carnegie Steel. We sign in with a Service Principal.
apiVersion: azure.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: azure-provider-config
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: azure-credentials
      key: credentials
      # Keep this secret safer than Ford kept his assembly line patents
```

### Installing Composition Functions (Your Specialist Tools)

Ford’s factory had specialist workers who knew exactly how to attach a chassis, fit a windshield, or bolt on an engine. In Crossplane v2, **Functions** are those specialists — they know how to transform your declarative intent into actual managed resources.

```yaml
# functions/function-patch-and-transform.yaml
# The chassis-fitting specialist
# Knows how to take XR fields and patch them onto managed resources
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.8.0
```

```yaml
# functions/function-go-templating.yaml
# The body-shop specialist — when you need more flexibility than simple patches
# Supports Go templates for complex transformations
# Ford's equivalent: the worker who could improvise when the part didn't quite fit
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-go-templating
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-go-templating:v0.7.0
```

```yaml
# functions/function-auto-ready.yaml
# The quality inspector at the end of the line
# Marks the XR as READY when all composed resources are healthy
# Ford had a man check every car before it left the factory. This is that man.
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-auto-ready
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-auto-ready:v0.3.0
```

```bash
# Apply everything in the right order
# (Ford learned the hard way: steel before bolts, bolts before engine)
kubectl apply -f providers/
kubectl apply -f functions/

# Check suppliers are healthy
kubectl get providers
kubectl get functions

# Expected output — what a healthy supply chain looks like:
# NAME                         INSTALLED   HEALTHY   PACKAGE                                                    AGE
# provider-azure-resources     True        True      xpkg.upbound.io/upbound/provider-azure-resources:v1       2m
#
# NAME                                INSTALLED   HEALTHY   AGE
# function-patch-and-transform        True        True      90s
# function-go-templating              True        True      90s
# function-auto-ready                 True        True      90s
```

Ford’s supply chain lesson: *know where your raw materials come from, and make sure they’re reliable.* A supplier who delivers inconsistently is worse than no supplier at all.

-----

## The Input: Defining What You’re Building

At Highland Park, Ford’s engineers didn’t just throw steel at workers and hope for the best. They had **blueprints** — precise specifications for every part. The blueprint told the factory: “We are building a Model T. It requires these inputs. Nothing else.”

In Crossplane v2, your **Input** has two layers:

1. **The XRD (CompositeResourceDefinition)** — the blueprint. It defines what parameters consumers can pass in. This is the platform team’s *contract* with the world.
1. **The XR (Composite Resource)** — the actual order. An instance of that blueprint, submitted by a consumer, specifying their particular values.

> **Crossplane v2 key change**: XRDs now use `apiVersion: apiextensions.crossplane.io/v2`. The `scope` field defaults to `Namespaced`. Claims (`claimNames`) are **not supported** in v2 — XRs are consumed directly. This is Ford removing the middle-man dealership and letting customers order directly from the factory.

### The XRD: Your Blueprint (The Factory Specification)

```yaml
# apis/v1alpha1/azure-resource-group/xrd-01.yaml
#
# Henry Ford's equivalent: the engineering specification document.
# "A Model T shall require: one engine, four wheels, one chassis.
#  Colour options: black."
#
# Our equivalent:
# "An Azure Resource Group shall require: one name, one location.
#  Colour options: whatever tags the consumer provides."

apiVersion: apiextensions.crossplane.io/v2          # v2 — not v1. This matters.
kind: CompositeResourceDefinition
metadata:
  # The XRD name is <plural>.<group> — Crossplane is strict about this
  # Like Ford labelling every blueprint "MODEL-T-SPEC-001" not "Car Thing"
  name: xazureresourcegroups.platform.example.com
spec:
  scope: Namespaced                                  # v2 default: Namespaced. Explicit is better.
  group: platform.example.com                        # Your platform's API group
  names:
    kind: XAzureResourceGroup                        # The 'X' prefix = Composite Resource convention
    plural: xazureresourcegroups
  # claimNames: intentionally absent
  # Claims are not supported in apiextensions.crossplane.io/v2
  # Ford would say: "Order from the factory directly. No dealerships."

  versions:
    - name: v1alpha1
      served: true         # This version accepts requests
      referenceable: true  # Compositions reference this version
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                parameters:
                  type: object
                  description: "The order form. What the consumer fills in."
                  required:
                    - resourceGroupName
                    - location
                  properties:
                    resourceGroupName:
                      type: string
                      description: "Name for the Azure Resource Group"
                      # Ford: "What do you want on the nameplate?"
                    location:
                      type: string
                      description: "Azure region where the Resource Group will live"
                      enum:
                        - westeurope
                        - northeurope
                        - eastus
                        - eastus2
                      # Ford: "Which factory depot should we deliver to?"
                    environment:
                      type: string
                      description: "Target environment — affects tagging and policies"
                      enum:
                        - dev
                        - test
                        - prod
                      default: dev
                      # Ford: "Standard model or deluxe? (We make them the same anyway)"
                    costCenter:
                      type: string
                      description: "Cost center for billing tags"
                      # Ford: "Who's paying? Sign here."
            status:
              type: object
              description: "What the factory reports back after building"
              properties:
                resourceGroupId:
                  type: string
                  description: "The Azure Resource ID of the provisioned Resource Group"
                  # Ford: "Your car's serial number — proof it was built"
```

```bash
# Apply the XRD — register the blueprint with the factory
kubectl apply -f apis/v1alpha1/azure-resource-group/xrd-01.yaml

# Crossplane now creates a new Kubernetes CRD for XAzureResourceGroup
# The factory has accepted the engineering specification
kubectl get xrd xazureresourcegroups.platform.example.com

# Output:
# NAME                                          ESTABLISHED   OFFERED   AGE
# xazureresourcegroups.platform.example.com     True          True      30s
```

### The XR: Placing an Order at the Factory Counter

Now a consumer can place an order. In Crossplane v2, this is an XR submitted directly into their namespace.

> **Crossplane v2 key change**: All Crossplane machinery (`compositionRef`, `compositionRevisionRef`, `resourceRefs`) now lives under `spec.crossplane`. This keeps the consumer-facing `spec.parameters` clean — they don’t need to see the factory’s internal workings, just like a Model T buyer didn’t care about the assembly line choreography, only that the car arrived.

```yaml
# apis/v1alpha1/azure-resource-group/xr-01.yaml
#
# This is the customer's order form.
# Ford: "Name, delivery address, standard or deluxe? Sign here."
# Us: "resourceGroupName, location, environment? Apply here."

apiVersion: platform.example.com/v1alpha1
kind: XAzureResourceGroup
metadata:
  name: team-atlas-dev-rg
  namespace: team-atlas                              # v2: namespace-scoped, no Claims needed
  # Ford: "Order placed at the Highland Park counter by Team Atlas"
spec:
  # Consumer-facing parameters — clean, no Crossplane noise
  # This is what the developer sees and fills in
  parameters:
    resourceGroupName: atlas-dev-resources
    location: westeurope
    environment: dev
    costCenter: "CC-ATLAS-001"

  # Crossplane v2: all machinery under spec.crossplane
  # The consumer doesn't need to understand this, just like
  # a Model T buyer didn't need to understand the production schedule
  crossplane:
    compositionRef:
      name: xazureresourcegroup-azure-v1alpha1
      # "Please build this using the standard azure composition"
      # Ford: "Standard Model T, please. Not the experimental one."
```

```bash
# Submit the order to the factory
kubectl apply -f apis/v1alpha1/azure-resource-group/xr-01.yaml

# Watch Crossplane pick it up and start building
kubectl get xazureresourcegroup team-atlas-dev-rg -n team-atlas

# Output — the factory floor status board:
# NAME                  SYNCED   READY   COMPOSITION                              AGE
# team-atlas-dev-rg     True     True    xazureresourcegroup-azure-v1alpha1       45s
```

Ford’s Input lesson: *the blueprint (XRD) defines what can be ordered; the order form (XR) is the actual request.* Separate them clearly, and the factory can process thousands of orders without confusion.

-----

## The Process: The Moving Assembly Line

Here’s where the magic happens. Ford’s assembly line didn’t build a car from a single huge machine — it was a **pipeline of specialised stations**, each doing one job perfectly before passing the work to the next.

Crossplane v2 **Compositions** work identically. A `mode: Pipeline` Composition is a sequence of Function steps, each transforming the XR’s desired state a little further, until the final output is a fully specified set of managed resources.

> **Crossplane v2 note**: Compositions still use `apiVersion: apiextensions.crossplane.io/v1`. Only the XRD moved to v2. Compositions remain on v1 — this is a common gotcha, like expecting the assembly line to be redesigned just because you updated the order form.

```
Ford's assembly line stations:
  Station 1: Fit the engine                          → Step 1: function-patch-and-transform
  Station 2: Attach the chassis                      → Step 2: function-go-templating (if needed)
  Station 3: Fit the body                            → Step 3: more patches
  Station 4: Final inspection                        → Step N: function-auto-ready

Each station receives the work-in-progress, does its job, passes it on.
Each Function receives the observed/desired state, transforms it, passes it on.
```

### The Composition: Your Assembly Line

```yaml
# apis/v1alpha1/azure-resource-group/composition-01.yaml
#
# This is the assembly line itself.
# Ford designed every station, every movement, every tool placement.
# We define every pipeline step, every patch, every transformation.

apiVersion: apiextensions.crossplane.io/v1          # Compositions stay on v1. Don't forget this.
kind: Composition
metadata:
  name: xazureresourcegroup-azure-v1alpha1
  labels:
    provider: azure
    product: resource-group
    # Ford labelled every assembly line variant. We label ours.
spec:
  # Which XR type does this assembly line handle?
  # Ford: "This line builds Model Ts. Not Model As. Model Ts."
  compositeTypeRef:
    apiVersion: platform.example.com/v1alpha1
    kind: XAzureResourceGroup

  # Crossplane v2: Pipeline mode is the way forward
  # The old inline 'resources' mode is to Pipeline mode
  # what horse-drawn wagons were to Ford's assembly line
  mode: Pipeline

  pipeline:
    # ─────────────────────────────────────────────────────────────────
    # ASSEMBLY STATION 1: Patch and Transform
    # Ford's engine-fitting station: take the raw XR fields and
    # stamp them onto the managed resource blueprint
    # ─────────────────────────────────────────────────────────────────
    - step: patch-and-transform
      functionRef:
        name: function-patch-and-transform
      input:
        apiVersion: pt.fn.crossplane.io/v1beta1
        kind: Resources
        resources:
          # The actual managed resource we're building
          # Ford: "This is the car body. Everything gets stamped onto it."
          - name: azure-resource-group
            base:
              apiVersion: azure.upbound.io/v1beta1
              kind: ResourceGroup
              spec:
                forProvider:
                  location: ""   # Will be stamped in from XR below
                  tags:
                    ManagedBy: crossplane
                    # Additional tags stamped in from XR parameters
                providerConfigRef:
                  name: azure-provider-config

            patches:
              # ── Stamp the location from XR parameter onto the Managed Resource ──
              # Ford Station 1A: "Fit the engine from the engine rack"
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.location
                toFieldPath: spec.forProvider.location
                # Read from XR spec.parameters.location
                # Write to the ResourceGroup's spec.forProvider.location

              # ── Stamp the resource group name as the external-name annotation ──
              # This controls the actual Azure resource name
              # Ford Station 1B: "Stamp the serial number on the chassis"
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.resourceGroupName
                toFieldPath: metadata.annotations[crossplane.io/external-name]

              # ── Stamp the environment tag ──
              # Ford Station 1C: "Apply the colour" (it's still black, but tagged)
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.environment
                toFieldPath: spec.forProvider.tags.Environment

              # ── Stamp the cost center tag ──
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.costCenter
                toFieldPath: spec.forProvider.tags.CostCenter

              # ── Combine name and environment into a useful name tag ──
              # Ford: "Print 'Model T - Standard' on the dashboard"
              - type: CombineFromComposite
                combine:
                  variables:
                    - fromFieldPath: spec.parameters.resourceGroupName
                    - fromFieldPath: spec.parameters.environment
                  strategy: string
                  string:
                    fmt: "%s-%s"
                toFieldPath: spec.forProvider.tags.Name

              # ── Write the Azure Resource ID back to the XR status ──
              # Ford: "Update the order tracking system: car is built, serial = X"
              - type: ToCompositeFieldPath
                fromFieldPath: status.atProvider.id
                toFieldPath: status.resourceGroupId
                policy:
                  fromFieldPath: Optional
                  # Optional: the ID only exists after Azure creates the resource
                  # Like a car's serial number — it exists after manufacture, not before

    # ─────────────────────────────────────────────────────────────────
    # ASSEMBLY STATION 2: Final Quality Inspection
    # Ford's end-of-line inspector who checked every car before it left
    # This function marks the XR as READY only when all managed
    # resources are healthy — your digital quality control department
    # ─────────────────────────────────────────────────────────────────
    - step: auto-ready
      functionRef:
        name: function-auto-ready
      # No input needed — this function inspects all resources from previous steps
      # Ford: "The inspector checks everything. If it passes, it ships."
```

```bash
# Install the assembly line
kubectl apply -f apis/v1alpha1/azure-resource-group/composition-01.yaml

# Check it's registered and healthy
kubectl get composition xazureresourcegroup-azure-v1alpha1

# Output:
# NAME                                    XR-KIND                GRPS                        AGE
# xazureresourcegroup-azure-v1alpha1      XAzureResourceGroup    platform.example.com         10s

# Ford would check: "Is the assembly line running? Are all stations staffed?"
kubectl get functions
# NAME                              INSTALLED   HEALTHY   AGE
# function-patch-and-transform      True        True      5m
# function-go-templating            True        True      5m
# function-auto-ready               True        True      5m
# 
# Good. All stations are staffed. Production can begin.
```

-----

## A More Complex Assembly Line: Azure Subscription

Ford didn’t just build one model. The Model T was a simple product, but his factory principles applied equally to complex multi-component vehicles. Let’s see SIPOC applied to something more involved: an **Azure Subscription**, which involves multiple composed resources.

### The XRD Blueprint for an Azure Subscription

```yaml
# apis/v1alpha1/azure-subscription/xrd-01.yaml
#
# A more complex order form.
# Ford: "Sir, you're ordering a touring car with extra luggage capacity.
#        That requires additional specifications."

apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xazuresubscriptions.platform.example.com
spec:
  scope: Namespaced
  group: platform.example.com
  names:
    kind: XAzureSubscription
    plural: xazuresubscriptions
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
                  required:
                    - subscriptionDisplayName
                    - billingAccountName
                    - enrollmentAccountName
                    - managementGroupId
                  properties:
                    subscriptionDisplayName:
                      type: string
                      description: "Display name for the Azure Subscription"
                      maxLength: 64
                      # Ford: "What name goes on the registration document?"

                    billingAccountName:
                      type: string
                      description: "Enterprise Agreement billing account name"
                      # Ford: "Which corporate account is paying for this order?"

                    enrollmentAccountName:
                      type: string
                      description: "EA enrollment account to create the subscription under"
                      # Ford: "Which dealer are we registered through?"

                    managementGroupId:
                      type: string
                      description: "Management Group to place the subscription into after creation"
                      # Ford: "Which factory district does this car go to after handover?"

                    environment:
                      type: string
                      description: "Subscription purpose — drives policy assignment"
                      enum:
                        - sandbox
                        - dev
                        - test
                        - prod
                      default: sandbox
                      # Ford: "Standard, commercial, or racing spec?"

                    workload:
                      type: string
                      description: "Azure workload type"
                      enum:
                        - Production
                        - DevTest
                      default: DevTest
                      # Ford: "Light duty or heavy haul?"

            status:
              type: object
              properties:
                subscriptionId:
                  type: string
                  description: "Provisioned Azure Subscription GUID"
                  # Ford: "Your Model T serial number"
                subscriptionState:
                  type: string
                  description: "Current state of the subscription"
                  # Ford: "On the line / finished / shipped"
```

### The XR: Placing the Subscription Order

```yaml
# apis/v1alpha1/azure-subscription/xr-01.yaml
#
# Team Atlas wants a production subscription.
# They fill in the order form. The factory does the rest.
# Ford: "Revolutionary concept."

apiVersion: platform.example.com/v1alpha1
kind: XAzureSubscription
metadata:
  name: atlas-prod-subscription
  namespace: team-atlas
spec:
  parameters:
    subscriptionDisplayName: "Atlas Production — Managed by Platform"
    billingAccountName: "contoso-ea-billing"
    enrollmentAccountName: "platform-enrollment"
    managementGroupId: "mg-production"
    environment: prod
    workload: Production

  crossplane:
    compositionRef:
      name: xazuresubscription-azure-v1alpha1
    # Crossplane v2: machinery under spec.crossplane, parameters stay clean
    # The consumer sees a simple form. The factory sees the pipeline.
```

### The Composition: A More Complex Assembly Line

```yaml
# apis/v1alpha1/azure-subscription/composition-01.yaml
#
# The subscription assembly line is more involved.
# Ford didn't just bolt four wheels on a frame for his touring car —
# he had extra stations, extra specialists, extra quality checks.
# We follow the same principle.

apiVersion: apiextensions.crossplane.io/v1          # Compositions: still v1
kind: Composition
metadata:
  name: xazuresubscription-azure-v1alpha1
  labels:
    provider: azure
    product: subscription
spec:
  compositeTypeRef:
    apiVersion: platform.example.com/v1alpha1
    kind: XAzureSubscription

  mode: Pipeline  # Always Pipeline in v2-era Crossplane. The assembly line is the way.

  pipeline:
    # ─────────────────────────────────────────────────────────────────
    # STATION 1: Create the Azure Subscription
    # Ford: "The main chassis station — everything else attaches to this"
    # ─────────────────────────────────────────────────────────────────
    - step: create-subscription
      functionRef:
        name: function-patch-and-transform
      input:
        apiVersion: pt.fn.crossplane.io/v1beta1
        kind: Resources
        resources:
          - name: azure-subscription
            base:
              apiVersion: billing.azure.upbound.io/v1beta1
              kind: Subscription
              spec:
                forProvider:
                  subscriptionName: ""       # Patched from XR
                  billingAccountName: ""     # Patched from XR
                  enrollmentAccountName: ""  # Patched from XR
                  workload: ""              # Patched from XR
                providerConfigRef:
                  name: azure-provider-config

            patches:
              # ── Subscription display name ──
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.subscriptionDisplayName
                toFieldPath: spec.forProvider.subscriptionName

              # ── Billing account ──
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.billingAccountName
                toFieldPath: spec.forProvider.billingAccountName

              # ── Enrollment account ──
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.enrollmentAccountName
                toFieldPath: spec.forProvider.enrollmentAccountName

              # ── Workload type ──
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.workload
                toFieldPath: spec.forProvider.workload

              # ── Write subscription ID back to XR status ──
              # "The chassis number is stamped. Update the tracking board."
              - type: ToCompositeFieldPath
                fromFieldPath: status.atProvider.subscriptionId
                toFieldPath: status.subscriptionId
                policy:
                  fromFieldPath: Optional

              # ── Write subscription state back to XR status ──
              - type: ToCompositeFieldPath
                fromFieldPath: status.atProvider.state
                toFieldPath: status.subscriptionState
                policy:
                  fromFieldPath: Optional

    # ─────────────────────────────────────────────────────────────────
    # STATION 2: Place subscription into Management Group
    # Ford: "Route the finished car to the correct depot for distribution"
    # This station waits for the subscription ID from Station 1
    # ─────────────────────────────────────────────────────────────────
    - step: assign-management-group
      functionRef:
        name: function-patch-and-transform
      input:
        apiVersion: pt.fn.crossplane.io/v1beta1
        kind: Resources
        resources:
          - name: management-group-subscription
            base:
              apiVersion: management.azure.upbound.io/v1beta1
              kind: ManagementGroupSubscriptionAssociation
              spec:
                forProvider:
                  managementGroupId: ""     # Patched from XR
                  subscriptionId: ""        # Patched from XR status (written by Station 1)
                providerConfigRef:
                  name: azure-provider-config

            patches:
              # ── Management group from XR parameters ──
              - type: FromCompositeFieldPath
                fromFieldPath: spec.parameters.managementGroupId
                toFieldPath: spec.forProvider.managementGroupId

              # ── Subscription ID from XR status (written by Station 1) ──
              # Ford: "Take the chassis number from the previous station's stamp"
              - type: FromCompositeFieldPath
                fromFieldPath: status.subscriptionId
                toFieldPath: spec.forProvider.subscriptionId
                policy:
                  fromFieldPath: Required
                  # Required: Station 2 won't proceed until Station 1 provides the ID
                  # Ford: "Don't attach the body before the chassis is finished"

    # ─────────────────────────────────────────────────────────────────
    # STATION 3: Final Inspection
    # Ford: "Sign it off. If it passes, ship it."
    # ─────────────────────────────────────────────────────────────────
    - step: auto-ready
      functionRef:
        name: function-auto-ready
```

```bash
# Apply the subscription XRD and Composition
kubectl apply -f apis/v1alpha1/azure-subscription/xrd-01.yaml
kubectl apply -f apis/v1alpha1/azure-subscription/composition-01.yaml

# Place the order
kubectl apply -f apis/v1alpha1/azure-subscription/xr-01.yaml

# Watch the assembly line process it
kubectl get xazuresubscription atlas-prod-subscription -n team-atlas -w

# Output — watching the factory floor:
# NAME                       SYNCED   READY   AGE
# atlas-prod-subscription    True     False   5s    ← Building...
# atlas-prod-subscription    True     False   15s   ← Station 1 working...
# atlas-prod-subscription    True     False   30s   ← Station 2 working...
# atlas-prod-subscription    True     True    45s   ← Shipped! Ready for use.

# Inspect what the factory built (the Output)
kubectl get managed | grep atlas

# Ford's equivalent: walking the factory floor and counting completed cars
```

-----

## The Output: What Rolls Off the Line

Ford’s assembly line produced **one output**: a Model T, ready to drive. Every single one identical. Predictable. Reliable.

Crossplane’s Pipeline produces **managed resources** — actual Azure infrastructure objects, reconciled continuously to match the desired state. Unlike Ford’s cars, which required no further attention once sold (until they broke down in a ditch), Crossplane’s managed resources are *continuously reconciled*. The factory floor never truly stops — it monitors every car it ever built and fixes deviations automatically.

```bash
# Inspect the actual Azure resources that were created
# These are the "cars" that rolled off the assembly line

kubectl get resourcegroup
# NAME                    READY   SYNCED   EXTERNAL-NAME          AGE
# atlas-dev-resources     True    True     atlas-dev-resources    2m

kubectl get subscription
# NAME                         READY   SYNCED   EXTERNAL-NAME                          AGE
# atlas-prod-subscription-x9k   True    True     a1b2c3d4-xxxx-xxxx-xxxx-xxxxxxxxxxxx   3m

# Describe a managed resource to see the full factory output
kubectl describe resourcegroup atlas-dev-resources

# Key things to look for in the output:
#
# Status.Conditions:
#   Type: Ready       Status: True   ← Car passed quality inspection
#   Type: Synced      Status: True   ← Factory monitoring confirms it matches spec
#
# Status.AtProvider:
#   Id: /subscriptions/.../resourceGroups/atlas-dev-resources  ← Azure resource ID
#   ProvisioningState: Succeeded    ← Azure confirms it exists
#
# This is Ford's quality sticker: "Built at Highland Park. Inspected. Approved."
```

### Reconciliation: The Factory Never Sleeps

Here’s where Crossplane beats Ford’s factory: if someone *drives the car into a wall* (deletes a resource via the Azure portal), Crossplane fixes it automatically.

```bash
# Simulate configuration drift — someone manually changes the resource group tags in Azure
# Ford's equivalent: a disgruntled worker repainting a car red on the factory floor

# Crossplane reconciles within seconds (default: every 10 minutes, 
# but triggered immediately when it detects drift)
# The "car" is repainted black again, automatically
# Ford would approve — he was very particular about the colour

kubectl get events -n team-atlas | grep atlas-dev-rg
# LAST SEEN   TYPE      REASON                    OBJECT                        MESSAGE
# 30s         Normal    ReconcileSuccess           xazureresourcegroup/atlas-dev-rg   Successfully reconciled resource group
# 15s         Warning   ReconcileError             xazureresourcegroup/atlas-dev-rg   Observed drift, correcting...
# 5s          Normal    ReconcileSuccess           xazureresourcegroup/atlas-dev-rg   Drift corrected. Good service resumed.
```

Ford’s Output lesson: *the assembly line doesn’t stop at delivery. It monitors. It corrects. Every car stays a Model T, not a red Chevrolet someone converted it into over the weekend.*

-----

## The Consumer: Self-Service at the Showroom

Ford’s master stroke wasn’t just the assembly line. It was making the **car affordable enough that the workers who built it could buy one**. He democratised the automobile. Before Ford, cars were hand-crafted luxury items for the wealthy. After Ford, they were something everyone could access.

This is exactly what Crossplane v2 does for cloud infrastructure. Before Crossplane, developers needed a platform engineer to provision every resource — an artisan craftsman, expensive and slow. After Crossplane, developers can self-serve from a catalogue of approved, compliant, standardised resources. The factory floor is open to all customers.

### The Consumer Experience: Ordering a Car at the Showroom

In the old world:

```
Developer: "I need a Resource Group in West Europe for my dev environment"
Platform Engineer: (opens Azure Portal, clicks 47 things, forgets a tag, has to redo it)
Developer: (waits two days)
Platform Engineer: "Here it is. Also I misconfigured the IAM, sorry."
Developer: (cries quietly)
```

In the Crossplane v2 world:

```yaml
# examples/team-payments-dev-rg.yaml
# A developer on the payments team ordering infrastructure
# Like walking into a Ford showroom with a completed order form
#
# They don't know (or need to know) about:
# - How Azure Resource Groups are actually created via ARM
# - Which service principal has which permissions
# - Which Composition pipeline runs behind the scenes
# - That there's a function-auto-ready checking everything is healthy
#
# They fill in: name, location, environment, cost centre.
# The factory handles the rest.

apiVersion: platform.example.com/v1alpha1
kind: XAzureResourceGroup
metadata:
  name: payments-dev-rg
  namespace: team-payments          # Namespaced in their own team namespace
spec:
  parameters:
    resourceGroupName: payments-dev-resources
    location: westeurope
    environment: dev
    costCenter: "CC-PAYMENTS-007"
  crossplane:
    compositionRef:
      name: xazureresourcegroup-azure-v1alpha1
```

```bash
# Developer applies this themselves, in their own namespace
kubectl apply -f team-payments-dev-rg.yaml -n team-payments

# They can check their own order status without bothering the platform team
kubectl get xazureresourcegroup -n team-payments

# Output:
# NAME               SYNCED   READY   AGE
# payments-dev-rg    True     True    60s
#
# "Your Model T is ready for collection, sir."
# "Cheers, Ford."

# They can see status details too
kubectl describe xazureresourcegroup payments-dev-rg -n team-payments

# Status:
#   Resource Group Id: /subscriptions/.../resourceGroups/payments-dev-resources
#   Conditions:
#     Ready:  True
#     Synced: True
#
# Ford: "There's your serial number. She's all yours."
```

### Multiple Teams, Multiple Orders, One Factory

The beauty of the assembly line is **scale**. Ford didn’t build one car at a time. He ran the line continuously, serving many customers simultaneously.

```bash
# Multiple teams ordering simultaneously
# Crossplane reconciles them all concurrently

kubectl apply -f team-atlas-rg.yaml -n team-atlas
kubectl apply -f team-payments-rg.yaml -n team-payments
kubectl apply -f team-logistics-rg.yaml -n team-logistics
kubectl apply -f team-fraud-detection-rg.yaml -n team-fraud

# All four resource groups provisioned in parallel
# Ford's equivalent: four different Model Ts simultaneously on the line
# Each independent, each to spec, each delivered promptly

kubectl get xazureresourcegroup --all-namespaces

# NAMESPACE        NAME                      SYNCED   READY   AGE
# team-atlas       atlas-dev-rg              True     True    2m
# team-payments    payments-dev-rg           True     True    90s
# team-logistics   logistics-test-rg         True     True    75s
# team-fraud       fraud-detection-prod-rg   True     True    60s
#
# Four cars. Four customers. One assembly line.
# Ford would nod approvingly.
```

### The Consumer’s RBAC: Not Everyone Gets the Keys

Ford sold to paying customers, not to any random person who wandered into the factory. Crossplane consumers are similarly scoped — RBAC ensures each team can only order (and see) their own resources.

```yaml
# Platform team applies this once — like setting up the showroom access policies
# developers in team-payments can only touch their namespace

apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: crossplane-consumer
  namespace: team-payments
  # Ford: "Customer pass for the Payments team showroom counter"
rules:
  - apiGroups: ["platform.example.com"]
    resources: ["xazureresourcegroups", "xazuresubscriptions"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
    # They can order, modify, and cancel their own resources
    # They cannot interfere with other teams' orders
  - apiGroups: ["platform.example.com"]
    resources: ["xazureresourcegroups/status"]
    verbs: ["get", "list", "watch"]
    # They can check the status board for their own orders

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: team-payments-consumers
  namespace: team-payments
subjects:
  - kind: Group
    name: team-payments       # Azure AD group for the payments team
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: crossplane-consumer
  apiGroup: rbac.authorization.k8s.io
```

```bash
# From a developer's perspective on the payments team:

# ✅ This works — ordering from their own showroom counter
kubectl apply -f payments-dev-rg.yaml -n team-payments

# ❌ This doesn't — they can't order from another team's counter
kubectl apply -f payments-dev-rg.yaml -n team-atlas
# Error: rolebindings.rbac.authorization.k8s.io is forbidden

# Ford: "Your pass is for Highland Park only, not the Detroit branch."
```

-----

## The Full Factory Floor: Putting It All Together

Let’s step back and see the complete SIPOC assembly line in one view. This is Ford’s factory, rendered in YAML.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    THE CROSSPLANE v2 ASSEMBLY LINE                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

  SUPPLIER              INPUT                 PROCESS               OUTPUT           CONSUMER
  ─────────────         ─────────────         ─────────────         ─────────────    ─────────────
  Provider        ──▶  XRD              ──▶  Composition     ──▶  Managed      ──▶  App Team
  (Azure API)          (Blueprint)           (Assembly Line)       Resource          (self-serves
                                                                   (The Car)         in their
  Functions       ──▶  XR               ──▶  Pipeline Steps  ──▶  Azure API    ──▶  namespace)
  (Specialists)        (Order Form)          (Stations)            (Real cloud
                                                                   resource)
  apiVersion:          apiVersion:           apiVersion:           Managed by
  pkg.crossplane       apiextensions         apiextensions         Provider
  .io/v1beta1          .crossplane           .crossplane           Reconciled
  kind: Function       .io/v2                .io/v1                continuously
                       kind: CRD             kind:
                                             Composition
                        ↓
                       XR submitted
                       (apiVersion:
                       platform.
                       example.com/v1alpha1)
                       namespace-scoped
                       spec.crossplane.*
                       (v2 pattern)
```

### Quick Reference: Getting the API Versions Right

This trips people up more than anything else. Ford had one assembly line model. Crossplane v2 has two different API versions for two different object types:

```yaml
# ┌─────────────────────────────────────────────────────────────────┐
# │  OBJECT TYPE                    │  API VERSION                  │
# ├─────────────────────────────────┼───────────────────────────────┤
# │  CompositeResourceDefinition    │  apiextensions.crossplane     │
# │  (XRD)                          │  .io/v2      ← v2!           │
# ├─────────────────────────────────┼───────────────────────────────┤
# │  Composition                    │  apiextensions.crossplane     │
# │                                 │  .io/v1      ← still v1!     │
# ├─────────────────────────────────┼───────────────────────────────┤
# │  Provider                       │  pkg.crossplane.io/v1         │
# │  Function                       │  pkg.crossplane.io/v1beta1    │
# ├─────────────────────────────────┼───────────────────────────────┤
# │  XR (Composite Resource)        │  your.group.com/v1alpha1      │
# │  (the actual order form)        │  (whatever you defined in XRD)│
# └─────────────────────────────────┴───────────────────────────────┘
```

### Testing the Assembly Line Without Touching Azure

Ford had prototype workshops where engineers tested new assembly line configurations before rolling them out to production. Crossplane has `crossplane render` — a dry-run tool that simulates what your Composition will produce, without actually calling Azure.

```bash
# Test the assembly line without production consequences
# Ford: "Run it in the prototype shop first"

crossplane render \
  apis/v1alpha1/azure-resource-group/xr-01.yaml \
  apis/v1alpha1/azure-resource-group/composition-01.yaml \
  --function-runtime-configs functions/

# Output — what would be built:
# ---
# apiVersion: azure.upbound.io/v1beta1
# kind: ResourceGroup
# metadata:
#   annotations:
#     crossplane.io/composition-resource-name: azure-resource-group
#     crossplane.io/external-name: atlas-dev-resources    ← Azure resource name
#   name: team-atlas-dev-rg-xkp9m
# spec:
#   forProvider:
#     location: westeurope                                 ← Patched from XR
#     tags:
#       CostCenter: CC-ATLAS-001                          ← Patched from XR
#       Environment: dev                                  ← Patched from XR
#       ManagedBy: crossplane
#       Name: atlas-dev-resources-dev                     ← Combined patch
#   providerConfigRef:
#     name: azure-provider-config
#
# Ford: "Prototype approved. Start production."
```

-----

## Debugging the Assembly Line

Every factory has breakdowns. Ford’s workers had spanners. We have `kubectl describe`.

```bash
# Something isn't working. Let's diagnose.
# Ford: "Which station is the hold-up?"

kubectl get xazureresourcegroup atlas-dev-rg -n team-atlas

# SYNCED   READY
# False    False   ← Something is wrong at one of the stations

# Step 1: Check what the XR says
kubectl describe xazureresourcegroup atlas-dev-rg -n team-atlas

# Look for the Events section at the bottom:
# Events:
#   Type      Reason             Message
#   Warning   CannotObserveComposedResource   cannot get object: resource group "atlas-dev-resources" not found
#
# Ford: "Station 1 says the chassis hasn't arrived. Check the steel supplier."

# Step 2: Check the managed resources the Composition created
kubectl get managed | grep atlas

# NAME                        READY   SYNCED   EXTERNAL-NAME          AGE
# atlas-dev-resources-xkp9m   False   False    atlas-dev-resources    30s

kubectl describe resourcegroup atlas-dev-resources-xkp9m

# Look for:
# Status.Conditions:
#   Synced: False
#   Last Transition Time: ...
#   Message: cannot create ResourceGroup: authorization error...
#
# Ford: "The steel mill is refusing to deliver. Check the supplier contract (ProviderConfig credentials)."

# Step 3: Check the Provider is healthy
kubectl get providers
kubectl describe provider provider-azure-resources

# Step 4: Check Function logs (Station worker logs)
kubectl get functions
kubectl logs -n crossplane-system -l pkg.crossplane.io/revision=function-patch-and-transform

# Ford: "Ask the station workers what happened. They saw everything."
```

Common issues and their Ford analogies:

```
Problem: Provider not HEALTHY
Ford: "The steel mill is on strike. No materials, no production."
Fix:  Check ProviderConfig credentials, Service Principal permissions

Problem: XRD not ESTABLISHED
Ford: "The engineering blueprint has errors. Production cannot start."
Fix:  Validate XRD schema — check for required/optional field mistakes

Problem: Composition not selecting correct XR
Ford: "The assembly line doesn't recognise this order form."
Fix:  Check compositeTypeRef matches your XRD group/kind exactly

Problem: Patch path not found
Ford: "Station worker reached for a part that wasn't on the rack."
Fix:  Verify fromFieldPath exists in XR; use policy.fromFieldPath: Optional if it might be absent

Problem: Managed resource stuck in SYNCED: False
Ford: "The car is half-built and nobody knows why it stopped."
Fix:  kubectl describe the managed resource; check status.conditions for Azure API errors
```

-----

## The Repository Structure: Your Factory Blueprints Archive

Every Ford factory had a blueprint archive. Every Crossplane repository should have a clear structure. Here’s how we’ve laid ours out in `learning-crossplane-sipoc`:

```
learning-crossplane-sipoc/              ← The factory archive
│
├── apis/                               ← Engineering blueprints (XRDs, XRs, Compositions)
│   └── v1alpha1/
│       ├── azure-resource-group/       ← Model T (simple product)
│       │   ├── xrd-01.yaml             ← Blueprint v1: what can be ordered
│       │   ├── xr-01.yaml              ← Example order form
│       │   ├── composition-01.yaml     ← Assembly line for this product
│       │   └── README.md               ← SIPOC walkthrough for this product
│       │
│       ├── azure-subscription/         ← Touring car (complex product)
│       │   ├── xrd-01.yaml
│       │   ├── xr-01.yaml
│       │   ├── composition-01.yaml
│       │   └── README.md
│       │
│       └── azure-aks-cluster/          ← Racing car (advanced product)
│           ├── xrd-01.yaml
│           ├── xr-01.yaml
│           ├── composition-01.yaml
│           └── README.md
│
├── providers/                          ← Supplier contracts
│   ├── provider-azure.yaml             ← Steel mill contract
│   ├── provider-config.yaml            ← Supplier credentials
│   └── README.md
│
├── functions/                          ← Specialist tools
│   ├── function-patch-and-transform.yaml
│   ├── function-go-templating.yaml
│   ├── function-auto-ready.yaml
│   └── README.md
│
├── tests/                              ← Prototype workshop
│   ├── render/                         ← crossplane render dry-run outputs
│   │   ├── azure-resource-group/
│   │   │   └── expected-output.yaml    ← What we expect the line to produce
│   │   └── azure-subscription/
│   │       └── expected-output.yaml
│   └── README.md
│
├── examples/                           ← Showroom order forms
│   ├── team-atlas-dev-rg.yaml          ← Example customer orders
│   ├── team-payments-dev-rg.yaml
│   ├── atlas-prod-subscription.yaml
│   └── README.md
│
└── docs/                               ← Factory manuals
    ├── sipoc-explained.md              ← This mental model, in detail
    ├── crossplane-v2-changes.md        ← What changed from v1 (important!)
    ├── composition-functions.md        ← How the pipeline stations work
    ├── provider-setup.md               ← Getting the suppliers connected
    └── glossary.md                     ← Factory terminology
```

-----

## The Verdict: Ford Was Right

Henry Ford’s insight wasn’t just about efficiency. It was about **democratisation through standardisation**. Make the process repeatable, make the product consistent, make access universal.

Crossplane v2 is the same insight applied to cloud infrastructure:

- **Repeatable**: the same Composition produces the same resources, every time
- **Consistent**: XRDs enforce the same schema, across every team
- **Universal**: any team can self-serve, in their own namespace, with appropriate RBAC

The differences between 1913 and now are mostly cosmetic:

|Ford’s Factory                     |Crossplane v2                                                    |
|-----------------------------------|-----------------------------------------------------------------|
|Moving assembly line               |Pipeline Compositions                                            |
|Engineering blueprint              |CompositeResourceDefinition (v2)                                 |
|Customer order form                |Composite Resource (XR)                                          |
|Specialised workers                |Composition Functions                                            |
|Supply chain                       |Providers                                                        |
|Quality inspector                  |function-auto-ready                                              |
|Factory floor CCTV                 |`kubectl get managed`                                            |
|Car serial number                  |`status.atProvider.id`                                           |
|“Any colour, as long as it’s black”|“Any resource, as long as it’s in the Composition”               |
|15 million Model Ts produced       |Theoretical infinite managed resources (your cloud bill may vary)|

Ford paid his workers $5 a day so they could afford the cars they built. Platform teams should build platforms that developers *actually want to use* — self-service, fast, compliant, and boring in all the right ways.

If developers are bypassing your platform and clicking around the Azure Portal manually, you don’t have a Crossplane problem. You have a UX problem. The assembly line should be the path of least resistance.

Build the line. Standardise the product. Let the consumers self-serve.

And remember Ford’s final lesson: **you don’t have to offer every colour. Black is fine. Consistency is the point.**

-----

*Somewhere in Highland Park, the ghost of Henry Ford examines a running Crossplane cluster, nods once, and says “Now THAT is an assembly line.” He then asks why everything is in YAML instead of stamped metal, and we explain it’s 2025. He does not look convinced. We show him the reconciliation loop. He looks slightly more convinced.*

*He asks about the colour options.*

*We say it’s whatever the XRD allows.*

*He nods. “Good.”*

-----

## Getting Started on Your Own Assembly Line

```bash
# Step 1: Create a Kind cluster (your prototype factory floor)
kind create cluster --name crossplane-factory

# Step 2: Install Crossplane (build the factory building)
helm repo add crossplane-stable https://charts.crossplane.io/stable
helm install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --version ">= 2.0.0"   # We want v2!

# Step 3: Install providers and functions (sign the supplier contracts)
kubectl apply -f providers/
kubectl apply -f functions/

# Step 4: Wait for suppliers to be ready
kubectl get providers --watch
kubectl get functions --watch

# Step 5: Apply your XRD (register the blueprint)
kubectl apply -f apis/v1alpha1/azure-resource-group/xrd-01.yaml

# Step 6: Apply your Composition (commission the assembly line)
kubectl apply -f apis/v1alpha1/azure-resource-group/composition-01.yaml

# Step 7: Dry-run test (prototype workshop)
crossplane render \
  apis/v1alpha1/azure-resource-group/xr-01.yaml \
  apis/v1alpha1/azure-resource-group/composition-01.yaml \
  --function-runtime-configs functions/

# Step 8: Submit your first XR (place your first order)
kubectl apply -f examples/team-atlas-dev-rg.yaml -n team-atlas

# Step 9: Watch it roll off the line
kubectl get xazureresourcegroup -n team-atlas --watch

# Step 10: Admire the output
kubectl get managed
# Ford: "Beautiful. Now build ten thousand more."
```

-----

## Further Reading

### Crossplane Documentation

- [Crossplane v2 Official Docs](https://docs.crossplane.io/latest/) — The factory manual, updated for the new model year
- [What’s New in v2](https://docs.crossplane.io/latest/whats-new/) — The release notes Ford would have written, if Ford wrote release notes
- [Composite Resource Definitions](https://docs.crossplane.io/latest/composition/composite-resource-definitions/) — Blueprint specification guide
- [Composition Functions](https://docs.crossplane.io/latest/concepts/composition-functions/) — The assembly station worker manual
- [Upbound Azure Provider](https://marketplace.upbound.io/providers/upbound/provider-azure-resources/) — Your steel mill catalogue

### Historical Context (For Verisimilitude)

- [The Highland Park Ford Plant](https://www.thehenryford.org/visit/henry-ford-museum/exhibits/made-in-america/) — The original assembly line, now a museum
- [The SIPOC Model](https://en.wikipedia.org/wiki/SIPOC) — Lean process improvement tool, predates Crossplane by about 80 years
- [Ford’s Five Dollar Day](https://www.thehenryford.org/collections-and-research/digital-collections/artifact/210133) — Democratising access through standardisation

### Repository

- [learning-crossplane-sipoc](https://github.com/stallone/learning-crossplane-sipoc) — All the code from this article, properly laid out in assembly-line order

-----

*This article is part of the “Infrastructure-as-Code Adventures” series:*

- **Crossplane Networking**: Mind the Gap — The London Underground *(published)*
- **Crossplane SIPOC**: The Ford Assembly Line — You are here, on the line
- **Crossplane Environments**: The Scaling Problem — Or: Why Ford Built More Than One Factory *(coming soon)*
- **Crossplane with Backstage**: The Showroom Catalogue — Making consumers feel like customers *(coming soon)*

-----

*Estimated reading time: about as long as a Model T took to traverse an early twentieth-century road. Which is to say: longer than you’d expect, but you arrive feeling like you understood something important.*

**Tags:** #crossplane #kubernetes #platformengineering #devops #iac #sipoc #azure #crossplanev2

-----

**Disclaimer:** No actual Henry Fords were resurrected for the writing of this article. The Model T was eventually discontinued in 1927, replaced by the Model A, which had more colour options. Crossplane’s Compositions have no such limitation, though your organisation’s governance policies might.

Henry Ford’s actual views on labour relations, antisemitism, and various other matters are not endorsed by this article, the author, or the Crossplane project. We are here for the assembly line metaphor only. The man built a good assembly line. We will acknowledge that and stop there.

*“Coming together is a beginning, staying together is progress, and working together is success.”* — Henry Ford, on teams that use GitOps properly.
