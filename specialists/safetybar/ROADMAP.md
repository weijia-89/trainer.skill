# safetybar.skill ROADMAP

**Current version:** v0.3.0 (synced with trainer v0.5.0)
**Status:** stable. The git-panic decision tree, the reflog recovery
patterns, and the "before you reset" pause prompt all ship in working
form.

## Near-term

- Pressure-scenarios for the worst-outcome failure modes. The short list
  today is force-pushing over a coworker's branch and accidental reset of
  uncommitted work. Detached HEAD with local changes and the
  merge-conflict spiral are next.
- A worked example of a real recovery: a session where someone ran
  `git reset --hard` and the reflog walk got the work back.

## Mid-term

- Coverage for less-common cases: lost stashes after `git stash drop`,
  submodule confusion, lost work from `git rebase --abort` when the
  user wanted `--continue`.
- A pre-flight checklist a user can run mentally before any
  destructive git command. The skill currently has the prompts inline;
  pulling them into a one-page reference would help.

## Out of scope

- safetybar is not a tutorial. It's a panic-response surface. Users in
  panic don't read tutorials.
- Recovery for GitHub-side destructive ops (force-push past a tag, branch
  deletion via the API). That's a separate operational surface.

## Open questions

- Whether to add a `safetybar verify` flow that checks for common
  pre-destructive setup (clean working tree, named branch, recent push)
  before running the actual command. Risk: turns the skill from
  panic-response into a friction-adding wrapper.
