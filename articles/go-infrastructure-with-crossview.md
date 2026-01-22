---

## title: "Don’t Pass GO Without Crossview: A Monopoly Guide to Crossplane’s Control Plane"
published: false
description: "Understanding Crossplane and Crossview through the lens of everyone’s favorite friendship-destroying board game"
tags: ["kubernetes", "devops", "infrastructure", "cloudnative"]
cover_image: https://dev-to-uploads.s3.amazonaws.com/uploads/articles/monopoly-crossplane-crossview.jpg
canonical_url: ""
series: "Infrastructure as Code Adventures"
organization: “the-software-s-journey"
---

# Don’t Pass GO Without Crossview: A Monopoly Guide to Crossplane’s Control Plane

Remember that time you flipped the Monopoly board because your sibling bought Park Place right before you could? Or when you mortgaged everything just to stay in the game? Well, managing cloud infrastructure can feel exactly like that—except instead of fake money, you’re burning through real Azure credits, and instead of going to jail, you’re debugging YAML at 3 AM.

But what if I told you there’s a way to manage your infrastructure empire with the clarity of a Monopoly board laid out in front of you? Enter **Crossplane** and **Crossview**—the dynamic duo that turns infrastructure chaos into a beautiful, visual game board you can actually understand.

Let me explain using the only framework that matters: Monopoly.

## 🎩 The Game Board: Understanding Crossplane

Before we talk about Crossview (the fancy GUI dashboard), let’s understand Crossplane using our favorite capitalist board game.

### The Deed Cards: Composite Resource Definitions (XRDs)

In Monopoly, deed cards represent the *option* to buy properties. They list what you *could* own and what the rules are for that property.

In Crossplane, **Composite Resource Definitions (XRDs)** work the same way. They define what infrastructure you *could* provision and what parameters are available.

```yaml
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.example.com
spec:
  group: example.com
  names:
    kind: XDatabase          # Like "Mediterranean Avenue"
    plural: xdatabases
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
              size:            # Small, medium, or large?
                type: string
                enum: ["small", "medium", "large"]
              storageGB:       # How much storage?
                type: integer
```

Think of this as the deed card for “Baltic Avenue”—it tells you what you’re getting and what options you have. You can’t actually *use* it until you buy it, but it’s there, waiting.

### The Properties You Own: Composite Resources (XRs)

When you land on Baltic Avenue and hand over your $60, you now *own* that property. It’s yours! The deed card becomes a real asset.

In Crossplane, when you create a **Composite Resource (XR)** based on an XRD, you’re buying that property. You’ve gone from “this exists as an option” to “this is mine and it’s running.”

```yaml
apiVersion: example.com/v1alpha1
kind: XDatabase
metadata:
  name: my-production-db
  namespace: production  # XRs can be namespaced in Crossplane 2.1!
spec:
  size: large
  storageGB: 100
```

Boom! You just bought Park Place. Well, the database equivalent. Your production database is now running in the cloud, and you’re collecting rent (or in this case, serving traffic).

In Crossplane 2.1, you can configure XRs to be namespace-scoped (perfect for multi-tenant scenarios) or cluster-scoped. Think of namespaces as different neighborhoods on your Monopoly board!

### The Buildings: Compositions

Here’s where it gets fun. In Monopoly, once you own a property, you can build houses and hotels on it. These buildings make your property more valuable and generate more rent.

In Crossplane, **Compositions** are exactly like that. They define what gets “built” when you create an XR. A Composition might say: “When someone creates a Database XR, we’re going to build them an Azure Database for PostgreSQL, a Storage Account for backups, monitoring dashboards, and a Key Vault secret for credentials.”

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: database-azure-production
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: XDatabase
  mode: Pipeline
  pipeline:
  - step: create-postgres-instance
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: postgres-server
        base:
          apiVersion: dbforpostgresql.azure.upbound.io/v1beta1
          kind: Server
          spec:
            forProvider:
              location: eastus
              sku:
                name: B_Gen5_2  # Big hotel on Boardwalk!
              storageMb: 102400
              version: "15"
      - name: backup-storage
        base:
          apiVersion: storage.azure.upbound.io/v1beta1
          kind: Account
          spec:
            forProvider:
              location: eastus
              accountTier: Standard
              accountReplicationType: LRS
      - name: monitoring-workspace
        base:
          apiVersion: operationalinsights.azure.upbound.io/v1beta1
          kind: Workspace
