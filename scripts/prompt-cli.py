#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)

SERIES_INDEX_FILE = Path("series/SERIES_INDEX.yaml")

DEFAULT_CONFIG = {
    "github_repository_url": "",
    "article_repository_url": (
        "https://github.com/vanHeemstraSystems/dev-to/articles/"
    ),
    "article_tone": "light-hearted, humorous, beginner-friendly",
    "article_humor_style": "playful and witty",
    "article_code_language": "Python",
    "article_frontmatter_required": True,
    "image_resolution": "1000x420",
    "image_aspect_ratio": "100:42",
    "image_format": "WebP",
    "image_max_file_size_kb": 400,
    # DEV.to cover images can be shown with extra cropping. Increase overall
    # whitespace so the composition survives various viewports.
    "image_whitespace_margin_percent": 24,
    "image_title_safe_left_right_percent": 12,
    # DEV.to cover images are frequently cropped (especially on top) depending
    # on layout and viewport. Use conservative safe areas for any typography.
    "image_title_safe_top_percent": 52,
    "image_title_safe_bottom_percent": 18,
    "image_style": (
        "cinematic digital illustration, highly detailed, "
        "storybook realism, polished composition"
    ),
    "article_structure": [
        "humorous opening hook",
        "introduce the metaphor",
        "explain the concept step-by-step",
        "include code examples",
        "include a SIPOC section",
        "recap the key idea",
        "end with a teaser for the next episode",
    ],
}


def load_yaml(path):
    path = Path(path)

    if not path.exists():
        print(f"Error: file not found: {path}")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except Exception as exc:
        print(f"Error reading YAML from {path}: {exc}")
        sys.exit(1)


