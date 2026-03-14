#!/usr/bin/env python3

import base64
import io
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml")
    print("Install with: pip install pyyaml pillow openai")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Missing dependency: pillow")
    print("Install with: pip install pillow")
    sys.exit(1)

try:
    from openai import OpenAI
    from openai import BadRequestError
except ImportError:
    print("Missing dependency: openai")
    print("Install with: pip install openai")
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
    "devto_organization": "the-software-s-journey",
    "article_title_prefix": "",
    "image_resolution": "1000x420",
    "image_aspect_ratio": "100:42",
    "image_format": "WebP",
    "image_max_file_size_kb": 400,
    "image_model": "gpt-image-1",
    "image_quality": "medium",
    "image_background": "opaque",
    "image_generation_size": "1536x1024",
    # When we crop the model output to 1000x420, avoid cutting off the top
    # where the title often lives. Use a top-anchored crop for height crops.
    "image_crop_anchor_y": "top",  # "top" | "center" | "bottom"
    "image_whitespace_margin_percent": 24,
    "image_title_safe_left_right_percent": 12,
    "image_title_safe_top_percent": 52,
    "image_title_safe_bottom_percent": 18,
    "image_style": (
        "cinematic digital illustration, highly detailed, "
        "storybook realism, polished composition"
    ),
    "images_local_dir": "images",
    "image_public_base_url": "",
    "image_public_branch": "main",
    "articles_local_dir": "articles",
    # Prefer predictable filenames: <series-slug>-episode-01.md
    "article_filename_template": "{series_slug}-{episode_label}.md",
    "image_filename_template": "episode-{episode_number:02d}.webp",
    "series_cover_filename": "series-cover.webp",
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

    if not config.get("image_public_base_url"):
        repo_url = config.get("github_repository_url", "").strip()
        branch = config.get("image_public_branch", "main").strip() or "main"
        if repo_url:
            derived = derive_raw_github_images_base_url(repo_url, branch)
            config["image_public_base_url"] = derived

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


def episode_image_title(episode):
    display_title = (episode.get("display_title") or "").strip()
    if display_title:
        return display_title

    return (episode.get("title") or "").strip()


def derive_raw_github_images_base_url(repo_url, branch):
    """
    Convert a GitHub repository URL into a raw-content images base URL.

    Example:
    https://github.com/software-journey/azure-data-platform
    ->
    https://raw.githubusercontent.com/software-journey/azure-data-platform/main/images
    """
    repo_url = (repo_url or "").strip().rstrip("/")
    if not repo_url:
        return ""

    parsed = urlparse(repo_url)

    if parsed.netloc not in {"github.com", "www.github.com"}:
        return ""

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return ""

    owner = parts[0]
    repo = parts[1]

    return (
        f"https://raw.githubusercontent.com/"
        f"{owner}/{repo}/{branch}/images"
    )


def build_title_safety_block(series_name, episode_number, title, config):
    lr = config["image_title_safe_left_right_percent"]
    top = config["image_title_safe_top_percent"]
    bottom = config["image_title_safe_bottom_percent"]
    title_center = int(top + (100 - top - bottom) / 2)

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
        f"- Aim for the title block center around ~{title_center}% of image "
        "height.\n"
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