```

See what happened? You bought one “property” (the Database XR), but the Composition automatically built you a hotel (PostgreSQL Server), a parking lot (Storage Account for backups), and a security system (Log Analytics workspace).

You’re basically the Donald Trump of cloud infrastructure. Without the bankruptcies. Hopefully.

## 🎲 The Problem: You Can’t See the Board!

Imagine playing Monopoly with your eyes closed. Someone tells you “you landed on a property” but won’t tell you which one, how much it costs, or what’s already on it. That’s what managing Crossplane resources with just `kubectl` feels like:

```bash
# What fresh hell is this?
kubectl get compositeresourcedefinitions
kubectl get compositions  
kubectl get xdatabases
kubectl describe xdatabase my-production-db
# ...500 lines of YAML later...
```

You’re squinting at YAML, grep-ing through status conditions, and trying to figure out if your database is actually running or if it’s stuck in some weird pending state. It’s like playing Monopoly by reading the rulebook aloud instead of just looking at the board.

**This is madness.**

## 🎨 Enter Crossview: The Actual Game Board

This is where [Crossview](https://github.com/corpobit/crossview) swoops in like a hero who actually read the instructions.

Crossview is a beautiful web dashboard that turns your Crossplane chaos into an actual visual game board. Finally, you can *see* your infrastructure empire!

### The Game Board Interface

When you open Crossview, you get a dashboard that shows you everything, organized and pretty:

- **All your properties (XRs)** - See every database, storage bucket, and Kubernetes cluster you’ve created
- **Property status** - Green = healthy and collecting rent, Red = something’s on fire
- **The buildings (managed resources)** - See every PostgreSQL Server, Storage Account, etc. built by your Compositions
- **Recent moves** - Activity feed showing what everyone’s been creating and deleting

It’s like being able to see the entire Monopoly board from above instead of crawling around on the floor trying to read property cards.

### Real-Time Property Status

In Monopoly, you can glance at the board and see: “Oh, Jenny owns all the railroads and has hotels on Boardwalk. I’m doomed.”

In Crossview, you get the same instant clarity:

```
🟢 Production Database (my-production-db)
   ├── 🟢 PostgreSQL Server: prod-db-server (Running)
   ├── 🟢 Storage Account: proddbbackups (Active)
   ├── 🟢 Log Analytics Workspace: db-monitoring (OK)
   └── 🟢 Network Security Group: db-security (Applied)
   
🔴 Staging API (my-api-gateway)
   ├── 🟡 API Management: staging-api (Updating...)
   ├── 🔴 Function App: api-handler (Error: Out of memory)
   └── 🟢 Cosmos DB: api-data (Active)
```

One glance tells you: production is printing money, but staging is on fire. Time to mortgage Baltic Avenue and fix that Function App.

### Searching Your Empire

In late-game Monopoly, you’ve got properties everywhere. “Wait, do I own the utilities? Which railroads do I have?”

Crossview has a search bar. Type “database” and boom—every database resource across every namespace. Type “production” and see everything in prod.

```
Search: "postgresql"

Results:
- XDatabase: customer-db (production namespace)
- XDatabase: analytics-db (analytics namespace)  
- PostgreSQL Server: legacy-postgres (default namespace)
```

It’s like having a property accountant who actually knows where you put everything.

## 🏦 The Bank: Resource Relationships

One of the most confusing parts of Crossplane is understanding relationships. A Claim creates an XR, which uses a Composition, which creates Managed Resources, which talk to cloud providers…

It’s like trying to explain Monopoly’s mortgage rules to a five-year-old.

Crossview shows you the relationships visually:

```
Composite Resource (XDatabase) 
    ↓  
Composition (database-azure-production)
    ↓
Managed Resources:
    ├── PostgreSQL Server
    ├── Storage Account
    ├── Log Analytics Workspace
    └── Network Security Group
