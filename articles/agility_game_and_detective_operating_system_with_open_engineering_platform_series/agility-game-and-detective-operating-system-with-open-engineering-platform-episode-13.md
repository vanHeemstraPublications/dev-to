---
title: "Agility Game and Detective Operating System with Open Engineering Platform! Ep.13: GitOps Is Not a Vibe, It's a Function Call"
published: false
description: "Episode 13: Plenty of platforms say 'Git is the source of truth' and mean 'we have a README that mentions Git.' This episode looks honestly at what Flux CD's role actually is in MVP 2 -- what the install script genuinely automates, what the --mode gitops flag genuinely verifies, and what's still an empty folder waiting for its GitRepository and Kustomization manifests."
tags: [gitops, fluxcd, kubernetes, devops]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/agility-detective-oep-episode-13.png"
series: "Agility Game and Detective Operating System with Open Engineering Platform"
canonical_url: ""
organization: "the-software-s-journey"
part: 2
---

# Agility Game and Detective Operating System with Open Engineering Platform! 🕵️🎮
## Episode 13: GitOps Is Not a Vibe, It's a Function Call

---

## The Honesty Episode

Every series eventually reaches the episode where someone has to admit a folder is emptier than the marketing slide suggested. The original series did this gracefully back in its fifth episode, pointing out that `controllers/detective-operating-system/` was just a `.gitkeep` file while the real controller lived one directory up. MVP 2 has earned its own version of that moment, and it deserves the same treatment: clear-eyed, not embarrassed, genuinely useful to know before you go looking for something that isn't there yet.

The headline claim across `INTENT_MVP_2.md` and the README is "Flux CD becomes the automation engine." That's the destination. This episode is about exactly how much of the road there is actually paved in this snapshot of the repository.

---

## SIPOC -- The GitOps Layer, As It Stands

| Suppliers | Inputs | Process | Outputs | Customers |
|---|---|---|---|---|
| deploy/flux/install.sh | A running MiniKube cluster, the Flux CLI (auto-installed via Homebrew on macOS arm64 if missing) | Install the Flux controllers, then apply GitRepository + Kustomization manifests from a flux/ bundle directory | A flux-system namespace with source-controller and kustomize-controller running | The cluster -- now CAPABLE of being driven by Flux, pending the actual source/kustomization manifests |
| oep run investigation --mode gitops | A Journey manifest path | Verify the file is committed AND pushed (does not apply anything itself) | A confirmation that Git, not the CLI, is now the next actor in the chain | Flux's own reconciliation loop -- whenever it's pointed at this repository |
| The flux/ directory in this snapshot | -- | Currently holds only a stray .DS_Store file | No GitRepository or Kustomization YAML present YET in this particular zip | This episode, which is telling you so before you go searching for it |

---

## What the Install Script Actually Does

```bash
# deploy/flux/install.sh (abbreviated, real content)

FLUX_NAMESPACE="${FLUX_NAMESPACE:-flux-system}"
FLUX_BUNDLE_DIR="${REPO_ROOT}/flux"
FLUX_COMPONENTS="${FLUX_BUNDLE_DIR}/install/gotk-components.yaml"
FLUX_SOURCES_DIR="${FLUX_BUNDLE_DIR}/sources"
FLUX_KUSTOMIZATIONS_DIR="${FLUX_BUNDLE_DIR}/kustomizations"

ensure_flux_cli() {
  if command -v flux >/dev/null 2>&1; then
    log "flux CLI present: $(flux --version 2>/dev/null || echo unknown)"
    return 0
  fi
  log "flux CLI not found on PATH"
  if [[ "$(uname -s)" == "Darwin" && "$(uname -m)" == "arm64" ]] && command -v brew >/dev/null 2>&1; then
    log "attempting auto-install via Homebrew: brew install fluxcd/tap/flux"
    brew install fluxcd/tap/flux || warn "brew install fluxcd/tap/flux failed"
  else
    warn "auto-install skipped (requires macOS arm64 with Homebrew on PATH)"
  fi
}

require_cmd kubectl
ensure_flux_cli

if ! kubectl cluster-info >/dev/null 2>&1; then
  die "no reachable cluster (check your kubeconfig / minikube status)"
fi

# ... installs flux-system components, then applies FLUX_SOURCES_DIR
# and FLUX_KUSTOMIZATIONS_DIR if they exist
```

This script is real, idempotent, and genuinely thoughtful -- it checks for an existing Flux install before reinstalling, it attempts to auto-install the Flux CLI on macOS via Homebrew (matching the "Mac Mini M4 Pro" development target from `INTENT_MVP_2.md`), and it fails loudly with a clear message if there's no reachable cluster. It is exactly the kind of bootstrap script you'd want sitting at the start of a GitOps pipeline.

What it is NOT, in this particular snapshot, is a script that has anything concrete to point at yet:

```
$ find flux -type f
flux/.DS_Store

That's the entire contents of the flux/ directory right now.
No gotk-components.yaml. No sources/. No kustomizations/.
```

---

## Why This Is Not a Scandal

It would be easy to read the empty `flux/` directory as a broken promise. It is not, and here is the more useful way to read it: `INTENT_MVP_2.md` is explicitly labeled `Status: Planned`. This is a roadmap document describing where the platform is GOING, with the CLI, the contracts, the Crossplane Composition, and the Backstage integration already built as the first wave of that journey -- pun very much intended. The Flux bootstrap script existing at all, fully idempotent and ready to apply manifests the moment they exist, is the scaffolding for the NEXT wave, not evidence that this wave shipped incomplete.

