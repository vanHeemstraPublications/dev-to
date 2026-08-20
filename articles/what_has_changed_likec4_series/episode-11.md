---
title: "What has changed, LikeC4? 🔁 Ep.11"
series: "What has changed, LikeC4?"
part: 11
organization: "the-software-s-journey"
tags: [likec4, ci-cd, github-actions, automation]
---

## Episode 11: Letting the Pipeline Ask the Question For Me

Here's the honest confession behind this whole series: I stopped manually asking "what has changed?" the day I put LikeC4 into CI. Now the pipeline asks it for me, on every single pull request, whether I remember to or not — which, let's be honest, is the only version of this discipline that actually survives contact with a busy sprint.

LikeC4 ships an official GitHub Action wrapping the CLI, and the simplest use builds the static site as a workflow artifact:

```yaml
steps:
  - uses: actions/checkout@v4

  - name: ⚙️ build
    uses: likec4/actions@v1
    with:
      action: build
      path: src/likec4
      output: dist
      base: /baseurl/

  - name: upload artifacts
    uses: actions/upload-artifact@v3
    with:
      name: likec4
      path: dist
```

Every merge to my documentation folder now produces a fresh, deployable site as a build artifact — no one has to remember to run `likec4 build` by hand and re-upload it somewhere. Want images generated automatically too, say for embedding in a Confluence page that can't render an iframe? Same action, different mode:

```yaml
steps:
  - name: export diagrams
    uses: likec4/actions@v1
    with:
      export: png
      path: src/likec4
      output: out/images
      use-dot-bin: 'true'
```

But the build and export steps are really the reward. The actual discipline lives earlier in the pipeline, as a required check before merge is even allowed:

```yaml
steps:
  - uses: actions/checkout@v4

  - name: 🔍 validate architecture model
    run: |
      npx likec4 validate
      npx likec4 format --check
```

Run this on every pull request touching `docs/likec4/**`, and I get exactly the guarantee this whole series has been chasing: a PR that introduces a syntax error, references an undeclared element, drifts a manually-adjusted layout out of sync with the model, or simply forgets to run the formatter, fails the check before a human reviewer ever has to notice it by eye. Architecture documentation gets the same red-X-blocks-merge treatment as a failing unit test, because as far as this pipeline is concerned, that's exactly what it is.

There's a genuinely nice second-order effect here too, one Claudio Taverna's advice about "diagram as code" gets exactly right: because `.c4` files are plain text, a pull request touching them shows a real, line-level diff — not a binary blob that changed, but the *specific* relationship that got added, the *specific* container that got renamed. Reviewing an architecture change becomes reviewing a diff, the same skill every developer on the team already has, rather than a separate, awkward "compare two screenshots side by side" exercise nobody actually does thoroughly. And it's a genuinely good nudge toward Architectural Decision Records, too — once the diagrams are properly kept in sync, most PRs touching them probably deserve an ADR explaining *why*, and most ADRs probably deserve a corresponding diagram change. The two disciplines end up reinforcing each other.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `likec4/actions@v1` | Workflow configuration (`action: build`, `export: png`, etc.) | Wrap the LikeC4 CLI as a reusable GitHub Action step | Build artifacts, exported images, or generated code, produced automatically | Every merge to the documentation folder |
| `likec4 validate` + `likec4 format --check` as a required CI check | Every pull request touching `.c4` files | Fail the check on syntax errors, layout drift, or unformatted files | A merge-blocking gate equivalent to a failing test | Reviewers, who no longer have to eyeball diagrams for correctness |
| Plain-text `.c4` diffs in pull requests | A proposed architecture change | Render as a normal, line-level Git diff | An architecture review that reads like a code review | The whole team, and the ADR discipline it naturally encourages |

Next stop: going one step further than CI — asking my architecture questions in plain language, and getting answers from the model itself.
