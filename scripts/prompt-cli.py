#!/usr/bin/env python3

"""
Prompt CLI

Generate prompt bundles locally from a chosen series YAML file.

Usage examples:

Generate all episodes for the Python series:

    python scripts/prompt-cli.py generate series/python_story_series.yaml

Generate all episodes for the Kubernetes series:

    python scripts/prompt-cli.py generate series/container_harbour_series.yaml

Generate one episode from a series:

    python scripts/prompt-cli.py generate series/container_harbour_series.yaml 4

Optional command to list available series:

    python scripts/prompt-cli.py list-series

Output will be written to:

    generated/<series-id>/

Example:

    generated/python_story_series/episode-04-adapter-pattern.md
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)


SERIES_INDEX_FILE = Path("series/SERIES_INDEX.yaml")


def load_yaml(path: Path):
    if not path.exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error reading YAML from {path}: {exc}")
        sys.exit(1)


def list_series():
    data = load_yaml(SERIES_INDEX_FILE)

    series_entries = data.get("series", [])
    if not series_entries:
        print("No series found in series/SERIES_INDEX.yaml")
        sys.exit(1)

    print("Available series:")
    for item in series_entries:
        print(f"- {item.get('id')}: {item.get('name')} ({item.get('file')})")


def generate_prompt_bundle(data, episode):
    series = data["series"]
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})

    props = "\n".join(f"- {p}" for p in episode.get("supporting_props", []))

    return f"""# Prompt Bundle

Series ID: {series.get('id', '')}
Series Name: {series.get('name', '')}
Series Type: {series.get('type', '')}

Episode: {episode['number']} - {episode['title']}
Slug: {episode.get('slug', '')}

Canvas:
- orientation: {series.get('orientation', '')}
- resolution: {series.get('resolution', '')}
- aspect ratio: {series.get('aspect_ratio', '')}
- whitespace margin: {series.get('whitespace_margin_percent', '')}%

Prompt Assets:
- deterministic config: {series.get('deterministic_config', '')}
- prompt template: {series.get('prompt_template', '')}

Defaults:
- setting: {defaults.get('setting', '')}
- lighting: {defaults.get('lighting', '')}

Composition:
- left third: {composition.get('left_third', '')}
- center: {composition.get('center', '')}
- right third: {composition.get('right_third', '')}
- background: {composition.get('background', '')}

Episode Metaphor:
{episode.get('metaphor', '')}

Center Action:
{episode.get('center_action', '')}

Supporting Props:
{props}

Suggested Subtitle:
Episode {episode['number']}: {episode['title']}
"""


def generate_all(series_path: Path):
    data = load_yaml(series_path)

    series = data.get("series", {})
    series_id = series.get("id", "unknown_series")
    episodes = data.get("episodes", [])

    if not episodes:
        print(f"No episodes found in {series_path}")
        sys.exit(1)

    output_dir = Path("generated") / series_id
    output_dir.mkdir(parents=True, exist_ok=True)

    for episode in episodes:
        filename = output_dir / f"episode-{episode['number']:02d}-{episode['slug']}.md"
        filename.write_text(generate_prompt_bundle(data, episode), encoding="utf-8")
        print(f"Generated {filename}")


def generate_single(series_path: Path, episode_number: str):
    data = load_yaml(series_path)

    series = data.get("series", {})
    series_id = series.get("id", "unknown_series")
    episodes = data.get("episodes", [])

    output_dir = Path("generated") / series_id
    output_dir.mkdir(parents=True, exist_ok=True)

    for episode in episodes:
        if str(episode.get("number")) == str(episode_number):
            filename = output_dir / f"episode-{episode['number']:02d}-{episode['slug']}.md"
            filename.write_text(generate_prompt_bundle(data, episode), encoding="utf-8")
            print(f"Generated {filename}")
            return

    print(f"Episode {episode_number} not found in {series_path}")
    sys.exit(1)


def print_usage():
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


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1]

    if command == "list-series":
        list_series()
        return

    if command != "generate":
        print("Unknown command.")
        print_usage()
        sys.exit(1)

    if len(sys.argv) < 3:
        print("Missing required argument: <series_file>")
        print_usage()
        sys.exit(1)

    series_file = Path(sys.argv[2])

    if len(sys.argv) == 3:
        generate_all(series_file)
    else:
        generate_single(series_file, sys.argv[3])


if __name__ == "__main__":
    main()