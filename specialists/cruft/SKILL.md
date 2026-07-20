---
name: cruft
description: |
  Use when an agent produces session-bound / intermediate / superseded artifacts (scratchpads, mid-synthesis, debug dumps). Tags them with the `.cruft.md` slug + a 1-2 line purpose/date header, and deletes them only after adversarial reviews pass and a PR merges or the session closes. Symptoms: "I'll clean this later," piles of scratchpad.*.md, cruft that outlives its use case, "just rm -rf .agent" without a gate.
type: project-skill
version: 1.0.0
authors: Wei Jia (2026-07-20)
license: MIT
required_tools: [file_read, shell]
recommended_tools: [git]
optional_tools: []
composes: []
---

# cruft — tag early, delete on a gate, never by hand-wave

```
IRON LAW: NO CRUFT DELETION UNLESS (adversarial review gate GREEN) AND (PR merged OR session closed).
```

Violating the gate deletes evidence you may need to defend a review finding. "I'll just rm it" is the
rationalization that turns a recoverable mistake into a permanent one.

## The convention (2 rules, that's it)

1. **Slug.** Any file that will become stale gets the suffix `.cruft.md` (lowercase). Examples:
   `scratchpad.lob-research.cruft.md`, `notes.merge-42.cruft.md`. The suffix is the ONLY signal the
   cleanup script trusts — no sidecar, no manifest to drift.
2. **Header.** First line of the file (markdown comment or `# META:`), one or two lines:
   `# META: <purpose> · use-case <YYYY-MM-DD> · CRUFT — delete after <PR-merge|session-close + reviews pass>`
   This is the staleness assessment made explicit, so a later reader knows *why it existed* before deleting.

## LLM responsibility (when to tag)

Before writing any scratchpad / intermediate synthesis / debug dump, ask ONE question: *will this be
wrong or irrelevant after this task or session ends?* If yes → name it `*.cruft.md` with the header.
If it is durable (a spec, a decision record, a reused reference) → do NOT tag it; give it a normal name
and let it live. Tagging is cheap; mistagging a real doc for deletion is not.

## Deterministic cleanup (the gate)

`scripts/prune_cruft.sh --root <dir> [--apply|--dry-run] [--force-after-review]`

- Default is `--dry-run`; it lists candidates and exits 0.
- `--apply` deletes ONLY if the **review gate is GREEN**:
  - a sentinel `.trainer/reviews-complete` exists, OR
  - `verify_trainer_codereview.sh` (trainer) exits 0, OR
  - called with explicit `--force-after-review` (human has eyeballed the review).
- If the gate is not satisfied it prints `REFUSED: review gate not satisfied` and exits 2. **No deletion.**
- Never touches files without the `.cruft.md` suffix. Never crosses into trainer.skill itself.

## Wiring (two triggers)

- **After PR merge** — `pr` skill §8 runs the code-review verification, writes `.trainer/reviews-complete`,
  then calls `prune_cruft.sh --apply`. Composed by `pr`.
- **Session close** — on opencode "clean cruft" / close-session, run `prune_cruft.sh --apply` (same gate).
  See also the request-cap contract R4c webfetch-cache cleanup; this script is the superset for
  `.cruft.md` session scratchpads.

## Red flags

- Deleting `.cruft.md` files during an open review (gate RED) — STOP.
- Hand-maintained cruft lists (the old `prune_*_cruft.sh` hardcoded arrays) — replace with the suffix scan.
- Tagging a durable doc as `.cruft.md` to "tidy" — that is silent data loss, not hygiene.