def write_yaml(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(
            data,
            handle,
            sort_keys=False,
            allow_unicode=True,
            width=88,
        )


def load_json(path):
    path = Path(path)

    if not path.exists():
        print(f"Error: config file not found: {path}")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        print(f"Error reading JSON from {path}: {exc}")
        sys.exit(1)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")


def prompt_input(label, default=""):
    if default:
        value = input(f"{label} [{default}]: ").strip()
        return value or default
    return input(f"{label}: ").strip()


def prompt_int(label, default):
    raw = prompt_input(label, str(default))
    try:
        return int(raw)
    except ValueError:
        print(f"Invalid number: {raw}")
        sys.exit(1)


def ensure_series_index_exists():
    SERIES_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

    if SERIES_INDEX_FILE.exists():
        data = load_yaml(SERIES_INDEX_FILE)
        if not isinstance(data, dict):
            data = {"series": []}
        if "series" not in data or not isinstance(data["series"], list):
            data["series"] = []
        return data

    data = {"series": []}
    write_yaml(SERIES_INDEX_FILE, data)
    return data


def add_series_to_index(series_id, series_name, series_file):
    index_data = ensure_series_index_exists()
    entries = index_data.get("series", [])

    for entry in entries:
        if entry.get("id") == series_id:
            return False

    entries.append(
        {
            "id": series_id,
            "name": series_name,
            "file": str(series_file),
        }
    )

    index_data["series"] = entries
    write_yaml(SERIES_INDEX_FILE, index_data)
    return True


def load_series_config(series):
    config = dict(DEFAULT_CONFIG)
    config_path = series.get("series_config")

    if config_path:
        loaded = load_json(config_path)
        if isinstance(loaded, dict):
            config.update(loaded)

    return config


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
        file_path = item.get("file")
        print(f"- {sid}: {name} ({file_path})")


def get_episode(data, episode_number):
    episodes = data.get("episodes", [])

    for episode in episodes:
        if str(episode.get("number")) == str(episode_number):
            return episode

    return None


_DISPLAY_TITLE_PLACEHOLDER = "add display title here"


def episode_image_title(episode):
    """
    Title to use in image prompt subtitle.

    We prefer an explicit `display_title` so that `center_action` can be used
    purely for scene/action description without also becoming the title.
    """

    display_title = (episode.get("display_title") or "").strip()
    if display_title:
        return display_title

    # Backwards-compatible fallback for older series files.
    return (episode.get("title") or "").strip()


def build_title_safety_block(series_name, episode_number, title, config):
    lr = config["image_title_safe_left_right_percent"]
    top = config["image_title_safe_top_percent"]
    bottom = config["image_title_safe_bottom_percent"]

    return (
        "DEV.to title safety requirements:\n"
        "- This image will be used as a DEV.to article header/banner.\n"
        "- DEV.to often crops the top/bottom edges of cover images.\n"
        "- Keep all text fully readable inside a conservative safe area.\n"
        "- Do not place important text near the extreme edges.\n"
        f"- Keep title typography at least {lr}% away from the left and right "
        "edges.\n"
        f"- Keep title typography at least {top}% away from the top edge.\n"
        f"- Keep title typography at least {bottom}% away from the bottom "
        "edge.\n"
        "- Do NOT place any text in the top safe-margin area.\n"
        "- Place the entire title block in the visual middle band of the "
        "image (not the top third).\n"
        "- Keep the subtitle clearly below the main title with generous "
        "spacing.\n"
        "- Use slightly smaller typography rather than oversized typography "
        "if needed.\n"
        "- Do not let any letter, banner, or ornament touch the image edge.\n"
        "- The full title and subtitle must be completely visible.\n\n"
        "Placement target (important):\n"
        f"- Treat the top {top}% of the image as a NO-TEXT zone.\n"
        "- Place the series title so its cap-height starts below that zone.\n"
        "- Aim for the title block center around ~65% of image height.\n"
        "- Place the subtitle below the series title (not above).\n\n"
        "Exact text to include:\n"
        "Top title:\n"
        f"\"{series_name}\"\n\n"
        "Subtitle:\n"
        f"\"Episode {episode_number}: {title}\""
    )


def build_image_prompt(data, episode, config):
    series = data.get("series", {})
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})

    series_name = series.get("name", "")
    title = episode_image_title(episode)
    metaphor = episode.get("metaphor", "")
    center_action = episode.get("center_action", "")

    setting = defaults.get("setting", "")
    lighting = defaults.get("lighting", "")

    left_third = composition.get("left_third", "")
    center = composition.get("center", "")
    right_third = composition.get("right_third", "")
    background = composition.get("background", "")

    props_text = ", ".join(episode.get("supporting_props", []))

    title_safety = build_title_safety_block(
        series_name,
        episode["number"],
        title,
        config,
    )

    repo_url = config.get("github_repository_url", "")
    repo_block = ""
    if repo_url:
        repo_block = (
            "\nReference repository for the series concept:\n"
            f"{repo_url}\n"
        )

    return f"""
Create a polished cinematic landscape banner illustration for a web article.

Series title:
"{series_name}"

Episode subtitle:
"Episode {episode['number']}: {title}"

Canvas requirements:
- resolution: {config["image_resolution"]}
- aspect ratio: {config["image_aspect_ratio"]}
- landscape banner composition
- about {config["image_whitespace_margin_percent"]}% whitespace around the
  artwork
- clean readable layout suitable for a DEV.to article header
- avoid clutter and keep the composition visually clear

Output requirements:
- export format: {config["image_format"]}
- target file size: under {config["image_max_file_size_kb"]} KB
- optimized for fast web loading
- suitable for DEV.to cover image usage

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
- {config["image_style"]}
- visually striking but not overcrowded
- designed specifically as a web article banner

{title_safety}{repo_block}

Avoid:
- visual clutter
- unreadable text
- cramped composition
- generic stock-art look
- flat lighting
- messy perspective
- low-detail background
- accidental portrait orientation
- oversized title text
- cropped-looking typography
""".strip()


def build_article_structure_block(config):
    lines = []
    for idx, item in enumerate(config["article_structure"], start=1):
        lines.append(f"{idx}. {item}")
    return "\n".join(lines)


