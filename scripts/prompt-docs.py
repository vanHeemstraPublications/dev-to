#!/usr/bin/env python3

"""
Prompt Docs Generator

Builds markdown indexes from all series YAML files in /series.

Usage:

    python scripts/prompt-docs.py

Outputs:

    docs/EPISODE_INDEX.md
    docs/SERIES_INDEX.md
"""

from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)


SERIES_DIR = Path("series")
EPISODE_INDEX_OUTPUT = Path("docs/EPISODE_INDEX.md")
SERIES_INDEX_OUTPUT = Path("docs/SERIES_INDEX.md")


def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error reading YAML from {path}: {exc}")
        sys.exit(1)


def get_series_files():
    files = sorted(
        p for p in SERIES_DIR.glob("*.yaml")
        if p.name != "SERIES_INDEX.yaml"
    )

    if not files:
        print("No series definition files found in /series")
        sys.exit(1)

    return files


def build_episode_index(series_files):
    lines = [
        "# Episode Index",
        "",
        "This file is generated from the YAML files in `series/`.",
        "",
    ]

    for path in series_files:
        data = load_yaml(path)
        series = data.get("series", {})
        episodes = data.get("episodes", [])

        series_name = series.get("name", path.stem)
        series_id = series.get("id", "unknown_series")

        lines.extend([
            f"## {series_name}",
            "",
            f"- series id: `{series_id}`",
            f"- source file: `{path.as_posix()}`",
            "",
        ])

        for ep in episodes:
            number = ep.get("number", "?")
            title = ep.get("title", "Untitled")
            slug = ep.get("slug", "")
            metaphor = ep.get("metaphor", "")
            center_action = ep.get("center_action", "")

            lines.extend([
                f"### Episode {number}: {title}",
                "",
                f"- slug: `{slug}`",
                f"- metaphor: {metaphor}",
                f"- center action: {center_action}",
                "",
            ])

    EPISODE_INDEX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    EPISODE_INDEX_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_series_index(series_files):
    lines = [
        "# Series Index",
        "",
        "This file is generated from the YAML files in `series/`.",
        "",
        "## Available Series",
        "",
    ]

    for path in series_files:
        data = load_yaml(path)
        series = data.get("series", {})
        episodes = data.get("episodes", [])
        defaults = data.get("defaults", {})

        series_id = series.get("id", "unknown_series")
        series_name = series.get("name", path.stem)
        series_type = series.get("type", "")
        prompt_template = series.get("prompt_template", "")
        deterministic_config = series.get("deterministic_config", "")
        setting = defaults.get("setting", "")
        lighting = defaults.get("lighting", "")

        lines.extend([
            f"### {series_name}",
            "",
            f"- id: `{series_id}`",
            f"- type: {series_type}",
            f"- source file: `{path.as_posix()}`",
            f"- prompt template: `{prompt_template}`",
            f"- deterministic config: `{deterministic_config}`",
            f"- setting: {setting}",
            f"- lighting: {lighting}",
            f"- episodes: {len(episodes)}",
            "",
        ])

    SERIES_INDEX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SERIES_INDEX_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    series_files = get_series_files()
    build_episode_index(series_files)
    build_series_index(series_files)

    print(f"Generated {EPISODE_INDEX_OUTPUT}")
    print(f"Generated {SERIES_INDEX_OUTPUT}")


if __name__ == "__main__":
    main()