def build_series_cover_prompt(data, config):
    series = data.get("series", {})
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})

    series_name = series.get("name", "")
    series_type = series.get("type", "")
    setting = defaults.get("setting", "")
    lighting = defaults.get("lighting", "")

    left_third = composition.get("left_third", "")
    right_third = composition.get("right_third", "")
    background = composition.get("background", "")

    return f"""
Create a polished cinematic landscape banner illustration for a web article
series overview.

Series title:
"{series_name}"

Optional small subtitle:
"{series_type}"

Canvas requirements:
- resolution: {config["image_resolution"]}
- aspect ratio: {config["image_aspect_ratio"]}
- landscape banner composition
- about {config["image_whitespace_margin_percent"]}% whitespace around the
  artwork
- clean readable layout suitable for a DEV.to article header or repository
    overview banner
- avoid clutter and keep the composition visually clear

Output requirements:
- export format: {config["image_format"]}
- target file size: under {config["image_max_file_size_kb"]} KB
- optimized for fast web loading

Scene setting:
{setting}

Lighting and atmosphere:
{lighting}

Composition guidance:
- left third: {left_third}
- center: broad series concept overview
- right third: {right_third}
- background: {background}

Style requirements:
- {config["image_style"]}
- visually striking but not overcrowded
- designed specifically as a series banner

Text safety requirements:
- keep all text fully readable in a conservative central safe area
- do not place text close to the top edge
- do not let text or ornaments touch the image edge
- keep the title fully visible

Avoid:
- visual clutter
- unreadable text
- cramped composition
- flat lighting
- messy perspective
- low-detail background
- oversized title text
""".strip()


def build_article_structure_block(config):
    lines = []
    for idx, item in enumerate(config["article_structure"], start=1):
        lines.append(f"{idx}. {item}")
    return "\n".join(lines)


def get_images_local_dir(series, config):
    series_id = series.get("id", "unknown_series")
    return Path(config["images_local_dir"]) / series_id


def get_articles_local_dir(series, config):
    series_id = series.get("id", "unknown_series")
    return Path(config["articles_local_dir"]) / series_id


def get_series_slug(series):
    """
    Slug used for outward-facing filenames.

    Convention: series ids end with "_series". We strip that suffix and then
    slugify, so:
      to_the_moon_terraform_series -> to-the-moon-terraform
    """

    series_id = (series.get("id") or "").strip() or "unknown_series"
    if series_id.endswith("_series"):
        series_id = series_id[: -len("_series")]
    return slugify(series_id)


def get_episode_image_filename(episode, config):
    return config["image_filename_template"].format(
        episode_number=int(episode["number"]),
        slug=episode.get("slug", ""),
    )


def get_episode_image_path(series, episode, config):
    images_dir = get_images_local_dir(series, config)
    images_dir.mkdir(parents=True, exist_ok=True)
    return images_dir / get_episode_image_filename(episode, config)


def get_series_cover_path(series, config):
    images_dir = get_images_local_dir(series, config)
    images_dir.mkdir(parents=True, exist_ok=True)
    return images_dir / config["series_cover_filename"]


def get_episode_cover_image_url(series, episode, config):
    base_url = (config.get("image_public_base_url") or "").rstrip("/")
    filename = get_episode_image_filename(episode, config)

    if not base_url:
        return ""

    return f"{base_url}/{series.get('id', 'unknown_series')}/{filename}"


def get_series_cover_image_url(series, config):
    base_url = (config.get("image_public_base_url") or "").rstrip("/")

    if not base_url:
        return ""

    return (
        f"{base_url}/"
        f"{series.get('id', 'unknown_series')}/"
        f"{config['series_cover_filename']}"
    )


def get_article_filename(series, episode, config):
    episode_number = int(episode["number"])
    episode_label = f"episode-{episode_number:02d}"
    series_slug = get_series_slug(series)
    return config["article_filename_template"].format(
        series_slug=series_slug,
        episode_label=episode_label,
        episode_number=episode_number,
        slug=episode.get("slug", ""),
    )


def get_article_output_path(series, episode, config):
    articles_dir = get_articles_local_dir(series, config)
    articles_dir.mkdir(parents=True, exist_ok=True)
    return articles_dir / get_article_filename(series, episode, config)


def derive_article_title_prefix(series):
    """
    Derive a stable DEV.to title prefix from the series name.

    Example:
      "To The Moon Terraform Series" -> "To The Moon Terraform"

    Heuristic:
    - If the series name ends with "Series", drop only that trailing word.
    """

    series_name = (series.get("name") or "").strip()
    if not series_name:
        return get_series_slug(series)

    tokens = series_name.split()
    if len(tokens) >= 2 and tokens[-1].lower() == "series":
        tokens = tokens[:-1]

    return " ".join(tokens)


