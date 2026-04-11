-----

## title: “Cable Car Git! 🚡 Ep.8: Recovering Lost Parcels”
published: false
description: “Episode 8: Nothing is truly lost in Git. `git reset`, `git revert`, `git cherry-pick`, and `git reflog` — the recovery tools that let you undo disasters, retrieve orphaned cabins, and surgically move individual parcels between lines.”
tags: [git, intermediate, versioncontrol, tutorial]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/cable-car-git-episode-08.png”
series: “Cable Car Git!”
canonical_url: “”
organization: “the-software-s-journey”

# Cable Car Git! 🚡

## Episode 8: Recovering Lost Parcels

> *“The network keeps a log of every movement. Nothing is truly lost — only temporarily unreachable.”*

-----

## When Things Go Wrong 🔧

The cable car network is not infallible. Occasionally, a cabin is dispatched to the wrong line. A parcel that should have gone to the main trunk ends up on a dead spur. An emergency requires moving a single parcel from one line to another. A rushed `git push --force` on a shared branch causes chaos.

None of these are fatal. Git keeps records of every movement that has ever happened — not just the current commit graph, but the history of how you navigated it. Every cabin that was ever dispatched is stored until Git’s garbage collection reclaims it, which takes weeks at minimum.

This episode covers the four recovery tools that experienced Git users reach for when things go wrong.

-----

## 🗂️ SIPOC — Recovery Operations

|**Suppliers**                                 |**Inputs**                       |**Process**                                                 |**Outputs**                                                                         |**Customers**                                          |
|----------------------------------------------|---------------------------------|------------------------------------------------------------|------------------------------------------------------------------------------------|-------------------------------------------------------|
|A commit that should not have been dispatched |The number of commits to undo    |`git reset` — move the branch pointer backwards             |Branch at earlier state; commits either still in working tree, staging area, or gone|You, on a local branch, fixing a mistake before pushing|
|A commit on a shared branch that needs undoing|The commit hash to reverse       |`git revert` — dispatch a new cabin that inverts the bad one|A new commit that cancels the effect of the original; history preserved             |The team, without history rewrite                      |
|One useful commit on the wrong branch         |The commit hash to copy          |`git cherry-pick` — copy a single cabin to the current line |A new commit with the same changes, applied on the current branch                   |Any branch that needs that specific change             |
|A deleted branch or “lost” commit             |The reflog (Git’s movement diary)|`git reflog` — read the full navigation history             |A commit hash for the state you want to restore                                     |You, finding the needle in the haystack                |

-----

## `git reset` — Moving the Branch Pointer Back ↩️

`git reset` moves the current branch’s pointer to an earlier commit. It is the “I want to be back there” command. Three modes control what happens to the commits being undone:

```
                Working Dir    Staging Area    Commits
                ───────────    ────────────    ────────────
--soft          unchanged      unchanged       pointer moved back
--mixed         unchanged      cleared         pointer moved back  (DEFAULT)
--hard          cleared        cleared         pointer moved back
```

Think of it in terms of the cable car:

- `--soft`: the cabin is un-dispatched, but the parcels are still on the loading platform (staged)
- `--mixed`: the cabin is un-dispatched, the parcels are back on the warehouse floor (unstaged)
- `--hard`: the cabin is un-dispatched and the parcels are gone from the station entirely

```bash
# Situation: you made 3 commits that should be 1 clean commit

git log --oneline
# c3d4e56 (HEAD) Fix typo
# b2a1c34 Add logout function
# 9d3f0a1 Add login function
# a1b2c3d Add README (the good starting point)

# Undo the last 3 commits — keep changes staged (--soft)
git reset --soft HEAD~3

git log --oneline
# a1b2c3d (HEAD) Add README

git status
# Changes to be committed:
#   modified: src/auth.py   ← all 3 commits' changes, back on the platform

# Now make one clean commit
git commit -m "Add login and logout with session management"
```

```bash
# --mixed (default): undo commit, keep files but unstage them
git reset HEAD~1
# or equivalently: git reset --mixed HEAD~1

# --hard: undo commit AND discard all changes (destructive — use carefully)
git reset --hard HEAD~1
```

### ⚠️ Critical rule: never `git reset` on shared branches

`git reset` rewrites history — it moves the branch pointer to an earlier commit, making later commits unreachable via that branch name. If those commits were already pushed to the remote and colleagues have pulled them, you will create chaos. Their local history will diverge from yours.

