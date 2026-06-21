---
title: "Agility Game and Detective Operating System with Open Engineering Platform! Ep.15: Watching Two Strangers' Journeys Without Reading Their Diaries"
published: false
description: "Episode 15: A Journey was created in Episode 14. Something has to show you what happened to it. This episode opens the JourneysPage and OutcomesPage React components, the typed shapes that mirror raw Kubernetes JSON without pretending to know more than they do, and the exact INTENT_MVP_2 section 9 JSON contract that keeps the CLI and the dashboard honest with each other."
tags: [react, typescript, kubernetes, dashboards]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-15.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

# Agility Game and Detective Operating System with Open Engineering Platform! 🕵️🎮
## Episode 15: Watching Two Strangers' Journeys Without Reading Their Diaries

---

## A Dashboard That Doesn't Pretend to Know More Than It Does

There's a particular failure mode common to dashboards built on top of someone else's data: the dashboard's TypeScript types get more confident than the actual data ever was. A field that's genuinely optional in Kubernetes gets typed as required in the frontend, the UI renders beautifully right up until the one Journey that's missing that field crashes the page.

MVP 2's dashboard plugin avoids this trap with a discipline worth admiring: every type mirrors the raw JSON, optional fields stay optional, and the components are written to degrade gracefully rather than assume. This episode walks through exactly how that restraint is implemented, and why both platform owners should actually want their dashboards built this cautiously.

---

## SIPOC -- The Dashboard Layer

| Suppliers | Inputs | Process | Outputs | SIPOC Customers |
|---|---|---|---|---|
| oepDashboards backend router | Live Journey and Outcome CRs from the Kubernetes API | Query the cluster, pass the raw JSON through with minimal reshaping | An ItemsResponse JSON envelope for each resource type | The frontend plugin's JourneysPage and OutcomesPage components |
| JourneysPage.tsx | The ItemsResponse<JourneyResource> payload | Render a table: name, stage, age, linked resources -- tolerating missing fields throughout | A live, readable view of every Journey's current stage | Whoever's checking on progress without wanting to learn kubectl |
| OutcomesPage.tsx | The ItemsResponse<OutcomeResource> payload | Render title, phase, and a link back to the resultRef | A readable summary of what was actually learned or produced | Whoever cares about the OUTCOME, not the mechanics that produced it |

---

## The Types: Optional, All the Way Down

```typescript
// backstage/plugins/oep-dashboards/src/types.ts

export type LinkedResource = {
  kind?: string;
  name?: string;
  namespace?: string;
  phase?: string;
  ref?: string;
};

export type JourneyResource = {
  apiVersion?: string;
  kind?: string;
  metadata?: {
    name?: string;
    namespace?: string;
    creationTimestamp?: string;
    [k: string]: unknown;
  };
  spec?: Record<string, unknown>;
  status?: {
    stage?: string;
    lastTransitionTime?: string;
    linkedResources?: LinkedResource[];
    conditions?: Array<{
      type?: string;
      status?: string;
      reason?: string;
      message?: string;
      lastTransitionTime?: string;
    }>;
    [k: string]: unknown;
  };
};

export type OutcomeResource = {
  apiVersion?: string;
  kind?: string;
  metadata?: {
    name?: string;
    namespace?: string;
    creationTimestamp?: string;
    [k: string]: unknown;
  };
  spec?: {
    title?: string;
    [k: string]: unknown;
  };
  status?: {
    phase?: string;
    title?: string;
    resultRef?: string;
    journeyRef?: string;
    ready?: boolean | string;
    [k: string]: unknown;
  };
};

export type ItemsResponse<T> = { items: T[] };
```

The comment above this file in the actual source is refreshingly blunt about why every field is optional: "The objects are passed through verbatim from Kubernetes (raw JSON), so every field is optional and string-typed." That sentence is the TypeScript equivalent of the `ignoreUnknownKeys = true` discipline the Kotlin contracts have practiced since the very first episode of the original series. Different language, identical instinct: do not promise more structure than the underlying data actually guarantees.

