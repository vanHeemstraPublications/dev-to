---
title: "Cable Car Git! 🚡 Ep.7"
part: 7
published: false
description: "Episode 7: Your local network connects to the central depot. `git remote`, `git push`, `git pull`, `git fetch` — and the pull request workflow that lets teams review and merge across the world."
tags: [git, beginners, versioncontrol, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/cable-car-git-episode-07.png"
series: "Cable Car Git Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: The Remote Depot

> *“The local network is yours. The depot connects you to everyone.”*

-----

## The Central Depot 🏛️

Every cable car network in a real alpine region connects to a central depot — a logistics hub where goods from multiple local networks are received, sorted, and redistributed. Operators of local networks send their outgoing cabins to the depot and receive incoming cabins from others. The depot is the shared infrastructure that makes the whole regional system work.

In Git, the **remote** is the central depot. It is a repository hosted on a server — GitHub, GitLab, Bitbucket, or a self-hosted instance — that every team member connects to. You push cabins (commits) to it. Your colleagues pull cabins from it. The remote is the authoritative, shared version of the network.

-----

## 🗂️ SIPOC — The Remote Depot

|**Suppliers**                       |**Inputs**                      |**Process**                                                       |**Outputs**                                         |**Customers**                                       |
|------------------------------------|--------------------------------|------------------------------------------------------------------|----------------------------------------------------|----------------------------------------------------|
|You (developer)                     |Local commits on a branch       |`git push origin <branch>` — send cabins to the depot             |A remote-tracking branch updated at the depot       |Your colleagues, who can now pull your work         |
|The remote depot                    |New commits pushed by colleagues|`git fetch origin` — download new cabins without applying         |Remote-tracking refs updated locally (`origin/main`)|You, inspecting what arrived before applying        |
|The remote depot + your local branch|Remote + local state            |`git pull origin <branch>` — fetch + merge (or rebase) in one step|Your local branch updated with remote changes       |Your working session, now including colleagues’ work|
|A feature branch pushed to remote   |A pull request / merge request  |Code review → approve → merge                                     |Feature integrated into main at the depot           |The project; CI/CD pipeline; the release            |

-----

## Connecting to a Remote Depot 🔌

When you `git clone`, the remote is set up automatically. When you `git init`, you add it manually:

```bash
# Add a remote — convention names it 'origin'
git remote add origin https://github.com/yourname/my-project.git

# Verify the connection
git remote -v
# origin  https://github.com/yourname/my-project.git (fetch)
# origin  https://github.com/yourname/my-project.git (push)

# See detailed information about the remote
git remote show origin
```

**`origin`** is just a conventional name — the default alias for the primary remote. You can rename it or have multiple remotes. Forks typically add a second remote:

```bash
# Add the original repository as 'upstream' when working from a fork
git remote add upstream https://github.com/original-author/project.git

git remote -v
# origin    https://github.com/yourfork/project.git (fetch)
# origin    https://github.com/yourfork/project.git (push)
# upstream  https://github.com/original-author/project.git (fetch)
# upstream  https://github.com/original-author/project.git (push)
```

-----

## `git push` — Sending Cabins to the Depot 📤

```bash
# Push the current branch to origin
git push origin main

# First push of a new branch — set the upstream tracking relationship
git push -u origin feature-login
# (after -u, you can just run 'git push' with no arguments on this branch)

# Push all branches
git push --all origin
```

### What `git push` does

It uploads all local commits that the remote does not yet have, on the specified branch. The remote depot’s branch pointer moves forward to include your new cabins.

```bash
git log --oneline --graph --all
# * b2a1c34 (HEAD -> main, origin/main) Add logout function
# ← origin/main tracks what the depot last had
```

After a successful push, `origin/main` moves to match your local `main`. The depot and your local network are synchronised.

### What happens when you cannot push

If someone else pushed to the same branch since your last pull, Git refuses:

```bash
git push origin main
# ! [rejected]        main -> main (fetch first)
# error: failed to push some refs to 'origin'
# hint: Updates were rejected because the remote contains work that you do not have locally.
```

The depot has cabins you do not have yet. Fetch and integrate first:

```bash
git pull origin main    # get the depot's new cabins + merge
git push origin main    # now you can send
```

-----

## `git fetch` — Looking in the Depot Without Touching Your Lines 👁️

`git fetch` downloads new cabins and branch updates from the depot but does **not** apply them to your local branches. It updates only the remote-tracking refs (`origin/main`, `origin/feature-login`).

```bash
git fetch origin
# remote: Enumerating objects: 5, done.
# From https://github.com/yourname/my-project
#    f2d8a91..c3d4e56  main -> origin/main

# Now you can inspect what arrived without being forced to integrate it
git log --oneline --graph origin/main
# * c3d4e56 (origin/main) Maria's payment fix
# * f2d8a91 (HEAD -> main) Your last commit
```

`origin/main` is ahead of your local `main`. You can see the new cabins without any of your work being affected. When you are ready to integrate:

```bash
git merge origin/main    # or
git rebase origin/main
```

**When to use `git fetch` over `git pull`:**

- When you want to inspect what changed before integrating
- When you are in the middle of something and want to be aware of remote changes without disrupting your working directory
- Before a rebase — see what you are rebasing onto before the operation starts

-----

## `git pull` — Fetch and Integrate in One Step 📥

```bash
# Fetch from origin and merge into current branch
git pull origin main

# Fetch from origin and rebase current branch on top of remote (cleaner history)
git pull --rebase origin main
```

`git pull` is `git fetch` + `git merge` (or `git rebase` with `--rebase`). It is convenient for keeping your branch up to date. Some teams configure `pull.rebase=true` globally so all pulls rebase rather than merge:

```bash
git config --global pull.rebase true
```

### Keeping your feature branch updated

While you work on `feature-login`, `main` on the depot keeps getting new commits. Regularly update:

```bash
# Update your local main
git fetch origin
git switch main
git merge origin/main     # or: git pull origin main

# Bring main's new cabins into your feature branch
git switch feature-login
git rebase main           # replay your feature commits on top of updated main
```

-----

## `git clone` — Building a Local Copy of a Remote Network 📋

```bash
# Clone an entire repository (creates a local directory)
git clone https://github.com/example/project.git

# Clone into a specific directory name
git clone https://github.com/example/project.git my-local-project

# Clone a specific branch
git clone --branch feature-login https://github.com/example/project.git

# Shallow clone — only the most recent history (fast, for CI or large repos)
git clone --depth 1 https://github.com/example/project.git
```

After cloning, `origin` is automatically set to the URL you cloned from.

-----

## Pull Requests: The Review Junction 📋

A **pull request** (GitHub/Bitbucket) or **merge request** (GitLab) is not a Git command — it is a feature of the hosting platform built around Git. It is the formal process for requesting that the depot accept your spur line’s cabins onto the main trunk, with an opportunity for review before they arrive.

### The standard workflow

```bash
# 1. Start from an up-to-date main
git switch main
git pull origin main

# 2. Create a feature branch
git switch -c feature/user-authentication

# 3. Do the work — small, logical commits
echo "def authenticate(user, pw):" > src/auth.py
git add src/auth.py
git commit -m "Add authentication skeleton"

echo "    return db.verify(user, pw)" >> src/auth.py
git add src/auth.py
git commit -m "Implement database verification"

# 4. Before pushing, clean up if desired (interactive rebase, Episode 5)
git rebase -i HEAD~2   # optional: squash or reword

# 5. Push the branch to the depot
git push -u origin feature/user-authentication

# 6. Open a pull request on GitHub/GitLab (via web UI or CLI)
# gh pr create --title "Add user authentication" --body "Implements #123"
```

On GitHub, after `git push`, you will see a banner: “Compare & pull request”. Click it.

### What a pull request contains

- Your branch’s commits vs. `main` — the diff
- A description of what the change does and why
- A space for reviewers to comment on specific lines
- A CI/CD status panel (if configured — tests run automatically)
- Approval buttons, request-changes buttons
- A merge button (when approved)

### After the PR is merged

```bash
# Switch back to main and get the now-merged work
git switch main
git pull origin main

# Your feature branch is no longer needed
git branch -d feature/user-authentication
git push origin --delete feature/user-authentication
```

-----

## Remote-Tracking Branch Reference 📊

After `git fetch`, your local repo knows the remote’s state via **remote-tracking branches**:

```bash
# See all remote-tracking branches
git branch -r
# origin/main
# origin/feature-login
# origin/fix-payment-null

# See local and remote together
git branch -a
# * main
#   feature/user-authentication
#   remotes/origin/main
#   remotes/origin/feature-login

# How far ahead/behind is your local main vs. origin/main?
git status
# On branch main
# Your branch is ahead of 'origin/main' by 2 commits.
#   (use "git push" to publish your local commits)
```

-----

## A Day in the Life: The Full Remote Workflow 📅

```bash
# Morning: start fresh, get the latest
git switch main
git pull origin main

# Create your branch
git switch -c feature/add-export-csv

# Work...
git add .
git commit -m "Add CSV export to reports module"
git add .
git commit -m "Add tests for CSV export"

# Before pushing: update with anything new that landed on main
git fetch origin
git rebase origin/main    # replay my commits on top of latest main

# Push
git push -u origin feature/add-export-csv

# Open PR, get review, address comments:
git add .
git commit -m "Address review: handle empty dataset edge case"
git push origin feature/add-export-csv  # PR updates automatically

# After approval and merge on GitHub:
git switch main
git pull origin main           # get the merged work
git branch -d feature/add-export-csv    # clean up local
git push origin --delete feature/add-export-csv  # clean up remote
```

-----

In **Episode 8** — the final episode — the network has gone wrong. A commit was made in error. A branch was deleted by mistake. A rebase ate three commits. We cover `git reset`, `git revert`, `git cherry-pick`, and `git reflog` — the recovery tools that mean nothing is truly lost.

-----

**🔗 Resources**

- **`git remote` reference**: [git-scm.com/docs/git-remote](https://git-scm.com/docs/git-remote)
- **`git push` reference**: [git-scm.com/docs/git-push](https://git-scm.com/docs/git-push)
- **GitHub pull request documentation**: [docs.github.com/en/pull-requests](https://docs.github.com/en/pull-requests)
- **GitHub CLI** (`gh`): [cli.github.com](https://cli.github.com)

-----

*🚡 Cable Car Git! is a series about Git — explained through the metaphor of a cable car parcel transport network, where every commit is a cabin and every branch is a route.*
