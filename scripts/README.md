# Scripts

This directory contains local tooling for the prompt framework.

## Included Scripts

### `prompt-cli.py`

Generate self-contained prompt bundles from a chosen series YAML file.

Each generated episode file contains:

1. structured prompt metadata
2. a ready-to-copy section called:

    ## ChatGPT Image Prompt

You can copy that prompt directly into ChatGPT to generate the image for the episode.

---

### `prompt-lint.py`

Validate the prompt framework structure and check for common issues.

This checks:

- required directories exist
- required files exist
- series index structure is valid
- series YAML files are valid
- episode numbers are unique within each series
- episode slugs are unique within each series

---

### `prompt-docs.py`

Generate documentation from all series YAML files.

This produces:

    docs/EPISODE_INDEX.md
    docs/SERIES_INDEX.md

---

## Setup

Install dependencies from the repository root:

    make install

Or manually:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

---

## List Available Series

List all series defined in `series/SERIES_INDEX.yaml`:

    python scripts/prompt-cli.py list-series

Example output:

    Available series:
    - python_story_series: Like Stories? Love Python! (series/python_story_series.yaml)
    - container_harbour_series: Welcome to container harbour! (series/container_harbour_series.yaml)

---

## Generate Prompt Bundles

### Generate all episodes for one series

Example:

    python scripts/prompt-cli.py generate series/python_story_series.yaml

Or:

    python scripts/prompt-cli.py generate series/container_harbour_series.yaml

This generates files such as:

    generated/python_story_series/episode-01-singleton-pattern.md
    generated/python_story_series/episode-02-factory-pattern.md
    generated/container_harbour_series/episode-01-what-is-kubernetes-really.md

---

### Generate a single episode

Example:

    python scripts/prompt-cli.py generate series/container_harbour_series.yaml 1

This generates:

    generated/container_harbour_series/episode-01-what-is-kubernetes-really.md

---

## Copy-Paste Workflow for ChatGPT

Each generated episode file is self-contained.

Example file:

    generated/container_harbour_series/episode-01-what-is-kubernetes-really.md

Inside that file you will find a section like this:

    ## ChatGPT Image Prompt

    Create a cinematic landscape banner illustration for the series
    "Welcome to container harbour!" ...

To generate the image:

1. Open the generated episode file
2. Scroll to `## ChatGPT Image Prompt`
3. Copy the text inside that section
4. Paste it directly into ChatGPT
5. Ask ChatGPT to generate the image

Example prompt to ChatGPT:

    Generate this image.

No additional files or context should be needed.

---

## Regenerate All Prompt Bundles

From the repository root:

    make generate-all

Or manually:

    python scripts/prompt-cli.py generate series/python_story_series.yaml
    python scripts/prompt-cli.py generate series/container_harbour_series.yaml

---

## Verifying the CLI

To verify that the CLI works:

    python -m py_compile scripts/prompt-cli.py
    python scripts/prompt-cli.py list-series

Both commands should run without errors.

---

## Suggested Commands

    make install
    make lint
    make docs
    make list-series
    make show-series-files
    make generate-all
    make generate-series SERIES=series/python_story_series.yaml
    make generate-series SERIES=series/container_harbour_series.yaml
    make generate-episode SERIES=series/container_harbour_series.yaml EP=4
    make validate

If you are not using the `Makefile`, the equivalent direct commands are:

    pip install -r requirements.txt
    python scripts/prompt-lint.py
    python scripts/prompt-docs.py
    python scripts/prompt-cli.py list-series
    python scripts/prompt-cli.py generate series/python_story_series.yaml
    python scripts/prompt-cli.py generate series/container_harbour_series.yaml
    python scripts/prompt-cli.py generate series/container_harbour_series.yaml 4

---

## Typical Workflow

1. Add or update episodes in a file in `series/`
2. Run the linter
3. Regenerate docs
4. Generate prompt bundles
5. Open the generated episode file
6. Copy the `## ChatGPT Image Prompt` section
7. Paste it into ChatGPT to generate the image

Example:

    make lint
    make docs
    make generate-all

---

## Repository Structure

    scripts/
        README.md
        prompt-cli.py
        prompt-lint.py
        prompt-docs.py

    series/
        SERIES_INDEX.yaml
        python_story_series.yaml
        container_harbour_series.yaml

    generated/
        python_story_series/
            episode-01-singleton-pattern.md
        container_harbour_series/
            episode-01-what-is-kubernetes-really.md

---

## Design Philosophy

The system follows this flow:

    series YAML (source of truth)
            ↓
    scripts/prompt-cli.py
            ↓
    generated Markdown prompt bundles
            ↓
    ChatGPT image generation

This keeps the workflow:

- version controlled
- reproducible
- series-driven
- copy-paste friendly
- simple to maintain