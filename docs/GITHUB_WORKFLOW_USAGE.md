# GitHub Workflow Usage

Workflows included:

generate-prompt-bundle.yml  
validate-prompt-system.yml

These automate prompt generation and validation.

## Additional Workflow: check-generated-docs.yml

This workflow ensures generated documentation is up to date.

It regenerates:

- `docs/EPISODE_INDEX.md`
- `docs/SERIES_INDEX.md`

Then it checks whether Git detects changes.

If changes are found, the workflow fails and contributors must regenerate and commit the updated docs.

Example local fix:

```bash
python scripts/prompt-docs.py
git add docs/EPISODE_INDEX.md docs/SERIES_INDEX.md
git commit -m "docs: refresh generated series indexes"
```

---

## Recommended local commands

```bash
pip install -r requirements.txt
python scripts/prompt-lint.py
python scripts/prompt-docs.py
python scripts/prompt-cli.py list-series
python scripts/prompt-cli.py generate series/python_story_series.yaml
python scripts/prompt-cli.py generate series/container_harbour_series.yaml
```

## Updated Bundle Generation Behavior

The `generate-prompt-bundle.yml` workflow supports two modes.

### Manual mode

Use **Run workflow** and optionally provide:

- `series_file`
- `episode_number`

Examples:

- `series/python_story_series.yaml`
- `series/container_harbour_series.yaml`
- `series/container_harbour_series.yaml` with episode `4`

### Automatic mode on push

When relevant files change, the workflow scans `series/*.yaml` and generates prompt bundles for every series file except `SERIES_INDEX.yaml`.

Generated files are uploaded as a GitHub Actions artifact named:

`prompt-bundles`

## Additional Workflow: commit-generated-bundles.yml

This workflow generates prompt bundles and commits them back into the repository automatically.

### Behavior

- on push to `main`, it generates all series bundles
- on manual run, it can generate:
  - one full series
  - one specific episode from one series

### Commit target

Generated files are committed into:

`generated/`

### Commit message

`chore(generated): refresh prompt bundles`

### Important

If you want generated prompt bundles versioned in Git, do not ignore `generated/` in `.gitignore`.