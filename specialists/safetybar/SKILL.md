---
name: safetybar
description: |
  Use when a git command went wrong, work appears lost, or a destructive git operation is being considered. Symptoms: panic about reset/force-push/branch-deletion, "I think I lost my work," merge or rebase conflicts you can't resolve, detached HEAD, unsure whether to revert or reset.
type: project-skill
version: 1.1.0
authors: Wei Jia (1.0, 2026-05-15); v1.1 Iron Law layering 2026-05-16
license: MIT
required_tools: [shell]
recommended_tools: [file_read, git]
optional_tools: []
composes: []
---

# safetybar — git catches you when the lift fails

```
IRON LAW: NO DESTRUCTIVE GIT COMMAND BEFORE READING ITS RECOVERY PATH IN THIS FILE.
```

Violating the letter of this rule is violating the spirit of this rule. "I'll just check the recovery after I run it" is the rationalization that produces lost work. The recovery is the first read; the command is the second action.

## Red Flags — STOP and re-read this section

If any of these thoughts is in your head right now, you are about to make a recoverable situation unrecoverable:

- "I'll just `git push --force` to fix this quickly."
- "The reflog will catch it, I don't need to read first."
- "It's just my local repo, no one else is affected." (Until you discover a collaborator was rebasing it.)
- "I'll figure it out as I go."
- "I've done this before, I don't need to check the recovery path."
- "I just need to undo, why is this so complicated."
- "If I run `git reset --hard` once more it'll work."
- "Let me clear the working tree first and start fresh." (Especially in a panic — see §1.)

Each red flag means: stop. Run **`git reflog > /tmp/reflog-$(date +%Y%m%d-%H%M%S).txt`** before anything else. Then read §1.

## Rationalizations — what you'll tell yourself, what's actually true

| Excuse | Reality |
|---|---|
| "Force-push is fine, I'm the only one on this branch" | You are not the only one. CI was rebasing. A teammate had it checked out. The webhook had it cached. |
| "I just need to clean up untracked files real quick" | `git clean -fdx` deletes uncommitted *and ungitignored* work. Read §2.7 first. |
| "Reflog only goes back 90 days, mine is older" | 90 days is the default; check with `git config gc.reflogExpire`. Often longer. Run reflog before assuming. |
| "I need to unbreak production right now, no time to read" | Production breakage is not fixed by a destructive git command. Pause. Read. Diet §3 forbids destructive ops during incidents. |
| "I'll just do it the way I learned" | The way you learned probably skipped recovery paths. The way you learned is what produced this situation. |

## Keywords for discovery

For trigger-keyword indexing: I broke git, lost my commits, git reset hard, force push, accidentally deleted branch, merge conflict, rebase conflict, detached HEAD, undo last commit, undo merge, reflog, recover deleted, git mess, untracked files lost, I think I lost my changes, git is broken, what does this git command do, can I git push --force, should I rebase or merge.

## Scope

You did something with git. You're not sure what happened. You're worried you lost work. This skill walks the recovery in the right order.

**Scope.** Recovery, undo, conflict resolution, lost-commit recovery, branch surgery. Not git basics — assume you can `git add`, `git commit`, `git push`. Not GitHub/GitLab workflow — that's platform-specific.

**The first thing to know.** Almost nothing is actually lost in git. **Reflog stores almost every state for 90 days by default.** If you panicked and ran something destructive, you probably still have your work. Read §1 before doing anything else.

## §1 — The "I think I lost my work" protocol

Before anything:

1. **Do not run any more git commands.** Especially not `git gc`, `git reset`, or anything with `--force`.
2. **Run `git reflog`.** This shows every HEAD change in the last 90 days, even ones that are "gone" from branches.
3. **Find the SHA of the state you want back.** It's somewhere in the reflog output, labeled with what you were doing ("commit:", "checkout:", "reset:", "merge:", etc.).
4. **Check out that SHA into a new branch:** `git checkout -b recovery-$(date +%Y%m%d) <sha>`. You now have your work back on a new branch.
5. **Verify** the files look right (`git log`, `ls`, `git status`).
6. **Then** decide whether to merge / rebase / cherry-pick the recovery branch back where you wanted it.

If `git reflog` shows the SHA but `git checkout <sha>` says "unknown revision," try `git fsck --lost-found` — orphaned commits land in `.git/lost-found/`.

If even that doesn't work and the work was committed at any point in the last 90 days, file system tools (`find`, search for distinctive file content) often recover it from `.git/objects/`. Beyond that, restore from your editor's undo history, your IDE's local history, or your last backup. (Yes — keep backups.)

## §2 — Undo paths for the seven scariest commands

For each scary command, this section gives the *recovery* path. Read the recovery before running the command, not after.

### 2.1 `git reset --hard HEAD~1` (and friends)