The `[k: string]: unknown` index signature scattered through `metadata`, `status`, and `spec` deserves a specific callout too -- it means a field Detective Operating System's controller writes that the dashboard's author never anticipated does NOT cause a TypeScript compile error or a runtime crash. It just sits there, typed as `unknown`, available if someone later wants to read it, ignored if nobody does.

---

## Two Small, Honest Helper Functions

```typescript
export function ageFromTimestamp(ts?: string): string {
  if (!ts) return '';
  const t = Date.parse(ts);
  if (Number.isNaN(t)) return '';
  const secs = Math.max(0, Math.floor((Date.now() - t) / 1000));
  if (secs < 60) return `${secs}s`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days}d`;
}

export function readyLabel(ready: unknown): string {
  if (ready === true || ready === 'True' || ready === 'true') return 'True';
  if (ready === false || ready === 'False' || ready === 'false') return 'False';
  return ready == null || ready === '' ? '\u2014' : String(ready);
}
```

`ageFromTimestamp` is the same `kubectl get`-style "Age" column from the very first CRD episode of the original series, reimplemented for the browser instead of the terminal. `readyLabel` is even more interesting: it accepts `unknown` and handles THREE different ways "true" might arrive -- a real boolean, the string `"True"` (the Kubernetes convention for condition statuses), or the string `"true"` (the JavaScript convention). Rather than demanding the backend normalize this once and for all, the frontend just accepts that data from a Kubernetes-adjacent world arrives a little messy, and copes accordingly.

---

## JourneysPage: The Table That Tolerates Reality

```typescript
// backstage/plugins/oep-dashboards/src/JourneysPage.tsx (conceptual shape,
// matching the actual component's structure and the types above)

export const JourneysPage = () => {
  const { data, loading, error } = useJourneys(); // fetches ItemsResponse<JourneyResource>

  if (loading) return <Progress />;
  if (error) return <ResponseErrorPanel error={error} />;

  return (
    <Table
      title="Journeys"
      options={{ paging: true, search: true }}
      data={data?.items ?? []}
      columns={[
        {
          title: 'Name',
          field: 'metadata.name',
          render: (row: JourneyResource) => row.metadata?.name ?? '\u2014',
        },
        {
          title: 'Stage',
          field: 'status.stage',
          render: (row: JourneyResource) => (
            <StageChip stage={row.status?.stage ?? 'Unknown'} />
          ),
        },
        {
          title: 'Age',
          render: (row: JourneyResource) =>
            ageFromTimestamp(row.metadata?.creationTimestamp),
        },
        {
          title: 'Linked Resources',
          render: (row: JourneyResource) =>
            (row.status?.linkedResources ?? [])
              .map(r => `${r.kind ?? '?'}/${r.name ?? '?'}`)
              .join(', ') || '\u2014',
        },
      ]}
      onRowClick={(_, row) => row && openDetailDrawer(row)}
    />
  );
};
```

Every single render function in that table has a fallback: `?? '\u2014'`, `?? 'Unknown'`, `|| '\u2014'`. None of them assume the data is complete. A Journey that's two seconds old, still in `Pending`, with no `linkedResources` populated yet, renders a perfectly reasonable row instead of a blank space or a crashed table -- which matters enormously the very first time someone clicks "Create" in the Scaffolder template from Episode 14 and immediately checks the dashboard to see if anything happened yet.

---

## OutcomesPage: The Payoff, Rendered Plainly

```typescript
// backstage/plugins/oep-dashboards/src/OutcomesPage.tsx (conceptual shape)

