---
title: "Cable Car Git! 🚡 Ep.6"
part: 6
published: false
description: "Episode 6: The command you are probably underusing. git stash temporarily stores your unfinished parcels in a secure locker so you can switch lines, handle emergencies, and come back exactly where you left off — with every advanced trick explained."
tags: [git, beginners, versioncontrol, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/cable-car-git-episode-06.png"
series: "Cable Car Git Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 6: The Holding Locker

> *“You’re mid-dispatch. An urgent parcel arrives. You need your hands free. Use the locker.”*

-----

## The Interruption Nobody Plans For 🚨

You are deep into the feature branch. Three files modified. An API refactor half done. `git status` shows eight changes, none of them ready to commit as a coherent unit.

Your manager pings: “Critical bug in production. Drop everything.”

You need to switch to `main`, create a hotfix branch, and fix the bug now. But you cannot commit your half-finished work — it would not even run. You cannot abandon it — it represents three hours of careful refactoring. You need your hands free for the emergency, and you need to come back to exactly this point when it is over.

Every cable car station has a **holding locker** — a secure storage space for parcels that are not ready to be dispatched but cannot be left on the open platform. You seal them into the locker, handle the emergency, and retrieve them when you are back.

In Git, the holding locker is `git stash`.

-----

## 🗂️ SIPOC — The Holding Locker

|**Suppliers**              |**Inputs**                               |**Process**                                                                  |**Outputs**                                                            |**Customers**                                               |
|---------------------------|-----------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------|------------------------------------------------------------|
|You (interrupted developer)|Uncommitted changes (staged and unstaged)|`git stash` — seals current changes into the locker, cleans working directory|A stash entry (`stash@{0}`) on the stash stack; clean working directory|You, on a different branch, handling the interruption       |
|The stash stack            |One or more stash entries                |`git stash list` — inspect all locker entries                                |A numbered list: `stash@{0}` (most recent), `stash@{1}`, etc.          |You, deciding which entry to retrieve                       |
|A stash entry              |The entry reference (`stash@{n}`)        |`git stash pop` or `git stash apply`                                         |Changes restored to working directory; locker entry optionally deleted |You, back on your feature branch, exactly where you left off|

-----

## The Basic Locker Operations 🔐

### Putting things in the locker

```bash
# You are mid-feature, working on feature/api-refactor
git status
# On branch feature/api-refactor
# Changes to be committed:
#   modified: src/api/client.py
# Changes not staged for commit:
#   modified: src/api/response.py
#   modified: tests/test_api.py

# Emergency arrives. Seal everything into the locker.
git stash
# Saved working directory and index state WIP on feature/api-refactor: f2d8a91 Add project configuration

git status
# On branch feature/api-refactor
# nothing to commit, working tree clean
```

The working directory is now clean. Three modified files are safely in the locker. You are free to switch branches.

```bash
# Handle the emergency on a clean branch
git switch main
git switch -c hotfix/payment-crash
# ... fix the bug, commit, merge, done ...

# Come back to your feature
git switch feature/api-refactor

# Retrieve the locker contents
git stash pop
# On branch feature/api-refactor
# Changes to be committed:
#   modified: src/api/client.py
# Changes not staged for commit:
#   modified: src/api/response.py
#   modified: tests/test_api.py
# Dropped refs/stash@{0} (abc1234...)
```

`git stash pop` retrieves the most recent stash entry and removes it from the locker. You are back exactly where you were — staged files still staged, unstaged files still unstaged.

-----

## The Locker Stack: Multiple Entries 📚

The stash is a **stack** — last in, first out, like a pile of parcels. You can push multiple entries and retrieve them by index.

```bash
# First stash — mid-API refactor
git stash -m "WIP: API client refactor, response parsing half done"
# stash@{0}: On feature/api-refactor: WIP: API client refactor...

# Switch to another branch, do some work, need to stash again
git switch feature/dark-mode
# ... start some work ...
git stash -m "WIP: dark mode toggle, CSS variables not wired yet"
# stash@{0}: On feature/dark-mode: WIP: dark mode toggle...
# stash@{1}: On feature/api-refactor: WIP: API client refactor...
```

Now the locker has two entries. The most recent is always `stash@{0}`:

```bash
git stash list
# stash@{0}: On feature/dark-mode: WIP: dark mode toggle, CSS variables not wired yet
# stash@{1}: On feature/api-refactor: WIP: API client refactor, response parsing half done
```

### Retrieving a specific entry

```bash
# Retrieve the API refactor stash (entry 1), not the most recent
git stash apply stash@{1}
# (applies the stash but does NOT remove it from the list)

# Retrieve AND remove entry 1
git stash pop stash@{1}
```

### `apply` vs. `pop`: the difference

|Command          |Retrieves changes|Removes from locker    |
|-----------------|-----------------|-----------------------|
|`git stash pop`  |✅                |✅ (removes `stash@{0}`)|
|`git stash apply`|✅                |❌ (keeps in locker)    |

Use `apply` when you want to apply the same stash to multiple branches (e.g., porting a partial change to a different base). Use `pop` for normal single-use retrieval.

-----

## Naming Your Locker Entries 🏷️

The default stash message — “WIP on branch-name: commit-hash commit-message” — is technically correct but archaeologically useless three days later. Always name your stashes:

```bash
# With -m flag
git stash -m "WIP: auth refactor, JWT validation half complete"

# With push subcommand (modern syntax, also accepts -m)
git stash push -m "WIP: dark mode toggle, needs CSS variable mapping"
```

Named stashes make `git stash list` readable:

```bash
git stash list
# stash@{0}: On feature/dark-mode: WIP: dark mode toggle, needs CSS variable mapping
# stash@{1}: On feature/api-refactor: WIP: auth refactor, JWT validation half complete
# stash@{2}: WIP on main: payment crash investigation notes
```

This is the most underused practice in git stash. Name every stash. Your future self will thank you.

-----

## Inspecting the Locker Without Retrieving 🔍

Before opening the locker, check what is inside:

```bash
# See a summary of what files are in the most recent stash
git stash show
# src/api/client.py     | 23 ++++++++++++++++++-----
# src/api/response.py   |  8 +++++---
# tests/test_api.py     | 15 +++++++++++++++
# 3 files changed, 38 insertions(+), 8 deletions(-)

# See the full diff of the most recent stash
git stash show -p

# See the full diff of a specific stash
git stash show -p stash@{1}
```

-----

## Advanced Stash Options 🛠️

### Stashing untracked files (`-u`)

By default, `git stash` only stashes changes to **tracked** files — files Git already knows about. Brand-new files you have created but never `git add`-ed are left on the warehouse floor.

```bash
# You created a new file during your work
touch src/api/retry_handler.py   # new, untracked

git stash
# Saved working directory and index state WIP on...
# (but retry_handler.py is still there — not stashed!)

git status
# Untracked files:
#   src/api/retry_handler.py   ← still here

# Use -u (or --include-untracked) to stash new files too
git stash -u
# Saved working directory and index state WIP on...

git status
# nothing to commit, working tree clean   ← retry_handler.py is now in the locker
```

### Stashing everything including ignored files (`-a`)

```bash
# --all: stashes tracked changes, untracked files, AND ignored files
# (use rarely — ignored files are usually build artifacts and should stay)
git stash --all
```

### Stashing only specific files

```bash
# Stash only the changes to src/api/client.py
git stash push -m "WIP: client timeout logic" -- src/api/client.py

# Stash changes across a directory
git stash push -m "WIP: response module refactor" -- src/api/
```

This is powerful for splitting your work: stash the changes you are not ready for, commit the changes you are, then retrieve the stash.

### Stashing only staged changes (`--staged`)

```bash
# You have staged some changes (ready to commit) and unstaged changes (not ready)
git status
# Changes to be committed:
#   modified: src/api/client.py   ← ready
# Changes not staged for commit:
#   modified: src/api/response.py ← not ready

# Stash ONLY the staged changes — keep the unstaged changes in working directory
git stash --staged -m "Staged client.py changes"

# Now only the unstaged response.py changes remain
git status
# Changes not staged for commit:
#   modified: src/api/response.py
```

### Interactive partial stash (`-p`)

```bash
# Choose exactly which hunks of which files to stash, interactively
git stash -p
# Asks for each changed section: stash this hunk? (y/n/q/a/?)
```

This combines the precision of `git add -p` with stash — you can stash half a file’s changes.

-----

## Creating a Branch From a Stash 🌿

Sometimes you realise your stashed work has grown complex enough to warrant its own branch. Instead of popping to the current branch and then creating a new one, `git stash branch` does both:

```bash
# Create a new branch from the state when you stashed,
# apply the stash, and remove the locker entry
git stash branch feature/api-retry-logic stash@{1}
# Switched to a new branch 'feature/api-retry-logic'
# On branch feature/api-retry-logic
# Changes not staged for commit:
#   modified: src/api/client.py
#   modified: src/api/response.py
# Dropped refs/stash@{1}
```

The new branch is created starting from the commit that was HEAD when you stashed. This is exactly the right base — the stashed changes apply cleanly because the branch and the stash share the same starting point.

-----

## Cleaning the Locker 🧹

Stash entries accumulate. An old `stash@{7}` with no label is a mystery. Clean up regularly:

```bash
# Delete a specific stash entry
git stash drop stash@{1}
# Dropped stash@{1} (abc1234...)

# Delete ALL stash entries (irreversible — there is no undo)
git stash clear
```

Use `git stash clear` cautiously. Dropped stash entries are not immediately gone — for a short window they are still in the reflog and recoverable (Episode 8). But after the reflog expires (default: 90 days for reachable, 30 days for unreachable), they are truly gone.

-----

## The Five Stash Habits That Change Everything 🏆

These are the practices that elevate `git stash` from “emergency only” to daily workflow tool:

**1. Always name your stashes.** `git stash -m "WIP: ..."` takes two seconds. The alternative — `stash@{4}` with no context — costs minutes when you come back cold.

**2. Use `-u` when you have new files.** If you created files during your work session, a plain `git stash` silently leaves them behind. You will switch branches and find them still there, polluting your clean working directory.

**3. Use partial stashing to separate concerns.** If you accidentally mixed two concerns (a bug fix and a feature) in the same working session, `git stash push -- <files>` lets you stash one concern, commit the other, then retrieve the stash.

**4. Inspect before popping.** `git stash show -p stash@{n}` lets you see what you are about to retrieve. Especially useful when you have multiple stash entries.

**5. Clean old stashes regularly.** A stash list longer than five entries is a red flag that work is being deferred rather than completed. Review and either commit, branch, or drop.

-----

## Common Gotchas ⚠️

**Conflict when popping:** If `main` has changed significantly since you stashed, `git stash pop` may produce conflicts. Resolve them exactly as you would a merge conflict: edit the files, `git add` them, then `git commit` (for apply) or `git reset` (if pop partially applied).

**Stash is local:** Like branches, stash entries are not transferred by `git push`. They exist only on your machine. If you move to a different machine or reinstall, the stash is gone.

**Branch switching with an incompatible stash:** If a stash contains changes that conflict with the target branch, `git stash pop` will fail. Use `git stash apply` — it leaves the stash entry in place so you can inspect and clean up the conflict without losing the stash.

**`git stash save` is deprecated:** Older tutorials use `git stash save "message"`. Prefer `git stash push -m "message"` — it is the current syntax and supports path filtering.

-----

In **Episode 7**, the parcels travel further — to the central depot (the remote). `git remote`, `git push`, `git pull`, `git fetch`, and the pull request workflow.

-----

**🔗 Resources**

- **`git stash` reference**: [git-scm.com/docs/git-stash](https://git-scm.com/docs/git-stash)
- **Atlassian stash guide**: [atlassian.com/git/tutorials/saving-changes/git-stash](https://www.atlassian.com/git/tutorials/saving-changes/git-stash)
- **Source article**: [Git Stash: The Command You’re Probably Underusing](https://blog.stackademic.com/git-stash-the-command-youre-probably-underusing-354e963bd2f0)

-----

*🚡 Cable Car Git! is a series about Git — explained through the metaphor of a cable car parcel transport network, where every commit is a cabin and every branch is a route.*
