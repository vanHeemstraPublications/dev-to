---
title: "Agility Game and Detective Operating System with Open Engineering Platform! Ep.12: Go Figure -- The OEP CLI"
published: false
description: "Episode 12: After eleven episodes of Kotlin, the platform suddenly switches languages on us. The OEP CLI is written in Go, using Cobra and client-go, and it ships four real commands that mean nobody ever has to hand-write a Journey YAML file from scratch again. This episode meets oep create, oep run, oep status, and oep result, one flag at a time."
tags: [go, cli, kubernetes, devtools]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-12.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

# Agility Game and Detective Operating System with Open Engineering Platform! 🕵️🎮
## Episode 12: Go Figure -- The OEP CLI

---

## A Plot Twist Nobody Saw Coming

Eleven episodes deep into this saga, you'd be forgiven for assuming everything in this platform is secretly Kotlin wearing a different hat. The contracts are Kotlin. The controller is Kotlin. The validation tests are Kotlin. Then you open `cli/oep/go.mod` and discover the user-facing command-line tool -- the thing both platform owners' actual end users will type into a terminal -- is written in Go.

This is not an accident, and it is not a betrayal of the "Kotlin Multiplatform is the default" principle from the original series' architecture doc. It's the SAME loose-coupling philosophy, applied to tooling instead of runtime services: the CLI talks to the Kubernetes API and to Git over well-defined, language-agnostic protocols. It does not need to share a process, a JVM, or a single import statement with the Kotlin controller it's indirectly steering.

---

## SIPOC -- The OEP CLI

| Suppliers | Inputs | Process | Outputs | Customers |
|---|---|---|---|---|
| A human at a terminal | A command, flags, an investigation name | Cobra parses the command tree; client-go talks to the Kubernetes API or a Git repo as needed | A created Journey YAML, an applied resource, a status report, or a fetched Case File | The same human -- now able to do everything Episodes 1 through 11 required kubectl and hand-written YAML for |
| The journeys.oep.io CRD (Episode 10) | A Journey CR's status.stage and status.linkedResources fields | Resolve the chain: Journey -> Mission -> Result -> Outcome | A human-readable table, or machine-readable JSON | Scripts, CI pipelines, and Backstage's own backend (Episode 13 onward) |
| Git, via internal/gitx | A rendered Journey YAML file | Add, commit, and (by default) push the file to the configured remote | A real commit in a real Git history | Flux CD -- whose entire job starts the moment this commit lands on the tracked branch |

---

## Why Go, Specifically

```
THE CASE FOR A SEPARATE CLI LANGUAGE

  Kotlin/JVM CLI:
    + Could share code with the contracts module directly
    - Cold start time noticeably slower for a tool people run
      dozens of times a day
    - Requires a JVM on every machine running the CLI

  Go CLI (what MVP 2 actually shipped):
    + Single static binary, no runtime dependency, fast cold start
    + client-go is the canonical, most battle-tested Kubernetes
      client library in existence -- written BY the Kubernetes
      project, for exactly this kind of tool
    + Cobra is the same command-tree library kubectl itself is
      built on, so the CLI's UX patterns feel instantly familiar
      to anyone who already knows kubectl
    - Cannot directly import the Kotlin contracts module
      (mitigated: the CLI works against the CRD's JSON shape,
       the same shape ANY language can read)
```

That last mitigation point is the entire MVP 1 thesis, recursively applied one layer up: just as Detective Operating System's Kotlin controller and the Python detector never shared code, only an HTTP+JSON contract, the Go CLI and the Kotlin contracts module never share code either -- only the same CRD-validated JSON shape, read independently by two completely different type systems.

---

## The Four Commands

```
oep version
  Prints the CLI's own version. The "hello, am I installed
  correctly" command every CLI needs.

oep create investigation <name>
  Writes a Journey CR to repositories/journeys/<name>.yaml
  and, by default, commits and pushes it.

oep run investigation <name>
  Applies the Journey (and a paired Investigation XR) either
  directly (--mode server) or by verifying it's committed and
  letting Flux pick it up (--mode gitops).

oep status investigation <name>
  Resolves a Journey and walks its Mission/Result/Outcome chain,
  printing a table or, with --output json, the exact JSON shape
  specified in INTENT_MVP_2.md section 9.

oep result <name>
  Fetches the Case File (the Result CR) behind a completed
  Outcome, in one of three formats.
```

---

## oep create investigation, in Practice

```bash
oep create investigation demo \
  --purpose improve-maintainability \
  --kind refactoring \
  --repo-url file:///mnt/sample
```

