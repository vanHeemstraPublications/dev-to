#!/usr/bin/env python3

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)

SERIES_INDEX_FILE = Path("series/SERIES_INDEX.yaml")


def load_yaml(path):
    path = Path(path)

    if not path.exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as exc:
        print(f"Error reading YAML from {path}: {exc}")
        sys.exit(1)


def list_series():
    if not SERIES_INDEX_FILE.exists():
        print("Error: series/SERIES_INDEX.yaml not found")
        sys.exit(1)

    data = load_yaml(SERIES_INDEX_FILE)
    series_entries = data.get("series", [])

    print("Available series:")

    for item in series_entries:
        sid = item.get("id")
        name = item.get("name")
        file = item.get("file")
        print(f"- {sid}: {name} ({file})")


def get_episode(data, episode_number):
    episodes = data.get("episodes", [])

    for episode in episodes:
        if str(episode.get("number")) == str(episode_number):
            return episode

    return None


def build_image_prompt(data, episode):
    series = data.get("series", {})
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})

    series_id = series.get("id", "")
    series_name = series.get("name", "")
    orientation = series.get("orientation", "landscape")
    resolution = series.get("resolution", "1792x1024")
    aspect_ratio = series.get("aspect_ratio", "16:9")
    whitespace = series.get("whitespace_margin_percent", 15)

    setting = defaults.get("setting", "")
    lighting = defaults.get("lighting", "")

    left_third = composition.get("left_third", "")
    center = composition.get("center", "")
    right_third = composition.get("right_third", "")
    background = composition.get("background", "")

    title = episode.get("title", "")
    metaphor = episode.get("metaphor", "")
    center_action = episode.get("center_action", "")
    props = episode.get("supporting_props", [])
    props_text = ", ".join(props)

    prompt = f"""
Create a polished cinematic {orientation} banner illustration for a web article.

Series title:
"{series_name}"

Episode subtitle:
"Episode {episode['number']}: {title}"

Canvas requirements:
- {aspect_ratio} aspect ratio
- {resolution} resolution
- landscape banner layout
- about {whitespace}% whitespace around artwork

Scene setting:
{setting}

Lighting:
{lighting}

Visual metaphor:
{metaphor}

Center action:
{center_action}

Composition guidance:
Left third: {left_third}
Center: {center}
Right third: {right_third}
Background: {background}

Supporting props:
{props_text}

Typography safety:
- text must remain fully visible inside a safe central area
- keep titles away from edges
- ensure the full title is readable

Style:
cinematic digital illustration, storybook realism, highly detailed, polished banner composition
"""

    return prompt.strip()


def build_article_prompt(data, episode):
    series = data.get("series", {})
    series_name = series.get("name")
    metaphor = episode.get("metaphor")
    title = episode.get("title")

    prompt = f"""
I have created a repository that contains markdown articles published to dev.to.

The articles live in:
https://github.com/vanHeemstraSystems/dev-to/articles/

Please inspect the formatting style used in those articles, especially the frontmatter.

Now create the following article.

Series:
{series_name}

Episode:
Episode {episode['number']}: {title}

Writing style requirements:
- light-hearted tone
- humorous delivery similar to Eddie Murphy's storytelling style
- beginner-friendly
- explain complex concepts in simple terms

Concept explanation metaphor:
{metaphor}

Article requirements:
- produce a complete dev.to-ready markdown article
- include frontmatter similar to the examples in the repository
- include headings and subheadings
- include humorous storytelling
- include practical code examples
- include explanations of the code
- ensure the article is engaging and readable

Structure suggestion:
1. humorous opening hook
2. introduce the metaphor
3. explain the concept step-by-step
4. include code examples
5. recap the key idea
6. end with a teaser for the next episode

Output:
Return the complete article in markdown including frontmatter.
"""

    return prompt.strip()


def generate_prompt_bundle(data, episode):
    series = data.get("series", {})
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})

    props_lines = ""
    for p in episode.get("supporting_props", []):
        props_lines += f"- {p}\n"

    image_prompt = build_image_prompt(data, episode)
    article_prompt = build_article_prompt(data, episode)

    text = f"""
# Prompt Bundle

Series ID: {series.get('id')}
Series Name: {series.get('name')}
Series Type: {series.get('type')}

Episode: {episode['number']} - {episode['title']}
Slug: {episode.get('slug')}

Canvas
orientation: {series.get('orientation')}
resolution: {series.get('resolution')}
aspect ratio: {series.get('aspect_ratio')}
whitespace margin: {series.get('whitespace_margin_percent')}%

Defaults
setting: {defaults.get('setting')}
lighting: {defaults.get('lighting')}

Composition
left third: {composition.get('left_third')}
center: {composition.get('center')}
right third: {composition.get('right_third')}
background: {composition.get('background')}

Episode Metaphor
{episode.get('metaphor')}

Center Action
{episode.get('center_action')}

Supporting Props
{props_lines}

--------------------------------------------------

ChatGPT Image Prompt

{image_prompt}

--------------------------------------------------

Claude / ChatGPT Article Prompt

{article_prompt}
""".strip()

    return text


def generate_all(series_file):
    data = load_yaml(series_file)

    series = data.get("series", {})
    series_id = series.get("id", "unknown_series")
    episodes = data.get("episodes", [])

    out_dir = Path("generated") / series_id
    out_dir.mkdir(parents=True, exist_ok=True)

    for ep in episodes:
        filename = out_dir / f"episode-{ep['number']:02d}-{ep['slug']}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(generate_prompt_bundle(data, ep))

        print(f"Generated {filename}")


def generate_single(series_file, episode_number):
    data = load_yaml(series_file)

    series = data.get("series", {})
    series_id = series.get("id", "unknown_series")

    episode = get_episode(data, episode_number)

    if not episode:
        print(f"Episode {episode_number} not found.")
        sys.exit(1)

    out_dir = Path("generated") / series_id
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = out_dir / f"episode-{episode['number']:02d}-{episode['slug']}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(generate_prompt_bundle(data, episode))

    print(f"Generated {filename}")


def print_usage():
    print("")
    print("Usage:")
    print("  python scripts/prompt-cli.py list-series")
    print("  python scripts/prompt-cli.py generate <series_file>")
    print("  python scripts/prompt-cli.py generate <series_file> <episode_number>")
    print("")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "list-series":
        list_series()
        return

    if command == "generate":
        if len(sys.argv) < 3:
            print("Missing series file.")
            return

        series_file = sys.argv[2]

        if len(sys.argv) == 3:
            generate_all(series_file)
        else:
            generate_single(series_file, sys.argv[3])

        return

    print("Unknown command.")
    print_usage()


if __name__ == "__main__":
    main()