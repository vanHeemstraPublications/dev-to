---

title: "Testing Your Cloud Infrastructure Like IKEA Furniture: 6 Layers of Crossplane v2 Testing (PostgreSQL Example)"
published: false
description: "Learn how to test Crossplane v2 compositions using a 6-layer strategy, explained through the metaphor of assembling IKEA furniture—using PostgreSQL as the running example."
tags: ["kubernetes", "crossplane", "testing", "devops"]
cover_image: https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/test-your-infrastructure-like-your-furniture.png
canonical_url: ""
series: "Infrastructure as Code Adventures"
organization: "the-software-s-journey"
---

Ever assembled an IKEA BILLY bookshelf? You open the box, lay out the pieces, follow the steps, tighten everything, and then do the most important part: give it a careful shake before trusting it with a shelf full of books.

Testing Crossplane compositions is the same idea—except your “bookshelf” is cloud infrastructure, and your “Allen key” is `kubectl`.

This article refactors the testing story into **six testing layers** (1–6), and uses a single prime target throughout: a **PostgreSQL database** composition (Azure PostgreSQL Flexible Server + Database) built with Crossplane v2 pipeline mode.

## Why test your infrastructure? (aka “don’t skip the instructions”)

The failure mode is familiar:

- You changed “one small thing” in a composition
- The rendered YAML looks plausible
- The cluster accepts it
- The cloud provider doesn’t
- Cleanup leaves something behind

A layered strategy gives you fast feedback early, and high confidence later—without paying the cost of running full end-to-end tests for every tiny change.

## The IKEA metaphor (mapping)

| IKEA furniture | Crossplane v2 |
|---|---|
| **Instruction manual** | XRD (CompositeResourceDefinition) |
| **Assembly steps** | Composition (pipeline mode) + Functions |
| **Individual pieces** | Managed Resources (e.g., `ResourceGroup`, `FlexibleServer`, `FlexibleServerDatabase`) |
| **Assembled furniture** | Composite Resource (XR) |
| **Quality checks** | Layered test suite (1–6) |

## The six testing layers (1–6)

Here’s the structure we’ll follow (adapted from the platform’s testing strategy docs):

| Layer | Name | Primary intent | Typical tools |
|---:|---|---|---|
| 1 | Local composition rendering | Validate XRD + Composition logic without a cluster | `crossplane render` |
| 2 | Cluster health + provider validation | Ensure Crossplane stack is stable; providers/functions Healthy | `kubectl`, health scripts, optional Uptest |
| 3 | Visual inspection & relationship debugging | Understand XR → managed resources graph and conditions | Crossview |
| 4 | In-cluster E2E tests | Validate reconciliation behavior and lifecycle | KUTTL |
| 5 | Cloud-side verification | Confirm real Azure resources match intent | Azure CLI |
| 6 | GitOps deployment & monitoring | Continuous reconciliation, drift detection, ops visibility | Flux + Headlamp |

## Our “flat-pack” example: PostgreSQL as a platform API

We’ll build a small Crossplane API package that gives platform consumers a namespaced XR:

- XR kind: `XPostgreSQLDatabase`
- Composed resources: `ResourceGroup` + `FlexibleServer` + `FlexibleServerDatabase`

Here’s the shape of the “instruction manual” (XRD) from the demo (trimmed):

```yaml
# apis/v1alpha1/postgresql-databases/xrd.yaml (excerpt)
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqldatabases.database.example.io
spec:
  group: database.example.io
  names:
    kind: XPostgreSQLDatabase
    plural: xpostgresqldatabases
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
                  location: { type: string, default: westeurope }
                  resourceGroupName: { type: string }
                  databaseName: { type: string, default: appdb }
                  adminUsername: { type: string, default: pgadmin }
                  adminPasswordSecretName: { type: string, default: postgres-admin-password }
                  adminPasswordSecretKey: { type: string, default: password }
                  postgresVersion: { type: string, default: "16" }
                  skuName: { type: string, default: B_Standard_B1ms }
                  storageMb: { type: integer, default: 32768 }
                required: [resourceGroupName]
          status:
            type: object
            properties:
              serverName: { type: string }
              databaseName: { type: string }
```

