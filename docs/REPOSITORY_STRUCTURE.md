# Recommended Directory Structure

```text
/prompts
    kubernetes_container_harbour_super_prompt.md
    kubernetes_episode_template.md
    python_story_episode_template.md
    PROMPT_TEMPLATE.md

/config
    IMAGE_GENERATION_CONFIG.yaml

/series
    SERIES_INDEX.yaml
    python_story_series.yaml
    container_harbour_series.yaml

/scripts
    README.md
    prompt-cli.py
    prompt-lint.py
    prompt-docs.py

/docs
    PROMPT_FRAMEWORK_README.md
    README_USAGE.md
    PROMPT_VERSIONING.md
    EPISODE_GENERATOR.md
    PROMPT_LINTER.md
    SERIES_STYLE_GUIDE.md
    IMAGE_REGRESSION_TESTING.md
    GITHUB_WORKFLOW_USAGE.md
    REPOSITORY_STRUCTURE.md
    EPISODE_INDEX.md
    SERIES_INDEX.md

/.github/workflows
    generate-prompt-bundle.yml
    validate-prompt-system.yml
    check-generated-docs.yml

/requirements.txt
/Makefile
```

---

## Handy commands

```bash
make install
make lint
make docs
make list-series
make generate-python
make generate-kubernetes
make validate
```