```go
// cli/oep/cmd/create_investigation.go (abbreviated)

const RepoURLAnnotation = "oep.io/repo-url"

func init() {
    f := createInvestigationCmd.Flags()
    f.StringVar(&createInvPurpose, "purpose", "", "purposeRef for the Journey (required)")
    f.StringVar(&createInvKind, "kind", "", "kindRef for the Journey (required)")
    f.StringVar(&createInvRepoURL, "repo-url", "", "URL of the target repository (required; stored as annotation)")
    f.StringArrayVar(&createInvCapabilities, "capability", []string{"investigations"}, "capabilityRefs (repeatable)")
    f.StringArrayVar(&createInvMissionRefs, "mission-ref", nil, "missionRefs in kind/name form, e.g. Mission/analyze-repository (repeatable)")
    f.BoolVar(&createInvNoPush, "no-push", false, "skip git push after commit")
    f.BoolVar(&createInvNoCommit, "no-commit", false, "write the file but do not git add/commit/push")
    f.BoolVar(&createInvForce, "force", false, "overwrite the target file if it already exists")

    for _, name := range []string{"purpose", "kind", "repo-url"} {
        createInvestigationCmd.MarkFlagRequired(name)
    }
}

func runCreateInvestigation(cmd *cobra.Command, args []string) error {
    name := args[0]
    j := schema.Journey{
        APIVersion: schema.JourneyAPIVersion,
        Kind:       schema.JourneyKind,
        Metadata: schema.ObjectMeta{
            Name:        name,
            Namespace:   schema.DefaultNamespace,
            Annotations: map[string]string{RepoURLAnnotation: createInvRepoURL},
        },
        Spec: schema.JourneySpec{
            PurposeRef:     createInvPurpose,
            KindRef:        createInvKind,
            CapabilityRefs: createInvCapabilities,
            MissionRefs:    missionRefs,
        },
    }
    // ... marshal to YAML, write to repositories/journeys/<name>.yaml,
    // then git add/commit/push unless --no-commit or --no-push
}
```

Notice the `--repo-url` flag gets stashed as a Kubernetes ANNOTATION on the Journey, under the key `oep.io/repo-url`, rather than as a spec field. That's a deliberate choice: it's metadata ABOUT how this Journey was created, not part of what the Journey actually IS. The `JourneySpec` contract from Episode 10 stays exactly as clean as it was -- the CLI just tucks its own bookkeeping into the part of the Kubernetes object that's explicitly meant for exactly this kind of side information.

---

## oep run investigation: Two Modes, One Honest Distinction

```go
// cli/oep/cmd/run_investigation.go (abbreviated)

var runInvestigationCmd = &cobra.Command{
    Use:   "investigation <name>",
    Short: "Apply a Journey (and paired Investigation XR) for an investigation",
    Long: `Apply the Journey CR at repositories/journeys/<name>.yaml and, by default,
a paired Crossplane Investigation XR with the same name so the Mission /
Result / Outcome chain is composed and the Journey's missionRefs resolve.

server mode applies both manifests via client-go (escape hatch).
gitops mode verifies the manifest is committed + pushed and lets Flux reconcile.`,
}
```

```bash
# server mode: apply directly, right now, via client-go
oep run investigation demo --mode server --wait

# gitops mode: confirm the YAML is committed and pushed, then step back
oep run investigation demo --mode gitops
```

The doc comment's own phrase -- "server mode... (escape hatch)" -- is doing a lot of honest work in six words. `--mode server` exists for demos, local development, and the moments when waiting for a Git-to-cluster reconciliation loop is genuinely the wrong tool for the job. `--mode gitops` is the mode MVP 2's whole architecture is actually built around: Git as the source of truth, Flux watching that source, the CLI getting out of the way the instant the commit lands.

---

## oep status investigation --output json: A Contract With a Paper Trail

```go
// cli/oep/cmd/status_investigation.go

// findingJSON is the EXACT shape demanded by INTENT_MVP_2 section 9: only
// ruleId and severity. Any drift here breaks the Wave 7 Backstage contract.
type findingJSON struct {
    RuleID   string `json:"ruleId"`
    Severity string `json:"severity"`
}

type outcomeJSON struct {
    Title string `json:"title"`
}

type statusJSON struct {
    Journey  string        `json:"journey"`
    Status   string        `json:"status"`
    Results  []findingJSON `json:"results"`
    Outcomes []outcomeJSON `json:"outcomes"`
}
```

```bash
oep status investigation demo --output json
```

```json
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
```

That code comment citing "INTENT_MVP_2 section 9" by name is the single most reassuring line in the entire CLI codebase. It means the JSON shape on your screen right now is not a developer's best guess at what the planning document probably meant -- it is a literal, traceable implementation of a numbered requirement, with a comment specifically placed so nobody accidentally "cleans up" the shape in a future refactor without noticing they've broken a documented contract.

---

## oep result: Three Formats for Three Different Afternoons

```bash
# Default: the raw findings array, perfect for piping into jq
oep result demo

# The full Result CR as YAML, for archiving in git or dry-run validating
oep result demo --format result-yaml

# The full Result CR as JSON, preserving status + metadata + findings together
oep result demo --format result-json
```

```
WHICH FORMAT, WHEN

  findings (default):
    "I just want to see what was found."
    oep result demo | jq '.[] | select(.severity == "high")'

  result-yaml:
    "I want to keep a record of this Result, or validate it
     before reapplying it somewhere else."
    oep result demo --format result-yaml | kubectl apply --dry-run=client -f -

  result-json:
    "I want EVERYTHING -- status, metadata, the findings,
     all of it, machine-readable."
    oep result demo --format result-json > archive/demo-result.json
```

---

## What's Next: GitOps Is Not a Vibe, It's a Function Call

The CLI's `--mode gitops` flag implies something is supposed to happen automatically once a commit lands. In Episode 13, we look honestly at what Flux CD's role actually is in this architecture, what's genuinely wired up in this snapshot of the repository, and what the install script promises versus what's actually sitting in the flux/ directory today.

---

**Resources**
- OEP source repository: the MVP 2 codebase this episode is built from
- Cobra: github.com/spf13/cobra
- client-go: github.com/kubernetes/client-go

---

*Agility Game and Detective Operating System with Open Engineering Platform -- two platforms, zero shared dependencies, one ontology underneath them both.*
