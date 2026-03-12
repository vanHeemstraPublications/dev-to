# Getting Started

This repository contains an automated system for producing article series for DEV.to.

It generates both:

• article prompts
• banner image prompts

Each episode becomes a self-contained production bundle.


--------------------------------------------------

Pipeline Overview

Series definition
        ↓
prompt-cli.py
        ↓
Generated prompt bundles
        ↓
Claude writes article
ChatGPT generates banner image
        ↓
articles/ + images/
        ↓
publish-to-dev workflow
        ↓
DEV.to


--------------------------------------------------

Creating a New Series

You do NOT need to manually create configuration files.

Instead, run:

    python scripts/prompt-cli.py generate series/<your_series>.yaml

If the file does not exist, the CLI will automatically start a setup wizard.


--------------------------------------------------

Example: Copilot Series with Snoopy

Run:

    python scripts/prompt-cli.py generate series/copilot_snoopy_series.yaml


The CLI will ask a few questions.

Example answers:

Series id:
    copilot_snoopy_series

Series name:
    Coding with Copilot & Snoopy

Number of episodes:
    4

Base metaphor:
    Snoopy as your digital assistant helping you code

Default setting:
    a playful cartoon workspace where Snoopy helps the developer

Lighting style:
    warm cartoon lighting

Code language:
    Python

Humor style:
    lighthearted Snoopy-style humor

GitHub repository URL:
    https://github.com/software-journey/copilot


--------------------------------------------------

Files Created Automatically

The CLI will generate:

    config/copilot-snoopy-series.json
    series/copilot_snoopy_series.yaml

It will also update:

    series/SERIES_INDEX.yaml


--------------------------------------------------

Generate Episode Prompt Bundles

After reviewing the created files, run again:

    python scripts/prompt-cli.py generate series/copilot_snoopy_series.yaml


This produces:

    generated/copilot_snoopy_series/

Example files:

    episode-01-episode-1.md
    episode-02-episode-2.md
    episode-03-episode-3.md
    episode-04-episode-4.md


--------------------------------------------------

Generating the Article

Open one of the generated episode files.

Example:

    generated/copilot_snoopy_series/episode-01-episode-1.md

Find the section:

    Claude / ChatGPT Article Prompt

Copy the prompt and paste it into Claude.

Claude will generate the complete article in DEV.to markdown format.


Save the result in:

    articles/


Example:

    articles/copilot-snoopy-episode-01.md


--------------------------------------------------

Generating the Banner Image

In the same episode bundle file, find:

    ChatGPT Image Prompt

Copy that prompt and paste it into ChatGPT.

Save the generated image as:

    images/<image>.webp


Recommended DEV.to image settings:

    1000 x 420 px
    WebP format
    under 400 KB


--------------------------------------------------

Publishing the Article

Commit the new files:

    articles/<article>.md
    images/<image>.webp

Push to GitHub.

The workflow:

    .github/workflows/publish-to-dev.yml

will automatically publish the article to DEV.to.


--------------------------------------------------

Summary

To create a new series:

1. Run

    python scripts/prompt-cli.py generate series/<series>.yaml

2. Answer the setup questions.

3. Generate prompts.

4. Use Claude to write the article.

5. Use ChatGPT to generate the image.

6. Commit and push.

The automation handles the rest.