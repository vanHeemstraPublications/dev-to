-----

## title: “Cable Car Git! 🚡 Ep.4: The Junction”
published: false
description: “Episode 4: Spur lines come home. Fast-forward merge vs. merge commit, how conflicts happen and how to resolve them, and when to use `--no-ff`. The junction is where the real Git understanding happens.”
tags: [git, beginners, versioncontrol, tutorial]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/cable-car-git-episode-04.png”
series: “Cable Car Git!”
canonical_url: “”
organization: “the-software-s-journey”

# Cable Car Git! 🚡

## Episode 4: The Junction

> *“Two lines. One network. The junction decides how they meet.”*

-----

## The Spur Lines Come Home 🏠

In Episode 3, we built spur lines. Ahmed has `feature-login` with two cabins. Maria has `fix-payment-null` with one cabin. Both branched from the same point on `main`.

Now both are ready to deliver their parcels to the main trunk. They need to come home through the junction.

In the physical cable car network, a junction is a piece of track infrastructure — it physically connects two lines and routes cabins from one onto the other. In Git, the junction is a **merge** — the operation that brings two branch histories together.

There are two kinds of junctions, and understanding both is essential.

-----

## 🗂️ SIPOC — The Junction

|**Suppliers**                              |**Inputs**                                        |**Process**                                          |**Outputs**                                                                      |**Customers**                                        |
|-------------------------------------------|--------------------------------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------|-----------------------------------------------------|
|A feature branch with commits              |The current position of `main` and the feature tip|`git merge feature-branch` from `main`               |Either a fast-forward advance of `main`, or a new merge commit joining both lines|The `main` branch, now containing the feature’s work |
|Two diverged lines with conflicting changes|Conflict markers in the affected files            |Manual conflict resolution + `git add` + `git commit`|A merge commit that resolves the conflict and joins both lines                   |The team — clean, conflict-free history going forward|

-----

## Type 1: The Smooth Merge — Fast-Forward 🚄

The simplest junction happens when the main line has not moved since the spur line split off. Main has been waiting. The spur line’s cabins can simply be added to the end of main — no junction infrastructure needed. The pointer just slides forward.

```
Before merge:

  A --- B --- C          ← main (waiting)
              \
               D --- E   ← feature-login (ready to deliver)

After git merge feature-login (fast-forward):

  A --- B --- C --- D --- E   ← main (HEAD advanced forward)
                              ← feature-login still points to E
```

No new cabin is created. The `main` pointer simply moves forward to E. This is a **fast-forward merge** — the cleanest possible junction.

```bash
# Start on main, make sure it hasn't moved since feature branched
git switch main

# Merge the feature branch
git merge feature-login
# Updating f2d8a91..b2a1c34
# Fast-forward
#  src/auth.py | 4 ++++
#  1 file changed, 4 insertions(+)

git log --oneline --graph
# * b2a1c34 (HEAD -> main, feature-login) Add logout function
# * 9d3f0a1 Add login function
# * f2d8a91 Add project configuration
```

Clean. Linear. The network map reads like a single uninterrupted line.

-----

## Type 2: The Junction Cabin — The Merge Commit 🔀

When both the main line and the spur line have moved since the split, the junction cannot be resolved by simply sliding a pointer. Both lines have new cabins that the other does not have. A new, dedicated **junction cabin** is needed — a merge commit that has two parents.

```
Before merge:

  A --- B --- C --- F        ← main (has moved — new cabin F)
              \
               D --- E       ← feature-login

After git merge feature-login (merge commit):

  A --- B --- C --- F --- M  ← main (HEAD)
              \         /
               D --- E       ← feature-login
```

`M` is the merge commit. It has two parents: `F` (from main) and `E` (from the feature line). It contains the combined work of both.

```bash
git switch main

# Add a commit to main (simulate someone else's work)
echo "CHANGELOG entry" > CHANGELOG.md
git add CHANGELOG.md
git commit -m "Add changelog"

# Now merge the feature branch (main has diverged — not fast-forwardable)
git merge feature-login
# Merge made by the 'ort' strategy.
#  src/auth.py | 4 ++++
#  1 file changed, 4 insertions(+)
#
# Merge branch 'feature-login'

git log --oneline --graph
# *   g3h4i56 (HEAD -> main) Merge branch 'feature-login'
# |\
# | * b2a1c34 (feature-login) Add logout function
# | * 9d3f0a1 Add login function
# * | d5e6f78 Add changelog
# |/
# * f2d8a91 Add project configuration
```

