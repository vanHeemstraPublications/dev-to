---
title: "What has changed, LikeC4? 🧰 Ep.10"
series: "What has changed, LikeC4?"
part: 10
organization: "the-software-s-journey"
tags: [likec4, cli, export, validate, format]
---

## Episode 10: The Rest of the Toolbox

`likec4 start` and `likec4 build` cover ninety percent of my week. This episode is the other ten percent — the commands I reach for when someone needs a plain image, a different diagramming format, or when I need the CLI to catch my own mistakes before a reviewer does.

Need a plain image for a slide deck? Export straight to PNG or JPEG:

```bash
likec4 export png -o ./assets
likec4 export jpg -o ./assets --quality 90
```

This spins up a local server and uses Playwright to take actual screenshots of the rendered views — worth knowing if I'm running this in CI, since Playwright needs its browser binaries installed first.

Need the model itself, structured, for some other tool to consume? Export to JSON:

```bash
likec4 export json -o dump.json
```

Need to hand a diagram to someone still living in draw.io? There's a dedicated export, one `.drawio` file per view:

```bash
likec4 export drawio
likec4 export drawio -o ./diagrams
likec4 export drawio --profile leanix -o ./diagrams
```

And for teams standardized on other diagramming ecosystems entirely, code generation covers Mermaid, Graphviz's Dot, D2, and PlantUML:

```bash
likec4 gen mmd
likec4 gen dot
likec4 gen d2
likec4 gen plantuml
```

Between the DrawIO export and this codegen list, I've genuinely never hit a "sorry, our team doesn't use a format LikeC4 can talk to" wall — the model stays the single source of truth, and whatever format a particular audience is used to is just another projection of it.

Now, the two commands that matter most for keeping this whole system honest, which is really what this series is about. First, validation:

```bash
likec4 validate
```

This checks for syntax errors, obviously, but also for something I didn't expect the first time I hit it: layout drift — an outdated manual layout, where I've hand-adjusted a diagram's positioning at some point and the underlying model has since changed enough that the saved layout no longer honestly reflects it. Find either kind of problem, and the command exits with a non-zero return code — which is exactly the behavior I want wired into CI, a topic the next episode is entirely about.

Second, formatting:

```bash
# Format all files in current workspace
likec4 format

# Check mode (CI-friendly, exits with code 1 if any file needs formatting)
likec4 format --check
```

`--check` never rewrites anything — it just tells me, with an exit code a pipeline can act on, whether someone's `.c4` files need a pass through the formatter before merging. Between `validate` and `format --check`, I have exactly the two gates I'd want for any other source file in this repository: is it syntactically and structurally sound, and is it formatted the way the rest of the team formats theirs. Nothing about architecture documentation exempts it from the same discipline I'd apply to application code — which, as far as I'm concerned, is rather the entire point of calling it "architecture as code" in the first place.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `likec4 export png/jpg/json/drawio` | The finished model and its views | Render to the requested external format | Slide-ready images, structured JSON, or DrawIO files | Stakeholders and tools outside the LikeC4 ecosystem |
| `likec4 gen mmd/dot/d2/plantuml` | The finished model | Generate equivalent source in another diagramming language | Interoperable diagram sources for other toolchains | Teams standardized on Mermaid, Dot, D2, or PlantUML |
| `likec4 validate` / `likec4 format --check` | The current `.c4` source tree | Check for syntax errors, layout drift, and formatting issues | A non-zero exit code on any problem | CI pipelines, and the next episode's entire premise |

Next stop: wiring `validate` and `build` into GitHub Actions, so the question "what has changed?" gets answered automatically on every pull request.
