---
name: lesson_06_reversibility
version: 2.0.0
parent_skill: form-check
audience: learner
rubric_component: 6
---

# Lesson 6 — Reversibility

**The pitch.** Some operations can be undone with `git revert`. Others delete your production database and your weekend. This lesson teaches you how to tell which is which, *before* the AI runs the command.

---

## The 90-second version

Before running any change that touches state:

1. **Classify the operation.** Is it idempotent (safe to repeat), reversible (undo exists), or irreversible (one-way)?
2. **Gate the irreversible ones.** Human approval, dry-run, explicit `--confirm` flag, backup-first — pick the gate that fits.
3. **Document the rollback.** Write the rollback command *before* you run the forward command. If you can't write the rollback, you can't run the forward.

If you don't do these three things, you are betting your data against the AI's accuracy.

---

## Why this matters

The Replit incident (Cautionary Tale #1) was a reversibility failure. The agent had write access to production. The agent ran a destructive operation during a code freeze. There was no dry-run, no human gate, no rollback plan. The database was deleted. Recovery took time; trust took longer.

Most of the worst AI-assisted incidents share a shape:

- The AI had the capability to do an irreversible thing.
- The human didn't notice it was about to do the irreversible thing.
- There was no rollback.

You can break that chain at any link. The cheapest link to break is the rollback documentation — it's a one-line note in the PR description, and it forces the question "wait, can I roll this back?" *before* the destructive command runs.

Self-assessed productivity is systematically miscalibrated (`LICHTENSTEIN-1982`, `KORIAT-BJORK-2005`, `[T1-replicated]`); the METR-2025 RCT (Cautionary Tale #5; n=16, preliminary) is one example consistent with this. Speed *perception* is exactly the wrong frame for irreversible operations regardless of the specific magnitude. A reversible operation can be fast; an irreversible operation must be deliberate.

---

## The full process

### Step 1: classify the operation

For every state-changing operation in your change, mark it with one of three labels:

**Idempotent** — running it twice has the same effect as running it once.

- `CREATE TABLE IF NOT EXISTS users` (safe to re-run)
- `chmod 644 file` (already 644 is a no-op)
- A function that sets a value rather than mutating it
- HTTP PUT / DELETE (per REST conventions)

**Reversible** — there's an inverse operation, and you've documented it.

- `git commit` (reversible by `git revert`)
- `git push` to a branch (reversible if not yet merged)
- Adding a database column (`ALTER TABLE ADD COLUMN`) — reversible by `DROP COLUMN` *if no data was written yet*
- Deploying a new version (reversible by deploying the previous version, *if you have it*)

**Irreversible** — no undo, or undo only via backup restoration.

- `DROP TABLE`, `DROP DATABASE`
- `rm -rf` against real data
- Sending an email
- Charging a credit card
- Making a Stripe transfer
- Posting to a public social account
- `git push --force` to `main`
- Publishing an npm/PyPI package
- Sending a webhook to an external system you don't control

**Friction point.** "Reversible" and "irreversible" are not always crisp categories. A migration that *adds* a column is reversible if you catch the mistake before data is written, but irreversible the moment users save records into it. When in doubt: treat as irreversible.

### Step 2: gate the irreversible ones

For each irreversible operation in your change, pick at least one gate:

**Gate A: human approval.** The change is reviewed by a human before it runs. (Pull request approved; commit signed; deploy approved in your CD tool.) This is the heaviest gate and the most reliable.

**Gate B: dry-run.** The operation has a `--dry-run` mode that prints what it *would* do without doing it. You run dry-run, read the output, then re-run without `--dry-run`. (Most database migration tools support this.) The dry-run output goes in the PR description.

**Gate C: explicit confirmation.** The script asks "type 'DELETE' to confirm" before doing the destructive thing. Useful for one-off scripts you wrote yourself, especially admin tools.

**Gate D: backup-first.** The operation creates a snapshot/backup *before* the destructive change. The snapshot is the rollback path. Documented retention and restore procedure are required.

**Gate E: staged rollout.** The change is deployed to 1% of users, then 10%, then 100% — with monitoring at each step. Each step is a checkpoint where you can stop and revert. This applies more to deploys than to one-off operations, but it's the canonical answer for "irreversible at scale."

For Floor 3 (vibe-dangerous): **at least one gate is required**. For maximally-irreversible operations (production data deletion, external charges): **two gates** is the floor.

### Step 3: write the rollback before the forward

Before running the forward operation, write the rollback. Two-column format works well:

```markdown
| Forward operation | Rollback |
|---|---|
| Run migration `add_users_table.sql` | Run `DROP TABLE users;` (no data yet at this point) |
| Deploy v2.3 to production | Re-deploy v2.2; image tag `myapp:2.2` |
| Charge customer $42 via Stripe | Issue refund: `stripe refunds create --charge=<charge_id>` |
| Send launch email to 5,000 subscribers | (cannot undo; consider staged rollout instead) |
```

If you can't write the rollback ("cannot undo" with no mitigation): you've identified a one-way door. Decide consciously whether to walk through it.

**The rollback note goes in the PR description, not just your head.** Future-you at 3am needs to find it without remembering.

### Step 4: run the operation, observe, verify

After running:

- Did the forward operation succeed? (Read the output, not "it should have worked.")
- Did downstream systems get the change? (Check the dashboard, the log, the count.)
- Is the rollback path still valid? (For example: if you deployed v2.3 and rolled back, can you still get v2.2 — is the image still in the registry?)

If the verification fails: execute the rollback. If the rollback succeeds: investigate without time pressure. If the rollback fails: this is now an incident; document everything, ping a human, do not improvise.

---

## What goes wrong

### Failure mode A: trusting the AI's claim of "this is safe"

The AI says "this migration is reversible because we're just adding a column." That's true *until you write data into the new column*. The AI is not tracking the temporal state of your production data; it's pattern-matching on "ADD COLUMN" → "reversible."

**Rule:** classify the operation yourself. Don't accept the AI's classification without verification.

### Failure mode B: assuming the dry-run output represents reality

Dry-run modes are implementations. They can have bugs. The dry-run output may differ from the real-run output because the dry-run skipped a side effect the real run will do.

**Rule:** dry-run is a strong signal, not a guarantee. Use it alongside other gates for genuinely high-stakes operations.

### Failure mode C: rollback that requires the thing you broke

Common pattern: "the rollback for this deploy is to re-deploy the previous version, which we'll fetch from the git tag." Then the deploy *deletes* the git tag as part of cleanup, and the rollback is no longer executable.

**Rule:** when you write the rollback, make sure the rollback's preconditions are *still true after the forward operation completes*. Mentally walk through it.

### Failure mode D: rollback that uses a credential you don't have right now

3am, production is broken. You go to run the rollback. The rollback requires a token you keep in a password manager you can't access on your phone. You're now improvising.

**Rule:** for vibe-dangerous changes, the rollback should be executable from a runbook with credentials you can get to without 2FA-on-a-locked-laptop.

### Failure mode E: "we can always restore from backup"

True if:

- The backup is recent.
- You've tested the restore procedure.
- The restore procedure isn't blocked by something the failure broke (e.g. "the backup is in S3, but the failure was in our IAM config, so we can't reach S3 right now").

False often enough that this is its own incident pattern.

**Rule:** "restore from backup" is the rollback only if you've *practiced the restore* recently. Untested backups are a hope, not a plan.

### Failure mode F: the irreversible operation that disguised itself as reversible

The classic: `git push --force` to `main`. Reversible? Yes, if you act in the next few minutes — the previous commits are still in `reflog` on machines that have them. ("Reflog" is git's local-only log of every state your repo has been in; commits not on any branch survive there for a while before garbage collection.) After a day or two, those commits get garbage-collected. Now it's irreversible.

**Rule:** "reversible" has a time component for some operations. Document the rollback window, not just the rollback procedure.

---

## When reversibility scoring gets relaxed

For pure read operations (`SELECT`, `GET`, `git log`): there's nothing to reverse. Mark explicitly:

> Reversibility: n/a (read-only operation).

For everything else, the answer is rarely "n/a." Even a "harmless" log statement can leak sensitive data into log archives that are themselves hard to scrub. The rubric weights reversibility at 8 *because* the default classification is "this matters."

---

## Exercises

### Exercise 1: classify ten operations

For each of the following, mark it idempotent, reversible, or irreversible. Then write the rollback (or "n/a" if not applicable):

1. Adding a new column to a database table
2. Sending a Slack message to a channel
3. Pushing a new image to a Docker registry
4. Updating an entry in a `users` table (`UPDATE users SET ...`)
5. Renaming a function across the codebase
6. Running a one-time script that emails 100 users
7. `chmod 600` on a file that's already `600`
8. `git push origin feature-branch` to a fresh branch
9. `git push --force origin main`
10. Publishing a new version of an npm package

(Answers: 1 reversible-with-window, 2 irreversible, 3 reversible-with-window, 4 reversible-with-backup, 5 reversible, 6 irreversible, 7 idempotent, 8 reversible, 9 irreversible-with-narrow-window, 10 irreversible.)

### Exercise 2: write the rollback for your current branch

Open the diff for whatever you're working on right now. For each state-changing operation in the diff, write the rollback. **If you can't, that's a finding.** Either redesign to make it reversible, add a gate, or note explicitly that you're walking through a one-way door.

### Exercise 3: practice the rollback

Pick a small reversible operation (a config change, a feature-flag flip). Apply it. Roll it back. **Time the rollback.** If the rollback took more than 2 minutes, simplify either the operation or the rollback before doing this on anything that matters.

---

## Cross-references

- **Rubric component 6** in `rubrics/confidence_score.md` — weight 8.
- **Cautionary tale #1** (Replit production DB deletion) in `learner/cautionary_tales.md`.
- **Token primer habit 7** (rotate first, scrub second) in `learner/token_handling_primer.md` — the reversibility principle applied specifically to leaked secrets.
- **QUICKSTART Floor 3 step 10** — "document the rollback" is its own checklist item.
- **Mini-runbook in `SKILL.md` Section 10** — step 8 ("ship behind a flag if vibe-dangerous") is reversibility in practice.

---

## Retrieval prompts

Per `learner/study_protocol.md` Habit 1 (retrieval beats re-reading): **close this file** and answer the questions below in writing or aloud. Then re-open and check.

If you miss two or more, schedule a re-read for **+3 days** (Habit 2 — spacing).

1. Close this file. State the three-way classification (idempotent / reversible / irreversible) and one example of each from your own work.
2. Recall the five gate types (human approval, dry-run, explicit confirm, backup-first, staged rollout). For each, name a kind of operation it's the right gate for.
3. What does the *rollback-before-forward* rule say, and why is it the rule rather than 'just be careful'?
4. Name three of the six failure modes covered in this lesson.

When you've answered all four cold (no peeking) on two separate occasions ≥1 week apart, this lesson has stuck. Move it to your spaced-review monthly cadence.
