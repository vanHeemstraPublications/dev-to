-----

## title: “Cable Car Git! 🚡 Ep.2: Your First Cabin”
published: false
description: “Episode 2: Load your first parcels, seal your first cabin, dispatch it. `git init`, `git add`, `git commit`, `git status`, `git log` — the five commands that start every journey on the network.”
tags: [git, beginners, versioncontrol, tutorial]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/cable-car-git-episode-02.png”
series: “Cable Car Git!”
canonical_url: “”
organization: “the-software-s-journey”

# Cable Car Git! 🚡

## Episode 2: Your First Cabin

> *“The network exists. Now load the first cabin.”*

-----

## Opening the Station 🏗️

In Episode 1, you understood the network. Commits are cabins, branches are lines, the staging area is the loading platform, the remote is the depot. The map is clear.

Now we build the first station and dispatch the first cabin. Five commands cover everything you need:

- `git init` — build the station
- `git status` — check what is on the loading platform and warehouse floor
- `git add` — move parcels from the floor to the platform
- `git commit` — seal and dispatch the cabin
- `git log` — read the network’s dispatch ledger

-----

## 🗂️ SIPOC — Dispatching the First Cabin

|**Suppliers**         |**Inputs**                                    |**Process**                                        |**Outputs**                                                       |**Customers**                                |
|----------------------|----------------------------------------------|---------------------------------------------------|------------------------------------------------------------------|---------------------------------------------|
|You (developer)       |A directory with files to track               |`git init` — installs the station (creates `.git/`)|An empty network, main line ready, no cabins yet                  |You, ready to stage and commit               |
|Your changed files    |Modified or new files in the working directory|`git add` — load parcels onto the platform         |Staged changes (index updated)                                    |`git commit`, which seals and dispatches them|
|The staging area      |Everything loaded on the platform             |`git commit -m "message"` — seal and dispatch      |A new cabin (commit) on the main line with a SHA-1 ID             |`git log` and all downstream consumers       |
|The repository history|All dispatched cabins                         |`git log` — read the dispatch ledger               |A human-readable list of cabins with IDs, authors, dates, messages|You, your team, the CI/CD pipeline           |

-----

## `git init` — Building the Station 🏗️

A Git repository starts with `git init`. Run it inside the directory you want to track:

```bash
mkdir my-project
cd my-project
git init
# Initialized empty Git repository in /Users/you/my-project/.git/
```

This creates a hidden `.git/` directory. That directory **is** the network — it contains the full commit history, all branch pointers, configuration, and the stash stack. You never edit it manually. But knowing it exists helps demystify Git: your project’s entire history lives in that one folder.

```bash
ls -la
# .git/    ← the entire network lives here
```

**Alternatively: clone an existing network**

If a project already exists on a remote depot (GitHub, GitLab), you do not `init` — you clone:

```bash
git clone https://github.com/example/project.git
# Creates a 'project/' directory with the full network already inside
```

Cloning downloads all cabins, all lines, and sets up the connection to the remote depot automatically.

-----

## `git status` — Checking the Platform 👁️

Before loading anything, you want to know what is on the warehouse floor and what is already on the platform. `git status` answers both questions:

```bash
# Create a file
echo "# My Project" > README.md

git status
# On branch main
#
# No commits yet
#
# Untracked files:
#   (use "git add <file>..." to include in what will be committed)
#         README.md
#
# nothing added to commit but untracked files present
```

Three zones in `git status` output:

1. **Staged changes** (“Changes to be committed”) — parcels on the platform, ready for the next cabin
1. **Unstaged changes** (“Changes not staged for commit”) — tracked files that have been modified, but not yet loaded
1. **Untracked files** — files Git has never seen before; not yet part of the network

`git status` is free and instant. Run it constantly. Run it before every `add`, before every `commit`, before every `push`. It never lies about the state of the station.

-----

## `git add` — Loading Parcels onto the Platform 📦

`git add` moves changes from the warehouse floor to the loading platform (staging area). You are declaring: “these specific changes will go into the next cabin.”

```bash
# Stage a specific file
git add README.md

git status
# On branch main
#
# No commits yet
#
# Changes to be committed:
#   (use "git rm --cached <file>..." to unstage)
#         new file:   README.md
```

`README.md` is now on the platform. It will be in the next cabin.

### Staging strategies

```bash
# Stage a single file
git add README.md

# Stage multiple specific files
git add src/auth.py tests/test_auth.py

# Stage all changes in the current directory (be careful — stages everything)
git add .

# Stage all changes across the whole repo
git add -A

# Interactive staging — choose exactly which changes to include, hunk by hunk
git add -p
```

**`git add -p` is worth knowing early.** It lets you review every changed section of every file and choose, interactively, whether each section goes into the cabin. This lets you load only the auth fix into one cabin and leave the unrelated formatting cleanup for the next one — keeping your commit history clean and meaningful.

### What `git add` does not do

`git add` does not change any file. It does not send anything to the remote. It does not create a commit. It only updates the staging area (the loading platform). The file on your warehouse floor is unchanged. You can `git add` and then continue editing the same file — Git will stage the version as it was *when you ran `git add`*, not the later version.

-----

## `git commit` — Sealing and Dispatching the Cabin ✉️

`git commit` seals the loading platform into a cabin and dispatches it along the current line. Everything currently staged goes into this cabin. The staging area is cleared.

```bash
git commit -m "Add README with project overview"
# [main (root-commit) a3f9c12] Add README with project overview
#  1 file changed, 1 insertion(+)
#  create mode 100644 README.md
```

The output tells you:

