#!/usr/bin/env python3

"""
Prompt Docs Generator

Builds a simple markdown index from SERIES_EPISODES.yaml.

Usage:

    python scripts/prompt-docs.py

Output:

    docs/EPISODE_INDEX.md
"""

from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install pyyaml")
    sys.exit(1)


SERIES_FILE = Path("series/SERIES_EPISODES.yaml")
OUTPUT_FILE = Path("docs/EPISODE_INDEX.md")


def main() -> None:
    if not SERIES_FILE.exists():
        print(f"Missing file: {SERIES_FILE}")
        sys.exit(1)

    data = yaml.safe_load(SERIES_FILE.read_text(encoding="utf-8"))

    series = data.get("series", {})
    episodes = data.get("episodes", [])

    title = series.get("name", "Episode Index")

    lines = [
        f"# {title} — Episode Index",
        "",
        "This file is generated from `series/SERIES_EPISODES.yaml`.",
        "",
        "## Episodes",
        "",
    ]

    for ep in episodes:
        number = ep.get("number", "?")
        episode_title = ep.get("title", "Untitled")
        slug = ep.get("slug", "")
        metaphor = ep.get("metaphor", "")
        center_action = ep.get("center_action", "")

        lines.extend(
            [
                f"### Episode {number}: {episode_title}",
                "",
                f"- slug: `{slug}`",
                f"- metaphor: {metaphor}",
                f"- center action: {center_action}",
                "",
            ]
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()