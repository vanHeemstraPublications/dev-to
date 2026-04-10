---
title: "Cable Car Git! 🚡 Ep.1"
part: 1
published: false
description: "Episode 1: Git explained through a cable car parcel transport network. The repository is the network, commits are cabins, branches are lines. Understand the system before you touch a command."
tags: [git, beginners, versioncontrol, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/cable-car-git-episode-01.png"
series: "Cable Car Git Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 1: Welcome to the Network

> *“Understand the system, and the commands follow naturally.”*

-----

## Something Goes Wrong on Every Project Without It 😬

Picture a software project with no version control. Six developers. One shared folder on a network drive. Everyone edits files directly. Maria overwrites Ahmed’s changes without knowing. The build breaks at 4pm on a Friday. Nobody knows which of the twelve simultaneous edits caused it. Ahmed opens his local copy — it was a working version from Tuesday. But it’s on his laptop at home.

This is not a historical scenario. This still happens. Usually at the worst possible moment.

**Git** is the answer the entire software industry settled on. It is a version control system — a tool that tracks every change made to every file, stores the complete history of a project, lets multiple people work in parallel without overwriting each other, and makes it possible to go back to any previous state at any time.

It was created by Linus Torvalds in 2005 for developing the Linux kernel. Today it is used by 97% of professional developers.

But let’s not start with the commands. Let’s start with the *system* — because once you understand what Git is actually doing, the commands become obvious.

-----

## 🗂️ SIPOC — The Transport Network

|**Suppliers**                          |**Inputs**                       |**Process**                                           |**Outputs**                                                                             |**Customers**                                                      |
|---------------------------------------|---------------------------------|------------------------------------------------------|----------------------------------------------------------------------------------------|-------------------------------------------------------------------|
|Developers (you, your team)            |Changed source files             |`git add` → stage changes; `git commit` → seal a cabin|A cabin (commit) carrying a snapshot of staged changes, dispatched along a line (branch)|Every developer pulling from the shared depot (remote)             |
|The Git repository                     |The complete network history     |Branching, merging, rebasing, stashing                |A navigable, shareable record of every change since the project began                   |The project itself — its history, its integrity, its recoverability|
|The remote depot (GitHub, GitLab, etc.)|Pushed cabins from all developers|`git push` / `git pull` to synchronise                |A shared, authoritative version of the network                                          |The team, CI/CD systems, deployment pipelines                      |

-----

## The Cable Car Network 🏔️

Imagine a mountain cable car network — the kind that transports goods, parcels, and materials up and down alpine terrain. Not the tourist kind. The working industrial kind, where real cargo moves along steel cables between stations, loaded into individual cabins at one end and unloaded at the other.

This network is your **Git repository**.

Everything Git does maps precisely onto this network:

|Cable car world                |Git world                                                              |
|-------------------------------|-----------------------------------------------------------------------|
|The network itself             |The Git repository (`.git/` directory)                                 |
|A parcel or package            |A file or set of file changes                                          |
|A cabin                        |A **commit** — sealed container carrying a snapshot of changes         |
|The cable line / route         |A **branch** — a named sequence of cabins                              |
|The main trunk line            |The `main` branch (formerly called `master`)                           |
|A spur line off the trunk      |A **feature branch**                                                   |
|The loading platform           |The **staging area** (index) — where you prepare parcels before sealing|
|Dispatching a loaded cabin     |`git commit`                                                           |
|The central depot              |The **remote** (GitHub, GitLab, Bitbucket)                             |
|Sending cabins to the depot    |`git push`                                                             |
|Receiving cabins from the depot|`git pull` / `git fetch`                                               |
|Holding locker at the station  |`git stash` — temporary parcel storage                                 |
|Two lines joining at a junction|A **merge**                                                            |
|The network map / timetable    |`git log`                                                              |

The beauty of this metaphor is that it captures Git’s core property: **nothing is ever lost**. Every cabin that was ever dispatched is still on the network. The full history of every route, every junction, every parcel that was ever loaded — all of it is preserved, navigable, and retrievable.

-----

## The Three States of a Parcel 📦

Before a parcel reaches a cabin, it passes through three states. This is the most important concept to understand before touching a single command.

```
Working Directory      Staging Area (Index)      Repository
─────────────────      ────────────────────      ──────────
Your files as          Parcels loaded onto        Sealed, dispatched
you edit them          the platform, ready        cabins — committed
                       to be sealed               history
      │                        │                       │
 git add ──────────────────────►                       │
                       git commit ────────────────────►
```

**Working Directory** — this is where you actually work. You edit files here. No Git action has happened yet. These are loose parcels on the warehouse floor.

**Staging Area (Index)** — when you run `git add`, you move parcels to the loading platform. You are saying: “these specific changes will go into the next cabin.” You can stage some files and not others. You can stage parts of a file. The staging area is your precise selection tool.

**Repository** — when you run `git commit`, the loading platform is sealed into a cabin and dispatched. The cabin now exists permanently in the network’s history. You cannot change a dispatched cabin (you can only issue a corrective cabin later — more on that in Episode 8).

-----

## What Is Actually Stored in a Cabin? 🎁

This is where many tutorials skip something important. Git does not store *diffs* (the differences between versions). Git stores **snapshots** — a complete picture of every tracked file at the moment the commit was created.

Each commit (cabin) contains:

- A **tree** — a complete snapshot of the entire project at that moment
- A **pointer to the parent commit** — the previous cabin in the chain
- **Metadata** — author, timestamp, and your commit message (the cabin’s bill of lading)
- A **unique SHA-1 hash** — a 40-character identifier like `a3f9c12d...` that acts as the cabin’s unique ID

When you look at a diff between two commits, Git is calculating it on demand by comparing two snapshots — not playing back a stored diff. This makes Git extraordinarily fast and resilient.

-----

## The Network Map: Visualising the History 🗺️

Every cable car network has a map. Git’s map is the commit graph.

```
  A --- B --- C --- D        ← main line (main branch)
              |
              E --- F        ← spur line (feature-login branch)
```

- Each letter is a commit (cabin)
- Each line is a branch (cable route)
- The arrow connecting cabins shows parent-child relationships
- `D` is the current tip of `main`
- `F` is the current tip of `feature-login`
- The branch split happened at `C` — that’s where the spur line left the main trunk

This graph is the heart of everything Git does. Understanding it makes every command — merge, rebase, stash, cherry-pick — immediately logical.

-----

## Installing Git and First Configuration ⚙️

```bash
# macOS (comes with Xcode tools, or install via Homebrew)
brew install git

# Ubuntu / Debian
sudo apt install git

# Windows
# Download from git-scm.com (includes Git Bash)
```

After installing, configure your identity — this appears in every cabin’s bill of lading:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Optional but recommended: set a default editor
git config --global core.editor "code --wait"   # VS Code
# git config --global core.editor "nano"        # Nano
# git config --global core.editor "vim"         # Vim

# Set the default branch name to 'main' (modern convention)
git config --global init.defaultBranch main
```

Verify your configuration:

```bash
git config --list
# user.name=Your Name
# user.email=you@example.com
# core.editor=code --wait
# init.defaultBranch=main
```

-----

## The Series Map: Eight Episodes 📋

This series covers Git from network entry to advanced recovery operations:

|#|Episode                                         |Cable car concept            |
|-|------------------------------------------------|-----------------------------|
|1|*This one* — What Git is and how it works       |Welcome to the network       |
|2|`init`, `add`, `commit`, `status`, `log`        |Your first cabin             |
|3|Branches, `switch`, `checkout`                  |Building new lines           |
|4|Merge strategies, conflicts                     |Joining lines at the junction|
|5|`rebase`, interactive rebase, squash            |Replaying the route          |
|6|`stash` — the full picture                      |The holding locker           |
|7|`remote`, `push`, `pull`, `fetch`, pull requests|The remote depot             |
|8|`reset`, `revert`, `cherry-pick`, `reflog`      |Recovering lost parcels      |

By Episode 8, you will understand not just *what* Git commands do, but *why* they work — because you will know the network.

The first cabin leaves in Episode 2. Get your parcels ready.

-----

**🔗 Resources**

- **Official Git documentation**: [git-scm.com/doc](https://git-scm.com/doc)
- **Pro Git book** (free): [git-scm.com/book](https://git-scm.com/book/en/v2)
- **Interactive Git tutorial**: [learngitbranching.js.org](https://learngitbranching.js.org)

-----

*🚡 Cable Car Git! is a series about Git — explained through the metaphor of a cable car parcel transport network, where every commit is a cabin and every branch is a route.*
