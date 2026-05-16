---
name: mode_config
version: 2.0.0
parent_skill: form-check
audience: learner
---

# Learner mode — how the skill knows you're new

`form-check` ships with two reading modes: **learner** and **default**.

- **Default** (senior-engineer voice): `SKILL.md` is the primary surface. The `learner/` directory is optional reference material. This is what an experienced engineer wants — terse, normative, fast to scan.
- **Learner** (coaching/mentor voice): the QUICKSTART, token-handling primer, cautionary tales, and four core lessons are pinned alongside `SKILL.md`. The reader gets thorough explanations, named friction points, glossary access, and graduated safety floors before being asked to score a change.

This file explains how to opt into learner mode and what changes when you do.

---

## Activating learner mode

Place a file named `.form-check.yaml` in your project root with:

```yaml
mode: learner
```

That's the whole contract. The skill's reading layer (whatever orchestrates it for you — your AI assistant, your IDE's skill loader, your custom harness) is expected to:

1. Detect the file on first invocation.
2. Pin `learner/QUICKSTART.md`, `learner/token_handling_primer.md`, and the four core lessons (`learner/lessons/01_code_read_depth.md`, `learner/lessons/02_test_verification.md`, `learner/lessons/03_hallucination_check.md`, `learner/lessons/06_reversibility.md`) into context alongside `SKILL.md`.
3. Use mentor-voice phrasing in responses: explain *why*, name friction points explicitly, define jargon on first use.
4. Apply the **graduated floors** from QUICKSTART (Floor 1 / 2 / 3) rather than jumping to the full 9-component rubric for every change.

If your harness doesn't support config-file detection: pin the learner files manually in your assistant's "always loaded" list, and prompt with `"reading mode: learner"` at the start of each session.

---

## What "graduated" means

In learner mode, the skill walks you up the safety ladder rather than starting at the top:

| Change tier | Default mode behavior | Learner mode behavior |
|---|---|---|
| Vibe-safe | Apply 9-component rubric | Apply Floor 1 (3 quick checks) + log the change |
| Vibe-careful | Apply 9-component rubric | Apply Floor 2 (Floor 1 + worst-case scenarios + checklists) |
| Vibe-dangerous | Apply 9-component rubric | Apply Floor 3 (Floor 2 + threat model + human reviewer + flagged deploy + rollback doc) — *then* score with the full rubric |

The full rubric is still authoritative; learner mode just sequences it so the persona builds the habit before they get the score formula.

---

## Graduation signals

You've outgrown learner mode when:

- Floor 1 takes you under five minutes without referring to the checklist.
- You can recite the four signals of the hallucination check from memory (registry / author / 30-day / docs match).
- You've shipped at least one Floor-3 change end-to-end, including a documented rollback that you verified worked.
- You've recognized at least one near-miss in your own work and traced it back to a floor step you would have skipped.

When those four are true, change your `.form-check.yaml`:

```yaml
mode: default
```

Or delete the file entirely. The `learner/` directory remains as reference — you'll still want to consult `token_handling_primer.md` years into your career.

---

## What learner mode does NOT do

- It does not lower the standard for vibe-dangerous changes. Floor 3 is the *minimum* for any change touching auth/payments/secrets/deletes, regardless of mode. Learner mode just makes Floor 3 explicit and walks you through it.
- It does not skip the rubric. The rubric is the eventual destination; learner mode is the on-ramp.
- It does not enable destructive operations. The forcing-constraint gate (`tools/check_forcing_constraint.sh`) and the scale-up annex remain locked behind their normal requirements regardless of mode.
- It does not modify the skill's behavior outside the reading layer. The tools (`tools/blast_radius.py`, `tools/scan_prompt_injection.sh`, `tools/check_forcing_constraint.sh`) are identical across modes.

---

## Why this is a config and not a separate skill

A separate `form-check-learner.skill` was the obvious alternative. Rejected because:

- The learner persona and the senior-engineer persona are the *same person at different points in time*. Splitting the skill makes upgrade discontinuous.
- Most of the substantive content (rubric, vibe-safety map, tool scripts) is identical. Duplication would drift.
- The cross-references from `learner/*` into `SKILL.md` and back are bidirectional and load-bearing. Splitting the skill would either break references or require maintaining a fragile mirror.

Single skill, two reading modes, one cross-reference graph. The complexity is in the reading layer, where it belongs.

---

## A note on harness support

As of v2.0.0 (May 2026), no widely-deployed AI-coding harness has native support for `mode:` config files. This spec is a forward-looking contract: it describes what good harness behavior looks like, so harness authors have a target.

Today, the practical implementation is:

1. Your AI assistant's "always-loaded context" / "system prompt" includes the learner files explicitly.
2. You prompt with `"reading mode: learner"` at the start of each session so the assistant adopts mentor voice in its responses.
3. You manually navigate to the floor that matches the change you're about to make.

That's it. The contract is read by humans (and AI assistants prompted by humans) until harness tooling catches up.
