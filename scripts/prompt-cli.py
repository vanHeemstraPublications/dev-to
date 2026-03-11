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

    if not series_entries:
        print("No series defined.")
        return

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


def build_title_safety_block(series_name, episode_number, title):
    return f"""
DEV.to title safety requirements:
- This image will be used as a DEV.to article header/banner, so all text must remain fully readable inside a conservative safe area.
- Do not place any important text near the extreme top edge, bottom edge, left edge, or right edge.
- Reserve a strong safe margin: keep all title typography at least 12% away from the left and right edges, at least 14% away from the top edge, and at least 12% away from the bottom edge.
- Place the main title block in the upper-middle portion of the artwork, not flush against the top border.
- Keep the subtitle clearly below the main title with generous spacing.
- Use slightly smaller typography rather than oversized typography if needed for readability.
- Do not let any letter, ornament, frame, or banner overlap the image boundary.
- Avoid decorative flourishes that extend beyond the safe text area.
- The full title and subtitle must be completely visible in the final banner image.

Exact text to include:
Top title:
"{series_name}"

Subtitle:
"Episode {episode_number}: {title}"
""".strip()


def build_prompt(data, episode):
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

    title_safety = build_title_safety_block(series_name, episode["number"], title)

    common = f"""
Create a polished cinematic {orientation} banner illustration for a web article.

Series title:
"{series_name}"

Episode subtitle:
"Episode {episode['number']}: {title}"

Canvas requirements:
- {aspect_ratio} aspect ratio
- {resolution} target resolution
- landscape banner composition
- about {whitespace}% whitespace around the artwork
- clean readable layout suitable for a header image
- avoid clutter and keep the composition visually clear

Scene setting:
{setting}

Lighting and atmosphere:
{lighting}

Visual metaphor:
{metaphor}

Center action:
{center_action}

Composition guidance:
- left third: {left_third}
- center: {center}
- right third: {right_third}
- background: {background}

Supporting props to include:
{props_text}

Style requirements:
- cinematic digital illustration
- highly detailed
- storybook realism
- polished composition
- visually striking but not overcrowded
- designed specifically as a web article banner

{text_wrap(title_safety)}
""".strip()

    if series_id == "python_story_series":
        series_specific = """
Additional series guidance:
- the tone should feel playful, witty, educational, and slightly humorous
- lean into a Hollywood storytelling atmosphere
- make the design pattern metaphor visually obvious at a glance
- emphasize film-set energy, production design, and narrative clarity
- the result should feel like a smart, light-hearted banner for a Python learning series
""".strip()
    elif series_id == "container_harbour_series":
        series_specific = """
Additional series guidance:
- the tone should feel adventurous, educational, cinematic, and lightly humorous
- lean into a grand early-20th-century harbour aesthetic
- make the Kubernetes metaphor visually obvious at a glance
- emphasize ships, docks, cranes, logistics, and maritime coordination
- the result should feel like a smart, memorable banner for a Kubernetes explainer series
""".strip()
    else:
        series_specific = """
Additional series guidance:
- keep the concept immediately understandable
- make the central metaphor easy to grasp visually
- ensure the image works well as a banner header
""".strip()

    negative = """
Avoid:
- visual clutter
- unreadable text
- cramped composition
- generic stock-art look
- flat lighting
- messy perspective
- low-detail background
- accidental portrait orientation
- oversized title text that touches or nearly touches the top edge
- title banners placed too high for DEV.to header usage
- cropped-looking typography
""".strip()

    return f"{common}\n\n{series_specific}\n\n{negative}"


def text_wrap(text):
    return text


def generate_prompt_bundle(data, episode):
    series = data.get("series", {})
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})

    props_lines = ""
    for prop in episode.get("supporting_props", []):
        props_lines += f"- {prop}\n"

    chatgpt_prompt = build_prompt(data, episode)

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

Prompt Assets
deterministic config: {series.get('deterministic_config')}
prompt template: {series.get('prompt_template')}

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

Suggested Subtitle
Episode {episode['number']}: {episode['title']}

--------------------------------------------------

ChatGPT Image Prompt

{chatgpt_prompt}
""".strip()

    return text


def generate_all(series_file):
    data = load_yaml(series_file)

    series = data.get("series", {})
    series_id = series.get("id", "unknown_series")
    episodes = data.get("episodes", [])

    if not episodes:
        print("No episodes defined.")
        sys.exit(1)

    out_dir = Path("generated") / series_id
    out_dir.mkdir(parents=True, exist_ok=True)

    for episode in episodes:
        filename = out_dir / f"episode-{episode['number']:02d}-{episode['slug']}.md"
        content = generate_prompt_bundle(data, episode)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

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
    content = generate_prompt_bundle(data, episode)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated {filename}")


def print_usage():
    print("")
    print("Usage:")
    print("  python scripts/prompt-cli.py list-series")
    print("  python scripts/prompt-cli.py generate <series_file>")
    print("  python scripts/prompt-cli.py generate <series_file> <episode_number>")
    print("")
    print("Examples:")
    print("  python scripts/prompt-cli.py list-series")
    print("  python scripts/prompt-cli.py generate series/python_story_series.yaml")
    print("  python scripts/prompt-cli.py generate series/container_harbour_series.yaml")
    print("  python scripts/prompt-cli.py generate series/container_harbour_series.yaml 4")
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
            print_usage()
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