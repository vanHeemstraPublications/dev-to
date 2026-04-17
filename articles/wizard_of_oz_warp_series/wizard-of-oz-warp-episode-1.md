---
title: "Wizard of Oz Warp 🌪️ Ep.1"
published: false
description: "Episode 1: Dorothy was bored in Kansas. You are bored in iTerm2. A tornado called Warp arrives, lifts you out of the grey terminal past, and drops you in a vividly new environment. Install Warp on your Mac Mini M4 Pro, understand blocks, and scaffold your first project."
tags: [warp, terminal, macos, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/wizard_of_oz_warp_series/wizard-of-oz-warp-episode-01.png"
series: "Wizard of Oz Warp Series"
canonical_url: ""
organization: "the-software-s-journey"
---
## Episode 1: Follow the Yellow Brick Road

> "Toto, I've a feeling we're not in Kansas anymore."— Dorothy Gale, The Wizard of Oz (1939)

## The Grey Skies of Kansas 🌩️

Kansas is a traditional terminal. It is grey, functional, unchanged since the 1970s in ways that matter. Commands vanish upward in a wall of text. You scroll to find output from thirty seconds ago. The prompt is a single blinking cursor that knows nothing about what you typed last week. An error arrives with no suggestion of how to fix it. You copy-paste from Stack Overflow into a terminal that treats you like a system administrator from 1983.

You are Dorothy. You have been working in this Kansas for years. It works. Everything works. The Ruby slippers are right there on your feet — you just do not know they are magic yet.

Then the tornado arrives. It is called **Warp**.

## 🗂️ SIPOC — The Journey Begins

| Suppliers | Inputs | Process | Outputs | Customers |
| --- | --- | --- | --- | --- |
| Warp installer (DMG) | Your Mac Mini M4 Pro, macOS Sequoia | Download → drag to Applications → launch → authenticate | A modern Agentic Development Environment running natively on Apple Silicon | You — with every future episode's workflow running here |
| Your project idea | An empty directory | Scaffold warp-of-oz-tasks with uv, FastAPI, Python 3.12 | A running health endpoint at http://localhost:8000/health | The series codebase that grows across all 8 episodes |
| Warp's block system | Every command you run | Group command + output into a navigable atomic Block | A terminal session you can navigate, copy, search, and share | Your future self — no more scrolling through output walls |

## The Land of Oz: What Warp Actually Is 🏙️

Warp is not a terminal emulator with an AI bolt-on. It is an **Agentic Development Environment** — a rethinking of what the terminal can be when you assume the developer also has access to a large language model, a cloud orchestration platform, and a team knowledge base.

It has two parts:

**Warp Terminal** — the application you download and run on your Mac. Built in Rust for performance. It supports zsh, bash, fish, and PowerShell. It adds blocks, a code-editor-quality input experience, AI features, a file editor, code review, and the ability to run local agents interactively.

**Oz** — the orchestration platform that lives at `oz.warp.dev`. Cloud agents that run in the background, triggered by Slack messages, GitHub PRs, Linear issues, or schedules. Oz is the Emerald City — not visible from Dorothy's first view of the munchkin country, but always glowing on the horizon.

This episode is about arriving. The tornado. The yellow bricks. The first steps.

## Step 1: Install Warp on the Mac Mini M4 Pro 💻

```bash
# Option 1: Direct download from warp.dev
# Download Warp.dmg → drag to /Applications → launch

# Option 2: Homebrew (recommended — keeps it updated)
brew install --cask warp
```

Warp runs natively on Apple Silicon — no Rosetta translation. The Mac Mini M4 Pro (24 GB unified memory, 12-core CPU) is an excellent host: Warp launches in under a second and local agent inference runs without thermal throttling.

After first launch, Warp asks you to sign in. A free account unlocks AI features with generous limits. Sign in with GitHub or email.

### Verifying the install

```bash
# Warp will already be your terminal — just confirm it loaded zsh correctly
echo $SHELL
# /bin/zsh

# Confirm macOS version
sw_vers
# ProductName:    macOS
# ProductVersion: 15.x.x (Sequoia)
# BuildVersion:   ...

# Confirm architecture
uname -m
# arm64   ← Apple Silicon, not x86_64
```

## The First Blocks: The Munchkins Welcome You 🌈

The first thing you notice in Warp is that command output is not a river — it is **Blocks**.

Every command and its output form a single, self-contained unit. The block has a border. You can click anywhere in it to select it. You can navigate between blocks with `Ctrl-Up` and `Ctrl-Down`. You can copy just the output, just the command, or both — with formatting preserved.

Try it:

```bash
# Run a command
ls -la ~

# Click somewhere else, then press Ctrl-Up
# You land on the ls -la ~ block, not anywhere in the sea of text

# Press Cmd-C on a block to copy just the output
# Press Shift-Cmd-C to copy "command + output" — useful for sharing

# Type: ls -la ~/Des
# Warp auto-completes the path. Press Tab. It works.
```

This is the yellow brick road. Every step is paved.

## Setting Up the Series Project: `warp-of-oz-tasks` 🏗️

Throughout this series, we build a single Python FastAPI application — a task management API — that grows from a bare scaffold to a production-grade service with authentication, background processing, and cloud agent automation. Every feature is added in Warp, using Warp's tools, on the Mac Mini M4 Pro.

### Install `uv` (Python package manager)

`uv` is a Rust-based Python package manager from Astral. Massively faster than `pip`. Perfect pairing with Warp on Apple Silicon.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (uv installer does this, but verify)
source ~/.zshrc
which uv
# /Users/you/.cargo/bin/uv (or ~/.local/bin/uv)

uv --version
# uv 0.x.x
```

### Scaffold the project

```bash
# Create the project directory
mkdir -p ~/projects/warp-of-oz-tasks
cd ~/projects/warp-of-oz-tasks

# Initialise with uv
uv init --name warp-of-oz-tasks --python 3.12

# The project structure uv creates:
# warp-of-oz-tasks/
# ├── .python-version    ← pins Python version
# ├── pyproject.toml     ← project metadata and dependencies
# ├── README.md
# └── hello.py           ← placeholder (we'll replace this)

# Add FastAPI and uvicorn
uv add fastapi "uvicorn[standard]"

# Confirm
cat pyproject.toml
```

### Write the first source file

```bash
# Remove the placeholder
rm hello.py

# Create the application entry point
cat > src/main.py << 'PYTHON'
"""
warp-of-oz-tasks: A FastAPI task management API.
Built across 8 episodes of the Warp of Oz series on a Mac Mini M4 Pro.
"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Warp of Oz Tasks",
    description="Follow the yellow brick road — one endpoint at a time.",
    version="0.1.0",
)

@app.get("/health")
async def health_check():
    """The Munchkins confirm you have arrived safely."""
    return {
        "status": "alive",
        "message": "Toto, I've a feeling we're not in Kansas anymore.",
        "timestamp": datetime.utcnow().isoformat(),
    }
PYTHON

# uv expects src layout — create the package
mkdir -p src
touch src/__init__.py
```

Wait — let's check the `pyproject.toml` and fix the source layout:

```bash
# Update pyproject.toml to reflect src layout
cat > pyproject.toml << 'TOML'
[project]
name = "warp-of-oz-tasks"
version = "0.1.0"
description = "A FastAPI task API — built with Warp, episode by episode."
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
TOML
```

### Run the first server

```bash
# Run with uv run (handles the venv automatically)
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Open another Warp tab (`Cmd-T`) and test:

```bash
curl http://localhost:8000/health | python3 -m json.tool
# {
#     "status": "alive",
#     "message": "Toto, I've a feeling we're not in Kansas anymore.",
#     "timestamp": "2026-04-17T..."
# }
```

The yellow brick road is paved. The first block sparkles.

## The Warp Input Editor: Cursor Movement in the Terminal 🖊️

Traditional terminals treat the input line like a 1970s text field. Warp treats it like a code editor:

```bash
# Multi-line input — press Shift-Enter for new lines
# The entire block becomes a multi-line script
python3 -c "
import sys
print(f'Python {sys.version}')
print('Running on Apple Silicon' if 'arm64' in sys.platform else 'Not ARM')
"

# Alt-click to place the cursor exactly where you want
# Cmd-Z to undo a character you deleted in the input
# Select text with Shift-Arrow and delete it

# This works like VS Code. Because Warp is built to.
```

## The `#` Key: Your First Taste of Magic ✨

Type `#` in Warp's input and start describing what you want in plain English:

```
# show me all python processes running on this machine
```

Warp converts this to:

```bash
ps aux | grep python
```

This is not AI autocomplete. This is natural language to shell command translation. Try more:

```
# find all files larger than 100MB in my home directory
# show disk usage for the current directory sorted by size
# what port is uvicorn running on
```

The Scarecrow is acquiring a brain. But that is Episode 2.

## The Project Structure So Far 📁

```
~/projects/warp-of-oz-tasks/
├── .python-version         ← Python 3.12
├── pyproject.toml          ← dependencies and metadata
├── README.md
└── src/
    ├── __init__.py
    └── main.py             ← health endpoint ✓
```

Commit this starting point:

```bash
cd ~/projects/warp-of-oz-tasks
git init
git add .
git commit -m "feat: scaffold warp-of-oz-tasks — the tornado has landed"
```

## The Series Map: Eight Episodes 🗺️

| # | Episode | Oz parallel | Warp feature | Codebase milestone |
| --- | --- | --- | --- | --- |
| 1 | This one — Yellow Brick Road | Dorothy arrives | Blocks, input editor, # key | Health endpoint |
| 2 | The Scarecrow Gets a Brain | Scarecrow + brain | AI completions, Active AI, agent chat | CRUD endpoints for tasks |
| 3 | The Tin Man Gets a Heart | Tin Man + heart | WARP.md, Rules, Skills | Auth middleware |
| 4 | The Lion Gets Courage | Cowardly Lion | Agent pair mode, code review panel | Debug a planted error |
| 5 | Flying Monkeys: Dispatch | Flying monkeys | Autonomous dispatch mode | Background task processor |
| 6 | The Emerald City: Oz | Emerald City | Cloud agents, Oz CLI, schedules | Scheduled cleanup agent |
| 7 | The Ruby Slippers: Augment | Ruby slippers | Augment Code Intent + Warp | Spec-driven feature |
| 8 | There's No Place Like Home | Going home | MCP, Warp Drive, full workflow | Production-ready service |

In **Episode 2**, the Scarecrow joins the road. He needs a brain. Warp's AI features are exactly that.

**🔗 Resources**

- **Warp download**: [warp.dev](https://www.warp.dev)
- **Warp documentation**: [docs.warp.dev](https://docs.warp.dev)
- **Oz platform**: [oz.warp.dev](https://oz.warp.dev)
- **uv (Python package manager)**: [docs.astral.sh/uv](https://docs.astral.sh/uv)
- **FastAPI**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

*🌪️ Warp of Oz Series follows the Yellow Brick Road through Warp's Agentic Development Environment — from the first install on a Mac Mini M4 Pro to cloud agent orchestration with Oz, with Augment Code Intent as the ruby slippers that were powerful all along.*