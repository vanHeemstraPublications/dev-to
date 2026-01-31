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

This article refactors the testing story into **six testing layers** (0–5), and uses a single prime target throughout: a **PostgreSQL database** composition (Azure PostgreSQL Flexible Server + Database) built with Crossplane v2 pipeline mode.

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
| **Quality checks** | Layered test suite (0–5) |

## The six testing layers (0–5)

Here’s the structure we’ll follow (adapted from the platform’s testing strategy docs):

| Layer | Name | Primary intent | Typical tools |
|---:|---|---|---|
| 0 | Local composition rendering | Validate XRD + Composition logic without a cluster | `crossplane render` |
| 1 | Cluster health + provider validation | Ensure Crossplane stack is stable; providers/functions Healthy | `kubectl`, health scripts, optional Uptest |
| 2 | Visual inspection & relationship debugging | Understand XR → managed resources graph and conditions | Crossview |
| 3 | In-cluster E2E tests | Validate reconciliation behavior and lifecycle | KUTTL |
| 4 | Cloud-side verification | Confirm real Azure resources match intent | Azure CLI |
| 5 | GitOps deployment & monitoring | Continuous reconciliation, drift detection, ops visibility | Flux + Headlamp |

## Our “flat-pack” example: PostgreSQL as a platform API

We’ll build a small Crossplane API package that gives platform consumers a namespaced XR:

- XR kind: `XPostgreSQLDatabase`
- Composed resources: `ResourceGroup` + `FlexibleServer` + `FlexibleServerDatabase`

In the repo, the canonical paths used in the demo are:

- `apis/v1alpha1/postgresql-databases/xrd.yaml`
- `apis/v1alpha1/postgresql-databases/composition.yaml`
- `apis/v1alpha1/postgresql-databases/examples/basic.yaml`
- `tests/e2e/postgresql-databases/basic/` (KUTTL)

## Layer 0 — Local composition rendering (unbox the parts)

Before you touch a cluster, validate that your “instruction manual + steps” actually produce the right parts.

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

## Layer 1 — Cluster validation & health (check your workshop is stable)

Even a perfect render can fail if the workshop is broken:

- Crossplane core isn’t stable
- providers/functions aren’t Healthy
- webhooks are timing out (common on local clusters under load)
- `ProviderConfig` credentials are misconfigured

The demo uses a pre-test health script (`scripts/check-crossplane-health.sh`) to gate everything else. The quality bar is simple: **stable Crossplane pods, Healthy providers/functions, and reliable webhook behavior**.

Optional (but powerful): run **Uptest** as a fast provider/credential smoke test (think “verify the screwdriver works” before you build the whole bookshelf).

## Layer 2 — Crossview visual inspection (use the exploded diagram)

When something is off, you want the “exploded view” that shows how everything connects:

- did your XR select the intended Composition?
- which managed resources were created?
- which condition/event explains why the XR isn’t Ready?

Crossview is great here because it visualizes the XR → composed resources graph. Use it as the interactive debugger between Layers 1 and 3.

## Layer 3 — In-cluster E2E with KUTTL (the shake test)

Now we let Kubernetes do the real assembly: create the XR, watch reconciliation, assert readiness, and ensure cleanup works.

The demo’s PostgreSQL test case builds up like this:

- **00**: create a password `Secret` + create the XR
- **00 assert**: wait for XR `Synced=True` and `Ready=True`
- **01 assert**: wait for composed managed resources to become `Ready=True`
- **01 verify (Azure)**: query Azure to ensure the server + database exist
- **02 delete**: delete the XR
- **02 assert**: confirm XR is gone

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

## Layer 4 — Cloud-side verification (confirm it works in the real world)

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

## Layer 5 — GitOps with Flux + Headlamp (keep it assembled over time)

Layer 5 answers a different question: “Can we deliver and operate this platform continuously from Git?”

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

Headlamp (with the Flux plugin) is the “ops dashboard” for this layer: it makes it obvious which Source/Kustomization is failing and why.

## The complete picture (full source)

All the code referenced here—including the PostgreSQL API package, KUTTL suites, helper scripts, and Flux structure—is in:

**[https://github.com/software-journey/crossplane-e2e-testing](https://github.com/software-journey/crossplane-e2e-testing)**

## Key takeaways (your assembly summary sheet)

- **Layer 0 catches the most mistakes fastest**: render before you reconcile.
- **Layer 1 prevents noisy failures**: don’t trust E2E results from an unhealthy cluster.
- **Layer 2 shortens debugging**: visualize the XR → managed resource graph.
- **Layer 3 proves lifecycle correctness**: create, assert, verify, delete.
- **Layer 4 closes the loop**: validate cloud reality, not just Kubernetes status.
- **Layer 5 makes it operable**: Git → Flux → Kubernetes → Crossplane, continuously.

---

**About the Author**: I'm Willem, a Cloud Engineer transitioning to platform engineering. I believe complex infrastructure concepts should be accessible to everyone—even if it means comparing them to Swedish furniture.