The `|\` and `|/` in the graph output show the two lines joining at the merge commit. The history is no longer linear — it reflects that two parallel tracks joined here.

### Forcing a merge commit even when fast-forward is possible

Sometimes you *want* a merge commit even on a fast-forwardable branch, to make the branch’s existence visible in the history:

```bash
git merge --no-ff feature-login
# Creates a merge commit even though fast-forward was possible
```

Teams that use GitHub/GitLab pull requests usually generate merge commits automatically (the “Create a merge commit” button). Some teams prefer squash merges or rebase merges — different junction strategies for different team philosophies. Episode 5 covers rebase.

-----

## When Lines Conflict at the Junction ⚠️

The junction breaks when both lines modified the same part of the same file. Git cannot decide which version to use — it requires human judgment.

```
Scenario: both main and feature-login modified src/auth.py line 1
```

```bash
git merge feature-login
# Auto-merging src/auth.py
# CONFLICT (content): Merge conflict in src/auth.py
# Automatic merge failed; fix conflicts and then commit the result.
```

The merge is paused. Git adds **conflict markers** inside the affected file:

```python
<<<<<<< HEAD
def login(user, password, remember_me=False):
    return verify(user, password, remember_me)
=======
def login(user, password):
    return verify(user, password)
>>>>>>> feature-login
```

The markers show you both versions:

- `<<<<<<< HEAD` — what is on `main` (where HEAD points)
- `=======` — the dividing line
- `>>>>>>> feature-login` — what the feature branch says

### Resolving the conflict

1. Open the file, understand both versions
1. Edit it to be the correct final version — remove all conflict markers
1. Stage the resolved file
1. Complete the merge

```python
# The correct version (combining both — remember_me was added on main)
def login(user, password, remember_me=False):
    return verify(user, password, remember_me)
```

```bash
# Stage the resolved file
git add src/auth.py

# Check what else is in conflict
git status
# All conflicts fixed but you are still merging.
#   (use "git commit" to conclude merge)

# Complete the merge
git commit
# (editor opens with a pre-filled merge commit message — accept it or edit it)
```

### Checking what is in conflict

```bash
# See which files have conflicts
git status

# See the conflict in a file (three-way diff format)
git diff
# Shows all unresolved conflicts

# Abort and undo the merge entirely — go back to before the merge started
git merge --abort
```

`git merge --abort` is your panic button. If the conflict resolution feels unclear or risky, abort, study the changes, plan the resolution, and try again.

-----

## Using a Merge Tool

For complex conflicts, a visual merge tool makes the three-way comparison much clearer:

```bash
# Configure your preferred merge tool (VS Code is excellent)
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd "code --wait $MERGED"

# Launch the merge tool for all conflicted files
git mergetool
```

VS Code’s built-in merge editor shows you “Current” (HEAD), “Incoming” (the branch being merged), and a “Result” panel you edit. You can accept one side, both sides, or write a custom combination.

-----

## The `git diff` Deep Dive 🔍

Before and during merges, `git diff` is your diagnostic instrument:

```bash
# What changed in working directory (not yet staged)?
git diff

# What is staged (ready to commit)?
git diff --staged

# What is different between two branches?
git diff main..feature-login

# What would change if you merged feature-login into main?
git diff main...feature-login   # triple-dot: changes on feature since divergence

# What changed in a specific file?
git diff main..feature-login -- src/auth.py
```

-----

## After the Merge: Tidying the Network 🧹

Once a feature branch is merged, its pointer is no longer needed:

```bash
# Delete the local branch (safe — Git warns if not merged)
git branch -d feature-login
# Deleted branch feature-login (was b2a1c34).

# If you pushed the branch to the remote, delete it there too
git push origin --delete feature-login
```

The cabins from `feature-login` still exist in the network history — they are now reachable via the merge commit on `main`. Only the pointer label is removed.

-----

## A Merge Conflict Checklist ✅

When you hit a conflict:

1. `git status` — understand which files are in conflict
1. Open each conflicted file — read *both* versions before choosing
1. Edit to the correct resolution — remove ALL conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
1. `git add <file>` for each resolved file
1. `git status` — confirm all conflicts are marked as resolved
1. `git commit` — seal the merge cabin
1. `git log --oneline --graph` — verify the merge looks correct

Never commit files that still contain `<<<<<<<` markers. Git will let you — but the markers are now your application code and it will break.

-----

In **Episode 5**, we look at an alternative junction strategy — `git rebase` — which avoids the merge commit entirely by replaying the spur line’s cabins from a new starting point on the main trunk. Linear history, clean network map, different trade-offs.

-----

**🔗 Resources**

- **`git merge` reference**: [git-scm.com/docs/git-merge](https://git-scm.com/docs/git-merge)
- **Merge conflict resolution**: [git-scm.com/book/en/v2/Git-Tools-Advanced-Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
- **VS Code merge editor**: [code.visualstudio.com/docs/sourcecontrol/overview](https://code.visualstudio.com/docs/sourcecontrol/overview)

-----

*🚡 Cable Car Git! is a series about Git — explained through the metaphor of a cable car parcel transport network, where every commit is a cabin and every branch is a route.*