**`git reset` is safe for local, unpushed commits only.** For shared branches, use `git revert`.

-----

## `git revert` — The Corrective Cabin 🔄

`git revert` does not move the branch pointer back. Instead, it creates a **new cabin** whose changes are the exact inverse of the commit you are reverting. The original bad commit stays in history. The new commit cancels its effect.

```
Before revert:

  A --- B --- C (bad) --- D   ← main

After git revert C:

  A --- B --- C (bad) --- D --- C' (reverts C)   ← main
```

```bash
# Revert a specific commit (creates a new commit immediately)
git revert b2a1c34
# (editor opens for the revert commit message — accept or edit)

# Revert without immediately committing (allows editing before committing)
git revert --no-commit b2a1c34
# (makes the inverted changes in your working directory — you review and commit manually)

# Revert a range of commits (most recent first)
git revert HEAD~3..HEAD
```

`git revert` is the safe option for shared branches. It preserves the full history (including the mistake and its correction) and can be pushed normally. Code reviewers can see exactly what happened and why.

-----

## `git cherry-pick` — Moving a Single Parcel 🍒

`git cherry-pick` copies a specific commit from any branch and applies it to the current branch. The original commit is untouched; a new commit with the same changes (but a different SHA-1) appears on the current branch.

**When you need it:** A colleague fixed a critical bug on `feature/payment-fix` but it has not been merged to `main` yet, and you need that fix on your own branch immediately.

```bash
# Find the commit you need
git log --oneline feature/payment-fix
# d9e8f7a Fix null currency default — this is the one you want
# c6b5a4d Add multi-currency support
# b3c2d1e Remove old payment module

# Apply only that commit to your current branch
git switch main
git cherry-pick d9e8f7a
# [main g4h5i67] Fix null currency default
# 1 file changed, 2 insertions(+), 1 deletion(-)
```

A new commit `g4h5i67` appears on `main` with the same changes as `d9e8f7a`. The original `d9e8f7a` on `feature/payment-fix` is unchanged.

### Cherry-picking a range

```bash
# Apply a range of commits (inclusive on both ends)
git cherry-pick d9e8f7a..c6b5a4d

# Apply multiple specific commits
git cherry-pick d9e8f7a c6b5a4d
```

### When cherry-pick conflicts

```bash
# Cherry-pick pauses if there is a conflict
git cherry-pick d9e8f7a
# CONFLICT in src/payment.py

# Resolve the conflict, then:
git add src/payment.py
git cherry-pick --continue

# Or abandon the cherry-pick:
git cherry-pick --abort
```

-----

## `git reflog` — The Network’s Movement Diary 📔

`git reflog` is Git’s private movement diary — a record of every time `HEAD` moved, regardless of whether the move was a commit, a checkout, a reset, a rebase, or anything else. It is the tool of last resort when you believe something is irretrievably lost.

Commits that are no longer reachable via any branch still appear in the reflog until Git’s garbage collector runs (at least 30 days by default for unreachable objects, 90 days for reachable ones).

```bash
git reflog
# g4h5i67 (HEAD -> main) HEAD@{0}: cherry-pick: Fix null currency default
# f2d8a91 HEAD@{1}: checkout: moving from feature-login to main
# b2a1c34 HEAD@{2}: commit: Add logout function
# 9d3f0a1 HEAD@{3}: commit: Add login function
# f2d8a91 HEAD@{4}: checkout: moving from main to feature-login
# f2d8a91 HEAD@{5}: reset: moving to HEAD~2   ← a reset that happened
# c3d4e56 HEAD@{6}: commit: the commit that was reset away
```

### Recovering a “deleted” branch

You deleted a branch by accident before merging it:

```bash
git branch -D feature-login   # oops
```

Find the tip commit using reflog:

```bash
git reflog
# b2a1c34 HEAD@{2}: commit: Add logout function   ← this was the tip of feature-login

# Recreate the branch pointing to that commit
git branch feature-login b2a1c34
```

The branch is restored. All its cabins are back on the network.

### Recovering from a bad `--hard` reset

```bash
# You ran: git reset --hard HEAD~3 (lost 3 commits)
# The 3 commits still exist in the reflog

git reflog
# a1b2c3d HEAD@{0}: reset: moving to HEAD~3
# c3d4e56 HEAD@{1}: commit: the most recent lost commit

# Get back to where you were
git reset --hard c3d4e56
```

