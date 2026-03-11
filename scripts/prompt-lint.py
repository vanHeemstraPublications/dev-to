#!/usr/bin/env python3

"""
Prompt Linter

Checks the repository for common prompt framework issues.

Usage:

    python scripts/prompt-lint.py

What it validates:
- required directories exist
- required core files exist
- SERIES_EPISODES.yaml is valid
- episode numbers are unique
- episode slugs are unique
"""

from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install pyyaml")
    sys.exit(1)


REQUIRED_DIRS = [
    Path("prompts"),
    Path("config"),
    Path("series"),
    Path("scripts"),
    Path("docs"),
]

REQUIRED_FILES = [
    Path("series/SERIES_EPISODES.yaml"),
    Path("config/IMAGE_GENERATION_CONFIG.yaml"),
    Path("prompts/PROMPT_TEMPLATE.md"),
    Path("prompts/python_story_episode_template.md"),
    Path("prompts/kubernetes_episode_template.md"),
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def main() -> None:
    for directory in REQUIRED_DIRS:
        if not directory.exists() or not directory.is_dir():
            fail(f"Missing required directory: {directory}")

    for file_path in REQUIRED_FILES:
        if not file_path.exists() or not file_path.is_file():
            fail(f"Missing required file: {file_path}")

    series_file = Path("series/SERIES_EPISODES.yaml")
    try:
        data = yaml.safe_load(series_file.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Could not parse YAML in {series_file}: {exc}")

    if not isinstance(data, dict):
        fail("SERIES_EPISODES.yaml must contain a top-level mapping")

    if "series" not in data:
        fail("SERIES_EPISODES.yaml is missing top-level key: 'series'")

    if "episodes" not in data:
        fail("SERIES_EPISODES.yaml is missing top-level key: 'episodes'")

    episodes = data["episodes"]
    if not isinstance(episodes, list) or not episodes:
        fail("'episodes' must be a non-empty list")

    seen_numbers = set()
    seen_slugs = set()

    for idx, episode in enumerate(episodes, start=1):
        if not isinstance(episode, dict):
            fail(f"Episode #{idx} is not a mapping")

        for key in ["number", "title", "slug"]:
            if key not in episode:
                fail(f"Episode #{idx} is missing required key: {key}")

        number = episode["number"]
        slug = episode["slug"]

        if number in seen_numbers:
            fail(f"Duplicate episode number found: {number}")
        if slug in seen_slugs:
            fail(f"Duplicate episode slug found: {slug}")

        seen_numbers.add(number)
        seen_slugs.add(slug)

    print("Prompt lint passed.")
    print(f"Validated {len(episodes)} episode(s).")


if __name__ == "__main__":
    main()