def build_devto_article_title(series, episode, config):
    prefix = (config.get("article_title_prefix") or "").strip()
    if not prefix:
        prefix = derive_article_title_prefix(series)
    return f"{prefix} Ep.{int(episode['number'])}"


def build_frontmatter_hint(series, episode, config):
    cover_image_url = get_episode_cover_image_url(series, episode, config)
    series_name = series.get("name", "")
    title = build_devto_article_title(series, episode, config)

    lines = [
        "---",
        f'title: "{title}"',
        "published: false",
        'description: "Add article description here."',
        'tags: ["add", "tags", "here"]',
        f'series: "{series_name}"',
    ]

    if cover_image_url:
        lines.append(f'cover_image: "{cover_image_url}"')
    else:
        lines.append(
            'cover_image: "REPLACE_WITH_PUBLIC_IMAGE_URL"'
        )

    lines.append("---")

    return "\n".join(lines)


def build_article_prompt(data, episode, config):
    series = data.get("series", {})
    defaults = data.get("defaults", {})
    composition = defaults.get("composition", {})

    series_name = series.get("name", "")
    series_type = series.get("type", "")
    title = episode_image_title(episode)
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
    frontmatter_hint = build_frontmatter_hint(series, episode, config)

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
- use this cover_image URL approach:
  use a PUBLIC absolute URL, not a local repository path
- include headings and subheadings
- include humorous storytelling
- include practical code examples
- include explanations of the code
- ensure the article is engaging and readable
- make the subject understandable for readers who are new to it

