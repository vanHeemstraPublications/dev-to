# Getting Started

This repository contains an automated system for producing article series for

[DEV.to](http://DEV.to).

It generates and organizes:

- article prompts
- banner image prompts
- article stubs
- [DEV.to](http://DEV.to)-ready cover images
- optional series cover images

Each episode becomes a consistent production unit.

---

Pipeline Overview

Series definition

```
    ↓
```

[prompt-cli.py](http://prompt-cli.py)

```
    ↓
```

prompt bundles and/or generated assets

```
    ↓
```

articles/ + images/

```
    ↓
```

commit and push

```
    ↓
```

publish-to-dev workflow

```
    ↓
```

[DEV.to](http://DEV.to)

---

Use the Makefile First

The easiest way to use this project is through the `Makefile`.

You can still call `python scripts/prompt-cli.py ...` directly, but the

Makefile gives you shorter and more memorable commands.

Examples:

```
make generate SERIES=azure_data_platform

make generate-image SERIES=azure_data_platform EP=1

make generate-article SERIES=azure_data_platform EP=1

make generate-assets SERIES=azure_data_platform EP=1

make generate-series-cover SERIES=azure_data_platform
```

To see all available commands:

```
make help
```

---

Important: [DEV.to](http://DEV.to) Cover Images Need a Public URL

[DEV.to](http://DEV.to) frontmatter expects:

```
cover_image: https://...
```

It does not resolve repository-local paths such as:

```
/images/azure-data-platform/episode-01.webp
```

For that reason, this repository uses two concepts:

1. Local image storage in the repository
  images//episode-01.webp
2. Public image URL for [DEV.to](http://DEV.to) frontmatter
  [https://raw.githubusercontent.com/](https://raw.githubusercontent.com/<owner>/<repo>/<branch>/images/<series_id>/episode-01.webp)[/](https://raw.githubusercontent.com/<owner>/<repo>/<branch>/images/<series_id>/episode-01.webp)[/](https://raw.githubusercontent.com/<owner>/<repo>/<branch>/images/<series_id>/episode-01.webp)[/images/](https://raw.githubusercontent.com/<owner>/<repo>/<branch>/images/<series_id>/episode-01.webp)[/episode-01.webp](https://raw.githubusercontent.com/<owner>/<repo>/<branch>/images/<series_id>/episode-01.webp)

The CLI can derive the public image base URL automatically from the GitHub

repository URL and branch.

---

Recommended Repository Layout

Use this structure:

```
articles/

  <series_id>/

    episode-01-<slug>.md

images/

  <series_id>/

    episode-01.webp

    series-cover.webp

generated/

  <series_id>/

    episode-01-<slug>.md

config/

  <series>.json

series/

  <series>.yaml

scripts/

  [prompt-cli.py](http://prompt-cli.py)

Makefile
```

Notes:

- `images/` is the single local source of truth for generated images.
- `articles/` contains article files.
- `generated/` contains prompt bundles.
- [DEV.to](http://DEV.to) uses the public absolute image URL, not the local path.

---

Installation

Preferred:

```
make install
```

Without Make:

```
python3 -m venv .venv

.venv/bin/pip install --upgrade pip

.venv/bin/pip install -r requirements.txt
```

Set your OpenAI API key:

The CLI reads the environment variable `**OPENAI_API_KEY**`.

- Get an API key from the OpenAI dashboard: `[https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)`
- Store it safely in a password manager (recommended) and **do not commit it**
to the repo.

Set it for your current terminal session:

```
export OPENAI_API_KEY="your_api_key_here"
```

Persist it (macOS zsh) by adding the same line to `~/.zshrc`, then restart your
terminal.

---

Creating a New Series

You do NOT need to manually create configuration files.

Preferred:

```
make generate SERIES=azure_data_platform
```

Without Make:

```
python scripts/[prompt-cli.py](http://prompt-cli.py) generate series/azure_data_platform.yaml
```

If the file does not exist, the CLI starts a setup wizard and creates:

- a config JSON file
- a series YAML file
- a SERIES_INDEX entry

The wizard also asks for:

- GitHub repository URL
- public image branch

These are used to derive the [DEV.to](http://DEV.to)-compatible public image base URL.

---

Example Setup

Run:

```
make generate SERIES=azure_data_platform
```

Or:

```
python scripts/[prompt-cli.py](http://prompt-cli.py) generate series/azure_data_platform.yaml
```

Example answers:

Series id:

```
azure-data-platform
```

Series name:

```
Azure Data Platform F1 Series
```

Series type:

```
dev_to_series
```

Number of episodes:

```
4
```

Base metaphor:

```
Formula 1 factory and race team
```

Default setting:

```
Formula 1
```

Default lighting:

```
bright cinematic atmosphere
```

Article code language:

```
Python
```

Humor style:

```
light-hearted, playful, and witty
```

Article tone:

```
light-hearted, humorous, beginner-friendly
```

Series GitHub repository URL:

```
[https://github.com/software-journey/azure-data-platform](https://github.com/software-journey/azure-data-platform)
```

Public image branch:

```
main
```

---

Files Created Automatically

The CLI creates:

```
config/azure-data-platform.json

series/azure_data_platform.yaml
```

It also updates:

```
series/SERIES_INDEX.yaml
```

---

How `title` and `display_title` Work

Each episode has both:

- `title`
- `display_title`

Example:

```
- number: 1

  title: Episode 1

  display_title: Welcome to the Factory
```

Purpose:

- `title` is a stable internal identifier
- `display_title` is the human-friendly episode title used in banners and
  article frontmatter

Automation behavior:

- during bootstrap, `display_title` is automatically initialized
- it is NOT left as a placeholder
- by default it starts as the same value as `title`
- you can later change it per episode

This avoids placeholder text accidentally appearing in generated prompts.

---

Generating Prompt Bundles

Preferred:

```
make generate SERIES=azure_data_platform
```

Generate one episode bundle:

```
make generate-episode SERIES=azure_data_platform EP=1
```

Without Make:

```
python scripts/[prompt-cli.py](http://prompt-cli.py) generate series/azure_data_platform.yaml

python scripts/[prompt-cli.py](http://prompt-cli.py) generate series/azure_data_platform.yaml 1
```

This produces files such as:

```
generated/azure-data-platform/[episode-01-episode-1.md](http://episode-01-episode-1.md)
```

Each bundle contains:

- image prompt
- article prompt
- local image path
- public cover image URL

---

Generating an Episode Banner Image

Preferred:

```
make generate-image SERIES=azure_data_platform EP=1
```

Generate all episode images:

```
make generate-images SERIES=azure_data_platform
```

Without Make:

```
python scripts/[prompt-cli.py](http://prompt-cli.py) generate-image series/azure_data_platform.yaml 1

python scripts/[prompt-cli.py](http://prompt-cli.py) generate-images series/azure_data_platform.yaml
```

Output location:

```
images/<series_id>/episode-01.webp
```

The CLI also saves the exact prompt beside it:

```
images/<series_id>/episode-01.prompt.txt
```

Image behavior:

- generates a source image via OpenAI
- crops to target aspect ratio
- resizes to 1000 x 420
- exports as WebP
- compresses to stay under configured size limit

---

Generating a Series Cover

Preferred:

```
make generate-series-cover SERIES=azure_data_platform
```

Without Make:

```
python scripts/[prompt-cli.py](http://prompt-cli.py) generate-series-cover series/azure_data_platform.yaml
```

Output location:

```
images/<series_id>/series-cover.webp
```

The series cover is useful for:

- repository README banner
- series landing page
- social preview artwork
- general branding for the full series

It is optional and separate from episode cover images.

---

Generating Article Stubs

Preferred:

```
make generate-article SERIES=azure_data_platform EP=1
```

Generate all article stubs:

```
make generate-articles SERIES=azure_data_platform
```

Without Make:

```
python scripts/[prompt-cli.py](http://prompt-cli.py) generate-article series/azure_data_platform.yaml 1

python scripts/[prompt-cli.py](http://prompt-cli.py) generate-articles series/azure_data_platform.yaml
```

Output location:

```
articles/<series_id>/episode-01-<slug>.md
```

The generated frontmatter already includes a [DEV.to](http://DEV.to)-compatible

`cover_image` field using a public absolute URL.

---

Generating Both Assets for One Episode

The easiest episode workflow is:

```
make generate-assets SERIES=azure_data_platform EP=1
```

This generates:

- the episode banner image
- the article stub

That gives you the main publishable assets for one episode in a single step.

---

Example Frontmatter

A generated article stub will look like:

```
---

title: "Episode 1: Welcome to the Factory"

published: false

description: "Add article description here."

tags: ["add", "tags", "here"]

series: "Azure Data Platform F1 Series"

cover_image: "[https://raw.githubusercontent.com/software-journey/azure-data-platform/main/images/azure-data-platform/episode-01.webp](https://raw.githubusercontent.com/software-journey/azure-data-platform/main/images/azure-data-platform/episode-01.webp)"

---
```

This is intentional.

Do not replace `cover_image` with a local path like:

```
/images/azure-data-platform/episode-01.webp
```

[DEV.to](http://DEV.to) expects a public URL.

---

Typical Workflow

1. Create or update the series file
  make generate SERIES=azure_data_platform
2. Edit the series YAML and refine episode metadata
  Especially:
  - display_title
  - metaphor
  - center_action
  - supporting_props
3. Generate both assets for one episode
  make generate-assets SERIES=azure_data_platform EP=1
4. Optionally generate a reusable series cover
  make generate-series-cover SERIES=azure_data_platform
5. Replace the article body with the full article you want to publish
6. Commit:
  articles//...
    images//...
7. Push to GitHub
8. Let the publishing workflow publish to [DEV.to](http://DEV.to)

---

Common Commands

Install dependencies:

```
make install
```

List series:

```
make list-series
```

Show series files:

```
make show-series-files
```

Generate prompt bundles:

```
make generate SERIES=azure_data_platform
```

Generate one episode bundle:

```
make generate-episode SERIES=azure_data_platform EP=1
```

Generate one episode image:

```
make generate-image SERIES=azure_data_platform EP=1
```

Generate all images:

```
make generate-images SERIES=azure_data_platform
```

Generate one article stub:

```
make generate-article SERIES=azure_data_platform EP=1
```

Generate all article stubs:

```
make generate-articles SERIES=azure_data_platform
```

Generate one episode image plus article stub:

```
make generate-assets SERIES=azure_data_platform EP=1
```

Generate a series cover:

```
make generate-series-cover SERIES=azure_data_platform
```

Show help:

```
make help
```

---

Summary

To create and publish a new episode with the easiest workflow:

1. Run
  make generate SERIES=azure_data_platform
2. Refine the episode metadata in the series YAML
3. Generate the publishable assets
  make generate-assets SERIES=azure_data_platform EP=1
4. Optionally generate the series cover
  make generate-series-cover SERIES=azure_data_platform
5. Write or paste the final article body
6. Commit and push

The automation keeps:

- images in one local location
- article files in one location
- public [DEV.to](http://DEV.to) cover URLs consistent
- prompt bundles reproducible

