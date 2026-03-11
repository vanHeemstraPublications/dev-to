# Scripts

This directory contains local tooling for the prompt framework.

## Included Scripts

### `prompt-cli.py`

Generate prompt bundles locally from a chosen series file.

Examples:

List all known series from `series/SERIES_INDEX.yaml`:

```bash
python scripts/prompt-cli.py list-series
```

Generate all episodes for the Python series:

```bash
python scripts/prompt-cli.py generate series/python_story_series.yaml
```

Generate all episodes for the Kubernetes series:

```bash
python scripts/prompt-cli.py generate series/container_harbour_series.yaml
```

Generate one episode from a series:

```bash
python scripts/prompt-cli.py generate series/container_harbour_series.yaml 4
```

Output examples:

generated/python_story_series/episode-04-adapter-pattern.md  
generated/container_harbour_series/episode-04-services-harbour-traffic-control.md

## prompt-lint.py

Validate the prompt framework structure and check for common issues.

Example:

```bash
python scripts/prompt-lint.py
```

This checks:

- required directories exist
- required files exist
- series YAML files are valid
- episode numbers are unique
- episode slugs are unique

## prompt-docs.py

Generate documentation from series YAML files.

Example:

```bash
python scripts/prompt-docs.py
```

Output:

docs/EPISODE_INDEX.md  
docs/SERIES_INDEX.md

# Setup

## Install dependencies:

```bash
pip install -r requirements.txt
```

## Suggested Commands

```bash
pip install -r requirements.txt
python scripts/prompt-cli.py list-series
python scripts/prompt-lint.py
python scripts/prompt-docs.py
python scripts/prompt-cli.py generate series/python_story_series.yaml
python scripts/prompt-cli.py generate series/container_harbour_series.yaml
python scripts/prompt-cli.py generate series/container_harbour_series.yaml 4
```

## Typical Local Workflow

1. Update one or more files in /series
2. Run the linter
3. Regenerate docs
4. Generate one or more prompt bundles

Example:

```bash
python scripts/prompt-lint.py
python scripts/prompt-docs.py
python scripts/prompt-cli.py generate series/python_story_series.yaml
python scripts/prompt-cli.py generate series/container_harbour_series.yaml
```

## Makefile Shortcuts

If your repository includes the root `Makefile`, you can use:

```bash
make install
make lint
make docs
make validate
make list-series
make show-series-files
make generate-all
make generate-series SERIES=series/python_story_series.yaml
make generate-series SERIES=series/container_harbour_series.yaml
make generate-episode SERIES=series/container_harbour_series.yaml EP=4
make clean
```