def build_article_prompt(data, episode, config):
    series = data.get("series", {})
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})

    series_name = series.get("name", "")
    series_type = series.get("type", "")
    title = episode.get("title", "")
    metaphor = episode.get("metaphor", "")
    center_action = episode.get("center_action", "")

    props_text = ", ".join(episode.get("supporting_props", []))

    setting = defaults.get("setting", "")
    left_third = composition.get("left_third", "")
    center = composition.get("center", "")
    right_third = composition.get("right_third", "")
    background = composition.get("background", "")

    github_url = config.get("github_repository_url", "")
    article_repo = config.get("article_repository_url", "")
    structure_block = build_article_structure_block(config)

    repo_reference = ""
    if github_url:
        repo_reference = (
            "\nSeries repository for reference:\n"
            f"{github_url}\n"
        )

    frontmatter_line = (
        "yes" if config["article_frontmatter_required"] else "no"
    )

    return f"""
I have created a repository that contains markdown articles published to
dev.to.

The articles live in:
{article_repo}

Please inspect the formatting style used in those articles, especially the
frontmatter.

Now create the following article.

Series:
{series_name}

Series type:
{series_type}

Episode:
Episode {episode["number"]}: {title}

Writing style requirements:
- tone: {config["article_tone"]}
- humor style: {config["article_humor_style"]}
- beginner-friendly
- explain complex concepts in simple terms
- include code samples in {config["article_code_language"]}
- include explanations of the code
- use a memorable metaphor consistently throughout the article

Primary metaphor:
{metaphor}

Episode-specific action:
{center_action}

Scene / setting inspiration:
{setting}

Visual inspiration:
- left third: {left_third}
- center: {center}
- right third: {right_third}
- background: {background}

Useful props / concepts to weave into the explanation:
{props_text}

Article requirements:
- produce a complete dev.to-ready markdown article
- include frontmatter similar to the examples in the repository:
  {frontmatter_line}
- include headings and subheadings
- include humorous storytelling
- include practical code examples
- include explanations of the code
- ensure the article is engaging and readable
- make the subject understandable for readers who are new to it

Suggested structure:
{structure_block}

SIPOC requirement:
Please include a section in the article that explains the concept using the
SIPOC pattern:
- Supplier
- Input
- Process
- Output
- Consumer

For the SIPOC section:
- explain each SIPOC element in simple language
- map each SIPOC element both to the real technical concept and to the
  metaphor used in the article
- make the SIPOC section practical and easy to understand
- prefer a compact table or bullet structure if that improves readability

Output:
Return the complete article in markdown including frontmatter.{repo_reference}
""".strip()


def generate_prompt_bundle(data, episode):
    series = data.get("series", {})
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})
    config = load_series_config(series)

    props_lines = ""
    for prop in episode.get("supporting_props", []):
        props_lines += f"- {prop}\n"

    image_prompt = build_image_prompt(data, episode, config)
    article_prompt = build_article_prompt(data, episode, config)

    github_repo_url = config.get("github_repository_url", "")
    if not github_repo_url:
        github_repo_url = "[UPDATE_SERIES_GITHUB_REPOSITORY_URL]"

    return f"""
# Prompt Bundle

Series ID: {series.get("id")}
Series Name: {series.get("name")}
Series Type: {series.get("type")}

Episode: {episode["number"]} - {episode["title"]}
Slug: {episode.get("slug")}

Canvas
orientation: landscape
resolution: {config["image_resolution"]}
aspect ratio: {config["image_aspect_ratio"]}
whitespace margin: {config["image_whitespace_margin_percent"]}%

Defaults
setting: {defaults.get("setting")}
lighting: {defaults.get("lighting")}

Composition
left third: {composition.get("left_third")}
center: {composition.get("center")}
right third: {composition.get("right_third")}
background: {composition.get("background")}

Episode Metaphor
{episode.get("metaphor")}

Center Action
{episode.get("center_action")}

Supporting Props
{props_lines}

--------------------------------------------------

ChatGPT Image Prompt

{image_prompt}

--------------------------------------------------

Claude / ChatGPT Article Prompt

{article_prompt}

--------------------------------------------------

Series GitHub Repository

{github_repo_url}
""".strip()


def derive_config_path_from_series_file(series_file):
    base = series_file.stem.replace("_", "-")
    return Path("config") / f"{base}.json"


