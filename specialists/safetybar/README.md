# safetybar — git catches you when the lift fails

A skill for when git looks broken, when you think you lost work, and for the seven scariest git commands.

## What it does

Almost nothing is actually lost in git. Reflog stores almost every state for 90 days by default. The skill exists to make that fact actionable for someone who just ran a destructive command and is panicking.

Seven sections:

1. The "I think I lost my work" protocol (reflog-first, then everything else)
2. Undo paths for the seven scariest commands (`reset --hard`, `push --force`, `clean -fd`, `branch -D`, `checkout -- <file>`, `rebase -i`, `stash drop`)
3. Conflict resolution
4. Detached HEAD
5. Branch surgery patterns
6. Anti-patterns
7. Prevention habits

The recovery path appears before the safer alternative in each entry. This ordering reflects that you are probably reading this skill *after* running the command, not before.

## When to invoke

- You ran something with `--force`, `--hard`, `-D`, or `clean -f` and are now worried.
- You have an active merge or rebase conflict and need a strategy.
- Your branch state looks unfamiliar (detached HEAD, unexpected history, missing commits).
- An AI assistant suggested a git command and you want to know what its recovery path looks like before you run it.

## When to skip

- You are doing routine `add` / `commit` / `push`. That is not what this skill is for.
- You are debugging non-git problems that happen to involve a git repository. Look elsewhere first.

## Composes with

None directly. The skill is self-contained. Other skills reference it:

- `diet §3.4` for in-incident rollback decisions.
- `pr §5.2` for code-level deploy rollback.
- `recovery` for engagements that span many commits and need branch surgery.

## What this skill protects against

The two most common beginner git disasters:

- Force-pushing to a shared branch and breaking everyone's clone. The skill teaches `--force-with-lease` and explains why `git revert` beats `--force` on shared branches.
- Running `git reset --hard` after a confusing state and losing uncommitted work that was never in git. The skill teaches the stash-first habit.

## Files

- `SKILL.md` — the seven sections
- `CHANGELOG.md` — version history
- This file

## License

MIT.