**What it does.** Discards uncommitted changes AND moves your branch pointer back N commits.

**Recovery.**
- The commits aren't gone — they're orphaned. `git reflog` shows them.
- `git reset --hard <sha-from-reflog>` puts you back where you were.
- Uncommitted changes you had at the time, however, are gone unless they were saved by an IDE.

**Safer alternative.** Use `git reset --soft HEAD~1` to undo a commit but **keep** the staged changes. Use `git stash` before any reset to save uncommitted work.

### 2.2 `git push --force` (the classic disaster)

**What it does.** Rewrites the remote branch's history; co-workers who pulled the old version now have divergent local branches.

**Recovery.**
- *Your* recovery is easy: `git reflog` → reset to pre-force SHA → `git push --force` again (back to the original state).
- *Co-workers' recovery* requires them to reset their local branches to the new remote — coordinate in chat before doing it.

**Safer alternative.** Always use `git push --force-with-lease`. It refuses to push if the remote has changed since you last fetched — i.e. if someone else has pushed in the interim, you'll be told to investigate before overwriting their work. This catches the most common force-push mistake.

**On a shared branch (main/master/release).** **Don't force-push at all.** Use `git revert` to create a new commit that undoes the unwanted change. The history grows by one commit; nothing is lost; nobody's clone breaks.

### 2.3 `git clean -fd` (or `-fdx`)

**What it does.** Deletes untracked files (and with `-x`, also gitignored files like `.env`).

**Recovery.** **There is no git-side recovery** — these files were never in git. If you ran this on `.env` files containing secrets, those are gone unless your IDE / editor / file-system trash retained them.

**Safer alternative.** `git clean -nfd` (note the `-n`) is a *dry run* — it lists what would be deleted without doing it. Always dry-run before `git clean -fd`. Beginners conflate `git clean` with `git reset` because both "clean things up." They're different. `git clean` is destructive in a way `git reset` isn't.

### 2.4 `git branch -D <name>` (deleting a branch with `-D`)

**What it does.** Deletes a branch pointer, including one with unmerged commits (the lowercase `-d` refuses).

**Recovery.** `git reflog` shows the branch's tip SHA. `git checkout -b <name> <sha>` re-creates it.

**Note.** Local branch deletion is recoverable. **Remote branch deletion** (`git push origin --delete <name>`) is also recoverable from your local reflog *if you had the branch checked out locally*. If you never had it locally, you depend on the platform's branch-deletion history (GitHub keeps it for 90 days for non-protected branches).

### 2.5 `git checkout -- <file>` / `git restore <file>`

**What it does.** Overwrites the file in your working directory with the last committed version. Discards uncommitted changes to that file.

**Recovery.** **There is no git-side recovery** — uncommitted changes were never in git. IDE local history (VS Code, JetBrains) often saves you here.

**Safer alternative.** Stash before restoring: `git stash push -- <file>` saves the file's current state with the option to recover via `git stash pop`.

### 2.6 `git rebase -i` (interactive rebase)

**What it does.** Rewrites a sequence of commits on a branch. The most useful and most dangerous beginner-accessible command.

**Recovery.** `git reflog` shows the pre-rebase state. `git reset --hard <pre-rebase-sha>` undoes the entire rebase.

**Hazards specific to rebase.**
- Conflicts during rebase pause the operation; finish or `git rebase --abort`.
- Rebasing commits that have been pushed to a shared branch requires force-push to update remote — see §2.2 hazards.
- Squash-merges in the rebase plan permanently lose intermediate commit boundaries (the squashed commits become one). If you might want them separate later, don't squash.

**Safer alternative.** For learning, use `git rebase -i` only on *local-only* branches you haven't pushed. Once you've pushed, prefer `git merge` (creates merge commit, preserves history). Or push the rebased branch to a *new* branch name so the original is intact.

### 2.7 `git stash drop` / `git stash clear`

**What it does.** Deletes a stash (or all stashes).