```

Click on any resource and see:

- **What created it** (the parent)
- **What it created** (the children)
- **Current status** (is it healthy?)
- **Events** (what’s been happening?)
- **Full YAML** (for the masochists among us)

### Multi-Cluster Game Nights

Got multiple Kubernetes clusters? Crossview can connect to all of them. It’s like hosting multiple Monopoly games simultaneously and being able to see all boards at once.

```javascript
// Crossview can switch between clusters
Clusters:
- 🟢 Production (eastus)  
- 🟢 Staging (westus2)
- 🟡 Development (westeurope)
- 🔴 Sandbox (southeastasia) - Connection Error
```

Click between them like switching between game boards. “Oh right, I forgot I had hotels on Boardwalk in the staging cluster!”

## 🎯 Installing Crossview: Let’s Play!

Ready to see your infrastructure empire in all its glory? Installing Crossview is easier than setting up Monopoly (no fighting over who gets to be the banker).

### The Quick Setup

First, make sure you have Crossplane running. If you don’t, that’s like trying to play Monopoly without the board:

```bash
# Install Crossplane (if you haven't already)
helm repo add crossplane-stable https://charts.crossplane.io/stable
helm repo update

helm install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace
```

Now for the star of the show—Crossview:

```bash
# Add Crossview Helm repo
helm repo add crossview https://corpobit.github.io/crossview
helm repo update

# Install Crossview (the game board!)
helm install crossview crossview/crossview \
  --namespace crossview \
  --create-namespace \
  --set secrets.dbPassword=$(openssl rand -base64 32) \
  --set secrets.sessionSecret=$(openssl rand -base64 32)

# Wait for it...
kubectl wait --for=condition=available --timeout=300s \
  deployment/crossview -n crossview
```

### Accessing Your Game Board

```bash
# Port forward to access locally
kubectl port-forward -n crossview svc/crossview 3001:3001

# Now open: http://localhost:3001
```

🎉 **BAM!** You’ve got a visual game board for your infrastructure!

### For Production (with LoadBalancer)

```bash
# If you're fancy and want a real URL
helm install crossview crossview/crossview \
  --namespace crossview \
  --create-namespace \
  --set service.type=LoadBalancer \
  --set secrets.dbPassword=$(openssl rand -base64 32) \
  --set secrets.sessionSecret=$(openssl rand -base64 32)

# Get the external IP
kubectl get svc crossview -n crossview

# Access at: http://<EXTERNAL-IP>:3001
```

## 🎲 Let’s Play: A Real Example

Let’s create some infrastructure and watch Crossview show us what’s happening, Monopoly-style!

### Roll the Dice: Create an XRD (Deed Card)

```yaml
# database-xrd.yaml
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.database.example.com
spec:
  group: database.example.com
  names:
    kind: XPostgreSQLInstance
    plural: xpostgresqlinstances
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
                  size:
                    type: string
                    enum: ["small", "medium", "large"]
                    default: "small"
                  storageGB:
                    type: integer
                    default: 20
                required:
                - storageGB
            required:
            - parameters
```

Apply it:

```bash
kubectl apply -f database-xrd.yaml
```

In Crossview, you’ll see this appear in the “Definitions” tab. It’s like adding a new deed card to your deck!

### Build Your Empire: Create a Composition (The Hotel Blueprint)

```yaml
# database-composition.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: postgresql-azure
  labels:
    provider: azure
    type: postgresql
spec:
  compositeTypeRef:
    apiVersion: database.example.com/v1alpha1
    kind: XPostgreSQLInstance
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      # The PostgreSQL Server (the hotel!)
      - name: postgresqlserver
        base:
          apiVersion: dbforpostgresql.azure.upbound.io/v1beta1
          kind: Server
          spec:
            forProvider:
              location: eastus
              administratorLogin: psqladmin
              version: "15"
              sku:
                name: B_Gen5_1  # Small hotel
                tier: Basic
                capacity: 1
              storageMb: 20480
              sslEnforcement: Enabled
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.storageGB
          toFieldPath: spec.forProvider.storageMb
          transforms:
          - type: math
            math:
              multiply: 1024  # Convert GB to MB
        - type: FromCompositeFieldPath
          fromFieldPath: spec.parameters.size
          toFieldPath: spec.forProvider.sku.name
          transforms:
          - type: map
            map:
              small: B_Gen5_1
              medium: GP_Gen5_2
              large: GP_Gen5_4
        
      # The Storage Account for backups (parking lot!)
      - name: storageaccount
        base:
          apiVersion: storage.azure.upbound.io/v1beta1
          kind: Account
          spec:
            forProvider:
              location: eastus
              resourceGroupName: crossplane-resources
              accountTier: Standard
              accountReplicationType: LRS
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.forProvider.name
          transforms:
          - type: string
            string:
              fmt: "%sbackups"
              type: Format
