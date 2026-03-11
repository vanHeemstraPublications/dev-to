#!/usr/bin/env python3

"""
Prompt CLI

Generate prompt bundles locally from SERIES_EPISODES.yaml.

Usage examples:

Generate all episodes:

    python scripts/prompt-cli.py generate

Generate one episode:

    python scripts/prompt-cli.py generate 4

Output will be written to:

    generated/

Example:

    generated/episode-04-adapter-pattern.md
"""

import sys
import yaml
from pathlib import Path


SERIES_FILE = Path("series/SERIES_EPISODES.yaml")
OUTPUT_DIR = Path("generated")


def load_series():
    if not SERIES_FILE.exists():
        print("Error: series/SERIES_EPISODES.yaml not found")
        sys.exit(1)

    with open(SERIES_FILE, "r") as f:
        return yaml.safe_load(f)


def generate_prompt(series, episode):
    props = "\n".join(f"- {p}" for p in episode.get("supporting_props", []))

    text = f"""# Prompt Bundle

Series: {series['series']['name']}

Episode: {episode['number']} - {episode['title']}

Metaphor:
{episode.get('metaphor','')}

Center Action:
{episode.get('center_action','')}

Supporting Props:
{props}

Suggested Subtitle:
Episode {episode['number']}: {episode['title']}
"""

    return text


def generate_all(data):

    series = data["series"]
    episodes = data["episodes"]

    OUTPUT_DIR.mkdir(exist_ok=True)

    for ep in episodes:

        filename = OUTPUT_DIR / f"episode-{ep['number']:02d}-{ep['slug']}.md"

        prompt = generate_prompt(data, ep)

        filename.write_text(prompt)

        print(f"Generated {filename}")


def generate_single(data, number):

    episodes = data["episodes"]

    OUTPUT_DIR.mkdir(exist_ok=True)

    for ep in episodes:

        if str(ep["number"]) == number:

            filename = OUTPUT_DIR / f"episode-{ep['number']:02d}-{ep['slug']}.md"

            prompt = generate_prompt(data, ep)

            filename.write_text(prompt)

            print(f"Generated {filename}")

            return

    print(f"Episode {number} not found.")


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/prompt-cli.py generate")
        print("  python scripts/prompt-cli.py generate <episode_number>")
        sys.exit(0)

    command = sys.argv[1]

    if command != "generate":
        print("Unknown command.")
        sys.exit(1)

    data = load_series()

    if len(sys.argv) == 2:
        generate_all(data)
    else:
        generate_single(data, sys.argv[2])


if __name__ == "__main__":
    main()