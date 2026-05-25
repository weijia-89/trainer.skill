<!-- sdk-review F1: trainer-owned overlay; bundle rsync --delete removes specialists/ copies -->

# Trainer mechanical pre-action gates (form-check cross-reference)

Root `trainer` routes here before destructive or wide-scope work. `form-check` owns tier scoring and adversarial review content; this file owns the trainer's mechanical gate procedure.

## Three facts (one sentence)

Before destructive or wide-scope action, state in one sentence:

1. **Canonical source of truth** (directory, file, or artifact; which is derived).
2. **Rollback path** (concrete commands to undo).
3. **Verification command** (single command confirming correct state after).

If all three cannot be stated, STOP and verify first.

## Triggers (mechanical)

- `rsync --delete`, `rm -rf`, `git reset --hard`, `git push --force`, `find ... -exec rm`
- Mass edit touching **more than 5 files** (count paths)
- Bundle or sync between two trees (`bundle_specialists.sh`, canonical mirror copies)
- Any `git push` (local pre-push hook must run on this commit graph)

**Pre-push subrule.** Run repo verify hook before push. Hook failure locally beats remote surprise.

## Adversarial-review pass (irreversible network ops)

When reversibility cost exceeds the three-facts gate (push, force-push, branch delete, PR open, merge, release tag, cross-project write):

1. List N potential holes (paths, sequencing, scope creep, sibling work, freeze-list, baseline claims).
2. For each hole, run ONE empirical verification (single tool call with verifiable answer).
3. Release only when cleared. Document in commit message, PR body, or session log.

**Stakes.** Required for vibe-careful or vibe-dangerous irreversible actions. Vibe-safe reversible actions: three-facts only.

**Worked example.** Buds 2026-05-19/20 orch cleanup: 14 holes caught pre-action via enumeration plus single-shot checks.

## Coaching when plan-first violated

Name breach, propose planning-artifact size for stakes tier, surface for sign-off before code. Coached override per trainer override rules (two rounds, then log).