### Recovering from a bad rebase

Interactive rebase gone wrong — you dropped a commit you needed:

```bash
git reflog
# a1b2c3d HEAD@{0}: rebase (finish): ...
# f1e2d3c HEAD@{4}: commit: the commit you accidentally dropped

git cherry-pick f1e2d3c   # bring it back
```

-----

## `git diff` and `git show` for Forensic Investigation 🔬

Before any recovery operation, investigate:

```bash
# What did a specific commit change?
git show b2a1c34

# What is different between two commits?
git diff 9d3f0a1..b2a1c34

# What changed between a branch and main?
git diff main..feature-login

# Who last modified each line of a file?
git blame src/auth.py
# b2a1c34 (Ahmed        2026-04-08 09:30:00 +0200  1) def login(user, password):
# 9d3f0a1 (Ahmed        2026-04-08 09:00:00 +0200  2)     return verify(user, password)
```

`git blame` is invaluable for understanding why a line is the way it is and who to ask about changing it.

-----

## The Full Recovery Toolkit: Decision Guide 🗺️

```
What went wrong?
│
├── "I committed something I should not have — not pushed yet"
│   → git reset (soft/mixed/hard depending on whether you want the changes)
│
├── "I committed something I should not have — already pushed to shared branch"
│   → git revert (creates a corrective commit — safe for shared history)
│
├── "I need one specific commit from another branch, but not the whole branch"
│   → git cherry-pick <commit-hash>
│
├── "I deleted a branch by mistake"
│   → git reflog → find the tip hash → git branch <name> <hash>
│
├── "I ran git reset --hard and lost commits"
│   → git reflog → find the hash → git reset --hard <hash>
│
├── "A rebase went wrong and ate my commits"
│   → git reflog → find pre-rebase hash → git reset --hard ORIG_HEAD
│   (Git saves ORIG_HEAD before risky operations like rebase and merge)
│
└── "I have no idea what happened"
    → git reflog (read the full movement diary — it will be there)
```

-----

## The Series Complete: The Full Network Map 🗺️

Eight episodes. Here is the full cable car / Git mapping:

|Cable car concept                |Git concept                |Episode|
|---------------------------------|---------------------------|-------|
|The network                      |The repository (`.git/`)   |1      |
|A parcel                         |A file change              |1      |
|A cabin                          |A commit                   |1, 2   |
|The loading platform             |The staging area           |2      |
|Dispatching a cabin              |`git commit`               |2      |
|The dispatch ledger              |`git log`                  |2      |
|A spur line                      |A branch                   |3      |
|Building a new line              |`git branch` + `git switch`|3      |
|Two lines joining                |`git merge`                |4      |
|A smooth junction                |Fast-forward merge         |4      |
|A junction cabin                 |Merge commit               |4      |
|Conflict at junction             |Merge conflict             |4      |
|Replaying the route              |`git rebase`               |5      |
|Editing the route                |Interactive rebase         |5      |
|The holding locker               |`git stash`                |6      |
|The locker stack                 |Stash list                 |6      |
|The central depot                |The remote                 |7      |
|Sending cabins to depot          |`git push`                 |7      |
|Receiving from depot             |`git pull` / `git fetch`   |7      |
|The review junction              |Pull request               |7      |
|Moving the pointer back          |`git reset`                |8      |
|A corrective cabin               |`git revert`               |8      |
|Copying one cabin to another line|`git cherry-pick`          |8      |
|The movement diary               |`git reflog`               |8      |

The network is yours. The cabins are all accounted for. Nothing is lost.

-----

**🔗 Resources**

- **`git reset` reference**: [git-scm.com/docs/git-reset](https://git-scm.com/docs/git-reset)
- **`git revert` reference**: [git-scm.com/docs/git-revert](https://git-scm.com/docs/git-revert)
- **`git cherry-pick` reference**: [git-scm.com/docs/git-cherry-pick](https://git-scm.com/docs/git-cherry-pick)
- **`git reflog` reference**: [git-scm.com/docs/git-reflog](https://git-scm.com/docs/git-reflog)
- **Oh Shit Git** (quick recovery reference): [ohshitgit.com](https://ohshitgit.com)

-----

*🚡 Cable Car Git! is a series about Git — explained through the metaphor of a cable car parcel transport network, where every commit is a cabin and every branch is a route. Thank you for riding the network.*