And here’s the “assembly steps” (Composition) in pipeline mode—showing the three composed resources and how we push useful IDs up into XR status (trimmed):

```yaml
# apis/v1alpha1/postgresql-databases/composition.yaml (excerpt)
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xpostgresqldatabases.database.example.io
  labels:
    provider: azure
    type: standard
spec:
  compositeTypeRef:
    apiVersion: database.example.io/v1alpha1
    kind: XPostgreSQLDatabase
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: resourcegroup
        base:
          apiVersion: azure.m.upbound.io/v1beta1
          kind: ResourceGroup
        # patches: location, external-name, tags, etc.
      - name: flexibleserver
        base:
          apiVersion: dbforpostgresql.azure.m.upbound.io/v1beta1
          kind: FlexibleServer
        patches:
          # ... name transforms to satisfy Azure constraints ...
          - type: ToCompositeFieldPath
            fromFieldPath: metadata.annotations[crossplane.io/external-name]
            toFieldPath: status.serverName
      - name: flexibleserverdatabase
        base:
          apiVersion: dbforpostgresql.azure.m.upbound.io/v1beta1
          kind: FlexibleServerDatabase
        patches:
          - type: FromCompositeFieldPath
            fromFieldPath: spec.parameters.databaseName
            toFieldPath: metadata.annotations[crossplane.io/external-name]
          - type: ToCompositeFieldPath
            fromFieldPath: metadata.annotations[crossplane.io/external-name]
            toFieldPath: status.databaseName
  - step: auto-ready
    functionRef:
      name: function-auto-ready
```

In the repo, the canonical paths used in the demo are:

- `apis/v1alpha1/postgresql-databases/xrd.yaml`
- `apis/v1alpha1/postgresql-databases/composition.yaml`
- `apis/v1alpha1/postgresql-databases/examples/basic.yaml`
- `tests/e2e/postgresql-databases/basic/` (KUTTL)

## Layer 1 — Local composition rendering (unbox the parts)

Before you touch a cluster, validate that your “instruction manual + steps” actually produce the right parts.

Example XR used for rendering (trimmed):

```yaml
# apis/v1alpha1/postgresql-databases/examples/basic.yaml (excerpt)
apiVersion: database.example.io/v1alpha1
kind: XPostgreSQLDatabase
metadata:
  name: render-postgres-example
  namespace: default
spec:
  crossplane:
    compositionSelector:
      matchLabels:
        provider: azure
        type: standard
  parameters:
    location: westeurope
    resourceGroupName: crossplane-e2e-test-rg
    databaseName: appdb
    adminUsername: pgadmin
    adminPasswordSecretName: postgres-admin-password
    adminPasswordSecretKey: password
    postgresVersion: "16"
    skuName: B_Standard_B1ms
    storageMb: 32768
```

Minimal render example (from the demo):

```bash
crossplane render \
  apis/v1alpha1/postgresql-databases/xrd.yaml \
  apis/v1alpha1/postgresql-databases/composition.yaml \
  apis/v1alpha1/postgresql-databases/examples/basic.yaml \
  --include-function-results \
  > rendered-output.yaml
```

This is where you catch:

- wrong patch paths
- schema mismatches between XR parameters and Composition expectations
- naming/transform issues (e.g., lowercasing and sanitizing Azure names)

If you maintain multiple APIs, treat examples as contracts and render them all (the demo includes a `scripts/render-all.sh` pattern that’s suitable for pre-commit and CI).

## Layer 2 — Cluster validation & health (check your workshop is stable)

Even a perfect render can fail if the workshop is broken:

- Crossplane core isn’t stable
- providers/functions aren’t Healthy
- webhooks are timing out (common on local clusters under load)
- `ProviderConfig` credentials are misconfigured

