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