#!/usr/bin/env python3

"""
Prompt Linter

Checks the repository for common prompt framework issues.

Usage:

    python scripts/prompt-lint.py

What it validates:
- required directories exist
- required core files exist
- SERIES_INDEX.yaml is valid (if present)
- all series YAML files are valid
- each series file contains required keys
- episode numbers are unique within each series
- episode slugs are unique within each series
- files referenced by SERIES_INDEX.yaml exist
"""

from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)


REQUIRED_DIRS = [
    Path("prompts"),
    Path("config"),
    Path("series"),
    Path("scripts"),
    Path("docs"),
]

REQUIRED_FILES = [
    Path("config/IMAGE_GENERATION_CONFIG.yaml"),
    Path("prompts/PROMPT_TEMPLATE.md"),
    Path("prompts/python_story_episode_template.md"),
    Path("prompts/kubernetes_episode_template.md"),
]

SERIES_DIR = Path("series")
SERIES_INDEX_FILE = SERIES_DIR / "SERIES_INDEX.yaml"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Could not parse YAML in {path}: {exc}")


def validate_series_file(path: Path) -> int:
    data = load_yaml(path)

    if not isinstance(data, dict):
        fail(f"{path} must contain a top-level mapping")

    if "series" not in data:
        fail(f"{path} is missing top-level key: 'series'")

    if "episodes" not in data:
        fail(f"{path} is missing top-level key: 'episodes'")

    series = data["series"]
    episodes = data["episodes"]

    if not isinstance(series, dict):
        fail(f"{path}: 'series' must be a mapping")

    for key in ["id", "name", "prompt_template"]:
        if key not in series:
            fail(f"{path}: 'series' is missing required key: {key}")

    if not isinstance(episodes, list) or not episodes:
        fail(f"{path}: 'episodes' must be a non-empty list")

    seen_numbers = set()
    seen_slugs = set()

    for idx, episode in enumerate(episodes, start=1):
        if not isinstance(episode, dict):
            fail(f"{path}: episode #{idx} is not a mapping")

        for key in ["number", "title", "slug"]:
            if key not in episode:
                fail(f"{path}: episode #{idx} is missing required key: {key}")

        number = episode["number"]
        slug = episode["slug"]

        if number in seen_numbers:
            fail(f"{path}: duplicate episode number found: {number}")
        if slug in seen_slugs:
            fail(f"{path}: duplicate episode slug found: {slug}")

        seen_numbers.add(number)
        seen_slugs.add(slug)

    prompt_template = Path(series["prompt_template"])
    if not prompt_template.exists():
        fail(f"{path}: referenced prompt template does not exist: {prompt_template}")

    deterministic_config = series.get("deterministic_config")
    if deterministic_config:
        config_path = Path(deterministic_config)
        if not config_path.exists():
            fail(f"{path}: referenced deterministic config does not exist: {config_path}")

    return len(episodes)


def validate_series_index() -> None:
    if not SERIES_INDEX_FILE.exists():
        return

    data = load_yaml(SERIES_INDEX_FILE)

    if not isinstance(data, dict):
        fail(f"{SERIES_INDEX_FILE} must contain a top-level mapping")

    if "series" not in data:
        fail(f"{SERIES_INDEX_FILE} is missing top-level key: 'series'")

    entries = data["series"]
    if not isinstance(entries, list) or not entries:
        fail(f"{SERIES_INDEX_FILE}: 'series' must be a non-empty list")

    seen_ids = set()
    seen_files = set()

    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            fail(f"{SERIES_INDEX_FILE}: entry #{idx} is not a mapping")

        for key in ["id", "name", "file"]:
            if key not in entry:
                fail(f"{SERIES_INDEX_FILE}: entry #{idx} is missing required key: {key}")

        series_id = entry["id"]
        file_path = Path(entry["file"])

        if series_id in seen_ids:
            fail(f"{SERIES_INDEX_FILE}: duplicate series id found: {series_id}")
        if str(file_path) in seen_files:
            fail(f"{SERIES_INDEX_FILE}: duplicate series file reference found: {file_path}")

        seen_ids.add(series_id)
        seen_files.add(str(file_path))

        if not file_path.exists():
            fail(f"{SERIES_INDEX_FILE}: referenced series file does not exist: {file_path}")


def main() -> None:
    for directory in REQUIRED_DIRS:
        if not directory.exists() or not directory.is_dir():
            fail(f"Missing required directory: {directory}")

    for file_path in REQUIRED_FILES:
        if not file_path.exists() or not file_path.is_file():
            fail(f"Missing required file: {file_path}")

    validate_series_index()

    series_files = sorted(
        p for p in SERIES_DIR.glob("*.yaml")
        if p.name != "SERIES_INDEX.yaml"
    )

    if not series_files:
        fail("No series definition files found in /series")

    total_episodes = 0
    for series_file in series_files:
        count = validate_series_file(series_file)
        total_episodes += count

    print("Prompt lint passed.")
    print(f"Validated {len(series_files)} series file(s).")
    print(f"Validated {total_episodes} episode(s) in total.")


if __name__ == "__main__":
    main()