```

```bash
kubectl apply -f database-composition.yaml
```

Now in Crossview, go to “Compositions” and you’ll see your blueprint. It’s like having the instructions for building hotels!

### Create Your XR (Buy the Property!)

```yaml
# my-database.yaml
apiVersion: database.example.com/v1alpha1
kind: XPostgreSQLInstance
metadata:
  namespace: production
  name: customer-database
spec:
  parameters:
    size: medium
    storageGB: 100
  writeConnectionSecretToRef:
    name: customer-db-credentials
```

```bash
kubectl apply -f my-database.yaml
```

### Watch the Magic in Crossview! 🎩✨

Open Crossview and navigate to the dashboard. You’ll see:

1. **Your XR** appears in the “Composite Resources” section (you bought the property!)
1. **Managed Resources start appearing** (the hotel construction begins!)
- PostgreSQL Server shows up with status “Creating”
- Storage Account appears immediately (fast construction!)
1. **Status updates in real-time**
- Watch the PostgreSQL Server go from “Creating” → “Ready”
- All with pretty green/yellow/red indicators

Click on your “customer-database” XR and you’ll see a beautiful tree view:

```
XPostgreSQLInstance: customer-database
├── 🟢 PostgreSQL Server: customer-database-xxxxx
│   └── Status: Ready
│   └── FQDN: customer-db.postgres.database.azure.com
└── 🟢 Storage Account: customerdatabasebackups
    └── Status: Succeeded
    └── Location: eastus
```

It’s like watching your Monopoly properties generate passive income, except this actually pays real money (or costs it, depending on your Azure bill).

## 🏆 Winning the Game: Best Practices

### Don’t Put Hotels on Baltic Avenue

Just like you wouldn’t waste money building hotels on cheap properties, don’t over-provision small environments:

```yaml
# Good: Right-sized for development
apiVersion: database.example.com/v1alpha1
kind: PostgreSQLInstance
metadata:
  namespace: development
  name: dev-database
spec:
  parameters:
    size: small      # db.t3.micro
    storageGB: 20    # Just enough
```

```yaml
# Bad: This is Boardwalk-level infrastructure for a dev environment
apiVersion: database.example.com/v1alpha1
kind: PostgreSQLInstance
metadata:
  namespace: development  
  name: dev-database
spec:
  parameters:
    size: large      # GP_Gen5_8 - WHY?!
    storageGB: 1000  # A terabyte for dev?!
```

Crossview will show you all your resources and their sizes. Use it to catch these expensive mistakes before your Azure bill makes you cry.

### Know When to Fold ’Em

In Monopoly, sometimes you need to mortgage properties to stay in the game. In Crossplane, sometimes you need to delete resources you’re not using.

Crossview makes this easy:

1. Search for old/unused resources
1. Check their last activity time
1. Delete the ones gathering dust

```bash
# Check in Crossview first, then clean up
kubectl delete xpostgresqlinstance old-test-database -n development
```

Watch in Crossview as the XR disappears and all the managed resources gracefully shut down. It’s oddly satisfying, like watching Monopoly properties get returned to the bank.

### Use Labels Like Property Groups

In Monopoly, you want to own all properties of the same color. In Crossplane, use labels to group related resources:

```yaml
apiVersion: database.example.com/v1alpha1
kind: XPostgreSQLInstance
metadata:
  name: user-service-db
  namespace: production
  labels:
    app: user-service
    environment: production
    team: backend
```

Then in Crossview, filter by labels:

- See all “production” resources
- See everything for “user-service”
- Find all resources owned by “backend” team

It’s like being able to highlight all your red properties on the board!

## 🎪 Advanced Strategies: Power Moves

### The Railroad Strategy: Providers

In Monopoly, owning all four railroads is a solid strategy. In Crossplane, installing multiple providers gives you options:

```bash
# The Azure Railroad (your main line!)
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-upbound
spec:
  package: xpkg.upbound.io/upbound/provider-azure:v0.42.0
EOF

# The AWS Railroad  
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-upbound
spec:
  package: xpkg.upbound.io/upbound/provider-aws:v0.42.0
EOF

# The GCP Railroad
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-gcp-upbound
spec:
  package: xpkg.upbound.io/upbound/provider-gcp:v0.42.0
EOF
```

In Crossview’s “Providers” section, you’ll see all your railroads—er, providers—and their health status. Now you can create databases on ANY cloud! Mix and match! Go wild!

### The Boardwalk & Park Place Combo: Compositions for Different Environments

Create multiple Compositions for the same XRD, like having different strategies for different property groups:

```yaml
# High-roller Composition for Production (Boardwalk)
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: postgresql-production
  labels:
    environment: production
