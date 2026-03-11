# Scripts

This directory contains local tooling for the prompt framework.

## Included Scripts

### `prompt-cli.py`

Generate prompt bundles locally from `series/SERIES_EPISODES.yaml`.

Examples:

Generate all episodes:

```bash
python scripts/prompt-cli.py generate
```

Generate one episode:

```bash
python scripts/prompt-cli.py generate 4
```

## prompt-docs.py

Generate documentation from series/SERIES_EPISODES.yaml.

Example:

```bash
python scripts/prompt-docs.py
```

Output:

docs/EPISODE_INDEX.md

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Or directly:

```bash
pip install pyyaml
```

## Suggested Commands

```bash
pip install -r requirements.txt
python scripts/prompt-lint.py
python scripts/prompt-docs.py
python scripts/prompt-cli.py generate
python scripts/prompt-cli.py generate 4
```

## Typical Local Workflow

1. Update series/SERIES_EPISODES.yaml
2. Run the linter
3. Regenerate docs
4. Generate one or more prompt bundles

Example:

```bash
python scripts/prompt-lint.py
python scripts/prompt-docs.py
python scripts/prompt-cli.py generate
```