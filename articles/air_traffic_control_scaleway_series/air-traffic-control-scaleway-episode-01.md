---

title: "Air Traffic Control Scaleway Ep.1"
published: false
part: 1
description: "Episode 1 of the Air Traffic Control series: configure Identity and Access Management on Scaleway — who flies, who watches, and who stays on the ground. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, iam, security]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-01.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"

---

# Cleared for Approach: Identity and Access Management on Scaleway

*“F-A-B, Mr. Tracy. All runways are cleared. But before any aircraft lifts off, we must know exactly* who *is behind the controls — and precisely* what *they are cleared to do.”*
*— International Rescue, Thunderbird 5 Orbital Station*

-----

Welcome to the **Scaleway Air Traffic Control Centre** — your operations hub in the French cloud.

In this series, we run our infrastructure the way International Rescue manages its missions: with discipline, precision, and absolute clarity about who is authorised to do what. In a busy airport, you do not simply wave aircraft onto the runway. Every pilot has a licence. Every aircraft has a flight plan. Every gate has a crew with specific clearances.

**Identity and Access Management (IAM)** on Scaleway works on precisely this principle.

Think of your Scaleway **Organisation** as Thunderbird Island itself — the central command. Your **Projects** are the individual Thunderbird vehicles: Dev is Thunderbird 1 (fast, agile, first on the scene), Production is Thunderbird 2 (heavy lifting, critical cargo), and Test is Thunderbird 3 (probing unmapped territory). Each requires its own flight crew, its own access codes, and its own launch protocols.

By the end of this episode, you will have configured the entire clearance architecture: SSH keys, collaborators, groups, applications, policies, and an API key — all locked down in a manner that would satisfy even the most zealous International Rescue security review.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

- Set up multiple **Projects** within a Scaleway Organisation
- Access the **IAM** section of the Scaleway Console
- Create **member accounts** and invite collaborators to your Organisation
- Navigate between Organisations as a guest member
- Create a **Group** and assign members to it
- Create **Applications** for non-human (programmatic) principals
- Define **Policies** with scoped permission sets for different principals
- Attach an existing Policy to an Application
- Generate an **API key** with a controlled expiry window
- Authenticate a live Scaleway API request using a secret key

### Pre-Launch Checklist

Before Scott Tracy can take Thunderbird 1 to maximum velocity, ground crew run their checks. Do the same:

- ✅ You hold an active [Scaleway account](https://console.scaleway.com) and own an Organisation
- ✅ Two teammates are available — they will serve as co-pilots, each assigned a different clearance level

-----

## 📊 SIPOC — How IAM Moves Through the System

Before we touch the Console, let us map the process. IAM is not a single action — it is a pipeline. The **SIPOC** model (Supplier → Input → Process → Output → Consumer) reveals exactly how identity and access flow through your Scaleway Organisation.

|Stage|SIPOC Element|IAM Equivalent                                                                                         |Example                                                                                                           |
|-----|-------------|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway IAM engine + your Organisation Owner account                                                  |The platform and the human who configures it                                                                      |
|**I**|**Input**    |Member definitions, Group memberships, Application names, Policy rules                                 |“User: teammate-1, Group: Developers, Scope: Dev project, Permission: FullAccess”                                 |
|**P**|**Process**  |Creating Projects → Onboarding members → Defining Groups → Writing Policies → Issuing API keys         |All the hands-on steps in this episode                                                                            |
|**O**|**Output**   |A working IAM architecture: scoped permissions enforced across all projects                            |Teammate 1 can create Instances in Dev. Teammate 2 can create Instances in Production. Applications hold API keys.|
|**C**|**Consumer** |Developers, CI/CD pipelines, automation scripts, and applications that interact with Scaleway resources|Your team, `app-1`, `app-2`, and your own `curl` commands                                                         |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway IAM   ──▶   Members         ──▶  Create Projects  ──▶  Scoped        ──▶   Developers
engine               Groups               Onboard users         policies              CI/CD
                     Applications         Define groups         enforced              pipelines
Organisation         Policy rules         Write policies        across all            Applications
Owner account        SSH keys             Issue API keys        projects              (app-1, app-2)
```

> **Tower to crew:** The SIPOC view tells us something important — IAM is only as good as the inputs you provide. Vague policy rules produce vague clearances. Garbage in, unrestricted access out. Thunderbird Island does not operate on vague.

-----

## 🛫 Section 1 — Establishing the Flight Zones: Set Up Projects

Every International Rescue operation begins with a clear separation of zones. We mirror this discipline with three Scaleway Projects.

### 1.1 — Create Three Projects

1. In the **Organisation Dashboard** menu, select the **Projects** tab.
1. Click **Create Project** and enter `Dev` as the Project Name.
1. Repeat to create a project named `Production`.
1. Repeat once more for a project named `Test`.

### 1.2 — Generate Three SSH Keys — One Per Zone

An SSH key is your pilot’s licence. Each zone gets its own key; cross-zone entry is not permitted. Open your terminal:

```bash
# Generate Ed25519 keys, AES-256-GCM encrypted, no passphrase
ssh-keygen -t ed25519 -C "login" -Z aes256-gcm@openssh.com \
           -f handson-iam-dev.pub -N ""

ssh-keygen -t ed25519 -C "login" -Z aes256-gcm@openssh.com \
           -f handson-iam-production.pub -N ""

ssh-keygen -t ed25519 -C "login" -Z aes256-gcm@openssh.com \
           -f handson-iam-test.pub -N ""
```

> **Why Ed25519?** It is modern, compact, and resistant to the brute-force attacks that might trouble a less security-conscious organisation. The `-Z aes256-gcm@openssh.com` flag encrypts the private key file at rest. International Rescue keeps its launch codes safe.

### 1.3 — Register SSH Keys to Each Project

Repeat this procedure for `Dev`, `Test`, and `Production` — using the corresponding key file each time.

1. Run `cat handson-iam-dev.pub` in your terminal to display the public key.
1. Copy the key. It begins with `ssh-ed25519`.
1. In the **Organisation Dashboard**, click the `Dev` project, then select the **SSH keys** tab.
1. Click **Add SSH key**. Enter a name such as `Hands on IAM dev` and paste the public key.
1. Click **Add SSH key** to confirm.
1. Repeat for `Test` and `Production` using their respective key files.

-----

## 🧑‍✈️ Section 2 — Crew Manifest: Adding Collaborators

No mission launches with anonymous personnel aboard. We now bring our two teammates into the Organisation — each with their own identity and password, ready to receive specific clearances.

1. In the **Management & Governance** drop-down, select **IAM**.
1. Select the **Users** tab, then click **Create member**.
1. For each teammate: enter their `username`, select **Send password by email**, then add their `email` and personal information. Leave **Assign member to group** empty for now. Click **Create member**.
1. Ask each teammate to check their inbox and log in to your Organisation.
1. Repeat for the second teammate.

> **Note:** Once logged in, teammates can reach your Organisation via the **Organisation** drop-down → **+ Add Organisation**. They will see the projects you created — but, with no policy assigned yet, they cannot touch anything. Clearance is coming. Patience, as Brains would say.

-----

## 🏗️ Section 3 — Clearance Architecture: Groups, Applications & Policies

With the crew aboard, we build the clearance architecture — the system that determines who may access which runway, and with what authority.

Think of it this way:

- A **Group** is a flight crew qualification — all pilots in the group share the same category of clearance.
- A **Policy** is the air traffic control instruction that says precisely which zones that clearance covers.
- An **Application** is an unmanned probe — a programmatic identity with its own flight plan.

### 3.1 — Create the Developers Group

1. In **IAM**, select the **Groups** tab. Click **Create group**.
1. Enter `Developers` as the Name. Leave Tags empty.
1. Click **Add a member** and add your first teammate.
1. Confirm with **Create group**.

### 3.2 — Deploy Unmanned Probes: Create Applications

Thunderbird 3 can fly to Space Station Alpha without a human crew. Our Applications are the cloud equivalent — automated systems that need identities and permissions, but no login.

1. In **IAM**, select the **Applications** tab. Click **Create application**.
1. Name it `app-1`. Leave Tags and Policy empty. Confirm.
1. Repeat to create a second application named `app-2`.

### 3.3 — Issue Flight Plans: Create Policies & Configure Rules

Three principals. Three policies. Each one a precisely scoped flight authorisation.

Navigate to **IAM** → **Policies** → **Create policy** for each of the following.

#### Policy A — Developers Group

|Field                   |Value                                                |
|------------------------|-----------------------------------------------------|
|**Name**                |`Hands on IAM developers`                            |
|**Principal**           |Group → `Developers`                                 |
|**Rule 1 — Scope**      |Access to resources → `Dev` project                  |
|**Rule 1 — Permissions**|AllProducts → `AllProductsFullAccess`                |
|**Rule 2 — Scope**      |Access to resources → All current and future projects|
|**Rule 2 — Permissions**|AllProducts → `AllProductsReadOnly`                  |

Work through the policy wizard in order: set **① Scope** and validate; set **② Permission sets** and validate; leave **③ CEL conditions** empty; add a second rule via **Add rule** and repeat. Finalise with **Create policy**.

> **Tower confirms:** Teammate 1 now has full command over the Dev zone and read-only visibility everywhere else. Ask them to attempt launching an Instance in both Dev and Production. Dev succeeds; Production refuses. Exactly as the clearance system intends.

#### Policy B — Individual User

|Field                   |Value                                     |
|------------------------|------------------------------------------|
|**Name**                |`Hands on IAM User`                       |
|**Principal**           |User → Teammate 2                         |
|**Rule 1 — Scope**      |Access to resources → `Production` project|
|**Rule 1 — Permissions**|Compute → `InstancesFullAccess`           |


> **Tower confirms:** Teammate 2 has been given the Production runway — specifically for compute resources. They can create and manage Instances there, and nowhere else.

#### Policy C — Application Principal

|Field                   |Value                                |
|------------------------|-------------------------------------|
|**Name**                |`app-policy`                         |
|**Principal**           |Application → `app-1`                |
|**Rule 1 — Scope**      |Access to resources → `Test` project |
|**Rule 1 — Permissions**|AllProducts → `AllProductsFullAccess`|

### 3.4 — Transfer Flight Plan: Attach Policy to app-2

`app-2` currently has no clearance — it sits idle on the apron. Rather than writing a new policy, we duplicate the existing `app-policy`.

1. In **IAM** → **Applications**, click `app-2`, then open the **Groups & Policies** tab.
1. In the **Policies** section, click **Attach a policy**.
1. Select **Duplicate an existing policy**, then choose `app-policy`. Confirm.

-----

## 🗺️ IAM Architecture — The Clearance Map

Your Organisation’s IAM implementation should now match the following layout:

```
┌────────────────────────────────────────────────────────────────┐
│                     ORGANISATION                               │
│                                                                │
│  PRINCIPALS             POLICIES              PROJECTS         │
│  ──────────────         ─────────────         ───────────      │
│                                                                │
│  Developers  ──────▶  IAM developers ──▶  Dev (Full)          │
│  Group                                ──▶  All (Read-Only)    │
│  (Teammate 1)                                                  │
│                                                                │
│  Teammate 2  ──────▶  IAM User       ──▶  Production          │
│  (IAM user)                               (InstancesFullAccess)│
│                                                                │
│  app-1       ──────▶  app-policy     ──▶  Test (Full)         │
│                                                                │
│  app-2       ──────▶  app-policy     ──▶  Test (Full)         │
│               (duplicated)                                     │
└────────────────────────────────────────────────────────────────┘
```

-----

## 🔑 Section 4 — The Master Override: API Keys

Every control tower has a master key — used sparingly, stored securely, and never left on the desk. In Scaleway, the **API key** is that master key. It allows you to issue commands to the platform programmatically, bypassing the Console entirely.

### 4.1 — Generate an API Key

1. In **IAM**, select the **API keys** tab. Click **Generate API key**.
1. Select **Myself (IAM user)** as the bearer.
1. Leave Description empty. Set **Expiration** to `1 hour`.
1. Select **No** for Object Storage usage.
1. Copy and securely store the **Secret Key** displayed. It will not be shown again.

> ⚠️ **Security Protocol — Restricted:** A Secret Key is sensitive data of the highest classification. Never commit it to a repository, paste it into a chat message, or leave it in a shell history file. The Organisation Owner’s API key inherits full permissions — treat it accordingly. International Rescue does not negotiate with those who mishandle launch codes.

> **Note:** When an Organisation Owner generates an API key for themselves, the key carries all permissions, since the Owner holds all permissions.

### 4.2 — Rename a Project via the Scaleway API

We will demonstrate the API key by renaming the `Test` project to `updated_test` — without touching the Console. A single `curl` command, precisely aimed.

1. In the **Project** header drop-down, select `Test`, then click **Copy ID** next to the project name to copy its UUID.
1. Open a terminal and run the following command, substituting your actual secret key and project ID:

```bash
curl -X PATCH \
  -H "X-Auth-Token: <your_secret_key>" \
  -H "Content-Type: application/json" \
  -d '{"name": "updated_test"}' \
  "https://api.scaleway.com/account/v3/projects/<test_project_id>"
```

1. Refresh your browser. The `Test` project is now named `updated_test`.

> **Note:** Take care with invisible whitespace when copying keys and IDs from the Console — a single hidden character produces a 401 Unauthorised response, and even the most experienced tower controller will spend a frustrating few minutes debugging. You have been warned by someone who has been there.

-----

## 🚀 Section 5 — Advanced Flight Options

You have now proven your ability at the controls. But International Rescue never stops improving its equipment. The API key you generated can power far more than a single `curl` call. Two recommended flight paths once you have your bearings:

### Scaleway CLI

The [Scaleway CLI](https://github.com/scaleway/scaleway-cli/blob/master/docs/commands/iam.md) gives you full IAM control from the terminal. Install it and try:

```bash
# List all IAM policies in your organisation
scw iam policy list

# Describe a specific policy by ID
scw iam policy get policy-id=<your-policy-id>

# List all IAM users
scw iam user list
```

### Terraform Provider

The [Scaleway Terraform provider](https://registry.terraform.io/providers/scaleway/scaleway/latest/docs/resources/iam_api_key) lets you manage IAM as infrastructure-as-code. A minimal API key resource looks like this:

```hcl
resource "scaleway_iam_application" "app_ci" {
  name        = "app-ci-pipeline"
  description = "Programmatic identity for CI/CD pipeline"
}

resource "scaleway_iam_api_key" "app_ci_key" {
  application_id = scaleway_iam_application.app_ci.id
  description    = "CI pipeline key — rotated monthly"
  expires_at     = "2026-04-01T00:00:00Z"
}
```

> The Terraform approach is strongly recommended for any IAM configuration that will persist beyond a lab environment. Infrastructure-as-code means your clearance architecture is version-controlled, peer-reviewed, and reproducible — three qualities that Jeff Tracy demands of every Thunderbird system.

-----

## 📋 Episode Debrief

*“All systems nominal. Clearances verified. The runway is yours — and only yours. Thunderbirds are GO.”*
*— Jeff Tracy, Thunderbird Island Operations Centre*

In this episode, you have:

- ✅ Created three Projects — `Dev`, `Production`, `Test` — each with its own SSH key
- ✅ Onboarded two collaborators as Organisation members
- ✅ Established a `Developers` Group for shared clearance management
- ✅ Registered two Applications as non-human principals (`app-1`, `app-2`)
- ✅ Defined three Policies with scoped permission sets across group, user, and application principals
- ✅ Duplicated an existing Policy and attached it to `app-2`
- ✅ Generated an API key with a one-hour expiry window
- ✅ Executed a live Scaleway API call via `curl` to rename a project
- ✅ Mapped the full process through the SIPOC model

The clearance architecture is in place. In the next episode, we will spin up our first compute resources inside these carefully guarded zones — and the IAM rules we built today will be the first thing that greets them.

-----

## 📡 Further Transmissions

- [Scaleway IAM documentation](https://www.scaleway.com/en/docs/iam/concepts/)
- [Scaleway CLI — IAM command reference](https://github.com/scaleway/scaleway-cli/blob/master/docs/commands/iam.md)
- [Terraform Provider — `scaleway_iam_api_key`](https://registry.terraform.io/providers/scaleway/scaleway/latest/docs/resources/iam_api_key)
- [Scaleway API — Update Project endpoint](https://www.scaleway.com/en/developers/api/account/#path-projects-update-project)

-----

*Estimated reading time: 12 minutes. Estimated hands-on time: 45–60 minutes with teammates.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
