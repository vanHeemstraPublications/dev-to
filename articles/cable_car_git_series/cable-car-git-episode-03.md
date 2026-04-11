---
title: "Cable Car Git! 🚡 Ep.3"
part: 3
published: false
description: "Episode 3: Branches are the spur lines that let two teams transport parcels in parallel without collisions. `git branch`, `git switch`, `git checkout` — build a new route, work in isolation, then prepare to merge."
tags: [git, beginners, versioncontrol, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/cable-car-git-episode-03.png"
series: "Cable Car Git Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: Building New Lines

> *“Two teams. Two routes. Same mountain. Zero collisions.”*

-----

## The Problem With One Line 🚧

In Episode 2, everything dispatched down a single main line. That works for solo development. It breaks down the moment two people work on the same project simultaneously.

Ahmed is building a login feature. Maria is fixing a critical bug in the payment processor. If they both commit to `main`:

- Ahmed’s unfinished login code might break Maria’s bug fix
- Maria might accidentally include Ahmed’s incomplete work in the hotfix release
- Neither can ship independently — they are entangled

The cable car network has a solution for this. It has always had it. You build a **spur line** — a separate route that branches off from the main trunk at a specific point, carries its own cabins independently, and joins back later when the work is ready.

In Git, spur lines are **branches**.

-----

## 🗂️ SIPOC — Building a New Line

|**Suppliers**               |**Inputs**                                  |**Process**                                   |**Outputs**                                         |**Customers**                                        |
|----------------------------|--------------------------------------------|----------------------------------------------|----------------------------------------------------|-----------------------------------------------------|
|The existing main line      |A point in the commit history to branch from|`git branch <name>` — create the spur line    |A new branch pointer at the current commit          |Developers who will work on this branch independently|
|You (developer)             |A branch name                               |`git switch <name>` (or `git checkout <name>`)|HEAD now points to the new line; new commits go here|Your feature, not touching main until you say so     |
|The feature branch + commits|Completed work ready to integrate           |`git merge <branch>` (Episode 4)              |The spur line’s cabins joined back to the main trunk|The team, deployment pipeline, other developers      |

-----

## What Is a Branch, Actually? 🤔

This is the most important thing to understand, and it is surprisingly simple.

A **branch is just a pointer to a commit** — a lightweight label that says “this is the tip of this line.” When you create a branch, Git creates a new pointer. When you commit on a branch, the pointer moves forward to your new cabin.

That’s it. A branch is a 41-byte file containing a commit hash. Creating a branch is instant. Switching branches is instant. Branches in Git are not copies of the codebase — they are labels pointing to nodes in the commit graph.

```
Before branching:

  A --- B --- C   ← main (HEAD)

After git branch feature-login:

  A --- B --- C   ← main
              ↑
              └── ← feature-login (HEAD still on main)

After git switch feature-login AND git commit D:

  A --- B --- C         ← main
              \
               D        ← feature-login (HEAD)
```

`HEAD` is the pointer that says “I am here.” When you switch branches, HEAD moves. When you commit, the branch HEAD is pointing to moves forward.

-----

## `git branch` — Creating and Listing Lines 📋

```bash
# List all branches (current branch marked with *)
git branch
# * main

# Create a new branch (does not switch to it yet)
git branch feature-login

git branch
# * main
#   feature-login

# Create AND switch to the new branch in one step (preferred)
git switch -c feature-login
# (or the older syntax: git checkout -b feature-login)
# Switched to a new branch 'feature-login'

# List all branches including remote-tracking branches
git branch -a
# * feature-login
#   main
#   remotes/origin/main
```

-----

## `git switch` — Changing Lines 🔄

```bash
# Switch to the main line
git switch main
# Switched to branch 'main'

# Switch back to the feature line
git switch feature-login
# Switched to branch 'feature-login'
```

When you switch branches, Git:

1. Updates every tracked file in your working directory to match the state of the new branch’s tip commit
1. Moves HEAD to point to the new branch

This is why Git warns you if you have uncommitted changes when switching — it cannot safely swap out your files if you have unsaved work. The solution for that situation is Episode 6 (`git stash`). For now, always commit or stash before switching.

### `git switch` vs `git checkout`

You will see both in documentation and tutorials. `git checkout` is the older command that does too many things (switches branches *and* restores files). `git switch` was introduced in Git 2.23 (2019) to be explicit. Use `git switch` for branch operations. Both work; `git switch` is clearer.

-----

## Working on a Feature Branch: The Full Cycle 🏗️

Let’s trace Ahmed building the login feature on a dedicated branch:

```bash
# Ahmed starts from an up-to-date main
git switch main
git pull origin main          # Get latest from the depot (Episode 7)

# Build the feature line off the current main tip
git switch -c feature-login

# Now Ahmed works — main is untouched
echo "def login(user, password):" > src/auth.py
echo "    return verify(user, password)" >> src/auth.py
git add src/auth.py
git commit -m "Add login function"

# More work on the feature
echo "def logout(session_id):" >> src/auth.py
echo "    return invalidate_session(session_id)" >> src/auth.py
git add src/auth.py
git commit -m "Add logout function"

# Check the network map
git log --oneline --graph --all
# * b2a1c34 (HEAD -> feature-login) Add logout function
# * 9d3f0a1 Add login function
# * f2d8a91 (main) Add project configuration
# * b1c3e47 Add authentication skeleton
# * a3f9c12 Add README
```

The main line is at `f2d8a91`. Ahmed’s feature line has two new cabins (`9d3f0a1` and `b2a1c34`) that main does not have. Maria can work on `main` (or her own branch) without any knowledge of or interference from Ahmed’s work.

-----

## Meanwhile, Maria Fixes a Bug 🐛

While Ahmed works on `feature-login`, Maria is on her own branch:

```bash
# Maria starts her own branch from main
git switch main
git switch -c fix-payment-null

# She finds and fixes the bug
echo "def charge(amount, currency='EUR'):" > src/payment.py
git add src/payment.py
git commit -m "Fix null currency default in charge function"

git log --oneline --graph --all
# * c4e2d89 (HEAD -> fix-payment-null) Fix null currency default in charge function
# | * b2a1c34 (feature-login) Add logout function
# | * 9d3f0a1 Add login function
# |/
# * f2d8a91 (main) Add project configuration
# * b1c3e47 Add authentication skeleton
# * a3f9c12 Add README
```

Now the network map shows three lines: `main`, `feature-login`, and `fix-payment-null`. They all branched from `f2d8a91`. They are completely independent. Cabins on one line do not affect the others.

-----

## Branch Naming Conventions 📛

Good branch names make the network map readable:

```bash
# Feature work
feature/user-authentication
feature/payment-refactor
feat/dark-mode               # shorter prefix

# Bug fixes
fix/null-currency-bug
bugfix/login-timeout
hotfix/critical-payment-error   # for urgent production fixes

# Chores, refactoring, documentation
chore/update-dependencies
refactor/payment-service
docs/api-documentation

# Releases
release/v2.1.0
```

The `/` creates a visual hierarchy in Git GUIs and helps `git branch --list "feature/*"` filter groups of branches.

-----

## Deleting a Branch 🗑️

Once a branch has been merged (Episode 4), the pointer is no longer needed. The cabins still exist in history — they are just accessed via main now.

```bash
# Delete a merged branch (safe — warns you if not merged)
git branch -d feature-login

# Force-delete an unmerged branch (use carefully — the work is not lost
# immediately, but will become unreachable via branch name)
git branch -D feature-login-abandoned

# Delete a remote-tracking branch
git push origin --delete feature-login
```

Regularly deleting merged branches keeps the network map readable. A repository with 50 stale branches is hard to navigate.

-----

## Viewing the Network Map 🗺️

```bash
# All branches, one line each, with the visual graph
git log --oneline --graph --all

# Current branch only
git log --oneline --graph

# List branches with their last commit
git branch -v
# * feature-login  b2a1c34 Add logout function
#   main           f2d8a91 Add project configuration
```

The graph output will grow more interesting in Episode 4 when branches start merging. For now, get comfortable reading it — it is the most important diagnostic tool in Git.

-----

## Practical Branch Hygiene ✅

A few rules that prevent problems:

**Never commit directly to `main` on a shared project.** Main is the trunk line. Finished work arrives there via merges, not direct dispatch.

**Keep branches short-lived.** A branch that exists for three days is easy to merge. A branch that exists for three months will have hundreds of conflicts when it finally tries to rejoin the trunk. Build small, merge often.

**Name branches after the ticket or task they implement.** `feature/auth-123` links directly to issue #123. A year from now, someone reading `git log` will be grateful.

**One concern per branch.** Do not mix a bug fix and a new feature on the same branch. If they need to be merged separately (bug fix to production today, feature next sprint), you want them on separate lines.

-----

In **Episode 4**, the spur lines come home. We cover how two lines rejoin at the junction — fast-forward merges, merge commits, and what to do when two lines’ parcels conflict at the junction.

-----

**🔗 Resources**

- **`git branch` reference**: [git-scm.com/docs/git-branch](https://git-scm.com/docs/git-branch)
- **`git switch` reference**: [git-scm.com/docs/git-switch](https://git-scm.com/docs/git-switch)
- **Interactive branch visualiser**: [learngitbranching.js.org](https://learngitbranching.js.org)

-----

*🚡 Cable Car Git! is a series about Git — explained through the metaphor of a cable car parcel transport network, where every commit is a cabin and every branch is a route.*