Suggested frontmatter example:
{frontmatter_hint}

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

    cover_image_url = get_episode_cover_image_url(series, episode, config)
    if not cover_image_url:
        cover_image_url = "[UPDATE_PUBLIC_COVER_IMAGE_URL]"

    return f"""
# Prompt Bundle

Series ID: {series.get("id")}
Series Name: {series.get("name")}
Series Type: {series.get("type")}

Episode: {episode["number"]} - {episode_image_title(episode)}
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

Local Image Path
{get_episode_image_path(series, episode, config)}

Public Cover Image URL
{cover_image_url}

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
    image_public_branch = prompt_input(
        "Public image branch",
        "main",
    )

    config_path = derive_config_path_from_series_file(series_file)

    config_data = dict(DEFAULT_CONFIG)
    config_data["github_repository_url"] = github_repo_url
    config_data["article_tone"] = article_tone
    config_data["article_humor_style"] = humor_style
    config_data["article_code_language"] = code_language
    config_data["image_public_branch"] = image_public_branch
    config_data["image_public_base_url"] = derive_raw_github_images_base_url(
        github_repo_url,
        image_public_branch,
    )

    if config_path.exists():
        print(f"Config already exists, not overwriting: {config_path}")
    else:
        write_json(config_path, config_data)
        print(f"Created {config_path}")

    episodes = []
    for number in range(1, episode_count + 1):
        internal_title = f"Episode {number}"
        default_display_title = f"Episode {number}"
        episode_slug = f"episode-{number}"

        episodes.append(
            {
                "number": number,
                "title": internal_title,
                "display_title": default_display_title,
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
            # Required by scripts/prompt-lint.py (used by other tooling too).
            "prompt_template": "prompts/PROMPT_TEMPLATE.md",
            # Default deterministic image generation settings.
            "deterministic_config": "config/IMAGE_GENERATION_CONFIG.yaml",
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


def crop_to_aspect(img, target_ratio, anchor_y="center"):
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target_ratio)
        if anchor_y == "top":
            top = 0
        elif anchor_y == "bottom":
            top = height - new_height
        else:
            top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))

    return img


def compress_webp(img, path, max_kb):
    for quality in range(95, 15, -5):
        img.save(path, "WEBP", quality=quality)
        size_kb = path.stat().st_size / 1024
        if size_kb <= max_kb:
            return

    img.save(path, "WEBP", quality=20)


def ensure_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Missing OPENAI_API_KEY environment variable.")
        sys.exit(1)
    return api_key


def generate_image_file(prompt, config, out_path):
    ensure_openai_api_key()
    client = OpenAI()

    try:
        result = client.images.generate(
            model=config["image_model"],
            prompt=prompt,
            size=config["image_generation_size"],
            quality=config["image_quality"],
            background=config["image_background"],
        )
    except BadRequestError as exc:
        message = ""
        try:
            payload = exc.body or {}
            err = payload.get("error") or {}
            message = (err.get("message") or "").strip()
        except Exception:
            message = ""

        if "Billing hard limit has been reached" in message:
            print("")
            print("OpenAI request failed: billing hard limit reached.")
            print("Fix: increase your OpenAI project/org spend limit or use a")
            print("different OPENAI_API_KEY with available budget.")
            print("")
            sys.exit(1)

        raise

    img_base64 = result.data[0].b64_json
    img_bytes = base64.b64decode(img_base64)

    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    width_str, height_str = config["image_resolution"].lower().split("x")
    target_width = int(width_str)
    target_height = int(height_str)
    target_ratio = target_width / target_height

    anchor_y = (config.get("image_crop_anchor_y") or "center").strip().lower()
    if anchor_y not in {"top", "center", "bottom"}:
        anchor_y = "center"

    img = crop_to_aspect(img, target_ratio, anchor_y=anchor_y)
    img = img.resize((target_width, target_height), Image.LANCZOS)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    compress_webp(img, out_path, config["image_max_file_size_kb"])


def generate_episode_image(data, episode):
    series = data.get("series", {})
    config = load_series_config(series)

    prompt = build_image_prompt(data, episode, config)
    out_path = get_episode_image_path(series, episode, config)

    prompt_path = out_path.with_suffix(".prompt.txt")
    prompt_path.write_text(prompt + "\n", encoding="utf-8")

    generate_image_file(prompt, config, out_path)

    print(f"Generated image {out_path}")
    print(f"Saved prompt {prompt_path}")

    public_url = get_episode_cover_image_url(series, episode, config)
    if public_url:
        print(f"Public cover URL: {public_url}")
    else:
        print("Public cover URL not configured.")


def generate_series_cover(data):
    series = data.get("series", {})
    config = load_series_config(series)

    prompt = build_series_cover_prompt(data, config)
    out_path = get_series_cover_path(series, config)

    prompt_path = out_path.with_suffix(".prompt.txt")
    prompt_path.write_text(prompt + "\n", encoding="utf-8")

    generate_image_file(prompt, config, out_path)

    print(f"Generated series cover {out_path}")
    print(f"Saved prompt {prompt_path}")

    public_url = get_series_cover_image_url(series, config)
    if public_url:
        print(f"Public series cover URL: {public_url}")
    else:
        print("Public series cover URL not configured.")


def build_article_markdown_stub(data, episode, config):
    series = data.get("series", {})
    title = build_devto_article_title(series, episode, config)
    series_name = series.get("name", "")
    cover_image_url = get_episode_cover_image_url(series, episode, config)
    organization = (config.get("devto_organization") or "").strip()

    if not cover_image_url:
        cover_image_url = "REPLACE_WITH_PUBLIC_IMAGE_URL"

    return f"""---
title: "{title}"
part: {int(episode["number"])}
published: false
description: "Add article description here."
tags: ["add", "tags", "here"]
series: "{series_name}"
cover_image: "{cover_image_url}"
canonical_url: ""
organization: "{organization}"
---

# {title}

