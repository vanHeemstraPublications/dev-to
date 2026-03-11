# Getting Started

This repository contains a small **content factory** for producing article series for **dev.to**.

The system generates two things automatically:

1. **Article prompts** for Claude / ChatGPT that generate the markdown article.
2. **Image prompts** for ChatGPT that generate the banner image.

Each episode becomes a **self-contained production unit**.

Workflow overview:

```
series YAML
      ↓
prompt-cli.py
      ↓
generated/<series>/episode-XX.md
      ↓
copy article prompt → Claude
copy image prompt → ChatGPT
      ↓
article + banner image
      ↓
commit to articles/
      ↓
publish-to-dev.yml → dev.to
```

---

# Step 1 — Create a New Series Definition

All series start as a YAML file in:

```
series/
```

Create a new file for your series:

```
series/copilot_snoopy_series.yaml
```

Example series: **Copilot explained through Snoopy as your digital assistant.**

```
series:
  id: copilot_snoopy_series
  name: "Coding with Copilot & Snoopy"
  type: dev_to_series
  orientation: landscape
  resolution: 1792x1024
  aspect_ratio: "16:9"
  whitespace_margin_percent: 15

defaults:
  setting: "cartoon-inspired workspace where Snoopy acts as your helpful coding assistant"
  lighting: "warm playful cartoon lighting"

  composition:
    left_third: "Snoopy acting as a cheerful digital assistant"
    center: "developer working with Copilot suggestions"
    right_third: "visual metaphor of Copilot helping generate code"
    background: "cartoon coding environment inspired by the Peanuts comic style"

episodes:

  - number: 1
    title: "What is GitHub Copilot?"
    slug: what-is-github-copilot
    metaphor: "Snoopy helping you write code like a playful assistant sitting on your desk"
    center_action: "Snoopy suggests code while the developer types"

    supporting_props:
      - laptop with code editor
      - Snoopy sitting on keyboard
      - floating code suggestions
      - coffee mug

  - number: 2
    title: "Writing Your First Code with Copilot"
    slug: writing-first-code-with-copilot
    metaphor: "Snoopy whispering helpful suggestions while you code"
    center_action: "Copilot suggestions appearing as Snoopy ideas"

    supporting_props:
      - code suggestions bubbles
      - Snoopy notebook
      - laptop screen
      - playful sticky notes

  - number: 3
    title: "Let Copilot Refactor Your Code"
    slug: copilot-refactor-code
    metaphor: "Snoopy reorganizing messy code like tidying a desk"
    center_action: "Snoopy cleaning up tangled code into neat blocks"

    supporting_props:
      - messy code turning into clean code
      - Snoopy holding a pencil
      - code diagrams
      - developer smiling

  - number: 4
    title: "Using Copilot Like a Pro"
    slug: using-copilot-like-a-pro
    metaphor: "Snoopy as your experienced coding sidekick"
    center_action: "Snoopy and developer solving problems together"

    supporting_props:
      - code editor with advanced suggestions
      - Snoopy high-five
      - developer workstation
      - playful code icons
```

---

# Step 2 — Register the Series

Open:

```
series/SERIES_INDEX.yaml
```

Add your new series:

```
series:

  - id: python_story_series
    name: "Like Stories? Love Python!"
    file: series/python_story_series.yaml

  - id: container_harbour_series
    name: "Welcome to container harbour!"
    file: series/container_harbour_series.yaml

  - id: copilot_snoopy_series
    name: "Coding with Copilot & Snoopy"
    file: series/copilot_snoopy_series.yaml
```

---

# Step 3 — Generate Episode Prompt Bundles

From the repository root run:

```
make generate-all
```

or manually:

```
python scripts/prompt-cli.py generate series/copilot_snoopy_series.yaml
```

This will generate files in:

```
generated/copilot_snoopy_series/
```

Example:

```
generated/copilot_snoopy_series/episode-01-what-is-github-copilot.md
generated/copilot_snoopy_series/episode-02-writing-first-code-with-copilot.md
generated/copilot_snoopy_series/episode-03-copilot-refactor-code.md
generated/copilot_snoopy_series/episode-04-using-copilot-like-a-pro.md
```

Each file contains **two prompts**:

```
ChatGPT Image Prompt
Claude / ChatGPT Article Prompt
```

---

# Step 4 — Generate the Article

Open the episode file.

Example:

```
generated/copilot_snoopy_series/episode-01-what-is-github-copilot.md
```

Scroll to:

```
Claude / ChatGPT Article Prompt
```

Copy the prompt and paste it into **Claude**.

Claude will generate the **full dev.to article in markdown with frontmatter**.

Save the result in:

```
articles/
```

Example:

```
articles/copilot-snoopy-episode-01.md
```

---

# Step 5 — Generate the Banner Image

In the same episode file, scroll to:

```
ChatGPT Image Prompt
```

Copy the prompt and paste it into **ChatGPT**.

This generates the banner image for the article.

Save the image in:

```
images/
```

Example:

```
images/copilot-snoopy-episode-01.png
```

---

# Step 6 — Commit the Article

Commit the new files:

```
articles/copilot-snoopy-episode-01.md
images/copilot-snoopy-episode-01.png
```

Push to the repository.

The workflow:

```
publish-to-dev.yml
```

will automatically publish the article to **dev.to**.

---

# Example Final Article Layout

Your article will appear on dev.to with:

- banner image
- title
- humorous story-style explanation
- Copilot examples
- Snoopy metaphor

Example title:

```
Coding with Copilot & Snoopy 🐶
Episode 1: What is GitHub Copilot?
```

---

# Summary

To create a new series:

1. Create a YAML file in `series/`
2. Register it in `SERIES_INDEX.yaml`
3. Run `make generate-all`
4. Use the generated prompts to create
   - the article
   - the banner image
5. Commit the files
6. The automation publishes to dev.to

You now have a **repeatable production pipeline for technical article series**.