**Recovery.** A dropped stash is *not* in `git stash list` anymore but its commit object often exists for ~14 days. `git fsck --no-reflog --lost-found` finds dangling commits; look for the stash-object signature (it's a commit with two parents).

**Safer alternative.** Convert important stashes to branches before dropping: `git stash branch <name> <stash-id>`. Then they become reachable through the branch and protected by normal reflog rules.

## §3 — Conflict resolution

A merge or rebase conflict is *not* an error — it's git saying "two changes touched the same lines and I don't know which to keep."

### 3.1 Anatomy of a conflict marker

```
<<<<<<< HEAD
your version of the code
=======
their version of the code
>>>>>>> branch-name
```

You resolve by:
1. Deleting the markers (`<<<<<<<`, `=======`, `>>>>>>>`).
2. Editing the section so the resulting code is what you want — which may be yours, theirs, both, neither, or a synthesis.
3. `git add <file>` to mark it resolved.
4. Continue: `git commit` (for merge) or `git rebase --continue` (for rebase).

### 3.2 The three-question conflict triage

For each conflict:

1. **Are both changes needed?** Merge them.
2. **Is only one change needed?** Pick it; delete the other.
3. **Neither change is what I want now?** Write the new correct version; delete both.

If you can't tell, *don't merge yet*. Get the conflicting authors (often: you + the AI assistant + the previous you) to resolve before committing.

### 3.3 The escape hatches

- `git merge --abort` cancels an in-progress merge.
- `git rebase --abort` cancels an in-progress rebase.
- `git cherry-pick --abort` cancels an in-progress cherry-pick.

These return you to the pre-operation state. Use them when you realize you're in over your head — better to back out and approach differently than to commit a half-resolved mess.

## §4 — Detached HEAD

**What it is.** HEAD points to a commit SHA instead of a branch. Common after `git checkout <sha>` or after some interactive-rebase states.

**Why it looks scary.** Git says "you are in 'detached HEAD' state. ... If you want to create a new branch to retain commits you create, you may do so..."

**What to do.**
- If you don't intend to commit anything: just `git checkout <branch-name>` to reattach.
- If you've made commits while detached and want to keep them: `git checkout -b <new-branch-name>` makes the current detached state a branch.
- If you've made commits while detached and forgot to branch before checking out a real branch: see §1 — they're in the reflog.

## §5 — Branch surgery patterns

### 5.1 "I committed to the wrong branch"

```bash
git log -1                            # note the SHA you want to move
git reset HEAD~1 --soft               # undo the commit, keep changes staged
git stash                             # save the changes
git checkout <right-branch>           # switch
git stash pop                         # restore the changes
git commit                            # commit on the right branch
```

### 5.2 "I want to move the last N commits from main to a new branch"

```bash
git branch new-feature-branch         # marks the current state
git reset --hard origin/main          # rewinds main to the remote state
git checkout new-feature-branch       # switch to the moved commits
```

### 5.3 "I want this one commit from another branch"

```bash
git cherry-pick <sha>
```

Cherry-pick is the right tool for "I want this specific change, not the whole branch." Conflicts can happen; resolve as in §3.

## §6 — Anti-patterns for beginners

- ❌ **Force-pushing to shared branches** to "clean up history." History on shared branches is contract, not aesthetic. Use revert.
- ❌ **Running `git reset --hard` to "fix" an unfamiliar git state.** It almost certainly makes things worse. Always read `git status` and `git log --oneline -10` first.
- ❌ **Following an AI-generated git command without reading it.** AI assistants confidently generate `--force` commands. Read every git command with `--force`, `--hard`, `-D`, or `clean -f` in it before running. *Especially* if the AI offered the command after you said "this is broken."
- ❌ **Resolving conflicts by accepting one side blindly** (`git checkout --theirs` / `--ours` without thinking). The conflict means git noticed a real problem — accept-blindly silences git, not the problem.
- ❌ **`rm -rf .git` to start over.** Almost never the right move and never the right move on a repository with un-pushed work. If you genuinely want to start over: clone again to a new directory, copy current files in, commit. Don't delete the repo metadata.

## §7 — Prevention habits

- **Set `merge.ff = false`** in your global config. Forces merge commits to be explicit, which preserves history readability.
- **Always `git status` before any destructive command.** Knowing the state stops 90% of "oh no" moments.
- **Stash before any rebase / reset / hard checkout.** `git stash push -m "before-rebase-$(date +%H%M)"` is a cheap insurance.
- **Branch before any experiment.** "I'll just try X on main" is the start of most disasters. `git checkout -b experiment-X` costs three seconds.
- **Push to a feature branch, not directly to main.** Even solo, even for "small" changes. Forces a moment of reflection between commit and main-branch state.
- **Read every AI-generated git command twice before running.** Hallucination + git = lost work.

## Composition with other skills

- `form-check/learner/token_handling_primer.md` covers the *credential* aspect of git mistakes (force-push exposing secrets). safetybar covers the *state* aspect.
- `diet §3` covers in-incident rollback decisions. The rollback *mechanic* (revert vs reset vs force) lives here.
- `recovery` engagements that touch many commits should rebase on a *new* branch and review before merging back — safetybar's "branch surgery" patterns apply.

## Provenance

This skill exists because git mistakes are the highest-frequency low-grade emergency for beginners, and the existing git documentation assumes you already know what's going on. The "I think I lost my work" protocol (§1) is the single most-asked beginner question; reflog-first is the single most-effective answer. Inspired by `man git-reflog` and 20+ years of mailing-list "help I broke git" threads.
