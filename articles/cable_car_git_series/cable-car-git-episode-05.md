---
title: "Cable Car Git! 🚡 Ep.5"
part: 5
published: false
description: "Episode 5: Rebase moves a spur line’s cabins to a new starting point on the trunk — creating a clean, linear history without merge commits. Interactive rebase lets you rewrite, squash, and reorder cabins before they arrive."
tags: [git, intermediate, versioncontrol, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/cable-car-git-episode-05.png"
series: "Cable Car Git Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 5: Replaying the Route

> *“The cabins are real. But the route they took can be rewritten.”*

-----

## The Junction’s Alternative 🔀

In Episode 4, we built junctions — merge commits that join two lines into a V-shaped convergence. They faithfully record that two parallel lines ran simultaneously and met at a specific point.

But sometimes you do not want the V-shape. You want the spur line’s cabins to appear as if they were always part of the main trunk — dispatched one after another from the latest main-line cabin, in a perfectly linear sequence.

The physical cable car equivalent: disassembling the spur line’s cabins, moving the entire track to start from the new tip of the main trunk, and re-dispatching the cabins from there. The parcels inside are identical. The route is different.

This is `git rebase`.

-----

## 🗂️ SIPOC — Replaying the Route

|**Suppliers**                |**Inputs**                                        |**Process**                                     |**Outputs**                                            |**Customers**                                          |
|-----------------------------|--------------------------------------------------|------------------------------------------------|-------------------------------------------------------|-------------------------------------------------------|
|A feature branch with commits|The current tip of `main` (the new starting point)|`git rebase main` — replay commits onto new base|New commits with new SHAs, same changes, linear history|A fast-forward merge from main — no merge commit needed|
|A messy local branch history |The last N commits to rewrite                     |`git rebase -i HEAD~N` — interactive rebase     |Reordered, squashed, reworded, or dropped commits      |A clean pull request that tells a coherent story       |

-----

## What Rebase Does Mechanically 🔧

```
Before rebase:

  A --- B --- C --- F        ← main (tip at F)
              \
               D --- E       ← feature-login (branched from C)

git rebase main (run from feature-login):

  A --- B --- C --- F        ← main
                    \
                     D' --- E'   ← feature-login (new base at F)
```

`D'` and `E'` are **new commits** — they have the same changes as `D` and `E` but different SHA-1 hashes, because their parent has changed. Git took the diff of each commit and replayed it on top of `F`.

The old `D` and `E` are now orphaned — no branch pointer references them. They will eventually be garbage-collected.

```bash
git switch feature-login

# Before: feature branches from C, main is now at F
git log --oneline --graph --all
# * f2d8c91 (main) Add changelog
# | * b2a1c34 (HEAD -> feature-login) Add logout function
# | * 9d3f0a1 Add login function
# |/
# * f2d8a91 Add project configuration

# Rebase: replay feature-login commits on top of current main
git rebase main
# Successfully rebased and updated refs/heads/feature-login.

git log --oneline --graph --all
# * e7a3b12 (HEAD -> feature-login) Add logout function
# * d6c2a01 Add login function
# * f2d8c91 (main) Add changelog
# * f2d8a91 Add project configuration
```

Now `feature-login` sits cleanly on top of `main`. No branches in the graph. A fast-forward merge from main is now possible:

```bash
git switch main
git merge feature-login       # fast-forward — no merge commit
# Updating f2d8c91..e7a3b12
# Fast-forward
```

The network map stays linear.

-----

## Rebase vs. Merge: The Trade-off ⚖️

This is not a question with a universal answer. Both are correct tools for different situations.

|                             |Merge                                                                       |Rebase                                                                    |
|-----------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------|
|**What it preserves**        |The true parallel history — shows that two people worked simultaneously     |A linear story — shows the changes in logical sequence                    |
|**Junction cabin**           |Creates a merge commit (explicit record of the join)                        |No merge commit (fast-forward after rebase)                               |
|**History**                  |Truthful but branchy — `git log --graph` shows diamonds                     |Clean and linear — `git log` reads like a story                           |
|**SHA-1 hashes**             |Original commits unchanged                                                  |Creates new commits with new hashes                                       |
|**Safety on shared branches**|Always safe — never rewrites history                                        |Dangerous — rewrites history, breaks other developers’ copies             |
|**Best for**                 |Shared branches, preserving contributor records, long-lived feature branches|Private local branches, cleaning up before PR, keeping a tidy main history|

**The golden rule of rebasing:** Never rebase commits that exist on a shared remote branch that others have pulled. Rewriting shared history orphans your colleagues’ work and creates reconciliation nightmares. Rebase is safe on your local, unpushed feature branches. It is dangerous on anything public.

-----

## Handling Conflicts During Rebase 🚧

Rebase conflicts work like merge conflicts — but they happen one commit at a time. Git replays each commit in sequence and stops when a conflict occurs.

```bash
git rebase main
# Auto-merging src/auth.py
# CONFLICT (content): Merge conflict in src/auth.py
# error: could not apply 9d3f0a1... Add login function
# hint: Resolve all conflicts manually, mark them as resolved with
# hint: "git add/rm <conflicted_files>", then run "git rebase --continue".
# hint: You can instead skip this commit: run "git rebase --skip".
# hint: To abort and get back to the state before "git rebase": run "git rebase --abort".
```

```bash
# 1. Resolve the conflict in src/auth.py (same as merge conflict resolution)
# 2. Stage the resolution
git add src/auth.py

# 3. Continue replaying the next commit
git rebase --continue

# If a commit's changes become empty after resolution (conflict resolved by deleting them):
git rebase --skip

# Abort entirely — return to state before rebase started
git rebase --abort
```

A rebase with many commits can create a sequence of conflict-resolution steps — one per conflicting commit. This is one reason to keep commits small and branches short-lived.

-----

## Interactive Rebase — The Route Editor ✏️

Regular rebase replays commits as-is onto a new base. **Interactive rebase** (`-i`) opens an editor where you can rewrite the history of the commits being replayed. This is the most powerful history-cleanup tool in Git.

```bash
# Open the interactive rebase editor for the last 3 commits
git rebase -i HEAD~3
```

An editor opens with a list of commits (oldest at top):

```
pick 9d3f0a1 Add login function
pick b2a1c34 Add logout function
pick c3d4e56 Fix typo in logout

# Rebase f2d8a91..c3d4e56 onto f2d8a91 (3 commands)
#
# Commands:
# p, pick   <commit> = use commit as-is
# r, reword <commit> = use commit, but edit the commit message
# e, edit   <commit> = use commit, but stop for amending
# s, squash <commit> = meld into previous commit (keep both messages)
# f, fixup  <commit> = meld into previous commit (discard this message)
# d, drop   <commit> = remove this commit entirely
# x, exec   <command> = run shell command
```

### Squash: merging “Fix typo” into the real commit

The “Fix typo in logout” commit is noise — it should have been part of “Add logout function”:

```
pick 9d3f0a1 Add login function
pick b2a1c34 Add logout function
fixup c3d4e56 Fix typo in logout
```

`fixup` squashes the typo fix into the previous commit and discards its message. The result: two clean cabins instead of three — one for login, one for logout (with the typo fix silently included).

### Reword: fixing a poor commit message

```
pick 9d3f0a1 Add login function
reword b2a1c34 Add logout function
pick c3d4e56 Fix typo in logout
```

When Git reaches `reword`, it stops and opens the editor for just that commit’s message. You change it to something better:

```
Add logout function with session invalidation
```

### Drop: removing a commit

You added some debug logging that should never have been committed:

```
pick 9d3f0a1 Add login function
pick b2a1c34 Add logout function
drop a1b2c3d Add debug print statements
```

The debug commit disappears from history.

### Squash everything into one commit

You want to present your entire feature as a single, polished cabin before merging:

```
pick 9d3f0a1 Add login function
squash b2a1c34 Add logout function
squash c3d4e56 Fix typo in logout
```

Git combines all three into one commit. An editor opens for you to write the combined message:

```
Add authentication functions

Implements login with session creation and logout with session
invalidation. Follows the IAuthService interface defined in #123.
```

One clean cabin containing a complete, tested feature.

-----

## `git commit --amend` — Correcting the Last Cabin ✏️

A lightweight alternative to interactive rebase for the single most recent cabin:

```bash
# Fix the last commit message (before pushing)
git commit --amend -m "Add login function with password hashing"

# Add a forgotten file to the last commit
git add src/password_hash.py
git commit --amend --no-edit   # --no-edit keeps the existing message
```

`--amend` creates a new commit with a new SHA-1. Like rebase, it rewrites history — only safe on local commits you have not pushed.

-----

## When to Use What: A Decision Guide 🗺️

```
Is the branch shared / already pushed and others have pulled it?
  YES → git merge (never rebase shared history)
  NO  ↓

Do you want the history to show "these two things happened in parallel"?
  YES → git merge --no-ff
  NO  ↓

Do you have messy intermediate commits to clean up before sharing?
  YES → git rebase -i (interactive, clean up, then push once)
  NO  ↓

Is main ahead and you want to update your branch without a merge commit?
  YES → git rebase main
  NO  → git merge main (fine either way)
```

-----

In **Episode 6**, we turn to the situation that interrupts both merge and rebase workflows: you are in the middle of something and an urgent interruption arrives. You cannot commit unfinished work. You cannot lose it. You need the **holding locker** — `git stash`.

-----

**🔗 Resources**

- **`git rebase` reference**: [git-scm.com/docs/git-rebase](https://git-scm.com/docs/git-rebase)
- **Interactive rebase deep dive**: [git-scm.com/book/en/v2/Git-Tools-Rewriting-History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History)
- **Merge vs. Rebase guide**: [atlassian.com/git/tutorials/merging-vs-rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)

-----

*🚡 Cable Car Git! is a series about Git — explained through the metaphor of a cable car parcel transport network, where every commit is a cabin and every branch is a route.*