The demo uses a pre-test health script (`scripts/check-crossplane-health.sh`) to gate everything else. The quality bar is simple: **stable Crossplane pods, Healthy providers/functions, and reliable webhook behavior**.

Optional (but powerful): run **Uptest** as a fast provider/credential smoke test (think “verify the screwdriver works” before you build the whole bookshelf).

## Layer 3 — Crossview visual inspection (use the exploded diagram)

When something is off, you want the “exploded view” that shows how everything connects:

- did your XR select the intended Composition?
- which managed resources were created?
- which condition/event explains why the XR isn’t Ready?

Crossview is great here because it visualizes the XR → composed resources graph. Use it as the interactive debugger between Layers 2 and 4.

## Layer 4 — In-cluster E2E with KUTTL (the shake test)

Now we let Kubernetes do the real assembly: create the XR, watch reconciliation, assert readiness, and ensure cleanup works.

The demo’s PostgreSQL test case builds up like this:

- **00**: create a password `Secret` + create the XR
- **00 assert**: wait for XR `Synced=True` and `Ready=True`
- **01 assert**: wait for composed managed resources to become `Ready=True`
- **01 verify (Azure)**: query Azure to ensure the server + database exist
- **02 delete**: delete the XR
- **02 assert**: confirm XR is gone

Representative KUTTL steps (excerpts from `tests/e2e/postgresql-databases/basic/`):

```yaml
# 00-secret.yaml (excerpt)
apiVersion: v1
kind: Secret
metadata:
  name: postgres-admin-password
  namespace: default
type: Opaque
stringData:
  # Demo-only password for e2e tests (Azure enforces complexity rules).
  password: "P@ssw0rd1234!"
```

```yaml
# 00-xr-postgres.yaml (excerpt)
apiVersion: database.example.io/v1alpha1
kind: XPostgreSQLDatabase
metadata:
  name: test-postgres-e2e-001
  namespace: default
spec:
  crossplane:
    compositionSelector:
      matchLabels:
        provider: azure
        type: standard
  parameters:
    location: westeurope
    resourceGroupName: crossplane-e2e-test-rg
    databaseName: appdb
    adminUsername: pgadmin
    adminPasswordSecretName: postgres-admin-password
    adminPasswordSecretKey: password
    postgresVersion: "16"
    skuName: B_Standard_B1ms
    storageMb: 32768
```

```yaml
# 00-assert.yaml (excerpt)
apiVersion: kuttl.dev/v1beta1
kind: TestAssert
timeout: 2400
commands:
- script: |
    kubectl wait -n default xpostgresqldatabase test-postgres-e2e-001 --for=condition=Synced --timeout=2400s
    kubectl wait -n default xpostgresqldatabase test-postgres-e2e-001 --for=condition=Ready --timeout=2400s
```

```yaml
# 01-verify-azure.yaml (excerpt)
apiVersion: kuttl.dev/v1beta1
kind: TestAssert
commands:
- script: |
    SERVER_NAME=$(kubectl get -n default xpostgresqldatabase test-postgres-e2e-001 -o jsonpath='{.status.serverName}')
    DB_NAME=$(kubectl get -n default xpostgresqldatabase test-postgres-e2e-001 -o jsonpath='{.status.databaseName}')
    az postgres flexible-server show --resource-group crossplane-e2e-test-rg --name "$SERVER_NAME" --output none
    az postgres flexible-server db show --resource-group crossplane-e2e-test-rg --server-name "$SERVER_NAME" --database-name "$DB_NAME" --output none
```

KUTTL suite config (so you can run everything consistently):

```yaml
apiVersion: kuttl.dev/v1beta1
kind: TestSuite
timeout: 2400
parallel: 1
startKIND: false
testDirs:
  - ./tests/e2e/postgresql-databases
```

Run it:

```bash
kubectl kuttl test \
  --config tests/e2e/kuttl-test.yaml \
  --timeout 2400 \
  --start-kind=false
```

If your tests don’t include cleanup, they’re not end-to-end—they’re “create-to-end”.

## Layer 5 — Cloud-side verification (confirm it works in the real world)

Kubernetes conditions are necessary, but the cloud control plane is the source of truth.

The demo’s E2E suite uses Azure CLI checks like:

```bash
SERVER_NAME=$(kubectl get -n default xpostgresqldatabase test-postgres-e2e-001 \
  -o jsonpath='{.status.serverName}')

DB_NAME=$(kubectl get -n default xpostgresqldatabase test-postgres-e2e-001 \
  -o jsonpath='{.status.databaseName}')

az postgres flexible-server show \
  --resource-group crossplane-e2e-test-rg \
  --name "$SERVER_NAME" \
  --output none

az postgres flexible-server db show \
  --resource-group crossplane-e2e-test-rg \
  --server-name "$SERVER_NAME" \
  --database-name "$DB_NAME" \
  --output none
```

This catches issues like:

- Azure name constraints
- subscription provider registration gaps (e.g., `Microsoft.DBforPostgreSQL`)
- resources that exist but don’t match intent (location/SKU/tags)

## Layer 6 — GitOps with Flux + Headlamp (keep it assembled over time)

Layer 6 answers a different question: “Can we deliver and operate this platform continuously from Git?”

In the demo, Flux is configured to reconcile the Crossplane APIs from the repo:

- `GitRepository`: `crossplane-configs` (namespace `flux-system`)
- `Kustomization`: `crossplane-apis` (namespace `flux-system`)

Then you run an explicit “proof” test (Step 16.1 in the demo):

- **Option A (config-only, safest)**: change a label in the PostgreSQL `Composition`, commit/push, confirm the label appears on the in-cluster `Composition`.
- **Option B (proves Crossplane reconciliation)**: add a tag to the composed `ResourceGroup` base in the Composition, then confirm:
  - the composed managed resource reflects it
  - optionally, Azure shows it

Reconciling on-demand:

```bash
flux reconcile source git crossplane-configs
flux reconcile kustomization crossplane-apis --with-source
```

Verifying the GitOps flow in-cluster:

```bash
# Confirm your committed label is now on the Composition
kubectl get composition xpostgresqldatabases.database.example.io \
  -o jsonpath='{.metadata.labels.gitops-test}'; echo
```

If you did **Option B** (ResourceGroup tag change), verify Crossplane reconciliation (and optionally Azure):

```bash
kubectl get -n default resourcegroups.azure.m.upbound.io \
  -l crossplane.io/composite=test-postgres-e2e-001 -o yaml

az group show --name crossplane-e2e-test-rg --query "tags.gitopsTest" -o tsv
```

Headlamp (with the Flux plugin) is the “ops dashboard” for this layer: it makes it obvious which Source/Kustomization is failing and why.

## The complete picture (full source)

All the code referenced here—including the PostgreSQL API package, KUTTL suites, helper scripts, and Flux structure—is in:

**[https://github.com/software-journey/crossplane-e2e-testing](https://github.com/software-journey/crossplane-e2e-testing)**

## Key takeaways (your assembly summary sheet)

- **Layer 1 catches the most mistakes fastest**: render before you reconcile.
- **Layer 2 prevents noisy failures**: don’t trust E2E results from an unhealthy cluster.
- **Layer 3 shortens debugging**: visualize the XR → managed resource graph.
- **Layer 4 proves lifecycle correctness**: create, assert, verify, delete.
- **Layer 5 closes the loop**: validate cloud reality, not just Kubernetes status.
- **Layer 6 makes it operable**: Git → Flux → Kubernetes → Crossplane, continuously.

---

**About the Author**: I'm Willem, a Cloud Engineer transitioning to platform engineering. I believe complex infrastructure concepts should be accessible to everyone—even if it means comparing them to Swedish furniture.