- The branch the cabin was dispatched on (`main`)
- The cabin’s unique ID — the first 7 characters of the SHA-1 hash (`a3f9c12`)
- Your commit message
- A summary of what changed

### What makes a good commit message?

The commit message is the cabin’s bill of lading. It tells future you — and your colleagues — what this cabin contains and why it was dispatched.

The standard convention:

- **Imperative mood, present tense**: “Add README” not “Added README” or “Adds README”
- **First line under 72 characters** — this is the summary, shown in `git log --oneline`
- **Optional body** (blank line, then detail) — why this change, what problem it solves

```bash
# Short commit (most common for small changes)
git commit -m "Fix null pointer in UserService.authenticate"

# Multi-line commit (for changes needing explanation)
git commit -m "Refactor payment processor to support multiple currencies

The previous implementation hardcoded EUR. This change introduces
a Currency enum and updates all downstream callers. Fixes #247."
```

### Committing everything at once (skip the staging step)

```bash
# Stages all tracked modified files AND commits in one step
# Does NOT include new untracked files
git commit -am "Fix typo in authentication error message"
```

Use this for small, obvious changes where the staging step adds no value. For anything larger, use `git add` first so you control exactly what goes in.

-----

## Building Up the Network: Multiple Cabins 🚡

Let’s dispatch three cabins to see the line forming:

```bash
# Cabin 1 — already dispatched
echo "# My Project" > README.md
git add README.md
git commit -m "Add README"

# Cabin 2
mkdir src
echo "def authenticate(user, password): pass" > src/auth.py
git add src/auth.py
git commit -m "Add authentication skeleton"

# Cabin 3
echo "name: my-project" > pyproject.toml
git add pyproject.toml
git commit -m "Add project configuration"
```

Three cabins dispatched. Three waypoints on the line. Each one sealed, immutable, referenced by its unique ID.

-----

## `git log` — Reading the Dispatch Ledger 📖

`git log` reads the full history of dispatched cabins on the current line:

```bash
git log
# commit f2d8a91c... (HEAD -> main)
# Author: Your Name <you@example.com>
# Date:   Thu Apr 10 09:00:00 2026
#
#     Add project configuration
#
# commit b1c3e47d...
# Author: Your Name <you@example.com>
# Date:   Thu Apr 10 08:45:00 2026
#
#     Add authentication skeleton
#
# commit a3f9c12d...
# Author: Your Name <you@example.com>
# Date:   Thu Apr 10 08:30:00 2026
#
#     Add README
```

The most recent cabin is at the top. `HEAD` points to the cabin you are currently “at” on the network — in this case, the tip of `main`.

### Useful `git log` variations

```bash
# Compact — one line per cabin
git log --oneline
# f2d8a91 Add project configuration
# b1c3e47 Add authentication skeleton
# a3f9c12 Add README

# Visual graph (shows branches and merges as a network diagram)
git log --oneline --graph --all
# * f2d8a91 (HEAD -> main) Add project configuration
# * b1c3e47 Add authentication skeleton
# * a3f9c12 Add README

# Last N cabins
git log -5

# Show what changed in each cabin (the diff)
git log -p

# Search by author
git log --author="Your Name"

# Search by message content
git log --grep="authentication"

# Show cabins that touched a specific file
git log -- src/auth.py
```

`git log --oneline --graph --all` is the network map. As you add branches (Episode 3), this command becomes your first tool for understanding the current state of the whole system.

-----

## Inspecting a Single Cabin 🔍

```bash
# Show the contents of the most recent cabin
git show
# (shows commit metadata + diff against parent)

# Show a specific cabin by its ID
git show b1c3e47

# Show just what files a cabin touched
git show --stat b1c3e47
# b1c3e47d...
# Author: Your Name <you@example.com>
# Add authentication skeleton
#  src/auth.py | 1 +
#  1 file changed, 1 insertion(+)
```

-----

## The Full Workflow in One Sequence 🔄

```bash
# 1. Check current state
git status

# 2. Make some changes
echo "def login(user, token): pass" >> src/auth.py

# 3. See exactly what changed (before staging)
git diff

# 4. Stage the changes
git add src/auth.py

# 5. Verify what is staged
git status
git diff --staged    # shows staged diff (what is on the platform)

# 6. Commit
git commit -m "Add login function stub"

# 7. Verify the cabin was dispatched
git log --oneline
# e7f9a23 Add login function stub
# f2d8a91 Add project configuration
# b1c3e47 Add authentication skeleton
# a3f9c12 Add README
```

Four cabins. Four waypoints. A navigable history that tells the story of how the project evolved.

-----

## The Holding Locker Preview 🔒

One more thing to know: the staging area can be cleared without committing. If you loaded parcels onto the platform and changed your mind:

```bash
# Unstage a file (remove it from the platform, keep the changes on the floor)
git restore --staged src/auth.py

# Or the older syntax:
git reset HEAD src/auth.py
```

The changes remain in your working directory. Only the staging area is cleared. The parcel is back on the warehouse floor, not in a cabin.

-----

In **Episode 3**, we build a new line off the main trunk — a feature branch. We will see how two developers can work in parallel without touching each other’s parcels.

-----

**🔗 Resources**

- **`git add` reference**: [git-scm.com/docs/git-add](https://git-scm.com/docs/git-add)
- **`git commit` reference**: [git-scm.com/docs/git-commit](https://git-scm.com/docs/git-commit)
- **Conventional Commits** (commit message standard): [conventionalcommits.org](https://www.conventionalcommits.org)

-----

*🚡 Cable Car Git! is a series about Git — explained through the metaphor of a cable car parcel transport network, where every commit is a cabin and every branch is a route.*