spec:
  compositeTypeRef:
    apiVersion: database.example.com/v1alpha1
    kind: XPostgreSQLInstance
  # ... creates geo-redundant PostgreSQL, automated backups, read replicas
```

```yaml
# Budget Composition for Development (Baltic Avenue)
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: postgresql-development
  labels:
    environment: development
spec:
  compositeTypeRef:
    apiVersion: database.example.com/v1alpha1
    kind: XPostgreSQLInstance
  # ... creates single-region PostgreSQL, minimal backups
```

Then in your XR, specify which Composition to use:

```yaml
apiVersion: database.example.com/v1alpha1
kind: XPostgreSQLInstance
metadata:
  name: my-database
  namespace: production
spec:
  compositionRef:
    name: postgresql-production  # The fancy one!
  parameters:
    storageGB: 100
```

Crossview shows you which Composition each XR is using. It’s like seeing which properties have hotels vs. houses!

## 🎬 Real-World Success Story

At my company (totally not making this up), we had 47 databases across Azure and AWS. Nobody knew who owned what. It was like a Monopoly game where someone spilled coffee on the board and we lost track of everything.

Then we installed Crossview.

Within 10 minutes, we discovered:

- 12 databases nobody was using (Free Parking!)
- 8 databases that should’ve been in production but were in staging (someone put hotels on Mediterranean Avenue)
- 3 databases running on SKUs 4x too large (oops, our Azure bill makes sense now)
- 1 database that was somehow running in the wrong region for 8 months (Go directly to jail, do not pass GO)

We deleted the unused ones, right-sized the oversized ones, and documented ownership for everything. Our Azure bill dropped 40% the next month.

**Crossview paid for itself in saved infrastructure costs on day one.** And by “paid for itself,” I mean it’s free, but you get the point.

## 🎯 The Endgame: Why Crossview Matters

Managing infrastructure without Crossview is like playing Monopoly in the dark while drunk. Sure, you might eventually figure out what’s happening, but it’s going to be painful and you’ll make expensive mistakes.

Crossview gives you:

- **Visual clarity**: See your entire infrastructure empire at a glance
- **Real-time updates**: Know when something breaks immediately
- **Relationship mapping**: Understand how resources connect
- **Multi-cluster support**: Manage multiple “game boards” from one dashboard
- **Search and filter**: Find that one database you created 6 months ago
- **Team collaboration**: Everyone can see the same board

Plus, it’s **open source and free**. It’s like getting a deluxe Monopoly set for the price of the cardboard version.

## 🚀 Your Next Move

Ready to turn your infrastructure chaos into an organized game board?

1. **Install Crossplane** (if you haven’t already)
1. **Install Crossview** using the Helm commands above
1. **Open the dashboard** and marvel at your infrastructure empire
1. **Create some XRDs and Compositions** (build your property empire!)
1. **Watch Crossview visualize everything** in real-time
1. **Never go back to managing infrastructure blind** again

Trust me, once you see your infrastructure laid out like a Monopoly board, you’ll wonder how you ever lived without it.

Now if you’ll excuse me, I need to go check Crossview. I think someone just deployed a hotel on my development cluster, and I need to figure out who’s the banker around here.

-----

## 🔗 Resources

- **Crossview GitHub**: https://github.com/corpobit/crossview
- **Crossplane Docs**: https://docs.crossplane.io/
- **Azure Provider Docs**: https://marketplace.upbound.io/providers/upbound/provider-azure
- **Install Guide**: Check the Crossview README for detailed installation instructions
- **My Therapy Bills**: From all the times I managed infrastructure without a GUI

-----

**Have you tried Crossview? Got any funny infrastructure horror stories?** Drop them in the comments! Let’s compare war stories about that time we accidentally deployed production databases to the wrong region. We’ve all been there.

And remember: In Monopoly and in infrastructure, always know where your properties are. Your Azure bill will thank you.

*P.S. - If you actually flip over your Kubernetes cluster like a Monopoly board when things go wrong, please seek professional help. And maybe use Crossview.*

-----

**About The Software’s Journey**: We’re on a mission to make infrastructure management less painful and more fun. Follow us for more analogies that probably shouldn’t work but somehow do. 🎲🚀
