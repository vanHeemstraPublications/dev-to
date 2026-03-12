# Scripts

This directory contains the automation tools used to generate article and image prompts for DEV.to series.

The main tool is:

    prompt-cli.py

This script powers the entire production pipeline for article series.

It can:

• list existing series  
• generate prompt bundles for episodes  
• bootstrap a brand new series automatically  

Each generated episode bundle contains:

• a ChatGPT image generation prompt  
• a Claude / ChatGPT article writing prompt  
• metadata about the episode  
• a link to the series GitHub repository  

These bundles live in:

    generated/<series_id>/


--------------------------------------------------

Basic Commands

List all series registered in the repository:

    python scripts/prompt-cli.py list-series


Generate prompt bundles for a series:

    python scripts/prompt-cli.py generate series/<series_file>.yaml


Generate only one episode:

    python scripts/prompt-cli.py generate series/<series_file>.yaml <episode_number>


Example:

    python scripts/prompt-cli.py generate series/container_harbour_series.yaml
    python scripts/prompt-cli.py generate series/python_story_series.yaml 3


--------------------------------------------------

Bootstrap New Series Automatically

If the series YAML file does not exist, the generator will automatically guide you through creating it.

Example:

    python scripts/prompt-cli.py generate series/copilot_snoopy_series.yaml

If the file does not exist, the CLI will ask:

• series id
• series name
• number of episodes
• metaphor
• humor style
• code language
• GitHub repository URL
• visual setting
• lighting style

The CLI will then create:

    config/<series>.json
    series/<series>.yaml

and update:

    series/SERIES_INDEX.yaml

After that, simply review the files and rerun the command.


--------------------------------------------------

Generated Prompt Bundles

After generation, files appear in:

    generated/<series_id>/

Example:

    generated/container_harbour_series/
        episode-01-what-is-kubernetes-really.md


Each bundle contains two sections:

    ChatGPT Image Prompt
    Claude / ChatGPT Article Prompt


--------------------------------------------------

Image Generation

The image prompt is designed specifically for DEV.to cover images.

Default settings:

    resolution: 1000x420
    aspect ratio: 100:42
    format: WebP
    file size target: < 400 KB

Images include safe title margins to prevent cropping in DEV.to headers.


--------------------------------------------------

Article Generation

The article prompt instructs Claude or ChatGPT to:

• produce a complete DEV.to markdown article
• include frontmatter
• include code samples
• use a humorous storytelling style
• explain the concept through the episode metaphor
• include a SIPOC explanation section


--------------------------------------------------

Typical Workflow

1. Create or bootstrap a series

    python scripts/prompt-cli.py generate series/new_series.yaml

2. Generate prompts

    make generate-all
    or
    python scripts/prompt-cli.py generate series/new_series.yaml

3. Open generated episode bundle

    generated/<series>/episode-XX.md

4. Copy:

    Claude / ChatGPT Article Prompt

Paste it into Claude to generate the article.

5. Copy:

    ChatGPT Image Prompt

Paste it into ChatGPT to generate the banner image.

6. Save the outputs

    articles/<article>.md
    images/<image>.webp

7. Commit and push.

The GitHub workflow will automatically publish the article to DEV.to.