def bootstrap_series(series_file):
    series_file = Path(series_file)

    print("")
    print("Series file not found.")
    print("Let's create starter files for this new series.")
    print("")

    inferred_id = series_file.stem
    default_name = inferred_id.replace("_", " ").strip().title()

    series_id = prompt_input("Series id", inferred_id)
    series_name = prompt_input("Series name", default_name)
    series_type = prompt_input("Series type", "dev_to_series")
    episode_count = prompt_int("Number of episodes", 4)
    base_metaphor = prompt_input(
        "Base metaphor",
        "a memorable metaphor that explains the topic simply",
    )
    setting = prompt_input(
        "Default setting",
        "a visually memorable setting for the series",
    )
    lighting = prompt_input(
        "Default lighting",
        "warm cinematic atmosphere",
    )
    code_language = prompt_input("Article code language", "Python")
    humor_style = prompt_input(
        "Humor style",
        "light-hearted, playful, and witty",
    )
    article_tone = prompt_input(
        "Article tone",
        "light-hearted, humorous, beginner-friendly",
    )
    github_repo_url = prompt_input(
        "Series GitHub repository URL",
        "https://github.com/software-journey/example",
    )

    config_path = derive_config_path_from_series_file(series_file)

    config_data = dict(DEFAULT_CONFIG)
    config_data["github_repository_url"] = github_repo_url
    config_data["article_tone"] = article_tone
    config_data["article_humor_style"] = humor_style
    config_data["article_code_language"] = code_language

    if config_path.exists():
        print(f"Config already exists, not overwriting: {config_path}")
    else:
        write_json(config_path, config_data)
        print(f"Created {config_path}")

    episodes = []
    for number in range(1, episode_count + 1):
        episode_title = f"Episode {number}"
        episode_slug = f"episode-{number}"
        episodes.append(
            {
                "number": number,
                "title": episode_title,
                "display_title": "add display title here",
                "slug": episode_slug,
                "metaphor": base_metaphor,
                "center_action": (
                    "describe the key action for this episode here"
                ),
                "supporting_props": [
                    "placeholder prop 1",
                    "placeholder prop 2",
                ],
            }
        )

    series_data = {
        "series": {
            "id": series_id,
            "name": series_name,
            "type": series_type,
            "orientation": "landscape",
            "resolution": DEFAULT_CONFIG["image_resolution"],
            "aspect_ratio": DEFAULT_CONFIG["image_aspect_ratio"],
            "whitespace_margin_percent": (
                DEFAULT_CONFIG["image_whitespace_margin_percent"]
            ),
            "series_config": str(config_path),
        },
        "defaults": {
            "setting": setting,
            "lighting": lighting,
            "composition": {
                "left_third": "main presenter or guide",
                "center": "core metaphor and primary action",
                "right_third": "supporting action or secondary character",
                "background": "supporting environment for the series",
            },
        },
        "episodes": episodes,
    }

    if series_file.exists():
        print(f"Series file already exists, not overwriting: {series_file}")
    else:
        write_yaml(series_file, series_data)
        print(f"Created {series_file}")

    added = add_series_to_index(series_id, series_name, series_file)
    if added:
        print(f"Updated {SERIES_INDEX_FILE}")
    else:
        print(f"Series already present in {SERIES_INDEX_FILE}")

    print("")
    print("Starter files created.")
    print("Please review and refine them, then rerun the generate command.")
    print("")


def generate_all(series_file):
    series_file = Path(series_file)

    if not series_file.exists():
        bootstrap_series(series_file)
        return

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
        filename = out_dir / (
            f"episode-{episode['number']:02d}-{episode['slug']}.md"
        )
        content = generate_prompt_bundle(data, episode)

        with open(filename, "w", encoding="utf-8") as handle:
            handle.write(content)

        print(f"Generated {filename}")


def generate_single(series_file, episode_number):
    series_file = Path(series_file)

    if not series_file.exists():
        bootstrap_series(series_file)
        return

    data = load_yaml(series_file)

    series = data.get("series", {})
    series_id = series.get("id", "unknown_series")
    episode = get_episode(data, episode_number)

    if not episode:
        print(f"Episode {episode_number} not found.")
        sys.exit(1)

    out_dir = Path("generated") / series_id
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = out_dir / (
        f"episode-{episode['number']:02d}-{episode['slug']}.md"
    )
    content = generate_prompt_bundle(data, episode)

    with open(filename, "w", encoding="utf-8") as handle:
        handle.write(content)

    print(f"Generated {filename}")


def print_usage():
    print("")
    print("Usage:")
    print("  python scripts/prompt-cli.py list-series")
    print("  python scripts/prompt-cli.py generate <series_file>")
    print(
        "  python scripts/prompt-cli.py generate "
        "<series_file> <episode_number>"
    )
    print("")
    print("Behavior:")
    print("- If the series file exists, prompt bundles are generated.")
    print("- If the series file does not exist, starter config and series")
    print("  files are created interactively.")
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