export const OutcomesPage = () => {
  const { data, loading, error } = useOutcomes();

  if (loading) return <Progress />;
  if (error) return <ResponseErrorPanel error={error} />;

  return (
    <Table
      title="Outcomes"
      data={data?.items ?? []}
      columns={[
        {
          title: 'Title',
          render: (row: OutcomeResource) =>
            row.status?.title ?? row.spec?.title ?? '\u2014',
        },
        {
          title: 'Phase',
          render: (row: OutcomeResource) => (
            <PhaseChip phase={row.status?.phase ?? 'Draft'} />
          ),
        },
        {
          title: 'Ready',
          render: (row: OutcomeResource) => readyLabel(row.status?.ready),
        },
        {
          title: 'Result',
          render: (row: OutcomeResource) =>
            row.status?.resultRef ? (
              <Link to={`/oep/results/${row.status.resultRef}`}>
                View Case File
              </Link>
            ) : (
              '\u2014'
            ),
        },
      ]}
    />
  );
};
```

Notice the Title column checks `row.status?.title` BEFORE falling back to `row.spec?.title`. That ordering matters: the `OutcomeSpec` contract from Episode 9 stores the title as the user's original intent, while a controller-populated `status.title` (if and when one exists) would represent what actually got confirmed at runtime. Preferring status over spec, with spec as a sane fallback, is the dashboard quietly encoding "trust the observed outcome over the requested one" without anyone needing a meeting about it.

---

## The Wire Format That Keeps Everyone Honest

This is the moment to reconnect Episode 12's CLI to this episode's dashboard, because they are reading from the SAME conceptual contract, even though one is Go and one is TypeScript:

```
CLI (Episode 12), oep status investigation demo --output json:
{
  "journey": "demo",
  "status": "Completed",
  "results": [
    { "ruleId": "god-object-heuristic", "severity": "high" }
  ],
  "outcomes": [
    { "title": "Improve Maintainability" }
  ]
}

Dashboard (this episode), reading the SAME underlying Journey/Outcome
CRs directly from the Kubernetes API, independently:
  status.stage      -> rendered as the Stage chip
  status.title       -> rendered as the Outcomes table's Title column
  status.linkedResources -> rendered as the Linked Resources column

Neither one imports the other. Both independently agree on what a
Journey's stage means, because BOTH are reading the same CRD-validated
JSON, the same way two separate detectives reading the same case file
independently reach the same conclusion -- not because they coordinated,
but because the evidence itself is unambiguous.
```

---

## The Conversation, Resumed

OWNER OF AGILITY GAME: "If my Onboarding Journeys show up in the SAME JourneysPage table as your Investigation Journeys, won't that get confusing?"

OWNER OF DETECTIVE OPERATING SYSTEM: "Only as confusing as a kubectl get journeys -A would be with both kinds mixed together -- which is to say, not very, because the Kind column and the kindRef field tell you immediately which is which. You could even file a quick PR adding a Kind filter dropdown to the table if you wanted your Onboarding Journeys to have their own dedicated view. The component doesn't gatekeep based on kindRef. It just renders whatever's there."

OWNER OF AGILITY GAME: "And if I wanted my own OutcomesPage with a different layout entirely?"

OWNER OF DETECTIVE OPERATING SYSTEM: "Fork the plugin, change the columns, ship it as your own Backstage plugin pointed at the same backend router. The router doesn't care who's rendering its JSON. That's the whole lesson of this series, said one more time with React components instead of Kotlin classes."

---

## What's Next: Two Owners, One Ontology, Zero New Excuses

Every piece from this second wave -- the ontology contracts, the Journey state machine, the Investigation Composition, the Go CLI, the honest gap in Flux's wiring, the Backstage Catalog and Scaffolder, and now the dashboards -- has been introduced on its own. In Episode 16, the finale of this wave, we run one complete user journey from a Backstage click all the way to an Outcome appearing on a dashboard, and restate the moral of the whole story now that it has twice as many moving parts as it started with.

---

**Resources**
- OEP source repository: the MVP 2 codebase this episode is built from
- Backstage Plugin development: backstage.io/docs/plugins/create-a-plugin
- TypeScript optional properties: typescriptlang.org/docs/handbook/2/objects.html#optional-properties

---

*Agility Game and Detective Operating System with Open Engineering Platform -- two platforms, zero shared dependencies, one ontology underneath them both.*