```
WHAT'S FULLY BUILT IN THIS SNAPSHOT:
  - The ontology contracts (Episode 9)
  - The Journey contract + CRD + cross-validation test (Episode 10)
  - The Investigation Crossplane Composition (Episode 11)
  - The OEP CLI, all four commands, including --mode gitops's
    commit-and-push verification logic (Episode 12)
  - The Flux install script's CONTROLLER bootstrap logic

WHAT'S SCAFFOLDED BUT NOT YET POPULATED IN THIS SNAPSHOT:
  - flux/sources/ (the GitRepository manifest pointing Flux at
    this repo)
  - flux/kustomizations/ (the Kustomization manifest telling Flux
    WHICH paths in this repo to reconcile, and how often)
```

The honest one-sentence summary: Flux's ENGINE is ready to be installed. Flux's MAP -- which repository, which paths, which interval -- has not been drawn yet in this zip.

---

## What --mode gitops Actually Verifies Today

Given that gap, it's worth being precise about what `oep run investigation --mode gitops` genuinely does right now, because it's more modest -- and more honest -- than "triggers Flux":

```go
// cli/oep/cmd/run_gitops.go (conceptual shape, matching the CLI's own
// stated behaviour: "gitops mode verifies the manifest is committed +
// pushed and lets Flux reconcile")

func runInvestigationGitOps(cmd *cobra.Command, name, manifestPath, repoRoot string, journey schema.Journey) error {
    // 1. Check the manifest file exists on disk at the expected path
    // 2. Check git status: is this file tracked and committed?
    // 3. Check the local branch is not ahead of (or has been pushed to) the remote
    // 4. Report success/failure -- WITHOUT calling Flux, WITHOUT applying
    //    anything to the cluster directly
    //
    // The actual reconciliation is left entirely to Flux's own polling
    // loop, whenever Flux is installed AND pointed at this repository.
}
```

```
THE DIVISION OF LABOUR, STATED PLAINLY

  oep run investigation --mode gitops:
    "Is this YAML committed? Is it pushed? Good. My job here is done."

  Flux (once its GitRepository + Kustomization exist):
    "I noticed a new commit on the tracked branch. Let me apply
     whatever changed under the paths I'm configured to watch."

  Neither one is impersonating the other. The CLI does not secretly
  call kubectl apply behind your back in gitops mode. Flux does not
  need the CLI to have run at all -- a Journey YAML committed and
  pushed by ANY means (a hand-written commit, a Backstage PR merge
  from Episode 14) is equally valid input to Flux's reconciliation
  loop.
```

---

## Architecture Diagram: The Honest Version

```
+-----------------------------------------------------------------------+
|  TODAY, in this snapshot:                                             |
|                                                                       |
|  User --> oep create investigation --> Git commit + push              |
|                    |                                                  |
|                    v                                                  |
|  oep run investigation --mode gitops --> verifies commit+push status  |
|                    |                       (does NOT apply anything)   |
|                    v                                                  |
|  oep run investigation --mode server --> applies directly via         |
|                                           client-go (the "escape       |
|                                           hatch" -- works TODAY,        |
|                                           with no Flux involved at all)|
+-----------------------------------------------------------------------+

+-----------------------------------------------------------------------+
|  THE NEXT WAVE, once flux/sources/ and flux/kustomizations/ exist:    |
|                                                                       |
|  User --> oep create investigation --> Git commit + push              |
|                    |                                                  |
|                    v                                                  |
|  Flux's source-controller notices the new commit on the GitRepository |
|                    |                                                  |
|                    v                                                  |
|  Flux's kustomize-controller applies the Kustomization's paths        |
|                    |                                                  |
|                    v                                                  |
|  Kubernetes API server now holds the new Journey, automatically,      |
|  with NOBODY having run --mode server OR --mode gitops's verification |
|  step at all -- Flux noticed the commit on its own polling schedule   |
+-----------------------------------------------------------------------+
```

---

## The Conversation, Resumed

OWNER OF AGILITY GAME: "So if I commit my own Journey YAML to the repo right now, does anything actually happen automatically?"

OWNER OF DETECTIVE OPERATING SYSTEM: "Not yet, in this exact snapshot -- because there's no GitRepository or Kustomization telling Flux to watch this repo at all. Today, SOMEONE still has to run `oep run investigation --mode server` to apply it directly, or wait for the next wave to fill in `flux/sources/` and `flux/kustomizations/`."

OWNER OF AGILITY GAME: "That's... a refreshingly honest answer for a platform document."

OWNER OF DETECTIVE OPERATING SYSTEM: "The alternative was pretending the empty folder was secretly populated and hoping nobody opened it. We tried that strategy with the `controllers/detective-operating-system/` folder in the FIRST series. It went fine specifically because we said so out loud instead of letting you discover it during an incident."

---

## What's Next: Backstage Learns to Read Minds (and Clusters)

GitOps needs someone, or something, to actually produce the commits Flux will eventually watch. In Episode 14, we meet the part of MVP 2 that's considerably more finished than the Flux bundle: Backstage, with a real Catalog provider that reads live cluster resources, and a real Scaffolder template that opens an actual GitHub pull request.

---

**Resources**
- OEP source repository: the MVP 2 codebase this episode is built from
- Flux CD: fluxcd.io
- Flux GitRepository and Kustomization CRDs: fluxcd.io/flux/components/source and fluxcd.io/flux/components/kustomize

---

*Agility Game and Detective Operating System with Open Engineering Platform -- two platforms, zero shared dependencies, one ontology underneath them both.*