Write your article here.
"""


def generate_article_stub(data, episode):
    series = data.get("series", {})
    config = load_series_config(series)

    out_path = get_article_output_path(series, episode, config)
    if out_path.exists():
        print(f"Article already exists, not overwriting: {out_path}")
        return

    content = build_article_markdown_stub(data, episode, config)
    out_path.write_text(content, encoding="utf-8")
    print(f"Generated article stub {out_path}")


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


def generate_single_image(series_file, episode_number):
    series_file = Path(series_file)

    if not series_file.exists():
        print(f"Series file not found: {series_file}")
        sys.exit(1)

    data = load_yaml(series_file)
    episode = get_episode(data, episode_number)

    if not episode:
        print(f"Episode {episode_number} not found.")
        sys.exit(1)

    generate_episode_image(data, episode)


def generate_all_images(series_file):
    series_file = Path(series_file)

    if not series_file.exists():
        print(f"Series file not found: {series_file}")
        sys.exit(1)

    data = load_yaml(series_file)
    episodes = data.get("episodes", [])

    if not episodes:
        print("No episodes defined.")
        sys.exit(1)

    for episode in episodes:
        generate_episode_image(data, episode)


def generate_single_article_stub(series_file, episode_number):
    series_file = Path(series_file)

    if not series_file.exists():
        print(f"Series file not found: {series_file}")
        sys.exit(1)

    data = load_yaml(series_file)
    episode = get_episode(data, episode_number)

    if not episode:
        print(f"Episode {episode_number} not found.")
        sys.exit(1)

    generate_article_stub(data, episode)


def generate_all_article_stubs(series_file):
    series_file = Path(series_file)

    if not series_file.exists():
        print(f"Series file not found: {series_file}")
        sys.exit(1)

    data = load_yaml(series_file)
    episodes = data.get("episodes", [])

    if not episodes:
        print("No episodes defined.")
        sys.exit(1)

    for episode in episodes:
        generate_article_stub(data, episode)


def print_usage():
    print("")
    print("Usage:")
    print("  python scripts/prompt-cli.py list-series")
    print("  python scripts/prompt-cli.py generate <series_file>")
    print(
        "  python scripts/prompt-cli.py generate <series_file> "
        "<episode_number>"
    )
    print("  python scripts/prompt-cli.py generate-image <series_file> "
          "<episode_number>")
    print("  python scripts/prompt-cli.py generate-images <series_file>")
    print("  python scripts/prompt-cli.py generate-article <series_file> "
          "<episode_number>")
    print("  python scripts/prompt-cli.py generate-articles <series_file>")
    print("  python scripts/prompt-cli.py generate-series-cover <series_file>")
    print("")
    print("Behavior:")
    print("- If the series file exists, prompt bundles can be generated.")
    print("- If the series file does not exist, starter config and series")
    print("  files are created interactively.")
    print("- Episode images are saved in images/<series_id>/")
    print("- Article stubs are saved in articles/<series_id>/")
    print(
        "- DEV.to cover_image uses a public absolute URL, not /images/..."
    )
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

    if command == "generate-image":
        if len(sys.argv) < 4:
            print("Missing arguments.")
            print_usage()
            return

        generate_single_image(sys.argv[2], sys.argv[3])
        return

    if command == "generate-images":
        if len(sys.argv) < 3:
            print("Missing series file.")
            print_usage()
            return

        generate_all_images(sys.argv[2])
        return

    if command == "generate-article":
        if len(sys.argv) < 4:
            print("Missing arguments.")
            print_usage()
            return

        generate_single_article_stub(sys.argv[2], sys.argv[3])
        return

    if command == "generate-articles":
        if len(sys.argv) < 3:
            print("Missing series file.")
            print_usage()
            return

        generate_all_article_stubs(sys.argv[2])
        return

    if command == "generate-series-cover":
        if len(sys.argv) < 3:
            print("Missing series file.")
            print_usage()
            return

        series_file = Path(sys.argv[2])

        if not series_file.exists():
            print(f"Series file not found: {series_file}")
            sys.exit(1)

        data = load_yaml(series_file)
        generate_series_cover(data)
        return

    print("Unknown command.")
    print_usage()


if __name__ == "__main__":
    main()
