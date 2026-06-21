---
title: "Agility Game and Detective Operating System with Open Engineering Platform! Ep.14: Backstage Learns to Read Minds (and Clusters)"
published: false
description: "Episode 14: Somebody has to produce the commits Flux is waiting for. This episode meets Backstage's two real contributions to MVP 2: a Catalog provider that quietly turns live cluster resources into browsable Catalog entries, and a Scaffolder template that mirrors the OEP CLI exactly and opens a genuine GitHub pull request when a user clicks a button instead of typing a command."
tags: [backstage, kubernetes, typescript, devops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-14.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

# Agility Game and Detective Operating System with Open Engineering Platform! 🕵️🎮
## Episode 14: Backstage Learns to Read Minds (and Clusters)

---

## The Part Where Someone Has to Click a Button

Episode 13 left us with an honest gap: Flux is ready to watch a repository, but nobody's described which repository or which paths yet, and someone still has to produce commits for it to eventually watch. The CLI from Episode 12 is one way to produce those commits. Backstage is the OTHER way -- and, unlike the Flux bundle, it's already fully wired, tested, and capable of opening real pull requests against real GitHub repositories.

This episode covers Backstage's two genuinely shipped contributions: a Catalog provider that quietly reads the cluster and turns what it finds into browsable entries, and a Scaffolder template that gives a non-YAML-fluent user the exact same capability as `oep create investigation`, expressed as a form with a submit button.

---

## SIPOC -- The Backstage Layer

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| OepCatalogProvider (backend plugin) | Live Kind, Capability, Space, Mission, etc. CRs sitting in the cluster | Poll the Kubernetes API, map each CR to a Backstage Catalog entity shape via a shared mapping table | Catalog entries of kind Resource or Component, tagged oep.io/<type> | Any user browsing the Backstage Catalog UI -- who sees real cluster state, not a hand-maintained registry |
| The Scaffolder Template (create-investigation) | A user filling in a form: name, purpose, optional kindRef, optional capabilityRefs, target repo | Render a Journey YAML from a skeleton, then either open a PR or commit directly | A new repositories/journeys/<name>.yaml file landing in Git | The exact same downstream pipeline Episode 13 described: Flux (eventually), or oep run --mode server today |
| The oepDashboards backend router | HTTP requests from the frontend plugin | Query live Journey and Outcome CRs, shape them for the React components (Episode 15) | JSON responses the JourneysPage and OutcomesPage components render | Whoever's looking at the dashboard, deciding whether to check on a Journey's progress |

---

## The Catalog Provider: Cluster State, Quietly Becoming a Catalog

```typescript
// backstage/packages/backend/src/plugins/oepCatalogProvider/mapping.ts

export type OepResourceMapping = {
  plural: string;
  k8sKind: string;
  backstageKind: 'Component' | 'Resource';
  specType: string;
  tagSuffix: string;
  owner: string;
  lifecycle?: string;
};

export const OEP_RESOURCE_MAPPINGS: ReadonlyArray<OepResourceMapping> = [
  {
    plural: 'kinds',
    k8sKind: 'Kind',
    backstageKind: 'Resource',
    specType: 'oep-kind',
    tagSuffix: 'kind',
    owner: 'group:default/oep',
  },
  {
    plural: 'capabilities',
    k8sKind: 'Capability',
    backstageKind: 'Resource',
    specType: 'oep-capability',
    tagSuffix: 'capability',
    owner: 'group:default/oep',
  },
  {
    plural: 'spaces',
    k8sKind: 'Space',
    backstageKind: 'Component',
    specType: 'oep-space',
    tagSuffix: 'space',
    owner: 'group:default/oep',
    lifecycle: 'production',
  },
  {
    plural: 'missions',
    k8sKind: 'Mission',
    backstageKind: 'Component',
    specType: 'oep-mission',
    tagSuffix: 'mission',
    owner: 'group:default/oep',
    lifecycle: 'production',
  },
  // ... agents, evidence, results, journeys, outcomes follow the same shape
];
```

This one table is doing all the conceptual heavy lifting. `Kind` and `Capability` -- the purely descriptive ontology nouns from Episode 9 -- get mapped to Backstage's `Resource` entity kind, because they describe something that exists but doesn't itself "run." `Space` and `Mission` get mapped to `Component`, with an explicit `lifecycle: production`, because they're closer to things a Backstage user would think of as actively running pieces of a system. The mapping is genuinely thoughtful about Backstage's own ontology, not just a mechanical 1-to-1 dump of Kubernetes Kinds into Catalog entries.

```
WHAT THIS BUYS BOTH PLATFORM OWNERS

  Without the Catalog provider:
    Someone manually maintains a catalog-info.yaml file describing
    "here are the Spaces and Missions that exist," which drifts
    out of date the moment anyone applies a new one via kubectl,
    the CLI, or a future Agility Game controller.

  With the Catalog provider:
    The Catalog reflects whatever is ACTUALLY in the cluster, polled
    directly from the Kubernetes API, refreshed automatically. If
    Agility Game's owner applies their own Space tomorrow with
    kindRef: onboarding, it shows up in the Catalog without either
    owner editing a single YAML file by hand.
```

---

## The Scaffolder Template: Same Capability, Friendlier Costume

```yaml
# backstage/examples/templates/create-investigation/template.yaml (abbreviated)

apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: create-oep-investigation
  title: Create OEP Investigation
  description: >-
    Create a new OEP Journey (investigation) by committing
    repositories/journeys/<name>.yaml to the ontology repo. Mirrors the
    oep create investigation CLI -- Flux + Crossplane pick the YAML up
    after merge and fan it out into the cluster.
spec:
  owner: group:default/oep
  type: investigation

  parameters:
    - title: Investigation details
      required: [name, purpose]
      properties:
        name:
          title: Name
          type: string
          pattern: '^[a-z][a-z0-9-]{1,62}[a-z0-9]$'
        purpose:
          title: Purpose
          type: string
          description: spec.purposeRef -- short identifier of the Purpose this investigation serves.
        kindRef:
          title: Kind (optional)
          type: string
          ui:field: EntityPicker
          ui:options:
            allowArbitraryValues: true
            catalogFilter:
              kind: Resource
              spec.type: oep-kind
        capabilityRefs:
          title: Capabilities (optional)
          type: array
          items: { type: string }
          ui:field: MultiEntityPicker
          ui:options:
            allowArbitraryValues: true
            catalogFilter:
              kind: API
              spec.type: oep-capability

    - title: Repository + PR settings
      required: [repoUrl]
      properties:
        repoUrl:
          title: Repository
          type: string
          default: github.com?owner=open-engineering-platform&repo=source
          ui:field: RepoUrlPicker
        openPullRequest:
          title: Open a Pull Request
          type: boolean
          default: true

  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          purpose: ${{ parameters.purpose }}
          kindRef: ${{ parameters.kindRef }}
          capabilityRefs: ${{ parameters.capabilityRefs }}
          repoUrl: ${{ parameters.repoUrl }}

    - id: publish-pr
      action: publish:github:pull-request
      if: ${{ parameters.openPullRequest }}
      input:
        repoUrl: ${{ parameters.repoUrl }}
        title: 'feat(journey): create ${{ parameters.name }}'

    - id: publish-direct
      action: publish:github
      if: ${{ not parameters.openPullRequest }}
      input:
        repoUrl: ${{ parameters.repoUrl }}
        defaultBranch: main
```

Look closely at that `kindRef` field's `EntityPicker` configuration: `catalogFilter: { kind: Resource, spec.type: oep-kind }`. That filter ONLY works because the Catalog provider from earlier in this episode already populated the Catalog with real `Kind` resources tagged `oep-kind`. The Scaffolder form and the Catalog provider are not two unrelated features that happen to ship in the same release -- the form's dropdown is LITERALLY populated by querying the same Catalog the provider maintains. A user filling in this form sees the actual `refactoring`, `security`, and `education` Kinds that exist in the cluster right now, not a hardcoded list someone forgot to update six months ago.

---

## Architecture Diagram: Two Paths, Same Destination

```
+-----------------------------------------------------------------------+
|  PATH A: the CLI (Episode 12)                                        |
|                                                                       |
|  Terminal --> oep create investigation demo --purpose ... --kind ... |
|       --> repositories/journeys/demo.yaml written                    |
|       --> git add, commit, push (internal/gitx)                       |
+----------------------------------+------------------------------------+
                                   |
+----------------------------------v------------------------------------+
|  PATH B: Backstage Scaffolder (this episode)                         |
|                                                                       |
|  Browser --> fills in Create OEP Investigation form                  |
|       --> EntityPicker shows REAL Kinds from OepCatalogProvider       |
|       --> fetch:template renders repositories/journeys/demo.yaml     |
|       --> publish:github:pull-request opens an ACTUAL GitHub PR      |
+----------------------------------+------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|              repositories/journeys/demo.yaml lands in Git             |
|              (via direct push, OR via PR merge -- either way)         |
+----------------------------------+------------------------------------+
                                   |
                                   v
              Episode 13's honest diagram from here:
              --mode server applies it directly today,
              OR Flux picks it up automatically once
              flux/sources/ and flux/kustomizations/ exist
```

Neither path is more "real" than the other. A terminal-comfortable engineer and a product manager who has never seen `kubectl` produce the EXACT SAME committed YAML file, validated against the EXACT SAME `journeys.oep.io` CRD schema from Episode 10, because both paths ultimately render from the same conceptual shape -- one via Cobra flags, one via a Backstage form.

---

## The Conversation, Resumed

OWNER OF AGILITY GAME: "If I wanted my own 'Create Onboarding Level' Scaffolder template, would it need to touch your create-investigation template at all?"

OWNER OF DETECTIVE OPERATING SYSTEM: "Not even slightly. You'd write your own template.yaml with your own EntityPicker filters -- probably pointed at a kindRef of onboarding instead of refactoring -- and your own skeleton rendering whatever YAML your Composition expects. The only thing we'd share is the same Backstage instance hosting both templates side by side in the same Scaffolder catalog, the way two unrelated apps sit on the same app store without ever importing each other's code."

OWNER OF AGILITY GAME: "And the Catalog provider would pick up MY resources automatically too, the same way it picks up yours?"

OWNER OF DETECTIVE OPERATING SYSTEM: "As long as your CRDs follow the same oep.io/v1alpha1 shape and you add your plural/kind pair to the shared OEP_RESOURCE_MAPPINGS table -- which is itself just a TypeScript array, not a gatekeeper -- yes. The provider doesn't care whose resource it is. It only cares whether the shape matches."

---

## What's Next: The Dashboards

Backstage can now CREATE a Journey via a form. The next question is whether it can show you what happened to it afterward. In Episode 15, we open the JourneysPage and OutcomesPage React components, and the backend router that feeds them -- the part of MVP 2 that turns "I clicked a button three minutes ago" into "here is exactly what stage that Journey is in right now."

---

**Resources**
- OEP source repository: the MVP 2 codebase this episode is built from
- Backstage Software Catalog: backstage.io/docs/features/software-catalog/overview
- Backstage Scaffolder: backstage.io/docs/features/software-templates/

---

*Agility Game and Detective Operating System with Open Engineering Platform -- two platforms, zero shared dependencies, one ontology underneath them both.*
